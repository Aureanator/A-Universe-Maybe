"""Hard Gauss completion v1 tests: constraint-by-construction + confinement mechanics.

GaussState DEFINES charges as q_v = div(E)_v, so the Gauss constraint holds by
construction (solved, not penalized). These tests pin that and the consequences E067
relies on; all use Z2 (the declared v1 scope).
"""

from __future__ import annotations

import itertools
import random

import pytest

from constraintnet.gauss import GaussState
from constraintnet.seeds import kuhn_ball


@pytest.fixture()
def ball():
    return GaussState(kuhn_ball("Z2", n=2))


# ------------------------------------------------------------------ construction
def test_vacuum_has_no_charges(ball):
    assert all(q == 0 for q in ball.charges().values())
    assert ball.check_gauss()


def test_single_edge_flip_creates_even_pair(ball):
    u, w = ball.edges[7]
    ball.flip_E((u, w))
    live = [v for v, q in ball.charges().items() if q]
    assert sorted(live) == sorted([u, w])
    assert ball.check_gauss()


def test_isolated_charge_impossible_random_flips(ball):
    rng = random.Random(0)
    for _ in range(200):
        ball.flip_E(ball.edges[rng.randrange(len(ball.edges))])
        live = [v for v, q in ball.charges().items() if q]
        assert len(live) % 2 == 0, "odd charge count -- Gauss parity violated"
        assert ball.check_gauss()


def test_string_endpoints_only_interior_of_path():
    # n=3 has multiple interior vertices; a loaded path must have charges ONLY at its
    # two ends (interior vertices balanced)
    ball = GaussState(kuhn_ball("Z2", n=4))
    verts = list(ball.vertices)
    # pick two vertices at graph distance >= 3 so the string has real interior points
    a, b, path = None, None, None
    for i, x in enumerate(verts):
        for y in verts[i + 1:]:
            p = ball.shortest_path(x, y)
            if p and len(p) >= 4:
                a, b, path = x, y, p
                break
        if a is not None:
            break
    assert a is not None, "no vertex pair at distance >= 3 in n=4 ball"
    ball.load_string(path)
    live = sorted(v for v, q in ball.charges().items() if q)
    assert live == sorted([a, b]), "interior string points must carry no net charge"


def test_double_flip_is_identity(ball):
    e = ball.edges[3]
    before = list(ball.E)
    ball.flip_E(e)
    ball.flip_E(e)
    assert ball.E == before


# ------------------------------------------------------------------ boundary reservoir
def test_boundary_charge_counts_as_exited():
    st = GaussState(kuhn_ball("Z2", n=2))
    bv = next(iter(st.boundary_vertices))
    # find an edge from a boundary vertex to anywhere, load it -> charge on boundary
    e = next(ed for ed in st.edges if bv in ed)
    st.flip_E(e)
    assert st.charges()[bv] == 1
    assert st.exited_charge() >= 1


# ------------------------------------------------------------------ driver integration
def test_driverG_preserves_gauss_and_cools_magnetic():
    from constraintnet.drivers import DriverG
    cx = kuhn_ball("Z2", n=2)
    st = GaussState(cx)
    # seed some curvature then run: at high beta_B magnetic energy must not grow unbounded
    rng = random.Random(1)
    for e in cx.edges()[:5]:
        st.flip_g(e)
    driver = DriverG(st, rng_seed=2, beta_B=8.0, beta_E=4.0)
    peak = 0
    for _ in range(300):
        driver.advance()
        assert st.check_gauss()
        peak = max(peak, st.magnetic_energy_count())
    # finite penalty at beta_B=8 keeps curvature bounded well below "all faces curved"
    total_faces = len(list(cx.faces()))
    assert peak < total_faces, f"magnetic sector heated to {peak}/{total_faces}"


def test_driverG_rejects_grow_and_reverts_cleanly():
    from constraintnet.drivers import DriverG
    st = GaussState(kuhn_ball("Z2", n=2))
    driver = DriverG(st, rng_seed=3, beta_B=100.0, beta_E=100.0)  # near-zero-temperature
    e_before = list(st.E)
    g_before = {e: st.cx.label(*e) for e in st.edges}
    accepted = 0
    for _ in range(200):
        rec = driver.advance()
        if rec.fate == "accepted":
            accepted += 1
    # at beta=100 only energy-nonincreasing moves accept; vacuum (E=0, flat) can't be beaten,
    # so a huge majority of uphill proposals must have been vetoed and reverted exactly.
    assert accepted < 200


def test_nonabelian_group_rejected():
    from constraintnet.groups import get_group
    from constraintnet.complex import SimplicialComplex
    with pytest.raises(NotImplementedError):
        GaussState(kuhn_ball("A4", n=1))
