"""Milestone 1 -- finite tetrahedral seed.

Implements ``A_4``, the tetrahedron, gauge fixing, holonomy and enumeration, and
reproduces the benchmark: **1728 raw gauge-fixed configurations reducing to 178
gauge-inequivalent classes**.

Run: ``PYTHONPATH=src python examples/milestone1.py``
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from constraintnet.gauge import (  # noqa: E402
    burnside_prediction,
    canonical_config,
    enumerate_gauge_fixed_configs,
    tetrahedron_moduli,
)
from constraintnet.groups import AlternatingGroup4, CyclicGroup  # noqa: E402
from constraintnet.holonomy import triangle_holonomy  # noqa: E402
from constraintnet.seeds import (  # noqa: E402
    TETRA_FREE_EDGES,
    TETRA_TREE,
    make_tetrahedron_boundary,
)


def rule(title: str) -> None:
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)


def main() -> int:
    a4 = AlternatingGroup4()

    rule("1. The group A4")
    print(f"   elements            : {a4.order()}")
    classes = a4.conjugacy_classes()
    for index, cls in enumerate(classes):
        representative = sorted(cls, key=repr)[0]
        print(
            f"   class {index}             : size {len(cls)}  "
            f"{a4.class_name(representative):38s} rep={a4.format(representative)}"
        )
    print(f"   generators          : {[a4.format(g) for g in a4.generators()]}")
    print(f"   word-metric diameter: {max(a4.word_lengths().values())} (cost units for relabelling)")

    rule("2. The seed  d(Delta^3)")
    cx = make_tetrahedron_boundary("A4")
    print(f"   {cx.summary()}")
    print(f"   chi = {cx.euler_characteristic()}  (a 2-sphere: 4 vertices, 6 edges, 4 faces)")

    rule("3. Gauge fixing a spanning tree")
    print(f"   fixed to identity   : {list(TETRA_TREE)}")
    print(f"   independent labels  : {list(TETRA_FREE_EDGES)}")
    for edge in TETRA_FREE_EDGES:
        print(f"     A_{edge[0]}{edge[1]} = {cx.label(*edge)!r} (before randomising)")

    rule("4. Enumeration")
    configs = enumerate_gauge_fixed_configs(a4, TETRA_FREE_EDGES)
    print(f"   raw gauge-fixed configurations : {len(configs)}  (= 12^3)")
    result = tetrahedron_moduli(a4)
    print(f"   gauge-inequivalent classes     : {result['class_count']}")
    print(f"   Burnside prediction            : {result['burnside']:.1f}")

    sizes: dict = {}
    for orbit in result["orbits"]:
        sizes[len(orbit)] = sizes.get(len(orbit), 0) + 1
    print("   orbit-size histogram           : " + ", ".join(
        f"{size} elements x {count} classes" for size, count in sorted(sizes.items(), reverse=True)
    ))

    rule("5. Cross-checks")
    assert len(configs) == 1728, "raw count must be 12^3 = 1728"
    assert result["class_count"] == 178, "expected the known benchmark of 178 classes"
    assert abs(result["burnside"] - 178.0) < 1e-9, "Burnside must agree with brute force"
    total = sum(len(orbit) for orbit in result["orbits"])
    assert total == 1728, "orbits must partition the raw configurations"

    # gauge invariance of curvature on a single random configuration
    from constraintnet.gauge import gauge_transform
    import random

    rng = random.Random(0)
    for edge in TETRA_FREE_EDGES:
        cx.set_label(*edge, rng.choice(a4.elements))
    before = {f: triangle_holonomy(cx, f) for f in cx.faces()}
    gauge_transform(cx, {v: rng.choice(a4.elements) for v in cx.vertices()})
    after = {f: triangle_holonomy(cx, f) for f in cx.faces()}
    same = all(a4.class_of(before[f]) == a4.class_of(after[f]) for f in cx.faces())
    print(f"   face-holonomy classes invariant under gauge transform : {same}")
    assert same

    # abelian control: conjugation is trivial, so no quotienting happens
    z3 = CyclicGroup(3)
    z3_result = tetrahedron_moduli(z3)
    print(f"   Z3 control (abelian)            : {z3_result['raw_count']} raw -> "
          f"{z3_result['class_count']} classes")

    print()
    print("MILESTONE 1 COMPLETE: 1728 raw gauge-fixed configurations, "
          f"{result['class_count']} gauge-inequivalent classes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
