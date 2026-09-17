"""Visual coordinates.  Projection only -- dynamics never reads these.

Two embedders are provided:

``from_grid``     uses lattice metadata attached at build time (a projection of the
                  combinatorics, nothing more);
``force_directed`` a plain 3D spring embedder for complexes with no grid, so even an
                  abstract complex can be drawn without assuming space.

Both return ``{vertex: numpy array(x, y, z)}`` normalised into roughly the unit cube.
"""

from __future__ import annotations

from typing import Dict, Optional

import numpy as np

from ..complex import SimplicialComplex

__all__ = ["positions", "from_grid", "force_directed"]


def from_grid(cx: SimplicialComplex) -> Optional[Dict[int, np.ndarray]]:
    """Coordinates taken from ``vertex.metadata['grid']`` if every vertex has one."""
    coords = {}
    for vertex in cx.vertices():
        grid = cx.vertex(vertex).metadata.get("grid")
        if grid is None:
            return None
        coords[vertex] = np.asarray(grid, dtype=float)
    return _normalise(coords)


def force_directed(
    cx: SimplicialComplex,
    iterations: int = 240,
    seed: int = 0,
    repulsion: float = 1.0,
    attraction: float = 0.6,
    jitter: float = 0.35,
) -> Dict[int, np.ndarray]:
    """Deterministic 3D spring embedder (Fruchterman-Reingold style)."""
    vertices = cx.vertices()
    if not vertices:
        return {}
    rng = np.random.default_rng(seed)
    index = {vertex: i for i, vertex in enumerate(vertices)}
    n = len(vertices)
    points = rng.normal(scale=1.0, size=(n, 3))

    edges = [(index[u], index[v]) for (u, v) in cx.edges() if u in index and v in index]
    if not edges:
        return {vertex: points[index[vertex]] for vertex in vertices}

    area = 1.0
    k = np.cbrt(area / max(1, n)) * 0.9
    temperature = 0.35
    adj_pairs = np.array(edges, dtype=int) if edges else np.zeros((0, 2), dtype=int)

    for step in range(iterations):
        disp = np.zeros_like(points)
        # repulsion between every pair (n is small: lattices here are <= a few hundred)
        delta = points[:, None, :] - points[None, :, :]
        distance = np.linalg.norm(delta, axis=-1)
        np.fill_diagonal(distance, 1e-6)
        force_mag = (repulsion * k * k) / distance
        disp += (delta / distance[..., None] * force_mag[..., None]).sum(axis=1)

        # attraction along edges
        if len(adj_pairs):
            a = points[adj_pairs[:, 0]]
            b = points[adj_pairs[:, 1]]
            diff = a - b
            norm = np.linalg.norm(diff, axis=1)[:, None]
            norm[norm == 0.0] = 1e-6
            pull = attraction * (norm * norm) / k
            vec = diff / norm * pull
            np.add.at(disp, adj_pairs[:, 0], -vec)
            np.add.at(disp, adj_pairs[:, 1], vec)

        length = np.linalg.norm(disp, axis=1)[:, None]
        length[length == 0.0] = 1e-9
        capped = disp / length * np.minimum(length, temperature)
        points += capped
        temperature = max(0.02, temperature * (0.985 if step < iterations // 2 else 0.96))

    # keep a hint of the original structure: tiny jitter-free stabilisation pass
    points += rng.normal(scale=jitter * 1e-3, size=points.shape)
    return _normalise({vertex: points[index[vertex]] for vertex in vertices})


def positions(cx: SimplicialComplex, method: str = "auto", seed: int = 0) -> Dict[int, np.ndarray]:
    """Best available visual embedding of ``cx``."""
    if method in ("auto", "grid"):
        grid = from_grid(cx)
        if grid is not None:
            return grid
        if method == "grid":
            raise ValueError("no 'grid' metadata on vertices")
    return force_directed(cx, seed=seed)


def _normalise(coords: Dict[int, np.ndarray]) -> Dict[int, np.ndarray]:
    stacked = np.stack(list(coords.values()))
    centre = stacked.mean(axis=0)
    shifted = {vertex: value - centre for vertex, value in coords.items()}
    scale = np.abs(np.stack(list(shifted.values()))).max() or 1.0
    return {vertex: value / scale for vertex, value in shifted.items()}
