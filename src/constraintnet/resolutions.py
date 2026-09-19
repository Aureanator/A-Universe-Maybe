r"""Internal resolution spaces: why matter is not light.

The tetrahedral boundary ``d(Delta^3)`` has no interior, so nothing can hide behind it. The
smallest body with genuine internal freedom is the **cone over that boundary**,
``v * d(Delta^3)`` -- one apex vertex joined to all four boundary vertices, giving four
internal edges ``x_i = A_{*i}`` and six interior faces ``(*, i, j)``.

Fix the external boundary data ``B`` (the six labels on ``d(Delta^3)``). An **internal
resolution** of ``B`` is an assignment of the four internal edges such that every interior
face's curvature lies in its prescribed flux class:

.. math::  \Phi_{(*ij)} = x_i\, A_{ij}\, x_j^{-1} \in c_{ij}

.. warning::
   **Convention (referee audit P1, corrected in Round 3 after finding F1).** There are THREE
   gauge-quotient conventions for interiors over a fixed boundary, and they differ:

   1. **rigid** (this module's default): quotient by apex-only gauge ``x_i -> nu^-1 x_i``.
      This is an APPARATUS convention: the boundary frame is treated as physical data and
      boundary-vertex gauge transforms are forbidden by fiat.  It is NOT justified by "any
      gauge preserving B pointwise acts through the apex" -- that sentence was FALSE (R3 F1):
      for symmetric boundaries, e.g. flat B, constant ``lambda_i = mu`` fixes every boundary
      label pointwise (``mu^-1 e mu = e``) yet acts on interiors as ``x_i -> nu^-1 x_i mu``.
   2. **within-fibre** (``within_fibre_resolution_orbits``): quotient additionally by the
      POINTWISE STABILIZER of B -- all boundary gauges fixing B label-by-label (flat B: the 12
      constant transforms; with apex freedom a 144-element group).  The honest gauge count at
      a fixed boundary.
   3. **pooled** (``pooled_resolution_orbits``): full vertex-gauge orbits of labelled
      pairs (B,x), including gauge copies of B. Equality of appearance alone is not
      sufficient for gauge equivalence. Intersections with a fixed-B fibre are
      exactly its stabilizer orbits, so within-fibre and pooled counts agree.

   Measured on A4 cone patterns, five-face declaration: raw 72 -> rigid 6 -> within-fibre **2**
   (the stabilizer collapse happens INSIDE the fibre) -> pooled 2.  Star-3: raw 36 -> rigid 3
   -> within-fibre/pooled 1.  Seeded patterns over all 1728 tree-gauge boundaries: rigid |I|=4,
   pooled 1.  Quote which convention you mean.  The Z3 control is blind to every difference by
   construction (abelian conjugation is trivial).

Under the rigid apparatus convention, boundary frames are held fixed and only
the apex carries freedom, ``lambda_* = nu``, ``lambda_i = e``:

.. math::  x_i \mapsto nu^{-1} x_i

which conjugates each interior curvature and therefore preserves its class. The set of orbits
is the hidden internal state space

.. math::  \mathcal{I}(B) = \{\text{admissible } x\} / \{\text{boundary-invisible gauge}\}

and its size is what the specification asks for: ``|I(B)| == 1`` means the process is direct
(light-like, nothing hidden); ``|I(B)| > 1`` means the same external boundary admits several
inequivalent interiors -- matter. ``|I(B)| == 0`` means the boundary cannot be resolved at all
under those flux classes: a forbidden configuration.

A clean closed result falls out of the flat-flux case: requiring every interior face to be
flat forces ``x_j = x_i A_ij`` around the boundary, which is consistent **iff** ``B`` is flat
on every boundary triangle -- so curvature cannot be capped off by a single interior vertex.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex
from .groups import Group
from .holonomy import triangle_holonomy

__all__ = [
    "ResolutionSpace",
    "internal_edge_labels",
    "interior_face_curvatures",
    "enumerate_internal_resolutions",
    "resolution_space",
    "resolution_table",
    "materialise_resolution",
    "pointwise_stabilizer",
    "within_fibre_resolution_orbits",
    "pooled_resolution_orbits",
]

EdgeKey = Tuple[int, int]


@dataclass(frozen=True)
class ResolutionSpace:
    """The hidden internal state space of a fixed boundary."""

    count_raw: int                     # admissible assignments before quotienting
    count_physical: int                # |I(B)| -- gauge-inequivalent interiors
    orbits: Tuple[Tuple[Tuple, ...], ...] = ()
    representatives: Tuple[Tuple, ...] = ()
    flux_classes: Dict[str, str] = field(default_factory=dict)

    def kind(self) -> str:
        if self.count_physical == 0:
            return "forbidden (no internal resolution exists)"
        if self.count_physical == 1:
            return "direct / light-like (nothing hidden)"
        return f"matter-like ({self.count_physical} inequivalent interiors)"


def internal_edge_labels(cx: SimplicialComplex, apex: int, boundary: Sequence[int]) -> List:
    """The ``x_i`` = labels on the cone's internal edges, in ``boundary`` order."""
    return [cx.label(apex, vertex) for vertex in boundary]


def interior_face_curvatures(
    group: Group,
    boundary_labels: Dict[Tuple[int, int], object],
    apex_order: Sequence[int],
    x: Sequence[object],
) -> Dict[Tuple[int, int], object]:
    r"""Curvature of every interior face for a candidate assignment ``x``.

    ``Phi_{(*ij)} = x_i * A_ij * x_j^{-1}`` -- the apex-edge pair closing the triangle that
    contains the boundary edge ``(i, j)``.
    """
    index = {vertex: position for position, vertex in enumerate(apex_order)}
    out: Dict[Tuple[int, int], object] = {}
    for (i, j), a_ij in boundary_labels.items():
        xi = x[index[i]]
        xj = x[index[j]]
        out[(i, j)] = group.multiply(group.multiply(xi, a_ij), group.inverse(xj))
    return out


def enumerate_internal_resolutions(
    cx: SimplicialComplex,
    apex: int,
    boundary: Sequence[int],
    flux_classes: Optional[Dict[Tuple[int, int], frozenset]] = None,
) -> List[Tuple]:
    """All assignments of the internal edges whose interior faces meet the flux classes.

    ``flux_classes`` maps a boundary edge ``(i, j)`` to the conjugacy class required of the
    interior face ``(*, i, j)``.  Omitted entries default to the identity class (flat).
    """
    group = cx.group
    boundary_labels = {
        tuple(sorted((i, j))): cx.label(i, j)
        for i, j in itertools.combinations(boundary, 2)
    }
    required: Dict[Tuple[int, int], frozenset] = {}
    identity_class = group.class_of(group.identity())
    for edge in boundary_labels:
        required[edge] = (flux_classes or {}).get(edge, identity_class)

    solutions: List[Tuple] = []
    for x in itertools.product(group.elements, repeat=len(boundary)):
        curvatures = interior_face_curvatures(group, boundary_labels, boundary, x)
        if all(curvatures[edge] in required[edge] for edge in required):
            solutions.append(tuple(x))
    return solutions


def resolution_space(
    cx: SimplicialComplex,
    apex: int,
    boundary: Sequence[int],
    flux_classes: Optional[Dict[Tuple[int, int], frozenset]] = None,
) -> ResolutionSpace:
    """Compute ``|I(B)|`` for the cone over ``boundary`` with apex ``apex``."""
    group = cx.group
    solutions = enumerate_internal_resolutions(cx, apex, boundary, flux_classes)

    # boundary-invisible gauge: x_i -> nu^{-1} x_i for any nu in G (only the apex transforms)
    canonical: Dict[Tuple, List[Tuple]] = {}
    for x in solutions:
        orbit = tuple(
            tuple(group.multiply(group.inverse(nu), value) for value in x) for nu in group.elements
        )
        representative = min(orbit, key=repr)
        canonical.setdefault(representative, []).append(x)

    representatives = tuple(sorted(canonical, key=repr))
    flux_summary: Dict[str, str] = {}
    if flux_classes:
        for edge, cls in sorted(flux_classes.items()):
            representative = sorted(cls, key=repr)[0]
            name = group.class_name(representative) if hasattr(group, "class_name") else repr(representative)
            flux_summary[f"*{edge[0]}{edge[1]}"] = name

    return ResolutionSpace(
        count_raw=len(solutions),
        count_physical=len(canonical),
        orbits=tuple(tuple(sorted(orbit, key=repr)) for orbit in canonical.values()),
        representatives=representatives,
        flux_classes=flux_summary,
    )


def resolution_table(cx: SimplicialComplex, apex: int, boundary: Sequence[int]):
    r"""Census of every flux pattern the cone can support, in a single pass.

    Instead of running one search per flux assignment (``|G|^6`` searches), enumerate all
    ``|G|^4`` internal assignments once, record each one's curvature signature -- the tuple of
    conjugacy-class ids of its six interior faces -- together with its gauge-orbit canonical
    form, then group.  Returns ``{signature: {"raw": n, "physical": |I|}}`` sorted by how many
    hidden states a pattern admits.
    """
    group = cx.group
    classes = list(group.conjugacy_classes())
    edges = [tuple(sorted(pair)) for pair in itertools.combinations(boundary, 2)]
    boundary_labels = {edge: cx.label(*edge) for edge in edges}

    def class_id(element) -> int:
        for index, cls in enumerate(classes):
            if element in cls:
                return index
        raise AssertionError("curvature outside every conjugacy class")

    buckets: Dict[Tuple[int, ...], set] = {}
    raw_counts: Dict[Tuple[int, ...], int] = {}
    for x in itertools.product(group.elements, repeat=len(boundary)):
        curvatures = interior_face_curvatures(group, boundary_labels, boundary, x)
        signature = tuple(class_id(curvatures[edge]) for edge in edges)
        orbit = tuple(
            tuple(group.multiply(group.inverse(nu), value) for value in x) for nu in group.elements
        )
        buckets.setdefault(signature, set()).add(min(orbit, key=repr))
        raw_counts[signature] = raw_counts.get(signature, 0) + 1

    table = {
        signature: {"raw": raw_counts[signature], "physical": len(orbits)}
        for signature, orbits in buckets.items()
    }
    return {
        "edges": edges,
        "class_names": [
            group.class_name(sorted(cls, key=repr)[0]) if hasattr(group, "class_name") else str(sorted(cls, key=repr)[0])
            for cls in classes
        ],
        "entries": dict(
            sorted(table.items(), key=lambda kv: (-kv[1]["physical"], -kv[1]["raw"], kv[0]))
        ),
    }


def materialise_resolution(
    cx: SimplicialComplex, apex: int, boundary: Sequence[int], x: Sequence[object]
) -> None:
    """Write a resolution's internal labels into ``cx`` (boundary data untouched)."""
    for vertex, value in zip(boundary, x):
        cx.set_label(apex, vertex, value)


def pointwise_stabilizer(
    group: Group, boundary: Sequence[int], label_of
) -> List[Tuple]:
    """All boundary-vertex gauges ``(lambda_i)`` with ``lambda_i^-1 A_ij lambda_j == A_ij``
    for every boundary edge -- the gauge symmetries that fix B LABEL-BY-LABEL.

    For flat B these are exactly the 12 constant tuples (R3 finding F1); for generic B they
    shrink to the centralizer data and often to the identity alone.
    """
    elements = list(group.elements)
    edges = list(itertools.combinations(boundary, 2))
    stab: List[Tuple] = []
    for lams in itertools.product(elements, repeat=len(boundary)):
        ok = True
        for (i, j) in edges:
            li = lams[boundary.index(i)]
            lj = lams[boundary.index(j)]
            a = label_of(i, j)
            if group.multiply(group.multiply(group.inverse(li), a), lj) != a:
                ok = False
                break
        if ok:
            stab.append(tuple(lams))
    return stab


def within_fibre_resolution_orbits(
    cx: SimplicialComplex,
    apex: int,
    boundary: Sequence[int],
    flux_classes: Optional[Dict[Tuple[int, int], frozenset]] = None,
    budget: int = 20_000_000,
) -> int:
    r"""Gauge orbits of admissible interiors AT A FIXED BOUNDARY, quotienting by the honest
    in-fibre gauge group: apex freedom ``nu`` AND the pointwise stabilizer of B.

    Action: ``(nu, lambda) . x_i = nu^-1 x_i lambda_i``.  The rigid count (apex-only) is a
    sub-quotion of this one; they differ exactly when B has symmetry -- flat B over A4:
    raw 72 -> rigid 6 -> within-fibre **2** on the five-face declaration (R3 F1: the collapse
    happens inside the fibre, no boundary copies involved).  For asymmetric B the stabilizer
    is trivial and within-fibre == rigid.
    """
    group = cx.group
    elements = list(group.elements)
    index = {g: i for i, g in enumerate(elements)}
    sols = enumerate_internal_resolutions(cx, apex, boundary, flux_classes)
    stab = pointwise_stabilizer(group, boundary, lambda i, j: cx.label(i, j))
    cost = len(sols) * len(elements) * len(stab)
    if cost > budget:
        raise ValueError(f"within-fibre orbit count too expensive ({cost} ops > {budget})")
    reps = set()
    for x in sols:
        best = None
        for nu in elements:
            nu_inv = group.inverse(nu)
            for lams in stab:
                cand = tuple(
                    index[group.multiply(group.multiply(nu_inv, x[k]), lams[k])]
                    for k in range(len(boundary))
                )
                if best is None or cand < best:
                    best = cand
        reps.add(best)
    return len(reps)


def pooled_resolution_orbits(
    cx: SimplicialComplex,
    apex: int,
    boundary: Sequence[int],
    flux_classes: Optional[Dict[Tuple[int, int], frozenset]] = None,
    budget: int = 40_000_000,
) -> int:
    r"""Number of FULL-gauge orbits of admissible pairs ``(B, x)``, boundary vertices included.

    This is the pooled (appearance-relative) count: two resolutions count as the same physical
    interior when ANY vertex gauge transformation -- including at the four boundary vertices --
    carries one labelled cone to the other.  Merging happens across gauge copies of the
    boundary, and separately INSIDE a fixed fibre via the pointwise stabilizer of B (see
    :func:`within_fibre_resolution_orbits` and R3 finding F1); for A4 cone patterns this
    collapses rigid counts hard (star-3: 3 -> 1; five-face: 6 -> 2; seeded 4 -> 1).  See the
    module-level convention warning before quoting either number.

    Cost is ``|solutions| * |G|^5`` worst case; raises ``ValueError`` past ``budget``.
    """
    group = cx.group
    elements = list(group.elements)
    n = len(elements)
    index = {g: i for i, g in enumerate(elements)}
    mul = [[index[group.multiply(a, b)] for b in elements] for a in elements]
    inv = [index[group.inverse(a)] for a in elements]

    boundary_edges = [tuple(sorted(pair)) for pair in itertools.combinations(boundary, 2)]
    b0 = tuple(index[cx.label(i, j)] for (i, j) in boundary_edges)
    pos = {e: k for k, e in enumerate(boundary_edges)}

    def oriented(bt: Tuple[int, ...], i: int, j: int) -> int:
        # boundary vertices are compared by their position in `boundary` order (orientation)
        ki, kj = boundary.index(i), boundary.index(j)
        key = tuple(sorted((i, j)))
        g = bt[pos[key]]
        return g if ki < kj else inv[g]

    def curvature_classes_of(bt, xt) -> Tuple[int, ...]:
        out = []
        for (i, j) in boundary_edges:
            xi = xt[boundary.index(i)]
            xj = xt[boundary.index(j)]
            a_ij = oriented(bt, i, j)
            c = mul[mul[xi][a_ij]][inv[xj]]
            out.append(c)
        return tuple(out)

    identity_class = group.class_of(group.identity())
    required: Dict[Tuple[int, int], frozenset] = {}
    for edge in boundary_edges:
        required[edge] = (flux_classes or {}).get(edge, identity_class)

    sols = []
    elems = elements
    for x in itertools.product(elems, repeat=len(boundary)):
        curvatures = interior_face_curvatures(group, {
            edge: cx.label(*edge) for edge in boundary_edges
        }, boundary, x)
        if all(curvatures[edge] in required[edge] for edge in required):
            sols.append(tuple(index[v] for v in x))

    total_cost = len(sols) * (n ** 5)
    if total_cost > budget:
        raise ValueError(
            f"pooled orbit count too expensive ({total_cost} ops > budget {budget}); "
            f"restrict the declaration or sample externally"
        )

    vertex_order = list(boundary) + [apex]
    reps = set()
    for xt in sols:
        best = None
        for lam in itertools.product(range(n), repeat=5):
            lam_map = {v: lam[k] for k, v in enumerate(vertex_order)}
            bt = []
            for (i, j) in boundary_edges:
                a = oriented(b0, i, j)
                g = mul[mul[inv[lam_map[i]]][a]][lam_map[j]]
                ki, kj = boundary.index(i), boundary.index(j)
                bt.append(g if ki < kj else inv[g])
            xt2 = []
            for v in boundary:
                a = xt[boundary.index(v)]  # A_{*v} stored apex->v
                g = mul[mul[inv[lam_map[apex]]][a]][lam_map[v]]
                xt2.append(g)
            cand = (tuple(bt), tuple(xt2))
            if best is None or cand < best:
                best = cand
        reps.add(best)
    return len(reps)
