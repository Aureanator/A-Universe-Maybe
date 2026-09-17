"""Milestone 4 — persistent defects: matter that survives conserved dynamics.

Physics of this module (derived, then measured; see PHYSICS_NOTES §2/§6)
------------------------------------------------------------------------
With the watched region set to a *closed ball* (nothing leaks out of the universe):

* moves on strictly **interior** edges are always accepted -- no observed face and no
  probe cycle uses them; they provide the internal buzz;
* moves on **surface** edges are generically rejected -- conservation confines charge;
* a nontrivial external cycle charge forces non-identity labels onto the surface
  1-skeleton, and those labels freeze.  In this engine *charge is written at infinity*
  (or on an observer membrane): what makes an object matter is that some outside loop
  measures a nontrivial residue;
* **persistence theorem**: if any probe-cycle charge is nontrivial then no
  appearance-preserving configuration can be fully flat -- a flat labelling has trivial
  loop holonomies everywhere.  Curvature therefore cannot evaporate while the charge
  lives, which is exactly spec Test 5: ``chargeClass(start) == chargeClass(end)``;
* **negative control**: a curvature lump with *trivial* external signature (all surface
  labels identity) is not protected by anything and presents nothing to the outside --
  a virtual fluctuation, not matter; it can never satisfy :func:`is_persistent`.

Measured at runtime (v0.4, Kuhn ball n=2, 300 steps): surface moves rejected 212/212,
interior moves accepted 88/88 -- **confinement is exact**.  Because interior moves are
unconditionally accepted, curvature *heats and diffuses* through the bulk (curved-face
count wanders from ~3 to ~67): localization is anchored by the frozen core, never by the
halo.  Persistence is therefore defined against the conserved external signature.

Tracking is purely relational: clusters of curved faces are matched step to step by
shared vertices; no coordinates are consulted anywhere in this module.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

from .complex import SimplicialComplex
from .dynamics import Simulation
from .holonomy import triangle_holonomy
from .objects import cluster_summary, curved_faces, face_clusters
from .region import Region
from .seeds import kuhn_ball

__all__ = [
    "Snapshot",
    "TrackedDefect",
    "DefectTracker",
    "seed_charged_defect",
    "seed_neutral_defect",
    "is_persistent",
    "run_persistence_experiment",
]

FaceKey = Tuple[int, int, int]


# --------------------------------------------------------------------------- #
# seeding
# --------------------------------------------------------------------------- #
def _order2_element(group):
    for element in group.elements:
        if group.order_of(element) == 2:
            return element
    raise ValueError("group has no order-2 element")


def seed_charged_defect(cx: SimplicialComplex, edge: Optional[Tuple[int, int]] = None, element=None) -> Dict:
    """Write a nontrivial residue onto the surface: matter.

    A single surface edge carries an order-2 element (Klein-four class, so every curved
    face lands in *one* conjugacy class and profiles stay readable).  The boundary faces
    containing that edge are frozen by conservation -- they are the object's identity as
    seen from outside; interior faces around the same edge form a fluctuating halo.
    """
    region = Region(cx, cx.tetrahedra(), "universe")
    surface_edges = region.boundary_surface_edges()
    if not surface_edges:
        raise ValueError("complex has no boundary surface to write charge on")
    target = tuple(edge) if edge is not None else surface_edges[0]
    if target not in set(surface_edges):
        raise ValueError(f"edge {target} is not a boundary surface edge; use seed_neutral_defect for interior seeds")
    value = element if element is not None else _order2_element(cx.group)
    cx.set_label(*target, value)
    return {"kind": "charged", "edge": target, "class": cx.group.class_name(value)}


def seed_neutral_defect(cx: SimplicialComplex, edge: Optional[Tuple[int, int]] = None, element=None) -> Dict:
    """A curvature lump invisible from outside: virtual fluctuation (negative control).

    The seeded edge is strictly interior and every surface label stays identity, so all
    probe-cycle charges are trivial; nothing protects this lump from diffusion.
    """
    region = Region(cx, cx.tetrahedra(), "universe")
    interior = region.interior_edges()
    if not interior:
        raise ValueError("complex has no interior edges to hide a neutral lump in")
    target = tuple(edge) if edge is not None else interior[0]
    value = element if element is not None else _order2_element(cx.group)
    cx.set_label(*target, value)
    return {"kind": "neutral", "edge": target, "class": cx.group.class_name(value)}


# --------------------------------------------------------------------------- #
# snapshots and tracking
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Snapshot:
    """One relational observation of a defect cluster at one step."""

    step: int
    faces: FrozenSet[FaceKey]
    vertices: FrozenSet[int]
    class_counts: Tuple[Tuple[str, int], ...]

    @property
    def size(self) -> int:
        return len(self.faces)

    def dominant_class(self) -> str:
        if not self.class_counts:
            return "vacuum"
        return max(self.class_counts, key=lambda kv: (kv[1], kv[0]))[0]


class TrackedDefect:
    """A defect identity carried across time by vertex-overlap matching.

    ``charge_core`` is the object's conserved external signature captured at birth:
    the nontrivial (boundary face, conjugacy class id) pairs that conservation freezes.
    An empty core means nothing is presented to the outside -- a virtual fluctuation,
    not matter -- and such an object can never satisfy :func:`is_persistent`.
    """

    def __init__(self, birth: Snapshot, charge_core: FrozenSet[Tuple[FaceKey, int]] = frozenset()):
        self.birth = birth
        self.charge_core = frozenset(charge_core)
        self.history: List[Snapshot] = [birth]
        self.gaps: int = 0          # observations where no cluster matched
        self.splits_seen: int = 0   # observations where >1 cluster overlapped

    def __len__(self) -> int:
        return len(self.history)

    @property
    def latest(self) -> Snapshot:
        return self.history[-1]

    @property
    def age(self) -> int:
        return self.latest.step - self.birth.step

    def charge_class(self) -> Tuple[str, ...]:
        """Conjugacy classes present at birth -- the object's charge signature."""
        return tuple(sorted(name for name, _ in self.birth.class_counts))

    def survival_ratio(self, window: Optional[int] = None) -> float:
        history = self.history if window is None else self.history[-window:]
        if not history:
            return 0.0
        return sum(1 for snap in history if snap.faces) / len(history)

    def charge_core_stable(self, cx: SimplicialComplex) -> bool:
        """Strict conservation (spec Test 5): every frozen core face still carries its class.

        This is a theorem of the dynamics, not an empirical hope -- accepted moves cannot
        alter observed boundary data.  Re-measuring it at runtime guards against bugs.
        """
        if not self.charge_core:
            return False
        group = cx.group
        for face, class_id in self.charge_core:
            current = group.class_of(triangle_holonomy(cx, face))
            if group.conjugacy_classes().index(current) != class_id:
                return False
        return True

    def charge_class_stable(self, window: Optional[int] = None) -> bool:
        """Descriptive only: dominant *cluster* class over the trailing window.

        Interior moves are accepted unconditionally, so curvature heats and diffuses; this
        metric measures that churn and is deliberately NOT part of ``is_persistent``.
        """
        history = self.history if window is None else self.history[-window:]
        return bool(history) and all(
            snap.dominant_class() == self.birth.dominant_class() for snap in history if snap.faces
        )

    def topological_invariants_stable(self, window: Optional[int] = None, tolerance: int = 2) -> bool:
        """Vertex support never collapses below ``birth size - tolerance``.

        The halo of a charged defect fluctuates (interior moves may flatten individual
        fan faces), but the frozen core -- two boundary triangles sharing the charge edge,
        four vertices -- can never be lost while the charge lives.  Tolerance 2 absorbs
        halo churn without letting an actual collapse through.
        """
        history = self.history if window is None else self.history[-window:]
        base = len(self.birth.vertices)
        return all(len(snap.vertices) >= base - tolerance for snap in history if snap.faces)

    def cluster_connected(self, cx: SimplicialComplex) -> bool:
        """Current faces form a single edge-connected cluster (by construction of the tracker)."""
        return bool(self.latest.faces) and len(face_clusters(cx, list(self.latest.faces))) == 1


class DefectTracker:
    """Re-detects curvature clusters each step and links them into defect identities."""

    def __init__(self, cx: SimplicialComplex):
        self.cx = cx
        self.defects: List[TrackedDefect] = []
        self.curved_count_history: List[Tuple[int, int]] = []  # (step, n_curved_faces)

    def _snapshot_of(self, cluster: Sequence[FaceKey], step: int) -> Snapshot:
        summary = cluster_summary(self.cx, cluster)
        return Snapshot(
            step=step,
            faces=frozenset(cluster),
            vertices=frozenset(summary["vertices"]),
            class_counts=tuple(sorted(summary["class_counts"].items())),
        )

    def observe(self, step: int) -> None:
        """One tracking tick: match every tracked defect to the best-overlapping cluster."""
        clusters = face_clusters(self.cx, curved_faces(self.cx))
        self.curved_count_history.append((step, sum(len(c) for c in clusters)))
        for defect in self.defects:
            previous = defect.latest.vertices
            candidates = [c for c in clusters if previous & {v for face in c for v in face}]
            overlapping = len(candidates)
            if overlapping > 1:
                defect.splits_seen += 1
            if not candidates:
                # keep an empty snapshot so windows measure the gap honestly
                defect.history.append(Snapshot(step, frozenset(), frozenset(), ()))
                defect.gaps += 1
                continue
            best = max(candidates, key=lambda c: len(previous & {v for face in c for v in face}))
            defect.history.append(self._snapshot_of(best, step))

    def adopt(self, cx_cluster: Sequence[FaceKey], step: int, charge_core=frozenset()) -> TrackedDefect:
        snapshot = self._snapshot_of(cx_cluster, step)
        defect = TrackedDefect(snapshot, charge_core=charge_core)
        self.defects.append(defect)
        return defect


def is_persistent(defect: TrackedDefect, cx: SimplicialComplex, window: int = 50) -> bool:
    """Matter = a nontrivial conserved external residue that stays one identifiable object.

    Three conditions, mirroring the specification's ``isPersistent`` with the semantics
    forced by measurement (§ see module docstring):

    1. **charge class stable**: the frozen core is nonempty and strictly unchanged --
       conservation makes this exact, not statistical;
    2. **identity persists**: matched in ≥ 99 % of the trailing window (no gaps);
    3. **cluster connected**: still a single edge-connected structure right now.

    The halo churns (interior moves are unconstrained and heat the bulk); anchoring is
    provided by the core, which is exactly what an outside observer means by "the object".
    """
    return (
        bool(defect.charge_core)
        and defect.charge_core_stable(cx)
        and defect.survival_ratio(window) >= 0.99
        and defect.cluster_connected(cx)
    )


# --------------------------------------------------------------------------- #
# experiment harness
# --------------------------------------------------------------------------- #
def run_persistence_experiment(
    kind: str = "charged",
    n: int = 2,
    steps: int = 1500,
    rng_seed: int = 7,
    group: str = "A4",
) -> Dict:
    """Seed one defect in a closed Kuhn ball and evolve it under conservation.

    Returns a report with acceptance statistics split by interior/surface support, the
    curved-face time series, tracking metrics and the strict conservation checks.
    """
    cx = kuhn_ball(group=group, n=n)
    region = Region(cx, cx.tetrahedra(), "universe")
    interior_edges = set(region.interior_edges())

    seed_info = seed_charged_defect(cx) if kind == "charged" else seed_neutral_defect(cx)

    # The conserved external signature at birth: nontrivial curvature classes on observed
    # boundary faces.  Conservation freezes these; they ARE the object for an outside observer.
    charge_core = frozenset(
        (face, cid) for face, cid in region.appearance().face_curvatures if cid != 0
    )

    tracker = DefectTracker(cx)
    initial_clusters = face_clusters(cx, curved_faces(cx))
    if not initial_clusters:
        raise AssertionError("seed produced no curvature at all")
    biggest = max(initial_clusters, key=len)
    defect = tracker.adopt(biggest, step=0, charge_core=charge_core)

    rng = random.Random(rng_seed)
    sim = Simulation(cx, region=region, rng=rng)
    sector_birth = sim.sector()

    accepted_interior = accepted_surface = rejected_interior = rejected_surface = 0
    for step in range(1, steps + 1):
        record = sim.attempt()
        touches_surface = any(edge not in interior_edges for edge in record.support_edges)
        if record.accepted:
            if touches_surface:
                accepted_surface += 1
            else:
                accepted_interior += 1
        elif touches_surface:
            rejected_surface += 1
        else:
            rejected_interior += 1
        tracker.observe(step)

    sector_end = sim.sector()
    frozen_ok = defect.charge_core_stable(cx) if charge_core else None
    curved_counts = [count for _, count in tracker.curved_count_history]
    return {
        "kind": kind,
        "seed": seed_info,
        "stats": sim.stats.summary(),
        "accept_rate": sim.stats.accept_rate,
        "accepted_interior": accepted_interior,
        "accepted_surface": accepted_surface,
        "rejected_interior": rejected_interior,
        "rejected_surface": rejected_surface,
        "sector_conserved": sector_birth == sector_end,
        "matter": bool(charge_core),
        "charge_core_size": len(charge_core),
        "frozen_core_classes_stable": frozen_ok,
        "curved_min": min(curved_counts),
        "curved_max": max(curved_counts),
        "ever_flat": 0 in curved_counts,
        "survival_ratio": defect.survival_ratio(),
        "gaps": defect.gaps,
        "splits_seen": defect.splits_seen,
        "charge_class_stable": defect.charge_class_stable(),
        "is_persistent": is_persistent(defect, cx),
        "birth_charge_class": defect.charge_class(),
    }
