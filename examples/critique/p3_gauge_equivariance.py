"""P3 — gauge equivariance of the proposal dynamics on the tetrahedron gauge slice.

Referee item 3: right-multiplication proposals by a generator set NOT closed under
conjugation give gauge-equivalent states different transition structure.  We measure, for
every tree-gauge triple t and every global conjugating element g:

* arm "current": generators = group.move_generators()          (not class-closed)
* arm "classes": generators = all non-identity elements         (class-closed)

transition structure = the set of ORBIT ids reachable in one proposal (orbit = global
conjugacy class of the resulting triple, per Qwen-cloud's canonicalize-for-reporting rule).
Equivariance holds iff reach(t^g) == map of reach(t) under conjugation, i.e. identical
reachable-orbit SETS.  Pre-registered docs/PREDICTIONS.md P3.
"""

from __future__ import annotations

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "src"))

from constraintnet.groups import AlternatingGroup4  # noqa: E402

G = AlternatingGroup4()
ELS = list(G.elements)


def mul(a, b):
    return G.multiply(a, b)


def inv(a):
    return G.inverse(a)


def conj(g, x):
    return G.multiply(G.multiply(inv(g), x), g)


def orbit(triple):
    return min(tuple(conj(g, x) for x in triple) for g in ELS)


def reachable(triple, gens):
    out = set()
    for pos in range(3):
        for h in gens:
            new = list(triple)
            new[pos] = mul(triple[pos], h)
            if tuple(new) != triple:
                out.add(orbit(tuple(new)))
    return out


def main():
    triples = list(itertools.product(ELS, repeat=3))
    arm_current_gens = list(G.move_generators())
    arm_classes_gens = [e for e in ELS if e != G.identity()]

    print(f"arm current generators: {len(arm_current_gens)} (class-closed? "
          f"{all(any(conj(g, h) == k for k in arm_current_gens) for g in ELS for h in arm_current_gens)})")
    print(f"arm classes generators: {len(arm_classes_gens)} (class-closed by construction)")

    for name, gens in [("current", arm_current_gens), ("classes", arm_classes_gens)]:
        violations = 0
        worst = (0, None)
        pairs_checked = 0
        example = None
        for t in triples:
            r_t = reachable(t, gens)
            for g in ELS:
                tc = tuple(conj(g, x) for x in t)
                if tc == t:
                    continue  # conjugation fixes this triple: equivariance trivial
                r_tc = reachable(tc, gens)
                pairs_checked += 1
                if len(r_t) != len(r_tc):
                    violations += 1
                    d = abs(len(r_t) - len(r_tc))
                    if d > worst[0]:
                        worst = (d, (t, g, len(r_t), len(r_tc)))
                        if example is None:
                            example = (t, g, sorted(map(str, r_t)), sorted(map(str, r_tc)))
        print(f"\narm={name}: gauge pairs checked {pairs_checked}, "
              f"reachable-orbit-COUNT mismatches: {violations} "
              f"({100.0 * violations / max(1, pairs_checked):.2f}%)")
        if worst[1]:
            t, g, a, b = worst[1]
            print(f"  worst mismatch |Δ|={worst[0]}: triple {tuple(G.format(x) for x in t)} "
                  f"conjugated by {G.format(g)}: {a} vs {b} reachable orbits")

    # stronger check for the class arm: exact SET equality (not just cardinality)
    set_violations = 0
    checked = 0
    for t in triples[:200]:
        r_t = reachable(t, arm_classes_gens)
        for g in ELS:
            tc = tuple(conj(g, x) for x in t)
            if tc == t:
                continue
            checked += 1
            if reachable(tc, arm_classes_gens) != r_t:
                set_violations += 1
    print(f"\narm=classes exact reachable-orbit-SET equality over {checked} pairs: "
          f"violations = {set_violations}")


if __name__ == "__main__":
    main()
