"""Exact nonincreasing ordering of a fixed set of distinct-edge rewrites.

Subset states suffice because updates of different edge variables commute. This
does NOT commute the non-abelian factors inside a face holonomy. Each affected
triangle is evaluated by its ordered group product for all (at most eight)
local subsets. No coordinate, randomness, or physical scheduler is introduced.

Failure with exhaustive status excludes only permutations of these supplied
moves, not arbitrary paths between the endpoints. Budget exhaustion is distinct.
"""

from collections import deque

from .curvature import CurvatureState


def nonincreasing_order(cx, moves, *, max_states=65536):
    """Return an exact permitted ordering or a scoped negative/inconclusive result.

Each input move supplies integer edge/multiplier indices in CurvatureState order.
Original delta fields are ignored: deltas must be recomputed in the new order.
The input complex is not mutated. The state budget counts discovered subsets,
including the empty subset and goal. There are exactly 2**len(moves) possible
subset assignments (all supplied multipliers must be nonidentity).
"""
    if not isinstance(max_states, int) or max_states < 1:
        raise ValueError("max_states must be a positive integer")
    state = CurvatureState(cx)
    moves = list(moves)
    interior = set(state.interior_edges)
    selected = {}
    for i, move in enumerate(moves):
        edge, multiplier = move["edge"], move["multiplier"]
        if edge not in interior or not 0 <= multiplier < len(state.elements) or multiplier == state.identity:
            raise ValueError("move outside allowed interior-edge proposal set")
        if edge in selected:
            raise ValueError("subset ordering requires distinct edges")
        selected[edge] = i
    after = {edge: state.multiply[state.labels[edge]][moves[i]["multiplier"]]
             for edge, i in selected.items()}
    affected = sorted({fi for edge in selected for fi in state.edge_faces[edge]})
    constant = state.energy - sum(state.flux[fi] != state.identity for fi in affected)
    factors = []
    for fi in affected:
        edges = state.face_edges[fi]
        bits = [selected[e] for e in edges if e in selected]
        positions = {bit: i for i, bit in enumerate(bits)}
        table = []
        for local in range(1 << len(bits)):
            a, b, c = [after[e] if e in selected and local & (1 << positions[selected[e]])
                       else state.labels[e] for e in edges]
            flux = state.multiply[state.multiply[a][b]][state.inverse[c]]
            table.append(int(flux != state.identity))
        factors.append((bits, table))
    energies = {}

    def energy(mask):
        if mask not in energies:
            energies[mask] = constant + sum(
                table[sum(((mask >> bit) & 1) << j for j, bit in enumerate(bits))]
                for bits, table in factors)
        return energies[mask]

    goal = (1 << len(moves)) - 1
    parents = {0: None}
    queue = deque([0])
    truncated = False
    checked = 0
    while queue and goal not in parents:
        mask = queue.popleft()
        for i in range(len(moves)):
            if mask & (1 << i):
                continue
            nxt = mask | (1 << i)
            checked += 1
            if energy(nxt) > energy(mask) or nxt in parents:
                continue
            if len(parents) == max_states:
                truncated = True
                continue
            parents[nxt] = (mask, i)
            queue.append(nxt)
            if nxt == goal:
                break
    order, result = [], []
    if goal in parents:
        mask = goal
        while mask:
            previous, i = parents[mask]
            order.append(i)
            result.append({"edge": moves[i]["edge"], "multiplier": moves[i]["multiplier"],
                           "delta": energy(mask) - energy(previous)})
            mask = previous
        order.reverse()
        result.reverse()
        status = "reordered"
    else:
        status = "budget_exhausted" if truncated else "no_nonincreasing_order"
    return {"status": status, "moves": result, "order": order,
            "initial_action": energy(0), "target_action": energy(goal),
            "discovered_states": len(parents), "energy_evaluations": len(energies),
            "transitions_checked": checked, "subset_states": 1 << len(moves),
            "max_states": max_states}
