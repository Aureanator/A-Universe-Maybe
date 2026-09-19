"""P18 figure: sharp 3D fronts, 2D tail, mass wake; symbol anisotropy vs edge weighting."""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from propagation_test import ROOT, evolve, kuhn_star, square_star

BLUE, ORANGE, AQUA, INK, MUTED, GRID, BG = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"
sigma = 2.0
t = 12 * sigma
D, ring = kuhn_star()
D2, _ = square_star()


def profile(Dm, w, m):
    X, Y, r, f, N = evolve(Dm, w, sigma, [t], m=m)
    u2 = f[t] ** 2
    bins = np.linspace(0, t + 4 * sigma, 90)
    idx = np.digitize(r.ravel(), bins)
    tot = u2.sum()
    prof = np.array([u2.ravel()[idx == i].sum() for i in range(1, len(bins))]) / tot
    return 0.5 * (bins[1:] + bins[:-1]) / sigma, prof


data = json.loads((ROOT / "reference/opus_session/data/propagation_test.json").read_text())
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), dpi=150)
fig.patch.set_facecolor(BG)
for ax in (a1, a2):
    ax.set_facecolor(BG)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(color=GRID, lw=0.6)
for (Dm, w, m, lab, col) in [(D, np.ones(14), 0.0, "3D project mesh, massless", BLUE),
                             (D, np.ones(14), 1.0 / sigma, "3D project mesh, mass (m·σ = 1)", ORANGE),
                             (D2, np.ones(4), 0.0, "2D square lattice, massless", AQUA)]:
    x, p = profile(Dm, w, m)
    a1.semilogy(x, np.maximum(p, 1e-16), color=col, lw=2, label=lab)
a1.axvline((t - 4 * sigma) / sigma, color=MUTED, lw=1, ls="--")
a1.text((t - 4 * sigma) / sigma - 0.3, 2e-1, "← well inside the cone", ha="right", fontsize=8, color=INK)
a1.set_ylim(1e-16, 1)
a1.set_xlabel("distance from source / pulse width (emergent metric), t = 12σ", color=MUTED)
a1.set_ylabel("share of the wave in each radial shell", color=MUTED)
a1.set_title("Sharp front in 3D; tail in 2D; mass leaves a wake", fontsize=9, color=INK, loc="left")
a1.legend(frameon=False, fontsize=8, loc="lower left")
for key, lab, col in [("uniform", "unit weights (slope %.2f)", BLUE), ("ring_weighted", "ring-4 edges at ½ (slope %.2f)", ORANGE)]:
    rows = data["N3_symbol"][key]["rows"]
    a2.loglog([r["kappa"] for r in rows], [r["spread_over_mean"] for r in rows], "o-", color=col, lw=2,
              label=lab % data["N3_symbol"][key]["loglog_slope"])
a2.set_xlabel("wavenumber (emergent units)", color=MUTED)
a2.set_ylabel("direction spread of ω²/k² (relative)", color=MUTED)
a2.set_title("Direction dependence of wave speed on the project mesh", fontsize=9, color=INK, loc="left")
a2.legend(frameon=False, fontsize=8, loc="upper left")
fig.suptitle("P18: the project's mesh carries round, sharp light fronts (in its own metric); mass makes a wake",
             fontsize=10, color=INK, x=0.01, ha="left")
fig.tight_layout()
out = ROOT / "out/p18_propagation.png"
fig.savefig(out)
print(out)
