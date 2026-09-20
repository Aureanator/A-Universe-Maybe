"""Figure for P22 (out/p22_freezeout.png). Reproduce: python examples/p22_graphics.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "reference/opus_session/data"
BLUES = ["#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#0d366b"]


def main():
    runs = []
    for p in ("A03", "A10", "rest"):
        runs += json.loads((D / f"p22_{p}.json").read_text())["runs"]
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    for k, lE in enumerate((0.3, 1.0)):
        a = ax[k]
        A = sorted([r for r in runs if r["arm"] == "A" and r["lam_E"] == lE], key=lambda r: r["theta"])
        for c, r in zip(BLUES, A):
            hot = np.sin(r["theta"]) ** 2
            a.semilogy(r["t"], r["N"], color=c, lw=2, label=f"dynamic record, hot fraction {hot:.2f}")
        for r in runs:
            if r["arm"] == "Q" and r["lam_E"] == lE and r["theta"] > 1.5:
                a.semilogy(r["t"], r["N"], color="#eb6834", lw=2, ls="--", label="frozen hot chop (Q), hot fraction 1")
            if r["arm"] == "C0":
                a.semilogy(r["t"], np.maximum(r["N"], 1e-20), color="#8a8a86", lw=2, ls=":", label="flat vacuum, no record (C0)")
        a.set_ylim(1e-9, 1.5)
        a.set_title(f"light left in the open box, λ_E = {lE}, λ_B = 2")
        a.set_xlabel("tick"); a.grid(alpha=0.25, which="both"); a.spines[["top", "right"]].set_visible(False)
    ax[0].set_ylabel("norm still inside")
    fig.legend(*ax[0].get_legend_handles_labels(), loc="lower center", ncol=4, frameon=False, fontsize=9)
    fig.suptitle("P22: a hot, dynamic record holds light (opacity); frozen chop and a calm vacuum let it go", fontsize=12)
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    out = ROOT / "out/p22_freezeout.png"
    fig.savefig(out, dpi=130)
    print(out)


if __name__ == "__main__":
    main()
