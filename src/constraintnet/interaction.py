"""Interaction by gluing: fiber products of internal resolution spaces (kernel, R3).

Two objects sharing a boundary face F must agree on the constraint flux threading every
edge of F.  For cones with apex labels ``x`` (object A) and ``y`` (probe B), glued along
triangle F with shared boundary labels ``A_vw``, the compatibility condition is

    mu⁻¹ (x_v · A_vw · x_w⁻¹) mu == y_v · A_vw · y_w⁻¹

for ONE relative frame mu and EVERY shared edge. Each apex has its own gauge
frame; matching individual conjugacy classes loses correlations between edges.
This is a specified compatibility convention, not a derived collision dynamics.
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
    *,
    matching: str = "relational",
) -> bool:
    """Match the ordered flux tuples in one common relative apex frame.

    ``shared_edges`` lists ((v,w), A_vw); ``index_*`` map boundary vertex -> slot in x/y.

    ``relational`` requires simultaneous conjugacy (the default). ``raw`` retains
    the historical fixed-frame equality control. ``classes`` is the deliberately
    coarser per-edge observable. Only the latter two gauge-invariant conventions
    (relational and classes) survive independent apex gauge transformations.
    Existence of an alignment counts once; alignment multiplicity is not a weight.
    """
    if matching not in {"relational", "raw", "classes"}:
        raise ValueError(f"unknown matching convention: {matching!r}")
    fluxes = []
    for (v, w), a_vw in shared_edges:
        fx = face_flux(group, x[index_x[v]], a_vw, x[index_x[w]])
        fy = face_flux(group, y[index_y[v]], a_vw, y[index_y[w]])
        if matching == "raw":
            if fx != fy:
                return False
            continue
        if group.class_of(fx) != group.class_of(fy):
            return False
        fluxes.append((fx, fy))
    if matching in {"raw", "classes"}:
        return True
    return any(all(group.conjugate(mu, fx) == fy for fx, fy in fluxes)
               for mu in group.elements)


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


def phase_locked_outcomes(
    group: Group,
    cycle_a: Sequence[Sequence],
    cycle_b: Sequence[Sequence],
    shared_edges: Sequence[Tuple[EdgeKey, object]],
    index_x: Dict[int, int],
    index_y: Dict[int, int],
    cap_K: int = 8,
) -> Dict:
    """Phase-locked interaction protocol (Section 4), evaluated over ALL phase pairs.

    Probe sits fixed at b; the object free-runs its clock from phase i.  Outcomes:

    * ``meshed``   joint non-empty on arrival (wait 0) -- actualize deterministically;
    * ``deferred`` force_advance steps sigma w <= K times until the joint opens (wait w);
    * ``scatter``  cap reached, joint never opened -- elastic bounce, no internal change.

    Returns per-(phaseA, phaseB) fates, duty cycle (immediate-mesh fraction), and the
    wait histogram -- the object's duty-cycle / absorption-cross-section profile.  This
    is pure kernel: a deterministic scan, no RNG, no sampling.
    """
    la, lb = len(cycle_a), len(cycle_b)
    fates: List[List[Tuple[str, Optional[int]]]] = []
    waits: Dict[int, int] = {}
    immediate = deferred = scatter = 0
    for i in range(la):
        row: List[Tuple[str, Optional[int]]] = []
        for j in range(lb):
            b = cycle_b[j]
            outcome = None
            for w in range(cap_K + 1):
                a = cycle_a[(i + w) % la]
                if compatible_on_shared_face(group, a, b, shared_edges, index_x, index_y):
                    outcome = ("meshed" if w == 0 else "deferred", w)
                    break
            if outcome is None:
                outcome = ("scatter", None)
            row.append(outcome)
            waits[outcome[1]] = waits.get(outcome[1], 0) + 1
            immediate += outcome[0] == "meshed"
            deferred += outcome[0] == "deferred"
            scatter += outcome[0] == "scatter"
        fates.append(row)
    total = la * lb
    return {
        "fates": fates,
        "duty_cycle": immediate / total,
        "deferred_fraction": deferred / total,
        "scatter_fraction": scatter / total,
        "wait_histogram": waits,
    }


def stride_scan(
    group: Group,
    state_at,
    cycle_length: int,
    probe_states: Sequence[Sequence],
    shared_edges: Sequence[Tuple[EdgeKey, object]],
    index_x: Dict[int, int],
    index_y: Dict[int, int],
    periods: Sequence[int],
    hits: int = 400,
) -> Dict[int, float]:
    """D1 aliasing scan: probe arrives every ``p`` ticks of the object clock.

    The visited phase set is the coset <p> of length L/gcd(p,L); mesh rate therefore
    depends on gcd(p, L), NOT on p -- resonances appear as structure against gcd, and
    equidistributed drivers (full-cycle sweeps) hide it.  ``state_at(phase)`` must be
    O(1) (e.g. odometer mixed-radix decoding).  Deterministic; no RNG.
    """
    out: Dict[int, float] = {}
    for p in periods:
        meshed = 0
        for h in range(hits):
            phase = (h * p) % cycle_length
            a = state_at(phase)
            if any(
                compatible_on_shared_face(group, a, b, shared_edges, index_x, index_y)
                for b in probe_states
            ):
                meshed += 1
        out[p] = meshed / hits
    return out


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
