"""Observer coarse-graining: cells are relational, density raises delay."""

from __future__ import annotations

import pytest

from constraintnet.observer import Observer, shells_from
from constraintnet.seeds import kuhn_ball


def test_shells_are_graph_distance_not_coordinates():
    cx = kuhn_ball("Z3", n=1)
    centre = min(cx.vertices())
    shells = shells_from(cx, centre)
    assert centre in shells[0]
    # every vertex appears exactly once across all shells
    seen = [v for members in shells.values() for v in members]
    assert sorted(seen) == cx.vertices()
    # neighbours of a shell-0 vertex live in shell 1
    first_neighbour = min(cx.adjacent(centre))
    assert first_neighbour in shells[1]


def test_density_and_mesh_fineness():
    cx = kuhn_ball("Z3", n=2)
    observer = Observer(cx, centre=min(cx.vertices()))
    hot_cell = max(observer.cells, key=lambda name: len(observer.cells[name]))

    for _ in range(50):
        observer.record_vertices(sorted(observer.cells[hot_cell])[:3], weight=1.0)

    rho_hot, n_hot = observer.density_field()[hot_cell]
    assert rho_hot > 0
    assert n_hot > 1.0, "a loaded cell must read finer than the uniform baseline"
    assert all(n >= 0.0 for _, n in observer.density_field().values())


def test_dense_cells_cost_more_to_traverse():
    cx = kuhn_ball("Z3", n=1)
    vertices = sorted(cx.vertices())
    path = [vertices[0]] + [v for v in vertices if v != vertices[0]][:4]

    clean = Observer(cx, centre=vertices[0])
    delay_vacuum = clean.propagation_delay(path)
    assert delay_vacuum == pytest.approx(len(path) - 1)

    loaded = Observer(cx, centre=vertices[0])
    for _ in range(200):
        loaded.record_vertices(path[1:], weight=1.0)
    delay_dense = loaded.propagation_delay(path)
    assert delay_dense > delay_vacuum, "signals must cost more where the mesh is denser"


def test_baseline_is_the_population_aware_uniform_expectation():
    cx = kuhn_ball("Z3", n=1)
    observer = Observer(cx, centre=min(cx.vertices()))
    observer.record_vertices(sorted(observer.cells["shell1"]), weight=4.0)
    total_vertices = sum(len(m) for m in observer.cells.values())
    assert observer.rho0 == pytest.approx(observer.total_events / total_vertices)
    # concentration means some cells sit above the baseline and the rest below it
    values = [n for _, n in observer.density_field().values()]
    assert max(values) > 1.0 >= min(values)


def test_equal_activity_reads_equal_density_regardless_of_cell_size():
    """Referee audit item 13 regression: raw per-cell counts confound activity with shell
    population; the fineness factor must not."""
    cx = kuhn_ball("Z3", n=2)
    observer = Observer(cx, centre=min(cx.vertices()))
    small = min(observer.cells, key=lambda c: len(observer.cells[c]))
    large = max(observer.cells, key=lambda c: len(observer.cells[c]))
    assert len(observer.cells[small]) < len(observer.cells[large])
    # identical activity PER VERTEX in both cells
    for v in observer.cells[small]:
        observer.record_vertices([v], weight=2.0)
    for v in observer.cells[large]:
        observer.record_vertices([v], weight=2.0)
    assert observer.n_factor(small) == pytest.approx(observer.n_factor(large))
    # while the raw counts differ by population -- that was the artifact
    ratio = observer.rho(large) / observer.rho(small)
    assert ratio == pytest.approx(len(observer.cells[large]) / len(observer.cells[small]))


def test_delay_report_is_human_readable():
    cx = kuhn_ball("Z3", n=1)
    vertices = sorted(cx.vertices())
    observer = Observer(cx, centre=vertices[0])
    report = observer.delay_report(vertices[:5])
    assert "hops" in report and "reduction steps" in report
