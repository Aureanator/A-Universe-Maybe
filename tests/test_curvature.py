"""Local action, reversibility, gauge controls, and lineage semantics."""

import math

from constraintnet.curvature import CurvatureState, SupportLineage
from constraintnet.gauge import gauge_transform
from constraintnet.holonomy import triangle_holonomy
from constraintnet.kinetics import CurvatureDriver
from constraintnet.landscape import curvature_action
from constraintnet.region import Region
from constraintnet.seeds import kuhn_ball, randomize_labels


def test_local_deltas_match_full_recomputation_and_inverse():
    cx = kuhn_ball("A4", n=2)
    randomize_labels(cx, seed=3)
    state = CurvatureState(cx)
    for edge in state.interior_edges:
        for multiplier in range(len(state.elements)):
            before = state.cx.labels_snapshot()
            old_energy = state.energy
            new, changed, delta = state.proposal(edge, multiplier)
            state.commit(edge, new, changed, delta)
            assert state.energy == curvature_action(state.cx) == old_energy + delta
            inverse = state.inverse[multiplier]
            state.commit(edge, *state.proposal(edge, inverse))
            assert state.cx.labels_snapshot() == before
            assert state.energy == old_energy


def test_gauge_transformed_proposal_has_identical_delta():
    cx = kuhn_ball("A4", n=2)
    randomize_labels(cx, seed=8)
    original = CurvatureState(cx)
    g = cx.group
    lambdas = {v: g.elements[(v * 7 + 1) % len(g.elements)] for v in cx.vertices()}
    gauge_transform(cx, lambdas)
    transformed = CurvatureState(cx)
    assert original.energy == transformed.energy
    for edge in original.interior_edges:
        _, v = original.edges[edge]
        for multiplier in range(len(g.elements)):
            conjugated = g.conjugate(lambdas[v], g.elements[multiplier])
            new, changed, delta = original.proposal(edge, multiplier)
            new2, changed2, delta2 = transformed.proposal(edge, transformed.index[conjugated])
            assert delta == delta2
            for fi in changed:
                base = original.faces[fi][0]
                assert g.conjugate(lambdas[base], original.elements[changed[fi]]) == transformed.elements[changed2[fi]]


def test_driver_preserves_boundary_and_action_ledger():
    cx = kuhn_ball("A4", n=2)
    randomize_labels(cx, seed=4)
    before = Region(cx, cx.tetrahedra()).gauge_invariant_state()
    driver = CurvatureDriver(cx, beta=math.inf, seed=2)
    previous = driver.state.energy
    for _ in range(300):
        driver.advance()
        assert driver.state.energy <= previous
        previous = driver.state.energy
        assert previous + driver.bath_ledger == driver.initial_energy
    assert Region(driver.state.cx, cx.tetrahedra()).gauge_invariant_state() == before
    assert previous == curvature_action(driver.state.cx)


def test_support_lineage_split_merge_and_censoring():
    def component(*faces):
        return {"faces": frozenset(faces), "tets": frozenset({0}), "kind": "loop"}
    tracker = SupportLineage([component(0, 1)], 10)
    tracker.advance([component(0), component(1)], 5)
    tracker.advance([component(0, 1)], 9)
    report = tracker.report(20, min_lifetime=10)
    assert report["geometric_events"] == {"birth": 0, "death": 0, "merge": 1, "split": 1}
    assert len(report["candidate_screen_passes"]) == 1
    assert report["candidate_screen_passes"][0]["censored"]
    assert report["candidate_screen_passes"][0]["lifetime"] == 11
