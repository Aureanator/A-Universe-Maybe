"""End-to-end: seeded flux loops -> detector -> boundary-memory and rigidity measurements.

Results codified here (see RESEARCH_DIARY E026-E027):
1. Vertex-star seeds of order-3 elements produce CLOSED FLUX LOOPS in Kuhn balls,
   detected by strings.flux_string_components as kind="loop" (n=1: 3-face loops at 6/8
   vertices; n=2 central vertex: a 12-face loop). Involution seeds are flat everywhere --
   existence of seeded loops depends on seed element order vs face orientation parity.
2. BOUNDARY MEMORY: any ball enclosing loop flux has NO flat-interior filling (|I|=0):
   the boundary data cannot be vacuum -- charge is measurable from outside, cone theorem
   (E010) generalized to balls.
3. RIGIDITY (negative result): with class-declared curvature on interior faces, enclosed
   loops admit a UNIQUE filling (|I|=1 even at class size 4). Loop fields carry no hidden
   entropy; E010's |I|=6 lives in the defect CORE (cone apex), not the field around it.
"""

import itertools
import pytest

from constraintnet.seeds import kuhn_ball
from constraintnet.strings import flux_string_components, _hol
from constraintnet.region import region_from_tets
from constraintnet.entropy import region_resolution_space, metric_ball_tets


def seed_star_loop(cx, v_star):
    """Label every edge incident to v_star by a fixed order-3 element; return curved map."""
    g = cx.group
    c = sorted([x for x in g.elements if g.order_of(x) == 3], key=repr)[0]
    for e in sorted(cx.edges()):
        cx.set_label(e[0], e[1], c if v_star in e else g.identity())
    curved = {}
    for f in cx.faces():
        fs = tuple(sorted(f))
        phi = _hol(cx, f)
        if phi != g.identity():
            curved[fs] = g.class_of(phi)
    return curved


def test_vertex_star_order3_seeds_closed_loops():
    cx = kuhn_ball("A4", n=1)
    curved = seed_star_loop(cx, 1)
    comps = flux_string_components(cx)
    assert len(comps) == 1 and comps[0].kind == "loop"
    assert all(len(cls) == 4 for cls in curved.values())      # order-3 class: size 4


def test_involution_star_seeds_are_flat():
    """t on the star of v with t^2=e kills curvature in both orientation-parity cases."""
    cx = kuhn_ball("A4", n=1)
    g = cx.group
    t = sorted([x for x in g.elements if g.order_of(x) == 2], key=repr)[0]
    for e in sorted(cx.edges()):
        cx.set_label(e[0], e[1], t if 1 in e else g.identity())
    assert flux_string_components(cx) == []


def test_central_loop_in_kuhn_n2():
    cx = kuhn_ball("A4", n=2)
    curved = seed_star_loop(cx, 13)                            # central vertex
    comps = flux_string_components(cx)
    assert len(comps) == 1 and comps[0].kind == "loop"
    assert comps[0].length == 12


def test_boundary_memory_no_vacuum_filling():
    """A ball enclosing loop flux admits NO flat-interior resolution: |I| = 0.

    The boundary appearance remembers the enclosed charge -- vacuum capping is impossible.
    """
    cx = kuhn_ball("A4", n=1)
    curved = seed_star_loop(cx, 1)
    tets = sorted(cx.tetrahedra())
    lf = sorted(curved)[0]
    center = next(t for t in tets if set(lf) <= set(t))
    reg = region_from_tets(cx, metric_ball_tets(cx, center, 1), name="enclosing")
    flat = frozenset({cx.group.identity()})
    space = region_resolution_space(
        cx, reg, {tuple(sorted(f)): flat for f in reg.interior_faces()}, max_internal_edges=5
    )
    assert space.count_physical == 0                           # forbidden: not vacuum


def test_enclosed_loop_rigid_under_class_declaration():
    """Class-declared curvature around an enclosed loop has a unique filling (|I|=1).

    Negative result with teeth: conjugacy-class slack (class size 4) does NOT produce
    hidden entropy in the field of the loop -- it is over-constrained by closure. Matter-
    like |I|>1 requires core structure (cone apex, E010), not enclosed flux alone.
    """
    cx = kuhn_ball("A4", n=2)
    curved = seed_star_loop(cx, 13)
    tets = sorted(cx.tetrahedra())
    lf = sorted(curved)[0]
    center = next(t for t in tets if set(lf) <= set(t))
    reg = region_from_tets(cx, metric_ball_tets(cx, center, 2), name="ball_r2")
    int_f = [tuple(sorted(f)) for f in reg.interior_faces()]
    declared = {f: curved[f] for f in int_f if f in curved}
    assert len(declared) >= 2                                  # loop genuinely enclosed
    space = region_resolution_space(cx, reg, declared, max_internal_edges=5)
    assert space.count_physical == 1                           # rigid
