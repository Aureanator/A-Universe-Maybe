"""The fermion verdict, computed from first principles (Layer-2 open problem 2 CLOSED).

Explicit D(A4)-modules + universal R-matrix R = sum_h e_h (x) h; vacuum lines found in the
grade-e subspace of W (x) W (project-first: per-vector grade filtering after SVD is wrong --
regression-guarded here); braiding c = flip o Rhat read off each vacuum line.

Result: among V4-flux dyons, exactly those with theta = -1 have R = -1 in the vacuum channel
of W (x) W -> TRUE FERMIONS by computed exchange, not just twist. Pure charges all R=+1
(Tannakian consistency of Rep(A4) inside D(A4)). Vacuum-channel multiplicities match
Verlinde N[0][i][i] sector by sector.
"""

import numpy as np
import pytest

from constraintnet.category import charge_conjugation, double_sectors, fusion_coefficients, s_matrix
from constraintnet.doubles import channel_intertwiners, module_for_sector, vacuum_braiding_eigenvalues
from constraintnet.groups import AlternatingGroup4


@pytest.fixture(scope="module")
def report():
    return vacuum_braiding_eigenvalues()


def test_vacuum_channels_match_verlinde():
    g = AlternatingGroup4()
    sectors = double_sectors(g)
    N = fusion_coefficients(s_matrix(sectors, g))
    rows = vacuum_braiding_eigenvalues()
    found = {}
    for r in rows:
        key = r["sector"]
        found[key] = found.get(key, 0) + 1
    expected = {str(W): N[0][i][i] for i, W in enumerate(sectors)}
    assert found == {k: v for k, v in expected.items() if v > 0}


def test_theta_minus_one_dyons_are_true_fermions(report):
    fermions = [r for r in report if "TRUE FERMION" in r["verdict"]]
    labels = sorted(r["sector"] for r in fermions)
    assert labels == ["([c3], W10)", "([c3], W11)"]
    for r in fermions:
        assert abs(r["theta"] + 1) < 1e-9 and r["R_vacuum_channel"] == -1


def test_pure_charges_have_bosonic_exchange(report):
    charges = [r for r in report if "([c0]" in r["sector"]]
    assert len(charges) == 2                                   # 1 and 3 (1',1'' pair crosswise)
    assert all(r["R_vacuum_channel"] == +1 for r in charges)


def test_twist_and_statistics_agree_on_all_found_channels(report):
    """For every vacuum channel computed: sign(R) == sign(theta) where theta is real.

    This agreement is a THEOREM of this model now, not an assumption; if a future change
    breaks it, the ribbon structure and exchange have decoupled and must be reconciled.
    """
    for r in report:
        assert abs(r["theta"].imag) < 1e-9                     # real theta on all channels found
        expected_R = -1 if r["theta"].real < 0 else +1
        assert r["R_vacuum_channel"] == expected_R


def test_module_axioms_hold_for_all_sectors():
    """Construction-time asserts (representation law, unitarity) must survive for all 14."""
    g = AlternatingGroup4()
    for W in double_sectors(g):
        mod = module_for_sector(W, g)                          # raises on axiom failure
        assert mod.dimension == len(mod.fluxes) * mod.dim_rho


# ------------------------------------------- E031: pair channels -- monodromy vs category data

def test_pair_channel_monodromy_matches_theta_ratio_all_channels():
    """THE measurement (E031): for every sector pair and every fusion channel,
    the concrete double braid (universal R-matrix) acts as theta_c/(theta_a theta_b),
    AND the concrete Hom dimension equals the Verlinde coefficient.

    520 channels over all 14x14 pairs; internal asserts raise on any disagreement --
    this test is the loop-loop braiding prediction table for Layer-2 item 3b.
    """
    from constraintnet.doubles import pair_channel_report
    rows, n_checked, max_err = pair_channel_report()
    assert n_checked == 520                                    # full coverage of D(A4) channels
    assert max_err < 1e-8                                      # measured == predicted exactly


def test_channel_intertwiners_respect_grading():
    """Regression (E031 bug): Hom must commute with BOTH k-actions AND flux-grade projectors.

    Without grade constraints, spurious grade-mixing maps inflate Hom (Schur fails: e.g.
    Hom(X, 1(x)X) came out 2 instead of 1). The Verlinde cross-check inside the solver
    is what catches it; this test pins the smallest failing case explicitly.
    """
    g = AlternatingGroup4()
    sectors = double_sectors(g)
    N = fusion_coefficients(s_matrix(sectors, g))
    mod1 = module_for_sector(sectors[0], g)                    # vacuum
    modX = module_for_sector(sectors[4], g)                    # ([c1], chi0)
    Ts = channel_intertwiners(mod1, modX, modX)
    assert len(Ts) == N[4][0][4] == 1                          # Schur restored by grading


def test_physical_eigenvalues_are_transversal_independent():
    """E028 caveat (iii): R = -1 for the fermions and channel monodromies must not depend
    on which transversal t_x was chosen -- only gauge copies change, never physics.
    """
    import constraintnet.doubles as dbl
    g = AlternatingGroup4()
    sectors = double_sectors(g)
    standard = {r["sector"]: r["R_vacuum_channel"] for r in vacuum_braiding_eigenvalues()}
    assert any(v == -1 for v in standard.values())             # fermions present at all
    original = dbl.module_for_sector
    try:
        def alt(sector, group=None, transversal_scan=None):
            scan = list(reversed(list((group or AlternatingGroup4()).elements)))
            return original(sector, group,
                            transversal_scan=scan if transversal_scan is None else transversal_scan)
        dbl.module_for_sector = alt
        reversed_rows = vacuum_braiding_eigenvalues()
    finally:
        dbl.module_for_sector = original
    got = {r["sector"]: r["R_vacuum_channel"] for r in reversed_rows}
    assert got == standard                                     # identical physics, other transversal
