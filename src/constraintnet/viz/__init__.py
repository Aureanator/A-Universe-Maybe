"""Visualization of the constraint network -- projection only, never physics.

Import is lazy: ``import constraintnet`` works without matplotlib installed; only touching
this package requires it.  Entry point::

    python -m constraintnet.viz --demo lattice --group A4 --steps 4000
    python -m constraintnet.viz --demo tetra --gif buzz.gif --frames 240

Modules
-------
``layout``   visual coordinates (grid metadata or force-directed); never read by dynamics
``frame``    the immutable snapshot protocol that drivers emit and the renderer consumes
``drivers``  what is being simulated while you watch: tetrahedron, orbit tour, lattice
``render``   matplotlib figure, animation loop, interactive controls, GIF recording
"""

from __future__ import annotations

from typing import Any

__all__ = ["Frame", "build_frame", "TetraDriver", "OrbitTourDriver", "LatticeDriver", "Viewer", "record_gif"]

_LAZY = {
    "Frame": ".frame",
    "build_frame": ".frame",
    "TetraDriver": ".drivers",
    "OrbitTourDriver": ".drivers",
    "LatticeDriver": ".drivers",
    "Viewer": ".render",
    "record_gif": ".render",
}


def __getattr__(name: str) -> Any:  # pragma: no cover - delegation
    target = _LAZY.get(name)
    if target is None:
        raise AttributeError(f"constraintnet.viz has no attribute {name!r}")
    import importlib

    module = importlib.import_module(target, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value
