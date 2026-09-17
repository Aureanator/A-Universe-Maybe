r"""Internal resolution spaces: why matter is not light.

The tetrahedral boundary ``d(Delta^3)`` has no interior, so nothing can hide behind it. The
smallest body with genuine internal freedom is the **cone over that boundary**,
``v * d(Delta^3)`` -- one apex vertex joined to all four boundary vertices, giving four
internal edges ``x_i = A_{*i}`` and six interior faces ``(*, i, j)``.

Fix the external boundary data ``B`` (the six labels on ``d(Delta^3)``). An **internal
resolution** of ``B`` is an assignment of the four internal edges such that every interior
face's curvature lies in its prescribed flux class:

.. math::  \Phi_{(*ij)} = x_i\, A_{ij}\, x_j^{-1} \in c_{ij}

Two resolutions are physically the same if a gauge transformation that is invisible at the
boundary relates them -- only the apex carries freedom, ``lambda_* = nu``, ``lambda_i = e``:

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
