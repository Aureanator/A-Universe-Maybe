"""P31: does a circulating structure work on the vacuum around it? (PREDICTIONS P31)

Spin-1/2 walker with a dynamic 2T quantum record on two loop edges. Compares the most circulating
state of a degenerate family with the least circulating state of the same family.
Reproduce: python examples/p31_selfbind.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

from constraintnet.current import cycle_transport, transport_current
from constraintnet.seeds import kuhn_ball
from constraintnet.spin_record import SpinRecordWalk

from p28_compact import loops
from p29_tail import coin_matrix

N, T_CLOSED, T_OPEN, EVERY = int(sys.argv[1]) if len(sys.argv) > 1 else 4, 400, 200, 5
LAM = (0.1, 0.1)
OUT = ROOT / f"reference/opus_session/data/p31_selfbind_n{N}.json"


def extreme_states(Q, cyc):
    """Most- and least-circulating walker states inside one degenerate family of the flat walk."""
    w = Q.walk
    n = len(w.arcs)
    flat = np.zeros((n, 2, 2), complex)
    flat[:] = np.eye(2)
    keep, w.mats = w.mats, flat                        # flat labels for the preparation
    U = w.matrix()
    C = coin_matrix(w, 2)
    w.mats = keep
    ev, V = np.linalg.eig(U)
    order = np.argsort(np.angle(ev))
    ev, V = ev[order], V[:, order]
    ang = np.angle(ev)
    steps = list(zip(cyc, cyc[1:] + cyc[:1]))
    fwd = [w.index[(a, b)] for a, b in steps]
    rev = [w.index[(b, a)] for a, b in steps]
    Msum = np.zeros((n * 2, n * 2), complex)
    Mdiff = np.zeros_like(Msum)
    for a in fwd + rev:
        P = C[2 * a:2 * a + 2, :]
        M = P.conj().T @ P
        Msum += M
        Mdiff += M if a in fwd else -M
    blocks, start = [], 0
    for i in range(1, len(ang) + 1):
        if i == len(ang) or abs(ang[i] - ang[start]) > 1e-8:
            blocks.append((start, i)); start = i
    best = None
    for (s0, s1) in blocks:
        if s1 - s0 < 2:
            continue
        Qb, _ = np.linalg.qr(V[:, s0:s1])
        A = Qb.conj().T @ Mdiff @ Qb
        B = Qb.conj().T @ Msum @ Qb
        A = (A + A.conj().T) / 2
        B = (B + B.conj().T) / 2
        bw, bv = np.linalg.eigh(B)
        if bw.max() < 1e-12:
            continue
        kp = bv[:, bw > 1e-10 * bw.max()]
        vals, vecs = np.linalg.eigh(np.linalg.solve(kp.conj().T @ B @ kp, kp.conj().T @ A @ kp))
        hi = abs(vals[-1])
        if best is None or hi > best[0]:
            plus = (Qb @ (kp @ vecs[:, -1])).reshape(n, 2)
            plus = plus / np.linalg.norm(plus)
            # the zero-current partner is the time-reversal-symmetric combination, not an
            # eigenvector of the ratio: inside a Kramers pair the extremes are +lambda and -lambda.
            eps = np.array([[0, 1], [-1, 0]], complex)
            kp_state = np.zeros_like(plus)
            kp_state[w.target] = np.einsum("ij,aj->ai", eps, plus.conj())
            zero = plus + kp_state
            if np.linalg.norm(zero) < 1e-8:
                zero = 1j * (plus - kp_state)
            best = (hi, plus, zero / np.linalg.norm(zero), float(ang[s0]), s1 - s0, 0.0)
    return best


def k_joint_check(Q, rng):
    """Antiunitary K: spinor reversal on the walker, conjugation + label inversion on the record."""
    w = Q.walk
    n = len(w.arcs)
    eps = np.array([[0, 1], [-1, 0]], complex)
    perm = Q.inv if Q.k == 1 else None
    idx = np.indices((Q.ng,) * Q.k).reshape(Q.k, -1)
    inv_conf = np.ravel_multi_index(tuple(Q.inv[idx[a]] for a in range(Q.k)), (Q.ng,) * Q.k)

    def K(Psi):
        out = np.zeros_like(Psi)
        out[w.target] = np.einsum("ij,acj->aci", eps, Psi.conj()[:, inv_conf, :])
        for ax, iab, iba in Q.qarcs:
            pass
        return out

    x = rng.normal(size=(n, Q.nc, 2)) + 1j * rng.normal(size=(n, Q.nc, 2))
    lhs = K(Q.step(x))
    rhs = x  # placeholder; the inverse step is applied below
    # inverse of the full tick: U^-1 = walk^-1 . rec^-1
    y = K(x)
    y = Q.apply_rec(y, inverse=True)
    cps = np.zeros_like(y)
    cps[Q.plain] = y[w.target[Q.plain]]
    for ax, iab, iba in Q.qarcs:
        cps[iab] = Q._transport(y[w.target[iab]], ax, False)
        cps[iba] = Q._transport(y[w.target[iba]], ax, True)
    ov = np.add.reduceat(w.phi[:, None, None] * cps, w.starts, axis=0)
    rhs = 2 * w.phi[:, None, None] * ov[w.vertex_of_arc] - cps
    return float(np.abs(lhs - rhs).max()), float(np.abs(K(K(x)) + x).max())


def observables(Q, Psi, cyc, E_vac):
    out, J = transport_current(Q.walk, Psi)
    ct = cycle_transport(Q.walk, out, cyc)
    p_arc = np.sum(np.abs(Psi) ** 2, axis=(1, 2))
    steps = list(zip(cyc, cyc[1:] + cyc[:1]))
    idx = [Q.walk.index[(a, b)] for a, b in steps] + [Q.walk.index[(b, a)] for a, b in steps]
    n = float(p_arc.sum())
    return {"norm": n, "bias": ct["bias"], "loop_weight": float(p_arc[idx].sum()),
            "E_rec": float(np.real(np.vdot(Psi, Q.apply_H(Psi)))) - E_vac * n,
            "P_vac": float(np.linalg.norm(np.tensordot(Psi, Q.vac.conj(), axes=(1, 0))) ** 2)}


def main():
    cx = kuhn_ball("A4", n=N)
    cyc = loops(cx)["axis_square_L4"]
    qedges = [tuple(sorted(e)) for e in zip(cyc[:2], cyc[1:3])]
    Q = SpinRecordWalk(cx, qedges, *LAM, mode="closed")
    Qo = SpinRecordWalk(cx, qedges, *LAM, mode="open")
    E_vac = float(np.real(Q.vac.conj() @ Q.apply_H(Q.vac[None, :, None])[0, :, 0]))
    bias0, plus, zero, phase, blockdim, zero_bias = extreme_states(Q, cyc)
    Ur = Q.rec_matrix()
    ksym, ksq = k_joint_check(Q, np.random.default_rng(0))
    res = {"lam": LAM, "record_states": Q.nc, "prep_bias": bias0, "prep_zero_bias": zero_bias,
           "prep_phase": phase, "prep_block_dim": blockdim,
           "rec_unitarity": float(np.abs(Ur.conj().T @ Ur - np.eye(Q.nc)).max()),
           "vac_stationarity": float(abs(abs(Q.vac.conj() @ Ur @ Q.vac) - 1)),
           "vac_overlap_flat": float(abs(Q.vac[0]) ** 2),
           "K_joint_symmetry_error": ksym, "K_joint_squared_plus_identity": ksq,
           "E_vac": E_vac, "arms": {}}
    open_index = [Qo.walk.index[a] for a in Q.walk.arcs]
    for name, psi, record in (("C+", plus, True), ("C0", zero, True),
                              ("Q+", plus, False), ("Q0", zero, False)):
        Psi = Q.product_state(psi)
        track = {"t": [], "bias": [], "E_rec": [], "P_vac": [], "loop_weight": [], "norm": []}
        for t in range(T_CLOSED + 1):
            if t % EVERY == 0:
                o = observables(Q, Psi, cyc, E_vac)
                track["t"].append(t)
                for k in ("bias", "E_rec", "P_vac", "loop_weight", "norm"):
                    track[k].append(o[k])
            if t < T_CLOSED:
                Psi = Q.step(Psi, record=record)
        # open release from the prepared state
        Po = np.zeros((len(Qo.walk.arcs), Qo.nc, 2), complex)
        Po[open_index] = Q.product_state(psi)
        gone = 0.0
        rel = {"t": [], "loop_weight": [], "bias": [], "norm": []}
        for t in range(T_OPEN + 1):
            if t % EVERY == 0:
                o = observables(Qo, Po, cyc, E_vac)
                rel["t"].append(t); rel["loop_weight"].append(o["loop_weight"])
                rel["bias"].append(o["bias"]); rel["norm"].append(o["norm"])
            if t < T_OPEN:
                Po = Qo.walk_step(Po)
                gone += float((np.abs(Qo.escaped) ** 2).sum())
                if record:
                    Po = Qo.apply_rec(Po)
        rel["bookkeeping_error"] = abs(rel["norm"][-1] + gone - 1)
        res["arms"][name] = {"closed": track, "release": rel}
        print(name, "bias0 %.4f -> %.4f" % (track["bias"][0], track["bias"][-1]),
              "E_rec %.5f -> %.5f" % (track["E_rec"][0], track["E_rec"][-1]),
              "P_vac %.4f" % track["P_vac"][-1],
              "release loop %.4f norm %.4f" % (rel["loop_weight"][-1], rel["norm"][-1]), flush=True)
        OUT.write_text(json.dumps(res) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
