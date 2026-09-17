"""Interaction by gluing: fiber products of internal resolution spaces (kernel, R3).

Two objects sharing a boundary face F must agree on the constraint flux threading every
edge of F.  For cones with apex labels ``x`` (object A) and ``y`` (probe B), glued along
triangle F with shared boundary labels ``A_vw``, the compatibility condition is

    x_v · A_vw · x_w⁻¹  ==  y_v · A_vw · y_w⁻¹      for each edge (v,w) of F

-- both sides must present the SAME transported curvature through the shared face.
The joint internal state space is the fiber product I_A ×_F I_B; when it is EMPTY the
interaction is forbidden: this is the primitive exclusion mechanism, counting-based and
deterministic -- no force, no potential, just incompatible bookkeeping.

Phase-locked actualization (Section 4 of the driver design): given the current internal
state and a set of joint-allowed states, ``actualize_min_cost`` selects the minimal-cost
element deterministically (word metric, tie-break by repr).  This is the ONLY state
selection anywhere -- no collapse postulate.
"""

from __future__ import annotations

import itertools
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from .groups import Group

__all__ = [
    "face_flux",
    "compatible_on_shared_face",
    "fiber_product",
    "meshable_phases",
    "actualize_min_cost",
]

EdgeKey = Tuple[int, int]


def face_flux(group: Group, apex_label_v, a_vw, apex_label_w):
    """Transported curvature through shared edge (v,w): x_v A_vw x_w^-1."""
    return group.multiply(group.multiply(apex_label_v, a_vw), group.inverse(apex_label_w))


def compatible_on_shared_face(
    group: Group,
    x: Sequence,
    y: Sequence,
    shared_edges: Sequence[Tuple[EdgeKey, object]],
    index_x: Dict[int, int],
    index_y: Dict[int, int],
) -> bool:
    """Do internal states x and y agree on the flux through every edge of the shared face?

    ``shared_edges`` lists ((v,w), A_vw); ``index_*`` map boundary vertex -> slot in x/y.
    """
    for (v, w), a_vw in shared_edges:
        if face_flux(group, x[index_x[v]], a_vw, x[index_x[w]]) != face_flux(
            group, y[index_y[v]], a_vw, y[index_y[w]]
        ):
            return False
    return True


def fiber_product(
    group: Group,
    states_a: Iterable[Sequence],
    states_b: Iterable[Sequence],
    shared_edges: Sequence[Tuple[EdgeKey, object]],
    index_x: Dict[int, int],
    index_y: Dict[int, int],
) -> List[Tuple[tuple, tuple]]:
    """All jointly resolvable pairs (a, b).  Empty list == forbidden channel."""
    states_b = [tuple(b) for b in states_b]
    out: List[Tuple[tuple, tuple]] = []
    for a in states_a:
        a = tuple(a)
        for b in states_b:
            if compatible_on_shared_face(group, a, b, shared_edges, index_x, index_y):
                out.append((a, b))
    return out


def meshable_phases(
    group: Group,
    cycle_a: Sequence[Sequence],
    cycle_b: Sequence[Sequence],
    shared_edges: Sequence[Tuple[EdgeKey, object]],
    index_x: Dict[int, int],
    index_y: Dict[int, int],
) -> List[List[bool]]:
    """Phase x phase meshability matrix: entry (i,j) = joint non-empty at those phases.

    For a single-cycle (equidistributed) sigma this matrix IS the exact interaction
    measure -- no sampling.  Row means give per-phase absorption probabilities.
    """
    return [
        [
            compatible_on_shared_face(group, a, b, shared_edges, index_x, index_y)
            for b in cycle_b
        ]
        for a in cycle_a
    ]


def actualize_min_cost(
    group: Group,
    current: Sequence,
    allowed: Iterable[Sequence],
):
    """Deterministic state selection: minimal total word cost from ``current``, tie-break repr.

    Cost of moving coordinate-wise from current to target = Σ wl(current_i⁻¹ target_i);
    this is the reconfiguration cost that doubles as the mass proxy (spec M5 seed).
    Returns None when ``allowed`` is empty: the interaction cannot be actualized.
    """
    allowed = [tuple(a) for a in allowed]
    if not allowed:
        return None

    def cost(target):
        return sum(
            group.word_length(group.multiply(group.inverse(c), t)) for c, t in zip(current, target)
        )

    return min(allowed, key=lambda t: (cost(t), repr(t)))
