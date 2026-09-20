"""P16 bag test: does the current model supply any outward (volume) pressure?

No model change. Whole Kuhn balls, identity boundary. See docs/PREDICTIONS.md P16
and docs/BAG_PICTURE.md. Reproduce: python examples/bag_test.py
"""

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from constraintnet.curvature import CurvatureState
from constraintnet.entropy import enumerate_region_resolutions_slice, interior_vertices
from constraintnet.region import region_from_tets
from constraintnet.seeds import kuhn_ball


def m1_flat_fillings(group, n, node_budget=4_000_000):
    cx = kuhn_ball(group, n=n)
    region = region_from_tets(cx, cx.tetrahedra())
    v_int = len(interior_vertices(cx, region))
    t0 = time.monotonic()
    try:
        sols = enumerate_region_resolutions_slice(cx, region, None, node_budget=node_budget)
    except ValueError as exc:
        return {"group": group, "n": n, "status": "skipped", "reason": str(exc)}
    raw = len(sols)
    order = len(cx.group.elements)
    gauge = order ** v_int
    return {"group": group, "n": n, "status": "exact", "interior_vertices": v_int,
            "interior_edges": len(region.interior_edges()), "raw_flat_fillings": raw,
            "gauge_orbit_size": gauge, "physical_I": raw / gauge,
            "seconds": round(time.monotonic() - t0, 2)}


def m2_lowest_excitations(group, n):
    cx = kuhn_ball(group, n=n)
    st = CurvatureState(cx)
    assert st.energy == 0
    degrees, supports = [], {}
    for e in st.interior_edges:
        for h in range(len(st.elements)):
            if h == st.identity:
                continue
            _, changed, delta = st.proposal(e, h)
            degrees.append(delta)
            supports.setdefault(delta, set()).add(frozenset(changed))
    h_min = min(degrees)
    n_min = degrees.count(h_min)
    return {"group": group, "n": n, "interior_edges": len(st.interior_edges),
            "tets": len(st.tets), "single_edge_excitations": len(degrees),
            "H_values": sorted(set(degrees)), "H_min": h_min, "N_at_H_min": n_min,
            "distinct_supports_at_H_min": len(supports[h_min]),
            "beta_star": math.log(n_min) / h_min}


def main():
    out = {"M1": [], "M2": []}
    for group, n in (("Z3", 1), ("Z3", 2), ("Z3", 3), ("A4", 1), ("A4", 2)):
        row = m1_flat_fillings(group, n)
        print("M1", row, flush=True)
        out["M1"].append(row)
    # Raw enumeration lists every gauge copy: 12**8 = 4.3e8 for A4 n=3 (tried; >25 min).
    out["M1"].append({"group": "A4", "n": 3, "status": "skipped",
                      "reason": "raw enumeration lists 12**8 gauge copies; not run"})
    for group in ("Z3", "A4"):
        for n in range(2, 9):
            row = m2_lowest_excitations(group, n)
            print("M2", row, flush=True)
            out["M2"].append(row)
    path = ROOT / "reference/opus_session/data/bag_test.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
