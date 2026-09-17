"""Curvature clusters: the naive matter candidates of Milestone 4."""

from __future__ import annotations

import pytest

from constraintnet.holonomy import triangle_holonomy
from constraintnet.objects import cluster_summary, curved_faces, detect_candidates, face_clusters
from constraintnet.seeds import kuhn_ball


def _edge_keys(face):
    a, b, c = face
    return {tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((a, c)))}


def test_flat_vacuum_contains_no_matter():
    cx = kuhn_ball("A4", n=1)
    assert curved_faces(cx) == []
    assert detect_candidates(cx) == []


def test_injecting_curvature_creates_a_cluster(ball_a4):
    cx = ball_a4  # randomly labelled: already has curvature
    faces = curved_faces(cx)
    assert faces, "expected curvature in a random labelling"
    clusters = face_clusters(cx)
    assert sum(len(cluster) for cluster in clusters) == len(faces)


def test_clusters_are_edge_connected(ball_a4):
    cx = ball_a4
    for cluster in face_clusters(cx):
        if len(cluster) < 2:
            continue
        # a spanning chain must exist: repeatedly find a face sharing an edge with the rest
        remaining = list(cluster)
        grown = {remaining.pop(0)}
        while remaining:
            edges_seen = set()
            for face in grown:
                edges_seen |= _edge_keys(face)
            for candidate in list(remaining):
                if _edge_keys(candidate) & edges_seen:
                    grown.add(candidate)
                    remaining.remove(candidate)
                    break
            else:
                pytest.fail(f"cluster is not edge-connected: {[list(f) for f in cluster]}")


def test_cluster_summary_reports_classes_and_members(ball_a4):
    cx = ball_a4
    candidates = detect_candidates(cx)
    assert candidates
    summary = max(candidates, key=lambda item: item["size"])
    total = sum(summary["class_counts"].values())
    assert total == summary["size"] == len(summary["faces"])
    assert summary["dominant_class"] in summary["class_counts"]
    for face in summary["faces"]:
        assert triangle_holonomy(cx, face) != cx.group.identity()


def test_single_curved_face_is_detected():
    """Neutralise everything except one face and check it shows up as exactly one cluster."""
    cx = kuhn_ball("Z3", n=1)
    group = cx.group
    # make every edge identity, then give one triangle a single nontrivial label
    for (u, v) in cx.edges():
        cx.set_label(u, v, group.identity())
    face = sorted(cx.faces())[0]
    i, j, k = face
    cx.set_label(i, j, 1)

    assert triangle_holonomy(cx, face) == 1
    curved = curved_faces(cx)
    assert face in curved
    clusters = face_clusters(cx)
    # edge (i,j) belongs to several triangles, so all of them are curved together:
    # the cluster must contain our face and be a single connected piece
    containing = [c for c in clusters if face in c]
    assert len(containing) == 1
    assert len(clusters) >= 1
