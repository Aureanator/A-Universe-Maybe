"""E071 -- does LINK TYPE protect electric flux? Hopf pair vs matched unlinked pair, same move law.

Run:  ./.venv/Scripts/python.exe examples/e071_link_lifetime.py
Writes reference/local_qwen/data/e071_link_lifetime.json

Priors LA-LE were registered in docs/PREDICTIONS.md ("E071") BEFORE this file was written. In short:
  LA  no protection -- linked and unlinked matched pairs decay at the same rate, because decay deletes one
      flux edge at a time and deleting an edge never has to change the link type of what is left;
  LB  deletion dominates creations at beta_E = 12 (decay nearly monotone in total flux length);
  LC  the invariant is mostly UNDEFINED along trajectories -- delete one edge of a closed loop and you
      create two charges, so the support stops being a union of loops almost immediately;
  LD  proposition: restricting moves to divergence-preserving ones admits NO single-edge move at all, so
      "charge-free = protected" is really "charge-free = frozen";
  LE  discovery condition: linked >> unlinked by more than seed scatter (would contradict LA's mechanism).

FIXTURES are prepared states (declared as such -- not emergent), verified before use: on the n=4 Kuhn ball,
A = 8-edge square loop at z=2; B = 8-edge rectangle with linking_number(A,B) = -1 (Hopf link); B' = same
shape displaced with linking_number(A,B') = 0. Grid coordinates are used ONLY to build and measure the
fixtures; no acceptance rule, energy or move in the dynamics sees them (spec prohibition).

Context: P13-P15 settled this question for MAGNETIC flux under the curvature action (no barrier). This is
the electric sector built in E067-E069 -- closed div E = 0 flux with no charges at all.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from constraintnet.drivers import DriverGZN          # noqa: E402
from constraintnet.gauss_zn import GaussStateZN      # noqa: E402
from constraintnet.linking import linking_number     # noqa: E402
from constraintnet.seeds import kuhn_ball            # noqa: E402

N_MESH = 4
BETA_B = 6.0
BETA_E = 12.0
HORIZON = 2000
SEEDS = (0, 1, 2, 3)
GROUPS = ("Z2", "Z3")

# --- prepared fixtures (lattice polygons; closed => div E = 0 => no charges) -------------
LOOP_A = [(1, 1, 2), (3, 1, 2), (3, 3, 2), (1, 3, 2)]          # square at z=2
LOOP_B = [(2, 2, 1), (2, 4, 1), (2, 4, 3), (2, 2, 3)]          # threads A: Lk = -1
LOOP_BP = [(0, 1, 1), (0, 3, 1), (0, 3, 3), (0, 1, 3)]         # displaced: Lk = 0


def lattice_path(pts):
    """Rasterise a lattice polygon into its unit-edge vertex path (closed)."""
    out = [tuple(pts[0])]
    for p, q in zip(pts, pts[1:] + pts[:1]):
        cur = list(p)
        for ax in range(3):
            while cur[ax] != q[ax]:
                cur[ax] += 1 if q[ax] > cur[ax] else -1
                out.append(tuple(cur))
    return out[:-1]


def segments_of(path):
    return list(zip(path, path[1:] + path[:1]))


def build(group):
    cx = kuhn_ball(group, n=N_MESH)
    gmap = {cx.vertex(v).metadata["grid"]: v for v in cx.vertices()}
    st = GaussStateZN(cx)
    paths = {name: [gmap[g] for g in lattice_path(pts)]
             for name, pts in (("A", LOOP_A), ("B", LOOP_B), ("Bp", LOOP_BP))}
    return st, paths


def verify_fixtures():
    """Linking numbers of the prepared fixtures, computed from the embedding (report only)."""
    sa = segments_of(lattice_path(LOOP_A))
    sb = segments_of(lattice_path(LOOP_B))
    sbp = segments_of(lattice_path(LOOP_BP))
    return {"Lk_AB": linking_number(sa, sb), "Lk_ABp": linking_number(sa, sbp),
            "lengths": {n: len(lattice_path(p)) for n, p in
                        (("A", LOOP_A), ("B", LOOP_B), ("Bp", LOOP_BP))}}


def arm_state(st, paths, arm):
    loops = {"single": ["A"], "linked": ["A", "B"], "unlinked": ["A", "Bp"]}[arm]
    for name in loops:
        # close the polygon: load_string walks an OPEN path, so a loop must be given its
        # first vertex again or it seeds charges at both ends instead of a closed flux tube
        st.load_string(list(paths[name]) + [paths[name][0]], flux=1)
    return loops


def run(group, arm, seed):
    st, paths = build(group)
    loops = arm_state(st, paths, arm)

    comp_paths = {n: set(zip(paths[n], paths[n][1:] + paths[n][:1])) for n in loops}
    L0 = st.electric_count()
    assert all(q == 0 for q in st.charges().values()), "fixture must be charge-free"

    driver = DriverGZN(st, rng_seed=seed, beta_B=BETA_B, beta_E=BETA_E)
    L_prev = L0
    deletions = creations = 0
    max_upward = 0.0
    free_steps = 0
    t_vacuum = None
    comp_gone = {}

    for step in range(HORIZON):
        driver.advance()
        assert st.check_gauss(), "Gauss violated -- impossible by construction"
        L = st.electric_count()
        d = L - L_prev
        if d < 0:
            deletions += int(-d)
        elif d > 0:
            creations += int(d)
            max_upward = max(max_upward, L - L0)
        L_prev = L
        if all(q == 0 for q in st.charges().values()):
            free_steps += 1
        if t_vacuum is None and L == 0:
            t_vacuum = step + 1
        for name in loops:
            if name in comp_gone:
                continue
            live_here = sum(1 for (u, w) in comp_paths[name]
                            if st.E[st._eindex[tuple(sorted((u, w)))]] != 0)
            if live_here == 0:
                comp_gone[name] = step + 1

    return {
        "group": group, "arm": arm, "seed": seed, "loops": loops,
        "L0": L0, "t_vacuum_flux": t_vacuum,
        "survived_to_horizon": t_vacuum is None,
        "component_gone_at": comp_gone,
        "deletions": deletions, "creations": creations,
        "max_upward_excursion_over_L0": max_upward,
        "frac_steps_divergence_free": round(free_steps / HORIZON, 4),
    }


def ld_charge_free_is_frozen(group):
    """LD: exhaustively check that no single-edge flux move preserves q == 0 everywhere.

    Changing flux on edge (u,v) by delta shifts q_u by -delta and q_v by +delta, so from a charge-free
    configuration every move creates charges. 'Charge-free is therefore protected' would mean
    'charge-free is frozen': no admissible dynamics at all. Checked once per group, not per run.
    """
    st, paths = build(group)
    arm_state(st, paths, "linked")
    admissible_free = []
    for e in st.edges:
        for delta in range(1, st.N):
            st.add_flux(e, delta)
            if all(q == 0 for q in st.charges().values()):
                admissible_free.append((e, delta))
            st.sub_flux(e, delta)
    return {"group": group, "moves_tested": len(st.edges) * (st.N - 1),
            "charge_free_preserving_moves": len(admissible_free),
            "examples": [list(map(list, m)) for m in admissible_free[:3]]}


def main():
    fixtures = verify_fixtures()
    print("fixtures:", json.dumps(fixtures))
    assert fixtures["Lk_AB"] in (-1, 1) and fixtures["Lk_ABp"] == 0, "fixture verification failed"

    results = {"config": {"mesh": N_MESH, "beta_B": BETA_B, "beta_E": BETA_E,
                          "horizon": HORIZON, "seeds": list(SEEDS)},
               "fixtures": fixtures, "runs": []}

    print("\n--- LD: is the charge-free sector frozen? (exhaustive over single-edge moves) ---")
    results["LD"] = [ld_charge_free_is_frozen(g) for g in GROUPS]
    for r in results["LD"]:
        print(f"{r['group']}: tested {r['moves_tested']} single-edge moves -> "
              f"{r['charge_free_preserving_moves']} preserve q == 0 everywhere"
              + ("   LD FALSE -- investigate" if r["charge_free_preserving_moves"] else "   => frozen"))

    print(f"\n{'group':>5} {'arm':>9} | {'t_vacuum per seed':>32} {'surv':>5} "
          f"{'del':>6} {'cre':>5} {'maxup':>5} {'frac free':>9}")
    summary = {}
    for group in GROUPS:
        for arm in ("single", "linked", "unlinked"):
            rows = [run(group, arm, s) for s in SEEDS]
            results["runs"].extend(rows)
            tv = [r["t_vacuum_flux"] for r in rows if r["t_vacuum_flux"] is not None]
            surv = sum(r["survived_to_horizon"] for r in rows)
            med = statistics.median(tv) if tv else None
            summary[f"{group}/{arm}"] = {
                "median_t": med, "survivors": surv,
                "deletions": sum(r["deletions"] for r in rows),
                "creations": sum(r["creations"] for r in rows),
                "max_upward": max(r["max_upward_excursion_over_L0"] for r in rows),
                "frac_free": round(statistics.mean(r["frac_steps_divergence_free"] for r in rows), 4),
            }
            print(f"{group:>5} {arm:>9} | {str([r['t_vacuum_flux'] for r in rows]):>32} "
                  f"{surv:>5} {summary[f'{group}/{arm}']['deletions']:>6} "
                  f"{summary[f'{group}/{arm}']['creations']:>5} "
                  f"{summary[f'{group}/{arm}']['max_upward']:>5.0f} "
                  f"{summary[f'{group}/{arm}']['frac_free']:>9.4f}")

    print("\n--- LA check: linked vs unlinked (same total flux length) ---")
    for group in GROUPS:
        lk = summary[f"{group}/linked"]["median_t"]
        ul = summary[f"{group}/unlinked"]["median_t"]
        sg = summary[f"{group}/single"]["median_t"]
        ratio = (lk / ul) if (lk and ul) else None
        print(f"{group}: linked {lk} vs unlinked {ul}  ratio {round(ratio,3) if ratio else 'n/a'}"
              f"   | single {sg}  (pair/single: "
              f"{round(lk/sg,2) if lk and sg else 'n'}/{round(ul/sg,2) if ul and sg else 'n'})")

    results["summary"] = summary
    out = ROOT / "reference" / "local_qwen" / "data" / "e071_link_lifetime.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
