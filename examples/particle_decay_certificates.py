"""P12: certify decay of the archived P11 endpoints; no stochastic rerun."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from constraintnet.curvature import CurvatureState
from constraintnet.decay import decay_certificate, verify_decay_certificate
from constraintnet.gauge import gauge_transform
from constraintnet.seeds import kuhn_ball


def main():
    source = ROOT / "reference/astra_session/data/scale_runs.json"
    reports = []
    for run in json.loads(source.read_text(encoding="utf-8")):
        if run["final_action"] == 0:
            continue
        cx = kuhn_ball(run["group"], n=run["n"])
        state = CurvatureState(cx)
        if len(run["final_labels"]) != len(state.edges):
            raise ValueError("archived label count mismatch")
        for edge, label in zip(state.edges, run["final_labels"]):
            cx.set_label(*edge, state.elements[label])
        cert = decay_certificate(cx)
        assert cert["initial_action"] == run["final_action"]
        actions = verify_decay_certificate(cx, cert)
        # Transport the same witness under an independent gauge change at each
        # vertex. Right multipliers conjugate at the edge's target vertex.
        group = cx.group
        lambdas = {v: group.elements[(7 * v + 1) % len(group.elements)] for v in cx.vertices()}
        transformed = cx.copy()
        gauge_transform(transformed, lambdas)
        transported = dict(cert, moves=[])
        for move in cert["moves"]:
            target = state.edges[move["edge"]][1]
            multiplier = group.conjugate(lambdas[target], state.elements[move["multiplier"]])
            transported["moves"].append(dict(move, multiplier=state.index[multiplier]))
        assert verify_decay_certificate(transformed, transported) == actions
        report = {"run": run["run"], "group": run["group"], "n": run["n"],
                  "source": str(source.relative_to(ROOT)),
                  "initial_labels": run["final_labels"], "edges": state.edges,
                  "group_elements": state.elements, "certificate": cert,
                  "actions": actions, "gauge_transport_verified": True,
                  "boundary_and_inverse_verified": True}
        reports.append(report)
        print(f"{run['run']}: {cert['status']}, actions={actions}, moves={len(cert['moves'])}", flush=True)
    output = ROOT / "reference/astra_session/data/decay_certificates.json"
    output.write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
