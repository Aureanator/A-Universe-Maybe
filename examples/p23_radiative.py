"""P23: radiative cooling -- can a flood of light calm a hot record? (PREDICTIONS P23)

Sequential flashes through an open box; each flash's escaped light is 'detected' (quantum-trajectory
unravelling of the exact record channel, weighted reservoir sampling of the detection event), which
leaves the record in a conditional pure state for the next flash. Exact per-flash expectations of the
record's vacuum population and energy are bookkept alongside.
Reproduce: python examples/p23_radiative.py <arm> <trajectory-seed>
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
from constraintnet.walk import ArcWalk, a4_irrep3

N, K, L, HOT_SEED = 5, 20, 80, 22
ARMS = {"cold03": (0.3, 2.0, 1.2), "hot03": (0.3, 2.0, 0.5), "cold10": (1.0, 2.0, 1.2),
        "coldU": (0.1, 0.1, 1.2), "hotU": (0.1, 0.1, 0.5)}
OUT = ROOT / "reference/opus_session/data"


def setup(lE, lB, sigma, n=None):
    n = N if n is None else n
    c = n // 2
    cx = kuhn_ball("A4", n=n)
    grid = {v: np.array(cx.vertex(v).metadata["grid"], float) for v in cx.vertices()}
    G = {tuple(int(x) for x in p): v for v, p in grid.items()}
    cyc = [G[(c, c, c)], G[(c + 1, c, c)], G[(c + 1, c + 1, c)], G[(c, c + 1, c)]]
    qedges = [tuple(sorted(e)) for e in zip(cyc[:3], cyc[1:4])]
    Q = QuantumRecordWalk(cx, qedges, lE, lB, mode="open")
    w = Q.walk
    loop = np.zeros(len(w.arcs), bool)
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
        loop[w.index[(a, b)]] = loop[w.index[(b, a)]] = True
    p0 = np.array([c + 0.5, c + 0.5, float(c)])
    pol = np.array([1.0, 2.0, 3.0]); pol /= np.linalg.norm(pol)
    amp = {v: np.exp(-((grid[v] - p0) @ (grid[v] - p0)) / (2 * sigma ** 2)) for v in w.interior}
    psi = np.array([w.phi[i] * amp[a] for i, (a, b) in enumerate(w.arcs)])[:, None] * pol[None, :]
    psi = psi.astype(complex) / np.linalg.norm(psi)
    # flash 'temperature': <cos omega> on the flat closed-box walk (1 = all long-wave, cold)
    wc = ArcWalk(cx, rep=a4_irrep3(cx.group), dim=3, mode="closed")
    pc = np.zeros((len(wc.arcs), 3), complex)
    for i, a in enumerate(w.arcs):
        j = wc.index.get(a)
        if j is not None:
            pc[j] = psi[i]
    pc /= np.linalg.norm(pc)
    cos_omega = float(np.real(np.vdot(pc, wc.step(pc))))
    return Q, psi, loop, cos_omega


def hot_state(Q):
    rng = np.random.default_rng(HOT_SEED)
    h = rng.normal(size=Q.nc) + 1j * rng.normal(size=Q.nc)
    h -= Q.vac * (Q.vac.conj() @ h)
    return h / np.linalg.norm(h)


def rec_energy(Q, r):
    return float(np.real(np.vdot(r, Q.apply_H(r[None, :, None])[0, :, 0])))


def episode(Q, psi, r, rng):
    """One flash. Returns the sampled conditional record state and exact expectations."""
    vacc = Q.vac.conj()
    Psi = psi[:, None, :] * r[None, :, None]
    total, chosen = 0.0, None
    exp_pvac, exp_E = 0.0, 0.0
    for t in range(L):
        Psi = Q.walk_step(Psi)
        E = Q.escaped                                            # (nlost, nc, 3)
        w = (np.abs(E) ** 2).sum(axis=1)                          # (nlost, 3)
        W = float(w.sum())
        exp_pvac += float((np.abs(np.tensordot(E, vacc, axes=(1, 0))) ** 2).sum())
        exp_E += float(np.real(np.vdot(E, Q.apply_H(E))))
        if chosen is not None:
            chosen = Q.apply_rec(chosen[None, :, None])[0, :, 0]
        if W > 0:
            total += W
            if rng.random() < W / total:
                k = rng.choice(w.size, p=(w / W).ravel())
                a, i = divmod(k, 3)
                chosen = E[a, :, i] / np.sqrt(w[a, i])
                chosen = Q.apply_rec(chosen[None, :, None])[0, :, 0]
        Psi = Q.apply_rec(Psi)
    # light still inside at the cut: detected in place (same sampling rule)
    w = (np.abs(Psi) ** 2).sum(axis=1)
    Nin = float(w.sum())
    exp_pvac += float((np.abs(np.tensordot(Psi, vacc, axes=(1, 0))) ** 2).sum())
    exp_E += float(np.real(np.vdot(Psi, Q.apply_H(Psi))))
    total += Nin
    if rng.random() < Nin / total:
        k = rng.choice(w.size, p=(w / Nin).ravel())
        a, i = divmod(k, 3)
        chosen = Psi[a, :, i] / np.sqrt(w[a, i])
    return chosen, {"exp_pvac": exp_pvac, "exp_E": exp_E, "N_cut": Nin, "sum": total}


def trajectory(arm, seed):
    lE, lB, sigma = ARMS[arm]
    Q, psi, loop, cos_omega = setup(lE, lB, sigma)
    E_vac = rec_energy(Q, Q.vac)
    Wd = Q.lam_E * np.trace(Q.L8) * Q.k * 12 ** (Q.k - 1) + Q.lam_B * Q.W.sum()
    rec = {"arm": arm, "seed": seed, "lam_E": lE, "lam_B": lB, "sigma": sigma, "flash_cos_omega": cos_omega,
           "E_inf": float(Wd / Q.nc) - E_vac, "pvac": [], "E": [], "exp_pvac": [], "exp_E": [], "N_cut": [], "sum_err": []}
    r = hot_state(Q)
    rng = np.random.default_rng(1000 + seed)
    rec["pvac"].append(float(abs(Q.vac.conj() @ r) ** 2)); rec["E"].append(rec_energy(Q, r) - E_vac)
    t0 = time.time()
    for k in range(K):
        r, info = episode(Q, psi, r, rng)
        rec["pvac"].append(float(abs(Q.vac.conj() @ r) ** 2)); rec["E"].append(rec_energy(Q, r) - E_vac)
        rec["exp_pvac"].append(info["exp_pvac"]); rec["exp_E"].append(info["exp_E"] - E_vac)
        rec["N_cut"].append(info["N_cut"]); rec["sum_err"].append(abs(info["sum"] - 1))
        if k % 5 == 4:
            print(arm, seed, "flash", k + 1, "E %.3f" % rec["E"][-1], "pvac %.2e" % rec["pvac"][-1],
                  "N_cut %.2e" % info["N_cut"], "%.0fs" % (time.time() - t0), flush=True)
            (OUT / f"p23_{arm}_{seed}.json").write_text(json.dumps(rec) + "\n", encoding="utf-8")
    (OUT / f"p23_{arm}_{seed}.json").write_text(json.dumps(rec) + "\n", encoding="utf-8")


def positive_frequency(Q, psi, lo=1e-6, hi=0.55):
    """Project the flash onto flat closed-box eigenmodes with eigenphase in (lo, hi]; lo = 1e-6
    excludes the exact-zero flat band that round-off otherwise splits to tiny positive phases."""
    cx = Q.cx
    wc = ArcWalk(cx, rep=a4_irrep3(cx.group), dim=3, mode="closed")
    idx = [Q.walk.index[a] for a in wc.arcs]
    pc = psi[idx].reshape(-1)
    U = wc.matrix()
    ev, V = np.linalg.eig(U)
    ph = np.angle(ev)
    sel = (ph > lo) & (ph <= hi)
    Vs, _ = np.linalg.qr(V[:, sel])
    pc = Vs @ (Vs.conj().T @ pc)
    out = np.zeros_like(psi)
    out[idx] = pc.reshape(-1, 3)
    return out / np.linalg.norm(out), int(sel.sum())


def lowest_band_filter(Q, psi, width=60.0, span=240):
    """Spectral filter onto the lowest positive band of the flat closed-box walk:
    psi_f = sum_t exp(-t^2/2w^2) exp(-i w0 t) U^t psi, with w0 the lowest non-zero walk phase."""
    cx = Q.cx
    wc = ArcWalk(cx, rep=a4_irrep3(cx.group), dim=3, mode="closed")
    lam = np.linalg.eigvalsh(wc.discriminant())
    ph = np.arccos(np.clip(lam, -1, 1))
    w0 = float(np.sort(ph[ph > 1e-6])[0])
    idx = [Q.walk.index[a] for a in wc.arcs]
    p0 = psi[idx]
    acc = np.zeros_like(p0)
    fwd, bwd = p0.copy(), p0.copy()
    Uinv = lambda x: _unstep_closed(wc, x)
    acc += fwd
    for t in range(1, span + 1):
        fwd = wc.step(fwd); bwd = Uinv(bwd)
        g = np.exp(-t * t / (2 * width ** 2))
        acc += g * (np.exp(-1j * w0 * t) * fwd + np.exp(1j * w0 * t) * bwd)
    out = np.zeros_like(psi)
    out[idx] = acc
    return out / np.linalg.norm(out), w0


def _unstep_closed(wc, psi):
    back = np.zeros_like(psi)
    back[wc.kept] = np.einsum("aji,aj->ai", wc.mats[wc.kept], psi[wc.target[wc.kept]])
    ov = np.add.reduceat(wc.phi[:, None] * back, wc.starts, axis=0)
    return 2 * wc.phi[:, None] * ov[wc.vertex_of_arc] - back


def ladder_redshift(n, lE=0.1, lB=0.1):
    """P24a: equilibrium of the record under lowest-band light in boxes of growing size."""
    out = []
    Q, psi, loop, _ = setup(lE, lB, 1.2, n=n)
    psi, w0 = lowest_band_filter(Q, psi)
    E_vac = rec_energy(Q, Q.vac)
    hot = hot_state(Q)
    for th in np.linspace(0, np.pi / 2, 7):
        r = np.cos(th) * Q.vac + np.sin(th) * hot
        E0, p0 = rec_energy(Q, r) - E_vac, float(abs(Q.vac.conj() @ r) ** 2)
        _, info = episode(Q, psi, r, np.random.default_rng(0))
        row = {"n": n, "w0": w0, "lam_E": lE, "lam_B": lB, "theta": float(th), "E0": E0,
               "dE": info["exp_E"] - E_vac - E0, "pvac0": p0, "dpvac": info["exp_pvac"] - p0,
               "N_cut": info["N_cut"], "sum_err": abs(info["sum"] - 1)}
        out.append(row)
        print({k: (round(v, 7) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
        (OUT / f"p24a_redshift_n{n}.json").write_text(json.dumps(out) + "\n", encoding="utf-8")


def ladder(lE, lB=2.0, posfreq=False):
    """Exact per-flash drift of record energy and vacuum population from a ladder of record states."""
    out = []
    for sigma in ((1.2,) if posfreq else (1.2, 0.5)):
        Q, psi, loop, cos_omega = setup(lE, lB, sigma)
        if posfreq:
            psi, nmodes = positive_frequency(Q, psi)
            print("positive-frequency modes kept:", nmodes, flush=True)
        E_vac = rec_energy(Q, Q.vac)
        hot = hot_state(Q)
        for th in np.linspace(0, np.pi / 2, 7):
            r = np.cos(th) * Q.vac + np.sin(th) * hot
            E0, p0 = rec_energy(Q, r) - E_vac, float(abs(Q.vac.conj() @ r) ** 2)
            _, info = episode(Q, psi, r, np.random.default_rng(0))
            row = {"lam_E": lE, "lam_B": lB, "sigma": sigma, "flash_cos_omega": cos_omega, "theta": float(th), "E0": E0,
                   "dE": info["exp_E"] - E_vac - E0, "pvac0": p0, "dpvac": info["exp_pvac"] - p0,
                   "N_cut": info["N_cut"], "sum_err": abs(info["sum"] - 1)}
            out.append(row)
            print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
            (OUT / (f"p23_ladder_{lE}.json" if lB == 2.0 else f"p23_ladder_{lE}_{lB}{'_posfreq' if posfreq else ''}.json")).write_text(json.dumps(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if sys.argv[1] == "redshift":
        ladder_redshift(int(sys.argv[2]))
    elif sys.argv[1] == "ladder":
        ladder(float(sys.argv[2]), float(sys.argv[3]) if len(sys.argv) > 3 else 2.0, "posfreq" in sys.argv)
    else:
        trajectory(sys.argv[1], int(sys.argv[2]))
