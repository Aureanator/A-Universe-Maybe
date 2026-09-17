"""Representation theory tests: character orthogonality and fusion rules of A4."""

from __future__ import annotations

import pytest

from constraintnet.reps import a4_irreps, decompose, inner_product, singlet_count, tensor_characters


@pytest.fixture(scope="module")
def table():
    return a4_irreps()


def test_orthonormality(table):
    g, irreps = table
    for i, a in enumerate(irreps):
        for j, b in enumerate(irreps):
            ip = inner_product(g, a.character, b.character)
            expected = 1.0 if i == j else 0.0
            assert abs(ip.real - expected) < 1e-9 and abs(ip.imag) < 1e-9


def test_dimension_sum_and_class_count(table):
    g, irreps = table
    assert len(irreps) == len(g.conjugacy_classes())  # number of irreps = number of classes
    assert sum(r.dimension**2 for r in irreps) == len(g.elements)


def test_three_dim_character_values(table):
    g, irreps = table
    chi3 = next(r for r in irreps if r.name == "3").character
    by_order = {}
    for index, x in enumerate(g.elements):
        by_order.setdefault(g.order_of(x), set()).add(chi3[index])
    assert by_order[1] == {3.0}
    assert by_order[2] == {-1.0}
    assert by_order[3] == {0.0}


def test_fusion_rule_3x3(table):
    g, irreps = table
    i3 = next(i for i, r in enumerate(irreps) if r.name == "3")
    fused = decompose(g, irreps, tensor_characters(irreps, i3, i3))
    assert fused == {"1": 1, "1'": 1, "1''": 1, "3": 2}  # 9 = 1+1+1+6


def test_phase_arithmetic_of_one_dims(table):
    """The spec's sectors 1, omega, omega^2 fuse as Z3: 1_i x 1_j = 1_{i+j mod 3}."""
    g, irreps = table
    onedims = [i for i, r in enumerate(irreps) if r.dimension == 1]
    assert len(onedims) == 3
    for a_pos, a in enumerate(onedims):
        for b_pos, b in enumerate(onedims):
            fused = decompose(g, irreps, tensor_characters(irreps, a, b))
            assert sum(fused.values()) == 1  # product of 1D irreps is irreducible
            assert list(fused.values())[0] == 1


def test_singlet_counts(table):
    g, irreps = table
    i3 = next(i for i, r in enumerate(irreps) if r.name == "3")
    i1p = next(i for i, r in enumerate(irreps) if r.name == "1'")
    assert singlet_count(g, irreps, 0, 0) == 1      # 1 x 1: one invariant coupling
    # 3 x 3 = 1 + 1' + 1'' + 2*3 carries exactly ONE trivial (x^2+y^2+z^2);
    # the 1', 1'' summands are twisted sectors -- charged, NOT singlets.
    assert singlet_count(g, irreps, i3, i3) == 1
    assert singlet_count(g, irreps, i1p, i3) == 0   # non-invariant: forbidden outcome
