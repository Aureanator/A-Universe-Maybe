"""Independent small controls for exact landscape enumeration."""

import itertools

import pytest

from constraintnet.gauge import gauge_fix_spanning_tree
from constraintnet.complex import spanning_tree
from constraintnet.landscape import curvature_action, enumerate_landscape, Landscape
from constraintnet.seeds import make_tetrahedron_boundary


def test_z2_landscape_matches_full_unfixed_edge_enumeration():
    cx = make_tetrahedron_boundary("Z2")
    edges = cx.edges()
    original = cx.labels_snapshot()
    result = enumerate_landscape(cx)
    assert cx.labels_snapshot() == original
    tree, _ = spanning_tree(edges)
    adjacency = {s: set() for s in result.energy}
    energies = {}

    def key(scratch):
        gauge_fix_spanning_tree(scratch, tree)
        return tuple(scratch.label(*edge) for edge in result.free_edges)

    for raw in itertools.product((0, 1), repeat=len(edges)):
        state = cx.copy()
        for edge, value in zip(edges, raw):
            state.set_label(*edge, value)
        source = key(state.copy())
        energies[source] = curvature_action(state)
        for edge in edges:
            other = state.copy()
            other.set_label(*edge, 1 - other.label(*edge))
            adjacency[source].add(key(other))
    assert adjacency == result.adjacency
    assert energies == result.energy


def test_plateau_with_late_downhill_exit_is_not_metastable():
    graph = Landscape((), {(0,): 0, (1,): 2, (2,): 2},
                      {(0,): {(1,)}, (1,): {(0,), (2,)}, (2,): {(1,)}}, {}, 3, 4)
    plateau = graph.plateaus()[1]
    assert plateau["states"] == {(1,), (2,)}
    assert plateau["downhill_exits"] == {(0,)}
    assert graph.nonincreasing_distances() == {(0,): 0, (1,): 1, (2,): 2}


def test_landscape_budget_checked_before_enumeration():
    with pytest.raises(ValueError, match="proposals"):
        enumerate_landscape(make_tetrahedron_boundary("A4"), max_proposals=10)
