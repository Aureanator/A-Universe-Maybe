"""Figure for P25 (out/p25_seeded.png). Reproduce: python examples/p25_graphics.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "reference/opus_session/data"
STY = {"V": ("#8a8a86", ":", "calm quantum vacuum (V)"),
       "C": ("#2a78d6", "-", "compatible seeding in cooled bath (C, 3 seeds)"),
       "I": ("#eb6834", "--", "imprinted flat pattern in same bath (I, 3 seeds)"),
       "Qc": ("#1baf7a", "-", "compatible, bath frozen (Qc)")}


def main():
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    for a, (L, title) in zip(ax, (("L6", "L6: axis square, ring-6 edges (60° pivots)"),
                                  ("L4", "L4: face-diagonal loop, ring-4 edges (90° pivots)"))):
        d = json.loads((D / f"p25_{L}.json").read_text())
        done = set()
        for r in d["runs"]:
            c, ls, lab = STY[r["arm"]]
            a.plot(r["t"], r["loop"], color=c, ls=ls, lw=2, label=None if r["arm"] in done else lab)
            done.add(r["arm"])
        a.set_title(title); a.set_xlabel("tick"); a.grid(alpha=0.25); a.spines[["top", "right"]].set_visible(False)
    ax[0].set_ylabel("weight on the loop's 8 arcs"); ax[0].set_ylim(0.8, 1.01)
    fig.legend(*ax[0].get_legend_handles_labels(), loc="lower center", ncol=4, frameon=False, fontsize=9)
    fig.suptitle("P25: loop patterns seeded in a cooled bath (λ_E = λ_B = 0.1, open walls)", fontsize=12)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(ROOT / "out/p25_seeded.png", dpi=130)


if __name__ == "__main__":
    main()
