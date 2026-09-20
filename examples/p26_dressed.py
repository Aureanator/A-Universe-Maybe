"""P26: a bounded, phase-resolved dressed-loop diagnostic (see PREDICTIONS).

Run: python examples/p26_dressed.py --n 5 --output <new-json-path>
Repeat with --n 6. Outputs are exclusive-created; completed checkpoints survive
an interrupted run. No automatic phase tuning or early stopping on an outcome.
"""

import argparse
from collections import deque
import json
from pathlib import Path
import sys
import time

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

from constraintnet.phase_filter import eigen_residual, phase_averages
from constraintnet.qrecord import QuantumRecordWalk
from constraintnet.seeds import kuhn_ball
from p25_seeded import df_branches, gibbs_bath, LOOPS


def setup(n):
    cx = kuhn_ball("A4", n=n)
    coords = {tuple(cx.vertex(v).metadata["grid"]): v for v in cx.vertices()}
    cycle = [coords[p] for p in LOOPS["L4"]]
    edges = [tuple(sorted(e)) for e in zip(cycle[:3], cycle[1:])]
    return cx, cycle, edges


def loop_distances(cx, cycle, arcs):
    """Graph distances from loop vertices; no embedding enters the measurement."""
    adj = {v: [] for v in cx.vertices()}
    for a, b in cx.edges():
        adj[a].append(b)
        adj[b].append(a)
    dist = {v: 0 for v in cycle}
    todo = deque(cycle)
    while todo:
        v = todo.popleft()
        for u in adj[v]:
            if u not in dist:
                dist[u] = dist[v] + 1
                todo.append(u)
    return np.array([dist[a] for a, _ in arcs])


def observables(Q, state, mask, distances):
    p = np.abs(state) ** 2
    arc_p = p.sum(axis=(1, 2))
    rec_p = p.sum(axis=(0, 2))
    return {
        "norm2": float(arc_p.sum()),
        "loop_weight": float(arc_p[mask].sum()),
        "distance_weights": np.bincount(distances, weights=arc_p).tolist(),
        "record_vacuum_population": float(np.sum(np.abs(
            np.einsum("aci,c->ai", state, Q.vac.conj())) ** 2)),
        "record_wilson_mean": float(rec_p @ Q.W),
        "record_configuration_probabilities": rec_p.tolist(),
    }


def embed_closed(closed_walk, open_walk, state):
    """Isometric embedding: retain every existing arc, zero the added exit arcs."""
    indices = np.array([open_walk.index[a] for a in closed_walk.arcs])
    out = np.zeros((len(open_walk.arcs),) + state.shape[1:], complex)
    out[indices] = state
    return out


def flat_step(Q, state):
    """Decoupled control: same coin and record, identity walker transport."""
    w = Q.walk
    ov = np.add.reduceat(w.phi[:, None, None] * state, w.starts, axis=0)
    coin = 2 * w.phi[:, None, None] * ov[w.vertex_of_arc] - state
    return Q.apply_rec(coin[w.target])  # closed shift is an involution


def run(n, output):
    start = time.perf_counter()
    output.parent.mkdir(parents=True, exist_ok=True)
    # Never silently overwrite an earlier scientific run.
    with output.open("x", encoding="utf-8") as f:
        json.dump({"experiment": "P26", "n": n, "status": "initializing"}, f)
    cx, cycle, edges = setup(n)
    Q = QuantumRecordWalk(cx, edges, 0.1, 0.1, mode="closed")
    df, mask = df_branches(Q, cycle)
    b, bath = gibbs_bath(Q, 0.14, 1)
    seed = df * b[None, :, None]
    seed /= np.linalg.norm(seed)
    flat_index = np.ravel_multi_index((Q.e_id,) * Q.k, (12,) * Q.k)
    free = df[:, flat_index, :][:, None, :] * Q.vac[None, :, None]
    del df
    rec_advanced = Q.apply_rec(Q.vac[None, :, None])[0, :, 0]
    vacuum_phase = float(np.angle(np.vdot(Q.vac, rec_advanced)))
    phases = [0.0, vacuum_phase]
    distances = loop_distances(cx, cycle, Q.walk.arcs)
    out = {
        "experiment": "P26", "status": "filtering", "n": n, "pattern": "L4",
        "couplings": [0.1, 0.1], "record_edges": edges, "record_configs": Q.nc,
        "bath": bath, "bath_seed": 1, "checkpoints": [64, 128, 256],
        "release_ticks": 128, "phases": phases, "filters": [], "release": [],
        "versions": {"python": sys.version, "numpy": np.__version__, "scipy": scipy.__version__},
    }
    frozen, _ = eigen_residual(Q.walk_step, seed, 0.0)
    free_report, _ = eigen_residual(lambda x: flat_step(Q, x), free, vacuum_phase)
    out["controls"] = {"frozen_compatible": frozen, "decoupled_vacuum": free_report}
    out["raw_seed"], _ = eigen_residual(Q.step, seed, vacuum_phase)
    out["raw_seed"].update(observables(Q, seed, mask, distances))
    # Known eigenstate filter amplitudes, evaluated analytically. Direct one-step
    # residuals above and exact-spectrum unit tests independently check the premise.
    out["controls"]["decoupled_filter_weights"] = [
        {"T": T, "zero_phase": float(abs(np.exp(1j * vacuum_phase * np.arange(T)).mean()) ** 2),
         "vacuum_phase": 1.0} for T in out["checkpoints"]]
    assert frozen["target_residual"] < 1e-12
    assert free_report["target_residual"] < 1e-12
    del free

    def save():
        out["elapsed_seconds"] = time.perf_counter() - start
        output.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    save()
    print(f"n={n} initialized, vacuum phase={vacuum_phase:.9f}", flush=True)
    finals = None
    for T, averages in phase_averages(Q.step, seed, phases, out["checkpoints"]):
        for phase, state in zip(phases, averages):
            report, advanced = eigen_residual(Q.step, state, phase)
            state_norm = np.linalg.norm(state)
            obs = observables(Q, state / state_norm, mask, distances)
            next_p = (np.abs(advanced) ** 2).sum(axis=(0, 2))
            report.update(obs)
            report.update({"T": T, "cesaro_residual_bound": 2 / (T * state_norm),
                           "record_diagonal_one_tick_l1": float(np.abs(
                               next_p - obs["record_configuration_probabilities"]).sum())})
            out["filters"].append(report)
            print(f"n={n} T={T} phase={phase:.6f} weight={report['filtered_weight']:.6g} "
                  f"loop={obs['loop_weight']:.6f} residual={report['target_residual']:.6g}", flush=True)
            del advanced
        if T == out["checkpoints"][-1]:
            finals = averages
        save()
    # Release BOTH tested phases, even a failed candidate, and the original seed.
    out["status"] = "releasing"
    save()
    Qo = QuantumRecordWalk(cx, edges, 0.1, 0.1, mode="open")
    loop_arcs = {Q.walk.arcs[i] for i in np.flatnonzero(mask)}
    omask = np.array([a in loop_arcs for a in Qo.walk.arcs])
    odist = loop_distances(cx, cycle, Qo.walk.arcs)
    for name, state in zip(["raw", "phase_zero", "phase_vacuum"], [seed] + finals):
        psi = embed_closed(Q.walk, Qo.walk, state / np.linalg.norm(state))
        gone = 0.0
        arm = {"arm": name, "samples": [], "max_bookkeeping_error": 0.0}
        out["release"].append(arm)
        for t in range(129):
            if t:
                psi = Qo.step(psi)
                gone += float(np.sum(np.abs(Qo.escaped) ** 2))
            norm2 = float(np.sum(np.abs(psi) ** 2))
            arm["max_bookkeeping_error"] = max(arm["max_bookkeeping_error"], abs(norm2 + gone - 1))
            if t in (0, 32, 64, 128):
                obs = observables(Qo, psi, omask, odist)
                obs.pop("record_configuration_probabilities")
                arm["samples"].append({"t": t, "escaped": gone, **obs})
                save()
                print(f"n={n} release {name} t={t} norm={norm2:.6f} loop={obs['loop_weight']:.6f}", flush=True)
        assert arm["max_bookkeeping_error"] < 1e-10
    out["status"] = "complete"
    save()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True, choices=[5, 6])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.n, args.output)
