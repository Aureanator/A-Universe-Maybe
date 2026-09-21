# Referee critique triage — item-by-item answers

Source: `Incoming frontier model critique-advice/Synthesized critique.txt` (unified audit from
Opus, Astra, online-Qwen + external mathematical critique). Every claim was checked against
current HEAD before patching; several audits lagged the commits. Verdicts below carry evidence
links to probes (`examples/critique/`), pre-registrations (`docs/PREDICTIONS.md`), tests, and
commits. Discipline: predictions written before runs; misses kept visible; nothing tuned.

**Scorecard: 4 confirmed-and-fixed bugs/hazards, 2 confirmed-with-fixes-shipped, 3 accepted-and-queued,
3 rebutted-or-outdated, 2 open-problems-named, 1 user-overridden.**

---

## Phase I — "bleeding cracks"

### Item 1 — Incomplete gauge quotient (the μ inflation of |I|)
**Verdict: CONFIRMED as convention hazard; REBUTTED as bug in `resolutions.py`. Fixed tooling shipped.**

- The cone fibre over a FIXED boundary admits no merging: any gauge preserving B pointwise acts
  through the apex only, which is exactly what we quotient by. Merging happens only when the
  boundary is held to its appearance and interiors are pooled across gauge copies of B.
- Measured (`examples/critique/p1_mu_quotient.py`, pinned in `tests/test_pooled_resolutions.py`):
  flat-boundary declarations — star-3 V4: raw 36 → rigid **3** → pooled **1**;
  5-face V4: raw 72 → rigid **6** → pooled **2** (the referee's exact pair, verbatim);
  all seeded patterns over the 1728 tree-gauge boundaries: rigid |I| = 4 everywhere (E030 intact)
  → pooled 1 in 40/40 sampled.
- Meta-finding: our own probe's first rigid column used conjugation instead of left-multiplication
  for the apex action; library cross-check caught it (the E018 lesson again — verify the action
  you quotient by, in code). Corrected numbers come from `resolution_space` itself.
- Shipped: convention warning at module top (`resolutions.py`), `pooled_resolution_orbits()` for
  the alternative semantics, slow tests pinning both counts. E030's |I(core)|=4 is rigid by
  definition and remains valid; every quote now states its convention.
- Z₃-blindness: accepted exactly as stated — abelian conjugation is trivial, control cannot fail.
- Commits `f968021`, `e27fb9c`.

### Item 2 — `Appearance` basis-dependent and lossy
**Verdict: CONFIRMED (both halves). Fixed.**

- Measured (`examples/critique/p2_root_dependence.py`): **17.0%** of single-edge moves flip their
  full-appearance verdict across spanning-tree roots (their number: 12.4%; same mechanism — the
  cycle-charge component; face curvatures are basis-free and behaved as predicted).
- Within one run the predicate is self-consistent (fixed root); cross-basis/cross-region
  signature comparisons were unsound — acknowledged.
- Lossiness confirmed: appearance's class-tuples collapse the 178 physical tetrahedron classes to
  82; `Region.gauge_invariant_state()` (raw based-loop holonomies transported to one basepoint,
  simultaneous-conjugacy canonical form) is exact-under-gauge and strictly finer — pinned by
  `tests/test_gauge_canonical.py` (>82 separation on the slice).
- Commit `dfaab17`.

### Item 3 — Gauge-variant dynamics / proposal asymmetry
**Verdict: FULLY CONFIRMED (worse than reported). Fixed with a new arm.**

- Exhaustive measurement (`examples/critique/p3_gauge_equivariance.py`): default proposals via
  `move_generators()` give **29.4%** of gauge-equivalent config pairs different reachable-orbit
  counts over the full 1728×12 slice sweep. The chain does not descend to orbits.
- Class-closed arm shipped: `class_closed_generators()` + `propose_edge_move(class_closed=True)`;
  **0 violations**, exact reachable-orbit-SET equality, pinned by test.
- Kept the default arm as a documented hypothesis (Layer-2 item 6 made move-set choice a run
  parameter with reachability assertions); the audit's point now holds by construction when
  requested and is labelled where not. Word-cost caveat documented in docstring.
- Commit `dfaab17`.

### Item 4 — Pachner 2→3 degeneracy bug
**Verdict: CONFIRMED — real bug at HEAD. Fixed. We predicted it would NOT reproduce; pre-registration caught us being wrong.**

- `apply_pachner_2_3` literally built `((u,w,a),(u,w,b),(u,w,c))` — 3-vertex tuples where
  4-vertex tetrahedra are required — crashing mid-mutation after partial mutation (explains every
  cascading MoveError the auditors saw). No test had ever exercised the move.
- Fixed to new-edge × face-EDGE tets `(u,w,a,b),(u,w,b,c),(u,w,c,a)` + transactional guard;
  `tests/test_pachner.py`: legality, boundary preservation (faces AND labels), exact revert,
  sequential re-scanned stability — 72/72 Kuhn n=2 sites clean.
- Commit `1434a1c`.

---

## Phase II — tautologies

### Item 5 — Confinement is a predicate
**Verdict: ACCEPTED as framing critique.** "Surface moves rejected 1108/1108" proves the
acceptance predicate forbids boundary change; it is a unit test, not a phenomenon. Reframed in
docs wherever quoted. The real experiment — softened predicate (boundary violations allowed at
penalty λ, does an area law emerge dynamically?) — is pre-registration P7, queued as the first
genuine physics paper of the programme. Not yet run; no claim made until it is.

### Item 6 — Persistence enforced by tracker definition
**Verdict: PARTIALLY ACCEPTED.** The conserved `charge_core` in `DefectTracker` is exact
conservation (frozen boundary-face classes), not cluster bookkeeping — the audit partly conflated
cluster membership with charge. But the critique's core stands for the *localization* claim: an
expanding curved-face cluster satisfies "connected" trivially. Independent criteria (bounded
extent, structural similarity across window, lifetime, mobility under probe) are specced and
queued; until then persistence claims carry this caveat explicitly.

### Item 7 — Theorems disguised as measurements
**Verdict: CONFIRMED labeling issue; fixed in documentation, split pinned by tests.**
`transition_graph(legitimacy="none")` is kinematic (its own docstring says so) and the
appearance-frozen single tetrahedron result (1 node, 0 accepted edges — total freeze) is a
theorem, already measured as such in `test_states.py`. Results tables now mark theorem vs
measurement; dynamical reachability on larger complexes remains available from Driver A logs
(queued: explicit table row once M2 numbers are regenerated).

---

## Phase III — axiomatic schisms

### Item 8 — Arrow of time missing
**Verdict: ACCEPTED, named open problem.** Current dynamics are reversible rearrangements under a
symmetric conservation law; Driver B's σ gives a clock (cycle spectrum), not an arrow. The entropy
functional S(R) = log|I(∂R)| exists but no monotonicity theorem or Lyapunov candidate is known.
Honest renaming option ("implications rearrange subject to boundary conservation") recorded in
PHYSICS_NOTES; the axiom's directedness is currently an interpretation of reduction *events*, not
a theorem of the update rule. This is nominated as the theory's hardest open problem.

### Item 9 — Dimension and topology by fiat
**Verdict: PARTIALLY RESOLVED (measured, honestly bounded).** New `spectral.py` + probe: exact
diffusion return probabilities; Kuhn balls read d_s = 0.6→1.8 rising with size — and the matched
Z³-box control reads ~2.0 at comparable size, so absolute "returns 3" was naive at accessible
meshes (finite-size/backtracking dominance). Defensible pinned claim: Kuhn diffusion is consistent
with cubic-lattice behaviour (no fractal collapse), by matched control. PL type remains an input —
declared as such; topology change via the now-fixed Pachner moves is available but unexercised in
physics runs. Commits `7a6087f`.

### Item 10 — Kinematic vs dynamic graph conflation
**Verdict: RESOLVED as documentation.** The codebase already separates them (`states.transition_graph`
legitimacy modes; Driver logs for the dynamical subgraph). Formal statement added to triage and
diary: charge lives on the kinematic implication complex (all possible cycles); time is the
partial order generated by ACCEPTED reductions only. No conflation remains in current claims.

### Item 11 — God's-eye observer
**Verdict: USER OVERRIDE, partially served.** The external observer stays ("we are PAYING to see
inside"). Internal-observer primitives already exist and are gauge-invariant (`Region.probe_cycles`,
`gauge_invariant_state`); building the full internal-observer-agreement test (two regions must
agree on gauge-invariant delay differences) is queued alongside backlog item 11.

---

## Phase IV — missing physics

### Item 12 — No first law / thermodynamics
**Verdict: ACCEPTED, queued with design.** Weighted dynamics accept ∝ exp(−λ·Δcost) + a conserved
ledger (total cost, event count, curvature under accepted moves) is specced; detailed-balance and
fluctuation–dissipation checks follow. No route-to-Einstein claim is made anywhere in the repo
while this is missing.

### Item 13 — Gravity is an analogy; ρ confounds activity with cell size
**Verdict: CONFIRMED + found WORSE than stated. Normalization fixed.**
- Population-aware density shipped (`rho_per_vertex`, baseline = events/vertices); regression test
  pins equal-per-vertex activity → equal n across shell sizes. Raw-count artifact measured at
  corr(rho, |shell|) = +0.41.
- **Deeper finding (P6):** vacuum / charged / neutral Driver A runs are *bit-for-bit identical* —
  acceptance depends only on interior-vs-surface edge membership, so event density carries ZERO
  matter information under this driver. The M7 gravity claim currently has no empirical content
  beyond acceptance-region geometry; the delay layer was already formula-prescribed (backlog item
  4 remains the gate). Nothing deleted or tuned; status stated plainly. Commit `f968021`.
- Scalar-vs-tensor critique accepted as open: a density factor can at best fix a conformal factor;
  rank-2 structure is not claimed anywhere current.

### Item 14 — Quantum layer aspirational (no F/R, no interference)
**Verdict: MOSTLY OUTDATED against HEAD.** Two-path interference EXISTS (`fringe.py`: discrete
Aharonov–Bohm two-path interferometer, visibility by exact counting; flux = which-path information;
Z₃ ω-weighted control). Category data exists (E031: monodromy = θ_c/(θ_aθ_b) on all 520 D(A₄)
channels, max err 2.4e-15; Hom dims == Verlinde everywhere — fusion derived twice; pair-channel
R-eigenvalues). Born measure remains DECLARED postulate (open problem, not derivation) — the audit
is right about that one sentence only.

---

## Phase V — epistemics

### Item 15 — No pre-registration
**Verdict: FIXED as practice.** `docs/PREDICTIONS.md` opened before any critique-response run; it
has already earned its keep twice this session (P4 miss caught a real bug narrative; P5 miss
showed the demand "returns 3" was itself naive).

### Item 16 — No universality matrix (S₃, Q₈, D₄)
**Verdict: FIXED (E064, local Qwen).** S3/Q8/D4 registered via axiom-verified `TableGroup`; sweep
run on the tetrahedron seed across {Z2,Z3,S3,D4,Q8,A4}: zero closed nonvacuum plateaus for every
group, orbit counts == Burnside (values hand-computed before execution), A4 little-group census
reproduces the pinned 130/26/21/1. Row 26's vacuum-only-basin result now holds within the tested
set including non-abelian groups with centers — a large center (Q8) is not sufficient to protect a
basin under action H. Feature-to-group-property mapping beyond this (commutator subgroups etc.)
remains open if future results need it.
Evidence: `examples/universality_matrix.py`, `reference/local_qwen/data/universality_matrix.json`,
CLAIMS row 57.

### Item 17 — Unpositioned against literature
**Verdict: FIXED.** `docs/RELATED_WORK.md` maps every module to lattice gauge theory,
Dijkgraaf–Witten TQFT / Kitaev, Regge calculus, causal sets, spin foams, and analog gravity, with
a do-not-contradict checklist (Elitzur, Elban-Gowda, fermion doubling, Coleman-Mandula caveat,
no-signalling).

---

## Round 3 — panel memorandum F1–F8 (full disposition in diary E036)

| Finding | Verdict | Disposition |
|---|---|---|
| **F1** μ-justification false; stabilizers act inside the fibre | CONFIRMED, two-referee | `pointwise_stabilizer()` + `within_fibre_resolution_orbits()`; three-convention warning; E034 erratum appended; pins: flat-B stab 12 (144 w/ apex), five-face 72→6→**2**, star-3 →1 |
| **F2** convention-warning numbers transposed | **RETRACTED by synthesis author** ("bad compression of Opus's table") | No contradiction existed; numeric quote removed from the warning anyway during the F1 rewrite — warnings now point at pinned tests, not prose tables |
| **F3** Driver A shadow-fix wiring | FIXED | `DriverA(model="relational"\|"legacy")`; relational (class-closed + canonical-state) is the DEFAULT; every record carries provenance; legacy reproduces v0.x bit-for-bit as control |
| **F4** gluing gauge-variance | FIXED, then ESCALATED by Astra's counterexample | Three named conventions (`raw`/`classes`/`relational`, default relational = one simultaneous frame); frames suite incl. counting identity physical = raw×\|orbit\|; NEW: absorption phase structure is convention-dependent (curved ensemble phase-invariant at 36 under relational) |
| **F5** Pachner orphan face + reverse-revert raise | FIXED + hardened | Drop uncarried face; revert via `move.added`; Astra guards: link conditions, `_realized`/`_tet_orders` snapshot-restore, exact-snapshot undo test |
| **F6** cavity blindness in canonical state | FIXED (Astra caught a bug IN the first fix — shell-swapping sort) | Per-component independent canonicalization in min-vertex order; `test_curvature_cannot_swap_surface_components`; completeness claim domain stated exactly |
| **F7** Driver B not gauge-equivariant | ACCEPTED as labelling | Cycle spectrum labelled SCHEDULER DIAGNOSTICS in class docstring; physics claims from sigma must be orbit-canonicalised |
| **F8** word-cost gauge dependence; property-suite coverage | FIXED | Class-closed arm cost = 1 per nontrivial relabelling (conjugation-invariant); legacy keeps word metric. Property suite E064 (`tests/test_properties.py`, 73 seeded tests, six groups); scaling study E065 (n=3, 500×2 steps/cell, quotient depth k≤4 — all invariants hold; whole-complex accept rate characterized as closed-form interior-edge fraction, CLAIMS row 58) |
| P7 design note | ADOPTED | Start-configuration control required alongside λ sweep (near-flat start is an independent forcing reason) — recorded in `PREDICTIONS.md` before any run |

---

## What the referee got wrong (for completeness)

1. Item 4's location was right but our pre-run prediction that it wouldn't reproduce was wrong —
   credited to them; the bug class (crash mid-mutation corrupting state) is exactly what they said.
2. Item 14 assumed an older snapshot: interference and category data landed before the audit.
3. Item 9's demand ignored finite-size effects that make "d_s returns 3" unmeasurable at our mesh
   sizes even for Z³ itself; we replaced it with a matched-control statement that survives scrutiny.
4. Item 1's "inflated by up to 12×" is convention-relative, not an error in the rigid count — but
   the pooled numbers (6→2 verbatim) show their instinct was pointing at something real.

## Standing queue created by this triage (+ Round 3 additions)

- P7 softened-predicate confinement pilot (area-law test) — first real physics target.
- **Free space / self-laid track — v1 DONE E066** (`DriverC`, `tests/test_driverC.py`,
  `examples/free_space_tracking.py`, CLAIMS row 59). Relinking integrated under relational acceptance;
  measured a genuine relinking-attributed relocation channel (~2/3 of tracked support changes) and a
  combinatorial tracking boundary that follows the object off-frame. Exposed naive overlap-lineage
  survival as a metric failure (vacuum heats, tracked cluster → ~100% of global curvature). FOLLOW-UPS
  kept below (subregion boundaries under relinking, edge birth/death beyond Pachner, stationary
  proposal scheme, extent-normalized persistence).
  <details><summary>original item text</summary>

  Integrate connectivity-changing moves
  into the driver move set under boundary preservation, so an entailment can lay the adjacency it
  travels on rather than only rewriting the gauge geometry of fixed rails. Current state: mainline
  `DriverA` proposes label moves only (`propose_edge_move`: A_e -> A_e g); Pachner 2<->3 exists as a
  reversible lab tool and is the dormant prototype for self-laid track; edge birth/death (implication
  creation/annihilation) does not exist at all. E065 nuance to respect: whole-complex relational
  acceptance is label-independent, so self-consistent track-building is expected to be a *boundary*
  phenomenon — the feedback loop closes only for boundary-conditioned regions or with global (Gauss)
  constraints. Needs a **tracking boundary** that follows an object wherever it wanders off the fixed
  frame (combinatorial recentering, not coordinates). Ultimate goal this serves: reproduce recognizable
  phenomena (p/e/n, atoms, fission/fusion, quantized line radiation) from first principles.

  </details>
- **Hard Gauss completion v1 — DONE E067** (`gauss.py`, `DriverG`, `tests/test_gauss.py`,
  `examples/gauss_confinement.py`, CLAIMS row 60). Explicit matter-coupled classical Z2 phase space with
  the constraint SOLVED (q_v := div E), satisfying HANDOFF correction 2. Measured a confinement scale
  (mean charge count 30→1.5 in beta_E; bound-pair fraction 0→0.75) and showed the magnetic vacuum stays
  cold at every beta_E — E066's heating was an acceptance-rule artifact, not intrinsic. FOLLOW-UPS: quantum
  amplitudes + nonabelian div; couple magnetic flux to electric strings (dyons = BOTH sectors); then mobile
  matter under a literal local Gauss law.
- Independent persistence criteria (extent, similarity, lifetime, mobility) — E066 sharpens this: naive
  overlap-lineage survival is vacuous under unconstrained acceptance; needs extent normalization against
  a matched vacuum control. E067 adds the tool: with Gauss solved, charge number is protected by construction,
  so persistence becomes measurable rather than tracker-dependent.
- Weighted dynamics + conserved ledger; detailed balance check.
- Dynamic signal delay (backlog item 4) — gate for any gravity language.
- Internal-observer agreement test (user-approved alongside god's-eye view).
- ~~Universality matrix S₃/Q₈/D₄~~ DONE E064 (CLAIMS row 57; zero closed nonvacuum basins, all six groups).
- Heat-kernel extrapolation or larger meshes for absolute d_s.
- Arrow-of-time: Lyapunov candidate or formal renaming decision (open problem, named).
- ~~F8 remainder: property-based invariant suite + scaling study~~ DONE E064/E065 (`tests/test_properties.py`, `examples/f8_scaling_study.py`, CLAIMS row 58).
- Particle program gates 1–4 (`docs/PARTICLE_PROGRAM.md`): unpinned persistent-structure search with negative controls; fusion/fission trajectory replay; bound-composite barrier; chemistry. Astra's audit queue items 1–4 closed this round; gate 2 onward is next.
