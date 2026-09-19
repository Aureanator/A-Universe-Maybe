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
from constraintnet.seeds import kuhn_ball, make_bipyramid, randomize_labels


def snapshot(cx):
    return (
        frozenset(tuple(sorted(t)) for t in cx.tetrahedra()),
        tuple((tuple(sorted(e)), cx.label(*e)) for e in sorted(cx.edges())),
        frozenset(tuple(sorted(f)) for f in cx.faces()),
        tuple((t, cx.tet_order(t)) for t in cx.tetrahedra()),
        tuple((e, cx.is_realized(*e)) for e in cx.edges()),
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
    def test_both_directions_preserve_euler_and_exact_undo(self):
        for triangulation, expected_faces in [("two", 7), ("three", 9)]:
            cx = make_bipyramid("A4", triangulation=triangulation)
            randomize_labels(cx, seed=19)
            for edge in cx.edges()[::2]:
                cx.set_realized(*edge, True)
            before = snapshot(cx)
            boundary = boundary_labels(cx)
            if triangulation == "two":
                a, b, _ = find_pachner_2_3_sites(cx)[0]
                move = apply_pachner_2_3(cx, a, b)
                assert cx.n_faces() == 9
            else:
                move = apply_pachner_3_2(cx, find_pachner_3_2_sites(cx)[0])
                assert cx.n_faces() == 7
            assert len(cx.vertices()) - cx.n_edges() + cx.n_faces() - cx.n_tetrahedra() == 1
            assert boundary_labels(cx) == boundary
            assert all(cx.tets_around_face(f) for f in cx.faces())
            revert_move(cx, move)
            assert snapshot(cx) == before
            assert cx.n_faces() == expected_faces

    def test_existing_equatorial_face_rejected_without_mutation(self):
        cx = make_bipyramid("A4", triangulation="three")
        edge = find_pachner_3_2_sites(cx)[0]
        equator = sorted(set(cx.vertices()) - set(edge))
        cx.add_face(equator)
        before = snapshot(cx)
        assert edge not in find_pachner_3_2_sites(cx)
        with pytest.raises(MoveError, match="link condition"):
            apply_pachner_3_2(cx, edge)
        assert snapshot(cx) == before

    def test_unrelated_surface_survives_round_trip(self):
        cx = make_bipyramid("A4", triangulation="three")
        edge = find_pachner_3_2_sites(cx)[0]
        cx.add_face((20, 21, 22))
        before = snapshot(cx)
        move = apply_pachner_3_2(cx, edge)
        assert cx.has_face((20, 21, 22))
        revert_move(cx, move)
        assert snapshot(cx) == before

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
