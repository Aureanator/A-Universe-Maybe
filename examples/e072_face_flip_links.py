"""E072 -- face-boundary dynamics: does a LOCAL divergence-preserving move set make topology protective?

Run:  ./.venv/Scripts/python.exe examples/e072_face_flip_links.py
Writes reference/local_qwen/data/e072_face_flip_links.json

Priors FA-FE were registered in docs/PREDICTIONS.md ("E072") BEFORE this file was written.

THE MOVE SET IS THE POINT. DriverHZN updates flux only along the boundary of one elementary triangle. Such a
move cannot create charge, so starting from a charge-free fixture the support stays a union of closed cycles at
EVERY step -- for the first time in this project a link class is an observable of the evolving state rather than
only of a prepared one (E071: divergence-free for 3-10% of steps; here it must be 100%, asserted). Energy is
electric length only, so decay needs configurations that are LONGER, not merely allowed -- a barrier whose
origin would be topological rather than imposed, which is what E070 said protection has to look like.

Fixtures are the verified E071 ones (single square loop; Hopf pair with Lk = -1; matched unlinked pair with
Lk = 0). Grid coordinates are used only to embed cycles for linking-number measurement, never in any rule.
Topological readout is done for Z2, where the mod-2 support decomposes exactly into edge-disjoint cycles; the
Z3 arms are reported energetically (a mod-3 decomposition needs a balanced integer lift -- stated limitation).
"""

from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

from constraintnet.drivers import DriverHZN          # noqa: E402
from constraintnet.gauss_zn import GaussStateZN      # noqa: E402
from constraintnet.linking import linking_number     # noqa: E402
from constraintnet.seeds import kuhn_ball            # noqa: E402

LOOP_A = [(1, 1, 2), (3, 1, 2), (3, 3, 2), (1, 3, 2)]
LOOP_B = [(2, 2, 1), (2, 4, 1), (2, 4, 3), (2, 2, 3)]
LOOP_BP = [(0, 1, 1), (0, 3, 1), (0, 3, 3), (0, 1, 3)]

N_MESH = 4
BETA_E = 4.0
HORIZON = 20000
SNAP_STRIDE = 100
TOPO_STRIDE = 500
SEEDS = (0, 1, 2)
MAX_CYCLES_FOR_TOPO = 6
MAX_CYCLE_LEN = 80


def lattice_path(pts):
    out = [tuple(pts[0])]
    for p, q in zip(pts, pts[1:] + pts[:1]):
        cur = list(p)
        for ax in range(3):
            while cur[ax] != q[ax]:
                cur[ax] += 1 if q[ax] > cur[ax] else -1
                out.append(tuple(cur))
    return out[:-1]


def build(group, arm):
    cx = kuhn_ball(group, n=N_MESH)
    gmap = {cx.vertex(v).metadata["grid"]: v for v in cx.vertices()}
    st = GaussStateZN(cx)
    loops = {"single": ["A"], "linked": ["A", "B"], "unlinked": ["A", "Bp"]}[arm]
    table = {"A": LOOP_A, "B": LOOP_B, "Bp": LOOP_BP}
    for name in loops:
        verts = [gmap[g] for g in lattice_path(table[name])]
        st.load_string(verts + [verts[0]], flux=1)
    assert all(q == 0 for q in st.charges().values()), "fixture must be charge-free"
    return st, {v: cx.vertex(v).metadata["grid"] for v in cx.vertices()}


def cycles_mod2(st):
    """Decompose the mod-2 flux support into closed trails (edge-disjoint; exact for Z2)."""
    inc = defaultdict(list)
    used = [False] * len(st.E)
    for i, a in enumerate(st.E):
        if a % 2 == 1:
            u, w = st.edges[i]
            inc[u].append(i)
            inc[w].append(i)

    def other(i, v):
        u, w = st.edges[i]
        return w if u == v else u

    cycles = []
    for s in sorted(inc):
        while any(not used[i] for i in inc[s]):
            cyc, cur = [s], s
            while True:
                opts = [i for i in inc[cur] if not used[i]]
                if not opts:
                    break
                e = opts[0]
                used[e] = True
                cur = other(e, cur)
                cyc.append(cur)
                if cur == s:
                    break
            if len(cyc) >= 4 and cyc[0] == cyc[-1]:
                cycles.append(cyc)
    return cycles


def linking_profile(st, pos):
    """(|linked pairs|, computable?, skipped?) for the current support."""
    cycles = cycles_mod2(st)
    if not cycles:
        return 0, False, "no-cycles"
    if len(cycles) < 2:
        return 0, True, "single-cycle"
    if len(cycles) > MAX_CYCLES_FOR_TOPO or any(len(c) - 1 > MAX_CYCLE_LEN for c in cycles):
        return 0, False, "too-complex"

    def segs(cyc):
        pts = [pos[v] for v in cyc]
        return list(zip(pts, pts[1:]))

    linked = 0
    computable = False
    for i in range(len(cycles)):
        for j in range(i + 1, len(cycles)):
            try:
                lk = linking_number(segs(cycles[i]), segs(cycles[j]))
            except Exception:
                continue
            computable = True
            if lk != 0:
                linked += 1
    return linked, computable, ("ok" if computable else "degenerate")


def run(group, arm, seed):
    st, pos = build(group, arm)
    driver = DriverHZN(st, rng_seed=seed, beta_E=BETA_E)
    L0 = st.electric_count()

    lengths = []
    max_upward = 0.0
    t_vacuum = None
    hit_support_steps = 0
    topo = []                      # (step, linked_pairs, computable, note, length)
    for step in range(HORIZON):
        driver.advance()
        assert all(q == 0 for q in st.charges().values()), "FA FAILED: face dynamics created charge"
        L = st.electric_count()
        if L > L0:
            max_upward = max(max_upward, L - L0)
        if driver.last_hit_support:
            hit_support_steps += 1
        if t_vacuum is None and L == 0:
            t_vacuum = step + 1
        if step % SNAP_STRIDE == 0:
            lengths.append(L)
        if group == "Z2" and step % TOPO_STRIDE == 0 and L > 0:
            linked, ok, note = linking_profile(st, pos)
            topo.append((step, linked, ok, note, L))

    # unlinking event: last snapshot with a linked pair before flux persists without one
    usable = [t for t in topo if t[3] == "ok"]
    rho_link = (sum(1 for t in usable if t[1] > 0) / len(usable)) if usable else None
    unlink_step, unlink_len_above_median = None, None
    seen_linked = False
    for idx, t in enumerate(usable):
        if t[1] > 0:
            seen_linked = True
        elif seen_linked and unlink_step is None:
            unlink_step = t[0]
            prior = [u[4] for u in usable[:idx]]
            med = statistics.median(prior) if prior else None
            unlink_len_above_median = (t[4] > med) if med is not None else None

    return {
        "group": group, "arm": arm, "seed": seed, "L0": L0,
        "t_vacuum": t_vacuum, "survived_to_horizon": t_vacuum is None,
        "max_upward_excursion": max_upward,
        "frac_accepted_moves_touching_support": round(hit_support_steps / HORIZON, 4),
        "final_length": st.electric_count(),
        "mean_length_sampled": round(statistics.mean(lengths), 2) if lengths else None,
        "rho_link": rho_link,
        "topo_snapshots_usable": len(usable),
        "topo_snapshots_skipped": len(topo) - len(usable),
        "unlink_step": unlink_step,
        "unlink_length_above_running_median": unlink_len_above_median,
    }


def main():
    results = {"config": {"mesh": N_MESH, "beta_E": BETA_E, "horizon": HORIZON,
                          "snap_stride": SNAP_STRIDE, "topo_stride": TOPO_STRIDE,
                          "seeds": list(SEEDS), "move": "elementary face boundary (divergence-preserving)"},
               "runs": []}

    print(f"{'group':>5} {'arm':>9} | {'t_vacuum per seed':>34} {'surv':>5} {'maxup':>6} "
          f"{'rho_link':>8} {'unlink@':>8} {'above med':>9} {'hit supp':>8}")
    summary = {}
    for group in ("Z2", "Z3"):
        for arm in ("single", "linked", "unlinked"):
            rows = [run(group, arm, s) for s in SEEDS]
            results["runs"].extend(rows)
            tv = [r["t_vacuum"] for r in rows if r["t_vacuum"] is not None]
            surv = sum(r["survived_to_horizon"] for r in rows)
            med = statistics.median(tv) if tv else None
            rl = [r["rho_link"] for r in rows if r["rho_link"] is not None]
            summary[f"{group}/{arm}"] = {
                "median_t_vacuum": med, "survivors": surv,
                "max_upward": max(r["max_upward_excursion"] for r in rows),
                "rho_link_mean": round(statistics.mean(rl), 3) if rl else None,
                "hit_support": round(statistics.mean(r["frac_accepted_moves_touching_support"] for r in rows), 4),
            }
            print(f"{group:>5} {arm:>9} | {str([r['t_vacuum'] for r in rows]):>34} {surv:>5} "
                  f"{summary[f'{group}/{arm}']['max_upward']:>6.0f} "
                  f"{str(summary[f'{group}/{arm}']['rho_link_mean']):>8} "
                  f"{str([r['unlink_step'] for r in rows]):>8} "
                  f"{str([r['unlink_length_above_running_median'] for r in rows]):>9} "
                  f"{summary[f'{group}/{arm}']['hit_support']:>8.4f}")

    print("\n--- FC check: linked vs unlinked (matched flux length) ---")
    for group in ("Z2", "Z3"):
        lk, ul = summary[f"{group}/linked"], summary[f"{group}/unlinked"]
        print(f"{group}: linked median {lk['median_t_vacuum']} (survivors {lk['survivors']}/"
              f"{len(SEEDS)}), unlinked median {ul['median_t_vacuum']} (survivors {ul['survivors']}/"
              f"{len(SEEDS)}) | rho_link {lk['rho_link_mean']} vs {ul['rho_link_mean']}")

    results["summary"] = summary
    out = ROOT / "reference" / "local_qwen" / "data" / "e072_face_flip_links.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
