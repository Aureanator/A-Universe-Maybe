"""Cross-check subset search with independent full-holonomy permutation search."""

import itertools

import pytest

from constraintnet.curvature import CurvatureState
from constraintnet.decay import verify_decay_certificate
from constraintnet.landscape import curvature_action
from constraintnet.path_order import nonincreasing_order
from constraintnet.seeds import kuhn_ball, randomize_labels


@pytest.mark.parametrize("group", ["Z3", "A4"])
@pytest.mark.parametrize("seed", [0,1,2])
def test_subset_search_matches_all_permutations(group, seed):
    cx = kuhn_ball(group, n=2)
    randomize_labels(cx, seed=seed)
    state = CurvatureState(cx)
    multiplier = next(i for i in range(len(state.elements)) if i != state.identity)
    moves = [{"edge": e, "multiplier": multiplier} for e in state.interior_edges[:4]]
    before = cx.labels_snapshot()
    feasible = []
    target = None
    for order in itertools.permutations(range(len(moves))):
        scratch = cx.copy()
        previous = curvature_action(scratch)
        valid = True
        for i in order:
            e = state.edges[moves[i]["edge"]]
            scratch.set_label(*e, cx.group.multiply(scratch.label(*e), state.elements[multiplier]))
            action = curvature_action(scratch)
            valid &= action <= previous
            previous = action
        if target is None:
            target = scratch.labels_snapshot()
        assert scratch.labels_snapshot() == target
        if valid:
            feasible.append(list(order))
    report = nonincreasing_order(cx, moves, max_states=16)
    assert (report["status"] == "reordered") == bool(feasible)
    assert cx.labels_snapshot() == before
    if feasible:
        assert report["order"] in feasible
        cert = dict(report, final_action=report["target_action"])
        verify_decay_certificate(cx, cert)
    else:
        assert report["status"] == "no_nonincreasing_order"


def test_budget_empty_and_uphill_only_cases():
    cx = kuhn_ball("Z3", n=1)
    state = CurvatureState(cx)
    ei, = state.interior_edges
    move = {"edge": ei, "multiplier": 1}
    assert nonincreasing_order(cx, [move])["status"] == "no_nonincreasing_order"
    cx.set_label(*state.edges[ei], 2)
    assert nonincreasing_order(cx, [move], max_states=1)["status"] == "budget_exhausted"
    assert nonincreasing_order(cx, [move], max_states=2)["status"] == "reordered"
    assert nonincreasing_order(cx, [])["moves"] == []
    with pytest.raises(ValueError, match="distinct"):
        nonincreasing_order(cx, [move, move])
    with pytest.raises(ValueError, match="positive"):
        nonincreasing_order(cx, [move], max_states=0)
    with pytest.raises(ValueError, match="proposal"):
        nonincreasing_order(cx, [dict(move, multiplier=0)])
