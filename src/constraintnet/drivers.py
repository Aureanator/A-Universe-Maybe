"""Kernel / driver architecture (refactor track R1; design by Satish + Qwen cloud).

KERNEL  = the pure relational mathematics: complexes, groups, labels with inverse
consistency, holonomy, gauge fixing and orbit canonicalization, resolution spaces.
No randomness, no scheduler -- enforced by ``tests/test_kernel_purity.py``.

DRIVERS = hypotheses about how one micro-step happens.  Swappable at runtime; they
declare their EVENT ONTOLOGY so the observer layer never has to assume whether a
vetoed proposal counts toward the density rho:

* :class:`DriverA` -- stochastic proposal with veto (the v0.x baseline).  Randomness
  lives ONLY here.  Ontology: ``counterfactual-veto`` -- rejected proposals are not
  events; only accepted moves count.
* :class:`DriverB` -- deterministic churn.  The state is a point of the raw gauge
  slice (tree edges fixed to identity); sigma = right-multiplication of one designated
  coordinate by a fixed generator: a verified bijection whose cycle decomposition is
  the object's internal CLOCK SPECTRUM, with phase = index within the current cycle.
  Ontology: ``do-undo-churn`` -- every step is a real event.
* :class:`DriverC` -- free space (v1).  Move set = label moves UNION Pachner 2<->3
  relinkings under the SAME relational acceptance as DriverA(relational): the region's
  canonical gauge-invariant state must be unchanged.  The entailment can now lay the
  adjacency it travels on: connectivity is dynamical, boundary stays frozen.
  Ontology: ``counterfactual-veto``.

WHY sigma LIVES ON THE RAW SLICE, NOT ON ORBITS (the canonicalization trap, PHYSICS_
NOTES §7.1): right-multiplication does not commute with conjugation, so "multiply then
re-canonicalize" is NOT in general a well-defined map on gauge orbits --
:func:`orbit_sigma_well_definedness` demonstrates the failure.  Kernel rule: explore on
the raw slice (or any verified-bijective representation), canonicalize only for
OBSERVABLES.  DriverB verifies bijectivity of sigma at init by exhaustive orbit check,
as mandated.

Naming note: this track's milestones are R1..R5 to avoid collision with the physics
specification's M1..M8.
"""

from __future__ import annotations

import itertools
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex
from .moves import (Move, apply_move, apply_pachner_2_3, apply_pachner_3_2,
                    find_pachner_2_3_sites, find_pachner_3_2_sites,
                    propose_edge_move, revert_move)
from .region import Region

__all__ = [
    "DynamicsDriver",
    "DriverRecord",
    "DriverA",
    "DriverB",
    "DriverC",
    "odometer_state",
    "conjugate_triple",
    "canonical_orbit_of_triple",
    "orbit_sigma_well_definedness",
]


# --------------------------------------------------------------------------- #
# interface
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DriverRecord:
    """One micro-step, whatever its fate."""

    driver: str
    fate: str            # "accepted" | "vetoed" | "churn"
    counts_toward_rho: bool
    detail: str = ""
    phase: Optional[Tuple[int, int]] = None   # (cycle index, cycle length) for DriverB
    model: str = ""


class DynamicsDriver(ABC):
    """Runtime-swappable micro-step strategy.  KERNEL knows nothing beyond this."""

    @abstractmethod
    def advance(self) -> DriverRecord:
        """Perform exactly one micro-step and report its fate."""

    @abstractmethod
    def event_ontology(self) -> str:
        """Semantics of vetoed/undone proposals for the observer density.

        One of ``"counterfactual-veto"`` (vetoed proposals are not events) or
        ``"do-undo-churn"`` (violations that get cleaned up ARE events).  The observer
        module MUST read this and never assume one semantics.
        """

    @abstractmethod
    def reversible(self) -> bool:
        ...

    def inverse_advance(self) -> None:
        """Exact undo of the last advance(); required iff reversible() is True."""
        raise NotImplementedError(f"{type(self).__name__} is not reversible")


# --------------------------------------------------------------------------- #
# Driver A -- stochastic proposal with veto (baseline, unchanged physics)
# --------------------------------------------------------------------------- #
class DriverA(DynamicsDriver):
    """Boundary-preserving proposals with explicit model provenance.

    Default ``relational`` uses all nonidentity group elements uniformly and
    preserves the complete retained boundary state. ``legacy`` reproduces the
    v0.x generator/appearance arm. These are distinct dynamical hypotheses.
    """

    def __init__(
        self,
        cx: SimplicialComplex,
        region: Optional[Region] = None,
        rng_seed: int = 0,
        model: str = "relational",
    ):
        if model not in {"relational", "legacy"}:
            raise ValueError(f"unknown DriverA model: {model!r}")
        self.model = model
        self.cx = cx
        self.region = region if region is not None else Region(cx, cx.tetrahedra(), "whole")
        self.rng = random.Random(rng_seed)
        self.step_index = 0

    def advance(self) -> DriverRecord:
        observe = (self.region.gauge_invariant_state if self.model == "relational"
                   else self.region.appearance)
        before = observe()
        move = propose_edge_move(self.cx, self.rng, class_closed=self.model == "relational")
        apply_move(self.cx, move)
        if observe() == before:
            fate, counts = "accepted", True
        else:
            revert_move(self.cx, move)
            fate, counts = "vetoed", False
        record = DriverRecord(
            driver="A", fate=fate, counts_toward_rho=counts, detail=move.describe(self.cx.group),
            model=self.model,
        )
        self.step_index += 1
        return record

    def event_ontology(self) -> str:
        return "counterfactual-veto"

    def reversible(self) -> bool:
        # accepted moves are individually invertible, but the MAP on states is not
        # (randomness discards counterfactuals): declared non-invertible.
        return False


# --------------------------------------------------------------------------- #
# Driver C -- free space: relational acceptance over label moves UNION relinking
# --------------------------------------------------------------------------- #
class DriverC(DynamicsDriver):
    """Free-space driver (v1): the track itself becomes dynamical.

    Proposes, with declared mixtures, either an elementary relabelling ``A_e -> A_e g``
    or a Pachner 2<->3 relinking (new-edge label for 2-3 drawn uniformly: a genuine
    internal degree of freedom created by the move).  Acceptance is IDENTICAL to
    DriverA(relational): the whole-complex region's ``gauge_invariant_state()`` must be
    unchanged after the applied move; otherwise revert exactly.

    v1 SCOPE (deliberate): whole-complex regions only -- a closed ball whose boundary
    sphere is frozen.  The observation region is REBUILT from the current tetrahedra on
    every step because relinking invalidates any stored tet set; subregion boundaries
    that survive relinking are future work.  Site pools are recomputed per proposal:
    availability of each Pachner direction changes with the triangulation, and proposals
    are uniform over currently legal sites.

    Why acceptance of interior relinkings is expected (not assumed): an interior 2-3/3-2
    preserves boundary combinatorics and touches no surface edge label, so transported
    boundary loops -- the entirety of the observation -- are unchanged.  Tests pin this;
    any veto of a purely-interior relinking means the observation depends on bulk
    triangulation and that finding must be documented, not swept.
    """

    def __init__(
        self,
        cx: SimplicialComplex,
        rng_seed: int = 0,
        pachner_share: float = 0.5,
        new_label_uniform: bool = True,
    ):
        if not 0.0 <= pachner_share <= 1.0:
            raise ValueError("pachner_share must lie in [0, 1]")
        self.cx = cx
        self.rng = random.Random(rng_seed)
        self.pachner_share = float(pachner_share)
        self.new_label_uniform = new_label_uniform
        self.step_index = 0
        self.last_kind = None  # "label" | "pachner23" | "pachner32" (diagnostic only)

    def _observe(self):
        # Rebuild from CURRENT tetrahedra: after relinking a stored Region is stale.
        return Region(self.cx, self.cx.tetrahedra(), "whole").gauge_invariant_state()

    def _propose_applied(self):
        """Apply one proposal to cx and return (move, kind); caller commits or reverts."""
        if self.rng.random() < self.pachner_share:
            sites = [("pachner23", s) for s in find_pachner_2_3_sites(self.cx)]
            sites += [("pachner32", e) for e in find_pachner_3_2_sites(self.cx)]
            if sites:
                kind, site = sites[self.rng.randrange(len(sites))]
                if kind == "pachner23":
                    (a, b, _face) = site
                    label = None
                    if self.new_label_uniform:
                        elems = tuple(self.cx.group.elements)
                        label = elems[self.rng.randrange(len(elems))]
                    return apply_pachner_2_3(self.cx, a, b, new_edge_label=label), kind
                return apply_pachner_3_2(self.cx, site), kind
            # no legal relinking: fall through to a label move
        move = propose_edge_move(self.cx, self.rng, class_closed=True)
        apply_move(self.cx, move)
        return move, "label"

    def advance(self) -> DriverRecord:
        before = self._observe()
        move, kind = self._propose_applied()
        if self._observe() == before:
            fate, counts = "accepted", True
        else:
            revert_move(self.cx, move)
            fate, counts = "vetoed", False
        self.last_kind = kind
        record = DriverRecord(
            driver="C", fate=fate, counts_toward_rho=counts,
            detail=f"{kind}: {move.describe(self.cx.group)}",
            model="freepach-v1",
        )
        self.step_index += 1
        return record

    def event_ontology(self) -> str:
        return "counterfactual-veto"

    def reversible(self) -> bool:
        # individual moves invert, but the stochastic map discards counterfactuals
        return False


# --------------------------------------------------------------------------- #
# orbit helpers for triples of free labels (single-tetrahedron gauge slice)
# --------------------------------------------------------------------------- #
def odometer_state(group, k: int, phase: int):
    """O(1) mixed-radix decode of an odometer phase -> slice state.

    Matches DriverB(mode="odometer"): slot 0 is the fastest digit.  Lets scans jump to
    arbitrary phases without walking the cycle.
    """
    elements = list(group.elements)
    n = len(elements)
    digits = []
    rem = int(phase)
    for _ in range(k):
        rem, d = divmod(rem, n)
        digits.append(elements[d])
    return tuple(digits)


def conjugate_triple(group, config, lam):
    """Global conjugation of a raw-slice config: a_i -> lam^-1 a_i lam."""
    inv = group.inverse(lam)
    return tuple(group.multiply(group.multiply(inv, a), lam) for a in config)


def canonical_orbit_of_triple(group, config) -> Tuple:
    """Canonical representative of the residual-conjugation orbit (observable only!)."""
    return min(conjugate_triple(group, config, lam) for lam in group.elements)


def orbit_sigma_well_definedness(group, free_edges_count: int = 3, gen_index: int = 0):  # orbits of G^k under global conjugation
    """Does 'multiply coordinate k by g, then re-canonicalize' descend to orbits?

    Returns a dict with the verdict.  Expected (and asserted by tests): NOT well
    defined -- equivariance fails because right-multiplication and conjugation do not
    commute.  This is why DriverB's sigma lives on the raw slice.
    """
    elements = list(group.elements)
    g = group.move_generators()[gen_index]
    triples = list(itertools.product(elements, repeat=free_edges_count))

    def sigma_raw(t):
        return tuple(a if k != 0 else group.multiply(a, g) for k, a in enumerate(t))

    equivariance_ok = True
    injective_on_reps = True
    reps = sorted({canonical_orbit_of_triple(group, t) for t in triples}, key=repr)
    images = {}
    for rep in reps:
        image = canonical_orbit_of_triple(group, sigma_raw(rep))
        if image in images:
            injective_on_reps = False
        images[rep] = image
        for lam in group.elements:
            alt = conjugate_triple(group, rep, lam)
            if canonical_orbit_of_triple(group, sigma_raw(alt)) != image:
                equivariance_ok = False
                break
    return {
        "generator": g,
        "n_orbits": len(reps),
        "well_defined_on_orbits": equivariance_ok,
        "injective_on_representatives": injective_on_reps,
    }


# --------------------------------------------------------------------------- #
# Driver B -- deterministic churn on the raw gauge slice
# --------------------------------------------------------------------------- #
@dataclass
class _CycleInfo:
    lengths: Tuple[int, ...]          # clock spectrum (multiset of cycle lengths)
    index_of: Dict[Tuple, Tuple[int, int]]  # state -> (cycle id, position in cycle)


class DriverB(DynamicsDriver):
    """Deterministic internal churn: sigma = right-multiply coordinate ``coordinate`` by
    generator ``generator`` on the raw gauge slice G^k (tree edges fixed to identity).

    * bijectivity is VERIFIED at init by exhaustive check over all |G|^k states;
    * the cycle decomposition of sigma is computed once: its lengths are the object's
      internal clock spectrum, and phase = position within the current cycle;
    * observables (orbit ids) are canonicalized projections only.

    R3 F7 labelling: sigma is bijective on the RAW slice but NOT gauge-equivariant --
    gauge-equivalent starts can reach different physical orbits. The cycle decomposition
    (e.g. 864 cycles of length 2 vs one of length 1728) is therefore SCHEDULER DIAGNOSTICS
    for a chosen slice coordinate system, not a gauge-invariant observable of the object.
    Label it as such in every report; physics claims from sigma must be orbit-canonicalised.
    """

    def __init__(self, group, k: int = 3, coordinate: int = 0, generator=None, mode: str = "churn"):
        if not 0 <= coordinate < k:
            raise ValueError("coordinate must index one of the k slice coordinates")
        self.group = group
        self.k = k
        gens = list(group.move_generators())
        self.generator = generator if generator is not None else gens[0]
        self.coordinate = coordinate
        self.mode = mode
        elements = list(group.elements)
        self.states = tuple(itertools.product(elements, repeat=k))
        if mode == "churn":
            self._sigma_map = {s: self._apply(s, self.generator) for s in self.states}
        elif mode == "odometer":
            # scheduler choice, NOT physics: mixed-radix increment over element indices,
            # ONE cycle of length |G|^k (equidistributed phases).  The clock spectrum
            # depends on this choice -- D1 diagnostics probe exactly that dependence.
            position = {element: i for i, element in enumerate(elements)}
            n = len(elements)

            def increment(state):
                digits = [position[v] for v in state]
                slot = 0
                while True:
                    digits[slot] += 1
                    if digits[slot] < n:
                        break
                    digits[slot] = 0
                    slot += 1
                    if slot == k:
                        break
                return tuple(elements[d] for d in digits)

            self._sigma_map = {s: increment(s) for s in self.states}
        else:
            raise ValueError(f"unknown mode {mode!r}")
        if len(set(self._sigma_map.values())) != len(self.states):
            raise AssertionError("sigma is not bijective on the raw gauge slice")
        self.inverse_generator = group.inverse(self.generator)
        self._inverse_map = {v: s for s, v in self._sigma_map.items()}
        self.cycles = self._decompose()
        self.state = self.states[0]
        self.history: List[Tuple] = []

    # ------------------------------------------------------------------ sigma
    def _apply(self, triple, element):
        return tuple(
            a if k != self.coordinate else self.group.multiply(a, element)
            for k, a in enumerate(triple)
        )

    def _decompose(self) -> _CycleInfo:
        index_of: Dict[Tuple, Tuple[int, int]] = {}
        lengths: List[int] = []
        for start in self.states:
            if start in index_of:
                continue
            cycle_id = len(lengths)
            position = 0
            current = start
            while True:
                index_of[current] = (cycle_id, position)
                current = self._sigma_map[current]
                position += 1
                if current == start:
                    break
            lengths.append(position)
        return _CycleInfo(lengths=tuple(lengths), index_of=index_of)

    # ------------------------------------------------------------- dynamics
    def advance(self) -> DriverRecord:
        self.history.append(self.state)
        self.state = self._sigma_map[self.state]
        cycle_id, position = self.cycles.index_of[self.state]
        return DriverRecord(
            driver="B",
            fate="churn",
            counts_toward_rho=True,
            detail=f"sigma on coordinate {self.coordinate}",
            phase=(position, self.cycles.lengths[cycle_id]),
        )

    def inverse_advance(self) -> None:
        if not self.history:
            raise RuntimeError("nothing to undo")
        self.state = self.history.pop()

    def event_ontology(self) -> str:
        return "do-undo-churn"

    def reversible(self) -> bool:
        return True

    # ---------------------------------------------------------- observables
    def clock_spectrum(self) -> Dict[int, int]:
        """Multiplicity of each cycle length -- the object's internal clock spectrum."""
        out: Dict[int, int] = {}
        for length in self.cycles.lengths:
            out[length] = out.get(length, 0) + 1
        return out

    def orbit_observable(self) -> Tuple:
        """Gauge-invariant projection of the current raw-slice state (reporting only)."""
        return canonical_orbit_of_triple(self.group, self.state)
