# constraintnet — a universe out of directed implications

**Axiom: directed implications reduce.** Nothing else is assumed — no space, no time,
no matter, no energy, no observer, no continuum, no coordinates.

`constraintnet` is a discrete *event–constraint–simplicial* simulator built from that
axiom. Edge labels carry group constraints; legitimate local reductions are exactly
those that preserve the boundary holonomy presented to the outside; persistent
topological defects are matter; rewrite cost is mass; interaction is boundary-compatible
gluing; and an observer coarse-grains event density into effective 3D geometry and
gravity-like propagation delay.

Coordinates exist only in the visualization layer. They never determine dynamics.

## Quick start

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install pytest matplotlib numpy   # Windows
PYTHONPATH=src .venv/Scripts/python.exe -m pytest -q              # 54 tests, ~1 s
PYTHONPATH=src .venv/Scripts/python.exe examples/milestone1.py    # reproduce 1728 -> 178
```

## What has been reproduced so far

| Result | Value | Status |
| --- | --- | --- |
| `A4` element count / conjugacy classes | 12 elements, classes of size 1,3,4,4 | ✅ |
| Gauge-fixed tetrahedron configurations | **1728** raw | ✅ |
| …quotiented by residual global conjugation | **178** inequivalent classes | ✅ |
| Independent prediction (Burnside: `(12³+3·4³+8·3³)/12`) | **178.0** | ✅ matches brute force |
| Face-holonomy conjugacy classes under gauge transform | invariant | ✅ |
| Region appearance (curvature + cycle charges) under gauge transform | invariant | ✅ |
| Bianchi identity `Σ_{∂R} ±Φ_f = 0` for abelian groups | holds for every labelling | ✅ |

## Two findings worth knowing before reading the code

1. **Charge cannot be a surface flux.** For curvature of the form `Φ = dA`, summing
   face holonomies over any closed surface is *identically zero* (every edge lies in two
   faces with opposite induced orientations). Curvature here behaves like magnetism: no
   net flux. Charge must therefore live on **cycles** — exactly as specified by
   `Q_C = Φ_C`. The usable Gauss law is the open-surface one: flux through a disk equals
   the holonomy of its boundary loop (tested in [tests/test_bianchi.py](<tests/test_bianchi.py>)).
2. **Tetrahedron orientation is data, not decoration.** Sorting simplex vertices throws
   away which side is "out"; interior faces then fail to cancel and "boundary" becomes
   meaningless. Orientations are propagated purely combinatorially (no coordinates) by
   `SimplicialComplex.orient_consistently()`.

## Layout

```
src/constraintnet/     the engine (group, complex, holonomy, region, gauge, seeds, ...)
tests/                 the specification's strict tests + integrity guards
examples/              one runnable script per milestone
docs/                  theory notes, conventions, architecture, findings
```

See [docs/SPEC.md](<docs/SPEC.md>) for the basement-to-capstone derivation,
[docs/PHYSICS_NOTES.md](<docs/PHYSICS_NOTES.md>) for what we verified and where the
specification had to be corrected, and [CHANGELOG.md](<CHANGELOG.md>) for progress.
