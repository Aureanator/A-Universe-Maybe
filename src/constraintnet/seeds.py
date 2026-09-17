"""Combinatorial seeds: the shapes the simulator is allowed to start from.

Everything here is pure combinatorics plus optional *visualization metadata*.  Grid
coordinates attached to vertices are bookkeeping for the renderer only; no dynamics
code reads them (enforced by ``tests/test_no_coordinate_teleportation.py``).
"""

from __future__ import annotations

import itertools
import random
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex
from .groups import Group, get_group

__all__ = [
    "TETRA_TREE",
    "TETRA_FREE_EDGES",
    "make_tetrahedron_boundary",
    "make_single_tetrahedron",
    "make_cone_over_tetrahedron",
    "make_bipyramid",
    "kuhn_ball",
    "stacked_ball",
    "randomize_labels",
]

# Spanning tree of the tetrahedron 1-skeleton used for gauge fixing: A01 = A12 = A23 = e
TETRA_TREE: Tuple[Tuple[int, int], ...] = ((0, 1), (1, 2), (2, 3))
# The three independent labels left after that fixing: A02, A03, A13
TETRA_FREE_EDGES: Tuple[Tuple[int, int], ...] = ((0, 2), (0, 3), (1, 3))


def _new(group) -> SimplicialComplex:
    return SimplicialComplex(get_group(group))


def make_tetrahedron_boundary(group="A4") -> SimplicialComplex:
    r"""``d(Delta^3)``: 4 vertices, 6 edges, 4 faces, no tetrahedra.

    This is the milestone-1 seed -- the minimal relational structure that supports
    nontrivial local cyclic closure.
    """
    cx = _new(group)
    for u, v in itertools.combinations(range(4), 2):
        cx.add_edge(u, v)
    for tri in itertools.combinations(range(4), 3):
        cx.add_face(tri)
    cx.validate()
    return cx


def make_single_tetrahedron(group="A4") -> SimplicialComplex:
    cx = _new(group)
    cx.add_tetra((0, 1, 2, 3))
    cx.validate()
    return cx


def make_cone_over_tetrahedron(
    group="A4", apex: int = 4, seed_labels=None
) -> Tuple["SimplicialComplex", int, List[int]]:
    r"""The cone ``v * d(Delta^3)``, i.e. the four-simplex ``Delta^4``.

    Boundary vertices are ``0..3``; the interior vertex is ``apex`` (default 4), joined to all
    four of them. Those four edges are genuine internal variables -- the smallest structure in
    which an external boundary can hide more than one resolution.

    Returns ``(complex, apex, boundary_vertices)``.
    """
    cx = _new(group)
    for u, v in itertools.combinations(range(4), 2):
        cx.add_edge(u, v)
    for tri in itertools.combinations(range(4), 3):
        cx.add_face(tri)
    cx.add_vertex(apex)
    for vertex in range(4):
        cx.add_edge(apex, vertex)
    for tri in itertools.combinations(range(4), 3):
        cx.add_tetra((apex,) + tri)
    if seed_labels is not None:
        import random as _random

        rng = _random.Random(seed_labels)
        for (u, v) in cx.edges():
            if u == apex or v == apex:
                continue  # internal labels are chosen by the resolution search
            cx._labels[(u, v)] = rng.choice(cx.group.elements)  # noqa: SLF001
    cx.orient_consistently()
    cx.validate()
    return cx, apex, list(range(4))


def make_bipyramid(group="A4", triangulation: str = "two") -> SimplicialComplex:
    """The triangular bipyramid on vertices ``a,b,c`` (equator) and ``d,e`` (apices).

    ``triangulation="two"``   : tets ``{0,1,2,3}``, ``{0,1,2,4}`` -- internal face ``abc``.
    ``triangulation="three"`` : tets around the new edge ``de`` -- three tetrahedra.

    Both have the *same* six-triangle boundary and Euler characteristic 1; they are
    the two sides of a Pachner 2-3 move (see ``docs/figures/pachner_2_3.svg``).
    """
    vertex_map = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}
    if triangulation == "two":
        tets = [(0, 1, 2, 3), (0, 1, 2, 4)]
    elif triangulation == "three":
        tets = [
            tuple(sorted((vertex_map["a"], vertex_map["b"], vertex_map["d"], vertex_map["e"]))),
            tuple(sorted((vertex_map["b"], vertex_map["c"], vertex_map["d"], vertex_map["e"]))),
            tuple(sorted((vertex_map["c"], vertex_map["a"], vertex_map["d"], vertex_map["e"]))),
        ]
    else:
        raise ValueError(f"unknown triangulation {triangulation!r}")
    cx = _new(group)
    for tet in tets:
        cx.add_tetra(tet)
    cx.orient_consistently()
    cx.validate()
    return cx


def kuhn_ball(group="A4", n: int = 2, seed_labels: bool = False) -> SimplicialComplex:
    r"""Triangulated 3-ball: the Kuhn (Freudenthal) subdivision of an ``n^3`` cube grid.

    Each unit cube is split into six tetrahedra along its main diagonal using all
    permutations of the axis order; intersections of these tetrahedra are always
    faces, so the result is a genuine simplicial complex with a 2-sphere boundary.

    Vertex metadata ``grid=(i, j, k)`` is attached for rendering only.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    cx = _new(group)

    def vertex_id(cell: Tuple[int, int, int]) -> int:
        i, j, k = cell
        return i + (n + 1) * j + (n + 1) ** 2 * k

    for cell in itertools.product(range(n), repeat=3):
        cx.add_vertex(vertex_id(cell), grid=cell)

    axes = (0, 1, 2)
    unit_vectors = {0: (1, 0, 0), 1: (0, 1, 0), 2: (0, 0, 1)}
    for cell in itertools.product(range(n), repeat=3):
        for order in itertools.permutations(axes):
            points = [cell]
            current = list(cell)
            for axis in order:
                ux, uy, uz = unit_vectors[axis]
                current = [current[0] + ux, current[1] + uy, current[2] + uz]
                points.append(tuple(current))
            tet = tuple(sorted(vertex_id(p) for p in points))
            cx.add_tetra(tet)
    # attach grid metadata for every vertex that appeared
    for v in cx.vertices():
        side = n + 1
        k, rem = divmod(v, side * side)
        j, i = divmod(rem, side)
        cx.vertex(v).metadata.setdefault("grid", (i, j, k))
    flipped = cx.orient_consistently()
    cx.metadata["orientation_flips"] = flipped
    if seed_labels:
        randomize_labels(cx)
    cx.validate()
    return cx


def stacked_ball(group="A4", tetrahedra: int = 8) -> SimplicialComplex:
    """A ball built by stacking tetrahedra onto boundary faces (dual-tree complex).

    Useful when a specific small triangulation is wanted; every stacked ball is a
    3-ball and all of its Pachner moves are easy to reason about.
    """
    cx = _new(group)
    cx.add_tetra((0, 1, 2, 3))
    next_vertex = 4
    while cx.n_tetrahedra() < tetrahedra:
        boundary = cx.boundary_faces()
        if not boundary:  # pragma: no cover - a ball always has boundary faces
            break
        face = sorted(boundary)[0]
        cx.add_tetra((face[0], face[1], face[2], next_vertex))
        next_vertex += 1
    cx.orient_consistently()
    cx.validate()
    return cx


def randomize_labels(cx: SimplicialComplex, seed: Optional[int] = None, generators_only: bool = False) -> None:
    """Assign uniformly random constraint labels to every edge.

    ``generators_only`` restricts labels to the generator set plus inverses, which is
    the natural "elementary" state space used by the move dynamics.
    """
    rng = random.Random(seed)
    choices = cx.group.move_generators() if generators_only else cx.group.elements
    for (a, b) in cx.edges():
        cx._labels[(a, b)] = rng.choice(choices)  # noqa: SLF001 - canonical orientation write
