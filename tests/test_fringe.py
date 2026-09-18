"""D2 fringe test: discrete Aharonov-Bohm measured on the cone interferometer."""

from __future__ import annotations

import pytest

from constraintnet.fringe import fringe_coherence
from constraintnet.resolutions import enumerate_internal_resolutions
from constraintnet.seeds import make_cone_over_tetrahedron


@pytest.fixture(scope="module")
def a4_interferometer():
    cx, apex, _ = make_cone_over_tetrahedron("A4")
    g = cx.group
    o2 = next(x for x in g.elements if g.order_of(x) == 2)
    return cx, apex, [0, 1, 2], frozenset(g.class_of(o2))


def test_flat_patch_perfectly_coherent(a4_interferometer):
    """Hidden multiplicity alone does NOT decohere: flat patch -> C = V = 1."""
    cx, apex, b3, _ = a4_interferometer
    sol = enumerate_internal_resolutions(cx, apex, b3)
    assert len(sol) == 12  # |G| gauge copies of the unique flat interior
    res = fringe_coherence(cx, apex, b3, sol, cx.label(0, 2))
    assert res["coherence"] == 1.0 and abs(res["visibility"] - 1.0) < 1e-12


def test_flux_through_interferometer_kills_coherence(a4_interferometer):
    """Flux on the face enclosed by the loop pins Phi_L to the flux CLASS (AB effect).

    Visibility = |chi_3(flux)|/3 = 1/3 exactly: the fringe readout IS the character.
    """
    cx, apex, b3, cV4 = a4_interferometer
    fc = {(0, 1): cV4, (1, 2): cV4, (0, 2): cV4}
    sol = enumerate_internal_resolutions(cx, apex, b3, fc)
    assert len(sol) == 72
    res = fringe_coherence(cx, apex, b3, sol, cx.label(0, 2))
    assert res["coherence"] == 0.0
    assert abs(res["visibility"] - 1.0 / 3.0) < 1e-9


def test_flux_outside_the_loop_keeps_fringes(a4_interferometer):
    """Flux on faces the loop does NOT enclose: coherence stays perfect -- locality."""
    cx, apex, b3, cV4 = a4_interferometer
    fc = {(0, 1): cV4, (1, 2): cV4}  # (*02) flat; loop bounds (*02)
    sol = enumerate_internal_resolutions(cx, apex, b3, fc)
    assert len(sol) == 36
    res = fringe_coherence(cx, apex, b3, sol, cx.label(0, 2))
    assert res["coherence"] == 1.0 and abs(res["visibility"] - 1.0) < 1e-9


def test_abelian_contrast_phase_shift_without_visibility_loss():
    """Z3: flux shifts the fringe phase (|omega^-k| = 1): which-PHASE, not which-PATH."""
    cx, apex, _ = make_cone_over_tetrahedron("Z3")
    k1 = frozenset({1})
    fc = {(0, 1): k1, (1, 2): k1, (0, 2): frozenset({2})}
    sol = enumerate_internal_resolutions(cx, apex, [0, 1, 2], fc)
    assert len(sol) == 3
    res = fringe_coherence(cx, apex, [0, 1, 2], sol, cx.label(0, 2))
    assert res["coherence"] == 0.0                      # shifted off trivial
    assert abs(res["visibility"] - 1.0) < 1e-9           # but fully coherent


def test_single_face_flux_interferometer_forbidden(a4_interferometer):
    """Chirality guard (M3 result reused): lone flux on one interior face is unrealizable --
    the interferometer itself can be a configuration the theory forbids."""
    cx, apex, b3, cV4 = a4_interferometer
    sol = enumerate_internal_resolutions(cx, apex, b3, {(0, 2): cV4})
    assert sol == []
