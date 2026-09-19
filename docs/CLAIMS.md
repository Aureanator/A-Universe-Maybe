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
| 26 | Tetrahedron-seed landscape under action H: vacuum is the only closed equal-action basin (178 physical states, zero nonvacuum closed plateaus, all states reach H=0 nonincreasingly in ≤3 moves; Z3 ≤2) — flux/sector labels alone do NOT make classical particles under this action | MEASURED (exhaustive) | Astra (P8); local verification of interaction arms | `docs/PREDICTIONS.md` P8; `reference/astra_session/data/landscape.json` |
| 27 | No stable particle species or binding at n ≤ 3 under H: all 57 lifetime-screened branches have immediate downhill moves, 42/57 exact one-move erasures; long endpoints absorbed to vacuum at proposals 15,157 / 17,523 — longevity was proposal-waiting-time artifact | MEASURED (NEGATIVE RESULT, kept visible) | Astra (P9+P10) | `docs/PREDICTIONS.md` P9–P10; `reference/astra_session/data/{runs,candidate_audit}.json` |
| 28 | Non-abelian critical slowing-down without metastability: at n=5, Z3 relaxes to vacuum in ≤47.3k proposals but A4 fails on 2/3 seeds within 200k (endpoints H=8/10, each with only 2 strict-downhill exits among 665×11 = 7,315 proposals); endpoints NOT local minima — no stability claim | MEASURED + reproduced bit-for-bit locally | Astra (P11); exact reproduction by local Qwen 2026-09-19 | `docs/PREDICTIONS.md` P11; `reference/astra_session/data/scale_runs*.json`, `scale_rerun.log`; diary E037 |

### P12 addition (2026-09-19)

**29 — MEASURED + constructive certificate (Codex):** both nonvacuum P11 A4 n=5
endpoints have zero-barrier paths to flat vacuum under the original permitted
interior-edge moves: H=8 -> 4 -> 0 and H=10 -> 6 -> 0. Every move is verified
by full holonomy recomputation, fixed boundary labels, inverse replay, and gauge
transport. This excludes an action barrier to complete decay at those endpoints;
it does not establish rates or exclude metastability elsewhere. Evidence:
`examples/particle_decay_certificates.py`, `tests/test_decay.py`, and
`reference/astra_session/data/decay_certificates.json`.

The earlier phrase "critical slowing-down" in row 28/P11 was an interpretation,
not a measured critical exponent or established critical point. The supported
observation is slow proposal-time relaxation with rare downhill moves. Likewise,
E037's suggestion that destroying-move dilution is a conjugacy-class mechanism
remains a hypothesis; these certificates do not derive that mechanism.

### P13 / P13b additions (2026-09-19)

**30 — DERIVED (Codex):** with all nonidentity right multipliers allowed on
each interior edge, the raw fixed-boundary label graph is connected for any
finite group on any fixed complex. Constructive path: multiply each differing
label a by a^-1 b. Therefore no nonconstant label observable is invariant under
ALL these unrestricted moves. Does not imply downhill connectivity or rule out
energetic metastability. Scope/proof: `docs/TOPOLOGY_AUDIT.md`; implementation
and checks: `rewrites.py`, `tests/test_rewrites.py`.

**31 — MEASURED, exact witnesses (Codex):** prescribed linked dual loops on
Kuhn n=8 in Z3 and an A4 order-3 subgroup lift have |Lk|=1 and a nonincreasing
38-move merger path through a junction, H=98 -> 84. Full 140-move erasure has
one +1 step, never exceeds initial H, and passes through a two-loop state with
|Lk|=0. Boundary, inverse, full-holonomy and gauge checks pass. This is not
spontaneous emergence, intrinsically non-abelian binding, nuclear fusion, a
minimal-barrier proof, or a sampled rate. The original downhill search's
32-state cutoff remains inconclusive. Evidence: `examples/topology*_audit.py`,
`reference/astra_session/data/topology*_audit.json`, `tests/test_topology_audit.py`.

**Historical E026/E027 correction:** n=1 order-3 vertex stars are boundary-open
arcs (six nontrivial supports, each with two boundary faces), not closed loops.
The n=2 central loop remains closed. The associated n=1 no-flat-filling count
is a fixed-region result, not a theorem about all enclosing regions. Exact
incidence checks replace the old false closure assertion; diary corrections
retain the original statements and their revised scope.

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

### P14 / P15 additions (2026-09-19)

**32 — MEASURED, exact witness (Astra run; Opus reproduction):** the P13 linked
fixture (Z3 and the A4 cyclic lift) has a fully NONINCREASING 140-move erasure,
H=98 -> 0. The P13b +1 step was an ordering artifact. Evidence: P14,
`topology_decay_order.json`, `tests/test_link_order_and_noncommuting.py`.

**33 — DERIVED + MEASURED (Opus):** in full A4, Hopf-linked flux loops with
non-commuting fluxes cannot be the whole curved support. pi_1 of the complement
is Z^2, so the meridians would have to commute. The prepared fixtures confirm this:
one junction component with a V4 tether of 5 faces (6 under the opposite tie
convention). The commuting controls give two clean linked loops.

**34 — MEASURED, exact witnesses (Opus):** those tethered non-abelian fixtures,
and the commuting controls, all have fully nonincreasing 140-move erasures to flat
vacuum. The tether and the linking vanish on the same move (step 52, H=80, Lk=0).
No single rewrite removes the tether. NOT shown: minimal barriers elsewhere,
rates, or stability of any other structure. Evidence: P15,
`reference/opus_session/data/noncommuting_link_audit.json`, `out/p15_noncommuting_links.png`.

**35 — MEASURED + DERIVED (Opus, P16):** with identity boundary, flat interiors
have exactly one physical filling (Z3 n≤3, A4 n≤2). The smallest excitations
(H=4) have 3n²(n−1) distinct supports (n=2..8): uniform volume entropy, no
inside/outside difference. With claim 30 (no conserved interior content), the
current model has surface tension but no bubble pressure. Evidence: P16,
`reference/opus_session/data/bag_test.json`, `tests/test_bag_test.py`;
interpretation in `docs/BAG_PICTURE.md` (framing POSTULATED).

**Note on row 23 (2026-09-19):** the "H³(A4,U(1)) menu check" is the 2+1D twist.
For 3D space plus time the Dijkgraaf–Witten twist is H⁴, and it does not by
itself make point charges fermionic. See `docs/BAG_PICTURE.md` §7. Row 23 is
unchanged as history.

**36 — DERIVED + MEASURED (Opus, P17):** on any connected graph with an exit,
a walk with probability weights escapes from every start. The same walk with
amplitude weights (identical generator, factor i) keeps exactly ||P_D psi0||^2,
where D is spanned by the eigenmodes vanishing at the exit. Symmetry and
degeneracy force D to be nonzero. Verified on 12 graphs, including the Kuhn
mesh (44/64 dark). Evidence: `docs/TRAPPING.md`, `tests/test_trapping.py`.

**37 — MEASURED, observed pattern (Opus, P17):** on the Sierpinski gasket
(levels 1–6, corner exit) the non-dark dimension is 3·2^(k-1)+1, and the slowest
non-dark leak rate falls doubly-exponentially (to 1.5e-31 at level 6). Not
proven for general k; supplied geometry, not self-built. Evidence:
`reference/opus_session/data/trapping_depth_rates.json`.

**38 — DERIVED + MEASURED (Opus, P18):** the project's Kuhn mesh, in the
emergent metric of any nearest-neighbour wave rule on it, has the exact
body-centred-cubic tetrahedral vertex star. Its edge classes are fixed by
link-ring size (6: short, 4: long, length ratio 2/√3). Weighting ring-4 edges by
½ makes the dispersion isotropic through fourth order. In rendering coordinates
the mesh looks anisotropic (speed ratio 2); that is a coordinate artifact under
architecture rule 4. Evidence: `docs/PROPAGATION.md`, `tests/test_propagation.py`.

**39 — MEASURED (Opus, P18):** scalar waves on that mesh reproduce the sharp
3D Huygens principle (interior share ≤ 3e-7). A 2D control keeps its
continuum tail (1.8%). Mass fills the cone interior, converging to the
continuum (39% at mσ = 1). Classical damped waves keep exactly the dark-mode
energy, so P17-style trapping needs signed waves, not specifically complex
amplitudes. Evidence: `reference/opus_session/data/propagation_test.json`.

### Framing update (2026-09-19): row 25 reconciled with the working statement

**Row 25 (basement axiom and emergence narrative)** remains POSTULATED framing.
Two sub-claims are revised, on evidence, without deleting the history above:

- **"Matter = persistent knot/defect" — SUPERSEDED.** Under the pre-v4
  classical action, no defect persists (rows 26–34). The replacement is
  "matter = trapped circulation of implication" (`WORKING_STATEMENT.md`
  clause 6). It is POSTULATED; its exact trapping mechanism is DERIVED (rows 36, 39).
- **"Mass = rewrite cost" — RETAINED, made precise.** Inertial mass is the
  rewrite cost of translating a structure. Equivalently, it is the
  maintenance cost in implication steps relative to a free implication
  crossing the same neighbourhood. The equivalence is a light-clock argument,
  checked by M1/M2 in `DYNAMICS_DESIGN.md`. The old readings (curvature count
  H; group word metric) are now the **pre-v4 control arm**, not physical mass.

**Control-arm labelling:** rows 7–35 were produced by the pre-v4 engine (static
labels, H-descent, external bath, Drivers A/B). They stay true as measured, and
become the named control arm for the v4 dynamics.
