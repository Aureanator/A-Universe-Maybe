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
PYTHONPATH=src .venv/Scripts/python.exe -m pytest -q              # 95 tests, ~8 s
PYTHONPATH=src .venv/Scripts/python.exe examples/milestone1.py    # reproduce 1728 -> 178
```

## Watch it buzz

An interactive window with live animation, play/pause, single-step, speed control and layer
toggles (also works headless — the GIF path is the same code):

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m constraintnet.viz --demo lattice --group A4 --n 2
PYTHONPATH=src .venv/Scripts/python.exe -m constraintnet.viz --demo tetra   # d(Delta^3), conservation bites
PYTHONPATH=src .venv/Scripts/python.exe -m constraintnet.viz --demo orbit    # tour the 178 gauge classes
PYTHONPATH=src .venv/Scripts/python.exe -m constraintnet.viz --demo lattice --gif out/buzz.gif --frames 200
```

What you see: edges coloured by constraint conjugacy class, triangles coloured by curvature,
**green ▲ = accepted reduction, red ✗ = rejected attempt**, glowing spheres = curvature
clusters (matter candidates), vertex size/colour = local mesh fineness `n = rho/rho0`, and a
white star carrying a test implication through the mesh so you can watch it slow down in dense
cells. Keys: `space` play/pause, `right` step, `e/f/o/d` toggle layers, `r` auto-rotate,
`s` save PNG, `q` quit.

## What has been reproduced so far

| Result | Value | Status |
| --- | --- | --- |
| `A4` element count / conjugacy classes | 12 elements, classes of size 1,3,4,4 | ✅ |
| Gauge-fixed tetrahedron configurations | **1728** raw | ✅ |
| …quotiented by residual global conjugation | **178** inequivalent classes | ✅ |
| Independent prediction (Burnside: `(12³+3·4³+8·3³)/12`) | **178.0** | ✅ matches brute force |
| Physical state graph over `d(Δ³)` | 178 states, **one** connected component | ✅ |
| Little-group classification of the 178 states | trivial ×130, Z₃ ×26, V₄ ×21, A₄ ×1 | ✅ from stabilisers |
| Face-holonomy classes under gauge transform | invariant | ✅ |
| Region appearance (curvature + cycle charges) under gauge transform | invariant | ✅ |
| Bianchi identity `Σ_{∂R} ±Φ_f = 0` for abelian groups | holds for every labelling | ✅ |
| Conservation filter, `d(Δ³)` from random state | ~36 % of proposals accepted | ✅ measured |
| Conservation filter, Kuhn 3-ball (48 tets) | ~21 % accepted; interior moves 100 %, boundary moves rejected | ✅ measured |
| Internal dynamics on `d(Δ³)` under conservation | **zero** accepted moves from the vacuum | ✅ expected: no interior edges |

## Two counting traps (found the hard way, now guarded by tests)

1. **Canonicalize for reporting, never for exploration.** Right-multiplication does not
   commute with conjugation, so walking the state graph from canonical representatives only
   *loses transitions*: it finds 174 orbits instead of 178, missing exactly four pure-Klein-four
   configurations whose incoming edges come from non-canonical neighbours. Explore raw
   gauge-slice configurations, project to orbits afterwards — see
   [src/constraintnet/states.py](<src/constraintnet/states.py>).
2. **Re-gauge-fix after every move** before recording a state, or gauge copies inflate counts by
   up to `|G|`.

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
src/constraintnet/
  groups.py      finite-group engine (Z_n, A4) + word metric = the cost primitive
  complex.py     vertices / oriented edges / faces / tetrahedra; orientation-aware boundaries
  holonomy.py    curvature on faces, charge on cycles, Bianchi identity
  region.py      regions, signed boundaries, gauge-invariant Appearance (the sector label)
  gauge.py       gauge transforms, spanning-tree fixing, moduli enumeration, little groups
  seeds.py       d(Delta^3), bipyramid (both Pachner sides), Kuhn balls, stacked balls
  moves.py       elementary relabellings + Pachner 2<->3 with legality checks
  dynamics.py    the main loop: propose -> test boundary -> commit or revert
  states.py      canonical state ids and transition graphs over physical states
  objects.py     curvature clusters as matter candidates
  observer.py    relational coarse-graining, mesh fineness n, propagation delay
  viz/           animated interactive viewer (projection only; matplotlib)
tests/           the specification's strict tests + integrity guards (95 passing)
examples/        one runnable script per milestone
docs/            theory notes, conventions, architecture, findings
docs/figures/    pachner_2_3.svg -- both triangulations of the bipyramid
```

See [docs/SPEC.md](<docs/SPEC.md>) for the basement-to-capstone derivation,
[docs/PHYSICS_NOTES.md](<docs/PHYSICS_NOTES.md>) for what we verified and where the
specification had to be corrected, and [CHANGELOG.md](<CHANGELOG.md>) for progress.
