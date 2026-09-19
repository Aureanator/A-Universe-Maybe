"""Constructive nonincreasing decay witnesses, with bounded plateau exploration.

Search order is an algorithm, not dynamics or a probability measure. Raw labels
are explored; only interior edges change. A closed plateau is a statement about
that reached equal-action component, not all states reachable from the input.
"""

from collections import deque

from .curvature import CurvatureState
from .landscape import curvature_action


def _load(state, labels):
    for edge, label in zip(state.edges, labels):
        state.cx.set_label(*edge, state.elements[label])
    state.labels = list(labels)
    state.flux = [state.face_flux(i) for i in range(len(state.faces))]
    state.energy = sum(f != state.identity for f in state.flux)


def _path(parents, key):
    moves = []
    while parents[key] is not None:
        key, move = parents[key]
        moves.append(move)
    return list(reversed(moves))


def _plateau_exit(state, max_states):
    start = tuple(state.labels)
    parents = {start: None}
    queue = deque([start])
    truncated = False
    proposals = 0
    while queue:
        key = queue.popleft()
        _load(state, key)
        for edge in state.interior_edges:
            for multiplier in range(len(state.elements)):
                if multiplier == state.identity:
                    continue
                new, _, delta = state.proposal(edge, multiplier)
                proposals += 1
                move = {"edge": edge, "multiplier": multiplier, "delta": delta}
                if delta < 0:
                    return "exit", _path(parents, key) + [move], len(parents), proposals
                if delta == 0:
                    nxt = list(key)
                    nxt[edge] = new
                    nxt = tuple(nxt)
                    if nxt not in parents:
                        if len(parents) == max_states:
                            truncated = True
                        else:
                            parents[nxt] = (key, move)
                            queue.append(nxt)
    return ("budget_exhausted" if truncated else "closed_plateau"), [], len(parents), proposals


def decay_certificate(cx, *, max_plateau_states=1000):
    """Return a replayable path to vacuum, or an explicitly limited search result.

At most H(initial) plateau searches occur: each successful one lowers integer H.
Memory and work per plateau are bounded by the state budget and proposal count.
The caller's complex is not mutated. Vacuum means flat curvature, not identity
edge labels; arbitrary fixed boundary conditions may prevent reaching it.
"""
    if not isinstance(max_plateau_states, int) or max_plateau_states < 1:
        raise ValueError("max_plateau_states must be a positive integer")
    state = CurvatureState(cx)
    initial = state.energy
    moves, searches = [], []
    status = "vacuum"
    while state.energy:
        start = tuple(state.labels)
        energy = state.energy
        status, path, count, proposals = _plateau_exit(state, max_plateau_states)
        searches.append({"action": energy, "status": status,
                         "discovered_states": count, "proposals_checked": proposals})
        _load(state, start)
        if status != "exit":
            break
        for move in path:
            proposal = state.proposal(move["edge"], move["multiplier"])
            assert proposal[2] == move["delta"] <= 0
            state.commit(move["edge"], *proposal)
            moves.append(move)
    if state.energy == 0:
        status = "vacuum"
    return {"status": status, "initial_action": initial, "final_action": state.energy,
            "moves": moves, "plateau_searches": searches,
            "max_plateau_states": max_plateau_states}


def verify_decay_certificate(cx, certificate):
    """Independently recompute H and boundary labels, then undo the entire witness.

This verifies the path, not a search's closed-plateau or exhaustion assertion.
Raises ValueError on an invalid witness. Uses full holonomies instead of cached
local action deltas. Returns the forward action sequence for reporting.
"""
    scratch = cx.copy()
    edges = tuple(scratch.edges())
    group = scratch.group
    elements = tuple(group.elements)
    interior = set(CurvatureState(cx).interior_edges)
    boundary = {edge: scratch.label(*edge) for i, edge in enumerate(edges) if i not in interior}
    initial_labels = scratch.labels_snapshot()
    actions = [curvature_action(scratch)]
    if actions[0] != certificate["initial_action"]:
        raise ValueError("initial action mismatch")
    for move in certificate["moves"]:
        ei, mi = move["edge"], move["multiplier"]
        if ei not in interior or not 0 <= mi < len(elements) or elements[mi] == group.identity():
            raise ValueError("move outside permitted proposal set")
        edge = edges[ei]
        scratch.set_label(*edge, group.multiply(scratch.label(*edge), elements[mi]))
        action = curvature_action(scratch)
        if action > actions[-1] or action - actions[-1] != move["delta"]:
            raise ValueError("invalid action change")
        if any(scratch.label(*e) != label for e, label in boundary.items()):
            raise ValueError("boundary changed")
        actions.append(action)
    if actions[-1] != certificate["final_action"]:
        raise ValueError("final action mismatch")
    if certificate["status"] == "vacuum" and actions[-1] != 0:
        raise ValueError("false vacuum claim")
    for move, previous in zip(reversed(certificate["moves"]), reversed(actions[:-1])):
        edge = edges[move["edge"]]
        inverse = group.inverse(elements[move["multiplier"]])
        scratch.set_label(*edge, group.multiply(scratch.label(*edge), inverse))
        if curvature_action(scratch) != previous:
            raise ValueError("inverse action mismatch")
    if scratch.labels_snapshot() != initial_labels:
        raise ValueError("inverse label mismatch")
    return actions
