"""constraintnet -- discrete simplicial constraint-network simulator.

Basement axiom: *directed implications reduce*.  Everything else in this package is
constructed from that: events (vertices), directed implications with group-valued
constraint labels (oriented edges), realized reductions, curvature on faces, charge
on cycles, persistent topological defects as matter, rewrite cost as mass, and an
observer who coarse-grains event density into effective geometry.

Coordinates appear only in the visualization layer; they never determine dynamics.

Modules
-------
``groups``      generic finite-group engine (Z_n, A_4) + word metric for costs
``complex``     vertices / oriented edges / faces / tetrahedra, label storage
``holonomy``    face curvature, loop holonomy (= charge), Bianchi identity
``region``      regions, boundaries, gauge-invariant external appearance
``gauge``       gauge transforms, spanning-tree fixing, moduli enumeration
``seeds``       tetrahedral seeds and lattices (pure combinatorics)
``moves``       elementary relabellings + Pachner moves with legitimacy tests
``dynamics``    the main loop: propose / test / commit or revert, event log
``objects``     persistent-defect detection, tracking, invariants
``resolutions`` cone-over-tetrahedron internal resolution spaces
``motion``      translating a defect by accepted rewrites -> mass proxy
``interaction`` gluing objects along shared faces, joint resolutions
``observer``    coarse-grained event density, propagation delay, curvature proxies
``viz``         projection-only rendering (matplotlib optional)
"""

from __future__ import annotations

import importlib
from typing import Any

__version__ = "0.1.0"

_EXPORTS = {
    # groups
    "Group": ".groups",
    "CyclicGroup": ".groups",
    "AlternatingGroup4": ".groups",
    "get_group": ".groups",
    # complex
    "SimplicialComplex": ".complex",
    "SimplicialError": ".complex",
    "Vertex": ".complex",
    "EdgeView": ".complex",
    "FaceView": ".complex",
    "TetraView": ".complex",
    # holonomy
    "triangle_holonomy": ".holonomy",
    "face_holonomy": ".holonomy",
    "loop_holonomy": ".holonomy",
    "curvature_map": ".holonomy",
    "same_conjugacy_class": ".holonomy",
    "bianchi_defect": ".holonomy",
    # region
    "Region": ".region",
    "Appearance": ".region",
    "NonManifoldBoundary": ".region",
    # gauge
    "gauge_transform": ".gauge",
    "gauge_fix_spanning_tree": ".gauge",
    "tetrahedron_moduli": ".gauge",
    "burnside_prediction": ".gauge",
}


def __getattr__(name: str) -> Any:  # pragma: no cover - trivial delegation
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module 'constraintnet' has no attribute {name!r}")
    module = importlib.import_module(module_name, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__():  # pragma: no cover - cosmetic
    return sorted(set(list(globals()) + list(_EXPORTS)))
