"""Gauge transformations, gauge fixing, and the tetrahedron moduli count.

The gauge action is the one from the specification: assign ``lambda_v`` to each
vertex and transform edge labels by

    A_uv  ->  lambda_u^{-1} * A_uv * lambda_v .

Consequences implemented here:

* face holonomies transform by conjugation at their base vertex, so their
  conjugacy classes are invariant (Test 2);
* fixing a spanning tree of the 1-skeleton to the identity leaves only a global
  diagonal conjugation as residual freedom -- exactly one group element -- which is
  what makes the tetrahedron's moduli space finite and countable;
* for ``A_4`` on ``d(Delta^3)``: ``12**3 = 1728`` raw gauge-fixed configurations,
  reducing to **178** gauge-inequivalent classes (Test 3).

The 178 is not a magic number: Burnside's lemma gives it in closed form,

    |orbits| = (1/|G|) * sum_{g in G} |C(g)|^3
             = (12^3 + 3*4^3 + 8*3^3) / 12 = 2136 / 12 = 178

where ``|C(g)|`` is the centralizer size of ``g``.  ``burnside_prediction()``
computes that from the group data and the code checks it against brute force.
"""

from __future__ import annotations

import itertools
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex, spanning_tree
from .groups import Group

__all__ = [
    "gauge_transform",
    "gauge_transform_edge",
    "gauge_fix_spanning_tree",
    "enumerate_gauge_fixed_configs",
    "global_conjugate_config",
    "quotient_by_global_conjugation",
    "tetrahedron_moduli",
    "burnside_prediction",
]

# --------------------------------------------------------------------------- #
# transformations
# --------------------------------------------------------------------------- #
def gauge_transform(cx: SimplicialComplex, lambdas: Dict[int, object]) -> None:
    """Apply ``A_uv -> lambda_u^{-1} A_uv lambda_v`` to every edge.

    Vertices missing from ``lambdas`` are treated as the identity.  Labels are
    rewritten in their stored (canonical) orientation so the reverse-orientation
    rule stays satisfied automatically.
    """
    group = cx.group
    e = group.identity()
    for (a, b), stored in list(cx._labels.items()):  # noqa: SLF001 - intentional in-module access
        lam_a = lambdas.get(a, e)
        lam_b = lambdas.get(b, e)
        new_stored = group.multiply(group.multiply(group.inverse(lam_a), stored), lam_b)
        cx._labels[(a, b)] = new_stored  # noqa: SLF001


def gauge_transform_edge(edge, g_source, g_target) -> None:
    """Spec-shaped single-edge gauge transform (``edge`` is an :class:`EdgeView`)."""
    group = edge.label and _group_of(edge)
    left = group.inverse(g_source)
    edge.label = group.multiply(group.multiply(left, edge.label), g_target)


def _group_of(edge) -> Group:  # pragma: no cover - tiny helper
    return edge._cx.group  # noqa: SLF001


# --------------------------------------------------------------------------- #
# gauge fixing
# --------------------------------------------------------------------------- #
def gauge_fix_spanning_tree(
    cx: SimplicialComplex,
    tree: Optional[Sequence[Tuple[int, int]]] = None,
    root: Optional[int] = None,
) -> Dict[int, object]:
    """Choose ``lambda_v`` so every spanning-tree edge carries the identity.

    Returns the gauge map that was applied.  With a connected complex and a tree on
    all vertices, the only remaining freedom is a single global conjugation.
    """
    group = cx.group
    if tree is None:
        tree_edges, _ = spanning_tree(cx.edges(), root=root)
    else:
        tree_edges = [tuple(sorted((int(u), int(v)))) for u, v in tree]

    # build adjacency of the tree and walk outward from the root
    children: Dict[int, List[Tuple[int, int]]] = {}
    for key in tree_edges:
        children.setdefault(key[0], [])
        children.setdefault(key[1], [])
    adj: Dict[int, List[int]] = {v: [] for edges in tree_edges for v in edges}
    for (u, v) in tree_edges:
        adj[u].append(v)
        adj[v].append(u)

    start = root if root is not None else (min(adj) if adj else None)
    lambdas: Dict[int, object] = {}
    if start is None:
        return lambdas
    lambdas[start] = group.identity()
    order = [start]
    parent: Dict[int, Optional[int]] = {start: None}
    queue = [start]
    while queue:
        node = queue.pop(0)
        for nxt in sorted(adj[node]):
            if nxt in parent:
                continue
            parent[nxt] = node
            order.append(nxt)
            queue.append(nxt)

    # propagate: lambda_c = A_pc^{-1} * lambda_p  makes the transformed tree edge trivial
    for node in order:
        p = parent[node]
        if p is None:
            continue
        a_pc = cx.label(p, node)
        lambdas[node] = group.multiply(group.inverse(a_pc), lambdas[p])

    gauge_transform(cx, lambdas)
    return lambdas


# --------------------------------------------------------------------------- #
# enumeration and quotienting
# --------------------------------------------------------------------------- #
def enumerate_gauge_fixed_configs(group: Group, free_edges: Sequence[Tuple[int, int]]):
    """All assignments of group elements to the independent (non-tree) edges."""
    return [tuple(values) for values in itertools.product(group.elements, repeat=len(free_edges))]


def global_conjugate_config(config: Sequence[object], lam, group: Group):
    """Residual gauge action after tree fixing: conjugate every label by ``lam``."""
    return tuple(group.conjugate(lam, value) for value in config)


def orbit_of_config(config: Sequence[object], group: Group) -> frozenset:
    return frozenset(global_conjugate_config(config, lam, group) for lam in group.elements)


def canonical_config(config: Sequence[object], group: Group):
    """Deterministic representative of an orbit (lexicographic minimum)."""
    return min(orbit_of_config(config, group))


def quotient_by_global_conjugation(configs: Iterable[Sequence[object]], group: Group):
    """Group configurations into residual-gauge orbits.

    Returns ``(orbits, canonical_index)`` where ``canonical_index`` maps each orbit's
    canonical representative to the orbit itself.
    """
    index: Dict[tuple, set] = {}
    for config in configs:
        rep = canonical_config(config, group)
        index.setdefault(rep, set()).add(tuple(config))
    orbits = [frozenset(members) for _, members in sorted(index.items(), key=lambda kv: list(kv[0]))]
    return orbits, index


def burnside_prediction(group: Group, n_free_edges: int) -> float:
    """Number of residual-conjugation orbits predicted by Burnside's lemma."""
    total = 0
    for lam in group.elements:
        centralizer_size = len(group.centralizer(lam))
        total += centralizer_size ** n_free_edges
    return total / group.order()


def tetrahedron_moduli(group: Group):
    """The milestone-1 benchmark: raw gauge-fixed count and inequivalent classes.

    Spanning tree on vertices ``0,1,2,3`` is ``(0,1), (1,2), (2,3)``, so the free
    labels are ``A_02, A_03, A_13``.
    """
    free_edges = [(0, 2), (0, 3), (1, 3)]
    configs = enumerate_gauge_fixed_configs(group, free_edges)
    orbits, index = quotient_by_global_conjugation(configs, group)
    return {
        "group": group.name,
        "free_edges": free_edges,
        "raw_count": len(configs),
        "class_count": len(orbits),
        "orbits": orbits,
        "canonical_index": index,
        "burnside": burnside_prediction(group, len(free_edges)),
    }
