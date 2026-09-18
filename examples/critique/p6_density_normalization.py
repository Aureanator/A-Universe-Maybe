"""P6 — the density-population artifact, measured before/after normalization (referee 13).

Driver A on Kuhn n=2: vacuum run (flat labels) and charged-defect run; shells around the
centre.  We record raw per-cell counts AND per-vertex densities, then compare shell profiles.

Pre-registered docs/PREDICTIONS.md P6: raw counts rise with shell population even in the
featureless vacuum; per-vertex normalization flattens vacuum while defect-core excess
survives (signal real, old magnitudes confounded).
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "src"))


def run(kind, steps=4000, seed=7):
    import random as _random

    from constraintnet.dynamics import Simulation
    from constraintnet.observer import Observer
    from constraintnet.persistence import seed_charged_defect, seed_neutral_defect
    from constraintnet.region import Region
    from constraintnet.seeds import kuhn_ball

    cx = kuhn_ball("A4", n=2)
    if kind == "charged":
        seed_charged_defect(cx)
    elif kind == "neutral":
        seed_neutral_defect(cx)
    region = Region(cx, cx.tetrahedra(), "universe")
    centre = min(cx.vertices())
    observer = Observer(cx, centre=centre)
    sim = Simulation(cx, region=region, rng=_random.Random(seed))

    for _ in range(steps):
        record = sim.attempt()
        if record.accepted:
            observer.record_move(record.support_edges, weight=1.0)
    return cx, observer


def profile(observer):
    out = {}
    for cell in sorted(observer.cells):
        members = observer.cells[cell]
        out[cell] = (len(members), observer.rho(cell), observer.rho_per_vertex(cell))
    return out


def main():
    print(f"{'run':10s} {'shell':8s} {'|cell|':>6s} {'raw rho':>9s} {'per-vertex':>10s}")
    for kind in ("vacuum", "charged", "neutral"):
        cx, obs = run(kind)
        prof = profile(obs)
        for cell, (size, raw, pv) in prof.items():
            print(f"{kind:10s} {cell:8s} {size:6d} {raw:9.1f} {pv:10.2f}")
        # correlation of raw count with shell size vs per-vertex flatness
        import statistics
        sizes = [v[0] for v in prof.values()]
        raws = [v[1] for v in prof.values()]
        pvs = [v[2] for v in prof.values()]

        def corr(a, b):
            ma, mb = statistics.mean(a), statistics.mean(b)
            num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
            den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
            return num / den if den else float("nan")

        print(f"  corr(raw rho, shell size)   = {corr(sizes, raws):+.3f}")
        print(f"  corr(per-vertex, shell size)= {corr(sizes, pvs):+.3f}")
        print()


if __name__ == "__main__":
    main()
