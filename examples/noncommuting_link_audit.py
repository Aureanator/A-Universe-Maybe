"""P15: linked flux loops whose fluxes do not commute (full A4).

Coordinates prepare the fixture and measure its embedding only; searches read
incidence and group labels. Fixtures are PREPARED, not emergent. Search order
is an algorithm, not time. See docs/PREDICTIONS.md P15.
Reproduce: python examples/noncommuting_link_audit.py --controls --census  (~40 min, 1 core)
"""

import argparse
from fractions import Fraction as Q
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from topology_audit import ROOT, support_report
from topology_rewrite_audit import gauge_verify
from constraintnet.curvature import CurvatureState
from constraintnet.decay import decay_certificate, verify_decay_certificate
from constraintnet.rewrites import boundary_rewrite_certificate, verify_boundary_rewrite_certificate
from constraintnet.seeds import kuhn_ball

DISKS = [(2, Q(17, 4), ((Q(9, 7), Q(37, 7)), (Q(9, 7), Q(44, 7)))),
         (1, Q(13, 4), ((Q(23, 7), Q(51, 7)), (Q(16, 7), Q(44, 7))))]


def arm_elements(g, arm):
    """Deterministic, declared choice of the two disk elements (first in element order)."""
    order3 = [x for x in g.elements if g.order_of(x) == 3]
    inv = [x for x in g.elements if g.order_of(x) == 2]
    h = order3[0]                                    # the P13 element
    comm = lambda x, y: g.multiply(x, y) == g.multiply(y, x)
    if arm == "C0":
        return h, h
    if arm == "C1":
        return inv[0], inv[1]
    if arm == "N1":
        return h, next(x for x in order3 if not comm(h, x))
    if arm == "N2":
        return inv[0], h
    raise ValueError(arm)


def linked_fixture_ab(arm, n=8, tie="disk1_first", ties=None):
    """tie: order of factors when an edge meets both disks at the same point
    (i.e. passes through their intersection line). Declared amendment, P15."""
    cx = kuhn_ball("A4", n=n)
    g = cx.group
    fluxes = arm_elements(g, arm)
    for edge in cx.edges():
        a, b = [cx.vertex(v).metadata["grid"] for v in edge]
        hits = []
        for (axis, plane, bounds), x in zip(DISKS, fluxes):
            diff = b[axis] - a[axis]
            if diff == 0:
                continue
            t = (plane - a[axis]) / diff
            if not 0 < t < 1:
                continue
            others = [i for i in range(3) if i != axis]
            point = [a[i] + t * (b[i] - a[i]) for i in others]
            if any(value in interval for value, interval in zip(point, bounds)):
                raise ValueError("fixture edge meets a disk boundary; ambiguous seed")
            if all(lo < value < hi for value, (lo, hi) in zip(point, bounds)):
                hits.append((t, x if diff > 0 else g.inverse(x)))
        if len({t for t, _ in hits}) != len(hits):
            if ties is not None:
                ties.append(tuple(edge))
            if tie == "disk2_first":
                hits.reverse()
        label = g.identity()
        for _, x in sorted(hits, key=lambda h: h[0]):
            label = g.multiply(label, x)
        cx.set_label(*edge, label)
    state = CurvatureState(cx)
    interior = set(state.interior_edges)
    assert all(l == state.identity for i, l in enumerate(state.labels) if i not in interior)
    return cx


def class_name(g, x):
    o = g.order_of(x)
    return {1: "e", 2: "V4"}.get(o, "C3") if o != 3 else ("C3a" if x in g.conjugacy_class(
        next(y for y in g.elements if g.order_of(y) == 3)) else "C3b")


def component_flux_classes(state):
    g = state.cx.group
    out = []
    for comp in state.components():
        classes = {}
        for fi in comp["faces"]:
            c = class_name(g, state.elements[state.flux[fi]])
            classes[c] = classes.get(c, 0) + 1
        out.append({"kind": comp["kind"], "faces": len(comp["faces"]),
                    "flux_classes": dict(sorted(classes.items()))})
    return sorted(out, key=lambda c: -c["faces"])


def meridian_check(state):
    """Based face holonomies (tree path from vertex 0) per two-loop component.

    For a Hopf-linked pair, pi_1 of the complement is Z^2: every based meridian
    of one loop should be ONE element, commuting with the other's. Reported only.
    """
    cx, g = state.cx, state.cx.group
    parent = {0: None}
    order = [0]
    adj = {}
    for a, b in cx.edges():
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    for v in order:
        for w in sorted(adj[v]):
            if w not in parent:
                parent[w] = v
                order.append(w)

    def path(v):  # holonomy from 0 to v along tree
        chain = []
        while parent[v] is not None:
            chain.append((parent[v], v))
            v = parent[v]
        x = g.identity()
        for a, b in reversed(chain):
            x = g.multiply(x, cx.label(a, b) if a < b else g.inverse(cx.label(b, a)))
        return x
    comps = state.components()
    based = []
    for comp in comps:
        vals = set()
        for fi in comp["faces"]:
            i = state.faces[fi][0]
            p = path(i)
            vals.add(g.multiply(g.multiply(p, state.elements[state.flux[fi]]), g.inverse(p)))
        based.append(vals)
    commute = all(g.multiply(x, y) == g.multiply(y, x) for x in based[0] for y in based[1]) \
        if len(based) == 2 else None
    return {"distinct_based_meridians": [len(v) for v in based], "all_commute": commute}


def fixture_report(arm):
    cx = linked_fixture_ab(arm)
    g = cx.group
    a, b = arm_elements(g, arm)
    state = CurvatureState(cx)
    rep = {"arm": arm, "a": a, "b": b, "commute": g.multiply(a, b) == g.multiply(b, a),
           "H": state.energy, "components": component_flux_classes(state),
           **support_report(cx)}
    if rep["kinds"] == ["loop", "loop"]:
        rep["meridians"] = meridian_check(state)
    return rep




def ordered_erasure(cx, *, max_states=200000):
    """Order the fixed per-edge 'set to identity' moves; nonincreasing if possible.

    Moves act on distinct edges, so the final state is order independent. Phase 1:
    greedy (most negative delta first, then zero; lowest index on ties). Phase 2,
    only if greedy gets stuck: depth-first search over subsets using only
    nonincreasing moves, with a visited-subset budget. Phase 3, if both fail:
    report the greedy path that allows the least uphill step when stuck. Its
    peak is an UPPER bound on this move set's barrier, not a minimal barrier.
    """
    target = kuhn_ball(cx.group, n=8)
    moves = boundary_rewrite_certificate(cx, target)["moves"]
    base = CurvatureState(cx)

    def greedy(allow_uphill):
        state = CurvatureState(cx)
        left = list(range(len(moves)))
        path, actions = [], [state.energy]
        while left:
            best = None
            for i in left:
                d = state.proposal(moves[i]["edge"], moves[i]["multiplier"])[2]
                if best is None or d < best[0]:
                    best = (d, i)
            if best[0] > 0 and not allow_uphill:
                return None, len(path)
            i = best[1]
            p = state.proposal(moves[i]["edge"], moves[i]["multiplier"])
            state.commit(moves[i]["edge"], *p)
            left.remove(i)
            path.append({"edge": moves[i]["edge"], "multiplier": moves[i]["multiplier"], "delta": p[2]})
            actions.append(state.energy)
        return path, actions

    path, info = greedy(False)
    if path is not None:
        return {"status": "nonincreasing", "method": "greedy", "moves": path,
                "peak_above_initial": 0}
    stuck_at = info
    # Phase 2: DFS over nonincreasing subsets.
    state = CurvatureState(cx)
    visited = set()
    stack_path = []
    found = [None]
    budget = [max_states]

    def dfs(mask):
        if found[0] is not None or budget[0] <= 0:
            return
        if mask == (1 << len(moves)) - 1:
            found[0] = list(stack_path)
            return
        cands = []
        for i in range(len(moves)):
            if not mask >> i & 1:
                d = state.proposal(moves[i]["edge"], moves[i]["multiplier"])[2]
                if d <= 0:
                    cands.append((d, i))
        for d, i in sorted(cands):
            nxt = mask | (1 << i)
            if nxt in visited:
                continue
            visited.add(nxt)
            budget[0] -= 1
            e, m = moves[i]["edge"], moves[i]["multiplier"]
            old = state.labels[e]
            p = state.proposal(e, m)
            state.commit(e, *p)
            stack_path.append({"edge": e, "multiplier": m, "delta": p[2]})
            dfs(nxt)
            stack_path.pop()
            q = state.proposal(e, state.inverse[m])
            state.commit(e, *q)
            assert state.labels[e] == old
            if found[0] is not None or budget[0] <= 0:
                return
    sys.setrecursionlimit(10000)
    dfs(0)
    if found[0] is not None:
        return {"status": "nonincreasing", "method": "dfs", "moves": found[0],
                "greedy_stuck_after": stuck_at, "dfs_states": max_states - budget[0],
                "peak_above_initial": 0}
    path, actions = greedy(True)
    return {"status": "budget_exhausted" if budget[0] <= 0 else "no_nonincreasing_order",
            "method": "greedy_min_uphill", "moves": path, "greedy_stuck_after": stuck_at,
            "dfs_states": max_states - budget[0],
            "peak_above_initial": max(actions) - actions[0],
            "uphill_steps": sum(m["delta"] > 0 for m in path)}


def verify_path(cx, moves):
    """Full-holonomy replay, boundary, inverse and gauge-transported checks."""
    target = cx.copy()
    st = CurvatureState(target)
    for m in moves:
        st.commit(m["edge"], *st.proposal(m["edge"], m["multiplier"]))
    end = st.cx
    state = CurvatureState(cx)
    actions = [state.energy]
    for m in moves:
        state.commit(m["edge"], *state.proposal(m["edge"], m["multiplier"]))
        actions.append(state.energy)
    cert = {"moves": moves, "actions": actions, "peak_above_initial": max(actions) - actions[0]}
    verify_boundary_rewrite_certificate(cx, end, cert)
    gauge_verify(cx, end, cert)
    if cert["peak_above_initial"] == 0 and actions[-1] == 0:
        verify_decay_certificate(cx, {"status": "vacuum", "initial_action": actions[0],
                                       "final_action": 0, "moves": moves})
    return actions


def snapshots(cx, moves):
    state = CurvatureState(cx)
    out = [dict(step=0, H=state.energy, components=component_flux_classes(state))]
    prev = [c["kind"] for c in out[0]["components"]]
    for i, m in enumerate(moves, 1):
        state.commit(m["edge"], *state.proposal(m["edge"], m["multiplier"]))
        comps = component_flux_classes(state)
        kinds = [c["kind"] for c in comps]
        if kinds != prev:
            rec = dict(step=i, H=state.energy, components=comps)
            if kinds == ["loop", "loop"]:
                rec.update(support_report(state.cx))
                rec["meridians"] = meridian_check(state)
            out.append(rec)
            prev = kinds
    return out


def run_arm(arm, tie="disk1_first"):
    t0 = time.monotonic()
    ties = []
    cx = linked_fixture_ab(arm, tie=tie, ties=ties)
    rep = {"arm": arm, "tie_convention": tie, "tie_edges": ties}
    rep["fixture"] = {k: v for k, v in fixture_report_cx(cx, arm).items()}
    for budget in (32, 256):
        cert = decay_certificate(cx, max_plateau_states=budget)
        actions = verify_decay_certificate(cx, cert)
        rep[f"plateau_search_{budget}"] = {
            "status": cert["status"], "moves": len(cert["moves"]),
            "actions_head": actions[:12], "final_action": actions[-1],
            "plateau_searches": cert["plateau_searches"][-3:]}
        print(arm, tie, "plateau", budget, cert["status"], actions[0], "->", actions[-1], flush=True)
        if cert["status"] == "vacuum":
            break
    er = ordered_erasure(cx)
    actions = verify_path(cx, er["moves"])
    er["actions"] = actions
    er["topology_changes"] = snapshots(cx, er["moves"])
    rep["ordered_erasure"] = er
    print(arm, tie, "ordered erasure", er["status"], er["method"], "peak+", er["peak_above_initial"],
          f"{time.monotonic()-t0:.0f}s", flush=True)
    return rep


def fixture_report_cx(cx, arm):
    g = cx.group
    a, b = arm_elements(g, arm)
    state = CurvatureState(cx)
    rep = {"a": a, "b": b, "commute": g.multiply(a, b) == g.multiply(b, a),
           "H": state.energy, "components": component_flux_classes(state), **support_report(cx)}
    if rep["kinds"] == ["loop", "loop"]:
        rep["meridians"] = meridian_check(state)
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arms", default="C0,C1,N1,N2")
    ap.add_argument("--controls", action="store_true", help="also run disk2_first ties for N arms")
    ap.add_argument("--out", default=str(ROOT / "reference/opus_session/data/noncommuting_link_audit.json"))
    ap.add_argument("--census", action="store_true", help="also run the one-edge census (disk1 ties)")
    args = ap.parse_args()
    jobs = [(a, "disk1_first") for a in args.arms.split(",") if a]
    if args.controls:
        jobs += [(a, "disk2_first") for a in ("N1", "N2")]
    out = []
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    for arm, tie in jobs:
        rep = run_arm(arm, tie)
        if args.census and tie == "disk1_first" and arm != "C0":
            rep["one_edge_census"] = one_edge_census(arm)
        out.append(rep)
        Path(args.out).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")


def one_edge_census(arm, tie="disk1_first"):
    """P15(i): every single interior-edge proposal from the prepared fixture."""
    from collections import Counter
    from topology_rewrite_audit import domain
    cx = linked_fixture_ab(arm, tie=tie)
    state = CurvatureState(cx)
    base = (tuple(state.labels), tuple(state.flux), state.energy)
    census = Counter()
    for edge in state.interior_edges:
        for h in range(len(state.elements)):
            if h == state.identity:
                continue
            p = state.proposal(edge, h)
            state.commit(edge, *p)
            census[("nonincreasing" if p[2] <= 0 else "uphill") + ":" + domain(state)] += 1
            state.commit(edge, *state.proposal(edge, state.inverse[h]))
    assert (tuple(state.labels), tuple(state.flux), state.energy) == base
    return dict(sorted(census.items()))


if __name__ == "__main__":
    main()
