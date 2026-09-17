"""Test 1 -- group correctness.

Specification: "For ``A_4``, there must be exactly 12 elements. Multiplication must
be closed. Every element must have an inverse. The conjugacy classes must match
``A_4``."
"""

from __future__ import annotations

import itertools

import pytest

from constraintnet.groups import AlternatingGroup4, CyclicGroup, get_group


class TestA4:
    def test_exactly_twelve_elements(self, a4):
        assert len(a4.elements) == 12
        assert len(set(a4.elements)) == 12

    def test_multiplication_is_closed(self, a4):
        elements = set(a4.elements)
        for a, b in itertools.product(a4.elements, repeat=2):
            assert a4.multiply(a, b) in elements

    def test_identity_laws(self, a4):
        e = a4.identity()
        for a in a4.elements:
            assert a4.multiply(e, a) == a
            assert a4.multiply(a, e) == a

    def test_every_element_has_an_inverse(self, a4):
        e = a4.identity()
        for a in a4.elements:
            inv = a4.inverse(a)
            assert a4.multiply(a, inv) == e
            assert a4.multiply(inv, a) == e

    def test_associativity(self, a4):
        for a, b, c in itertools.product(a4.elements, repeat=3):
            left = a4.multiply(a4.multiply(a, b), c)
            right = a4.multiply(a, a4.multiply(b, c))
            assert left == right

    def test_conjugacy_classes_have_A4_sizes(self, a4):
        sizes = sorted(len(cls) for cls in a4.conjugacy_classes())
        assert sizes == [1, 3, 4, 4]

    def test_conjugacy_class_names(self, a4):
        names = {a4.class_name(a) for a in a4.elements}
        assert names == {
            "identity",
            "order-2 (double transposition)",
            "order-3 (+)",
            "order-3 (-)",
        }

    def test_classes_partition_the_group(self, a4):
        classes = a4.conjugacy_classes()
        total = sum(len(cls) for cls in classes)
        assert total == 12
        for x, y in itertools.combinations(classes, 2):
            assert not (x & y)

    def test_class_equation_centralizer_times_class(self, a4):
        for a in a4.elements:
            assert len(a4.class_of(a)) * len(a4.centralizer(a)) == 12

    def test_element_orders_match_A4(self, a4):
        orders = sorted(a4.order_of(a) for a in a4.elements)
        assert orders == [1, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3]

    def test_generators_actually_generate(self, a4):
        # word_lengths() raises if the declared generators do not reach every element
        lengths = a4.word_lengths()
        assert len(lengths) == 12
        assert lengths[a4.identity()] == 0
        assert max(lengths.values()) >= 1

    def test_not_abelian(self, a4):
        assert a4.is_abelian() is False


class TestZ3:
    def test_structure(self, z3):
        assert z3.elements == (0, 1, 2)
        assert z3.identity() == 0
        assert z3.multiply(2, 2) == 1
        assert z3.inverse(1) == 2
        assert z3.is_abelian() is True

    def test_classes_are_singletons(self, z3):
        classes = z3.conjugacy_classes()
        assert len(classes) == 3
        assert all(len(cls) == 1 for cls in classes)


def test_factory_roundtrip():
    for name, order in (("Z2", 2), ("Z3", 3), ("A4", 12)):
        assert get_group(name).order() == order
    with pytest.raises(KeyError):
        get_group("S5")
