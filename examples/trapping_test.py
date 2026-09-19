"""P17: can amplitudes trap where probabilities cannot? (derivations: docs/TRAPPING.md)

Same generator (graph Laplacian L) for both walks; exit set B with leak Gamma.
  classical  p(t)   = exp(-(L + Gamma P_B) t) p0          survival sum(p)
  amplitude  psi(t) = exp(-i (L - i Gamma P_B) t) psi0    survival ||psi||^2
NumPy only. No constraintnet dynamics is used; the Kuhn graph is just the
1-skeleton of the existing mesh. Reproduce: python examples/trapping_test.py
"""

import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

GAMMA = 1.0
TOL = 1e-8


# ---------------------------------------------------------------- graphs
def path_graph(n):
    return list(range(n)), [(i, i + 1) for i in range(n - 1)], [], "end 0"


def cycle_graph(n):
    edges = [(i, (i + 1) % n) for i in range(n)]
    refl = {i: (-i) % n for i in range(n)}             # fixes vertex 0
    return list(range(n)), edges, [refl], "vertex 0"


def complete_graph(n):
    edges = list(itertools.combinations(range(n), 2))
    gens = [{**{i: i for i in range(n)}, 1: 2, 2: 1}]
    gens.append({0: 0, **{i: (i % (n - 1)) + 1 for i in range(1, n)}})  # cycle on 1..n-1
    return list(range(n)), edges, gens, "vertex 0"


def sierpinski(level):
    """Vertices (a,b) with a,b >= 0, a+b <= 2^level; corner exit (0,0)."""
    edges = set()

    def tri(a, b, s):
        if s == 1:
            p = [(a, b), (a + 1, b), (a, b + 1)]
            for u, v in itertools.combinations(p, 2):
                edges.add(tuple(sorted((u, v))))
            return
        h = s // 2
        tri(a, b, h); tri(a + h, b, h); tri(a, b + h, h)
    tri(0, 0, 2 ** level)
    verts = sorted({v for e in edges for v in e})
    idx = {v: i for i, v in enumerate(verts)}
    E = [(idx[u], idx[v]) for u, v in edges]
    refl = {idx[(a, b)]: idx[(b, a)] for (a, b) in verts}
    return list(range(len(verts))), E, [refl], idx[(0, 0)]


def kuhn_graph(n):
    from constraintnet.seeds import kuhn_ball
    cx = kuhn_ball("Z3", n=n)
    vs = sorted(cx.vertices())
    idx = {v: i for i, v in enumerate(vs)}
    grid = {idx[v]: tuple(cx.vertex(v).metadata["grid"]) for v in vs}
    E = [(idx[a], idx[b]) for a, b in cx.edges()]
    by_grid = {g: i for i, g in grid.items()}
    eset = {tuple(sorted(e)) for e in E}
    gens = []
    for perm in itertools.permutations(range(3)):
        m = {i: by_grid[tuple(g[perm[k]] for k in range(3))] for i, g in grid.items()}
        if {tuple(sorted((m[a], m[b]))) for a, b in eset} == eset:
            gens.append(m)
    exit_v = by_grid[(0, 0, 0)]
    return list(range(len(vs))), E, gens, exit_v


# ---------------------------------------------------------------- linear algebra
def laplacian(n, edges, weights=None):
    L = np.zeros((n, n))
    for k, (i, j) in enumerate(edges):
        w = 1.0 if weights is None else weights[k]
        L[i, j] -= w; L[j, i] -= w; L[i, i] += w; L[j, j] += w
    return L


def expm(A):
    """Scaling-and-squaring Taylor exponential (NumPy only)."""
    norm = np.linalg.norm(A, 1)
    s = max(0, int(np.ceil(np.log2(norm / 0.25))) if norm > 0 else 0)
    X = A / (2 ** s)
    R = np.eye(len(A), dtype=complex if np.iscomplexobj(A) else float)
    term = R.copy()
    for k in range(1, 30):
        term = term @ X / k
        R = R + term
    for _ in range(s):
        R = R @ R
    return R


def _is_prime(n):
    if n < 2:
        return False
    for q in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % q == 0:
            return n == q
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2; r += 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


PRIMES = []
_c = (1 << 26) - 1
while len(PRIMES) < 3:
    if _is_prime(_c):
        PRIMES.append(_c)
    _c -= 2


def krylov_rank_mod_p(Lint, B, p):
    """Exact rank over GF(p) of span{L^k e_b}. rank_p <= rank_Q (rigorous),
    so N - rank_p is a rigorous UPPER bound on dim D; agreement over several
    primes gives the rational rank with overwhelming probability."""
    n = len(Lint)
    Lm = np.mod(Lint, p).astype(np.int64)
    rows, pivots = np.zeros((0, n), dtype=np.int64), []
    for b in B:
        v = np.zeros(n, dtype=np.int64); v[b] = 1
        for _ in range(n + 1):
            w = v.copy()
            if pivots:
                coeff = w[pivots]
                w = np.mod(w - np.mod(coeff @ rows, p), p)
            nz = np.nonzero(w)[0]
            if len(nz) == 0:
                break
            c = int(nz[0])
            w = np.mod(w * pow(int(w[c]), p - 2, p), p)
            if len(rows):
                f = rows[:, c].copy()
                rows = np.mod(rows - np.mod(np.outer(f, w), p), p)
            rows = np.vstack([rows, w]); pivots.append(c)
            v = np.mod(Lm @ v, p)
    return len(pivots)


def dark_subspace(L, B):
    """Exact dim D (modular Krylov rank over three primes; must agree), then
    numerical basis = eigenvectors of K = L - i P_B with the dim-D smallest
    decay rates. Returns (basis, multiplicities, info)."""
    n = len(L)
    Lint = np.rint(L).astype(np.int64)
    assert np.array_equal(Lint, L), "exact rank needs an integer Laplacian"
    ranks = [krylov_rank_mod_p(Lint, B, p) for p in PRIMES]
    assert len(set(ranks)) == 1, ranks
    d = n - ranks[0]
    PB = np.zeros((n, n)); PB[B, B] = 1
    E, V = np.linalg.eig(L - 1j * PB)
    order = np.argsort(-E.imag)            # smallest decay first
    rates = -E.imag[order]
    Dm = np.linalg.qr(V[:, order[:d]])[0] if d else np.zeros((n, 0))
    ev = np.linalg.eigvalsh(L)
    mults, start = [], 0
    for i in range(1, n + 1):
        if i == n or ev[i] - ev[i - 1] > 1e-7 * max(1.0, abs(ev[i])):
            mults.append(i - start); start = i
    info = {"exact_dim_D": d, "primes": PRIMES,
            "max_rate_inside_D": float(rates[:d].max()) if d else 0.0,
            "first_rate_outside_D": float(rates[d]) if d < n else None}
    return Dm, mults, info


def orbits(n, gens):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for g in gens:
        for i, j in g.items():
            parent[find(i)] = find(j)
    return len({find(i) for i in range(n)})


def analyse(name, verts, edges, gens, B, weights=None, T=None):
    n = len(verts)
    B = [B] if isinstance(B, int) else list(B)
    L = laplacian(n, edges, weights)
    PB = np.zeros((n, n)); PB[B, B] = 1.0
    # check automorphisms fix exits and commute with L
    for g in gens:
        P = np.zeros((n, n))
        for i, j in g.items():
            P[j, i] = 1
        assert np.allclose(P @ L, L @ P) and all(g[b] == b for b in B)
    D, mults, info = dark_subspace(L, B)
    dimD = D.shape[1]
    t4 = sum(max(0, m - len(B)) for m in mults)
    t5 = n - orbits(n, gens) if gens else 0
    K = L - 1j * GAMMA * PB
    # decay rates on the complement (restricted operator is exact by invariance)
    slow = info["first_rate_outside_D"]
    M = L + GAMMA * PB
    lam_c = float(np.linalg.eigvalsh(M).min())
    if T is None:
        T = min(40.0 / slow, 1e9) if slow and slow > 0 else 50.0
    Uq = expm(-1j * K * T)
    Uc = expm(-M * T)
    surv_q = (np.abs(Uq) ** 2).sum(axis=0)       # per single-vertex start
    surv_c = Uc.sum(axis=0)
    pred_q = (np.abs(D) ** 2).sum(axis=1) if dimD else np.zeros(n)   # ||P_D e_j||^2
    far = int(np.argmax(_dist(n, edges, B)))
    return {"graph": name, "N": n, "exits": len(B), "dim_D": dimD,
            "dark_fraction": dimD / n, "bound_T4_degeneracy": t4,
            "bound_T5_symmetry": t5, "automorphisms_used": len(gens),
            "max_rate_inside_D_numerical": info["max_rate_inside_D"],
            "classical_rate_lambda_min": lam_c, "slowest_nondark_rate": slow, "T": T,
            "classical_max_survival_T": float(surv_c.max()),
            "amplitude_mean_survival_T": float(surv_q.mean()),
            "predicted_mean_dimD_over_N": dimD / n,
            "max_abs_error_vs_T3": float(np.abs(surv_q - pred_q).max()),
            "quasi_dark_present": bool(slow is not None and slow * T < 20),
            "classical_mean_survival_T": float(surv_c.mean()),
            "far_vertex_survival_T": float(surv_q[far]), "far_vertex_predicted": float(pred_q[far])}


def _dist(n, edges, B):
    adj = [[] for _ in range(n)]
    for i, j in edges:
        adj[i].append(j); adj[j].append(i)
    d = [-1] * n
    q = list(B)
    for b in B:
        d[b] = 0
    for v in q:
        for w in adj[v]:
            if d[w] < 0:
                d[w] = d[v] + 1; q.append(w)
    return np.array(d, dtype=float)


def lead_control(level=3, lead=6000, t=1500.0):
    """Explicit 1-D lead replaces Gamma P_B: dark states must stay exactly."""
    verts, edges, gens, b = sierpinski(level)
    n = len(verts)
    L0 = laplacian(n, edges)
    D, _, _ = dark_subspace(L0, [b])
    E = list(edges) + [(b, n)] + [(n + k, n + k + 1) for k in range(lead - 1)]
    Lf = laplacian(n + lead, E)
    w, V = np.linalg.eigh(Lf)

    def evolve(psi):
        full = np.zeros(n + lead, complex); full[:n] = psi
        out = V @ (np.exp(-1j * w * t) * (V.T @ full))
        return float((np.abs(out[:n]) ** 2).sum())
    dark = D[:, 0]
    bright = np.zeros(n); bright[_dist(n, edges, [b]).argmax()] = 1.0
    bright = bright - D @ (D.T @ bright); bright /= np.linalg.norm(bright)
    return {"level": level, "lead_sites": lead, "t": t,
            "dark_state_region_norm": evolve(dark),
            "bright_state_region_norm": evolve(bright)}


def symmetry_breaking(level=4, eps_list=(1e-3, 3e-3, 1e-2, 3e-2, 1e-1), seed=7):
    verts, edges, gens, b = sierpinski(level)
    n = len(verts)
    D0, _, _ = dark_subspace(laplacian(n, edges), [b])
    k0 = D0.shape[1]
    u = np.random.default_rng(seed).uniform(-1, 1, len(edges))
    rows = []
    for eps in eps_list:
        L = laplacian(n, edges, 1 + eps * u)
        PB = np.zeros((n, n)); PB[b, b] = 1
        rates = np.sort(-np.linalg.eigvals(L - 1j * GAMMA * PB).imag)
        quasi = rates[:k0]                          # the k0 slowest = former dark states
        rows.append({"eps": eps, "former_dark": k0,
                     "slowest_rate": float(rates[0]),
                     "median_rate_former_dark": float(np.median(quasi)),
                     "max_rate_former_dark": float(quasi.max())})
    le = np.log([r["eps"] for r in rows])
    lr = np.log([r["median_rate_former_dark"] for r in rows])
    slope_all = float(np.polyfit(le, lr, 1)[0])
    slope_small = float(np.polyfit(le[:3], lr[:3], 1)[0])
    # Exact check that the symmetry is really broken: integer weights 1000 +/- 1.
    signs = np.where(np.random.default_rng(seed).uniform(-1, 1, len(edges)) > 0, 1, -1)
    Lint = laplacian(n, edges, 1000 + signs)
    D_int, _, _ = dark_subspace(Lint, [b])
    return {"level": level, "rows": rows, "loglog_slope_all": slope_all,
            "loglog_slope_three_smallest_eps": slope_small,
            "exact_dim_D_integer_weights_1000pm1": D_int.shape[1],
            "exact_dim_D_unbroken": k0}


def main():
    out = {"gamma": GAMMA, "graphs": []}
    cases = [("path n=40", *path_graph(40)[:3], 0),
             ("cycle n=40", *cycle_graph(40)[:3], 0),
             ("cycle n=41", *cycle_graph(41)[:3], 0),
             ("complete n=12", *complete_graph(12)[:3], 0)]
    for k in range(1, 7):
        v, e, g, b = sierpinski(k)
        cases.append((f"sierpinski level {k}", v, e, g, b))
    for n in (2, 3):
        v, e, g, b = kuhn_graph(n)
        cases.append((f"kuhn ball n={n} 1-skeleton", v, e, g, b))
    for name, v, e, g, b in cases:
        r = analyse(name, v, e, g, b)
        print({k: (round(x, 6) if isinstance(x, float) else x) for k, x in r.items()}, flush=True)
        out["graphs"].append(r)
    out["lead_control"] = lead_control()
    print("lead", out["lead_control"], flush=True)
    out["symmetry_breaking"] = symmetry_breaking()
    print("break", out["symmetry_breaking"], flush=True)
    path = ROOT / "reference/opus_session/data/trapping_test.json"
    path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
