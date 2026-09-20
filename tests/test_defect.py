import numpy as np

from constraintnet.defect import GaugePatch, flux_ring, ring_is_closed
from constraintnet.seeds import kuhn_ball, make_tetrahedron_boundary
from constraintnet.walk import ArcWalk


def _patch(group):
    cx = make_tetrahedron_boundary(group)
    return GaugePatch(cx)


def test_star_and_plaquette_are_commuting_projectors():
    for group in ("Z2", "Z3"):
        P = _patch(group)
        _, A, B = P.hamiltonian()
        for a in A:
            assert np.abs(a @ a - a).max() < 1e-12
        for b in B:
            assert np.abs(b @ b - b).max() < 1e-12
        assert max(np.abs(a @ b - b @ a).max() for a in A for b in B) < 1e-12
        assert max(np.abs(x @ y - y @ x).max() for x in A for y in A) < 1e-12


def test_non_abelian_patch_is_gapped():
    cx = make_tetrahedron_boundary("A4")
    face = sorted(cx.faces())[0]
    edges = [tuple(sorted(p)) for p in ((face[0], face[1]), (face[1], face[2]), (face[0], face[2]))]
    P = GaugePatch(cx, edges=edges, faces=[face])
    H, A, B = P.hamiltonian()
    assert max(np.abs(a @ b - b @ a).max() for a in A for b in B) < 1e-12
    ev = np.round(np.linalg.eigvalsh(H), 10)
    gs = ev.min()
    assert int((ev == gs).sum()) == 1
    assert float(np.min(ev[ev > gs]) - gs) > 0.5


def test_flux_of_one_edge_is_a_closed_ring_of_six_or_four_faces():
    cx = kuhn_ball("A4", n=3)
    interior = set(ArcWalk(cx, dim=1, mode="closed").interior)
    edges = [e for e in cx.edges() if e[0] in interior and e[1] in interior]
    assert edges
    for e in edges:
        assert ring_is_closed(cx, e)
        assert len(flux_ring(cx, e)) in (4, 6)
