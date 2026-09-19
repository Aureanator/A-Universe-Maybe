"""P18 pins: the project mesh is BCC in its emergent metric; sharp 3D fronts; mass wake."""

import numpy as np
import pytest

from examples.propagation_test import (check_bcc, damped_wave_trapping, evolve, interior_fraction,
                                       kuhn_star, square_star, symbol_anisotropy)


def test_kuhn_star_is_bcc_in_emergent_metric():
    D, ring = kuhn_star()
    r = check_bcc(D, ring)
    assert np.allclose(r["A_tilde_uniform"], 2 * np.eye(3) + 2 * np.ones((3, 3)))
    assert r["n_short_ring6"] == 8 and r["n_long_ring4"] == 6 and r["short_lengths_equal"]
    assert abs(r["long_over_short"] - 2 / np.sqrt(3)) < 1e-12
    assert np.allclose(r["short_pairwise_cosines"], [-1, -1 / 3, 1 / 3])
    assert np.allclose(r["long_pairwise_cosines"], [-1, 0]) and r["long_along_cube_axes"]


def test_ring_weighting_removes_quartic_anisotropy():
    D, ring = kuhn_star()
    uni = symbol_anisotropy(D, np.ones(len(D)))
    wtd = symbol_anisotropy(D, np.where(ring == 4, 0.5, 1.0))
    assert abs(uni["loglog_slope"] - 2) < 0.02 and abs(wtd["loglog_slope"] - 4) < 0.02


@pytest.mark.slow
def test_sharp_in_3d_tail_in_2d_wake_with_mass():
    D, _ = kuhn_star()
    s = 1.5; t = 12 * s
    _, _, r, f, _ = evolve(D, np.ones(len(D)), s, [t])
    assert interior_fraction(r, f[t], t, s) < 1e-5
    _, _, r, f, _ = evolve(D, np.ones(len(D)), s, [t], m=1.0 / s)
    assert interior_fraction(r, f[t], t, s) > 0.3
    D2, _ = square_star()
    _, _, r, f, _ = evolve(D2, np.ones(4), s, [t])
    assert interior_fraction(r, f[t], t, s) > 0.01


def test_real_damped_wave_keeps_exactly_dark_energy():
    for row in damped_wave_trapping()["rows"]:
        assert abs(row["energy_fraction_T"] - row["predicted_dark_energy_fraction"]) < 1e-6
