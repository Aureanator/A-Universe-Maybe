"""Hard Gauss-law completion v1: classical Z2 phase space with solved constraint.

HANDOFF correction 2: H = -sum A_v - sum B_f is a FINITE PENALTY model whose bare
charge-defect states violate the literal A_v = 1 restriction; "a charge-sector/matter-
coupled Gauss constraint needs an explicit construction". This module is that
construction at the CLASSICAL Z2 PHASE-SPACE level (scope, stated plainly):

* gauge DOF: connection bits g_e on complex edges (magnetic sector; curvature B_f is
  the face holonomy coboundary -- existing machinery);
* electric DOF: flux bits E_e in {0,1} carried by each edge;
* matter DOF: charges q_v in {0,1} at vertices, NOT independent -- they are DEFINED by
  the solved Gauss constraint   q_v = XOR_{e incident to v} E_e   (div E = rho).

Consequences that come for free from the constraint being solved rather than penalized:
- an isolated charge cannot be configured at all: charges ARE string endpoints;
- total charge parity is identically even (XOR of a coboundary over closed complex = 0);
- boundary vertices with q_v = 1 are absorption channels: the exterior is the implicit
  reservoir, so N_exited = sum_{v in boundary} q_v counts charges leaving the frame --
  the open-boundary channel P32-3 asked for, defined rather than postulated;
- a charge can only disappear by annihilating its partner (flipping the connecting
  E-bit) or by exiting through the boundary. This is the confinement-relevant
  protection that acceptance-rule freezing alone does NOT provide (E066).

Dynamics lives in drivers.DriverG (Metropolis over {flip g_e, flip E_e} with energy
H = beta_B * #{curved faces} + beta_E * sum_e E_e); this module contains NO randomness.
Group-generic extension (nonabelian div, quantum amplitudes) is future work; Z2 first,
declared.
"""

from __future__ import annotations

import itertools
from typing import Dict, FrozenSet, Tuple


class GaussState:
    """(g, E) classical configuration on a SimplicialComplex with q := div(E)."""

    def __init__(self, cx):
        self.cx = cx
        self.group = cx.group  # expected Z2; enforced below
        if not cx.group.is_abelian() or cx.group.order() != 2:
            raise NotImplementedError("GaussState v1 is Z2-only (declared scope)")
        self.edges = tuple(tuple(sorted(e)) for e in cx.edges())
        self._eindex = {e: i for i, e in enumerate(self.edges)}
        n = len(self.edges)
        self.E = [0] * n                      # electric flux bits
        self.vertices = tuple(sorted(cx.vertices()))
        self._incident: Dict[int, list] = {v: [] for v in self.vertices}
        for i, (u, w) in enumerate(self.edges):
            self._incident[u].append(i)
            self._incident[w].append(i)
        boundary = set()
        use: Dict[Tuple[int, int, int], int] = {}
        for t in cx.tetrahedra():
            for f in itertools.combinations(sorted(t), 3):
                use[f] = use.get(f, 0) + 1
        for f, c in use.items():
            if c == 1:
                boundary.update(f)
        self.boundary_vertices = frozenset(v for v in self.vertices if v in boundary)

    # ------------------------------------------------------------- constraint
    def charges(self) -> Dict[int, int]:
        """q_v = XOR of incident E bits -- the Gauss constraint, solved."""
        q = {v: 0 for v in self.vertices}
        for i, bit in enumerate(self.E):
            if bit:
                u, w = self.edges[i]
                q[u] ^= 1
                q[w] ^= 1
        return q

    def check_gauss(self) -> bool:
        """Parity of total charge must be even (coboundary identity)."""
        return sum(self.charges().values()) % 2 == 0

    # ------------------------------------------------------------- observables
    def magnetic_energy_count(self) -> int:
        """Number of curved faces (B_f != identity)."""
        from .holonomy import triangle_holonomy
        ident = self.group.identity()
        return sum(triangle_holonomy(self.cx, f) != ident for f in self.cx.faces())

    def electric_count(self) -> int:
        return sum(self.E)

    def energy(self, beta_B: float, beta_E: float) -> float:
        return beta_B * self.magnetic_energy_count() + beta_E * self.electric_count()

    def exited_charge(self) -> int:
        """Charges sitting on boundary vertices = absorbed by the exterior reservoir."""
        q = self.charges()
        return sum(q[v] for v in self.boundary_vertices)

    def charge_pairs_distance(self, dual_adj) -> list:
        """Pair up live charges greedily and report their graph distances (diagnostic)."""
        live = [v for v, qv in self.charges().items() if qv]
        out = []
        while len(live) >= 2:
            a = live.pop(0)
            dist = dual_adj(a)
            best = min((dist.get(b, float("inf")), b) for b in live) if live else (None, None)
            live.remove(best[1])
            out.append(best[0])
        return out

    # ------------------------------------------------------------- moves
    def flip_E(self, edge) -> int:
        """Flip one electric flux bit. Gauss is preserved BY DEFINITION of q: the two
        endpoint charges toggle -- pair creation/annihilation/motion in one rule."""
        i = self._eindex[tuple(sorted(edge))]
        self.E[i] ^= 1
        return i

    def flip_g(self, edge) -> None:
        """Flip one connection bit (magnetic move; toggles curvature of faces on e)."""
        u, v = edge
        ident, other = list(self.group.elements)
        old = self.cx.label(u, v)
        new = other if old == ident else ident
        self.cx.set_label(u, v, new)

    # ------------------------------------------------------------- preparation
    def load_string(self, path_vertices) -> None:
        """Set E=1 along the given vertex path (a flux string; charges at its ends)."""
        for u, w in zip(path_vertices, path_vertices[1:]):
            i = self._eindex[tuple(sorted((u, w)))]
            self.E[i] = 1

    def shortest_path(self, a: int, b: int):
        """BFS on the 1-skeleton; returns vertex path or None."""
        adj: Dict[int, set] = {}
        for (u, w) in self.edges:
            adj.setdefault(u, set()).add(w)
            adj.setdefault(w, set()).add(u)
        if a == b:
            return [a]
        prev = {a: None}
        frontier = [a]
        while frontier and b not in prev:
            nxt = []
            for u in frontier:
                for w in adj.get(u, ()):
                    if w not in prev:
                        prev[w] = u
                        nxt.append(w)
            frontier = nxt
        if b not in prev:
            return None
        path, cur = [], b
        while cur is not None:
            path.append(cur)
            cur = prev[cur]
        return list(reversed(path))
