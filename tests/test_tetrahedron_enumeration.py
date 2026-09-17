"""Test 3 -- tetrahedron enumeration (the milestone-1 benchmark).

Specification: "For ``A_4``, gauge fixing a spanning tree must produce 1728 raw
configurations. Quotienting by residual global conjugation must produce 178 classes."

The number is reproduced by brute force *and* independently predicted from the
centralizer sizes via Burnside's lemma, so agreement is not an accident of one
implementation matching another.
"""

from __future__ import annotations

import itertools

import pytest

from constraintnet.gauge import (
    burnside_prediction,
    canonical_config,
    enumerate_gauge_fixed_configs,
    global_conjugate_config,
    orbit_of_config,
    quotient_by_global_conjugation,
    tetrahedron_moduli,
)
from constraintnet.holonomy import triangle_holonomy
from constraintnet.seeds import TETRA_FREE_EDGES, make_tetrahedron_boundary


def test_raw_gauge_fixed_count_is_1728(a4):
    configs = enumerate_gauge_fixed_configs(a4, TETRA_FREE_EDGES)
    assert len(configs) == 12 ** 3 == 1728
    assert len(set(configs)) == 1728


def test_classes_after_global_conjugation_are_178(a4):
    result = tetrahedron_moduli(a4)
    assert result["raw_count"] == 1728
    assert result["class_count"] == 178, (
        f"expected the known benchmark 178 gauge-inequivalent classes, "
        f"got {result['class_count']}"
    )


def test_burnside_predicts_the_same_number(a4):
    predicted = burnside_prediction(a4, n_free_edges=3)
    assert predicted == pytest.approx(178.0)
    # closed form: (12^3 + 3*4^3 + 8*3^3)/12
    assert (12 ** 3 + 3 * 4 ** 3 + 8 * 3 ** 3) / 12 == pytest.approx(178.0)


def test_orbits_partition_the_raw_configurations(a4):
    result = tetrahedron_moduli(a4)
    total = sum(len(orbit) for orbit in result["orbits"])
    assert total == 1728
    seen = set()
    for orbit in result["orbits"]:
        assert not (seen & set(orbit))
        seen |= set(orbit)


def test_orbit_sizes_are_divisors_consistent_with_centralizers(a4):
    """|orbit| must equal 12 / |stabiliser|, hence a divisor of 12."""
    result = tetrahedron_moduli(a4)
    for orbit in result["orbits"]:
        size = len(orbit)
        assert 12 % size == 0


def test_canonical_representative_is_constant_on_an_orbit(a4):
    configs = enumerate_gauge_fixed_configs(a4, TETRA_FREE_EDGES)
    for config in configs[:200]:
        rep = canonical_config(config, a4)
        for member in orbit_of_config(config, a4):
            assert canonical_config(member, a4) == rep


def test_abelian_group_has_trivial_quotient(z3):
    """For an abelian group conjugation does nothing: 27 configs, 27 classes."""
    result = tetrahedron_moduli(z3)
    assert result["raw_count"] == 27
    assert result["class_count"] == 27
    assert result["burnside"] == pytest.approx(27.0)


def test_gauge_fixed_complexes_realise_distinct_states(a4):
    """Build a real ``d(Delta^3)`` for each gauge-fixed configuration and check that

    (a) the spanning tree really is trivial, and
    (b) the number of distinct *gauge-invariant appearances* never exceeds 178 --
        it cannot be finer than the orbit decomposition, since appearance is a gauge
        invariant.
    """
    configs = enumerate_gauge_fixed_configs(a4, TETRA_FREE_EDGES)
    appearances = set()
    for (a02, a03, a13) in configs:
        cx = make_tetrahedron_boundary("A4")
        e = a4.identity()
        assert all(cx.label(u, v) == e for (u, v) in ((0, 1), (1, 2), (2, 3)))
        cx.set_label(0, 2, a02)
        cx.set_label(0, 3, a03)
        cx.set_label(1, 3, a13)
        # d(Delta^3) has no 3-simplices, so the observable surface is its face set
        curvatures = frozenset(
            (face, id_key(a4, triangle_holonomy(cx, face))) for face in cx.faces()
        )
        appearances.add(curvatures)
    assert len(appearances) <= 178


def id_key(group, element):
    return next(i for i, cls in enumerate(group.conjugacy_classes()) if element in cls)
