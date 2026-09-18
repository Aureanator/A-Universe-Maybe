"""Gauge-invariant relational state + class-closed proposals (referee audit items 2, 3)."""

from __future__ import annotations

import random

import pytest

from constraintnet.gauge import gauge_transform
from constraintnet.moves import class_closed_generators
from constraintnet.region import Region
from constraintnet.seeds import kuhn_ball, make_tetrahedron_boundary, randomize_labels


class TestGaugeInvariantState:
    def test_exact_under_random_gauge(self):
        cx = kuhn_ball("A4", n=2)
        randomize_labels(cx, seed=13)
        region = Region(cx, cx.tetrahedra(), "universe")
        state0 = region.gauge_invariant_state()
        rng = random.Random(5)
        for _ in range(6):
            lambdas = {v: rng.choice(list(cx.group.elements)) for v in cx.vertices()}
            gauge_transform(cx, lambdas)
            assert region.gauge_invariant_state() == state0, "canonical form not gauge-invariant"

    def test_strictly_finer_than_appearance_on_tetrahedron(self):
        """appearance() collapses the 178 physical classes to 82 class-tuples; the canonical
        raw-holonomy form must separate strictly more (referee item 2's relational-loss claim)."""
        group = None
        states, appearances = set(), set()
        els = None
        cx0 = make_tetrahedron_boundary("A4")
        els = list(cx0.group.elements)
        for a in els:
            for b in els:
                for c in els:
                    cx = make_tetrahedron_boundary("A4")
                    cx.set_label(0, 2, a)
                    cx.set_label(0, 3, b)
                    cx.set_label(1, 3, c)
                    region = Region(cx, [], "dDelta3")
                    states.add(region.gauge_invariant_state())
                    appearances.add(region.appearance().signature())
        assert len(appearances) == 82
        assert len(states) > 82, "canonical form should retain relational data classes discard"
        assert len(states) <= 178

    def test_empty_region(self):
        cx = make_tetrahedron_boundary("A4")
        # remove all labels variety: identity everywhere -> trivial state exists
        region = Region(cx, [], "dDelta3")
        assert isinstance(region.gauge_invariant_state(), tuple)


class TestClassClosedProposals:
    def test_generator_set_is_conjugation_closed(self):
        cx = make_tetrahedron_boundary("A4")
        gens = class_closed_generators(cx.group)
        g = cx.group
        assert len(gens) == 11
        for h in gens:
            for x in g.elements:
                assert g.conjugate(x, h) in gens

    def test_reachable_orbits_equivariant_under_global_conjugation(self):
        """Exhaustive-ish equivariance on the tetrahedron slice (referee item 3 pin)."""
        cx = make_tetrahedron_boundary("A4")
        g = cx.group
        els = list(g.elements)

        def set_labels(triple):
            cx.set_label(0, 2, triple[0])
            cx.set_label(0, 3, triple[1])
            cx.set_label(1, 3, triple[2])

        def orbit_of_current():
            # canonical under global conjugation of the three free labels via region state
            return Region(cx, [], "dDelta3").gauge_invariant_state()

        gens = class_closed_generators(g)
        rng = random.Random(3)
        triples = [tuple(rng.choice(els) for _ in range(3)) for _ in range(40)]
        for t in triples:
            set_labels(t)
            base = orbit_of_current()
            conjg = rng.choice(els)
            tc = tuple(g.conjugate(conjg, x) for x in t)
            set_labels(tc)
            moved = orbit_of_current()
            assert base == moved  # same physical state; canonical form agrees

        # and one-move reachable sets agree for config vs conjugate (class-closed arm)
        def reach(triple):
            out = set()
            for pos in range(3):
                for h in gens:
                    new = list(triple)
                    new[pos] = g.multiply(triple[pos], h)
                    if tuple(new) != triple:
                        set_labels(tuple(new))
                        out.add(orbit_of_current())
            return frozenset(out)

        violations = 0
        for t in triples[:15]:
            r1 = reach(t)
            for conjg in els:
                tc = tuple(g.conjugate(conjg, x) for x in t)
                if tc == t:
                    continue
                if reach(tc) != r1:
                    violations += 1
        assert violations == 0, "class-closed arm must be exactly equivariant"
