"""P29a (amended): stationary states with a tail -- where circulation is allowed (PREDICTIONS P29a).

Per-eigenvector currents are basis-dependent inside degenerate eigenspaces, so the current is
maximised over each eigenspace by a generalized eigenproblem. Also checks the antiunitary
K psi(w->v) = rho(A_wv) conj(psi(v->w)), which satisfies K U = U^-1 K and K^2 = +1.

Exact diagonalisation of the flat closed walk; per eigenstate we measure loop current, divergence,
localisation and where the current sits. Reproduce: python examples/p29_tail.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

from constraintnet.current import transport_current
from constraintnet.seeds import kuhn_ball, randomize_labels
from constraintnet.walk import ArcWalk, a4_irrep3

from p28_compact import loops, odd_cycle

N, DRAWS = 4, 10
OUT = ROOT / "reference/opus_session/data/p29a_tail_v2.json"


def loop_sets(cx):
    out = dict(loops(cx))
    five = odd_cycle(cx, 5)
    if five:
        out["found_L5"] = five
    return out


def hop_ball(cx, verts, r=1):
    nb = {v: set() for v in cx.vertices()}
    for a, b in cx.edges():
        nb[a].add(b); nb[b].add(a)
    seen = set(verts)
    front = set(verts)
    for _ in range(r):
        front = {u for v in front for u in nb[v]} - seen
        seen |= front
    return seen


def coin_matrix(w, dim):
    n = len(w.arcs)
    C = np.zeros((n * dim, n * dim))
    for k in range(n * dim):
        e = np.zeros((n, dim))
        e[k // dim, k % dim] = 1
        ov = np.add.reduceat(w.phi[:, None] * e, w.starts, axis=0)
        C[:, k] = (2 * w.phi[:, None] * ov[w.vertex_of_arc] - e).reshape(-1)
    return C


def k_symmetry_check(w, dim, rng):
    n = len(w.arcs)

    def K(psi):
        out = np.zeros_like(psi)
        out[w.target] = np.einsum("aij,aj->ai", w.mats, psi.conj())
        return out

    def unstep(psi):
        back = np.zeros_like(psi)
        back[w.kept] = np.einsum("aji,aj->ai", w.mats[w.kept], psi[w.target[w.kept]])
        ov = np.add.reduceat(w.phi[:, None] * back, w.starts, axis=0)
        return 2 * w.phi[:, None] * ov[w.vertex_of_arc] - back

    x = rng.normal(size=(n, dim)) + 1j * rng.normal(size=(n, dim))
    return (float(np.abs(K(w.step(x)) - unstep(K(x))).max()),
            float(np.abs(K(K(x)) - x).max()))


def analyse(seed, dim=3):
    cx = kuhn_ball("A4", n=N)
    if seed is not None:
        randomize_labels(cx, seed=seed)
    w = ArcWalk(cx, rep=a4_irrep3(cx.group), dim=3, mode="closed")
    n_arcs = len(w.arcs)
    U = w.matrix()
    C = coin_matrix(w, 3)
    ev, V = np.linalg.eig(U)
    order = np.argsort(np.angle(ev))
    ev, V = ev[order], V[:, order]
    ksym, ksq = k_symmetry_check(w, 3, np.random.default_rng(0))
    # orthonormal bases of the degenerate blocks
    ang = np.angle(ev)
    blocks, start = [], 0
    for i in range(1, len(ang) + 1):
        if i == len(ang) or abs(ang[i] - ang[start]) > 1e-8:
            blocks.append((start, i)); start = i
    L = loop_sets(cx)
    ball = {name: hop_ball(cx, cyc, 1) for name, cyc in L.items()}
    rows = {}
    max_div = 0.0
    for name, cyc in L.items():
        steps = list(zip(cyc, cyc[1:] + cyc[:1]))
        fwd = [w.index[(a, b)] for a, b in steps]
        rev = [w.index[(b, a)] for a, b in steps]
        idx = fwd + rev
        Msum = np.zeros((n_arcs * 3, n_arcs * 3), complex)
        Mdiff = np.zeros_like(Msum)
        for a in fwd + rev:
            P = C[3 * a:3 * a + 3, :]
            M = P.conj().T @ P
            Msum += M
            Mdiff += M if a in fwd else -M
        near_arcs = [i for i, (a, b) in enumerate(w.arcs) if a in ball[name]]
        best = {"bias": 0.0, "loop_weight": 0.0, "product": 0.0}
        best_bias = {"bias": 0.0, "loop_weight": 0.0, "loop_J_share": 0.0, "near_weight": 0.0}
        one_dim_max = 0.0
        for (s0, s1) in blocks:
            Q, _ = np.linalg.qr(V[:, s0:s1])
            A = Q.conj().T @ Mdiff @ Q
            B = Q.conj().T @ Msum @ Q
            A = (A + A.conj().T) / 2
            B = (B + B.conj().T) / 2
            bw = np.linalg.eigvalsh(B)
            if bw.max() < 1e-12:
                continue
            keep = np.linalg.eigh(B)[1][:, bw > 1e-10 * bw.max()]
            Ar = keep.conj().T @ A @ keep
            Br = keep.conj().T @ B @ keep
            evals, evecs = np.linalg.eigh(np.linalg.inv(Br) @ Ar if Br.shape[0] > 1 else Ar / Br[0, 0].real)
            for lam, vec in ((evals[-1], evecs[:, -1]), (evals[0], evecs[:, 0])):
                psi = (Q @ (keep @ vec)).reshape(n_arcs, 3)
                psi = psi / np.linalg.norm(psi)
                bias = float(np.real(np.vdot(psi.reshape(-1), Mdiff @ psi.reshape(-1))
                                     / np.vdot(psi.reshape(-1), Msum @ psi.reshape(-1))))
                out, J = transport_current(w, psi)
                max_div = max(max_div, float(np.abs(np.add.reduceat(J, w.starts)).max()))
                p_arc = np.sum(np.abs(psi) ** 2, axis=1)
                lw = float(p_arc[idx].sum())
                if s1 - s0 == 1:
                    one_dim_max = max(one_dim_max, abs(bias))
                if abs(bias) * lw > best["product"]:
                    best = {"bias": bias, "loop_weight": lw, "product": abs(bias) * lw,
                            "phase": float(ang[s0]), "block_dim": s1 - s0,
                            "near_weight": float(p_arc[near_arcs].sum())}
                if abs(bias) > abs(best_bias["bias"]):
                    edge_J = float(np.abs(np.array([out[a] for a in fwd]) - np.array([out[a] for a in rev])).sum())
                    all_J = float(np.abs(J).sum()) / 2
                    best_bias = {"bias": bias, "loop_weight": lw,
                                 "loop_J_share": edge_J / all_J if all_J > 1e-14 else 0.0,
                                 "near_weight": float(p_arc[near_arcs].sum()),
                                 "phase": float(ang[s0]), "block_dim": s1 - s0}
        rows[name] = {"best_bias": best_bias, "best_tradeoff": best,
                      "max_bias_in_1d_blocks": one_dim_max}
    return {"seed": seed, "dim": int(len(ev)), "n_blocks": len(blocks),
            "largest_block": max(b - a for a, b in blocks),
            "n_1d_blocks": sum(1 for a, b in blocks if b - a == 1),
            "K_symmetry_error": ksym, "K_squared_error": ksq,
            "max_divergence": max_div, "loops": rows}


def main():
    out = []
    for seed in [None] + list(range(1, DRAWS + 1)):
        r = analyse(seed)
        out.append(r)
        print("seed", seed, "blocks", r["n_blocks"], "1d", r["n_1d_blocks"], "max1d %.1e" %
              max(v["max_bias_in_1d_blocks"] for v in r["loops"].values()),
              {k: (round(v["best_bias"]["bias"], 3), round(v["best_bias"]["loop_weight"], 3),
                   round(v["best_tradeoff"]["product"], 4)) for k, v in r["loops"].items()}, flush=True)
        OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
