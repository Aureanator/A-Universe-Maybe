"""Combinatorial integrity of the simplicial complex.

These are not in the specification's list of seven tests, but they guard the two
invariants that everything else silently depends on:

* the reverse-orientation rule ``A_ji = A_ij^{-1}`` cannot drift out of sync;
* tetrahedron orientations cancel interior faces -- without it "boundary" is nonsense.
"""

from __future__ import annotations

import pytest

from constraintnet.complex import (
    SimplicialComplex,
    SimplicialError,
    face_induced_signs,
    reverse_orientation,
)
from constraintnet.region import NonManifoldBoundary, Region
from constraintnet.seeds import (
    kuhn_ball,
    make_bipyramid,
    make_single_tetrahedron,
    make_tetrahedron_boundary,
    randomize_labels,
    stacked_ball,
)


class TestOrientationRule:
    def test_reverse_orientation_is_inverse_by_construction(self, a4):
        cx = make_tetrahedron_boundary("A4")
        randomize_labels(cx, seed=1)
        for (u, v) in cx.edges():
            assert cx.label(v, u) == a4.inverse(cx.label(u, v))

    def test_setting_label_from_either_side_stays_consistent(self, a4):
        cx = make_tetrahedron_boundary("A4")
        element = (1, 2, 0, 3)
        cx.set_label(0, 2, element)
        assert cx.label(0, 2) == element
        assert cx.label(2, 0) == a4.inverse(element)
        cx.set_label(2, 0, element)  # set from the reverse direction
        assert cx.label(2, 0) == element
        assert cx.label(0, 2) == a4.inverse(element)

    def test_non_group_label_rejected(self):
        cx = make_tetrahedron_boundary("Z3")
        with pytest.raises(SimplicialError):
            cx.set_label(0, 1, 7)


class TestDegeneracy:
    @pytest.mark.parametrize("edge", [(1, 1), (5, 5)])
    def test_degenerate_edge_rejected(self, edge):
        cx = SimplicialComplex("Z3")
        with pytest.raises(SimplicialError):
            cx.add_edge(*edge)

    def test_degenerate_face_and_tetra_rejected(self):
        cx = SimplicialComplex("Z3")
        with pytest.raises(SimplicialError):
            cx.add_face((0, 1, 1))
        with pytest.raises(SimplicialError):
            cx.add_tetra((0, 1, 2, 2))

    def test_subsimplices_are_created_automatically(self):
        cx = SimplicialComplex("Z3")
        cx.add_tetra((0, 1, 2, 3))
        assert len(cx.faces()) == 4
        assert len(cx.edges()) == 6
        assert len(cx.vertices()) == 4
        cx.validate()


class TestOrientationCancellation:
    def test_kuhn_ball_without_orienting_is_not_a_manifold(self):
        """Forgetting tetrahedron orientations makes interior faces fail to cancel."""
        cx = kuhn_ball("Z3", n=1)
        for key in list(cx._tets):  # noqa: SLF001 - deliberately corrupting state
            cx.set_tet_order(key, tuple(sorted(key)))
        region = Region(cx, cx.tetrahedra(), "unoriented ball")
        with pytest.raises(NonManifoldBoundary):
            region.boundary_faces_signed()

    def test_oriented_kuhn_ball_has_a_closed_boundary(self):
        for n in (1, 2):
            cx = kuhn_ball("Z3", n=n)
            region = Region(cx, cx.tetrahedra(), f"ball{n}")
            assert region.is_closed_boundary()

    def test_kuhn_ball_boundary_is_a_sphere_by_euler_characteristic(self):
        """Boundary of a 3-ball must be a 2-sphere: V - E + F = 2."""
        cx = kuhn_ball("Z3", n=1)
        region = Region(cx, cx.tetrahedra(), "ball")
        faces = region.boundary_faces()
        edges = region.boundary_surface_edges()
        vertices = {v for face in faces for v in face}
        assert len(vertices) - len(edges) + len(faces) == 2

    def test_flipping_one_tetrahedron_breaks_cancellation(self):
        cx = kuhn_ball("Z3", n=1)
        tet = sorted(cx.tetrahedra())[0]
        order = list(cx.tet_order(tet))
        order[2], order[3] = order[3], order[2]
        cx.set_tet_order(tet, tuple(order))
        with pytest.raises(NonManifoldBoundary):
            Region(cx, cx.tetrahedra(), "broken").boundary_faces_signed()

    def test_face_induced_signs_flip_with_parity(self):
        base = (0, 1, 2, 3)
        flipped = (1, 0, 2, 3)
        signs_a = face_induced_signs(base)
        signs_b = face_induced_signs(flipped)
        for face in signs_a:
            assert signs_b[face] == -signs_a[face]

    def test_reverse_orientation_helper(self):
        # parity relative to sorted order; a 3-cycle is even, so (2,0,1) is not reversed
        assert reverse_orientation((0, 1, 2)) is False
        assert reverse_orientation((0, 2, 1)) is True
        assert reverse_orientation((2, 0, 1)) is False
        assert reverse_orientation((1, 0, 2)) is True


class TestSeeds:
    def test_tetrahedron_boundary_counts(self):
        cx = make_tetrahedron_boundary("A4")
        assert (len(cx.vertices()), len(cx.edges()), len(cx.faces()), cx.n_tetrahedra()) == (4, 6, 4, 0)
        assert cx.euler_characteristic() == 2  # a 2-sphere

    def test_bipyramid_sides_match(self):
        two = make_bipyramid("A4", "two")
        three = make_bipyramid("A4", "three")
        assert sorted(two.boundary_faces()) == sorted(three.boundary_faces())
        assert two.euler_characteristic() == three.euler_characteristic() == 1

    def test_stacked_ball_is_a_ball(self):
        cx = stacked_ball("Z3", tetrahedra=9)
        region = Region(cx, cx.tetrahedra(), "stack")
        assert region.is_closed_boundary()
        faces = region.boundary_faces()
        edges = region.boundary_surface_edges()
        vertices = {v for face in faces for v in face}
        assert len(vertices) - len(edges) + len(faces) == 2

    def test_copy_is_independent(self, ball_a4):
        group = ball_a4.group
        edge = ball_a4.edges()[0]
        clone = ball_a4.copy()
        original_value = ball_a4.label(*edge)
        other = next(g for g in group.elements if g != original_value)
        clone.set_label(*edge, other)
        assert clone.label(*edge) == other
        assert ball_a4.label(*edge) == original_value, "copy shares mutable state with original"
        assert clone.tet_order(ball_a4.tetrahedra()[0]) == ball_a4.tet_order(ball_a4.tetrahedra()[0])
