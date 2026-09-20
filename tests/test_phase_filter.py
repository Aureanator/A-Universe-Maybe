import numpy as np
import pytest

from constraintnet.phase_filter import eigen_residual, phase_averages


def test_phase_filter_agrees_with_exact_spectral_window_and_telescoping_identity():
    rng = np.random.default_rng(21)
    Q, _ = np.linalg.qr(rng.normal(size=(7, 7)) + 1j * rng.normal(size=(7, 7)))
    angles = np.array([0.0, 0.0, 0.37, -0.9, 1.8, 2.4, -2.1])
    U = (Q * np.exp(1j * angles)) @ Q.conj().T
    psi = rng.normal(size=7) + 1j * rng.normal(size=7)
    psi /= np.linalg.norm(psi)
    phases = [0.0, 0.37, 0.71]
    for T, states in phase_averages(lambda x: U @ x, psi, phases, [1, 11, 67]):
        for phase, state in zip(phases, states):
            window = np.exp(1j * np.outer(np.arange(T), angles - phase)).mean(axis=0)
            exact = Q @ (window * (Q.conj().T @ psi))
            assert np.linalg.norm(state - exact) < 1e-13
            z = np.exp(1j * phase)
            rhs = z * (z ** (-T) * np.linalg.matrix_power(U, T) @ psi - psi) / T
            assert np.linalg.norm(U @ state - z * state - rhs) < 1e-13
            report, _ = eigen_residual(lambda x: U @ x, state, phase)
            assert report['target_residual'] <= 2 / (T * np.linalg.norm(state)) + 1e-13


def test_stationary_ray_at_nonzero_phase_survives_only_the_matching_filter():
    phase = 2 * np.pi / 8
    step = lambda x: np.exp(1j * phase) * x
    psi = np.array([1.0, 0.0])
    _, (zero, matched) = next(phase_averages(step, psi, [0.0, phase], [8]))
    assert np.linalg.norm(zero) < 1e-14
    assert np.linalg.norm(matched - psi) < 1e-14
    report, _ = eigen_residual(step, matched, phase)
    assert report['target_residual'] < 1e-14


def test_small_residual_does_not_certify_spatial_localization():
    # A spatially uniform eigenvector passes stationarity perfectly.
    psi = np.ones(20) / np.sqrt(20)
    report, _ = eigen_residual(lambda x: x.copy(), psi, 0.0)
    assert report['target_residual'] < 1e-14
    assert abs(abs(psi[0]) ** 2 - 0.05) < 1e-14
    with pytest.raises(ValueError):
        next(phase_averages(lambda x: x, psi, [0.0], [3, 2]))
    with pytest.raises(ValueError):
        eigen_residual(lambda x: x, np.zeros(2), 0.0)


def test_dressed_controls_and_open_embedding_on_small_quantum_record():
    from constraintnet.qrecord import QuantumRecordWalk
    from constraintnet.seeds import kuhn_ball
    from examples.p26_dressed import df_branches, embed_closed, flat_step, loop_distances

    cx = kuhn_ball("A4", n=4)
    coords = {tuple(cx.vertex(v).metadata['grid']): v for v in cx.vertices()}
    cycle = [coords[p] for p in [(1, 1, 2), (2, 1, 2), (2, 2, 2), (1, 2, 2)]]
    edges = list(zip(cycle[:2], cycle[1:3]))
    Q = QuantumRecordWalk(cx, edges, 0.1, 0.1)
    df, mask = df_branches(Q, cycle)
    psi = df * Q.vac[None, :, None]
    assert np.linalg.norm(Q.walk_step(psi) - psi) < 1e-12
    i0 = np.ravel_multi_index((Q.e_id,) * Q.k, (12,) * Q.k)
    free = df[:, i0, :][:, None, :] * Q.vac[None, :, None]
    z = np.vdot(Q.vac, Q.apply_rec(Q.vac[None, :, None])[0, :, 0])
    assert np.linalg.norm(flat_step(Q, free) - z * free) < 1e-12
    Qo = QuantumRecordWalk(cx, edges, 0.1, 0.1, mode='open')
    opened = embed_closed(Q.walk, Qo.walk, psi)
    assert abs(np.linalg.norm(opened) - np.linalg.norm(psi)) < 1e-14
    # Cancellation on a compact loop makes its first tick boundary-independent.
    assert np.linalg.norm(Qo.step(opened) - embed_closed(Q.walk, Qo.walk, Q.step(psi))) < 1e-12
    distances = loop_distances(cx, cycle, Q.walk.arcs)
    assert np.all(distances[mask] == 0)
    assert np.max(distances) > 0
