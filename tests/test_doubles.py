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
from constraintnet.doubles import module_for_sector, vacuum_braiding_eigenvalues
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
