"""Figure for P21 (out/p21_quantum_record.png). Reproduce: python examples/p21_graphics.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "reference/opus_session/data"
COL = {"A": "#2a78d6", "Q": "#eb6834"}
LS = {0.3: "--", 1.0: "-"}


def main():
    g2 = json.loads((D / "p21_G2.json").read_text())
    g3 = json.loads((D / "p21_G3.json").read_text())
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
    for r in g2["runs"][1:]:
        if r["lam_B"] == 2.0 and r["lam_E"] in LS:
            ax[0].plot(r["t"], r["df_overlap"], color=COL[r["arm"]], ls=LS[r["lam_E"]], lw=2,
                       label=f"{'dynamic record (A)' if r['arm']=='A' else 'quenched (Q)'}, λ_E={r['lam_E']}")
    for r in g3["runs"][1:]:
        if r["lam_B"] == 2.0 and r["lam_E"] in LS:
            ax[1].plot(r["t"], r["fid_C0"], color=COL[r["arm"]], ls=LS[r["lam_E"]], lw=2)
            ax[2].plot(r["t"], np.array(r["E_rec"]) / r["E_rec_infinite_T"], color=COL[r["arm"]], ls=LS[r["lam_E"]], lw=2)
    ax[0].set_title("G2: trapped DF loop - overlap with its vacuum form")
    ax[1].set_title("G3: free flash - fidelity with flat-vacuum light")
    ax[2].set_title("G3: energy in the record / infinite-temperature value")
    for a in ax:
        a.set_xlabel("tick"); a.grid(alpha=0.25); a.spines[["top", "right"]].set_visible(False)
    fig.legend(*ax[0].get_legend_handles_labels(), loc="lower center", ncol=4, frameon=False, fontsize=9)
    fig.suptitle("P21: option A (quantum record on 3 edges, lossless box, λ_B = 2)", fontsize=12)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    out = ROOT / "out/p21_quantum_record.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=130)
    print(out)


if __name__ == "__main__":
    main()
