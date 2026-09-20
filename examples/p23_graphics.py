"""Figure for P23/P24a (out/p23_p24a_radiative.png). Reproduce: python examples/p23_graphics.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "reference/opus_session/data"


def crossing(rows):
    E = np.array([r["E0"] for r in rows]); d = np.array([r["dE"] for r in rows])
    for i in range(len(E) - 1):
        if d[i] > 0 >= d[i + 1]:
            return E[i] + (E[i + 1] - E[i]) * d[i] / (d[i] - d[i + 1])
    return float("nan")


def curves():
    lad = json.loads((D / "p23_ladder_0.1_0.1.json").read_text())
    out = [("broad light, <cos ω>=0.30", [r for r in lad if r["sigma"] == 0.5], "#eb6834"),
           ("broad light, <cos ω>=0.84", [r for r in lad if r["sigma"] == 1.2], "#e87ba4")]
    for n, c in ((5, "#86b6ef"), (6, "#3987e5"), (7, "#0d366b")):
        rows = json.loads((D / f"p24a_redshift_n{n}.json").read_text())
        out.append((f"lowest band, box n={n}, ω₀={rows[0]['w0']:.3f}", rows, c))
    return out


def main():
    cs = curves()
    Ehot = cs[0][1][-1]["E0"]
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
    for lab, rows, c in cs:
        E = np.array([r["E0"] for r in rows]) / Ehot
        d = np.array([r["dE"] for r in rows])
        ax[0].plot(E, d / np.abs(d).max(), color=c, lw=2, marker="o", ms=5, label=lab)
    ax[0].axhline(0, color="#8a8a86", lw=1)
    ax[0].set_xlabel("record energy / hot-state energy"); ax[0].set_ylabel("energy drift per flash (each curve scaled to its max)")
    ax[0].set_title("where light holds the record: drift = 0")
    w0 = [rows[0]["w0"] for _, rows, _ in cs[2:]]
    Es = [crossing(rows) / Ehot for _, rows, _ in cs[2:]]
    ax[1].plot(w0, Es, color="#2a78d6", lw=2, marker="o", ms=8)
    for x, y, (_, rows, _) in zip(w0, Es, cs[2:]):
        ax[1].annotate(f"n={rows[0]['n']}: {y:.2f}", (x, y), textcoords="offset points", xytext=(8, -4), fontsize=9)
    ax[1].set_xlabel("light's phase per tick ω₀ (lower = redshifted)"); ax[1].set_ylabel("equilibrium E* / hot-state energy")
    ax[1].set_title("redshifted light holds the record calmer"); ax[1].set_ylim(0, 0.6)
    for a in ax:
        a.grid(alpha=0.25); a.spines[["top", "right"]].set_visible(False)
    ax[0].legend(frameon=False, fontsize=8, loc="lower left")
    fig.suptitle("P23/P24a: radiative equilibrium of a quantum record (unfolded couplings λ_E = λ_B = 0.1)", fontsize=12)
    fig.tight_layout()
    fig.savefig(ROOT / "out/p23_p24a_radiative.png", dpi=130)
    print([round(x, 3) for x in Es], [round(crossing(r) / Ehot, 3) for _, r, _ in cs[:2]])


if __name__ == "__main__":
    main()
