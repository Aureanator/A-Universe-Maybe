"""Design checks for the v4 dynamics (docs/DYNAMICS_DESIGN.md, section 4).

A gauge-covariant weighted reflection (Szegedy) walk on the periodic Kuhn
lattice: amplitudes on directed edges (arcs) x internal space of a
representation rho of G. Checks are exact or spectral; nothing here is a
physics claim beyond the stated identities. Reproduce:
python examples/v4_design_checks.py
"""

import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

STAR = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)]
STAR = STAR + [tuple(-x for x in s) for s in STAR]
RING = {s: (4 if sorted(map(abs, s)) == [0, 1, 1] else 6) for s in STAR}   # face diagonals ring 4


def torus(n):
    verts = list(itertools.product(range(n), repeat=3))
    idx = {v: i for i, v in enumerate(verts)}
    arcs = []
    for v in verts:
        for d in STAR:
            w = tuple((a + b) % n for a, b in zip(v, d))
            arcs.append((idx[v], idx[w], d))
    return verts, idx, arcs


def a4_irrep3():
    from constraintnet.groups import AlternatingGroup4
    g = AlternatingGroup4()
    Q = np.linalg.qr(np.vstack([np.ones(4), np.eye(4)[:3]]).T)[0][:, 1:]   # basis of sum-zero space
    def rep(p):
        P = np.zeros((4, 4))
        for i, j in enumerate(p):
            P[j, i] = 1
        return Q.T @ P @ Q
    return g, rep


def walk(n, labels=None, rep=None, dim=1, ring_weights=(1.0, 0.5)):
    """Unitary U = S_rho * C on arcs x C^dim. labels: dict (v,w)->group element (g_vw)."""
    verts, idx, arcs = torus(n)
    A = len(arcs)
    arc_id = {(a, b, d): i for i, (a, b, d) in enumerate(arcs)}
    w6, w4 = ring_weights
    wt = np.array([w6 if RING[d] == 6 else w4 for (_, _, d) in arcs])
    N = A * dim
    C = np.zeros((N, N))
    by_vertex = {}
    for i, (a, b, d) in enumerate(arcs):
        by_vertex.setdefault(a, []).append(i)
    for v, ids in by_vertex.items():
        psi = np.sqrt(wt[ids] / wt[ids].sum())
        R = 2 * np.outer(psi, psi) - np.eye(len(ids))
        for x in range(dim):
            sl = [i * dim + x for i in ids]
            C[np.ix_(sl, sl)] = R
    S = np.zeros((N, N))
    for i, (a, b, d) in enumerate(arcs):
        j = arc_id[(b, a, tuple(-x for x in d))]
        M = np.eye(dim) if labels is None else rep(labels[(b, a)])   # transport by g_wv = g_vw^-1
        S[j * dim:(j + 1) * dim, i * dim:(i + 1) * dim] = M
    return S @ C, verts, arcs, wt


def checks(n=4):
    out = {}
    U, verts, arcs, wt = walk(n)
    V, A = len(verts), len(arcs)
    out["unitary_trivial"] = float(np.abs(U @ U.T - np.eye(A)).max())
    ev = np.linalg.eigvals(U)
    # classical walk P_vw = w/W; spectrum via momentum space (vertex-transitive torus)
    W = sum(6 * [1.0] + 0 * [0]) if False else None
    ks = [2 * np.pi * np.array(k) / n for k in itertools.product(range(n), repeat=3)]
    wsum = sum((1.0 if RING[d] == 6 else 0.5) for d in STAR)
    lam = np.array([sum((1.0 if RING[d] == 6 else 0.5) * np.cos(k @ np.array(d)) for d in STAR) / wsum
                    for k in ks])
    theta = np.arccos(np.clip(lam, -1, 1))
    predicted = np.concatenate([np.exp(1j * theta), np.exp(-1j * theta)])
    # remove predicted from spectrum (multiset match) -> remainder must be +-1
    ev_left = list(ev)
    worst = 0.0
    for p in predicted:
        j = int(np.argmin(np.abs(np.array(ev_left) - p)))
        worst = max(worst, abs(ev_left[j] - p))
        ev_left.pop(j)
    ev_left = np.array(ev_left)
    out["szegedy_max_mismatch"] = float(worst)
    out["remainder_count"] = int(len(ev_left))
    out["remainder_all_pm1"] = bool(np.all(np.minimum(np.abs(ev_left - 1), np.abs(ev_left + 1)) < 1e-8))
    out["remainder_expected_arcs_minus_2V"] = A - 2 * V
    out["lambda_min_over_torus"] = float(lam.min())
    # continuum BZ scan for lambda = -1 (doubler) and lambda = 1 away from k = 0
    g1 = np.linspace(-np.pi, np.pi, 61)
    K = np.stack(np.meshgrid(g1, g1, g1, indexing="ij"), -1).reshape(-1, 3)
    L = sum((1.0 if RING[d] == 6 else 0.5) * np.cos(K @ np.array(d)) for d in STAR) / wsum
    out["BZ_lambda_min"] = float(L.min())
    far = np.linalg.norm(K, axis=1) > 0.5
    out["BZ_max_lambda_away_from_0"] = float(L[far].max())
    # gauge-covariant version with random A4 labels in the 3-dim irrep
    g, rep = a4_irrep3()
    rng = np.random.default_rng(3)
    els = list(g.elements)
    labels = {}
    for (a, b, d) in arcs:
        if (a, b) not in labels:
            h = els[rng.integers(len(els))]
            labels[(a, b)] = h; labels[(b, a)] = g.inverse(h)
    U3, *_ = walk(n, labels, rep, 3)
    out["unitary_A4_irrep3"] = float(np.abs(U3 @ U3.T - np.eye(len(U3))).max())
    lam_g = {v: els[rng.integers(len(els))] for v in range(V)}
    labels2 = {(a, b): g.multiply(g.multiply(g.inverse(lam_g[a]), h), lam_g[b]) for (a, b), h in labels.items()}
    U3g, *_ = walk(n, labels2, rep, 3)
    e1 = np.sort_complex(np.round(np.linalg.eigvals(U3), 9))
    e2 = np.sort_complex(np.round(np.linalg.eigvals(U3g), 9))
    out["gauge_spectrum_max_diff"] = float(np.abs(e1 - e2).max())
    return out


if __name__ == "__main__":
    res = checks()
    print(json.dumps(res, indent=1))
    (ROOT / "reference/opus_session/data/v4_design_checks.json").write_text(json.dumps(res, indent=1) + "\n")
