# Claims register

Per Round-3 panel suggestion (§3 of `reference/referee_synthesis/synthesized_referee_report_R2.md`):
every load-bearing claim carries a **status** and a **producing model**, with an evidence pointer.
Statuses:

* **MEASURED** — reproducible number from this repository (test-pinned or probe-logged, seed stated).
* **DERIVED** — mathematics following from declared definitions; verified symbolically/exhaustively.
* **POSTULATED** — declared model input or hypothesis; not derived from the basement axiom.
* **SCHEDULER-ARTIFACT** — property of a chosen coordinate/scheduler on the state space, NOT an observable.
* **PARKED** — claim withheld pending named evidence; kept visible with its reason, never deleted.

Rule: no sentence enters README/PHYSICS_NOTES with a status it cannot defend. When a number's
convention changes, both numbers stay here with their convention names (control-arm discipline).

| # | Claim | Status | Producing model(s) | Evidence / pointer |
|---|---|---|---|---|
| 1 | Gauge-fixed tetrahedron slice: 12³ = **1728** raw configs → **178** classes under residual global conjugation; `gauge_invariant_state()` separates exactly these 178 (complete on this slice) while `appearance()` gives 82 | MEASURED + DERIVED (Burnside) | local Qwen (orig.); independently reconstructed by Opus R3 + panel | `examples/milestone1.py`; `tests/test_gauge_canonical.py`; R3 memo §1 |
| 2 | Little-group census of the 178: **130 trivial, 26 Z₃, 21 V₄, 1 A₄** (orbit sizes 12/4/3/1) | MEASURED + DERIVED | local Qwen; panel-verified | `tests/test_backlog_claims.py::test_little_group_census_matches_known_histogram` |
| 3 | Cone v\*∂Δ³ hidden internal states: rigid \|I(B)\| = **4** for seeded declarations across all 1728 tree-gauge boundaries; pooled generically **1** | MEASURED (rigid convention) | local Qwen (E030); panel-endorsed as convention-explicit | `examples/milestone3.py`; `tests/test_pooled_resolutions.py` |
| 4 | Fibre collapse under pointwise stabilizer: five-face raw 72 → rigid 6 → within-fibre **2**; star-3 36→3→**1**; flat-B pointwise stabilizer = 12 constant transforms (144 with apex freedom) | MEASURED | Astra R2 + Opus R3 (finding F1); local fix | `resolutions.py` three-convention warning; `tests/test_pooled_resolutions.py`; diary E036/F1, E034 erratum |
| 5 | D(A₄) anyon data: **14** types; T-twists (+1,+1,−1,−1 on V₄ dyons; 1,ω,ω² per order-3 class); S unitary; S² = C; (ST)³ = S²; Σd² = 144; Verlinde N nonnegative integers; safe sub-rules (Rep(A₄) charge fusion; shift rule 1′×F₁=F₂; ⟨g,π⟩×⟨g⁻¹,π̄⟩ ⊃ 𝟙 exactly once; C₂²=3C₁+2C₂) | DERIVED + verified | local Qwen (category layer); panel cross-checked | `sectors.py`, `fermion*` probes, `tests/test_sectors*.py`; Layer-2 brief pass criteria |
| 6 | Fermionic twists exist: order-2-flux dyons with θ = χ_ρ(g_C)/dim ρ = **−1** (W₁₀, W₁₁; R = −1 reported). CAVEAT (binding): these are **loop excitations in 3+1D**; point fermions in bulk require a twisted cocycle/spin structure — H³(A₄,U(1)) menu check is an open task | MEASURED + DERIVED, with caveat | local Qwen; Astra/Opus reproduced; caveat per README & R3 §1 | `fermion.py` probe output; README fermion section |
| 7 | Driver A (legacy model): vacuum / charged-defect / neutral-lump accept sequences **bit-for-bit identical**, accept rate ≈ **0.325** — event density carries zero matter information under appearance-only conservation | MEASURED (NEGATIVE RESULT, kept visible) | local Qwen probe p6; panel rebuilt from scratch and confirmed | diary E035; `tests/test_backlog_claims.py`; R3 memo §1 |
| 8 | Gauge-equivariance of proposals: **29.4%** violations on the legacy generator arm, **0** on the class-closed arm (exhaustive) | MEASURED | local Qwen probe p3; panel-verified | commits `f968021`; `tests/test_drivers.py` |
| 9 | Observer shell-size confound: corr(ρ_raw, \|shell\|) = **+0.41**; removed by per-vertex normalization (uniform activity → uniform factors) | MEASURED (fix verified) | local Qwen probe p6; panel-verified | `observer.py` rho_per_vertex; `tests/test_observer.py` |
| 10 | Spectral dimension: Kuhn balls read d_s(t≈2..8) ≈ 0.6–1.9 rising with size; matched Z³-box control reads ≈ 2.0 — pinned claim is **matched-control consistency**, not "d_s returns 3" | MEASURED (honest form) | local Qwen probe p5 | `spectral.py`, `tests/test_spectral.py`; diary E035 |
| 11 | Gluing cross-sections, probe x = slice phase 0 vs full 12³ ensemble: **raw** flat 12 : curved 3 (the legacy "×4 suppression" — declared artifact of fixed-frame equality); **classes** and **relational**: flat 12 : curved **36** (×3 enhancement) | MEASURED per convention | local Qwen (classes), Astra frames analysis, local re-measurement (relational) | `tests/test_interaction.py::test_cross_section_ratio_all_three_conventions` |
| 12 | Absorption **phase structure is convention-dependent**: over an 18-phase grid — flat boundary classes {12,36,48,144,192}, relational {12,36,48,144}; curved boundary classes {36,108,144,192}, relational **{36}** (phase-invariant: trivial stabilizer saturates the orbit) | MEASURED (deterministic sweep, no RNG) | local Qwen (E036 re-measurement after Astra escalation) | `tests/test_interaction.py::test_absorption_phase_structure_is_convention_dependent` |
| 13 | Counting identity for complete probe ensembles: relational count = raw count × \|conjugation orbit of x's flux tuple\| | MEASURED (structural, pinned on nontrivial cases) | Astra | `tests/test_interaction_frames.py::test_relational_probe_count_matches_orbit_times_raw_fibre` |
| 14 | Pachner moves preserve Euler characteristic and boundary labels both directions with exact snapshot undo; guards reject link-condition violations without mutation | MEASURED (72 Kuhn n=2 sites + rejection tests) | local Qwen (F5 fix); Astra hardening | `tests/test_pachner.py`; diary E036/F5 |
| 15 | Canonical state is complete on the single-tetrahedron slice and blind to nothing across boundary components (per-component canonicalization, min-vertex order; vertex gauge cannot move curvature between labelled shells) | MEASURED + DERIVED | Astra caught the shell-swap bug in the first fix | `tests/test_gauge_canonical.py::test_curvature_cannot_swap_surface_components` |
| 16 | Born rule: sample space = fusion channels of the category (canonical); **the probability measure \|c_k\|² is a POSTULATED ingredient**, not derived. Gleason and Zurek-envariance routes are named open problems | POSTULATED (measure), DERIVED (sample space) | online-Qwen memo + Opus review; retraction trail in referee README | `reference/theory_memo/Memo.txt` §4/§8 as patched; Layer-2 brief item 4 |
| 17 | Curvature action H = count of nonidentity face holonomies as candidate reduction action; Metropolis kinetics against an external bath conserves H + bath ledger (bookkeeping, not a first law) | POSTULATED (action), MEASURED (ledger conservation) | Astra particle program | `curvature.py`, `kinetics.py`, `tests/test_curvature.py` |
| 18 | Relational gluing (one simultaneous apex-frame alignment) as the physical interaction rule — gauge-invariant and correlation-complete, but still a **declared convention**, one of several admissible ones; existence counts once, multiplicity is not a weight | POSTULATED (default convention) | Astra (counterexample-driven); adopted after review | `interaction.py` docstring; `tests/test_interaction_frames.py`; diary E036/F4 |
| 19 | Driver B cycle spectrum (e.g. 864 cycles of length 2 vs one odometer cycle of 1728) | **SCHEDULER-ARTIFACT** — diagnostics of a slice coordinate system, not an object observable; σ is not gauge-equivariant | local Qwen (F7 labelling) | `drivers.py` DriverB docstring; R3 memo F7 |
| 20 | Odometer mode = single equidistributed cycle | SCHEDULER-ARTIFACT by construction (declared scheduler choice, useful for phase sweeps) | local Qwen | `drivers.py` comment |
| 21 | M7 gravity: "density rises around matter → propagation delay → geometry" | **PARKED** — E035 shows zero label dependence under Driver A; the only legitimate source of slowdown is dynamic delay (backlog item 4); no gravity language until then | local Qwen negative result; panel endorsed parking without reservation | diary E035; backlog item 4; README parked-gravity note |
| 22 | Gapless photon / electromagnetism from the continuum limit | **PARKED** — named gap; D(A₄) supplies no gapless mode (audit paragraph: excellent microscopic skeleton, definitively insufficient infrared theory) | online-Qwen/Opus audit paragraph | Memo §7 as patched; RELATED_WORK |
| 23 | Point fermions in bulk | **PARKED** — θ=−1 twists are loop excitations absent spin structure; H³(A₄,U(1)) menu check open | README caveat; Layer-2 brief item 2 | diary (fermion entries); Layer-2 brief |
| 24 | Clausius δQ = TδS / Jacobson route to Einstein equations | **PARKED** — entropy functional S(R) = log |I(∂R)| implemented as ingredient; area-law test pending; backreaction is the missing theorem | online-Qwen memo §5/§9 | Layer-2 brief item 5 |
| 25 | Basement axiom "directed implications reduce" and the emergence narrative (charge = holonomy, mass = rewrite cost, matter = persistent knot) | POSTULATED framing + partial DERIVED content; each sub-claim lives or dies by its own row above | Satish Mallya + online Qwen (theory); local implementations per row | `reference/theory_memo/Memo.txt`; README |

## Protections list (R3 §4 — load-bearing walls of credibility)

Future speed must not cost these. Any change that weakens one requires an explicit diary entry:

1. **The parked gravity claim** stays parked until dynamic delay (backlog item 4) measures slowdown
   with the hardcoded-n control arm OFF.
2. **Born measure as postulate** — sample-space-derived, measure-postulated; no re-mystification.
3. **Fermion loop-excitation caveat** travels with every fermion mention.
4. **Visible negative results** (E035 label-blindness, d_s honesty, ×4 suppression artifact) are never
   deleted or quietly re-tuned; superseded conventions remain as named control arms (`raw`, `classes`,
   `legacy`).
5. **The pre-registration that caught itself wrong** (Pachner no-reproduce prediction contradicted by
   probe p4) stays in PREDICTIONS.md verbatim, outcome appended.
6. **RELATED_WORK do-not-contradict checklist** (Elitzur, Elban-Gowda, doubling, Coleman-Mandula
   caveat, no-signalling) binds new claims.

## Provenance legend

*local Qwen* — this repository's implementing agent across sessions (compacted lineage).
*Astra* — GPT-based reviewer/agent working in the sibling checkout, imported after review (E036).
*Opus* — external verification pass (reference/opus_audit/, R3 panel).
*online Qwen* — theory-sounding-out instance (Memo.txt), synthesis author of referee rounds.
*panel* — joint reconstruction across the above.
