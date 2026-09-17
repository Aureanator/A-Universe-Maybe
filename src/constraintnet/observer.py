"""The observer layer: coarse-graining events without ever using coordinates as physics.

An observer cannot see individual microscopic reductions, so it groups *events* (vertices)
into cells and counts accepted rewrites per cell.  The partition must not smuggle geometry
in through the back door, so cells are defined **relationally**: by graph-distance shells
around a chosen event, or by an explicit grouping of vertices.  Grid coordinates attached to
a lattice may be used afterwards to *draw* those cells -- never to define them.

Quantities produced here are the prototype versions of the specification's module 11:

``rho(cell)``   accepted rewrites recorded in a cell (event density)
``n(cell)``     ``rho / rho0``, the local mesh-fineness factor
``delay(path)`` microscopic reduction steps needed to traverse a path, inflated where the
                mesh is fine -- this is the gravity-like propagation delay
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .complex import SimplicialComplex

__all__ = ["Observer", "shells_from", "propagation_delay"]


def shells_from(cx: SimplicialComplex, source: int) -> Dict[int, Set[int]]:
    """BFS distance shells around ``source`` in the 1-skeleton (purely relational)."""
    dist: Dict[int, int] = {source: 0}
    queue = [source]
    while queue:
        node = queue.pop(0)
        for nxt in cx.adjacent(node):
            if nxt not in dist:
                dist[nxt] = dist[node] + 1
                queue.append(nxt)
    shells: Dict[int, Set[int]] = defaultdict(set)
    for vertex, distance in dist.items():
        shells[distance].add(vertex)
    return dict(shells)


class Observer:
    """Coarse-grained event counter over a relational cell decomposition.

    Parameters
    ----------
    cx:
        The complex being observed.
    cells:
        Optional explicit mapping ``cell_name -> set of vertices``.  When omitted, shells
        around ``centre`` are used (graph distance), which is coordinate-free by construction.
    baseline:
        Vacuum density ``rho0``.  Defaults to the smallest nonzero cell count so that
        ``n >= 1`` everywhere and ``n == 1`` in the emptiest active cell.
    """

    def __init__(
        self,
        cx: SimplicialComplex,
        cells: Optional[Dict[str, Set[int]]] = None,
        centre: Optional[int] = None,
        baseline: Optional[float] = None,
    ):
        self.cx = cx
        if cells is None:
            centre = centre if centre is not None else (min(cx.vertices()) if cx.vertices() else 0)
            shells = shells_from(cx, centre)
            cells = {f"shell{distance}": set(members) for distance, members in sorted(shells.items())}
        self.cells: Dict[str, Set[int]] = {name: set(members) for name, members in cells.items()}
        self._vertex_to_cell: Dict[int, str] = {}
        for name, members in self.cells.items():
            for vertex in members:
                self._vertex_to_cell[vertex] = name
        self.counts: Dict[str, float] = {name: 0.0 for name in self.cells}
        self.total_events = 0
        self._baseline_override = baseline

    # ------------------------------------------------------------------ recording
    def cell_of_vertex(self, vertex: int) -> Optional[str]:
        return self._vertex_to_cell.get(vertex)

    def record_vertices(self, vertices: Iterable[int], weight: float = 1.0) -> None:
        """Register that reductions happened at these events."""
        for vertex in vertices:
            cell = self.cell_of_vertex(vertex)
            if cell is None:
                continue
            self.counts[cell] += weight
            self.total_events += weight

    def record_move(self, support_edges: Iterable[Tuple[int, int]], weight: float = 1.0) -> None:
        """Record an accepted rewrite; both endpoints of each affected edge share the event."""
        seen: Set[int] = set()
        for u, v in support_edges:
            seen.add(u)
            seen.add(v)
        self.record_vertices(seen, weight=weight / max(1, len(seen)))

    # ------------------------------------------------------------------ readouts
    def rho(self, cell: str) -> float:
        return self.counts.get(cell, 0.0)

    @property
    def rho0(self) -> float:
        """Baseline vacuum density ``rho0``: the uniform expectation.

        Taking the *emptiest active cell* as the reference is degenerate early in a run --
        while only one cell holds events it becomes its own baseline and every reading says
        ``n == 1``, so no signal ever looks delayed.  The uniform expectation
        ``total_events / n_cells`` is well defined from the first event onwards: cells above
        average are finer (``n > 1``), below average coarser (``n < 1``).
        """
        if self._baseline_override is not None:
            return max(1e-12, float(self._baseline_override))
        cells = len(self.cells) or 1
        return max(1e-12, self.total_events / cells)

    def n_factor(self, cell: str) -> float:
        """Local mesh-fineness factor ``n(x) = rho(x) / rho0``; > 1 means a finer mesh."""
        return self.rho(cell) / self.rho0

    def n_at_vertex(self, vertex: int) -> float:
        cell = self.cell_of_vertex(vertex)
        return self.n_factor(cell) if cell else 1.0

    def density_field(self) -> Dict[str, Tuple[float, float]]:
        """``cell -> (rho, n)`` for reporting and rendering."""
        return {name: (self.rho(name), self.n_factor(name)) for name in sorted(self.cells)}

    def curvature_proxy(self) -> Dict[str, float]:
        """The early-prototype curvature summary ``K(x) ~ rho(x) - rho0``."""
        base = self.rho0
        return {name: self.rho(name) - base for name in sorted(self.cells)}

    # ------------------------------------------------------------------ traversal
    def edge_cost(self, u: int, v: int) -> float:
        """Microscopic reductions needed to actualize the implication ``u -> v``.

        An implication costs at least one step; crossing cells where the mesh is finer
        (larger event density) costs proportionally more -- this single rule is what becomes
        gravitational time delay in the observer's description.  Cells coarser than average
        do not make an implication cheaper than one reduction, hence the floor.
        """
        return max(1.0, 0.5 * (self.n_at_vertex(u) + self.n_at_vertex(v)))

    def propagation_delay(self, path: Sequence[int]) -> float:
        """Total reduction steps for a test implication to traverse ``path``."""
        return sum(self.edge_cost(u, v) for u, v in zip(path, path[1:]))

    def hop_count(self, path: Sequence[int]) -> int:
        return max(0, len(path) - 1)

    def delay_report(self, path: Sequence[int]) -> str:
        hops = self.hop_count(path)
        delay = self.propagation_delay(path)
        return f"{hops} hops -> {delay:.2f} reduction steps ({delay / max(1, hops):.2f}/hop)"
