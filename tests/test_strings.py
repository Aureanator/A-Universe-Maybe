"""Layer-2 item 2 (detector v1): flux-string clustering + GF(3) solvability engine.

The headline test is Bianchi's theorem re-derived as linear algebra: an isolated curved
face has NO preimage under d, so single-face flux is unrealizable -- while every exact
curvature pattern is solvable by construction. Detection then runs on real configurations.
"""

import itertools

import pytest

from constraintnet.seeds import kuhn_ball, make_single_tetrahedron
from constraintnet.strings import (
    classify_faces, curved_face_set, flux_string_components, is_flux_realizable,
    solve_flux_z3, ordered_loop_tets,
)


def _faces_of(cx):
    return [tuple(sorted(t)) for t in cx.faces()]


def _true_curvatures(cx):
    g = cx.group
    out = {}
    for tri in _faces_of(cx):
        i, j, k = tri

        def lab(u, v):
            return g.inverse(cx.label(v, u)) if u > v else cx.label(u, v)
        phi = g.multiply(g.multiply(lab(i, j), lab(j, k)), lab(k, i))
        out[tri] = phi
    return out


# ------------------------------------------------------------------ GF(3) solvability

def test_isolated_flux_unrealizable_rank_theorem():
    """Bianchi as a rank computation: exactly one curved face has no preimage under d."""
    cx = kuhn_ball("Z3", n=1)
    faces = _faces_of(cx)
    single = {faces[0]: 1}
    assert not is_flux_realizable(cx, single)


def test_exact_curvature_always_solvable():
    """Any pattern Phi = d psi (from actual labels) is in the image; solver verifies."""
    cx = kuhn_ball("Z3", n=1)
    # deterministic nonzero 1-cochain: label edge e by (u+v) mod 3
    for (u, v) in cx.edges():
        cx.set_label(u, v, (u + v) % 3)
    pattern = {f: phi % 3 for f, phi in _true_curvatures(cx).items()}
    solution = solve_flux_z3(cx, pattern)
    assert solution is not None
    # verify d(solution) == pattern on every face
    for f, want in pattern.items():
        i, j, k = f

        def lab(u, v):
            a = solution[(u, v)] if u < v else -solution[(v, u)]
            return a % 3
        assert (lab(i, j) + lab(j, k) + lab(k, i)) % 3 == want


def test_closed_surface_zero_condition_detected():
    """A pattern violating the closed-surface condition on some tet is rejected."""
    cx = make_single_tetrahedron("Z3")
    faces = _faces_of(cx)
    assert len(faces) == 4
    # one tet: d-image requires signed sum zero; (1,0,0,0) violates it
    assert not is_flux_realizable(cx, {faces[0]: 1})
    # alternating pattern satisfies the single-tet relation and IS realizable
    assert is_flux_realizable(cx, {f: 1 for f in faces})


# ------------------------------------------------------------------ detection

def test_flat_complex_has_no_strings():
    cx = kuhn_ball("Z3", n=1)
    assert curved_face_set(cx) == []
    assert flux_string_components(cx) == []


def test_boundary_arc_is_not_a_closed_loop():
    cx = make_single_tetrahedron("Z3")
    cx.set_label(0, 1, 1)
    comp, = flux_string_components(cx)
    assert comp.length == 2
    assert comp.kind == "sheet/junction"
    with pytest.raises(ValueError, match="not a closed"):
        ordered_loop_tets(cx, comp)


def test_loop_walk_traverses_the_detected_dual_cycle():
    from constraintnet.curvature import CurvatureState

    cx = kuhn_ball("Z3", n=2)
    state = CurvatureState(cx)
    cx.set_label(*state.edges[state.interior_edges[0]], 1)
    comp, = flux_string_components(cx)
    assert comp.kind == "loop"
    walk = ordered_loop_tets(cx, comp)
    assert len(set(walk)) == len(comp.tets_touched) == len(comp.faces)
    crossed = {tuple(sorted(set(a) & set(b))) for a, b in zip(walk, walk[1:]+walk[:1])}
    assert crossed == set(comp.faces)


def test_single_tet_bubble_detected_as_sheet():
    cx = make_single_tetrahedron("Z3")
    faces = _faces_of(cx)
    solution = solve_flux_z3(cx, {f: 1 for f in faces})
    assert solution is not None
    for (u, v), value in solution.items():
        cx.set_label(u, v, value % 3)
    comps = flux_string_components(cx)
    assert len(comps) == 1
    comp = comps[0]
    assert comp.length == 4
    assert comp.kind == "sheet/junction"           # one tet carries all four: bubble, not string


def test_classify_faces_synthetic_loop_and_junction():
    f1, f2, f3, f4 = (0, 1, 2), (0, 2, 3), (1, 2, 3), (1, 3, 4)
    # clean dual cycle: each tet carries exactly two component faces
    loop_struct = {"tA": [f1, f2], "tB": [f2, f3], "tC": [f3, f4], "tD": [f4, f1]}
    assert classify_faces([f1, f2, f3, f4], loop_struct) == "loop"
    # add branching: one tet carries three -> sheet/junction
    branch = dict(loop_struct)
    branch["tE"] = [f1, f2, f3]
    assert classify_faces([f1, f2, f3, f4], branch) == "sheet/junction"
    # endpoint: a tet carrying exactly one -> not a loop
    end = dict(loop_struct)
    end["tF"] = [f4]
    assert classify_faces([f1, f2, f3, f4], end) == "sheet/junction"
