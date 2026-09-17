"""Regions, their boundaries, and what an outside observer can measure.

A **region** is a connected set of tetrahedra of the complex.  Everything physical
about a region that is visible from outside is encoded in :class:`Appearance`:

* the conjugacy class of the curvature of every face of ``dR``;
* the conjugacy class of the holonomy of every cycle an outside observer can walk
  on the boundary surface (a fundamental cycle basis of the boundary 1-skeleton).

Because both are conjugacy classes, :class:`Appearance` is invariant under gauge
transformations.  Because charge lives on cycles rather than surfaces (Bianchi),
the second item -- not a flux integral -- is the conserved "unresolved constraint
presented to the outside".

A local rewrite is *legitimate* exactly when it leaves ``appearance()`` unchanged;
that single predicate implements conservation without adding it as a law.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Dict, FrozenSet, Iterable, List, Sequence, Set, Tuple

from .complex import SimplicialComplex, face_induced_signs, fundamental_cycles
from .groups import Group
from .holonomy import loop_holonomy, triangle_holonomy

__all__ = [
    "NonManifoldBoundary",
    "Appearance",
    "Region",
    "region_from_tets",
    "closed_surface_flux",
]


class NonManifoldBoundary(Exception):
    """Raised when a region's boundary is not a proper surface (a face appears twice)."""


FaceKey = Tuple[int, int, int]
EdgeKey = Tuple[int, int]


@dataclass(frozen=True)
class Appearance:
    """Gauge-invariant data presented by a region to its exterior.

    Conjugacy classes are stored as integer ids into the group's class list (so the
    structure is hashable and comparable across time steps); ``labels`` maps those
    ids to readable text for reports.
    """

    face_curvatures: FrozenSet[Tuple[FaceKey, int]] = frozenset()
    cycle_charges: FrozenSet[Tuple[Tuple[int, ...], int]] = frozenset()
    labels: Tuple[Tuple[str, str], ...] = ()

    def describe(self) -> Dict[str, List[str]]:
        lookup = dict(self.labels)
        return {
            "boundary_face_curvatures": [
                f"{list(face)}: {lookup.get(f'f:{cid}', '?')}"
                for face, cid in sorted(self.face_curvatures, key=lambda item: list(item[0]))
            ],
            "cycle_charges": [
                f"loop{list(loop)}: {lookup.get(f'c:{cid}', '?')}"
                for loop, cid in sorted(self.cycle_charges, key=lambda item: list(item[0]))
            ],
        }

    def nontrivial_cycles(self) -> List[Tuple[Tuple[int, ...], str]]:
        lookup = dict(self.labels)
        trivial = 0
        out = []
        for loop, cid in sorted(self.cycle_charges, key=lambda item: list(item[0])):
            if cid != trivial:
                out.append((loop, lookup.get(f"c:{cid}", "?")))
        return out

    def is_trivial(self) -> bool:
        """True when nothing at all is presented to the outside (pure vacuum)."""
        return all(cid == 0 for _, cid in self.face_curvatures) and all(
            cid == 0 for _, cid in self.cycle_charges
        )

    def signature(self) -> tuple:
        """A compact hashable label for this appearance (used as a sector id).

        Nested tuples throughout -- lists would make it unhashable and it is used as a
        dictionary key for superselection sectors.
        """
        return (
            tuple(sorted((tuple(face), cid) for face, cid in self.face_curvatures)),
            tuple(sorted((tuple(loop), cid) for loop, cid in self.cycle_charges)),
        )

    def nontrivial_face_count(self) -> int:
        return sum(1 for _, cid in self.face_curvatures if cid != 0)


class Region:
    """A connected subcomplex of tetrahedra with cached boundary machinery."""

    def __init__(self, cx: SimplicialComplex, tets: Iterable[Tuple[int, ...]], name: str = ""):
        self.cx = cx
        self.name = name or "region"
        self.tets: FrozenSet[Tuple[int, ...]] = frozenset(
            tuple(sorted(int(v) for v in tet)) for tet in tets
        )

    # ------------------------------------------------------------- skeleton
    def vertices(self) -> List[int]:
        out: Set[int] = set()
        for tet in self.tets:
            out |= set(tet)
        return sorted(out)

    def edges(self) -> List[EdgeKey]:
        out: Set[EdgeKey] = set()
        for tet in self.tets:
            for pair in itertools.combinations(sorted(tet), 2):
                if self.cx.has_edge(*pair):
                    out.add(tuple(sorted(pair)))  # type: ignore[arg-type]
        return sorted(out)

    def faces(self) -> List[FaceKey]:
        known = set(self.cx.faces())
        out: Set[FaceKey] = set()
        for tet in self.tets:
            for tri in itertools.combinations(sorted(tet), 3):
                key = tuple(sorted(tri))
                if key in known:
                    out.add(key)  # type: ignore[arg-type]
        return sorted(out)

    # ------------------------------------------------------------ boundary
    def boundary_faces_signed(self) -> Dict[FaceKey, int]:
        """Net oriented multiplicity of every face in ``d(region)``.

        Interior faces cancel in pairs (they are seen with opposite induced
        orientations from their two tetrahedra).  A coefficient with magnitude
        greater than one means the boundary is not a surface.
        """
        counts: Dict[FaceKey, int] = {}
        for tet in sorted(self.tets):
            for face, sign in face_induced_signs(self.cx.tet_order(tet)).items():
                counts[face] = counts.get(face, 0) + sign
        boundary = {f: c for f, c in counts.items() if c != 0}
        for face, count in boundary.items():
            if abs(count) > 1:
                raise NonManifoldBoundary(
                    f"face {list(face)} appears with multiplicity {count} in the "
                    f"boundary of region '{self.name}' -- not a manifold boundary"
                )
        return boundary

    def boundary_faces(self) -> List[FaceKey]:
        return sorted(self.boundary_faces_signed())

    def interior_faces(self) -> List[FaceKey]:
        all_faces = set(self.faces())
        boundary = set(self.boundary_faces())
        return sorted(all_faces - boundary)

    def boundary_surface_edges(self) -> List[EdgeKey]:
        out: Set[EdgeKey] = set()
        for face in self.boundary_faces():
            for pair in itertools.combinations(face, 2):
                if self.cx.has_edge(*pair):
                    out.add(tuple(sorted(pair)))  # type: ignore[arg-type]
        return sorted(out)

    def interior_edges(self) -> List[EdgeKey]:
        boundary = set(self.boundary_surface_edges())
        return [e for e in self.edges() if e not in boundary]

    def is_closed_boundary(self) -> bool:
        """True when every boundary edge is shared by exactly two boundary faces."""
        usage: Dict[EdgeKey, int] = {}
        for face in self.boundary_faces():
            for pair in itertools.combinations(face, 2):
                key = tuple(sorted(pair))  # type: ignore[var-annotated]
                usage[key] = usage.get(key, 0) + 1
        return bool(usage) and all(count == 2 for count in usage.values())

    def observed_faces(self) -> List[FaceKey]:
        """Faces whose curvature is externally visible.

        For a 3D region that is ``d(region)``.  A complex with no tetrahedra -- such as
        ``d(Delta^3)`` itself -- *is* its own observable surface, so every face counts;
        otherwise such a complex would report "nothing to protect" and conservation would
        silently do nothing.
        """
        if self.tets:
            return self.boundary_faces()
        return sorted({tuple(sorted(face)) for face in self.cx.faces()})

    def surface_edges(self) -> List[EdgeKey]:
        """1-skeleton of the observable surface (see :meth:`observed_faces`)."""
        out: Set[EdgeKey] = set()
        for face in self.observed_faces():
            for pair in itertools.combinations(face, 2):
                if self.cx.has_edge(*pair):
                    out.add(tuple(sorted(pair)))  # type: ignore[arg-type]
        return sorted(out)

    def probe_cycles(self) -> List[Tuple[int, ...]]:
        """Fundamental cycles of the observable surface's 1-skeleton.

        These are the loops an external observer can walk without entering the region;
        their holonomy conjugacy classes are the observable charges.
        """
        return fundamental_cycles(self.surface_edges())

    # ---------------------------------------------------------- observables
    def appearance(self) -> Appearance:
        group = self.cx.group
        classes = list(group.conjugacy_classes())

        def class_id(cls) -> int:
            for index, known in enumerate(classes):
                if known == cls:
                    return index
            raise AssertionError("conjugacy class not found")

        face_curvatures = tuple(
            (face, class_id(group.class_of(triangle_holonomy(self.cx, face))))
            for face in self.observed_faces()
        )
        cycle_charges = tuple(
            (loop, class_id(group.class_of(loop_holonomy(self.cx, loop))))
            for loop in self.probe_cycles()
        )
        labels: List[Tuple[str, str]] = []
        for cid, cls in enumerate(classes):
            representative = sorted(cls, key=repr)[0]
            text = _describe(group, representative)
            labels.append((f"f:{cid}", text))
            labels.append((f"c:{cid}", text))
        return Appearance(
            face_curvatures=frozenset(face_curvatures),
            cycle_charges=frozenset(cycle_charges),
            labels=tuple(labels),
        )

    def charge_report(self) -> Dict[str, str]:
        group = self.cx.group
        report: Dict[str, str] = {}
        for loop in self.probe_cycles():
            value = loop_holonomy(self.cx, loop)
            report[str(list(loop))] = _describe(group, value)
        return report

    def __repr__(self) -> str:  # pragma: no cover - cosmetic
        return (
            f"<Region '{self.name}' tets={len(self.tets)} V={len(self.vertices())} "
            f"E={len(self.edges())} F={len(self.faces())} dF={len(self.boundary_faces())}>"
        )


def _describe(group: Group, element) -> str:
    if hasattr(group, "format"):  # A4 and friends provide cycle notation
        return group.format(element)  # type: ignore[attr-defined]
    if element == group.identity():
        return "e"
    return f"{element!r}"


def region_from_tets(cx: SimplicialComplex, tets: Iterable[Tuple[int, ...]], name: str = "") -> Region:
    return Region(cx, tets, name=name)


def closed_surface_flux(cx: SimplicialComplex, faces_with_signs: Dict[FaceKey, int]):
    """Product of face curvatures over a closed surface (abelian groups only).

    Provided for diagnostics: the Bianchi identity says this is the identity for any
    closed surface and any labelling.  For non-abelian groups an ordered product over
    a surface needs extra framing data, so we refuse rather than silently return a
    gauge-dependent number.
    """
    group = cx.group
    if not group.is_abelian():
        raise TypeError(
            "closed-surface flux is only well defined for abelian groups; "
            "use Region.appearance() (cycle charges) for non-abelian groups"
        )
    result = group.identity()
    for face, sign in sorted(faces_with_signs.items()):
        value = triangle_holonomy(cx, tuple(sorted(face)))
        if sign < 0:
            value = group.inverse(value)
        result = group.multiply(result, value)
    return result
