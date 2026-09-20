"""P19: first tests of the v4.0 implication walk (docs/DYNAMICS_DESIGN.md; PREDICTIONS P19 + A1, A2).

Run parts separately: python examples/p19_walk.py a|b|c|d|e_exact|e_time
Results go to reference/opus_session/data/p19_<part>.json.
"""

import itertools
import json
import sys
import time
from fractions import Fraction as Q
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from constraintnet.curvature import CurvatureState
from constraintnet.gauge import gauge_transform
from constraintnet.seeds import kuhn_ball, randomize_labels
from constraintnet.walk import ArcWalk, a4_irrep3

OUT = ROOT / "reference/opus_session/data"
STAR = [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (1, 1, 1)]
STAR = STAR + [tuple(-x for x in s) for s in STAR]
RINGW = {s: (0.5 if sorted(map(abs, s)) == [0, 1, 1] else 1.0) for s in STAR}


def save(name, obj):
    (OUT / f"p19_{name}.json").write_text(json.dumps(obj, indent=1, default=float) + "\n", encoding="utf-8")
    print(json.dumps(obj, indent=1, default=float)[:3000], flush=True)


# ------------------------------------------------------------------ a: identities
def part_a():
    res = []
    for n in (3, 4):
        cx = kuhn_ball("A4", n=n)
        row = {"n": n}
        w = ArcWalk(cx, mode="closed")
        U = w.matrix()
        row["closed_arcs"] = len(w.arcs)
        row["closed_unitarity"] = float(np.abs(U.conj().T @ U - np.eye(len(U))).max())
        lam = np.linalg.eigvalsh(w.discriminant())
        th = np.arccos(np.clip(lam, -1, 1))
        pred = list(np.exp(1j * th)) + list(np.exp(-1j * th))
        ev = list(np.linalg.eigvals(U))
        worst = 0.0
        for p in pred:
            j = int(np.argmin(np.abs(np.array(ev) - p))); worst = max(worst, abs(ev[j] - p)); ev.pop(j)
        ev = np.array(ev)
        row["szegedy_max_mismatch"] = float(worst)
        row["remainder_all_pm1"] = bool(np.all(np.minimum(abs(ev - 1), abs(ev + 1)) < 1e-8))
        # gauge covariance with random labels, A4 3-dim irrep
        g = cx.group
        rep = a4_irrep3(g)
        rl = cx.copy(); randomize_labels(rl, seed=11)
        U1 = ArcWalk(rl, rep=rep, dim=3, mode="closed").matrix()
        rng = np.random.default_rng(5)
        els = list(g.elements)
        lambdas = {v: els[rng.integers(len(els))] for v in rl.vertices()}
        rg = rl.copy(); gauge_transform(rg, lambdas)
        U2 = ArcWalk(rg, rep=rep, dim=3, mode="closed").matrix()
        e1 = np.sort_complex(np.round(np.linalg.eigvals(U1), 8)); e2 = np.sort_complex(np.round(np.linalg.eigvals(U2), 8))
        row["gauge_spectrum_max_diff"] = float(np.abs(e1 - e2).max())
        row["irrep_unitarity"] = float(np.abs(U1.conj().T @ U1 - np.eye(len(U1))).max())
        wo = ArcWalk(rl, rep=rep, dim=3, mode="open")
        Uo = wo.matrix()
        row["open_norm"] = float(np.linalg.norm(Uo, 2))
        row["open_spectral_radius"] = float(np.abs(np.linalg.eigvals(Uo)).max())
        res.append(row)
    save("a", res)


# ------------------------------------------------------------------ b: momentum blocks, DF
def block(k, w=RINGW):
    D = np.array(STAR, float)
    wt = np.array([w[s] for s in STAR])
    phi = np.sqrt(wt / wt.sum())
    C = 2 * np.outer(phi, phi) - np.eye(14)
    P = np.zeros((14, 14), complex)
    for i, s in enumerate(STAR):
        j = STAR.index(tuple(-x for x in s))
        P[j, i] = np.exp(-1j * np.dot(k, s))
    return P @ C, D, wt


def part_b():
    out = {}
    rng = np.random.default_rng(2)
    ks = rng.uniform(-np.pi, np.pi, size=(300, 3))
    worst, flat_ok = 0.0, True
    for k in ks:
        U, D, wt = block(k)
        ev = np.linalg.eigvals(U)
        lam = (wt * np.cos(D @ k)).sum() / wt.sum()
        th = np.arccos(lam)
        nontriv = sorted(ev, key=lambda z: min(abs(z - 1), abs(z + 1)))[-2:]
        worst = max(worst, min(abs(nontriv[0] - np.exp(1j * th)), abs(nontriv[0] - np.exp(-1j * th))))
        flat_ok &= int(np.sum(np.minimum(abs(ev - 1), abs(ev + 1)) < 1e-9)) == 12
    out["block_theta_vs_arccos_lambda_max_err"] = float(worst)
    out["twelve_flat_eigenvalues_per_k"] = bool(flat_ok)
    for name, w in (("ring_weights", RINGW), ("unit_weights", {s: 1.0 for s in STAR})):
        D = np.array(STAR, float); wt = np.array([w[s] for s in STAR])
        A = 0.5 * (D * wt[:, None]).T @ D
        ev_, V = np.linalg.eigh(A); M = V @ np.diag(ev_ ** -0.5) @ V.T
        i = np.arange(400) + 0.5
        ph = np.arccos(1 - 2 * i / 400); tt = np.pi * (1 + 5 ** 0.5) * i
        dirs = np.stack([np.cos(tt) * np.sin(ph), np.sin(tt) * np.sin(ph), np.cos(ph)], 1)
        rows = []
        for kap in (0.05, 0.1, 0.2, 0.4):
            speeds = []
            for dvec in dirs[::4]:
                U, _, _ = block(M @ (kap * dvec), w)
                ev = np.linalg.eigvals(U)
                nontriv = sorted(ev, key=lambda z: min(abs(z - 1), abs(z + 1)))[-1]
                speeds.append(abs(np.angle(nontriv)) / kap)
            speeds = np.array(speeds)
            rows.append({"kappa": kap, "mean_theta_over_k": float(speeds.mean()),
                         "spread_over_mean": float((speeds.max() - speeds.min()) / speeds.mean())})
        sl = np.polyfit(np.log([r["kappa"] for r in rows]), np.log([r["spread_over_mean"] for r in rows]), 1)[0]
        out[name] = {"rows": rows, "loglog_slope": float(sl),
                     "predicted_speed_sqrt_2_over_W": float(np.sqrt(2 / wt.sum()))}
    # DF: compact cycle state on an axis square, with random labels, 3-dim irrep
    cx = kuhn_ball("A4", n=4); randomize_labels(cx, seed=4)
    rep = a4_irrep3(cx.group)
    wk = ArcWalk(cx, rep=rep, dim=3, mode="closed")
    grid = {tuple(cx.vertex(v).metadata["grid"]): v for v in cx.vertices()}
    cyc = [grid[(1, 1, 2)], grid[(2, 1, 2)], grid[(2, 2, 2)], grid[(1, 2, 2)]]
    Tr = np.eye(3)
    for a, b in zip(cyc, cyc[1:] + cyc[:1]):
        Tr = rep(cx.label(b, a)) @ Tr       # transport along a->b
    evs, V = np.linalg.eig(Tr)
    x1 = np.real(V[:, np.argmin(abs(evs - 1))]); x1 /= np.linalg.norm(x1)
    psi = np.zeros((len(wk.arcs), 3), complex)
    x = x1.copy()
    for i, (a, b) in enumerate(zip(cyc, cyc[1:] + cyc[:1])):
        psi[wk.index[(a, b)]] = x
        y = -rep(cx.label(b, a)) @ x          # reverse arc at b
        psi[wk.index[(b, a)]] = y
        x = rep(cx.label(b, a)) @ x
    out["DF_cycle_holonomy_has_fixed_vector"] = bool(np.min(abs(evs - 1)) < 1e-9)
    out["DF_eigen_residual"] = float(np.abs(wk.step(psi) - psi).max())
    save("b", out)


# ------------------------------------------------------------------ c: relational light cone on the torus
def part_c(n=40, sigma_hops=3.0, T=None):
    D = np.array(STAR, float); wt = np.array([RINGW[s] for s in STAR]); W = wt.sum()
    A = 0.5 * (D * wt[:, None]).T @ D
    ev_, V = np.linalg.eigh(A); M = V @ np.diag(ev_ ** -0.5) @ V.T
    phi = np.sqrt(wt / W)
    c = np.sqrt(2 / W)
    ax = np.arange(n) - n // 2
    X = np.stack(np.meshgrid(ax, ax, ax, indexing="ij"), -1).astype(float)
    Y = X @ M.T
    r = np.linalg.norm(Y, axis=-1)
    short = np.linalg.norm(M @ np.array([1.0, 0, 0]))
    sig = sigma_hops * short
    zs = [np.array(z) for z in itertools.product((-1, 0, 1), repeat=3) if any(z)]
    half = min(np.linalg.norm(M @ (n * z)) for z in zs) / 2
    if T is None:
        T = int((half - 8 * sig) / c)   # front plus its 4-sigma tail must not reach the half-torus
    if T < 10:
        return {"n": n, "T": T, "status": "window too small for this torus", "sigma_emergent": float(sig)}
    G = np.exp(-r ** 2 / (2 * sig ** 2))
    psi = (G[..., None] * phi).astype(complex)
    psi /= np.linalg.norm(psi)
    shifts = [tuple(int(v) for v in s) for s in STAR]
    rev = [STAR.index(tuple(-x for x in s)) for s in STAR]
    cum = np.zeros((n, n, n)); arrival = np.full((n, n, n), -1.0)
    total_final = None
    beyond = []
    prob_hist = []
    for t in range(1, T + 1):
        ov = (psi * phi).sum(-1)
        cps = 2 * phi * ov[..., None] - psi
        new = np.empty_like(psi)
        for i, s in enumerate(shifts):
            new[..., rev[i]] = np.roll(cps[..., i], shift=s, axis=(0, 1, 2))
        psi = new
        p = (np.abs(psi) ** 2).sum(-1)
        prob_hist.append(p.astype(np.float32))
        if t % max(1, T // 8) == 0:
            beyond.append({"t": t, "weight_beyond_1.25ct": float(p[r > 1.25 * c * t + 3 * sig].sum()),
                           "weight_beyond_ct_plus_3sig": float(p[r > c * t + 3 * sig].sum())})
    # registered: median arrival (half of the vertex's cumulative weight over the run);
    # secondary: tick of the peak
    P = np.array(prob_hist)
    cumP = np.cumsum(P, axis=0)
    arrival = (cumP < 0.5 * cumP[-1]).sum(0) + 1.0
    arrival_peak = P.argmax(0) + 1.0
    i = np.arange(60) + 0.5
    ph = np.arccos(1 - 2 * i / 60); tt = np.pi * (1 + 5 ** 0.5) * i
    dirs = np.stack([np.cos(tt) * np.sin(ph), np.sin(tt) * np.sin(ph), np.cos(ph)], 1)
    sel = (r > max(3 * sig, 0.35 * c * T)) & (r < 0.9 * c * T)
    if sel.sum() < 1000:
        return {"n": n, "T": T, "status": "window too small for this torus", "cT": float(c * T), "sigma_emergent": float(sig)}
    lab = np.argmax((Y[sel] / r[sel][:, None]) @ dirs.T, axis=1)
    speeds, speeds_peak = [], []
    for j in range(60):
        m = lab == j
        if m.sum() > 20:
            speeds.append(np.polyfit(arrival[sel][m], r[sel][m], 1)[0])
            speeds_peak.append(np.polyfit(arrival_peak[sel][m], r[sel][m], 1)[0])
    speeds = np.array(speeds); speeds_peak = np.array(speeds_peak)
    out = {"n": n, "T": T, "predicted_speed": float(c), "sigma_emergent": float(sig),
           "measured_speed_mean": float(speeds.mean()),
           "speed_spread_over_mean": float((speeds.max() - speeds.min()) / speeds.mean()),
           "direction_bins_used": int(len(speeds)), "outside_cone": beyond,
           "peak_speed_mean": float(speeds_peak.mean()),
           "peak_speed_spread_over_mean": float((speeds_peak.max() - speeds_peak.min()) / speeds_peak.mean()),
           "norm_final": float(np.linalg.norm(psi))}
    return out


# ------------------------------------------------------------------ fixtures
def disk_fixture(n, disks, elements):
    """Label edges by ordered crossings of rectangular disks (P13/P15 method)."""
    cx = kuhn_ball("A4", n=n)
    g = cx.group
    for edge in cx.edges():
        a, b = [cx.vertex(v).metadata["grid"] for v in edge]
        hits = []
        for (axis, plane, bounds), x in zip(disks, elements):
            diff = b[axis] - a[axis]
            if diff == 0:
                continue
            t = (plane - a[axis]) / diff
            if not 0 < t < 1:
                continue
            others = [i for i in range(3) if i != axis]
            pt = [a[i] + t * (b[i] - a[i]) for i in others]
            if all(lo < v < hi for v, (lo, hi) in zip(pt, bounds)):
                hits.append((t, x if diff > 0 else g.inverse(x)))
        lab = g.identity()
        for _, x in sorted(hits, key=lambda h: h[0]):
            lab = g.multiply(lab, x)
        cx.set_label(*edge, lab)
    return cx


def elements(g):
    o3 = [x for x in g.elements if g.order_of(x) == 3]
    o2 = [x for x in g.elements if g.order_of(x) == 2]
    return o3[0], o2[0]


SINGLE6 = [(2, Q(13, 4), ((Q(9, 7), Q(33, 7)), (Q(9, 7), Q(33, 7))))]


def curved_vertices(cx):
    st = CurvatureState(cx)
    return sorted({v for fi, f in enumerate(st.faces) if st.flux[fi] != st.identity for v in f})


# ------------------------------------------------------------------ d: two-route holonomy on a mesh cycle
def part_d():
    rows = []
    g0 = kuhn_ball("A4", n=6).group
    h3, h2 = elements(g0)
    for name, h in (("order3", h3), ("V4", h2)):
        cx = disk_fixture(6, SINGLE6, [h])
        g = cx.group
        rep = a4_irrep3(g)
        grid = {tuple(cx.vertex(v).metadata["grid"]): v for v in cx.vertices()}
        found = None
        for (x, y, z) in itertools.product(range(6), repeat=3):   # axis squares in the x-z plane
            sq = [(x, y, z), (x + 1, y, z), (x + 1, y, z + 1), (x, y, z + 1)]
            if not all(p in grid for p in sq):
                continue
            vs = [grid[p] for p in sq]
            hol = g.identity()
            for a, b in zip(vs, vs[1:] + vs[:1]):
                hol = g.multiply(hol, cx.label(a, b))
            if hol != g.identity():
                found = (vs, hol); break
        vs, hol = found
        # route 1: v0 -> v1 -> v2 ; route 2: v0 -> v3 -> v2  (equal length L = 2)
        def transport(path):
            Tm = np.eye(3)
            for a, b in zip(path, path[1:]):
                Tm = rep(cx.label(b, a)) @ Tm
            return Tm
        T1, T2 = transport([vs[0], vs[1], vs[2]]), transport([vs[0], vs[3], vs[2]])
        # Walk restricted to the 4-cycle subgraph: degree-2 coin (= swap), transported shift.
        def run(labelled):
            cyc = vs
            arcs = [(cyc[i], cyc[(i + 1) % 4]) for i in range(4)] + [(cyc[(i + 1) % 4], cyc[i]) for i in range(4)]
            idx = {a: i for i, a in enumerate(arcs)}
            det = 0.0
            for e in np.eye(3):
                psi = np.zeros((8, 3), complex)
                psi[idx[(cyc[0], cyc[1])]] = e / np.sqrt(2); psi[idx[(cyc[0], cyc[3])]] = e / np.sqrt(2)
                for _ in range(2):
                    c = np.zeros_like(psi)                     # coin: swap the two outgoing arcs
                    for v in cyc:
                        outs = [a for a in arcs if a[0] == v]
                        c[idx[outs[0]]], c[idx[outs[1]]] = psi[idx[outs[1]]], psi[idx[outs[0]]]
                    new = np.zeros_like(psi)
                    for (a, b) in arcs:
                        M = rep(cx.label(b, a)) if labelled else np.eye(3)
                        new[idx[(b, a)]] = M @ c[idx[(a, b)]]
                    psi = new
                outs = [a for a in arcs if a[0] == cyc[2]]
                sym = (psi[idx[outs[0]]] + psi[idx[outs[1]]]) / np.sqrt(2)
                det += np.vdot(sym, sym).real / 3
            return det
        det_flux = run(True)
        det_triv = run(False)
        chi = float(np.trace(rep(hol)))
        rows.append({"flux": name, "cycle_holonomy_class_order": g.order_of(hol), "chi3": chi,
                     "detection_flux": det_flux, "detection_trivial": det_triv,
                     "predicted": 0.5 * (1 + chi / 3),
                     "difference_trivial_minus_flux": det_triv - det_flux,
                     "registered_contrast_clause_abs_chi_over_3": abs(chi) / 3})
    # the same numbers from the full ArcWalk restricted to the 4-cycle subgraph (sanity)
    save("d", rows)


# ------------------------------------------------------------------ e: trapping
def trapped_stats(w, near_vertices, tol=1e-9):
    U = w.matrix()
    ev, V = np.linalg.eig(U)
    mod = np.abs(ev)
    trapped = mod > 1 - tol
    gap = float(1 - mod[~trapped].max()) if (~trapped).any() else None
    Qm = np.linalg.qr(V[:, trapped])[0] if trapped.any() else np.zeros((len(U), 0))
    near_arcs = np.array([a[0] in near_vertices for a in w.arcs])
    mask = np.repeat(near_arcs, w.dim)
    near_weight = float((np.abs(Qm[mask]) ** 2).sum() / max(1, Qm.shape[1])) if Qm.shape[1] else 0.0
    return {"dim_trapped": int(trapped.sum()), "size": len(U), "gap_below_trapped": gap,
            "trapped_count_tol_1e-6": int((mod > 1 - 1e-6).sum()),
            "mean_trapped_weight_near_flux": near_weight,
            "near_arc_fraction_of_space": float(mask.mean())}


def part_e_exact():
    rows = []
    g0 = kuhn_ball("A4", n=6).group
    h3, h2 = elements(g0)
    vac = kuhn_ball("A4", n=6)
    for name, h in (("order3", h3), ("V4", h2)):
        cx = disk_fixture(6, SINGLE6, [h])
        cv = set(curved_vertices(cx))
        nb = set(cv)
        for a, b in cx.edges():
            if a in cv: nb.add(b)
            if b in cv: nb.add(a)
        rep = a4_irrep3(cx.group)
        t0 = time.time()
        fx = trapped_stats(ArcWalk(cx, rep=rep, dim=3, mode="open"), nb)
        vc = trapped_stats(ArcWalk(vac, rep=rep, dim=3, mode="open"), nb)
        rows.append({"flux": name, "curved_faces": int(CurvatureState(cx).energy),
                     "fixture": fx, "vacuum": vc, "seconds": round(time.time() - t0, 1)})
        print(rows[-1], flush=True)
    save("e_exact", rows)


def part_e_time(T=20000):
    from topology_audit import linked_fixture
    from noncommuting_link_audit import linked_fixture_ab
    g0 = kuhn_ball("A4", n=8).group
    h3, _ = elements(g0)
    fixtures = {"P13_linked_order3": linked_fixture("A4"),
                "P15_tethered_N1": linked_fixture_ab("N1"),
                "single_loop_order3": disk_fixture(8, [(2, Q(17, 4), ((Q(9, 7), Q(37, 7)), (Q(9, 7), Q(44, 7))))], [h3])}
    vac = kuhn_ball("A4", n=8)
    rows = []
    for name, cx in fixtures.items():
        cv = set(curved_vertices(cx))
        rep = a4_irrep3(cx.group)
        res = {"fixture": name, "curved_faces": int(CurvatureState(cx).energy)}
        for label, cmplx in (("fixture", cx), ("vacuum", vac)):
            w = ArcWalk(cmplx, rep=rep, dim=3, mode="open")
            src = np.array([a[0] in cv for a in w.arcs])
            near = src.copy()
            kept_final, near_final, curve = [], [], []
            for e in np.eye(3):
                psi = (w.phi * src)[:, None] * e[None, :]
                psi = psi.astype(complex); psi /= np.linalg.norm(psi)
                c = []
                for t in range(1, T + 1):
                    psi = w.step(psi)
                    if t in (100, 1000, 5000, 10000, T):
                        c.append(float((np.abs(psi) ** 2).sum()))
                kept_final.append(float((np.abs(psi) ** 2).sum()))
                near_final.append(float((np.abs(psi[near]) ** 2).sum()))
                curve.append(c)
            res[label] = {"retained_T": float(np.mean(kept_final)),
                          "retained_near_flux_T": float(np.mean(near_final)),
                          "retained_at_t_100_1k_5k_10k_T": list(np.mean(curve, axis=0))}
        rows.append(res)
        print(res, flush=True)
    save("e_time", rows)


if __name__ == "__main__":
    part = sys.argv[1]
    {"a": part_a, "b": part_b, "c": lambda: save("c", [part_c(40), part_c(80), part_c(120)]), "d": part_d,
     "e_exact": part_e_exact, "e_time": part_e_time}[part]()
