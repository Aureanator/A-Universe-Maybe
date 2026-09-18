"""P4b — isolate the Pachner failure: fresh complex per move, then sequential with re-scan.

Failure mode seen in p4_pachner.py: after a 2->3 + revert round trip, later sites from the
ORIGINAL site list raise MoveError ("face belongs to 1/0 tetrahedra") or SimplicialError
("degenerate tetrahedron").  Two candidate causes:
  (a) stale site list across mutations (harness bug),
  (b) revert_move not restoring the complex exactly (library bug).
This probe separates them.
"""

from __future__ import annotations

import itertools
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "src"))

from constraintnet.moves import (  # noqa: E402
    apply_pachner_2_3,
    find_pachner_2_3_sites,
    revert_move,
)
from constraintnet.seeds import kuhn_ball, randomize_labels  # noqa: E402


def snapshot(cx):
    return (
        frozenset(tuple(sorted(t)) for t in cx.tetrahedra()),
        tuple((tuple(sorted(e)), cx.label(*e)) for e in sorted(cx.edges())),
        frozenset(tuple(sorted(f)) for f in cx.faces()),
    )


def main():
    base = kuhn_ball("A4", n=2)
    randomize_labels(base, seed=7)

    # ---- (a) each site on a FRESH copy -------------------------------------------------
    sites0 = find_pachner_2_3_sites(base)
    print(f"Kuhn n=2 legal 2->3 sites: {len(sites0)}")
    ok = fail = 0
    for k, (a, b, face) in enumerate(sites0):
        cx = base.copy()
        before = snapshot(cx)
        try:
            mv = apply_pachner_2_3(cx, a, b)
            revert_move(cx, mv)
            ok += snapshot(cx) == before
            fail += snapshot(cx) != before
        except Exception as e:  # noqa: BLE001
            fail += 1
            print(f"  fresh-copy site {a},{b}: {type(e).__name__}: {e}")
    print(f"(a) fresh-copy round trips: ok={ok} fail={fail}")

    # ---- (b) sequential on ONE complex, re-scanning sites each time --------------------
    cx = base.copy()
    rounds_ok = rounds_fail = 0
    drift_at = None
    for r in range(12):
        sites = find_pachner_2_3_sites(cx)
        if not sites:
            break
        (a, b, face) = sites[r % len(sites)]
        before = snapshot(cx)
        try:
            mv = apply_pachner_2_3(cx, a, b)
            revert_move(cx, mv)
            if snapshot(cx) == before:
                rounds_ok += 1
            else:
                rounds_fail += 1
                if drift_at is None:
                    drift_at = (r, (a, b), before, snapshot(cx))
        except Exception as e:  # noqa: BLE001
            rounds_fail += 1
            print(f"  sequential round {r} at {a},{b}: {type(e).__name__}: {e}")
            if drift_at is None:
                drift_at = (r, (a, b), before, snapshot(cx))
    print(f"(b) sequential re-scanned rounds: ok={rounds_ok} fail={rounds_fail}")

    # ---- (c) does revert restore FACE set exactly? one site, detailed diff -------------
    cx = base.copy()
    sites = find_pachner_2_3_sites(cx)
    if sites:
        (a, b, face) = sites[0]
        tets0, edges0, faces0 = snapshot(cx)
        mv = apply_pachner_2_3(cx, a, b)
        revert_move(cx, mv)
        tets1, edges1, faces1 = snapshot(cx)
        print(f"(c) site {a},{b}: tets restored={tets0 == tets1}  "
              f"edges+labels restored={edges0 == edges1}  faces restored={faces0 == faces1}")
        if faces0 != faces1:
            print("    faces lost:", sorted(faces0 - faces1))
            print("    faces gained:", sorted(faces1 - faces0))


if __name__ == "__main__":
    main()
