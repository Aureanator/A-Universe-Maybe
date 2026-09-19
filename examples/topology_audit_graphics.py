"""Render actual P13b support and action witnesses; no invented trajectories."""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection

from topology_audit import ROOT, linked_fixture
from constraintnet.curvature import CurvatureState


def draw(ax, state, title):
    cx = state.cx
    def center(simplex):
        return tuple(sum(cx.vertex(v).metadata["grid"][i] for v in simplex)/len(simplex)
                     for i in range(3))
    palette = ["#2864b7", "#dd792b", "#578d68"]
    for ci, component in enumerate(state.components()):
        segments = []
        for fi in component["faces"]:
            face = center(state.faces[fi])
            for ti in state.face_tets[fi]:
                segments.append([face, center(state.tets[ti])])
        color = palette[ci % len(palette)] if component["kind"] == "loop" else "#8156a6"
        ax.add_collection3d(Line3DCollection(segments, colors=color, linewidths=2.6))
        junctions = [center(state.tets[ti]) for ti in component["tets"]
                     if sum(fi in component["faces"] for fi in state.tet_faces[ti]) != 2]
        if junctions:
            ax.scatter(*zip(*junctions), color="#be3040", s=55, marker="D", depthshade=False)
    ax.set(xlim=(.8,7.5), ylim=(.8,6.5), zlim=(1.8,6.5), title=title)
    ax.set_box_aspect((6.7,5.7,4.7), zoom=1.4)
    ax.view_init(elev=23, azim=-62)
    ax.set_axis_off()


def main():
    records = json.loads((ROOT / "reference/astra_session/data/topology_rewrite_audit.json").read_text())
    record = next(r for r in records if r["group"] == "Z3")
    cert = record["unrestricted_erasure"]
    junction = next(s["step"] for s in record["snapshots"] if "junction/open" in s["kinds"])
    merged = next(s["step"] for s in record["snapshots"]
                  if s["step"] > junction and s["kinds"] == ["loop"])
    state = CurvatureState(linked_fixture("Z3"))
    selected = {0: state.cx.copy()}
    for step, move in enumerate(cert["moves"], 1):
        state.commit(move["edge"], *state.proposal(move["edge"], move["multiplier"]))
        if step in (junction, merged):
            selected[step] = state.cx.copy()
    plt.rcParams.update({"font.size": 11, "axes.titlesize": 13})
    fig = plt.figure(figsize=(13,9), facecolor="white", layout="constrained")
    titles = ["Start: two linked flux loops | H = 98 | |Lk| = 1",
              f"Move {junction}: junction | H = {cert['actions'][junction]}",
              f"Move {merged}: one merged loop | H = {cert['actions'][merged]}"]
    for panel, (step, title) in enumerate(zip((0, junction, merged), titles), 1):
        draw(fig.add_subplot(2,2,panel, projection="3d"), CurvatureState(selected[step]), title)
    ax = fig.add_subplot(2,2,4)
    actions = cert["actions"]
    ax.step(range(len(actions)), actions, where="post", color="#2864b7", linewidth=2)
    ax.axhline(actions[0], color="#9b9b9b", linestyle="--", linewidth=1)
    ax.scatter([junction, merged], [actions[junction], actions[merged]], color="#8156a6", zorder=3)
    uphill = [i for i in range(1,len(actions)) if actions[i] > actions[i-1]]
    for i in uphill:
        ax.annotate(f"Only uphill step: {actions[i-1]} to {actions[i]}",
                    xy=(i, actions[i]), xytext=(i+17, actions[i]+16),
                    arrowprops={"arrowstyle":"->", "color":"#be3040"}, color="#be3040", fontsize=10)
    ax.set(xlabel="Constructed rewrite index (not physical time)",
           ylabel="Curved-face action H", title="Complete erasure witness: 140 moves", ylim=(-5,112))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=.15)
    fig.suptitle("Linked flux can merge under nonincreasing local rewrites", fontsize=18)
    fig.supxlabel("P13b | prescribed Z3 fixture on Kuhn n=8 | exact fixed boundary | geometric merger, not a nuclear reaction", fontsize=10)
    output = ROOT / "out/topology_audit.png"
    output.parent.mkdir(exist_ok=True)
    fig.savefig(output, dpi=170)
    print(output)


if __name__ == "__main__":
    main()
