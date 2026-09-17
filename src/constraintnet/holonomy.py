"""Holonomy: curvature on faces, charge on cycles.

Two distinct gauge-invariant quantities are computed here and they must not be
confused (see ``docs/PHYSICS_NOTES.md`` section 2):

* **Curvature** of a triangular face ``(i,j,k)``::

      Phi_ijk = A_ij * A_jk * A_ki

  Under a gauge transformation it maps to ``lambda_i^{-1} Phi_ijk lambda_i``, so its
  *conjugacy class* is invariant.

* **Charge** of a closed cycle ``C``::

      Q_C = Phi_C = prod_{(u,v) in C} A_uv

  which transforms by conjugation at the basepoint, hence again has an invariant
  conjugacy class.

Why charge cannot be "curvature summed through a closed surface"
---------------------------------------------------------------
For abelian groups it is *identically zero*: every edge of a closed surface lies in
exactly two faces with opposite induced orientations, so all labels cancel --

    Phi_[123] - Phi_[023] + Phi_[013] - Phi_[012] == 0   for every labelling,

which is ``d^2 = 0`` read additively (verified numerically in
``tests/test_bianchi.py``).  Curvature of the form ``Phi = dA`` is therefore a
"magnetic" quantity with no net flux: **charge must be measured on cycles whose
constraint fails to close**, exactly as the specification defines it.

For non-abelian groups the surface sum is not even well defined without extra
framing, and the naive transported-and-ordered product is *not* an identity (checked
empirically for ``A_4``); :func:`bianchi_defect` therefore refuses non-abelian groups
instead of reporting a meaningless number.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .complex import FaceView, SimplicialComplex, face_induced_signs, triangle_edges
from .groups import Group

__all__ = [
    "triangle_holonomy",
    "face_holonomy",
    "path_holonomy",
    "loop_holonomy",
    "curvature_map",
    "curvature_classes",
    "same_conjugacy_class",
    "is_trivial",
    "transport_to",
    "bianchi_defect",
]


def _as_triple(face) -> Tuple[int, int, int]:
    if isinstance(face, FaceView):
        return face.vertices  # type: ignore[return-value]
    triple = tuple(int(v) for v in face)
    if len(set(triple)) != 3:
        raise ValueError(f"not a triangle: {face!r}")
    return triple  # type: ignore[return-value]


def triangle_holonomy(cx: SimplicialComplex, tri) -> object:
    """``A_ij * A_jk * A_ki`` for the oriented triangle ``(i, j, k)``."""
    i, j, k = _as_triple(tri)
    group = cx.group
    a = cx.label(i, j)
    b = cx.label(j, k)
    c = cx.label(k, i)
    return group.multiply(group.multiply(a, b), c)


def face_holonomy(cx: SimplicialComplex, face) -> object:
    """Spec-facing alias for :func:`triangle_holonomy`."""
    return triangle_holonomy(cx, face)


def path_holonomy(cx: SimplicialComplex, vertices: Sequence[int]):
    """Ordered product of labels along an open path ``v0 -> v1 -> ... -> vn``."""
    group = cx.group
    result = group.identity()
    for u, v in zip(vertices, vertices[1:]):
        if not cx.has_edge(u, v):
            raise KeyError(f"path uses missing edge {u}->{v}")
        result = group.multiply(result, cx.label(u, v))
    return result


def loop_holonomy(cx: SimplicialComplex, loop: Sequence[int]):
    """Holonomy of a closed vertex loop ``[v0, ..., vn]`` (implicitly ``vn -> v0``).

    The result is based at ``v0``; under gauge transformation it maps to
    ``lambda_v0^{-1} * Phi * lambda_v0``, so its conjugacy class is invariant.
    """
    if len(loop) < 2:
        raise ValueError(f"loop too short: {loop!r}")
    vertices = [int(v) for v in loop]
    if vertices[0] == vertices[-1]:
        vertices = vertices[:-1]
    closed = vertices + [vertices[0]]
    return path_holonomy(cx, closed)


def curvature_map(
    cx: SimplicialComplex, faces: Optional[Iterable] = None
) -> Dict[Tuple[int, int, int], object]:
    """Face holonomies for all (or selected) faces, keyed by canonical face."""
    faces = cx.faces() if faces is None else list(faces)
    out: Dict[Tuple[int, int], object] = {}
    for face in faces:
        triple = _as_triple(face)
        out[tuple(sorted(triple))] = triangle_holonomy(cx, triple)
    return dict(out)


def curvature_classes(
    cx: SimplicialComplex, faces: Optional[Iterable] = None
) -> Dict[Tuple[int, int, int], frozenset]:
    """Conjugacy class of each face holonomy -- the gauge-invariant curvature data."""
    group = cx.group
    return {face: group.class_of(value) for face, value in curvature_map(cx, faces).items()}


def same_conjugacy_class(group: Group, a, b) -> bool:
    """The legitimacy predicate used by every conservation test in the project."""
    return group.class_of(a) == group.class_of(b)


def is_trivial(group: Group, a) -> bool:
    return a == group.identity()


# --------------------------------------------------------------------------- #
# Bianchi identity (abelian): why charge cannot be a surface sum
# --------------------------------------------------------------------------- #
def transport_to(
    cx: SimplicialComplex, vertex_from: int, vertex_to: int, allowed: Optional[set] = None
):
    """Parallel transport along the shortest deterministic path in the 1-skeleton.

    Returns the product of labels from ``vertex_from`` to ``vertex_to``; ties are
    broken by sorted vertex order so results are reproducible.  ``allowed`` restricts
    intermediate vertices (used when staying inside one tetrahedron).
    """
    if vertex_from == vertex_to:
        return cx.group.identity()
    allowed_set = None if allowed is None else set(allowed)
    frontier = [[vertex_from]]
    visited = {vertex_from}
    while frontier:
        next_frontier = []
        for path in sorted(frontier, key=lambda p: (len(p), list(p))):
            tail = path[-1]
            for nxt in sorted(cx.adjacent(tail, allowed=allowed_set)):
                if nxt in visited:
                    continue
                candidate = path + [nxt]
                if nxt == vertex_to:
                    return path_holonomy(cx, candidate)
                visited.add(nxt)
                next_frontier.append(candidate)
        frontier = next_frontier
    raise KeyError(f"no path from {vertex_from} to {vertex_to}")


def bianchi_defect(cx: SimplicialComplex) -> float:
    """Maximal violation of the abelian Bianchi identity, over all tetrahedra.

    For each tetrahedron the signed product of its four face curvatures is computed;
    because curvature is exact (``Phi = dA``) it must be the identity for *every*
    labelling.  Returns ``0.0`` when that holds everywhere and ``1.0`` otherwise, so
    it can be used directly as a hard assertion.

    Raises :class:`TypeError` for non-abelian groups: there the surface product needs
    framing data (basepoint, tree, ordering) and the naive choice is not an identity,
    which is precisely why charge in this project is defined on cycles instead.
    """
    group = cx.group
    if not group.is_abelian():
        raise TypeError(
            f"bianchi_defect is an abelian statement; {group.name} needs framed "
            "surface products -- use Region.appearance() (cycle charges) instead"
        )
    worst = 0.0
    for tet in cx.tetrahedra():
        signs = face_induced_signs(cx.tet_order(tet))
        product = group.identity()
        for face, sign in sorted(signs.items()):
            value = triangle_holonomy(cx, tuple(sorted(face)))
            if sign < 0:
                value = group.inverse(value)
            product = group.multiply(product, value)
        worst = max(worst, 0.0 if product == group.identity() else 1.0)
    return worst
