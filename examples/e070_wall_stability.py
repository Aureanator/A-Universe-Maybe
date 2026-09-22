"""E070 -- what does stability actually cost? Hard wall (superselection) vs soft wall (Kramers).

Run:  ./.venv/Scripts/python.exe examples/e070_wall_stability.py
Writes reference/local_qwen/data/e070_wall_stability.json and figures/e070_arrhenius.png

Priors SA-SD were registered in docs/PREDICTIONS.md ("E070") BEFORE this file was written. Restated:
  SA  with a hard wall the enclosed charge sum is invariant under every allowed move;
  SB  a hard wall makes the enclosed charge absolutely stable (lifetime = horizon) while the no-wall
      control decays near E069's value (~1800 steps at beta_E=12);
  SC  with a soft wall of weight lambda, first-passage time grows exponentially in lambda (Kramers),
      log t ~ c*lambda, with censoring at the top of the scan;
  SD  if the hard wall does NOT stabilize, restricting admissible rewrites is not sufficient and some
      unmodelled channel is doing the work -- the most interesting possible outcome.

HONESTY NOTE.  The wall is IMPOSED structure: a boundary condition on which rewrites are admissible.
Nothing here claims that walls emerge.  The purpose is to measure what a stability mechanism must look
like in this framework, so that an emergent candidate can be held up against it.  The wall is defined
relationally (BFS layers of the 1-skeleton), never from grid coordinates.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from constraintnet.drivers import DriverGZN          # noqa: E402
from constraintnet.gauss_zn import GaussStateZN      # noqa: E402
from constraintnet.seeds import kuhn_ball            # noqa: E402

N_MESH = 3
BETA_B = 6.0
BETA_E = 12.0
HORIZON = 8000
SEEDS = (0, 1, 2)
LAMBDA_SCAN = (1.0, 2.0, 4.0, 8.0)


def seed_enclosed(st, k=1, hard=True, lam=1.0):
    """Seed a meson across the layer-k sphere around a vertex, then impose that sphere as a wall.

    Returns (source, enclosed_region).  The string carries flux through the sphere, so the region is
    left with net charge sum != 0: inside must contain at least one defect for as long as the crossing
    flux cannot be undone.
    """
    pool = [v for v in st.vertices if v not in st.boundary_vertices]
    src = max(pool, key=lambda v: len(st.wall_between_layers(v, k)))
    dist = st.bfs_layers(src)
    outside = min(w for w in st.vertices if dist.get(w, -1) > k)
    st.load_string(st.shortest_path(src, outside), flux=1)
    region = frozenset(v for v, d in dist.items() if d <= k)
    wall = st.wall_between_layers(src, k)
    if hard or lam != 1.0:
        st.apply_wall(wall, hard=hard, lam=lam)
    return src, region


def run_case(mode, seed, lam=None):
    """mode in {'control','soft','hard'}; returns first-passage diagnostics."""
    st = GaussStateZN(kuhn_ball("Z3", n=N_MESH))
    if mode == "control":
        pool = [v for v in st.vertices if v not in st.boundary_vertices]
        src = max(pool, key=lambda v: len(st.wall_between_layers(v, 1)))
        dist = st.bfs_layers(src)
        outside = min(w for w in st.vertices if dist.get(w, -1) > 1)
        st.load_string(st.shortest_path(src, outside), flux=1)
        region = frozenset(v for v, d in dist.items() if d <= 1)
    else:
        _, region = seed_enclosed(st, k=1, hard=(mode == "hard"), lam=(lam or 1.0))

    q_in_0 = st.region_charge(region)
    driver = DriverGZN(st, rng_seed=seed, beta_B=BETA_B, beta_E=BETA_E)

    # census of accepted moves that touch the wall: does lambda ever gate one?  A move that only
    # REDUCES crossing flux is downhill for every lambda, so it cannot be blocked by raising lambda.
    wall_idx = [st._eindex[e] for e in st.wall]
    def crossing_load():
        return sum(GaussStateZN.weight(st.E[i], st.N) for i in wall_idx)
    load_before = crossing_load()
    wall_moves = {"up": 0, "down": 0}

    t_region_neutral = None       # first step where the enclosed sector can be empty again
    min_live_inside = 99
    leak_detected = False
    for step in range(HORIZON):
        driver.advance()
        load_after = crossing_load()
        if load_after != load_before:
            wall_moves["up" if load_after > load_before else "down"] += abs(load_after - load_before)
        load_before = load_after
        assert st.check_gauss(), "Gauss violated -- impossible by construction"
        q_in = st.region_charge(region)
        if mode == "hard":
            assert q_in == q_in_0, "HARD WALL LEAKED -- SA false, investigate before anything else"
        if q_in != q_in_0 and not leak_detected:
            leak_detected = True
        live_inside = [v for v in st.live_defects() if v in region]
        min_live_inside = min(min_live_inside, len(live_inside))
        if t_region_neutral is None and q_in == 0:
            t_region_neutral = step + 1

    return {
        "mode": mode, "lam": lam, "seed": seed,
        "q_in_initial": q_in_0,
        "t_region_neutral": t_region_neutral,
        "survived_to_horizon": t_region_neutral is None,
        "min_live_inside": min_live_inside,
        "final_q_in": st.region_charge(region),
        "wall_moves_up": wall_moves["up"],
        "wall_moves_down": wall_moves["down"],
    }


def main():
    results = {"config": {"mesh": N_MESH, "beta_B": BETA_B, "beta_E": BETA_E,
                          "horizon": HORIZON, "seeds": list(SEEDS), "lambdas": list(LAMBDA_SCAN)},
               "hard_wall": [], "control": [], "soft_scan": {}}

    print("=== A. hard wall vs no-wall control (Z3, beta_E=%.0f, horizon %d) ===" % (BETA_E, HORIZON))
    print(f"{'mode':>8} | {'t_region_neutral per seed':>34} {'survivors':>9} {'min live inside':>15}")
    for mode in ("control", "hard"):
        rows = [run_case(mode, s) for s in SEEDS]
        results[{"control": "control", "hard": "hard_wall"}[mode]] = rows
        tv = [r["t_region_neutral"] for r in rows]
        surv = sum(r["survived_to_horizon"] for r in rows)
        print(f"{mode:>8} | {str(tv):>34} {f'{surv}/{len(rows)}':>9} "
              f"{min(r['min_live_inside'] for r in rows):>15}")

    print("\n=== B. soft wall Kramers scan (log first-passage time vs barrier weight lambda) ===")
    print(f"{'lambda':>7} | {'t_region_neutral per seed':>34} {'survivors':>9} {'median log10 t':>14}")
    medians = {}
    for lam in LAMBDA_SCAN:
        rows = [run_case("soft", s, lam=lam) for s in SEEDS]
        results["soft_scan"][str(lam)] = rows
        tv = [r["t_region_neutral"] for r in rows if r["t_region_neutral"] is not None]
        surv = sum(r["survived_to_horizon"] for r in rows)
        med = statistics.median(tv) if tv else None
        medians[lam] = med
        lg = round(math.log10(med), 3) if med else None
        ups = sum(r["wall_moves_up"] for r in rows)
        downs = sum(r["wall_moves_down"] for r in rows)
        print(f"{lam:>7.1f} | {str([r['t_region_neutral'] for r in rows]):>34} "
              f"{f'{surv}/{len(rows)}':>9} {str(lg):>14} | wall moves up={ups} down={downs}")

    usable = [(l, m) for l, m in medians.items() if m]
    if len(usable) >= 2:
        xs = [math.log(l) for l, _ in usable]
        ys = [math.log(m) for _, m in usable]
        n = len(xs)
        mx, my = sum(xs) / n, sum(ys) / n
        slope = (sum((x - mx) * (y - my) for x, y in zip(xs, ys))
                 / sum((x - mx) ** 2 for x in xs)) if sum((x - mx) ** 2 for x in xs) else float("nan")
        results["arrhenius_slope_log_t_vs_log_lambda"] = round(slope, 3)
        print(f"\nlog-log slope (t vs lambda) over usable points: {slope:.3f}   "
              f"(Kramers-like if ~lambda-linear in log t; SC expects positive)")

    out_json = ROOT / "reference" / "local_qwen" / "data" / "e070_wall_stability.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out_json}")

    # ---- Arrhenius figure ---------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.4, 4.4), dpi=110)
    xs = [l for l, m in usable]
    ys = [m for l, m in usable]
    ax.semilogy(xs, ys, "o-", color="#1565c0", label="soft wall median first-passage")
    ctrl = [r["t_region_neutral"] for r in results["control"] if r["t_region_neutral"]]
    if ctrl:
        ax.axhline(statistics.median(ctrl), color="#9e9e9e", ls="--", lw=1, label="no-wall control")
    ax.axhline(HORIZON, color="#c62828", ls=":", lw=1, label=f"censoring horizon {HORIZON}")
    for l, m in usable:
        ax.annotate(f"{int(m)}", (l, m), textcoords="offset points", xytext=(4, 6), fontsize=8)
    ax.set_xlabel("wall weight $\\lambda$ (extra energy per unit crossing flux)")
    ax.set_ylabel("median time to neutralise enclosed sector")
    ax.set_title("E070 · cost of stability: superselection (flat) vs Kramers barrier (rising)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.25, which="both")
    out_png = ROOT / "reference" / "local_qwen" / "figures" / "e070_arrhenius.png"
    fig.tight_layout()
    fig.savefig(out_png)
    print(f"wrote {out_png}")


if __name__ == "__main__":
    main()
