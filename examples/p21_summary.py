"""Summarise P21 JSON into the registered readouts. Reproduce: python examples/p21_summary.py"""
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "reference/opus_session/data"


def rows(geom):
    d = json.loads((D / f"p21_{geom}.json").read_text())
    out = []
    c0 = d["runs"][0]
    for r in d["runs"]:
        t = np.array(r["t"])
        x = {"arm": r["arm"], "lE": r["lam_E"], "lB": r["lam_B"],
             "vac_e_overlap": round(r["vac_overlap_with_identity"], 4),
             "max_norm_dev": float(np.max(np.abs(r["norm_dev"]))),
             "near_avg": r["near_avg_second_half"], "near_ratio_C0": r["near_avg_second_half"] / c0["near_avg_second_half"],
             "1-Pvac@10": 1 - r["P_vac"][list(t).index(10)], "1-Pvac@T": 1 - r["P_vac"][-1],
             "Erec_max": max(r["E_rec"]), "Erec_avg2": float(np.mean(r["E_rec"][len(t) // 2:])),
             "Erec_frac_inf": (float(np.mean(r["E_rec"][len(t) // 2:])) / r["E_rec_infinite_T"]) if r["E_rec_infinite_T"] else 0.0,
             "purity": r["purity"], "reverse_err": r.get("reverse_err"), "vac_stat_err": r["vac_stationarity_err"]}
        if r["fid_C0"]:
            x["fid@10"] = r["fid_C0"][1]; x["fid@T"] = r["fid_C0"][-1]; x["fid_min"] = min(r["fid_C0"])
        if r["df_overlap"]:
            x["df@T"] = r["df_overlap"][-1]; x["df_avg2"] = float(np.mean(r["df_overlap"][len(t) // 2:]))
            x["df_leak@50"] = 1 - r["df_overlap"][list(t).index(50)]
        out.append(x)
    return out


if __name__ == "__main__":
    for g in ("G1", "G2", "G3"):
        if (D / f"p21_{g}.json").exists():
            print("==", g)
            for x in rows(g):
                print({k: (round(v, 6) if isinstance(v, float) else v) for k, v in x.items()})
