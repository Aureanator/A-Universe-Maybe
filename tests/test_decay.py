"""Decay certificates must distinguish witnesses, closure, and search cutoffs."""

from copy import deepcopy

import pytest

from constraintnet.curvature import CurvatureState
from constraintnet.decay import decay_certificate, verify_decay_certificate
from constraintnet.seeds import kuhn_ball, randomize_labels


@pytest.mark.parametrize("group", ["Z3", "A4"])
def test_vacuum_and_single_excitation_with_inverse(group):
    cx = kuhn_ball(group, n=2)
    vacuum = decay_certificate(cx)
    assert vacuum["status"] == "vacuum"
    assert verify_decay_certificate(cx, vacuum) == [0]
    state = CurvatureState(cx)
    edge = state.edges[state.interior_edges[0]]
    label = next(g for g in cx.group.elements if g != cx.group.identity())
    cx.set_label(*edge, label)
    before = cx.labels_snapshot()
    cert = decay_certificate(cx, max_plateau_states=1)
    assert cert["status"] == "vacuum"
    assert len(cert["moves"]) == 1
    assert verify_decay_certificate(cx, cert)[-1] == 0
    assert cx.labels_snapshot() == before
    corrupt = deepcopy(cert)
    corrupt["moves"][0]["delta"] += 1
    with pytest.raises(ValueError, match="action change"):
        verify_decay_certificate(cx, corrupt)
    corrupt = deepcopy(cert)
    corrupt["moves"][0]["edge"] = next(i for i in range(len(state.edges)) if i not in state.interior_edges)
    with pytest.raises(ValueError, match="proposal set"):
        verify_decay_certificate(cx, corrupt)


def test_closed_plateau_with_fixed_curved_boundary():
    cx = kuhn_ball("Z3", n=1)
    state = CurvatureState(cx)
    # Give the fixed boundary nonzero curvature. The one interior body diagonal
    # can still vary; enumerate its entire three-state space.
    boundary_edge = next(e for i, e in enumerate(state.edges) if i not in state.interior_edges)
    cx.set_label(*boundary_edge, 1)
    cert = decay_certificate(cx, max_plateau_states=10)
    assert cert["status"] == "closed_plateau"
    assert cert["final_action"] > 0
    verify_decay_certificate(cx, cert)


def test_cutoff_does_not_claim_closed_plateau():
    cx = kuhn_ball("Z3", n=1)
    randomize_labels(cx, seed=0)
    limited = decay_certificate(cx, max_plateau_states=1)
    complete = decay_certificate(cx, max_plateau_states=3)
    assert limited["status"] == "budget_exhausted"
    assert complete["status"] == "closed_plateau"
    assert complete["plateau_searches"][-1]["discovered_states"] == 3


def test_equal_action_steps_reconstruct_a_valid_path():
    cx = kuhn_ball("Z3", n=2)
    randomize_labels(cx, seed=0)
    cert = decay_certificate(cx, max_plateau_states=100)
    assert any(move["delta"] == 0 for move in cert["moves"])
    actions = verify_decay_certificate(cx, cert)
    assert all(a >= b for a, b in zip(actions, actions[1:]))


def test_archived_witnesses_replay():
    import json
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "reference/astra_session/data/decay_certificates.json"
    for report in json.loads(path.read_text(encoding="utf-8")):
        cx = kuhn_ball(report["group"], n=report["n"])
        state = CurvatureState(cx)
        assert [list(e) for e in state.edges] == report["edges"]
        for edge, label in zip(state.edges, report["initial_labels"]):
            cx.set_label(*edge, state.elements[label])
        assert verify_decay_certificate(cx, report["certificate"]) == report["actions"]


def test_invalid_budget():
    with pytest.raises(ValueError):
        decay_certificate(kuhn_ball("Z3", n=1), max_plateau_states=0)
