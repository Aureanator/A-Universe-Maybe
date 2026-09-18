"""E003 codified: reachability is move-set-relative (exact counts, deterministic BFS).

On the 1728-point gauge slice A4^3 with right-multiplication moves at any position:
- a FIXED order-3 generator reaches exactly 27 states;
- moves by ANY element of both order-3 classes reach all 1728 (ergodic);
- order-2 moves reach exactly 64 = 4^3 raw states.

External audit origin (reference/opus_audit/crosscheck*.py); now an in-repo regression
guard so the fragmentation numbers cannot silently drift.
"""

import itertools
from collections import deque

from constraintnet.groups import AlternatingGroup4


def _reachable(g, gens):
    e = g.identity()
    start = (e, e, e)
    seen = {start}
    frontier = deque([start])
    while frontier:
        t = frontier.popleft()
        for pos in range(3):
            for h in gens:
                d = list(t)
                d[pos] = g.multiply(t[pos], h)
                d = tuple(d)
                if d not in seen:
                    seen.add(d)
                    frontier.append(d)
    return seen


def test_fixed_order3_generator_reaches_27():
    g = AlternatingGroup4()
    c3 = sorted([x for x in g.elements if g.order_of(x) == 3], key=repr)[0]
    assert len(_reachable(g, [c3])) == 27


def test_all_order3_moves_are_ergodic_on_the_slice():
    g = AlternatingGroup4()
    threes = [x for x in g.elements if g.order_of(x) == 3]
    assert len(_reachable(g, threes)) == 1728


def test_order2_moves_reach_exactly_64():
    g = AlternatingGroup4()
    twos = [x for x in g.elements if g.order_of(x) == 2]
    comp = _reachable(g, twos)
    assert len(comp) == 64                                     # = 4^3
