# Changelog

All notable changes to `constraintnet`. Versions follow the milestone numbering of the
programming specification; `[Unreleased]` holds work in progress.

## [Unreleased] — Round 3 panel response + Astra merge

### Added
- **Z_N Gauss completion + N-ality classifier** (local Qwen, diary E069): `gauss_zn.py` — electric flux a_e ∈ Z_N
  with charges DEFINED by the solved constraint q_v := div(E)_v mod N (never configured independently), plus a pure
  pair-cancellation classifier that reports irreducible *N-ality content* (mesonic vs baryonic); `drivers.DriverGZN`
  Metropolis driver with exact inverse reverts (21 tests). Measured on the n=3 Kuhn ball
  (`examples/e069_nality_and_dyons.py`): **abelian N-ality delays annihilation but is NOT a selection rule** — all
  six seeded Z3 baryons decay within 12k steps (median delay only ×1.4 over mesons; the pre-registered three-body
  barrier does not exist because charge fuses additively at a vertex: two unit charges become the antiparticle of the
  third). **Abelian models contain no dyons** — magnetic observable unchanged by an electric string (4.508 vs 4.510)
  and a co-located charge–curvature correlation decays 0.257 → 0.053 (control level 0.053). Plasma threshold
  quantified: at β_E = 2 the *unseeded* vacuum carries ~26 spontaneous charges (baryonic 66% of steps); clean only
  for β_E ≥ 8 — E068's matched-vacuum lesson with numbers. Z2 confirmed to carry no baryonic content ever.
- Independent extent-based persistence criterion (local Qwen, diary E068): `persistence_metrics.py` — pure,
  charge-signature-free test of objecthood via extent stability + locality + matched-vacuum signal-to-noise
  (14 tests). INDEPENDENT of Milestone-4 `is_persistent`. Validated on relational curvature (`examples/e068_extent_vs_charge.py`,
  Z2 n=3, 500×3 seeds + matched vacuum): seeded lump rejected by both gates (lifetime 38, locality 0.88,
  SNR −0.2) — reproduces E066's negative verdict without using charge. TWO metric findings: locality alone
  misfires on a cold vacuum (lone object dominates → need vacuum-relative SNR); and CONFINEMENT ≠ PERSISTENCE
  (a Gauss-confined pair at high β_E annihilates — retracting the string lowers energy; matter needs a
  charge-conjugation selection rule). Confined-pair regime reported INCONCLUSIVE, not tuned to prior.
  CLAIMS row 61. Safety note: an accidental same-name overwrite of `persistence.py` was caught via git and
  restored before any harm.
- Hard Gauss completion v1 (local Qwen, diary E067): explicit matter-coupled classical Z2 phase space
  (`src/constraintnet/gauss.py`, `DriverG` in drivers.py) satisfying HANDOFF correction 2 — charges are
  DEFINED as q_v := div(E)_v over electric flux bits, so the Gauss constraint is SOLVED not penalized.
  By construction: charge parity identically even, isolated charge unconfigurable (charges are string
  endpoints), boundary vertices absorb charge as an exterior reservoir (the open-boundary channel P32-3).
  `tests/test_gauss.py` (9 tests). `examples/gauss_confinement.py` measures a CONFINEMENT SCALE: mean live
  charge count falls monotonically in string tension beta_E (30.3→1.5 across 0..8), bound-pair fraction
  rises 0→0.75; and the magnetic vacuum stays COLD (#curved faces max = 0) at every beta_E — E066's runaway
  heating was an artifact of RELATIONAL acceptance, not intrinsic. CLAIMS row 60;
  figure `reference/local_qwen/figures/e067_gauss_confinement.png`.
- Free space v1 — DriverC (local Qwen, diary E066): Pachner 2<->3 relinkings added to the relational
  move set (`src/constraintnet/drivers.py::DriverC`, model `freepach-v1`); entailment can now lay the
  adjacency it travels on. `tests/test_driverC.py` (8 tests) pin: interior relinkings never vetoed,
  boundary sphere + canonical state frozen, Euler V−E+F−T=1 step-by-step, NO-TELEPORTATION (surviving
  faces keep holonomy). `examples/free_space_tracking.py` measures a combinatorial tracking boundary:
  relinking is a genuine relocation channel (~2/3 of tracked support changes; first displacement steps
  {4,3,1} vs label-only {34,20,1}), BUT naive overlap-lineage survival is a metric failure — the vacuum
  heats (6→~230 A / ~370 C curved faces) and tracked clusters end at 96–100% of global curvature.
  Persistence needs extent-normalization vs matched vacuum + confinement beyond boundary freezing.
  CLAIMS row 59; figure `reference/local_qwen/figures/e066_free_space_accretion.png`.
- F8 scaling study (local Qwen, diary E065): `examples/f8_scaling_study.py` — invariants hold at
  n=3 / 500 steps × 2 seeds / quotient depth k=1..4 for all six groups. MECHANISM FINDING (prior
  refuted): whole-complex DriverA(relational) accepts ONLY purely-interior-edge proposals (zero
  surface acceptances in 12,000 moves), acceptance rate = closed-form interior-edge fraction
  (0.265 → 0.419 with n, Euler on the sphere) — bulk churns freely, boundary frozen; whole-complex
  accept rates are geometry-dominated and not comparable to single-tetrahedron baselines (CLAIMS
  row 58). Records `reference/local_qwen/data/f8_scaling.json`. F8 closed.
- Universality matrix + property suite (local Qwen, diary E064): generic `TableGroup` with axioms
  verified at construction; S3/Q8/D4 registered alongside Z2/Z3/A4. Tetrahedron-seed landscape:
  zero closed nonvacuum plateaus for ALL six groups (physical states 8/27/49/176/176/178;
  brute-force orbits == Burnside against hand-computed values; A4 little-group census reproduces
  pinned 130/26/21/1) — CLAIMS row 26's vacuum-only-basin result survives non-abelian generalization
  within the tested set (row 57). New `tests/test_properties.py` (73 seeded tests: gauge invariance,
  DriverA relational conservation recomputed from the complex, cross-group Pachner round-trips,
  oriented-edge consistency, quotient==Burnside); first P2 draft failing on interior-face churn
  confirmed the designed boundary-only conservation asymmetry. Triage item 16 closed; F8 remainder
  partially closed (scaling study still queued). `examples/universality_matrix.py`,
  `reference/local_qwen/data/universality_matrix.json`. Suite green 454.
- P33 local recreation (local Qwen): independent from-scratch implementation of the registered
  virtual-pair perturbation protocol (`docs/P33_VIRTUAL_PAIRS.md`) without reading Astra's
  uncommitted sibling module — `src/constraintnet/defect_perturb.py`,
  `tests/test_defect_perturb.py` (9 tests), `examples/p33_effective_local.py`, records under
  `reference/local_qwen/data/`. All registered identities pass; K4 cancellation exact;
  bipyramid second order improves at every coupling; cross-check against Astra's archived run
  agrees to machine precision (band max diff 0.0 / 5.3e-15). Two bugs caught only by the
  asymmetric fixture recorded in diary E063; CLAIMS row 56.
- P32A (Astra): 48 explicit electric charge-pair preparations in Z2/Z3/A4 finite
  patches; matrix-free projector actions, unitary character strings and exact
  commuting-projector evolution. Path, endpoint, energy, translation-intervention
  and annihilation checks pass. `DEFECT_AUDIT.md` distinguishes finite penalties,
  hard gauge restriction and probability continuity; H freezes defect locations.
  P32-3/4 remain untested pending boundary/state-space definitions. Diary E061,
  claim 54, archived data and two new regression tests.
- Corrected rules (Opus, from the user's restatement + literature): `src/constraintnet/defect.py` (Gauss-law projector A_v,
  flatness B_f, H = -sum A - sum B, defects), `tests/test_defect.py`, `docs/CORRECTIONS_2026-09-20.md`, P32 registration,
  WORKING_STATEMENT amendment 2 (matter = constraint defect), diary E060. Flux of one edge = the closed ring of faces
  around it (6 or 4), verified on every interior edge.
- P31 spin-1/2 walker with a dynamic 2T quantum record (Opus): `src/constraintnet/spin_record.py`, `examples/p31_selfbind.py`,
  data. Circulation does no work on its surroundings (energies equal to 0.25-2.5%); nothing binds; joint Kramers protection
  untested. Diary E057; claim 53.
- P30 vacuum-churn sweep (Opus): `examples/p30_churn.py`, `p30_graphics.py`, data, figure. P29's disorder was the
  infinite-temperature limit (92% curved); A4 circulation is permanent below ~10% curvature and short-lived above;
  the 2T lift is permanent at every level. Diary E056; claim 52.
- P29a/P29b tails and the spin-1/2 lift (Opus): `examples/p29_tail.py`, `examples/p29b_spin.py`, data `p29a_tail_v2.json`,
  `p29b_spin.json`. Time-reversal K with K^2=+1 forbids stationary current outside degenerate eigenspaces; random A4 labels
  leave none; the 2T spinor lift gives K^2=-1, Kramers degeneracy and circulation (bias 0.76-0.93) carried by the field.
  DYNAMICS_DESIGN section 17; diary E055; claims 50-51.
- P28 compact-loop kinematics (Opus): `examples/p28_compact.py`, data `p28_compact.json`. Only phases 0 and pi; existence
  law H a = e^{iL theta} a; 1/sqrt(weight) amplitudes (triangles work); zero current including 0/pi superpositions;
  two-traversal internal return on odd loops with order-2 holonomy. DYNAMICS_DESIGN section 16; diary E054; claim 49.
- P27 written up (Astra's run, appended by Opus): outcome in PREDICTIONS, claims 47–48, diary E053. The P26 dressed
  loop is a calm loop and slightly worse than plain calm seeds; no directed current; compact-eigenray no-current theorem.
- P25 seeded patterns in a compatible cooled bath (Opus): `examples/p25_seeded.py`, `p25_graphics.py`, data `p25_*.json`,
  figure. No birth shock; exact permanence in a frozen bath; slow erosion from record motion; 90° loops outlast 60°.
  DYNAMICS_DESIGN §13; diary E051; claim 45.
- P23 radiative cooling + P24a redshift proxy (Opus): `examples/p23_radiative.py` (trajectory unravelling, ladders,
  lowest-band spectral filter), `examples/p23_graphics.py`, data `p23_*`, `p24a_*`, figure. Folding diagnosis; narrow low light
  cools the record; E* falls with redshift. DYNAMICS_DESIGN §12; diary E050; claim 44.
- P22 freeze-out (Opus): open-wall mode for `QuantumRecordWalk` (escape bookkeeping), `examples/p22_freezeout.py`,
  `p22_graphics.py`, data `p22_*.json`, test. Hot dynamic record is opaque (power-law release), no cooling; P22-3/4 priors failed.
  DYNAMICS_DESIGN §11; diary E049; claim 43.
- P21 option A at small scale (Opus): `src/constraintnet/qrecord.py` (`QuantumRecordWalk`), `examples/p21_quantum_record.py`,
  `p21_summary.py`, `p21_graphics.py`, `tests/test_qrecord.py`, data `p21_*.json`. Exact accounting; free light
  coherent in a weak quantum vacuum; the DF loop responds to the record (dynamic ≫ quenched); no binding. DYNAMICS_DESIGN §10;
  diary E048; claim 42.
- v4.1-sc `RecordWalk` (reversible record engine, tested) + P20 registration; P20 withdrawn and the rule
  retired on energy accounting (user objection accepted). Options A/B/C in DYNAMICS_DESIGN §9. Diary E047.
- P19 run (Opus): `src/constraintnet/walk.py` (v4.0 ArcWalk engine), `examples/p19_walk.py`,
  `tests/test_walk.py`, data `reference/opus_session/data/p19_*.json`. Engine passes a–d; P19e negative
  (a frozen record does not trap). Diary E046; claims 40–41; design gate → v4.1.
- v4 dynamics design (Opus with the user): `docs/DYNAMICS_DESIGN.md`, `examples/v4_design_checks.py`,
  `tests/test_v4_design.py`; P19 registered (not run). Framing reconciled (README preface, CLAIMS note,
  MEMO_PATCHES P11, ELECTRON_TARGET, PARTICLE_PROGRAM): matter = trapped circulation; mass = translation
  rewrite cost = maintenance cost. Working statement clause 12 (references only between structures) and item L.
- `docs/WORKING_STATEMENT.md` (v4 integrated picture, status per clause) and P18 light fronts (Opus):
  `docs/PROPAGATION.md` (D1–D7), `examples/propagation_test.py`, `propagation_graphics.py`,
  `tests/test_propagation.py`, data, and figure `out/p18_propagation.png`. Diary E044; claims 38–39.
- P17 trapping (Opus): `docs/TRAPPING.md` (theorems T1–T6), `examples/trapping_test.py`,
  `trapping_depth_rates.py` (mpmath), `trapping_graphics.py`, `tests/test_trapping.py`, data and figure
  `out/p17_trapping.png`. Diary E043; claims 36–37.
- P16 bag test (`examples/bag_test.py`, `tests/test_bag_test.py`, `reference/opus_session/data/bag_test.json`)
  and `docs/BAG_PICTURE.md` (why/how of the wake/bubble picture, job spec for a cone extension,
  twist/fermion correction, sum-over-paths assessment). Diary E042; claim 35.
- P15 (Opus): non-commuting linked flux fixtures in full A4 (`examples/noncommuting_link_audit.py`,
  graphics script, `reference/opus_session/data/noncommuting_link_audit.json`,
  `out/p15_noncommuting_links.png`). A forced V4 tether is confirmed. Greedy ordered
  erasure is nonincreasing in all six arms. One-edge census included. Tie-order
  amendment declared before measurement.
- P14 outcome recorded (Astra run, Opus reproduction); `tests/test_link_order_and_noncommuting.py`
  (P14 replay, P15 fixture/commutator/tie/erasure pins). Diary E040–E041, claims 32–34.
- P13/P13b topology audit: exact linking, prescribed linked flux fixtures in Z3
  and an A4 subgroup lift, full one-edge domain census, 38-move nonincreasing
  merger and 140-move erasure certificates (one +1 step), and reproducible figure.
  Constructive fixed-boundary rewrite-connectivity proof and path verifier.
  Original bounded-search cutoff retained as inconclusive.
- P12 constructive decay certificates: both archived A4 n=5 nonvacuum endpoints
  reach flat vacuum in two downhill moves (8→4→0 and 10→6→0), with full-action,
  boundary, inverse, and gauge-transport verification. Bounded raw-state plateau
  search distinguishes closed plateaus from inconclusive budget exhaustion.
  Reproduce with `python examples/particle_decay_certificates.py`.

### Fixed
- Linking signs now include over/under depth, use rational predicates, and reject
  uncertified projections; the skipped Hopf-link test now runs. Closed-loop
  classification checks face incidence to exclude boundary-open arcs. Dual
  embedding uses an actual cycle walk and rejects nonadjacent tetrahedra.
- **F1 justification drift**: false "never within a fixed fibre" sentence corrected; `pointwise_stabilizer()`
  + `within_fibre_resolution_orbits()` shipped; three-convention warning (rigid/within-fibre/pooled);
  pins: flat-B stabilizer 12 constants, five-face raw 72→rigid 6→within-fibre 2, star-3 →1.
  E034 marked with erratum (amended, not rewritten).
- **F4 gluing gauge-variance**, escalated by Astra's counterexample: per-edge class equality was too
  coarse; `compatible_on_shared_face` now offers three named conventions — `raw` (historical control),
  `classes` (coarse observable), **`relational`** (default: one simultaneous frame alignment for all
  shared-edge fluxes). Absorption phase structure measured per convention (curved ensemble is
  phase-invariant at 36 under relational; flat stays modulated).
- **F5 Pachner bookkeeping**: orphan face after 2→3 dropped; revert(3→2) undoes via `move.added`;
  Astra hardening — link-condition guards, `_realized`/`_tet_orders` snapshot-restore, exact-snapshot undo.
- **F6 cavity blindness**: per-component canonicalization; Astra-caught shell-swap bug fixed (components
  keep min-vertex order; vertex gauge cannot move curvature between labelled shells).
- `spectral.py` invalid-escape warning (raw docstring); README memo link after file relocation.

### Changed
- **Driver A model provenance**: `DriverA(model="relational"|"legacy")`; relational (class-closed proposals
  + full canonical-state preservation) is the DEFAULT; legacy reproduces v0.x bit-for-bit as control arm;
  every record carries provenance. Historical numbers (accept ≈0.325, E035 negative) stand as LEGACY-model results.
- Class-closed arm move cost = 1 per nontrivial relabelling (conjugation-invariant); legacy keeps word metric.
- Driver B cycle spectrum explicitly labelled SCHEDULER DIAGNOSTICS (F7).

### Added (Astra import, reviewed and suite-verified)
- `curvature.py` (CurvatureState indexed arithmetic over declared action H = curved-face count;
  SupportLineage birth/death/merge/split tracking), `kinetics.py` (Metropolis curvature driver vs external
  bath; ledger bookkeeping), `landscape.py` (exact small-system landscapes: plateaus, downhill exits,
  nonincreasing-path distances).
- `tests/test_interaction_frames.py` (convention counterexamples, true apex-action invariance, counting
  identity physical = raw×|orbit|), `tests/test_curvature.py`, `tests/test_landscape.py`.
- `examples/critique/gluing_frame_counterexample.py`; particle search examples ×4;
  `docs/PARTICLE_PROGRAM.md` (four demonstration gates: candidate / fusion-fission / bound composite /
  chemistry — no catalogues, forces, or valences in the microscopic state).

### Documentation
- Diary **E036** (full R3 disposition incl. F2 retraction by synthesis author) + E034 erratum;
  `docs/CRITIQUE_TRIAGE.md` Round-3 table; **`docs/CLAIMS.md`** claims register (measured/derived/
  postulated/scheduler-artifact/parked × producing model) + protections list (R3 §4);
  P7 start-configuration controls recorded in `PREDICTIONS.md` before any run;
  `reference/astra_session/Astra_WORKING_STATE_2026-09-18.md` (provenance).

### Suite
- 285 collected, 284 passed + 1 skipped (Hopf linking, documented), zero warnings.

## [Unreleased, earlier] — Round 2 referee-audit response (wound-licking arc)

### Fixed
- **Pachner 2→3 built degenerate 3-vertex replacement tuples** and corrupted the complex when
  crashing mid-mutation; corrected to new-edge × face-edge tetrahedra + transactional guard;
  `tests/test_pachner.py` (12 tests) closes a coverage hole (the move had never been tested).
- **Observer density was population-blind**: shells of unequal size confounded activity with
  cell count; all fineness/delay readouts now use per-vertex density with baseline
  events/vertices.
### Added
- `moves.class_closed_generators` + `propose_edge_move(class_closed=True)`: conjugation-closed
  proposals make the Markov chain descend to gauge orbits (29.4% equivariance violations → 0).
- `Region.gauge_invariant_state()`: raw based-loop holonomies, basepoint-transported and
  simultaneous-conjugacy canonicalized — exact gauge invariant, strictly finer than appearance.
- `resolutions.pooled_resolution_orbits` + convention warning (rigid vs pooled |I|; referee's
  exact 6→2 reproduced on the 5-flux-face declaration).
- `spectral.py`: exact diffusion return probabilities and spectral-dimension estimates
  (kernel-pure, no RNG); matched-control finding: Kuhn diffusion ≍ cubic-lattice box.
### Documentation
- `docs/PREDICTIONS.md` (pre-registration log, live), `docs/CRITIQUE_TRIAGE.md` (all 17 audit
  items answered with evidence), `docs/RELATED_WORK.md` (literature map + do-not-contradict
  checklist); diary E033–E035.
### Negative results logged (no claim deleted silently — claims parked with reasons)
- Driver A event density is label-blind (vacuum = charged = neutral profiles bit-for-bit);
  M7 gravity content parked pending curvature-coupled event placement.
- Absolute d_s → 3 unmeasurable at toy scale (Z³ control reads ~2 too); matched-consistency
  statement pinned instead.

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

## [0.4.0] — Milestone 4 (persistent defect)

### Added
- **Persistence module** (`persistence.py`): `seed_charged_defect` / `seed_neutral_defect`,
  relational cluster tracking (`DefectTracker`, vertex-overlap identity matching, gap and
  split accounting), `TrackedDefect` with conserved `charge_core`, and `is_persistent`
  implementing the specification's three conditions with semantics forced by measurement.
- **Experiment harness** `run_persistence_experiment(kind=charged|neutral)` reporting
  confinement statistics (accepted/rejected split by interior vs surface support),
  curvature-heating time series, tracking metrics and strict conservation checks.
- `examples/milestone4.py` — runnable narrative with internal assertions.
- `tests/test_persistence.py` — spec Test 5 plus confinement theorems and a tamper guard
  proving `charge_core_stable` is not vacuously true. Suite now **121 tests**.

### Verified
- **Confinement is exact**: over 1500 steps on the closed Kuhn ball (n=2), surface-edge
  moves were rejected **1108/1108** and interior moves accepted **392/392** — charge can
  never leak through an observed boundary, and nothing inside ever can.
- **Spec Test 5**: the charged defect's conserved external signature (two frozen boundary
  faces, order-2 class) is identical at start and end; universe sector invariant throughout.
- **Persistence theorem holds empirically**: with nontrivial cycle/face charge, curvature
  never vanishes (`ever_flat: False`) while the interior churns chaotically.
- Tracked identity survival 100 %, zero gaps, cluster stays a single connected structure.
- **Negative control**: the neutral lump (interior seed, trivial external signature)
  correctly fails `is_persistent` — nothing measures it, so it is a virtual fluctuation,
  not matter. `matter := nontrivial conserved external residue`.

### Finding: interior heating and diffusion
Because every strictly-interior relabelling is accepted unconditionally, curvature *heats*
and diffuses through the bulk (curved-face count wanders 3 → 72 in 1500 steps). Localization
of matter is therefore anchored by the frozen core — the conserved external residue — and
never by the halo. This sharpens the M5 region-relativity question (PHYSICS_NOTES §6):
any mass proxy must be defined against a fixed watched region, since free interior churn
makes unanchored "defect position" meaningless.

## Planned
- **0.4.1** Milestone 4b — cone demo in the viewer: frozen core vs flickering halo (nice-to-have).
- **0.5.0** Milestone 5 — motion cost / first mass proxy.
- **0.6.0** Milestone 6 — interaction by gluing, joint resolutions, forbidden channels.
- **0.7.0** Milestone 7 — observer density and gravity-like propagation delay.
- **0.8.0** Milestone 8 — 3D visualization (projection only).
