import numpy as np

from constraintnet.qrecord import QuantumRecordWalk
from constraintnet.seeds import kuhn_ball
from constraintnet.walk import ArcWalk, a4_irrep3


def _setup():
    cx = kuhn_ball("A4", n=4)
    G = {tuple(cx.vertex(v).metadata["grid"]): v for v in cx.vertices()}
    q = [(G[(1, 1, 1)], G[(2, 1, 1)]), (G[(2, 1, 1)], G[(2, 2, 1)])]
    w = ArcWalk(cx, dim=1, mode="closed")
    rng = np.random.default_rng(1)
    psi = rng.normal(size=(len(w.arcs), 3)) + 1j * rng.normal(size=(len(w.arcs), 3))
    return cx, q, psi / np.linalg.norm(psi)


def test_quantum_record_is_unitary_reversible_and_vacuum_stationary():
    cx, q, psi = _setup()
    Q = QuantumRecordWalk(cx, q, 0.4, 1.0)
    Ur = Q.rec_matrix()
    assert np.abs(Ur.conj().T @ Ur - np.eye(Q.nc)).max() < 1e-12
    assert abs(abs(Q.vac.conj() @ Ur @ Q.vac) - 1) < 1e-12
    P0 = Q.product_state(psi)
    P = P0
    for _ in range(25):
        P = Q.step(P)
    assert abs(np.linalg.norm(P) - 1) < 1e-12
    for _ in range(25):
        P = Q.unstep(P)
    assert np.abs(P - P0).max() < 1e-12


def test_zero_electric_coupling_is_v40_and_labels_follow_walk_convention():
    cx, q, psi = _setup()
    Q = QuantumRecordWalk(cx, q, 0.0, 1.0)
    wk = ArcWalk(cx, rep=a4_irrep3(cx.group), dim=3, mode="closed")
    i0 = np.ravel_multi_index((Q.e_id,) * Q.k, (12,) * Q.k)
    P, p = Q.product_state(psi), psi.copy()
    for _ in range(15):
        P, p = Q.step(P), wk.step(p)
    assert np.abs(P[:, i0] - p).max() < 1e-12
    el = list(cx.group.elements)[7]
    cx2 = kuhn_ball("A4", n=4)
    cx2.set_label(*sorted(q[1]), el)
    wk2 = ArcWalk(cx2, rep=a4_irrep3(cx.group), dim=3, mode="closed")
    lab = [Q.e_id] * Q.k
    lab[1] = Q.eidx[el]
    ic = np.ravel_multi_index(tuple(lab), (12,) * Q.k)
    P = np.zeros_like(P); P[:, ic] = psi; p = psi.copy()
    for _ in range(15):
        P, p = Q.walk_step(P), wk2.step(p)
    assert np.abs(P[:, ic] - p).max() < 1e-12


def test_open_mode_matches_v40_open_and_bookkeeps_escape():
    cx, q, _ = _setup()
    Q = QuantumRecordWalk(cx, q, 0.0, 1.0, mode="open")
    wk = ArcWalk(cx, rep=a4_irrep3(cx.group), dim=3, mode="open")
    rng = np.random.default_rng(3)
    psi = rng.normal(size=(len(wk.arcs), 3)) + 0j
    psi /= np.linalg.norm(psi)
    i0 = np.ravel_multi_index((Q.e_id,) * Q.k, (12,) * Q.k)
    P, p = Q.product_state(psi), psi.copy()
    for _ in range(15):
        P, p = Q.step(P), wk.step(p)
    assert np.abs(P[:, i0] - p).max() < 1e-12
    Qd = QuantumRecordWalk(cx, q, 0.5, 1.0, mode="open")
    P, gone = Qd.product_state(psi), 0.0
    for _ in range(40):
        P = Qd.step(P)
        gone += float((np.abs(Qd.escaped) ** 2).sum())
    assert abs(float((np.abs(P) ** 2).sum()) + gone - 1) < 1e-12
