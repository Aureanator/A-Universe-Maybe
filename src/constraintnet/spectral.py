r"""Spectral geometry probes: diffusion-based dimension of the mesh (referee audit item 9).

The complex is 3-dimensional BY CONSTRUCTION (3-simplices); what nobody has measured is that
its *diffusion behaviour* is consistent with that input.  The spectral dimension d_s(t) of a
graph is read from the return probability P(t) of the simple random walk:

.. math:: P(t) \sim t^{-d_s/2} \quad (t \to \text{intermediate})

For a d-dimensional lattice, d_s = d at intermediate times; fractals, bottlenecks or
lower-dimensional skeletons show up as d_s != 3.  If this ever FAILS on our Kuhn balls, the
"3D relational geometry" narrative is contradicted by its own walk — which is exactly why we
measure it instead of asserting it.

Pure Python, no RNG (kernel purity): return probabilities are computed exactly by dynamic
programming over walk lengths.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Sequence, Set, Tuple

from .complex import SimplicialComplex

__all__ = [
    "tetra_adjacency",
    "vertex_adjacency",
    "return_probabilities",
    "spectral_dimension_estimate",
]


def _neighbours(adj: Dict[int, Set[int]], u: int) -> List[int]:
    return sorted(adj.get(u, ()))


def tetra_adjacency(cx: SimplicialComplex) -> Dict[int, Set[int]]:
    """Tetrahedra as nodes; edges when they share a triangular face."""
    import itertools

    by_face: Dict[Tuple[int, int, int], List[Tuple[int, ...]]] = {}
    for tet in cx.tetrahedra():
        t = tuple(sorted(tet))
        for face in itertools.combinations(t, 3):
            by_face.setdefault(face, []).append(t)
    ids = {t: i for i, t in enumerate(sorted(cx.tetrahedra(), key=lambda t: tuple(t)))}
    out: Dict[int, Set[int]] = {i: set() for i in ids.values()}
    for tets in by_face.values():
        for a in range(len(tets)):
            for b in range(a + 1, len(tets)):
                out[ids[tets[a]]].add(ids[tets[b]])
                out[ids[tets[b]]].add(ids[tets[a]])
    return out


def vertex_adjacency(cx: SimplicialComplex) -> Dict[int, Set[int]]:
    """The 1-skeleton as a walk graph."""
    out: Dict[int, Set[int]] = {v: set() for v in cx.vertices()}
    for (u, v) in cx.edges():
        out.setdefault(u, set()).add(v)
        out.setdefault(v, set()).add(u)
    return out


def return_probabilities(adj: Dict[int, Set[int]], steps: int) -> List[float]:
    """P(t) = mean over start vertices of Prob(back at start at time t), exact DP.

    P(0) = 1 by convention.  Isolated nodes (degree 0) stay put — their contribution is a
    delta that would fake a dimension-0 tail at long times, so they are excluded from the mean
    and reported nowhere else; on connected meshes this never triggers.
    """
    nodes = [u for u in sorted(adj) if adj.get(u)]
    n = len(nodes)
    if n == 0:
        return [1.0] + [0.0] * steps
    pos = {u: i for i, u in enumerate(nodes)}
    nbrs = [[pos[v] for v in _neighbours(adj, u)] for u in nodes]

    acc = [0.0] * (steps + 1)
    for s_idx, _s in enumerate(nodes):
        p = [0.0] * n
        p[s_idx] = 1.0
        for t in range(1, steps + 1):
            q = [0.0] * n
            for i in range(n):
                pi = p[i]
                if pi == 0.0:
                    continue
                share = pi / len(nbrs[i])
                for j in nbrs[i]:
                    q[j] += share
            p = q
            acc[t] += p[s_idx]
    return [1.0] + [a / n for a in acc[1:]]


def spectral_dimension_estimate(probs: Sequence[float], t_lo: int = 4, t_hi: int | None = None) -> float:
    """d_s = -2 * slope of log P(t) vs log t over [t_lo, t_hi] (least squares).

    Choose t_hi well below the time the walk feels the boundary (roughly (graph diameter)^2 / 2);
    a single number is meaningless without that care — always report the range used.
    """
    hi = t_hi if t_hi is not None else max(t_lo + 1, len(probs) - 1)
    pts = [(math.log(t), math.log(p)) for t, p in enumerate(probs) if t_lo <= t <= hi and p > 0]
    if len(pts) < 2:
        return float("nan")
    mx = sum(x for x, _ in pts) / len(pts)
    my = sum(y for _, y in pts) / len(pts)
    num = sum((x - mx) * (y - my) for x, y in pts)
    den = sum((x - mx) ** 2 for x, _ in pts)
    slope = num / den if den else float("nan")
    return -2.0 * slope
