# Research Diary — Event-Constraint Dynamics

**Project:** constraintnet — a discrete event–constraint–simplicial simulator built from a single axiom.
**Axiom:** *Directed implications reduce.* No space, time, matter, energy, observer, continuum, or coordinates is assumed.
**Repository:** this workspace; branch `bionic/kernel-drivers` (tip of all findings below unless noted).
**Evidence rule:** every entry cites code and tests. Tests are the authoritative record; when prose and tests disagree, the tests win. Statuses: **VERIFIED** (proof or exhaustive computation), **MEASURED** (deterministic simulation, reproducible), **PROVISIONAL** (conditional on stated open items).

Reading guide: entries are chronological within parts; each is self-contained. Conventions (class order `[id, 3−, 3+, 2]`, conjugation `x ↦ g⁻¹xg`, canonical edge keys) live in [CONVENTIONS.md](CONVENTIONS.md); theory narrative in [../Memo.txt](<../Memo.txt>) with corrections in [MEMO_PATCHES.md](MEMO_PATCHES.md).

---

## Part I — The finite seed and its gauge structure

### E001. Gauge-fixed tetrahedral configurations: 1728 → 178 (VERIFIED)
For the tetrahedral boundary ∂Δ³ with edge labels in A₄, spanning-tree gauge fixing leaves three independent labels; raw slice size |A₄|³ = 1728. Quotienting by residual global conjugation yields **exactly 178** physical classes. Independently confirmed by Burnside: (12³ + 3·4³ + 8·3³)/12 = 2136/12 = 178, and orbit sizes {1², 3²¹, 4²⁶, 12¹³⁰} satisfy Σ = 1728. Little-group census: trivial ×130, Z₃ ×26, V₄ ×21, A₄ ×1 — only the vacuum is fully symmetric.
*Evidence:* `tests/test_tetrahedron_enumeration.py`; recomputed independently via triple-orbit machinery in `tests/test_backlog_claims.py`.

### E002. Canonicalize for reporting, never for exploration (VERIFIED; methodological)
Right-multiplication of edge labels does not commute with global conjugation. Exploring the transition graph from canonical orbit representatives alone **loses transitions**: 174 orbits found instead of 178, missing exactly four pure-Klein-four configurations whose only incoming edges come from non-canonical neighbours. The correct protocol explores raw gauge-slice configurations and projects to orbits afterwards.
*Evidence:* `tests/test_states.py`; `docs/PHYSICS_NOTES.md` §7; asserted failure of naive equivariance in `drivers.py::orbit_sigma_well_definedness`.

### E003. Reachability is move-set-relative (MEASURED, exact)
On the 1728-point gauge slice: a **fixed** order-3 generator reaches only 27 states; moves by **any** element of the order-3 classes reach all 1728 and touch all curvature signatures (ergodic); order-2 moves reach exactly 64 = 4³ raw states. The frozen early visualization, whose seed gauge-fixes to three order-2 labels, explores precisely **6 physical classes**, sizes [4,12,12,12,12,12]. Superselection-like fragmentation here is dynamical (relative to the allowed rewrite set), while charge conservation is relative to the boundary-preservation rule — two logically distinct layers.
*Evidence:* `reference/opus_audit/crosscheck*.py` (external audit, corrections applied); to be codified as in-repo assertions (queued).

### E004. Curvature signature counts and a chirality-flip theorem (VERIFIED)
Face-holonomy class 4-tuples over ∂Δ³: **82** ordered signatures; **20** under pure multiset sorting (the number quoted in early notes — it is a sort, not a group quotient); true vertex-relabeling orbits are **13** (orientation-preserving) and **11** (full S₄). The strict refinement occurs because relabeling can invert an edge (`A_ji = A_ij⁻¹`), and inversion swaps the two order-3 chirality classes: a single relabeling orbit spans several sorted tuples.
*Evidence:* `reference/opus_audit/vertex_reweight.py` + README corrections; class-order conventions in CONVENTIONS.md.

---

## Part II — Charge, conservation, confinement

### E005. Charge cannot be surface flux; it is cycle holonomy (VERIFIED)
For curvature Φ = dA and abelian G, the signed sum of face curvatures over **any closed surface vanishes identically** — every edge of a closed surface lies in two faces with opposite induced orientations (d² = 0 read additively). Curvature is "magnetic": no monopole flux. The usable Gauss law is the open-disk one: flux through a disk equals the holonomy of its boundary loop. Hence physical charge = conjugacy class of **cycle** holonomies, as the axiom-stack demands. Non-abelian Bianchi requires framing data that was deliberately not invented; the code raises `TypeError` rather than return a framing-dependent number.
*Evidence:* `tests/test_bianchi.py`; `holonomy.bianchi_defect()`.

### E006. Confinement of charge is exact (MEASURED)
On a closed Kuhn 3-ball (48 tetrahedra, A₄ labels), under the rule that a move is accepted iff no watched region's appearance changes: surface-edge moves rejected **1108/1108**, interior moves accepted **392/392** over 1500 steps. Charge cannot leak through a closed boundary; the leaks counter (boundary conjugacy data recomputed after every fluctuation pair) stays zero.
*Evidence:* `tests/test_boundary_conservation.py`, `tests/test_backlog_claims.py` item 1; `persistence.py`.

### E007. Matter is a conserved external residue; neutral lumps are virtual (VERIFIED, definitional + test)
A persistent object is defined as a **nontrivial conserved external residue**: charged defects survive 100% of runs with zero gaps and charge class start == end (spec Test 5); a neutral interior lump has trivial external signature and no protection — classified *virtual fluctuation, not matter*, by definition rather than dynamics.
*Evidence:* `tests/test_persistence.py`; `persistence.py::is_persistent`.

### E008. The reject rule is a one-way door (VERIFIED, exhaustive proof)
A violated constraint can never be restored by the reject-and-revert rule alone: exhaustive BFS on the Z₃ tetrahedral state space (729 states) proves Kac return time = |S|/N₀ and that rejection never re-satisfies a violation. Genuine restoration requires an energy-raising kick combined with low Metropolis β (both trials restored full sector). Honesty note: "temperature" in this study is a statistical parameter over a chosen action, **not** physical temperature.
*Evidence:* branch `bionic/kick-test`, `kick.py` + exact proof; honesty note in docstring.

### E009. Accept rate is topology, not dynamics (MEASURED)
Interior accept rate on the closed ball: measured 392/1500 = 0.2613 against combinatorial interior fraction 26/98 = 0.2653 — agreement within 1σ. The acceptance statistics of the constraint filter are fixed by region combinatorics, not by driver details.
*Evidence:* session measurement recorded in README findings table; cross-driver consistency E014.

---

## Part III — Hidden internal state (the matter/light distinction)

### E010. Cone over ∂Δ³: hidden interiors exist only non-abelianly (VERIFIED, exhaustive census)
For the cone v∗∂Δ³ with boundary data B, admissible interior resolutions modulo boundary-invisible gauge give |I(B)|: flat B with no flux → **|I| = 1** (raw exactly |G| = 12; light-like); curved B under flat-interior requirement → **|I| = 0** (one vertex cannot cap arbitrary curvature); uniform Klein-four flux → **|I| = 6** (raw 72). Flux census over flat boundaries: 103 realizable patterns, |I| ∈ {1,3,4,6,12,16,24,36,48}, and the **vacuum is the unique light-like pattern**. Z₃ control: all 27 patterns give |I| = 1 — hidden internal ambiguity requires non-abelian-ness.
*Evidence:* `tests/test_resolutions.py`; `resolutions.py`.

### E011. Chirality selection on flux distributions (VERIFIED)
Uniform order-3 flux around the cone is **unrealizable** (three equal order-3 curvatures do not close), while uniform Klein-four flux is realizable. Not every formally stated charge distribution exists; chirality is a selection rule, first appearing at the level of flux closure. Related: single-face Z₃ flux is unrealizable by the rank theorem E019.
*Evidence:* `tests/test_resolutions.py`; `strings.py` solver.

---

## Part IV — Quantum-structural results

### E012. Sector multiplicities from centralizers (VERIFIED, exact)
For boundary charge q, residual symmetry H = C_G(q). Decomposing the conjugation action on internal resolutions: order-3 charge → Z₃ sectors with multiplicities **(4, 2, 2)**; order-2 charge → V₄ uniform **(2, 2, 2, 2)**. These are the primitive quantum sectors of the theory — irreps of the trap's own residual symmetry.
*Evidence:* `sectors.py`, `tests/test_sectors.py`; memo cross-checks 54+45+45 and 48+32+32+32 (external, Opus).

### E013. Fusion sanity: exactly one singlet in 3⊗3 (VERIFIED; lesson encoded)
A₄ irreps via χ₃(g) = fix(g) − 1 and abelianization A₄/V₄ ≅ Z₃ (homomorphism asserted at construction). Verified orthonormality, Σd² = 12, fusion 3⊗3 = 1 + 1′ + 1″ + 3·3. The invariant content: **exactly one** trivial summand — "three 1D summands ≠ three singlets"; the ω-charged partners are twisted sectors, not invariants. This lesson is guarded by test to prevent regression of interpretation, not just computation.
*Evidence:* `reps.py`, `tests/test_reps.py`.

### E014. Cross-driver consistency of a statistical quantity (MEASURED)
Z₃ flat cone pair: exact meshable fraction **1/9** computed by full phase sweep (deterministic ensemble over initial phases); DriverA (stochastic veto) reproduces **0.1118 ± 6×10⁻⁴**. Same underlying set, two measures — the mandatory ensemble harness works and the drivers agree where they must.
*Evidence:* `interaction.py`, phase-sweep runner; recorded in R_TRACK finding 2.

### E015. Discrete Aharonov–Bohm: visibility IS the flux character (MEASURED, exact)
Two-path probe around a curvature defect yields fringe visibility **V = |χ₃(flux)|/3 exactly**. Z₃ (abelian) probes shift phase with V = 1 — which-phase information trades against which-path exactly as in continuum AB. This is interferometric sector identification available inside the simulation, not an analogy.
*Evidence:* `fringe.py`, `tests/test_fringe.py`.

### E016. Absorption cross-sections: curvature suppresses ×4; abelian blindness (MEASURED)
Full-ensemble absorption of probes by an object is **phase-invariant** — an invariant of the object–face pair. A₄ flat shared face: 12/1728 compatible probes; curved: **3/1728** (suppression exactly ×4). Z₃ gives 0.1111 regardless of curvature — *abelian blindness* to curvature as a distinguisher. Prepared-probe absorption, however, IS phase-dependent (0 ↔ ⅓ gating): clock-gating is real physics for individual probes; ensemble averaging hides it.
*Evidence:* `interaction.py::phase_locked_outcomes`, stride scans; R_TRACK findings 3–4.

### E017. D(A₄) modular data, complete and verified (VERIFIED — the kinematic capstone)
The Drinfeld double D(A₄) of this theory: **14 sectors** ([flux class], centralizer irrep); quantum dimensions d = |cl(g)|·dim ρ with Σd² = 144 = |A₄|². S-matrix (normalization |C_A||C_B|/|G|², pinned by hand-built toric-code Z₂ control): unitary, symmetric, vacuum row d_a/|G|. **S² = charge conjugation** (involution). **(ST)³ = (τ/D)S² with Gauss phase τ/D = 1 exactly** (c ≡ 0 mod 8, untwisted). Verlinde coefficients: nonnegative integers; quantum-dimension homomorphism; vacuum appears exactly once in every a×ā. Sub-rules all green: pure charges fuse as Rep(A₄); **shift rule 1′ × F₁ = F₂ exact**; twisted action for ρ=3 matches explicit restriction Res 3|⟨c₁⟩ = χ₀+χ₁+χ₂. Flux-level class algebra, exact structure constants (class order [id, 3−, 3+, 2]): **C₂² = 3C₁ + 2C₂**; **C₃·C₄ = 4C₁ + 4C₂** with no flux term surviving; **C₃² = 4C₄ only** — squares land in the opposite chirality class, never the identity (a 3-cycle's inverse is never in its own class).
*Evidence:* `category.py`, `tests/test_category.py` (every criterion above is an assertion).

### E018. Convention referee: unitarity sees the ring; (ST)³ sees the ribbon (VERIFIED — methodological discovery)
Two conjugation-direction conventions for the S-matrix sum both yield unitary, symmetric matrices with correct vacuum rows **and identical fusion coefficients** — every "obvious" check passes for both. They are separated only by the chirality-sensitive identity (ST)³ = (τ/D)S²: the asymmetric form (first factor conjugated by x, second by x⁻¹) satisfies it exactly; the symmetric variant fails with error O(1). Two apparent theories with the same fusion ring and different braided-ribbon structure; the third identity is the referee. General lesson recorded: partial axiom satisfaction must never be reported as full verification when a discriminating identity exists.
*Evidence:* `tests/test_category.py::test_st3_identity_referees_convention`; docstring warning in `category.py::s_matrix`.

### E019. Bianchi's theorem as a rank computation; isolated flux is impossible (VERIFIED)
Over Z₃, prescribed face curvatures Φ = φ are realizable as dA iff φ lies in the image of the coboundary map — decided by Gaussian elimination over GF(3). Consequences derived rather than postulated: patterns with exactly **one curved face have no preimage** (isolated flux cannot exist); every exact curvature pattern is solvable; on a single tetrahedron, alternating four-face patterns are realizable and detect as closed bubbles. The smallest realizable flux supports are closed dual loops.
*Evidence:* `strings.py::solve_flux_z3`, `tests/test_strings.py`.

### E020. Topological spins: fermionic twists exist; statistics pending (VERIFIED for twist)
θ_{(C,ρ)} = χ_ρ(g_C)/dim ρ — a charge's character evaluated on its **own flux** (self-Aharonov–Bohm; in a relational universe this is the native spin: no ambient space to rotate under). Spectrum: pure charges θ=1 (the 3-dim irrep a non-abelian boson); order-3 dyons θ ∈ {1, ω, ω²} (spin ±1/3 anyonic loops); **two V₄-flux dyons with θ = −1** — self-dual, arriving as a relabeling doublet. Explicit caveat maintained: θ = −1 fixes the ribbon twist; exchange statistics live in R-symbols; the W₂×W₂ → vacuum channel must be checked before any "fermion" claim.
*Evidence:* `category.py::t_matrix`, structural tests; external table `reference/opus_audit/fermion.py`.

---

## Part V — Geometry, observer, gravity-adjacent

### E021. Static charge contributes zero event density (MEASURED — negative result with teeth)
Vacuum-twin experiment: matched runs (same complex, driver, step count; charged vs flat initial labels) give per-shell density ratios of **exactly 1.000**. A static topological defect does not densify the observer's event mesh at all. Consequence for the gravity programme: propagation delay must be derived from **activity** — churn, waits, do-undo work near defects — never hardcoded as ×n(x); the hardcoded-n variant is retained only as a flagged control arm to avoid circularity.
*Evidence:* session measurement recorded in README; method = matched-run differencing.

### E022. Holographic entropy S(R) = log|I(∂R)|: vacuum entropy is exactly zero (MEASURED, ×3 sizes)
Region-generalized internal-resolution entropy with cone conventions reproduced exactly (spot-checks: vacuum 12→1; uniform V₄ flux 72→6). Nested face-metric balls in Z₃ Kuhn n=2 at radii 1, 2, 3: **S_flat ≡ 0** at every radius — flat fillings relative to boundary are unique (H¹(R,∂R; Z₃) = 0 empirically); free-curvature baseline S_free = E_int·log 3 = 0, 2.197, 7.690 against |∂R| = 12, 24, 34 — volume-like, not area-linear. **Hidden-resolution entropy is entirely defect-carried.** For the Jacobson route to field equations this sharpens rather than helps: horizon entropy must come from defect resolution degeneracy, and the defect ensemble awaits seeded flux loops.
*Evidence:* `entropy.py`, `tests/test_entropy.py`; measurement rows in commit 168f46d.

### E023. Gluing is obstructed globally: Bianchi re-derived as sheaf defect (VERIFIED)
Curvature assignments that are locally free (each tetrahedron individually fillable) can fail to glue to global sections. On the Z₃ exhaustive model: the Gauss kernel equals the global image **as sets**, and **54 of 81 candidate worlds are forbidden by globality alone**. The Bianchi identity re-emerges as the failure of a sheaf gluing axiom — geometry's consistency condition is a cohomological obstruction, computed rather than imposed.
*Evidence:* `sheaf.py`, `tests/test_sheaf.py`.

### E024. Tetrahedron orientation is data, not decoration (VERIFIED; methodological)
Sorting simplex vertices discards which side is "out"; interior faces then fail to cancel and "boundary" becomes meaningless. Orientations are propagated purely combinatorially (no coordinates) by `orient_consistently()`, with flip counts reported. Kuhn lattices require it.
*Evidence:* `complex.py`, `tests/test_complex_integrity.py`.

### E025. Legitimacy is region-relative (OPEN, by design)
"A rewrite is physical iff it preserves the appearance of watched region R" makes what-counts-as-outside part of the setup. Feature reading: observers are physical apparatus; charge is always measured relative to one. Cost: mass proxies and costs become finite-size dependent and must be reported as functions of R. Current stance: feature, with region size always reported alongside any cost. Not settled by user; M5 must state its choice explicitly.
*Evidence:* `docs/PHYSICS_NOTES.md` §6.

---

## Part VI — Standing open problems (ordered as research agenda)

1. **Gapless photon.** Untwisted D(G) for finite G is a gapped topological phase; electromagnetism is gapless. Candidate resolutions: critical growth dynamics, anyonic condensation, or separate-sector origin. Falsifiable and bounded; the simulation is referee.
2. **R-symbol / statistics check.** θ = −1 dyons (E020): compute F/R data of D(A₄); test R = −1 in W₂×W₂ → vacuum channel. Fermion claim gated on this.
3. **Seeded flux loops → defect-ensemble entropy** (E022 dependency), then area-law verdict with real defects.
4. **Knot/link invariants of flux strings** via barycentric PL embedding of the Kuhn ball (documented choice: coordinates enter invariants of combinatorics, never dynamics). Hypothesis to log, not tune: m ∝ crossing number at fixed flux class.
5. **Interferometric sector identification and loop–loop braiding** against category R-eigenvalues; three-loop braiding deferred.
6. **Born rule:** sample space = fusion channels (canonical); the measure remains one declared postulate (equal a priori weight per micro-resolution). Envariance route needs the glued flux–antiflux pair-state constructor; Gleason route needs the tube-algebra inner product. Both named, both open.
7. **Continuum limit and Lorentz recovery** — entirely open.
8. **A₄ sufficiency verdict (standing):** excellent microscopic skeleton, definitively insufficient infrared theory — no chirality of fermions, no gapless photon, no bulk point fermions (θ=−1 dyons are loops in 3+1D; point fermions need twist/spin structure). Both halves are results.

---

## Appendix A — Reproducibility

- Suite: `PYTHONPATH=src python -m pytest -q` → **197 tests green** at diary creation (commit d2f72df, branch `bionic/kernel-drivers`).
- Key reproductions one-liners in README ("Quick start"); GIFs regenerable via `python -m constraintnet.viz --demo {tetra|orbit|lattice} --gif out/x.gif`.
- External audit material (scripts + outputs of an independent reviewer, with our corrections applied): [reference/opus_audit/](opus_audit/README.md).

## Appendix B — Version anchors for headline numbers

| Number | Meaning | Anchor |
| --- | --- | --- |
| 1728 → 178 | gauge slice → physical classes | commit d122273 (M1) |
| 1108/1108, 392/392 | confinement rejection/acceptance | commit 2f427ac (M4) |
| \|I\| = 6 | hidden interiors, uniform V₄ flux | commit 4f6f596 (M3) |
| 1/9 vs 0.1118±6e-4 | cross-driver consistency | commit 4c23db2 (R2/R3-lite) |
| τ/D = 1, Σd²=144 | D(A₄) Gauss sum, total dimension | commit 59e18ef (Layer-2 item 1) |
| S_flat ≡ 0 | vacuum entropy zero ×3 radii | commit 168f46d (entropy) |

*Diary opened 2026-09-17/18 by the resident agent at Satish Mallya's request, entries E001–E025 distilled from commits d122273 → d2f72df and session measurement logs. Append new entries at the end; never edit old ones except to append a dated correction.*

---

## Part V (continued) — seeded flux loops: existence, boundary memory, and where entropy lives

### E026. Closed flux loops exist end-to-end in A₄ Kuhn balls; seed existence is order-parity-selected (MEASURED, exhaustive over seeds)
Labeling every edge incident to a vertex v by a fixed order-3 element of A₄ produces curvature supported on a **closed dual loop** — detected as kind="loop" (enter-and-exit at every touched tetrahedron) by the E019-era detector: 3-face loops at 6 of 8 vertices in Kuhn n=1, and a **12-face loop around the central vertex of Kuhn n=2**. The same construction with an involution seed is flat everywhere (t² = e annihilates both orientation-parity cases), while Z₃ seeds of value 1 survive only where traversal signs agree. Existence of seeded loops therefore depends on the **order of the seed element relative to face-orientation parity** — a selection rule discovered during construction, not assumed.
*Evidence:* `tests/test_flux_loops.py` (all three facts asserted); seeding helper `seed_star_loop`; detector from E019.

**Dated correction, 2026-09-19 (E039):** the n=1 three-face supports at six of
eight vertices are boundary-open arcs, not closed dual loops. Each has two
faces incident to only one tetrahedron. The original classifier checked tet
degree but omitted face incidence. The n=2 central twelve-face loop remains
closed. The old n=1 assertion is replaced by explicit incidence checks for all
eight vertices; the original claim above remains visible as error history.

### E027. Boundary memory and rigidity: enclosed flux forbids vacuum filling, but carries zero hidden entropy — matter-entropy is CORE-localized (MEASURED; positive + negative result)
Two measurements on balls enclosing the seeded loops:

**Dated scope correction, 2026-09-19 (E039):** measurement (a)'s actual test
uses the n=1 boundary arc corrected above. Its zero flat-interior filling count
remains verified for that fixed region, but is not a theorem about every ball
enclosing a closed loop or evidence for unpinned particle stability. The n=2
rigidity test in (b) is unchanged. The original broader interpretation follows
as historical text, superseded by this correction.

**(a) Boundary memory (positive).** Any ball whose boundary encloses loop flux admits **no flat-interior resolution: |I| = 0**. The boundary appearance cannot be vacuum — charge is measurable from outside purely as a filling obstruction. This generalizes the cone theorem E010 ("curved boundaries cannot be capped by one vertex") to arbitrary enclosing regions, and strengthens E006/E007 conservation claims: the exterior does not merely see a conserved class, it sees an **unsatisfiability** of the vacuum hypothesis.

**(b) Rigidity (negative result with teeth).** Declaring the loop's curvature by full conjugacy class (size 4 — maximal non-abelian slack) on interior faces yields a **unique filling: |I| = 1**, even when the region has genuine interior edges. Conjugacy-class ambiguity is over-constrained by flatness-plus-closure: representative choices that survive are pinned by the surrounding flat sea.

**Synthesis.** Hidden-resolution entropy (E022's defect-carried entropy) does **not** live in the field around a flux loop — it lives in the **core**: E010's |I| = 6 arises precisely at the cone apex where internal edges close the curved boundary from *inside*. A loop plus its core structure is matter; a loop alone is a rigid string with measurable charge and zero entropy. This sharpens open problem 3: the defect-ensemble entropy experiment must target **core-containing regions** (all edges of a deep vertex interior), which requires gauge-slice enumeration to beat brute force at A₄ sizes — concrete plan recorded in the queue.
*Evidence:* `tests/test_flux_loops.py::test_boundary_memory_no_vacuum_filling`, `::test_enclosed_loop_rigid_under_class_declaration`; measurement log 2026-09-18 (Kuhn n=1 r=1; Kuhn n=2 r=2, |dR| = 24, E_int = 2, declared = 4).

---

## Part IV (continued) — the fermion verdict

### E028. Two dyons of D(A₄) are TRUE FERMIONS: exchange sign R = −1 computed from the universal R-matrix (VERIFIED; open problem 2 closed)

**Method, per the E018 convention-discipline.** No remembered F-symbol formulas. Simple D(A₄)-modules built concretely: basis {(x, v)} over the flux class with transversal-corrected action k·(x,v) = (kxk⁻¹, ρ(t⁻¹kt)v), representation law and unitarity asserted at construction for all 14 sectors. The universal R-matrix of the double, 𝓡 = Σ_h e_h ⊗ h, acts concretely; braiding c = flip ∘ R̂. Vacuum lines of W⊗W sought in the **grade-e subspace** (pairs whose grade product is e — k-invariant because products conjugate), found by nullspace, with monodromy c² = +1 asserted on every line before reading any sign.

**Methodological catch (recorded because it bit first):** solving k-invariance on the full tensor space and filtering grades per-vector afterwards is **wrong** — SVD bases mix grades arbitrarily; it silently dropped W₀₀'s vacuum line while admitting suspicious survivors. Project-first, then solve. The corrected computation finds exactly the six vacuum channels predicted by Verlinde (N[0][i][i] = 1 for 1, 3, W₀₀…W₁₁), sector-by-sector agreement between two independent machineries.

**Result.**

| sector | θ | R (vacuum channel) | verdict |
| --- | --- | --- | --- |
| ([c₃], W₁₀) | −1 | **−1** | **true fermion (odd exchange)** |
| ([c₃], W₁₁) | −1 | **−1** | **true fermion (odd exchange)** |
| ([c₃], W₀₀), ([c₃], W₀₁) | +1 | +1 | bosonic |
| ([c₀], 1), ([c₀], 3) | +1 | +1 | bosonic (Tannakian consistency of Rep(A₄) ⊂ D(A₄)) |

Across every channel found, **sign(R) = sign(θ)** — twist and statistics agree throughout this model; now a test-guarded theorem of the framework, not an assumption imported from continuum spin-statistics.

**Physical reading.** Fermions in Event-Constraint Dynamics are neither postulated nor bolted on: they are the self-dual V₄-flux dyons whose centralizer character is odd on its own flux. "Statistics is a charge evaluated on its own flux" (E020 preview) is now exact — θ and R both compute to −1 for the same two sectors, from combinatorial data alone.

**Standing caveats.** (i) Dimensional audit unchanged: in 3+1D these are fermionic **loops**; point-fermion-in-bulk still requires a twist/spin-structure analysis (H³(A₄,U(1)) menu). (ii) The R computation covers vacuum channels of W⊗W; general pair-channel R/F data remain to be tabulated for full braiding calculations (loop–loop braiding, item 3b). (iii) Transversal-independence of the eigenvalues is expected (gauge) and worth an explicit regression test.
*Evidence:* `doubles.py` (`vacuum_braiding_eigenvalues`, construction asserts), `tests/test_doubles.py` (5 tests incl. Verlinde cross-match and sign agreement); commit 7cd41e4.

---

## Part V (continued) — the core entropy measurement

### E029. Gauge-slice CSP solver: exact |I(∂R)| at A₄ core scale, cross-validated against brute force (VERIFIED; method)

**Method.** The brute-force resolution enumerator costs |G|^|E_int| — dead on arrival at the one interesting geometry (Kuhn n=2 central star: 14 interior edges → 12¹⁴ ≈ 1.3e15). Replacement: treat fixed-boundary filling as a constraint-satisfaction problem — variables = interior edge labels, one constraint per interior face (holonomy ∈ declared class) — solved by MRV backtracking with forward checking. The physics that makes it fast: **conjugacy-class constraints propagate.** A face whose other two edges are known restricts the third label to at most |C| values (4 for order-3 flux in A₄, 1 for flat), so branching follows class size and constraint density, not |G|. Deterministic tie-breaks; budget exhaustion raises and is reported as *skipped*, never silently truncated.

**Validation.** Exact solution-set equality against brute force on: the cone vacuum (|I|=1) and uniform V₄-flux controls (72 raw / 6 physical), plus 24 pseudo-random regions across Z₃/A₄ × {tetra, bipyramid, cone, Kuhn-1} with mixed declared/flat/unconstrained face classes. Zero mismatches.

**Methodological note (the one bug worth recording).** A first characterization pass assumed the free gauge acts as uniform left multiplication x → λ⁻¹x on all interior edges. It does not: for an edge stored as (w, v*) with w < v*, the free endpoint is the *target* and the action is x → xλ. Mixed orientation. The library quotient (`gauge_image`) was always right; the hand-rolled probe was wrong and produced 12 "states" instead of 4. Lesson generalizes E018: verify the group action you think you're quotienting by, in code, before interpreting orbit counts.
*Evidence:* `entropy.py::enumerate_region_resolutions_slice`; `tests/test_entropy.py::test_slice_matches_brute_on_cone_controls`, `::test_slice_matches_brute_random_regions`, `::test_slice_budget_exhaustion_is_reported_not_truncated`; commit 4f918a5.

### E030. CORE ENTROPY CONFIRMED: hidden-resolution entropy localizes at the defect core; |I(core)| = 4 = |flux class| (MEASURED; E027 prediction resolved)

**Setup.** Kuhn n=2, G = A₄, order-3 star seed at central vertex 13 — the only fully interior vertex of its closed star (E_int = 14, V_free = {13}; all 14 interior edges pass through it, so the gauge action is free and |I| = |Sol|/12 exactly). Curvature classes declared on interior faces from the seeded configuration: 12 curved ([c₃]), 24 flat; boundary faces all flat (the enclosed string is visible only in cycle charges — E026 geometry).

**Result.**

| region | E_int | raw \|Sol\| | physical \|I\| |
| --- | --- | --- | --- |
| core star(13) | 14 | 48 | **4** (S = log 4 ≈ 1.386) |
| field balls r=1,2 (core excluded) | 0, 2 | 1 | 1 — rigid, E027 reproduced |
| full ball | 26 | 48 | **4** — identical to core |
| involution seed control (flat) | 14 | 12 = \|G\| | 1 — flat star connections are pure gauge |
| Z₃ twin of the same core | 14 | 3 | 1 — abelian cores carry no hidden state |

**Three claims, each measured.** (1) **E027's prediction confirmed:** hidden-resolution entropy lives in the core, not the field — the field around a flux loop is rigid (|I|=1), the core carrying it has |I| = 4. (2) **Localization:** enlarging from the core star to the full ball (14 → 26 interior edges) adds *zero* entropy — every added edge is determined by propagation from the core; S(full ball) = S(core). The entropy of this piece of matter is exactly its core's, a sharp form of "matter is a topological knot with finite internal state." (3) **Non-abelian necessity survives generalization:** the Z₃ twin core has |I| = 1 — E010's "hidden state requires non-abelian-ness" holds at cores, not just cones.

**State structure.** All four physical states share ONE support: exactly 7 of the 14 star edges are active (non-identity), 7 identity — a polarization fixed by the link geometry, not by the state. States differ only in *which* order-3 element fills the support, and those four elements form exactly one conjugacy class. For this seed geometry the core's hidden internal state space is in bijection with its own flux class: **the knot's hidden degrees of freedom are the possible orientations of its charge.** (Cone counterpoint: uniform V₄-flux gave |I| = 6 ≠ |class| — the bijection is data for this geometry, not a theorem; relation to seed order and link structure open.)

**Physical reading.** A flux string with this core presents identical external data in all four internal states (same boundary appearance by construction) — an outside observer cannot distinguish them, yet they are not gauge copies. This is the framework's *hidden matter state* made concrete at ball scale: a conserved external residue plus a finite, exactly-counted interior multiplicity that no measurement through the boundary can resolve. The E010 cone count was the seed; this is the same phenomenon in a genuine 3-ball with a degree-14 core.
*Evidence:* `tests/test_core_entropy.py` (8 tests: core |I|=4, field rigidity, localization at 26 edges, involution & Z₃ controls, state/support/class structure); `examples/core_entropy.py`; commit (this session).

### E031. Pair-channel braiding of D(A₄) measured end-to-end: monodromy = θ_c/(θ_aθ_b) on all 520 channels; two independent routes to fusion agree (VERIFIED)

**Method.** For every sector pair (a,b) and every simple summand c of a⊗b: build the channel intertwiners T: M_c → M_a⊗M_b as the nullspace of the FULL equivariance system — commuting with all k-actions AND all flux-grade projectors p_h — then apply the concrete double braid 𝓜 = c_{B,A}∘c_{A,B}, assembled from the universal R-matrix 𝓡 = Σ_h e_h ⊗ h acting on hand-built D(G)-modules.

**Result.** 520 channels checked over all 14×14 pairs. (1) Concrete Hom dimensions match the Verlinde coefficients N^c_{ab} computed independently from the S-matrix — fusion derived twice, by modular data and by intertwiner counting, agreeing everywhere. (2) 𝓜 acts on each channel as the scalar θ_c/(θ_aθ_b) to 2.4e-15: max error across all channels. Phase spectrum: 180 trivial, 76 fermionic-π mutual, 96+96 ω_±, 36+36 ∓ω — the complete mutual-statistics table for loop-loop braiding (Layer-2 item 3b now has its reference predictions).

**Two bugs caught by cross-checks, both recorded per E018 discipline.** (i) *Grade-blind Hom:* intertwining only the k-actions admits spurious grade-mixing maps — Schur's lemma fails (Hom(X, 𝟙⊗X) came out 2 instead of 1). The Verlinde cross-check inside the solver caught it; D(G)-intertwiners must respect BOTH structures of the double. (ii) *Vectorization convention:* row-major vec requires vec(AT) = (A⊗I)v, not (I⊗A); the swapped form silently passes whenever one factor is 1-dimensional — which is exactly why the vacuum-channel checks (E028) had missed it. Discriminating case: charge-3 ⊗ flux, where the two conventions genuinely differ.

**Transversal independence (closes E028 caveat iii).** Rebuilding modules with reversed transversal scans reproduces R = −1 for both fermion sectors and identical channel monodromies — gauge bookkeeping changes nothing physical, now regression-guarded.

**Physical reading.** The double braid is what an interferometer measures when one flux string passes through the spanning surface of another. That this mesh-native quantity equals a pure ribbon-category prediction — on every channel, including the multiplicity-2 ones — means the loop physics in the simulation is governed by D(A₄) modular data all the way down, with no additional input. In particular: two W₁₀ fermionic loops braid through each other's channels with π phases exactly where the fusion channel is itself a fermion.
*Evidence:* `doubles.py` (`pair_channel_report`, `channel_intertwiners`, `double_braid_matrix`, grade-constraint + row-major comments); `tests/test_doubles.py::test_pair_channel_monodromy_matches_theta_ratio_all_channels`, `::test_channel_intertwiners_respect_grading`, `::test_physical_eigenvalues_are_transversal_independent`; `examples/pair_channels.py`.

### E032. Glued flux–antiflux pair states constructed; envariance of every equal-amplitude swap verified (VERIFIED structure; Born measure still postulated — open problem 6 stays open)

**Method.** For a sector a with antiparticle ā, the vacuum channel Hom_D(1, M_a⊗M_ā) is multiplicity one (guaranteed for every anyon); its normalized image |Ψ⟩ is the categorical Bell pair — the category-theoretic image of a string nucleating flux g next to flux g⁻¹ with conjugate charges and vacuum total. Schmidt structure via SVD; envariance by solving (τ_A⊗I)|Ψ⟩ = (I⊗V_B)|Ψ⟩ for every transposition τ of support basis vectors, then checking V_B unitary on the support.

**Result.** Every sector tested — pure charges (rank 3 for the 3), order-3 flux loops (rank 4), and both fermion dyons W₁₀,W₁₁ (rank 3) — yields a pair state maximally entangled on its support: ρ_A = P/rank exactly, S = log(rank). All C(rank,2) equal-amplitude swaps on side A are reproduced by unitaries on side B alone, residuals < 1e-8. The swap symmetries Zurek's envariance argument requires now exist as computed objects in the framework.

**Honest status of the Born rule (unchanged, sharpened).** Sample space = fusion channels (canonical); the measure remains one declared postulate (equal a priori weight per micro-resolution). What E032 changes: any future envariance derivation can no longer be hand-waving about "swap-symmetric states" — it must be checked against these pair states, on these swaps, with this reduced structure. The gap between envariant structure and probability measure is now the precise, named, standing open problem (Part VI item 6), not a vague one. Gleason route likewise waits on a fixed tube-algebra inner product.

**Physical reading.** The entanglement entropy of a flux loop with its antiflux partner equals log of the anyon's module dimension — for the order-3 string, log 4: the same number as the core's hidden interior count (E030) from an entirely different counting (Schmidt rank of the glued pair vs gauge orbits of cappings). Coincidence at A₄ scale or shadow of a deeper identity (internal resolution space ≍ pair-channel space)? Logged as a question, not a claim.
*Evidence:* `doubles.py` (`pair_state`, `envariance_check`); `tests/test_doubles.py::test_pair_states_maximally_entangled_with_vacuum_total_charge`, `::test_envariance_swaps_undone_by_environment_alone`; commit (this session).



### E033. External referee audit answered; Pachner 2→3 was broken at HEAD and pre-registration caught us calling it a non-repro (FIXED)

**Method.** A unified external critique (Opus/Astra/online-Qwen synthesis, `Incoming frontier model critique-advice/`) leveled 17 claims at the codebase. Each claim was checked against current HEAD with dedicated probes (`examples/critique/p1..p6`), predictions pre-registered in `docs/PREDICTIONS.md` before any run, per the audit's own item 15.

**Result (three fixes, one lesson).**
(1) **Pachner 2→3 was genuinely broken**: `apply_pachner_2_3` built three *3-vertex* tuples `((u,w,a),(u,w,b),(u,w,c))` where 4-vertex tetrahedra are required; it crashed mid-mutation after removing two tetrahedra and adding the new edge, corrupting the complex — every cascading MoveError the auditors saw follows. We had *predicted* non-reproduction; the probe found it on a fresh complex at a legal site within seconds. Correct replacement tets are (new edge) × (face EDGE): `(u,w,a,b),(u,w,b,c),(u,w,c,a)`; transactional guard added; `tests/test_pachner.py` (12 tests: legality, boundary faces+labels preserved, exact revert, sequential re-scanned stability); 72/72 Kuhn n=2 sites clean. The move had *never* been tested — a category error in our test coverage now closed.
(2) **Proposal dynamics were gauge-variant**: exhaustive sweep (1728 slice triples × 12 conjugators) shows the default `move_generators()` arm gives different reachable-orbit counts for **29.4%** of gauge-equivalent pairs — the chain does not descend to orbits, worse than the audit's example. Shipped `class_closed_generators` / `propose_edge_move(class_closed=True)`: proposals over a conjugation-closed set give **exact** reachable-orbit-set equality (0 violations), pinned by test; default arm retained as a documented hypothesis-arm.
(3) **Appearance basis-dependence confirmed**: 17.0% of single-edge verdicts flip across spanning-tree roots (their estimate: 12.4%). Shipped `Region.gauge_invariant_state()`: raw based-loop holonomies transported to one basepoint along fixed BFS paths — vertex gauge then acts by a *single* simultaneous conjugation — canonicalized lexicographically. Exact under random gauges (tested), and strictly finer than appearance's class-tuples, which collapse the 178 physical tetrahedron classes to 82.

**Lesson (formalized).** Pre-registration is not ceremony: had we "verified" the Pachner claim with our own expectations instead of predictions, we'd have read the cascading errors as harness noise a second time. A prediction that can be wrong is an instrument; one that can't is decoration.
*Evidence:* `docs/CRITIQUE_TRIAGE.md` (all 17 items); `tests/test_pachner.py`, `tests/test_gauge_canonical.py`; probes p2/p3/p4/p4b; commits `1434a1c`, `dfaab17`.

### E034. The μ quotient, settled: rigid vs pooled internal-resolution counts, and the referee's exact 6→2 reproduced (VERIFIED, convention now explicit)

**Method.** Cone v\*∂Δ³ over A₄ with declared interior-flux classes; three equivalence relations computed on the same solution sets: raw; **rigid** (apex-only gauge x_i ↦ ν⁻¹x_i, boundary labels pointwise — the `resolutions.py` convention); **pooled** (full vertex-gauge orbits of pairs (B,x): boundary vertices transform too, interiors merge across gauge copies of B). Shipped `pooled_resolution_orbits()` + module-level convention warning.

**Result.** Flat-boundary declarations: star-3 order-2 flux raw 36 → rigid **3** → pooled **1**; five-face declaration raw 72 → rigid **6** → pooled **2** — the referee's exact quoted pair, verbatim; all six faces same. Seeded declarations over all 1728 tree-gauge boundaries: rigid |I| = 4 everywhere (E030 intact), pooled 1 in 40/40 sampled. The inflation critique is a *convention hazard*, not an error in the rigid count: within one fixed-boundary fibre no merging is possible at all (any gauge preserving B pointwise acts through the apex, already quotiented); pooling across ∂B's gauge orbit is a different physical question — how many gauge-inequivalent worlds share one appearance (answer at these seeds: generically one).
**Meta-finding.** Our own probe's first rigid column silently used conjugation μ⁻¹xμ instead of left multiplication ν⁻¹x for the apex action; cross-checking against `resolution_space` caught it — E018's discipline ("verify the action you quotient by, in code") biting a third time, now on our own audit tooling. Corrected numbers come from the library itself and are pinned by slow tests including the exact-numbers case.
*Evidence:* `resolutions.py` (warning + `pooled_resolution_orbits`), `tests/test_pooled_resolutions.py`, probe p1; commit `e27fb9c`.

> **ERRATUM (Round 3, finding F1 — see E036).** The sentence "within one fixed-boundary fibre no merging is possible at all (any gauge preserving B pointwise acts through the apex, already quotiented)" is FALSE and was shipped three times. For symmetric boundaries the pointwise stabilizer of B is nontrivial: constant `lambda_i = mu` fixes an identity-labelled B label-by-label yet acts on interiors as `x_i -> nu^-1 x_i mu`. The collapse happens INSIDE the fibre: five-face declaration raw 72 -> rigid 6 -> within-fibre **2**. The rigid count stands only as a declared apparatus convention (boundary frames physical, boundary gauge forbidden by fiat). Corrected warning + `within_fibre_resolution_orbits()` in `resolutions.py`; pinned by `tests/test_pooled_resolutions.py`. Prose was not failing CI; now it does.

### E035. Two negative results worth their cost: Driver A event density is label-blind, and "d_s returns 3" was naive at toy scale (MEASURED)

**Result 1 — density carries zero matter information under appearance-only conservation.** Population-aware normalization shipped for the observer (raw per-cell counts confounded activity with shell population; corr(rho, |shell|) = +0.41 measured). But the probe found something worse than the referee's item 13: vacuum, charged-defect and neutral-lump Driver A runs on Kuhn n=2 are **bit-for-bit identical** (profiles 20.5 / 637.0 / 376.5 in all three arms). Mechanism: acceptance depends only on whether a proposed edge touches an observed surface face — not on labels, flux, or defects. The M7 "density rises around matter" claim therefore has *no empirical content* under this driver; the delay layer was already formula-prescribed (backlog item 4). Nothing deleted, nothing tuned: the gravity section is explicitly parked pending a driver whose event placement couples to curvature (Driver B churn does — residue cleanup concentrates events near flux). A clean negative result beats an unfalsified analogy.

**Result 2 — spectral dimension by matched control.** New `spectral.py` computes exact random-walk return probabilities (no RNG, kernel-pure). Kuhn balls read d_s(t=2..8) = 0.59 / 1.56 / 1.76 for n = 1/2/3 — far from 3 and rising with size. The matched control settles it: a Z³ box (6³) reads ≈ 2.0 over the same window — *any* lattice at this size does, finite-size/backtracking dominance. So "measure d_s and show it returns 3" was itself naive; the defensible pinned claim is **consistency with cubic-lattice diffusion** (Kuhn ball within tolerance of matched box; no fractal collapse), plus full P(t) curves recorded including bipartite odd-time zeros. Absolute d_s → 3 requires larger meshes or heat-kernel extrapolation, logged as follow-up.

**Methodological note.** Both results are the referee audit paying for itself: one demand we failed upward into a stronger negative result; one we answered by showing their proposed measurement could not work at our scale either.
*Evidence:* `observer.py` (rho_per_vertex), `tests/test_observer.py`, probe p6; `spectral.py`, `tests/test_spectral.py`, probe p5; commits `f968021`, `7a6087f`.

### E036. Round 3: cracks in the sentences about the repairs — F1–F8 disposition, the gluing frame escalation, and the Astra merge (FIXED / MEASURED / RETRACTED per finding)

**Method.** Panel of independent re-clones (Opus verification pass, Astra second re-review, Qwen synthesis; memo `reference/referee_synthesis/synthesized_referee_report_R2.md`). Local disposition: fix in code where the finding is a bug, fix in prose where it is justification drift, retract where the referee retracts, and keep every superseded convention as a named control arm rather than deleting it.

**F1 — stabilizer truth (FIXED; two-referee).** The E034 mechanism sentence was false: 12 constant boundary transforms fix flat B pointwise yet act nontrivially on interiors. Shipped `pointwise_stabilizer()` + `within_fibre_resolution_orbits()`; three-convention warning (rigid = apparatus convention by fiat / within-fibre = honest fixed-B gauge count / pooled = orbits of labelled pairs (B,x)). Measured and pinned: flat-B pointwise stabilizer = 12 constants (144 with apex freedom); five-face raw 72 -> rigid 6 -> within-fibre **2**; star-3 -> 1; asymmetric B has trivial stabilizer. Rigid counts remain correct AS DEFINED.

**F2 — RETRACTED by the synthesis author.** The claimed transposition in the convention warning was "a bad compression of Opus's table"; no contradiction existed between memo and triage. Recorded in `reference/referee_synthesis/README.md`. Lesson recorded: compressions of tables inside warnings are exactly where transcription errors hide — the F1 rewrite removed the numeric quote from the warning entirely, replacing it with a pointer to pinned tests.

**F4 — gluing gauge-variance (FIXED, then ESCALATED by Astra).** Round-3-local fix replaced raw apex-based flux equality with per-edge conjugacy-class equality. Astra's counterexample (`examples/critique/gluing_frame_counterexample.py`) showed classes are TOO COARSE: a single apex frame acts on ALL shared-edge fluxes simultaneously; per-edge class matching discards the cross-edge correlation (explicit A4 pair: classes match, zero common alignments exist). Final API: three named conventions — `raw` (historical control), `classes` (coarse observable), **`relational`** (default: exists ONE mu with mu^-1 fx_i mu == fy_i for all shared edges) — plus exhaustive tests in `tests/test_interaction_frames.py`, including the counting identity physical = raw x |flux-tuple orbit| and independent apex-frame invariance under the TRUE action (left multiplication; per-spoke conjugation is NOT a gauge action — an earlier regression test of ours tested the wrong transformation and passed by luck).

**New measurement from the escalation — absorption phase structure is convention-dependent.** Deterministic 18-phase sweep, probe ensemble over all 12^3 internal states: flat boundary classes {12,36,48,144,192} vs relational {12,36,48,144}; curved boundary (o2,o3,e) classes {36,108,144,192} vs relational **{36}** — under honest simultaneous-frame matching the curved-boundary cross-section is phase-INVARIANT at exactly 36 (trivial stabilizer saturates the orbit), while flat stays modulated. The ×4 curvature suppression of legacy raw counting is confirmed as an artifact (gauge-invariant conventions: flat 12 : curved 36, i.e. x3 ENHANCEMENT for this state). Duty-cycle physics survives F4 but its SHAPE belongs to the declared interaction model, not to free data.

**F5 — Pachner bookkeeping (FIXED + hardened).** 2->3 dropped the uncarried shared face (chi 1->2 on bipyramid); revert(3->2) raised "belongs to 0 tetrahedra" — undo now runs 2->3 on `move.added`. Astra's hardening imported: link-condition guards (equatorial face must not pre-exist; no faces outside the collapsing pair may ride the dropped edge), `_realized` flags and `_tet_orders` snapshotted and restored, `prune=False` discipline so revert is exact. Consolidated test asserts Euler invariance both directions, boundary-label preservation, no orphan faces, and full snapshot equality after revert.

**F6 — cavity blindness (FIXED; Astra caught a bug IN the fix).** `gauge_invariant_state()` now canonicalizes every boundary component independently under conjugation. First implementation sorted components by MEASURED holonomy before concatenating — which identified curvature-on-shell-1 with curvature-on-shell-2, a relabelling vertex gauge can never perform. Components keep deterministic min-vertex order; each is canonicalized in place. `test_curvature_cannot_swap_surface_components` fails pre-fix, passes post-fix. Completeness claim stated exactly: complete on the single-tetrahedron slice (separates 178 of 1728).

**F3/F7 — driver provenance (WIRED).** DriverA takes `model in {"relational", "legacy"}`: relational = class-closed proposals + full canonical-state preservation, now the DEFAULT; legacy reproduces v0.x generator/appearance dynamics bit-for-bit as a control arm. Every DriverRecord carries model provenance. The historical 0.325 accept-rate and E035 negative were measured under legacy semantics — they remain valid AS MEASURED; new runs must state the model. DriverB docstring now labels sigma's cycle spectrum (864x2 vs one 1728) as SCHEDULER DIAGNOSTICS of a slice coordinate system, not an object observable.

**Astra merge — particle & reaction program imported.** `curvature.py` (CurvatureState: indexed group arithmetic over the declared action H = count of nonidentity face holonomies; SupportLineage overlap tracking with explicit warning that merger/split != reaction), `kinetics.py` (Metropolis curvature driver against an external bath; boundary labels fixed, no core frozen; bookkeeping conservation, not a first law), `landscape.py` (exact small-system landscapes: plateaus, downhill exits, nonincreasing-path distances to vacuum). Four search examples + `docs/PARTICLE_PROGRAM.md`: four demonstration gates (particle candidate / fusion-fission trajectory / bound composite / chemistry) with the standing prohibition on inserting catalogues, forces, or valences into the microscopic state. Authored by Astra; imported after review, suite-verified in-tree.

**Suite:** 285 collected, 284 passed + 1 skipped (Hopf linking, documented), zero warnings after spectral.py r-string fix.
*Evidence:* `resolutions.py`, `interaction.py`, `tests/test_interaction_frames.py`, `tests/test_pooled_resolutions.py`, `moves.py`, `tests/test_pachner.py`, `region.py`, `tests/test_gauge_canonical.py`, `drivers.py`, `tests/test_drivers.py`, `docs/PARTICLE_PROGRAM.md`, `reference/astra_session/Astra_WORKING_STATE_2026-09-18.md`; R3 memo findings F1–F8.

### E037. The particle hunt, first campaign: no metastable particles under H — and a glassy surprise at n=5 (MEASURED; imported Astra P8–P11 + exact local reproduction)

**Method.** The declared reduction action H = number of curved faces on Kuhn balls with fixed identity outer boundary, class-closed proposals (all 11 nonidentity multipliers uniform), Metropolis kinetics as a declared driver hypothesis (β a dimensionless penalty, NOT temperature). P8: exhaustive landscape of the tetrahedron slice. P9: 96 runs × 10k proposals across groups/sizes/β/starts. P10: replay-audit of every screened branch — proposal age is not proper time. P11: n=4,5 horizon search. Full pre-registration and outcomes in `docs/PREDICTIONS.md` P8–P11; records under `reference/astra_session/data/`. Authored by Astra; reproduced locally.

**Result 1 (P8, HIT).** Vacuum is the ONLY closed equal-action basin on the tetrahedron seed: 178 physical states, zero nonvacuum closed plateaus, every state reaches H=0 by a nonincreasing path in ≤3 moves (Z3: ≤2). A nonzero flux or D(A₄) sector label does NOT by itself make a classical particle under this action.

**Result 2 (P9+P10, NEGATIVE — the honest kind).** 57 branches across the campaign passed a lifetime/size screen; on exhaustive local audit EVERY one had an immediate downhill move and 42/57 admitted exact one-move erasure with all other face holonomies untouched. The two long downhill endpoints reached absorbing vacuum at proposals 15,157 / 17,523. Apparent longevity was waiting-time artifact: a specific destroying move is proposed ~once per E_interior×(|G|−1) proposals. No stable particle species, no binding, under this action at n ≤ 3.

**Result 3 (P11, HIT + surprise).** Relaxation slows with mesh size AND group order — but not gently: Z3 n=5 finishes in ≤47k proposals; **A4 n=5 seeds 0 and 1 do not finish within the 200k horizon**, ending at H = 8 / 10 (from ≈1250) with exactly 2 strict-downhill exits each among 665×11 = 7,315 possible proposals (~0.03% per proposal). Endpoints are NOT local minima — no stability claim. What is measured is **non-abelian critical slowing-down without metastability**: barrier-free glassy relaxation near vacuum, the P10 waiting-time mechanism operating at scale, with A4 (nontrivial conjugacy structure) orders of magnitude slower than Z3 at identical geometry.

**Reproduction — FULL CAMPAIGN.** All 12 P11 runs reproduce bit-for-bit in this tree (identical step counts, endpoints, audits; `reference/astra_session/data/scale_runs_reproduction_local.json`), and local reruns of `particle_search.py` + `particle_candidate_audit.py` regenerate landscape.json, runs.json and candidate_audit.json SEMANTICALLY IDENTICAL to Astra's archived records (byte differences are line-ending only). The entire P8–P11 campaign is cross-checkout reproducible from deterministic seeded streams: two independent checkouts, same numbers.

**Interpretation discipline.** These are NO-results for particles-as-action-minima under one declared action. They do NOT exclude: persistence under finite-β detailed-balance dynamics with proper-time clocks; knot/link-protected sectors (Layer-2 brief: flux-string loops, not face clusters); actions with different null structure; or boundary-condition-coupled stability. The glass finding does suggest where to look next: A4's destroying-move dilution is a CONJUGACY-class phenomenon — the same algebra that makes charge also makes rare-decay. Matter, if it comes, will hide in the ratio of barrier-free trap depth to proposal measure, not in energy minima.
*Evidence:* `docs/PREDICTIONS.md` P8–P11 (verbatim pre-registrations + outcomes); `reference/astra_session/data/{landscape,runs,candidate_audit,scale_runs}.json`; `examples/particle_{search,scale_search,candidate_audit}.py`; reproduction log `scale_rerun.log`.

### E038. Both large-mesh survivors have two-move decay certificates (2026-09-19, Codex)

**Question.** P11 showed immediate downhill exits at both A4 n=5 endpoints,
but that alone did not demonstrate a nonincreasing route all the way to vacuum.
P12 registered that stronger test before execution, keeping the archived labels,
action, interior-edge proposal set, and exact outer boundary unchanged.

**Method.** `decay.py` searches raw equal-action label states breadth-first for
a downhill exit and repeats at the lower action. Each plateau has a 1000-state
discovery budget; a cutoff is reported separately from an exhausted closed
plateau. Successful descent can repeat at most H(initial) times. This is a
certificate-finding algorithm, not a new physical driver or a clock. It does
not identify states by gauge representatives during exploration.

**Result.** Seed 0: H=8 -> 4 -> 0. Seed 1: H=10 -> 6 -> 0. Each certificate
uses just two strictly downhill moves and no plateau wandering. Independent
full holonomy recomputation checks each action change; all boundary labels stay
fixed; inverse replay returns every edge label exactly; transporting each right
multiplier by the target-vertex gauge transformation reproduces the same action
sequence. The machine-readable artifact includes initial labels, edge and group
ordering, moves, search accounting, and forward action sequence.

**Scope.** These two configurations have a constructive zero-action-barrier
route to flat vacuum. Flat does not require every raw edge label to be identity.
The existence certificate says nothing about sampled rates, a proper-time clock,
or other configurations. Nuclei, atoms, chemical bonds and bulk point fermions
remain unestablished. Category-level exchange signs are not a demonstration of
point-fermion exchange in the 3D solver.

**Interpretation correction to E037 (history retained).** Neither a critical
point nor a critical exponent was measured, so "critical slowing-down" is too
strong. Likewise, the proposed conjugacy-class explanation and prediction about
where matter "will hide" are hypotheses, not results. Supported: rare destroying
proposals can accompany long proposal-time survival despite a two-move downhill
route to vacuum. The next particle gate is whether a proposed topological
obstruction is actually preserved by all permitted rewrites, including junctions
and reconnections; it cannot be inferred from a knotted rendering alone.

*Evidence:* `examples/particle_decay_certificates.py`;
`reference/astra_session/data/decay_certificates.json`; `tests/test_decay.py`.

**Validation.** Full regression run: 288 passed, 1 skipped, 3 renderer fixture
errors (Windows temp-directory permissions). The three renderer tests passed on
the authorized rerun outside the sandbox with a fresh workspace basetemp. The
targeted decay/driver run passed all 34 tests, including the newly added purity
guard for `decay.py` (added after the full run collected tests). Thus 292 distinct
tests passed across these runs; one existing test remains skipped. No failed
assertion was suppressed or changed to obtain this result.

### E039. Linked flux loops merge under the permitted rewrites (2026-09-19, Codex)

**Prerequisites.** Inspection found that linking-number signs omitted the
over/under factor; the skipped Hopf test's diagnosis as a projection problem
was incomplete. Exact rational signed crossings now replace that measurement,
with explicit projection-degeneracy failures/retries. Hopf, unlink, reflection,
orientation, subdivision and multiple-view controls pass. The old loop
classifier also accepted some boundary-open arcs: requiring two incident tets
per curved face fixes this. Actual cyclic adjacency, not sorted support, now
determines the PL dual embedding. These fixes do not validate all single-knot
heuristics or establish a correspondence with the category's braiding operators.

**P13 registered test.** The specified two-disk fixture on Kuhn n=8 produces
two disjoint dual loops of lengths 52,46 and |Lk|=1, in Z3 and its declared A4
order-3 subgroup lift. These are prepared test configurations, not spontaneous
emergence. The 32-state-per-plateau search makes three moves, H=98,98,98,96,
retaining |Lk|=1, then exhausts its budget. This remains an inconclusive outcome.

**P13b registered follow-up.** All 6,064 / 33,352 initial proposals (Z3 / A4)
were checked for support-domain changes. Each group has eight nonincreasing
proposals, all remaining two loops. No one-step nonincreasing domain escape
appears at this initial state; junction-creating uphill moves do exist.

The constructive ascending-edge-order erasure path tells a different multi-step
story: at step 37 it merges both loops into a junction (H=86), then one loop at
step 38 (H=84), with no preceding action increase. Thus a linked loop pair is
NOT protected from merger even by the downhill-or-equal move condition. The
full 140-move route has one uphill step (84 -> 85 at step 40), returns to two
loops with Lk=0 at step 52 (H=80), and reaches flat vacuum. It never exceeds the
initial H=98. Necessity of the +1 step is unproved. Linking is undefined, not
zero, on junction/single-loop states; Lk=0 alone is not a general unlink proof.

Every path has independent full-holonomy, boundary, inverse, and transported
gauge-witness checks. Nonincreasing merger prefixes are also checked using the
P12 decay verifier. Z3 and A4 agree on the paths because their fixture labels
and erasure moves lie in the same cyclic subgroup; the A4 census additionally
tests multipliers outside it. No intrinsically non-abelian stability is inferred.

**Exact scope theorem.** Under all nonidentity interior-edge multipliers, any
two assignments with identical boundary labels connect by setting each differing
edge a to b with multiplier a^-1 b. This forbids nonconstant invariants of ALL
these moves on a fixed-boundary label space. It does not prove connectivity of
the nonincreasing graph or exclude metastability. A frozen extra probe, a
no-reconnection rule, or a different action is a different declared model.

**Interpretation.** There are now actual linked flux structures and reproducible
merger/split/erasure witnesses, but no stable particles, nuclear reactions, atoms,
or chemistry. The next gate is an energetic/dynamical stability argument, not
the assertion that an embedded knot must survive arbitrary permitted rewrites.

*Evidence:* `docs/TOPOLOGY_AUDIT.md` (proof, controls and complete scope);
`examples/topology_audit.py`, `topology_rewrite_audit.py`,
`topology_audit_graphics.py`; `reference/astra_session/data/topology*_audit.json`;
`out/topology_audit.png`; `tests/test_topology_audit.py`, `test_linking.py`,
`test_knots.py`, `test_strings.py`, `test_rewrites.py`.

**Regression consequence and validation.** The full run gave 307 passes and
one failure: `test_vertex_star_order3_seeds_closed_loops` had codified the false
n=1 closure claim. Explicit incidence enumeration found two boundary faces in
each of the six nontrivial vertex-star supports. The corrected eight-vertex arc
test and the existing n=2 closed-loop test both pass. Dated E026/E027 corrections
above preserve the mistake and narrow the interpretation; no detector guard was
weakened to retain the old result. All 49 targeted checks passed after that
correction (flux loops, exact linking, strings, knots, drivers). Earlier all 52
targeted topology/rewrite checks passed. Across the full run and targeted
correction, all 308 current tests have passed; there are no skipped tests.
The full run used a fresh workspace basetemp outside the sandbox because of the
previously diagnosed Windows pytest temporary-directory permission problem.

### E040. The P13b uphill step was an ordering artifact: abelian linked loops erase with zero barrier (2026-09-19; run by Astra/Codex, reproduced and recorded by Opus)

**Question (P14, registered before running).** Is the single +1 step at move 40 of
the P13b erasure necessary? Take steps 33–48 and search every ordering of those
16 distinct-edge rewrites, keeping all other steps fixed.

**Result.** HIT in Z3 and A4: `path_order.nonincreasing_order` finds an ordering
after 291 discovered subset states. The only change is to postpone original step
38 (86 -> 84) until after steps 39–40. The complete 140-move path is then
nonincreasing, H=98 -> 0. It passes full-holonomy, boundary, inverse and gauge-transport
checks. A fresh rerun in a separate Linux checkout reproduces the archived
JSON semantically identically; only the path separator differs. The P15 greedy scheduler
(E041) independently finds a different nonincreasing erasure of the same labels.
**Scope:** the prepared abelian linked pair has no action barrier to complete
erasure under H. This says nothing about rates. Linking of commuting fluxes gives
no energetic protection.
*Evidence:* `examples/topology_decay_order.py`; `src/constraintnet/path_order.py`;
`tests/test_path_order.py`; `tests/test_link_order_and_noncommuting.py::test_p14_*`;
`reference/astra_session/data/topology_decay_order.json`.

### E041. Non-commuting linked fluxes: topology forces a tether; the action still gives no barrier (2026-09-19, Opus)

**Why this experiment.** Every earlier link test lived in a cyclic subgroup, so Z3
and A4 agreed by construction. The memo's "knots protect matter" thesis has not
yet been tested with the non-abelian structure that motivates A4. For line
defects with non-commuting fluxes, the continuum rule (Poenaru–Toulouse) is that
they cannot cross freely: a connecting string with commutator flux must form.

**Fixture (P15, prepared).** Same Kuhn n=8 ball and P13 disks; disk 1 carries a,
disk 2 carries b; labels are ordered products along each edge. Four edges pass
exactly through the disk-intersection line. Their factor order was fixed by a
declared amendment before any measurement (disk 1 first), and the reverse
convention runs as a control.

**Derived and confirmed.** The complement of a Hopf link has fundamental group Z^2,
so a two-loop Hopf state must have commuting meridian holonomies. Measured: the
commuting arms (C0 = the P13 labels, C1 = distinct V4 fluxes) give two loops,
|Lk|=1, H=98, and commuting based meridians. The non-commuting arms (N1: order 3 with
order 3; N2: V4 with order 3) give ONE junction component, H=103: loops plus a
5-face V4 tether along the intersection arc. The tie control gives a 6-face tether
(H=104) and the same topology. **Non-abelian linking is visible in the labels as
extra, unavoidable flux.** This is the first result in the program where Z3 and A4
necessarily differ at the level of topology.

**Dynamics.** One-edge census: in N1/N2, all 33,352 single proposals keep the one
junction component (10 nonincreasing), so no single move removes the tether.
C1 matches the P13b A4 census exactly. Plateau searches (32/256 states) all hit their budgets, which is
inconclusive. The per-edge "set to identity" move set, ordered by a greedy
scheduler, gives a fully nonincreasing 140-move path to flat vacuum in all six
runs. In the N arms the tether survives until step 52 (H=80). On that move the
structure becomes two loops with Lk=0 and non-commuting meridians, which is legal
because an unlinked complement has a free fundamental group. Tether and linking disappear on the
same move: the tether shortens and pulls the loops through each other, which is the
continuum expectation. Verified by holonomy, boundary, inverse, P12-verifier and
gauge-transport replay.

**Interpretation (bounded).** After P8–P15, every tested structure under H has a
zero-barrier route to vacuum when the outer boundary is identity. That includes
clusters, glassy endpoints, abelian links and tethered non-abelian links. H behaves
as a uniform string tension on closed flux networks, and tension resolves every
entanglement tried so far. Topology here constrains WHICH intermediate structures
occur (the tether); it has not constrained WHETHER decay occurs. This is not a
proof for all fixtures. It does say where protection cannot come from under this
action: closed, contractible flux networks in a flat-bounded ball. The remaining
candidates are listed in `reference/opus_session/WORKING_STATE_2026-09-19.md`:
Gauss-law point charges, non-contractible or boundary-anchored flux, and a changed
action or measure. Each would be a declared model change that needs its own
pre-registration.
*Evidence:* `docs/PREDICTIONS.md` P15; `examples/noncommuting_link_audit.py`,
`examples/noncommuting_link_graphics.py`; `reference/opus_session/data/noncommuting_link_audit.json`;
`out/p15_noncommuting_links.png`; `tests/test_link_order_and_noncommuting.py`.

### E042. The bag test: the model has tension but no pressure (2026-09-19, Opus)

**Why.** The user proposed a picture: vacuum is the cancelling interference of the
"wakes" of implications, and a particle is a pressurised bubble in it. A bubble
is stable only if an outward push balances the inward surface tension. So before
building wakes we asked the cheap question (P16, registered first): does the
CURRENT model contain any interior quantity that grows with volume and differs
between inside and outside?

**Result (all predictions HIT).** A flat interior has exactly one physical filling
(Z3 n=1–3, A4 n=1–2). Raw counts equal |G|^(interior vertices), so they are pure
gauge. The smallest loop excitations always cost H=4. Their count, 3n²(n−1)
distinct supports, grows like volume. That gives a uniform loop-gas entropy at
finite β, the same inside and outside, so it pushes nothing outward. Claim 30
already rules out conserved interior content. A4 n=3 exact enumeration was
skipped: it would list 4.3e8 gauge copies.

**Interpretation.** The energy of a bubble in this model has only a surface term,
so its minimum is at zero size. That is exactly what P8–P15 observed. The
missing piece is a conserved, trapped content whose confinement energy rises as
the bubble shrinks (the bag model's quarks, a Q-ball's charge, a cavity's light).
`docs/BAG_PICTURE.md` records the picture, the precedents, the job specification
for any cone/wake extension, a correction on "twisted" theories and fermions,
and the user's "cannot choose, so takes every path" idea (sum over paths) with
its amplitude-vs-probability caveat.
*Evidence:* `docs/PREDICTIONS.md` P16; `examples/bag_test.py`;
`reference/opus_session/data/bag_test.json`; `tests/test_bag_test.py`.

### E043. Probabilities always escape; amplitudes trap by interference, and fractal depth makes leaks vanish doubly-exponentially (2026-09-19, Opus)

**Question (P17, derived before running).** The user's picture: a particle is a
region where an implication wanders forever along an ergodic, fractal route
because every way out cancels. Is that possible with probability weights, with
amplitude weights, or with neither? Same generator (graph Laplacian), same exit;
only the factor i differs.

**Derived (docs/TRAPPING.md).** T1: probabilities escape from every start on every
connected geometry (positive-definite generator). T3: amplitude survival tends
exactly to ||P_D psi0||^2, where D is spanned by the eigenmodes that vanish at
the exit. T4/T5: degeneracy and exit-fixing symmetry force such modes. T6
(perturbative): broken symmetry gives decay at rate ~eps^2.

**Measured.** All verified on 12 graphs, including the project's own Kuhn mesh
(44 of 64 modes dark). An explicit-lead control and exact integer
symmetry-breaking were run as well; see the PREDICTIONS P17 outcome. Two
unregistered observations on the Sierpinski gasket: the dark fraction climbs
toward 1 with depth (non-dark dimension 3·2^(k-1)+1), and the slowest leak of the
non-dark states falls doubly-exponentially, down to 1.5e-31 at level 6
(150-digit spectra).

**Interpretation (bounded).** This settles the earlier open point on the
amplitude side. Trapping requires amplitudes, because probability weights provably
cannot trap. So stable matter in this picture needs amplitude weights. That
motivates, but does not derive, the amplitude/Born layer (CLAIMS row 16). Both
of the user's intuitions receive exact support on supplied geometries:
"geometry that lines up" (symmetry/degeneracy) traps permanently, and "finite
depth" gives finite but rapidly exploding lifetimes. Fractality is not the
mechanism; symmetry, degeneracy and self-similar bottlenecks are. Open: whether
the model's own record can build such a trap around the implication that made
it (self-confinement), which is the step from trapped light to matter.
*Evidence:* `docs/TRAPPING.md`; `examples/trapping_test.py`,
`trapping_depth_rates.py`, `trapping_graphics.py`; `tests/test_trapping.py`;
`reference/opus_session/data/trapping_*.json`; `out/p17_trapping.png`.

### E044. The project's mesh is secretly BCC: round, sharp light fronts in its own metric, and mass makes a wake (2026-09-19, Opus)

**Why.** The integrated working statement (`docs/WORKING_STATEMENT.md`, v4)
adopts "reading 1": influence spreads isotropically at one speed, so the
corollary cone is the light cone. Before building on it, P18 asked whether the
project's own mesh can carry such fronts at all.

**Derived first (docs/PROPAGATION.md).**
- **The preferred axis is only apparent.** In rendering coordinates the Kuhn mesh
  has a preferred (1,1,1) axis, with a speed ratio of 2, and no nonnegative
  reweighting removes it. But coordinates are rendering only.
- **The emergent metric is BCC.** In the metric defined by the dynamics, the
  mesh's vertex star is exactly the body-centred-cubic tetrahedral star. The
  two edge classes are told apart purely combinatorially, by link-ring size 6
  or 4, the same numbers that appeared as H = 6 or 4 in P16.
- **Quartic isotropy.** Weighting ring-4 edges by ½ makes the dispersion
  isotropic through fourth order.
- **Real waves trap too.** Classical real waves obey the P17 trapping theorem
  (T3′). Trapping needs signed interference, not complex numbers as such.

**Measured.** Everything registered was confirmed except N3's front-radius
test, which sits below measurement resolution; the exact symbol test confirms
N3 directly. Highlights:
- 3D massless fronts are sharp (interior share ≤ 3e-7); the 2D control keeps a
  1.8% tail, matching the continuum.
- A mass term fills the cone interior, converging to the continuum (39%
  at mσ = 1).
- The damped real wave keeps exactly the dark-mode energy.

One wording error in D1 (plane-wave versus front speed) was caught by an
unregistered readout and amended in place, with a note.

**Interpretation (bounded).** Clause 3 of the working statement holds on the
project's mesh for scalar waves: the light cone is round in the emergent metric,
fronts are sharp in 3D, and mass leaves a wake. The mesh's "true" geometry is
BCC, with a combinatorial weighting (by ring size) that improves isotropy.
Checks A–C are unchanged (spin, doubling, unitarity), and K (self-confinement)
remains the central open problem.
*Evidence:* `docs/PROPAGATION.md`; `examples/propagation_test.py`,
`propagation_graphics.py`; `tests/test_propagation.py`;
`reference/opus_session/data/propagation_test.json`; `out/p18_propagation.png`.

### E045. Framing reconciled; the v4 dynamics designed and registered (2026-09-19, Opus with the user)

**Reconciliation.** The original framing's "persistent topological defects are
matter" is marked SUPERSEDED on the evidence of P8–P16. "Rewrite cost is mass"
is RETAINED in the user's precise form: inertial mass is the rewrite cost of
translating a structure, equivalently its maintenance cost in implication
steps relative to free passage (the light-clock argument). The curvature-count
and word-metric readings become the pre-v4 control arm. Edits:
- README preface (original paragraph kept)
- CLAIMS framing note
- MEMO_PATCHES P11
- ELECTRON_TARGET W0/W6
- PARTICLE_PROGRAM
- WORKING_STATEMENT clauses 6 and 12

**Design.** `docs/DYNAMICS_DESIGN.md` registers v4.0: a gauge-covariant
weighted-reflection (Szegedy) walk.
- Amplitudes live on directed edges with an internal space carrying a
  representation of A4; labels transport orientation.
- One hop per tick; ring-size weights; no mass parameter.
- Labels form a fixed prepared record for now; dynamical labels are v4.1.

The design checks passed before any physics run:
- exact unitarity (total implication conserved);
- gauge covariance;
- the Szegedy identity (spectrum = e^{±i arccos λ} of the classical walk, plus
  flat bands of multiplicity arcs − 2V);
- linear, emergent-isotropic massless dispersion;
- no doubled light cone, since the minimum of λ over the Brillouin zone is
  −5/11 (the mesh has triangles).

**Two watch items.**
- Flat bands: non-translating circulation, 12 of 14 arc dimensions per vertex.
  They are not particle candidates.
- The spin-½ doubling question (B) is untouched.

The physics tests P19a–e are registered and not run. P19e asks whether a
prepared flux record traps implication beyond the vacuum control. No
direction is predicted.
*Evidence:* `docs/DYNAMICS_DESIGN.md`; `examples/v4_design_checks.py`;
`tests/test_v4_design.py`; `reference/opus_session/data/v4_design_checks.json`.

### E046. The v4.0 walk works as a light engine, but a frozen record traps nothing (2026-09-19, Opus)

P19 ran on the registered design, with two amendments made before any code:
realisations fixed in advance, and the closed variant defined as the induced
subgraph.

**The engine passes every structural test.**
- **Exact conservation and covariance:** implication is conserved exactly and
  the walk is gauge-covariant.
- **Dispersion:** exactly the Szegedy form, with long-wave speed sqrt(2/11) and
  quartic-isotropic under the ring weighting.
- **Relational light cone:** round to 0.3% over 60 directions on a 120³ torus,
  with weight outside it falling exponentially. No lattice mode outruns the
  long-wave speed.
- **Holonomy:** non-abelian interference is exact, matching ½(1 + χ₃/3).

One registered clause (P19d "contrast") was mis-stated at registration. It is
recorded as such; the underlying formula is confirmed. An implementation bug
(a wrap-around window in P19c) was found, fixed and rerun, with the buggy
numbers superseded.

**The physics answer is negative.** Prepared flux structures (single loop,
linked, tethered) held fixed do not trap implication. Exact spectra show the
same trapped dimension as vacuum, minus two. Packets on the flux escape to
1e-32. The only trapped states anywhere are compact cycle states that never
translate (derived result DF). They have no finite inertia, so they are not
matter under the M1 definition.

**Interpretation.** The frozen record of the old picture (defects) and the
light of the new one (walk) do not, combined, make matter. What remains is the
feedback: implication must reshape the record that guides it, which is item K,
self-confinement. This is where the working statement locates matter anyway
("the record built by implications forms the cancelling structure that then
traps them"). v4.1 needs a reversible, gauge-covariant, conserving rule for
how passing implication changes labels. That design needs the user's
philosophical input: are labels separate from the implications that cross
them, or the same thing?
*Evidence:* `src/constraintnet/walk.py`; `examples/p19_walk.py`;
`reference/opus_session/data/p19_{a,b,c,d,e_exact,e_time}.json`;
`tests/test_walk.py`.

### E047. A responsive record, built and then retired: chop must cost implication (2026-09-19, Opus with the user)

**Built from the user's answers.**
- Free light reads the chop.
- Contained light pivots at loci set by the geometry, in steps. The dihedral
  angles are exactly 60° on ring-6 edges and 90° on ring-4 edges, checked.
- The pivot must travel with the structure, not be pinned in all six
  degrees of freedom.

**Rule (v4.1-sc).** Circulation around an edge writes a quantised 120° chop,
oriented by the local spin. `RecordWalk` implements it and is exactly
reversible: 50 ticks, 5,850 chops, restored to 1e-15 with labels bit for bit.

**Why it was retired before any valid run.** The user objected that chop costs
the wave nothing, and the objection is correct. Norm is conserved, but the
evolution operator changes with the record, so the wave's energy isn't. A
record must hold, and cost, implication. P20 was withdrawn; its one launch
had also hit a NaN preparation bug, since fixed. Energy-accounted options
(A: quantum record; B: ledger, curved face = ε of stored implication;
C: no separate record) are laid out in `DYNAMICS_DESIGN.md` §9 for decision.

### E048. Option A at small scale: a quantum record in a lossless box (2026-09-19, Opus with the user)

**Choice.** The user chose to try A directly: "implement A on a small scale on one or three of
our interesting geometries … reflective boundary box that echoes losslessly". The conversation
had also concluded that B, done reversibly, becomes A, and that the geometric face cost is the
Wilson form 1 − χ₃/3.

**Build.** `QuantumRecordWalk` (`src/constraintnet/qrecord.py`):
- 3 quantum edges (1728 record states); everything else frozen flat.
- The walk is controlled on the record; the record has an electric term (A4 Laplacian on the
  order-3 class) and a magnetic term (Wilson).
- One fixed unitary, so there is nothing to account by hand.
- A closed n = 6 Kuhn box: every arc has its reverse, so the walls echo losslessly.

**Registered and run as P21:** three geometries (pivot vortex, DF loop, free flash), a 6-point
coupling grid, and quenched-chop controls.

**What we learned.**
- The accounting is exact.
- Free light passes a weakly fluctuating quantum vacuum almost untouched, and the energy it
  deposits is ∝ λ_E² and levels off. A strongly fluctuating vacuum heats up under light.
- The trapped DF loop is the structure the record interacts with. Dynamic ≫ quenched, so it
  is response, not noise. At moderate coupling the loop stays in place while its internal state
  beats coherently with the record (overlap 1 → 0.34 → 0.84).
- The pivot vortex is not bound, which was the prior.
- One correction to my own prior: I expected "leak" to mean escape. At moderate coupling it
  mostly means rotation in place.

*Evidence:* `examples/p21_quantum_record.py`; `reference/opus_session/data/p21_*.json`;
`tests/test_qrecord.py`; `out/p21_quantum_record.png`.

### E049. Freeze-out: the hot record is opaque but does not cool (2026-09-20, Opus with the user)

**Question.** The user asked whether "the vacuum wasn't always calm" lines up with the model.
Conversation answer: qualitatively yes. The cosmological order is formation by cooling, with light
going free at decoupling, and P21 already showed loops surviving only in calm chop. Two
distinctions:
- "hot" should be a *state* above the vacuum, with the rule fixed;
- a closed reversible box cannot cool, so a cooling channel is needed.

**Test (P22).** Open walls, a hot record, one flash of light.

**Result.**
- **Opacity, not formation.** The dynamic hot record holds light about 30–100× longer than frozen
  chop of the same statistics, and releases it as a power law. The flat vacuum lets light go at
  once. Retained light ∝ hot fraction, with no threshold.
- **No cooling:** the record's energy dwarfs what the light can carry.

**Priors P22-3 and P22-4 failed on direction.** I expected trapping to prefer calm; it prefers hot.
The registered surprise criterion was met, but the interpretation is lingering (slow release), not
binding.

**Next.** Cooling needs radiation to dominate the energy budget, or a growing or expanding mesh.
*Evidence:* `examples/p22_freezeout.py`, `reference/opus_session/data/p22_*.json`,
`out/p22_freezeout.png`.

### E050. Radiative cooling: light has a temperature only when it is narrow and low (2026-09-20, Opus)

**Plan.** The user set the order: radiative, then expanding, then both.

**P23: a flood of flashes.** Built as a quantum-trajectory unravelling of the exact record channel:
- escaped light is detected, the record keeps its conditional state, and the next flash arrives;
- exact per-flash drifts come from a ladder of record states.

**Three findings in sequence, each registered before it was run:**
1. **Folding.** The earlier couplings (λ_B = 2) put the record's quasi-energy past π per flip.
   Light then heats it to infinite temperature whatever the light is, so the λ_B = 2 trajectories
   were stopped.
2. **Broad light still heats**, even with the record unfolded (0.1, 0.1).
3. **Narrow light cools.** Light from the lowest positive band holds the record at half its hot
   energy. My prior, that light's symmetric band makes any light infinitely hot, failed; the
   failure was informative.

**P24a: the redshift proxy.** Bigger boxes allow lower bands:
- E*/E_hot = 0.51, 0.22, 0.14 at ω₀ = 0.52, 0.40, 0.33;
- magnetic excitations freeze out once ω₀ drops below their gap;
- a cooler record is more transparent.

This is the cosmological sequence in miniature: redshift → freeze-out → transparency.

**Not yet shown:**
- loops forming;
- the record reaching its true vacuum (the vacuum population still drops slightly, since
  electric excitations are below ω₀).

**Needed next:** a growth or expansion rule, which is the user's call (axiom-level).
*Evidence:* `examples/p23_radiative.py`, `examples/p23_graphics.py`, `reference/opus_session/data/p23_*`,
`p24a_*`, `out/p23_p24a_radiative.png`.

### E051. Seeding patterns in a compatible cooled bath (2026-09-20, Opus with the user)

**The user's proposal.**
- Extract the statistics of the cooled vacuum near where matter would form.
- Preseed our patterns in statistically equivalent noise, back-calculated from the matter so the
  two have compatible provenance.
- The clarification: "we can't have the particle instantiated in an incompatible bath … 'with
  enough noise this happened somewhere', not a rigorous reproduction of the Big Bang. Whether it
  *continues* to persist is another question."

**Built (P25).**
- The bath is a Gibbs sample of the record at the P24a freeze-out energy.
- The pattern is seeded per record branch in that branch's compatible form.
- Two loops: 60° pivots (ring-6) and 90° pivots (ring-4).

**Result.**
- Compatible seeding removes the birth shock.
- A frozen bath keeps the pattern exactly.
- A moving bath erodes it slowly (about 15 % in 600 ticks), all of it from the record's motion.
- 90° loops persist better.
- The bath's own provenance check failed: the Gibbs form is not shown to be stationary under the
  light that produced it.

**Consequence.** Matter, if it exists here, must be a *joint* state that co-moves with its record:
a dressed loop. Next, find it. Its record statistics would then be the back-calculated bath, which
is the user's provenance condition made exact.
*Evidence:* `examples/p25_seeded.py`, `reference/opus_session/data/p25_*.json`, `out/p25_seeded.png`.

### E052. Resumption and phase-resolved dressed-loop search (2026-09-20, Astra)

Read Opus's handoff through P25; preserved the work and user-supplied correction
that Astra may commit. Installed missing SciPy locally, declared the `quantum`
dependency extra, and verified the full existing suite: **356 passed in 400.03 s**.
Four additional phase-filter and embedding tests passed separately. Commit
`29a2f51` preserves P19–P25 plus the P26 executable and preregistration before any
P26 measurement.

**Analytic correction.** A persistent ray may have any eigenphase. Unphased
averaging can remove it. The exact Cesaro telescoping identity gives a residual
bound with the filtered norm in the denominator; merely averaging longer is not
an eigenstate certificate. A stationary joint record also need not be stationary
under the separate cooling channel. DYNAMICS_DESIGN section 14 states the scope.

**P26 measured.** Compatible L4 loop, three quantum edges, (0.1,0.1), Gibbs fraction
0.14 and seed 1, in closed boxes n=5 and n=6. Fixed phases zero and the isolated
record vacuum; windows 64,128,256; then 128 open-wall ticks for both filters and
the raw seed. No dynamics changed.

The vacuum phase (-0.289325 rad/tick) retains about 59% filtered weight and gives
98.04–99.68% normalized loop weight. Full-U residuals improve about 55-fold to
0.0056–0.0057. Open-release loop loss is reduced by about 69% and 76%, with escape
accounting accurate to 4.14e-14. All diagnostic priors pass, but the 1e-8 exact
eigenstate gate fails. Zero-phase filtering retains only about 0.012% and does not
produce a near-eigenstate.

**Interpretation limit.** The selected record is 97.8–99.5% in its isolated vacuum
mode. This can explain improvement over a noisy seed without self-confinement.
The decoupled flat-loop control is already exactly persistent. The next comparison
must include an unfiltered vacuum seed; longer or refined eigenstate searches
must retain full-U residual and boundary checks. A current/orientation measurement
is independently necessary before interpreting a localized dark mode as the
Williamson–van der Mark circulation. The expansion decision remains open.

*Evidence:* `examples/p26_dressed.py`, `examples/p26_summary.py`,
`reference/astra_session/data/p26_{dressed_n5,dressed_n6,summary}.json`,
`tests/test_phase_filter.py`, figure `out/p26_dressed.png`.

### E053. P27 written up: the dressed loop is just a calm loop, and compact states cannot circulate (2026-09-20; Astra's run, written up by Opus)

Astra registered and ran P27, then stopped before the write-up. Recomputed from the archived data.

**Result.**
- The P26 phase-filtered candidate loses *more* weight on release than a plain calm seed
  (ratio 1.09 at n = 5, 1.23 at n = 6), and overlaps those seeds at 0.94–0.98. P26's advantage
  over the noisy seed was calm selection, as Astra suspected in E052.
- Neither calm seed is a near-eigenray (residuals 0.074, 0.126).
- No directed current anywhere: 1e-12 initially, ≤ 1e-6 integrated over 128 ticks.

**The structural point** is Astra's theorem (§15): a state confined strictly to a loop, with exits
available, has exactly zero current. So "matter is trapped circulation" fails in its strict form.
Three ways out remain: support outside the loop (a field tail), a time-dependent superposition
rather than one eigenray, or circulation carried by an internal variable that probability flow
cannot see.

The user's reading points at the third: the several internal states can be read either as a
wavefunction over them or as a constant, invisible transition between them. That is the subject of
P28.

*Evidence:* `reference/astra_session/data/p27_vacuum_n{5,6}.json`, `examples/p27_summary.py`,
`out/p27_vacuum.png`.

### E054. Compact loops: two phases, no current, and a two-traversal internal return (2026-09-20, Opus with the user)

**The user's question,** after P27 closed off circulation: can the several internal states be read
either as a wavefunction over them, or as a constant invisible transition between them?

**Answer, derived and then checked.** Both, and the model pins it down:
- a compact loop state forces the coin to −1, amplitudes scaling as 1/√weight (so triangles work
  too, which P19 had missed);
- only two walk phases exist, 0 and π;
- existence is H a₀ = e^{iLθ} a₀, so on odd loops θ = π needs an order-2 holonomy;
- the 0/π superposition is exactly 2-periodic: the invisible transition, made exact.

**The negative that came with it.** The superposition carries no current *at any tick*, not merely
on average. Forward and backward arcs always hold equal weight; it is a standing wave. So the
no-current result now covers time-dependent compact states as well.

**The positive.** On an odd loop with an order-2 holonomy, the internal vector returns with −1 per
traversal: two traversals to come back, invisible to any probability measure. That is the first
structure in this project with the shape the electron target wants, and it is kinematic, not a spin
claim.

**Next.** Directed transport requires leaving the strictly compact class: a tail or surrounding
field. That is also what the §15 scope note said. The expansion rule is still the user's open call.
*Evidence:* `examples/p28_compact.py`, `reference/opus_session/data/p28_compact.json`.

### E055. The tail, time reversal, and why matter may need spin-½ (2026-09-20, Opus with the user)

**The user's choice:** give the candidate a tail. Real matter's central disturbance is much smaller
than its field, and the field is part of matter's imposition.

**First finding (P29a).** My per-eigenvector current readout was ill-posed inside degenerate
eigenspaces; amended mid-stream and re-run with a per-eigenspace maximisation. The real structure
underneath: the walk has an antiunitary K with K U = U⁻¹ K and **K² = +1**, so every eigenspace has
a current-free basis. With identity labels, symmetry supplies degeneracy and circulation is easy
(bias 0.65). With random labels, the spectrum splits almost completely and **no** stationary state
circulates (≤ 1.3e-11).

**Second finding (P29b).** Lifting the internal space to the 2-dim spinor representation of 2T
gives K_s² = −1. Kramers degeneracy then survives disorder, and circulation returns at bias
0.76–0.93 in every draw. The circulating states are delocalised: ≤ 8.5 % of the weight on the loop,
≤ 16 % of the current on its edges.

**Reading.** Stationary circulation in a disordered vacuum requires the spin-½ lift, and what
circulates is the field, not the core. That is the user's picture arrived at from the other end,
and it promotes working-statement item A from optional to required.

**Still owed:** an axiom-level reason for 2T labels; self-binding (these are box eigenstates); and
the expansion rule.
*Evidence:* `examples/p29_tail.py`, `examples/p29b_spin.py`,
`reference/opus_session/data/p29a_tail_v2.json`, `p29b_spin.json`.

### E056. How hot was that vacuum? (2026-09-20, Opus with the user)

**The user's question:** how much energy is the "disordered vacuum" of P29 carrying? With enough
ambient churn anything falls apart or comes together, and our objects are tiny.

**Calibration.** P29's random labels curve 92 % of faces at mean Wilson cost 1.0: it is the
infinite-temperature record, not a vacuum. The cooled vacua of P23/P24a sit at 0.14–0.51 of that.

**Sweep (P30).** Diluting the labels gives curvature densities from 0 to 92 %.
- Without the spin lift, circulation is permanent below ~10 % curvature, survives ~100 ticks at
  25–92 %, and is not permanent above ~10 %. My registered prediction that it would die by 5 % was
  wrong; it is hardier than that.
- With the spin lift it is permanent at every level tested.
- Per-face churn energy is 0.001–0.10 rad/tick, against 0.75 rad/tick for the lowest quantum that
  fits an n = 4 box (0.33 at n = 7). Long-wavelength light is slow in lattice terms, so a real
  vacuum around a tiny structure is near the flat end of this sweep.

**Reading.** Both of the user's directions are visible in one figure: enough churn does dissolve a
circulating structure without the spin lift, and the lift is precisely what makes a structure
indifferent to its neighbourhood's temperature.
*Evidence:* `examples/p30_churn.py`, `examples/p30_graphics.py`,
`reference/opus_session/data/p30_churn.json`, `out/p30_churn.png`.

### E057. A circulating structure does no work on its vacuum (2026-09-20, Opus)

**Built:** `SpinRecordWalk` — the P21 quantum record with 2T labels (24 elements, the double cover)
and a spin-½ walker, since P29b showed circulation needs that lift. The magnetic cost uses the
spinor character, so a face carrying the central element (a 2π rotation) costs the maximum.

**Bug caught in the control.** Inside a Kramers pair the two extremes of circulation are +λ and −λ,
not flow and no-flow; the zero-current control is the time-reversal-symmetric combination. Fixed
before any result was reported.

**Result.** The circulating state and the standing state of the same family shift the record's
energy identically to within 0.25–2.5 %. The record reacts to the walker being there, not to its
flow. Neither binds: both empty an open box, as delocalised states must.

**Open:** whether Kramers protection survives a dynamic record. The antiunitary I tested left out
the label transport, so that check is void; the slow observed decay (1–9 % over 400 ticks) is
consistent with approximate protection but proves nothing.

*Evidence:* `examples/p31_selfbind.py`, `reference/opus_session/data/p31_selfbind_n{4,6}.json`.

### E058. The project's origin, and what proof theory says about it (2026-09-20, Opus with the user)

**Origin (user, recorded now as provenance):** the whole programme grew from asking *what would a
mathematical derivation look like from inside, as logic is progressively applied?*

Re-read that way, several results change meaning:
- a self-contained sub-derivation has no direction, which is precisely the compact-loop no-current
  theorem: direction requires an open dependency on the surroundings;
- a closed loop of inference can only be idempotent or sign-flipping, which is the θ ∈ {0, π}
  result, with the two-traversal return as a parity obligation;
- discreteness is the natural state (there is no half an inference), so the continuum is what needs
  explaining, not the steps.

**Literature (see RELATED_WORK):** the formal counterpart is Girard's Geometry of Interaction —
cut elimination as a token travelling a proof net, proofs as operators, with token machines,
multi-token causal versions and quantum-computation semantics already in place. Also De Raedt et
al.'s logical-inference derivations of the relativistic wave equations, and the Wolfram model.

**Two technical leads this hands us:**
1. **Non-invertible transport.** GoI's dynamic algebra is built from partial isometries (a stack
   discipline), not group elements. Astra's no-current theorem assumes invertible transport, so a
   stack-like rule is a candidate escape from the no-circulation result — and a stack *is* a
   record, which is an independent reason for the record to exist.
2. **The net is consumed.** In GoI the graph is rewritten by reduction; our mesh never changes.
   That is where the expansion rule belongs, and it suggests its form: reduction should rewrite
   mesh structure (Pachner-type moves), not merely move amplitude.

### E059. Reading the neighbours: four upgrades, one of which reframes the goal (2026-09-20, Opus)

Read the closest programmes properly (RELATED_WORK) and wrote `docs/UPGRADES_FROM_LITERATURE.md`.

1. **Kitaev's quantum double** is the same mathematical object with a finished theory attached, and
   it says matter is a **constraint defect**: a charge is a vertex where the Gauss law fails, a flux
   is a face with non-trivial holonomy, and both are gapped and topologically protected. We never
   imposed the Gauss law, and our terms are soft rather than projectors, so we have no gap. Our
   "trapped circulation" target may simply be the wrong object.
2. **Ribbon operators** create pairs at the *ends* of a string, with the string unobservable. Our
   closed loops have no ends, which is why P28 found no current and P31 found no binding. The user's
   "tail" is the string.
3. **Derrick's theorem** is the name of our P14–P16 result. Escapes: a Skyrme-type term, gauge
   fields, or time dependence. The topological-constraint route is the cheap one.
4. **Braid matter** stalled exactly where we are: states too stable to interact, a zoo without
   superselection rules, no masses. The quantum double supplies the missing rule; computed here, our
   groups would give **14 sectors for A4** and **42 for 2T**, which is a falsifiable target.

Recommended order: Gauss law and gap, then ribbon pair creation, then sector counting, and only then
back to circulation and the electron.

### E060. The obvious corrections, made (2026-09-20, Opus with the user)

**The user restated the axiom:** causality travels to local effect, and it is always travelling as a
conserved quantity; a multidimensional causal structure enumerates irreducible self-referential
links. Read literally that is a per-vertex *constraint*, which our rules never had.

**Corrected and implemented** (`defect.py`, `tests/test_defect.py`, `docs/CORRECTIONS_2026-09-20.md`):
- local conservation as the projector A_v, flatness as B_f, H = −Σ A_v − Σ B_f;
- exact projectors, exactly commuting, on Z2, Z3 and A4 patches; unique gapped ground state;
- charge = a vertex where A_v fails (a point), flux = a face where B_f fails;
- **on our own mesh**, one edge's label disturbs exactly the closed ring of faces around it, size 6
  or 4, for every interior edge. Flux is a loop; our ring structure was the flux structure all
  along, and the old "pivot edge" was a flux-loop generator.

**Consequences for the old rules:** "matter is trapped circulation" is retired (C3); a static
compact state carries no current so by the axiom it cannot be matter (C6); the missing stabiliser
that P14–P16 found (Derrick's theorem) is replaced by constraint stability rather than a force
balance (C5).

**For the dimensional step,** registered as P32-5/6: the mesh generalises to d dimensions with
labels in A_{d+1} (4D → A5, spin lift binary icosahedral), and since flux is codimension-2 while
p + q = d − 1 is needed to link, **flux links flux only in three dimensions** — charge–flux braiding
survives in all of them. That is the sharpest form yet of the user's own conjecture about why three
dimensions persist.

### E061. Newer handoff reconciled; explicit charge pairs and constraint audit (2026-09-20, Astra)

The user supplied the discussion after Opus's latest commit. The workspace now
contained P28–P31 and the uncommitted defect kernel, superseding the older handoff
through P25. Preserved the newer pending work in `e1daede`, with P32A registered
before the probe. The three original defect tests pass locally. P31's saved
campaign was preserved, not claimed as a fresh local reproduction.

**Audit:** the implemented H=-sum A-sum B is an energetic penalty on the full
edge Hilbert space, not enforcement of an A_v=1 state restriction. The old walk
already conserved probability locally; the newly added gauge constraint is a
different property. Small couplings do not imply no gap. These distinctions,
plus path/mobility and dimensional caveats, are in `DEFECT_AUDIT.md` with primary
literature links. Original wording is retained with amendments.

**P32A:** constructed 48 ordered endpoint/character preparations: Z2 and Z3 on
the tetrahedron boundary; A4 1' and 1'' on a single face. Every pair costs two
Hamiltonian units, with only its two endpoint stars violated. Direct/alternate
paths agree on the flat vacuum; one-edge continuations move endpoints; inverse
strings annihilate adjacent pairs. Algebraic errors are below 1.1e-15. These are
controlled string operations, not spontaneous or energy-isolated reactions.

**Persistence:** exact evolution from the commuting projectors matches a dense
Z2 exponential and changes each pair only by its energy phase (error below
7.2e-15). Since every local defect projector commutes with H, every defect
location stays fixed. This proves persistence in the supplied Hamiltonian and
also shows that autonomous propagation is absent.

**Hard-constraint check:** projecting either charged endpoint gives zero.
An all-identity record basis vector is flat but has <A_v>=1/|G|. Thus P32-3
needs an open-system map and P32-4 needs an explicit old-to-new-state embedding.
Neither was silently imported from the wave engine. No dimensional experiment
or nuclear/atomic/fermionic claim was made.

Next work should specify admissible charge transport and its conservation rules,
then probe mobile configurations and interactions. A gap or an immobile eigenstate
alone is not the requested moving matter. Evidence: `defect_ops.py`,
`examples/p32_defects.py`, `reference/astra_session/data/p32a_defects.json`,
`tests/test_defect_ops.py`.

**Validation:** full suite **370 passed in 405.02 s**, using a fresh pycache and
pytest temporary directory in this checkout. All saved P32A cases also pass the
registered normalization, endpoint, flatness, energy, path, projection, motion
intervention and phase-evolution tolerances.

### E062. Conserving motion and an exchange-statistics control (2026-09-20, Astra)

Triage prioritized the missing autonomous transport law over another stability
search under the frozen H0. Registered P32B in `644e49a`, then implemented the
Z2 operator W_ab(I-S_a S_b)/2. It moves one occupied endpoint to an empty one.
The algebra conserves N, H0 and B, but changes A_v. Pair persistence is imposed
by number conservation, not binding. At kappa=0.2 the operator bound
H-E_vac >= (1-kappa*d_max)N + sum(I-B) retains a positive charge-cost bound.

All 16 initial pairs and 80 time samples completed on a tetrahedron and the
two-tetrahedron bipyramid. Occupations change by up to 0.7166; energy, norm,
number, flatness and continuity errors are below 4.30e-14. The flat pair sector
equals a hard-core boson graph to 1.37e-16. Unprojected strings fail the
number/energy-conservation control, as predicted. Full matrix residuals meet
the registered 1e-10 tolerance. There is no inferred binding or reaction result.

During the work, the user supplied the quantum spin liquid article. Primary
papers led to the Levin–Wen exchange-algebra test, registered as P32C in
`5c2ef6a` before execution. All 108 oriented neighbor triples have nonzero,
unit-norm products with relative sign +1. The canonical fermion control gives
-1 in every case. Error is below 2.23e-16. The diagnostic therefore identifies
our tested electric pairs as a bosonic baseline; it can distinguish the desired
fermion sign and must not confuse a spinor label with exchange statistics.

Seven relevant defect tests pass, including independent Pauli-matrix comparison
and a finite-difference check on the local current. The full suite's previous
370-test result belongs to P32A; no new full-suite claim is made here. New data:
`p32b_transport.json` and `p32c_exchange.json` under `reference/astra_session/data`.

Next priority: connect an admissible local dynamics and its sign structure to
the reduction rules before searching for bound states. Spin-liquid/string-net
work supplies benchmarks, not a derivation of our dynamics. The dimensional
audit, hard-Gauss-law completion, open-boundary channel and state-space embedding
remain separate work items; Williamson–van der Mark remains a target.

### E063. P33 recreated independently: virtual pairs check the bookkeeping to machine precision, and two bugs only the bipyramid could catch (MEASURED; cross-checkout reproduction)

**Context.** The Opus P19–P31 + Astra P26–P33 wave was fast-forward merged into this canonical
checkout from the sibling tree (committed history only, per instruction) and pushed to GitHub.
SciPy 1.18.1 / NumPy 2.5.3 installed to match the sibling environment; full suite green after
merge. Astra's P33 implementation existed only as uncommitted files in the sibling — so this tree
re-implemented the registered protocol (`docs/P33_VIRTUAL_PAIRS.md`, commits b8e462f/a836e7d)
from scratch, deliberately without reading their code: the pre-registration itself is the spec,
and agreement becomes a two-implementation test of BOTH the physics and the protocol's completeness.

**Result.** Every registered identity holds in the independent implementation: first-order block
sum_m P_m V P_m = -sum W_ab(I-S_aS_b)/2 (P32B's transport form, residual <= 2.0e-13); flat-sector
duality to E_vac + sum n_v and -sum X_aX_b; all four second-order coefficient formulas with
C_vac = -|E|/2 exactly (-3 tetrahedron, -4.5 bipyramid); the pre-execution K4 cancellation is real
and exact (C identically zero to 8e-16 — first and second order coincide at every coupling,
residuals scale lam^3, observed orders 3.000–3.006); on the bipyramid second order improves
everywhere (3.03e-4 -> 1.85e-5 at lam=0.01). Exact evolution: norm/energy/flatness conserved to
<= 7.2e-15; bare defect number is NOT conserved (>1e-8 sector departure) — as registered, and the
point of the exercise: P32B's exact number conservation is the leading-order shadow of a simpler
non-conserving rule, so it need not be postulated fundamentally.

**Cross-checkout reproduction.** Against Astra's archived run: band eigenvalues max diff 0.0
(tetrahedron) and 5.3e-15 (bipyramid); first/second-order matrices <= 2.1e-15. Two independent
implementations of one pre-registration, same numbers — the protocol was complete enough to pin
the computation uniquely.

**Methodological harvest (bugs as fixtures).** Two implementation bugs were INVISIBLE on the
tetrahedron and caught only by the bipyramid: (i) iterating all vertex pairs instead of complex
edges in the dual hopping — K4 has every pair as an edge, so V-duality passed there while wrong;
(ii) a set-mutation ordering error in the shared-endpoint predictor. Both are exactly the class
of "verified on the friendly fixture" failure this project keeps hitting; the registered decision
to run BOTH fixtures is what caught them. Recorded so future protocols keep the asymmetric-fixture
requirement.

**Status discipline.** H(lam), continuous-time unitary evolution and the phase action remain
POSTULATED (protocol's own ledger); success removes exact N-conservation as a fundamental
postulate for LEADING hopping only — no fermions, no binding, no derivation from reduction.
*Evidence:* `src/constraintnet/defect_perturb.py`, `tests/test_defect_perturb.py` (9 tests),
`examples/p33_effective_local.py`, `reference/local_qwen/data/p33_effective.json`; PREDICTIONS
P33 outcome; CLAIMS row 56.

### E064. Universality matrix across six groups + property suite: the vacuum-only-basin result survives non-abelian generalization (MEASURED, exploratory; 2026-09-21, local Qwen)

**Context.** Two standing triage items closed in one unit. Item 16: no universality matrix —
every landscape/persistence result was A4/Z3-only, so "group-generic architecture" had never been
exercised past two groups. F8 remainder: property-based invariant suite (referee R3 complaint that
the green-test count exceeds coverage). The specific target was CLAIMS row 26: on the tetrahedron
seed with curvature action H and exact edge-multiplier dynamics, vacuum is the ONLY closed
equal-action basin (measured exhaustively for A4; Z3 arm ≤3 moves). If that fact is A4-specific,
the "no classical particles from sector labels alone" story narrows; if it survives S3/Q8/D4/Z2,
it strengthens within the tested class.

**Method.** New groups via a generic `TableGroup` (explicit element list + product rule) that
VERIFIES AXIOMS AT CONSTRUCTION: two-sided identity search, right inverses, full associativity
triple loop, and generator-set coverage by BFS — a broken table fails loudly where it is built.
S3 as permutations of 3; Q8 as (sign, unit) pairs with the i/j/k rules; D4 as r^p s^eps with
s r = r^-1 s. Probe (`examples/universality_matrix.py`): for G in {Z2,Z3,S3,D4,Q8,A4}, orbit
decomposition of G^3 under residual global conjugation, cross-checked against Burnside
(1/|G|)·Σ_g |C_G(g)|³ with values hand-computed BEFORE running code (8/27/49/176/176/178), plus
the little-group census and the exact landscape (`constraintnet.landscape`) on the tetrahedron
boundary. Recorded as an EXPLORATORY search, not a pre-registration; the Burnside numbers are
analytic cross-checks of the orbit code, not physics predictions.

**Result 1 — universality holds within the tested set.** Zero closed nonvacuum plateaus for every
group: Z2 (8 physical states), Z3 (27), S3 (49), D4 (176), Q8 (176), A4 (178). Brute-force orbit
counts equal Burnside everywhere; the A4 little-group census reproduces the pinned histogram
(130 trivial / 26 Z3 / 21 V4 / 1 A4). Notably Q8 — with its large center {±1} and three distinct
order-4 centralizers — traps no basin either. Scope limits stated: six small groups, one action H,
tetrahedron seed, declared multiplier dynamics; not a theorem for arbitrary finite groups.

**Result 2 — property suite (73 seeded tests, `tests/test_properties.py`).** P1 vertex gauge
preserves Region.gauge_invariant_state and face-holonomy classes while moving raw labels; P2
DriverA(relational) conserves the region's gauge-invariant state AND boundary-surface face classes,
recomputed from the complex every step (never driver bookkeeping); P3 Pachner 2-3 / 3-2 apply+revert
exact snapshots across all six groups with randomized labels; P4 oriented-edge inverse consistency
survives random relabeling and gauge transformation; P5 kernel orbit quotient == Burnside for every
registered group including the new TableGroups.

**Harvest — a test failure that was physics (design confirmation).** The first version of P2 asserted
conservation of ALL face-holonomy classes under DriverA(relational) and failed on every non-abelian
seed: accepted moves churn INTERIOR face curvature while preserving exactly the boundary-surface
observables. That is not a kernel bug — it is the designed asymmetry (bulk curvature invisible to a
region's boundary observables churns freely; only boundary data is the conserved quantity), and the
gauge_invariant_state assertion itself never failed once across 6 groups × 3 seeds × 60 steps. The
test was corrected to assert boundary-surface conservation with an explicit comment that interior
churn is expected. Recorded because a naive "everything observable is conserved" reading of the
relational model is WRONG in exactly this direction, and future tests must state which surface they
observe.

**Development bug (fixed before commit).** The TableGroup generator-coverage check initially BFS'd
each generator individually and demanded each generate the whole group alone — S3's transposition
legitimately generates only 2 of 6. Corrected to set semantics (single BFS over all generators and
inverses). Same class of error as E063: a check that passes/fails on friendly inputs only.

**Status.** MEASURED within the tested groups; strengthens row 26's scope from {A4, Z3} to six
groups including non-abelian ones with centers and dihedral structure. No new physics claimed; no
claim about arbitrary finite groups or other actions. Suite green: 454 tests.
*Evidence:* `src/constraintnet/groups.py` (TableGroup + S3/Q8/D4), `examples/universality_matrix.py`,
`reference/local_qwen/data/universality_matrix.json`, `tests/test_properties.py`; CLAIMS row 57;
triage item 16 closed, F8 remainder partially closed (scaling study still queued).

### E065. F8 scaling study: invariants hold at n=3 over 12,000 driver steps — and the whole-complex relational driver turns out to be exactly "bulk churns freely, boundary frozen" (MEASURED; one prior refuted) (2026-09-21, local Qwen)

**Context.** F8's remainder from the Round-3 referee: property coverage at small fixtures only
(E064 tested n=2 / 60 steps). The scaling study pushes the same invariants along mesh size
(n=2 → n=3), run length (60 → 500 steps × 2 seeds), and quotient depth (k = 1..4 free edges,
|G|^k up to 20736 configs for A4), for all six registered groups.

**Result 1 — invariants survive at scale.** Vertex gauge preserves Region.gauge_invariant_state and
boundary face classes exactly at n=3 (raw labels verified moving); DriverA(relational) conserves the
region state and boundary-surface classes recomputed from the complex every step across 6 groups ×
2 meshes × 500 steps × 2 seeds; Pachner 2-3 apply+revert exact snapshots at n=3 with randomized
labels; kernel quotient == Burnside for k = 1..4. No exceptions.

**Result 2 — the mechanism finding (prior refuted).** The first draft predicted accept rates should
DROP with mesh size (more observed loops → tighter conservation). Measurement: rate RISES, ~0.25 at
n=2 to ~0.44 at n=3. A label-diff probe (classifying every accepted move by which edge's label
actually changed — after discarding a first attempt that parsed record text and got garbage) shows
why exactly: for a WHOLE-COMPLEX region, DriverA(relational) accepts ONLY proposals on purely-
interior edges — zero surface-edge acceptances in 12,000 moves across every group and mesh — and
interior proposals are accepted essentially always (all cells within |z| ≤ 2.1 of the closed-form
Binomial count). The acceptance rate is therefore pure geometry: interior-edge fraction
(E_total − E_surface)/E_total = 26/98 ≈ 0.265 at n=2, 117/279 ≈ 0.419 at n=3 (Euler on the boundary
sphere), growing toward ~1 with mesh size as volume/surface. The prior was wrong because boundary
observability does not grow with bulk size: the observed surface stays a sphere while invisible
interior edges proliferate.

**Interpretation discipline.** This is a characterization of OUR chosen region+driver, not of
physics in general: "whole-complex region" means the only conserved observables are on the boundary
sphere, so the relational dynamics is exactly bulk churn with frozen boundary — E064-P2's asymmetry
sharpened to a closed form. Consequence for future cross-checks (backlog item 7): whole-complex
accept rates are geometry-dominated and must NOT be compared against single-tetrahedron baselines
(~0.34) as if they measured the same thing; per-move-class and per-shell statistics need a region
specification to mean anything. Recorded as CLAIMS row 58 (MEASURED, module characterization).

**Methodological note.** The label-diff-vs-text-parsing lesson: classifying driver events by parsing
record.detail produced impossible numbers (488/500 "interior proposals" at interior fraction 0.265);
diffing labels before/after each step is slower but ground truth. Driver event records are for humans;
measurements must come from the complex.

*Evidence:* `examples/f8_scaling_study.py`, `reference/local_qwen/data/f8_scaling.json`; CLAIMS row 58;
triage F8 closed (property suite E064 + scaling study E065). Suite unaffected (no kernel changes);
study script assertions all held.

### E066. Free space v1: the track becomes dynamical — relinking is a real relocation channel, and naive object-tracking is exposed as a metric failure (MEASURED; one prior refuted in an unexpected direction) (2026-09-21, local Qwen)

**Context.** User-directed queue item ("free space / self-laid track"): mainline DriverA only
rewrites the gauge geometry of FIXED rails. DriverC (new, `src/constraintnet/drivers.py`) adds
Pachner 2<->3 relinkings to the move set under the SAME relational acceptance — entailment can now
lay adjacency while it travels. v1 scope: whole-complex regions (closed ball, boundary sphere
frozen); observation region rebuilt from current tetrahedra every step (stored tets go stale under
relinking). Tests (`tests/test_driverC.py`, 8): interior relinkings NEVER vetoed (Z2/A4 — if this
ever fails, the observation secretly sees bulk triangulation); mixed runs freeze boundary labels and
canonical state exactly, keep Euler V−E+F−T = 1, no degenerate tets; NO-TELEPORTATION: surviving
faces provably keep holonomy under relinking (curvature changes only on faces added/removed by the
move itself or containing the changed edge); provenance driver="C", model="freepach-v1".

**Measurement (`examples/free_space_tracking.py`, A4 n=3, 300 steps x 3 seeds, C vs A control;
priors P1-P3 stated in the script docstring before running).** Tracking boundary = combinatorial
overlap lineage of curved-face sets as VERTEX TUPLES (face indices do not survive relinking — a
tracker on a dynamical track must be identification-stable), recentered implicitly every step.

- **P2 CONFIRMED — relinking is a genuine new channel.** First displacement of the seeded cluster's
  support out of its initial tet-set: steps {4,3,1} under DriverC vs {34,20,1} under labels-only;
  ~two-thirds of tracked-support relocations in C runs are attributable to Pachner moves (78+19 of
  164 label-attributed... precisely: pachner23 78 + pachner32 19 vs label 47 across seeds). Curvature
  can move because THE GROUND MOVES, without any label changing — motion via re-laid adjacency, the
  thing pure-label dynamics cannot do. Zero lineage ambiguities in all six runs.
- **P1's real lesson was about our metrics, not the defect.** Naive overlap-lineage survival: 6/6
  runs "survived" 300 steps — but global curvature energy grew 6 -> ~230 (A) / ~370 (C) curved faces
  and the tracked cluster ended at 96-100% OF ALL GLOBAL CURVATURE. The seed did not persist; it
  evaporated into a heating vacuum, and the tracker faithfully followed the heat. Under whole-complex
  relational acceptance nothing constrains bulk pair creation (E065 mechanism), so "lifetime" without
  size normalization against matched vacuum measures the tracker, not the physics. Any future
  persistence claim must be extent-normalized with a vacuum control — this is now the concrete spec
  for the queued "independent persistence criteria" item.
- **Free space heats and grows.** Relinking accelerates heating (~1.6x at matched steps) and inflates
  the triangulation (162 -> ~250 tets; DriverA arm fixed at 162): the proposal scheme has no
  stationarity — flagged for the weighted-dynamics/detailed-balance queue item. Boundary conservation
  itself held every step in both arms (asserted, not assumed).

**Interpretation discipline.** Negative result kept visible: free space v1 does NOT confine anything;
matter-protection requires Gauss-law completion or energetic acceptance, not just boundary freezing.
The positive physics content is the relocation channel itself — a defect can now move by having its
track relaid under it, which is exactly the "building its own track" mechanism asked for, measured to
exist and to dominate relocation (~2/3 of events).

*Evidence:* `src/constraintnet/drivers.py` (DriverC), `tests/test_driverC.py`,
`examples/free_space_tracking.py`, `reference/local_qwen/data/free_space_tracking.json`,
`reference/local_qwen/figures/e066_free_space_accretion.png`; CLAIMS row 59; triage free-space item
updated (v1 done; follow-ups: subregion boundaries under relinking, edge birth/death beyond Pachner,
stationary proposal scheme, extent-normalized persistence).

### E067. Hard Gauss completion v1: matter-coupled Z2 phase space with the constraint SOLVED - confinement scale measured, and E066's vacuum heating exposed as an acceptance-rule artifact (MEASURED; three priors held) (2026-09-21, local Qwen)

**Context.** HANDOFF correction 2: H = -sum A_v - sum B_f is a FINITE PENALTY model whose bare
charge-defect states violate the literal A_v=1 restriction; "a charge-sector/matter-coupled Gauss
constraint needs an explicit construction". E066 had just shown whole-complex RELATIONAL acceptance
cannot confine anything (heats the vacuum, tracked object -> ~100% of global curvature) and named the
prerequisite: confinement beyond boundary freezing. This unit builds that completion at the classical
Z2 phase-space level and measures what constraint-plus-energy protects.

**Construction (`src/constraintnet/gauss.py`, no RNG; `DriverG` in drivers.py).** State = (connection
bits g_e, electric flux bits E_e). Charges are NOT independent DOF: q_v := XOR_{e incident to v} E_e -
the Gauss constraint SOLVED (div E = rho), not penalized. Consequences by construction: an isolated
charge cannot be configured at all (charges ARE string endpoints); total charge parity is identically
even; a boundary vertex with q_v=1 is an absorption channel (exterior reservoir) - the open-boundary
channel P32-3 asked for, defined rather than postulated. DriverG = Metropolis over {flip g_e} U
{flip E_e} on H = beta_B * #{curved faces} + beta_E * sum E_e. Scope stated plainly: classical Z2 phase
space, not quantum amplitudes, not nonabelian - that is what "completion v1" means here.

**Tests (`tests/test_gauss.py`, 9).** Vacuum has no charges; single edge flip creates an even pair;
200 random flips keep parity even every step (isolated charge impossible); a loaded string carries
charge ONLY at its two ends (interior points balanced); double-flip is identity; boundary charge counts
as exited; DriverG preserves Gauss and keeps the magnetic sector bounded at high beta_B; near-zero-
temperature vetoes uphill moves; nonabelian group rejected (declared scope).

**Measurement (`examples/gauss_confinement.py`, Z2 n=3, 600 steps x 4 seeds; priors G1-G3 stated in
the script docstring BEFORE running).** Gauss asserted every step in every run.
- **G1 CONFIRMED (structural):** charge parity even throughout; isolated charge never appears. The
  constraint is real because it is solved, not because a penalty makes violations rare.
- **G2 CONFIRMED - the E066 contrast:** magnetic vacuum stays COLD at every beta_E scanned (#curved
  faces max = 0 across all runs). E066's runaway heating (6 -> ~370 curved faces) was purely an artifact
  of RELATIONAL acceptance, NOT intrinsic to the model. Energy-based acceptance fixes it.
- **G3 CONFIRMED - confinement scale:** mean live charge count falls monotonically with string tension
  beta_E: 30.3 (beta_E=0) -> 26.4 -> 17.8 -> 3.9 -> 1.5 (beta_E=8); bound-pair fraction rises 0 -> 0.75,
  multi-charge (deconfined) fraction falls 1.0 -> 0. At high tension the seeded interior pair persists as
  a bound pair - the string cannot cheaply break because breaking it costs two endpoints.

**Interpretation discipline.** This is NOT mobile matter under a literal local Gauss law in the full
quantum sense, and not a claim of electrons/quarks/confinement-in-nature: it is the explicit classical
Z2 completion HANDOFF asked for, showing that (a) solving rather than penalizing Gauss makes charge a
conserved string-endpoint by construction, and (b) constraint + energy gives the persistence E066's
acceptance rule lacked. The quantum/nonabelian completion and any coupling between the magnetic flux and
electric-string sectors (so a defect is BOTH - a dyon) are the named next steps.

*Evidence:* `src/constraintnet/gauss.py`, `src/constraintnet/drivers.py` (DriverG),
`tests/test_gauss.py` (9 tests), `examples/gauss_confinement.py`,
`reference/local_qwen/data/gauss_completion.json`, figure
`reference/local_qwen/figures/e067_gauss_confinement.png`; CLAIMS row 60; triage hard-Gauss item updated.

### E068. Independent extent-based persistence criterion: validated against E066, and two honest findings about the metric itself (MEASURED + METHODOLOGY; one prior refuted) (2026-09-21, local Qwen)

**Context.** E066 exposed that naive overlap-lineage survival is vacuous under unconstrained
acceptance (tracker follows the heat; clusters end at ~100% of global curvature). It promised a fix:
extent normalization against matched vacuum. This unit builds that criterion as an INDEPENDENT test
that consults NO charge signature -- deliberately separate from the Milestone-4 charge-signature
`is_persistent` in persistence.py (which stays untouched and load-bearing). If two independent notions
of "object" agree, that is evidence; if not, which one is load-bearing becomes the finding.

**Safety note (methodological).** Before writing I overwrote an existing tracked file `persistence.py`
with a new module of the same name -- caught immediately via git (348 lines of Milestone-4 work),
restored with `git checkout HEAD --`, then verified all three target filenames absent before writing.
Lesson recorded: CHECK EXISTENCE before creating any file; the handoff warned about exactly this class
of duplicate-work error.

**Criterion (`src/constraintnet/persistence_metrics.py`, pure, no RNG; 14 tests).** extent_stability
|S(t)|/|S(0)|; lifetime_until band [1/k,k]; locality median tracked/global; vacuum_noise mean spurious
components in matched vacuum; signal_to_noise (mean support minus vacuum level)/vacuum. Verdict =
survived-horizon AND localized (locality gate), with a second SNR gate reported side by side.

**Experiment (`examples/e068_extent_vs_charge.py`, Z2 n=3, 500 steps x 3 seeds; priors stated before
running).** Two regimes, each with a matched no-seed vacuum control:
- **R1 relational-curvature (DriverA(relational)): prior NOT persistent. CONFIRMED.** lifetime 38,
  locality 0.881 (became the background), vacuum level 118 curved faces, SNR -0.20 -> rejected by BOTH
  gates. The criterion reproduces E066's verdict WITHOUT consulting charge -- independent validation.
- **R2 gauss-confined-pair (DriverG high beta_E): prior INDEPENDENTLY PERSISTENT. REFUTED / INCONCLUSIVE.**
  SNR 0.62, extent undefined at t=0 (averaged initial support collapsed). The pair does not sustain
  trackable excess-over-vacuum structure.

**Two findings about the metric itself (the real harvest).**
1. **Locality alone misfires on a cold vacuum.** R2 locality = 0.667 in a regime where matched vacuum is
   empty (level ~0): a LONE object trivially dominates global structure, so tracked/global -> 1 looks like
   E066's "became the background" but is the opposite -- dominance, not dilution. Fix: the load-bearing
   gate must be VACUUM-RELATIVE signal-to-noise (does the seed sustain what unseeded churn does not?),
   with locality demoted to a reported diagnostic. Stated as a principle, not retrofitted to force R2 True.
2. **Confinement is not persistence.** At high beta_E retracting a flux string LOWERS energy, so Metropolis
   drives a pre-existing pair toward annihilation; Gauss protects charge NUMBER but nothing prevents the
   pair meeting and vanishing. "Confined" (bounded separation) != "persistent" (survives). Matter needs a
   charge-conjugation SELECTION rule preventing annihilation -- which neither Gauss nor string tension
   supplies. Directly informs docs/ELECTRON_TARGET.md (why an electron must be stable, not merely confined).

**Status.** Criterion delivered and independently validated on R1; R2 reported honestly as inconclusive
(annihilation vs averaging-artifact not separated under this tracking) rather than tuned to a prior. No
new physics claim beyond the metric + the confinement!=persistence observation. Figure omitted
deliberately (budget); numbers table is decisive.

*Evidence:* `src/constraintnet/persistence_metrics.py`, `tests/test_persistence_metrics.py` (14 tests),
`examples/e068_extent_vs_charge.py`, `reference/local_qwen/data/e068_extent_persistence.json`; CLAIMS
row 61; triage persistence-criteria item updated.


### E069. N-ality: non-self-dual charge delays annihilation but is not a selection rule, and abelian
sectors provably contain no dyons (MEASURED + NEGATIVE for PC; PD confirmed) (2026-09-21, local Qwen)

**Claim under test.** E068 ended by demanding a *charge-conjugation selection rule*: Gauss protects charge
number, yet a confined pair still annihilates because retracting the string lowers energy and in Z2 every
charge is its own antiparticle. Hypothesis: move to Z_N (N >= 3), where charges are not self-inverse, so that
neutral composites split into pair-cancellable (**mesonic**) and irreducible (**baryonic**) content, and the
lattice arithmetic itself forbids the baryon's decay.

**Method.** `gauss_zn.GaussStateZN`: electric flux a_e in Z_N per edge (canonically oriented u<v; flow u->v),
charges DEFINED by the solved constraint q_v := div(E)_v mod N -- never configured independently. Magnetic
sector unchanged. Pure classifier `nality_content` performs maximal cancellation k <-> (N-k) and reports
residual content. Dynamics: new `drivers.DriverGZN`, Metropolis on H = beta_B*#{curved faces} +
beta_E*sum_e|a_e| with exact inverse reverts (Z_N moves are not involutions). Seeds: meson = flux string
between the two furthest interior vertices; baryon = 3-arm Y from a junction, which is neutral because
q_junction = -3 = 0 mod 3 while carrying no cancelling pair. Priors PA-PD registered in PREDICTIONS.md first.

**Results.**
1. **PA holds by construction** (asserted every step): total charge identically 0 mod N, and a flux update
   moves charge only at its two endpoints, oppositely.
2. **PB holds: Z2 has no baryonic content at all** -- exhaustive over neutral multisets up to size 6, the
   residual is always empty. E068's annihilating pair was therefore the generic behaviour of a self-dual
   charge group, not an artefact of that experiment.
3. **Structural bonus:** an equal-flux star junction is invisible iff it has exactly N arms. Z3 gives an
   irreducible triple (neutral, 0 pairs, 3 constituents); Z4's three-arm seed leaves the junction charged and
   reads as a 4-site object. Neutrality-counts-as-N-ality in one line.
4. **PC REFUTED as stability; direction only partially right.** At beta_E = 12 with a 12,000-step horizon every
   seeded baryon decays: t_vacuum = [1899, 2261, 3023, 3135, 1833, 3966], 0/6 survivors (meson: [1895, 1992,
   2060, 1001, 1832, 1797]). Median delay is x1.4 only (2642 vs 1863), and per-seed it is bimodal: +1 to +4
   steps for two seeds, +269 to +2169 for the rest. The horizon-3000 "survivors" were slow decays, not stable
   objects.
5. **The pre-registered mechanism was wrong, and instructively so.** I predicted decay would require a
   three-body coincidence. It does not: charge is *additive at a vertex*, so two unit charges meeting FUSE into
   a single q=2 site -- which is precisely the antiparticle of the third. A two-step route (merge, then
   annihilate) always exists; N-ality only adds encounters. **N-ality is a kinetic hindrance, not a forbidden
   process.** Consequence for the particle programme: absolute stability cannot be obtained from abelian charge
   arithmetic. It requires either (a) a balancing charge that is dynamically inaccessible (superselection:
   partner held in the exterior reservoir, so decay means walking to the boundary) or (b) nonabelian fusion
   rules that constrain which outcomes exist at all.
6. **PD confirmed: abelian models contain no dyons.** With identical magnetic initial condition and rng stream,
   adding an electric string leaves the curved-face count untouched in the tail (4.508 vs 4.510). Seeding a
   charge ONTO a curved cluster produces correlation 0.2569 early, decaying to 0.0534 -- indistinguishable from
   a charge placed far away (0.0528). Flux and charge diffuse independently; the sector factorisation is now
   measured rather than asserted. Any dyon must therefore come from nonabelian flux x centralizer-irrep
   structure (the D(A4) layer), not from an inserted cross term.
7. **Plasma threshold, quantified.** At beta_E = 2 the *unseeded* vacuum carries ~25.6 spontaneous charges and
   reads baryonic in 66% of steps; at beta_E = 8 it holds 0.27, at 12 exactly 0. My first run of this harness was
   performed at beta_E = 2 and its "lifetimes" were meaningless -- a single object cannot be tracked inside a
   charge plasma. This is E068's matched-vacuum/SNR lesson with concrete numbers attached.
8. **Removal channel.** exited_charge = 0 at every observed t_vacuum: these objects annihilate rather than being
   absorbed by the exterior reservoir, even though live charges sit on boundary vertices 25-70% of the time.

**Two harness bugs worth recording.** (i) `load_string` copied from the Z2 module ignored edge orientation; in
Z2 flipping is its own inverse so nothing complained, but in Z3 it *doubled* flux instead of cancelling -- caught
by a forward-then-backward regression test. (ii) The first star-seed helper silently returned zero arms (the n=3
Kuhn ball's 8 interior vertices are mutually at distance <= 2, so a min-arm-length filter was unsatisfiable),
which classified a supposedly baryonic seed as 'vacuum'. Both now fail loudly: seeding asserts the intended
N-ality landed.

**Status.** Delivered: Z_N Gauss completion, N-ality classifier (21 tests), decoupling measurement. Verdict:
hypothesis PC refuted in its strong form and weakened to a measured kinetic delay; PD confirmed; PB and PA hold.
The search for a stability mechanism continues, now narrowed to superselection or nonabelian fusion.

*Evidence:* `src/constraintnet/gauss_zn.py`, `src/constraintnet/drivers.py` (DriverGZN),
`tests/test_gauss_zn.py` (21 tests), `examples/e069_nality_and_dyons.py`,
`reference/local_qwen/data/e069_nality_dyons.json`; CLAIMS row 62; PREDICTIONS E069 outcome appended.

**Animation.** `examples/e069_nality_movie.py` renders `reference/local_qwen/figures/e069_meson_vs_baryon.gif`: the
two regimes side by side under an identical move law (seed 5, beta_E = 12). The replay asserts it reproduces the
harness decay times exactly (meson 1797, baryon 3966) before drawing a frame. Near t ~ 2200 the baryon panel flips
to "MESONIC (0 irreducible)" with two live charges -- the fusion step that kills it -- while the meson panel already
reads ANNIHILATED. Mesh lines are projection only; every change shown is an accepted local rewrite, and the HUD
prints sum q mod 3 as a running Gauss-leak check.
