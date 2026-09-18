"""P2 — does the spanning-tree basis of probe_cycles change any accept/reject verdict?

Referee item 2 claims root choice flips ~12.4% of surface-move verdicts.  We measure, on a
Kuhn n=2 ball with random A4 labels: for every single-edge generator move, the verdict under
the FULL appearance predicate (face classes + cycle classes) computed at each possible tree
root, plus the face-only verdict, so any disagreement can be attributed to one mechanism.

Pre-registered docs/PREDICTIONS.md P2: prediction is ZERO flips (face curvatures are basis-
independent actual triangle holonomies; every edge move that changes a boundary face class is
caught identically in every basis).
"""

from __future__ import annotations

import itertools
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "src"))

from constraintnet.complex import fundamental_cycles  # noqa: E402
from constraintnet.holonomy import loop_holonomy, triangle_holonomy  # noqa: E402
from constraintnet.moves import Move, apply_move, revert_move  # noqa: E402
from constraintnet.region import Region  # noqa: E402
from constraintnet.seeds import kuhn_ball, randomize_labels  # noqa: E402


def face_part(cx, region):
    g = cx.group
    return frozenset(
        (f, g.class_of(triangle_holonomy(cx, f))) for f in region.observed_faces()
    )


def cycle_part(cx, surface_edges, root):
    g = cx.group
    cycles = fundamental_cycles(surface_edges, root=root)
    return frozenset(
        (tuple(loop), g.class_of(loop_holonomy(cx, loop))) for loop in cycles
    )


def main():
    cx = kuhn_ball("A4", n=2)
    randomize_labels(cx, seed=3)
    region = Region(cx, cx.tetrahedra(), "universe")
    surface = region.surface_edges()
    roots = sorted({v for e in surface for v in e})

    gens = list(cx.group.move_generators())
    edges = [e for e in cx.edges()]

    flips_full = 0
    flips_face_only = 0
    cycle_only_flips = 0
    total = 0
    example_flip = None

    for (u, v) in edges:
        for g in gens:
            new = cx.group.multiply(cx.label(u, v), g)
            if new == cx.label(u, v):
                continue
            move = Move(kind="edge", edge=(u, v), old_label=cx.label(u, v), new_label=new)

            faces_before = face_part(cx, region)
            verdicts_full = {}
            verdicts_cycle = {}
            for r in roots:
                cb = cycle_part(cx, surface, r)
                apply_move(cx, move)
                fa = face_part(cx, region)
                ca = cycle_part(cx, surface, r)
                revert_move(cx, move)
                verdicts_full[r] = (faces_before == fa) and (cb == ca)
                verdicts_cycle[r] = (cb == ca)

            verdict_face_only = faces_before == face_part_after(cx, move, region)
            total += 1
            vals = set(verdicts_full.values())
            if len(vals) > 1:
                flips_full += 1
                if example_flip is None:
                    example_flip = ((u, v), g, {r: verdicts_full[r] for r in roots})
            # attribute: does the face-only verdict differ from any full verdict?
            if any(v != verdict_face_only for v in verdicts_full.values()):
                cycle_only_flips += 1

    print(f"moves tested: {total}")
    print(f"verdict flips across tree roots (full appearance predicate): {flips_full}")
    print(f"moves where cycle-part participation changes the face-only verdict: {cycle_only_flips}"
          f"  ({100.0 * cycle_only_flips / max(1, total):.1f}%)")
    if example_flip:
        print("example flip:", example_flip)


def face_part_after(cx, move, region):
    apply_move(cx, move)
    fp = face_part(cx, region)
    revert_move(cx, move)
    return fp


if __name__ == "__main__":
    main()
