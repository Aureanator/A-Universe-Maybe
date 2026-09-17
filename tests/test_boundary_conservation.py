"""Test 4 -- boundary conservation, plus superselection of sectors.

Specification: "No accepted move may change the boundary holonomy conjugacy class."

We test it two ways: directly (before/after appearance comparison around every attempt)
and statistically (run thousands of moves and assert the watched region's signature never
moves).  The second form is the one that would catch a subtle leak.
"""

from __future__ import annotations

import random

import pytest

from constraintnet.dynamics import Simulation
from constraintnet.holonomy import loop_holonomy, triangle_holonomy
from constraintnet.moves import propose_edge_move
from constraintnet.region import Region
from constraintnet.seeds import kuhn_ball, make_single_tetrahedron, randomize_labels


def test_no_accepted_move_changes_boundary_observables(ball_a4):
    cx = ball_a4
    region = Region(cx, cx.tetrahedra(), "ball")
    sim = Simulation(cx, region=region, rng=random.Random(3))

    for _ in range(600):
        before = region.appearance()
        record = sim.attempt()
        after = region.appearance()
        if record.accepted:
            assert before == after
        else:
            # a rejected move must leave the complex exactly as it was
            assert before == after


def test_sector_signature_is_constant_over_a_long_run(ball_a4):
    cx = ball_a4
    region = Region(cx, cx.tetrahedra(), "ball")
    sim = Simulation(cx, region=region, rng=random.Random(11))
    sector = region.appearance().signature()
    charges = {loop: loop_holonomy(cx, loop) for loop in region.probe_cycles()}

    stats = sim.run(3000)
    assert stats.proposals == 3000
    assert region.appearance().signature() == sector, "the system drifted out of its sector"

    group = cx.group
    for loop, value in charges.items():
        assert group.class_of(loop_holonomy(cx, loop)) == group.class_of(value)


def test_interior_moves_are_accepted_and_boundary_ones_are_not(ball_z3):
    """Interior relabellings cannot be seen outside; boundary ones generically can.

    This is the mechanism that makes conservation non-vacuous: the rejection filter bites
    exactly on edges an outside observer's probe loops traverse.
    """
    cx = ball_z3
    region = Region(cx, cx.tetrahedra(), "ball")
    interior = set(region.interior_edges())
    boundary = set(region.boundary_surface_edges())

    sim_in = Simulation(
        cx, region=region, rng=random.Random(5),
        move_generator=lambda c, r: propose_edge_move(c, r, edges=sorted(interior)),
    )
    stats_in = sim_in.run(400)
    assert stats_in.accept_rate == 1.0, "interior moves must always preserve external appearance"

    sim_out = Simulation(
        cx, region=region, rng=random.Random(6),
        move_generator=lambda c, r: propose_edge_move(c, r, edges=sorted(boundary)),
    )
    stats_out = sim_out.run(400)
    assert stats_out.accept_rate < 1.0, "boundary moves were never rejected -- filter is broken"


def test_rejected_moves_leave_labels_untouched(ball_a4):
    cx = ball_a4
    region = Region(cx, cx.tetrahedra(), "ball")
    sim = Simulation(cx, region=region, rng=random.Random(8))
    for _ in range(200):
        snapshot = dict(cx._labels)  # noqa: SLF001
        record = sim.attempt()
        if not record.accepted:
            assert dict(cx._labels) == snapshot  # noqa: SLF001


def test_probe_regions_pin_a_subregion(ball_z3):
    """Watching a smaller region is stricter than watching the whole complex."""
    cx = ball_z3
    tets = sorted(cx.tetrahedra())
    inner = Region(cx, tets[:2], "inner-pair")
    outer = Region(cx, cx.tetrahedra(), "ball")

    loose = Simulation(cx, region=outer, rng=random.Random(13))
    strict = Simulation(cx, region=outer, probe_regions=[inner], rng=random.Random(13))

    loose_stats = loose.run(500)
    strict_stats = strict.run(500)
    assert strict_stats.accept_rate <= loose_stats.accept_rate
    inner_signature = inner.appearance().signature()
    for _ in range(200):
        strict.attempt()
    assert inner.appearance().signature() == inner_signature
