"""Holographic entropy S(R) = log |I(dR)| -- the Jacobson-route ingredient (Layer-2 item 5).

Generalizes ``resolutions.resolution_space`` from cones to arbitrary regions, with the
SAME conventions:

* admissible interior resolution = assignment of labels to the region's INTERIOR edges
  (edges lying in no boundary face) such that every INTERIOR face has curvature inside its
  required conjugacy class; omitted classes default to flat. Boundary-face data is B itself.
* boundary-invisible equivalence = vertex gauges trivial on every vertex appearing in a
  boundary face, free elsewhere (for the cone this reduces exactly to the apex-only
  x_i -> nu^-1 x_i action -- spot-checked against resolutions.py in tests).

Ensembles for the area-law test:
* ``flat``     : all interior faces required flat. Vacuum control; expected topological.
* ``defect``   : curvature declared on a known set of interior faces (the seeded defect),
                 everything else flat -- entropy of hidden fillings around a pinned defect.
* ``free``     : every interior face unconstrained -- the VOLUME baseline.

Kernel module: no RNG, no scheduler. Ensemble label assignment happens in callers/tests.
Brute force over |G|^{|E_int|}: pass ``max_internal_edges`` to bound cost; oversized
regions are reported as skipped rather than silently truncated.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex
from .groups import Group
from .region import Region, region_from_tets

__all__ = [
    "RegionResolutionSpace", "interior_vertices", "enumerate_region_resolutions",
    "enumerate_region_resolutions_slice", "region_resolution_space",
    "metric_ball_tets", "area_law_study",
]


@dataclass(frozen=True)
class RegionResolutionSpace:
    count_raw: int
    count_physical: int
    n_boundary_faces: int
    n_tets: int
    n_interior_edges: int
    skipped_reason: Optional[str] = None

    @property
    def entropy(self) -> float:
        """S(R) = log |I(dR)| (natural log; 0 for the unique light-like filling)."""
        return math.log(self.count_physical) if self.count_physical > 0 else float("-inf")


def interior_vertices(cx: SimplicialComplex, region: Region) -> List[int]:
    """Vertices of R that appear in NO boundary face -- the free gauge degrees."""
    boundary_verts = {v for f in region.boundary_faces() for v in f}
    return sorted(v for v in region.vertices() if v not in boundary_verts)


def enumerate_region_resolutions(
    cx: SimplicialComplex,
    region: Region,
    flux_classes: Optional[Dict[Tuple[int, int, int], frozenset]] = None,
    max_internal_edges: int = 10,
) -> List[Tuple]:
    """All interior-edge assignments whose interior faces meet the required flux classes.

    ``flux_classes`` keys are interior face vertex-triples (canonical sorted order).
    Returns tuples of labels aligned with ``region.interior_edges()`` order.
    """
    group = cx.group
    int_edges = region.interior_edges()
    if len(int_edges) > max_internal_edges:
        raise ValueError(
            f"region has {len(int_edges)} interior edges > budget {max_internal_edges}"
        )

    required: Dict[Tuple[int, int, int], object] = {}
    identity_class = group.class_of(group.identity())
    for face in region.interior_faces():
        key = tuple(sorted(face))
        # CONVENTION (matches resolutions.py): omitted faces default to FLAT;
        # an explicit None value marks the face unconstrained.
        required[key] = identity_class if flux_classes is None else flux_classes.get(key, identity_class)

    snapshot = cx.labels_snapshot()

    def face_holonomy(i: int, j: int, k: int, labels: Dict):
        def lab(u, v):
            return labels[(u, v)] if u < v else group.inverse(labels[(v, u)])
        return group.multiply(group.multiply(lab(i, j), lab(j, k)), lab(k, i))

    solutions: List[Tuple] = []
    for assignment in itertools.product(group.elements, repeat=len(int_edges)):
        labels = dict(snapshot)
        for (u, v), value in zip(int_edges, assignment):
            labels[(u, v)] = value
        ok = True
        for face in region.interior_faces():
            cls = required[tuple(sorted(face))]
            if cls is None:
                continue
            phi = face_holonomy(*face, labels)
            if phi not in cls:
                ok = False
                break
        if ok:
            solutions.append(tuple(assignment))
    return solutions


def region_resolution_space(
    cx: SimplicialComplex,
    region: Region,
    flux_classes: Optional[Dict[Tuple[int, int, int], frozenset]] = None,
    max_internal_edges: int = 10,
    method: str = "brute",
    node_budget: int = 4_000_000,
) -> RegionResolutionSpace:
    """|I(dR)| for region R with current boundary data; gauge quotient at interior vertices.

    ``method="brute"`` enumerates |G|^|E_int| (exact, small regions).
    ``method="slice"`` runs the constraint-propagation solver: same solution set,
    cost driven by class sizes and constraint density instead of |G|^k -- this is what
    makes A4 core regions (14+ interior edges) tractable.
    """
    group = cx.group
    stats = dict(
        n_boundary_faces=len(region.boundary_faces()),
        n_tets=len(region.tets),
        n_interior_edges=len(region.interior_edges()),
    )
    try:
        if method == "slice":
            solutions = enumerate_region_resolutions_slice(
                cx, region, flux_classes, node_budget=node_budget
            )
        else:
            solutions = enumerate_region_resolutions(cx, region, flux_classes, max_internal_edges)
    except ValueError as exc:
        return RegionResolutionSpace(0, 0, skipped_reason=str(exc), **stats)

    int_edges = region.interior_edges()
    free_verts = interior_vertices(cx, region)
    boundary_verts = {v for f in region.boundary_faces() for v in f}

    def gauge_image(x: Tuple, lambdas: Dict[int, object]) -> Tuple:
        out = []
        for (u, v), value in zip(int_edges, x):
            lam_u = lambdas.get(u) if u in free_verts else None
            lam_v = lambdas.get(v) if v in free_verts else None
            left = group.identity() if lam_u is None else group.inverse(lam_u)
            right = group.identity() if lam_v is None else lam_v
            out.append(group.multiply(group.multiply(left, value), right))
        return tuple(out)

    canonical: Dict[Tuple, int] = {}
    for x in solutions:
        orbit = [
            gauge_image(x, dict(zip(free_verts, combo)))
            for combo in itertools.product(group.elements, repeat=len(free_verts))
        ]
        representative = min(orbit, key=repr)
        canonical[representative] = canonical.get(representative, 0) + 1

    return RegionResolutionSpace(
        count_raw=len(solutions), count_physical=len(canonical), **stats
    )


# --------------------------------------------------------------------------- slice solver

def enumerate_region_resolutions_slice(
    cx: SimplicialComplex,
    region: Region,
    flux_classes: Optional[Dict[Tuple[int, int, int], frozenset]] = None,
    node_budget: int = 4_000_000,
) -> List[Tuple]:
    """Exact solution enumeration by MRV backtracking with class propagation.

    Same conventions and same solution set as :func:`enumerate_region_resolutions`
    (cross-validated in tests), but cost scales with conjugacy-class sizes and
    constraint density rather than |G|^|E_int|: a face whose two other edges are
    known restricts the third to at most |C| values, so curved faces of class size 4
    branch by 4 (or collapse to 1 when flat), not by |G|=12.

    Raises ValueError when ``node_budget`` is exhausted (reported as skipped upstream,
    never silently truncated).
    """
    group = cx.group
    int_edges = region.interior_edges()
    k = len(int_edges)
    pos: Dict[Tuple[int, int], int] = {e: idx for idx, e in enumerate(int_edges)}

    identity_class = group.class_of(group.identity())
    required: Dict[Tuple[int, int, int], object] = {}
    for face in region.interior_faces():
        key = tuple(sorted(face))
        required[key] = (
            identity_class if flux_classes is None else flux_classes.get(key, identity_class)
        )

    snapshot = cx.labels_snapshot()

    def const_term(u: int, v: int):
        e = (min(u, v), max(u, v))
        value = snapshot[e]
        return value if u < v else group.inverse(value)

    # constraints: (terms, cls) with terms = [(edge_pos | None, sign, constant)] in face order
    constraints: List[Tuple[List[Tuple[Optional[int], int, object]], frozenset]] = []
    for face in region.interior_faces():
        cls = required[tuple(sorted(face))]
        if cls is None:
            continue  # unconstrained face imposes nothing
        i, j, kk = sorted(face)
        terms = []
        for (u, v) in ((i, j), (j, kk), (kk, i)):
            e = (min(u, v), max(u, v))
            if e in pos:
                p = pos[e]
                sign = 1 if u < v else -1
                terms.append((p, sign, None))
            else:
                terms.append((None, 1, const_term(u, v)))
        constraints.append((terms, cls))

    all_elements = tuple(group.elements)
    full_domain = frozenset(all_elements)
    assigned: List[Optional[object]] = [None] * k
    domains: List[frozenset] = [full_domain] * k
    solutions: List[Tuple] = []
    nodes = 0

    def term_value(term, index: int):
        p, sign, const = term
        value = const if p is None else assigned[index]
        if value is None:
            raise AssertionError("term_value on unassigned variable")
        return value if sign == 1 else group.inverse(value)

    def propagate() -> bool:
        """Forward-check: restrict domains from constraints; False on wipeout."""
        changed = True
        while changed:
            changed = False
            for terms, cls in constraints:
                unknowns = [idx for idx, (p, _, _) in enumerate(terms) if p is not None and assigned[p] is None]
                if len(unknowns) == 0:
                    prod = group.identity()
                    for term in terms:
                        prod = group.multiply(prod, term_value(term, term[0]))
                    if prod not in cls:
                        return False
                elif len(unknowns) == 1:
                    m = unknowns[0]
                    p_m, sign_m, _ = terms[m]
                    left = group.identity()
                    for term in terms[:m]:
                        if term[0] is None or assigned[term[0]] is not None:
                            left = group.multiply(left, term_value(term, term[0]))
                        else:  # earlier unknown -- cannot isolate; skip (MRV will assign it)
                            break
                    else:
                        right = group.identity()
                        for term in terms[m + 1:]:
                            if term[0] is None or assigned[term[0]] is not None:
                                right = group.multiply(right, term_value(term, term[0]))
                            else:
                                break
                        else:
                            # left * f(x) * right ∈ cls with f = id or inverse  =>  allowed set
                            allowed = set()
                            for c in cls:
                                target = group.multiply(group.inverse(left), group.multiply(c, group.inverse(right)))
                                allowed.add(target if sign_m == 1 else group.inverse(target))
                            new_domain = domains[p_m] & frozenset(allowed)
                            if not new_domain:
                                return False
                            if new_domain != domains[p_m]:
                                domains[p_m] = new_domain
                                changed = True
        return True

    def backtrack():
        nonlocal nodes
        nodes += 1
        if nodes > node_budget:
            raise ValueError(f"slice solver exceeded node budget {node_budget}")
        unassigned = [p for p in range(k) if assigned[p] is None]
        if not unassigned:
            solutions.append(tuple(assigned))
            return
        p = min(unassigned, key=lambda q: (len(domains[q]), q))  # MRV, deterministic tie-break
        for value in sorted(domains[p], key=repr):
            assigned[p] = value
            saved = list(domains)
            if propagate():
                backtrack()
            domains[:] = saved
            assigned[p] = None

    if propagate():
        backtrack()
    return solutions


# --------------------------------------------------------------------------- region families

def metric_ball_tets(cx: SimplicialComplex, center_tet: Tuple[int, ...], radius: int):
    """Tetrahedra within ``radius`` face-adjacency steps of ``center_tet``."""
    from collections import deque
    tets = cx.tetrahedra()
    tet_set = set(tets)
    if center_tet not in tet_set:
        raise ValueError("center tet not in complex")

    def neighbors(t):
        out = []
        for face in itertools.combinations(sorted(t), 3):
            for other in cx.tets_around_face(face):
                if other != t:
                    out.append(other)
        return out

    seen = {center_tet}
    frontier = deque([(center_tet, 0)])
    while frontier:
        t, d = frontier.popleft()
        if d == radius:
            continue
        for nb in neighbors(t):
            if nb not in seen:
                seen.add(nb)
                frontier.append((nb, d + 1))
    return tuple(sorted(seen))


def area_law_study(
    cx: SimplicialComplex,
    center_tet: Tuple[int, ...],
    radii: Sequence[int] = (1, 2, 3),
    defect_flux: Optional[Dict[Tuple[int, int, int], frozenset]] = None,
    max_internal_edges: int = 10,
):
    """S(R) vs |dR| and |R| over nested balls, for the three ensembles.

    Returns list of dicts with one row per (radius, ensemble). Rows whose region exceeds
    the interior-edge budget carry skipped_reason instead of numbers -- reported, not hidden.
    """
    rows = []
    for r in radii:
        tets = metric_ball_tets(cx, center_tet, r)
        region = region_from_tets(cx, tets, name=f"ball_r{r}")
        ensembles = {
            "flat": {},
            "defect": dict(defect_flux or {}),
            "free": {tuple(sorted(f)): None for f in region.interior_faces()},
        }
        # 'free' means unconstrained: represent by flux_classes=None and a sentinel pass
        for name, fc in ensembles.items():
            if name == "free":
                space = _free_space(cx, region)
            else:
                space = region_resolution_space(cx, region, fc or None, max_internal_edges)
            rows.append({"radius": r, "ensemble": name, **{
                "S": space.entropy, "boundary_faces": space.n_boundary_faces,
                "tets": space.n_tets, "interior_edges": space.n_interior_edges,
                "count_physical": space.count_physical, "skipped": space.skipped_reason,
            }})
    return rows


def _free_space(cx: SimplicialComplex, region: Region) -> RegionResolutionSpace:
    """Unconstrained interior: |Sol| = |G|^k; quotient by free-vertex gauge action."""
    group = cx.group
    k = len(region.interior_edges())
    free_verts = interior_vertices(cx, region)
    stats = dict(n_boundary_faces=len(region.boundary_faces()), n_tets=len(region.tets),
                 n_interior_edges=k)
    total = len(group.elements) ** k
    # Burnside: fixed assignments under each gauge element (edge fixed iff lambda_u^-1 x lambda_v = x
    # for every interior edge; count per-gauge by direct product over edges).
    fixed_total = 0
    for combo in itertools.product(group.elements, repeat=len(free_verts)):
        lambdas = dict(zip(free_verts, combo))
        n_fixed = 1
        for (u, v) in region.interior_edges():
            lu, lv = lambdas.get(u), lambdas.get(v)
            if lu is None and lv is None:
                n_fixed *= len(group.elements)  # both endpoints pinned: every label fixed
                continue
            a = group.identity() if lu is None else group.inverse(lu)
            b = group.identity() if lv is None else lv
            # count x with a * x * b == x  (conjugation-like equation)
            cnt = sum(
                1 for x in group.elements
                if group.multiply(group.multiply(a, x), b) == x
            )
            n_fixed *= cnt
        fixed_total += n_fixed
    orbits = fixed_total // (len(group.elements) ** len(free_verts))
    return RegionResolutionSpace(count_raw=total, count_physical=orbits, **stats)
