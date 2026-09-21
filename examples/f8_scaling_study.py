"""F8 scaling study (referee R3 remainder): do kernel invariants survive at scale?

Run: python examples/f8_scaling_study.py
Writes reference/local_qwen/data/f8_scaling.json.

The Round-3 referee complaint behind F8 was coverage: green tests on small fixtures.
E064 landed the property suite (tests/test_properties.py) but only at kuhn_ball n=2 /
bipyramid scale and 60 steps.  This study pushes the SAME invariants along three axes:

1. MESH SIZE: kuhn balls n=2 vs n=3 for every registered group {Z2,Z3,S3,D4,Q8,A4};
   vertex gauge invariance, DriverA(relational) conservation recomputed from the
   complex every step (gauge_invariant_state + boundary-surface face classes), and
   Pachner 2-3 apply+revert exact snapshots -- all at n=3.
2. RUN LENGTH: 500 driver steps per cell (vs 60 in the suite).
3. QUOTIENT DEPTH: kernel orbit quotient == Burnside for k = 1..4 free edges
   (|G|^k up to 20736 configs for A4), not just the tetrahedron's k=3.

MECHANISM FINDING (a refuted prior, recorded honestly).  The first draft of this
script predicted accept rates should DROP with mesh size (more observed loops ->
tighter conservation).  Measurement says the opposite: rate RISES n=2 (~0.25) to
n=3 (~0.44), and a label-diff mechanism probe (study_acceptance_mechanism) shows
why exactly: for a WHOLE-COMPLEX region, DriverA(relational) accepts ONLY proposals
on purely-interior edges -- zero surface-edge acceptances across every group and
mesh tested -- and interior proposals appear to be accepted essentially always.
The acceptance rate is therefore the closed-form interior-edge fraction:
(E_total - E_surface)/E_total with E_surface from Euler on the boundary sphere
(0.265 at n=2, 0.419 at n=3), which grows toward ~1 as volume/surface with mesh
size.  The whole-complex relational driver is exactly "bulk churns freely,
boundary frozen" -- the same asymmetry E064-P2 found from the other direction.
The prior was wrong because boundary observability does not grow with bulk size:
the observed surface stays the sphere while invisible interior edges proliferate.

Conservation verdicts are hard assertions (script fails loudly); rates and times are
measurements written to JSON.  RNG lives here, never in KERNEL.
"""

import json
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.drivers import DriverA
from constraintnet.gauge import (
    burnside_prediction,
    enumerate_gauge_fixed_configs,
    gauge_transform,
    quotient_by_global_conjugation,
)
from constraintnet.groups import get_group
from constraintnet.holonomy import triangle_holonomy
from constraintnet.moves import apply_pachner_2_3, find_pachner_2_3_sites, revert_move
from constraintnet.region import Region
from constraintnet.seeds import kuhn_ball, randomize_labels

GROUPS = ("Z2", "Z3", "S3", "D4", "Q8", "A4")
STEPS = 500
SEEDS = (0, 1)


def snapshot(cx):
    return (
        frozenset(tuple(sorted(t)) for t in cx.tetrahedra()),
        tuple((tuple(sorted(e)), cx.label(*e)) for e in sorted(cx.edges())),
        frozenset(tuple(sorted(f)) for f in cx.faces()),
    )


def boundary_class_multiset(cx, region):
    group = cx.group
    return sorted(
        tuple(sorted(group.conjugacy_class(triangle_holonomy(cx, f))))
        for f in region.boundary_faces()
    )


def study_gauge_invariance_at_scale():
    """Vertex gauge preserves observables exactly at n=3; raw labels must move."""
    out = {}
    for name in GROUPS:
        cx = kuhn_ball(name, n=3)
        randomize_labels(cx, seed=31)
        region = Region(cx, cx.tetrahedra(), "whole")
        state0 = region.gauge_invariant_state()
        classes0 = boundary_class_multiset(cx, region)
        labels_before = {e: cx.label(*e) for e in cx.edges()}
        rng = random.Random(99)
        gauge_transform(cx, {v: cx.group.elements[rng.randrange(cx.group.order())]
                             for v in cx.vertices()})
        assert region.gauge_invariant_state() == state0, f"{name}: n=3 gauge broke state"
        assert boundary_class_multiset(cx, region) == classes0, f"{name}: n=3 class drift"
        moved = any(cx.label(*e) != labels_before[e] for e in cx.edges())
        if not cx.group.is_abelian():
            assert moved, f"{name}: gauge transform did nothing (vacuous test)"
        out[name] = {"preserved": True, "raw_labels_moved": bool(moved)}
    return out


def study_driver_conservation_at_scale():
    """DriverA(relational): state + boundary classes conserved over STEPS steps at n=2/n=3.

    Diagnostics: fate counts and wall time per step (observe cost dominates and grows
    with the complex -- recorded, not asserted).
    """
    out = {}
    for name in GROUPS:
        rows = []
        for n in (2, 3):
            accepted = vetoed = 0
            t_total = 0.0
            for seed in SEEDS:
                cx = kuhn_ball(name, n=n)
                randomize_labels(cx, seed=seed)
                region = Region(cx, cx.tetrahedra(), "whole")
                driver = DriverA(cx, region=region, rng_seed=seed, model="relational")
                state0 = region.gauge_invariant_state()
                classes0 = boundary_class_multiset(cx, region)
                for _ in range(STEPS):
                    t0 = time.perf_counter()
                    record = driver.advance()
                    t_total += time.perf_counter() - t0
                    if record.fate == "accepted":
                        accepted += 1
                    else:
                        vetoed += 1
                    assert region.gauge_invariant_state() == state0, (
                        f"{name} n={n} seed={seed}: state changed at step count "
                        f"accepted={accepted}")
                    assert boundary_class_multiset(cx, region) == classes0, (
                        f"{name} n={n} seed={seed}: boundary class drift")
            total = accepted + vetoed
            rows.append({
                "n": n, "edges": len(cx.edges()), "tets": cx.n_tetrahedra(),
                "steps_per_seed": STEPS, "seeds": list(SEEDS),
                "accepted": accepted, "vetoed": vetoed,
                "accept_rate": round(accepted / total, 4),
                "ms_per_step": round(1000 * t_total / total, 3),
            })
        rows_out = {
            "per_mesh": rows,
            # first-draft prior was "rate drops with size"; measurement refutes it -- see
            # study_acceptance_mechanism (interior-edge fraction grows with n).
            "accept_rate_rises_n2_to_n3": bool(rows[1]["accept_rate"] > rows[0]["accept_rate"]),
        }
        out[name] = rows_out
    return out


def study_acceptance_mechanism():
    """Classify every ACCEPTED move by surface-vs-interior edge via label diff (no parsing).

    Hard assertions: zero accepted moves on surface edges; accepted interior counts within
    4 sigma of Binomial(steps, interior_frac) -- i.e., acceptance == interior proposals.
    Vetoed moves revert and leave no trace, so proposal-side counts are analytic.
    """
    out = {}
    for name in GROUPS:
        per_n = []
        for n in (2, 3):
            acc_int = acc_surf = 0
            interior_fracs = []
            for seed in SEEDS:
                cx = kuhn_ball(name, n=n)
                randomize_labels(cx, seed=seed)
                region = Region(cx, cx.tetrahedra(), "whole")
                surf = set()
                for f in region.boundary_faces():
                    for pair in [(f[0], f[1]), (f[1], f[2]), (f[2], f[0])]:
                        surf.add(tuple(sorted(pair)))
                edges = [tuple(sorted(e)) for e in cx.edges()]
                interior_fracs.append(sum(1 for e in edges if e not in surf) / len(edges))
                driver = DriverA(cx, region=region, rng_seed=seed, model="relational")
                for _ in range(STEPS):
                    before = {e: cx.label(*e) for e in edges}
                    record = driver.advance()
                    if record.fate == "accepted":
                        moved = [e for e in edges if cx.label(*e) != before[e]]
                        assert len(moved) == 1
                        if moved[0] in surf:
                            acc_surf += 1
                        else:
                            acc_int += 1
            frac = sum(interior_fracs) / len(interior_fracs)
            expected = STEPS * len(SEEDS) * frac
            sigma = (STEPS * len(SEEDS) * frac * (1 - frac)) ** 0.5
            assert acc_surf == 0, f"{name} n={n}: surface move accepted ({acc_surf})"
            z = (acc_int - expected) / sigma if sigma else 0.0
            assert abs(z) <= 4.0, (
                f"{name} n={n}: interior acceptances {acc_int} vs closed-form {expected:.1f} "
                f"(z={z:.2f}) -- interior moves are NOT all accepted; mechanism claim wrong")
            per_n.append({"n": n, "interior_edge_fraction": round(frac, 4),
                          "accepted_interior": acc_int, "accepted_surface": acc_surf,
                          "closed_form_expected": round(expected, 1), "z_score": round(z, 2)})
        out[name] = per_n
    return out


def study_pachner_at_scale():
    """Pachner 2-3 apply+revert exact snapshots at n=3 with randomized labels."""
    out = {}
    for name in GROUPS:
        cx = kuhn_ball(name, n=3)
        randomize_labels(cx, seed=41)
        rng = random.Random(5)
        checked = 0
        for _ in range(4):
            sites = find_pachner_2_3_sites(cx)
            assert sites, f"{name}: no 2-3 sites at n=3"
            (a, b, _face) = sites[rng.randrange(len(sites))]
            before = snapshot(cx)
            new_label = cx.group.elements[rng.randrange(cx.group.order())]
            move = apply_pachner_2_3(cx, a, b, new_edge_label=new_label)
            assert cx.n_tetrahedra() == len(before[0]) + 1
            revert_move(cx, move)
            assert snapshot(cx) == before, f"{name}: n=3 Pachner round-trip drift"
            checked += 1
        out[name] = {"round_trips_exact": checked}
    return out


def study_quotient_depth():
    """Kernel quotient == Burnside for k=1..4 free edges (beyond the tetrahedron's k=3)."""
    out = {}
    for name in GROUPS:
        group = get_group(name)
        per_k = {}
        for k in (1, 2, 3, 4):
            # enumerate_gauge_fixed_configs uses only len(free_edges): k slice coordinates
            configs = enumerate_gauge_fixed_configs(group, list(range(k)))
            orbits, _ = quotient_by_global_conjugation(configs, group)
            predicted = burnside_prediction(group, k)
            assert len(orbits) == int(predicted), (
                f"{name} k={k}: quotient {len(orbits)} != Burnside {predicted}")
            assert sum(len(o) for o in orbits) == group.order() ** k
            per_k[str(k)] = {"raw": group.order() ** k, "orbits": len(orbits),
                             "burnside": predicted}
        out[name] = per_k
    return out


def main():
    print("[1/5] gauge invariance at n=3 ...")
    gauge_part = study_gauge_invariance_at_scale()
    print("[2/5] DriverA(relational) conservation, 500 steps x 2 seeds, n=2 and n=3 ...")
    driver_part = study_driver_conservation_at_scale()
    for name, rows in driver_part.items():
        r2, r3 = rows["per_mesh"]
        print(f"      {name:>3}: accept rate n=2 {r2['accept_rate']:.3f} "
              f"({r2['edges']} edges) | n=3 {r3['accept_rate']:.3f} ({r3['edges']} edges) "
              f"| ms/step {r3['ms_per_step']}")
    print("[3/5] acceptance mechanism (label-diff classification) ...")
    mechanism_part = study_acceptance_mechanism()
    for name, rows in mechanism_part.items():
        r2, r3 = rows
        print(f"      {name:>3}: accepted interior/surface  n=2 {r2['accepted_interior']}/{r2['accepted_surface']} "
              f"(closed form {r2['closed_form_expected']}, z={r2['z_score']}) | "
              f"n=3 {r3['accepted_interior']}/{r3['accepted_surface']} (closed form {r3['closed_form_expected']}, z={r3['z_score']})")
    print("[4/5] Pachner round-trips at n=3 ...")
    pachner_part = study_pachner_at_scale()
    print("[5/5] quotient == Burnside, k=1..4 free edges ...")
    quotient_part = study_quotient_depth()

    payload = {
        "provenance": {
            "script": "examples/f8_scaling_study.py",
            "model": "local Qwen (LM Studio), F8 scaling study session",
            "nature": ("robustness/coverage study closing referee F8 remainder; conservation "
                       "verdicts are hard assertions, rates and times are diagnostics"),
            "mechanism_finding": (
                "whole-complex DriverA(relational) accepts only purely-interior-edge proposals "
                "(zero surface acceptances all groups/meshes); acceptance rate equals the "
                "closed-form interior-edge fraction, which RISES with mesh size -- refuting the "
                "first draft's drop-with-size prior"),
            "exact_landscape_tractability": (
                "proposals scale as |G|^free * edges * (|G|-1); exact landscapes stay on "
                "tetrahedron-sized seeds, scale coverage uses the stochastic driver"),
        },
        "gauge_invariance_n3": gauge_part,
        "driver_conservation": driver_part,
        "acceptance_mechanism": mechanism_part,
        "pachner_n3": pachner_part,
        "quotient_depth_k1_to_k4": quotient_part,
    }
    out_path = (Path(__file__).resolve().parents[1]
                / "reference" / "local_qwen" / "data" / "f8_scaling.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    print(f"\nALL ASSERTIONS HELD at scale. wrote {out_path}")


if __name__ == "__main__":
    main()
