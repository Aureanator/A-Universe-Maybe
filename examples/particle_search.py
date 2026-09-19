"""P8 exact census and P9 registered bulk sweep; reproducible artifacts.

Run: python examples/particle_search.py
Writes machine-readable measurements and compressed microscopic event traces.
No particle identities, forces, coordinates, or reaction rules drive this run.
"""

import argparse
import gzip
import json
import math
from pathlib import Path
import random
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.curvature import CurvatureState, SupportLineage
from constraintnet.kinetics import CurvatureDriver
from constraintnet.landscape import enumerate_landscape
from constraintnet.seeds import kuhn_ball, make_tetrahedron_boundary


def initial_complex(group, n, start, seed):
    cx = kuhn_ball(group, n=n)
    indexed = CurvatureState(cx)
    rng = random.Random(seed + 100_000)
    edges = list(indexed.interior_edges)
    if start == "dilute":
        edges = rng.sample(edges, max(1, len(edges) // 10))
    for ei in edges:
        cx.set_label(*indexed.edges[ei], rng.choice(cx.group.elements))
    return cx


def run_one(group, n, beta_name, start, seed, steps, out):
    beta = math.inf if beta_name == "inf" else float(beta_name)
    cx = initial_complex(group, n, start, seed)
    driver = CurvatureDriver(cx, beta=beta, seed=seed)
    state = driver.state
    tracker = SupportLineage(state.components(), len(state.tets))
    run_id = f"{group}_n{n}_b{beta_name}_{start}_s{seed}"
    trajectory = []
    frames = []
    capture = group == "A4" and n == 3 and seed == 0 and start == "uniform"
    boundary = {e: cx.label(*e) for e in cx.edges()
                if e not in {state.edges[i] for i in state.interior_edges}}

    def sample(step):
        components = state.components()
        trajectory.append({"step": step, "action": state.energy,
                           "components": len(components),
                           "loops": sum(c["kind"] == "loop" for c in components),
                           "largest_tet_fraction": max((len(c["tets"]) / len(state.tets)
                                                        for c in components), default=0)})
        if capture:
            frames.append({"step": step, "flux": list(state.flux), "action": state.energy})

    sample(0)
    with gzip.open(out / f"{run_id}.events.jsonl.gz", "wt", encoding="utf-8") as trace:
        trace.write(json.dumps({"model": "curvature_metropolis_v1", "run": run_id,
                                "beta": beta_name, "initial_labels": list(state.labels),
                                "edges": state.edges, "group_elements": state.elements}) + "\n")
        for step in range(1, steps + 1):
            driver.advance()
            record = driver.last_event
            trace.write(json.dumps(record, separators=(",", ":")) + "\n")
            if record["accepted"]:
                tracker.advance(state.components(), step)
            if step % max(1, steps // 100) == 0:
                sample(step)
    assert all(state.cx.label(*e) == label for e, label in boundary.items())
    downhill = equal = 0
    for edge in state.interior_edges:
        for multiplier in driver.generators:
            delta = state.proposal(edge, multiplier)[2]
            downhill += delta < 0
            equal += delta == 0
    result = {"id": run_id, "group": group, "n": n, "beta": beta_name,
              "start": start, "seed": seed, "steps": steps,
              "model": "curvature_metropolis_v1", "boundary": "fixed_identity_outer_only",
              "faces": len(state.faces), "tetrahedra": len(state.tets),
              "interior_edges": len(state.interior_edges),
              "initial_action": driver.initial_energy, "final_action": state.energy,
              "accepted": driver.accepted, "bath_ledger": driver.bath_ledger,
              "final_downhill_proposals": downhill, "final_equal_action_proposals": equal,
              "boundary_preserved": True, "trajectory": trajectory,
              "lineage": tracker.report(steps)}
    if capture:
        with gzip.open(out / f"{run_id}.frames.json.gz", "wt", encoding="utf-8") as stream:
            json.dump({"run": result, "frames": frames, "faces": state.faces,
                       "tets": state.tets, "elements": state.elements,
                       "identity": state.identity,
                       "vertex_metadata": {v: cx.vertex(v).metadata for v in cx.vertices()}}, stream)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--steps", type=int, default=10_000)
    parser.add_argument("--out", type=Path, default=Path("out/particle_search"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    census = {g: enumerate_landscape(make_tetrahedron_boundary(g)).summary() for g in ("Z3", "A4")}
    (args.out / "landscape.json").write_text(json.dumps(census, indent=2), encoding="utf-8")
    results = []
    started = time.monotonic()
    for group in ("Z3", "A4"):
        for n in (2, 3):
            for beta in ("0", "1", "2", "inf"):
                for start in ("uniform", "dilute"):
                    for seed in range(3):
                        result = run_one(group, n, beta, start, seed, args.steps, args.out)
                        results.append(result)
                        (args.out / "runs.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
                        print(f"{len(results):2d}/96 {result['id']}: H {result['initial_action']} -> "
                              f"{result['final_action']}, candidates "
                              f"{len(result['lineage']['candidate_screen_passes'])}, "
                              f"{time.monotonic() - started:.1f}s", flush=True)


if __name__ == "__main__":
    main()
