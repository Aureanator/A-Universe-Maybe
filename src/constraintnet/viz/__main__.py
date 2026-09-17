"""Command-line entry point for the viewer.

Examples
--------
Interactive window (needs a display)::

    python -m constraintnet.viz --demo lattice --group A4 --n 2

Record what happens instead::

    python -m constraintnet.viz --demo tetra   --gif out/tetra_buzz.gif --frames 180
    python -m constraintnet.viz --demo lattice --png out/lattice.png --advance 400
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "src"))


def build_driver(args: argparse.Namespace):
    if args.demo == "tetra":
        from .drivers import TetraDriver

        return TetraDriver(group=args.group, seed=args.seed, gauge_fixed=not args.raw_labels)
    if args.demo == "orbit":
        from .drivers import OrbitTourDriver

        return OrbitTourDriver(group=args.group, seed=args.seed, dwell=max(1, args.dwell))
    if args.demo == "lattice":
        from .drivers import LatticeDriver

        return LatticeDriver(
            group=args.group,
            n=args.n,
            seed=args.seed,
            interior_moves=args.interior_moves,
            signal_every=max(0, args.signal_every),
        )
    raise SystemExit(f"unknown demo {args.demo!r}")


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description="Animated viewer for the constraint-network simulator")
    parser.add_argument("--demo", choices=("tetra", "orbit", "lattice"), default="lattice")
    parser.add_argument("--group", default="A4", help="A4 (default), Z3, Z2, ...")
    parser.add_argument("--n", type=int, default=2, help="lattice resolution for the lattice demo")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--dwell", type=int, default=6, help="orbit tour: animation frames per state")
    parser.add_argument("--signal-every", type=int, default=60, help="frames between test-signal pulses (0 = off)")
    parser.add_argument("--interior-moves", action="store_true", help="restrict moves to interior edges")
    parser.add_argument("--raw-labels", action="store_true", help="skip gauge fixing so residual copies are visible")
    parser.add_argument("--advance", type=int, default=0, help="run this many steps before drawing/recording")
    parser.add_argument("--frames", type=int, default=180, help="animation frames to record")
    parser.add_argument("--interval", type=int, default=70, help="milliseconds per animation frame")
    parser.add_argument("--steps-per-frame", type=int, default=6)
    parser.add_argument("--gif", default=None, help="record an animated GIF to this path and exit")
    parser.add_argument("--png", default=None, help="save a single still frame to this path and exit")
    args = parser.parse_args(argv)

    driver = build_driver(args)
    if args.advance:
        for _ in range(args.advance):
            driver.advance()

    if args.png:
        from .render import Viewer

        viewer = Viewer(driver, rotate=False)
        os.makedirs(os.path.dirname(os.path.abspath(args.png)), exist_ok=True)
        viewer._draw(driver.frame())
        viewer.fig.savefig(args.png, dpi=140, facecolor=viewer.fig.get_facecolor())
        print(f"wrote still frame -> {args.png}")
        return 0

    if args.gif:
        from .render import record_gif

        path = record_gif(
            driver,
            args.gif,
            frames=args.frames,
            interval_ms=args.interval,
            steps_per_frame=args.steps_per_frame,
        )
        print(f"wrote animation -> {path}")
        return 0

    from .render import Viewer

    viewer = Viewer(driver)
    try:
        viewer.run()
    except Exception as exc:  # pragma: no cover - depends on the machine's display
        fallback = os.path.join("out", f"{args.demo}_buzz.gif")
        print(f"no interactive display available ({exc}); recording {fallback} instead")
        record_gif(driver, fallback, frames=args.frames, interval_ms=args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
