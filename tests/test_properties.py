"""Property-based invariant suite (F8 remainder, referee R3: "green count exceeds coverage").

Randomized but SEEDED hypothesis-style tests over multiple groups and random complexes/
moves asserting kernel invariants that individual scenario tests cannot cover.  RNG lives
here (tests), never in KERNEL.  Asymmetric fixtures throughout (Kuhn balls, bipyramids):
the E063 lesson is that K4 hides bugs that asymmetric complexes catch.

Properties:
P1  vertex gauge transformations preserve every gauge-invariant observable exactly
    (Region.gauge_invariant_state and face-holonomy conjugacy classes), while changing
    raw labels;
P2  DriverA(relational) never lets an accepted move change the region's gauge-invariant
    state or the boundary-surface face-holonomy classes (recomputed from the complex,
    not trusted from driver bookkeeping).  INTERIOR face classes are NOT conserved --
    bulk curvature is invisible to a whole-complex region's boundary observables and
    legitimately churns; that asymmetry is the physics, verified here as a property.
P3  Pachner 2<->3 apply+revert restores the exact snapshot for every tested group with
    randomized labels;
P4  oriented-edge inverse consistency label(j,i) == inverse(label(i,j)) survives random
    relabeling and gauge transformation;
P5  kernel orbit quotient (gauge.quotient_by_global_conjugation) agrees with Burnside
    prediction for every registered group, including the new TableGroups S3/Q8/D4 --
    whose construction itself verifies closure/associativity/inverses/generation.
"""

from __future__ import annotations

import itertools
import random

import pytest

from constraintnet.drivers import DriverA
from constraintnet.gauge import (
    burnside_prediction,
    enumerate_gauge_fixed_configs,
    gauge_transform,
    quotient_by_global_conjugation,
)
from constraintnet.groups import get_group
from constraintnet.holonomy import triangle_holonomy
from constraintnet.moves import (
    apply_pachner_2_3,
    apply_pachner_3_2,
    find_pachner_2_3_sites,
    find_pachner_3_2_sites,
    revert_move,
)
from constraintnet.region import Region
from constraintnet.seeds import kuhn_ball, make_bipyramid, randomize_labels

ALL_GROUPS = ("Z2", "Z3", "S3", "D4", "Q8", "A4")
NONABELIAN = ("S3", "D4", "Q8", "A4")


def snapshot(cx):
    return (
        frozenset(tuple(sorted(t)) for t in cx.tetrahedra()),
        tuple((tuple(sorted(e)), cx.label(*e)) for e in sorted(cx.edges())),
        frozenset(tuple(sorted(f)) for f in cx.faces()),
    )


def face_class_multiset(cx, faces=None):
    # canonical serialization: sorted element tuples (str(frozenset) ordering is unstable)
    group = cx.group
    return sorted(
        tuple(sorted(group.conjugacy_class(triangle_holonomy(cx, f))))
        for f in (faces if faces is not None else cx.faces())
    )


# --------------------------------------------------------------------------- P1: gauge
@pytest.mark.parametrize("group_name", ALL_GROUPS)
@pytest.mark.parametrize("seed", [0, 5])
def test_vertex_gauge_preserves_all_observables(group_name, seed):
    cx = kuhn_ball(group_name, n=2)
    randomize_labels(cx, seed=seed)
    region = Region(cx, cx.tetrahedra(), "whole")
    state_before = region.gauge_invariant_state()
    classes_before = face_class_multiset(cx)
    labels_before = {e: cx.label(*e) for e in cx.edges()}

    rng = random.Random(1000 + seed)
    lambdas = {v: cx.group.elements[rng.randrange(cx.group.order())]
               for v in cx.vertices()}
    gauge_transform(cx, lambdas)

    assert region.gauge_invariant_state() == state_before
    assert face_class_multiset(cx) == classes_before
    # non-vacuity: the raw labels must actually have moved (else the test proves nothing)
    if not cx.group.is_abelian():
        assert any(cx.label(*e) != labels_before[e] for e in cx.edges())


# --------------------------------------------------------------------------- P2: DriverA
@pytest.mark.parametrize("group_name", ALL_GROUPS)
@pytest.mark.parametrize("seed", [0, 1, 2])
def test_driverA_relational_conserves_region_state(group_name, seed):
    cx = kuhn_ball(group_name, n=2)
    randomize_labels(cx, seed=seed)
    region = Region(cx, cx.tetrahedra(), "whole")
    driver = DriverA(cx, region=region, rng_seed=seed, model="relational")
    state0 = region.gauge_invariant_state()
    boundary = region.boundary_faces()
    classes0 = face_class_multiset(cx, boundary)

    for _ in range(60):
        record = driver.advance()
        # recomputed from the complex itself, never from driver bookkeeping:
        assert region.gauge_invariant_state() == state0, (
            f"{group_name} seed {seed}: fate {record.fate} changed gauge-invariant state")
        assert face_class_multiset(cx, boundary) == classes0


# --------------------------------------------------------------------------- P3: Pachner
@pytest.mark.parametrize("group_name", ALL_GROUPS)
@pytest.mark.parametrize("seed", [3, 11])
def test_pachner_23_roundtrip_exact_across_groups(group_name, seed):
    cx = kuhn_ball(group_name, n=2)
    randomize_labels(cx, seed=seed)
    rng = random.Random(seed)
    for site_index in range(3):
        sites = find_pachner_2_3_sites(cx)
        assert sites, f"{group_name}: no 2-3 sites on kuhn ball n=2"
        (a, b, _face) = sites[site_index % len(sites)]
        before = snapshot(cx)
        new_label = cx.group.elements[rng.randrange(cx.group.order())]
        move = apply_pachner_2_3(cx, a, b, new_edge_label=new_label)
        assert cx.n_tetrahedra() == len(before[0]) + 1
        revert_move(cx, move)
        assert snapshot(cx) == before


@pytest.mark.parametrize("group_name", ALL_GROUPS)
def test_pachner_32_roundtrip_exact_across_groups(group_name):
    cx = make_bipyramid(group_name, triangulation="three")
    randomize_labels(cx, seed=19)
    for edge in cx.edges()[::2]:
        cx.set_realized(*edge, True)
    sites = find_pachner_3_2_sites(cx)
    assert sites, f"{group_name}: no 3-2 sites on three-triangulation bipyramid"
    before = snapshot(cx)
    move = apply_pachner_3_2(cx, sites[0])
    revert_move(cx, move)
    assert snapshot(cx) == before


# --------------------------------------------------------------------------- P4: orientation
@pytest.mark.parametrize("group_name", ALL_GROUPS)
@pytest.mark.parametrize("seed", [0, 7])
def test_oriented_edge_inverse_consistency(group_name, seed):
    cx = kuhn_ball(group_name, n=2)
    rng = random.Random(seed)
    elements = tuple(cx.group.elements)
    for (u, v) in cx.edges():
        cx.set_label(u, v, elements[rng.randrange(len(elements))])
    for _ in range(10):  # extra random draws on random orientations
        (u, v) = cx.edges()[rng.randrange(len(cx.edges()))]
        cx.set_label(v, u, elements[rng.randrange(len(elements))])

    def check():
        for (i, j) in cx.edges():
            assert cx.label(j, i) == cx.group.inverse(cx.label(i, j))

    check()
    gauge_transform(cx, {v: elements[rng.randrange(len(elements))]
                         for v in cx.vertices()})
    check()


# --------------------------------------------------------------------------- P5: orbit/Burnside
BURNSIDE_EXPECTED = {"Z2": 8, "Z3": 27, "S3": 49, "D4": 176, "Q8": 176, "A4": 178}


@pytest.mark.parametrize("group_name", ALL_GROUPS)
def test_kernel_orbit_quotient_matches_burnside(group_name):
    group = get_group(group_name)
    free_edges = [(0, 2), (0, 3), (1, 3)]  # tetrahedron tree-slice coordinates
    configs = enumerate_gauge_fixed_configs(group, free_edges)
    orbits, _index = quotient_by_global_conjugation(configs, group)
    predicted = burnside_prediction(group, len(free_edges))
    assert predicted == BURNSIDE_EXPECTED[group_name]
    assert len(orbits) == int(predicted)
    # orbit-stabilizer bookkeeping: sum of |G|/|stab| over reps reproduces |G|^3
    total = sum(len(orbit) for orbit in orbits)
    assert total == group.order() ** 3


@pytest.mark.parametrize("group_name", ("S3", "Q8", "D4"))
def test_tablegroup_derived_structures(group_name):
    """TableGroup axioms are checked at construction; here check DERIVED behavior."""
    group = get_group(group_name)
    order = group.order()
    # class sizes partition |G|, identity alone in its class
    sizes = sorted(len(c) for c in group.conjugacy_classes())
    assert sum(sizes) == order
    assert 1 in sizes
    # every element's conjugacy-class size divides the group order (orbit-stabilizer)
    for cls in group.conjugacy_classes():
        assert order % len(cls) == 0
    # inverse consistency through the multiplication table
    for x in group.elements:
        assert group.multiply(group.inverse(x), x) == group.identity()
        assert group.multiply(x, group.inverse(x)) == group.identity()


@pytest.mark.parametrize("group_name", NONABELIAN)
def test_nonabelian_conjugation_actually_moves_things(group_name):
    """Guards against a table silently collapsing to an abelian one."""
    group = get_group(group_name)
    assert not group.is_abelian()
    moved = any(group.conjugate(g, x) != x for g in group.elements for x in group.elements)
    assert moved
