"""The visualization layer must work headless and deterministically.

No test here opens a window: the renderer is exercised through the same code path used for
GIF recording, which is exactly the guarantee that CI can watch the simulation too.
"""

from __future__ import annotations

import numpy as np
import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg", force=True)

from constraintnet.seeds import kuhn_ball  # noqa: E402
from constraintnet.viz.drivers import LatticeDriver, OrbitTourDriver, TetraDriver, shortest_path  # noqa: E402
from constraintnet.viz.frame import build_frame  # noqa: E402
from constraintnet.viz.layout import force_directed, from_grid, positions  # noqa: E402


class TestLayout:
    def test_grid_metadata_is_preferred(self):
        cx = kuhn_ball("Z3", n=1)
        coords = positions(cx)
        assert set(coords) == set(cx.vertices())
        values = np.stack(list(coords.values()))
        assert np.abs(values).max() == pytest.approx(1.0)

    def test_force_directed_is_deterministic(self):
        cx = kuhn_ball("Z3", n=1)
        first = force_directed(cx, seed=3)
        second = force_directed(cx, seed=3)
        for vertex in cx.vertices():
            assert np.allclose(first[vertex], second[vertex])

    def test_force_directed_spreads_vertices(self):
        cx = kuhn_ball("Z3", n=1)
        coords = force_directed(cx, seed=1)
        values = np.stack(list(coords.values()))
        # no two vertices should collapse onto each other
        pairwise = np.linalg.norm(values[:, None, :] - values[None, :, :], axis=-1)
        np.fill_diagonal(pairwise, 1.0)
        assert pairwise.min() > 1e-3

    def test_layout_never_reads_dynamics(self):
        """Positions must not depend on labels -- they are a projection only."""
        from constraintnet.seeds import randomize_labels

        cx = kuhn_ball("Z3", n=1)
        before = positions(cx, method="force", seed=2)
        randomize_labels(cx, seed=99)
        after = positions(cx, method="force", seed=2)
        for vertex in cx.vertices():
            assert np.allclose(before[vertex], after[vertex])


class TestFrames:
    def test_tetra_frame_contents(self):
        driver = TetraDriver(group="A4", seed=1)
        frame = driver.frame()
        assert len(frame.edges) == 6
        assert len(frame.faces) == 4
        assert len(frame.edge_class_labels) == 4
        assert all(0 <= cid < 4 for (_, _, cid) in frame.edges)

    def test_lattice_frame_tracks_density_and_objects(self):
        driver = LatticeDriver(group="A4", n=1, seed=2, signal_every=5)
        for _ in range(60):
            driver.advance()
        frame = driver.frame()
        assert frame.density, "observer cells should have recorded events"
        assert any(n > 1.0 for _, n in frame.density.values())
        assert frame.counters["step"] == "60"

    def test_signals_follow_real_paths(self):
        """Every pulse must travel along existing edges (0 and 7 are cube-diagonal neighbours,
        so the shortest path can legitimately be a single hop)."""
        cx = kuhn_ball("A4", n=1)
        vertices = sorted(cx.vertices())
        for source, target in ((vertices[0], vertices[-1]), (vertices[0], vertices[len(vertices) // 2])):
            path = shortest_path(cx, source, target)
            assert path and path[0] == source and path[-1] == target
            for u, v in zip(path, path[1:]):
                assert cx.has_edge(u, v)

    def test_orbit_tour_covers_distinct_states(self):
        driver = OrbitTourDriver(group="A4", dwell=1)
        seen = set()
        for _ in range(20):
            driver.advance()
            seen.add(tuple(map(repr, driver.orbits[driver.index])))
        assert len(seen) > 1


class TestRendererHeadless:
    def test_viewer_draws_and_saves(self, tmp_path):
        from constraintnet.viz.render import Viewer

        driver = TetraDriver(group="A4", seed=4)
        viewer = Viewer(driver, rotate=True)
        for _ in range(10):
            driver.advance()
        viewer._tick(0)
        out = tmp_path / "frame.png"
        viewer.fig.savefig(out, dpi=90, facecolor=viewer.fig.get_facecolor())
        assert out.exists() and out.stat().st_size > 5_000

    def test_layer_toggles_do_not_break_drawing(self, tmp_path):
        from constraintnet.viz.render import Viewer

        driver = LatticeDriver(group="A4", n=1, seed=3)
        viewer = Viewer(driver)
        for label in ("faces", "edges", "objects", "density"):
            viewer._on_toggle(label)
            viewer._draw(driver.frame())
        out = tmp_path / "layers.png"
        viewer.fig.savefig(out, dpi=80, facecolor=viewer.fig.get_facecolor())
        assert out.exists()

    def test_gif_recording_pipeline(self, tmp_path):
        from constraintnet.viz.render import record_gif

        driver = TetraDriver(group="Z3", seed=6)
        path = tmp_path / "tiny.gif"
        record_gif(driver, str(path), frames=2, interval_ms=10, steps_per_frame=1)
        assert path.exists() and path.stat().st_size > 1_000
