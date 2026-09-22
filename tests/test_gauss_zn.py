"""Z_N Gauss completion tests (E069): solved constraint mod N + the N-ality classifier.

Two families.  (1) Structural: charges are div(E), so total charge is identically zero, a flux
update touches only its two endpoints by opposite amounts, and moves invert exactly.  (2) The
classifier: hand-checked pair-cancellation cases, including the load-bearing one -- three like
charges in Z3 are neutral yet contain no cancelling pair, which is the selection rule E068 said was
missing from Z2.

Fixtures are deliberately asymmetric (kuhn_ball n=2 over Z3): Z2 and K4-style symmetric settings
hide orientation and self-inverse bugs.
"""

from __future__ import annotations

import itertools
import random

import pytest

from constraintnet.gauss_zn import GaussStateZN, charge_curvature_correlation, nality_content
from constraintnet.seeds import kuhn_ball


@pytest.fixture()
def z3():
    return GaussStateZN(kuhn_ball("Z3", n=2))


@pytest.fixture()
def z4():
    return GaussStateZN(kuhn_ball("Z4", n=2))


# ------------------------------------------------------------------ construction
def test_vacuum_is_charge_free(z3):
    assert all(q == 0 for q in z3.charges().values())
    assert z3.check_gauss()
    assert z3.nality()["kind"] == "vacuum"


def test_orientation_convention_is_antisymmetric(z3):
    """Flux +1 on the canonical edge (u<v) means flow u->v: q_u = N-1, q_v = +1."""
    u, w = z3.edges[5]
    assert u < w
    z3.add_flux((u, w), 1)
    q = z3.charges()
    assert q[u] == z3.N - 1 and q[w] == 1
    assert z3.check_gauss()


def test_reversed_flux_swaps_the_pair(z3):
    u, w = z3.edges[5]
    z3.add_flux((u, w), 2)                      # = -1 mod 3
    q = z3.charges()
    assert q[u] == 1 and q[w] == 2


def test_add_then_sub_flux_is_exact_identity(z3):
    rng = random.Random(7)
    snapshot = list(z3.E)
    for _ in range(60):
        e = z3.edges[rng.randrange(len(z3.edges))]
        d = rng.randrange(1, z3.N)
        z3.add_flux(e, d)
        z3.sub_flux(e, d)
    assert z3.E == snapshot


def test_total_charge_vanishes_and_support_is_two_endpoints(z3):
    """PA: sum q = 0 mod N always; a flux update moves charge only at its endpoints."""
    rng = random.Random(11)
    for _ in range(400):
        e = z3.edges[rng.randrange(len(z3.edges))]
        before = z3.charges()
        d = rng.randrange(1, z3.N)
        z3.add_flux(e, d)
        after = z3.charges()
        changed = {v for v in before if before[v] != after[v]}
        assert changed <= set(e), (e, changed)
        assert z3.total_charge() == 0


def test_load_string_respects_edge_orientation(z3):
    """Regression: walking a path forward then backward must cancel exactly in Z_N.

    In Z2 the distinction is invisible (flip is its own inverse); in Z3 ignoring it silently
    doubles flux instead of cancelling it -- and would have made every baryon seed wrong.
    """
    i, j, k = z3.cx.faces()[0]
    z3.load_string([i, j, k], flux=1)
    z3.load_string([k, j, i], flux=1)
    assert all(a == 0 for a in z3.E)
    assert all(q == 0 for q in z3.charges().values())


def test_closed_flux_loop_carries_no_charge(z3):
    """A closed electric loop is neutral flux: charge-free but energetically present.

    This is the abelian 'electric glueball' -- evidence that charge and flux are distinct
    bookkeeping in this model, not synonyms.
    """
    i, j, k = z3.cx.faces()[0]
    z3.load_string([i, j, k, i], flux=1)
    assert all(q == 0 for q in z3.charges().values())
    assert z3.electric_count() > 0.0
    assert z3.nality()["kind"] == "vacuum"


def test_shift_g_inverts_and_restores_curvature(z3):
    base = z3.magnetic_energy_count()
    edges = [z3.edges[i] for i in (0, 4, 9, 13)]
    for e in edges:
        z3.shift_g(e, 1)
    for e in reversed(edges):
        z3.unshift_g(e, 1)
    assert z3.magnetic_energy_count() == base
    snap = {tuple(sorted(k)): v for k, v in z3.cx.labels_snapshot().items()}
    fresh = GaussStateZN(kuhn_ball("Z3", n=2))
    assert snap == {tuple(sorted(k)): v for k, v in fresh.cx.labels_snapshot().items()}


def test_rejects_nonabelian_group():
    with pytest.raises(NotImplementedError):
        GaussStateZN(kuhn_ball("A4", n=1))


# ------------------------------------------------------------------ classifier: hand cases
def test_classifier_meson(z3):
    r = nality_content({0: 1, 5: 2}, 3)
    assert (r["kind"], r["pairs"], r["constituents"]) == ("mesonic", 1, 0)


def test_classifier_baryon_is_neutral_yet_irreducible(z3):
    """THE selection rule: three like charges in Z3 sum to zero but contain no cancelling pair."""
    r = nality_content({0: 1, 3: 1, 8: 1}, 3)
    assert r["total_charge"] == 0
    assert (r["kind"], r["pairs"], r["constituents"]) == ("baryonic", 0, 3)


def test_classifier_antibaryon():
    r = nality_content({1: 2, 2: 2, 3: 2}, 3)
    assert (r["kind"], r["constituents"]) == ("baryonic", 3)


def test_classifier_flags_unreachable_total_charge():
    r = nality_content({0: 1, 1: 1, 2: 2}, 3)          # total = 4 = 1 mod 3
    assert r["kind"] == "charged" and r["total_charge"] == 1


def test_classifier_mixed_pair_plus_baryon():
    """(1,1,1,1,2): one pair cancels, THREE like charges remain -> still baryonic content.

    The residual count is a multiple of 3 here: neutrality forces it, which is exactly the
    arithmetic behind 'confinement to colour singlets' in a Z3 gauge theory.
    """
    r = nality_content({0: 1, 1: 1, 2: 1, 3: 1, 4: 2}, 3)
    assert (r["pairs"], r["constituents"]) == (1, 3)
    assert r["kind"] == "baryonic"


def test_classifier_self_inverse_charge_in_z4(z4):
    """In Z4 the charge 2 is its own antiparticle: pairs cancel in twos, an ODD residue survives.

    [2,2,2,1,3] is neutral (sum 8 = 0 mod 4) yet one charge-2 site cannot be paired away -- so
    irreducible content is not exclusive to odd N; it is the failure of self-duality that matters.
    """
    even = nality_content({0: 2, 1: 2, 2: 1, 3: 3}, 4)   # [2,2,1,3], total 8 = 0 mod 4
    assert (even["kind"], even["pairs"], even["constituents"]) == ("mesonic", 2, 0)
    odd = nality_content({0: 2, 1: 2, 2: 2, 3: 1, 4: 1}, 4)   # [2,2,2,1,1], total 8 = 0 mod 4
    assert (odd["kind"], odd["pairs"], odd["constituents"]) == ("baryonic", 1, 3)


def test_z2_has_no_baryonic_content_ever():
    """PB: exhaustively, every neutral Z2 charge multiset is pair-cancellable.

    This is why E068's confined pair had nothing protecting it: in Z2 conjugation is trivial and
    'particle = antiparticle', so annihilation is always the two-body route.
    """
    for size in range(0, 7):
        for combo in itertools.combinations_with_replacement((1,), size):
            charges = {i: q for i, q in enumerate(combo)}
            if sum(charges.values()) % 2 != 0:
                continue
            r = nality_content(charges, 2)
            assert r["kind"] in ("vacuum", "mesonic"), (combo, r)
            assert r["constituents"] == 0


# ------------------------------------------------------------------ baryon seed
def test_load_star_seeds_an_irreducible_triple(z3):
    interior = [v for v in z3.vertices if v not in z3.boundary_vertices]
    center = interior[0]
    neighbours = sorted({w for (x, w) in z3.edges if x == center} |
                        {x for (x, w) in z3.edges if w == center})
    ends = [v for v in neighbours if v != center][:3]
    assert len(ends) == 3
    z3.load_star(center, ends, flux=1)
    q = z3.charges()
    assert q[center] == 0                       # -3*flux = 0 mod 3: the centre is invisible
    live = {v for v, qq in q.items() if qq}
    assert live == set(ends)
    assert all(q[v] == 1 for v in live)
    assert z3.nality()["kind"] == "baryonic" and z3.is_baryonic()


def test_gauss_holds_through_a_long_z3_run(z3):
    from constraintnet.drivers import DriverGZN
    d = DriverGZN(z3, rng_seed=3, beta_B=6.0, beta_E=2.0)
    for _ in range(150):
        d.advance()
        assert z3.check_gauss()


# ------------------------------------------------------------------ kernel purity + decoupling
def test_no_rng_in_this_kernel_module():
    import inspect
    import constraintnet.gauss_zn as gz
    src = inspect.getsource(gz)
    for token in ("import random", "numpy.random", "random.", "randint", "shuffle"):
        assert token not in src, token


def test_correlation_is_zero_on_vacuum(z3):
    assert charge_curvature_correlation(z3) == 0.0
