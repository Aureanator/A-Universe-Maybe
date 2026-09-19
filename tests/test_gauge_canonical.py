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
        # independently reconstructed by the R3 panel and now pinned: on this slice the raw-
        # holonomy canonical form is COMPLETE -- exactly the 178 Burnside physical classes
        assert len(states) == 178, f"expected exactly the 178 orbits, got {len(states)}"

    def test_empty_region(self):
        cx = make_tetrahedron_boundary("A4")
        # remove all labels variety: identity everywhere -> trivial state exists
        region = Region(cx, [], "dDelta3")
        assert isinstance(region.gauge_invariant_state(), tuple)

    def test_cavity_component_not_invisible(self):
        """R3 F6: a change on a DISCONNECTED second surface component must move the canonical
        state (the old single-root version silently skipped it)."""
        import itertools

        from constraintnet.complex import SimplicialComplex

        cx = SimplicialComplex("A4")
        # two disjoint tetrahedral boundaries: vertices 0-3 and 10-13
        for base in (0, 10):
            for u, v in itertools.combinations(range(base, base + 4), 2):
                cx.add_edge(u, v)
            for tri in itertools.combinations(range(base, base + 4), 3):
                cx.add_face(tri)
        g = cx.group
        t = next(x for x in g.elements if g.order_of(x) == 3)
        cx.set_label(10, 12, t)  # curvature ONLY on the second component
        region = Region(cx, [], "two-shells")
        state_with = region.gauge_invariant_state()
        cx.set_label(10, 12, g.identity())
        state_without = region.gauge_invariant_state()
        assert state_with != state_without, "cavity component invisible in canonical state"

    def test_curvature_cannot_swap_surface_components(self):
        """Vertex gauge cannot move curvature between distinct labelled shells."""
        import itertools

        from constraintnet.complex import SimplicialComplex

        cx = SimplicialComplex("A4")
        for base in (0, 10):
            for tri in itertools.combinations(range(base, base + 4), 3):
                cx.add_face(tri)
        g = cx.group
        flux = next(x for x in g.elements if g.order_of(x) == 3)
        region = Region(cx, [], "two-shells")
        cx.set_label(0, 2, flux)
        on_first_shell = region.gauge_invariant_state()
        cx.set_label(0, 2, g.identity())
        cx.set_label(10, 12, flux)
        assert region.gauge_invariant_state() != on_first_shell

    def test_multi_component_gauge_invariance(self):
        import itertools
        import random

        from constraintnet.complex import SimplicialComplex
        from constraintnet.gauge import gauge_transform

        cx = SimplicialComplex("A4")
        for base in (0, 10):
            for u, v in itertools.combinations(range(base, base + 4), 2):
                cx.add_edge(u, v)
            for tri in itertools.combinations(range(base, base + 4), 3):
                cx.add_face(tri)
        rng = random.Random(9)
        for (u, v) in cx.edges():
            cx.set_label(u, v, rng.choice(list(cx.group.elements)))
        region = Region(cx, [], "two-shells")
        s0 = region.gauge_invariant_state()
        gauge_transform(cx, {v: rng.choice(list(cx.group.elements)) for v in cx.vertices()})
        assert region.gauge_invariant_state() == s0


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
