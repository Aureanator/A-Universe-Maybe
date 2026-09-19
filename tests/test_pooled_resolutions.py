"""Pooled (full-gauge) resolution orbits vs rigid counts (referee audit item 1)."""

from __future__ import annotations

import pytest

from constraintnet.resolutions import (
    pointwise_stabilizer,
    pooled_resolution_orbits,
    resolution_space,
    within_fibre_resolution_orbits,
)
from constraintnet.seeds import make_cone_over_tetrahedron


def _v4_class(group):
    return next(c for c in group.conjugacy_classes() if {group.order_of(x) for x in c} == {2})


class TestPooledOrbits:
    def test_flat_declaration_pools_to_one(self):
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        assert pooled_resolution_orbits(cx, apex, boundary) == 1

    @pytest.mark.slow
    def test_klein_four_star_rigid_three_pools_to_one(self):
        """Star declaration: raw 36 -> rigid 3 -> pooled 1."""
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        group = cx.group
        v4 = _v4_class(group)
        flux = {e: v4 for e in [(0, 1), (0, 2), (0, 3)]}
        rigid = resolution_space(cx, apex, boundary, flux_classes=flux)
        assert rigid.count_raw == 36 and rigid.count_physical == 3
        assert pooled_resolution_orbits(cx, apex, boundary, flux_classes=flux) == 1

    @pytest.mark.slow
    def test_referee_exact_six_to_two(self):
        """The referee's exact numbers on the 5-flux-face declaration: rigid 6 -> pooled 2."""
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        group = cx.group
        v4 = _v4_class(group)
        flux = {e: v4 for e in [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)]}
        rigid = resolution_space(cx, apex, boundary, flux_classes=flux)
        assert rigid.count_raw == 72 and rigid.count_physical == 6
        assert pooled_resolution_orbits(cx, apex, boundary, flux_classes=flux) == 2

    def test_budget_guard(self):
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        with pytest.raises(ValueError):
            pooled_resolution_orbits(cx, apex, boundary, budget=10)


class TestWithinFibreStabilizer:
    """R3 finding F1: the mechanism sentence made executable. The old justification claimed
    merging happens 'never within a fixed fibre' -- this class fails CI by proving WHERE it
    actually happens (inside, via the pointwise stabilizer of symmetric boundaries)."""

    def test_flat_boundary_stabilizer_is_12_constants(self):
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        stab = pointwise_stabilizer(cx.group, boundary, lambda i, j: cx.label(i, j))
        assert len(stab) == 12
        assert all(len(set(t)) == 1 for t in stab), "flat-B stabilizer must be exactly the constants"

    def test_five_face_collapse_inside_the_fibre(self):
        """raw 72 -> apex-only rigid 6 -> within-fibre 2, at ONE fixed boundary."""
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        v4 = _v4_class(cx.group)
        flux = {e: v4 for e in [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)]}
        rs = resolution_space(cx, apex, boundary, flux_classes=flux)
        assert (rs.count_raw, rs.count_physical) == (72, 6)
        assert within_fibre_resolution_orbits(cx, apex, boundary, flux_classes=flux) == 2

    def test_star_three_within_fibre(self):
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        v4 = _v4_class(cx.group)
        flux = {e: v4 for e in [(0, 1), (0, 2), (0, 3)]}
        assert within_fibre_resolution_orbits(cx, apex, boundary, flux_classes=flux) == 1

    def test_asymmetric_boundary_stabilizer_trivial(self):
        """Generic B: pointwise stabilizer collapses to identity; within-fibre == rigid."""
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        g = cx.group
        threes = [x for x in g.elements if g.order_of(x) == 3]
        cx.set_label(0, 1, threes[0])
        cx.set_label(0, 2, threes[1])
        cx.set_label(0, 3, threes[2])
        stab = pointwise_stabilizer(g, boundary, lambda i, j: cx.label(i, j))
        ident = g.identity()
        assert all(t == (ident,) * len(boundary) for t in stab), f"expected trivial stabilizer, got {len(stab)}"
