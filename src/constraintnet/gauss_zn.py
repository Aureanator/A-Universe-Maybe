"""Z_N Gauss completion: the solved matter-coupled constraint for a NON-self-dual charge group.

WHY THIS EXISTS (E068 -> E069).  E067 built :class:`~constraintnet.gauss.GaussState` over Z2 and
E068 measured what it protects: charge NUMBER is conserved identically, yet a confined pair still
annihilates, because retracting the flux string lowers energy and in Z2 every charge is its own
antiparticle -- so nothing forbids two defects meeting and vanishing.  E068's conclusion was that
matter needs a *charge-conjugation selection rule*.  This module supplies the cheapest arena in which
such a rule can even exist: over Z_N with N >= 3, charges are NOT all self-inverse, neutral composites
split into pair-cancellable (**mesonic**) and irreducible (**baryonic**) content, and the decay of the
latter cannot proceed by a two-body encounter.

SCOPE, stated plainly (same discipline as gauss.py): CLASSICAL abelian phase space -- connection
labels g_e in an abelian cyclic group plus integer electric flux bits a_e in Z_N.  No quantum
amplitudes, no nonabelian covariant divergence, no cross-coupling between the two sectors.  The
absence of flux-charge coupling is not an oversight: it is the object of measurement (prediction PD),
and it is what makes the honest statement "abelian models contain no dyons" checkable rather than
rhetorical.  Nonabelian Gauss completion is future work and points at the D(A4) layer in doubles.py.

CONVENTIONS.  Each undirected edge {u,v} is stored with u < v; a flux value a on that edge means
`a units flowing u -> v`.  Charge is DEFINED, never configured independently:

    q_v := sum_{e into v} a_e - sum_{e out of v} a_e   (mod N)          [div E = rho]

so total charge is identically zero mod N on a closed complex (coboundary identity), an isolated
charge cannot be written down at all, and every flux update touches exactly two charges, by opposite
amounts.  Those three facts are the PA assertions of E069 and hold by construction.
"""

from __future__ import annotations

import itertools
from collections import Counter
from typing import Dict, List, Tuple


class GaussStateZN:
    """(g, a) classical configuration on a SimplicialComplex over Z_N with q := div(E)."""

    def __init__(self, cx):
        self.cx = cx
        self.group = cx.group
        n = getattr(self.group, "n", None)
        if n is None or not self.group.is_abelian():
            raise NotImplementedError(
                "GaussStateZN is cyclic-abelian only (declared scope); "
                "nonabelian div E needs a covariant construction"
            )
        if n < 2:
            raise ValueError("N must be >= 2")
        self.N = int(n)
        self.edges: Tuple[Tuple[int, int], ...] = tuple(tuple(sorted(e)) for e in cx.edges())
        self._eindex = {e: i for i, e in enumerate(self.edges)}
        self.E: List[int] = [0] * len(self.edges)      # electric flux a_e in Z_N
        self.vertices = tuple(sorted(cx.vertices()))

        # signed incidence: +1 where the edge's canonical direction (u<v) points INTO v
        self._inc: Dict[int, List[Tuple[int, int]]] = {v: [] for v in self.vertices}
        for i, (u, w) in enumerate(self.edges):
            self._inc[u].append((i, -1))   # flow u->w leaves u
            self._inc[w].append((i, +1))   # and arrives at w

        # a face used by exactly one tetrahedron lies on the boundary 2-sphere
        use: Dict[Tuple[int, int, int], int] = {}
        for t in cx.tetrahedra():
            for f in itertools.combinations(sorted(t), 3):
                use[f] = use.get(f, 0) + 1
        self.boundary_vertices = frozenset(
            v for f, c in use.items() if c == 1 for v in f if v in self._inc
        )

    # ------------------------------------------------------------- constraint (SOLVED)
    def charges(self) -> Dict[int, int]:
        """q_v = div(E)_v mod N -- the Gauss constraint, solved rather than penalized."""
        N = self.N
        q = {v: 0 for v in self.vertices}
        E = self.E
        for v, incs in self._inc.items():
            s = 0
            for i, sign in incs:
                if E[i]:
                    s += sign * E[i]
            q[v] = s % N
        return q

    def total_charge(self) -> int:
        return sum(self.charges().values()) % self.N

    def check_gauss(self) -> bool:
        """Coboundary identity: total charge is identically 0 mod N."""
        return self.total_charge() == 0

    # ------------------------------------------------------------- observables
    @staticmethod
    def weight(a: int, N: int) -> int:
        """Word length of a in Z_N with generator {+-1}: min(a, N-a)."""
        a %= N
        return min(a, N - a)

    def electric_count(self) -> float:
        """Total electric flux cost sum_e |a_e| (word-length norm)."""
        N = self.N
        return float(sum(self.weight(a, N) for a in self.E))

    def invalidate_caches(self) -> None:
        """Drop the curvature cache.  Needed only if labels are mutated behind our back;
        :meth:`shift_g` invalidates automatically."""
        self._mag_cache = None

    def magnetic_energy_count(self) -> int:
        """Number of curved faces (B_f != identity).  Cached; invalidated by :meth:`shift_g`."""
        cached = getattr(self, "_mag_cache", None)
        if cached is not None:
            return cached
        from .holonomy import triangle_holonomy
        ident = self.group.identity()
        value = sum(triangle_holonomy(self.cx, f) != ident for f in self.cx.faces())
        self._mag_cache = value
        return value

    def energy(self, beta_B: float, beta_E: float) -> float:
        return beta_B * self.magnetic_energy_count() + beta_E * self.electric_count()

    def live_defects(self) -> Dict[int, int]:
        """Sites carrying nonzero charge (defect SITES, not partons: two unit charges that
        have merged onto one vertex appear here as a single site of charge 2 in Z3)."""
        return {v: q for v, q in self.charges().items() if q}

    def exited_charge(self) -> int:
        """Net charge sitting on boundary vertices = handed to the exterior reservoir."""
        q = self.charges()
        return sum(q[v] for v in self.boundary_vertices) % self.N

    # ------------------------------------------------------------- classification (pure)
    def nality(self) -> dict:
        """Pair-cancellation content of the live charges.  See :func:`nality_content`."""
        return nality_content(self.charges(), self.N)

    def is_baryonic(self) -> bool:
        return self.nality()["constituents"] > 0

    # ------------------------------------------------------------- moves
    def add_flux(self, edge, delta: int = 1) -> int:
        """a_e += delta (mod N).  Gauss holds BY DEFINITION of q: the two endpoint charges
        shift by -delta and +delta.  One rule covers pair creation, annihilation and motion."""
        i = self._eindex[tuple(sorted(edge))]
        self.E[i] = (self.E[i] + delta) % self.N
        return i

    def sub_flux(self, edge, delta: int = 1) -> int:
        """Exact inverse of :meth:`add_flux` (needed because Z_N moves are not involutions)."""
        return self.add_flux(edge, -delta)

    def shift_g(self, edge, delta: int = 1) -> None:
        """Multiply the connection label on `edge` by generator^delta (magnetic move)."""
        u, v = edge
        g = self.group
        gen = g.generators()[0]
        step = gen if delta > 0 else g.inverse(gen)
        val = self.cx.label(u, v)
        for _ in range(abs(delta)):
            val = g.multiply(val, step)
        self.cx.set_label(u, v, val)
        self._mag_cache = None

    def unshift_g(self, edge, delta: int = 1) -> None:
        self.shift_g(edge, -delta)

    # ------------------------------------------------------------- preparation
    def load_string(self, path_vertices, flux: int = 1) -> None:
        """Add `flux` units flowing ALONG the directed vertex path.

        Edges are stored canonically with u < v, so a traversal that runs against the canonical
        direction must SUBTRACT.  (Z2 does not care -- flipping is its own inverse -- which is
        exactly why this had to be written down for Z_N; caught by tests/test_gauss_zn.py.)
        """
        for u, w in zip(path_vertices, path_vertices[1:]):
            i = self._eindex[tuple(sorted((u, w)))]
            signed = flux if u < w else -flux
            self.E[i] = (self.E[i] + signed) % self.N

    def load_star(self, center: int, ends, flux: int = 1):
        """Seed `len(ends)` strings of equal flux from a common centre.

        In Z3 three arms give q_center = -3*flux = 0 and three unit charges at the tips: an
        irreducible (baryonic) object -- neutral overall, containing no cancelling pair.
        Returns the list of paths actually used.
        """
        paths = []
        for e in ends:
            p = self.shortest_path(center, e)
            if p is None or len(p) < 2:
                raise ValueError(f"no path from {center} to {e}")
            self.load_string(p, flux=flux)
            paths.append(p)
        return paths

    def shortest_path(self, a: int, b: int):
        """BFS on the 1-skeleton; returns a vertex path or None."""
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


# --------------------------------------------------------------------------- #
# N-ality classifier (pure, standalone so it can be tested against hand cases)
# --------------------------------------------------------------------------- #
def nality_content(charges: Dict[int, int], N: int) -> dict:
    """Maximal pairwise cancellation of live charges, k <-> (N-k).

    Returns a dict with:
      * ``pairs``        -- number of cancelling (k, N-k) pairs found;
      * ``residual``     -- sorted tuple of surviving (charge value, multiplicity);
      * ``constituents`` -- total residual sites, the irreducible content R;
      * ``kind``         -- 'vacuum' | 'mesonic' (neutral, fully pair-cancellable)
                            | 'baryonic' (neutral but NOT pair-cancellable).

    Note that a configuration with nonzero TOTAL charge is not reachable from div(E) at all;
    such input is reported as kind='charged' rather than silently normalised.
    """
    if N < 2:
        raise ValueError("N must be >= 2")
    counts = Counter(int(q) % N for q in charges.values())
    counts.pop(0, None)
    total = sum(k * c for k, c in counts.items()) % N

    residual: Dict[int, int] = {}
    pairs = 0
    seen = set()
    for k in sorted(counts):
        if k in seen:
            continue
        j = (-k) % N
        seen.update({k, j})
        if j == k:                       # self-inverse charge (exists iff N even)
            pairs += counts[k] // 2
            rest = counts[k] % 2
            if rest:
                residual[k] = rest
        else:
            m = min(counts.get(k, 0), counts.get(j, 0))
            pairs += m
            for x in (k, j):
                rest = counts.get(x, 0) - m
                if rest > 0:
                    residual[x] = rest

    constituents = sum(residual.values())
    if not counts:
        kind = "vacuum"
    elif total != 0:
        kind = "charged"                 # unreachable from a solved div(E); flagged, not hidden
    elif constituents == 0:
        kind = "mesonic"
    else:
        kind = "baryonic"
    return {
        "pairs": pairs,
        "residual": tuple(sorted(residual.items())),
        "constituents": constituents,
        "kind": kind,
        "total_charge": total,
    }


def charge_curvature_correlation(state) -> float:
    """Pearson correlation over vertices between live charge and incident curvature.

    Diagnostic for prediction PD (E069): in the abelian model the two sectors share no term in
    H and no shared move, so this must sit at the level of a control with the seed placed far
    away.  A growing correlation would be evidence of flux-charge binding -- i.e. a dyon.
    """
    from .holonomy import triangle_holonomy
    N = state.N
    ident = state.group.identity()
    q = state.charges()
    curv = {v: 0 for v in state.vertices}
    for f in state.cx.faces():
        if triangle_holonomy(state.cx, f) != ident:
            for v in f:
                curv[v] += 1
    xs = [float(q[v]) for v in state.vertices]
    ys = [float(curv[v]) for v in state.vertices]
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return 0.0                       # one factor constant -> no correlation defined
    return sxy / (sxx ** 0.5 * syy ** 0.5)
