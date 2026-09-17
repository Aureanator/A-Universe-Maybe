"""Milestone 3 -- internal resolution spaces ``|I(B)|``.

These numbers are the specification's criterion for matter: a boundary whose interior is
uniquely determined is light-like; one admitting several inequivalent interiors carries
hidden state. Everything here is brute force over at most ``|G|^4 = 20736`` assignments, so
the counts are exact rather than sampled.
"""

from __future__ import annotations

import itertools
import random

import pytest

from constraintnet.gauge import gauge_transform
from constraintnet.holonomy import triangle_holonomy
from constraintnet.resolutions import (
    materialise_resolution,
    resolution_space,
    resolution_table,
)
from constraintnet.seeds import make_cone_over_tetrahedron


@pytest.fixture(scope="module")
def cone_a4():
    return make_cone_over_tetrahedron("A4")


@pytest.fixture(scope="module")
def edges_of(cone_a4):
    cx, apex, boundary = cone_a4
    return [tuple(sorted(pair)) for pair in itertools.combinations(boundary, 2)]


class TestConeCombinatorics:
    def test_cone_is_a_four_simplex(self, cone_a4):
        cx, apex, boundary = cone_a4
        assert (len(cx.vertices()), len(cx.edges()), len(cx.faces()), cx.n_tetrahedra()) == (5, 10, 10, 4)
        assert cx.euler_characteristic() == 1

    def test_internal_edges_are_exactly_four(self, cone_a4):
        cx, apex, boundary = cone_a4
        internal = [edge for edge in cx.edges() if apex in edge]
        assert len(internal) == 4

    def test_boundary_is_untouched_by_the_cone_operation(self, cone_a4):
        cx, apex, boundary = cone_a4
        for face in itertools.combinations(boundary, 3):
            assert cx.has_face(face)


class TestLightLikeAndForbidden:
    def test_flat_boundary_without_flux_is_light_like(self, cone_a4):
        cx, apex, boundary = cone_a4
        space = resolution_space(cx, apex, boundary)
        assert space.count_physical == 1
        assert space.kind().startswith("direct")

    def test_raw_count_equals_the_free_apex_gauge(self, cone_a4):
        cx, apex, boundary = cone_a4
        space = resolution_space(cx, apex, boundary)
        group = cx.group
        assert space.count_raw == group.order()  # x_0 free, everything else forced by flatness

    @pytest.mark.parametrize("seed", [0, 1, 2, 3])
    def test_curved_boundary_cannot_be_capped(self, seed):
        """Requiring flat interior faces is consistent iff the boundary itself is flat."""
        cx, apex, boundary = make_cone_over_tetrahedron("A4", seed_labels=seed)
        group = cx.group
        curved = [f for f in cx.faces() if apex not in f and triangle_holonomy(cx, f) != group.identity()]
        space = resolution_space(cx, apex, boundary)
        if curved:
            assert space.count_physical == 0, "curvature must not be cap-able by one interior vertex"
            assert space.kind().startswith("forbidden")


class TestMatterLikeInterior:
    def test_uniform_order_two_flux_admits_six_interiors(self, cone_a4, edges_of):
        cx, apex, boundary = cone_a4
        group = cx.group
        order_two = next(
            cls for cls in group.conjugacy_classes() if group.order_of(sorted(cls, key=repr)[0]) == 2
        )
        space = resolution_space(cx, apex, boundary, {edge: order_two for edge in edges_of})
        assert space.count_raw == 72
        assert space.count_physical == 6
        assert space.kind().startswith("matter-like")

    def test_orbits_are_free(self, cone_a4, edges_of):
        cx, apex, boundary = cone_a4
        group = cx.group
        order_two = next(
            cls for cls in group.conjugacy_classes() if group.order_of(sorted(cls, key=repr)[0]) == 2
        )
        space = resolution_space(cx, apex, boundary, {edge: order_two for edge in edges_of})
        assert space.count_raw == space.count_physical * group.order()

    def test_order_three_flux_cannot_close_uniformly(self, cone_a4, edges_of):
        cx, apex, boundary = cone_a4
        group = cx.group
        for cls in group.conjugacy_classes():
            representative = sorted(cls, key=repr)[0]
            if group.order_of(representative) != 3:
                continue
            space = resolution_space(cx, apex, boundary, {edge: cls for edge in edges_of})
            assert space.count_physical == 0, "three equal order-3 fluxes do not close around a triangle"


class TestFluxCensus:
    def test_census_size_and_histogram(self, cone_a4):
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        table = resolution_table(cx, apex, boundary)
        assert len(table["entries"]) == 103
        physical_values = {info["physical"] for info in table["entries"].values()}
        assert physical_values == {1, 3, 4, 6, 12, 16, 24, 36, 48}

    def test_vacuum_is_the_unique_light_like_pattern(self, cone_a4):
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        table = resolution_table(cx, apex, boundary)
        light_like = [sig for sig, info in table["entries"].items() if info["physical"] == 1]
        assert light_like == [tuple([0] * 6)], "only the all-flat pattern should be light-like"

    def test_raw_counts_are_multiples_of_the_gauge_order(self, cone_a4):
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        group = cx.group
        table = resolution_table(cx, apex, boundary)
        for signature, info in table["entries"].items():
            assert info["raw"] % group.order() == 0 or info["physical"] == 1


class TestAbelianControl:
    def test_Z3_admits_no_hidden_interiors(self):
        cx, apex, boundary = make_cone_over_tetrahedron("Z3")
        table = resolution_table(cx, apex, boundary)
        assert {info["physical"] for info in table["entries"].values()} == {1}


class TestInvariance:
    def test_search_agrees_with_census_on_a_curved_boundary(self):
        """Two independent computations of the same number: the one-pass census and a targeted
        search for a specific flux pattern, on a genuinely curved boundary."""
        cx, apex, boundary = make_cone_over_tetrahedron("A4", seed_labels=5)
        group = cx.group
        classes = list(group.conjugacy_classes())
        edges = [tuple(sorted(pair)) for pair in itertools.combinations(boundary, 2)]

        table = resolution_table(cx, apex, boundary)
        matter = [(sig, info) for sig, info in table["entries"].items() if info["physical"] > 1]
        assert matter, "expected flux patterns with hidden interiors even for a curved boundary"

        signature, info = matter[0]
        flux = {edge: classes[cid] for edge, cid in zip(edges, signature)}
        space = resolution_space(cx, apex, boundary, flux)
        assert space.count_physical == info["physical"]
        assert space.count_raw == info["raw"]

    def test_resolution_count_is_gauge_invariant(self):
        """|I(B)| is computed from conjugacy classes only, so a gauge transformation cannot move it."""
        cx, apex, boundary = make_cone_over_tetrahedron("A4", seed_labels=5)
        group = cx.group
        classes = list(group.conjugacy_classes())
        edges = [tuple(sorted(pair)) for pair in itertools.combinations(boundary, 2)]
        table = resolution_table(cx, apex, boundary)
        signature, info = next(
            (sig, meta) for sig, meta in table["entries"].items() if meta["physical"] > 1
        )
        flux = {edge: classes[cid] for edge, cid in zip(edges, signature)}

        before = resolution_space(cx, apex, boundary, flux)
        rng = random.Random(2)
        gauge_transform(cx, {v: rng.choice(group.elements) for v in cx.vertices()})
        after = resolution_space(cx, apex, boundary, flux)
        assert before.count_physical == after.count_physical == info["physical"]

    def test_materialising_a_resolution_leaves_the_boundary_alone(self):
        # flat external boundary: this is where uniform order-2 flux is realisable
        cx, apex, boundary = make_cone_over_tetrahedron("A4")
        group = cx.group
        edges = [tuple(sorted(pair)) for pair in itertools.combinations(boundary, 2)]
        order_two = next(
            cls for cls in group.conjugacy_classes() if group.order_of(sorted(cls, key=repr)[0]) == 2
        )
        space = resolution_space(cx, apex, boundary, {edge: order_two for edge in edges})
        before = {edge: cx.label(*edge) for edge in edges}

        materialise_resolution(cx, apex, boundary, space.representatives[0])

        after = {edge: cx.label(*edge) for edge in edges}
        assert before == after, "internal resolution must not disturb the external boundary"
        for edge in edges:
            assert group.class_of(triangle_holonomy(cx, (apex, *edge))) == order_two
