"""P28: what a compact loop can do instead of circulating (PREDICTIONS P28).

Finds the exact compact (loop-supported) invariant subspace of the flat walk, its phases and
dimensions, checks the 1/sqrt(weight) amplitude law, currents, the 0/pi superposition's exact
2-periodicity, and the internal return period on odd loops.
Reproduce: python examples/p28_compact.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from constraintnet.current import cycle_transport, transport_current
from constraintnet.seeds import kuhn_ball, randomize_labels
from constraintnet.walk import ArcWalk, a4_irrep3

N, DRAWS = 4, 20
OUT = ROOT / "reference/opus_session/data/p28_compact.json"


def loops(cx):
    G = {tuple(cx.vertex(v).metadata["grid"]): v for v in cx.vertices()}
    cand = {"triangle_L3": [(1, 1, 1), (2, 1, 1), (2, 2, 1)],
            "axis_square_L4": [(1, 1, 2), (2, 1, 2), (2, 2, 2), (1, 2, 2)],
            "diag_square_L4": [(1, 2, 3), (2, 3, 3), (2, 2, 2), (1, 1, 2)],
            "mixed_L5": [(1, 1, 1), (2, 1, 1), (2, 2, 1), (2, 2, 2), (1, 1, 1)]}
    edges = {tuple(sorted(e)) for e in cx.edges()}
    out = {}
    for name, pts in cand.items():
        vs = [G[p] for p in pts]
        if len(set(vs)) != len(vs):
            continue
        if all(tuple(sorted((a, b))) in edges for a, b in zip(vs, vs[1:] + vs[:1])):
            out[name] = vs
    return out


def odd_cycle(cx, length=5):
    """Shortest search for a chordless-enough simple cycle of the given odd length."""
    nb = {v: set() for v in cx.vertices()}
    for a, b in cx.edges():
        nb[a].add(b); nb[b].add(a)
    interior = set(ArcWalk(cx, dim=1, mode="closed").interior)
    nb = {v: (s & interior) for v, s in nb.items() if v in interior}
    start = min(nb)
    stack = [[start]]
    while stack:
        path = stack.pop()
        if len(path) == length:
            if path[0] in nb[path[-1]]:
                return path
            continue
        for u in sorted(nb[path[-1]] & interior):
            if u not in path and u > start:
                stack.append(path + [u])
    return None


def loop_arcs(w, cyc):
    steps = list(zip(cyc, cyc[1:] + cyc[:1]))
    fwd = [w.index[(a, b)] for a, b in steps]
    bwd = [w.index[(b, a)] for a, b in steps]
    return steps, fwd, bwd


def compact_subspace(w, cyc, tol=1e-9):
    """The maximal U-invariant subspace supported on the loop's arcs, then diagonalised.

    Iterate S <- {v in S : U v has no weight off the loop and stays in S} to a fixed point.
    """
    steps, fwd, bwd = loop_arcs(w, cyc)
    arcs = fwd + bwd
    dim = len(arcs) * 3
    basis = []
    for a in arcs:
        for i in range(3):
            e = np.zeros((len(w.arcs), 3), complex)
            e[a, i] = 1
            basis.append(e)
    img = [w.step(b) for b in basis]
    inside = np.zeros((dim, dim), complex)
    outside = np.zeros((3 * (len(w.arcs) - len(arcs)), dim), complex)
    for j, m in enumerate(img):
        inside[:, j] = np.concatenate([m[a] for a in arcs])
        outside[:, j] = np.delete(m, arcs, axis=0).reshape(-1)
    Q = np.eye(dim, dtype=complex)
    while Q.shape[1]:
        leak = outside @ Q
        stay = (np.eye(dim) - Q @ Q.conj().T) @ (inside @ Q)
        A = np.vstack([leak, stay])
        _, sv, vh = np.linalg.svd(A)
        rank = int(np.sum(sv > tol * max(1.0, sv[0] if sv.size else 1.0)))
        if rank == 0:
            break
        Q = Q @ vh[rank:].conj().T
        if Q.shape[1] == 0:
            break
        Q, _ = np.linalg.qr(Q)
    if Q.shape[1] == 0:
        return [], basis, arcs
    block = Q.conj().T @ inside @ Q
    ev, vec = np.linalg.eig(block)
    states = []
    for lam, col in zip(ev, vec.T):
        coeff = Q @ col
        psi = sum(c * b for c, b in zip(coeff, basis))
        psi = psi / np.linalg.norm(psi)
        states.append((complex(lam), psi))
    return states, basis, arcs


def holonomy(cx, rep, cyc):
    H = np.eye(3)
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
        H = rep(cx.label(b, a)) @ H        # transport a->b, matching ArcWalk
    return H


def analyse(name, cyc, seed):
    cx = kuhn_ball("A4", n=N)
    if seed is not None:
        randomize_labels(cx, seed=seed)
    rep = a4_irrep3(cx.group)
    w = ArcWalk(cx, rep=rep, dim=3, mode="closed")
    L = len(cyc)
    H = holonomy(cx, rep, cyc)
    evH = np.linalg.eigvals(H)
    states, _, arcs = compact_subspace(w, cyc)
    phases = sorted(float(np.angle(l)) for l, _ in states)
    res = max((float(np.abs(w.step(p) - l * p).max()) for l, p in states), default=0.0)
    d0 = int(np.sum(np.abs(evH - 1) < 1e-9))
    dpi = int(np.sum(np.abs(evH - (-1) ** L) < 1e-9))
    got0 = sum(1 for l, _ in states if abs(np.angle(l)) < 1e-9)
    gotpi = sum(1 for l, _ in states if abs(abs(np.angle(l)) - np.pi) < 1e-9)
    row = {"loop": name, "L": L, "seed": seed, "n_compact": len(states),
           "phases_are_0_or_pi": bool(all(min(abs(p), abs(abs(p) - np.pi)) < 1e-9 for p in phases)),
           "max_eigen_residual": res, "dim_theta0": got0, "dim_thetapi": gotpi,
           "predicted_dim_theta0": d0, "predicted_dim_thetapi": dpi,
           "holonomy_order": int(cx.group.order_of(_hol_element(cx, cyc)))}
    # amplitude law and currents
    steps, fwd, bwd = loop_arcs(w, cyc)
    wts = np.array([w.weights[a] for a in fwd])
    amp_dev, cur = [], []
    for lam, psi in states:
        mag = np.array([np.linalg.norm(psi[a]) for a in fwd])
        scaled = mag * np.sqrt(wts)
        amp_dev.append(float(scaled.std() / scaled.mean()) if scaled.mean() > 1e-12 else 0.0)
        out, _ = transport_current(w, psi)
        cur.append(abs(cycle_transport(w, out, cyc)["bias"]))
    row["max_sqrtw_amplitude_deviation"] = max(amp_dev, default=0.0)
    row["max_eigenstate_current_bias"] = max(cur, default=0.0)
    # superposition of a theta=0 and a theta=pi state on the same loop
    z = [p for l, p in states if abs(np.angle(l)) < 1e-9]
    pi_ = [p for l, p in states if abs(abs(np.angle(l)) - np.pi) < 1e-9]
    if z and pi_:
        psi = (z[0] + pi_[0]) / np.sqrt(2)
        psi /= np.linalg.norm(psi)
        biases = []
        st = psi.copy()
        for t in range(4):
            out, _ = transport_current(w, st)
            biases.append(cycle_transport(w, out, cyc)["bias"])
            st = w.step(st)
        row["superposition_period2_error"] = float(np.abs(st - w.step(w.step(psi))).max()
                                                   + np.abs(w.step(w.step(psi)) - psi).max())
        row["superposition_biases"] = [float(b) for b in biases]
        row["superposition_two_tick_mean"] = float(abs(biases[0] + biases[1]) / 2)
    # internal return after one traversal, for the theta=pi states
    if pi_:
        a0 = pi_[0][fwd[0]]
        row["internal_return"] = float(np.real(np.vdot(a0, H @ a0) / np.vdot(a0, a0)))
    return row


def _hol_element(cx, cyc):
    g = cx.group
    h = g.identity()
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
        h = g.multiply(cx.label(b, a), h)
    return h


def main():
    cx = kuhn_ball("A4", n=N)
    L = loops(cx)
    five = odd_cycle(cx, 5)
    if five:
        L["found_L5"] = five
    rows = []
    for name, cyc in L.items():
        for seed in [None] + list(range(1, DRAWS + 1)):
            rows.append(analyse(name, cyc, seed))
        r = rows[-1]
        print(name, len(cyc), "phases0/pi ok", all(x["phases_are_0_or_pi"] for x in rows if x["loop"] == name),
              "dims match", all(x["dim_theta0"] == x["predicted_dim_theta0"] and
                                x["dim_thetapi"] == x["predicted_dim_thetapi"] for x in rows if x["loop"] == name),
              "max resid", max(x["max_eigen_residual"] for x in rows if x["loop"] == name), flush=True)
    OUT.write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
