"""Universality matrix: is the tetrahedron-seed landscape story A4-specific?

Run: python examples/universality_matrix.py
Writes reference/local_qwen/data/universality_matrix.json.

Motivation.  CLAIMS row 26 (MEASURED, local Qwen, P8) states that on the
tetrahedron seed with G = A4 (and Z3), vacuum is the only closed equal-action
basin of the curvature action H under exact edge-multiplier dynamics.  That is
an existence-of-matter-relevant fact about ONE group slice unless tested
across groups.  This probe runs two things for each small group:

1. Orbit enumeration of G^3 (the gauge-fixed tree-slice triples) under the
   residual GLOBAL conjugation a_i -> lam^-1 a_i lam, with an independent
   Burnside cross-check:
       #orbits = (1/|G|) * sum_g |C_G(g)|^3 .
   Analytic predictions computed by hand BEFORE running code:
       A4 -> 178 (pinned precedent, tests/test_backlog_claims.py),
       S3 -> 49, Q8 -> 176, D4 -> 176; abelian groups -> |G|^3 (conjugation
       trivial).  Disagreement means the code or the arithmetic is wrong.
   Also reports the little-group census: stabilizer = intersection of the
   coordinate centralizers, classified by (order, cyclicity).  A4 must give
   130 trivial / 26 Z3 / 21 V4 / 1 A4.

2. The exact curvature-action landscape (constraintnet.landscape) on the
   tetrahedron boundary for each group.  Key universality question: is
   "zero closed nonvacuum plateaus" universal across these groups, or does
   some group admit a trapped equal-action basin?  This is an EXPLORATORY
   search (not a pre-registered prediction); the Burnside numbers above are
   mathematical cross-checks of the orbit code, not physics predictions.

No coordinates, no particles, no inserted dynamics: labels carry group
constraints, moves multiply edge labels by nonidentity elements, gauge fixing
and orbit projection are bookkeeping.
"""

import itertools
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.drivers import conjugate_triple
from constraintnet.groups import get_group
from constraintnet.landscape import enumerate_landscape
from constraintnet.seeds import make_tetrahedron_boundary

GROUP_NAMES = ("Z2", "Z3", "S3", "D4", "Q8", "A4")

# Hand-computed Burnside predictions (see module docstring): analytic values of
# (1/|G|) sum_g |C_G(g)|^3, recorded before the code was run.
BURNSIDE_PREDICTIONS = {"Z2": 8, "Z3": 27, "S3": 49, "D4": 176, "Q8": 176, "A4": 178}

# Pinned A4 little-group census (tests/test_backlog_claims.py).
A4_CENSUS_PREDICTION = {"trivial(order 1)": 130, "cyclic(order 3)": 26,
                        "noncyclic(order 4)": 21, "whole group(order 12)": 1}


def orbits_under_global_conjugation(group):
    """Brute-force orbit decomposition of G^3 under diagonal conjugation.

    Returns (orbit_reps, census) where each orbit carries its stabilizer type.
    Only used for |G| <= 12, so |G|^3 <= 1728: exhaustive is cheap and exact.
    """
    triples = list(itertools.product(group.elements, repeat=3))
    orbits: dict = {}
    for t in triples:
        rep = min(conjugate_triple(group, t, lam) for lam in group.elements)
        orbits.setdefault(rep, []).append(t)

    def stabilizer_type(rep):
        # lambda fixes all three coordinates under conjugation iff it lies in
        # the intersection of their centralizers (centralizer of <a,b,c>).
        stab = [lam for lam in group.elements
                if conjugate_triple(group, rep, lam) == tuple(rep)]
        order = len(stab)
        if order == 1:
            return "trivial(order 1)"
        if order == group.order():
            return f"whole group(order {order})"
        cyclic = any(group.order_of(x) == order for x in stab)
        return f"cyclic(order {order})" if cyclic else f"noncyclic(order {order})"

    census = Counter(stabilizer_type(rep) for rep in orbits)
    return orbits, dict(sorted(census.items()))


def burnside_orbits(group):
    """(1/|G|) * sum_g |C_G(g)|^3 -- independent count of G^3 conjugation orbits."""
    total = sum(len(group.centralizer(g)) ** 3 for g in group.elements)
    num, rem = divmod(total, group.order())
    assert rem == 0, "Burnside sum must be divisible by |G|"
    return num


def classify_group_landscape(name):
    group = get_group(name)
    orbits, census = orbits_under_global_conjugation(group)
    burnside = burnside_orbits(group)
    expected = BURNSIDE_PREDICTIONS[name]
    if burnside != expected or len(orbits) != expected:
        raise AssertionError(
            f"{name}: brute {len(orbits)} / Burnside {burnside} vs predicted {expected}")

    land = enumerate_landscape(make_tetrahedron_boundary(name))
    summary = land.summary()

    record = {
        "order": group.order(),
        "abelian": bool(group.is_abelian()),
        "conjugacy_classes": sorted(len(c) for c in group.conjugacy_classes()),
        "orbits_G3_bruteforce": len(orbits),
        "orbits_G3_burnside": burnside,
        "burnside_prediction_handcomputed": expected,
        "little_group_census": census,
        "landscape": summary,
    }
    if name == "A4":
        if census != A4_CENSUS_PREDICTION:
            raise AssertionError(f"A4 census {census} != pinned {A4_CENSUS_PREDICTION}")
        record["little_group_census_matches_pinned_A4"] = True
    return record


def main():
    out_path = (Path(__file__).resolve().parents[1]
                / "reference" / "local_qwen" / "data" / "universality_matrix.json")
    results = {}
    print(f"{'G':>4} {'|G|':>4} ab  classes | orbits G^3 (brute=burnside) | "
          "phys states | closed nonvac plateaus")
    for name in GROUP_NAMES:
        rec = classify_group_landscape(name)
        results[name] = rec
        ls = rec["landscape"]
        print(f"{name:>4} {rec['order']:>4} {str(rec['abelian']):>3} "
              f"{str(rec['conjugacy_classes']):>8} | "
              f"{rec['orbits_G3_bruteforce']:>6} = {rec['orbits_G3_burnside']:<6} | "
              f"{ls['physical_states']:>9} | {ls['nonvacuum_closed_plateaus']}")

    closed_groups = [n for n, r in results.items()
                     if r["landscape"]["nonvacuum_closed_plateaus"] > 0]
    verdict = {
        "closed_nonvacuum_basin_found_for": closed_groups,
        "universality_within_tested_groups": (
            "vacuum is the only closed equal-action basin for every tested group"
            if not closed_groups else
            "NOT universal: at least one tested group has a closed nonvacuum basin"),
    }
    print("\nVERDICT:", verdict["universality_within_tested_groups"])

    payload = {
        "provenance": {
            "script": "examples/universality_matrix.py",
            "model": "local Qwen (LM Studio), universality matrix session",
            "nature": ("exploratory cross-group search; Burnside values are analytic "
                       "cross-checks computed by hand before running code"),
            "related_claims": ["CLAIMS row 26 (P8): A4/Z3 zero closed nonvacuum basins"],
        },
        "groups": results,
        "verdict": verdict,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
