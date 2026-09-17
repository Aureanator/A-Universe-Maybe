"""R1 tests: driver interface contracts + kernel purity (T1, T2 of the refactor spec)."""

from __future__ import annotations

import pathlib
import re

import pytest

from constraintnet.drivers import (
    DriverA,
    DriverB,
    canonical_orbit_of_triple,
    orbit_sigma_well_definedness,
)
from constraintnet.groups import AlternatingGroup4
from constraintnet.region import Region
from constraintnet.seeds import make_tetrahedron_boundary

KERNEL_MODULES = [
    # pure relational mathematics: RNG must be unreachable here
    "complex.py",
    "groups.py",
    "holonomy.py",
    "gauge.py",
    "region.py",
    "resolutions.py",
    "objects.py",
    "interaction.py",
    "observer.py",
    "reps.py",
    "fringe.py",
    "sectors.py",
    "sheaf.py",
]
# PENDING MIGRATION (contain stochastic harnesses, to move behind drivers):
# dynamics.py, persistence.py (run_persistence_experiment), seeds.py (randomize_labels),
# moves.py (propose_edge_move takes rng).  DriverA's random in drivers.py is LEGAL.


# ------------------------------------------------------------------ T2 kernel purity
@pytest.mark.parametrize("module_name", KERNEL_MODULES)
def test_kernel_module_has_no_rng(module_name):
    """RNG must be unreachable from the KERNEL core: no imports, no calls."""
    source = (pathlib.Path(__file__).resolve().parents[1] / "src/constraintnet" / module_name).read_text(
        encoding="utf-8"
    )
    # strip docstrings crudely for call detection, but even IMPORTS are banned
    assert not re.search(r"^\s*(import random|from random)\b", source, re.MULTILINE), module_name
    assert "random." not in source.replace("randomize_labels", ""), module_name
    assert "np.random" not in source and "numpy.random" not in source, module_name


# ------------------------------------------------------------------ T1 DriverB reversibility
def test_driver_b_bijective_and_clock_spectrum():
    driver = DriverB(AlternatingGroup4())
    total = sum(count * length for length, count in driver.clock_spectrum().items())
    assert total == 12**3  # exhaustive: every slice state lies on exactly one cycle


def test_driver_b_full_cycle_returns_to_start():
    driver = DriverB(AlternatingGroup4(), generator=None)
    start = driver.state
    _, length = driver.cycles.index_of[start]
    for _ in range(length):
        driver.advance()
    assert driver.state == start


def test_driver_b_exact_inverse_roundtrip():
    group = AlternatingGroup4()
    driver = DriverB(group)
    # move to a nontrivial state deterministically
    origin = driver.state
    for _ in range(7):
        driver.advance()
    middle = driver.state
    for _ in range(7):
        driver.inverse_advance()
    assert driver.state == origin
    # and the inverse map agrees with sigma^-1 everywhere (bijection check)
    for state in driver.states[:200]:
        forward = driver._sigma_map[state]
        assert driver._inverse_map[forward] == state


def test_driver_b_phase_reported_and_orbit_observable_gauge_invariant():
    group = AlternatingGroup4()
    driver = DriverB(group)
    record = driver.advance()
    assert record.phase is not None and record.counts_toward_rho
    position, length = record.phase
    assert 0 <= position < length
    # orbit observable is constant along conjugation, varies along the slice generally
    from constraintnet.drivers import conjugate_triple

    state = driver.state
    lam = group.elements[5]
    assert canonical_orbit_of_triple(group, state) == canonical_orbit_of_triple(
        group, conjugate_triple(group, state, lam)
    )


# ------------------------------------------------------------------ the canonicalization trap
def test_sigma_is_NOT_well_defined_on_orbits():
    """Right-multiplication does not commute with conjugation: 'multiply then
    re-canonicalize' fails to descend to gauge orbits.  DriverB therefore churns on the
    RAW SLICE and canonicalizes only for observables."""
    verdict = orbit_sigma_well_definedness(AlternatingGroup4())
    assert verdict["well_defined_on_orbits"] is False


# ------------------------------------------------------------------ DriverA contract
def test_driver_a_fate_trichotomy_and_determinism():
    def run(seed):
        cx = make_tetrahedron_boundary("Z3")
        seed_charged_defect_z3(cx)
        driver = DriverA(cx, region=Region(cx, cx.tetrahedra(), "whole"), rng_seed=seed)
        return [(r.fate, r.counts_toward_rho, r.detail) for _ in range(40) for r in [driver.advance()]]

    first = run(3)
    second = run(3)
    assert first == second  # deterministic under fixed seed
    fates = {f for f, _, _ in first}
    assert fates <= {"accepted", "vetoed"}
    for fate, counts, _ in first:
        assert counts == (fate == "accepted")  # ontology honored per record


def seed_charged_defect_z3(cx):
    """Minimal Z3 analogue of the charged seed (keeps this test independent of A4)."""
    edges = sorted(cx.edges())
    cx.set_label(*edges[0], 1)
