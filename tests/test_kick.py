"""Kick-test experiments (branch bionic/kick-test): violation restoration regimes.

All trials are deterministic under fixed seeds; assertions encode the measured physics,
not wishes.  Fast settings here; see examples/kick_test.py for the full study.
"""

from __future__ import annotations

import pytest

from constraintnet.kick import curvature_energy, force_kick, run_kick_trial
from constraintnet.holonomy import triangle_holonomy
from constraintnet.persistence import seed_charged_defect
from constraintnet.region import Region
from constraintnet.seeds import kuhn_ball


def _setup():
    cx = kuhn_ball(group="A4", n=2)
    region = Region(cx, cx.tetrahedra(), "universe")
    info = seed_charged_defect(cx)
    return cx, region, info


# ------------------------------------------------------------------ kick sanity
@pytest.mark.parametrize("mode,e_down", [("down", True), ("up", False)])
def test_kick_changes_appearance_and_energy_direction(mode, e_down):
    cx, region, _ = _setup()
    signature0 = region.appearance().signature()
    energy0 = curvature_energy(cx)
    kick = force_kick(cx, region, mode=mode)
    assert region.appearance().signature() != signature0
    energy1 = curvature_energy(cx)
    if e_down:
        assert energy1 < energy0
    else:
        # DEGENERACY FINDING: every non-identity class of A4 contains a generator, so the
        # class-weighted curvature action assigns weight 1 to ALL charges -- an "up" kick
        # can never strictly raise E from an already-charged state.  The action is blind
        # to charge type; it only counts curved faces.
        assert energy1 >= energy0


# ------------------------------------------------------------------ reject rule
@pytest.mark.parametrize("seed", [1, 2])
def test_reject_rule_can_never_restore(seed):
    """Structural: legality is relative to the CURRENT appearance, so undoing the kick
    is itself illegal.  The kicked sector is permanent."""
    trial = run_kick_trial("reject", steps=400, seed=seed)
    assert trial.restored_sector_at is None
    assert trial.restored_charge_at is None
    assert trial.distinct_sectors_visited == 2  # initial + locked-in kicked sector


# ------------------------------------------------------------------ free diffusion
@pytest.mark.parametrize("seed", [1, 2])
def test_free_diffusion_never_restores_full_sector(seed):
    """Weak observables recover by coincidence; the complete conserved data does not."""
    trial = run_kick_trial("free", steps=800, seed=seed)
    assert trial.restored_sector_at is None
    # superselection drift: a large fraction of steps show NEW external configurations
    assert trial.distinct_sectors_visited > 300


def test_free_charge_recovery_is_coincidence_not_pressure():
    """Charge classes do come back quickly under free diffusion -- but only because the
    observable is tiny (two faces, ~6% probability per step at stationarity)."""
    trial = run_kick_trial("free", steps=800, seed=1)
    assert trial.restored_charge_at is not None  # measured: ~step 140


# ------------------------------------------------------------------ metropolis
@pytest.mark.parametrize("seed", [1, 2])
def test_low_temperature_freezes_wrong_state_down_kick(seed):
    """A charge-annihilating kick LOWERS curvature energy; at low T nothing climbs back.
    The zero-temperature limit is a system locked into the violated sector."""
    trial = run_kick_trial("metro", beta=4.0, steps=400, seed=seed, kick_mode="down")
    assert trial.accepted < 50          # measured: 0/3000 in the full study
    assert trial.restored_sector_at is None


def test_up_kick_low_temperature_can_genuinely_restore():
    """Cold dynamics after an energy-raising kick can slide back into the original sector
    -- the only regime observed with genuine restoration pressure (see study table)."""
    trial = run_kick_trial("metro", beta=4.0, steps=800, seed=2, kick_mode="up")
    assert trial.restored_charge_at is not None and trial.restored_charge_at < 400
