"""Summarize completed P26 runs and render a scientific diagnostic figure.

Run after both p26_dressed runs: python examples/p26_summary.py
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "reference/astra_session/data"


def summarize(d):
    if d["status"] != "complete":
        raise ValueError("P26 run is not complete")
    zero, vacuum = d["filters"][-2:]
    release = {r["arm"]: r for r in d["release"]}
    loss = {arm: r["samples"][0]["loop_weight"] - r["samples"][-1]["loop_weight"]
            for arm, r in release.items()}
    return {
        "n": d["n"], "raw_residual": d["raw_seed"]["target_residual"],
        "vacuum_filter_weight": vacuum["filtered_weight"],
        "zero_filter_weight": zero["filtered_weight"],
        "loop_weight": vacuum["loop_weight"], "residual": vacuum["target_residual"],
        "best_phase_residual": vacuum["best_phase_residual"],
        "best_phase": vacuum["best_phase"],
        "record_vacuum_population": vacuum["record_vacuum_population"],
        "record_diagonal_l1": vacuum["record_diagonal_one_tick_l1"],
        "loop_loss_128": loss,
        "loss_ratio_vacuum_to_raw": loss["phase_vacuum"] / loss["raw"],
        "open_final_loop": {arm: r["samples"][-1]["loop_weight"] for arm, r in release.items()},
        "bookkeeping_error": max(r["max_bookkeeping_error"] for r in d["release"]),
        "P26_1": (all(c["target_residual"] < 1e-12 for c in
                      [d["controls"]["frozen_compatible"], d["controls"]["decoupled_vacuum"]])
                  and all(r["max_bookkeeping_error"] < 1e-10 for r in d["release"])),
        "P26_2": (vacuum["target_residual"] <= d["raw_seed"]["target_residual"] / 4
                  and vacuum["loop_weight"] >= 0.8),
        "P26_3_release": loss["phase_vacuum"] <= loss["raw"] / 2,
        "P26_4": vacuum["filtered_weight"] > zero["filtered_weight"],
        "eigenstate_residual_gate": vacuum["target_residual"] < 1e-8,
    }


def main():
    runs = [json.loads((DATA / f"p26_dressed_n{n}.json").read_text()) for n in [5, 6]]
    rows = [summarize(d) for d in runs]
    delta = abs(rows[0]["loop_weight"] - rows[1]["loop_weight"])
    summary = {"runs": rows, "loop_weight_box_difference": delta, "P26_3_boundary": delta <= 0.05}
    print(json.dumps(summary, indent=2))
    (DATA / "p26_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, axs = plt.subplots(2, 2, figsize=(11, 7.5), constrained_layout=True)
    colors = {"zero": "#c46c25", "vacuum": "#126ca0", "raw": "#666666"}
    for d, style in zip(runs, ["-", "--"]):
        for phase_index, name in enumerate(["zero", "vacuum"]):
            records = d["filters"][phase_index::2]
            t = [r["T"] for r in records]
            label = f"{name} phase, n={d['n']}"
            for ax, key in zip(axs.flat[:3], ["target_residual", "filtered_weight", "loop_weight"]):
                ax.plot(t, [r[key] for r in records], style, color=colors[name], marker="o", ms=4, label=label)
        for arm in d["release"]:
            name = arm["arm"].replace("phase_", "")
            axs[1, 1].plot([r["t"] for r in arm["samples"]],
                           [r["loop_weight"] for r in arm["samples"]], style,
                           color=colors[name], label=f"{name}, n={d['n']}")
    axs[0, 0].set(title="Full-state one-tick residual", ylabel="||U x - exp(i phase) x||", yscale="log")
    axs[0, 1].set(title="Finite-window filtered weight", ylabel="||F_T||² (before normalization)", yscale="log")
    axs[1, 0].set(title="Localization after normalization", ylabel="Weight on the eight loop arcs", ylim=(0, 1.02))
    axs[1, 1].set(title="Open-boundary release", xlabel="Ticks after release", ylabel="Absolute loop weight", ylim=(0.8, 1.005))
    for ax in axs.flat[:3]:
        ax.set_xlabel("Filter window T (ticks)")
        ax.set_xticks([64, 128, 256])
    for ax in axs.flat:
        ax.grid(alpha=0.2)
    axs[0, 0].legend(fontsize=8)
    axs[1, 1].legend(fontsize=8, ncol=2)
    fig.suptitle("P26: phase filtering improves a prepared loop; no exact eigenstate established", fontsize=13)
    out = ROOT / "out/p26_dressed.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=160)
    print(out)


if __name__ == "__main__":
    main()
