# Changelog

All notable changes to `constraintnet`. Versions follow the milestone numbering of the
programming specification; `[Unreleased]` holds work in progress.

## [0.1.0] — Milestone 1 (finite tetrahedral seed)

### Added
- **Group engine** (`groups.py`): abstract finite-group interface (identity, multiply,
  inverse, generators, conjugacy class, equality) with derived centralizers, element
  orders and a generator word metric used later as the cost/mass primitive.
  Implementations: `CyclicGroup(n)` (Z3 for testing) and `AlternatingGroup4`
  (`A4`, presentation ⟨s,t | s² = t³ = (st)³ = e⟩).
- **Simplicial complex** (`complex.py`): vertices, oriented edges, triangular faces,
  tetrahedra. Edge labels stored once per edge so the reverse-orientation rule
  `A_ji = A_ij⁻¹` holds by construction; tetrahedron orientation stored explicitly;
  `orient_consistently()` propagates orientations combinatorially; graph utilities
  (spanning tree, fundamental cycle basis).
- **Holonomy** (`holonomy.py`): face curvature `Φ_ijk = A_ij A_jk A_ki`, path and loop
  holonomies (= charge), conjugacy-class comparison predicate used by every conservation
  test, and the abelian Bianchi check.
- **Regions** (`region.py`): signed boundary faces with interior cancellation, closedness
  checks, probe cycles, and `Appearance` — the gauge-invariant data a region presents to
  its exterior (boundary curvature classes + cycle charge classes).
- **Gauge module** (`gauge.py`): vertex gauge transformations, spanning-tree gauge fixing,
  enumeration of gauge-fixed configurations, quotient by residual global conjugation, and
  a closed-form Burnside prediction as an independent cross-check.
- **Seeds** (`seeds.py`): `d(Δ³)`, single tetrahedron, triangular bipyramid in both
  Pachner-related triangulations, Kuhn (Freudenthal) triangulated 3-balls, stacked balls,
  random labelling. Grid coordinates attached for rendering only.
- **Test suite** (`tests/`): specification Tests 1–3 plus integrity guards — 54 tests.
- **Figure**: `docs/figures/pachner_2_3.svg`, the two triangulations of the bipyramid.

### Verified
- `A4`: 12 elements, closed multiplication, inverses, associativity, conjugacy classes
  of size 1/3/4/4, class equation `|cl(g)|·|C(g)| = 12`, element orders 1+3×2+8×3.
- Gauge fixing a spanning tree leaves exactly global conjugation as residual freedom.
- **1728 raw gauge-fixed tetrahedron configurations → 178 gauge-inequivalent classes**,
  matching the specification and independently predicted by Burnside's lemma.
- Face-holonomy conjugacy classes, loop charges and full region `Appearance` are invariant
  under gauge transformations while raw edge labels genuinely move.
- Bianchi identity `Σ_{f ∈ ∂R} ±Φ_f = 0` for abelian groups over random labelings; Kuhn
  ball boundary is a closed surface with `V − E + F = 2`.

### Corrected (against the specification)
- The spec's `boundaryHolonomy(region)` as "product of labels around the oriented boundary
  loop" cannot be a *surface* charge: for curvature `Φ = dA` that sum is identically zero.
  Charge is implemented on cycles (`Q_C = Φ_C`), and the open-surface Gauss law
  (flux through a disk = holonomy of its boundary) is tested instead.
- The spec's snippets treat `SimplicialComplex.vertices/edges/faces/tetrahedra` as plain
  attributes; they are implemented as accessor methods for consistency, and tetrahedron
  orientation had to be added as explicit state (absent from the spec) or boundaries do
  not cancel.

## Planned
- **0.2.0** Milestone 2 — boundary-preserving dynamics, accept/reject logging, transition-graph connectivity.
- **0.3.0** Milestone 3 — cone over `∂Δ³`, internal resolution counting (`|I(B)|`).
- **0.4.0** Milestone 4 — persistent defect with conserved charge class.
- **0.5.0** Milestone 5 — motion cost / first mass proxy.
- **0.6.0** Milestone 6 — interaction by gluing, joint resolutions, forbidden channels.
- **0.7.0** Milestone 7 — observer density and gravity-like propagation delay.
- **0.8.0** Milestone 8 — 3D visualization (projection only).
