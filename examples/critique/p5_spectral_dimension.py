"""P5 — spectral dimension of Kuhn balls via exact diffusion (referee item 9).

Pre-registered docs/PREDICTIONS.md P5: long-time d_s ~ 3 within [2.5, 3.5] for n>=3; short
times deviate (recorded, not hidden); vertex-skeleton walk also ~3 or we get a diary entry.
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "src"))

from constraintnet.seeds import kuhn_ball  # noqa: E402
from constraintnet.spectral import (  # noqa: E402
    return_probabilities,
    spectral_dimension_estimate,
    tetra_adjacency,
    vertex_adjacency,
)


def report(name, adj, steps=30):
    probs = return_probabilities(adj, steps)
    n_nodes = len([u for u in adj if adj[u]])
    d_early = spectral_dimension_estimate(probs, 2, 6)
    d_mid = spectral_dimension_estimate(probs, 4, min(16, steps))
    print(f"{name:28s} nodes={n_nodes:5d}  P: " + " ".join(f"{p:.3f}" for p in probs[1:9]))
    print(f"{'':28s} d_s(t=2..6) = {d_early:5.2f}   d_s(t=4..16) = {d_mid:5.2f}")


def main():
    # ground-truth controls first
    path = {i: {j for j in (i - 1, i + 1) if 0 <= j < 41} for i in range(41)}
    report("CONTROL 41-path (expect ~1)", path, steps=25)

    grid = {}
    L = 6
    for x in range(L):
        for y in range(L):
            for z in range(L):
                u = (x, y, z)
                grid[u] = {
                    (a, b, c)
                    for a, b, c in [(x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)]
                    if 0 <= a < L and 0 <= b < L and 0 <= c < L
                }
    report("CONTROL Z^3 6-cube (~3 early)", grid, steps=25)

    for n in (1, 2, 3):
        cx = kuhn_ball("A4", n=n)
        report(f"Kuhn n={n} tetra-adjacency", tetra_adjacency(cx))
    for n in (1, 2, 3, 4):
        cx = kuhn_ball("A4", n=n)
        report(f"Kuhn n={n} vertex graph", vertex_adjacency(cx), steps=25)


if __name__ == "__main__":
    main()
