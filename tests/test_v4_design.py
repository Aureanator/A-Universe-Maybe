"""v4.0 walk design checks (docs/DYNAMICS_DESIGN.md section 4)."""

from examples.v4_design_checks import checks


def test_v4_walk_identities():
    r = checks(n=3)
    assert r["unitary_trivial"] < 1e-12 and r["unitary_A4_irrep3"] < 1e-12
    assert r["szegedy_max_mismatch"] < 1e-9
    assert r["remainder_all_pm1"] and r["remainder_count"] == r["remainder_expected_arcs_minus_2V"]
    assert abs(r["BZ_lambda_min"] + 5 / 11) < 1e-9 and r["BZ_max_lambda_away_from_0"] < 0.97
    assert r["gauge_spectrum_max_diff"] < 1e-6
