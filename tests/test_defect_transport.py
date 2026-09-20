import numpy as np
import pytest
from scipy.linalg import expm

from constraintnet.defect import GaugePatch
from constraintnet.defect_ops import DefectDynamics
from constraintnet.defect_transport import Z2DefectTransport
from constraintnet.seeds import make_single_tetrahedron


def pauli_product(operators):
    out = np.ones((1, 1))
    for operator in operators:
        out = np.kron(out, operator)
    return out


def test_full_hilbert_transport_against_independent_pauli_construction():
    p = GaugePatch(make_single_tetrahedron('Z2'))
    D = DefectDynamics(p)
    T = Z2DefectTransport(D)
    eye, x, z = np.eye(2), np.array([[0, 1], [1, 0]]), np.diag([1, -1])
    I = np.eye(p.dim)
    S = {v: pauli_product([x if v in e else eye for e in p.edges]) for v in p.vertices}
    N = sum((I - s) / 2 for s in S.values())
    K = np.zeros((p.dim, p.dim))
    rng = np.random.default_rng(3202)
    psi = rng.normal(size=p.dim) + 1j * rng.normal(size=p.dim)
    psi /= np.linalg.norm(psi)
    for index, edge in enumerate(p.edges):
        W = pauli_product([z if i == index else eye for i in range(len(p.edges))])
        a, b = edge
        hop = W @ (I - S[a] @ S[b]) / 2
        assert np.linalg.norm(T.hop(edge, psi) - hop @ psi) < 1e-12
        assert np.linalg.norm(hop - hop.T) < 1e-12
        K -= T.kappa * hop
    H0, _, B = p.hamiltonian()
    assert np.linalg.norm(T.kinetic(psi) - K @ psi) < 1e-12
    assert np.linalg.norm(T.number(psi) - N @ psi) < 1e-12
    assert np.linalg.norm(K @ N - N @ K) < 1e-12
    assert np.linalg.norm(K @ H0 - H0 @ K) < 1e-12
    assert all(np.linalg.norm(K @ b - b @ K) < 1e-12 for b in B)
    assert np.linalg.norm(K @ S[0] - S[0] @ K) > 1
    assert max(map(abs, T.continuity_residual(psi).values())) < 1e-12
    # Nonzero current and a finite-difference density derivative are independent
    # guards against a current implementation that returns zero or reverses sign.
    assert max(map(abs, T.currents(psi).values())) > 1e-3
    dt = 1e-5
    plus, minus = expm(-1j * dt * (H0 + K)) @ psi, expm(1j * dt * (H0 + K)) @ psi
    for v in p.vertices:
        n = (I - S[v]) / 2
        rate = (np.vdot(plus, n @ plus).real - np.vdot(minus, n @ minus).real) / (2 * dt)
        div = sum(j if a == v else -j if b == v else 0
                  for (a, b), j in T.currents(psi).items())
        assert abs(rate + div) < 1e-9


def test_transport_moves_charge_but_does_not_annihilate_a_pair_or_leave_vacuum():
    D = DefectDynamics(GaugePatch(make_single_tetrahedron('Z2')))
    T = Z2DefectTransport(D)
    vacuum = D.flat_vacuum()
    pair = D.string_factor([0, 1], [1, -1]) * vacuum
    target = D.string_factor([0, 2], [1, -1]) * vacuum
    assert np.linalg.norm(T.hop((1, 2), pair) - target) < 1e-12
    assert np.linalg.norm(T.hop((0, 1), pair)) < 1e-12
    assert np.linalg.norm(T.kinetic(vacuum)) < 1e-12
    assert np.linalg.norm(T.hop((2, 1), pair) - target) < 1e-12
    assert np.linalg.norm(T.directed_hop(2, 1, pair) - target) < 1e-12
    assert np.linalg.norm(T.directed_hop(1, 2, pair)) < 1e-12
    with pytest.raises(ValueError):
        Z2DefectTransport(DefectDynamics(GaugePatch(make_single_tetrahedron('Z3'))))
    with pytest.raises(ValueError):
        Z2DefectTransport(D, kappa=np.nan)
    with pytest.raises(ValueError):
        T.currents(np.zeros_like(vacuum))
