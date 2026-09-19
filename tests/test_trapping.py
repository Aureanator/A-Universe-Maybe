"""P17 pins: probabilities always escape; amplitudes trap exactly on the dark subspace."""

import json
from pathlib import Path

import numpy as np
import pytest

from examples.trapping_test import (GAMMA, complete_graph, cycle_graph, dark_subspace, expm,
                                    laplacian, lead_control, orbits, path_graph, sierpinski)

ROOT = Path(__file__).resolve().parents[1]


def _walks(verts, edges, b, T):
    n = len(verts)
    L = laplacian(n, edges)
    PB = np.zeros((n, n)); PB[b, b] = 1
    Uq = expm(-1j * (L - 1j * GAMMA * PB) * T)
    Uc = expm(-(L + GAMMA * PB) * T)
    return L, (np.abs(Uq) ** 2).sum(axis=0), Uc.sum(axis=0)


@pytest.mark.parametrize("builder,arg,T", [(path_graph, 8, 4000.0), (cycle_graph, 10, 3000.0),
                                           (complete_graph, 6, 500.0), (sierpinski, 2, 2000.0)])
def test_classical_escapes_and_amplitude_limit_is_projection(builder, arg, T):
    verts, edges, gens, b = builder(arg)
    b = 0 if isinstance(b, str) else b
    L, sq, sc = _walks(verts, edges, b, T)
    assert sc.max() < 1e-12                               # T1
    D, _, _ = dark_subspace(L, [b])
    assert np.allclose(sq, (np.abs(D) ** 2).sum(axis=1), atol=1e-8)   # T3 per start
    assert abs(sq.mean() - D.shape[1] / len(verts)) < 1e-8


def test_exact_dark_dimensions():
    assert dark_subspace(laplacian(8, path_graph(8)[1]), [0])[0].shape[1] == 0
    assert dark_subspace(laplacian(10, cycle_graph(10)[1]), [0])[0].shape[1] == 4
    assert dark_subspace(laplacian(7, complete_graph(7)[1]), [0])[0].shape[1] == 5
    for k in range(1, 5):                                  # observed pattern, k = 1..6 archived
        verts, edges, gens, b = sierpinski(k)
        n = len(verts)
        d = dark_subspace(laplacian(n, edges), [b])[0].shape[1]
        assert d == n - (3 * 2 ** (k - 1) + 1)
        assert d >= n - orbits(n, gens)                    # T5


def test_explicit_lead_keeps_dark_state():
    r = lead_control(level=2, lead=800, t=150.0)
    assert abs(r["dark_state_region_norm"] - 1) < 1e-10
    assert r["bright_state_region_norm"] < 0.95


def test_broken_symmetry_has_no_exact_dark_state():
    verts, edges, _, b = sierpinski(3)
    w = 1000 + np.where(np.random.default_rng(7).uniform(-1, 1, len(edges)) > 0, 1, -1)
    assert dark_subspace(laplacian(len(verts), edges, w), [b])[0].shape[1] == 0


def test_archived_depth_rates():
    data = json.loads((ROOT / "reference/opus_session/data/trapping_depth_rates.json").read_text())
    slow = [float(data[str(k)]["rates"][0]) for k in range(1, 7)]
    assert all(r > 0 for r in slow)
    assert slow[5] < 1e-30 and slow[4] < 1e-15 and slow[3] < 1e-7
    for k in range(1, 7):
        rates = [float(x) for x in data[str(k)]["rates"]]
        assert abs(sum(rates) - GAMMA) < 1e-4             # trace identity: sum of rates = Gamma
        assert data[str(k)]["krylov_dim"] == 3 * 2 ** (k - 1) + 1
