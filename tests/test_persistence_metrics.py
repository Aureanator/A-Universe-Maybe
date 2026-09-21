"""Tests for extent-based persistence metrics (E068). Pure functions over trajectories;
these pin the arithmetic and the E066 failure-mode detection, independent of any driver."""

from __future__ import annotations

import pytest

from constraintnet.persistence_metrics import (
    evaluate,
    extent_stability,
    lifetime_until,
    locality,
    signal_to_noise,
    vacuum_noise,
)


def test_extent_stability_normalizes_to_initial():
    assert extent_stability([4, 4, 5, 12]) == [1.0, 1.0, 1.25, 3.0]


def test_extent_stability_zero_or_empty_is_empty():
    assert extent_stability([]) == []
    assert extent_stability([0, 3, 5]) == []  # zero initial -> undefined ratio -> []


def test_lifetime_none_when_within_band():
    stab = extent_stability([10, 11, 9, 12, 8])  # stays within [1/3, 3]
    assert lifetime_until(stab, band=3.0) is None


def test_lifetime_detects_growth_into_blob():
    stab = extent_stability([5, 6, 20, 40])  # crosses band at index 2 (20/5=4 > 3)
    assert lifetime_until(stab, band=3.0) == 2


def test_lifetime_detects_shrink_away():
    stab = extent_stability([100, 90, 20])  # 20/100 = 0.2 < 1/3 at index 2
    assert lifetime_until(stab, band=3.0) == 2


def test_locality_median_and_bounds():
    # object stays a small fraction of a large global structure -> low locality
    tracked = [5, 5, 5]
    glob = [100, 120, 90]
    assert locality(tracked, glob) == pytest.approx(5 / 100)


def test_locality_detects_becoming_the_background():
    # E066 failure: tracked support equals global (tracker followed the heat)
    assert locality([50, 80, 200], [50, 80, 200]) == pytest.approx(1.0)


def test_vacuum_noise_mean():
    assert vacuum_noise([]) == 0.0
    assert vacuum_noise([0, 1, 1, 2]) == pytest.approx(1.0)


def test_evaluate_compact_stable_object_is_independently_persistent():
    tracked = [6] * 40                 # object keeps its size
    glob = [200 + t for t in range(40)]  # quiet-ish background, object is a small fraction
    v = evaluate(tracked, glob, band=3.0, vacuum_components=[1, 1, 2])
    assert v.survived_horizon and v.localized
    assert v.independently_persistent


def test_evaluate_dissolving_blob_is_not_localized():
    # E066 regime: tracked support balloons to match global -> locality ~1, not localized
    tracked = [6] + [20 * t for t in range(1, 40)]
    glob = list(tracked)
    v = evaluate(tracked, glob, band=3.0, vacuum_components=[3, 4, 5])
    assert not v.localized
    assert not v.independently_persistent


def test_signal_to_noise_lone_object_in_cold_vacuum_is_high():
    # E068 finding: a lone persistent object in an empty (cold) vacuum has locality ~1 but
    # is genuinely there -- SNR against near-zero vacuum is the load-bearing signal.
    assert signal_to_noise([6] * 40, vacuum_level=0.0) > 5.0


def test_signal_to_noise_seed_matching_vacuum_is_zero():
    # E066 regime: seed sustains no more structure than unseeded churn -> SNR ~ 0 (no object)
    assert abs(signal_to_noise([30] * 40, vacuum_level=30.0)) < 1e-9


def test_evaluate_reports_thresholds_verbatim():
    v = evaluate([10] * 10, [40] * 10, band=2.5, vacuum_components=[0, 0])
    assert v.band == 2.5 and v.horizon == 10
    assert v.vacuum_noise_mean == 0.0
