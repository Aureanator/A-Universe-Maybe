"""Kick test (experimental): does a violated constraint restore itself?

The proposal under test (Satish): *do* the illegal moves -- the opposing constraints
would win next turn, so evolution stays an ergodic irreducible Markov chain and charge
conservation emerges statistically instead of by rejection.

Three regimes are compared after forcing **one** illegal boundary relabelling (the kick):

``"reject"``   the production rule (v0.4): accept only appearance-preserving moves.
               Legality is defined against the *current* appearance, so a move that
               would undo the kick changes it -- and is rejected.  The kicked sector is
               permanent: restoration is structurally impossible, not merely unlikely.
``"free"``     accept everything: uniform random walk on labelings G^E.  Restoration is
               guaranteed *eventually* (finite + irreducible ⇒ positive recurrent) with
               expected return ~ |G|^{E_surface}; we measure whether it happens inside
               the trial window at all.
``"metro"``    Metropolis acceptance on a gauge-invariant curvature action,
               E = Σ_faces w([Φ_f]),  w(class) = min word length over the class.
               Violations accepted with probability e^{-β ΔE}: the finite-temperature
               generalisation whose zero-temperature limit is the reject rule.

Observables per trial (first restoration times; ``None`` = never inside the window):

* ``sector``  full appearance signature equals the pre-kick one;
* ``charge``  both frozen core faces carry their original curvature classes;
* ``label``   the kicked edge carries its exact original element.

Inertia reading: the relaxation response to a kick *is* a dynamical mass proxy -- how
fast (or whether) the constraint reasserts itself.

Measured (full study, 20 trials, 3000 steps each; examples/kick_test.py)
------------------------------------------------------------------------
* reject-rule: restoration NEVER, both kick directions, exactly 2 sectors ever visited.
  Legality is defined against the current appearance, so undoing a violation is itself
  illegal -- a one-way door.  Structural, not statistical.
* free diffusion: full sector NEVER restored (0/4); weak observables restore fast
  (charge classes at steps 68–548) but that is pure coincidence on a tiny observable,
  and ~60 % of steps visit brand-new external configurations (superselection drift).
  Ergodicity guarantees return in ~|G|^{E_surface}; matter needs observational times.
* Metropolis, charge-annihilating (down) kick: low T freezes the violated state
  (0/3000 accepted -- restoration costs an activation the bath won't pay); intermediate T
  wanders and passes through charges by luck.  No targeted restoration pressure.
* Metropolis, energy-raising (up) kick + LOW temperature: **genuine reproducible
  restoration** -- full sector recovered in BOTH trials (steps 286 and 160; one also
  restored the exact label).  Cold downhill relaxation re-imposes the constraint when
  the violation costs curvature.
* Degeneracy finding: every non-identity class of A4 contains a generator, so this
  action weights all charges equally -- it counts curved faces and is blind to charge
  type.  Restoration returns *a* low-curvature sector; targeting THE original sector
  would need an action measuring distance-to-boundary-appearance, not total curvature.

Verdict: "the opposing constraints win next turn" holds only in the cold +
energy-raising corner of parameter space; everywhere else violations persist or restore
only by coincidence.  Exact conservation (reject rule) and restoration dynamics are
different physics, not two views of one mechanism.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

from .complex import SimplicialComplex
from .holonomy import triangle_holonomy
from .moves import apply_move, propose_edge_move
from .region import Region
from .seeds import kuhn_ball
from .persistence import seed_charged_defect

__all__ = ["curvature_energy", "force_kick", "KickTrial", "run_kick_trial", "run_kick_study"]

FaceKey = Tuple[int, int, int]


# --------------------------------------------------------------------------- #
# gauge-invariant curvature action
# --------------------------------------------------------------------------- #
def _class_energy_table(group) -> Dict[FrozenSet, float]:
    """w(class) = minimum word length over the elements of a conjugacy class."""
    return {
        frozenset(cls): min(group.word_length(element) for element in cls)
        for cls in group.conjugacy_classes()
    }


def curvature_energy(cx: SimplicialComplex, table=None) -> float:
    """E = Σ_faces w([Φ_f]).  Gauge invariant because w is taken class-wise."""
    table = table if table is not None else _class_energy_table(cx.group)
    return float(
        sum(table[frozenset(cx.group.class_of(triangle_holonomy(cx, face)))] for face in cx.faces())
    )


# --------------------------------------------------------------------------- #
# the kick
# --------------------------------------------------------------------------- #
def force_kick(cx: SimplicialComplex, region: Region, mode: str = "down") -> Dict:
    r"""Force one appearance-changing relabelling.  Illegal by construction.

    ``mode="down"`` picks the appearance-changing relabelling with the LOWEST resulting
    total curvature energy (charge annihilation -- restoration then costs an Arrhenius
    activation); ``mode="up"`` picks the highest (restoration is energetically downhill,
    so pressure exists if anywhere does).
    """
    group = cx.group
    signature_before = region.appearance().signature()
    for edge in sorted(region.boundary_surface_edges()):
        old = cx.label(*edge)
        # a relabelling perturbs EVERY face containing the edge, so rank candidates by
        # the true total-energy change, not by the label's own class weight
        evaluated = []
        for candidate in group.elements:
            if candidate == old:
                continue
            cx.set_label(*edge, candidate)
            if region.appearance().signature() != signature_before:
                evaluated.append((curvature_energy(cx), candidate))
        cx.set_label(*edge, old)
        if evaluated:
            _, best = max(evaluated) if mode == "up" else min(evaluated)
            cx.set_label(*edge, best)
            return {"edge": edge, "old_label": old, "new_label": best}
    raise AssertionError("no single relabelling changes the appearance -- kick impossible")


# --------------------------------------------------------------------------- #
# trials
# --------------------------------------------------------------------------- #
@dataclass
class KickTrial:
    variant: str
    beta: Optional[float]
    steps: int
    seed: int
    kick_mode: str = "down"
    restored_sector_at: Optional[int] = None
    restored_charge_at: Optional[int] = None
    restored_label_at: Optional[int] = None
    accepted: int = 0
    proposals: int = 0
    distinct_sectors_visited: int = 1

    def as_row(self) -> str:
        def fmt(t):
            return "never" if t is None else str(t)

        beta = "-" if self.beta is None else f"{self.beta:g}"
        return (
            f"{self.kick_mode:>4} {self.variant:<7} beta={beta:<5} seed={self.seed:<3} |"
            f" sector->{fmt(self.restored_sector_at):>6}"
            f" charge->{fmt(self.restored_charge_at):>6}"
            f" label->{fmt(self.restored_label_at):>6}"
            f" | accepted {self.accepted:>5}/{self.proposals}"
            f" | sectors visited {self.distinct_sectors_visited}"
        )


def run_kick_trial(
    variant: str = "free",
    beta: Optional[float] = None,
    steps: int = 5000,
    seed: int = 1,
    n: int = 2,
    kick_mode: str = "down",
) -> KickTrial:
    """Kick once, then evolve under the chosen acceptance regime; record restoration times."""
    if variant not in ("reject", "free", "metro"):
        raise ValueError(f"unknown variant {variant!r}")

    cx = kuhn_ball(group="A4", n=n)
    region = Region(cx, cx.tetrahedra(), "universe")
    seed_info = seed_charged_defect(cx)
    group = cx.group

    sector0 = region.appearance().signature()
    core_faces = sorted(face for face, cid in region.appearance().face_curvatures if cid != 0)
    core_classes0 = {
        face: frozenset(group.class_of(triangle_holonomy(cx, face))) for face in core_faces
    }

    kick = force_kick(cx, region, mode=kick_mode)
    assert kick["edge"] == tuple(seed_info["edge"]), "kick should land on the seeded charge edge"
    kicked_label = kick["old_label"]

    table = _class_energy_table(group) if variant == "metro" else None
    rng = random.Random(seed)
    trial = KickTrial(variant=variant, beta=beta, steps=steps, seed=seed, kick_mode=kick_mode)
    sectors_seen = {sector0}  # pre-kick sector counts as visited (it is the target)

    def energy() -> float:
        return curvature_energy(cx, table)

    e_current = energy() if variant == "metro" else 0.0

    for t in range(1, steps + 1):
        move = propose_edge_move(cx, rng)
        trial.proposals += 1

        if variant == "reject":
            before = region.appearance()
            apply_move(cx, move)
            if region.appearance() == before:
                accepted = True
            else:
                from .moves import revert_move

                revert_move(cx, move)
                accepted = False
        elif variant == "free":
            apply_move(cx, move)
            accepted = True
        else:  # metro
            apply_move(cx, move)
            e_new = energy()
            delta = e_new - e_current
            if delta <= 0 or rng.random() < math.exp(-beta * delta):
                e_current = e_new
                accepted = True
            else:
                from .moves import revert_move

                revert_move(cx, move)
                accepted = False

        trial.accepted += int(accepted)

        signature = region.appearance().signature()
        sectors_seen.add(signature)
        if trial.restored_sector_at is None and signature == sector0:
            trial.restored_sector_at = t
        if (
            trial.restored_charge_at is None
            and core_faces
            and all(
                frozenset(group.class_of(triangle_holonomy(cx, face))) == core_classes0[face]
                for face in core_faces
            )
        ):
            trial.restored_charge_at = t
        if trial.restored_label_at is None and cx.label(*kick["edge"]) == kicked_label:
            trial.restored_label_at = t

    trial.distinct_sectors_visited = len(sectors_seen)
    return trial


def run_kick_study(steps: int = 3000, seeds=(1, 2), betas=(0.25, 1.0, 4.0)) -> List[KickTrial]:
    """Full comparison grid: kick up/down × reject / free diffusion / Metropolis at several β."""
    trials: List[KickTrial] = []
    for mode in ("down", "up"):
        for seed in seeds:
            trials.append(run_kick_trial("reject", steps=steps, seed=seed, kick_mode=mode))
            trials.append(run_kick_trial("free", steps=steps, seed=seed, kick_mode=mode))
            for beta in betas:
                trials.append(
                    run_kick_trial("metro", beta=beta, steps=steps, seed=seed, kick_mode=mode)
                )
    return trials
