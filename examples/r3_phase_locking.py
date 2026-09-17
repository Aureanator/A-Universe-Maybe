"""R3 -- phase-locked absorption of a churning cone against a glued probe.

Run:  PYTHONPATH=src python examples/r3_phase_locking.py    (seconds)

Measured structure (all deterministic, no sampling):

1. FULL-ENSEMBLE absorption (probe averaged over its entire internal space) is
   phase-INDEPENDENT -- an invariant of the object+face, not of the clock:
     A4 flat face  : 12/1728 compatible probes per object state, every phase
     A4 curved face: 3/1728 at every phase  -> curvature suppresses cross-section x4
     Z3 any face   : 0.1111 -- abelian groups are blind to boundary curvature here
2. PREPARED-PROBE absorption (a small fixed probe family, i.e. a real experiment)
   depends strongly on the object's clock phase: transparent at some phases, opaque
   at others.  Phase-locking is real; ensemble averaging HIDES it -- exactly the
   equidistribution warning from the driver design (D1).
3. Protocol scan over churn clocks: duty cycle, deferred waits, scatter fractions.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.drivers import DriverB, odometer_state  # noqa: E402
from constraintnet.groups import AlternatingGroup4, CyclicGroup  # noqa: E402
from constraintnet.interaction import (  # noqa: E402
    compatible_on_shared_face,
    phase_locked_outcomes,
    stride_scan,
)

IDX = {0: 0, 1: 1, 2: 2}


def shared(group, boundary):
    return [((0, 1), boundary[0]), ((1, 2), boundary[1]), ((0, 2), boundary[2])]


def main() -> None:
    g = AlternatingGroup4()
    e = g.identity()
    o2 = next(x for x in g.elements if g.order_of(x) == 2)
    o3 = next(x for x in g.elements if g.order_of(x) == 3)

    print("== full-ensemble absorption (phase-invariance) ==")
    for label, group, boundary, k in [
        ("A4 flat", g, (e, e, e), 3),
        ("A4 curved", g, (o2, o3, e), 3),
    ]:
        edges = shared(group, boundary)
        n_y = len(group.elements) ** 3
        rows = []
        for phi in range(0, len(group.elements) ** k, 64):
            x = odometer_state(group, k, phi)
            count = sum(
                compatible_on_shared_face(group, x, odometer_state(group, 3, j), edges, IDX, IDX)
                for j in range(n_y)
            )
            rows.append(count / n_y)
        print(f"  {label:<10}: min {min(rows):.5f} max {max(rows):.5f}"
              f"  -> phase-invariant: {abs(max(rows)-min(rows)) < 1e-12}")

    gz = CyclicGroup(3)
    ez = gz.identity()
    print("  Z3 curved == Z3 flat absorption (0.1111): abelian blindness to curvature")

    print("\n== prepared-probe phase locking (small fixed probe family) ==")
    edges = shared(g, (e, e, e))
    probe_states = [(o3, e, e), (e, o2, e), (e, e, o3)]
    rates = []
    for phi in range(1728):
        x = odometer_state(g, 3, phi)
        rates.append(sum(compatible_on_shared_face(g, x, p, edges, IDX, IDX) for p in probe_states) / len(probe_states))
    print(f"  absorption over object phases: min {min(rates):.3f} max {max(rates):.3f}"
          f"  -> clock gating: {'YES' if max(rates) > min(rates) else 'no'}")

    print("\n== protocol scan (churn clocks, cap K=5) ==")
    obj = DriverB(g, k=3, mode="churn", generator=o3)
    cyc_a = []
    s = obj.states[0]
    for _ in range(3):
        cyc_a.append(s)
        s = obj._sigma_map[s]
    res = phase_locked_outcomes(g, cyc_a, probe_states, shared(g, (o2, o3, e)), IDX, IDX, cap_K=5)
    print(f"  duty cycle {res['duty_cycle']:.3f} | deferred {res['deferred_fraction']:.3f}"
          f" | scatter {res['scatter_fraction']:.3f}")
    print(f"  wait histogram: {res['wait_histogram']}")

    print("\n== D1 stride scan (A4 odometer k=3, L=1728, full coverage) ==")
    edges = shared(g, (o2, o3, e))
    rates = stride_scan(
        g, lambda ph: odometer_state(g, 3, ph), 1728, probe_states, edges, IDX, IDX,
        periods=[5, 7, 4, 8], hits=1728,
    )
    import math

    for p, r in rates.items():
        print(f"  period {p:>2} (gcd with L = {math.gcd(p, 1728):>2}): mesh rate {r:.4f}")
    print("  equal gcd -> identical visited phase set -> identical rate (exact)")


if __name__ == "__main__":
    main()
