"""P21: option A at small scale -- a quantum record in a lossless box (PREDICTIONS P21).

Geometries G1 (pivot vortex), G2 (DF cycle), G3 (free flash); arms C0, A(lE,lB), Q(lE,lB).
Coordinates prepare initial states only; measurements are relational (arcs, hop balls).
Reproduce: python examples/p21_quantum_record.py [G1 G2 G3]
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from constraintnet.seeds import kuhn_ball
from constraintnet.qrecord import QuantumRecordWalk

N, T, EVERY = 6, 600, 5
GRID = [(lE, lB) for lE in (0.05, 0.3, 1.0) for lB in (0.5, 2.0)]
OUT = ROOT / "reference/opus_session/data"


def three_fold_axis(Q):
    for i, x in enumerate(Q.els):
        if Q.g.order_of(x) == 3:
            ev, V = np.linalg.eig(Q.R[i])
            v = np.real(V[:, np.argmin(abs(ev - 1))])
            return v / np.linalg.norm(v)


def hop_ball(cx, centre, r):
    nb = {v: set() for v in cx.vertices()}
    for a, b in cx.edges():
        nb[a].add(b); nb[b].add(a)
    seen, front = {centre}, {centre}
    for _ in range(r):
        front = {u for v in front for u in nb[v]} - seen
        seen |= front
    return seen


def setup(geom):
    cx = kuhn_ball("A4", n=N)
    grid = {v: np.array(cx.vertex(v).metadata["grid"], float) for v in cx.vertices()}
    G = {tuple(int(x) for x in p): v for v, p in grid.items()}
    probe = QuantumRecordWalk(cx, [(G[(3, 3, 3)], G[(4, 3, 3)])], 0.0, 0.0)
    w = probe.walk
    axis = three_fold_axis(probe)
    nA = len(w.arcs)
    info = {}
    if geom == "G1":
        p0, sig, R = np.array([3.0, 3, 3]), 1.2, 1.2
        helper = np.array([1.0, 0, 0]) if abs(axis[0]) < 0.9 else np.array([0.0, 1, 0])
        u1 = np.cross(axis, helper); u1 /= np.linalg.norm(u1); u2 = np.cross(axis, u1)
        pol = (u1 + 1j * u2) / np.sqrt(2)
        amp = {}
        for v in w.interior:
            d = grid[v] - p0
            rho = np.hypot(d[0], d[1])
            amp[v] = np.exp(-(d @ d) / (2 * sig ** 2)) * ((rho - R) + 1j * d[2])
        psi = np.array([w.phi[i] * amp[a] for i, (a, b) in enumerate(w.arcs)])[:, None] * pol[None, :]
        psi /= np.linalg.norm(psi)
        # quantum edges: the 3 edges carrying the most initial walker weight (relational rule)
        wt = {}
        for i, (a, b) in enumerate(w.arcs):
            key = (min(a, b), max(a, b))
            wt[key] = wt.get(key, 0) + float((abs(psi[i]) ** 2).sum())
        qedges = sorted(wt, key=lambda e: (-round(wt[e], 12), e))[:3]
        centre = G[(3, 3, 3)]
        near = hop_ball(cx, centre, 1)
        mask = np.array([a in near for a, _ in w.arcs])
        info["near"] = "arcs leaving the hop-1 ball of the centre vertex"
    elif geom == "G2":
        cyc = [G[(2, 2, 3)], G[(3, 2, 3)], G[(3, 3, 3)], G[(2, 3, 3)]]
        psi = np.zeros((nA, 3), complex)
        mask = np.zeros(nA, bool)
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            psi[w.index[(a, b)]] = axis
            psi[w.index[(b, a)]] = -axis
            mask[w.index[(a, b)]] = mask[w.index[(b, a)]] = True
        psi /= np.linalg.norm(psi)
        qedges = [tuple(sorted(e)) for e in zip(cyc[:3], cyc[1:4])]
        info["near"] = "the 8 arcs of the DF cycle"
    else:
        p0, sig = np.array([2.0, 3, 3]), 1.0
        pol = np.array([1.0, 2.0, 3.0]); pol /= np.linalg.norm(pol)
        amp = {v: np.exp(-((grid[v] - p0) @ (grid[v] - p0)) / (2 * sig ** 2)) for v in w.interior}
        psi = np.array([w.phi[i] * amp[a] for i, (a, b) in enumerate(w.arcs)])[:, None] * pol[None, :]
        psi = psi.astype(complex) / np.linalg.norm(psi)
        tri = [G[(3, 3, 3)], G[(4, 3, 3)], G[(4, 4, 3)]]
        qedges = [tuple(sorted((tri[i], tri[j]))) for i, j in ((0, 1), (1, 2), (0, 2))]
        near = set(tri)
        mask = np.array([a in near for a, _ in w.arcs])
        info["near"] = "arcs leaving the quantum triangle's vertices"
    info["qedges_grid"] = [[list(map(int, grid[a])), list(map(int, grid[b]))] for a, b in qedges]
    return cx, psi, qedges, mask, info


def run(geom, lE, lB, record=True, c0_ref=None, df=None, reverse=False):
    cx, psi, qedges, mask, info = setup(geom)
    Q = QuantumRecordWalk(cx, qedges, lE, lB)
    Psi = Q.product_state(psi)
    Psi0 = Psi.copy()
    E_vac = float(np.real(Q.vac.conj() @ Q.apply_H(Q.vac[None, :, None])[0, :, 0]))
    E_inf = float(np.real((Q.lam_E * np.trace(Q.L8) * Q.k * 12 ** (Q.k - 1) + Q.lam_B * Q.W.sum()) / Q.nc)) - E_vac
    rec = {"geom": geom, "arm": ("A" if record else "Q") if lE > 0 else "C0", "lam_E": lE, "lam_B": lB,
           "vac_overlap_with_identity": float(abs(Q.vac[np.ravel_multi_index((Q.e_id,) * Q.k, (12,) * Q.k)]) ** 2),
           "E_rec_infinite_T": E_inf, "info": info, "t": [], "norm_dev": [], "P_vac": [], "E_rec": [],
           "near": [], "fid_C0": [], "df_overlap": [], "purity": {}}
    Ur = Q.rec_matrix()
    rec["vac_stationarity_err"] = float(abs(abs(Q.vac.conj() @ Ur @ Q.vac) - 1))
    walkers = []
    t0 = time.time()
    for t in range(1, T + 1):
        Psi = Q.step(Psi, record=record)
        if t % EVERY == 0:
            p2 = (np.abs(Psi) ** 2).sum(axis=(1, 2))
            rec["t"].append(t)
            rec["norm_dev"].append(float(p2.sum() - 1))
            rec["P_vac"].append(float(np.linalg.norm(np.tensordot(Psi, Q.vac.conj(), axes=(1, 0))) ** 2))
            rec["E_rec"].append(float(np.real(np.vdot(Psi, Q.apply_H(Psi)))) - E_vac)
            rec["near"].append(float(p2[mask].sum()))
            if c0_ref is not None:
                phi0 = c0_ref[len(rec["t"]) - 1]
                rec["fid_C0"].append(float((np.abs(np.tensordot(Psi, phi0.conj(), axes=([0, 2], [0, 1]))) ** 2).sum()))
            if df is not None:
                rec["df_overlap"].append(float((np.abs(np.tensordot(Psi, df.conj(), axes=([0, 2], [0, 1]))) ** 2).sum()))
            if lE == 0:
                walkers.append(Psi[:, np.ravel_multi_index((Q.e_id,) * Q.k, (12,) * Q.k)].copy())
        if t in (T // 2, T) and lE > 0:
            M = Psi.transpose(1, 0, 2).reshape(Q.nc, -1)
            rho = M @ M.conj().T
            rec["purity"][str(t)] = float(np.real(np.vdot(rho, rho)))
    rec["seconds"] = time.time() - t0
    if reverse:
        for t in range(T):
            Psi = Q.unstep(Psi, record=record)
        rec["reverse_err"] = float(np.abs(Psi - Psi0).max())
    n = len(rec["t"])
    rec["near_avg_second_half"] = float(np.mean(rec["near"][n // 2:]))
    rec["baseline_near_uniform"] = float(mask.sum() / len(mask))
    print(geom, rec["arm"], lE, lB, "near_avg", round(rec["near_avg_second_half"], 5),
          "1-Pvac(T)", round(1 - rec["P_vac"][-1], 5), "Erec(T)", round(rec["E_rec"][-1], 5),
          "Einf", round(E_inf, 3), "%.0fs" % rec["seconds"], flush=True)
    return rec, walkers, psi


def main(geoms):
    for geom in geoms:
        out = {"N": N, "T": T, "every": EVERY, "grid": GRID, "runs": []}
        c0, walkers, psi = run(geom, 0.0, 0.0)
        out["runs"].append(c0)
        ref = walkers if geom == "G3" else None
        df = psi if geom == "G2" else None
        if df is not None:
            c0, _, _ = run(geom, 0.0, 0.0, df=df)
            out["runs"][0] = c0
        for lE, lB in GRID:
            rev = (lE, lB) == (1.0, 2.0)
            out["runs"].append(run(geom, lE, lB, True, ref, df, reverse=rev)[0])
            out["runs"].append(run(geom, lE, lB, False, ref, df)[0])
            (OUT / f"p21_{geom}.json").write_text(json.dumps(out) + "\n", encoding="utf-8")
        (OUT / f"p21_{geom}.json").write_text(json.dumps(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:] or ["G1", "G2", "G3"])
