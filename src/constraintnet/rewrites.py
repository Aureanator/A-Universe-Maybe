"""Constructive connectivity of labels under unrestricted interior-edge rewrites.

For any finite group G, the fixed-boundary label space is G**E_interior. Each
factor's proposal graph is complete: a becomes b by multiplying by a^-1 b.
The product graph is therefore connected. A gauge quotient cannot disconnect a
connected graph. This excludes nonconstant invariants of ALL these moves, not
energetic metastability, and does not apply to a constrained subset of moves.
"""

from .curvature import CurvatureState
from .landscape import curvature_action


def _matched(source, target):
    a, b = CurvatureState(source), CurvatureState(target)
    if (source.vertices() != target.vertices() or a.edges != b.edges or
            a.faces != b.faces or a.tets != b.tets):
        raise ValueError("source and target must use the same labelled complex")
    if (a.elements != b.elements or a.identity != b.identity or
            a.multiply != b.multiply or a.inverse != b.inverse):
        raise ValueError("source and target must use the same group law and ordering")
    interior = set(a.interior_edges)
    if any(x != y for i, (x, y) in enumerate(zip(a.labels, b.labels)) if i not in interior):
        raise ValueError("source and target boundary labels differ")
    return a, b


def boundary_rewrite_certificate(source, target):
    """Join any two fixed-boundary label assignments, allowing action increases.

One move per differing interior edge, using all nonidentity group multipliers.
This is a path-existence construction, not a dynamics or a physical distance.
The recorded peak is a path barrier upper bound, never a minimum-barrier claim.
"""
    state, end = _matched(source, target)
    moves = []
    actions = [state.energy]
    for edge in state.interior_edges:
        if state.labels[edge] == end.labels[edge]:
            continue
        h = state.multiply[state.inverse[state.labels[edge]]][end.labels[edge]]
        proposal = state.proposal(edge, h)
        moves.append({"edge": edge, "multiplier": h, "delta": proposal[2]})
        state.commit(edge, *proposal)
        actions.append(state.energy)
    return {"moves": moves, "actions": actions,
            "peak_above_initial": max(actions) - actions[0]}


def verify_boundary_rewrite_certificate(source, target, certificate):
    """Full-holonomy replay, fixed boundary, exact target labels, and inverse check."""
    initial, end = _matched(source, target)
    cx = source.copy()
    g = cx.group
    interior = set(initial.interior_edges)
    boundary = {e: cx.label(*e) for i, e in enumerate(initial.edges) if i not in interior}
    actions = [curvature_action(cx)]
    for move in certificate["moves"]:
        ei, mi = move["edge"], move["multiplier"]
        if ei not in interior or not 0 <= mi < len(initial.elements) or mi == initial.identity:
            raise ValueError("move outside allowed interior-edge rewrites")
        edge = initial.edges[ei]
        cx.set_label(*edge, g.multiply(cx.label(*edge), initial.elements[mi]))
        action = curvature_action(cx)
        if action - actions[-1] != move["delta"]:
            raise ValueError("action difference mismatch")
        if any(cx.label(*e) != label for e, label in boundary.items()):
            raise ValueError("boundary changed")
        actions.append(action)
    if cx.labels_snapshot() != target.labels_snapshot():
        raise ValueError("path does not reach target labels")
    if actions != certificate["actions"] or max(actions)-actions[0] != certificate["peak_above_initial"]:
        raise ValueError("action trace or peak mismatch")
    for move, previous in zip(reversed(certificate["moves"]), reversed(actions[:-1])):
        edge = initial.edges[move["edge"]]
        h = g.inverse(initial.elements[move["multiplier"]])
        cx.set_label(*edge, g.multiply(cx.label(*edge), h))
        if curvature_action(cx) != previous:
            raise ValueError("inverse action mismatch")
    if cx.labels_snapshot() != source.labels_snapshot():
        raise ValueError("inverse labels mismatch")
    return actions
