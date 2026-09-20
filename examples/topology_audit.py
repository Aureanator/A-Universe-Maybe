"""P13: a prescribed linked flux fixture and its permitted rewrite witnesses.

Coordinates are used only to prepare this diagnostic fixture and to measure its
PL embedding. The imported decay search sees only incidence and group labels.
"""

import argparse
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from constraintnet.curvature import CurvatureState
from constraintnet.decay import decay_certificate, verify_decay_certificate
from constraintnet.gauge import gauge_transform
from constraintnet.knots import dual_embed_loop
from constraintnet.linking import linking_number
from constraintnet.seeds import kuhn_ball
from constraintnet.strings import flux_string_components, ordered_loop_tets


def linked_fixture(group="Z3"):
    cx = kuhn_ball(group, n=8)
    g = cx.group
    h = next(x for x in g.elements if g.order_of(x) == 3)
    powers = [g.identity(), h, g.multiply(h, h)]
    # (normal axis, plane, bounds on the other two ascending axes)
    disks = [(2, Q(17,4), ((Q(9,7), Q(37,7)), (Q(9,7), Q(44,7)))),
             (1, Q(13,4), ((Q(23,7), Q(51,7)), (Q(16,7), Q(44,7))))]
    for edge in cx.edges():
        a, b = [cx.vertex(v).metadata["grid"] for v in edge]
        exponent = 0
        for axis, plane, bounds in disks:
            diff = b[axis] - a[axis]
            if diff == 0:
                continue
            t = (plane - a[axis])/diff
            if not 0 < t < 1:
                continue
            others = [i for i in range(3) if i != axis]
            point = [a[i] + t*(b[i]-a[i]) for i in others]
            if any(value in interval for value, interval in zip(point, bounds)):
                raise ValueError("fixture edge meets a disk boundary; ambiguous seed")
            if all(lo < value < hi for value, (lo, hi) in zip(point, bounds)):
                exponent += 1 if diff > 0 else -1
        cx.set_label(*edge, powers[exponent % 3])
    state = CurvatureState(cx)
    assert all(label == state.identity for i, label in enumerate(state.labels)
               if i not in set(state.interior_edges))
    return cx


def embedded_loops(cx):
    def center(simplex):
        return tuple(sum(Q(cx.vertex(v).metadata["grid"][i]) for v in simplex)/len(simplex)
                     for i in range(3))
    result = []
    for comp in flux_string_components(cx):
        if comp.kind != "loop":
            continue
        walk = ordered_loop_tets(cx, comp)
        tets = {tet: center(tet) for tet in walk}
        faces = {face: center(face) for face in comp.faces}
        result.append(dual_embed_loop(tets, walk, faces))
    return result


def support_report(cx):
    components = flux_string_components(cx)
    result = {"kinds": [c.kind for c in components], "lengths": [c.length for c in components]}
    if len(components) == 2 and all(c.kind == "loop" for c in components):
        a, b = embedded_loops(cx)
        # Loop orientation is a deterministic walk, not transported lineage.
        # Only |linking| is compared across states.
        result["absolute_linking"] = abs(linking_number(a, b))
    else:
        result["absolute_linking"] = None
    return result


def audit(group):
    cx = linked_fixture(group)
    initial = support_report(cx)
    print(f"{group} fixture: {initial}", flush=True)
    if initial["kinds"] != ["loop", "loop"] or initial["absolute_linking"] != 1:
        return {"group": group, "n": 8, "status": "fixture_failed", "initial_support": initial}
    cert = decay_certificate(cx, max_plateau_states=32)
    actions = verify_decay_certificate(cx, cert)
    state = CurvatureState(cx)
    snapshots = [dict(step=0, action=actions[0], **initial)]
    for i, move in enumerate(cert["moves"], 1):
        state.commit(move["edge"], *state.proposal(move["edge"], move["multiplier"]))
        snapshots.append(dict(step=i, action=actions[i], **support_report(state.cx)))
    original = CurvatureState(cx)
    g = cx.group
    lambdas = {v: g.elements[(7*v+1) % len(g.elements)] for v in cx.vertices()}
    gauged = cx.copy()
    gauge_transform(gauged, lambdas)
    assert support_report(gauged) == initial
    transported = dict(cert, moves=[])
    for move in cert["moves"]:
        target = original.edges[move["edge"]][1]
        h = g.conjugate(lambdas[target], original.elements[move["multiplier"]])
        transported["moves"].append(dict(move, multiplier=original.index[h]))
    assert verify_decay_certificate(gauged, transported) == actions
    report = {"group": group, "n": 8, "fixture": "two_rectangular_disks_P13",
              "initial_nonidentity_labels": [[list(edge), label] for edge, label in
                  zip(original.edges, original.labels) if label != original.identity],
              "group_elements": original.elements, "certificate": cert,
              "snapshots": snapshots, "gauge_transport_verified": True,
              "boundary_and_inverse_verified": True}
    print(f"{group}: {cert['status']}, {len(cert['moves'])} moves, H={actions[0]}->{actions[-1]}", flush=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-only", action="store_true")
    args = parser.parse_args()
    if args.fixture_only:
        for group in ("Z3", "A4"):
            print(group, support_report(linked_fixture(group)), flush=True)
        return
    output = ROOT / "reference/astra_session/data/topology_audit.json"
    reports = []
    started = time.monotonic()
    for group in ("Z3", "A4"):
        reports.append(audit(group))
        output.write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
        print(f"elapsed={time.monotonic()-started:.1f}s", flush=True)


if __name__ == "__main__":
    main()
