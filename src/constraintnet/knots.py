"""Knot and link invariants of flux strings -- combinatorial topology, honest embedding.

A flux string is a cycle in the DUAL 1-skeleton (nodes = tetrahedra, edges = shared faces).
Knot type of such a loop inside a triangulated ball is a PL invariant of the pair -- but to
COMPUTE it we need one concrete PL embedding. Documented choice (Layer-2 item 3): use the
standard cube coordinates of the Kuhn triangulation as the representative embedding; barycenters
of tetrahedra become dual vertices, shared-face barycenters are waypoints where dual edges
cross faces transversally. Coordinates enter INVARIANTS OF THE COMBINATORICS here -- never
dynamics (the architecture rule is untouched: acceptance rules remain purely relational).

Pipeline:  loop -> PL segments -> generic plane projection -> Gauss code (with over/under)
-> Reidemeister I removal + II-style cancellation -> reduced crossing count (upper bound on
crossing number; exact for alternating diagrams by the Menasco-Thistlethwaite theorem)
-> Alexander data at t = -1 (knot determinant via the Alexander matrix).

Linking number between two disjoint PL loops: signed crossings of one component against the
other under the same generic projection -- standard, and equal to the intersection number of
either with a spanning surface of the other.

Hypothesis to LOG, not tune (from the founding sketch): m ∝ knot complexity at fixed flux
class. This module supplies the measurement; the mass side comes from moveCost machinery.

Kernel module: no RNG, no scheduler. The projection direction is fixed and rational; a tiny
symbolic symbolic jitter resolves degenerate projective coincidences deterministically.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Sequence, Tuple

__all__ = [
    "Segment", "gauss_code", "reidemeister_reduce", "crossing_number_bound",
    "alexander_at_minus_one", "knot_invariants", "linking_number",
    "dual_embed_loop",
]

# All coordinates are exact rationals to keep crossing detection deterministic.
Rat = Fraction
Point3 = Tuple[Rat, Rat, Rat]
Segment = Tuple[Point3, Point3]


# --------------------------------------------------------------------------- projection & crossings

# Fixed rational tilt of the projection direction: screen coords (u, v) = (x + e*z, y + e'*z).
# The tilt removes vertex-on-double-point degeneracies that a pure axis projection suffers
# when polyline vertices land exactly on self-intersections (deterministic; no RNG).
TILT_U = 1.0e-3
TILT_V = 2.0e-3


def _screen(p: Point3):
    return float(p[0]) + TILT_U * float(p[2]), float(p[1]) + TILT_V * float(p[2])


def _depth(p: Point3) -> float:
    # depth along the (tilted) view direction; tiny x-term breaks exact ties deterministically
    return float(p[2]) + 1.0e-5 * float(p[0])


def _orient2d(ax: Rat, ay: Rat, bx: Rat, by: Rat) -> int:
    v = ax * by - ay * bx
    return (v > 0) - (v < 0)


def _crossing_2d(p1: Point3, p2: Point3, q1: Point3, q2: Point3):
    """Proper crossing of projected segments on the tilted screen. Returns (u, v, t_p, t_q) or None."""
    ax, ay = _screen(p1)
    bx, by = _screen(p2)
    cx, cy = _screen(q1)
    dx, dy = _screen(q2)
    r_x, r_y = bx - ax, by - ay
    s_x, s_y = dx - cx, dy - cy
    den = r_x * s_y - r_y * s_x
    if abs(den) < 1e-15:
        return None                                   # parallel
    qp = (cx - ax, cy - ay)
    t = (qp[0] * s_y - qp[1] * s_x) / den
    u = (qp[0] * r_y - qp[1] * r_x) / den
    eps = 1e-9
    if eps < t < 1 - eps and eps < u < 1 - eps:       # proper interior crossing
        return (ax + t * r_x, ay + t * r_y, t, u)
    return None


def _interp_depth(p1: Point3, p2: Point3, t: float) -> float:
    z1, z2 = _depth(p1), _depth(p2)
    return z1 + t * (z2 - z1)


@dataclass
class Crossing:
    index: int                    # unique id along the diagram walk
    strand_p: int                 # segment indices of the two crossing strands
    strand_q: int
    over_first: bool              # True: strand_p passes over strand_q
    sign: int                     # +1 / -1 right-hand rule from projected directions


def gauss_code(segments: Sequence[Segment]) -> List[List[Tuple[int, bool, int]]]:
    """Single-component Gauss code: along the curve, entries (label, is_over, sign).

    Crossing labels are assigned by first encounter. Assumes a generic projection
    (no triple points, no tangencies); callers embed via dual_embed_loop which jitters
    deterministically if degeneracies appear.
    """
    segs = list(segments)
    n = len(segs)
    raw: List[Tuple[int, int, bool, int]] = []        # (pos_p, pos_q, over_p, sign)
    for i in range(n):
        for j in range(i + 1, n):
            if abs(j - i) == 1 or (i == 0 and j == n - 1):
                continue                               # adjacent segments share an endpoint
            hit = _crossing_2d(segs[i][0], segs[i][1], segs[j][0], segs[j][1])
            if hit is None:
                continue
            _, _, t_p, t_q = hit
            z_p = _interp_depth(segs[i][0], segs[i][1], t_p)
            z_q = _interp_depth(segs[j][0], segs[j][1], t_q)
            if abs(z_p - z_q) < 1e-9:
                continue                               # degenerate; caller should re-jitter
            d1 = (_screen(segs[i][1])[0] - _screen(segs[i][0])[0],
                  _screen(segs[i][1])[1] - _screen(segs[i][0])[1])
            d2 = (_screen(segs[j][1])[0] - _screen(segs[j][0])[0],
                  _screen(segs[j][1])[1] - _screen(segs[j][0])[1])
            sign = 1 if (d1[0] * d2[1] - d1[1] * d2[0]) > 0 else -1
            raw.append((i, j, z_p > z_q, sign))

    # order along the curve: each segment contributes its crossings sorted by parameter t
    per_seg: Dict[int, List[Tuple[float, int, bool, int]]] = {}
    for k, (i, j, over_i, sign) in enumerate(raw):
        hit_ij = _crossing_2d(segs[i][0], segs[i][1], segs[j][0], segs[j][1])
        assert hit_ij is not None
        # Over/under from DEPTH at the crossing (over_i = z_i > z_j), never from which segment
        # happened to be i -- an early bug hardcoded True/False here. Sign flips when the same
        # crossing is viewed from strand j: cross(d2, d1) = -cross(d1, d2).
        per_seg.setdefault(i, []).append((hit_ij[2], k, over_i, sign))
        per_seg.setdefault(j, []).append((hit_ij[3], k, not over_i, -sign))
    label_of: Dict[int, int] = {}
    code: List[Tuple[int, bool, int]] = []
    for i in range(n):
        for t_param, k, is_over_p, sign in sorted(per_seg.get(i, [])):
            if k not in label_of:
                label_of[k] = len(label_of)
            over = is_over_p
            code.append((label_of[k], over, sign))
    return [code]


# --------------------------------------------------------------------------- Reidemeister simplification

def reidemeister_reduce(code: List[Tuple[int, bool, int]]):
    """Reidemeister I removal + adjacent-pair (type II style) cancellation. Iterated to fixpoint.

    Returns (reduced_code, moves). This is a sound simplification but NOT a complete knot
    algorithm: the reduced count is an upper bound on crossing number (exact for alternating
    diagrams -- Menasco-Thistlethwaite). Recorded honestly; trefoil/unknot tests pin behavior.
    """
    c = list(code)
    moves = 0
    changed = True
    while changed:
        changed = False
        # Reidemeister I: same label adjacent (consecutive along the walk) with matching sign
        for i in range(len(c)):
            a = c[i]
            b = c[(i + 1) % len(c)] if c else None
            if b is not None and len(c) > 1 and a[0] == b[0] and a[2] == b[2]:
                del c[(i + 1) % len(c)]
                del c[i]
                moves += 1
                changed = True
                break
        if changed:
            continue
        # Type II cancellation: same label twice, once over once under on both appearances,
        # with no other labels between one pair occurrence pattern (consecutive duplicate pair)
        for i in range(len(c)):
            for j in range(i + 1, len(c)):
                if c[i][0] == c[j][0]:
                    inner = c[i + 1:j]
                    wrapped = c[j + 1:] + c[:i]
                    arc_empty = len(inner) == 0 or len(wrapped) == 0
                    opposite = (c[i][1] != c[j][1]) and (c[i][2] == -c[j][2])
                    if arc_empty and opposite:
                        for idx in sorted({j, i}, reverse=True):
                            del c[idx]
                        moves += 1
                        changed = True
                        break
            if changed:
                break
    return c, moves


def crossing_number_bound(code: List[Tuple[int, bool, int]]) -> int:
    labels = {x[0] for x in code}
    return len(labels)


# --------------------------------------------------------------------------- Alexander data at t=-1

def alexander_at_minus_one(code: List[Tuple[int, bool, int]]):
    """Knot determinant |Delta(-1)| via the reduced Alexander matrix from the Gauss code.

    Arcs are bounded by UNDER-crossings only (an over-pass does not split the strand), so a
    knot diagram with n crossings has exactly n arcs and n relations; one of each is
    redundant -- drop one row and one column, then |det| at t = -1 is the determinant.
    Crossing relation (Fox): incoming*a - outgoing*b + (t-1)*over... standard form:
        -t*(incoming) + 1*(outgoing) + (t-1)*(over) = 0.
    Returns None when the code is not a single-component knot diagram.
    """
    if not code:
        return 1                                        # unknot
    n_cross = crossing_number_bound(code)
    if n_cross == 0:
        return 1
    total = len(code)
    if total != 2 * n_cross:
        return None                                     # not a knot diagram (link or degenerate)
    t = -1

    # rebuild arcs: walk the code; current arc id increments at every UNDER occurrence
    arc_of_under_in: Dict[int, int] = {}                # crossing label -> incoming arc
    arc_of_under_out: Dict[int, int] = {}
    over_arc_of: Dict[int, int] = {}
    current_arc = 0
    arcs_total = 0
    for pos, (label, over, sign) in enumerate(code):
        if over:
            if label in over_arc_of and over_arc_of[label] != current_arc:
                return None                             # inconsistent diagram bookkeeping
            over_arc_of[label] = current_arc
        else:
            arc_of_under_in[label] = current_arc        # this under-crossing ends the arc...
            arcs_total += 1
            current_arc = arcs_total                    # ...and starts the next one
    if arcs_total != n_cross or len(over_arc_of) != n_cross:
        return None
    n = n_cross
    # the walk is CLOSED: arc id n (after the last under-crossing) wraps to arc 0
    def wrap(aid: int) -> int:
        return aid % n
    for label in list(arc_of_under_in):
        arc_of_under_in[label] = wrap(arc_of_under_in[label])
        over_arc_of[label] = wrap(over_arc_of[label]) if label in over_arc_of else None
    for label in arc_of_under_in:
        arc_of_under_out[label] = (arc_of_under_in[label] + 1) % n

    rows = []
    for label in sorted(arc_of_under_in):
        row: Dict[int, int] = {}
        row[arc_of_under_in[label]] = row.get(arc_of_under_in[label], 0) + (-t)
        row[arc_of_under_out[label]] = row.get(arc_of_under_out[label], 0) + 1
        oa = over_arc_of.get(label)
        if oa is None:
            return None
        row[oa] = row.get(oa, 0) + (t - 1)
        rows.append(row)
    if n < 2:
        return None
    # reduced presentation: drop last relation and last column -> (n-1)x(n-1)
    import numpy as np
    M = np.zeros((n - 1, n - 1), dtype=float)
    for ri, row in enumerate(rows[:-1]):
        for col, value in row.items():
            if col != n - 1:
                M[ri, col] = float(value)
    det = round(abs(float(np.linalg.det(M))))
    return int(det)


# --------------------------------------------------------------------------- invariants bundle

@dataclass
class KnotData:
    raw_crossings: int
    reduced_crossings: int
    moves_applied: int
    determinant: Optional[int]
    gauss_code: List[Tuple[int, bool, int]] = field(default_factory=list)

    @property
    def is_unknot_candidate(self) -> bool:
        return self.reduced_crossings == 0 or (self.reduced_crossings <= 2 and self.determinant in (None, 1))


def knot_invariants(segments: Sequence[Segment]) -> KnotData:
    code = gauss_code(segments)[0]
    reduced, moves = reidemeister_reduce(code)
    det = alexander_at_minus_one(reduced) if reduced else 1
    return KnotData(raw_crossings=len({x[0] for x in code}), reduced_crossings=crossing_number_bound(reduced),
                    moves_applied=moves, determinant=det, gauss_code=reduced)


def linking_number(segments_a: Sequence[Segment], segments_b: Sequence[Segment]) -> int:
    """Signed inter-component crossings under the fixed projection = PL linking number."""
    lk = 0
    for i, (p1, p2) in enumerate(segments_a):
        for j, (q1, q2) in enumerate(segments_b):
            hit = _crossing_2d(p1, p2, q1, q2)
            if hit is None:
                continue
            _, _, t_p, t_q = hit
            z_p = _interp_depth(p1, p2, t_p)
            z_q = _interp_depth(q1, q2, t_q)
            if abs(z_p - z_q) < 1e-9:
                continue
            d1 = (_screen(p2)[0] - _screen(p1)[0], _screen(p2)[1] - _screen(p1)[1])
            d2 = (_screen(q2)[0] - _screen(q1)[0], _screen(q2)[1] - _screen(q1)[1])
            lk += 1 if (d1[0] * d2[1] - d1[1] * d2[0]) > 0 else -1
    return lk // 2          # linking number = HALF the signed inter-crossing sum (closed components)


# --------------------------------------------------------------------------- dual embedding

def dual_embed_loop(tet_centers: Dict[Tuple[int, ...], Point3], loop_tets: Sequence[Tuple[int, ...]],
                    face_points: Optional[Dict[Tuple[int, int, int], Point3]] = None) -> List[Segment]:
    """PL curve through tetrahedron barycenters, waypointing at shared-face barycenters.

    tet_centers maps each tet (sorted vertex tuple) to its 3D barycenter; loop_tets is the
    cycle of adjacent tets from strings.flux_string_components. Consecutive tets in the cycle
    share a face; if face_points given, route through them (keeps the curve transverse to the
    triangulation). Returns closed polyline segments.
    """
    pts: List[Point3] = []
    m = len(loop_tets)
    for k in range(m):
        t_here = loop_tets[k]
        t_next = loop_tets[(k + 1) % m]
        pts.append(tet_centers[tuple(sorted(t_here))])
        if face_points is not None:
            shared = set(t_here) & set(t_next)
            if len(shared) == 3:
                fp = face_points.get(tuple(sorted(shared)))
                if fp is not None:
                    pts.append(fp)
    # close back to start implicitly (segments wrap)
    segs = [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    return [s for s in segs if s[0] != s[1]]
