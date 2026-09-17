"""Milestone 4 -- persistent defect: seed matter, evolve under conservation, watch it survive.

Run:  PYTHONPATH=src python examples/milestone4.py

Story: one order-2 (Klein-four) label written on a single surface edge of a closed Kuhn
ball is a *charge*: conservation freezes the curvature classes of the boundary faces that
contain it, and the persistence theorem says no appearance-preserving evolution can make
curvature vanish.  The interior buzzes -- every accepted move there is unconstrained --
and curvature heats and diffuses through the bulk; what persists is the external residue.

The neutral control (same lump hidden strictly in the interior) presents nothing to any
outside loop: it is a virtual fluctuation, not matter, and ``is_persistent`` says so.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.persistence import run_persistence_experiment  # noqa: E402


def report(r) -> None:
    print(f"\n=== {r['kind'].upper()} defect :: seed edge {r['seed']['edge']} in class {r['seed']['class']} ===")
    print(f"  moves: {r['stats']}")
    print(f"  confinement: surface moves accepted {r['accepted_surface']}, rejected {r['rejected_surface']}"
          f"   |   interior: accepted {r['accepted_interior']}, rejected {r['rejected_interior']}")
    print(f"  matter (nontrivial external residue): {r['matter']}   core faces frozen: {r['charge_core_size']}")
    print(f"  sector conserved over run: {r['sector_conserved']}")
    print(f"  charge class start == end (spec Test 5): {r['frozen_core_classes_stable']}")
    print(f"  tracked identity survival: {r['survival_ratio']:.2%}   gaps: {r['gaps']}   splits seen: {r['splits_seen']}")
    print(f"  curvature heating: curved faces min {r['curved_min']} -> max {r['curved_max']} (ever flat: {r['ever_flat']})")
    print(f"  is_persistent: {r['is_persistent']}")


def main() -> None:
    charged = run_persistence_experiment(kind="charged", n=2, steps=1500, rng_seed=7)
    neutral = run_persistence_experiment(kind="neutral", n=2, steps=1500, rng_seed=7)
    report(charged)
    report(neutral)

    # strict assertions -- the milestone's success criteria
    assert charged["matter"] and charged["charge_core_size"] == 2
    assert charged["sector_conserved"], "appearance of a closed universe must be invariant"
    assert charged["frozen_core_classes_stable"], "spec Test 5: charge class start == end"
    assert charged["survival_ratio"] == 1.0 and charged["gaps"] == 0
    assert charged["is_persistent"], "charged defect must qualify as persistent matter"
    assert charged["accepted_surface"] == 0, "charge leaked through the boundary!"
    assert charged["rejected_interior"] == 0, "interior moves cannot be rejected (theorem)"

    assert not neutral["matter"] and not neutral["is_persistent"], "neutral lump is not matter"
    assert neutral["sector_conserved"]

    print("\nMilestone 4 OK: a localized nontrivial defect persists, conserves its charge")
    print("class under boundary-preserving updates, and stays identifiable; the neutral")
    print("control correctly fails to qualify as matter.")


if __name__ == "__main__":
    main()
