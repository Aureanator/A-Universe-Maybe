"""E030: CORE ENTROPY MEASUREMENT -- E027's prediction, tested.

Prediction (from the E027 rigidity negative result): hidden-resolution entropy lives in
the defect CORE (a fully interior vertex capping curvature from inside), not in the
field around a flux loop.

Measured on Kuhn n=2 with A4 and an order-3 star seed at the central vertex 13
(the only fully-interior vertex; E_int = 14, V_free = {13}):

    core region star(13):        raw |Sol| = 48, physical |I| = 4   (S = log 4)
    field-only balls r=1,2:      |I| = 1  (rigid -- E027 reproduced)
    full ball (E_int = 26):      |I| = 4  (identical to core: entropy LOCALIZES at the core)

Controls:
    involution seed (flat):      raw = 12 = |G|, |I| = 1   (flat star connections are pure gauge;
                                                             also confirms free gauge action)
    Z3 twin of the same core:    |I| = 1   ("hidden state requires non-abelian-ness" holds
                                             at cores, not just cones -- E010 generalized)

State structure: all four physical states share ONE support (7 of 14 star edges active,
7 identity -- a polarization fixed by the link geometry), and differ only in WHICH
order-3 element fills it; the four filling elements form exactly one conjugacy class.
The hidden internal state space of this core is in bijection with its flux class.

Slice solver (E029) makes these exact at 12^14 scale: ~0.1 s where brute force needs ~1e15.
"""

import itertools
import math

import pytest

from constraintnet.seeds import kuhn_ball
from constraintnet.region import region_from_tets
from constraintnet.strings import _hol, flux_string_components
from constraintnet.entropy import (region_resolution_space, interior_vertices,
                                   metric_ball_tets)


def seed_star(cx, v_star, order):
    g = cx.group
    c = sorted([x for x in g.elements if g.order_of(x) == order], key=repr)[0]
    for e in sorted(cx.edges()):
        cx.set_label(e[0], e[1], c if v_star in e else g.identity())
    decl = {}
    for f in cx.faces():
        decl[tuple(sorted(f))] = g.class_of(_hol(cx, f))
    return decl


def star_region(cx, v):
    return region_from_tets(cx, [t for t in cx.tetrahedra() if v in t], name=f"star{v}")


def declared_space(cx, reg, decl):
    fc = {f: decl.get(f, frozenset({cx.group.identity()}))
          for f in map(tuple, map(sorted, reg.interior_faces()))}
    return region_resolution_space(cx, reg, fc, method="slice")


@pytest.fixture()
def seeded_core():
    cx = kuhn_ball("A4", n=2)
    decl = seed_star(cx, 13, 3)
    return cx, decl


def test_central_vertex_is_the_only_full_core(seeded_core):
    cx, _ = seeded_core
    cores = []
    for v in sorted(cx.vertices()):
        reg = star_region(cx, v)
        if interior_vertices(cx, reg) == [v]:
            cores.append(v)
    assert cores == [13]


def test_seeded_loop_is_closed(seeded_core):
    cx, _ = seeded_core
    comps = flux_string_components(cx)
    assert len(comps) == 1 and comps[0].kind == "loop" and comps[0].length == 12


def test_core_carries_hidden_entropy(seeded_core):
    """THE measurement: |I(star(13))| = 4 physical states from 48 raw resolutions."""
    cx, decl = seeded_core
    space = declared_space(cx, star_region(cx, 13), decl)
    assert space.skipped_reason is None
    assert space.count_raw == 48
    assert space.count_physical == 4
    assert math.isclose(space.entropy, math.log(4))


def test_field_regions_are_rigid(seeded_core):
    """E027 reproduced: balls enclosing loop faces but NOT the core admit a unique filling."""
    cx, decl = seeded_core
    curved = sorted(decl)
    lf = next(f for f in curved if len(f) == 3 and 13 not in f or True)
    center = next(t for t in cx.tetrahedra() if set(curved[0]) <= set(t))
    for r in (1, 2):
        reg = region_from_tets(cx, metric_ball_tets(cx, center, r), name=f"field_r{r}")
        assert 13 not in interior_vertices(cx, reg)     # field-only: core excluded
        space = declared_space(cx, reg, decl)
        assert space.count_physical == 1                # rigid


def test_entropy_localizes_at_core(seeded_core):
    """Full ball (E_int=26) has the SAME |I| as the core neighborhood: field edges add none."""
    cx, decl = seeded_core
    full = region_from_tets(cx, list(cx.tetrahedra()), name="full")
    assert interior_vertices(cx, full) == [13]
    space = declared_space(cx, full, decl)
    assert space.n_interior_edges == 26
    assert space.count_physical == 4


def test_involution_seed_control_is_pure_gauge():
    """Flat declaration: solutions are exactly the |G| constant configurations -> |I|=1."""
    cx = kuhn_ball("A4", n=2)
    seed_star(cx, 13, 2)                                # involution star is flat (E026)
    assert flux_string_components(cx) == []
    space = declared_space(cx, star_region(cx, 13), {})
    assert space.count_raw == len(cx.group.elements)    # freeness of the gauge action
    assert space.count_physical == 1


def test_z3_twin_core_has_no_hidden_state():
    """Abelian twin: |I| = 1 -- hidden state requires non-abelian-ness, at cores too."""
    cx = kuhn_ball("Z3", n=2)
    decl = seed_star(cx, 13, 3)
    space = declared_space(cx, star_region(cx, 13), decl)
    assert space.count_physical == 1


def test_four_states_share_support_filled_by_one_class(seeded_core):
    """State structure: fixed support (7 active edges); fillings = one conjugacy class."""
    cx, decl = seeded_core
    reg = star_region(cx, 13)
    group = cx.group
    fc = {f: decl.get(f, frozenset({group.identity()}))
          for f in map(tuple, map(sorted, reg.interior_faces()))}
    space = region_resolution_space(cx, reg, fc, method="slice")
    from constraintnet.entropy import enumerate_region_resolutions_slice
    sols = enumerate_region_resolutions_slice(cx, reg, fc)
    ie = reg.interior_edges()

    # gauge orbits via canonical min-rep (gauge only at vertex 13; mixed orientation)
    def gimg(x, lam):
        out = []
        for (u, v), value in zip(ie, x):
            left = group.identity() if u != 13 else group.inverse(lam)
            right = group.identity() if v != 13 else lam
            out.append(group.multiply(group.multiply(left, value), right))
        return tuple(out)

    orbits = {}
    for s in sols:
        rep = min(repr(gimg(s, lam)) for lam in group.elements)
        orbits.setdefault(rep, s)
    assert len(orbits) == 4
    supports = set()
    fillings = []
    for rep, s in orbits.items():
        supports.add(frozenset(i for i, v in enumerate(s) if v != group.identity()))
        nz = [v for v in s if v != group.identity()]
        assert len(set(nz)) == 1                        # one label fills the whole support
        fillings.append(nz[0])
    assert len(supports) == 1                           # polarization fixed by geometry
    classes = {g for g in group.conjugacy_classes() if fillings[0] in g}
    assert all(any(f in c for c in classes) for f in fillings)   # one class, four elements
    assert len(set(fillings)) == 4
