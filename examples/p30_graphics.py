"""Figure for P30 (out/p30_churn.png). Reproduce: python examples/p30_graphics.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / "reference/opus_session/data/p30_churn.json").read_text())
BLUES = {"1e-10": "#0d366b", "0.001": "#3987e5", "0.01": "#9ec5f4"}
LAB = {"1e-10": "forever (δ=1e-10)", "0.001": "~1,000 ticks", "0.01": "~100 ticks"}


def curve(kind, delta):
    ps = sorted({r["p"] for r in rows})
    x, y = [], []
    for p in ps:
        sel = [r for r in rows if r["kind"] == kind and r["p"] == p]
        x.append(np.mean([r["curvature"]["curved_fraction"] for r in sel]))
        y.append(np.mean([max(r["loops"][L][delta]["max_bias"] for L in r["loops"]) for r in sel]))
    return np.array(x), np.array(y)


fig, ax = plt.subplots(1, 2, figsize=(12.5, 4.6), sharey=True)
for a, kind, title in ((ax[0], "A4", "A4 labels (no spin lift)"), (ax[1], "2T", "2T spinor labels (spin-½ lift)")):
    for d, c in BLUES.items():
        x, y = curve(kind, d)
        a.plot(100 * x, y, color=c, lw=2, marker="o", ms=5, label=LAB[d])
    a.set_title(title); a.set_xlabel("vacuum churn: curved faces (%)")
    a.grid(alpha=0.25); a.spines[["top", "right"]].set_visible(False); a.set_ylim(-0.02, 0.9)
ax[0].set_ylabel("strongest stationary circulation")
fig.legend(*ax[0].get_legend_handles_labels(), loc="lower center", ncol=3, frameon=False, fontsize=9,
           title="how long the circulation lasts", title_fontsize=9)
fig.suptitle("P30: how much vacuum churn stationary circulation can stand", fontsize=12)
fig.tight_layout(rect=(0, 0.13, 1, 1))
fig.savefig(ROOT / "out/p30_churn.png", dpi=130)
print("ok")
