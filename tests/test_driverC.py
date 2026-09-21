"""DriverC free-space tests: relational acceptance over label moves UNION relinking.

Pins, for whole-complex regions (v1 scope):
T1  purely-interior Pachner proposals are NEVER vetoed (boundary observables cannot
    see interior relinking -- if this ever fails, the observation depends on bulk
    triangulation and that is a headline finding, not a flaky test);
T2  mixed runs freeze the boundary sphere labels and the canonical state exactly, keep
    Euler characteristic V-E+F-T == 1 (Pachner preserves ball topology), and never
    leave degenerate tets;
T3  NO TELEPORTATION: surviving faces keep their holonomy under relinking -- the curved
    face set can only change on faces added/removed by the move itself, or faces
    containing the edge whose label changed. Curvature cannot jump elsewhere;
T4  record provenance (driver="C", model="freepach-v1") and ontology declarations.
"""

from __future__ import annotations

import itertools

import pytest

from constraintnet.drivers import DriverC
from constraintnet.holonomy import triangle_holonomy
from constraintnet.region import Region
from constraintnet.seeds import kuhn_ball, randomize_labels


def curved_faces(cx):
    ident = cx.group.identity()
    return {tuple(sorted(f)): triangle_holonomy(cx, f) != ident for f in cx.faces()}


def curved_set(cx):
    return {f for f, c in curved_faces(cx).items() if c}


def euler(cx):
    return len(cx.vertices()) - len(cx.edges()) + cx.n_faces() - cx.n_tetrahedra()


def surface_state(cx):
    region = Region(cx, cx.tetrahedra(), "whole")
    labels = {(tuple(sorted(e)), cx.label(*e)) for e in region.boundary_surface_edges()}
    return frozenset(labels)


# --------------------------------------------------------------------------- T1
@pytest.mark.parametrize("group_name", ["Z2", "A4"])
def test_interior_relinkings_never_vetoed(group_name):
    cx = kuhn_ball(group_name, n=2)
    randomize_labels(cx, seed=3)
    driver = DriverC(cx, rng_seed=1, pachner_share=1.0)  # force relinking proposals
    vetoes = accepted_pachner = 0
    for _ in range(80):
        record = driver.advance()
        if driver.last_kind == "label":
            continue  # fell through: no legal site right now
        if record.fate == "vetoed":
            vetoes += 1
        else:
            accepted_pachner += 1
    assert vetoes == 0, "interior relinking vetoed: observation sees bulk triangulation"
    assert accepted_pachner > 20, f"suspiciously few relinkings ({accepted_pachner})"


# --------------------------------------------------------------------------- T2
@pytest.mark.parametrize("group_name", ["Z3", "Q8", "A4"])
def test_mixed_run_freezes_boundary_and_preserves_topology(group_name):
    cx = kuhn_ball(group_name, n=3)
    randomize_labels(cx, seed=11)
    driver = DriverC(cx, rng_seed=7, pachner_share=0.5)
    state0 = driver._observe()
    surf0 = surface_state(cx)
    for step in range(150):
        driver.advance()
        assert driver._observe() == state0, f"canonical state drift at step {step}"
        assert surface_state(cx) == surf0, f"boundary sphere moved at step {step}"
        assert euler(cx) == 1, f"Euler characteristic broken at step {step}"
        for tet in cx.tetrahedra():
            assert len(set(tet)) == 4, f"degenerate tet {tet} at step {step}"


# --------------------------------------------------------------------------- T3
def test_no_teleportation_under_relinking():
    """Surviving faces keep holonomy under relinking; label moves only touch their edge."""
    cx = kuhn_ball("A4", n=2)
    randomize_labels(cx, seed=5)
    driver = DriverC(cx, rng_seed=9, pachner_share=0.7)
    prev = curved_set(cx)
    checked_relink_steps = 0
    for step in range(120):
        edges_before = {tuple(sorted(e)): cx.label(*e) for e in cx.edges()}
        faces_before = {tuple(sorted(f)) for f in cx.faces()}
        kind = None
        # replicate the driver's own proposal by stepping it and reading last_kind AFTER;
        # to know the move BEFORE classification we recompute diffs, which is what matters.
        record = driver.advance()
        kind = driver.last_kind
        now_faces = {tuple(sorted(f)) for f in cx.faces()}
        now = curved_set(cx)
        added = now_faces - faces_before
        removed = faces_before - now_faces
        diff = prev ^ now
        if record.fate == "vetoed":
            assert diff == set(), f"veto left curvature trace at step {step}"
            assert now_faces == faces_before, f"veto changed face set at step {step}"
        elif kind == "label":
            moved = [e for e in edges_before
                     if cx.has_edge(*e) and cx.label(*e) != edges_before[e]]
            assert len(moved) == 1, f"label move touched {len(moved)} edges at step {step}"
            changed_edge = tuple(sorted(moved[0]))
            for f in diff:  # only faces containing the changed edge may change curvature
                assert changed_edge in [tuple(sorted(p))
                                        for p in itertools.combinations(f, 2)], (
                    f"curvature teleported on label move at step {step}: face {f}")
        else:
            checked_relink_steps += 1
            for f in diff:
                assert f in added or f in removed, (
                    f"surviving face {f} changed curvature under {kind} at step {step}: "
                    "relinking must preserve holonomy of surviving faces")
        prev = now
    assert checked_relink_steps > 10, "too few relinkings exercised"


# --------------------------------------------------------------------------- T4
def test_record_provenance_and_ontology():
    cx = kuhn_ball("A4", n=2)
    driver = DriverC(cx, rng_seed=0)
    record = driver.advance()
    assert record.driver == "C"
    assert record.model == "freepach-v1"
    assert record.fate in {"accepted", "vetoed"}
    assert driver.event_ontology() == "counterfactual-veto"
    assert driver.reversible() is False


def test_pachner_share_bounds_validated():
    cx = kuhn_ball("A4", n=2)
    with pytest.raises(ValueError):
        DriverC(cx, pachner_share=1.5)
