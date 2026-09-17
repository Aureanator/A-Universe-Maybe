"""Shared fixtures for the constraintnet test-suite."""

from __future__ import annotations

import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:  # works even when pytest's pythonpath ini is bypassed
    sys.path.insert(0, SRC)

from constraintnet.groups import AlternatingGroup4, CyclicGroup  # noqa: E402
from constraintnet.holonomy import bianchi_defect  # noqa: E402
from constraintnet.region import Region  # noqa: E402
from constraintnet.seeds import (  # noqa: E402
    kuhn_ball,
    make_bipyramid,
    make_single_tetrahedron,
    make_tetrahedron_boundary,
    randomize_labels,
)


@pytest.fixture(scope="session")
def a4() -> AlternatingGroup4:
    return AlternatingGroup4()


@pytest.fixture(scope="session")
def z3() -> CyclicGroup:
    return CyclicGroup(3)


@pytest.fixture
def tetra_boundary():
    """``d(Delta^3)`` with random labels -- the milestone-1 seed."""
    cx = make_tetrahedron_boundary("A4")
    randomize_labels(cx, seed=7)
    return cx


@pytest.fixture
def ball_a4():
    """Triangulated 3-ball (one cube -> six tetrahedra) over ``A_4``."""
    cx = kuhn_ball("A4", n=1)
    randomize_labels(cx, seed=11)
    return cx


@pytest.fixture
def ball_z3():
    cx = kuhn_ball("Z3", n=1)
    randomize_labels(cx, seed=11)
    return cx


@pytest.fixture
def ball_region_a4(ball_a4):
    return Region(ball_a4, ball_a4.tetrahedra(), "ball")


__all__ = [
    "a4",
    "z3",
    "tetra_boundary",
    "ball_a4",
    "ball_z3",
    "ball_region_a4",
    "bianchi_defect",
    "make_bipyramid",
    "make_single_tetrahedron",
]
