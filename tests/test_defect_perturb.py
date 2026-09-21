"""P33 local recreation: registered algebra identities and spectral predictions.

All tolerances per docs/P33_VIRTUAL_PAIRS.md (1e-10 for algebra/evolution residuals).
The K4 cancellation is the PRE-EXECUTION refinement recorded in commit a836e7d; the bipyramid
second-order improvement is the registered HIT condition at the smallest coupling.
"""

import numpy as np
import pytest

from constraintnet.defect_perturb import EffectiveDefects


@pytest.fixture(scope="module")
def tet():
    return EffectiveDefects("tetrahedron")


@pytest.fixture(scope="module")
def bip():
    return EffectiveDefects("bipyramid")


def test_fixtures_and_flat_dimensions(tet, bip):
    assert (tet.patch.dim, tet.flat_dim) == (64, 8)      # 2^6 edges; even subsets of 4 vertices
    assert (bip.patch.dim, bip.flat_dim) == (512, 16)    # 2^9 edges; even subsets of 5 vertices
    assert tet.E_vac == pytest.approx(-8.0, abs=1e-9)
    assert bip.E_vac == pytest.approx(-12.0, abs=1e-9)


def test_subset_basis_orthonormal_and_complete(tet, bip):
    for ed in (tet, bip):
        audit = ed.basis_audit()
        assert max(audit.values()) < 1e-10


def test_first_order_block_identity_matches_p32b_form(tet, bip):
    # sum_m P_m V P_m == -sum_ab W_ab (I - S_a S_b)/2 on the full space.
    for ed in (tet, bip):
        assert ed.first_order_block_identity() < 1e-10


def test_flat_sector_duality(tet, bip):
    for ed in (tet, bip):
        d = ed.duality_audit()
        assert max(d.values()) < 1e-10


def test_second_order_coefficient_formulas(tet, bip):
    for ed in (tet, bip):
        coeffs = ed.coefficient_predictions()
        errors = [v for k, v in coeffs.items() if not k.endswith("_value")]
        assert max(errors) < 1e-10
        n_edges = len(ed.patch.edges)
        assert coeffs["C_vac_value"] == pytest.approx(-n_edges / 2, abs=1e-10)


def test_k4_second_order_cancellation_is_identically_zero(tet):
    """Pre-execution refinement (a836e7d): on K4 every registered coefficient vanishes."""
    c_pair = tet.pair_matrix(tet.second_order_full()["C"])
    assert np.abs(c_pair).max() < 1e-12


def test_bipyramid_second_order_is_nonzero(bip):
    c_pair = bip.pair_matrix(bip.second_order_full()["C"])
    assert np.abs(c_pair).max() > 0.5   # generic graph: corrections genuinely present


def test_sweep_orders_and_k4_degeneracy(tet, bip):
    tet_sweeps = tet.sweep()
    for s in tet_sweeps:
        assert s["first_order_error"] == pytest.approx(s["second_order_error"], abs=1e-12)
    orders = [s["observed_order_second"] for s in tet_sweeps[1:] if s["observed_order_second"]]
    assert all(abs(o - 3.0) < 0.15 for o in orders)     # O(lam^3) residual, both approximations

    bip_sweeps = bip.sweep()
    smallest = bip_sweeps[0]
    assert smallest["second_order_error"] < smallest["first_order_error"]   # registered HIT
    improvement_orders = [s["observed_order_second"] for s in bip_sweeps[1:] if s["observed_order_second"]]
    assert all(o > 2.5 for o in improvement_orders)


def test_exact_evolution_conservation_and_sector_departure(bip):
    rows = bip.evolve_bare_pairs(0.08)
    bare_pair_probability_0 = None
    max_departure = 0.0
    for row in rows:
        assert abs(row["norm"] - 1.0) < 1e-10
        probs = {int(k): v for k, v in row["sector_probabilities"].items()}
        flatness = sum(p for m, p in probs.items() if m % 2 == 0)
        assert abs(flatness - 1.0) < 1e-10              # V and H0 preserve the flat sector
        if row["time"] == 0.0:
            bare_pair_probability_0 = probs[2]
        else:
            max_departure = max(max_departure, 1.0 - probs[2])
    assert bare_pair_probability_0 > 0.99
    # Registered prediction: nonzero departure from the bare two-defect sector (>1e-8).
    assert max_departure > 1e-8
