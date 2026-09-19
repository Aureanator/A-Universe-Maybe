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
# ------------------------------------------------------------------ R3 absorption invariants
def _a4_pieces():
    g = AlternatingGroup4()
    e = g.identity()
    o2 = next(x for x in g.elements if g.order_of(x) == 2)
    o3 = next(x for x in g.elements if g.order_of(x) == 3)
    return g, e, o2, o3


def _shared(g, boundary):
    return [((0, 1), boundary[0]), ((1, 2), boundary[1]), ((0, 2), boundary[2])]


IDX = {0: 0, 1: 1, 2: 2}


# R3 F4 regression coverage lives in tests/test_interaction_frames.py: the honest apex
# gauge action is LEFT MULTIPLICATION x_i -> nu^-1 x_i (Astra's note); an earlier version
# of this file tested per-spoke CONJUGATION, which is not a gauge action at all -- it
# conjugates flux AND boundary label jointly and its verdict-preservation was incidental.
# The frames suite exhaustively verifies independent apex frames under the true action.


def test_legacy_raw_full_ensemble_absorption_is_phase_invariant():
    """LEGACY CONTROL (matching='raw'): raw-equality absorption is phase-invariant.
    This pin encodes the fixed-frame convention, NOT a physical statement -- under
    gauge-invariant conventions absorption IS phase-modulated (see next test)."""
    g, e, o2, o3 = _a4_pieces()
    from constraintnet.drivers import odometer_state

    n_y = 12**3
    counts_seen = {}
    for boundary in [(e, e, e), (o2, o3, e)]:
        edges = _shared(g, boundary)
        for phi in range(0, n_y, 96):
            x = odometer_state(g, 3, phi)
            c = sum(
                compatible_on_shared_face(g, x, odometer_state(g, 3, j), edges, IDX, IDX,
                                          matching="raw")
                for j in range(n_y)
            )
            counts_seen.setdefault(str(boundary[1]), set()).add(c)
    assert all(len(v) == 1 for v in counts_seen.values())  # one count per boundary type


def test_absorption_phase_structure_is_convention_dependent():
    """R3 F4 supersession, measured exactly (deterministic 18-phase grid, no RNG).

    The old 'phase-invariant absorption' pin was a RAW-equality artifact. Under the
    gauge-invariant conventions the phase structure of the absorption cross-section is
    ITSELF convention-dependent -- measured distinct counts over phases 0,96,...,1632:

      boundary (e,e,e):   classes {12,36,48,144,192}   relational {12,36,48,144}
      boundary (o2,o3,e): classes {36,108,144,192}     relational {36}

    Under honest simultaneous-frame matching a CURVED-boundary probe ensemble absorbs at
    exactly 36 for every internal phase (trivial stabilizer of the flux tuple saturates
    the orbit), while flat-boundary absorption stays phase-modulated. Duty-cycle physics
    survives, but its shape is part of the declared interaction model, not free data.
    """
    g, e, o2, o3 = _a4_pieces()
    from constraintnet.drivers import odometer_state

    n_y = 12**3
    expected = {
        ((e, e, e), "classes"): {12, 36, 48, 144, 192},
        ((e, e, e), "relational"): {12, 36, 48, 144},
        ((o2, o3, e), "classes"): {36, 108, 144, 192},
        ((o2, o3, e), "relational"): {36},
    }
    for (boundary, mode), want in expected.items():
        edges = _shared(g, boundary)
        counts = set()
        for phi in range(0, n_y, 96):
            x = odometer_state(g, 3, phi)
            c = sum(
                compatible_on_shared_face(g, x, odometer_state(g, 3, j), edges, IDX, IDX,
                                          matching=mode)
                for j in range(n_y)
            )
            counts.add(c)
        assert counts == want, f"{boundary[1]} / {mode}: got {sorted(counts)}, want {sorted(want)}"


def test_cross_section_ratio_all_three_conventions():
    """R3 F4: the same probe (x = slice phase 0) against flat vs curved shared boundaries,
    measured under every declared convention. The old '12 vs 3 = x4 suppression' is a
    RAW-equality artifact; gauge-invariant conventions measure flat 12 : curved 36 --
    curvature ENHANCES joint-resolvable frames x3 for this state, not suppresses.
    Relational happens to agree numerically with classes on these two flux tuples
    (trivial stabilizer / identity flux); the frames suite shows they differ elsewhere."""
    g, e, o2, o3 = _a4_pieces()
    from constraintnet.drivers import odometer_state

    x = odometer_state(g, 3, 0)
    n_y = 12**3

    def count(boundary, mode):
        edges = _shared(g, boundary)
        return sum(
            compatible_on_shared_face(g, x, odometer_state(g, 3, j), edges, IDX, IDX,
                                      matching=mode)
            for j in range(n_y)
        )

    assert count((e, e, e), "raw") == 12 and count((o2, o3, e), "raw") == 3   # legacy x4
    assert count((e, e, e), "classes") == 12 and count((o2, o3, e), "classes") == 36
    assert count((e, e, e), "relational") == 12 and count((o2, o3, e), "relational") == 36


def test_abelian_blind_to_curvature():
    gz = CyclicGroup(3)
    ez = gz.identity()
    from constraintnet.drivers import odometer_state

    x = odometer_state(gz, 3, 5)
    n_y = 27

    def count(boundary):
        edges = _shared(gz, boundary)
        return sum(
            compatible_on_shared_face(gz, x, odometer_state(gz, 3, j), edges, IDX, IDX)
            for j in range(n_y)
        )

    assert count((ez, ez, ez)) == count((1, 2, 0))


def test_prepared_probe_reveals_clock_gating():
    g, e, o2, o3 = _a4_pieces()
    from constraintnet.drivers import odometer_state

    edges = _shared(g, (e, e, e))
    probes = [(o3, e, e), (e, o2, e), (e, e, o3)]
    rates = [
        sum(compatible_on_shared_face(g, odometer_state(g, 3, phi), p, edges, IDX, IDX) for p in probes)
        / len(probes)
        for phi in range(12**3)
    ]
    assert max(rates) > min(rates)  # phase-locking real against prepared probes


def test_protocol_outcome_semantics():
    from constraintnet.interaction import phase_locked_outcomes

    g, e, o2, o3 = _a4_pieces()
    edges = _shared(g, (o2, o3, e))
    res = phase_locked_outcomes(
        g, [(e, e, e), (o3, e, e)], [(e, e, e), (o2, e, e)], edges, IDX, IDX, cap_K=5
    )
    assert abs(res["duty_cycle"] + res["deferred_fraction"] + res["scatter_fraction"] - 1.0) < 1e-12
    assert set(res["wait_histogram"].keys()) <= {None, *range(6)}


def test_stride_equal_gcd_identical_rate():
    g, e, o2, o3 = _a4_pieces()
    from constraintnet.drivers import odometer_state
    from constraintnet.interaction import stride_scan

    edges = _shared(g, (o2, o3, e))
    probes = [(o3, e, e)]
    rates = stride_scan(
        g, lambda ph: odometer_state(g, 3, ph), 12**3, probes, edges, IDX, IDX,
        periods=[5, 7, 4, 20], hits=12**3,
    )
    assert rates[5] == rates[7]      # gcd 1: both visit every phase (guaranteed)
    assert rates[4] == rates[20]     # gcd(4,L) == gcd(20,L) == 4: same coset (guaranteed)
    # NB: different-gcd periods can coincide by accident of the profile -- never assert that


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
