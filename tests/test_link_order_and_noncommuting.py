"""P14 archived nonincreasing erasure replay; P15 non-commuting linked fixtures."""

import json
from pathlib import Path

import pytest

from examples.topology_audit import linked_fixture
from examples.noncommuting_link_audit import (arm_elements, linked_fixture_ab,
                                               fixture_report_cx, meridian_check)
from constraintnet.curvature import CurvatureState
from constraintnet.decay import verify_decay_certificate

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.slow
@pytest.mark.parametrize("group", ["Z3", "A4"])
def test_p14_archived_erasure_is_nonincreasing_to_vacuum(group):
    reports = json.loads((ROOT / "reference/astra_session/data/topology_decay_order.json")
                         .read_text(encoding="utf-8"))
    report = next(r for r in reports if r["group"] == group)
    assert report["window_search"]["status"] == "reordered"
    actions = verify_decay_certificate(linked_fixture(group), report["certificate"])
    assert actions[0] == 98 and actions[-1] == 0 and len(actions) == 141
    assert all(b <= a for a, b in zip(actions, actions[1:]))


def test_p15_c0_reproduces_p13_labels():
    assert linked_fixture_ab("C0").labels_snapshot() == linked_fixture("A4").labels_snapshot()


@pytest.mark.slow
@pytest.mark.parametrize("arm", ["C1", "N1", "N2"])
def test_p15_commutator_decides_tether(arm):
    cx = linked_fixture_ab(arm)
    g = cx.group
    a, b = arm_elements(g, arm)
    rep = fixture_report_cx(cx, arm)
    if g.multiply(a, b) == g.multiply(b, a):
        assert rep["kinds"] == ["loop", "loop"] and rep["absolute_linking"] == 1
        assert rep["H"] == 98 and rep["meridians"]["all_commute"]
    else:
        # Hopf complement has pi_1 = Z^2: non-commuting meridians force extra flux.
        assert rep["kinds"] == ["sheet/junction"] and rep["H"] == 103
        (comp,) = rep["components"]
        assert comp["flux_classes"].get("V4", 0) >= 5


@pytest.mark.parametrize("arm", ["N1", "N2"])
def test_p15_tie_convention_changes_tether_length_only(arm):
    # 4 edges pass exactly through the disk-intersection line (declared amendment).
    ties = []
    a = CurvatureState(linked_fixture_ab(arm, tie="disk1_first", ties=ties))
    b = CurvatureState(linked_fixture_ab(arm, tie="disk2_first"))
    assert len(ties) == 4
    assert (a.energy, b.energy) == (103, 104)
    assert len(a.components()) == len(b.components()) == 1


@pytest.mark.slow
def test_p15_archived_paths_are_nonincreasing_erasures():
    data = json.loads((ROOT / "reference/opus_session/data/noncommuting_link_audit.json")
                      .read_text(encoding="utf-8"))
    assert len(data) == 6
    for rep in data:
        cx = linked_fixture_ab(rep["arm"], tie=rep["tie_convention"])
        er = rep["ordered_erasure"]
        cert = {"status": "vacuum", "initial_action": er["actions"][0], "final_action": 0,
                "moves": er["moves"]}
        actions = verify_decay_certificate(cx, cert)
        assert actions == er["actions"] and er["peak_above_initial"] == 0
