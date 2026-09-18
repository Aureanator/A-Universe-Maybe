"""Pachner 2<->3 round-trip tests (referee audit item 4).

The 2->3 implementation once built 3-vertex tuples where 4-vertex tetrahedra were required,
crashing mid-mutation and corrupting the complex; no test exercised the move.  These are the
tests that should always have existed: legality, boundary preservation, exact revert, and
sequential stability with re-scanned sites.
"""

from __future__ import annotations

import itertools

import pytest

from constraintnet.moves import (
    MoveError,
    apply_pachner_2_3,
    apply_pachner_3_2,
    find_pachner_2_3_sites,
    find_pachner_3_2_sites,
    revert_move,
)
from constraintnet.seeds import kuhn_ball, randomize_labels


def snapshot(cx):
    return (
        frozenset(tuple(sorted(t)) for t in cx.tetrahedra()),
        tuple((tuple(sorted(e)), cx.label(*e)) for e in sorted(cx.edges())),
        frozenset(tuple(sorted(f)) for f in cx.faces()),
    )


def boundary_faces(cx):
    use: dict = {}
    for t in cx.tetrahedra():
        for f in itertools.combinations(sorted(t), 3):
            use[f] = use.get(f, 0) + 1
    return frozenset(f for f, c in use.items() if c == 1)


def boundary_labels(cx):
    out = set()
    for f in boundary_faces(cx):
        for pair in itertools.combinations(f, 2):
            out.add((tuple(sorted(pair)), cx.label(*pair)))
    return frozenset(out)


@pytest.fixture()
def ball():
    cx = kuhn_ball("A4", n=2)
    randomize_labels(cx, seed=7)
    return cx


class TestPachner23:
    def test_sites_exist(self, ball):
        assert len(find_pachner_2_3_sites(ball)) > 0

    def test_move_applies_and_grows_tet_count(self, ball):
        (a, b, face) = find_pachner_2_3_sites(ball)[0]
        n_before = ball.n_tetrahedra()
        move = apply_pachner_2_3(ball, a, b)
        assert ball.n_tetrahedra() == n_before + 1  # -2 +3
        u, w = move.payload["new_edge"]
        assert ball.has_edge(u, w)

    def test_boundary_preserved(self, ball):
        (a, b, face) = find_pachner_2_3_sites(ball)[0]
        bf, bl = boundary_faces(ball), boundary_labels(ball)
        apply_pachner_2_3(ball, a, b)
        assert boundary_faces(ball) == bf
        assert boundary_labels(ball) == bl  # the move is invisible from outside

    def test_replacement_tetrahedra_are_nondegenerate(self, ball):
        (a, b, face) = find_pachner_2_3_sites(ball)[0]
        move = apply_pachner_2_3(ball, a, b)
        for tet in move.added:
            assert len(set(tet)) == 4

    @pytest.mark.parametrize("site_index", [0, 1, 7, 35, 71])
    def test_round_trip_exact_over_site_sample(self, ball, site_index):
        sites = find_pachner_2_3_sites(ball)
        (a, b, face) = sites[site_index % len(sites)]
        before = snapshot(ball)
        move = apply_pachner_2_3(ball, a, b)
        revert_move(ball, move)
        assert snapshot(ball) == before

    def test_sequential_stability_with_rescan(self, ball):
        base = snapshot(ball)
        for r in range(10):
            sites = find_pachner_2_3_sites(ball)
            (a, b, face) = sites[r % len(sites)]
            before = snapshot(ball)
            move = apply_pachner_2_3(ball, a, b)
            revert_move(ball, move)
            assert snapshot(ball) == before, f"drift at round {r}"
        assert snapshot(ball) == base


class TestPachner32:
    def test_inverse_recovers_two_tetrahedra(self, ball):
        (a, b, face) = find_pachner_2_3_sites(ball)[0]
        tets_before = frozenset(tuple(sorted(t)) for t in ball.tetrahedra())
        move = apply_pachner_2_3(ball, a, b)
        u, w = move.payload["new_edge"]
        assert (u, w) in find_pachner_3_2_sites(ball) or (w, u) in [
            tuple(sorted(s)) for s in find_pachner_3_2_sites(ball)
        ] or any(set(s) == {u, w} for s in find_pachner_3_2_sites(ball))
        apply_pachner_3_2(ball, (u, w))
        tets_after = frozenset(tuple(sorted(t)) for t in ball.tetrahedra())
        assert tets_after == tets_before

    def test_illegal_site_raises(self, ball):
        with pytest.raises(MoveError):
            apply_pachner_3_2(ball, (0, 1))  # interior edge with many tets, not a bipyramid neck
