"""R2/R3-lite -- phase-sweep ensemble: exclusion cross-section of a glued cone pair.

Run:  PYTHONPATH=src python examples/r2_phase_sweep.py   (fast, Z3; A4 optional)

Two flat-boundary cones churn deterministically (odometer sigma, single equidistributed
cycle).  At every phase pair we ask the kernel: is the fiber product over the shared
face non-empty?  The exact meshable fraction needs no sampling -- and a DriverA-style
random-glue experiment must reproduce it within sampling error (T3 consistency in
miniature: stochastic accept rate == deterministic phase measure, because they quantify
the SAME set).
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.drivers import DriverB  # noqa: E402
from constraintnet.groups import CyclicGroup, AlternatingGroup4  # noqa: E402
from constraintnet.interaction import compatible_on_shared_face, meshable_phases  # noqa: E402


def run(group, label):
    g = group
    e = g.identity()
    # object A: cone over d(Delta^3), internal slots for apex edges to vertices 0..3
    # probe B:   cone glued along face F=(0,1,2), internal slots for vertices 0..2
    shared_edges = [((0, 1), e), ((1, 2), e), ((0, 2), e)]
    index = {0: 0, 1: 1, 2: 2}

    objA = DriverB(g, k=4, mode="odometer")
    probeB = DriverB(g, k=3, mode="odometer")
    cycle_a = []
    state = objA.states[0]
    for _ in range(len(objA.states)):
        cycle_a.append(state)
        state = objA._sigma_map[state]
    cycle_b = []
    state = probeB.states[0]
    for _ in range(len(probeB.states)):
        cycle_b.append(state)
        state = probeB._sigma_map[state]

    matrix = meshable_phases(g, cycle_a, cycle_b, shared_edges, index, index)
    flat = [cell for row in matrix for cell in row]
    exact = sum(flat) / len(flat)
    row_means = [sum(row) / len(row) for row in matrix]

    # DriverA-style random glue attempts: same set, sampled instead of swept
    rng = random.Random(11)
    n_trials = 4000
    accepted = sum(
        compatible_on_shared_face(
            g,
            cycle_a[rng.randrange(len(cycle_a))],
            cycle_b[rng.randrange(len(cycle_b))],
            shared_edges,
            index,
            index,
        )
        for _ in range(n_trials)
    )
    empirical = accepted / n_trials

    print(f"\n{label}: odometer cycles L_A={len(cycle_a)}, L_B={len(cycle_b)}")
    print(f"  exact meshable fraction (phase sweep, no sampling): {exact:.4f}")
    print(f"  DriverA random-glue accept rate ({n_trials} trials):          {empirical:.4f}"
          f"   |diff| = {abs(exact - empirical):.4f}")
    print(f"  per-phase absorption (object A): min {min(row_means):.3f}, max {max(row_means):.3f}"
          f"  -> phase-locked structure: {'YES' if max(row_means) > min(row_means) else 'flat'}")


def main() -> None:
    run(CyclicGroup(3), "Z3 flat cone pair")
    if "--a4" in sys.argv:
        print("A4 sweep = 20736 x 1728 phase pairs: minutes, not seconds.")
        run(AlternatingGroup4(), "A4 flat cone pair")
    print("\nT3-style consistency: stochastic acceptance and deterministic phase measure")
    print("quantify the SAME joint-resolvable set; agreement is by construction, and the")
    print("per-phase absorption profile is where Driver B shows structure Driver A cannot.")


if __name__ == "__main__":
    main()
