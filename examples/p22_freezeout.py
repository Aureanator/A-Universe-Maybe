"""P22: freeze-out -- does trapped light appear only once the chop calms? (PREDICTIONS P22)

Hot record state |r_theta> = cos(theta)|vac> + sin(theta)|hot>, flash of ordinary light centred on
the quantum square, open walls. Escaped branches keep their record: its vacuum population is
frozen at escape (U_rec alone conserves it), so record calmness is bookkept for the whole world.
Reproduce: python examples/p22_freezeout.py [A03|A10|rest]
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

N, T, EVERY, SEED = 6, 600, 5, 22
THETAS = [0.0, np.pi / 8, np.pi / 4, 3 * np.pi / 8, np.pi / 2]
OUT = ROOT / "reference/opus_session/data"


def setup(lE, lB):
    cx = kuhn_ball("A4", n=N)
    grid = {v: np.array(cx.vertex(v).metadata["grid"], float) for v in cx.vertices()}
    G = {tuple(int(x) for x in p): v for v, p in grid.items()}
    cyc = [G[(2, 2, 3)], G[(3, 2, 3)], G[(3, 3, 3)], G[(2, 3, 3)]]
    qedges = [tuple(sorted(e)) for e in zip(cyc[:3], cyc[1:4])]
    Q = QuantumRecordWalk(cx, qedges, lE, lB, mode="open")
    w = Q.walk
    loop = np.zeros(len(w.arcs), bool)
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
        loop[w.index[(a, b)]] = loop[w.index[(b, a)]] = True
    p0, sig = np.array([2.5, 2.5, 3.0]), 1.2
    pol = np.array([1.0, 2.0, 3.0]); pol /= np.linalg.norm(pol)
    amp = {v: np.exp(-((grid[v] - p0) @ (grid[v] - p0)) / (2 * sig ** 2)) for v in w.interior}
    psi = np.array([w.phi[i] * amp[a] for i, (a, b) in enumerate(w.arcs)])[:, None] * pol[None, :]
    psi = psi.astype(complex) / np.linalg.norm(psi)
    return Q, psi, loop


def hot_state(Q):
    rng = np.random.default_rng(SEED)
    h = rng.normal(size=Q.nc) + 1j * rng.normal(size=Q.nc)
    h -= Q.vac * (Q.vac.conj() @ h)
    return h / np.linalg.norm(h)


def run(lE, lB, theta, record=True):
    Q, psi, loop = setup(lE, lB)
    hot = hot_state(Q)
    r = np.cos(theta) * Q.vac + np.sin(theta) * hot
    Psi = psi[:, None, :] * r[None, :, None]
    vac = Q.vac.conj()
    E_vac = float(np.real(Q.vac.conj() @ Q.apply_H(Q.vac[None, :, None])[0, :, 0]))
    rec = {"lam_E": lE, "lam_B": lB, "theta": theta, "arm": ("A" if record else "Q") if lE > 0 else "C0",
           "t": [], "N": [], "loop": [], "Pvac_in": [], "Pvac_total": [], "E_in": [], "escaped": []}
    gone, pvac_out = 0.0, 0.0
    rec["E_rec0"] = float(np.real(np.vdot(Psi, Q.apply_H(Psi)))) - E_vac
    t0 = time.time()
    for t in range(1, T + 1):
        Psi = Q.walk_step(Psi)
        esc = Q.escaped
        gone += float((np.abs(esc) ** 2).sum())
        pvac_out += float((np.abs(np.tensordot(esc, vac, axes=(1, 0))) ** 2).sum())
        if record:
            Psi = Q.apply_rec(Psi)
        if t % EVERY == 0:
            p2 = (np.abs(Psi) ** 2).sum(axis=(1, 2))
            pin = float((np.abs(np.tensordot(Psi, vac, axes=(1, 0))) ** 2).sum())
            rec["t"].append(t); rec["N"].append(float(p2.sum())); rec["loop"].append(float(p2[loop].sum()))
            rec["Pvac_in"].append(pin); rec["Pvac_total"].append(pin + pvac_out)
            rec["escaped"].append(gone)
            if t % (4 * EVERY) == 0:
                rec["E_in"].append(float(np.real(np.vdot(Psi, Q.apply_H(Psi)))) - E_vac * rec["N"][-1])
    rec["bookkeeping_err"] = abs(rec["N"][-1] + gone - 1)
    rec["seconds"] = time.time() - t0
    print(rec["arm"], lE, lB, round(theta, 4), "N(T)", round(rec["N"][-1], 6), "loop", round(rec["loop"][-1], 6),
          "Pvac_tot 0->T", round(np.cos(theta) ** 2, 4), round(rec["Pvac_total"][-1], 6),
          "Pvac_in/N", round(rec["Pvac_in"][-1] / max(rec["N"][-1], 1e-300), 4), "%.0fs" % rec["seconds"], flush=True)
    return rec


def main(part):
    runs = []
    if part in ("A03", "A10"):
        lE = 0.3 if part == "A03" else 1.0
        for th in THETAS:
            runs.append(run(lE, 2.0, th, True))
            (OUT / f"p22_{part}.json").write_text(json.dumps({"T": T, "runs": runs}) + "\n", encoding="utf-8")
    else:
        runs.append(run(0.0, 2.0, 0.0))
        for lE in (0.3, 1.0):
            for th in (np.pi / 4, np.pi / 2):
                runs.append(run(lE, 2.0, th, False))
                (OUT / "p22_rest.json").write_text(json.dumps({"T": T, "runs": runs}) + "\n", encoding="utf-8")
    (OUT / f"p22_{part}.json").write_text(json.dumps({"T": T, "runs": runs}) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
