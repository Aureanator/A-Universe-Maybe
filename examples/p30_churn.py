"""P30: how much vacuum churn can stationary circulation stand? (PREDICTIONS P30)

Dilute label disorder p, both internal spaces (A4 3-dim irrep; 2T spinor lift). For tolerance
windows delta, maximise the loop current over sets of levels inside the window; delta ~ 1/lifetime.
Reproduce: python examples/p30_churn.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

from constraintnet.seeds import kuhn_ball
from constraintnet.walk import ArcWalk, a4_irrep3

from p28_compact import loops
from p29_tail import coin_matrix
from p29b_spin import binary_tetrahedral

N = 4
PS = [0.0, 0.003, 0.01, 0.03, 0.1, 0.3, 1.0]
DELTAS = [1e-10, 1e-6, 1e-4, 1e-3, 1e-2]
SEEDS = [1, 2, 3]
OUT = ROOT / "reference/opus_session/data/p30_churn.json"


def dilute_walk(cx, kind, p, seed):
    rng = np.random.default_rng(seed)
    if kind == "A4":
        g = cx.group
        rep = a4_irrep3(g)
        els = [x for x in g.elements if x != g.identity()]
        w = ArcWalk(cx, rep=None, dim=3, mode="closed")
        mats = np.zeros((len(w.arcs), 3, 3), complex)
        chosen = {}
        for i, (a, b) in enumerate(w.arcs):
            key = (min(a, b), max(a, b))
            if key not in chosen:
                chosen[key] = g.identity() if rng.random() >= p else els[rng.integers(len(els))]
            M = rep(chosen[key])
            mats[i] = M if a < b else M.T
    else:
        G = binary_tetrahedral()
        nonid = [M for M in G if np.abs(M - np.eye(2)).max() > 1e-12]
        w = ArcWalk(cx, rep=None, dim=2, mode="closed")
        mats = np.zeros((len(w.arcs), 2, 2), complex)
        chosen = {}
        for i, (a, b) in enumerate(w.arcs):
            key = (min(a, b), max(a, b))
            if key not in chosen:
                chosen[key] = np.eye(2, dtype=complex) if rng.random() >= p else nonid[rng.integers(len(nonid))]
            M = chosen[key]
            mats[i] = M if a < b else M.conj().T
    w.mats = mats
    return w, chosen


def curvature_stats(cx, chosen, kind):
    """Curvature density and mean Wilson cost of the drawn labels."""
    if kind != "A4":
        return None
    g = cx.group
    rep = a4_irrep3(g)
    curved, wsum, counted = 0, 0.0, 0
    faces = cx.faces()
    for f in faces:
        if any((min(u, v), max(u, v)) not in chosen
               for u, v in ((f[0], f[1]), (f[1], f[2]), (f[0], f[2]))):
            continue                                   # face outside the closed walk's edge set
        counted += 1
        h = g.identity()
        for u, v in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            key = (min(u, v), max(u, v))
            lab = chosen.get(key, g.identity())
            if (u, v) != key:
                lab = g.inverse(lab)
            h = g.multiply(lab, h)
        w_ = 1 - float(np.trace(rep(h)).real) / 3
        wsum += w_
        curved += int(h != g.identity())
    return {"curved_fraction": curved / counted, "mean_wilson": wsum / counted,
            "total_wilson": wsum, "faces": counted}


def max_bias_windows(w, dim, cyc):
    n_arcs = len(w.arcs)
    C = coin_matrix(w, dim)
    steps = list(zip(cyc, cyc[1:] + cyc[:1]))
    fwd = [w.index[(a, b)] for a, b in steps]
    rev = [w.index[(b, a)] for a, b in steps]
    Msum = np.zeros((n_arcs * dim, n_arcs * dim), complex)
    Mdiff = np.zeros_like(Msum)
    for a in fwd + rev:
        P = C[dim * a:dim * a + dim, :]
        M = P.conj().T @ P
        Msum += M
        Mdiff += M if a in fwd else -M
    U = w.matrix()
    ev, V = np.linalg.eig(U)
    order = np.argsort(np.angle(ev))
    ev, V = ev[order], V[:, order]
    ang = np.angle(ev)
    out = {}
    for delta in DELTAS:
        blocks, start = [], 0
        for i in range(1, len(ang) + 1):
            if i == len(ang) or abs(ang[i] - ang[start]) > delta:
                blocks.append((start, i)); start = i
        best = 0.0
        best_lw = 0.0
        for (s0, s1) in blocks:
            if s1 - s0 < 2:
                continue
            Q, _ = np.linalg.qr(V[:, s0:s1])
            A = Q.conj().T @ Mdiff @ Q
            B = Q.conj().T @ Msum @ Q
            A = (A + A.conj().T) / 2
            B = (B + B.conj().T) / 2
            bw, bv = np.linalg.eigh(B)
            if bw.max() < 1e-12:
                continue
            keep = bv[:, bw > 1e-10 * bw.max()]
            Ar = keep.conj().T @ A @ keep
            Br = keep.conj().T @ B @ keep
            evals, evecs = np.linalg.eigh(np.linalg.solve(Br, Ar) if Br.shape[0] > 1 else Ar / Br[0, 0].real)
            for lam, vec in ((evals[-1], evecs[:, -1]), (evals[0], evecs[:, 0])):
                if abs(lam) > best:
                    psi = (Q @ (keep @ vec)).reshape(n_arcs, dim)
                    psi /= np.linalg.norm(psi)
                    p_arc = np.sum(np.abs(psi) ** 2, axis=1)
                    best = float(abs(lam))
                    best_lw = float(p_arc[fwd + rev].sum())
        out[str(delta)] = {"max_bias": best, "loop_weight": best_lw,
                           "lifetime_ticks": (1.0 / delta)}
    return out, float(np.sort(np.abs(ang[np.abs(ang) > 1e-9]))[0])


def main():
    rows = []
    cx = kuhn_ball("A4", n=N)
    L = {k: v for k, v in loops(cx).items() if k in ("triangle_L3", "axis_square_L4")}
    for kind, dim in (("A4", 3), ("2T", 2)):
        for p in PS:
            for seed in SEEDS:
                w, chosen = dilute_walk(cx, kind, p, seed)
                stats = curvature_stats(cx, chosen, kind)
                row = {"kind": kind, "p": p, "seed": seed, "curvature": stats, "loops": {}}
                for name, cyc in L.items():
                    res, lowest = max_bias_windows(w, dim, cyc)
                    row["loops"][name] = res
                    row["lowest_positive_phase"] = lowest
                rows.append(row)
                OUT.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
            r = rows[-1]
            print(kind, "p", p, "curved %.3f" % (stats["curved_fraction"] if stats else -1),
                  {d: round(np.mean([x["loops"]["axis_square_L4"][d]["max_bias"]
                                     for x in rows if x["kind"] == kind and x["p"] == p]), 4)
                   for d in ("1e-10", "0.001")}, flush=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
