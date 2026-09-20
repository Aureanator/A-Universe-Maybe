"""Exact signed-crossing linking number of disjoint oriented closed PL cycles.

The embedding is measurement data, never an input to rewrite acceptance. Crossing
sign is sign(det(projected tangent A, tangent B) * (depth A - depth B)); omitting
the over/under factor computes a planar intersection count instead of linking.
The half-sum definition is standard: S. Friedl, Knot theory, Definition 1.3.1,
https://web.stanford.edu/~sfh/knot.pdf .

Every predicate uses rational arithmetic. Nongeneric views are retried without
changing the curves. A finite projection budget may fail explicitly; no crossing
is silently dropped and no half-integer sum is rounded to an integer.
"""

from fractions import Fraction as Q


class DegenerateProjection(ValueError):
    """The chosen projection cannot certify the linking number."""


def _cycle(segments):
    result = [tuple(tuple(Q(x) for x in p) for p in segment) for segment in segments]
    if len(result) < 3:
        raise ValueError("a closed polygon needs at least three segments")
    for i, segment in enumerate(result):
        if len(segment) != 2 or any(len(p) != 3 for p in segment):
            raise ValueError("expected three-dimensional segments")
        a, b = segment
        if a == b or b != result[(i + 1) % len(result)][0]:
            raise ValueError("expected a closed ordered polygon without zero edges")
    return result


def _project(segments, tilt):
    u, v = map(Q, tilt)
    return [tuple((x + u*z, y + v*z, z) for x, y, z in segment) for segment in segments]


def _cross(a, b):
    return a[0]*b[1] - a[1]*b[0]


def _sign_at_crossing(p, q):
    a, b = p
    c, d = q
    r = (b[0]-a[0], b[1]-a[1])
    s = (d[0]-c[0], d[1]-c[1])
    if r == (0, 0) or s == (0, 0):
        raise DegenerateProjection("segment projects to a point")
    offset = (c[0]-a[0], c[1]-a[1])
    den = _cross(r, s)
    if den == 0:
        if _cross(offset, r) != 0:
            return 0
        axis = 0 if r[0] else 1
        if max(min(a[axis], b[axis]), min(c[axis], d[axis])) <= min(
                max(a[axis], b[axis]), max(c[axis], d[axis])):
            raise DegenerateProjection("collinear projected segments overlap")
        return 0
    t, u = _cross(offset, s)/den, _cross(offset, r)/den
    if not (0 <= t <= 1 and 0 <= u <= 1):
        return 0
    if t in (0, 1) or u in (0, 1):
        raise DegenerateProjection("projected crossing touches a vertex")
    depth = a[2] + t*(b[2]-a[2]) - c[2] - u*(d[2]-c[2])
    if depth == 0:
        raise ValueError("the two curves intersect in three dimensions")
    return 1 if den*depth > 0 else -1


def linking_number(segments_a, segments_b, *, projection=None):
    """Integer linking, or ValueError if closed/disjoint/generic checks fail.

An explicit projection is (u,v) for screen=(x+u*z,y+v*z), with z as depth.
Without one, try 32 deterministic rational views. The bound is an implementation
limit, not a claim that every embedded pair is covered by these views.
"""
    a, b = _cycle(segments_a), _cycle(segments_b)
    views = [projection] if projection is not None else [
        (Q(1, 1000), Q(2, 1000))] + [(Q(k, 997), Q(k*k+1, 991)) for k in range(1, 32)]
    for view in views:
        try:
            pa, pb = _project(a, view), _project(b, view)
            total = sum(_sign_at_crossing(p, q) for p in pa for q in pb)
        except DegenerateProjection:
            if projection is not None:
                raise
            continue
        if total % 2:
            raise ValueError("odd crossing sum: cannot certify a closed disjoint link")
        return total // 2
    raise DegenerateProjection("no generic view within the 32-projection budget")
