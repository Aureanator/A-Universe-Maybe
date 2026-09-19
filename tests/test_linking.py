"""Exact link controls, including orientation and degeneracy handling."""

from fractions import Fraction as Q

import pytest

from constraintnet.linking import DegenerateProjection, linking_number


def polygon(points):
    return list(zip(points, points[1:] + points[:1]))


def hopf():
    a = polygon([(-2,-2,0), (2,-2,0), (2,2,0), (-2,2,0)])
    b = polygon([(0,0,-1), (3,0,-1), (3,0,1), (0,0,1)])
    return a, b


def transform(curve, fn):
    return [(fn(a), fn(b)) for a, b in curve]


def test_hopf_symmetry_orientation_reflection_and_views():
    a, b = hopf()
    value = linking_number(a, b)
    # A bounds the positively oriented z=0 rectangle; B crosses its interior
    # once downward at (0,0,0), giving intersection number -1.
    assert value == -1
    assert linking_number(b, a) == value
    reverse = [(end, start) for start, end in reversed(a)]
    assert linking_number(reverse, b) == -value
    mirror = lambda p: (-p[0], p[1], p[2])
    assert linking_number(transform(a, mirror), transform(b, mirror)) == -value
    for view in [(Q(1,13), Q(2,17)), (Q(-2,19), Q(3,23)), (Q(3,7), Q(-5,11))]:
        assert linking_number(a, b, projection=view) == value
    shear = lambda p: (p[0] + 2*p[2] + 7, 3*p[1] - p[2] - 4, 2*p[2] + 1)
    assert linking_number(transform(a, shear), transform(b, shear)) == value


def test_subdivision_and_unlink():
    a, b = hopf()
    subdivided = []
    for start, end in a:
        mid = tuple(Q(x+y, 2) for x, y in zip(start, end))
        subdivided.extend([(start, mid), (mid, end)])
    assert linking_number(subdivided, b) == linking_number(a, b)
    moved = transform(b, lambda p: (p[0] + 10, p[1], p[2]))
    assert linking_number(a, moved) == 0


def test_degenerate_projection_and_bad_curves_are_not_zero_links():
    a, b = hopf()
    with pytest.raises(DegenerateProjection):
        linking_number(a, b, projection=(0, 0))
    with pytest.raises(ValueError):
        linking_number(a[:-1], b)
    with pytest.raises(ValueError):
        linking_number(a, a)
