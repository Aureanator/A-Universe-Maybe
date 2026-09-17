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

## [0.2.0] — Milestone 2 (boundary-preserving dynamics) + viewer

### Added
- **Dynamics** (`dynamics.py`): the specification's main loop -- propose, apply temporarily,
  test whether the watched region's `Appearance` is preserved, commit or revert. Conservation
  is not a rule bolted on; it *is* the acceptance predicate. Event log, accept/reject stats,
  per-edge rejection counts, optional probe regions ("this observer watches that object").
- **Canonical states** (`states.py`): `StateId` = orbit representative + superselection sector;
  `transition_graph()` exploring raw gauge-slice configurations and projecting to orbits.
- **Observer layer** (`observer.py`): cells defined *relationally* (graph-distance shells or an
  explicit vertex grouping -- never coordinates), event recording, density `rho`, mesh-fineness
  `n = rho/rho0`, curvature proxy `rho - rho0`, and `propagation_delay(path)` where dense cells
  cost more reductions.
- **Object detection** (`objects.py`): curved faces, edge-connected curvature clusters, per-cluster
  class summaries (Milestone 4 groundwork).
- **Animated interactive viewer** (`viz/`): live 3D view with play/pause, single-step, speed slider,
  layer toggles and keyboard shortcuts; accepted moves flash green ▲, rejected ones red ✗;
  curvature clusters drawn as spheres; vertex size/colour = mesh fineness; a white star carries a
  test implication through the mesh so delay is visible. Identical code path records GIFs headlessly.
  Demos: `--demo tetra | orbit | lattice` (`python -m constraintnet.viz`).
- **Layout** (`viz/layout.py`): grid-metadata or deterministic force-directed embedding; verified
  label-independent, i.e. purely a projection.

### Measured
- Transition graph over `d(Δ³)`/A4: 1728 slice configurations → **178 physical states in one
  connected component**; little groups trivial ×130, Z₃ ×26, V₄ ×21, A₄ ×1.
- Conservation filter: interior-edge moves accepted 100 % of the time (they cannot be seen from
  outside), boundary-edge moves rejected generically; ~36 % acceptance on `d(Δ³)` and ~21 % on a
  48-tetrahedron Kuhn ball. From the vacuum, `d(Δ³)` accepts **zero** moves -- no interior edges,
  hence no internal degrees of freedom.
- Signals cost strictly more reductions through loaded cells than through the vacuum.

### Fixed (both would have silently corrupted results)
- **Canonicalize for reporting, never for exploration.** Exploring only canonical representatives
  loses transitions because right-multiplication does not commute with conjugation: it found 174
  orbits instead of 178, missing exactly the four pure-Klein-four configurations. Regression test
  added (`tests/test_states.py`).
- `move_generators()` returned only inverses, dropping the generators themselves and skewing the
  word metric that serves as the cost/mass primitive.
- `detect_candidates()` clustered *all* faces, so the flat vacuum registered as one giant matter
  candidate; it now clusters only curved faces.
- Observer baseline: using the emptiest active cell as `rho0` is degenerate early in a run (the one
  populated cell becomes its own reference and every reading says `n = 1`, hiding all delay). Now
  the uniform expectation `total_events / n_cells`.
- `Appearance.signature()` contained lists, so sector ids were unhashable; nested tuples now.
- `Move` dataclass fields lacked annotations (silently ignored by `@dataclass`).
- `Region.appearance()` on a complex with no tetrahedra reported "nothing to protect"; such a
  complex is now treated as its own observable surface, otherwise conservation did nothing there.

## [0.3.0] — Milestone 3 (cone over `∂Δ³`: hidden internal states)

### Added
- **Resolutions** (`resolutions.py`): the cone `v * ∂Δ³` (= `Δ⁴`) with four genuine internal
  edges `x_i = A_{*i}`; admissibility `Φ_{(*ij)} = x_i A_ij x_j⁻¹ ∈ c_ij`; quotient by the
  boundary-invisible gauge `x_i → ν⁻¹ x_i` (only the apex transforms); `ResolutionSpace.kind()`
  classifies a boundary as light-like / matter-like / forbidden; `resolution_table()` produces a
  complete flux census in one pass over all `|G|⁴` interiors instead of `|G|⁶` searches.
- **Seeds**: `make_cone_over_tetrahedron(group, apex, seed_labels)` returning `(complex, apex, boundary)`.
- **Example** `examples/milestone3.py`; 19 new tests (`tests/test_resolutions.py`) — 114 passing.

### Measured (exact brute force over ≤ 20736 assignments, not sampled)
- Cone combinatorics: `V=5, E=10, F=10, T=4`, `χ = 1`.
- **Flat boundary + zero flux → `|I| = 1`** (light-like). Raw count is exactly `|G| = 12`: the free
  apex gauge, everything else forced by flatness — matching the closed-form derivation
  (`x_j = x_i A_ij` around the boundary is consistent iff `B` is flat).
- **Curved boundary + zero flux → `|I| = 0`** for every random seed tested: a single interior vertex
  cannot cap off curvature. Matter needs more interior than one vertex.
- **Uniform order-2 (Klein four) flux on all six interior faces → raw 72, `|I| = 6`.** The
  representative is literally the three nontrivial elements of `V₄` on the apex edges: a charge knot.
- Full census for flat `B`: **103 realisable flux patterns out of 4096**, with
  `|I| ∈ {1, 3, 4, 6, 12, 16, 24, 36, 48}`; the **vacuum is the unique light-like pattern** — every
  other realisable interior hides at least three states.
- Uniform order-3 flux is unrealisable (three equal order-3 curvatures do not close around a
  triangle), while uniform order-2 does — an ordering/chirality effect of non-abelian-ness.
- **Abelian control: for `Z₃` every one of the 27 realisable patterns has `|I| = 1`.** Hidden
  internal ambiguity requires a non-abelian group, exactly as the specification argues.
- `|I(B)|` is invariant under gauge transformations (it depends only on conjugacy classes), and
  materialising a resolution never disturbs the external boundary labels.

### Note on class indexing
Conjugacy-class *indices* follow `Group.conjugacy_classes()` order — for `A₄` that is
`[identity, order-3 (−), order-3 (+), order-2]`, which is **not** the textbook order. A label list
hand-written in an early exploration script mislabelled results; all reporting now derives names via
`Group.class_name`. Guarded by tests.

## Planned
- **0.4.0** Milestone 4 — persistent defect with conserved charge class (next).
- **0.5.0** Milestone 5 — motion cost / first mass proxy.
- **0.6.0** Milestone 6 — interaction by gluing, joint resolutions, forbidden channels.
- **0.7.0** Milestone 7 — observer density and gravity-like propagation delay.
- **0.8.0** Milestone 8 — 3D visualization (projection only).
