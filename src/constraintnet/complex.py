"""Simplicial complex with group-valued labels on oriented edges.

A graph is not enough for 3D matter: the simulator needs vertices, oriented edges,
triangular faces and tetrahedra, because *curvature* lives on faces and *charge*
lives on cycles.  This module stores that combinatorics and nothing else -- no
coordinates, no geometry, no dynamics.

Single source of truth
----------------------
An edge is stored once, under its canonical key ``(min(u, v), max(u, v))``, with a
single label.  The reverse-orientation rule required by the specification,

    A_ji = A_ij^{-1},

is therefore not an invariant that could drift out of sync -- it is enforced by
construction: :meth:`SimplicialComplex.label` inverts on read when the requested
orientation is opposite to the stored one.

Orientation conventions
-----------------------
* Canonical orientation of a simplex = its vertices sorted ascending.
* The boundary of an oriented tetrahedron ``[v0 v1 v2 v3]`` (vertices already in
  ascending order) uses the standard simplicial convention::

      d[v0 v1 v2 v3] = [v1 v2 v3] - [v0 v2 v3] + [v0 v1 v3] - [v0 v1 v2]

  i.e. the face omitting ``vk`` carries sign ``(-1)**k`` and induced vertex order
  equal to the remaining vertices in tet order.
* Holonomy of an oriented triangle ``(i, j, k)`` is ``A_ij * A_jk * A_ki``.
  Reversing the orientation inverts the holonomy (see ``tests/test_holonomy.py``).
"""

from __future__ import annotations

import itertools
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple

from .groups import Group, get_group

__all__ = [
    "SimplicialError",
    "Vertex",
    "EdgeView",
    "FaceView",
    "TetraView",
    "SimplicialComplex",
]


class SimplicialError(Exception):
    """Raised when a combinatorial or labelling invariant is violated."""


# --------------------------------------------------------------------------- #
# vertices
# --------------------------------------------------------------------------- #
@dataclass
class Vertex:
    """A primitive actualization.  Not a point in space."""

    id: int
    metadata: dict = field(default_factory=dict)

    def __eq__(self, other) -> bool:
        return isinstance(other, Vertex) and self.id == other.id

    def __hash__(self) -> int:
        return hash(("vertex", self.id))


# --------------------------------------------------------------------------- #
# views: read-through wrappers so the spec's attribute shapes hold
# --------------------------------------------------------------------------- #
class EdgeView:
    """An *oriented* edge ``source -> target`` reading state from the complex."""

    __slots__ = ("_cx", "source", "target")

    def __init__(self, cx: "SimplicialComplex", source: int, target: int):
        if source == target:
            raise SimplicialError(f"degenerate edge {source}->{target}")
        self._cx = cx
        self.source = source
        self.target = target

    @property
    def label(self):
        return self._cx.label(self.source, self.target)

    @label.setter
    def label(self, value) -> None:
        self._cx.set_label(self.source, self.target, value)

    @property
    def realized(self) -> bool:
        """True when the implication has actualized (``A => B``)."""
        return self._cx.is_realized(self.source, self.target)

    @realized.setter
    def realized(self, value: bool) -> None:
        self._cx.set_realized(self.source, self.target, bool(value))

    def reversed(self) -> "EdgeView":
        return EdgeView(self._cx, self.target, self.source)

    @property
    def key(self) -> Tuple[int, int]:
        return self._cx.edge_key(self.source, self.target)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<Edge {self.source}->{self.target} label={self.label!r}>"


class FaceView:
    """An oriented triangle ``(i, j, k)``; holonomy runs ``ij * jk * ki``."""

    __slots__ = ("_cx", "vertices")

    def __init__(self, cx: "SimplicialComplex", vertices: Tuple[int, int, int]):
        if len(set(vertices)) != 3:
            raise SimplicialError(f"degenerate face {vertices}")
        self._cx = cx
        self.vertices = tuple(vertices)

    @property
    def i(self) -> int:
        return self.vertices[0]

    @property
    def j(self) -> int:
        return self.vertices[1]

    @property
    def k(self) -> int:
        return self.vertices[2]

    @property
    def edge_ij(self) -> EdgeView:
        return EdgeView(self._cx, self.i, self.j)

    @property
    def edge_jk(self) -> EdgeView:
        return EdgeView(self._cx, self.j, self.k)

    @property
    def edge_ki(self) -> EdgeView:
        return EdgeView(self._cx, self.k, self.i)

    @property
    def edges(self) -> Tuple[EdgeView, EdgeView, EdgeView]:
        return (self.edge_ij, self.edge_jk, self.edge_ki)

    @property
    def key(self) -> Tuple[int, int, int]:
        return tuple(sorted(self.vertices))  # type: ignore[return-value]

    def reversed(self) -> "FaceView":
        i, j, k = self.vertices
        return FaceView(self._cx, (i, k, j))

    def holonomy(self):
        from .holonomy import triangle_holonomy

        return triangle_holonomy(self._cx, self.vertices)

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<Face ({self.i},{self.j},{self.k})>"


class TetraView:
    """A tetrahedron on four vertices with its induced boundary orientation."""

    __slots__ = ("_cx", "vertices")

    def __init__(self, cx: "SimplicialComplex", vertices: Iterable[int]):
        verts = tuple(sorted(int(v) for v in vertices))
        if len(set(verts)) != 4:
            raise SimplicialError(f"degenerate tetrahedron {vertices}")
        self._cx = cx
        self.vertices = verts

    @property
    def key(self) -> Tuple[int, int, int, int]:
        return self.vertices

    @property
    def faces(self) -> List[FaceView]:
        """The four triangular faces in canonical (sorted) orientation."""
        return [FaceView(self._cx, f) for f in tetra_faces(self.vertices)]

    def boundary_faces(self) -> List[Tuple[FaceView, int]]:
        """``(face, sign)`` pairs with the induced *outward* orientation.

        Uses the tetrahedron's stored orientation (:meth:`SimplicialComplex.tet_order`),
        not the sorted vertex tuple.
        """
        out = []
        for ordered, sign in tetra_boundary(self._cx.tet_order(self.vertices)):
            out.append((FaceView(self._cx, ordered), sign))
        return out

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<Tetra {self.vertices}>"


# --------------------------------------------------------------------------- #
# simplex helpers (pure functions, no state)
# --------------------------------------------------------------------------- #
def tetra_faces(tet: Tuple[int, ...]) -> List[Tuple[int, int, int]]:
    """The four faces of a tetrahedron, each sorted ascending."""
    return [tuple(sorted(c)) for c in itertools.combinations(tet, 3)]  # type: ignore[misc]


def tetra_boundary(tet: Tuple[int, ...]) -> List[Tuple[Tuple[int, int, int], int]]:
    r"""Induced boundary orientation of the *ordered* tetrahedron ``[v0 v1 v2 v3]``.

    Returns ``[(ordered_face_triple, sign), ...]`` with sign ``(-1)**k`` for the face
    omitting index ``k``.  Summing these over consistently oriented tetrahedra makes
    interior faces cancel in pairs, leaving the boundary surface.

    The vertex order is not cosmetic -- it *is* the orientation.  Sorting throws that
    information away, and then adjacent tetrahedra induce equal rather than opposite
    orientations on their shared face so nothing cancels (exactly what happens to a
    Kuhn lattice if you forget it; see ``docs/PHYSICS_NOTES.md``).
    """
    out = []
    for k in range(4):
        ordered = tuple(v for i, v in enumerate(tet) if i != k)
        out.append((ordered, 1 if k % 2 == 0 else -1))
    return out


def face_induced_signs(ord_tet: Tuple[int, int, int, int]) -> Dict[Tuple[int, int, int], int]:
    """Sign of each face's induced orientation relative to canonical sorted order.

    Flipping the parity of ``ord_tet`` flips every sign -- the simplicial statement
    that reversing a tetrahedron reverses its whole boundary.
    """
    out: Dict[Tuple[int, int, int], int] = {}
    for k in range(4):
        ordered = tuple(v for i, v in enumerate(ord_tet) if i != k)
        sign = 1 if k % 2 == 0 else -1
        if reverse_orientation(ordered):
            sign = -sign
        out[tuple(sorted(ordered))] = sign
    return out


def triangle_edges(tri: Tuple[int, int, int]) -> List[Tuple[int, int]]:
    """The three oriented edges of the loop ``i -> j -> k -> i``."""
    i, j, k = tri
    return [(i, j), (j, k), (k, i)]


def reverse_orientation(ordered: Tuple[int, ...]) -> bool:
    """True if ``ordered`` has odd parity relative to sorted order."""
    ref = sorted(ordered)
    perm = tuple(ref.index(v) for v in ordered)
    inversions = sum(
        1
        for a in range(len(perm))
        for b in range(a + 1, len(perm))
        if perm[a] > perm[b]
    )
    return bool(inversions % 2)


# --------------------------------------------------------------------------- #
# the complex
# --------------------------------------------------------------------------- #
class SimplicialComplex:
    """Vertices / oriented edges / faces / tetrahedra with group edge labels."""

    def __init__(self, group=None):
        self.group: Group = get_group(group if group is not None else "Z3")
        #: free-form bookkeeping (how a lattice was built, etc.); never read by dynamics
        self.metadata: dict = {}
        self._vertices: Dict[int, Vertex] = {}
        self._labels: Dict[Tuple[int, int], object] = {}
        self._realized: Dict[Tuple[int, int], bool] = {}
        self._faces: Set[Tuple[int, int, int]] = set()
        self._tets: Set[Tuple[int, int, int, int]] = set()
        # canonical sorted key -> ordered 4-tuple encoding the tetrahedron orientation
        self._tet_orders: Dict[Tuple[int, ...], Tuple[int, ...]] = {}
        self._next_vertex = 0

    # ------------------------------------------------------------- vertices
    def add_vertex(self, vertex_id: Optional[int] = None, **metadata) -> int:
        if vertex_id is None:
            vertex_id = self._next_vertex
        vertex_id = int(vertex_id)
        if vertex_id in self._vertices:
            self._vertices[vertex_id].metadata.update(metadata)
            return vertex_id
        self._vertices[vertex_id] = Vertex(vertex_id, dict(metadata))
        self._next_vertex = max(self._next_vertex, vertex_id + 1)
        return vertex_id

    def vertices(self) -> List[int]:
        """Sorted vertex ids.  Collection accessors are methods throughout: use
        ``vertices()``, ``edges()``, ``faces()``, ``tetrahedra()``."""
        return sorted(self._vertices)

    def vertex(self, vertex_id: int) -> Vertex:
        return self._vertices[vertex_id]

    def has_vertex(self, vertex_id: int) -> bool:
        return vertex_id in self._vertices

    # ---------------------------------------------------------------- edges
    @staticmethod
    def edge_key(u: int, v: int) -> Tuple[int, int]:
        if u == v:
            raise SimplicialError(f"degenerate edge {u}->{v}")
        return (u, v) if u < v else (v, u)

    def add_edge(self, u: int, v: int, label=None, realized: bool = True) -> EdgeView:
        self.add_vertex(u)
        self.add_vertex(v)
        key = self.edge_key(u, v)
        if key not in self._labels:
            stored = self.group.identity() if label is None else label
            self._labels[key] = self._canon_label(key, stored)
            self._realized[key] = bool(realized)
        elif label is not None:
            self.set_label(u, v, label)
        return EdgeView(self, u, v)

    def has_edge(self, u: int, v: int) -> bool:
        return self.edge_key(u, v) in self._labels

    def remove_edge(self, u: int, v: int, prune: bool = True) -> None:
        key = self.edge_key(u, v)
        self._labels.pop(key, None)
        self._realized.pop(key, None)
        if prune:
            self._prune_faces()
            self._prune_edges()

    def edges(self) -> List[Tuple[int, int]]:
        return sorted(self._labels)

    def n_edges(self) -> int:
        return len(self._labels)

    def label(self, u: int, v: int):
        """``A_uv``; returns the inverse when the stored orientation is ``v->u``."""
        key = self.edge_key(u, v)
        try:
            stored = self._labels[key]
        except KeyError:
            raise SimplicialError(f"edge {self._fmt(u, v)} not in complex") from None
        return stored if u == key[0] else self.group.inverse(stored)

    def set_label(self, u: int, v: int, value) -> None:
        key = self.edge_key(u, v)
        if key not in self._labels:
            raise SimplicialError(f"edge {self._fmt(u, v)} not in complex")
        stored = value if u == key[0] else self.group.inverse(value)
        self._validate_label(stored)
        self._labels[key] = stored

    def raw_label(self, u: int, v: int):
        """Label as stored (canonical orientation), no inversion.  Debugging aid."""
        return self._labels[self.edge_key(u, v)]

    def is_realized(self, u: int, v: int) -> bool:
        return self._realized.get(self.edge_key(u, v), False)

    def set_realized(self, u: int, v: int, value: bool) -> None:
        key = self.edge_key(u, v)
        if key not in self._labels:
            raise SimplicialError(f"edge {self._fmt(u, v)} not in complex")
        self._realized[key] = bool(value)

    def edge(self, u: int, v: int) -> EdgeView:
        if not self.has_edge(u, v):
            raise SimplicialError(f"edge {self._fmt(u, v)} not in complex")
        return EdgeView(self, u, v)

    def incident_edges(self, vertex_id: int) -> List[Tuple[int, int]]:
        return [k for k in self._labels if vertex_id in k]

    def adjacent(self, vertex_id: int, allowed=None) -> List[int]:
        """Neighbours of ``vertex_id`` in the 1-skeleton.

        ``allowed`` optionally restricts the returned neighbours to a vertex set
        (used by transport/BFS inside a single tetrahedron).
        """
        out = []
        for key in self._labels:
            if vertex_id not in key:
                continue
            other = key[1] if key[0] == vertex_id else key[0]
            if allowed is None or other in allowed:
                out.append(other)
        return sorted(out)

    # ---------------------------------------------------------------- faces
    def add_face(self, tri: Iterable[int], create_edges: bool = True) -> FaceView:
        verts = tuple(int(v) for v in tri)
        if len(set(verts)) != 3:
            raise SimplicialError(f"degenerate face {tri}")
        key = tuple(sorted(verts))
        if create_edges:
            for a, b in itertools.combinations(key, 2):
                self.add_edge(a, b)
        self._faces.add(key)
        return FaceView(self, verts)

    def has_face(self, tri: Iterable[int]) -> bool:
        try:
            key = tuple(sorted(int(v) for v in tri))
        except TypeError:  # pragma: no cover
            return False
        return len(key) == 3 and key in self._faces

    def remove_face(self, tri: Iterable[int], prune: bool = True) -> None:
        key = tuple(sorted(int(v) for v in tri))
        self._faces.discard(key)
        if prune:
            self._prune_edges()

    def faces(self) -> List[Tuple[int, int, int]]:
        return sorted(self._faces)

    def n_faces(self) -> int:
        return len(self._faces)

    def face(self, tri: Iterable[int]) -> FaceView:
        key = tuple(sorted(int(v) for v in tri))
        if key not in self._faces:
            raise SimplicialError(f"face {key} not in complex")
        return FaceView(self, key)

    def faces_around_edge(self, u: int, v: int) -> List[Tuple[int, int, int]]:
        key = self.edge_key(u, v)
        return [f for f in self._faces if key[0] in f and key[1] in f]

    # ----------------------------------------------------------- tetrahedra
    def add_tetra(
        self,
        verts: Iterable[int],
        create_subsimplices: bool = True,
        orientation: int = 1,
    ) -> TetraView:
        """Add a tetrahedron; ``orientation`` fixes which way is 'out'.

        ``+1`` takes sorted vertex order as positive, ``-1`` the opposite.  Call
        :meth:`orient_consistently` afterwards so neighbouring tetrahedra agree;
        without that, boundary faces do not cancel and region charges are meaningless.
        """
        key = tuple(sorted(int(v) for v in verts))
        if len(set(key)) != 4:
            raise SimplicialError(f"degenerate tetrahedron {verts}")
        if orientation not in (-1, 1):
            raise ValueError("orientation must be +1 or -1")
        if create_subsimplices:
            for face in tetra_faces(key):
                self.add_face(face)
        self._tets.add(key)
        self._tet_orders.setdefault(key, key if orientation == 1 else _flip(key))
        return TetraView(self, key)

    def tet_order(self, tet: Iterable[int]) -> Tuple[int, ...]:
        """The ordered vertex tuple encoding a tetrahedron's orientation."""
        key = tuple(sorted(int(v) for v in tet))
        return self._tet_orders.get(key, key)

    def set_tet_order(self, tet: Iterable[int], order: Tuple[int, ...]) -> None:
        key = tuple(sorted(int(v) for v in tet))
        if key not in self._tets:
            raise SimplicialError(f"tetrahedron {key} not in complex")
        if sorted(int(v) for v in order) != list(key):
            raise SimplicialError(f"order {order} is not a permutation of tet {key}")
        self._tet_orders[key] = tuple(int(v) for v in order)

    def orient_consistently(self, seed=None) -> int:
        """Choose tetrahedron orientations so that interior faces cancel.

        Purely combinatorial: start from one tetrahedron, walk the face-adjacency
        graph, and give each neighbour whichever parity makes their shared face carry
        opposite induced orientations.  No coordinates are consulted -- orientation
        here means only "on which side of this face does that tetrahedron sit".
        Returns the number of tetrahedra re-oriented; raises if the complex is not
        orientable.
        """
        tets = sorted(self._tets)
        if not tets:
            return 0
        by_face: Dict[Tuple[int, int, int], List[Tuple[int, ...]]] = {}
        for tet in tets:
            for face in tetra_faces(tet):
                by_face.setdefault(face, []).append(tet)

        start = tuple(sorted(int(v) for v in seed)) if seed is not None else tets[0]
        if start not in self._tets:
            raise SimplicialError(f"seed tetrahedron {start} not in complex")
        chosen: Dict[Tuple[int, ...], Tuple[int, ...]] = {start: self.tet_order(start)}
        queue, flipped = [start], 0
        while queue:
            current = queue.pop(0)
            signs = face_induced_signs(chosen[current])
            for face in tetra_faces(current):
                for neighbour in by_face[face]:
                    if neighbour in chosen:
                        continue
                    base = tuple(sorted(neighbour))
                    picked = None
                    for candidate in (base, _flip(base)):
                        if face_induced_signs(candidate)[face] == -signs[face]:
                            picked = candidate
                            break
                    if picked is None:  # pragma: no cover - defensive
                        raise SimplicialError(
                            f"cannot orient tetrahedron {list(neighbour)} against "
                            f"{list(current)} across face {list(face)}"
                        )
                    if picked != base:
                        flipped += 1
                    chosen[neighbour] = picked
                    queue.append(neighbour)
        for key, order in chosen.items():
            self._tet_orders[key] = order
        return flipped

    def has_tetra(self, verts: Iterable[int]) -> bool:
        key = tuple(sorted(int(v) for v in verts))
        return len(set(key)) == 4 and key in self._tets

    def remove_tetra(self, verts: Iterable[int], prune: bool = True) -> None:
        key = tuple(sorted(int(v) for v in verts))
        if key not in self._tets:
            raise SimplicialError(f"tetrahedron {key} not in complex")
        self._tets.discard(key)
        self._tet_orders.pop(key, None)
        if prune:
            self._prune_faces()
            self._prune_edges()

    def tetrahedra(self) -> List[Tuple[int, int, int, int]]:
        return sorted(self._tets)

    def n_tetrahedra(self) -> int:
        return len(self._tets)

    def tetra(self, verts: Iterable[int]) -> TetraView:
        key = tuple(sorted(int(v) for v in verts))
        if key not in self._tets:
            raise SimplicialError(f"tetrahedron {key} not in complex")
        return TetraView(self, key)

    def tets_around_face(self, tri: Iterable[int]) -> List[Tuple[int, int, int, int]]:
        key = tuple(sorted(int(v) for v in tri))
        return [t for t in self._tets if set(key).issubset(set(t))]

    def tets_around_edge(self, u: int, v: int) -> List[Tuple[int, int, int, int]]:
        key = self.edge_key(u, v)
        return [t for t in self._tets if key[0] in t and key[1] in t]

    # ------------------------------------------------------------ topology
    def boundary_faces(self) -> List[Tuple[int, int, int]]:
        """Faces contained in exactly one tetrahedron (boundary of a pure 3D region)."""
        out = []
        for face in self._faces:
            if len(self.tets_around_face(face)) == 1:
                out.append(face)
        return sorted(out)

    def interior_faces(self) -> List[Tuple[int, int, int]]:
        return sorted(f for f in self._faces if len(self.tets_around_face(f)) > 1)

    def shared_face(self, tet_a, tet_b) -> Optional[Tuple[int, int, int]]:
        """The triangle shared by two tetrahedra, or ``None``."""
        a = set(tuple(sorted(int(v) for v in tet_a)))
        b = set(tuple(sorted(int(v) for v in tet_b)))
        common = tuple(sorted(a & b))
        return common if len(common) == 3 else None

    def link_of_face(self, tri: Iterable[int]) -> Set[int]:
        """Vertices ``w`` such that ``tri + w`` is a tetrahedron."""
        key = set(int(v) for v in tri)
        return {v for t in self._tets if key.issubset(t) and len(t - key) == 1}

    def closed_star_tets(self, vertex_id: int) -> Set[Tuple[int, int, int, int]]:
        return {t for t in self._tets if vertex_id in t}

    def euler_characteristic(self) -> float:
        v = len(self._vertices)
        e = len(self._labels)
        f = len(self._faces)
        t = len(self._tets)
        return v - e + f - t

    # ------------------------------------------------------------- copying
    def copy(self) -> "SimplicialComplex":
        clone = SimplicialComplex(self.group)
        clone._vertices = {k: Vertex(v.id, dict(v.metadata)) for k, v in self._vertices.items()}
        clone._labels = dict(self._labels)
        clone._realized = dict(self._realized)
        clone._faces = set(self._faces)
        clone._tets = set(self._tets)
        clone._tet_orders = dict(self._tet_orders)
        clone._next_vertex = self._next_vertex
        clone.metadata = dict(self.metadata)
        return clone

    def labels_snapshot(self) -> Dict[Tuple[int, int], object]:
        """Copy of stored (canonically oriented) labels -- cheap state for search."""
        return dict(self._labels)

    # -------------------------------------------------------------- pruning
    def _prune_faces(self) -> None:
        """Drop faces no longer belonging to any tetrahedron."""
        used = set()
        for tet in self._tets:
            used.update(tetra_faces(tet))
        self._faces &= used

    def _prune_edges(self) -> None:
        """Drop edges no longer belonging to any face (hence no tetrahedron)."""
        used = set()
        for face in self._faces:
            for pair in itertools.combinations(face, 2):
                used.add(tuple(sorted(pair)))
        for key in list(self._labels):
            if key not in used:
                del self._labels[key]
                self._realized.pop(key, None)

    def prune_isolated_vertices(self) -> int:
        """Drop vertices that no longer belong to any edge.  Returns how many."""
        used = set()
        for key in self._labels:
            used.update(key)
        doomed = [v for v in self._vertices if v not in used]
        for vertex_id in doomed:
            del self._vertices[vertex_id]
        return len(doomed)

    # ------------------------------------------------------------- integrity
    def _canon_label(self, key, value):
        return value  # add_edge always passes the label for canonical orientation

    def _validate_label(self, value) -> None:
        if value not in self.group.elements:
            raise SimplicialError(
                f"label {value!r} is not an element of {self.group.name}"
            )

    def validate(self) -> None:
        """Assert every combinatorial and labelling invariant.  Raises on failure."""
        for key in self._labels:
            if len(set(key)) != 2:
                raise SimplicialError(f"degenerate edge {key}")
            for v in key:
                if v not in self._vertices:
                    raise SimplicialError(f"edge {key} references missing vertex {v}")
            if self._labels[key] not in self.group.elements:
                raise SimplicialError(f"edge {key} carries non-group label {self._labels[key]!r}")
        for face in self._faces:
            if len(set(face)) != 3:
                raise SimplicialError(f"degenerate face {face}")
            for a, b in itertools.combinations(face, 2):
                if not self.has_edge(a, b):
                    raise SimplicialError(f"face {face} missing edge {(a, b)}")
        for tet in self._tets:
            if len(set(tet)) != 4:
                raise SimplicialError(f"degenerate tetrahedron {tet}")
            for face in tetra_faces(tet):
                if face not in self._faces:
                    raise SimplicialError(f"tetrahedron {tet} missing face {face}")

    # ---------------------------------------------------------------- misc
    @staticmethod
    def _fmt(u: int, v: int) -> str:
        return f"{u}->{v}"

    def summary(self) -> str:
        return (
            f"SimplicialComplex(group={self.group.name}, V={len(self._vertices)}, "
            f"E={len(self._labels)}, F={len(self._faces)}, T={len(self._tets)}, "
            f"chi={self.euler_characteristic()})"
        )

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return f"<{self.summary()}>"


def _flip(key: Tuple[int, ...]) -> Tuple[int, ...]:
    """An odd permutation of ``key`` -- the opposite orientation."""
    order = list(key)
    order[0], order[1] = order[1], order[0]
    return tuple(order)


# --------------------------------------------------------------------------- #
# graph utilities shared by several modules
# --------------------------------------------------------------------------- #
def adjacency(edge_list: Iterable[Tuple[int, int]]) -> Dict[int, Set[int]]:
    adj: Dict[int, Set[int]] = defaultdict(set)
    for u, v in edge_list:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def connected_components(edge_list: Iterable[Tuple[int, int]]) -> List[Set[int]]:
    adj = adjacency(edge_list)
    seen: Set[int] = set()
    components: List[Set[int]] = []
    for start in sorted(adj):
        if start in seen:
            continue
        stack, component = [start], set()
        seen.add(start)
        while stack:
            node = stack.pop()
            component.add(node)
            for nxt in adj[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        components.append(component)
    return components


def spanning_tree(edge_list: Iterable[Tuple[int, int]], root: Optional[int] = None):
    """Return ``(tree_edges, non_tree_edges)`` for one connected component.

    Deterministic: edges are visited in sorted order so that downstream framed
    products are reproducible.
    """
    edges = sorted({tuple(sorted((int(u), int(v)))) for u, v in edge_list})
    adj = adjacency(edges)
    if not adj:
        return [], []
    start = root if root is not None else min(adj)
    tree: List[Tuple[int, int]] = []
    visited = {start}
    stack = [start]
    while stack:
        node = stack.pop(0)
        for nxt in sorted(adj[node]):
            key = (node, nxt) if node < nxt else (nxt, node)
            if nxt not in visited:
                visited.add(nxt)
                tree.append(key)
                stack.append(nxt)
    non_tree = [e for e in edges if e not in set(tree)]
    return tree, non_tree


def fundamental_cycles(edge_list: Iterable[Tuple[int, int]], root: Optional[int] = None):
    """Cycle basis of a connected graph as vertex loops.

    For every non-tree edge ``(u, v)`` the fundamental cycle is the loop
    ``u -> ... -> root -> ... -> v -> u`` obtained from the spanning tree.  Used
    for the external observables of a region (charge lives on cycles).
    """
    edges = sorted({tuple(sorted((int(u), int(v)))) for u, v in edge_list})
    adj = adjacency(edges)
    if not adj:
        return []
    start = root if root is not None else min(adj)
    tree, non_tree = spanning_tree(edges, root=start)
    parent = {start: None}
    order = [start]
    queue = [start]
    tree_adj = adjacency(tree)
    while queue:
        node = queue.pop(0)
        for nxt in sorted(tree_adj[node]):
            if nxt not in parent:
                parent[nxt] = node
                order.append(nxt)
                queue.append(nxt)

    def path_to_root(node):
        path = []
        while node is not None:
            path.append(node)
            node = parent.get(node)
        return path

    cycles = []
    for (u, v) in non_tree:
        if u not in parent or v not in parent:  # disconnected remainder
            continue
        up_from_u = path_to_root(u)                 # u -> ... -> root
        down_to_v = list(reversed(path_to_root(v)))  # root -> ... -> v
        loop = up_from_u + down_to_v[1:]             # drop duplicated root
        cycles.append(tuple(loop))                   # closes via the chord (v, u)
    return cycles
