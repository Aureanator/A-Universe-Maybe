"""Frame invariance and relational information of shared-face compatibility."""

import itertools

import pytest

from constraintnet.groups import AlternatingGroup4, CyclicGroup
from constraintnet.interaction import compatible_on_shared_face, face_flux


IDX = {0: 0, 1: 1, 2: 2}


def test_class_match_does_not_imply_one_common_frame():
    g = AlternatingGroup4()
    e = g.identity()
    x = (e, (0, 2, 3, 1), (1, 2, 0, 3))
    y = (e, (0, 2, 3, 1), (0, 3, 1, 2))
    edges = [((0, 1), e), ((1, 2), e), ((0, 2), e)]
    assert compatible_on_shared_face(g, x, y, edges, IDX, IDX, matching="classes")
    assert not compatible_on_shared_face(g, x, y, edges, IDX, IDX)


def test_independent_apex_frames_preserve_true_and_false_verdicts():
    g = AlternatingGroup4()
    e = g.identity()
    o2 = next(a for a in g.elements if g.order_of(a) == 2)
    o3 = next(a for a in g.elements if g.order_of(a) == 3)
    x = (e, o2, o3)
    edges = [((0, 1), o2), ((1, 2), o3), ((0, 2), e)]
    states = list(itertools.product(g.elements, repeat=3))
    rejected = next(y for y in states
                    if not compatible_on_shared_face(g, x, y, edges, IDX, IDX))
    for y, expected in [(x, True), (rejected, False)]:
        for nu, eta in itertools.product(g.elements, repeat=2):
            tx = tuple(g.multiply(g.inverse(nu), a) for a in x)
            ty = tuple(g.multiply(g.inverse(eta), a) for a in y)
            assert compatible_on_shared_face(g, tx, ty, edges, IDX, IDX) == expected


def test_boundary_gauge_and_distinct_index_orders():
    g = AlternatingGroup4()
    x = (g.elements[2], g.elements[5], g.elements[7])
    y = x
    edges = [((0, 1), g.elements[3]), ((1, 2), g.elements[6]),
             ((0, 2), g.elements[9])]
    lambdas = (g.elements[4], g.elements[8], g.elements[11])
    transformed = [((v, w), g.multiply(g.multiply(g.inverse(lambdas[v]), a), lambdas[w]))
                   for (v, w), a in edges]
    tx = tuple(g.multiply(x[v], lambdas[v]) for v in range(3))
    ty = tuple(g.multiply(y[v], lambdas[v]) for v in (2, 0, 1))
    assert compatible_on_shared_face(g, tx, ty, transformed, IDX, {2: 0, 0: 1, 1: 2})


def test_abelian_conventions_agree_exhaustively():
    g = CyclicGroup(3)
    states = list(itertools.product(g.elements, repeat=3))
    edges = [((0, 1), 1), ((1, 2), 2), ((0, 2), 0)]
    for x, y in itertools.product(states, repeat=2):
        results = {compatible_on_shared_face(g, x, y, edges, IDX, IDX, matching=mode)
                   for mode in ("raw", "classes", "relational")}
        assert len(results) == 1


def test_relational_probe_count_matches_orbit_times_raw_fibre():
    """Independent counting identity for complete probe ensembles, no fitted counts."""
    g = AlternatingGroup4()
    e = g.identity()
    o2 = next(a for a in g.elements if g.order_of(a) == 2)
    o3 = next(a for a in g.elements if g.order_of(a) == 3)
    probes = list(itertools.product(g.elements, repeat=3))
    for labels in [(e, e, e), (o2, o3, e)]:
        edges = list(zip(((0, 1), (1, 2), (0, 2)), labels))
        for x in [(e, e, e), (e, o2, o3)]:
            flux = tuple(face_flux(g, x[v], a, x[w]) for (v, w), a in edges)
            orbit = {tuple(g.conjugate(mu, a) for a in flux) for mu in g.elements}
            raw = sum(compatible_on_shared_face(g, x, y, edges, IDX, IDX, matching="raw")
                      for y in probes)
            physical = sum(compatible_on_shared_face(g, x, y, edges, IDX, IDX)
                           for y in probes)
            assert physical == raw * len(orbit)


def test_unknown_convention_rejected_even_on_empty_interface():
    with pytest.raises(ValueError, match="unknown matching"):
        compatible_on_shared_face(CyclicGroup(3), (), (), [], {}, {}, matching="typo")
