"""P10: replay every screened branch and search for exact decay witnesses."""

import gzip
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from constraintnet.curvature import CurvatureState, SupportLineage
from constraintnet.kinetics import CurvatureDriver
from particle_search import initial_complex


def audit_branch(state, branch, step):
    support = branch["faces"]
    generators = [i for i in range(len(state.elements)) if i != state.identity]
    touching = {ei for fi in support for ei in state.face_edges[fi]} & set(state.interior_edges)
    downhill, erasures, witnesses = 0, 0, []
    for edge in sorted(touching):
        for multiplier in generators:
            new, changed, delta = state.proposal(edge, multiplier)
            downhill += delta < 0
            erase = all(changed.get(fi, state.flux[fi]) == state.identity for fi in support)
            erase &= all(value == state.flux[fi] for fi, value in changed.items() if fi not in support)
            if erase:
                erasures += 1
                witnesses.append({"edge": edge, "multiplier": multiplier, "delta": delta})
    all_proposals = len(state.interior_edges) * len(generators)
    return {"branch": branch["id"], "step": step, "faces": len(support),
            "support_changes": branch["support_changes"],
            "age_in_proposals": step - branch["born"],
            "age_per_specific_proposal": (step - branch["born"]) / all_proposals,
            "local_downhill_proposals": downhill, "one_move_erasures": erasures,
            "erase_probability_per_proposal": erasures / all_proposals,
            "witnesses": witnesses}


def main():
    out = Path("out/particle_search")
    runs = json.loads((out / "runs.json").read_text())
    audits = []
    for run in runs:
        candidates = run["lineage"]["candidate_screen_passes"]
        if not candidates:
            continue
        schedule = {}
        for candidate in candidates:
            at = candidate["born"] + min(1000, candidate["lifetime"] - 1)
            schedule.setdefault(at, []).append(candidate["id"])
        cx = initial_complex(run["group"], run["n"], run["start"], run["seed"])
        state = CurvatureState(cx)
        tracker = SupportLineage(state.components(), len(state.tets))
        with gzip.open(out / f"{run['id']}.events.jsonl.gz", "rt") as trace:
            header = json.loads(next(trace))
            assert header["initial_labels"] == state.labels
            for line in trace:
                event = json.loads(line)
                step = event["step"]
                if event["accepted"]:
                    proposal = state.proposal(event["edge"], event["multiplier"])
                    assert proposal[2] == event["delta_proposed"]
                    state.commit(event["edge"], *proposal)
                    tracker.advance(state.components(), step)
                assert state.energy == event["action"]
                for ident in schedule.get(step, []):
                    report = audit_branch(state, tracker.live[ident], step)
                    audits.append({"run": run["id"], **report})
        assert state.energy == run["final_action"]
    extensions = []
    for run in runs:
        if run["beta"] != "inf" or run["final_action"] == 0:
            continue
        cx = initial_complex(run["group"], run["n"], run["start"], run["seed"])
        driver = CurvatureDriver(cx, beta=math.inf, seed=run["seed"])
        first_vacuum = None
        with gzip.open(out / f"{run['id']}.extension.jsonl.gz", "wt") as trace:
            for step in range(1, 200_001):
                driver.advance()
                record = driver.last_event
                if step == run["steps"]:
                    assert driver.state.energy == run["final_action"]
                if step > run["steps"]:
                    trace.write(json.dumps(record, separators=(",", ":")) + "\n")
                if driver.state.energy == 0 and first_vacuum is None:
                    first_vacuum = step
                # At infinite beta the vacuum cannot leave; the stopping condition
                # follows from positive action cost of every interior edge change.
                if first_vacuum is not None:
                    break
        extensions.append({"run": run["id"], "final_action": driver.state.energy,
                           "proposals_run": driver.step, "first_vacuum_step": first_vacuum,
                           "planned_horizon": 200_000})
    result = {"branches_audited": len(audits),
              "one_step_erasable": sum(a["one_move_erasures"] > 0 for a in audits),
              "with_local_downhill": sum(a["local_downhill_proposals"] > 0 for a in audits),
              "audits": audits, "extensions": extensions}
    assert len(audits) == sum(len(r["lineage"]["candidate_screen_passes"]) for r in runs)
    (out / "candidate_audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "audits"}, indent=2))


if __name__ == "__main__":
    main()
