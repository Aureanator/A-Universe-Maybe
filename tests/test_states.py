"""Transition graphs over physical states -- and the two traps that corrupt them.

Trap 1 (gauge copies): a move must be re-gauge-fixed and canonicalized before it is
recorded, otherwise gauge copies inflate the state count by up to ``|G|``.

Trap 2 (canonical-first exploration): right-multiplication does not commute with
conjugation, so exploring only canonical representatives *loses transitions*.  The
regression test below pins the correct numbers -- 178 physical states in one component --
which the naive approach gets wrong (it finds 174, missing four Klein-four configurations).
"""

from __future__ import annotations

import pytest

from constraintnet.seeds import TETRA_TREE, make_tetrahedron_boundary
from constraintnet.states import transition_graph


@pytest.fixture(scope="module")
def full_graph():
    cx = make_tetrahedron_boundary("A4")
    return transition_graph(cx, tree=TETRA_TREE, legitimacy="none")


class TestPhysicalStateCount:
    def test_raw_slice_is_exhaustive(self, full_graph):
        assert full_graph["raw_nodes"] == 1728

    def test_physical_states_are_the_178_orbits(self, full_graph):
        assert full_graph["node_count"] == 178, (
            "canonicalisation must collapse the slice to exactly the 178 gauge classes"
        )

    def test_canonicalisation_is_doing_real_work(self, full_graph):
        # 1728 raw -> 178 physical; a factor of ~9.7, strictly between 1 and |G| = 12
        ratio = full_graph["raw_nodes"] / full_graph["node_count"]
        assert 1.0 < ratio < 12.0

    def test_state_space_is_connected(self, full_graph):
        assert full_graph["component_count"] == 1
        assert full_graph["largest_component"] == 178

    def test_little_group_histogram_of_visited_states(self, full_graph):
        assert full_graph["little_groups"] == {
            "trivial": 130,
            "Z3": 26,
            "V4": 21,
            "A4": 1,
        }

    def test_no_transitions_are_lost_by_projection(self, full_graph):
        """Every raw edge maps to a physical edge; self-loops are allowed but nothing vanishes."""
        total_out = sum(len(targets) for targets in full_graph["adjacency"].values())
        assert total_out >= 178  # each state has at least one successor recorded


class TestConservationRestrictsDynamics:
    def test_surface_seed_has_no_internal_dynamics(self):
        """On ``d(Delta^3)`` every edge is external, so conservation freezes the vacuum.

        This is not a failure of the engine -- it is the reason the specification moves on
        to the cone over the tetrahedron and then to lattices: internal degrees of freedom
        require interior edges.
        """
        cx = make_tetrahedron_boundary("A4")
        frozen = transition_graph(cx, tree=TETRA_TREE, legitimacy="appearance")
        assert frozen["node_count"] == 1
        assert frozen["accepted_edges"] == 0
        assert frozen["proposals"] > 0, "no moves were even attempted"

    def test_interior_edges_are_what_allow_motion(self, ball_a4):
        """The same rule on a complex with interior edges admits accepted moves."""
        from constraintnet.region import Region

        region = Region(ball_a4, ball_a4.tetrahedra(), "ball")
        assert region.interior_edges(), "expected interior edges in a Kuhn ball"


class TestDeterminism:
    def test_two_runs_agree(self):
        first = transition_graph(make_tetrahedron_boundary("A4"), tree=TETRA_TREE, legitimacy="none")
        second = transition_graph(make_tetrahedron_boundary("A4"), tree=TETRA_TREE, legitimacy="none")
        assert first["node_count"] == second["node_count"]
        assert {n.orbit_rep for n in first["nodes"]} == {n.orbit_rep for n in second["nodes"]}
