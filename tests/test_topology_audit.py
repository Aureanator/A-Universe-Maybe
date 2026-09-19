"""Replay the prescribed linked fixture and its topology-changing witnesses."""

import json
from pathlib import Path

import pytest

from examples.topology_audit import linked_fixture, support_report
from constraintnet.curvature import CurvatureState
from constraintnet.decay import verify_decay_certificate
from constraintnet.gauge import gauge_transform
from constraintnet.landscape import curvature_action
from constraintnet.rewrites import boundary_rewrite_certificate
from constraintnet.seeds import kuhn_ball

DATA = Path(__file__).resolve().parents[1] / "reference/astra_session/data"


@pytest.mark.slow
@pytest.mark.parametrize("group", ["Z3", "A4"])
def test_linked_fixture_has_nonincreasing_merger_and_replayable_erasure(group):
    reports = json.loads((DATA / "topology_rewrite_audit.json").read_text(encoding="utf-8"))
    report = next(r for r in reports if r["group"] == group)
    cx = linked_fixture(group)
    assert support_report(cx) == report["initial_support"]
    assert report["initial_support"]["absolute_linking"] == 1
    assert sum(report["one_edge_domain_census"].values()) == report["proposal_count"]
    cert = report["unrestricted_erasure"]
    assert cert == boundary_rewrite_certificate(cx, kuhn_ball(group, n=8))
    assert len(cert["moves"]) == 140
    assert [m["delta"] for m in cert["moves"] if m["delta"] > 0] == [1]
    assert max(cert["actions"]) == cert["actions"][0] == 98
    prefix = {"status": "prefix", "initial_action": 98, "final_action": 84,
              "moves": cert["moves"][:38]}
    assert verify_decay_certificate(cx, prefix) == cert["actions"][:39]
    state = CurvatureState(cx)
    initial_boundary = {state.edges[i]: label for i, label in enumerate(state.labels)
                        if i not in set(state.interior_edges)}
    for step, move in enumerate(cert["moves"], 1):
        state.commit(move["edge"], *state.proposal(move["edge"], move["multiplier"]))
        if step in (37,38,52,140):
            assert curvature_action(state.cx) == cert["actions"][step]
            kinds = sorted(c["kind"] for c in state.components())
            assert kinds == {37:["junction/open"], 38:["loop"], 52:["loop","loop"], 140:[]}[step]
        if step == 37:
            changed = state.cx.copy()
            g = changed.group
            gauge_transform(changed, {v:g.elements[(7*v+1) % len(g.elements)] for v in changed.vertices()})
            assert CurvatureState(changed).components() == state.components()
    assert all(label == state.identity for label in state.labels)
    assert all(state.index[state.cx.label(*edge)] == label for edge, label in initial_boundary.items())


def test_original_budget_exhaustion_is_preserved():
    reports = json.loads((DATA / "topology_audit.json").read_text(encoding="utf-8"))
    assert len(reports) == 2
    for report in reports:
        assert report["certificate"]["status"] == "budget_exhausted"
        assert report["certificate"]["max_plateau_states"] == 32
        assert [s["action"] for s in report["snapshots"]] == [98,98,98,96]
        assert all(s["absolute_linking"] == 1 for s in report["snapshots"])
