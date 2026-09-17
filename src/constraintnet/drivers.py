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
from .moves import Move, apply_move, propose_edge_move, revert_move
from .region import Region

__all__ = [
    "DynamicsDriver",
    "DriverRecord",
    "DriverA",
    "DriverB",
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
    """The v0.x dynamics: propose a random generator relabelling; commit iff the watched
    appearance is preserved.  Randomness lives only in this driver."""

    def __init__(
        self,
        cx: SimplicialComplex,
        region: Optional[Region] = None,
        rng_seed: int = 0,
    ):
        self.cx = cx
        self.region = region if region is not None else Region(cx, cx.tetrahedra(), "whole")
        self.rng = random.Random(rng_seed)
        self.step_index = 0

    def advance(self) -> DriverRecord:
        before = self.region.appearance()
        move = propose_edge_move(self.cx, self.rng)
        apply_move(self.cx, move)
        if self.region.appearance() == before:
            fate, counts = "accepted", True
        else:
            revert_move(self.cx, move)
            fate, counts = "vetoed", False
        record = DriverRecord(
            driver="A", fate=fate, counts_toward_rho=counts, detail=move.describe(self.cx.group)
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
# orbit helpers for triples of free labels (single-tetrahedron gauge slice)
# --------------------------------------------------------------------------- #
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
