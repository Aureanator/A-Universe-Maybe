"""CoreDriver -- animate E030: hidden internal states of a flux-string core.

A Kuhn n=2 ball with an order-3 star seed at the central vertex 13 carries a closed flux
loop (12 curved faces). The boundary appearance is FIXED; the interior admits exactly four
inequivalent resolutions (|I| = 4, E030). This driver cycles through those four physical
states -- each one shown for a dwell of frames -- while:

* curved faces glow in their conjugacy class colour (the flux loop silhouette),
* the 14 core edges are drawn bold; active ones (non-identity label) pulse,
* an "outside observer" probe cycle fires repeatedly and reads the SAME charge every time
  (that's the whole point: four interiors, one exterior),
* a HUD counter shows state k of 4, raw solution count, and boundary appearance hash.

Coordinates come from the standard projection layout -- visualization only; the states are
gauge orbits computed combinatorially by the slice solver in entropy.py.
"""

from __future__ import annotations

import itertools
from typing import Dict, List, Tuple

import numpy as np

from ..entropy import enumerate_region_resolutions_slice, interior_vertices
from ..region import region_from_tets
from ..seeds import kuhn_ball
from ..strings import _hol, flux_string_components
from .frame import Flash, ObjectMark, Pulse, build_frame
from .drivers import _BaseDriver

__all__ = ["CoreDriver"]


class CoreDriver(_BaseDriver):
    """Cycle the four hidden internal resolutions of the degree-14 core."""

    def __init__(self, dwell: int = 8, seed: int = 0):
        super().__init__(seed=seed)
        self.cx = kuhn_ball("A4", n=2)
        g = self.cx.group
        c = sorted([x for x in g.elements if g.order_of(x) == 3], key=repr)[0]
        for e in sorted(self.cx.edges()):
            self.cx.set_label(e[0], e[1], c if 13 in e else g.identity())
        self.decl = {tuple(sorted(f)): g.class_of(_hol(cx := self.cx, f)) for f in self.cx.faces()}

        self.region = region_from_tets(self.cx, [t for t in self.cx.tetrahedra() if 13 in t], name="star13")
        fc = {f: self.decl.get(f, frozenset({g.identity()}))
              for f in map(tuple, map(sorted, self.region.interior_faces()))}
        self.fc = fc
        sols = enumerate_region_resolutions_slice(self.cx, self.region, fc)
        self.raw_count = len(sols)
        ie = self.region.interior_edges()
        self.core_edges = ie

        # gauge orbits via canonical min-rep (gauge only at vertex 13; mixed orientation)
        def gimg(x, lam):
            out = []
            for (u, v), value in zip(ie, x):
                left = g.identity() if u != 13 else g.inverse(lam)
                right = g.identity() if v != 13 else lam
                out.append(g.multiply(g.multiply(left, value), right))
            return tuple(out)

        orbits: Dict[str, Tuple] = {}
        for s in sols:
            rep = min(repr(gimg(s, lam)) for lam in g.elements)
            orbits.setdefault(rep, s)
        self.states = [orbits[r] for r in sorted(orbits)]
        assert len(self.states) == 4, "E030 expects exactly four physical states"

        # snapshot of boundary-fixed labels to restore between states
        self.snapshot = dict(self.cx.labels_snapshot())
        self.dwell = max(1, dwell)
        self.state_index = 0
        self.frame_in_state = 0
        self.appearance_hash = None
        self._apply_state()
        comps = flux_string_components(self.cx)
        self.loop_length = comps[0].length if comps else 0

    # -- state application -----------------------------------------------------
    def _apply_state(self) -> None:
        for (u, v), value in self.snapshot.items():
            self.cx.set_label(u, v, value)
        for (u, v), value in zip(self.core_edges, self.states[self.state_index]):
            self.cx.set_label(u, v, value)
        from constraintnet.holonomy import triangle_holonomy
        ok = all(triangle_holonomy(self.cx, f) in self.fc[f] for f in self.region.interior_faces())
        assert ok, "state violates declared curvature classes"
        appearance = self.region.appearance()
        h = abs(hash(appearance.signature())) % 10**6
        if self.appearance_hash is None:
            self.appearance_hash = h
        self.exterior_same = (h == self.appearance_hash)

    # -- animation -------------------------------------------------------------
    def advance(self) -> None:
        self.frame_in_state += 1
        if self.frame_in_state >= self.dwell:
            self.frame_in_state = 0
            self.state_index = (self.state_index + 1) % len(self.states)
            self._apply_state()
            self._push(f"interior -> state {self.state_index} of {len(self.states)} "
                       f"(exterior unchanged: {self.exterior_same})")
        self.step_index += 1
        self._age_flashes(decay=0.10)
        self._advance_pulses(speed=0.05)

    def _probe_pulse(self) -> Pulse:
        # a fixed probe cycle on the boundary surface encircling the string (deterministic)
        boundary = sorted({v for f in self.region.boundary_faces() for v in f})
        ring = [v for v in boundary if v != 13][:6]
        from .drivers import shortest_path
        path: List[int] = []
        for a, b in zip(ring, ring[1:] + ring[:1]):
            seg = shortest_path(self.cx, a, b)
            path.extend(seg[:-1])
        return Pulse(path=path or [boundary[0], boundary[1]], progress=(self.step_index % 40) / 40.0,
                     label="probe")

    def _positions(self):
        if not hasattr(self, "_cached_positions"):
            from .layout import positions as layout_positions
            self._cached_positions = layout_positions(self.cx, seed=1)
        return self._cached_positions

    def frame(self):
        g = self.cx.group
        state = self.states[self.state_index]
        n_active = sum(1 for v in state if v != g.identity())
        counters = {
            "system": "Kuhn 3-ball, A4, order-3 core at v13",
            "hidden interior states |I|": str(len(self.states)),
            "current state": f"{self.state_index} of {len(self.states) - 1}",
            "raw resolutions (all gauge)": str(self.raw_count),
            "core edges active / total": f"{n_active} / {len(state)}",
            "flux loop length": str(self.loop_length),
            "boundary appearance": ("FIXED" if self.exterior_same else "CHANGED?!"),
            "entropy S = log|I|": f"{np.log(len(self.states)):.3f}",
        }
        marks = [ObjectMark(centroid=self._positions()[13], label=f"|I| = {len(self.states)}",
                            charge="core", radius=0.22)]
        return build_frame(
            self.cx,
            step=self.step_index,
            objects=marks,
            flashes=[],
            pulses=[self._probe_pulse()],
            counters=counters,
            log_lines=list(self.log),
            positions_override=self._positions(),
            title="core entropy: four hidden interiors, one exterior -- the observer cannot tell them apart",
            note="bold edges = core star; states cycle by gauge-inequivalent interior relabelling; "
                 "probe cycle reads the same charge in every state",
        )
