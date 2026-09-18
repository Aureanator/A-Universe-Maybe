"""Spectral dimension probes with ground-truth controls (referee audit item 9)."""

from __future__ import annotations

import pytest

from constraintnet.seeds import kuhn_ball
from constraintnet.spectral import (
    return_probabilities,
    spectral_dimension_estimate,
    tetra_adjacency,
    vertex_adjacency,
)


def test_path_graph_is_one_dimensional():
    path = {i: {j for j in (i - 1, i + 1) if 0 <= j < 41} for i in range(41)}
    probs = return_probabilities(path, steps=20)
    assert probs[0] == 1.0
    d = spectral_dimension_estimate(probs, 2, 8)
    assert 0.6 <= d <= 1.5, f"path graph should diffuse ~1D, got {d}"


def _z3_box(L):
    grid = {}
    for x in range(L):
        for y in range(L):
            for z in range(L):
                grid[(x, y, z)] = {
                    (a, b, c)
                    for a, b, c in [
                        (x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                        (x, y - 1, z), (x, y, z + 1), (x, y, z - 1),
                    ]
                    if 0 <= a < L and 0 <= b < L and 0 <= c < L
                }
    return grid


def test_finite_size_dominance_matched_control():
    """Honest P5 finding: at every size we can afford, d_s(t) reads well below 3 -- for Z^3
    BOXES TOO (6-cube reads ~2).  The estimator is validated by MATCHED CONTROL: a Kuhn ball
    must diffuse like the cubic lattice box of comparable size, not anomalously.  Absolute
    d_s -> 3 requires larger meshes / heat-kernel extrapolation (logged as follow-up)."""
    box = _z3_box(6)
    d_box = spectral_dimension_estimate(return_probabilities(box, steps=16), 2, 8)
    assert 0.5 <= d_box <= 4.0

    cx = kuhn_ball("A4", n=2)
    d_v = spectral_dimension_estimate(
        return_probabilities(vertex_adjacency(cx), steps=16), 2, 8)
    assert abs(d_v - d_box) < 1.2, (
        f"Kuhn ball diffusion anomalous vs matched Z^3 box: {d_v} vs {d_box}")


def test_d_s_rises_with_mesh_size():
    """Trend requirement: bigger Kuhn balls diffuse closer to 3 (no fractal collapse)."""
    ds = []
    for n in (1, 2, 3):
        cx = kuhn_ball("A4", n=n)
        probs = return_probabilities(tetra_adjacency(cx), steps=20)
        ds.append(spectral_dimension_estimate(probs, 2, 8))
    assert ds[0] < ds[1] <= ds[2] + 0.3, f"d_s not rising with size: {ds}"


def test_return_probability_normalised():
    cx = kuhn_ball("A4", n=1)
    probs = return_probabilities(vertex_adjacency(cx), steps=8)
    assert probs[0] == 1.0
    # bipartite-ish graphs give exact zeros at odd times; that is physics, not a bug
    assert all(0.0 <= p <= 1.0 for p in probs)
    assert probs[2] > 0.0
