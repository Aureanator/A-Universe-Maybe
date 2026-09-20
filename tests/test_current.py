import numpy as np
import pytest

from constraintnet.current import continuity_residual, cycle_transport, transport_current
from constraintnet.gauge import gauge_transform
from constraintnet.qrecord import QuantumRecordWalk
from constraintnet.seeds import kuhn_ball, randomize_labels
from constraintnet.walk import ArcWalk, a4_irrep3


@pytest.mark.parametrize('mode', ['closed', 'open'])
def test_current_obeys_local_quantum_record_continuity_and_boundary_accounting(mode):
    cx = kuhn_ball('A4', n=3)
    coords = {tuple(cx.vertex(v).metadata['grid']): v for v in cx.vertices()}
    edge = (coords[1, 1, 1], coords[2, 1, 1])
    Q = QuantumRecordWalk(cx, [edge], 0.1, 0.1, mode=mode)
    rng = np.random.default_rng(37)
    psi = rng.normal(size=(len(Q.walk.arcs), Q.nc, 3)) + 1j * rng.normal(size=(len(Q.walk.arcs), Q.nc, 3))
    psi /= np.linalg.norm(psi)
    for _ in range(3):
        outgoing, current = transport_current(Q.walk, psi)
        after = Q.step(psi)
        assert np.max(np.abs(continuity_residual(Q.walk, psi, after, current))) < 1e-13
        assert np.max(np.abs(current[Q.walk.kept] + current[Q.walk.target[Q.walk.kept]])) < 1e-14
        escaped = 0 if Q.escaped is None else np.sum(np.abs(Q.escaped) ** 2)
        assert abs(outgoing[~Q.walk.kept].sum() - escaped) < 1e-13
        psi = after


def test_probability_current_is_invariant_under_local_internal_frames():
    cx = kuhn_ball('A4', n=3)
    randomize_labels(cx, seed=7)
    rep = a4_irrep3(cx.group)
    frames = {v: cx.group.elements[(3 * v + 2) % 12] for v in cx.vertices()}
    other = cx.copy()
    gauge_transform(other, frames)
    w = ArcWalk(cx, rep=rep, dim=3, mode='closed')
    wg = ArcWalk(other, rep=rep, dim=3, mode='closed')
    rng = np.random.default_rng(19)
    psi = rng.normal(size=(len(w.arcs), 3)) + 1j * rng.normal(size=(len(w.arcs), 3))
    psi /= np.linalg.norm(psi)
    # Norm invariance holds for either convention; use rho(g_v)^-1 here.
    transformed = np.array([rep(frames[v]).T @ psi[i] for i, (v, _) in enumerate(w.arcs)])
    q, j = transport_current(w, psi)
    qg, jg = transport_current(wg, transformed)
    assert np.max(np.abs(q - qg)) < 1e-14
    assert np.max(np.abs(j - jg)) < 1e-14


def test_cycle_bias_detects_direction_and_reverses_with_cycle_orientation():
    cx = kuhn_ball('A4', n=3)
    coords = {tuple(cx.vertex(v).metadata['grid']): v for v in cx.vertices()}
    cycle = [coords[p] for p in [(1, 1, 1), (2, 1, 1), (2, 2, 1), (1, 2, 1)]]
    w = ArcWalk(cx, mode='closed')
    # Prepare an amplitude whose COINED state travels only in the chosen direction.
    coined = np.zeros((len(w.arcs), 1), complex)
    for a, b in zip(cycle, cycle[1:] + cycle[:1]):
        coined[w.index[a, b], 0] = 0.5
    ov = np.add.reduceat(w.phi[:, None] * coined, w.starts, axis=0)
    psi = 2 * w.phi[:, None] * ov[w.vertex_of_arc] - coined
    outgoing, _ = transport_current(w, psi)
    forward = cycle_transport(w, outgoing, cycle)
    backward = cycle_transport(w, outgoing, list(reversed(cycle)))
    assert abs(forward['bias'] - 1) < 1e-14
    assert abs(backward['bias'] + 1) < 1e-14
    assert abs(forward['traffic'] - 1) < 1e-14


def test_exact_compact_branch_eigenrays_have_zero_current_despite_nontrivial_transport():
    from examples.p25_seeded import df_branches

    cx = kuhn_ball('A4', n=3)
    coords = {tuple(cx.vertex(v).metadata['grid']): v for v in cx.vertices()}
    cycle = [coords[p] for p in [(1, 1, 1), (2, 1, 1), (2, 2, 1), (1, 2, 1)]]
    Q = QuantumRecordWalk(cx, [(cycle[0], cycle[1])], 0.0, 0.1)
    df, mask = df_branches(Q, cycle)
    # Check the no-current theorem's exit assumption for this fixture.
    for v in cycle:
        assert any(a == v and not mask[i] and Q.walk.phi[i] > 0
                   for i, (a, _) in enumerate(Q.walk.arcs))
    for c in range(Q.nc):
        psi = np.zeros_like(df)
        psi[:, c, :] = df[:, c, :]
        phase = np.exp(-1j * 0.1 * Q.W[c])
        assert np.linalg.norm(Q.step(psi) - phase * psi) < 1e-12
        outgoing, current = transport_current(Q.walk, psi)
        assert np.max(np.abs(current)) < 1e-12
        assert abs(cycle_transport(Q.walk, outgoing, cycle)['traffic'] - 1) < 1e-12
