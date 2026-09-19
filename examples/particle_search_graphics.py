"""Render measured P8-P10 data; coordinates are used here only."""

import gzip
import itertools
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import numpy as np

from constraintnet.groups import AlternatingGroup4


OUT = Path("out/particle_search")
BG = "#101827"
FG = "#e5eefb"
COLORS = ["#70d6ff", "#ffb86b", "#a5ecaa", "#e598d8"]


def style():
    plt.rcParams.update({"figure.facecolor": BG, "axes.facecolor": BG,
                         "axes.edgecolor": "#6d7d93", "axes.labelcolor": FG,
                         "text.color": FG, "xtick.color": FG, "ytick.color": FG,
                         "font.size": 11, "grid.color": "#344154",
                         "savefig.facecolor": BG})


def summary():
    runs = json.loads((OUT / "runs.json").read_text())
    exact = json.loads((OUT / "landscape.json").read_text())
    audit = json.loads((OUT / "candidate_audit.json").read_text())
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.7), gridspec_kw={"width_ratios": [1, 1.5, 1]})
    fig.suptitle("An unfrozen particle search — what survives the checks?", fontsize=21, x=0.05, ha="left")
    fig.text(0.05, 0.86, "Chosen action: number of curved faces. No supplied particles, forces, or reaction rules.", color="#aebed3")
    ax = axes[0]
    histogram = exact["A4"]["action_histogram_physical"]
    ax.bar([int(k) for k in histogram], list(histogram.values()), color=COLORS[0], width=0.65)
    ax.set(title="Exact A4 seed: 178 physical states", xlabel="Curvature action H", ylabel="Gauge orbits")
    ax.text(0.04, 0.95, "0 nonvacuum stable plateaus\nEvery state can descend to vacuum\nin at most 3 moves", transform=ax.transAxes, va="top", fontsize=10)
    ax.set_ylim(0, 150)
    ax = axes[1]
    for color, beta in zip(COLORS, ("0", "1", "2", "inf")):
        selected = [r for r in runs if r["group"] == "A4" and r["n"] == 3 and r["beta"] == beta]
        values = np.array([[t["action"] / r["faces"] for t in r["trajectory"]] for r in selected])
        x = [t["step"] / selected[0]["interior_edges"] for t in selected[0]["trajectory"]]
        label = f"beta = {beta}" if beta != "inf" else "downhill only"
        ax.plot(x, np.median(values, axis=0), color=color, label=label)
        ax.fill_between(x, values.min(axis=0), values.max(axis=0), color=color, alpha=0.13)
    ax.set(title="A4 bulk: n=3, both starts, all seeds", xlabel="Proposals per interior edge", ylabel="Curved fraction of all faces")
    ax.legend(frameon=False, fontsize=9)
    ax.grid(alpha=0.3)
    ax = axes[2]
    ax.bar([0, 1, 2], [audit["branches_audited"], audit["with_local_downhill"], audit["one_step_erasable"]], color=[COLORS[0], COLORS[1], COLORS[3]], width=0.65)
    ax.set_xticks([0, 1, 2], ["Pass age/size\nscreen", "Immediate\ndownhill", "One-move\nerasure"])
    ax.set(title="Apparent longevity audited", ylabel="Branches", ylim=(0, 70))
    for i, value in enumerate((57, 57, 42)):
        ax.text(i, value + 1.5, str(value), ha="center", fontsize=13)
    fig.text(0.05, 0.07, "96 registered runs · 960,000 proposals · geometric merges/splits observed; stable particles and chemistry NOT established.", fontsize=11, color="#ffd18a")
    fig.text(0.05, 0.025, "Band = full six-run range, not uncertainty. Fixed outer boundary; no frozen core. Action penalty beta is not physical temperature.", fontsize=9, color="#aebed3")
    fig.subplots_adjust(left=0.06, right=0.98, top=0.75, bottom=0.22, wspace=0.35)
    fig.savefig(OUT / "search_summary.png", dpi=170)
    fig.savefig(OUT / "search_summary.svg")
    plt.close(fig)


def animation():
    data = []
    for beta in ("0", "1", "2", "inf"):
        path = OUT / f"A4_n3_b{beta}_uniform_s0.frames.json.gz"
        with gzip.open(path, "rt") as stream:
            data.append(json.load(stream))
    first = data[0]
    positions = {int(k): np.array(v["grid"], dtype=float) for k, v in first["vertex_metadata"].items()}
    tets = first["tets"]
    centers = [np.mean([positions[v] for v in t], axis=0) for t in tets]
    dual = []
    for face in first["faces"]:
        incident = [i for i, t in enumerate(tets) if set(face).issubset(t)]
        centroid = np.mean([positions[v] for v in face], axis=0)
        dual.append([centers[incident[0]], centers[incident[1]]] if len(incident) == 2
                    else [centers[incident[0]], centroid])
    g = AlternatingGroup4()
    classes = [g.class_of(tuple(e)) for e in first["elements"]]
    class_order = list(g.conjugacy_classes())
    class_colors = {c: COLORS[i % len(COLORS)] for i, c in enumerate(class_order)}
    corners = list(itertools.product((0, 3), repeat=3))
    box = [[a, b] for a, b in itertools.combinations(corners, 2)
           if sum(x != y for x, y in zip(a, b)) == 1]
    fig = plt.figure(figsize=(12, 10))
    fig.suptitle("Curvature networks under four declared dynamics", fontsize=21, y=0.98)
    fig.text(0.5, 0.94, "A4 · Kuhn n=3 · identical uniform start and seed · outer boundary fixed · no frozen core", ha="center", color="#adbed4", fontsize=10)
    artists = []
    names = ["Unweighted", "Action penalty beta=1", "Action penalty beta=2", "Downhill only"]
    for i in range(4):
        ax = fig.add_subplot(2, 2, i + 1, projection="3d")
        ax.add_collection3d(Line3DCollection(box, colors="#44546a", linewidths=0.6))
        collection = Line3DCollection([dual[0]], linewidths=2.1, alpha=0.95)
        ax.add_collection3d(collection)
        ax.set(xlim=(-0.1, 3.1), ylim=(-0.1, 3.1), zlim=(-0.1, 3.1))
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=23, azim=-52)
        ax.set_axis_off()
        title = ax.set_title(names[i], fontsize=12, pad=-3)
        artists.append((collection, title))
    clock = fig.text(0.5, 0.06, "", ha="center", fontsize=13)
    fig.text(0.5, 0.025, "Lines = dual links crossing curved faces; colors = flux conjugacy classes. These are not identified particles or chemical bonds.", ha="center", fontsize=9, color="#ffd18a")
    fig.subplots_adjust(left=0.015, right=0.985, bottom=0.09, top=0.89, hspace=0.04, wspace=0.02)

    def update(frame):
        for i, (collection, title) in enumerate(artists):
            state = data[i]["frames"][frame]
            curved = [j for j, value in enumerate(state["flux"]) if value != first["identity"]]
            collection.set_segments([dual[j] for j in curved])
            collection.set_color([class_colors[classes[state["flux"][j]]] for j in curved])
            title.set_text(f"{names[i]}  |  H = {state['action']}")
        step = data[0]["frames"][frame]["step"]
        clock.set_text(f"Proposal step {step:,}  ·  one rendered frame per 100 proposals")
        return [a for pair in artists for a in pair] + [clock]

    update(20)
    fig.savefig(OUT / "curvature_networks.png", dpi=140)
    anim = FuncAnimation(fig, update, frames=len(first["frames"]), interval=100, blit=False)
    anim.save(OUT / "curvature_networks.gif", writer=PillowWriter(fps=10), dpi=85)
    plt.close(fig)


if __name__ == "__main__":
    style()
    summary()
    animation()
    print("Wrote search_summary.png/.svg and curvature_networks.png/.gif")
