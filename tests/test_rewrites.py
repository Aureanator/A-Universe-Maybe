"""Connectivity does not assume abelian labels or downhill-only moves."""

from copy import deepcopy

import pytest

from constraintnet.curvature import CurvatureState
from constraintnet.rewrites import boundary_rewrite_certificate, verify_boundary_rewrite_certificate
from constraintnet.seeds import kuhn_ball, randomize_labels


@pytest.mark.parametrize("group", ["Z3", "A4"])
def test_any_fixed_boundary_labels_can_be_joined(group):
    source = kuhn_ball(group, n=2)
    randomize_labels(source, seed=9)
    target = source.copy()
    state = CurvatureState(source)
    for i in state.interior_edges:
        target.set_label(*state.edges[i], state.elements[(3*i+1) % len(state.elements)])
    before = source.labels_snapshot(), target.labels_snapshot()
    cert = boundary_rewrite_certificate(source, target)
    assert len(cert["moves"]) == sum(source.label(*e) != target.label(*e) for e in state.edges)
    verify_boundary_rewrite_certificate(source, target, cert)
    assert before == (source.labels_snapshot(), target.labels_snapshot())


def test_uphill_moves_are_explicit_and_invalid_targets_rejected():
    source = kuhn_ball("A4", n=2)
    target = source.copy()
    state = CurvatureState(source)
    target.set_label(*state.edges[state.interior_edges[0]], state.elements[1])
    cert = boundary_rewrite_certificate(source, target)
    assert cert["peak_above_initial"] > 0
    verify_boundary_rewrite_certificate(source, target, cert)
    broken = deepcopy(cert)
    broken["moves"][0]["delta"] += 1
    with pytest.raises(ValueError, match="difference"):
        verify_boundary_rewrite_certificate(source, target, broken)
    boundary = next(i for i in range(len(state.edges)) if i not in state.interior_edges)
    target.set_label(*state.edges[boundary], state.elements[1])
    with pytest.raises(ValueError, match="boundary"):
        boundary_rewrite_certificate(source, target)
    with pytest.raises(ValueError, match="complex"):
        boundary_rewrite_certificate(source, kuhn_ball("A4", n=1))


@pytest.mark.parametrize("group", ["Z3", "A4"])
def test_every_pair_on_single_interior_edge(group):
    source = kuhn_ball(group, n=1)
    state = CurvatureState(source)
    assert len(state.interior_edges) == 1
    edge = state.edges[state.interior_edges[0]]
    for a in state.elements:
        source.set_label(*edge, a)
        for b in state.elements:
            target = source.copy()
            target.set_label(*edge, b)
            cert = boundary_rewrite_certificate(source, target)
            assert len(cert["moves"]) == (a != b)
            verify_boundary_rewrite_certificate(source, target, cert)
