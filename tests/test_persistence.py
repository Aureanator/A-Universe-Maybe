"""Spec Test 5 (persistent-defect conservation) + M4 persistence semantics.

Deterministic seeds; each experiment run is ~1 s.
"""

from __future__ import annotations

import pytest

from constraintnet.persistence import (
    DefectTracker,
    is_persistent,
    run_persistence_experiment,
    seed_charged_defect,
    seed_neutral_defect,
)
from constraintnet.objects import curved_faces, face_clusters
from constraintnet.region import Region
from constraintnet.seeds import kuhn_ball


@pytest.fixture(scope="module")
def charged_run():
    return run_persistence_experiment(kind="charged", steps=300, rng_seed=7)


@pytest.fixture(scope="module")
def neutral_run():
    return run_persistence_experiment(kind="neutral", steps=300, rng_seed=7)


# --------------------------------------------------------------------- conservation
def test_sector_conserved(charged_run, neutral_run):
    """The gauge-invariant sector of the universe never changes (spec Test 5)."""
    assert charged_run["sector_conserved"]
    assert neutral_run["sector_conserved"]


def test_charged_defect_persists(charged_run):
    assert charged_run["matter"] is True
    assert charged_run["charge_core_size"] == 2          # two frozen boundary faces
    assert charged_run["frozen_core_classes_stable"] is True
    assert charged_run["survival_ratio"] == 1.0
    assert charged_run["gaps"] == 0
    assert charged_run["is_persistent"] is True


def test_neutral_lump_is_not_matter(neutral_run):
    """Trivial external signature => nothing protects it, by definition and by predicate."""
    assert neutral_run["matter"] is False
    assert neutral_run["charge_core_size"] == 0
    assert neutral_run["is_persistent"] is False


# --------------------------------------------------------------------- confinement
def test_confinement_surface_moves_never_accepted(charged_run):
    """No single surface relabelling ever preserved the appearance: charge cannot leak."""
    assert charged_run["accepted_surface"] == 0
    assert charged_run["rejected_surface"] > 100


def test_interior_moves_never_rejected(charged_run, neutral_run):
    """Theorem: interior edges touch no observed face and no probe cycle."""
    assert charged_run["rejected_interior"] == 0
    assert neutral_run["rejected_interior"] == 0


# --------------------------------------------------------------------- guards
def test_core_stability_detects_manual_tampering():
    """charge_core_stable must not be vacuously true: break conservation by hand, see it fail."""
    cx = kuhn_ball(group="A4", n=2)
    info = seed_charged_defect(cx)
    region = Region(cx, cx.tetrahedra(), "universe")
    core = frozenset((f, c) for f, c in region.appearance().face_curvatures if c != 0)
    tracker = DefectTracker(cx)
    defect = tracker.adopt(max(face_clusters(cx, curved_faces(cx)), key=len), step=0, charge_core=core)
    assert defect.charge_core_stable(cx)

    # overwrite the charge-carrying edge with the identity -- an illegitimate external rewrite
    cx.set_label(*info["edge"], cx.group.identity())
    assert not defect.charge_core_stable(cx)


def test_seeds_reject_wrong_domain():
    """Charged seeds must live on the surface; neutral interior seeds are separate calls."""
    cx = kuhn_ball(group="A4", n=2)
    region = Region(cx, cx.tetrahedra(), "universe")
    interior = region.interior_edges()[0]
    with pytest.raises(ValueError):
        seed_charged_defect(cx, edge=tuple(interior))
