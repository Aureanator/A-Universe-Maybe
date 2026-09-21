"""Free-space tracking study (E066): does a seeded defect persist and wander when the
TRACK ITSELF is dynamical, and can a combinatorial boundary keep sight of it?

Run: python examples/free_space_tracking.py
Writes reference/local_qwen/data/free_space_tracking.json.

DriverC (v1) adds Pachner 2<->3 relinkings to the relational move set: entailment can
now lay the adjacency it travels on, while the boundary sphere stays frozen (tests in
tests/test_driverC.py pin acceptance structure, topology, and no-teleportation locally).

This example is an EXPLORATORY measurement with analytic priors stated up front:

P1  PERSISTENCE. Under whole-complex relational acceptance nothing constrains bulk
    curvature except the frozen boundary: pair creation/annihilation is legal anywhere
    (E065 mechanism), so the prior is that a localized seed DISSOLVES into vacuum churn
    on a short timescale -- dynamical, not topological, persistence. If lifetimes are
    long instead, something protective was missed; report either way.
P2  WANDER. Relinking relocates curvature WITHOUT label changes (surviving faces keep
    holonomy; the face set itself moves), so a cluster can drift through the mesh via a
    channel that pure-label dynamics (DriverA control) does not have. Prior: DriverC
    support trajectories decorrelate from the seed faster than DriverA's, and some
    relocation steps are attributable to relinkings specifically.
P3  TRACKING BOUNDARY. Object identity is followed by combinatorial overlap lineage of
    curved-face sets (vertex tuples -- face indices do not survive relinking), recentered
    implicitly at every step: the tracker follows wherever the object goes, off any
    fixed frame. Report how often the tracked support leaves the initial neighborhood
    and whether lineage ever breaks ambiguously (two candidate successors of comparable
    overlap -> logged as ambiguity, resolved by max overlap, counted).

Controls: DriverA(relational) at matched seeds/steps; boundary sphere labels asserted
constant every step in both arms (conservation is measured, not assumed).
"""

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.drivers import DriverA, DriverC
from constraintnet.holonomy import triangle_holonomy
from constraintnet.region import Region
from constraintnet.seeds import kuhn_ball

GROUP = "A4"
N = 3
STEPS = 300
SEEDS = (0, 1, 2)


# ---------------------------------------------------------------- helpers
def curved(cx):
    ident = cx.group.identity()
    return {tuple(sorted(f)) for f in cx.faces() if triangle_holonomy(cx, f) != ident}


def components(curved_set, cx):
    """Curved-face clusters; adjacency = co-contained in a current tetrahedron."""
    face_tets = {}
    for t in (tuple(sorted(x)) for x in cx.tetrahedra()):
        for face in itertools.combinations(t, 3):
            face_tets.setdefault(face, []).append(t)
    unseen = set(curved_set)
    out = []
    while unseen:
        start = min(unseen)
        comp, queue = {start}, [start]
        unseen.discard(start)
        for f in queue:
            for t in face_tets.get(f, ()):
                for g in itertools.combinations(t, 3):
                    if g in unseen and g in curved_set:
                        unseen.discard(g)
                        comp.add(g)
                        queue.append(g)
        out.append({"faces": frozenset(comp),
                    "tets": frozenset(t for f in comp for t in face_tets.get(f, ()))})
    return out


def seed_defect(cx):
    """Deterministic localized seed on the tet nearest combinatorial center.

    Multiply every edge of that tet by a fixed order-3 element; if the result is flat
    (products can cancel), keep multiplying one more edge until curvature appears.
    Returns (seed_tets, initial_curved_faces).
    """
    tets = sorted(tuple(sorted(t)) for t in cx.tetrahedra())
    center = tets[len(tets) // 2]
    order3 = next(x for x in cx.group.elements if cx.group.order_of(x) == 3)
    edges = list(itertools.combinations(center, 2))
    for k in range(1, len(edges) + 2):
        for (u, v) in edges[:k]:
            cx.set_label(u, v, cx.group.multiply(cx.label(u, v), order3))
        if curved(cx):
            break
    return center, curved(cx)


def surface_labels(cx):
    region = Region(cx, cx.tetrahedra(), "whole")
    return frozenset((tuple(sorted(e)), cx.label(*e))
                     for e in region.boundary_surface_edges())


# ---------------------------------------------------------------- tracking run
def run_tracked(driver_kind, seed):
    cx = kuhn_ball(GROUP, n=N)
    seed_tet, initial_curved = seed_defect(cx)
    assert initial_curved, "seed produced no curvature"
    driver = (DriverC(cx, rng_seed=seed, pachner_share=0.5) if driver_kind == "C"
              else DriverA(cx, rng_seed=seed, model="relational"))
    surf0 = surface_labels(cx)

    seed_components = components(initial_curved, cx)
    tracked = max(seed_components, key=lambda c: len(c["faces"]))["faces"]
    initial_tets = frozenset(t for f in tracked for t in
                             [tuple(sorted(t)) for t in cx.tetrahedra()
                              if set(f) <= set(t)])

    lifetime = STEPS
    alive = True
    ambiguities = 0
    relocations_by_kind = Counter()   # support-changing accepted steps, by move kind
    displaced_history = []            # fraction of occupied tets OUTSIDE initial tet set
    support_history = []              # tracked cluster face-count over time (accretion test)
    energy_history = []
    tet_count_history = []

    for step in range(1, STEPS + 1):
        record = driver.advance()
        assert surface_labels(cx) == surf0, f"boundary moved ({driver_kind} seed {seed})"
        cur_all = curved(cx)
        energy_history.append(len(cur_all))     # count of curved faces
        tet_count_history.append(cx.n_tetrahedra())

        if alive and record.fate == "accepted":
            comps = components(cur_all, cx)
            candidates = sorted(
                ((len(tracked & c["faces"]), c) for c in comps if tracked & c["faces"]),
                key=lambda x: -x[0])
            if not candidates:
                lifetime = step
                alive = False
            else:
                best_overlap, best = candidates[0]
                if len(candidates) > 1 and candidates[1][0] >= max(2, best_overlap // 2):
                    ambiguities += 1     # split-like event: comparable rival successors
                new_faces = best["faces"]
                if new_faces != tracked:
                    kind = getattr(driver, "last_kind", None) or ("label"
                                                                  if driver_kind == "A" else "?")
                    relocations_by_kind[kind] += 1
                tracked = new_faces

        if alive and tracked:
            support_history.append(len(tracked))
            occ = frozenset(t for f in tracked for t in
                            [tuple(sorted(x)) for x in cx.tetrahedra() if set(f) <= set(x)])
            outside = len(occ - initial_tets)
            displaced_history.append(outside / max(1, len(occ)))

    # summary metrics
    first_displacement_step = next((i + 1 for i, d in enumerate(displaced_history)
                                    if d > 0), None)
    return {
        "driver": driver_kind, "seed": seed,
        "lifetime_step": lifetime if not alive else STEPS,
        "survived_full_run": alive,
        "support_changes_by_move_kind": dict(relocations_by_kind),
        "lineage_ambiguities": ambiguities,
        "first_displacement_step": first_displacement_step,
        "max_displaced_fraction": max(displaced_history) if displaced_history else 0.0,
        "final_energy_curved_faces": energy_history[-1] if energy_history else None,
        "tracked_support_final": support_history[-1] if support_history else 0,
        "tracked_over_global_final": round(
            (support_history[-1] / energy_history[-1])
            if support_history and energy_history and energy_history[-1] else 0.0, 3),
        "energy_start": len(initial_curved),
        "tet_count_start": tet_count_history[0] if tet_count_history else None,
        "tet_count_end": tet_count_history[-1] if tet_count_history else None,
        "energy_trajectory": energy_history,
        "support_trajectory": support_history,
    }


def main():
    results = {"C": [], "A": []}
    for kind in ("C", "A"):
        for seed in SEEDS:
            r = run_tracked(kind, seed)
            results[kind].append(r)
            print(f"driver {kind} seed {seed}: survived={r['survived_full_run']} "
                  f"lifetime={r['lifetime_step']} reloc by kind={r['support_changes_by_move_kind']} "
                  f"ambig={r['lineage_ambiguities']} first displacement step={r['first_displacement_step']} "
                  f"max displaced frac={r['max_displaced_fraction']:.2f} "
                  f"tets {r['tet_count_start']}->{r['tet_count_end']} | "
                  f"energy {r['energy_start']}->{r['final_energy_curved_faces']} "
                  f"tracked final={r['tracked_support_final']} "
                  f"(fraction of global {r['tracked_over_global_final']})")

    def summarize(arm):
        rows = results[arm]
        return {
            "survival_rate": sum(r["survived_full_run"] for r in rows) / len(rows),
            "median_lifetime": sorted(r["lifetime_step"] for r in rows)[len(rows) // 2],
            "runs_with_displacement": sum(r["first_displacement_step"] is not None
                                          for r in rows),
            "total_relocations_by_kind": dict(Counter(dict(
                (k, v) for r in rows for k, v in r["support_changes_by_move_kind"].items()))),
        }

    verdict = {"C": summarize("C"), "A": summarize("A")}
    print("\nSUMMARY:", json.dumps(verdict, indent=2))

    payload = {
        "provenance": {
            "script": "examples/free_space_tracking.py",
            "model": "local Qwen (LM Studio), E066 free-space tracking study",
            "nature": ("exploratory; priors P1-P3 stated in module docstring BEFORE running; "
                       "boundary conservation asserted every step both arms"),
        },
        "config": {"group": GROUP, "n": N, "steps": STEPS, "seeds": list(SEEDS),
                   "driverC_pachner_share": 0.5},
        "runs": results,
        "summary": verdict,
    }
    out = (Path(__file__).resolve().parents[1]
           / "reference" / "local_qwen" / "data" / "free_space_tracking.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
