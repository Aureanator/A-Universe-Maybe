"""P13b: exhaustive one-edge domain audit and unrestricted erasure witness."""

from collections import Counter
import argparse
import json
import time

from topology_audit import ROOT, linked_fixture, support_report
from constraintnet.curvature import CurvatureState
from constraintnet.decay import verify_decay_certificate
from constraintnet.gauge import gauge_transform
from constraintnet.rewrites import boundary_rewrite_certificate, verify_boundary_rewrite_certificate
from constraintnet.seeds import kuhn_ball


def support(state):
    components = state.components()
    return {"kinds": sorted(c["kind"] for c in components),
            "lengths": sorted(len(c["faces"]) for c in components)}


def domain(state):
    components = state.components()
    if any(c["kind"] != "loop" for c in components):
        return "junction"
    return "two_loops" if len(components) == 2 else "loop_count_changed"


def gauge_verify(source, target, certificate):
    state = CurvatureState(source)
    g = source.group
    lambdas = {v: g.elements[(7*v+1) % len(g.elements)] for v in source.vertices()}
    a, b = source.copy(), target.copy()
    gauge_transform(a, lambdas)
    gauge_transform(b, lambdas)
    transported = dict(certificate, moves=[])
    for move in certificate["moves"]:
        v = state.edges[move["edge"]][1]
        h = g.conjugate(lambdas[v], state.elements[move["multiplier"]])
        transported["moves"].append(dict(move, multiplier=state.index[h]))
    assert verify_boundary_rewrite_certificate(a, b, transported) == certificate["actions"]


def annotate_milestones(report):
    """Extract and independently verify topology-changing prefixes of the witness."""
    cert = report["unrestricted_erasure"]
    snapshots = report["snapshots"]
    first = next((s["step"] for s in snapshots if s["kinds"] != ["loop", "loop"]), None)
    selected = {} if first is None else {first: "first_domain_exit"}
    if first is not None:
        single = next((s["step"] for s in snapshots if s["step"] > first and s["kinds"] == ["loop"]), None)
        pair = next((s["step"] for s in snapshots if s["step"] > first and s["kinds"] == ["loop", "loop"]), None)
        if single is not None:
            selected[single] = "first_single_loop"
        if pair is not None:
            selected[pair] = "first_restored_two_loop_domain"
    cx = linked_fixture(report["group"])
    state = CurvatureState(cx)
    milestones = {}
    for step, move in enumerate(cert["moves"], 1):
        state.commit(move["edge"], *state.proposal(move["edge"], move["multiplier"]))
        if step in selected:
            nonincreasing = all(m["delta"] <= 0 for m in cert["moves"][:step])
            if nonincreasing:
                prefix = {"status": "prefix", "initial_action": cert["actions"][0],
                          "final_action": cert["actions"][step], "moves": cert["moves"][:step]}
                assert verify_decay_certificate(cx, prefix) == cert["actions"][:step+1]
            milestones[selected[step]] = {"step": step, "action": state.energy,
                                         "nonincreasing_prefix": nonincreasing,
                                         **support_report(state.cx)}
        if step >= max(selected, default=0):
            break
    report["milestones"] = milestones


def audit(group):
    cx = linked_fixture(group)
    state = CurvatureState(cx)
    baseline = tuple(state.labels), tuple(state.flux), state.energy
    census = Counter()
    witnesses = {}
    for edge in state.interior_edges:
        for h in range(len(state.elements)):
            if h == state.identity:
                continue
            proposal = state.proposal(edge, h)
            delta = proposal[2]
            state.commit(edge, *proposal)
            result = domain(state)
            arm = "nonincreasing" if delta <= 0 else "uphill"
            census[arm + ":" + result] += 1
            key = arm + ":" + result
            if result != "two_loops" and key not in witnesses:
                target = state.cx.copy()
                cert = boundary_rewrite_certificate(cx, target)
                verify_boundary_rewrite_certificate(cx, target, cert)
                gauge_verify(cx, target, cert)
                witnesses[key] = {"certificate": cert, "after": support_report(target),
                                  "gauge_transport_verified": True}
            state.commit(edge, *state.proposal(edge, state.inverse[h]))
    assert (tuple(state.labels), tuple(state.flux), state.energy) == baseline
    target = kuhn_ball(group, n=8)
    certificate = boundary_rewrite_certificate(cx, target)
    verify_boundary_rewrite_certificate(cx, target, certificate)
    gauge_verify(cx, target, certificate)
    snapshots = [dict(step=0, action=state.energy, **support(state))]
    for step, move in enumerate(certificate["moves"], 1):
        state.commit(move["edge"], *state.proposal(move["edge"], move["multiplier"]))
        snapshots.append(dict(step=step, action=state.energy, **support(state)))
    assert not state.components() and state.energy == 0
    report = {"group": group, "n": 8, "initial_support": support_report(cx),
              "proposal_count": len(state.interior_edges)*(len(state.elements)-1),
              "one_edge_domain_census": dict(sorted(census.items())),
              "one_edge_witnesses": witnesses,
              "unrestricted_erasure": certificate, "snapshots": snapshots,
              "gauge_transport_verified": True, "boundary_and_inverse_verified": True}
    annotate_milestones(report)
    print(f"{group} census={report['one_edge_domain_census']}", flush=True)
    print(f"{group} unrestricted erasure: {len(certificate['moves'])} moves, "
          f"H={certificate['actions'][0]}->{certificate['actions'][-1]}, "
          f"peak={max(certificate['actions'])}", flush=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--annotate-existing", action="store_true")
    args = parser.parse_args()
    output = ROOT / "reference/astra_session/data/topology_rewrite_audit.json"
    if args.annotate_existing:
        reports = json.loads(output.read_text(encoding="utf-8"))
        for report in reports:
            annotate_milestones(report)
            print(report["group"], report["milestones"], flush=True)
        output.write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
        return
    reports = []
    started = time.monotonic()
    for group in ("Z3", "A4"):
        reports.append(audit(group))
        output.write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
        print(f"elapsed={time.monotonic()-started:.1f}s", flush=True)


if __name__ == "__main__":
    main()
