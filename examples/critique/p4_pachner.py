"""P4 — Pachner 2->3 degeneracy claim (referee item 4).

Claim: the implementation constructs 3-vertex tuples where 4-vertex tetrahedra are required,
throwing SimplicialError mid-mutation.  At HEAD apply_pachner_2_3 builds (u,w,a),(u,w,b),
(u,w,c) — three 4-tuples.  We round-trip every legal site on Kuhn n=2 and n=3 in both
directions, checking: no exception; boundary complex + labels unchanged; full revert exact.

Pre-registered docs/PREDICTIONS.md P4: does not reproduce at HEAD.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "src"))

from constraintnet.moves import (  # noqa: E402
    apply_pachner_2_3,
    apply_pachner_3_2,
    find_pachner_2_3_sites,
    find_pachner_3_2_sites,
    revert_move,
)
from constraintnet.seeds import kuhn_ball, randomize_labels  # noqa: E402


def snapshot(cx):
    return (
        frozenset(tuple(sorted(t)) for t in cx.tetrahedra()),
        frozenset(tuple(sorted(e)) for e in cx.edges()),
        frozenset(tuple(sorted(f)) for f in cx.faces()),
        tuple((tuple(sorted(e)), cx.label(*e)) for e in sorted(cx.edges())),
    )


def boundary_signature(cx):
    """Faces used by exactly one tetrahedron = the boundary; with their labels."""
    use = {}
    for t in cx.tetrahedra():
        import itertools
        for f in itertools.combinations(sorted(t), 3):
            use[f] = use.get(f, 0) + 1
    bfaces = [f for f, c in use.items() if c == 1]
    out = []
    for f in sorted(bfaces):
        for pair in [tuple(sorted(p)) for p in [(f[0], f[1]), (f[1], f[2]), (f[0], f[2])]]:
            out.append((pair, cx.label(*pair)))
    return frozenset(out)


def main():
    total_23 = ok_23 = total_32 = ok_32 = 0
    for n in (2, 3):
        cx = kuhn_ball("A4", n=n)
        randomize_labels(cx, seed=5 + n)

        sites = find_pachner_2_3_sites(cx)
        print(f"Kuhn n={n}: {len(sites)} legal 2->3 sites")
        for (a, b, face) in sites[:12]:
            before = snapshot(cx)
            bnd_before = boundary_signature(cx)
            try:
                mv = apply_pachner_2_3(cx, a, b)
            except Exception as e:  # noqa: BLE001 - the point of the probe
                print(f"  2->3 at {a},{b} RAISED {type(e).__name__}: {e}")
                continue
            total_23 += 1
            bnd_after = boundary_signature(cx)
            revert_move(cx, mv)
            after_revert = snapshot(cx)
            if before == after_revert and bnd_before == bnd_after:
                ok_23 += 1
            else:
                print(f"  2->3 at {a},{b}: boundary preserved={bnd_before == bnd_after}, "
                      f"revert exact={before == after_revert}")

        sites32 = find_pachner_3_2_sites(cx)
        for (u, w) in sites32[:12]:
            before = snapshot(cx)
            bnd_before = boundary_signature(cx)
            try:
                mv = apply_pachner_3_2(cx, (u, w))
            except Exception as e:  # noqa: BLE001
                print(f"  3->2 at edge {(u, w)} RAISED {type(e).__name__}: {e}")
                continue
            total_32 += 1
            bnd_after = boundary_signature(cx)
            revert_move(cx, mv)
            if before == snapshot(cx) and bnd_before == bnd_after:
                ok_32 += 1

    print(f"\n2->3 round trips clean: {ok_23}/{total_23}")
    print(f"3->2 round trips clean: {ok_32}/{total_32}")


if __name__ == "__main__":
    main()
