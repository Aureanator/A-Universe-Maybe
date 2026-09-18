"""Layer-2 brief item 1: D(A4) modular data, every pass criterion as an assertion.

S unitary; S symmetric; vacuum row d_a/|G|; S^2 = charge conjugation; (ST)^3 = (tau/D)S^2
with tau/D = 1; sum d^2 = 144; Verlinde fusion nonnegative integers with quantum-dimension
homomorphism; pure charges fuse as Rep(A4); the shift rule 1' x F1 = F2; a x abar contains
vacuum exactly once; flux-level class algebra C2^2 = 3C1 + 2C2, C3.C4 = 4C1 + 4C2 exact,
C3^2 support {the other order-3 class} only. Toric-code Z2 control pins the normalization.
"""

import cmath
import itertools

import pytest

from constraintnet.category import (
    AnyonType, charge_conjugation, class_algebra_product, double_sectors,
    fusion_coefficients, quantum_dimensions, s_matrix, sector_report, t_matrix,
)
from constraintnet.groups import AlternatingGroup4, CyclicGroup
from constraintnet.reps import a4_irreps, decompose

OMEGA = cmath.exp(2j * cmath.pi / 3)
TOL = 1e-9


@pytest.fixture(scope="module")
def data():
    return sector_report()


def matmul(A, B):
    n = len(A)
    return [[sum(A[i][k] * B[k][j] for k in range(n)) for j in range(n)] for i in range(n)]


# ------------------------------------------------------------------ sectors

def test_sector_census(data):
    sectors = data["sectors"]
    assert len(sectors) == 14
    assert str(sectors[0]) == "([c0], 1)"                      # vacuum first
    dims = [int(d) for d in quantum_dimensions(sectors)]
    assert dims == [1, 1, 1, 3] + [4] * 6 + [3] * 4            # charges; 3-/3+ dyons; V4 dyons
    assert data["total_quantum_dim_sq"] == pytest.approx(144.0)


# ------------------------------------------------------------------ modular S and T

def test_s_matrix_axioms(data):
    sectors, S = data["sectors"], data["S"]
    n = len(S)
    for i, j in itertools.product(range(n), repeat=2):
        assert abs(S[i][j] - S[j][i]) < 1e-9                   # symmetric
        err = abs(sum(S[i][k] * S[j][k].conjugate() for k in range(n)) - (1 if i == j else 0))
        assert err < 1e-9                                      # unitary
    for j, s in enumerate(sectors):                            # vacuum row = d_a / |G|
        assert abs(S[0][j] - s.quantum_dimension / 12) < 1e-9


def _multiset_eq(values, expected):
    key = lambda z: (round(z.real, 6), round(z.imag, 6))       # noqa: E731
    return sorted(map(key, values)) == sorted(map(key, expected))


def test_t_matrix_structure(data):
    T = data["T"]
    assert all(abs(T[i] - 1) < 1e-9 for i in range(4))         # pure charges are bosons
    for block in (range(4, 7), range(7, 10)):                  # order-3 dyons: {1, w, w^2}
        assert _multiset_eq([T[i] for i in block], [1.0, OMEGA, OMEGA ** 2])
    v4 = [T[i] for i in range(10, 14)]                         # V4 dyons: two +1, two -1
    assert sum(1 for t in v4 if abs(t + 1) < 1e-9) == 2        # fermionic TWIST candidates
    assert sum(1 for t in v4 if abs(t - 1) < 1e-9) == 2


def test_s_squared_is_charge_conjugation(data):
    S, C = data["S"], data["charge_conj"]
    n = len(S)
    assert all(C[C[i]] == i for i in range(n))                 # involution
    S2 = matmul(S, S)
    for i, j in itertools.product(range(n), repeat=2):
        expected = 1.0 if i == C[j] else 0.0
        assert abs(S2[i][j] - expected) < 1e-9


def test_st3_identity_referees_convention(data):
    """(ST)^3 = (tau/D) S^2 with Gauss phase tau/D = 1 for untwisted D(A4).

    This identity is the chirality referee: a symmetric-conjugation variant of the
    S-matrix passes unitarity/symmetry/vacuum-row AND yields identical fusion, yet
    fails this test with error O(1). If someone "simplifies" s_matrix to conjugate
    both factors in the same direction, this is the test that catches them.
    """
    sectors, S, T = data["sectors"], data["S"], data["T"]
    n = len(S)
    d = quantum_dimensions(sectors)
    tau = sum(dd * dd * t for dd, t in zip(d, T))
    D = abs(tau)
    assert abs(D - 12) < 1e-9                                  # |tau| = D (Gauss)
    phase = tau / D
    assert abs(phase - 1) < 1e-9                               # c == 0 mod 8, untwisted
    Tm = [[T[j] if i == j else 0 for j in range(n)] for i in range(n)]
    ST3 = matmul(matmul(matmul(S, Tm), matmul(S, Tm)), matmul(S, Tm))
    S2 = matmul(S, S)
    err = max(abs(ST3[i][j] - phase * S2[i][j]) for i in range(n) for j in range(n))
    assert err < 1e-9


# ------------------------------------------------------------------ fusion ring

def test_verlinde_sanity(data):
    """Nonnegativity/integrality are asserted inside fusion_coefficients; here the ring laws."""
    N, C = data["N"], data["charge_conj"]
    n = len(N)
    d = quantum_dimensions(data["sectors"])
    for a, b in itertools.product(range(n), repeat=2):
        assert abs(d[a] * d[b] - sum(N[c][a][b] * d[c] for c in range(n))) < 1e-9
        for c in range(n):
            assert N[c][a][b] >= 0                             # brief pass criterion
            assert N[c][a][b] == N[c][b][a]                    # commutative ring
    assert all(N[0][i][C[i]] == 1 for i in range(n))           # vacuum once in a x abar


def test_pure_charges_fuse_as_rep_a4(data):
    N = data["N"]
    gA, irreps = a4_irreps()
    for i, j in itertools.product(range(4), repeat=2):
        chi = tuple(a * b for a, b in zip(irreps[i].character, irreps[j].character))
        dec = decompose(gA, irreps, chi)
        for k in range(4):
            assert N[k][i][j] == dec.get(irreps[k].name, 0), (i, j, k)


def test_shift_rule_and_twisted_action(data):
    """1' x F1 = F2 exactly; and rho x ([g],pi) = ([g], pi (x) Res rho) for rho = 3."""
    N, sectors = data["N"], data["sectors"]
    i_1p, i_F1, i_F2 = 1, 5, 6                                 # canonical order
    outs = [k for k in range(14) if N[k][i_F1][i_1p] > 0]
    assert outs == [i_F2] and N[i_F2][i_F1][i_1p] == 1

    g = AlternatingGroup4()
    c1_rep = sectors[4].representative
    pw = [g.identity(), c1_rep, g.multiply(c1_rep, c1_rep)]
    chi3 = {x: float(sum(1 for idx, img in enumerate(x) if img == idx) - 1) for x in pw}
    res = {}
    for k in range(3):                                         # decompose Res_<c1> 3 into Z3 chars
        mult = sum(chi3[x] * (OMEGA ** (-k * j)) for j, x in enumerate(pw)) / 3
        res[f"chi{k}"] = round(mult.real)
    assert res == {"chi0": 1, "chi1": 1, "chi2": 1}            # regular representation
    row = {sectors[k].label: N[k][4][3] for k in range(14) if sectors[k].class_index == 1}
    assert row == res                                          # Verlinde agrees with restriction


# ------------------------------------------------------------------ flux-level class algebra

def test_class_algebra_quoted_rules(data):
    """Class order [id, 3-, 3+, 2] (CONVENTIONS.md). Qwen's quoted rules made exact:

    C2^2 = 3 C1 + 2 C2   -> K[3][3] = (3,0,0,2)
    C3.C4 = 4 C1 + 4 C2  -> K[1][2] = K[2][1] = (4,0,0,4)   (exact: no flux term survives)
    C3^2 support         -> K[1][1] = (0,0,4,0), K[2][2] = (0,4,0,0): squares land in the
                            opposite chirality class only -- no identity term (inverse of a
                            3-cycle never lies in its own class).
    """
    K = data["class_algebra"]
    assert K[3][3] == (3, 0, 0, 2)
    assert K[1][2] == (4, 0, 0, 4) and K[2][1] == (4, 0, 0, 4)
    assert K[1][1] == (0, 0, 4, 0) and K[2][2] == (0, 4, 0, 0)


# ------------------------------------------------------------------ toric-code control

def test_toric_code_Z2_control_pins_normalization():
    """Hand-built D(Z2): the formula must reproduce the exact +-1/2 toric S-matrix.

    This pins the |C||D|/|G|^2 prefactor: the (1/|G|) variant quoted loosely in older
    notes gives a vacuum row of dim(pi) and fails here for any nontrivial flux sector.
    """
    Z2 = CyclicGroup(2)
    e = Z2.identity()
    s_el = next(x for x in Z2.elements if x != e)
    cent = tuple(sorted(Z2.elements))

    def cd(f):
        return {x: complex(f(x)) for x in Z2.elements}

    triv, sign = (lambda x: 1), (lambda x: 1 if x == e else -1)
    sec = (
        AnyonType(0, "1", e, frozenset({e}), cent, cd(triv), 1),
        AnyonType(0, "sgn", e, frozenset({e}), cent, cd(sign), 1),
        AnyonType(1, "m", s_el, frozenset({s_el}), cent, cd(triv), 1),
        AnyonType(1, "eps", s_el, frozenset({s_el}), cent, cd(sign), 1),
    )
    S = s_matrix(sec, Z2)
    expected = [[0.5, 0.5, 0.5, 0.5], [0.5, 0.5, -0.5, -0.5],
                [0.5, -0.5, 0.5, -0.5], [0.5, -0.5, -0.5, 0.5]]
    assert max(abs(S[i][j] - expected[i][j]) for i in range(4) for j in range(4)) < 1e-12
