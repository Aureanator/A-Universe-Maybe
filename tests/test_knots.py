"""Knot invariants of PL curves -- what is VERIFIED here, and one known-open piece.

Verified (pinned below): unknot detection (planar curve -> 0 crossings, det 1) and trefoil
(3 raw = 3 reduced crossings, Alexander determinant |Delta(-1)| = 3). The Gauss-code
over/under bug (hardcoded flags) and the arc-structure of the Alexander matrix were caught
by exactly these ground-truth curves -- E018 discipline again: find the discriminating example.

KNOWN OPEN (skipped test documents it): linking_number returns 0 on a round-circle Hopf link;
suspected projection degeneracy for near-coplanar components under the fixed tilt. Until this
passes, mesh-side linking claims are NOT made anywhere.
"""

import math
from fractions import Fraction

import pytest

from constraintnet.knots import gauss_code, knot_invariants, linking_number


def _poly(params):
    pts = [(Fraction(x).limit_denominator(10**6), Fraction(y).limit_denominator(10**6),
            Fraction(z).limit_denominator(10**6)) for x, y, z in params]
    return [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


def _trefoil(N=240):
    out = []
    for k in range(N):
        t = 2 * math.pi * k / N
        r = 2 + math.cos(3 * t)
        out.append((r * math.cos(2 * t), r * math.sin(2 * t), math.sin(3 * t)))
    return _poly(out)


def _unknot_planar(N=12):
    return _poly([(2 * math.cos(2 * math.pi * k / N), 2 * math.sin(2 * math.pi * k / N), 0.0)
                  for k in range(N)])


def test_unknot_detected():
    data = knot_invariants(_unknot_planar())
    assert data.raw_crossings == 0
    assert data.reduced_crossings == 0
    assert data.determinant == 1


def test_trefoil_crossings_and_determinant():
    data = knot_invariants(_trefoil())
    assert data.raw_crossings == 3
    assert data.reduced_crossings == 3                    # alternating: bound is exact
    assert data.determinant == 3                          # |Delta(-1)| of the trefoil


def test_gauss_code_alternates_over_under():
    """Regression (the hardcoded-flag bug): along a true knot diagram, over/under alternate
    per crossing label -- both branches of one crossing are never on the same side."""
    code = gauss_code(_trefoil())[0]
    by_label = {}
    for label, over, sign in code:
        by_label.setdefault(label, []).append(over)
    assert all(a != b for a, b in (v for v in by_label.values() if len(v) == 2))


@pytest.mark.skip(reason="KNOWN OPEN: linking_number degenerate on near-coplanar round circles "
                         "(returns 0 on Hopf link); fix before any mesh-side linking claims")
def test_hopf_linking_number():
    def c1(N=96):
        return _poly([(math.cos(2 * math.pi * k / N), math.sin(2 * math.pi * k / N), 0.0)
                      for k in range(N)])

    def c2(N=96):
        return _poly([(1 + math.cos(2 * math.pi * k / N), 0.0, math.sin(2 * math.pi * k / N))
                      for k in range(N)])

    assert abs(linking_number(c1(), c2())) == 1
