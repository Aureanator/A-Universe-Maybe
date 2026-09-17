"""R2/R3-lite tests: fiber products, exclusion, odometer scheduler, T3 consistency."""

from __future__ import annotations

import random

from constraintnet.drivers import DriverB
from constraintnet.groups import AlternatingGroup4, CyclicGroup
from constraintnet.interaction import (
    actualize_min_cost,
    compatible_on_shared_face,
    fiber_product,
    meshable_phases,
)


def _setup(group):
    e = group.identity()
    shared_edges = [((0, 1), e), ((1, 2), e), ((0, 2), e)]
    index = {0: 0, 1: 1, 2: 2}
    return shared_edges, index


# ------------------------------------------------------------------ compatibility
def test_compatibility_known_cases():
    g = CyclicGroup(3)
    shared, index = _setup(g)
    assert compatible_on_shared_face(g, (0, 0, 0, 1), (0, 0, 0), shared, index, index)
    assert not compatible_on_shared_face(g, (0, 0, 0, 0), (1, 0, 0), shared, index, index)


def test_fiber_product_symmetry_and_emptiness():
    g = AlternatingGroup4()
    shared, index = _setup(g)
    e = g.identity()
    a_fixed = (e, e, e, e)
    # every b compatible with itself-matching flux: construct one explicitly
    joint = fiber_product(g, [a_fixed], [a_fixed[:3]], shared, index, index)
    assert joint == [(a_fixed, a_fixed[:3])]
    empty = fiber_product(
        g, [(e, e, e, e)], [(g.move_generators()[0], e, e)], shared, index, index
    )
    assert empty == []  # forbidden channel: incompatible bookkeeping, no force needed


# ------------------------------------------------------------------ odometer scheduler
def test_odometer_single_cycle():
    g = CyclicGroup(3)
    driver = DriverB(g, k=2, mode="odometer")
    assert len(driver.cycles.lengths) == 1 and driver.cycles.lengths[0] == 9
    h = AlternatingGroup4()
    d2 = DriverB(h, k=2, mode="odometer")
    assert len(d2.cycles.lengths) == 1 and d2.cycles.lengths[0] == 144


def test_odometer_reversible_via_history():
    driver = DriverB(CyclicGroup(3), k=2, mode="odometer")
    origin = driver.state
    for _ in range(5):
        driver.advance()
    for _ in range(5):
        driver.inverse_advance()
    assert driver.state == origin


# ------------------------------------------------------------------ exact vs sampled (T3 miniature)
def test_phase_measure_equals_stochastic_accept_rate():
    g = CyclicGroup(3)
    shared, index = _setup(g)
    objA = DriverB(g, k=4, mode="odometer")
    probeB = DriverB(g, k=3, mode="odometer")

    def full_cycle(driver):
        state, out = driver.states[0], []
        for _ in range(len(driver.states)):
            out.append(state)
            state = driver._sigma_map[state]
        return out

    cycle_a, cycle_b = full_cycle(objA), full_cycle(probeB)
    matrix = meshable_phases(g, cycle_a, cycle_b, shared, index, index)
    flat = [cell for row in matrix for cell in row]
    exact = sum(flat) / len(flat)

    rng = random.Random(11)
    n = 4000
    accepted = sum(
        compatible_on_shared_face(
            g, cycle_a[rng.randrange(len(cycle_a))], cycle_b[rng.randrange(len(cycle_b))], shared, index, index
        )
        for _ in range(n)
    )
    assert abs(accepted / n - exact) < 0.05  # agreement within sampling error


# ------------------------------------------------------------------ deterministic selection
def test_actualize_min_cost_rules():
    g = AlternatingGroup4()
    e = g.identity()
    current = (e, e, e, e)
    assert actualize_min_cost(g, current, []) is None            # forbidden: no selection
    assert actualize_min_cost(g, current, [current, (e, e, e, g.move_generators()[0])]) == current
    # deterministic tie-break: identical costs resolve by repr, reproducibly
    allowed = [(g.elements[3], e), (g.elements[5], e)]
    first = actualize_min_cost(g, (e, e), allowed)
    second = actualize_min_cost(g, (e, e), list(reversed(allowed)))
    assert first == second
