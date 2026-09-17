"""The frame protocol: what a driver emits and what the renderer draws.

Keeping this as a plain data snapshot means the simulation never depends on matplotlib and
the renderer never depends on the simulation -- which is also what makes headless recording
and interactive play/pause trivially equivalent code paths.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

from ..complex import SimplicialComplex
from ..groups import Group
from ..holonomy import triangle_holonomy
from ..observer import Observer
from .layout import positions as layout_positions

__all__ = ["Flash", "Pulse", "ObjectMark", "Frame", "build_frame", "class_labels"]

FaceKey = Tuple[int, int, int]


@dataclass
class Flash:
    """A transient marker where something happened (accepted or rejected)."""

    edge: Tuple[int, int]
    kind: str  # "accept" | "reject" | "signal"
    age: float = 0.0  # seconds-ish; renderer fades it out


@dataclass
class Pulse:
    """A test implication travelling along a path -- the gravity-delay visualisation."""

    path: Sequence[int]
    progress: float = 0.0  # 0..1 along the path in hop units
    label: str = "signal"


@dataclass
class ObjectMark:
    centroid: np.ndarray
    label: str
    charge: str = ""
    age: int = 0
    radius: float = 0.12


@dataclass
class Frame:
    step: int = 0
    positions: Dict[int, np.ndarray] = field(default_factory=dict)
    edges: List[Tuple[int, int, int]] = field(default_factory=list)  # (u, v, class id)
    faces: List[Tuple[FaceKey, int]] = field(default_factory=list)  # (triangle, curvature class)
    tets: List[Tuple[int, int, int, int]] = field(default_factory=list)
    edge_class_labels: List[str] = field(default_factory=list)
    face_class_labels: List[str] = field(default_factory=list)
    objects: List[ObjectMark] = field(default_factory=list)
    density: Dict[str, Tuple[float, float]] = field(default_factory=dict)  # cell -> (rho, n)
    vertex_cell: Dict[int, str] = field(default_factory=dict)
    counters: Dict[str, str] = field(default_factory=dict)
    log: List[str] = field(default_factory=list)
    flashes: List[Flash] = field(default_factory=list)
    pulses: List[Pulse] = field(default_factory=list)
    title: str = ""
    note: str = ""


def class_labels(group: Group) -> List[str]:
    """Readable names for each conjugacy class, in the group's canonical class order."""
    out = []
    for cls in group.conjugacy_classes():
        representative = sorted(cls, key=repr)[0]
        if hasattr(group, "class_name"):
            name = group.class_name(representative)  # type: ignore[attr-defined]
            out.append(f"{name} ({len(cls)})")
        else:
            out.append(f"class {representative!r} ({len(cls)})")
    return out


def _class_id(group: Group, element) -> int:
    for index, cls in enumerate(group.conjugacy_classes()):
        if element in cls:
            return index
    return 0


def build_frame(
    cx: SimplicialComplex,
    *,
    step: int = 0,
    observer: Optional[Observer] = None,
    objects: Sequence[ObjectMark] = (),
    flashes: Sequence[Flash] = (),
    pulses: Sequence[Pulse] = (),
    counters: Optional[Dict[str, str]] = None,
    log_lines: Sequence[str] = (),
    title: str = "",
    note: str = "",
    positions_override: Optional[Dict[int, np.ndarray]] = None,
    layout_seed: int = 0,
) -> Frame:
    """Snapshot the current state of ``cx`` into a drawable :class:`Frame`."""
    group = cx.group
    coords = positions_override if positions_override is not None else layout_positions(cx, seed=layout_seed)

    edges = [(u, v, _class_id(group, cx.label(u, v))) for (u, v) in cx.edges()]
    faces = [
        (face, _class_id(group, triangle_holonomy(cx, face)))
        for face in cx.faces()
    ]
    density = observer.density_field() if observer is not None else {}
    vertex_cell = {
        vertex: cell
        for cell, members in (observer.cells.items() if observer else {})
        for vertex in members
    }

    return Frame(
        step=step,
        positions=coords,
        edges=edges,
        faces=faces,
        tets=cx.tetrahedra(),
        edge_class_labels=class_labels(group),
        face_class_labels=class_labels(group),
        objects=list(objects),
        density=density,
        vertex_cell=vertex_cell,
        counters=dict(counters or {}),
        log=list(log_lines),
        flashes=list(flashes),
        pulses=list(pulses),
        title=title,
        note=note,
    )
