"""Local rewrites: elementary relabellings and Pachner moves.

Two families of moves exist in this engine.

**Elementary relabelling** (the specification's candidate move) multiplies one edge label
by a generator, ``A_e -> A_e g``.  Its cost is the word length of ``old^-1 * new``, i.e.
the minimum number of generator multiplications implementing it -- the primitive that
becomes mass in :mod:`constraintnet.motion`.

**Pachner moves** change the triangulation while keeping its boundary fixed, so they are
the natural "internal resolution" moves: the interior reorganises and the external
boundary does not notice.  A 2-3 move replaces two tetrahedra sharing a face by three
tetrahedra around a newly created edge (see ``docs/figures/pachner_2_3.svg``); 3-2 is its
exact inverse.

Neither family is *physical* on its own.  A move counts as a legitimate reduction only if
it preserves the region's :class:`~constraintnet.region.Appearance`; that test lives in
:mod:`constraintnet.dynamics`, and every caller must apply it before committing.
"""

from __future__ import annotations

import itertools
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex, tetra_faces
from .groups import Group

__all__ = [
    "Move",
    "MoveError",
    "propose_edge_move",
    "apply_move",
    "revert_move",
    "generator_distance",
    "find_pachner_2_3_sites",
    "apply_pachner_2_3",
    "find_pachner_3_2_sites",
    "apply_pachner_3_2",
]


class MoveError(Exception):
    """Raised when a proposed move is not applicable to the complex."""


# --------------------------------------------------------------------------- #
# moves
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Move:
    """A proposed (or committed) local rewrite.

    ``kind`` is ``"edge"``, ``"pachner23"`` or ``"pachner32"``.  ``payload`` carries the
    structured bookkeeping needed to undo combinatorial moves exactly (created/dropped
    edges and their labels).
    """

    kind: str
    edge: Optional[Tuple[int, int]] = None
    old_label: Any = None
    new_label: Any = None
    generator: Any = None
    removed: Tuple[Tuple[int, ...], ...] = ()
    added: Tuple[Tuple[int, ...], ...] = ()
    cost: int = 0
    payload: dict = field(default_factory=dict)

    # ------------------------------------------------------------------ text
    def describe(self, group: Optional[Group] = None) -> str:
        if self.kind == "edge" and self.edge is not None:
            u, v = self.edge
            if group is not None and hasattr(group, "format"):
                return f"A_{u}{v}: {group.format(self.old_label)} -> {group.format(self.new_label)}"
            return f"A_{u}{v}: {self.old_label} -> {self.new_label}"
        if self.kind == "pachner23":
            return (
                f"2->3  remove {[list(t) for t in self.removed]}  "
                f"add {[list(t) for t in self.added]}  new edge {self.payload.get('new_edge')}"
            )
        if self.kind == "pachner32":
            return (
                f"3->2  remove {[list(t) for t in self.removed]}  "
                f"add {[list(t) for t in self.added]}  dropped edge {self.payload.get('dropped_edge')}"
            )
        return f"{self.kind}"

    # -------------------------------------------------------------- support
    def support_edges(self) -> Tuple[Tuple[int, int], ...]:
        """Edges whose labels this move touches -- used to choose probe regions."""
        if self.kind == "edge" and self.edge is not None:
            return (self.edge,)
        out = set()
        for tet in tuple(self.removed) + tuple(self.added):
            for pair in itertools.combinations(sorted(tet), 2):
                out.add(tuple(sorted(pair)))
        return tuple(sorted(out))


# --------------------------------------------------------------------------- #
# elementary edge moves
# --------------------------------------------------------------------------- #
def generator_distance(group: Group, old, new) -> int:
    """Minimum generator steps taking ``old`` to ``new`` by right multiplication.

    The specification's ``generatorDistance(oldLabel, newLabel)`` and the seed of
    mass/inertia: relabelling by an element that is far in the word metric costs more.
    """
    return group.word_length(group.multiply(group.inverse(old), new))


def propose_edge_move(
    cx: SimplicialComplex,
    rng: random.Random,
    edges: Optional[Sequence[Tuple[int, int]]] = None,
    generators: Optional[Sequence] = None,
) -> Move:
    """Pick an edge and multiply its label by a generator: ``A_e -> A_e g``."""
    candidates = list(edges) if edges else cx.edges()
    if not candidates:
        raise MoveError("complex has no edges to relabel")
    u, v = candidates[rng.randrange(len(candidates))]
    gens = list(generators) if generators else list(cx.group.move_generators())
    g = gens[rng.randrange(len(gens))]
    old = cx.label(u, v)
    new = cx.group.multiply(old, g)
    return Move(
        kind="edge",
        edge=(u, v),
        old_label=old,
        new_label=new,
        generator=g,
        cost=generator_distance(cx.group, old, new),
    )


def apply_move(cx: SimplicialComplex, move: Move) -> None:
    """Apply an edge relabelling (combinatorial moves are applied by their own helpers)."""
    if move.kind != "edge" or move.edge is None:
        raise MoveError(f"apply_move handles edge moves only, got {move.kind!r}")
    cx.set_label(move.edge[0], move.edge[1], move.new_label)


def revert_move(cx: SimplicialComplex, move: Move) -> None:
    """Undo a committed move exactly, including combinatorial ones."""
    if move.kind == "edge":
        if move.edge is None:
            raise MoveError("edge move without an edge")
        cx.set_label(move.edge[0], move.edge[1], move.old_label)
        return
    if move.kind == "pachner23":
        new_edge = tuple(move.payload["new_edge"])
        apply_pachner_3_2(cx, new_edge, restore_label=None)
        return
    if move.kind == "pachner32":
        removed = [tuple(t) for t in move.removed]
        # the two surviving tetrahedra share face (a,b,c); rebuild around the dropped edge
        dropped = tuple(move.payload["dropped_edge"])
        label = move.payload.get("dropped_label")
        apply_pachner_2_3(cx, removed[0], removed[1], new_edge_label=label)
        return
    raise MoveError(f"cannot revert move kind {move.kind!r}")


# --------------------------------------------------------------------------- #
# Pachner 2 <-> 3
# --------------------------------------------------------------------------- #
def find_pachner_2_3_sites(cx: SimplicialComplex):
    """Interior faces whose replacement by a new edge is legal.

    Two conditions are checked: the face lies in exactly two tetrahedra, and the opposite
    vertices are not already joined -- otherwise the created edge would break the complex.
    """
    sites = []
    for face in cx.interior_faces():
        tets = sorted(cx.tets_around_face(face))
        if len(tets) != 2:
            continue
        a, b = tets
        opposite = sorted({v for v in a if v not in face} | {v for v in b if v not in face})
        if len(opposite) != 2:
            continue
        u, w = opposite
        if cx.has_edge(u, w):
            continue
        sites.append((a, b, face))
    return sites


def apply_pachner_2_3(
    cx: SimplicialComplex,
    tet_a: Sequence[int],
    tet_b: Sequence[int],
    new_edge_label=None,
) -> Move:
    """Replace two tetrahedra sharing a face by three around a newly created edge.

    The new edge's label is a genuine choice -- the move creates an internal degree of
    freedom -- and defaults to the identity.  It is recorded in ``Move.payload`` so that
    :func:`revert_move` can undo everything exactly.
    """
    face = cx.shared_face(tet_a, tet_b)
    if face is None:
        raise MoveError(f"{list(tet_a)} and {list(tet_b)} do not share a face")
    tets = sorted(cx.tets_around_face(face))
    if len(tets) != 2:
        raise MoveError(f"face {list(face)} belongs to {len(tets)} tetrahedra, need exactly 2")
    opposite = sorted({v for v in tets[0] if v not in face} | {v for v in tets[1] if v not in face})
    if len(opposite) != 2:
        raise MoveError("could not identify the two opposite vertices")
    u, w = opposite
    if cx.has_edge(u, w):
        raise MoveError(f"edge ({u},{w}) already exists; a 2->3 move would break the complex")

    label = cx.group.identity() if new_edge_label is None else new_edge_label
    a, b, c = face
    # The three replacement tetrahedra are (new edge) x (edge of the shared face):
    # {u,w,a,b}, {u,w,b,c}, {u,w,c,a}.  (Historical bug, referee audit: this line once
    # built the 3-vertex tuples (u,w,a),(u,w,b),(u,w,c), crashing mid-mutation.)
    added = (
        tuple(sorted((u, w, a, b))),
        tuple(sorted((u, w, b, c))),
        tuple(sorted((u, w, c, a))),
    )
    for tet in added:  # transactional guard: validate BEFORE any mutation
        if len(set(tet)) != 4:
            raise MoveError(f"replacement tetrahedron {tet} is degenerate; complex untouched")
    removed = (tuple(sorted(tets[0])), tuple(sorted(tets[1])))

    for tet in removed:
        cx.remove_tetra(tet, prune=False)
    cx.add_edge(u, w, label=label)
    for tet in added:
        cx.add_tetra(tet)
    cx.orient_consistently()
    cx.validate()

    return Move(
        kind="pachner23",
        removed=removed,
        added=added,
        cost=1,
        payload={"new_edge": (u, w), "new_label": label, "shared_face": face},
    )


def find_pachner_3_2_sites(cx: SimplicialComplex) -> List[Tuple[int, int]]:
    """Interior edges that can collapse back to two tetrahedra.

    Legal when exactly three tetrahedra surround the edge, they live on five vertices in
    total, and the three remaining ("equatorial") vertices form a triangle -- i.e. the
    neighbourhood really is the bipyramid of the 2-3 move.
    """
    sites = []
    for (u, w) in cx.edges():
        tets = sorted(cx.tets_around_edge(u, w))
        if len(tets) != 3:
            continue
        verts: set = set()
        for tet in tets:
            verts |= set(tet)
        equator = sorted(v for v in verts if v not in (u, w))
        if len(equator) != 3:
            continue
        a, b, c = equator
        if not (cx.has_edge(a, b) and cx.has_edge(b, c) and cx.has_edge(a, c)):
            continue
        sites.append((u, w))
    return sites


def apply_pachner_3_2(
    cx: SimplicialComplex,
    edge: Tuple[int, int],
    restore_label=None,
) -> Move:
    """Inverse of :func:`apply_pachner_2_3`: collapse three tetrahedra to two.

    ``restore_label`` is unused by the move itself but kept for symmetry with revert; the
    label of the disappearing edge is recorded so a later 2->3 can restore it exactly.
    """
    u, w = edge
    tets = sorted(cx.tets_around_edge(u, w))
    if len(tets) != 3:
        raise MoveError(f"edge {edge} has {len(tets)} incident tetrahedra, need 3")
    verts: set = set()
    for tet in tets:
        verts |= set(tet)
    equator = sorted(v for v in verts if v not in (u, w))
    if len(equator) != 3:
        raise MoveError("3->2 needs exactly three equatorial vertices")
    a, b, c = equator
    dropped_label = cx.label(u, w)

    removed = tuple(tets)
    added = (tuple(sorted((a, b, c, u))), tuple(sorted((a, b, c, w))))
    for tet in removed:
        cx.remove_tetra(tet, prune=False)
    cx.add_face((a, b, c))
    for tet in added:
        cx.add_tetra(tet)
    if not cx.tets_around_edge(u, w):
        cx.remove_edge(u, w)
    cx.orient_consistently()
    cx.validate()

    return Move(
        kind="pachner32",
        removed=removed,
        added=added,
        cost=1,
        payload={"dropped_edge": (u, w), "dropped_label": dropped_label, "new_face": (a, b, c)},
    )
