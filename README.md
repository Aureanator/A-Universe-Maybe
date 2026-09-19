# constraintnet — a universe out of directed implications

**Axiom: directed implications reduce.** Nothing else is assumed — no space, no time,
no matter, no energy, no observer, no continuum, no coordinates.

`constraintnet` is a discrete *event–constraint–simplicial* simulator built from that
axiom. Edge labels carry finite-group constraints; legitimate local reductions are
exactly those that preserve the boundary holonomy presented to the outside; persistent
topological defects are matter; rewrite cost is mass; interaction is boundary-compatible
gluing (fiber product of internal resolution spaces); and an observer coarse-grains
event density into effective 3D geometry and gravity-like propagation delay.

Coordinates exist only in the visualization layer. They never determine dynamics.

- Theory narrative & audit trail: [Memo.txt](<reference/theory_memo/Memo.txt>) (Qwen ⇄ Opus review thread)
- Spec-to-code map: [docs/SPEC.md](<docs/SPEC.md>) · findings: [docs/PHYSICS_NOTES.md](<docs/PHYSICS_NOTES.md>),
  [docs/R_TRACK.md](<docs/R_TRACK.md>) · conventions: [docs/CONVENTIONS.md](<docs/CONVENTIONS.md>)
- Claims register (status × producing model) & protections list: [docs/CLAIMS.md](<docs/CLAIMS.md>) ·
  particle/reaction program gates: [docs/PARTICLE_PROGRAM.md](<docs/PARTICLE_PROGRAM.md>)
- Independent audit scripts (external, with corrections): [reference/opus_audit/](<reference/opus_audit/README.md>)

## Quick start

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install pytest matplotlib numpy   # Windows
PYTHONPATH=src .venv/Scripts/python.exe -m pytest -q              # 285 tests (~4 min incl. slow)
PYTHONPATH=src .venv/Scripts/python.exe examples/milestone1.py    # reproduce 1728 -> 178
PYTHONPATH=src .venv/Scripts/python.exe examples/milestone3.py    # hidden internal states |I(B)|
PYTHONPATH=src .venv/Scripts/python.exe examples/milestone4.py    # persistent defect + confinement
PYTHONPATH=src .venv/Scripts/python.exe examples/core_entropy.py  # E030: core entropy |I|=4, exact at 12^14 scale
```

## Watch it buzz

Interactive window with live animation, play/pause, single-step, speed control and layer
toggles (headless GIF path is the same code):

```bash
PYTHONPATH=src .venv/Scripts/python.exe -m constraintnet.viz --demo lattice --group A4 --n 2
PYTHONPATH=src .venv/Scripts/python.exe -m constraintnet.viz --demo tetra    # d(Delta^3), conservation bites
PYTHONPATH=src .venv/Scripts/python.exe -m constraintnet.viz --demo orbit    # tour the 178 gauge classes
PYTHONPATH=src .venv/Scripts/python.exe -m constraintnet.viz --demo lattice --gif out/buzz.gif --frames 200
PYTHONPATH=src .venv/Scripts/python.exe -m constraintnet.viz --demo core     # E030: four hidden interiors, one exterior (animated)
```

Edges coloured by constraint conjugacy class, triangles by curvature, **green ▲ accepted /
red ✗ rejected**, glowing spheres = curvature clusters (matter candidates), vertex size =
local mesh fineness `n = rho/rho0`, white star = test implication you can watch slow down.
Keys: `space` play/pause, `right` step, `e/f/o/d` layers, `r` rotate, `s` PNG, `q` quit.

## Architecture rules (enforced by tests)

1. **KERNEL / DRIVERS split.** KERNEL = complexes, groups, labels, holonomy, gauge &
   canonicalization, resolutions, fiber products, observer — **no RNG, no scheduler**
   (`test_kernel_module_has_no_rng`). DRIVERS implement `DynamicsDriver`
   (advance / event_ontology / reversible / inverse_advance) and are swappable at runtime.
   DriverA = stochastic veto (randomness lives only here); DriverB = deterministic churn
   (verified-bijective bijection on the gauge slice; cycle decomposition = internal clock
   spectrum). **The drivers are hypotheses; experiments referee them — neither is hardcoded
   "correct", and A is never deleted when B works.**
2. **Canonicalize for reporting, never for exploration.** Right-multiplication does not
   commute with conjugation: exploring from orbit representatives loses transitions (174
   orbits found instead of 178). Explore raw gauge slice; project to orbits afterwards.
3. **Determinism stance.** No probability in KERNEL. Statistics come from ensembles over
   initial conditions (phase sweeps), not in-run RNG, except inside DriverA by design.
4. **No coordinates in dynamics, ever.** Layout is projection-only; acceptance rules are
   purely relational.

## Status

| Track | Done | Open |
| --- | --- | --- |
| Physics spec M1–M8 | **M1** 1728→178 ✅ · **M2** boundary-preserving dynamics ✅ · **M3** cone hidden states \|I(B)\| ✅ · **M4** persistent defect, confinement exact, spec Test 5 ✅ | M5 motion cost · M6 interaction gluing (kernel exists; sim-level runs pending) · M7 observer density → delay · M8 full 3D viz |
| R-track (kernel/drivers) | **R1** driver interface + both drivers ✅ · **R2/R3-lite** fiber products + phase-sweep harness ✅ · **R3** phase-locked absorption invariants ✅ | R4 D1–D4 diagnostics report · R5 Bell/CHSH glued-pair referee experiment |
| Extras shipped along the way | reps.py (A₄ irreps/fusion/singlets) · fringe.py (discrete Aharonov–Bohm) · sectors.py (centralizer charge-knot sectors) · sheaf.py (gluing-defect theorem ≙ Bianchi) · backlog assertion suite ✅ | — |
| Layer 2 (category/knots/measurement) | **D(A₄) modular data complete** — 14 sectors, S/T/Verlinde, every brief pass criterion green incl. (ST)³=(τ/D)S² with τ/D=1; class algebra exact (C₂²=3C₁+2C₂, C₃·C₄=4C₁+4C₂). **Fermion verdict: W₁₀,W₁₁ true fermions** (R = −1 from the universal R-matrix, `doubles.py`). **Flux-string detector v1** + GF(3) solvability (Bianchi as rank theorem: isolated flux unrealizable). **Entropy S(R)=log\|I(∂R)\|**: vacuum S≡0 at every radius; free baseline volume-like; gauge-slice CSP solver makes A₄ cores exact (12¹⁴ → 0.1 s); **CORE ENTROPY MEASURED: \|I(core)\|=4, field rigid, entropy localizes at core**. Reachability assertions codified (27/1728/64). **Memo patches P1–P10** (`docs/MEMO_PATCHES.md`) | knot/link invariants (PL embedding recipe specced); interferometry; loop–loop braiding vs R-eigenvalues; pair-state constructor; general pair-channel R/F tabulation |

## Verified findings (measured or derived; tests are the authoritative record)

### The finite seed
| Result | Value |
| --- | --- |
| A₄ elements / conjugacy classes | 12; sizes 1, 3, 4, 4 |
| Gauge-fixed d(Δ³): raw → physical classes | **1728 → 178**; Burnside (12³+3·4³+8·3³)/12 = 178 ✓ |
| Little-group census of the 178 | trivial ×130, Z₃ ×26, V₄ ×21, A₄ ×1 — independently recomputed via triple-orbit machinery (backlog item 5a) ✅ |
| Curvature signature counts | **82** ordered · **20** multiset-sort ("signatures" as quoted in the memo — a sort, not a group quotient) · **13 / 11** true vertex-relabeling orbits (A₄ / S₄); relabeling flips order-3 chirality via edge inversion. See [reference/opus_audit](<reference/opus_audit/README.md>) |
| Move-set-relative reachability | fixed order-3 generator → 27 of 1728; all order-3 → 1728 (ergodic, all signatures); order-2 → 64 raw = 4³, and the frozen GIF seed explores exactly **6 physical classes** [4,12,12,12,12,12] |

### Conservation & matter
| Result | Value |
| --- | --- |
| Charge is cycle holonomy, not surface flux | Σ face curvature over any closed surface ≡ 0 (abelian); Bianchi = d²=0 read additively; non-abelian Bianchi needs framing data we refuse to invent → `TypeError` by design |
| Confinement (closed Kuhn ball n=2, 1500 steps) | surface moves rejected **1108/1108**; interior accepted **392/392** — charge cannot leak; leaks counter = 0 (backlog item 1) ✅ |
| Persistent charged defect (spec Test 5) | survival 100%, zero gaps, charge class start == end; worldline residue constant except at logged events (item 6) ✅ |
| Neutral interior lump | trivial external signature → *virtual fluctuation, not matter* (definition: matter := nontrivial conserved external residue) |
| Interior heating | unconditionally-accepted interior moves diffuse curvature (curved faces 3→72); localization anchored by frozen core only — honest limitation |
| Cone v∗∂Δ³ hidden interiors | flat B, no flux → \|I\|=1 light-like; curved B → \|I\|=0 (one vertex can't cap curvature); uniform Klein-four flux → **\|I\|=6**; vacuum is the *unique* light-like pattern out of 103 realisable; Z₃ control: all 27 patterns \|I\|=1 — **hidden state requires non-abelian-ness** |
| **Core entropy (E030)** | Kuhn n=2 A₄ order-3 core: raw 48 → **\|I\|=4 = \|flux class\|**; field balls rigid \|I\|=1; full ball (E_int 26) same 4 — **entropy localizes at the core**; involution control raw=\|G\| pure gauge; Z₃ twin \|I\|=1. Four states = one support (7/14 edges, geometry-fixed) filled by one of four class elements |
| Kick study (branch `bionic/kick-test`) | reject-rule can never restore a violated constraint (one-way door, exhaustive BFS proof on Z₃ tetra, 729 states); genuine restoration only for energy-raising kick + low Metropolis β. "Temperature" there = statistical parameter over a chosen action, **not physical T** |

### Quantum-structural
| Result | Value |
| --- | --- |
| Sector multiplicities (spec's H=C_G(q)) | order-3 charge → Z₃ sectors **(4,2,2)**; order-2 → V₄ uniform **(2,2,2,2)** — exact, `sectors.py` |
| A₄ fusion sanity | 3⊗3 = 1+1′+1″+3·3 with **exactly one** singlet ("three 1D summands ≠ three singlets" — test-guarded) |
| Discrete Aharonov–Bohm (fringe.py) | visibility = \|χ₃(flux)\|/3 exactly; Z₃ shifts phase with V=1 (which-phase vs which-path trade) |
| Absorption cross-sections (R3) | full-ensemble absorption is **phase-invariant** (an object+face invariant): A₄ flat 12/1728 probes, curved **3/1728 — curvature suppresses ×4**; Z₃ blind to curvature; prepared-probe gating real (0 ↔ ⅓) but hidden by ensemble averaging |
| D(A₄) topological spins | θ = χ_ρ(g_C)/dim ρ (self-AB): V₄-flux dyons W2,W3 → **θ=−1 twist candidates**; order-3 dyons θ ∈ {1,ω,ω²}; 14 sectors; Σd² = 12+36+96 = **144** ✓. Twist ≠ exchange statistics — R-symbol check is Layer-2 work |
| Sheaf/gluing (sheaf.py) | locally free, globally obstructed: Gauss kernel == global image as SETS; **54/81 worlds forbidden by globality alone** — Bianchi re-derived as sheaf defect |

### Observer & gravity-adjacent
| Result | Value |
| --- | --- |
| Vacuum-twin density (matched runs, charged vs flat) | ratio exactly **1.000 per shell**: *static charge contributes zero event density*. Consequence: M7 delay must be derived from **activity** (churn/waits/do-undo work), never hardcoded ×n(x); hardcoded-n kept only as flagged control arm |
| Accept-rate identity | measured 392/1500 = 0.2613 vs combinatorial interior fraction 26/98 = 0.2653 — accept rate is **topology, not dynamics** (within 1σ) |
| T3 cross-driver consistency | Z₃ flat cone: exact meshable fraction 1/9 by full phase sweep; DriverA reproduces 0.1118 ± 6e-4 — same set, two measures |

## Honest caveats (read before citing anything)

- **The kinematic sector is D(A₄)** — Dijkgraaf–Witten / Kitaev quantum double, a known
  mathematical object newly *derived* from the axiom. The novel claims are dynamical and
  gravitational (move-set-relative reachability, reconfiguration-cost mass, churn-sourced
  delay, holographic entropy, envariance-Born) — all measurements waiting to happen.
- **Gapless-photon problem #1:** DW phases for finite G are gapped; the photon is not.
  Candidate resolutions (critical growth / condensation / separate sector) all open.
- **A₄ audit verdict:** excellent microscopic skeleton, definitively insufficient infrared
  theory — no chirality, no gapless photon, no bulk point fermions (θ=−1 dyons are
  *loops* in 3+1D; point fermions need a twist/spin structure). Both halves are results.
- **Born rule:** sample space derived from fusion channels; the probability *measure*
  remains one declared postulate (equal a priori weight per micro-resolution), with
  envariance/Gleason routes named but open.
- **F(O) ≅ O matter definition is provisional** until F = a driver sweep's closure and
  persistence = cycle membership + invariant constancy (Driver B operationalizes this).
- **Legitimacy is region-relative** (PHYSICS_NOTES §6): what counts as "outside" is part
  of the setup; costs must always be reported with the enclosing region. Unsettled by design.

## Known issues / queued

0. **External referee audit (frontier-model synthesis) answered item-by-item** in
   [docs/CRITIQUE_TRIAGE.md](<docs/CRITIQUE_TRIAGE.md>): 4 bugs/hazards fixed (Pachner 2→3 was
   broken at HEAD; gauge-variant proposals 29.4% equivariance failure -> class-closed arm;
   basis-dependent appearance -> `gauge_invariant_state`; population-blind density),
   2 negative results logged (Driver A event density is label-blind — gravity claim parked;
   d_s=3 unreachable at toy scale even for Z³ — matched-control statement pinned), pre-registration
   live in [docs/PREDICTIONS.md](<docs/PREDICTIONS.md>). Literature positioning:
   [docs/RELATED_WORK.md](<docs/RELATED_WORK.md>).
1. Viz: accepted-move green ▲ effectively invisible in lattice GIFs (flash dies in ~1 frame;
   interior markers occluded). Planned: proposed→accepted/rejected lifecycle animation.
2. RNG migration out of `dynamics/persistence/seeds/moves` to widen the kernel purity fence.
3. Physics M5–M8 and R4–R5 as per Status table; Layer-2 brief items tracked in
   [docs/R_TRACK.md](<docs/R_TRACK.md>) queue + commit messages until a dedicated doc lands.
4. Triage standing queue: softened-predicate confinement pilot (P7, first real physics target),
   independent persistence criteria, weighted dynamics + conserved ledger, dynamic delay
   (gate for gravity language), internal-observer agreement test, S₃/Q₈/D₄ universality matrix,
   heat-kernel d_s extrapolation, arrow-of-time open problem (named).

## Layout

```
src/constraintnet/
  groups.py      finite-group engine (Z_n, A4) + word metric = the cost primitive
  complex.py     vertices / oriented edges / faces / tetrahedra; orientation-aware boundaries
  holonomy.py    curvature on faces, charge on cycles, Bianchi identity
  region.py      regions, signed boundaries, gauge-invariant Appearance (the sector label)
  gauge.py       gauge transforms, spanning-tree fixing, moduli enumeration, little groups
  seeds.py       d(Delta^3), bipyramid (both Pachner sides), Kuhn balls, stacked balls
  moves.py       elementary relabellings + Pachner 2<->3 (fixed + round-trip tested) + class-closed proposals
  spectral.py    exact diffusion return probabilities -> matched-control spectral dimension
  dynamics.py    the main loop: propose -> test boundary -> commit or revert
  states.py      canonical state ids and transition graphs over physical states
  resolutions.py cone over d(Delta^3): hidden internal states, |I(B)| flux census
  objects.py     curvature clusters as matter candidates
  persistence.py defect seeding, relational tracking, confinement, is_persistent (M4)
  drivers.py     DynamicsDriver ABC; DriverA stochastic veto; DriverB deterministic churn
  interaction.py fiber products over shared faces; phase-locked protocol; stride scans
  reps.py        A4 irreps, fusion, singlet counting (character machinery)
  fringe.py      two-path probes: discrete Aharonov-Bohm visibility
  sectors.py     centralizer charge-knot sector multiplicities (spec's H = C_G(q))
  sheaf.py       gluing axiom as counting theorem; Bianchi re-derived as sheaf defect
  category.py    D(A4) modular data: S/T/Verlinde fusion, class algebra (Layer-2)
  strings.py     flux-string detector + GF(3) solvability engine (Bianchi-as-rank)
  entropy.py     holographic S(R)=log|I(dR)| for general regions; area-law study
  observer.py    relational coarse-graining, mesh fineness n, propagation delay
  viz/           animated interactive viewer (projection only; matplotlib)
tests/           spec tests + integrity guards + Layer-2 pass criteria (222 passing)
examples/        one runnable script per milestone
docs/            RESEARCH_DIARY (E001-E025, the scientific record) · SPEC · PHYSICS_NOTES
                 R_TRACK · LAYER2 · MEMO_PATCHES · CONVENTIONS · figures/
reference/       external audit material (opus_audit/) — not part of the package
out/             regenerable GIFs: lattice_conservation.gif, orbit_tour_178.gif,
                 core_entropy_states.gif (E030: |I|=4 interior cycling, exterior FIXED), ...
```

## Versioning

Git branches: `main` = physics milestones M1–M4; `bionic/kernel-drivers` (current tip) =
R-track + extras; `bionic/kick-test` = kick/restoration study. One commit per unit of
work with the finding in the message; CHANGELOG.md tracks releases. The test suite is the
authoritative record — when docs and tests disagree, the tests win.
