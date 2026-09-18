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

### E027. Boundary memory and rigidity: enclosed flux forbids vacuum filling, but carries zero hidden entropy — matter-entropy is CORE-localized (MEASURED; positive + negative result)
Two measurements on balls enclosing the seeded loops:

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

