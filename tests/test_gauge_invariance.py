"""Test 2 -- gauge invariance.

Specification: "Apply a gauge transformation. Edge labels change, but face holonomy
conjugacy classes must not change."

We strengthen it: loop (charge) holonomy conjugacy classes and the whole region
:class:`~constraintnet.region.Appearance` must also be invariant, while raw edge
labels must genuinely move -- otherwise the test would pass vacuously.
"""

from __future__ import annotations

import random

import pytest

from constraintnet.gauge import gauge_fix_spanning_tree, gauge_transform
from constraintnet.holonomy import loop_holonomy, triangle_holonomy
from constraintnet.seeds import TETRA_TREE, make_bipyramid, randomize_labels


def _random_gauge_map(cx, group, seed):
    rng = random.Random(seed)
    return {v: rng.choice(group.elements) for v in cx.vertices()}


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_face_holonomy_classes_survive_gauge_transform(tetra_boundary, a4, seed):
    cx = tetra_boundary
    before = {f: triangle_holonomy(cx, f) for f in cx.faces()}
    labels_before = dict(cx._labels)  # noqa: SLF001

    gauge_transform(cx, _random_gauge_map(cx, a4, seed))

    after = {f: triangle_holonomy(cx, f) for f in cx.faces()}
    for face in before:
        assert a4.class_of(before[face]) == a4.class_of(after[face]), face


def test_edge_labels_really_change(tetra_boundary, a4):
    cx = tetra_boundary
    before = dict(cx._labels)  # noqa: SLF001
    gauge_transform(cx, _random_gauge_map(cx, a4, 99))
    changed = [k for k in before if cx._labels[k] != before[k]]  # noqa: SLF001
    assert changed, "gauge transformation did nothing -- test would be vacuous"


def test_loop_charges_and_appearance_are_invariant(ball_a4, ball_region_a4, a4):
    region = ball_region_a4
    appearance_before = region.appearance()
    loops = region.probe_cycles()
    charges_before = {loop: loop_holonomy(ball_a4, loop) for loop in loops}

    gauge_transform(ball_a4, _random_gauge_map(ball_a4, a4, 202))

    appearance_after = region.appearance()
    assert appearance_before.face_curvatures == appearance_after.face_curvatures
    assert appearance_before.cycle_charges == appearance_after.cycle_charges
    for loop in loops:
        after = loop_holonomy(ball_a4, loop)
        assert a4.class_of(charges_before[loop]) == a4.class_of(after)


def test_gauge_fixing_trivialises_the_spanning_tree(tetra_boundary, a4):
    cx = tetra_boundary
    before = {f: triangle_holonomy(cx, f) for f in cx.faces()}
    gauge_fix_spanning_tree(cx, tree=TETRA_TREE, root=0)
    e = a4.identity()
    assert all(cx.label(u, v) == e for (u, v) in TETRA_TREE), "tree edges must be pure gauge"
    after = {f: triangle_holonomy(cx, f) for f in cx.faces()}
    for face in before:
        assert a4.class_of(before[face]) == a4.class_of(after[face])


def test_residual_freedom_is_only_global_conjugation(tetra_boundary, a4):
    """After tree fixing, any gauge map keeping the tree fixed is a global conjugation."""
    cx = tetra_boundary
    gauge_fix_spanning_tree(cx, tree=TETRA_TREE, root=0)
    e = a4.identity()

    # applying a vertex-dependent gauge map and re-fixing must land on a global conjugate
    labels_before = dict(cx._labels)  # noqa: SLF001
    gauge_transform(cx, _random_gauge_map(cx, a4, 5))
    gauge_fix_spanning_tree(cx, tree=TETRA_TREE, root=0)

    free_edges = [(0, 2), (0, 3), (1, 3)]
    before_cfg = tuple(labels_before[edge] for edge in free_edges)
    after_cfg = tuple(cx._labels[edge] for edge in free_edges)  # noqa: SLF001
    related = any(
        tuple(a4.conjugate(lam, x) for x in before_cfg) == after_cfg for lam in a4.elements
    )
    assert related, "residual gauge freedom was more than global conjugation"


def test_pachner_pair_shares_boundary_observables_after_matching_labels(a4):
    """The two triangulations of the bipyramid have identical boundary combinatorics."""
    two = make_bipyramid("A4", "two")
    three = make_bipyramid("A4", "three")
    randomize_labels(two, seed=4)
    # copy every shared edge label across: both share the same 9 edges minus edge (3,4)
    for key in two.edges():
        if three.has_edge(*key):
            three.set_label(*key, two.label(*key))
    from constraintnet.region import Region

    r_two = Region(two, two.tetrahedra(), "two")
    r_three = Region(three, three.tetrahedra(), "three")
    assert sorted(r_two.boundary_faces()) == sorted(r_three.boundary_faces())
    # boundary face curvatures agree wherever both sides have the same triangle
    curv_two = {f: triangle_holonomy(two, f) for f in r_two.boundary_faces()}
    curv_three = {f: triangle_holonomy(three, f) for f in r_three.boundary_faces()}
    assert set(curv_two) == set(curv_three)
    for face in curv_two:
        assert a4.class_of(curv_two[face]) == a4.class_of(curv_three[face])
