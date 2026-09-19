"""P15 figure: action along verified nonincreasing erasures, commuting vs non-commuting."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "reference/opus_session/data/noncommuting_link_audit.json").read_text())
runs = {(r["arm"], r["tie_convention"]): r for r in data}
series = [(("C0", "disk1_first"), "C0  commuting, a = b (order 3)", "#2a78d6", "-"),
          (("C1", "disk1_first"), "C1  commuting, distinct V4", "#eb6834", "-"),
          (("N1", "disk1_first"), "N1 / N2  non-commuting (identical H)", "#1baf7a", "-"),
          (("N1", "disk2_first"), "N1 / N2  tie control (disk 2 first)", "#1baf7a", ":")]
fig, ax = plt.subplots(figsize=(9, 5), dpi=150)
fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
for key, label, color, ls in series:
    a = runs[key]["ordered_erasure"]["actions"]
    ax.plot(range(len(a)), a, ls, color=color, lw=2, label=label)
ax.axvline(52, color="#52514e", lw=1, ls="--")
ax.annotate("step 52: tether and linking vanish together\n(two loops, Lk = 0; meridians do not commute)",
            xy=(52, 80), xytext=(60, 95), fontsize=8, color="#0b0b0b",
            arrowprops=dict(arrowstyle="-", color="#52514e", lw=0.8))
ax.annotate("N arms start as ONE junction:\nloop A + loop B + V4 tether (5-6 faces)",
            xy=(0, 103), xytext=(14, 108), fontsize=8, color="#0b0b0b",
            arrowprops=dict(arrowstyle="-", color="#52514e", lw=0.8))
ax.set_xlabel("rewrite index (search order, NOT time)", color="#52514e")
ax.set_ylabel("H = curved faces (declared action)", color="#52514e")
ax.set_title("P15: linked flux loops erase with no uphill step, whether or not fluxes commute\n"
             "Kuhn n=8, A4, prepared fixtures; every path verified (holonomy, boundary, inverse, gauge)",
             fontsize=10, color="#0b0b0b", loc="left")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.grid(axis="y", color="#e6e5e0", lw=0.6)
ax.set_ylim(0, 115)
ax.legend(frameon=False, fontsize=8, loc="lower left")
fig.tight_layout()
out = ROOT / "out/p15_noncommuting_links.png"
fig.savefig(out)
print(out)
