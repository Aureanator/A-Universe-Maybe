"""P33 local recreation runner: audits, coefficient checks, spectral sweep, exact evolution.

Independent implementation from the registered protocol in docs/P33_VIRTUAL_PAIRS.md (commits
b8e462f, a836e7d) -- written by local Qwen 2026-09-20 without reading the sibling checkout's
uncommitted module, so agreement with Astra's archived p33_virtual_pairs.json is a genuine
cross-checkout reproduction. Writes machine-readable records; refuses to overwrite.

Run: PYTHONPATH=src python examples/p33_effective_local.py [--output PATH]
"""

import argparse
import json
from pathlib import Path

import numpy as np

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.defect_perturb import EffectiveDefects

DEFAULT_OUTPUT = Path("reference/local_qwen/data/p33_effective.json")


def run_fixture(fixture):
    ed = EffectiveDefects(fixture)
    audit = {**ed.basis_audit(),
             "first_order_block_identity": ed.first_order_block_identity(),
             **ed.duality_audit()}
    coeffs = ed.coefficient_predictions()
    second = ed.second_order_full()
    c_pair = ed.pair_matrix(second["C"])
    first_pair = ed.pair_matrix(sum(P @ ed.V @ P for P in ed.P.values()))
    sweeps = ed.sweep()

    evolutions = {}
    conservation_max = 0.0
    max_sector_departure = 0.0
    for lam in (0.01, 0.02, 0.04, 0.08):
        rows = ed.evolve_bare_pairs(lam)
        evolutions[str(lam)] = rows
        for row in rows:
            flat_prob = row["sector_probabilities"].get("2", 0.0)
            conservation_max = max(
                conservation_max,
                abs(row["norm"] - 1.0),
                abs(flat_prob + row["sector_probabilities"].get("0", 0.0)
                    + row["sector_probabilities"].get("4", 0.0) - 1.0),
            )
            if row["time"] > 0:
                departure = (row["sector_probabilities"].get("0", 0.0)
                             + row["sector_probabilities"].get("4", 0.0))
                max_sector_departure = max(max_sector_departure, departure)
    return {
        "fixture": fixture,
        "dimension": ed.patch.dim,
        "flat_dimension": ed.flat_dim,
        "vertices": list(ed.patch.vertices),
        "edges": [list(e) for e in ed.patch.edges],
        "vacuum_energy": ed.E_vac,
        "exact_audit": audit,
        "coefficient_predictions": coeffs,
        "first_order_matrix": first_pair.real.tolist(),
        "second_order_matrix": c_pair.real.tolist(),
        "sweeps": sweeps,
        "evolutions": evolutions,
        "summary": {
            "exact_audit_error_max": max(v for v in audit.values()),
            "coefficient_prediction_error_max": max(
                v for k, v in coeffs.items() if k.endswith(("error", "vanishes", "transfer", "coefficient"))),
            "conservation_error_max": conservation_max,
            "four_defect_weight_grown_max": max_sector_departure,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit(f"refusing to overwrite {args.output}; choose a new path")
    report = {
        "experiment": "P33-local-recreation",
        "protocol_commits": ["b8e462f", "a836e7d"],
        "implementer": "local Qwen, independent of sibling uncommitted module",
        "date": "2026-09-20",
        "status": "complete",
        "runs": [run_fixture(f) for f in ("tetrahedron", "bipyramid")],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=1), encoding="utf-8")
    for run in report["runs"]:
        print(f"{run['fixture']}: dim={run['dimension']} flat={run['flat_dimension']} "
              f"E_vac={run['vacuum_energy']:.3f} audit_max={run['summary']['exact_audit_error_max']:.2e} "
              f"coeffs_max={run['summary']['coefficient_prediction_error_max']:.2e} "
              f"conservation_max={run['summary']['conservation_error_max']:.2e}")
        for s in run["sweeps"]:
            print(f"  lam={s['coupling']:.2f} err1={s['first_order_error']:.3e} "
                  f"err2={s['second_order_error']:.3e}")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
