"""Stochastic curvature-action hypothesis driver; no particle or reaction rules.

Uses an external Metropolis bath. H + bath_ledger is bookkeeping conservation of
the chosen dimensionless action, not a derived physical first law. The outer
boundary labels are fixed; no object's own core or boundary is frozen.
"""

import math
import random

from .curvature import CurvatureState
from .drivers import DriverRecord, DynamicsDriver


class CurvatureDriver(DynamicsDriver):
    def __init__(self, cx, *, beta, seed=0):
        if math.isnan(beta) or beta < 0:
            raise ValueError("beta must be nonnegative")
        self.state = CurvatureState(cx)
        if not self.state.interior_edges:
            raise ValueError("curvature driver needs interior edges")
        self.beta = beta
        self.rng = random.Random(seed)
        self.generators = [i for i in range(len(self.state.elements))
                           if i != self.state.identity]
        self.step = self.accepted = self.bath_ledger = 0
        self.initial_energy = self.state.energy
        self.last_event = None

    def advance(self):
        edge = self.rng.choice(self.state.interior_edges)
        multiplier = self.rng.choice(self.generators)
        new, changed, delta = self.state.proposal(edge, multiplier)
        # Always draw, even for downhill moves, for consistent RNG consumption.
        uniform = self.rng.random()
        accepted = delta <= 0 or uniform < math.exp(-self.beta * delta)
        self.step += 1
        if accepted:
            self.state.commit(edge, new, changed, delta)
            self.accepted += 1
            self.bath_ledger -= delta
        assert self.state.energy + self.bath_ledger == self.initial_energy
        self.last_event = {"step": self.step, "edge": edge, "multiplier": multiplier,
                           "accepted": accepted, "delta_proposed": delta,
                           "action": self.state.energy, "bath_ledger": self.bath_ledger}
        return DriverRecord(driver="C", fate="accepted" if accepted else "vetoed",
                            counts_toward_rho=accepted, model="curvature_metropolis_v1",
                            detail=f"edge={edge} deltaH={delta} H={self.state.energy}")

    def event_ontology(self):
        return "counterfactual-veto"

    def reversible(self):
        # Edge rewrites are invertible; the bath-driven stochastic map is not.
        return False
