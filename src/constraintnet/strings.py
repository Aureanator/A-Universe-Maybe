"""Flux-string detection -- Layer-2 item 2, detector v1.

Physics premise (the dimensional audit): in 3+1D untwisted D(G) magnetic flux is a STRING,
not a point. The detector therefore looks for closed loops of curved faces via the dual
1-skeleton: nodes = tetrahedra, dual edges = shared primal faces; a curved face is the
dual edge it crosses. A component in which every tet touches exactly two component faces
is LOOP-LIKE (a string); anything else is sheet/junction -- reported as such, not forced.

Also ships the GF(3) FLUX SOLVABILITY engine: curvature of the form Phi = dA over Z3 is a
linear image; Gaussian elimination decides whether a prescribed face-curvature pattern is
realizable at all (and returns one A when it is). Corollary, derived rather than asserted:
a pattern with exactly ONE curved face has no solution -- isolated flux cannot exist; the
smallest realizable supports are closed dual loops. This is Bianchi's theorem as a rank
computation.

Kernel module: no RNG, no scheduler, no coordinates in any acceptance rule. (Grid metadata
on Kuhn vertices may be used ONLY for reporting/embedding, never here.)

Deferred (recipe in docs/LAYER2.md): PL knot/link invariants of detected loops via the
barycentric embedding; interferometric sector identification; loop-loop braiding phases.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex
from .groups import Group

__all__ = [
    "FluxString", "curved_face_set", "flux_string_components", "classify_component",
    "solve_flux_z3", "is_flux_realizable",
]


# --------------------------------------------------------------------------- detection

@dataclass(frozen=True)
class FluxString:
    faces: Tuple[Tuple[int, int, int], ...]      # curved faces in the component
    tets_touched: Tuple[Tuple[int, int, int, int], ...]
    kind: str                                    # "loop" | "sheet/junction"
    face_classes: Dict[str, int] = field(default_factory=dict)  # class_name -> count

    @property
    def length(self) -> int:                     # combinatorial loop length = #faces pierced
        return len(self.faces)


def curved_face_set(cx: SimplicialComplex) -> List[Tuple[int, int, int]]:
    """Faces whose holonomy is non-identity."""
    e = cx.group.identity()
    out = []
    for face in cx.faces():
        phi = cx.face_holonomy(face) if hasattr(cx, "face_holonomy") else _hol(cx, face)
        if phi != e:
            out.append(tuple(sorted(face)))
    return sorted(set(out))


def _hol(cx: SimplicialComplex, tri: Sequence[int]):
    g = cx.group
    i, j, k = tri

    def lab(u, v):
        return cx.label(u, v) if u < v else g.inverse(cx.label(v, u))
    return g.multiply(g.multiply(lab(i, j), lab(j, k)), lab(k, i))


def flux_string_components(cx: SimplicialComplex) -> List[FluxString]:
    """Cluster curved faces by shared-tet adjacency; classify loop vs sheet/junction.

    Two curved faces are adjacent when a single tetrahedron contains both (equivalently,
    the dual edges cross into a common dual vertex). A component is LOOP-LIKE iff every
    touched tet carries exactly two of its faces -- enter and exit, no endpoints, no
    branching. Isolated faces (touched by tets carrying only that one face) are endpoints:
    realizable only with sources, which the Bianchi/rank machinery forbids in bulk.
    """
    curved = curved_face_set(cx)
    if not curved:
        return []
    curved_set = set(curved)

    # adjacency via common tetrahedron
    face_tets: Dict[Tuple[int, int, int], List[Tuple[int, int, int, int]]] = {f: [] for f in curved}
    for tet in cx.tetrahedra():
        tets_faces = [tuple(sorted(t)) for t in itertools.combinations(sorted(tet), 3)]
        for f in tets_faces:
            if f in curved_set:
                face_tets[f].append(tet)

    adj: Dict[Tuple, set] = {f: set() for f in curved}
    tet_members: Dict[Tuple[int, int, int, int], List[Tuple]] = {}
    for f, tets in face_tets.items():
        for t in tets:
            tet_members.setdefault(t, []).append(f)

    # union-find over faces sharing tets
    parent = {f: f for f in curved}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for t, members in tet_members.items():
        for a, b in itertools.combinations(members, 2):
            union(a, b)

    groups: Dict[Tuple, List[Tuple]] = {}
    for f in curved:
        groups.setdefault(find(f), []).append(f)

    g = cx.group
    out: List[FluxString] = []
    for members in groups.values():
        faces = tuple(sorted(members))
        tets_touched = tuple(sorted({t for f in faces for t in face_tets[f]}))
        members_by_tet = {t: [mf for mf in tet_members[t] if mf in set(faces)]
                          for t in tets_touched}
        kind = classify_faces(faces, members_by_tet)
        class_counts: Dict[str, int] = {}
        for f in faces:
            phi = _hol(cx, f)
            if hasattr(g, "class_name"):
                name = g.class_name(phi)
            else:                                   # Z_n control groups: key by class size
                name = f"cls(size={len(g.conjugacy_class(phi))})"
            class_counts[name] = class_counts.get(name, 0) + 1
        out.append(FluxString(faces=faces, tets_touched=tets_touched, kind=kind,
                              face_classes=class_counts))
    return sorted(out, key=lambda s: (-s.length, s.faces[0]))


def classify_faces(faces: Iterable[Tuple[int, int, int]],
                   tet_members: Dict[Tuple[int, int, int, int], Sequence]) -> str:
    """Pure classifier: 'loop' iff every touched tet carries exactly two component faces.

    ``tet_members`` maps tetrahedron -> its faces that belong to the component.
    Enter-and-exit at every dual vertex: no endpoints, no branching.
    """
    face_set = set(faces)
    counts = [sum(1 for f in members if tuple(sorted(f)) in face_set) for members in tet_members.values()]
    if not counts or any(c != 2 for c in counts):
        return "sheet/junction"
    return "loop"


# --------------------------------------------------------------------------- GF(3) solvability

def _edge_index(cx: SimplicialComplex):
    edges = sorted({tuple(sorted((u, v))) for tri in cx.faces() for u, v in itertools.combinations(tri, 2)})
    return {e: i for i, e in enumerate(edges)}


def solve_flux_z3(cx: SimplicialComplex, flux_pattern: Dict[Tuple[int, int, int], int]):
    """Solve dA = phi over Z3 for prescribed face curvatures phi (0 = flat omitted).

    Returns a dict edge->Z3 label on success, or None when the pattern is not closed
    (rank test on the augmented system). Curvature of face (i,j,k) enters as
    A_ij + A_jk - A_ki... with signs from traversal vs canonical storage: an edge pair
    (u,v), u<v contributes +1 to a face-traversal term and -1 when traversed backwards.
    """
    edges = sorted({tuple(sorted((u, v))) for tri in cx.faces()
                    for u, v in itertools.combinations(tri, 2)})
    eidx = {e: i for i, e in enumerate(edges)}
    faces = sorted(set(flux_pattern) | {tuple(sorted(t)) for t in cx.faces()})
    rows, rhs = [], []
    for tri in faces:
        row = [0] * len(edges)
        i, j, k = tri
        for u, v in ((i, j), (j, k), (k, i)):
            key = tuple(sorted((u, v)))
            sign = 1 if u < v else -1
            row[eidx[key]] = (row[eidx[key]] + sign) % 3
        rows.append(row)
        rhs.append(int(flux_pattern.get(tri, 0)) % 3)

    x = _gauss_mod_p(rows, rhs, len(edges), p=3)
    if x is None:
        return None
    return {edges[i]: x[i] for i in range(len(edges))}


def is_flux_realizable(cx: SimplicialComplex, flux_pattern: Dict[Tuple[int, int, int], int]) -> bool:
    return solve_flux_z3(cx, flux_pattern) is not None


def _gauss_mod_p(rows: List[List[int]], rhs: List[int], n_vars: int, p: int):
    """Solve M x = b over Z_p. Returns one solution vector or None if inconsistent."""
    m = [row[:] + [b] for row, b in zip(rows, rhs)]
    pivots: List[int] = []
    r = 0
    for c in range(n_vars):
        pr = next((i for i in range(r, len(m)) if m[i][c] % p), None)
        if pr is None:
            continue
        m[r], m[pr] = m[pr], m[r]
        inv = pow(m[r][c], -1, p)
        m[r] = [(v * inv) % p for v in m[r]]
        for i in range(len(m)):
            if i != r and m[i][c]:
                factor = m[i][c]
                m[i] = [(a - factor * b) % p for a, b in zip(m[i], m[r])]
        pivots.append(c)
        r += 1
        if r == len(m):
            break
    # inconsistency: row of zeros with nonzero rhs
    for i in range(r, len(m)):
        if any(v % p for v in m[i][:n_vars]) is False and m[i][n_vars] % p:
            return None
    x = [0] * n_vars
    for i, c in enumerate(pivots):
        x[c] = m[i][n_vars] % p
    # verify (cheap insurance against sign slips)
    for row, b in zip(rows, rhs):
        if sum(a * xv for a, xv in zip(row, x)) % p != b:
            return None
    return x
