"""The main loop: propose, test against the boundary, commit or revert.

This is the whole physics of the prototype in one place.  A move is *not* physical
because it is allowed by some rulebook; it is physical exactly when it leaves the region's
gauge-invariant :class:`~constraintnet.region.Appearance` untouched -- "conservation is not
added as a separate law, it is the condition for a rewrite to count as a legitimate
resolution".

Everything else in this module is bookkeeping: accept/reject statistics, per-move cost
(word length of the relabelling), an event log, and hooks where the observer layer can
record that something happened.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex
from .groups import Group
from .moves import Move, apply_move, propose_edge_move, revert_move
from .region import Appearance, Region
from .states import StateId, gauge_fix_and_canonicalize

__all__ = ["MoveRecord", "Stats", "Simulation"]


@dataclass
class MoveRecord:
    """One attempt at a local rewrite, accepted or not."""

    step: int
    kind: str
    description: str
    accepted: bool
    cost: int = 0
    reason: str = ""
    support_edges: Tuple[Tuple[int, int], ...] = ()
    changed_faces: Tuple[Tuple[int, int, int], ...] = ()

    def line(self) -> str:
        mark = "OK  " if self.accepted else "REJ "
        return f"{mark} step {self.step:5d} | {self.description} | cost={self.cost} | {self.reason}"


@dataclass
class Stats:
    """Running tallies of the simulation."""

    proposals: int = 0
    accepted: int = 0
    rejected: int = 0
    total_cost: int = 0
    reasons: Dict[str, int] = field(default_factory=dict)
    per_edge_rejections: Dict[Tuple[int, int], int] = field(default_factory=dict)

    @property
    def accept_rate(self) -> float:
        return (self.accepted / self.proposals) if self.proposals else 0.0

    def merge(self, other: "Stats") -> None:
        self.proposals += other.proposals
        self.accepted += other.accepted
        self.rejected += other.rejected
        self.total_cost += other.total_cost
        for key, value in other.reasons.items():
            self.reasons[key] = self.reasons.get(key, 0) + value

    def summary(self) -> str:
        return (
            f"proposals={self.proposals} accepted={self.accepted} rejected={self.rejected} "
            f"accept_rate={self.accept_rate:.3f} total_cost={self.total_cost}"
        )


class Simulation:
    """Boundary-preserving dynamics on a labelled simplicial complex.

    Parameters
    ----------
    cx:
        The complex to evolve (mutated in place).
    region:
        The region whose external appearance must be preserved.  ``None`` means "the whole
        complex", i.e. nothing at all may leak out.
    probe_regions:
        Extra regions that must also stay untouched -- used to express "this observer is
        watching that object" and, in the motion experiments, to pin what counts as outside.
    move_generator:
        Callable ``(cx, rng) -> Move``; defaults to elementary generator relabellings.
    on_event:
        Optional hook ``(MoveRecord) -> None`` for observers/loggers.
    """

    def __init__(
        self,
        cx: SimplicialComplex,
        region: Optional[Region] = None,
        probe_regions: Sequence[Region] = (),
        rng: Optional[random.Random] = None,
        move_generator: Optional[Callable[[SimplicialComplex, random.Random], Move]] = None,
        on_event: Optional[Callable[[MoveRecord], None]] = None,
    ):
        self.cx = cx
        self.region = region if region is not None else Region(cx, cx.tetrahedra(), "whole")
        self.probe_regions = list(probe_regions)
        self.rng = rng or random.Random()
        self.move_generator = move_generator or (lambda c, r: propose_edge_move(c, r))
        self.on_event = on_event
        self.log: List[MoveRecord] = []
        self.stats = Stats()
        self.step_index = 0

    # ------------------------------------------------------------------ state
    def appearances(self) -> Tuple[Appearance, ...]:
        return (self.region.appearance(),) + tuple(r.appearance() for r in self.probe_regions)

    def sector(self) -> Tuple:
        """Gauge-invariant superselection label of the current configuration."""
        return self.region.appearance().signature()

    # ------------------------------------------------------------------ moves
    def attempt(self) -> MoveRecord:
        """Propose one move, test it against every watched boundary, commit or revert."""
        before = self.appearances()
        move = self.move_generator(self.cx, self.rng)
        apply_move(self.cx, move)
        after = self.appearances()

        if all(a == b for a, b in zip(before, after)):
            record = MoveRecord(
                step=self.step_index,
                kind=move.kind,
                description=move.describe(self.cx.group),
                accepted=True,
                cost=move.cost,
                reason="boundary appearance preserved",
                support_edges=move.support_edges(),
            )
            self.stats.accepted += 1
            self.stats.total_cost += move.cost
        else:
            revert_move(self.cx, move)
            which = [index for index, (a, b) in enumerate(zip(before, after)) if a != b]
            record = MoveRecord(
                step=self.step_index,
                kind=move.kind,
                description=move.describe(self.cx.group),
                accepted=False,
                cost=0,
                reason=f"would change observable(s) of watched region index {which}",
                support_edges=move.support_edges(),
            )
            self.stats.rejected += 1
            for edge in move.support_edges():
                self.stats.per_edge_rejections[edge] = (
                    self.stats.per_edge_rejections.get(edge, 0) + 1
                )

        self.stats.proposals += 1
        key = "accepted" if record.accepted else record.reason.split(" index")[0]
        self.stats.reasons[key] = self.stats.reasons.get(key, 0) + 1
        self.log.append(record)
        self.step_index += 1
        if self.on_event is not None:
            self.on_event(record)
        return record

    def run(self, steps: int) -> Stats:
        for _ in range(steps):
            self.attempt()
        return self.stats


def canonical_state(
    cx: SimplicialComplex, tree: Sequence[Tuple[int, int]], root: Optional[int] = None, region: Optional[Region] = None
) -> StateId:
    """Convenience wrapper so callers do not import :mod:`constraintnet.states` directly."""
    return gauge_fix_and_canonicalize(cx, tree=tree, root=root, region=region)
