"""Canonical states: gauge-fixed labels, orbit IDs, and transition graphs.

Two subtleties live here, and getting either wrong silently corrupts every count.

**1. Re-gauge-fix after every move.** A move applied to a representative generally leaves
the spanning-tree slice, so the result must be projected back (``gauge_fix_spanning_tree``)
and then canonicalized over the residual global conjugation before it can be recorded --
otherwise gauge copies are counted as distinct dynamical states and counts inflate by up to
``|G|``.

**2. Canonicalize for reporting, never for exploration.** This is the trap that bit us
first.  Right-multiplication does not commute with conjugation:

    (lambda^-1 x lambda) * g   !=   lambda^-1 (x * g') lambda   in general,

so the set of successors depends on *which* member of an orbit you stand on.  Exploring
only from canonical representatives therefore loses transitions -- concretely it finds
174 rather than all **178** orbits for ``A_4`` on ``d(Delta^3)``, missing exactly the four
configurations whose labels lie in the Klein four subgroup, because their only incoming
edges come from non-canonical members of neighbouring orbits.

The correct construction implemented below explores the *raw* configuration graph (which
is gauge-slice honest) and projects to orbit representatives afterwards, so reported nodes
are physical states while no transition is dropped.
"""

from __future__ import annotations

import itertools
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from .complex import SimplicialComplex, connected_components
from .gauge import canonical_config, gauge_fix_spanning_tree, global_conjugate_config, stabilizer_of_config
from .groups import Group
from .holonomy import triangle_holonomy
from .moves import Move, apply_move, propose_edge_move, revert_move
from .region import Region

__all__ = [
    "StateId",
    "sector_signature",
    "gauge_fix_and_canonicalize",
    "free_edges_of",
    "transition_graph",
    "graph_components",
]


# --------------------------------------------------------------------------- #
# state identity
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class StateId:
    """The physical identity of a configuration.

    ``orbit_rep`` is the canonical representative of the residual-conjugation orbit;
    ``sector`` is the superselection label (gauge-invariant appearance signature).  Two
    configurations differing only by gauge have identical values by construction.
    """

    orbit_rep: Tuple
    sector: Tuple = ()
    free_edges: Tuple[Tuple[int, int], ...] = ()

    def little_group_size(self, group: Group) -> int:
        return len(stabilizer_of_config(self.orbit_rep, group))

    def short(self) -> str:
        return f"{self.orbit_rep!r}#{abs(hash(self.sector)) % 10_000:04d}"


def free_edges_of(cx: SimplicialComplex, tree: Sequence[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Non-tree edges in deterministic order -- the physical degrees of freedom."""
    tree_set = {tuple(sorted((int(u), int(v)))) for u, v in tree}
    return [edge for edge in cx.edges() if edge not in tree_set]


def sector_signature(cx: SimplicialComplex, region: Optional[Region] = None) -> Tuple:
    """Gauge-invariant signature of what a region presents to its exterior.

    With tetrahedra present this is the region's :class:`~constraintnet.region.Appearance`;
    for a pure surface such as ``d(Delta^3)`` every face is observable, so the curvature
    classes of all faces are used.
    """
    group = cx.group
    classes = list(group.conjugacy_classes())

    def class_id(element) -> int:
        for index, cls in enumerate(classes):
            if element in cls:
                return index
        raise AssertionError("element outside every conjugacy class")

    if region is not None and region.tets:
        appearance = region.appearance()
        faces = tuple(sorted((tuple(f), cid) for f, cid in appearance.face_curvatures))
        cycles = tuple(sorted((tuple(loop), cid) for loop, cid in appearance.cycle_charges))
        return ("region", faces, cycles)

    faces = tuple(
        sorted((tuple(face), class_id(triangle_holonomy(cx, face))) for face in cx.faces())
    )
    return ("surface", faces)


def gauge_fix_and_canonicalize(
    cx: SimplicialComplex,
    tree: Sequence[Tuple[int, int]],
    root: Optional[int] = None,
    region: Optional[Region] = None,
) -> StateId:
    """Project the current configuration onto a physical state id (in place).

    The complex is modified: it is re-gauge-fixed into the tree slice.  Callers that must
    preserve their own labelling should pass a copy.
    """
    gauge_fix_spanning_tree(cx, tree=tree, root=root)
    free = free_edges_of(cx, tree)
    labels = tuple(cx._labels[edge] for edge in free)  # noqa: SLF001
    orbit_rep = canonical_config(labels, cx.group)
    return StateId(orbit_rep=orbit_rep, sector=sector_signature(cx, region), free_edges=tuple(free))


# --------------------------------------------------------------------------- #
# transition graphs over physical states
# --------------------------------------------------------------------------- #
def transition_graph(
    template: SimplicialComplex,
    tree: Sequence[Tuple[int, int]],
    generators: Optional[Sequence] = None,
    max_states: int = 200_000,
    legitimacy: str = "appearance",
    root: Optional[int] = None,
):
    """Explore the state graph reachable by accepted elementary moves.

    Exploration happens on raw gauge-slice configurations (see the module docstring for why
    exploring canonical representatives directly is wrong); nodes of the returned graph are
    :class:`StateId` physical states obtained by projecting each visited configuration over
    the residual global conjugation.

    Parameters
    ----------
    legitimacy:
        ``"appearance"`` keeps only moves preserving the sector (the specification's
        conservation rule); ``"none"`` accepts every move, which is what one uses to map the
        full state space before adding dynamics.

    Returns a dict with raw and physical node/edge counts, adjacency maps, per-node reject
    counts, accept rate, connected components of the physical graph, and the little-group
    histogram of the visited physical states.
    """
    group = template.group
    root = root if root is not None else min(min(edge) for edge in tree)

    slice_template = template.copy()
    gauge_fix_spanning_tree(slice_template, tree=tree, root=root)
    free = tuple(free_edges_of(slice_template, tree))
    start_labels = tuple(slice_template._labels[edge] for edge in free)  # noqa: SLF001

    scratch = slice_template.copy()

    def sector_of(labels: Tuple) -> Tuple:
        for edge, value in zip(free, labels):
            scratch._labels[edge] = value  # noqa: SLF001
        return sector_signature(scratch)

    gens = list(generators) if generators else list(group.move_generators())

    raw_adjacency: Dict[Tuple, Set[Tuple]] = {start_labels: set()}
    rejected: Counter = Counter()
    proposals = 0
    queue: List[Tuple] = [start_labels]
    truncated = False

    while queue:
        current = queue.pop(0)
        current_sector = sector_of(current) if legitimacy == "appearance" else None
        for index, edge in enumerate(free):
            old = current[index]
            for g in gens:
                new = group.multiply(old, g)
                labels = current[:index] + (new,) + current[index + 1 :]
                proposals += 1
                if legitimacy == "appearance" and sector_of(labels) != current_sector:
                    rejected[current] += 1
                    continue
                raw_adjacency[current].add(labels)
                if labels not in raw_adjacency:
                    raw_adjacency[labels] = set()
                    queue.append(labels)
        if len(raw_adjacency) > max_states:
            truncated = True
            break

    # ---- project to physical states (reporting only; exploration is already complete) --
    physical_of: Dict[Tuple, StateId] = {}
    for labels in raw_adjacency:
        orbit_rep = canonical_config(labels, group)
        physical_of[labels] = StateId(
            orbit_rep=orbit_rep, sector=sector_of(labels), free_edges=free
        )

    physical_nodes = sorted({state for state in physical_of.values()}, key=lambda s: repr(s.orbit_rep))
    adjacency: Dict[StateId, Set[Tuple[StateId, str]]] = {node: set() for node in physical_nodes}
    raw_edges = 0
    for labels, targets in raw_adjacency.items():
        source = physical_of[labels]
        for target_labels in targets:
            target = physical_of[target_labels]
            raw_edges += 1
            adjacency[source].add((target, f"{labels} -> {target_labels}"))

    edge_list = [(a, b) for a, targets in adjacency.items() for (b, _) in targets]
    components = graph_components(physical_nodes, edge_list)
    little_groups: Counter = Counter()
    for node in physical_nodes:
        little_groups[_little_group_label(node.orbit_rep, group)] += 1

    return {
        "raw_nodes": len(raw_adjacency),
        "raw_edges": raw_edges,
        "nodes": physical_nodes,
        "node_count": len(physical_nodes),
        "adjacency": adjacency,
        "rejected_per_node": dict(rejected),
        "proposals": proposals,
        "accepted_edges": raw_edges,
        "reject_count": sum(rejected.values()),
        "accept_rate": (raw_edges / proposals) if proposals else 0.0,
        "components": components,
        "component_count": len(components),
        "largest_component": max((len(c) for c in components), default=0),
        "little_groups": dict(little_groups),
        "free_edges": free,
        "truncated": truncated,
        "legitimacy": legitimacy,
    }


def _little_group_label(config: Tuple, group: Group) -> str:
    stab = stabilizer_of_config(config, group)
    order = len(stab)
    if order == 1:
        return "trivial"
    if order == group.order():
        return group.name
    orders = {group.order_of(x) for x in stab}
    if order == 2:
        return "Z2"
    if order == 3:
        return "Z3"
    if order == 4:
        return "V4" if orders <= {1, 2} else "Z4"
    return f"order-{order}"


def graph_components(nodes: Sequence[StateId], edge_list: Iterable[Tuple[StateId, StateId]]):
    """Connected components of the undirected view of a transition graph.

    Isolated nodes are reported as their own components, so ``sum(len(c) for c in ...)``
    always equals ``len(nodes)``.
    """
    index = {node: position for position, node in enumerate(nodes)}
    pairs = [(index[a], index[b]) for a, b in edge_list if a in index and b in index]
    raw = connected_components(pairs)
    covered = set().union(*raw) if raw else set()
    components = [set(component) for component in raw]
    components.extend({position} for position in range(len(nodes)) if position not in covered)
    return [
        sorted(component, key=lambda i: str(nodes[i]))
        for component in sorted(
            components, key=lambda c: (-len(c), sorted(map(str, (nodes[i] for i in c))))
        )
    ]
