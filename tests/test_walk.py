"""v4.0 walk: identities (P19a), DF cycle states and dispersion (P19b), holonomy (P19d)."""

import numpy as np

from constraintnet.gauge import gauge_transform
from constraintnet.seeds import kuhn_ball, randomize_labels
from constraintnet.walk import ArcWalk, a4_irrep3
from examples.p19_walk import block, STAR, RINGW


def test_closed_walk_unitary_gauge_covariant_and_szegedy():
    cx = kuhn_ball("A4", n=3)
    w = ArcWalk(cx, mode="closed")
    U = w.matrix()
    assert np.abs(U.conj().T @ U - np.eye(len(U))).max() < 1e-12
    lam = np.linalg.eigvalsh(w.discriminant())
    ev = np.linalg.eigvals(U)
    for th in np.arccos(np.clip(lam, -1, 1)):
        assert np.abs(ev - np.exp(1j * th)).min() < 1e-6
    rep = a4_irrep3(cx.group)
    rl = cx.copy(); randomize_labels(rl, seed=11)
    rg = rl.copy()
    gauge_transform(rg, {v: cx.group.elements[(3 * v + 1) % 12] for v in rg.vertices()})
    e1 = np.sort_complex(np.round(np.linalg.eigvals(ArcWalk(rl, rep=rep, dim=3, mode="closed").matrix()), 7))
    e2 = np.sort_complex(np.round(np.linalg.eigvals(ArcWalk(rg, rep=rep, dim=3, mode="closed").matrix()), 7))
    assert np.abs(e1 - e2).max() < 1e-6


def test_open_walk_never_increases_norm():
    cx = kuhn_ball("A4", n=3); randomize_labels(cx, seed=2)
    Uo = ArcWalk(cx, rep=a4_irrep3(cx.group), dim=3, mode="open").matrix()
    assert np.linalg.norm(Uo, 2) <= 1 + 1e-12


def test_momentum_block_dispersion_and_flat_bands():
    D = np.array(STAR, float); wt = np.array([RINGW[s] for s in STAR])
    for k in np.random.default_rng(0).uniform(-np.pi, np.pi, (30, 3)):
        U, _, _ = block(k)
        ev = np.linalg.eigvals(U)
        assert int(np.sum(np.minimum(abs(ev - 1), abs(ev + 1)) < 1e-9)) == 12
        th = np.arccos((wt * np.cos(D @ k)).sum() / wt.sum())
        assert np.abs(ev - np.exp(1j * th)).min() < 1e-9


def test_df_compact_cycle_state_with_random_labels():
    cx = kuhn_ball("A4", n=4); randomize_labels(cx, seed=4)
    rep = a4_irrep3(cx.group)
    wk = ArcWalk(cx, rep=rep, dim=3, mode="closed")
    grid = {tuple(cx.vertex(v).metadata["grid"]): v for v in cx.vertices()}
    cyc = [grid[(1, 1, 2)], grid[(2, 1, 2)], grid[(2, 2, 2)], grid[(1, 2, 2)]]
    Tr = np.eye(3)
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
        Tr = rep(cx.label(b, a)) @ Tr
    evs, V = np.linalg.eig(Tr)
    x = np.real(V[:, np.argmin(abs(evs - 1))]); x /= np.linalg.norm(x)
    psi = np.zeros((len(wk.arcs), 3), complex)
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
        psi[wk.index[(a, b)]] = x
        psi[wk.index[(b, a)]] = -rep(cx.label(b, a)) @ x
        x = rep(cx.label(b, a)) @ x
    assert np.abs(wk.step(psi) - psi).max() < 1e-12


def test_record_walk_is_exactly_reversible():
    from constraintnet.walk import RecordWalk
    cx = kuhn_ball("A4", n=4); randomize_labels(cx, seed=3)
    rw = RecordWalk(cx, kappa=0.0, mode="closed")
    rng = np.random.default_rng(0)
    psi = rng.normal(size=(len(rw.walk.arcs), 3)) + 1j * rng.normal(size=(len(rw.walk.arcs), 3))
    psi /= np.linalg.norm(psi)
    p0, l0, n = psi.copy(), rw.lab.copy(), 0
    for _ in range(20):
        psi, c = rw.step(psi); n += c
    assert n > 0
    for _ in range(20):
        psi = rw.unstep(psi)
    assert np.abs(psi - p0).max() < 1e-12 and np.array_equal(rw.lab, l0)
