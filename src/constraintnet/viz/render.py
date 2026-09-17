"""The animated, interactive viewer.

Layout: a large 3D view of the complex on the left; on the right a live readout (counters,
event log) and an observer-density panel.  Controls along the bottom: play/pause, single
step, speed, and layer toggles.  Keyboard: ``space`` play/pause, ``right`` step, ``e`` edges,
``f`` faces, ``o`` objects, ``d`` density, ``r`` auto-rotate, ``s`` save PNG, ``q`` quit.

Everything drawn here comes from :class:`~constraintnet.viz.frame.Frame` snapshots, so the
interactive path and the headless GIF-recording path are the same code -- which is how a
simulation running at 2 tok/s of thinking time still ends up verifiable by eye.
"""

from __future__ import annotations

import os
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg", force=False)  # respects an existing interactive backend if present

from matplotlib.animation import FuncAnimation, PillowWriter  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection  # noqa: E402

from .frame import Frame  # noqa: E402

__all__ = ["Viewer", "record_gif"]

# identity class first (drawn faint), then vivid colours for nontrivial charges
PALETTE = [
    "#9aa0a6",  # vacuum / identity
    "#ff9e64",  # order-2, Z3 element 1
    "#7dcfff",  # order-3 (+)
    "#f7768e",  # order-3 (-)
    "#9ece6a",
    "#bb9af7",
    "#e0af68",
    "#2ac3de",
]


def class_color(index: int, alpha: float = 1.0) -> Tuple[float, float, float, float]:
    hex_value = PALETTE[index % len(PALETTE)]
    rgb = tuple(int(hex_value[i : i + 2], 16) / 255 for i in (1, 3, 5))
    return (*rgb, alpha)


def _density_color(value: float) -> Tuple[float, float, float, float]:
    """Neutral at n = 1, hot where the mesh is dense."""
    t = float(np.clip((value - 1.0) / max(1e-9, 4.0), 0.0, 1.0))
    return (0.35 + 0.65 * t, 0.62 - 0.45 * t, 0.85 - 0.75 * t, 0.95)


class Viewer:
    """Interactive matplotlib window driven by a driver emitting frames."""

    def __init__(
        self,
        driver,
        *,
        interval_ms: int = 60,
        rotate: bool = True,
        show_edges: bool = True,
        show_faces: bool = True,
        show_objects: bool = True,
        show_density: bool = True,
        max_faces: int = 420,
    ):
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Button, CheckButtons, Slider

        self.driver = driver
        self.playing = False
        self.rotate = rotate
        self.show_edges = show_edges
        self.show_faces = show_faces
        self.show_objects = show_objects
        self.show_density = show_density
        self.max_faces = max_faces
        self.azim = -60.0
        self.elev = 18.0

        self.fig = plt.figure(figsize=(15.2, 8.4), dpi=96)
        self.fig.patch.set_facecolor("#16161e")
        grid = self.fig.add_gridspec(
            3, 4, left=0.02, right=0.985, top=0.90, bottom=0.20, wspace=0.16, hspace=0.42
        )
        self.ax = self.fig.add_subplot(grid[:, :3], projection="3d")
        self.ax_readout = self.fig.add_subplot(grid[0:2, 3])
        self.ax_density = self.fig.add_subplot(grid[2, 3])
        for axis in (self.ax, self.ax_readout, self.ax_density):
            axis.set_facecolor("#16161e")

        # ---- controls (single row, generous gaps: this used to overlap the slider label) --
        control_y = 0.058
        self.btn_play = _button(self.fig, (0.025, control_y, 0.075, 0.072), "Play")
        self.btn_step = _button(self.fig, (0.112, control_y, 0.062, 0.072), "Step")
        self.btn_reset = _button(self.fig, (0.186, control_y, 0.075, 0.072), "Reset view")
        self.slider_speed = Slider(
            _axes(self.fig, (0.345, control_y + 0.006, 0.135, 0.042)),
            "speed",
            valmin=1,
            valmax=60,
            valinit=8,
            valstep=1,
            color="#7aa2f7",
        )
        self.toggles = CheckButtons(
            _axes(self.fig, (0.545, control_y - 0.030, 0.42, 0.150)),
            labels=["edges", "faces", "objects", "density", "auto-rotate"],
            actives=[show_edges, show_faces, show_objects, show_density, rotate],
        )
        try:
            self.toggles.set_label(size=9, color="#a9b1d6")
        except Exception:  # pragma: no cover - matplotlib version differences
            for text in getattr(self.toggles, "labels", []):
                text.set_fontsize(9)
                text.set_color("#a9b1d6")
        self.toggles.on_clicked(self._on_toggle)
        self.btn_play.on_clicked(self._on_play)
        self.btn_step.on_clicked(lambda _event: (self.driver.advance(), self._draw(self.driver.frame())))
        self.btn_reset.on_clicked(lambda _event: self.ax.view_init(elev=self.elev, azim=self.azim))
        self.slider_speed.on_changed(lambda value: self._set_interval(int(value)))

        self.fig.text(0.02, 0.955, "constraintnet", color="#c0caf5", fontsize=17, fontweight="bold")
        self.fig.text(
            0.20,
            0.957,
            "coordinates are a projection only -- dynamics never sees them",
            color="#565f89",
            fontsize=10,
            style="italic",
        )
        self.fig.canvas.mpl_connect("key_press_event", self._on_key)

        self._last_frame: Optional[Frame] = None
        self._draw(self.driver.frame())
        self.animation: Optional[FuncAnimation] = None
        self.interval_ms = interval_ms

    # ------------------------------------------------------------------ drawing
    def _draw(self, frame: Frame) -> None:
        ax = self.ax
        ax.cla()
        ax.set_axis_off()
        positions = frame.positions
        if not positions:
            return
        points = np.stack(list(positions.values()))
        span = max(np.abs(points).max(), 1e-6)
        for limit in (ax.set_xlim, ax.set_ylim, ax.set_zlim):
            limit(-span * 1.15, span * 1.15)

        # ---- faces: curvature on triangles -----------------------------------
        if self.show_faces and frame.faces and len(frame.faces) <= self.max_faces:
            polys, colors = [], []
            for triangle, class_id in frame.faces:
                try:
                    verts = [positions[v] for v in triangle]
                except KeyError:
                    continue
                polys.append(verts)
                alpha = 0.10 if class_id == 0 else 0.55
                colors.append(class_color(class_id, alpha))
            if polys:
                collection = Poly3DCollection(polys, facecolors=colors, edgecolors="#2a2e3f", linewidths=0.4)
                ax.add_collection3d(collection)

        # ---- edges: constraint labels ---------------------------------------
        if self.show_edges and frame.edges:
            segments, colors, widths = [], [], []
            for (u, v, class_id) in frame.edges:
                try:
                    segments.append([positions[u], positions[v]])
                except KeyError:
                    continue
                colors.append(class_color(class_id, 0.35 if class_id == 0 else 0.95))
                widths.append(0.6 if class_id == 0 else 1.7)
            lines = Line3DCollection(segments, colors=colors, linewidths=widths)
            ax.add_collection3d(lines)

        # ---- vertices: coloured by local mesh fineness -----------------------
        if positions:
            vertex_colors, sizes = [], []
            for vertex, coord in positions.items():
                n_value = 1.0
                cell = frame.vertex_cell.get(vertex)
                if self.show_density and cell and cell in frame.density:
                    n_value = frame.density[cell][1]
                vertex_colors.append(_density_color(n_value))
                sizes.append(26 + 90 * min(3.0, max(0.0, n_value - 1.0)))
            ax.scatter(
                points[:, 0],
                points[:, 1],
                points[:, 2],
                c=vertex_colors,
                s=sizes,
                depthshade=False,
                edgecolors="#c0caf5",
                linewidths=0.35,
            )

        # ---- persistent objects ---------------------------------------------
        if self.show_objects:
            for mark in frame.objects:
                centre = np.asarray(mark.centroid, dtype=float)
                radius = max(0.05, float(mark.radius))
                ax.scatter(
                    [centre[0]], [centre[1]], [centre[2]],
                    s=900 * radius ** 2, c=[class_color(_label_index(mark.charge), 0.30)],
                    edgecolors="#e0af68", linewidths=1.4, depthshade=False,
                )
                ax.text(centre[0], centre[1], centre[2] + radius * 1.6, mark.label,
                        color="#e0af68", fontsize=8, ha="center")

        # ---- flashes: accepted / rejected attempts --------------------------
        for flash in frame.flashes:
            try:
                a, b = positions[flash.edge[0]], positions[flash.edge[1]]
            except KeyError:
                continue
            mid = (a + b) / 2.0
            fade = max(0.0, 1.0 - flash.age)
            if flash.kind == "accept":
                ax.scatter([mid[0]], [mid[1]], [mid[2]], s=170 * fade + 30,
                           c=[(0.62, 0.85, 0.45, 0.85 * fade)], marker="^", depthshade=False)
            else:
                ax.scatter([mid[0]], [mid[1]], [mid[2]], s=150 * fade + 25,
                           c=[(0.97, 0.42, 0.52, 0.9 * fade)], marker="x", linewidths=2.2, depthshade=False)

        # ---- travelling test signals ----------------------------------------
        for pulse in frame.pulses:
            path = [positions[v] for v in pulse.path if v in positions]
            if len(path) < 2:
                continue
            stacked = np.stack(path)
            ax.plot(stacked[:, 0], stacked[:, 1], stacked[:, 2],
                    color="#7aa2f7", alpha=0.35, linewidth=1.0)
            head = _interpolate(stacked, pulse.progress)
            trail_start = max(0.0, pulse.progress - 0.18)
            tail = np.stack([_interpolate(stacked, t) for t in np.linspace(trail_start, pulse.progress, 6)])
            ax.plot(tail[:, 0], tail[:, 1], tail[:, 2], color="#7dcfff", alpha=0.8, linewidth=2.4)
            ax.scatter([head[0]], [head[1]], [head[2]], s=150, c="#ffffff", marker="*", depthshade=False)

        # ---- legend ----------------------------------------------------------
        handles = [Patch(facecolor=class_color(i, 0.9), label=text) for i, text in enumerate(frame.edge_class_labels)]
        ax.legend(handles=handles, loc="upper left", fontsize=7.5, framealpha=0.25,
                  facecolor="#1f2330", labelcolor="#c0caf5")

        if self.rotate:
            self.azim = (self.azim + 1.6) % 360
        ax.view_init(elev=self.elev, azim=self.azim)
        ax.set_title(frame.title or "constraintnet", color="#c0caf5", fontsize=12, pad=4)

        self._draw_readout(frame)
        self._draw_density(frame)
        self._last_frame = frame

    def _draw_readout(self, frame: Frame) -> None:
        ax = self.ax_readout
        ax.cla()
        ax.set_axis_off()
        lines: List[str] = []
        for key, value in frame.counters.items():
            lines.append(f"{key:>20s} : {value}")
        lines.append("")
        lines.append("event log")
        for entry in frame.log[-7:]:
            lines.append(entry[:46])
        if frame.note:
            lines.append("")
            lines.append(_wrap(frame.note, 40))
        ax.text(0.0, 1.0, "\n".join(lines), color="#a9b1d6", fontsize=8.2, family="monospace", va="top")

    def _draw_density(self, frame: Frame) -> None:
        ax = self.ax_density
        ax.cla()
        if not (self.show_density and frame.density):
            ax.set_axis_off()
            return
        cells = sorted(frame.density.items(), key=lambda kv: -kv[1][1])[:12]
        names = [name for name, _ in cells]
        values = [value[1] for _, value in cells]
        colours = [_density_color(value) for value in values]
        ax.barh(range(len(names)), values, color=colours)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=7.5, color="#a9b1d6")
        ax.invert_yaxis()
        ax.tick_params(axis="x", labelsize=7.5, colors="#a9b1d6")
        for spine in ax.spines.values():
            spine.set_color("#3b4261")
        ax.set_title("mesh fineness  n = rho/rho0", color="#c0caf5", fontsize=9)

    # ------------------------------------------------------------- interaction
    def _on_play(self, _event=None):
        self.playing = not self.playing
        self.btn_play.label.set_text("Pause" if self.playing else "Play")
        self.fig.canvas.draw_idle()

    def _set_interval(self, steps_per_frame: int) -> None:
        self.steps_per_frame = max(1, int(steps_per_frame))

    def _on_toggle(self, label: str):
        mapping = {
            "edges": "show_edges",
            "faces": "show_faces",
            "objects": "show_objects",
            "density": "show_density",
            "auto-rotate": "rotate",
        }
        attribute = mapping.get(label)
        if attribute:
            current = getattr(self, attribute)
            setattr(self, attribute, not current)
            self._draw(self.driver.frame())

    def _on_key(self, event):
        key = (event.key or "").lower()
        if key in (" ", "p"):
            self._on_play()
        elif key == "right":
            for _ in range(getattr(self, "steps_per_frame", 8)):
                self.driver.advance()
            self._draw(self.driver.frame())
        elif key == "e":
            self.show_edges = not self.show_edges
            self._draw(self.driver.frame())
        elif key == "f":
            self.show_faces = not self.show_faces
            self._draw(self.driver.frame())
        elif key == "o":
            self.show_objects = not self.show_objects
            self._draw(self.driver.frame())
        elif key == "d":
            self.show_density = not self.show_density
            self._draw(self.driver.frame())
        elif key == "r":
            self.rotate = not self.rotate
        elif key == "s":
            self.fig.savefig("constraintnet_frame.png", dpi=150, facecolor=self.fig.get_facecolor())
        elif key in ("q", "escape"):
            plt_close()

    # ------------------------------------------------------------------- loops
    def _tick(self, _frame_number: int):
        if self.playing:
            for _ in range(getattr(self, "steps_per_frame", 8)):
                if self.driver.done:
                    break
                self.driver.advance()
        self._draw(self.driver.frame())
        return []

    def run(self) -> None:
        """Start the animation loop and open the interactive window."""
        import matplotlib.pyplot as plt

        self.playing = True
        self.btn_play.label.set_text("Pause")
        self.animation = FuncAnimation(
            self.fig, self._tick, interval=self.interval_ms, blit=False, cache_frame_data=False
        )
        plt.show()


def record_gif(
    driver,
    path: str,
    frames: int = 160,
    interval_ms: int = 70,
    steps_per_frame: int = 6,
    **kwargs,
) -> str:
    """Render a driver to an animated GIF without needing a display."""
    viewer = Viewer(driver, **kwargs)
    viewer.playing = True
    viewer.steps_per_frame = max(1, int(steps_per_frame))
    animation = FuncAnimation(
        viewer.fig, viewer._tick, frames=frames, interval=interval_ms, blit=False, cache_frame_data=False
    )
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    animation.save(path, writer=PillowWriter(fps=max(2, int(1000 / max(1, interval_ms)))))
    return path


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def _axes(fig, rect):
    axis = fig.add_axes(rect)
    axis.set_facecolor("#1f2330")
    for spine in axis.spines.values():
        spine.set_color("#3b4261")
    return axis


def _button(fig, rect, label):
    from matplotlib.widgets import Button

    button = Button(_axes(fig, rect), label, color="#2f3549", hovercolor="#3b4261")
    button.label.set_color("#c0caf5")
    button.label.set_fontsize(10)
    return button


def _interpolate(stacked: np.ndarray, progress: float) -> np.ndarray:
    t = float(np.clip(progress, 0.0, 1.0)) * (len(stacked) - 1)
    lower = int(np.floor(t))
    upper = min(len(stacked) - 1, lower + 1)
    fraction = t - lower
    return stacked[lower] * (1 - fraction) + stacked[upper] * fraction


def _label_index(text: str) -> int:
    """Map a charge description onto a palette slot deterministically."""
    if not text or "identity" in text.lower() or text == "e":
        return 0
    words = {"order-2": 1, "double": 1, "(+)": 2, "+": 2, "(-)": 3, "-": 3}
    for key, index in words.items():
        if key in text:
            return index
    return 1 + (abs(hash(text)) % (len(PALETTE) - 1))


def _wrap(text: str, width: int) -> str:
    import textwrap

    return "\n".join(textwrap.wrap(text, width=width))


def plt_close() -> None:
    import matplotlib.pyplot as plt

    plt.close("all")
