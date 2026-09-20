import numpy as np
import pytest
from scipy.linalg import expm

from constraintnet.defect import GaugePatch
from constraintnet.defect_ops import DefectDynamics
from constraintnet.seeds import make_tetrahedron_boundary


def test_matrix_free_projectors_and_evolution_match_independent_dense_operators():
    p = GaugePatch(make_tetrahedron_boundary('Z2'))
    D = DefectDynamics(p)
    H, A, B = p.hamiltonian()
    rng = np.random.default_rng(123)
    state = rng.normal(size=p.dim) + 1j * rng.normal(size=p.dim)
    state /= np.linalg.norm(state)
    for v, matrix in zip(p.vertices, A):
        assert np.linalg.norm(D.star(v, state) - matrix @ state) < 1e-13
    for f, matrix in zip(p.faces, B):
        assert np.linalg.norm(D.plaquette(f, state) - matrix @ state) < 1e-13
    assert np.linalg.norm(D.hamiltonian(state) - H @ state) < 1e-13
    result = D.evolve(state, 0.37)
    assert np.linalg.norm(result - expm(-0.37j * H) @ state) < 1e-12
    assert np.linalg.norm(D.evolve(result, -0.37) - state) < 1e-12


def test_string_path_equality_requires_flatness_and_reversal_inverts_the_unitary():
    D = DefectDynamics(GaugePatch(make_tetrahedron_boundary('Z3')))
    a, b, c = D.patch.vertices[:3]
    char = np.exp(2j * np.pi * np.array(D.patch.els) / 3)
    direct, detour = D.string_factor([a, b], char), D.string_factor([a, c, b], char)
    vacuum = D.flat_vacuum()
    assert np.linalg.norm((direct - detour) * vacuum) < 1e-12
    # They are NOT equal operators on arbitrary curved configurations.
    assert np.max(np.abs(direct - detour)) > 1
    assert np.max(np.abs(direct * D.string_factor([b, a], char) - 1)) < 1e-12
    with pytest.raises(ValueError):
        D.string_factor([a, b], [3, -1, 0])
