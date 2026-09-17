"""Kick test -- does a violated constraint restore itself? (experimental branch)

Run:  PYTHONPATH=src python examples/kick_test.py        # ~4 minutes

One illegal move is forced on the charge edge of a closed Kuhn ball; then three
acceptance regimes compete to undo it: the production reject-rule, free diffusion, and
Metropolis dynamics on a gauge-invariant curvature action at several temperatures.
Restoration times are recorded for three observables: full sector (exact conserved data),
charge classes of the frozen core faces, and the exact edge label.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.kick import run_kick_study  # noqa: E402


def main() -> None:
    print("kick study :: A4 Kuhn ball n=2, one forced illegal move, 3000 steps per trial\n")
    trials = run_kick_study(steps=3000, seeds=(1, 2), betas=(0.25, 1.0, 4.0))
    for trial in trials:
        print(trial.as_row())

    print(
        "\nreading: 'never' means no restoration inside the window; sectors visited counts\n"
        "distinct gauge-invariant external configurations touched (the superselection drift)."
    )


if __name__ == "__main__":
    main()
