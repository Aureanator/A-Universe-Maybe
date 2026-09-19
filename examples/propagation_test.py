"""P18: round, sharp light fronts on the project's mesh? (derivations: docs/PROPAGATION.md)

Wave rule u_tt = -(L + m^2) u on the infinite periodic Kuhn lattice (the star is
read from seeds.kuhn_ball), solved EXACTLY in continuous time by FFT:
u(t) = IFFT( FFT(u0) cos(omega(k) t) ), omega^2 = L(k) + m^2, L(k) = sum w (1 - cos k.d).
Continuum reference: the same grid and the same initial data, but symbol k^T A k,
i.e. isotropic in the emergent metric. Only the symbol differs.
Coordinates prepare pulses and measure; they never enter the rule.
Reproduce: python examples/propagation_test.py
"""

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))


# ------------------------------------------------------------------ stars
def kuhn_star():
    """(vectors, ring sizes) of the project's mesh, read from an interior region."""
    from constraintnet.seeds import kuhn_ball
    from constraintnet.curvature import CurvatureState
    cx = kuhn_ball("Z3", n=4)
    st = CurvatureState(cx)
    g = {v: np.array(cx.vertex(v).metadata["grid"]) for v in cx.vertices()}
    ring = {}
    for ei in st.interior_edges:
        a, b = st.edges[ei]
        d = tuple(int(x) for x in g[b] - g[a])
        nd = tuple(-x for x in d)
        r = len(st.edge_faces[ei])
        for key in (d, nd):
            ring.setdefault(key, set()).add(r)
    assert all(len(v) == 1 for v in ring.values()), "ring size must be constant per direction"
    vecs = sorted(ring)
    return np.array(vecs, dtype=float), np.array([next(iter(ring[v])) for v in vecs])


def square_star():
    return np.array([(1, 0), (-1, 0), (0, 1), (0, -1)], dtype=float), np.array([4] * 4)


def a_tilde(D, w):
    return 0.5 * (D * w[:, None]).T @ D


def inv_sqrt(A):
    ev, V = np.linalg.eigh(A)
    return V @ np.diag(ev ** -0.5) @ V.T


# ------------------------------------------------------------------ N1
def check_bcc(D, ring):
    A = a_tilde(D, np.ones(len(D)))
    M = inv_sqrt(A)
    Y = D @ M.T
    short = Y[ring == 6]; long_ = Y[ring == 4]
    ls, ll = np.linalg.norm(short, axis=1), np.linalg.norm(long_, axis=1)
    us = short / ls[:, None]; ul = long_ / ll[:, None]
    cs = np.round(us @ us.T, 10); cl = np.round(ul @ ul.T, 10)
    off_s = sorted(set(cs[~np.eye(len(us), dtype=bool)]))
    off_l = sorted(set(cl[~np.eye(len(ul), dtype=bool)]))
    # long vectors must point along the cube axes defined by the short ones
    axes_ok = all(np.allclose(sorted(np.abs(np.round(us @ u, 10))), [1 / np.sqrt(3)] * 8) for u in ul)
    return {"A_tilde_uniform": A.tolist(), "A_eigenvalues": np.linalg.eigvalsh(A).tolist(),
            "n_short_ring6": int(len(short)), "n_long_ring4": int(len(long_)),
            "short_lengths_equal": bool(np.allclose(ls, ls[0])),
            "long_over_short": float(ll[0] / ls[0]), "expected_long_over_short": 2 / np.sqrt(3),
            "short_pairwise_cosines": off_s, "long_pairwise_cosines": off_l,
            "long_along_cube_axes": bool(axes_ok)}


# ------------------------------------------------------------------ symbol anisotropy (N3)
def fib_sphere(n):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n); th = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)


def symbol_anisotropy(D, w, kappas=(0.05, 0.1, 0.2, 0.4)):
    A = a_tilde(D, w); M = inv_sqrt(A)
    dirs = fib_sphere(400)
    out = []
    for kap in kappas:
        kg = (dirs * kap) @ M        # grid wavevector for emergent wavevector kap*n
        L = ((1 - np.cos(kg @ D.T)) * w).sum(1)
        rel = L / kap ** 2
        out.append({"kappa": kap, "spread_over_mean": float((rel.max() - rel.min()) / rel.mean())})
    ks = np.log([o["kappa"] for o in out]); sp = np.log([o["spread_over_mean"] for o in out])
    return {"rows": out, "loglog_slope": float(np.polyfit(ks, sp, 1)[0])}


# ------------------------------------------------------------------ exact lattice evolution
def evolve(D, w, sigma, t_list, m=0.0, continuum=False, margin=4.0):
    dim = D.shape[1]
    A = a_tilde(D, w); M = inv_sqrt(A)
    R_needed = max(t_list) + margin * sigma
    # smallest emergent length of a nonzero periodic shift z*N
    zs = np.array(np.meshgrid(*[[-1, 0, 1]] * dim)).reshape(dim, -1).T
    zs = zs[np.any(zs != 0, axis=1)]
    shortest = min(np.linalg.norm(M @ z) for z in zs)
    N = int(np.ceil(2.2 * R_needed / shortest)) + 2
    N += N % 2
    ax = np.arange(N) - N // 2
    X = np.stack(np.meshgrid(*[ax] * dim, indexing="ij"), -1).astype(float)
    Y = X @ M.T
    r = np.linalg.norm(Y, axis=-1)
    u0 = np.exp(-r ** 2 / (2 * sigma ** 2))
    k1 = 2 * np.pi * np.fft.fftfreq(N)
    K = np.stack(np.meshgrid(*[k1] * dim, indexing="ij"), -1)
    if continuum:
        sym = np.einsum("...i,ij,...j->...", K, A, K)
    else:
        sym = np.zeros(K.shape[:-1])
        for d, wd in zip(D, w):
            sym += wd * (1 - np.cos(K @ d))
    omega = np.sqrt(sym + m * m)
    U0 = np.fft.fftn(np.fft.ifftshift(u0))
    fields = {}
    for t in t_list:
        fields[t] = np.fft.fftshift(np.real(np.fft.ifftn(U0 * np.cos(omega * t))))
    return X, Y, r, fields, N


def interior_fraction(r, u, t, sigma):
    u2 = u ** 2
    return float(u2[r < t - 4 * sigma].sum() / u2.sum())


def emergent_anisotropy(Y, r, u, t, sigma, ndirs=60):
    shell = (r > t - 4 * sigma) & (u ** 2 > 1e-12 * (u ** 2).max())
    y, rr, u2 = Y[shell], r[shell], u[shell] ** 2
    dirs = fib_sphere(ndirs) if Y.shape[-1] == 3 else np.stack(
        [np.cos(2 * np.pi * np.arange(ndirs) / ndirs), np.sin(2 * np.pi * np.arange(ndirs) / ndirs)], 1)
    lab = np.argmax((y / rr[:, None]) @ dirs.T, axis=1)
    means = np.array([np.average(rr[lab == j], weights=u2[lab == j]) for j in range(ndirs)
                      if (lab == j).any()])
    return float((means.max() - means.min()) / means.mean())


def grid_speed_ratio(D, w, sigma):
    """Front speed along grid (1,1,1) vs grid (1,-1,0), from two times (offsets cancel)."""
    t1, t2 = 8 * sigma, 12 * sigma
    X, Y, r, f, N = evolve(D, w, sigma, [t1, t2])
    res = {}
    for name, v in {"diag_111": (1, 1, 1), "perp_1m10": (1, -1, 0), "axis_100": (1, 0, 0)}.items():
        v = np.array(v, float); v /= np.linalg.norm(v)
        xn = np.linalg.norm(X, axis=-1)
        cosang = np.where(xn > 0, (X @ v) / np.maximum(xn, 1e-12), 0)
        sel = cosang > np.cos(np.deg2rad(6))
        pos = []
        for t in (t1, t2):
            u2 = f[t][sel] ** 2
            far = xn[sel] > 0.5 * t * np.sqrt(v @ a_tilde(D, w) @ v)
            pos.append(np.average(xn[sel][far], weights=u2[far]))
        res[name] = (pos[1] - pos[0]) / (t2 - t1)
    A = a_tilde(D, w)
    pred = {k: float(np.sqrt(np.array(v) @ A @ np.array(v) / np.dot(v, v)))
            for k, v in {"diag_111": (1, 1, 1), "perp_1m10": (1, -1, 0), "axis_100": (1, 0, 0)}.items()}
    # Front (ray) speed along n is 1/sqrt(n^T A^-1 n); it equals the plane-wave
    # speed sqrt(n^T A n) only along eigen-directions of A (diag_111, perp_1m10).
    Ai = np.linalg.inv(A)
    ray = {k: float(1 / np.sqrt(np.array(v) @ Ai @ np.array(v) / np.dot(v, v)))
           for k, v in {"diag_111": (1, 1, 1), "perp_1m10": (1, -1, 0), "axis_100": (1, 0, 0)}.items()}
    return {"sigma": sigma, "measured_grid_speeds": res, "predicted_grid_speeds": pred,
            "predicted_ray_speeds": ray,
            "measured_ratio_diag_over_perp": res["diag_111"] / res["perp_1m10"],
            "predicted_ratio": pred["diag_111"] / pred["perp_1m10"]}


def front_runs(D, w, sigmas, m_sigma=0.0, label=""):
    rows = []
    for s in sigmas:
        t = 12 * s
        m = m_sigma / s
        X, Y, r, f, N = evolve(D, w, s, [t], m=m)
        Xc, Yc, rc, fc, _ = evolve(D, w, s, [t], m=m, continuum=True)
        row = {"label": label, "sigma": s, "m_sigma": m_sigma, "grid_N": N,
               "interior_fraction_lattice": interior_fraction(r, f[t], t, s),
               "interior_fraction_continuum": interior_fraction(rc, fc[t], t, s),
               "anisotropy_lattice": emergent_anisotropy(Y, r, f[t], t, s),
               "anisotropy_continuum": emergent_anisotropy(Yc, rc, fc[t], t, s)}
        print(row, flush=True)
        rows.append(row)
    return rows


# ------------------------------------------------------------------ N6 damped real waves
def damped_wave_trapping(level=3, T=80000.0, gamma=1.0):
    from trapping_test import sierpinski, laplacian, dark_subspace, expm, _dist
    verts, edges, _, b = sierpinski(level)
    n = len(verts)
    L = laplacian(n, edges)
    PB = np.zeros((n, n)); PB[b, b] = 1
    G = np.block([[np.zeros((n, n)), np.eye(n)], [-L, -gamma * PB]])
    U = expm(G * T)
    D, _, _ = dark_subspace(L, [b])
    rows = []
    for j in [int(np.argmax(_dist(n, edges, [b]))), 5, 17, 30]:
        u0 = np.zeros(n); u0[j] = 1.0
        y = U @ np.concatenate([u0, np.zeros(n)])
        u, v = y[:n], y[n:]
        E0 = 0.5 * u0 @ L @ u0
        ET = 0.5 * (v @ v + u @ L @ u)
        uD = np.real(D @ (D.conj().T @ u0))
        ED = 0.5 * uD @ L @ uD
        rows.append({"start": j, "energy_fraction_T": float(ET / E0),
                     "predicted_dark_energy_fraction": float(ED / E0)})
    return {"level": level, "T": T, "rows": rows}


def main():
    out = {}
    D, ring = kuhn_star()
    out["N1_star"] = check_bcc(D, ring)
    print("N1", out["N1_star"], flush=True)
    w_uni = np.ones(len(D))
    w_ring = np.where(ring == 4, 0.5, 1.0)
    out["N3_symbol"] = {"uniform": symbol_anisotropy(D, w_uni), "ring_weighted": symbol_anisotropy(D, w_ring)}
    print("N3 symbol", out["N3_symbol"], flush=True)
    out["N2_grid_speed"] = [grid_speed_ratio(D, w_uni, s) for s in (1.5, 3.0)]
    print("N2", out["N2_grid_speed"], flush=True)
    sig = (1.5, 2.0, 3.0, 4.0)
    out["N3_N4_kuhn_uniform_massless"] = front_runs(D, w_uni, sig, 0.0, "kuhn uniform")
    out["N3_kuhn_ring_weighted_massless"] = front_runs(D, w_ring, sig, 0.0, "kuhn ring 1:1/2")
    out["N5_kuhn_uniform_massive"] = (front_runs(D, w_uni, (1.5, 2.0, 3.0), 0.5, "kuhn m*sigma=0.5")
                                      + front_runs(D, w_uni, (1.5, 2.0, 3.0), 1.0, "kuhn m*sigma=1"))
    D2, r2 = square_star()
    out["N4_square_2d_massless"] = front_runs(D2, np.ones(4), (1.5, 2.0, 3.0, 4.0, 6.0), 0.0, "square 2D")
    out["N6_damped_wave"] = damped_wave_trapping()
    print("N6", out["N6_damped_wave"], flush=True)
    path = ROOT / "reference/opus_session/data/propagation_test.json"
    path.write_text(json.dumps(out, indent=1, default=float) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
