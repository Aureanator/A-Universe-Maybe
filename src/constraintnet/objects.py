"""Object detection: curvature clusters as matter candidates (Milestone 4 groundwork).

A *curvature cluster* is a set of faces with nontrivial holonomy that are edge-connected.
It is the most naive possible candidate for "localized nontrivial structure"; persistence,
charge-class tracking and invariants get layered on top in Milestone 4.  Nothing here knows
about coordinates: centroids are computed from *visual* positions supplied by the caller.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .complex import connected_components
from .holonomy import triangle_holonomy
from .region import Region

__all__ = ["curved_faces", "face_clusters", "cluster_summary", "detect_candidates"]

FaceKey = Tuple[int, int, int]


def curved_faces(cx) -> List[FaceKey]:
    """Faces whose holonomy is not the identity."""
    e = cx.group.identity()
    return [face for face in cx.faces() if triangle_holonomy(cx, face) != e]


def face_clusters(cx, faces: Optional[Sequence[FaceKey]] = None) -> List[List[FaceKey]]:
    """Group curved faces into edge-connected clusters."""
    faces = list(curved_faces(cx) if faces is None else faces)
    if not faces:
        return []
    index = {face: i for i, face in enumerate(faces)}
    pairs: List[Tuple[int, int]] = []
    by_edge: Dict[Tuple[int, int], List[int]] = {}
    for face in faces:
        for pair in _edge_keys(face):
            by_edge.setdefault(pair, []).append(index[face])
    for members in by_edge.values():
        for a in range(len(members)):
            for b in range(a + 1, len(members)):
                pairs.append((members[a], members[b]))
    groups = connected_components(pairs) if pairs else [{i} for i in index]
    out = []
    for group in sorted(groups, key=lambda g: (-len(g), min(g))):
        out.append([faces[i] for i in sorted(group)])
    return out


def cluster_summary(cx, cluster: Sequence[FaceKey]) -> Dict:
    """Class counts, member vertices and a visual centroid for one cluster."""
    group = cx.group
    classes: Dict[str, int] = {}
    for face in cluster:
        value = triangle_holonomy(cx, face)
        name = group.class_name(value) if hasattr(group, "class_name") else repr(value)
        classes[name] = classes.get(name, 0) + 1
    vertices = sorted({v for face in cluster for v in face})
    dominant = max(classes.items(), key=lambda kv: (kv[1], kv[0]))[0] if classes else "vacuum"
    return {
        "faces": list(cluster),
        "vertices": vertices,
        "class_counts": classes,
        "dominant_class": dominant,
        "size": len(cluster),
    }


def detect_candidates(cx, region: Optional[Region] = None) -> List[Dict]:
    """All curvature clusters in ``cx`` (optionally restricted to a region's faces).

    Only *curved* faces are clustered.  Passing every face here would make the flat vacuum
    look like one giant matter candidate -- which is exactly what this used to do.
    """
    allowed = set(region.faces() if region is not None else cx.faces())
    curved = [face for face in curved_faces(cx) if face in allowed]
    return [cluster_summary(cx, cluster) for cluster in face_clusters(cx, curved)]


def centroid_of(vertices: Iterable[int], positions: Dict[int, np.ndarray]) -> Optional[np.ndarray]:
    points = [positions[v] for v in vertices if v in positions]
    if not points:
        return None
    return np.mean(np.stack(points), axis=0)


def _edge_keys(face: FaceKey):
    a, b, c = face
    return [tuple(sorted((a, b))), tuple(sorted((b, c))), tuple(sorted((a, c)))]
