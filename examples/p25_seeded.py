"""P25: seed loop patterns in a compatible cooled bath and test persistence (PREDICTIONS P25).

Bath: Gibbs state of the record generator at the P24a n=7 energy fraction (0.14), unfolded couplings.
Compatible seeding: Psi = sum_c b_c |c> (x) |DF_c>, DF_c the compact loop state built with branch c's
transports and the fixed vector of its loop holonomy nearest the reference. Control: imprinted |b>(x)|DF_flat>.
Reproduce: python examples/p25_seeded.py <L6|L4|provenance>
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

from constraintnet.seeds import kuhn_ball
from constraintnet.qrecord import QuantumRecordWalk

N, T, EVERY, FRAC, LAM = 6, 600, 5, 0.14, (0.1, 0.1)
LOOPS = {"L6": [(2, 2, 3), (3, 2, 3), (3, 3, 3), (2, 3, 3)],
         "L4": [(2, 3, 4), (3, 4, 4), (3, 3, 3), (2, 2, 3)]}
XREF = np.array([1.0, 0.3, -0.5]) / np.linalg.norm([1.0, 0.3, -0.5])
OUT = ROOT / "reference/opus_session/data"


def rec_H(Q):
    H = Q.apply_H(np.eye(Q.nc, dtype=complex)[None])[0]
    return (H + H.conj().T) / 2


def gibbs_bath(Q, frac, seed):
    """Typical pure state of the Gibbs ensemble of the record generator at energy fraction frac."""
    H = rec_H(Q)
    ev, V = np.linalg.eigh(H)
    E_vac = float(np.real(Q.vac.conj() @ H @ Q.vac))
    E_inf = float(ev.mean())
    target = E_vac + frac * (E_inf - E_vac)

    def mean_E(beta):
        w = np.exp(-beta * (ev - ev[0])); w /= w.sum()
        return float(w @ ev) - target
    beta = brentq(mean_E, 1e-6, 1e4)
    p = np.exp(-beta * (ev - ev[0])); p /= p.sum()
    rng = np.random.default_rng(seed)
    b = V @ (np.sqrt(p) * np.exp(2j * np.pi * rng.random(len(p))))
    return b / np.linalg.norm(b), {"beta": beta, "E_vac": E_vac, "E_inf": E_inf, "target": target,
                                   "E_sample": float(np.real(np.vdot(b, H @ b)))}


def setup(loop):
    cx = kuhn_ball("A4", n=N)
    G = {tuple(cx.vertex(v).metadata["grid"]): v for v in cx.vertices()}
    cyc = [G[p] for p in LOOPS[loop]]
    qedges = [tuple(sorted(e)) for e in zip(cyc[:3], cyc[1:4])]
    return cx, cyc, qedges


def df_branches(Q, cyc):
    """DF_c for every record branch c: array (n_arcs, nc, 3), plus loop-arc mask."""
    w = Q.walk
    labs = np.indices((12,) * Q.k).reshape(Q.k, -1)                   # (k, nc)
    qpos = {e: ax for ax, e in enumerate(Q.qedges)}
    steps = list(zip(cyc, cyc[1:] + cyc[:1]))
    # transport matrix for each step a->b per branch: rho(label(b,a)); label(a,b)=g for a<b
    mats = []
    for a, b in steps:
        key = (min(a, b), max(a, b))
        if key in qpos:
            g = labs[qpos[key]]
            R = Q.R[g]                                                  # rho(g) = rho(label(lo,hi))
            # label(b,a): if a<b it is label(b,a)=g^-1 -> R^T ; if a>b it is label(b,a)=label(lo,hi)=g -> R
            mats.append(np.transpose(R, (0, 2, 1)) if a < b else R)
        else:
            mats.append(np.broadcast_to(np.eye(3), (Q.nc, 3, 3)))
    hol = np.broadcast_to(np.eye(3), (Q.nc, 3, 3)).copy()
    for M in mats:
        hol = np.einsum("cij,cjk->cik", M, hol)
    x0 = np.zeros((Q.nc, 3))
    for c in range(Q.nc):
        evs, V = np.linalg.eig(hol[c])
        fixed = np.abs(evs - 1) < 1e-9
        B = np.real(V[:, fixed])
        B, _ = np.linalg.qr(B)
        x = B @ (B.T @ XREF)
        if np.linalg.norm(x) < 1e-9:
            x = B[:, 0]
        x0[c] = x / np.linalg.norm(x)
    psi = np.zeros((len(w.arcs), Q.nc, 3), complex)
    mask = np.zeros(len(w.arcs), bool)
    x = x0.copy()
    for (a, b), M in zip(steps, mats):
        psi[w.index[(a, b)]] = x
        y = -np.einsum("cij,cj->ci", M, x)
        psi[w.index[(b, a)]] = y
        mask[w.index[(a, b)]] = mask[w.index[(b, a)]] = True
        x = np.einsum("cij,cj->ci", M, x)
    psi /= np.sqrt(8.0)
    return psi, mask


def residual_check(cx, cyc, qedges, DFc):
    Q0 = QuantumRecordWalk(cx, qedges, 0.0, 0.0, mode="open")
    return float(np.abs(Q0.walk_step(DFc) - DFc).max())


def run(Q, Psi, mask, record=True):
    rec = {"t": [], "loop": [], "N": []}
    gone = 0.0
    for t in range(1, T + 1):
        Psi = Q.walk_step(Psi)
        gone += float((np.abs(Q.escaped) ** 2).sum())
        if record:
            Psi = Q.apply_rec(Psi)
        if t % EVERY == 0:
            p2 = (np.abs(Psi) ** 2).sum(axis=(1, 2))
            rec["t"].append(t); rec["loop"].append(float(p2[mask].sum())); rec["N"].append(float(p2.sum()))
    rec["bookkeeping_err"] = abs(rec["N"][-1] + gone - 1)
    return rec


def main_loop(loop):
    cx, cyc, qedges = setup(loop)
    Q = QuantumRecordWalk(cx, qedges, *LAM, mode="open")
    DFc, mask = df_branches(Q, cyc)
    res = residual_check(cx, cyc, qedges, DFc)
    i0 = np.ravel_multi_index((Q.e_id,) * Q.k, (12,) * Q.k)
    DFflat = DFc[:, i0, :]
    out = {"loop": loop, "T": T, "frac": FRAC, "lam": LAM, "DF_branch_residual": res, "runs": []}
    print(loop, "DF_c residual", res, flush=True)

    def go(arm, Psi, record=True, extra=None):
        t0 = time.time()
        nrm = float(np.linalg.norm(Psi))
        r = run(Q, Psi / nrm, mask, record)
        r.update({"arm": arm, "norm_before_normalising": nrm, **(extra or {})})
        out["runs"].append(r)
        print(loop, arm, extra, "loop@50 %.5f loop@T %.5f N@T %.5f" % (r["loop"][9], r["loop"][-1], r["N"][-1]),
              "%.0fs" % (time.time() - t0), flush=True)
        (OUT / f"p25_{loop}.json").write_text(json.dumps(out) + "\n", encoding="utf-8")

    go("V", DFflat[:, None, :] * Q.vac[None, :, None])
    for seed in (1, 2, 3):
        b, info = gibbs_bath(Q, FRAC, seed)
        go("C", DFc * b[None, :, None], True, {"seed": seed, **info})
        go("I", DFflat[:, None, :] * b[None, :, None], True, {"seed": seed, **info})
        if seed == 1:
            go("Qc", DFc * b[None, :, None], False, {"seed": seed, **info})


def provenance():
    """P25-2: one flash of lowest-band light at n=7 on Gibbs bath samples at FRAC."""
    import p23_radiative as P
    Q, psi, loop, _ = P.setup(*LAM, 1.2, n=7)
    psi, w0 = P.lowest_band_filter(Q, psi)
    E_vac = P.rec_energy(Q, Q.vac)
    rows = []
    for seed in (1, 2):
        b, info = gibbs_bath(Q, FRAC, seed)
        E0 = P.rec_energy(Q, b) - E_vac
        _, ep = P.episode(Q, psi, b, np.random.default_rng(0))
        rows.append({"seed": seed, "w0": w0, "E0": E0, "dE": ep["exp_E"] - E_vac - E0, **info})
        print(rows[-1], flush=True)
        (OUT / "p25_provenance.json").write_text(json.dumps(rows) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "provenance":
        provenance()
    else:
        main_loop(sys.argv[1])
