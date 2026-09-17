"""Sectors tests: the spec's quantum-structure claims for A4, computed exactly."""

from __future__ import annotations

from constraintnet.groups import AlternatingGroup4
from constraintnet.sectors import conjugation_multiplicities, residual_symmetry, sector_report


def test_residual_symmetries_match_spec():
    g = AlternatingGroup4()
    e = g.identity()
    assert len(residual_symmetry(g, e)) == 12
    q3 = next(x for x in g.elements if g.order_of(x) == 3)
    h3 = residual_symmetry(g, q3)
    assert len(h3) == 3 and all(g.order_of(x) in (1, 3) for x in h3)  # ~ Z3
    q2 = next(x for x in g.elements if g.order_of(x) == 2)
    h4 = residual_symmetry(g, q2)
    assert len(h4) == 4 and all(g.order_of(x) in (1, 2) for x in h4)  # ~ V4


def test_order3_charge_sectors_are_4_2_2():
    g = AlternatingGroup4()
    order3 = [x for x in g.elements if g.order_of(x) == 3]
    q3 = next(iter(order3))
    hinfo, mults = conjugation_multiplicities(g, q3, order3)
    assert hinfo["type"] == "Z3"
    assert mults == {0: 4, 1: 2, 2: 2}          # phases 1, omega, omega^2 with counts
    assert sum(mults.values()) == len(order3)   # all Z3 irreps are 1D: multiplicities = dims


def test_v4_charge_uniform_real_sectors():
    g = AlternatingGroup4()
    order3 = [x for x in g.elements if g.order_of(x) == 3]
    q2 = next(x for x in g.elements if g.order_of(x) == 2)
    hinfo, mults = conjugation_multiplicities(g, q2, order3)
    assert hinfo["type"] == "V4" and mults == [2, 2, 2, 2]


def test_adjoint_control_and_report_consistency():
    report = sector_report()
    ctrl = report["adjoint control"]
    assert ctrl["<chi_conj,1>"] == ctrl["n_classes"] == 4
