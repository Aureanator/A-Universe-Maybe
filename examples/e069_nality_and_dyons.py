"""E069 -- N-ality and dyons: does a non-self-dual charge supply the selection rule E068 asked for?

Run:  ./.venv/Scripts/python.exe examples/e069_nality_and_dyons.py
Writes reference/local_qwen/data/e069_nality_dyons.json.

Priors were registered in docs/PREDICTIONS.md ("E069") BEFORE this file was run; restated tersely so
the log is self-contained:

PA  structural: sum q = 0 mod N identically and a flux update touches only its two endpoints by
    opposite amounts. Asserted every step (DriverGZN) and in tests/test_gauss_zn.py.
PB  Z2 control: no baryonic content exists in Z2 -- every charge is self-inverse -- so E068's
    annihilating confined pair is the generic case there, not a flaw in that experiment.
PC  Z3 physics: three like charges are neutral yet irreducible; decay needs multi-body coincidence,
    so median time-to-vacuum(baryon) > median time-to-vacuum(meson) at matched beta_E.
PD  dyons: the abelian model has no flux-charge cross term, so (i) magnetic observables are
    statistically unchanged by an electric string and (ii) charge-curvature correlation does not
    persist when a charge is seeded on top of curvature. Growing correlation refutes factorisation.

GEOMETRY CAVEAT discovered while building this harness (n=3 Kuhn ball): the interior is only 8
vertices, they are mutually at graph distance <= 2, and EVERY interior vertex is adjacent to the
boundary. So on this frame annihilation cannot be separated from absorption by geometry alone -- both
are reported separately below rather than conflated into "decay".

Nothing here inserts a particle label, pinning potential or coupling constant to force an answer.
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.drivers import DriverGZN
from constraintnet.gauss_zn import GaussStateZN, charge_curvature_correlation
from constraintnet.seeds import kuhn_ball

N_MESH = 3
STEPS_PLASMA = 800
STEPS_LIFE = 3000
STEPS_LONG = 12000
SEEDS = tuple(range(6))
BETA_B = 6.0
PLASMA_SCAN = (2.0, 4.0, 8.0, 12.0)
COLD = (8.0, 12.0)


# ------------------------------------------------------------------ geometry helpers (no RNG)
def _adj(st):
    adj = {}
    for (u, w) in st.edges:
        adj.setdefault(u, set()).add(w)
        adj.setdefault(w, set()).add(u)
    return adj


def _bfs(st, src):
    adj = _adj(st)
    dist = {src: 0}
    frontier = [src]
    while frontier:
        nxt = []
        for u in frontier:
            for w in adj.get(u, ()):
                if w not in dist:
                    dist[w] = dist[u] + 1
                    nxt.append(w)
        frontier = nxt
    return dist


def interior(st):
    return [v for v in st.vertices if v not in st.boundary_vertices]


def pick_meson_sites(st):
    """The two mutually furthest interior vertices."""
    pool = interior(st)
    best, bestd = None, -1
    for i, a in enumerate(pool):
        d = _bfs(st, a)
        for b in pool[i + 1:]:
            if d.get(b, -1) > bestd:
                best, bestd = (a, b), d[b]
    return best[0], best[1], bestd


def pick_star_sites(st, arms=3, min_len=2):
    """A junction vertex plus `arms` targets whose shortest paths leave by DISTINCT first edges.

    Distinct first edges are what make it a Y rather than one string with branches folded onto each
    other; without them the "baryon" is not three separate arms.  Raises if no such centre exists --
    silently seeding fewer arms than requested is exactly how this harness first produced a bogus
    'vacuum' classification for a supposedly baryonic seed.
    """
    pool = interior(st)
    for center in sorted(pool, key=lambda c: max(_bfs(st, c)[w] for w in pool)):
        groups: dict = {}
        for w in pool:
            if w == center:
                continue
            p = st.shortest_path(center, w)
            if p and len(p) - 1 >= min_len:
                groups.setdefault(p[1], []).append(w)
        if len(groups) >= arms:
            ends = [min(v) for _, v in sorted(groups.items())[:arms]]
            return center, ends
    raise RuntimeError(
        f"no vertex supports {arms} disjoint arms of length >= {min_len} "
        f"(interior has {len(pool)} vertices); enlarge the mesh or lower min_len explicitly"
    )


# ------------------------------------------------------------------ seeding regimes
def seed_regime(group, regime):
    """Return (state, seed_info).  regime in {'vacuum','meson','baryon'}."""
    st = GaussStateZN(kuhn_ball(group, n=N_MESH))
    if regime == "vacuum":
        return st, {}
    if regime == "meson":
        a, b, sep = pick_meson_sites(st)
        st.load_string(st.shortest_path(a, b), flux=1)
        info = {"sites": [a, b], "separation": sep}
    elif regime == "baryon":
        c, ends = pick_star_sites(st)
        paths = st.load_star(c, ends, flux=1)
        info = {"center": c, "ends": ends, "arm_lengths": [len(p) - 1 for p in paths]}
    else:
        raise ValueError(regime)
    assert st.check_gauss()
    return st, info


# ------------------------------------------------------------------ one run
def run(group, regime, seed, beta_E, steps):
    st, info = seed_regime(group, regime)
    n0 = st.nality()
    if regime != "vacuum":                     # never trust a seed again without checking it landed
        expected = {"meson": ("mesonic", "baryonic"),   # Z2 meson reads 'mesonic'; Z3 too
                    "baryon": ("baryonic",)}[regime]
        assert n0["kind"] in expected, (regime, n0)

    driver = DriverGZN(st, rng_seed=seed, beta_B=BETA_B, beta_E=beta_E)
    live_traj, kinds, boundary_hits = [], [], 0
    t_vacuum, removal_exited = None, None
    for step in range(steps):
        driver.advance()
        assert st.check_gauss(), "PA violated"
        live = st.live_defects()
        kinds.append(st.nality()["kind"])
        live_traj.append(len(live))
        if any(v in st.boundary_vertices for v in live):
            boundary_hits += 1
        if t_vacuum is None and not live:
            t_vacuum = step + 1
            removal_exited = st.exited_charge()

    kc = Counter(kinds)
    total = len(kinds)
    seeded_kind = n0["kind"]
    return {
        "group": group, "regime": regime, "seed": seed, "beta_E": beta_E, "steps": steps,
        "seed_info": info,
        "initial_nality": {"kind": seeded_kind, "constituents": n0["constituents"]},
        "t_vacuum": t_vacuum,
        "survived_to_horizon": t_vacuum is None,
        "exited_charge_at_vacuum": removal_exited,
        "frac_boundary_occupied": round(boundary_hits / total, 3),
        f"frac_{seeded_kind}": round(kc.get(seeded_kind, 0) / total, 3),
        "frac_baryonic": round(kc.get("baryonic", 0) / total, 3),
        "frac_vacuum": round(kc.get("vacuum", 0) / total, 3),
        "mean_live_defects": round(statistics.mean(live_traj), 2),
        "max_live_defects": max(live_traj),
    }


def key_frac(r):
    """The 'still looks like what we seeded' fraction, whatever the seeded kind was."""
    k = r["initial_nality"]["kind"]
    return r.get(f"frac_{k}", 0.0) if k != "vacuum" else r["frac_vacuum"]


# ------------------------------------------------------------------ PD: sector decoupling
CURV_FACE_INDEX = 7


def run_decoupling(seed, with_string: bool, co_locate: bool):
    """Identical magnetic initial condition and rng stream; the only difference is whether an
    electric string exists and where it sits relative to a seeded curved cluster.

    Co-location deliberately places one charge endpoint ON the curvature, which creates a positive
    charge-curvature correlation at t=0 BY CONSTRUCTION.  The factorisation claim is that this
    correlation must then decay to control level as the charge diffuses away -- not that it starts
    small.  Early-quarter vs tail-quarter means are therefore both reported.
    """
    st = GaussStateZN(kuhn_ball("Z3", n=N_MESH))
    tri = st.cx.faces()[CURV_FACE_INDEX]
    for (u, w) in ((tri[0], tri[1]), (tri[1], tri[2])):
        st.shift_g((u, w), 1)
    curv_site = tri[0]

    if with_string:
        if co_locate:
            far = max(interior(st), key=lambda v: (_bfs(st, curv_site).get(v, -1), -v))
            path = st.shortest_path(curv_site, far)
            assert path and len(path) - 1 >= 2, "co-located arm degenerated to nothing"
        else:
            a, b, _ = pick_meson_sites(st)
            path = st.shortest_path(a, b)
        st.load_string(path, flux=1)

    driver = DriverGZN(st, rng_seed=seed, beta_B=BETA_B, beta_E=COLD[-1])
    magE, corrs = [], []
    for _ in range(STEPS_PLASMA):
        driver.advance()
        magE.append(st.magnetic_energy_count())
        corrs.append(charge_curvature_correlation(st))
    q1 = slice(0, STEPS_PLASMA // 4)
    tail = slice(STEPS_PLASMA * 3 // 4, None)
    return {
        "seed": seed, "with_string": with_string, "co_locate": co_locate,
        "mean_magE_tail": round(statistics.mean(magE[tail]), 3),
        "corr_early": round(statistics.mean(abs(c) for c in corrs[q1]), 4),
        "corr_tail": round(statistics.mean(abs(c) for c in corrs[tail]), 4),
    }


# ------------------------------------------------------------------ main
def main():
    results = {"config": {"mesh": N_MESH, "steps_plasma": STEPS_PLASMA, "steps_life": STEPS_LIFE,
                          "beta_B": BETA_B, "plasma_scan": list(PLASMA_SCAN), "cold": list(COLD),
                          "steps_long": STEPS_LONG, "seeds": list(SEEDS)},
               "classification": [], "plasma": {}, "lifetimes": {}, "decoupling": []}

    print("=== A. classification of seeded composites (deterministic) ===")
    print(f"{'group':>6} {'regime':>8} | {'kind':>9} {'pairs':>5} {'constituents':>12} {'total q':>7}")
    for group in ("Z2", "Z3", "Z4"):
        for regime in ("vacuum", "meson", "baryon"):
            if group == "Z2" and regime == "baryon":
                continue                      # PB: Z2 cannot carry baryonic content at all
            st, info = seed_regime(group, regime)
            nal = st.nality()
            results["classification"].append(
                {"group": group, "regime": regime,
                 **{k: (list(v) if isinstance(v, tuple) else v) for k, v in nal.items()},
                 "seed_info": {k: val for k, val in info.items() if k != "sites"}})
            print(f"{group:>6} {regime:>8} | {nal['kind']:>9} {nal['pairs']:>5} "
                  f"{nal['constituents']:>12} {nal['total_charge']:>7}")

    print("\n=== B0. plasma threshold: is 'vacuum' empty enough to talk about single objects? ===")
    print(f"{'beta_E':>7} | {'mean #live (unseeded)':>21} {'frac_baryonic':>13} {'max #live':>9}")
    for beta_E in PLASMA_SCAN:
        rows = [run("Z3", "vacuum", s, beta_E, STEPS_PLASMA) for s in SEEDS]
        results["plasma"][str(beta_E)] = rows
        print(f"{beta_E:>7.1f} | {statistics.mean(r['mean_live_defects'] for r in rows):>21.2f} "
              f"{statistics.mean(r['frac_baryonic'] for r in rows):>13.3f} "
              f"{max(r['max_live_defects'] for r in rows):>9}")

    print("\n=== B1. lifetimes in the COLD regimes (%d steps x %d seeds) ===" % (STEPS_LIFE, len(SEEDS)))
    print(f"{'group':>5} {'regime':>7} {'beta_E':>6} | {'median t_vac':>12} {'survivors':>9} "
          f"{'frac still-seeded-kind':>20} {'mean #live':>10} {'bdry occ':>8}")
    for beta_E in COLD:
        for group, regime in (("Z2", "meson"), ("Z3", "meson"), ("Z3", "baryon")):
            rows = [run(group, regime, s, beta_E, STEPS_LIFE) for s in SEEDS]
            results["lifetimes"][f"{group}/{regime}/{beta_E}"] = rows
            tv = [r["t_vacuum"] for r in rows if r["t_vacuum"] is not None]
            med = statistics.median(tv) if tv else None
            surv = sum(r["survived_to_horizon"] for r in rows)
            print(f"{group:>5} {regime:>7} {beta_E:>6.1f} | {str(med):>12} "
                  f"{f'{surv}/{len(rows)}':>9} {statistics.mean(key_frac(r) for r in rows):>20.3f} "
                  f"{statistics.mean(r['mean_live_defects'] for r in rows):>10.2f} "
                  f"{statistics.mean(r['frac_boundary_occupied'] for r in rows):>8.3f}")

    print("\n=== B2. long horizon at beta_E=%.0f: is the hindrance heavy-tailed? (%d steps x %d seeds) ==="
          % (COLD[-1], STEPS_LONG, len(SEEDS)))
    print(f"{'regime':>7} | {'t_vacuum per seed':>46} {'survivors':>9} {'frac_baryonic':>13}")
    for regime in ("meson", "baryon"):
        rows = [run("Z3", regime, s, COLD[-1], STEPS_LONG) for s in SEEDS]
        results["long_horizon"] = results.get("long_horizon", {})
        results["long_horizon"][regime] = rows
        tv = [r["t_vacuum"] for r in rows]
        surv = sum(r["survived_to_horizon"] for r in rows)
        print(f"{regime:>7} | {str(tv):>46} {f'{surv}/{len(rows)}':>9} "
              f"{statistics.mean(r['frac_baryonic'] for r in rows):>13.3f}")

    print("\n=== C. flux-charge decoupling (PD) ===")
    print(f"{'string?':>8} {'co-located?':>12} | {'magE(tail)':>10} {'corr early':>10} {'corr tail':>10}")
    for with_string, co_locate in ((False, False), (True, False), (True, True)):
        rows = [run_decoupling(s, with_string, co_locate) for s in range(4)]
        results["decoupling"].append({"with_string": with_string, "co_locate": co_locate, "runs": rows})
        print(f"{str(with_string):>8} {str(co_locate):>12} | "
              f"{statistics.mean(r['mean_magE_tail'] for r in rows):>10.3f} "
              f"{statistics.mean(r['corr_early'] for r in rows):>10.4f} "
              f"{statistics.mean(r['corr_tail'] for r in rows):>10.4f}")

    out = (Path(__file__).resolve().parents[1] / "reference" / "local_qwen" / "data"
           / "e069_nality_dyons.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
