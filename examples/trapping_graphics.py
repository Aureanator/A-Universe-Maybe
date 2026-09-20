"""P17 figure: probabilities escape, amplitudes trap; leak slows doubly-exponentially with depth."""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trapping_test import ROOT, GAMMA, _dist, dark_subspace, expm, laplacian, sierpinski

BLUE, ORANGE, INK, MUTED, GRID, BG = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"

verts, edges, _, b = sierpinski(3)
n = len(verts)
L = laplacian(n, edges)
PB = np.zeros((n, n)); PB[b, b] = 1
D, _, _ = dark_subspace(L, [b])
far = int(np.argmax(_dist(n, edges, [b])))
ts = np.logspace(-1, 5, 120)
q, c = [], []
for t in ts:
    q.append(float((np.abs(expm(-1j * (L - 1j * GAMMA * PB) * t)[:, far]) ** 2).sum()))
    c.append(float(expm(-(L + GAMMA * PB) * t)[:, far].sum()))
pred = float((np.abs(D[far]) ** 2).sum())

depth = json.loads((ROOT / "reference/opus_session/data/trapping_depth_rates.json").read_text())
levels = sorted(int(k) for k in depth)
slow = [float(depth[str(k)]["rates"][0]) for k in levels]
frac = [1 - depth[str(k)]["krylov_dim"] / depth[str(k)]["N"] for k in levels]

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), dpi=150)
fig.patch.set_facecolor(BG)
for ax in (a1, a2):
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(color=GRID, lw=0.6)
a1.semilogx(ts, q, color=BLUE, lw=2, label="amplitudes (same generator, factor i)")
a1.semilogx(ts, c, color=ORANGE, lw=2, label="probabilities")
a1.axhline(pred, color=MUTED, lw=1, ls="--")
a1.text(0.12, pred + 0.03, f"derived limit ||P_D e||^2 = {pred:.3f}", fontsize=8, color=INK)
a1.set_xlabel("time (units of 1/edge rate)", color=MUTED)
a1.set_ylabel("probability still inside", color=MUTED)
a1.set_title("Sierpinski level 3, start farthest from the exit", fontsize=9, color=INK, loc="left")
a1.legend(frameon=False, fontsize=8, loc="lower left")
a1.set_ylim(0, 1.05)
a2.semilogy(levels, slow, "o-", color=BLUE, lw=2, ms=6)
for k, r, f in zip(levels, slow, frac):
    a2.annotate(f"{r:.1e}\ndark {f:.0%}", (k, r), textcoords="offset points", xytext=(6, 4),
                fontsize=7, color=INK)
a2.set_ylim(1e-33, 10)
a2.set_xlim(0.7, 6.8)
a2.set_xlabel("fractal depth (gasket level)", color=MUTED)
a2.set_ylabel("slowest leak rate of the non-dark states", color=MUTED)
a2.set_title("Leak rate vs depth (exact, 150-digit spectrum)", fontsize=9, color=INK, loc="left")
fig.suptitle("P17: probabilities always escape; amplitudes trap by interference, "
             "and the leak slows doubly-exponentially with depth", fontsize=10, color=INK, x=0.01, ha="left")
fig.tight_layout()
out = ROOT / "out/p17_trapping.png"
fig.savefig(out)
print(out)
