"""P11: registered larger-mesh follow-up, with complete traces and endpoint audit."""

import gzip
import json
import math
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.kinetics import CurvatureDriver
from particle_search import initial_complex


def main():
    out = Path("out/particle_search")
    reports = []
    started = time.monotonic()
    for group in ("Z3", "A4"):
        for n in (4, 5):
            for seed in range(3):
                cx = initial_complex(group, n, "uniform", seed)
                driver = CurvatureDriver(cx, beta=math.inf, seed=seed)
                name = f"scale_{group}_n{n}_s{seed}"
                trajectory = [{"step": 0, "action": driver.initial_energy}]
                with gzip.open(out / f"{name}.events.jsonl.gz", "wt") as stream:
                    stream.write(json.dumps({"model": "curvature_metropolis_v1", "run": name,
                                             "initial_labels": driver.state.labels,
                                             "edges": driver.state.edges,
                                             "group_elements": driver.state.elements}) + "\n")
                    for step in range(1, 200_001):
                        driver.advance()
                        stream.write(json.dumps(driver.last_event, separators=(",", ":")) + "\n")
                        if step % 1000 == 0 or driver.state.energy == 0:
                            components = driver.state.components()
                            trajectory.append({"step": step, "action": driver.state.energy,
                                               "components": len(components),
                                               "sizes": [len(c["faces"]) for c in components]})
                        if driver.state.energy == 0:
                            break
                downhill = equal = 0
                for ei in driver.state.interior_edges:
                    for h in driver.generators:
                        delta = driver.state.proposal(ei, h)[2]
                        downhill += delta < 0
                        equal += delta == 0
                report = {"run": name, "group": group, "n": n, "seed": seed,
                          "model": "curvature_metropolis_v1", "beta": "inf",
                          "start": "uniform", "planned_horizon": 200_000,
                          "steps": driver.step, "initial_action": driver.initial_energy,
                          "final_action": driver.state.energy, "downhill_exits": downhill,
                          "equal_action_proposals": equal, "trajectory": trajectory,
                          "interior_edges": len(driver.state.interior_edges),
                          "final_labels": list(driver.state.labels)}
                reports.append(report)
                (out / "scale_runs.json").write_text(json.dumps(reports, indent=2), encoding="utf-8")
                print(f"{name}: H={driver.state.energy}, step={driver.step}, downhill={downhill}, "
                      f"equal={equal}, elapsed={time.monotonic()-started:.1f}s", flush=True)


if __name__ == "__main__":
    main()
