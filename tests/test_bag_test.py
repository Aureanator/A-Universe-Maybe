"""P16 bag test pins: no hidden flat entropy; minimal excitations scale with volume."""

import pytest

from examples.bag_test import m1_flat_fillings, m2_lowest_excitations


@pytest.mark.parametrize("group,n", [("Z3", 1), ("Z3", 2), ("A4", 1), ("A4", 2)])
def test_flat_interior_has_unique_physical_filling(group, n):
    row = m1_flat_fillings(group, n)
    assert row["status"] == "exact"
    assert row["raw_flat_fillings"] == row["gauge_orbit_size"]
    assert row["physical_I"] == 1


@pytest.mark.parametrize("group", ["Z3", "A4"])
@pytest.mark.parametrize("n", [2, 3, 4])
def test_minimal_excitation_supports_scale_like_volume(group, n):
    row = m2_lowest_excitations(group, n)
    assert row["H_min"] == 4 and row["H_values"] == [4, 6]
    assert row["distinct_supports_at_H_min"] == 3 * n * n * (n - 1)
