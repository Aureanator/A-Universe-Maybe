"""E030 -- core entropy: hidden internal states of a flux-string CORE, measured exactly.

E027 found that the field around a closed flux loop is RIGID (|I| = 1): loop fields carry
no hidden entropy. The sharpened question: does hidden-resolution entropy live in the
CORE -- a fully interior vertex capping curvature from inside (the cone apex generalized
to a real ball)?

This script answers it on Kuhn n=2 with A4, where the central vertex 13 is the only full
core (14 interior edges; brute force would need 12^14 ~ 1e15 trials -- the gauge-slice
CSP solver does it in ~0.1 s):

    core star(13), order-3 seed:   raw |Sol| = 48, physical |I| = 4, S = log 4
    field-only balls r=1,2:        |I| = 1     (rigid; E027 reproduced)
    full ball (E_int = 26):        |I| = 4     (entropy LOCALIZES at the core)
    involution seed control:       raw = 12,   |I| = 1  (flat star = pure gauge)
    Z3 twin of the core:           |I| = 1     (hidden state requires non-abelian-ness)

State structure: all four states share one support (7 active edges -- a polarization fixed
by the link geometry) and differ only in WHICH order-3 element fills it; those four
elements form exactly one conjugacy class. The core's hidden state space is its flux class.

Run: ``PYTHONPATH=src python examples/core_entropy.py``
"""

from __future__ import annotations

import math
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from constraintnet.entropy import (  # noqa: E402
    interior_vertices, metric_ball_tets, region_resolution_space,
)
from constraintnet.region import region_from_tets  # noqa: E402
from constraintnet.seeds import kuhn_ball  # noqa: E402
from constraintnet.strings import _hol, flux_string_components  # noqa: E402


def rule(title: str) -> None:
    print()
    print("=" * 74)
    print(title)
    print("=" * 74)


def seed_star(cx, v_star, order):
    group = cx.group
    c = sorted([x for x in group.elements if group.order_of(x) == order], key=repr)[0]
    for e in sorted(cx.edges()):
        cx.set_label(e[0], e[1], c if v_star in e else group.identity())
    return {tuple(sorted(f)): group.class_of(_hol(cx, f)) for f in cx.faces()}


def star_region(cx, v):
    return region_from_tets(cx, [t for t in cx.tetrahedra() if v in t], name=f"star{v}")


def declared_space(cx, reg, decl):
    fc = {f: decl.get(f, frozenset({cx.group.identity()}))
          for f in map(tuple, map(sorted, reg.interior_faces()))}
    return region_resolution_space(cx, reg, fc, method="slice")


def main() -> int:
    rule("CORE ENTROPY -- Kuhn n=2, A4, order-3 star seed at central vertex 13")
    cx = kuhn_ball("A4", n=2)
    decl = seed_star(cx, 13, 3)
    comps = flux_string_components(cx)
    print(f"seeded curvature: {[(c.kind, c.length) for c in comps]} (closed loop expected)")
    print(f"core check: interior_vertices(star(13)) == {interior_vertices(cx, star_region(cx, 13))}")

    t0 = time.time()
    core = declared_space(cx, star_region(cx, 13), decl)
    dt = time.time() - t0
    print(f"\ncore star(13):   raw |Sol| = {core.count_raw:4d}   physical |I| = {core.count_physical}"
          f"   S = {core.entropy:.4f}   [{dt:.2f}s; brute force would need 12^{core.n_interior_edges}]")

    curved = sorted(decl)
    center = next(t for t in cx.tetrahedra() if set(curved[0]) <= set(t))
    for r in (1, 2):
        reg = region_from_tets(cx, metric_ball_tets(cx, center, r), name=f"field_r{r}")
        space = declared_space(cx, reg, decl)
        tag = "core included!" if 13 in interior_vertices(cx, reg) else "field only"
        print(f"field ball r={r}: raw |Sol| = {space.count_raw:4d}   physical |I| = {space.count_physical}"
          f"   ({tag})")

    full = region_from_tets(cx, list(cx.tetrahedra()), name="full")
    space = declared_space(cx, full, decl)
    print(f"full ball:     raw |Sol| = {space.count_raw:4d}   physical |I| = {space.count_physical}"
          f"   (E_int = {space.n_interior_edges}: entropy localizes at the core)")

    rule("CONTROLS")
    cx2 = kuhn_ball("A4", n=2)
    seed_star(cx2, 13, 2)
    print(f"involution seed: curved components = {flux_string_components(cx2)} (flat, E026)")
    space2 = declared_space(cx2, star_region(cx2, 13), {})
    print(f"                 raw |Sol| = {space2.count_raw} (= |G|: flat star connections are pure gauge)"
          f"   physical |I| = {space2.count_physical}")

    cx3 = kuhn_ball("Z3", n=2)
    decl3 = seed_star(cx3, 13, 3)
    space3 = declared_space(cx3, star_region(cx3, 13), decl3)
    print(f"Z3 twin core:    raw |Sol| = {space3.count_raw}   physical |I| = {space3.count_physical}"
          f"   (abelian cores carry no hidden state)")

    rule("VERDICT")
    ok = (core.count_physical == 4 and space.count_physical == 4 and space2.count_physical == 1
          and space3.count_physical == 1)
    print("E027 prediction CONFIRMED" if ok else "UNEXPECTED -- check measurements")
    print("Hidden-resolution entropy lives in the defect core, not its field;")
    print("|I(core)| = 4 = |flux class|: the knot's hidden degrees of freedom are the")
    print("possible orientations of its own charge (for this seed geometry).")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
