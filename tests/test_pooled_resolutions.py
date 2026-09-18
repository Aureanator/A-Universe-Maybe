"""Pooled (full-gauge) resolution orbits vs rigid counts (referee audit item 1)."""

from __future__ import annotations

import pytest

from constraintnet.resolutions import pooled_resolution_orbits, resolution_space
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
