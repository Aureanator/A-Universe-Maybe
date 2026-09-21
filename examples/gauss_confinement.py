"""Hard Gauss completion v1: matter-coupled Z2 phase space, confinement + vacuum stability.

Run: python examples/gauss_confinement.py
Writes reference/local_qwen/data/gauss_completion.json.

HANDOFF correction 2 demanded an EXPLICIT construction of a charge-sector/matter-coupled
Gauss constraint (the projector model's bare charges violate literal A_v=1). E066 showed
whole-complex RELATIONAL acceptance cannot confine anything -- it heats the vacuum and
naive lineage tracking follows the heat. This study builds the completion and measures
what constraint-plus-energy protects. Priors stated BEFORE running:

G1  STRUCTURAL (provable, asserted every step): with charges DEFINED as q_v = div(E)_v,
    total charge parity is identically even; an isolated charge cannot be configured --
    charges are string endpoints. Gauss holds by construction, not penalty.
G2  VACUUM STABILITY (contrast E066). Prior: energy-based Metropolis at high beta_B keeps
    the magnetic sector cold (#curved faces ~ 0), because heating was an artifact of
    relational acceptance, not intrinsic to the model. If magE grows anyway, that is a bug.
G3  CONFINEMENT SCALE. Prior: beta_E (energy per flux edge) suppresses spurious electric
    pairs monotonically -- mean charge count falls toward the seeded pair as beta_E rises;
    at high beta_E the seeded interior pair persists (string cannot cheaply break).

Boundary-exit demo defines the open channel P32-3 asked for: a charge reaching the boundary
is absorbed by the exterior reservoir (exited_charge), total parity STILL even.

Scope, stated plainly: CLASSICAL Z2 phase space (connection bits + electric flux bits);
not quantum amplitudes, not nonabelian. That is what "completion v1" means here.
"""

import json
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.drivers import DriverG
from constraintnet.gauss import GaussState
from constraintnet.seeds import kuhn_ball

N = 3
STEPS = 600
SEEDS = (0, 1, 2, 3)
BETA_B = 8.0
BETA_E_SCAN = (0.0, 1.0, 2.0, 4.0, 8.0)


def far_interior_pair(st):
    interior = [v for v in st.vertices if v not in st.boundary_vertices]
    best, bestd = None, -1
    for i, a in enumerate(interior):
        for b in interior[i + 1:]:
            p = st.shortest_path(a, b)
            d = len(p) - 1 if p else -1
            if d > bestd:
                best, bestd = (a, b), d
    return best[0], best[1], bestd


def run(beta_E, seed):
    cx = kuhn_ball("Z2", n=N)
    st = GaussState(cx)
    a, b, sep0 = far_interior_pair(st)
    st.load_string(st.shortest_path(a, b))
    assert sorted(v for v, q in st.charges().items() if q) == sorted([a, b])
    driver = DriverG(st, rng_seed=seed, beta_B=BETA_B, beta_E=beta_E)

    counts = []          # live charge count per step
    seps_when_pair = []  # separation when exactly two charges remain
    magE = []
    for _ in range(STEPS):
        driver.advance()
        assert st.check_gauss(), "Gauss violated -- impossible by construction"
        q = [v for v, qv in st.charges().items() if qv]
        counts.append(len(q))
        magE.append(st.magnetic_energy_count())
        if len(q) == 2:
            p = st.shortest_path(q[0], q[1])
            seps_when_pair.append((len(p) - 1) if p else sep0)

    state_frac = Counter()
    for c in counts:
        key = "vacuum" if c == 0 else ("bound-pair" if c == 2 else "multi")
        state_frac[key] += 1
    total = len(counts)
    return {
        "beta_E": beta_E, "seed": seed, "initial_separation": sep0,
        "frac_vacuum": round(state_frac["vacuum"] / total, 3),
        "frac_bound_pair": round(state_frac["bound-pair"] / total, 3),
        "frac_multi": round(state_frac["multi"] / total, 3),
        "mean_charge_count": round(statistics.mean(counts), 2),
        "final_charge_count": counts[-1],
        "mean_sep_when_pair": (round(statistics.mean(seps_when_pair), 2)
                               if seps_when_pair else None),
        "sep_ratio_when_pair": (round(statistics.mean(seps_when_pair) / sep0, 3)
                                if seps_when_pair else None),
        "magE_final": magE[-1], "magE_max": max(magE),
    }


def boundary_exit_demo(seed=0):
    """Seed a pair with one endpoint adjacent to the boundary; watch it get absorbed."""
    cx = kuhn_ball("Z2", n=N)
    st = GaussState(cx)
    interior = [v for v in st.vertices if v not in st.boundary_vertices]
    # pick an interior vertex whose shortest path to a boundary vertex is length 1
    a = next(v for v in interior
             if any(nb in st.boundary_vertices for nb in
                    {w for (x, w) in st.edges if x == v} | {x for (x, w) in st.edges if w == v}))
    b = interior[len(interior) // 2]
    st.load_string(st.shortest_path(a, b))
    driver = DriverG(st, rng_seed=seed, beta_B=BETA_B, beta_E=8.0)
    exited_seen = parity_ok = True
    min_charge_count = 99
    for _ in range(STEPS):
        driver.advance()
        parity_ok &= st.check_gauss()
        q = [v for v, qv in st.charges().items() if qv]
        min_charge_count = min(min_charge_count, len(q))
        exited_seen &= (st.exited_charge() >= 0)
    return {"seed": seed, "gauss_held_throughout": bool(parity_ok),
            "final_exited_charge": st.exited_charge(),
            "min_live_charges": min_charge_count}


def main():
    scan = {str(b): [] for b in BETA_E_SCAN}
    print(f"{'beta_E':>7} | mean#chg frac_vac frac_pair frac_multi  sep_ratio  magE_max")
    for beta_E in BETA_E_SCAN:
        rows = [run(beta_E, s) for s in SEEDS]
        scan[str(beta_E)] = rows
        m = lambda k: statistics.mean(r[k] for r in rows if r[k] is not None)
        print(f"{beta_E:>7.1f} | {m('mean_charge_count'):>7.2f} "
              f"{m('frac_vacuum'):>7.2f} {m('frac_bound_pair'):>9.2f} {m('frac_multi'):>10.2f}  "
              f"{(m('sep_ratio_when_pair') if any(r['sep_ratio_when_pair'] is not None for r in rows) else float('nan')):>8.2f}  "
              f"{max(r['magE_max'] for r in rows)}")

    exit_demo = boundary_exit_demo()
    print("\nBoundary-exit (open channel):", json.dumps(exit_demo))

    # verdicts against priors G1-G3
    cold = all(r["magE_max"] == 0 for b in scan.values() for r in b)
    mono = all(statistics.mean(r["mean_charge_count"] for r in scan[str(x)]) >=
               statistics.mean(r["mean_charge_count"] for r in scan[str(y)]) - 1e-9
               for x, y in zip(BETA_E_SCAN[:-1], BETA_E_SCAN[1:]))
    verdict = {
        "G1_gauss_by_construction": True,   # asserted every step; would have raised
        "G2_vacuum_cold_all_betaE": cold,
        "G3_charge_count_monotone_decreasing_in_betaE": bool(mono),
    }
    print("\nVERDICTS:", json.dumps(verdict))

    payload = {
        "provenance": {
            "script": "examples/gauss_confinement.py",
            "model": "local Qwen (LM Studio), E067 hard-Gauss completion v1",
            "nature": ("explicit classical Z2 matter-coupled Gauss construction; priors G1-G3 "
                       "stated in docstring before running; Gauss asserted every step"),
        },
        "config": {"n": N, "steps": STEPS, "seeds": list(SEEDS), "beta_B": BETA_B,
                   "beta_E_scan": list(BETA_E_SCAN)},
        "scan": scan,
        "boundary_exit_demo": exit_demo,
        "verdicts": verdict,
    }
    out = (Path(__file__).resolve().parents[1]
           / "reference" / "local_qwen" / "data" / "gauss_completion.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
