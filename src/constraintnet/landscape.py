"""Exact small-system curvature-action landscapes; no stochastic dynamics.

H counts nonidentity face holonomies. It is an explicit candidate reduction
action, not derived physical energy. All nonidentity edge multipliers are allowed,
including on tree edges; gauge fixing and orbit projection are bookkeeping.
No conserved boundary is imposed here: this is the unfrozen landscape control.
"""

from collections import Counter, deque
from dataclasses import dataclass
import itertools

from .complex import spanning_tree
from .gauge import canonical_config, gauge_fix_spanning_tree
from .holonomy import triangle_holonomy


def curvature_action(cx):
    """Gauge-invariant, dimensionless count of curved faces."""
    return sum(triangle_holonomy(cx, f) != cx.group.identity() for f in cx.faces())


@dataclass
class Landscape:
    free_edges: tuple
    energy: dict
    adjacency: dict
    orbit_sizes: dict
    raw_count: int
    proposal_count: int

    def plateaus(self):
        """Equal-action components and their downhill exits, including singleton nodes."""
        unseen = set(self.energy)
        result = []
        while unseen:
            start = min(unseen)
            component = {start}
            queue = [start]
            unseen.remove(start)
            for state in queue:
                for nxt in self.adjacency[state]:
                    if nxt in unseen and self.energy[nxt] == self.energy[state]:
                        unseen.remove(nxt)
                        component.add(nxt)
                        queue.append(nxt)
            exits = {nxt for state in component for nxt in self.adjacency[state]
                     if self.energy[nxt] < self.energy[state]}
            result.append({"energy": self.energy[start], "states": frozenset(component),
                           "downhill_exits": frozenset(exits)})
        return sorted(result, key=lambda p: (p["energy"], min(p["states"])))

    def nonincreasing_distances(self, target_energy=0):
        """Shortest nonincreasing path lengths to a target-action state; missing = no path."""
        distance = {s: 0 for s, energy in self.energy.items() if energy == target_energy}
        queue = deque(sorted(distance))
        while queue:
            state = queue.popleft()
            for predecessor in sorted(self.adjacency[state]):
                if predecessor not in distance and self.energy[predecessor] >= self.energy[state]:
                    distance[predecessor] = distance[state] + 1
                    queue.append(predecessor)
        return distance

    def summary(self):
        plateaus = self.plateaus()
        distances = self.nonincreasing_distances()
        return {
            "raw_states": self.raw_count,
            "physical_states": len(self.energy),
            "proposals_enumerated": self.proposal_count,
            "action_histogram_physical": dict(sorted(Counter(self.energy.values()).items())),
            "plateaus": [{"action": p["energy"], "physical_states": len(p["states"]),
                          "downhill_exit_states": len(p["downhill_exits"])} for p in plateaus],
            "nonvacuum_closed_plateaus": sum(p["energy"] > 0 and not p["downhill_exits"]
                                            for p in plateaus),
            "states_with_nonincreasing_vacuum_path": len(distances),
            "max_shortest_nonincreasing_vacuum_path": max(distances.values(), default=None),
        }


def enumerate_landscape(template, *, max_proposals=2_000_000):
    """Exhaust all raw tree-slice states and physical edge moves, then quotient.

    Budget is checked before enumeration. The template is not mutated. Inputs
    must have a connected 1-skeleton. Adjacency is unweighted existence of a move;
    it is not a stochastic transition matrix or an equal-orbit probability prior.
    """
    edges = template.edges()
    if not edges:
        raise ValueError("landscape needs a connected complex with edges")
    tree, _ = spanning_tree(edges)
    if len(tree) != len(template.vertices()) - 1:
        raise ValueError("landscape needs a connected 1-skeleton")
    free = tuple(e for e in edges if e not in set(tree))
    group = template.group
    elements = tuple(group.elements)
    raw_count = len(elements) ** len(free)
    proposal_count = raw_count * len(edges) * (len(elements) - 1)
    if proposal_count > max_proposals:
        raise ValueError(f"landscape requires {proposal_count} proposals > {max_proposals}")
    states = list(itertools.product(elements, repeat=len(free)))
    canonical = {s: canonical_config(s, group) for s in states}
    orbit_sizes = Counter(canonical.values())
    energy, adjacency = {}, {rep: set() for rep in orbit_sizes}
    scratch = template.copy()
    identity = group.identity()
    generators = [g for g in elements if g != identity]
    for state in states:
        labels = {edge: identity for edge in edges}
        labels.update(zip(free, state))
        scratch._labels = dict(labels)
        rep = canonical[state]
        value = curvature_action(scratch)
        if rep in energy and energy[rep] != value:
            raise AssertionError("action changed under gauge equivalence")
        energy[rep] = value
        for edge in edges:
            for multiplier in generators:
                scratch._labels = dict(labels)
                scratch.set_label(*edge, group.multiply(labels[edge], multiplier))
                gauge_fix_spanning_tree(scratch, tree=tree)
                successor = tuple(scratch.label(*e) for e in free)
                adjacency[rep].add(canonical[successor])
    return Landscape(free, energy, adjacency, dict(orbit_sizes), raw_count, proposal_count)
