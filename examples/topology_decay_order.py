"""P14: exact reordering control for the sole uphill step in the P13b path."""

import json
import time

from topology_audit import ROOT, linked_fixture
from topology_rewrite_audit import gauge_verify
from constraintnet.curvature import CurvatureState
from constraintnet.decay import verify_decay_certificate
from constraintnet.path_order import nonincreasing_order
from constraintnet.seeds import kuhn_ball


def main():
    source = ROOT / "reference/astra_session/data/topology_rewrite_audit.json"
    output = ROOT / "reference/astra_session/data/topology_decay_order.json"
    reports = []
    started = time.monotonic()
    for record in json.loads(source.read_text(encoding="utf-8")):
        group = record["group"]
        cx = linked_fixture(group)
        original = record["unrestricted_erasure"]
        moves = original["moves"]
        state = CurvatureState(cx)
        for move in moves[:32]:
            state.commit(move["edge"], *state.proposal(move["edge"], move["multiplier"]))
        assert state.energy == original["actions"][32]
        window = nonincreasing_order(state.cx, moves[32:48], max_states=65536)
        print(f"{group}: {window['status']}, subsets={window['discovered_states']}, order={window['order']}", flush=True)
        report = {"group": group, "n": 8, "source": str(source.relative_to(ROOT)),
                  "window_steps_inclusive": [33,48], "window_search": window}
        if window["status"] == "reordered":
            expected = CurvatureState(state.cx)
            for move in moves[32:48]:
                expected.commit(move["edge"], *expected.proposal(move["edge"], move["multiplier"]))
            for move in window["moves"]:
                state.commit(move["edge"], *state.proposal(move["edge"], move["multiplier"]))
            assert state.labels == expected.labels and state.flux == expected.flux
            new_moves = moves[:32] + window["moves"] + moves[48:]
            cert = {"status": "vacuum", "initial_action": original["actions"][0],
                    "final_action": 0, "moves": new_moves}
            actions = verify_decay_certificate(cx, cert)
            gauge_verify(cx, kuhn_ball(group, n=8),
                         {"moves": new_moves, "actions": actions, "peak_above_initial": 0})
            report.update(certificate=cert, actions=actions,
                          gauge_transport_verified=True, boundary_and_inverse_verified=True)
            print(f"{group}: complete {len(new_moves)}-move nonincreasing decay, "
                  f"H={actions[0]}->{actions[-1]}", flush=True)
        reports.append(report)
        output.write_text(json.dumps(reports, indent=2) + "\n", encoding="utf-8")
        print(f"elapsed={time.monotonic()-started:.1f}s", flush=True)


if __name__ == "__main__":
    main()
