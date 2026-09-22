"""E069 animation -- a Z3 meson and a Z3 baryon evaporating, side by side, same move law.

Run:  ./.venv/Scripts/python.exe examples/e069_nality_movie.py
Writes reference/local_qwen/figures/e069_meson_vs_baryon.gif

WHAT YOU ARE LOOKING AT.  Both panels are the SAME n=3 Kuhn ball under the SAME driver (DriverGZN,
beta_B=6, beta_E=12, rng seed 5).  Thin grey lines are the simplicial mesh -- its topology never moves.
Thick coloured lines are edges carrying electric flux a_e in Z3 (cyan = +1 along the canonical direction,
orange = -1); they change only through accepted local rewrites.  Discs are live charges q_v := div(E)_v:
magenta q=1, green q=2, with the value printed.

Left panel is seeded as a MESON (flux string: one +1 and one -1 charge -- pair-cancellable).  Right panel
is the BARYON: three arms from one junction, neutral because -3 = 0 mod 3, yet containing no cancelling
pair at all.

THE RESULT SHOWN (diary E069 / CLAIMS 62): the meson evaporates at t=1797 while the baryon lasts to
t=3966 -- but it does not survive forever, and you can watch why: two unit charges meet and FUSE into a
q=2 site, which is precisely the antiparticle of the third.  N-ality buys extra encounters, not immunity.

Coordinates come from vertex metadata grid=(i,j,k) through a fixed axonometric projection and are used for
PROJECTION ONLY -- no acceptance rule or dynamical quantity touches them (spec prohibition).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "examples"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.animation import PillowWriter

from constraintnet.drivers import DriverGZN          # noqa: E402
from e069_nality_and_dyons import seed_regime        # noqa: E402  identical seeding, no duplication

SEED = 5
BETA_E = 12.0
T_MAX = 4400
STRIDE = 50
EXPECT_T_VACUUM = {"meson": 1797, "baryon": 3966}    # replay must reproduce the harness numbers

FLUX_COLORS = {1: "#22b8ff", 2: "#ff8c1a"}
CHARGE_COLORS = {1: "#ff3fa4", 2: "#3ddc7f"}


def iso(grid):
    """Fixed axonometric projection of grid=(i,j,k).  Visual only -- dynamics never sees this."""
    i, j, k = grid
    return (i - 0.38 * k, j + 0.18 * k)


def record(regime, seed=SEED):
    """Replay one harness run deterministically, snapshotting every STRIDE steps."""
    st, info = seed_regime("Z3", regime)
    driver = DriverGZN(st, rng_seed=seed, beta_B=6.0, beta_E=BETA_E)
    frames, t_vacuum = [], None
    for step in range(T_MAX):
        if step % STRIDE == 0:
            frames.append((step, list(st.E), {v: q for v, q in st.charges().items() if q}, st.nality()))
        driver.advance()
        assert st.check_gauss(), "Gauss violated -- impossible by construction"
        if t_vacuum is None and not st.live_defects():
            t_vacuum = step + 1
    assert t_vacuum == EXPECT_T_VACUUM[regime], (regime, t_vacuum)   # determinism cross-check
    return st, frames, info, t_vacuum


def draw(ax, st, frame, label, t_vacuum):
    step, E, live, nal = frame
    pos = {v: iso(st.cx.vertex(v).metadata["grid"]) for v in st.vertices}

    segs, colors, widths, alphas = [], [], [], []
    for (u, w) in st.edges:                       # st.edges: canonical order matching st.E
        a, b = pos[u], pos[w]
        segs.append([(a[0], a[1]), (b[0], b[1])])
        colors.append("#9aa4b2"); widths.append(0.5); alphas.append(0.16)
    for (u, w), flux in zip(st.edges, E):
        if not flux:
            continue
        p, q = pos[u], pos[w]
        segs.append([(p[0], p[1]), (q[0], q[1])])
        colors.append(FLUX_COLORS.get(flux, "#ffffff")); widths.append(2.6); alphas.append(0.95)

    lc = LineCollection(segs, colors=colors, linewidths=widths)
    lc.set_alpha(alphas)
    ax.add_collection(lc)

    for v, q in sorted(live.items()):
        x, y = pos[v]
        ax.scatter([x], [y], s=200 if q == 1 else 150, c=[CHARGE_COLORS.get(q, "#ffffff")],
                   edgecolors="white", linewidths=0.8, zorder=5)
        ax.text(x, y, str(q), color="black", fontsize=7, ha="center", va="center", zorder=6)

    dead = t_vacuum is not None and step >= t_vacuum
    status = "ANNIHILATED" if dead else f"{nal['kind'].upper()} ({nal['constituents']} irreducible)"
    ax.set_title(f"{label}   t={step:4d}   live charges = {len(live)}   {status}",
                 fontsize=9, color="#e6edf3")
    leak = nal["total_charge"]
    ax.text(0.015, 0.05, f"sum q mod 3 = {leak}   (Gauss leak -- must stay 0)", transform=ax.transAxes,
            fontsize=7, color="#c62828" if leak else "#7ee787")
    ax.set_xlim(-1.4, 3.5); ax.set_ylim(-0.9, 4.0)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def main():
    st_m, frames_m, _info_m, tvac_m = record("meson")
    st_b, frames_b, _info_b, tvac_b = record("baryon")
    print(f"replay reproduced harness t_vacuum: meson {tvac_m}, baryon {tvac_b}")

    fig, axes = plt.subplots(2, 1, figsize=(7.4, 8.8), dpi=80)
    fig.patch.set_facecolor("#0e1116")

    def update(i):
        for ax in axes:
            ax.clear()
            ax.set_facecolor("#0e1116")
        draw(axes[0], st_m, frames_m[i], "MESON  (flux string: +1 and -1, pair-cancellable)", tvac_m)
        draw(axes[1], st_b, frames_b[i], "BARYON (three arms; neutral, no cancelling pair)", tvac_b)
        fig.suptitle("E069 · Z3 Gauss-completed vacuum at beta_E = 12 · identical move law, different N-ality\n"
                     "cyan/orange = flux +1/-1 · magenta/green = charge q=1/2 · mesh is projection only;\n"
                     "the baryon outlives the meson but still annihilates -- two 1's fuse into the 2 that kills it",
                     color="#e6edf3", fontsize=9.5)
        return []

    anim = matplotlib.animation.FuncAnimation(fig, update, frames=len(frames_m), blit=False)
    out = ROOT / "reference" / "local_qwen" / "figures" / "e069_meson_vs_baryon.gif"
    out.parent.mkdir(parents=True, exist_ok=True)
    anim.save(str(out), writer=PillowWriter(fps=18))
    print(f"wrote {out}  ({out.stat().st_size/1e6:.2f} MB, {len(frames_m)} frames)")


if __name__ == "__main__":
    main()
