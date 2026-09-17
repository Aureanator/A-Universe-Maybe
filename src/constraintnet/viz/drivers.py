"""What the viewer animates.

Each driver owns a simulation and emits :class:`~constraintnet.viz.frame.Frame` snapshots.
They are deliberately different experiments:

``TetraDriver``
    ``d(Delta^3)`` with conservation switched on -- watch accepted relabellings ripple
    through face curvature, and rejected attempts flash red because every edge of the
    tetrahedron is *external*.
``OrbitTourDriver``
    A walk through the 178 gauge-inequivalent configurations of the tetrahedron, showing
    each state's orbit size and little group.
``LatticeDriver``
    A Kuhn 3-ball starting from the flat vacuum: internal fluctuations create curvature
    while the boundary appearance stays fixed, curvature clusters get flagged as matter
    candidates, event density accumulates in observer cells, and test signals slow down
    where the mesh is dense.
"""

from __future__ import annotations

import random
from collections import deque
from typing import Deque, Dict, List, Optional, Sequence, Tuple

import numpy as np

from ..complex import SimplicialComplex
from ..dynamics import MoveRecord, Simulation
from ..gauge import (
    canonical_config,
    enumerate_gauge_fixed_configs,
    gauge_fix_spanning_tree,
    quotient_by_global_conjugation,
    stabilizer_of_config,
)
from ..groups import get_group
from ..holonomy import triangle_holonomy
from ..observer import Observer
from ..moves import propose_edge_move
from ..objects import centroid_of, detect_candidates
from ..region import Region
from ..seeds import (
    TETRA_FREE_EDGES,
    TETRA_TREE,
    kuhn_ball,
    make_tetrahedron_boundary,
    randomize_labels,
)
from .frame import Flash, ObjectMark, Pulse, build_frame

__all__ = ["TetraDriver", "OrbitTourDriver", "LatticeDriver"]


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def shortest_path(cx: SimplicialComplex, source: int, target: int) -> List[int]:
    """BFS path in the 1-skeleton -- combinatorial, no geometry involved."""
    if source == target:
        return [source]
    previous: Dict[int, Optional[int]] = {source: None}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        for nxt in cx.adjacent(node):
            if nxt in previous:
                continue
            previous[nxt] = node
            if nxt == target:
                path = [nxt]
                while path[-1] != source:
                    path.append(previous[path[-1]])
                return list(reversed(path))
            queue.append(nxt)
    return []


class _BaseDriver:
    """Shared plumbing: clock, event log, fading flashes, travelling pulses."""

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)
        self.step_index = 0
        self.log: Deque[str] = deque(maxlen=7)
        self.flashes: List[Flash] = []
        self.pulses: List[Pulse] = []

    # -- subclass contract ----------------------------------------------------
    def advance(self) -> None:  # pragma: no cover - abstract
        raise NotImplementedError

    def frame(self):  # pragma: no cover - abstract
        raise NotImplementedError

    @property
    def done(self) -> bool:
        return False

    # -- shared ---------------------------------------------------------------
    def _age_flashes(self, decay: float = 0.12) -> None:
        kept = []
        for flash in self.flashes:
            flash.age += decay
            if flash.age < 1.0:
                kept.append(flash)
        self.flashes = kept

    def _advance_pulses(self, speed: float = 0.08) -> None:
        kept = []
        for pulse in self.pulses:
            pulse.progress += speed
            if pulse.progress <= 1.0:
                kept.append(pulse)
        self.pulses = kept

    def _push(self, line: str) -> None:
        self.log.append(line)


# --------------------------------------------------------------------------- #
# d(Delta^3): conservation with no interior
# --------------------------------------------------------------------------- #
class TetraDriver(_BaseDriver):
    """Random-walk of legitimate reductions on the tetrahedral seed."""

    def __init__(self, group="A4", seed: int = 0, gauge_fixed: bool = True, signal_every: int = 24):
        super().__init__(seed=seed)
        self.cx = make_tetrahedron_boundary(group)
        randomize_labels(self.cx, seed=seed)
        if gauge_fixed:
            gauge_fix_spanning_tree(self.cx, tree=TETRA_TREE, root=0)
        self.region = Region(self.cx, [], name="dDelta3")
        self.observer = Observer(self.cx, centre=min(self.cx.vertices()))
        self.sim = Simulation(self.cx, region=self.region, rng=random.Random(seed + 1))
        self.signal_every = signal_every

    def advance(self) -> None:
        record = self.sim.attempt()
        if record.support_edges:
            self.flashes.append(Flash(edge=record.support_edges[0], kind="accept" if record.accepted else "reject"))
        if record.accepted:
            self.observer.record_move(record.support_edges)
        self._push(record.line())
        self.step_index += 1
        self._age_flashes()
        self._advance_pulses()
        if self.signal_every and self.step_index % self.signal_every == 0:
            self._fire_signal()

    def _fire_signal(self) -> None:
        vertices = sorted(self.cx.vertices())
        path = shortest_path(self.cx, vertices[0], vertices[-1])
        if len(path) > 1:
            self.pulses.append(Pulse(path=path, progress=0.0, label="probe"))

    def frame(self):
        stats = self.sim.stats
        appearance = self.region.appearance()
        counters = {
            "system": f"d(Delta^3) over {self.cx.group.name}",
            "step": str(self.step_index),
            "accepted": str(stats.accepted),
            "rejected": str(stats.rejected),
            "accept rate": f"{stats.accept_rate:.2f}",
            "curved faces": str(appearance.nontrivial_face_count()),
            "sector": f"#{abs(hash(appearance.signature())) % 10**6:06d}",
        }
        return build_frame(
            self.cx,
            step=self.step_index,
            observer=self.observer,
            flashes=self.flashes,
            pulses=self.pulses,
            counters=counters,
            log_lines=list(self.log),
            title="Tetrahedral seed: every edge is external, so conservation bites",
            note="green flash = accepted reduction, red = rejected (would change what the outside sees)",
        )


# --------------------------------------------------------------------------- #
# tour of the 178 gauge classes
# --------------------------------------------------------------------------- #
class OrbitTourDriver(_BaseDriver):
    """Step through the physical state space of ``d(Delta^3)`` one orbit at a time."""

    def __init__(self, group="A4", seed: int = 0, dwell: int = 1):
        super().__init__(seed=seed)
        self.group = get_group(group)
        self.cx = make_tetrahedron_boundary(self.group)
        configs = enumerate_gauge_fixed_configs(self.group, TETRA_FREE_EDGES)
        orbits, _ = quotient_by_global_conjugation(configs, self.group)
        self.orbits: List[frozenset] = sorted(orbits, key=lambda o: (len(o), repr(sorted(map(str, o)))))
        self.index = 0
        self.dwell = max(1, dwell)
        self._counter = 0
        self._apply_current()

    def _apply_current(self) -> None:
        representative = min(self.orbits[self.index])
        for edge, value in zip(TETRA_FREE_EDGES, representative):
            self.cx.set_label(edge[0], edge[1], value)

    def advance(self) -> None:
        self._counter += 1
        if self._counter % self.dwell == 0:
            self.index = (self.index + 1) % len(self.orbits)
            self._apply_current()
            self._push(f"state {self.index}/{len(self.orbits)} :: {_describe_config(self.cx, TETRA_FREE_EDGES)}")
        self.step_index += 1
        self._age_flashes(decay=0.2)

    @property
    def done(self) -> bool:
        return False

    def frame(self):
        orbit = self.orbits[self.index]
        representative = min(orbit)
        stab = stabilizer_of_config(representative, self.group)
        appearance = Region(self.cx, [], "dDelta3").appearance()
        counters = {
            "system": f"gauge-class tour over {self.group.name}",
            "state": f"{self.index + 1} / {len(self.orbits)}",
            "orbit size": str(len(orbit)),
            "little group": _little_group_name(stab, self.group),
            "curved faces": str(appearance.nontrivial_face_count()),
        }
        return build_frame(
            self.cx,
            step=self.index,
            flashes=self.flashes,
            counters=counters,
            log_lines=list(self.log),
            title=f"Gauge-inequivalent state {self.index + 1} of {len(self.orbits)}",
            note="each stop is one physical state: all gauge copies have been quotiented out",
        )


def _describe_config(cx: SimplicialComplex, edges) -> str:
    group = cx.group
    parts = []
    for edge in edges:
        value = cx.label(*edge)
        parts.append(f"A{edge[0]}{edge[1]}={group.format(value) if hasattr(group, 'format') else value}")
    return " ".join(parts)


def _little_group_name(stab, group) -> str:
    order = len(stab)
    if order == 1:
        return "trivial"
    if order == group.order():
        return group.name
    orders = {group.order_of(x) for x in stab}
    if order == 2:
        return "Z2"
    if order == 3:
        return "Z3"
    if order == 4:
        return "V4" if orders <= {1, 2} else "Z4"
    return f"order-{order}"


# --------------------------------------------------------------------------- #
# Kuhn lattice: vacuum fluctuations, curvature clusters, density, signals
# --------------------------------------------------------------------------- #
class LatticeDriver(_BaseDriver):
    """A triangulated 3-ball evolving under boundary-preserving reductions."""

    def __init__(
        self,
        group="A4",
        n: int = 2,
        seed: int = 0,
        signal_every: int = 60,
        interior_moves: bool = False,
        max_objects: int = 6,
    ):
        super().__init__(seed=seed)
        self.cx = kuhn_ball(group, n=n)
        # start from the flat vacuum: every label is the identity
        for (u, v) in self.cx.edges():
            self.cx.set_label(u, v, self.cx.group.identity())
        self.region = Region(self.cx, self.cx.tetrahedra(), "ball")
        centre = min(self.cx.vertices(), key=lambda v: len(self.cx.adjacent(v)))
        self.observer = Observer(self.cx, centre=centre)
        edges_pool = sorted(self.region.interior_edges()) if interior_moves else None
        move_generator = None if edges_pool is None else (lambda c, r: propose_edge_move(c, r, edges=edges_pool))
        self.sim = Simulation(
            self.cx,
            region=self.region,
            rng=random.Random(seed + 7),
            move_generator=move_generator,
        )
        self.signal_every = signal_every
        self.max_objects = max_objects
        self.signals_sent = 0
        self.last_delay: Optional[str] = None

    def advance(self) -> None:
        record = self.sim.attempt()
        if record.support_edges:
            for edge in record.support_edges[:2]:
                self.flashes.append(Flash(edge=edge, kind="accept" if record.accepted else "reject"))
        if record.accepted:
            self.observer.record_move(record.support_edges)
        self._push(record.line())
        self.step_index += 1
        self._age_flashes(decay=0.08)
        self._advance_pulses(speed=0.06)
        if self.signal_every and self.step_index % self.signal_every == 0:
            self._fire_signal()

    def _fire_signal(self) -> None:
        boundary = sorted({v for face in self.region.boundary_faces() for v in face})
        if len(boundary) < 2:
            return
        source, target = self.rng.sample(boundary, 2)
        path = shortest_path(self.cx, source, target)
        if len(path) > 1:
            self.pulses.append(Pulse(path=path, progress=0.0, label=f"{source}->{target}"))
            self.signals_sent += 1
            self.last_delay = self.observer.delay_report(path)

    def _objects(self) -> List[ObjectMark]:
        marks: List[ObjectMark] = []
        candidates = detect_candidates(self.cx)[: self.max_objects]
        for summary in candidates:
            centre = centroid_of(summary["vertices"], self._positions())
            if centre is None:
                continue
            marks.append(
                ObjectMark(
                    centroid=centre,
                    label=f"{summary['dominant_class']} x{summary['size']}",
                    charge=summary["dominant_class"],
                    age=self.step_index,
                    radius=min(0.28, 0.06 + 0.03 * summary["size"]),
                )
            )
        return marks

    def _positions(self):
        from .layout import positions as layout_positions

        if not hasattr(self, "_cached_positions"):
            self._cached_positions = layout_positions(self.cx, seed=1)
        return self._cached_positions

    def frame(self):
        stats = self.sim.stats
        appearance = self.region.appearance()
        curved = len([f for f in self.cx.faces() if triangle_holonomy(self.cx, f) != self.cx.group.identity()])
        counters = {
            "system": f"Kuhn 3-ball over {self.cx.group.name} ({self.cx.n_tetrahedra()} tets)",
            "step": str(self.step_index),
            "accepted / rejected": f"{stats.accepted} / {stats.rejected}",
            "accept rate": f"{stats.accept_rate:.2f}",
            "curved faces": str(curved),
            "matter candidates": str(len(detect_candidates(self.cx))),
            "signals sent": str(self.signals_sent),
            "last signal delay": self.last_delay or "-",
            "sector": f"#{abs(hash(appearance.signature())) % 10**6:06d}",
        }
        return build_frame(
            self.cx,
            step=self.step_index,
            observer=self.observer,
            objects=self._objects(),
            flashes=self.flashes,
            pulses=self.pulses,
            counters=counters,
            log_lines=list(self.log),
            positions_override=self._positions(),
            title="3-ball: vacuum fluctuations stay invisible outside; curvature clusters are matter candidates",
            note="sphere size = cluster extent, colour = charge class; signals slow down in dense cells",
        )
