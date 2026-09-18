"""Layer-2 item 5: region entropy S(R)=log|I(dR)| -- conventions pinned against the
cone machinery (resolutions.py), then first area-law measurements."""

import itertools

import pytest

from constraintnet.entropy import (
    area_law_study, interior_vertices, metric_ball_tets, region_resolution_space,
)
from constraintnet.region import region_from_tets
from constraintnet.resolutions import resolution_space
from constraintnet.seeds import kuhn_ball, make_cone_over_tetrahedron


@pytest.fixture()
def cone_a4():
    return make_cone_over_tetrahedron("A4")


def _as_region(cx):
    """Wrap the whole cone complex as a Region (its tets; boundary auto-detected)."""
    return region_from_tets(cx, cx.tetrahedra(), name="cone")


# ------------------------------------------------------------------ convention spot-checks

def test_region_version_matches_cone_on_vacuum(cone_a4):
    cx, apex, boundary = cone_a4
    cone_space = resolution_space(cx, apex, boundary)
    reg_space = region_resolution_space(cx, _as_region(cx))
    assert (cone_space.count_raw, cone_space.count_physical) == \
        (reg_space.count_raw, reg_space.count_physical)
    assert cone_space.count_physical == 1          # light-like vacuum, known result


def test_region_version_matches_cone_on_uniform_v4_flux(cone_a4):
    cx, apex, boundary = cone_a4
    group = cx.group
    order_two = next(c for c in group.conjugacy_classes() if len(c) == 3)
    cone_space = resolution_space(
        cx, apex, boundary, {tuple(sorted((i, j))): order_two
                             for i, j in itertools.combinations(boundary, 2)}
    )
    flux = {tuple(sorted((apex, i, j))): order_two
            for i, j in itertools.combinations(boundary, 2)}
    reg_space = region_resolution_space(cx, _as_region(cx), flux)
    assert cone_space.count_physical == 6          # known |I| for uniform Klein-four flux
    assert (cone_space.count_raw, cone_space.count_physical) == \
        (reg_space.count_raw, reg_space.count_physical)


# ------------------------------------------------------------------ structural checks

def test_flat_vacuum_ball_is_topological():
    """Z3 Kuhn n=1 ball with flat data and flat-interior requirement: |I| = 1.

    Flat fillings of a 3-ball rel boundary are classified by H^1(R, dR; Z3) = 0 --
    entropy zero is the vacuum control for the area-law claim.
    """
    cx = kuhn_ball("Z3", n=1)
    center = sorted(cx.tetrahedra())[0]
    tets = metric_ball_tets(cx, center, radius=1)
    region = region_from_tets(cx, tets, name="ball")
    space = region_resolution_space(cx, region, max_internal_edges=12)
    if space.skipped_reason:
        pytest.skip(space.skipped_reason)
    assert space.count_physical == 1


def test_free_ensemble_is_volume_baseline(cone_a4):
    """Unconstrained interior must strictly beat the flat-interior count (volume effect)."""
    from constraintnet.entropy import _free_space
    cx, apex, boundary = cone_a4
    region = _as_region(cx)
    flat = region_resolution_space(cx, region)
    free_cone = _free_space(cx, region)
    assert free_cone.count_physical > flat.count_physical


def test_area_law_study_smoke_z3():
    cx = kuhn_ball("Z3", n=2)
    center = sorted(cx.tetrahedra())[len(cx.tetrahedra()) // 2]
    rows = area_law_study(cx, center, radii=(1,), max_internal_edges=9)
    assert len(rows) == 3                          # flat / defect / free at r=1
    names = {r["ensemble"] for r in rows}
    assert names == {"flat", "defect", "free"}
    measured = [r for r in rows if not r["skipped"]]
    assert measured                                # at least the small radii complete


# ---------------------------------------------------------- slice solver (E029 method)

def test_slice_matches_brute_on_cone_controls(cone_a4):
    from constraintnet.entropy import (enumerate_region_resolutions,
                                       enumerate_region_resolutions_slice)
    cx, apex, boundary = cone_a4
    region = _as_region(cx)
    brute = enumerate_region_resolutions(cx, region)
    slice_ = enumerate_region_resolutions_slice(cx, region)
    assert sorted(map(repr, brute)) == sorted(map(repr, slice_))
    group = cx.group
    order_two = next(c for c in group.conjugacy_classes() if len(c) == 3)
    flux = {tuple(sorted((apex, i, j))): order_two
            for i, j in itertools.combinations(boundary, 2)}
    brute_f = enumerate_region_resolutions(cx, region, flux)
    slice_f = enumerate_region_resolutions_slice(cx, region, flux)
    assert sorted(map(repr, brute_f)) == sorted(map(repr, slice_f))
    assert len(slice_f) == 72                      # raw; physical 6 via quotient below


def test_slice_matches_brute_random_regions():
    """Deterministic pseudo-random regions/declarations: the two solvers agree exactly.

    Test-side seeded RNG explores CONFIGURATION space only; KERNEL stays RNG-free.
    Covers both groups, unconstrained (None) classes, curved and flat declarations.
    """
    import random
    from constraintnet.seeds import (make_single_tetrahedron, make_bipyramid,
                                     make_cone_over_tetrahedron)
    from constraintnet.entropy import (enumerate_region_resolutions,
                                       enumerate_region_resolutions_slice)
    rng = random.Random(20260918)
    compared = 0

    def build(fn, gname):
        out = fn(gname)
        return out[0] if isinstance(out, tuple) else out

    for builder in (make_single_tetrahedron, make_bipyramid,
                    make_cone_over_tetrahedron, lambda G: kuhn_ball(G, n=1)):
        for gname in ("Z3", "A4"):
            for _ in range(8):
                cx = build(builder, gname)
                group = cx.group
                classes = list(group.conjugacy_classes())
                for e in sorted(cx.edges()):
                    cx.set_label(e[0], e[1], rng.choice(list(group.elements)))
                tets = list(cx.tetrahedra())
                if not tets:
                    continue
                region = region_from_tets(cx, rng.sample(tets, rng.randint(1, min(len(tets), 3))))
                if len(region.interior_edges()) > 6 or not region.interior_faces():
                    continue
                fc = {}
                for f in region.interior_faces():
                    key = tuple(sorted(f))
                    cls = rng.choice(classes + [classes[0], classes[0]])   # bias flat
                    fc[key] = frozenset(cls) if rng.random() < 0.8 else None
                brute = enumerate_region_resolutions(cx, region, fc, max_internal_edges=10)
                slice_ = enumerate_region_resolutions_slice(cx, region, fc)
                assert sorted(map(repr, brute)) == sorted(map(repr, slice_)), \
                    f"solver disagreement on {gname} region"
                compared += 1
    assert compared >= 20                          # the loop really exercised both solvers


def test_slice_budget_exhaustion_is_reported_not_truncated():
    cx = kuhn_ball("A4", n=2)
    group = cx.group
    region = region_from_tets(cx, [t for t in cx.tetrahedra() if 13 in t], name="star13")
    space = region_resolution_space(cx, region, method="slice", node_budget=5)
    assert space.skipped_reason is not None and "budget" in space.skipped_reason
    assert space.count_physical == 0               # nothing silently half-counted
