"""POSTULATED Z2 transport conserving defect number and projector energy.

This changes individual star occupations; it is not locally gauge invariant.
No derivation from the implication axiom, binding, or fermion claim is made.
See docs/P32B_TRANSPORT.md for the exact algebra and registered scope.
"""

import numpy as np


class Z2DefectTransport:
    """Local T_ab=W_ab(1-S_a S_b)/2 on the existing edge Hilbert space."""

    def __init__(self, dynamics, kappa=0.2):
        self.dynamics = dynamics
        self.patch = p = dynamics.patch
        if p.n != 2:
            raise ValueError('this diagnostic requires Z2')
        if not np.isfinite(kappa) or kappa < 0:
            raise ValueError('kappa must be finite and nonnegative')
        self.kappa = float(kappa)
        h = next(i for i in range(p.n) if i != p.e_id)
        # Z2 gauge transformations are involutive permutations: scatter=gather.
        self.star_flips = {v: dynamics.perms[v][h] for v in p.vertices}
        char = np.full(p.n, -1.0)
        char[p.e_id] = 1.0
        self.phases = {e: dynamics.string_factor(e, char).real for e in p.edges}

    def occupation(self, vertex, state):
        state = self.dynamics._state(state)
        return (state - state[self.star_flips[vertex]]) / 2

    def number(self, state):
        state = self.dynamics._state(state)
        return sum((self.occupation(v, state) for v in self.patch.vertices),
                   np.zeros_like(state))

    def hop(self, edge, state):
        state = self.dynamics._state(state)
        a, b = edge = tuple(sorted(edge))
        one = (state - state[self.star_flips[a]][self.star_flips[b]]) / 2
        return self.phases[edge] * one

    def kinetic(self, state):
        state = self.dynamics._state(state)
        return -self.kappa * sum((self.hop(e, state) for e in self.patch.edges),
                                 np.zeros_like(state))

    def directed_hop(self, target, source, state):
        """Unit-amplitude t_target,source; zero unless only source is occupied."""
        return self.hop((target, source), self.occupation(source, state))

    def hamiltonian(self, state):
        return self.dynamics.hamiltonian(state) + self.kinetic(state)

    def currents(self, state):
        """Expectations of J_ab=-i[K_ab,n_a], oriented as stored edges a<b."""
        state = self.dynamics._state(state)
        norm = np.vdot(state, state).real
        if norm == 0:
            raise ValueError('currents require a nonzero state')
        return {e: float(2 * np.vdot(-self.kappa * self.hop(e, state),
                                     self.occupation(e[0], state)).imag / norm)
                for e in self.patch.edges}

    def continuity_residual(self, state):
        """Exact Schrödinger derivative plus edge-current divergence, by vertex."""
        state = self.dynamics._state(state)
        norm = np.vdot(state, state).real
        currents = self.currents(state)  # Also rejects the zero vector.
        derivative = -1j * self.hamiltonian(state)
        residual = {v: float(2 * np.vdot(self.occupation(v, state), derivative).real / norm)
                    for v in self.patch.vertices}
        for (a, b), j in currents.items():
            residual[a] += j
            residual[b] -= j
        return residual
