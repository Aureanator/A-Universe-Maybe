"""The Bianchi finding: charge cannot be a surface sum (abelian case, exactly zero).

While writing the region code we expected "net charge enclosed by a region" to be the
curvature flux through its boundary.  It is identically zero for curvature of the form
``Phi = dA``, because every edge of a closed surface lies in two faces with opposite
induced orientations and all labels cancel.  These tests pin that down so nobody
re-introduces a fake "Gauss law" later -- charge lives on *cycles* instead.
"""

from __future__ import annotations

import pytest

from constraintnet.holonomy import bianchi_defect, triangle_holonomy
from constraintnet.region import Region, closed_surface_flux
from constraintnet.seeds import kuhn_ball, make_single_tetrahedron, randomize_labels


def test_reversing_face_orientation_inverts_its_holonomy(ball_a4, a4):
    for face in ball_a4.faces():
        forward = triangle_holonomy(ball_a4, face)
        backward = triangle_holonomy(ball_a4, (face[0], face[2], face[1]))
        assert backward == a4.inverse(forward)


def test_single_tetrahedron_surface_sum_is_identity_for_every_labelling(z3):
    for seed in range(12):
        cx = make_single_tetrahedron("Z3")
        randomize_labels(cx, seed=seed)
        region = Region(cx, cx.tetrahedra(), "tet")
        assert closed_surface_flux(cx, region.boundary_faces_signed()) == 0


def test_bianchi_defect_zero_on_random_labelings(ball_z3):
    for seed in range(10):
        randomize_labels(ball_z3, seed=seed)
        assert bianchi_defect(ball_z3) == 0.0


def test_whole_ball_boundary_flux_is_identity(z3):
    cx = kuhn_ball("Z3", n=2)
    for seed in range(4):
        randomize_labels(cx, seed=seed)
        region = Region(cx, cx.tetrahedra(), "ball")
        assert region.is_closed_boundary()
        assert closed_surface_flux(cx, region.boundary_faces_signed()) == z3.identity()


def test_bianchi_refuses_nonabelian_groups_instead_of_lying(ball_a4):
    with pytest.raises(TypeError) as excinfo:
        bianchi_defect(ball_a4)
    assert "cycle charges" in str(excinfo.value)


def test_flux_through_an_open_patch_equals_its_boundary_loop(z3):
    r"""The usable Gauss law: flux through a *disk* equals its boundary loop holonomy.

    For the closed surface of a tetrahedron the signed curvature sum vanishes, so for
    any disk patch ``P`` inside it::

        sum_{f in P} sign(f) Phi_f  ==  Phi_{dP}

    i.e. what an open surface measures is exactly the charge of the cycle that bounds
    it -- which is why the specification defines ``Q_C = Phi_C`` on cycles.
    """
    cx = make_single_tetrahedron("Z3")
    randomize_labels(cx, seed=21)
    region = Region(cx, cx.tetrahedra(), "tet")
    signed = region.boundary_faces_signed()

    missing_face, _ = sorted(signed.items())[0]
    patch = {f: s for f, s in signed.items() if f != missing_face}

    flux_through_patch = closed_surface_flux(cx, patch)
    boundary_loop_charge = triangle_holonomy(cx, missing_face)

    # the patch's induced boundary runs opposite to the omitted face's outward side,
    # hence the inverse; this is an orientation convention, not a physics choice
    assert flux_through_patch == z3.inverse(boundary_loop_charge)
