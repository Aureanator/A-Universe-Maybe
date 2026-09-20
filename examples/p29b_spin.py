"""P29b: does the spin-1/2 lift restore circulation? (PREDICTIONS P29b)

Same walk, but the internal space is the 2-dim spinor representation of the binary tetrahedral
group 2T (the double cover of A4). Checks Kramers degeneracy and the maximum stationary loop
current per eigenspace, against P29a's A4 3-dim irrep result.
Reproduce: python examples/p29b_spin.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

from constraintnet.current import transport_current
from constraintnet.seeds import kuhn_ball
from constraintnet.walk import ArcWalk

from p28_compact import loops, odd_cycle
from p29_tail import coin_matrix, hop_ball

N, DRAWS = 4, 10
OUT = ROOT / "reference/opus_session/data/p29b_spin.json"
EPS = np.array([[0, 1], [-1, 0]], complex)            # i * sigma_y


def binary_tetrahedral():
    """The 24 unit quaternions of 2T, as SU(2) matrices."""
    qs = []
    for i in range(4):
        for s in (1, -1):
            q = np.zeros(4); q[i] = s
            qs.append(q)
    for signs in np.ndindex(2, 2, 2, 2):
        qs.append(np.array([(-1) ** s for s in signs], float) / 2)
    out = []
    for w_, x, y, z in qs:
        out.append(np.array([[w_ + 1j * z, y + 1j * x], [-y + 1j * x, w_ - 1j * z]], complex))
    return out


def spin_walk(cx, seed):
    """ArcWalk structure with 2-dim spinor labels; reverse arcs carry the adjoint."""
    w = ArcWalk(cx, rep=None, dim=2, mode="closed")
    G = binary_tetrahedral()
    rng = np.random.default_rng(seed) if seed is not None else None
    mats = np.zeros((len(w.arcs), 2, 2), complex)
    assigned = {}
    for i, (a, b) in enumerate(w.arcs):
        key = (min(a, b), max(a, b))
        if key not in assigned:
            assigned[key] = np.eye(2, dtype=complex) if rng is None else G[rng.integers(len(G))]
        M = assigned[key]
        # arc a->b transports by rho(A_ba); fix rho(A_ba) = M for a<b and its adjoint otherwise
        mats[i] = M if a < b else M.conj().T
    w.mats = mats
    return w


def k_check(w, rng):
    n = len(w.arcs)

    def K(psi):
        out = np.zeros_like(psi)
        out[w.target] = np.einsum("aij,jk,ak->ai", w.mats, EPS, psi.conj())
        return out

    def unstep(psi):
        back = np.zeros_like(psi)
        back[w.kept] = np.einsum("aji,aj->ai", w.mats[w.kept].conj(), psi[w.target[w.kept]])
        ov = np.add.reduceat(w.phi[:, None] * back, w.starts, axis=0)
        return 2 * w.phi[:, None] * ov[w.vertex_of_arc] - back

    x = rng.normal(size=(n, 2)) + 1j * rng.normal(size=(n, 2))
    return (float(np.abs(K(w.step(x)) - unstep(K(x))).max()),
            float(np.abs(K(K(x)) + x).max()))


def analyse(seed):
    cx = kuhn_ball("A4", n=N)
    w = spin_walk(cx, seed)
    n_arcs = len(w.arcs)
    U = w.matrix()
    unitarity = float(np.abs(U.conj().T @ U - np.eye(U.shape[0])).max())
    ksym, ksq = k_check(w, np.random.default_rng(0))
    C = coin_matrix(w, 2)
    ev, V = np.linalg.eig(U)
    order = np.argsort(np.angle(ev))
    ev, V = ev[order], V[:, order]
    ang = np.angle(ev)
    blocks, start = [], 0
    for i in range(1, len(ang) + 1):
        if i == len(ang) or abs(ang[i] - ang[start]) > 1e-8:
            blocks.append((start, i)); start = i
    L = dict(loops(cx))
    five = odd_cycle(cx, 5)
    if five:
        L["found_L5"] = five
    ball = {name: hop_ball(cx, cyc, 1) for name, cyc in L.items()}
    rows = {}
    for name, cyc in L.items():
        steps = list(zip(cyc, cyc[1:] + cyc[:1]))
        fwd = [w.index[(a, b)] for a, b in steps]
        rev = [w.index[(b, a)] for a, b in steps]
        idx = fwd + rev
        Msum = np.zeros((n_arcs * 2, n_arcs * 2), complex)
        Mdiff = np.zeros_like(Msum)
        for a in idx:
            P = C[2 * a:2 * a + 2, :]
            M = P.conj().T @ P
            Msum += M
            Mdiff += M if a in fwd else -M
        near_arcs = [i for i, (a, b) in enumerate(w.arcs) if a in ball[name]]
        best_bias = {"bias": 0.0, "loop_weight": 0.0, "loop_J_share": 0.0, "phase": 0.0, "block_dim": 0}
        best = {"product": 0.0, "bias": 0.0, "loop_weight": 0.0}
        for (s0, s1) in blocks:
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
                psi = (Q @ (keep @ vec)).reshape(n_arcs, 2)
                psi = psi / np.linalg.norm(psi)
                flat = psi.reshape(-1)
                bias = float(np.real(np.vdot(flat, Mdiff @ flat) / np.vdot(flat, Msum @ flat)))
                p_arc = np.sum(np.abs(psi) ** 2, axis=1)
                lw = float(p_arc[idx].sum())
                if abs(bias) * lw > best["product"]:
                    best = {"product": abs(bias) * lw, "bias": bias, "loop_weight": lw,
                            "phase": float(ang[s0]), "block_dim": s1 - s0,
                            "near_weight": float(p_arc[near_arcs].sum())}
                if abs(bias) > abs(best_bias["bias"]):
                    out, J = transport_current(w, psi)
                    edge_J = float(np.abs(np.array([out[a] for a in fwd]) - np.array([out[a] for a in rev])).sum())
                    all_J = float(np.abs(J).sum()) / 2
                    best_bias = {"bias": bias, "loop_weight": lw,
                                 "loop_J_share": edge_J / all_J if all_J > 1e-14 else 0.0,
                                 "near_weight": float(p_arc[near_arcs].sum()),
                                 "phase": float(ang[s0]), "block_dim": s1 - s0,
                                 "divergence": float(np.abs(np.add.reduceat(J, w.starts)).max())}
        rows[name] = {"best_bias": best_bias, "best_tradeoff": best}
    return {"seed": seed, "dim": int(len(ev)), "unitarity_error": unitarity,
            "K_symmetry_error": ksym, "K_squared_plus_identity_error": ksq,
            "n_blocks": len(blocks), "n_odd_blocks": sum(1 for a, b in blocks if (b - a) % 2),
            "n_1d_blocks": sum(1 for a, b in blocks if b - a == 1),
            "min_block_dim": min(b - a for a, b in blocks), "loops": rows}


def main():
    out = []
    for seed in [None] + list(range(1, DRAWS + 1)):
        r = analyse(seed)
        out.append(r)
        print("seed", seed, "dim", r["dim"], "blocks", r["n_blocks"], "min block", r["min_block_dim"],
              "odd blocks", r["n_odd_blocks"], "K^2+1 %.1e" % r["K_squared_plus_identity_error"],
              {k: (round(v["best_bias"]["bias"], 3), round(v["best_bias"]["loop_weight"], 3))
               for k, v in r["loops"].items()}, flush=True)
        OUT.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
