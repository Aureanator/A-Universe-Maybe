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

**40 — MEASURED + DERIVED (Opus, P19):** the v4.0 walk (gauge-covariant
Szegedy walk on the Kuhn mesh, ring weights) conserves implication exactly and
is gauge-covariant.
- Its dispersion is θ = arccos λ(k), with long-wave speed sqrt(2/11).
- It gives a relational light cone isotropic to 0.3% (torus 120³), with
  exponentially small weight outside the cone.
- No mode outruns that speed (sampled).
- It reproduces non-abelian holonomy interference ½(1 + χ₃/3) exactly.
- Compact non-translating cycle states exist whenever the holonomy fixes a
  vector (DF, derived and checked).

Evidence: `reference/opus_session/data/p19_{a,b,c,d}.json`, `tests/test_walk.py`.

**41 — MEASURED (NEGATIVE, Opus, P19e):** a frozen prepared flux record
(single loop, P13 linked, P15 tethered) traps no implication beyond the
vacuum's cycle states. Trapped dimension: fixture 2,875 against vacuum 2,877
(n = 6, exact). Retained weight of packets on the flux: ≤ 4e-32 after 20,000
ticks. Self-confinement therefore needs dynamical labels (v4.1).
Evidence: `reference/opus_session/data/p19_e_exact.json`, `p19_e_time.json`.

**42 — MEASURED (Opus, P21):** an energy-accounted quantum record (option A: 3 quantum A4
edges, electric term plus Wilson term, one fixed unitary, closed n = 6 box) is exactly
reversible and conserving to about 1e-13.
- Free light passes a weakly fluctuating quantum vacuum with fidelity ≥ 0.985 over 600 ticks.
  The energy it deposits is ∝ λ_E² and levels off. A strongly fluctuating vacuum heats up
  steadily.
- The dynamic record disturbs a trapped DF loop far more than quenched chop from the same
  vacuum does. At moderate coupling the loop stays on its arcs (82–99 %) and beats coherently
  with the record.
- A pivot vortex is not bound (±3 %).

*Status:* POSTULATED model, MEASURED behaviour; partial record (other edges frozen).
Evidence: `reference/opus_session/data/p21_{G1,G2,G3}.json`, `tests/test_qrecord.py`.

**43 — MEASURED (Opus, P22):** with open walls, a hot *dynamic* quantum record holds light.
- It releases light as roughly t^−1 to t^−1.9, retaining about 30–100× more at T = 600 than
  frozen chop of the same statistics. A flat vacuum releases light exponentially.
- Retained light is proportional to the hot fraction, with no threshold.
- A single flash cannot cool the record: the record's energy dwarfs the light's.
- So the model shows opacity when hot and transparency when calm, but not formation on cooling.

*Status:* POSTULATED model, MEASURED behaviour; the record is pinned to 3 edges.
Evidence: `reference/opus_session/data/p22_*.json`.

**44 — MEASURED (Opus, P23/P24a):** a quantum A4 record exchanging energy with light behaves
thermodynamically only when two conditions hold:
- its quasi-energy spectrum is unfolded (spans less than π);
- the light is spectrally narrow.

Under those conditions:
- broad light holds it near infinite temperature;
- narrow light at phase ω₀ holds it at an equilibrium E* that falls steeply with ω₀
  (0.51 → 0.22 → 0.14 × E_hot for ω₀ = 0.52 → 0.40 → 0.33, box n = 5 → 7);
- a lower-energy record retains less light, so it is more transparent.

*Status:* MEASURED (exact per-flash expectations); a static redshift proxy, not expansion
dynamics. Evidence: `reference/opus_session/data/p23_ladder_*`, `p24a_redshift_n*.json`.

**45 — MEASURED (Opus, P25):** compact loop patterns seeded compatibly in a cooled quantum-record
bath (each record branch holds its own compatible loop form) behave as follows:
- they have no birth shock, whereas imprinting costs about 4.5 %;
- they are exactly permanent if the bath is frozen;
- they erode at about 2–3e-4 per tick if the bath moves (λ = 0.1);
- 90° loops (ring-4) outlast 60° loops (ring-6).

The erosion comes entirely from record motion. A persistent pattern would have to be a joint
loop-plus-record eigenstate (not yet found).

*Status:* MEASURED; the bath is Gibbs-form (provenance check failed, see the P25-2 outcome).
Evidence: `reference/opus_session/data/p25_*.json`.

**46 — MEASURED (Astra, P26):** phase-resolved filtering improves the persistence
of a prepared compatible L4 loop in the partial quantum-record model. At the
isolated record-vacuum phase, a 256-tick filter retains 0.590–0.593 of the seed's
squared amplitude. After normalization, 98.04–99.68% lies on the loop in boxes
n=6 and n=5. The full-step residual falls from 0.314 to about 0.0057. Subsequent
128-tick open-wall loop-weight loss is 0.235–0.314 times the unfiltered seed's loss.

All four registered diagnostic predictions pass; the exact-eigenstate residual
gate fails. Filtering also selects 97.8–99.5% record-vacuum population, so this
does not isolate self-binding from selecting a calmer component. The exact
decoupled dark-loop control already persists. No autonomous confinement, mobile
particle, directed current, spin/exchange or cooling provenance is established.

*Status:* MEASURED, finite windows, prepared state, three pinned quantum edges;
remaining edges frozen flat. Evidence: `reference/astra_session/data/p26_*.json`,
`examples/p26_dressed.py`, `tests/test_phase_filter.py`; preregistration commit `29a2f51`.

**47 — MEASURED (Astra's run, P27; appended by Opus from the archived data):** the phase-filtered
"dressed loop" of P26 is not a distinct bound state.
- Its 128-tick loop loss is 1.09× (n = 5) and 1.23× (n = 6) the loss of a plain calm seed
  (compatible-vacuum or imprinted-vacuum), so it is *worse* than starting calm.
- Its squared overlap with a calm seed is 0.94–0.98.
- Neither calm seed reaches a near-eigenray: full-step residuals 0.074 and 0.126 against the
  registered bound of 0.063.
- Probability current around the loop is zero to 1e-12 initially and stays at 1e-6 or below over
  128 open ticks, in every arm.

*Status:* MEASURED; prepared states, three pinned quantum edges, finite windows.
Evidence: `reference/astra_session/data/p27_vacuum_n{5,6}.json`, `examples/p27_vacuum.py`,
`src/constraintnet/current.py`, `tests/test_current.py`.

**48 — DERIVED (Astra, DYNAMICS_DESIGN §15):** a joint eigenray supported strictly on a loop,
where every occupied vertex has an unused exit arc of positive coin weight, has exactly zero net
probability current on every edge. The argument holds for entangled records and any eigenphase.

*Consequence:* in this architecture, perfect trapping and directed probability circulation are
mutually exclusive.

**49 — DERIVED and MEASURED (Opus, P28):** for a state supported strictly on a cycle of the flat
walk (every cycle vertex having unused arcs of positive weight):
- the coin acts as −1 on it, which forces amplitudes to scale as 1/√(edge weight) around the cycle,
  so mixed-weight cycles (triangles) carry compact states;
- its walk phase can only be 0 or π;
- it exists exactly when H a = e^{iLθ} a for the ordered holonomy H, so on odd cycles θ = π needs an
  order-2 holonomy, and then the internal vector returns with −1 per traversal (a two-traversal
  return);
- every such eigenstate, and every 0/π superposition of them, carries exactly zero net current;
  the superposition is exactly 2-periodic and alternates weight between interleaved arcs.

*Status:* DERIVED analytically, verified over 84 cases (4 cycle types × 21 label draws) to 1e-14.
Evidence: `examples/p28_compact.py`, `reference/opus_session/data/p28_compact.json`.

**50 — DERIVED and MEASURED (Opus, P29a):** the walk carries an antiunitary symmetry
K ψ(w→v) = ρ(A_wv)·conj(ψ(v→w)) with K U = U⁻¹ K and **K² = +1** (verified to 1.8e-15). Hence every
eigenspace admits a current-free basis, and stationary circulation exists only in degenerate
eigenspaces.
- With identity labels (all eigenspaces degenerate): maximum loop bias 0.652.
- With random A4 labels (162 of 165 eigenspaces one-dimensional): maximum bias over every
  eigenspace 1.3e-11, i.e. none.

*Status:* DERIVED, verified over 11 label sets and 4 loops. Evidence:
`reference/opus_session/data/p29a_tail_v2.json`.

**51 — MEASURED (Opus, P29b):** replacing the internal space by the 2-dim spinor representation of
the binary tetrahedral group 2T (the double cover of A4) gives K_s² = −1 (5.0e-16), hence Kramers
degeneracy: no one-dimensional eigenspaces in any random draw. Stationary loop circulation returns,
with maximum bias 0.76–0.93 per draw against ≤ 1.3e-11 for A4.
- The circulating states are delocalised: loop weight ≤ 0.085, and ≤ 0.16 of the total current sits
  on the loop's own edges. The circulation is carried by the surrounding field.

*Consequence:* in this architecture, stationary circulation in a disordered vacuum **requires the
spin-½ lift**. This is kinematics; no self-binding, mass, charge or exchange statistics follows.
*Status:* MEASURED, closed box n = 4, 10 random 2T label draws.
Evidence: `reference/opus_session/data/p29b_spin.json`, `examples/p29b_spin.py`.

**52 — MEASURED (Opus, P30):** vacuum churn was calibrated and swept (dilute labels, closed n = 4
box, 120 interior faces, 3 seeds).
- P29's "disordered vacuum" is the infinite-temperature limit: 92.5 % of faces curved, mean Wilson
  cost 1.02 per face; the cooled vacua of P24a sit at 0.14–0.51 of that energy.
- **A4 labels:** exact stationary circulation survives to about 8 % curved faces (bias 0.45) and is
  gone by 25 %; at ~100-tick lifetimes it persists to 92 % (bias 0.36). So without the spin lift,
  circulation is a lifetime, set by how much the churn splits the degeneracies.
- **2T spinor labels:** exact circulation at every churn level tested, bias 0.53–0.80 including
  92.5 % curved faces.
- Scale: at λ_B = 0.1 the churn carries 0.001–0.10 rad/tick per face, against 0.749 rad/tick for the
  lowest quantum that fits the box (0.33 at n = 7).

*Status:* MEASURED, static labels, closed box; δ-windows are a lifetime proxy.
Evidence: `reference/opus_session/data/p30_churn.json`, `out/p30_churn.png`.

**53 — MEASURED (Opus, P31):** with a spin-½ walker and a *dynamic* 2T quantum record on two loop
edges (`src/constraintnet/spin_record.py`), a circulating state and the time-reversal-symmetric
standing state of the same degenerate family shift the record's energy by amounts differing by
2.5 % (n = 4) and 0.25 % (n = 6). The record responds to the walker's presence, not to its
circulation: **circulation does no work on its surroundings**, and neither state binds (both empty
an open box). Whether Kramers protection survives a dynamic record is untested — the operator used
for that check was incomplete.

*Status:* MEASURED; prepared states, two quantum edges, remaining labels frozen flat.
Evidence: `reference/opus_session/data/p31_selfbind_n{4,6}.json`.

**54 — MEASURED / DERIVED (Astra, P32A):** the finite-penalty projector model
supports explicit electric pairs made by unitary one-dimensional-character
strings. Across 48 preparations (Z2/Z3 tetrahedron boundaries and an A4 single
face), only endpoint stars are violated, every face is flat, and energy is
E_vac+2. Paths agree on the tested flat vacuum. Single-edge string continuations
move endpoints; inverse strings annihilate adjacent pairs. Errors are below
1e-12. These are operations on the existing edge Hilbert space, not new particles
inserted as primitive degrees of freedom.

Since [H,A_v]=[H,B_f]=0, H freezes every local defect occupation. Exact persistence
under this H is not evidence of propagation, self-binding or survival under an
open-boundary channel. A literal restriction to A_v=1 excludes these bare charged
states. The prior handoff's probability-conservation/gauge-invariance identification,
no-gap inference from weak coupling, and local-immobility claim are superseded
by `DEFECT_AUDIT.md`; all old finite measurements remain on record.

*Status:* POSTULATED Hamiltonian; exact finite-patch algebra and MEASURED prepared
states. No new fermion, nucleus, atom or bond result. Evidence:
`reference/astra_session/data/p32a_defects.json`, `examples/p32_defects.py`,
`tests/test_defect_ops.py`.

**55 — DERIVED / MEASURED (Astra, P32B/P32C):** a declared local Z2 transport
term moves electric defects while conserving total defect number, every flux
projector, and H0. Sixteen initial pairs on two finite simplicial 3-balls pass
the registered continuity and energy checks (errors below 4.30e-14).
The flat-pair restriction equals a hard-core boson hopping graph. An explicit
exchange-algebra test gives +1 for all 108 comparisons; an independent canonical
fermion control gives -1. No fermionic exchange is found in this sector.

*Status:* POSTULATED extension, not derived from the axiom. Local gauge symmetry
is not retained; pair number and therefore pair persistence are imposed. No
self-binding, reaction or electron claim. Protocols and evidence:
`P32B_TRANSPORT.md`, `P32C_EXCHANGE.md`, and
`reference/astra_session/data/p32{b_transport,c_exchange}.json`.

**56 — DERIVED + MEASURED (local Qwen, P33 local recreation; independent reproduction of Astra's run):**
for the POSTULATED perturbation H(lam) = H0 - lam*sum_edges W_e on Z2 tetrahedron and
bipyramid edge models, the registered perturbative algebra holds exactly: the first-order
number-sector projection equals P32B's transport form sum_m P_m V P_m = -sum_ab W_ab(I-S_aS_b)/2
(residuals <= 2.0e-13); all four second-order coefficient formulas hold (C_vac = -|E|/2;
diagonal (deg a + deg b - |E|)/2 with no two-body diagonal potential; shared-endpoint transfers
sum(1[v=b] - 1/2) over common neighbours; disjoint transfers vanish by vacuum/four-defect
cancellation); the pre-execution K4 symmetry cancellation is confirmed identically (C = 0 on the
tetrahedron, both approximations coincide, residuals scale as lam^3 with observed order
3.000-3.006); on the bipyramid second order improves at every registered coupling
(observed order ~3.0-3.1). Exact evolution of all 16 bare pairs conserves norm, total energy and
flatness (<= 7.2e-15) while bare defect number is NOT conserved (sector departure > 1e-8 as
registered). Conclusion per the interpretation gate: EXACT defect-number conservation is removed
as a required fundamental postulate for the LEADING hopping approximation only; nothing here
derives the perturbation from reduction, produces fermions, or establishes binding.
Cross-checkout reproduction: an independent implementation written from the protocol alone agrees
with Astra's archived numbers to machine precision (band eigenvalues max diff 0.0 on tetrahedron,
5.3e-15 on bipyramid; first/second-order matrices <= 2.1e-15).
*Status:* DERIVED algebra + MEASURED numerics within the declared model; POSTULATED H(lam) itself.
Evidence: `src/constraintnet/defect_perturb.py`, `tests/test_defect_perturb.py` (9 tests),
`examples/p33_effective_local.py`, `reference/local_qwen/data/p33_effective.json`; protocol
`docs/P33_VIRTUAL_PAIRS.md` (commits b8e462f, a836e7d); Astra records
`reference/astra_session/data/p33_virtual_pairs.json`. Diary E063.

**57 — MEASURED, exploratory (local Qwen, universality matrix):** the tetrahedron-seed landscape
result of row 26 ("vacuum is the only closed equal-action basin under action H with exact
edge-multiplier dynamics") holds for every group in {Z2, Z3, S3, D4, Q8, A4}: zero nonvacuum closed
plateaus across all six (physical state counts 8/27/49/176/176/178). Orbit decomposition of G^3 under
residual global conjugation agrees with Burnside's lemma for every group against values hand-computed
before execution; the A4 little-group census reproduces the pinned histogram (130 trivial / 26 Z3 /
21 V4 / 1 whole-group). Q8 — non-abelian with center {±1} and three distinct order-4 centralizers —
traps no basin, so a large center is not sufficient to protect one under this action. *Scope:* six
small groups, single action H, tetrahedron seed, declared multiplier dynamics; exploratory search,
NOT a theorem for arbitrary finite groups or other actions; strengthens but does not universalize
row 26. New machinery: `TableGroup` verifies closure/associativity/identity/inverses/generation at
construction (a broken table fails where it is built). *Evidence:* `examples/universality_matrix.py`,
`reference/local_qwen/data/universality_matrix.json`, `src/constraintnet/groups.py`,
`tests/test_properties.py::test_kernel_orbit_quotient_matches_burnside`. Diary E064.

**58 — MEASURED (local Qwen, F8 scaling study; module characterization):** for the WHOLE-COMPLEX
region, DriverA(model="relational") on kuhn balls accepts only proposals on purely-interior edges:
zero surface-edge acceptances in 12,000 moves across {Z2,Z3,S3,D4,Q8,A4} × n ∈ {2,3}, and interior
proposals are accepted essentially always (accepted counts within |z| ≤ 2.1 of the closed-form
Binomial(steps, interior-edge fraction)). The acceptance rate is therefore pure boundary geometry --
(E_total − E_surface)/E_total = 0.265 at n=2, 0.419 at n=3 (Euler on the sphere), rising toward ~1
with mesh size -- refuting this study's first-draft prior that rates should drop with system size.
Equivalently: whole-complex relational dynamics is exactly "bulk churns freely, boundary frozen"
(E064-P2's interior-churn asymmetry in closed form). *Scope:* characterization of the declared
region+driver combination, not of dynamics under arbitrary regions; consequence -- accept-rate
cross-checks (backlog item 7) are meaningless without stating the observed region, and whole-complex
rates must not be compared to single-tetrahedron baselines. All F8 scaling assertions held: gauge
invariance at n=3, conservation recomputed-from-complex over 500×2 steps per cell, Pachner exact
round-trips at n=3, kernel quotient == Burnside for k = 1..4 free edges. *Evidence:*
`examples/f8_scaling_study.py`, `reference/local_qwen/data/f8_scaling.json`. Diary E065.

**59 — MEASURED (local Qwen, E066 free-space v1; DriverC characterization + tracking-methodology):**
(a) STRUCTURAL (pinned by tests): Pachner 2<->3 relinkings integrate cleanly into relational dynamics
-- interior relinkings are never vetoed (boundary observables cannot see them), boundary sphere and
canonical state stay exactly frozen across mixed label+relinking runs, Euler characteristic V-E+F-T=1
is preserved step-by-step, and NO-TELEPORTATION holds: surviving faces keep their holonomy under
relinking; curvature changes only on move-added/move-removed faces or faces containing the changed
edge. (b) NEW PHYSICS CHANNEL (exploratory measurement, A4 n=3, 300 steps x 3 seeds vs label-only
control): relocation of a seeded curvature cluster acquires a relinking-attributed component (~2/3 of
tracked support changes in DriverC runs; first displacement at steps {4,3,1} vs {34,20,1}) -- motion by
having the track relaid under the object, without label change. (c) NEGATIVE/METHODOLOGICAL: under
whole-complex relational acceptance nothing confines bulk curvature creation -- vacuum energy grows
6 -> ~230 (A) / ~370 (C) curved faces at matched steps (relinking heats ~1.6x faster; triangulation
inflates 162 -> ~250 tets, no stationarity of the proposal scheme), and naive overlap-lineage
"survival" is a METRIC FAILURE: tracked clusters end at 96-100% of global curvature (the tracker
follows the heat). Persistence claims therefore require extent normalization against matched vacuum
AND confinement beyond boundary freezing (Gauss completion or energetic acceptance) -- free space v1
provides neither, by design. *Scope:* A4 n=3 balls, whole-complex regions, uniform site-pool
proposals; exploratory for (b), structural pins for (a). *Evidence:* `src/constraintnet/drivers.py`,
`tests/test_driverC.py` (8 tests), `examples/free_space_tracking.py`,
`reference/local_qwen/data/free_space_tracking.json`, figure
`reference/local_qwen/figures/e066_free_space_accretion.png`. Diary E066.

**60 - MEASURED (local Qwen, E067 hard-Gauss completion v1; classical Z2 phase space):** an explicit
matter-coupled Gauss construction satisfying HANDOFF correction 2's demand: charges are DEFINED as q_v
:= div(E)_v over electric flux bits E_e on the complex edges, so the constraint is SOLVED not penalized.
Structural consequences verified (9 tests + asserted every step): total charge parity identically even,
isolated charge unconfigurable (charges are string endpoints), loaded strings carry charge only at their
two ends, boundary vertices absorb charge as an exterior reservoir (the open-boundary channel P32-3 asked
for). Measurement (Z2 n=3, 600 steps x 4 seeds; priors G1-G3 stated before running): (G2) the magnetic
vacuum stays COLD (#curved faces max = 0) at every string tension scanned -- E066's runaway heating was an
artifact of RELATIONAL acceptance, not intrinsic; energy-based Metropolis acceptance removes it. (G3) a
CONFINEMENT SCALE: mean live charge count falls monotonically in beta_E (energy per flux edge) 30.3 ->
26.4 -> 17.8 -> 3.9 -> 1.5 across beta_E = 0..8, bound-pair fraction rises 0 -> 0.75 while the deconfined
multi-charge phase vanishes; at high tension a seeded interior pair persists as a bound string. *Scope:*
classical Z2 (connection + flux bits), NOT quantum amplitudes, NOT nonabelian, no magnetic-electric sector
coupling yet -- this is the completion v1 HANDOFF required, not mobile matter under a full local Gauss law
and not a claim of nature's confinement. *Evidence:* `src/constraintnet/gauss.py`, `tests/test_gauss.py`,
`examples/gauss_confinement.py`, `reference/local_qwen/data/gauss_completion.json`, figure
`reference/local_qwen/figures/e067_gauss_confinement.png`. Diary E067.

**61 - MEASURED / METHODOLOGICAL (local Qwen, E068 independent extent-based persistence criterion):** an
extent-only persistence test that consults NO charge signature (independent of Milestone-4 is_persistent),
built to close E066's promise of "extent normalization against matched vacuum". Validated on relational
curvature (DriverA(relational), Z2 n=3, 500x3 seeds + matched no-seed vacuum): a seeded lump is rejected
by both gates (lifetime 38 steps, locality 0.881 = became-the-background, SNR -0.20 against a hot vacuum
of ~118 curved faces) -- the criterion reproduces E066's negative verdict WITHOUT using charge, so two
independent notions of objecthood agree that unconstrained curvature is not matter. TWO metric findings:
(i) LOCALITY ALONE MISFIRES ON A COLD VACUUM -- a lone object in an empty background has tracked/global
-> 1 (dominance), indistinguishable from E066 dilution; the load-bearing gate must be vacuum-relative
signal-to-noise, locality demoted to diagnostic. (ii) CONFINEMENT IS NOT PERSISTENCE -- a Gauss-confined
charge pair at high beta_E is driven to ANNIHILATE (retracting the string lowers energy); Gauss protects
charge number but nothing prevents annihilation, so "confined" != "persistent"; matter needs a charge-
conjugation selection rule. The confined-pair regime is reported INCONCLUSIVE (extent undefined at t=0;
annihilation vs averaging-artifact not separated) rather than tuned to the prior that it would persist.
*Scope:* Z2 n=3, classical; metric + observation, no new physics entity claimed. *Evidence:*
`src/constraintnet/persistence_metrics.py`, `tests/test_persistence_metrics.py`,
`examples/e068_extent_vs_charge.py`, `reference/local_qwen/data/e068_extent_persistence.json`. Diary E068.

**62 - MEASURED / NEGATIVE (local Qwen, E069 Z_N Gauss completion + N-ality classifier):** abelian
N-ality **delays** annihilation but does **not** supply the charge-conjugation selection rule that E068
demanded. Built `gauss_zn.GaussStateZN` (electric flux a_e in Z_N; charges DEFINED by the solved
constraint q_v := div(E)_v mod N) and a pure classifier `nality_content` that pair-cancels live charges
(k <-> N-k) and reports irreducible content. Measured on the n=3 Kuhn ball under `DriverGZN` (Metropolis,
H = beta_B*#curved + beta_E*sum|a_e|):
* **Structural (holds).** Z2 carries NO baryonic content whatsoever (exhaustive over all neutral charge
  multisets up to size 6): every charge is self-inverse, so E068's annihilating pair was the generic case,
  not an artefact. An equal-flux star junction is invisible iff it has exactly N arms -- a genuinely
  irreducible triple in Z3 (neutral, zero cancelling pairs, 3 constituents), a 4-site object in Z4.
* **PC REFUTED as a stability claim.** Seeded Z3 baryons ALL decay: t_vacuum = [1899, 2261, 3023, 3135,
  1833, 3966] within 12,000 steps (0/6 survivors) against meson [1895, 1992, 2060, 1001, 1832, 1797].
  Median delay only x1.4 (2642 vs 1863); per-seed bimodal (+1 to +2169 steps). The pre-registered
  mechanism -- decay needing three-body coincidence -- is WRONG: charge is additive at a site, so two unit
  charges FUSE into the antiparticle of the third and a two-step route always exists. N-ality is a kinetic
  hindrance (extra encounters), not a forbidden process. Absolute stability therefore cannot come from
  abelian charge arithmetic; it needs an inaccessible balancing charge (superselection / lightest-in-sector)
  or nonabelian fusion constraints.
* **PD MEASURED -- abelian models contain no dyons.** The magnetic observable is unchanged by an electric
  string (mean curved faces in the tail: 4.508 without vs 4.510 with), and a charge deliberately seeded ON
  a curved cluster has its charge-curvature correlation decay from 0.2569 (early quarter) to 0.0534 -- the
  level of a charge merely present somewhere (0.0528). Flux and charge diffuse independently: the product
  structure of the sectors is confirmed rather than assumed. Dyon coupling requires nonabelian flux x
  centralizer-irrep structure, not an added cross term.
* **Plasma threshold quantified.** At beta_E = 2 the *unseeded* vacuum carries ~25.6 spontaneous charges and
  reads baryonic in 66% of steps; at beta_E >= 8 it is clean (0.27 -> 0.00). Single-object language requires
  a measured plasma threshold plus matched-vacuum controls -- E068's SNR lesson, now with numbers.
* **Removal channel identified.** exited_charge = 0 at every t_vacuum: these objects annihilate rather than
  being absorbed by the exterior reservoir, despite boundary occupancy in 0.25-0.70 of steps.
*Scope:* classical abelian Z_N (N=2,3,4), n=3 Kuhn ball (interior is only 8 mutually close vertices, every
one adjacent to the boundary -- annihilation and absorption cannot be separated geometrically on this
frame); comparisons ACROSS N are confounded by the proposal law (in Z_N a random shift retracts with
probability 1/(N-1)), which is why the load-bearing comparison is within N=3. *Evidence:*
`src/constraintnet/gauss_zn.py`, `tests/test_gauss_zn.py` (21 tests), `examples/e069_nality_and_dyons.py`,
`reference/local_qwen/data/e069_nality_dyons.json`. Diary E069.

**63 - MEASURED (local Qwen, E070 wall stability: hard superselection vs soft energy barrier):** stability in this
framework is a property of WHICH rewrites exist, not of what they cost. Two imposed boundary conditions on admissible
rewrites, defined relationally (BFS layers of the 1-skeleton -- no grid coordinates), tested on Z3 at beta_E = 12:
* **Hard wall = absolute stability.** With flux proposals across a closed sphere structurally disallowed, the enclosed
  charge sum is invariant (asserted every step; no leak) and the region can never become neutral: 3/3 seeds survive the
  full 8,000-step horizon with >=1 live defect inside, while the identical no-wall control neutralises at t = [11,
  3393, 2408]. Mechanism is superselection -- neutrality would require changing frozen crossing flux -- not a barrier.
* **Soft wall = NO stability (negative).** Weighting crossings by lambda in {1,2,4,8} leaves decay time bit-for-bit
  unchanged (log-log slope 0.000). The census of accepted crossing-flux changes explains it: up = 0, down = 3 -- every
  accepted change is RETRACTIVE, and retraction is downhill for every lambda, so raising lambda pays the system MORE to
  annihilate. Kramers/Arrhenius scaling needs an uphill segment on the decay path; string retraction has none.
* **Consequence for the particle programme.** Energy can bias rates among existing reductions but cannot remove a
  reduction; therefore cost cannot protect matter -- only structure can (a missing move, not an expensive one). This
  turns the knot/topological-closure hypothesis from a preference into a REQUIREMENT: a stable object must block the
  shortening rewrite combinatorially.
*Scope:* classical abelian Z3, n=3 Kuhn ball, walls imposed (no emergence claimed); Metropolis driver, so "admissible"
means proposed-and-accepted and uphill moves are already effectively removed at beta_E = 12. *Evidence:*
`src/constraintnet/gauss_zn.py` (wall API), `tests/test_gauss_zn.py` (23 tests incl. hard-wall invariance),
`examples/e070_wall_stability.py`, `reference/local_qwen/data/e070_wall_stability.json`,
`reference/local_qwen/figures/e070_arrhenius.png`. Diary E070.

**64 - MEASURED / NEGATIVE + STRUCTURAL (local Qwen, E071 link type vs electric-flux lifetime; the trilemma):**
link/knot type does NOT protect abelian electric flux in the current move set, for structural rather than numerical
reasons. Prepared fixtures on the n=4 Kuhn ball (verified: Lk(A,B) = -1 Hopf, Lk(A,B') = 0; all loops 8 edges and
charge-free; grid coordinates used only to build and measure them), evolved with DriverGZN at beta_E = 12:
* **No protection.** Linked vs unlinked arms of identical flux length are indistinguishable: Z2 medians 1638 vs 1443
  (one decayed seed each, 3/4 survivors in both); Z3 zero decays in either arm within 2000 steps.
* **Mechanism confirmed.** Creations = 0 and max upward excursion = 0 in every run: total flux length decreases
  monotonically. Decay is edge-by-edge deletion, which never needs to change link type.
* **The invariant barely exists along trajectories.** Divergence-free fraction of steps = 0.028-0.098; after the first
  deletion the support is not a union of loops at all, so 'the knot class of the evolving object' is undefined ~95% of
  the time.
* **Charge-freedom is frozen (exhaustive).** Z2 604/604 and Z3 1208/1208 single-edge moves create charges; none keeps
  q == 0. Limit stated honestly: multi-edge moves along closed cycles DO preserve divergence, so the freeze claim covers
  single-edge dynamics only -- and that loophole is where E072 goes.
* **Apparent longevity = proposal dilution.** ~6 deletions per 2000 steps purely from hitting-rate; Z3 outlives Z2 for a
  reason in the proposal law (1 of 2 deltas deletes), not physics -- same confound flagged in E069.
* **The trilemma (standing frame).** Either dynamics can act -> flux decays by local deletion and topology is irrelevant;
or you forbid charge creation -> single-edge dynamics vanish and nothing evolves; or protection needs a THIRD option: a
local divergence-preserving move set (flux updates along elementary face boundaries -- the toric-code/string-net rule)
where unlinking cannot be done by deletion and must pass through longer configurations: a barrier of topological rather
than imposed origin, exactly what E070 demanded. Registered as E072.
*Scope:* abelian Z2/Z3 electric sector, n=4 Kuhn ball, prepared loop fixtures (declared), Metropolis at beta_E = 12.
*Evidence:* `examples/e071_link_lifetime.py`, `reference/local_qwen/data/e071_link_lifetime.json`.
Diary E071.

**65 - MEASURED / NEGATIVE (local Qwen, E072 face-boundary dynamics: locality does not make topology protective):** a
LOCAL charge-conserving move set still fails to protect contractible flux in a ball -- and linking slightly ACCELERATED
annihilation. DriverHZN updates flux only along boundaries of elementary triangles, so div E is preserved by construction
(verified over 360k moves: charge zero at every step) and the support stays a union of closed cycles -- which made rho_link
measurable on EVOLVING states for the first time: 1.000 (Hopf arm) vs 0.000 (matched unlinked control), read off the state.
* **Barriers appear but are tiny:** upward excursions of total flux length became positive (max +2 Z2, +1..+3 Z3) where
  E071 gave exactly zero -- we left monotone deletion, but a few units at beta_E = 4 protects nothing.
* **No protection; mild anti-protection (Z2):** linked median 8431 vs matched unlinked 9831, survivors 0/3 vs 2/3. The
  readout shows why: the pair NEVER unlinked (unlink_step None everywhere); components MERGED where adjacent and the merged
  cycle then shrank -- linking brings strands into contact and hands annihilation a shortcut.
* **Z3 inconclusive** ([6078, 19159, 19700] vs [None, 11702, None], censored near horizon) -- reported as inconclusive, not
  support. FD untestable (no unlinking event ever occurred).
* **Verdict as pre-committed:** failure of the knot hypothesis at this scale, not a measurement problem; caveats stated
  (8-edge fixtures => shallow linking; Z3 censoring) but not used as excuses.
* **Consequence for E073.** Face moves change flux by a BOUNDARY, so its class in H_1(complex; Z_N) is conserved EXACTLY.
  That group is trivial in a 3-ball -- which is exactly why everything evaporated from E069 through E072. Give the relational
  complex nontrivial homology (periodic / 3-torus Kuhn lattice) and a noncontractible flux cycle cannot be removed by ANY
  local rewrite: protection as a missing move, supplied by global topology of the entailment network rather than by cost.
*Scope:* abelian Z2/Z3 electric flux, n=4 Kuhn ball, prepared loop fixtures, Metropolis at beta_E = 4, horizon 20k, seeds
0-2. *Evidence:* `src/constraintnet/gauss_zn.py` (add_face_flux), `src/constraintnet/drivers.py` (DriverHZN),
`tests/test_gauss_zn.py` (27 tests), `examples/e072_face_flip_links.py`,
`reference/local_qwen/data/e072_face_flip_links.json`. Diary E072.
