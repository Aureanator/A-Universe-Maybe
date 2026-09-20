"""P20: does a responsive record hold a pivoting wave together? (PREDICTIONS P20; DYNAMICS_DESIGN section 8)

Arms: C0 (v4.0, no feedback), C1 (random chops matched in count), F(kappa) for
kappa in {0.5, 0.2, 0.05} x max|K| at t=0. Coordinates prepare the initial vortex
ring only; measurements are relational (graph ball around the centre vertex).
Reproduce: python examples/p20_record.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from constraintnet.seeds import kuhn_ball, randomize_labels
from constraintnet.walk import RecordWalk

N, T, SIGMA, RING_R, BALL = 16, 400, 3.0, 3.0, 4
CHECK = (10, 50, 100, 200, 400)


def initial_state(rw):
    cx, w = rw.cx, rw.walk
    grid = {v: np.array(cx.vertex(v).metadata["grid"], float) for v in cx.vertices()}
    p0 = np.array([N / 2] * 3)
    n0 = rw.q_axes[0]                                   # spin along an A4 3-fold axis
    helper = np.array([1.0, 0.0, 0.0]) if abs(n0[0]) < 0.9 else np.array([0.0, 1.0, 0.0])
    u1 = np.cross(n0, helper); u1 /= np.linalg.norm(u1)
    u2 = np.cross(n0, u1)
    pol = (u1 + 1j * u2) / np.sqrt(2)
    amp = {}
    for v in w.interior:
        d = grid[v] - p0
        rho = np.hypot(d[0], d[1])
        amp[v] = np.exp(-(d @ d) / (2 * SIGMA ** 2)) * ((rho - RING_R) + 1j * d[2])
    psi = np.array([w.phi[i] * amp[a] for i, (a, b) in enumerate(w.arcs)])[:, None] * pol[None, :]
    centre = min(w.interior, key=lambda v: np.linalg.norm(grid[v] - p0))
    return psi / np.linalg.norm(psi), centre


def hop_ball(cx, centre, r):
    nb = {v: set() for v in cx.vertices()}
    for a, b in cx.edges():
        nb[a].add(b); nb[b].add(a)
    seen, front = {centre}, {centre}
    for _ in range(r):
        front = {u for v in front for u in nb[v]} - seen
        seen |= front
    return seen


def run(arm, kappa_abs=None, chop_counts=None, seed=7):
    cx = kuhn_ball("A4", n=N)
    rw = RecordWalk(cx, kappa=np.inf if arm in ("C0", "C1") else kappa_abs)
    psi, centre = initial_state(rw)
    ball = hop_ball(cx, centre, BALL)
    in_ball = np.array([a in ball for a, _ in rw.walk.arcs])
    rng = np.random.default_rng(seed)
    interior_edges = rw.ring_edges
    rec = {"arm": arm, "kappa": kappa_abs, "checkpoints": []}
    counts = []
    for t in range(1, T + 1):
        psi, c = rw.step(psi)
        if arm == "C1":
            c = chop_counts[t - 1]
            if c:
                ei = rng.choice(interior_edges, size=c, replace=False)
                sa = np.array(rw.q_ids)[rng.integers(len(rw.q_ids), size=c)]
                sb = np.array(rw.q_ids)[rng.integers(len(rw.q_ids), size=c)]
                rw.lab[ei] = rw.mul[rw.mul[sa, rw.lab[ei]], sb]
                rw._rebuild()
        counts.append(int(c))
        if t in CHECK:
            rec["checkpoints"].append({"t": t, "norm_in_region": float((np.abs(psi) ** 2).sum()),
                                       "weight_in_ball": float((np.abs(psi[in_ball]) ** 2).sum()),
                                       "chops_so_far": int(sum(counts)), "H": int(rw.curvature_count())})
            print(arm, kappa_abs, rec["checkpoints"][-1], flush=True)
    rec["chop_counts"] = counts
    return rec


def main():
    probe = RecordWalk(kuhn_ball("A4", n=N), kappa=np.inf)
    psi0, _ = initial_state(probe)
    p2 = np.append((np.abs(psi0) ** 2).sum(1), 0.0)
    Kmax = float(np.abs(p2[probe.r_fwd].sum(1) - p2[probe.r_bwd].sum(1)).max())
    out = {"N": N, "T": T, "Kmax_t0": Kmax, "arms": []}
    out["arms"].append(run("C0"))
    feedback = []
    for f in (0.5, 0.2, 0.05):
        feedback.append(run("F", kappa_abs=f * Kmax))
        feedback[-1]["kappa_fraction"] = f
    out["arms"] += feedback
    for fb in feedback:                                   # one matched random-chop control per kappa
        c1 = run("C1", chop_counts=fb["chop_counts"])
        c1["matched_to_kappa_fraction"] = fb["kappa_fraction"]
        out["arms"].append(c1)
    (ROOT / "reference/opus_session/data/p20_record.json").write_text(
        json.dumps(out, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
