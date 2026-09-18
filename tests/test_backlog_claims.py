"""Backlog assertions (Qwen cloud, items 1/5/6): leaks, census, sectors -- kernel-side.

These encode the PASS criteria as executable tests so results are checkable without
further context. Viz/HUD surfaces for these numbers are separate follow-ups; here the
claims themselves must hold at the engine level:

* item 1 (leak counter): under veto dynamics on a closed Kuhn ball, boundary face
  curvature classes recomputed DIRECTLY from the complex after every attempted move
  never change -- leaks == 0 is measured, not assumed;
* item 5a (tour census): over all gauge-inequivalent tetrahedron configurations, the
  (orbit count, little group) histogram equals 130 trivial / 26 Z3 / 21 V4 / 1 A4 and
  totals 178;
* item 5c/sectors: stabilizer types map to the spec's sector multiplicities --
  Z3 -> (4,2,2), V4 -> (2,2,2,2) (cross-checked via sectors.conjugation_multiplicities);
* item 6 (worldline): a tracked charged defect's boundary residue class is constant
  across its lifetime under allowed evolution (per-step engine check).
"""

from __future__ import annotations

import itertools

from constraintnet.drivers import DriverA, canonical_orbit_of_triple, conjugate_triple
from constraintnet.groups import AlternatingGroup4
from constraintnet.holonomy import triangle_holonomy
from constraintnet.persistence import seed_charged_defect
from constraintnet.region import Region
from constraintnet.sectors import conjugation_multiplicities
from constraintnet.seeds import kuhn_ball


def _boundary_classes(cx, region):
    return tuple(
        (face, cx.group.class_name(triangle_holonomy(cx, face)))
        for face in region.boundary_faces()
    )


# ---------------------------------------------------------------- item 1: leak counter
def test_leak_counter_zero_over_long_run():
    cx = kuhn_ball(group="A4", n=2)
    region = Region(cx, cx.tetrahedra(), "universe")
    seed_charged_defect(cx)
    driver = DriverA(cx, region=region, rng_seed=13)
    boundary0 = _boundary_classes(cx, region)
    leaks = 0
    for _ in range(400):
        driver.advance()
        if _boundary_classes(cx, region) != boundary0:
            leaks += 1
    assert leaks == 0


# ---------------------------------------------------------------- item 5a: census of the 178
def _orbits_and_stabilizers():
    g = AlternatingGroup4()
    triples = list(itertools.product(g.elements, repeat=3))
    orbits: dict = {}
    for t in triples:
        orbits.setdefault(canonical_orbit_of_triple(g, t), []).append(t)

    def stabilizer(rep):
        return [lam for lam in g.elements if conjugate_triple(g, rep, lam) == tuple(rep)]

    census: dict = {}
    for rep in orbits:
        stab = stabilizer(rep)
        size = len(stab)
        if size == 1:
            kind = "trivial"
        elif size == 3:
            kind = "Z3"
        elif size == 4:
            kind = "V4"
        else:
            kind = "A4"
        census[kind] = census.get(kind, 0) + 1
    return orbits, census


def test_little_group_census_matches_known_histogram():
    orbits, census = _orbits_and_stabilizers()
    assert len(orbits) == 178
    assert census == {"trivial": 130, "Z3": 26, "V4": 21, "A4": 1}


# ---------------------------------------------------------------- item 5c: sector multiplicities per stabilizer type
def test_sector_multiplicities_for_stabilizer_types():
    g = AlternatingGroup4()
    order3 = [x for x in g.elements if g.order_of(x) == 3]
    q3 = next(iter(order3))
    q2 = next(x for x in g.elements if g.order_of(x) == 2)
    _, mults_z3 = conjugation_multiplicities(g, q3, order3)
    _, mults_v4 = conjugation_multiplicities(g, q2, order3)
    assert mults_z3 == {0: 4, 1: 2, 2: 2}   # Z3 stabilizer -> (4, 2, 2)
    assert mults_v4 == [2, 2, 2, 2]         # V4 stabilizer -> uniform (2,2,2,2)


# ---------------------------------------------------------------- item 6: worldline conservation
def test_worldline_residue_constant_per_step():
    cx = kuhn_ball(group="A4", n=2)
    region = Region(cx, cx.tetrahedra(), "universe")
    seed_charged_defect(cx)
    core_faces = sorted(f for f, cid in region.appearance().face_curvatures if cid != 0)

    def residue():
        return tuple(cx.group.class_name(triangle_holonomy(cx, f)) for f in core_faces)

    baseline = residue()
    driver = DriverA(cx, region=region, rng_seed=21)
    silent_changes = 0
    for _ in range(300):
        driver.advance()
        if residue() != baseline:
            silent_changes += 1
    assert silent_changes == 0
