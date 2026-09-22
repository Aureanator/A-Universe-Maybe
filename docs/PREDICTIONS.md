# Pre-registration log

Discipline (referee item 15): every experiment below was **written down before it was run**.
Predictions carry the date and mental state of their writing. Outcomes are appended verbatim
after the run, never edited into the predictions. If we are wrong, the wrongness stays visible.

This file is the epistemic shield for the critique-response work (`docs/CRITIQUE_TRIAGE.md`).

## P33 — Effective hopping and virtual pairs (2026-09-20, Astra; before running)

`P33_VIRTUAL_PAIRS.md` registers the full local perturbation H=H0-lambda sum W,
its comparison with P32B's first-order number-sector projection, and the
second-order virtual zero/four-defect corrections. Fixed tetrahedron/bipyramid
fixtures, four couplings, and all 16 initial pairs. Predictions include exact
first-order agreement, cancellation of disjoint-pair transfer, additive diagonal
charge costs, and nonconservation of bare defect number under the full rule.
No axiom-level derivation, fermions or binding is asserted. Outcomes follow later.

**P33 outcome — local recreation (local Qwen, 2026-09-20).** This tree did not have Astra's
uncommitted implementation, so the protocol was re-implemented independently from
`docs/P33_VIRTUAL_PAIRS.md` alone (`src/constraintnet/defect_perturb.py`,
`tests/test_defect_perturb.py`, `examples/p33_effective_local.py`) — a genuine cross-checkout
test of the pre-registration's completeness. ALL registered checks pass: subset-basis
orthonormality/completeness (<= 1.1e-16); first-order block identity with P32B's transport form
(<= 2.0e-13); flat-sector duality H0 = E_vac + sum n_v and V = -sum X_aX_b over complex edges
(<= 2.0e-15; note: K4 hides the edge-vs-all-pairs distinction, the bipyramid does not — one of
two implementation bugs found only there); all four second-order coefficient formulas (<= 1.7e-15)
with C_vac = -3 = -|E|/2 on tetrahedron and -4.5 on bipyramid; the pre-execution K4 cancellation
confirmed identically (C_pair max abs 8.0e-16, first- and second-order spectra coincide at every
coupling, observed error order 3.000–3.006 = O(lam^3)); bipyramid second order improves at every
registered coupling (err 3.03e-4 -> 1.85e-5 at lam=0.01; observed order ~3.0–3.1). Exact evolution
of all 16 bare pairs: norm/energy/flatness conserved <= 7.2e-15, bare-sector departure > 1e-8 as
predicted. **Cross-check against Astra's archived run** (`reference/astra_session/data/p33_virtual_pairs.json`,
written by their independent implementation; completed-run data artifact archived from the sibling
working tree 2026-09-20 so evidence paths resolve in this checkout — their uncommitted CODE was
never read; only this data artifact's summary fields were consulted, as cross-check targets): band eigenvalues agree to max diff **0.0** (tetrahedron) and
**5.3e-15** (bipyramid); first/second-order matrices to <= 2.1e-15; vacuum energies exact.
Two implementations, one protocol, same numbers. Interpretation per the registered gate: exact
defect-number conservation is not required as a fundamental postulate for the leading hopping
approximation; nothing about binding or fermions changes. Records:
`reference/local_qwen/data/p33_effective.json`; diary E063; CLAIMS row 56.

## P29a — Stationary states with a tail: where circulation is allowed, and what it costs (2026-09-20, Opus; registered before running)

**Decision behind it (user, 2026-09-20).** Give the candidate a tail: support outside the loop, a
surrounding field. Real matter's core is far smaller than its field, and the field is part of
matter's imposition. Self-binding still has to be earned, so this experiment only maps what the
flat walk allows; the record's role comes next (P29b).

**Analytic frame (DERIVED).**
- Every eigenstate has a time-independent density, so its current is divergence-free at every
  vertex: Σ_w J(v,w) = 0. Stationary flow therefore runs in closed circuits; a ring current needs
  no return path.
- P28: strict confinement to a loop forces the coin to −1, hence θ ∈ {0, π} and zero current. The
  minimal relaxation is amplitude on the arcs leaving the loop's vertices, which is what "tail"
  means here.
- The walk with the A4 3-dim irrep is a **real orthogonal** matrix (the coin, the shift and the
  irrep are all real), so its spectrum is conjugate-symmetric and complex eigenvectors come in
  ± pairs. This is where any circulation must come from.

**Setup.** Flat closed Kuhn box, n = 4, ring weights (1, ½), the 3-dim irrep; the full walk
diagonalised exactly (dimension 3 × number of arcs). Two label sets: identity, and 10 random draws.
Loops: the P28 axis square (L = 4), the face-diagonal square (L = 4), the triangle (L = 3) and the
found odd cycle (L = 5).

**Per eigenstate we record:** phase; current bias around each loop; the largest single-edge current;
divergence; weight on the loop's arcs; weight within hop distance 1 of the loop; inverse
participation ratio over vertices; and the share of total |J| carried on loop edges versus outside.

**Predictions.**
- **P29a-1 (exact):** divergence ≤ 1e-12 for every eigenstate; eigen-residuals ≤ 1e-10.
- **P29a-2:** every eigenstate with |loop bias| > 1e-9 has phase away from 0 and π (by more than
  1e-6). Circulation requires a genuinely complex state.
- **P29a-3 (the cost of a tail):** among states carrying |bias| ≥ 0.01, the maximum weight on the
  loop's arcs is below 0.5, while compact (zero-current) states reach 1.0. Circulation is paid for
  in delocalisation.
- **P29a-4:** for current-carrying states, most of the total |J| sits *off* the loop: the loop's
  share is below 0.5 for the state with the largest loop bias. If this fails, the flow really is
  concentrated on the core rather than the field.
- **P29a-5 (exploratory, no direction):** the best trade-off, defined as the largest product of
  (loop weight) × (|bias|), is recorded for each loop and label set, together with that state's
  phase. No prior on its size or on which loop wins.

**Claim limits.** These are flat-walk kinematics in a closed box. A box eigenstate is not a bound
particle, a tail here is not yet a field with its own dynamics, and nothing about self-binding,
mass or charge follows. P29b will ask whether a responsive record changes the trade-off.

**P29a AMENDMENT (2026-09-20, registered after the first run was seen, before the re-run).**

- **What the first run showed.** Divergence ≤ 2e-15 and residuals fine (P29a-1 holds), but the
  per-eigenvector current readout is **ill-posed**: the spectrum is massively degenerate (423–549
  of 588 gaps below 1e-8), and inside a degenerate eigenspace the current depends on which basis
  the diagonaliser happens to return. With identity labels it returned 219 current-carrying
  vectors; with random labels it returned essentially none (max |J| 9.8e-14). Both are basis
  artefacts, not physics. The first run's `p29a_tail.json` is kept and marked superseded.
- **The symmetry behind it (DERIVED, verified to 1.4e-15).** Define the antiunitary
  K ψ(w→v) = ρ(A_wv) · conj(ψ(v→w)): conjugate and reverse every arc, transporting as the walk
  does. Then **K U = U⁻¹ K** and **K² = +1**.
  - Consequently every eigenspace admits a K-invariant basis, and a K-invariant state has
    q(v,w) = q(w,v), i.e. **zero current**.
  - So stationary current is never forced: it lives only in degenerate eigenspaces, as a complex
    combination, always paired with its time-reverse.
  - This is the walk's version of time-reversal symmetry, with K² = +1, i.e. no Kramers protection.
- **P29a-2 is withdrawn as stated** (it asked a basis-dependent question). Replaced by:
  - **P29a-2′:** in each degenerate eigenspace, the maximum loop bias is obtained by solving the
    generalized eigenproblem max ψ†(Σ_f M_f − M_r)ψ / ψ†(Σ M)ψ over that space. Predictions:
    every one-dimensional eigenspace gives bias ≤ 1e-9; circulation requires degeneracy.
  - **P29a-3′ (the cost of a tail, restated basis-independently):** for the eigenspace maximiser
    with |bias| ≥ 0.01, the loop weight stays below 0.5, while compact zero-current states reach 1.0.
  - **P29a-4′:** for the state of largest |bias|, most of the total |J| sits off the loop
    (loop share < 0.5).
  - **P29a-5′ (exploratory):** record the best (loop weight × |bias|) per loop and label set.

## P32C — Exchange-algebra control (2026-09-20, Astra; before running)

Following the user's quantum-spin-liquid lead, `P32C_EXCHANGE.md` registers the
Levin–Wen triple-hop diagnostic on all 108 oriented neighbor triples of the two
P32B fixtures. Prediction: relative sign +1 for the edge-model electric pairs,
-1 for an independently implemented canonical-fermion control; neither product
may vanish. This is a test of statistics in the specified sector, not an imported
fermion construction or a derivation from the axiom. Outcome to be appended.

**P32C OUTCOME (appended after execution):** all 108 cases passed. Nonzero
unit-norm products have relative sign +1 in the edge model and -1 in the
canonical-fermion control; maximum edge-model error 2.23e-16. This is a bosonic
exchange-algebra baseline, not emergent fermions. Preregistration `5c2ef6a`;
data `reference/astra_session/data/p32c_exchange.json`.

## P32B — Conserving autonomous transport diagnostic (2026-09-20, Astra; before running)

The protocol and checked operator algebra are in `P32B_TRANSPORT.md`. On the
full Z2 edge spaces of a tetrahedron and a two-tetrahedron bipyramid, test the
explicitly POSTULATED Hermitian K=-0.2 sum W_ab (I-S_a S_b)/2. Predictions:
local defect occupations move, while total defect number, H0, flatness and norm
are conserved; the flat two-defect sector equals a hard-core boson configuration
graph. Controls and tolerances are fixed in that protocol. Persistence under a
number-preserving rule is not self-binding; this is not a hard-Gauss-law model
or a derivation of mobility/fermions from the axiom. Outcome to be appended.

**P32B OUTCOME (appended after execution):** all 16 pair preparations and 80
time samples passed. Local occupations changed by up to 0.6848/0.7166 in the
tetrahedron/bipyramid. Conservation/readout errors stayed below 4.30e-14,
and the two-defect sector matched the boson graph to 1.37e-16. The raw-string
control violates N/H0 conservation, and the projected rule changes individual
A_v as predicted. This proves transport under the declared extension; it does
not derive that law, binding or hard-Gauss-law matter. Preregistration `644e49a`;
data `reference/astra_session/data/p32b_transport.json`.

## P32 — The corrected rules, and why three dimensions (2026-09-20, Opus; registered before the re-runs)

**Axiom, as the user restated it:** causality travels to local effect, and it is always travelling
as a conserved quantity; a multidimensional causal structure can enumerate irreducible,
self-referential links.

**Corrections now in the kernel** (`src/constraintnet/defect.py`, `docs/CORRECTIONS_2026-09-20.md`):
local conservation is the projector A_v, flatness is B_f, H = −Σ A_v − Σ B_f, charge = a vertex
where A_v fails, flux = a face where B_f fails.

**Already measured while implementing (stated here so the re-runs are judged against it):**
A_v, B_f are exact commuting projectors (Z2, Z3, A4 patches, error 0.0); the tetrahedron-boundary
ground state is unique and gapped; a single edge's label disturbs exactly the closed ring of faces
around that edge, of size 6 or 4, on every interior edge of an n = 3 Kuhn ball.

**Predictions for the re-runs (P19–P31 repeated with the corrected rules).**
- **P32-1:** a single charge defect costs the same energy wherever it sits (translation-independent
  to 1e-12) and cannot be removed by any local unitary acting away from it.
- **P32-2:** a defect pair created by a string operator depends only on its endpoints: two different
  paths with the same ends give the same state to 1e-12.
- **P32-3:** with the hard constraints, a prepared defect survives open-wall release, unlike every
  soft-coupling candidate in P25–P31 (which lost 1–17 % per 400 ticks and emptied the box).
- **P32-4:** the old candidates fail *as matter* under the corrected rules: a compact dark loop
  carries no charge (A_v holds everywhere) and no net flux, so it is not a defect at all.

**Predictions for the dimensional step (registered now, before any d > 3 code exists).**
- **P32-5:** the Kuhn subdivision generalises: a d-cube splits into d! simplices, each a d-simplex
  whose rotation group is A_{d+1}; d = 3 gives A4 (ours), d = 4 gives A5, and the spin lift is the
  double cover (binary icosahedral for d = 4).
- **P32-6 (why three dimensions):** gauge flux is codimension-2, so it is a (d−2)-dimensional
  object: a loop in 3D, a sheet in 4D. Closed p- and q-dimensional objects link only when
  p + q = d − 1. Therefore **flux links flux only in d = 3**, while charge–flux braiding works in
  every d. If "irreducible self-referential links" means flux linking flux, three dimensions is the
  only dimension that supports it.
  - **Test:** build d = 4, enumerate the flux objects, and check that no pair of them has a
    non-trivial linking invariant while charge–flux braiding survives.
  - **Failure mode that would refute it:** a d = 4 flux sheet pair with non-trivial linking, or a
    3D flux pair with none.

### P32A — Executable charge-pair probe and constraint audit (2026-09-20, Astra; before running)

The newer handoff supersedes the earlier P25/P27 continuation. The three supplied
defect-kernel tests pass locally. The original P32 predictions above are retained.
Before claiming new stable matter, distinguish the implemented finite-penalty
Hamiltonian from a restriction to A_v=1: a state with A_v=0 is an excitation of
the former but is excluded by the latter. Gauge invariance is not the same
condition as the walk's already verified probability continuity equation.

**Fixed finite fixtures.** Full tetrahedron boundary for Z2 and Z3; one triangular
face with all three edges quantum for A4 (dimensions64,729,1728). Use every
nontrivial one-dimensional character: Z2 k=1; Z3 k=1,2; A4 1',1''.
The normalized uniform superposition of flat configurations is the vacuum.
Prepare a pair along each ordered pair of distinct vertices with the diagonal
unitary W_path=chi(product of oriented path labels). Compare the direct path
with each two-edge path via a third vertex. This covers only these electric
charge families, not all non-Abelian charges, flux sectors or 3D bound states.

**Predictions and readouts.**
1. Every prepared pair has A=0 exactly at its two endpoints, A=1 elsewhere,
   B=1 on every face, norm1, and energy E_vac+2, tolerance1e-12. All endpoints
   have the same cost; direct and alternate paths agree on this flat vacuum.
2. A one-edge unitary string continuation moves one endpoint to a neighbouring
   vertex with no change in pair energy. The inverse direct-edge string removes
   an adjacent pair. A unitary supported on an edge disjoint from the endpoints'
   stars cannot change their A readouts (check the opposite edge on the tetrahedron).
   These are explicit interventions, not autonomous motion or closed-system decay.
3. Evolve with the stated H, U(t)=exp(-itH), at t=0.37 and7.25, using commuting
   projector factors. Pair states change only by exp(-it(E_vac+2)); all local
   defect probabilities stay fixed. Check against a dense exponential for Z2.
   This is expected frozen-sector stability, not self-binding or propagation.
4. Applying A at either charged endpoint annihilates the pair state. Thus exact
   all-vertex Gauss enforcement would remove these bare charge states.
5. The all-identity *basis vector* is flat but has <A_v>=1/|G|, not1. A classical
   flat record or an old dark walker loop alone therefore cannot certify P32-4.

**Scope amendments before running.** P32-3 has no implemented open-boundary
channel for this new state space, and P32-4 has no old-to-new-state embedding.
Leave both untested, rather than importing the old walk's boundary operation or
calling a conserved defect projector a demonstrated lifetime. Since [H,A_v]=
[H,B_f]=0, this H alone cannot transport defects. A moving-matter claim will
require an explicit dynamics/charge-sector construction consistent with the axiom.

Code planned: `src/constraintnet/defect_ops.py`, `examples/p32_defects.py`.
Data planned: `reference/astra_session/data/p32a_defects.json`.

**P32A OUTCOME (2026-09-20, appended after running).** Preregistration and the
newer Opus handoff were committed in `e1daede` before the probe. All five bounded
predictions pass in 48 ordered endpoint/character cases (12 Z2, 24 Z3, 12 A4):

- Every pair has energy E_vac+2, A=0 only at the endpoints, and all B=1.
  Maximum energy residual: 1.09e-15; endpoint expectation error: 4.45e-16.
- Alternate paths agree exactly in the saved arrays. String reversal/continuation
  moves and annihilates pairs with error below 8.3e-16. Opposite-edge interventions
  preserve the original endpoints' star readouts.
- Evolution at both registered times gives only the predicted phase, with
  maximum error 7.2e-15. All defect locations remain fixed under H.
- Charged-endpoint projection norms are below 3e-16: a hard A_v=1 restriction
  excludes these bare states.
- The flat basis vector has <A_v>=1/2, 1/3, 1/12, respectively; flatness alone is
  not a charge-free quantum record.

These are explicit electric excitations and local string interventions in the
POSTULATED finite-penalty model, not moving or self-bound particles. The full
P32-1 claim about a lone charge is not tested by a neutral pair; P32-2 is
verified only for the specified flat, contractible fixtures and 1D characters.
P32-3 and P32-4 remain undefined/untested without an open channel and state-space
map. P32-5/6 are not run. `docs/DEFECT_AUDIT.md` records the interpretation and
dimensional caveats, with the original handoff claims preserved.

## P31 — Does a circulating structure work on the vacuum around it? (2026-09-20, Opus; registered before running)

**Why.** P29b/P30: circulation needs the spin-½ lift, and it is carried by the field around the
loop. Everything so far used *static* labels, which can neither respond nor carry energy away. The
self-binding question the user set ("self-binding has to be earned") needs a record that can move.

**Build (new).** `src/constraintnet/spin_record.py`, `SpinRecordWalk`: the P21 quantum record with
labels in 2T (24 elements, the double cover) and a spin-½ walker. The magnetic cost uses the spinor
character, so a face whose holonomy is the central element (a 2π rotation) costs the maximum 2 and
a flat face costs 0. Two quantum edges on the loop gives 576 record states; all other labels are
frozen flat. Couplings (λ_E, λ_B) = (0.1, 0.1), which keeps the record unfolded (W spans 0–20, so
0–2 rad/tick).

**Arms.** All in the closed n = 4 box, 400 ticks, then 200 ticks of open release.
- **C+**: the walker state that maximises loop circulation inside its degenerate family of the flat
  spin walk, times the record vacuum.
- **C0**: the state in the *same* family with the least circulation — same energy, same family,
  no flow. This isolates circulation from mere presence.
- **Q+ / Q0**: the same two states with the record frozen (U_rec = identity).
- **V**: record vacuum, no walker, as the energy reference.

**Measured.** Record energy ⟨λ_E L/8 + λ_B W⟩ − vacuum; record vacuum population; loop current bias;
on release, loop weight and bias retained, with escape bookkeeping.

**Predictions.**
- **P31-1 (exact):** unitarity and norm to 1e-12; the record vacuum is stationary with no walker to
  1e-12; λ_E = 0 reproduces the flat spin walk to 1e-12.
- **P31-2:** both walker arms *raise* the record energy (light heats the record, as in P21–P23):
  ΔE > 0 for C+ and C0.
- **P31-3 (the self-binding comparison; prior negative):** the two energies differ by no more than
  20 % of the larger, i.e. circulation as such does not dig its own well.
  - **Surprise criterion:** C+ lowers the record energy by ≥ 1.5× relative to C0, or drives it
    below the vacuum (ΔE < 0). Either would be the first sign of a structure working on its
    surroundings in its own favour.
- **P31-4 (does the record break the protection?):** the loop bias of C+ under the dynamic record
  decays with a half-life of fewer than 400 ticks, while the frozen-record control Q+ keeps it
  constant to 1e-6.
- **P31-5 (Kramers with a moving record, analytic-then-checked):** I expect the joint step to admit
  an antiunitary K (spinor reversal on the walker, conjugation with label inversion on the record)
  with K U K⁻¹ = U⁻¹ and K² = −1. If it holds, the protection survives a dynamic record and
  P31-4's decay must come from entanglement with the record rather than from lost degeneracy. No
  prior on which.
- **P31-6 (release):** C+ retains more loop weight than C0 on open release. No prior on size.

**Claim limits.** Two quantum edges, everything else frozen flat, a prepared state, one box. Nothing
about mass, charge or mobility follows, and a favourable energy comparison would be a hint of
self-binding, not a demonstration of it.

**P31 OUTCOME (2026-09-20, appended after the runs; predictions above untouched).**
Data: `reference/opus_session/data/p31_selfbind_n{4,6}.json`; code `examples/p31_selfbind.py`,
`src/constraintnet/spin_record.py`.

**Control bug found and fixed before the reported runs.** My first "least circulating" state was
taken as the other extreme of the ratio inside the degenerate family. Inside a Kramers pair those
extremes are +λ and −λ — the same circulation reversed, not circulation versus none. The correct
control is the time-reversal-symmetric combination ψ + K_sψ, which has exactly zero current
(measured |bias| ≤ 3e-16 at t = 0). The first run is discarded; nothing was reported from it.

| | C+ (circulating) | C0 (standing) | Q+ (frozen record) | Q0 |
|---|---:|---:|---:|---:|
| n = 4: bias 0 → 400 ticks | 0.606 → 0.551 | −0.000 → −0.028 | 0.606 → 0.595 | −0.000 → −0.001 |
| n = 4: record energy at 400 | 0.000806 | 0.000827 | 0.007591 | 0.007593 |
| n = 6: bias 0 → 400 | 0.639 → 0.632 | −0.000 → 0.019 | 0.639 → 0.613 | −0.000 → −0.003 |
| n = 6: record energy at 400 | 0.01207 | 0.01210 | 0.01693 | 0.01691 |

- **P31-1: PASS.** Record unitarity 2.2e-15, vacuum stationarity 1.7e-15, escape bookkeeping
  ≤ 1.8e-15.
- **P31-2: PASS.** Both walker arms raise the record energy (0.0008 at n = 4, 0.0121 at n = 6).
- **P31-3: prior-negative CONFIRMED, and sharply.** The circulating and standing states shift the
  record's energy by amounts differing by **2.5 % (n = 4) and 0.25 % (n = 6)**, far inside the
  registered 20 %. The surprise criterion is not met anywhere. **Circulation does no work on its
  surroundings**: the record responds to the walker's presence, not to its flow.
- **P31-4: FAIL as worded.** Under the dynamic record the bias decays slowly (−9 % at n = 4, −1 %
  at n = 6 over 400 ticks), not with a half-life under 400 ticks. The frozen control is not
  constant either (−2 % and −4 %), because the record vacuum is a superposition of configurations
  and the walker state is exact only in the flat one.
- **P31-5: INCONCLUSIVE, my fault.** The joint antiunitary I tested omitted the label transport
  (a placeholder was left in the operator), so its 4.7 mismatch shows nothing. Whether Kramers
  protection survives a dynamic record is **open**; the slow decay above is consistent with
  approximate protection but does not establish it.
- **P31-6: no signal.** On open release both arms empty the box (norm ≤ 1e-4 at n = 4 and ≤ 1e-5 at
  n = 6), as expected for states with only ~5 % of their weight on the loop. These are delocalised
  box eigenstates, not bound objects.

**Reading.** With the spin lift and a responsive record, a circulating structure still does not act
on its surroundings in its own favour, and nothing binds. Self-binding remains unearned, which is
the condition the user set. The one open thread is P31-5: whether the protection that makes the
circulation permanent survives a dynamic record.

## P30 — How much churn does the vacuum actually carry, and how much can circulation stand? (2026-09-20, Opus; registered before running)

**The user's question.** How much energy is the "disordered vacuum" of P29 carrying? With enough
ambient churn anything falls apart or comes together, and our objects are tiny: photons that repeat
at a comparable rate would be enormously high in frequency.

**First, the calibration (measured before registering this).** P29's random labels put **91.2 % of
faces curved**, mean Wilson cost 0.994 per face, order histogram 76 flat / 212 order-2 / 576
order-3 out of 864 faces. That is the **infinite-temperature limit** of the record: by construction
the energy fraction is 1.0, against the cooled vacua of P24a at 0.51, 0.22 and 0.14. So P29's
vacuum is not a physical vacuum at all; it is the maximally hot one, and the honest reading of P29a
is "in a maximally hot vacuum, A4 circulation is destroyed".

**This experiment: dilute the churn.** Each edge is flat with probability 1 − p and carries a
uniform non-identity label otherwise, for p ∈ {0, 0.003, 0.01, 0.03, 0.1, 0.3, 1}, three seeds,
closed n = 4 box, loops = triangle (L = 3) and axis square (L = 4), both internal spaces (A4 3-dim
irrep, and the 2T spinor lift).

**Measured.** Curvature density and mean Wilson cost (the vacuum's energy per face); the spectrum;
then, for tolerance windows δ ∈ {1e-10, 1e-6, 1e-4, 1e-3, 1e-2}, the maximum loop bias attainable
within any set of levels lying inside a window of width δ. A window of width δ means the
combination stays coherent for about 1/δ ticks, so δ converts directly into a **circulation
lifetime in ticks**.

**Predictions.**
- **P30-1 (descriptive):** curvature density rises with p roughly as 1 − (1 − p)³ (three edges per
  face), reaching 0.91 at p = 1. Mean Wilson cost per curved face ≈ 1.09 (mixing 1 and 4/3).
- **P30-2 (A4, exact degeneracy):** at δ = 1e-10 the maximum bias falls below 0.01 once p ≥ 0.01.
- **P30-3 (A4, quasi-stationary):** at δ = 1e-3, i.e. lifetimes of about 1000 ticks, the maximum
  bias stays ≥ 0.3 for p ≤ 0.03. Circulation in a nearly flat vacuum is long-lived even without
  spin-½. Medium confidence.
- **P30-4 (2T):** at δ = 1e-10 the maximum bias is ≥ 0.5 at every p, including p = 1: Kramers
  degeneracy is exact and disorder-proof.
- **P30-5 (scale, descriptive, no prior):** report the vacuum's magnetic energy per face at
  λ_B = 0.1 beside the box's lowest positive walk phase, so the ambient churn and the available
  quanta are in the same units (radians per tick).

**Claim limits.** Still closed-box kinematics with static labels; δ-windows are a proxy for
lifetime, not a decay measurement; no self-binding or mass follows.

**P30 OUTCOME (2026-09-20, appended after the run; predictions above untouched).**
Data: `reference/opus_session/data/p30_churn.json`; code `examples/p30_churn.py`; figure
`examples/p30_graphics.py` → `out/p30_churn.png`. Curvature is counted over the 120 faces whose
three edges all lie inside the closed walk.

| p | curved faces | mean Wilson / face | A4 forever | A4 ~1e3 ticks | A4 ~1e2 ticks | 2T (any) |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 0 % | 0 | 0.533 | 0.577 | 0.634 | 0.533 |
| 0.003 | 1.1 % | 0.011 | 0.609 | 0.638 | 0.676 | 0.595 |
| 0.01 | 5.3 % | 0.057 | 0.484 | 0.671 | 0.676 | 0.680 |
| 0.03 | 8.3 % | 0.086 | 0.450 | 0.464 | 0.643 | 0.720 |
| 0.1 | 25.3 % | 0.282 | **0.000** | **0.000** | 0.524 | 0.797 |
| 0.3 | 65.3 % | 0.724 | **0.000** | **0.000** | 0.385 | 0.794 |
| 1 | 92.5 % | 1.018 | **0.000** | 0.120 | 0.359 | 0.791 |

- **P30-1: PASS in form, with one correction.** Curvature follows 1 − (1 − p)³ closely from p = 0.03
  upward (8.3 % vs 8.7 %, 25.3 % vs 27.1 %, 65.3 % vs 65.7 %); at p = 1 it saturates at 92.5 %, since
  a random holonomy is the identity with probability 1/12. Mean Wilson per *curved* face is 1.10,
  against the predicted 1.09. The small-p points sit above the curve on 120 faces × 3 seeds.
- **P30-2: FAIL — circulation survives more churn than I expected.** I predicted exact-forever
  circulation would die by p ≥ 0.01 (5 % curvature). It survives at 5 % (0.48) and 8 % (0.45),
  though with seed variance (one of three seeds gives 0 at each). It dies completely at 25 %.
- **P30-3: PASS on the mean, not on the worst seed.** At ~1,000-tick lifetimes, A4 circulation holds
  0.46 at 8 % curvature (mean over seeds), but the weakest seed gives 0.04.
- **P30-4: PASS.** With the 2T lift, the strongest exact-forever circulation is 0.53–0.80 at *every*
  churn level, including 92.5 % curvature. Kramers degeneracy is exact and completely
  disorder-proof.
- **P30-5 (scale).** At λ_B = 0.1 the vacuum's magnetic energy per face runs from 0.001 to
  0.10 rad/tick across this range, against the box's lowest available quantum at 0.749 rad/tick
  (n = 4; it falls to 0.33 at n = 7). So even the maximally churned vacuum holds about a seventh of
  one quantum per face locally, while summing to ~11 rad/tick across the box.

**Reading (the user's question answered).**
- P29's "disordered vacuum" was the **maximally hot** one: 92 % of faces curved, the
  infinite-temperature limit, not a physical vacuum.
- Without the spin lift, circulation is a **lifetime** question: it is permanent below about 10 %
  curvature, lasts ~100 ticks at 25–90 %, and is gone as a permanent feature above ~10 %.
- With the spin lift it is **permanent at every churn level tested**.
- A quantum's frequency is set by how many cells its wavelength spans: 0.75 rad/tick is the lowest
  mode that fits in this box and 0.33 at n = 7. Long-wavelength ambient light is, in lattice terms,
  vanishingly slow, so a real vacuum around a small structure sits near the p ≈ 0 end — where even
  A4 circulation is permanent. The spin lift is what makes it survive a *hot* neighbourhood.

## P29b — Does the spin-½ lift restore circulation? (2026-09-20, Opus; registered before running)

**Why.** P29a (amended) shows that in the A4 3-dim irrep walk, stationary current lives only in
degenerate eigenspaces, and with generic labels there is essentially no degeneracy: 162 of 165
blocks are one-dimensional and the maximum loop bias over *every* eigenspace is ≤ 1.3e-11. With
identity labels, where symmetry makes every block degenerate, biases reach 0.65. The cause is the
antiunitary K with **K² = +1**: no protected degeneracy, so a current state is never forced.

**The physics this points at.** For a half-integer-spin time reversal, K² = −1 and Kramers' theorem
makes every level at least doubly degenerate, whatever the disorder. That is the working statement's
open item A: lifting the labels to the binary tetrahedral group 2T, the double cover of A4, acting
in its 2-dim spinor representation. So the question "can matter carry circulation in a disordered
vacuum?" turns into "does matter need spin-½?".

**Setup.** Same closed Kuhn box n = 4 and the same four loops. The walk keeps its coin and ring
weights, but the internal space is 2-dimensional and each edge carries a label drawn from 2T's 24
unit quaternions in the spinor representation, with the reverse arc carrying the adjoint. Labels:
identity, and 10 random draws, matching P29a. K_s ψ(w→v) = ρ(A_wv)·(iσ_y)·conj(ψ(v→w)).

**Predictions.**
- **P29b-1 (exact):** K_s U = U⁻¹ K_s to 1e-12 and **K_s² = −1** to 1e-12; the walk stays unitary.
- **P29b-2 (Kramers):** for every random label draw, every eigenvalue block has even dimension, and
  the number of distinct blocks is at most half the dimension. No one-dimensional blocks at all,
  against 162 of 165 in P29a.
- **P29b-3 (circulation returns):** in every random draw, at least one loop has a maximum eigenspace
  bias ≥ 0.1, against ≤ 1.3e-11 in P29a. This is the registered discriminator.
- **P29b-4 (the tail's cost):** the maximum-bias state has loop weight < 0.5, so circulation is
  still paid for in delocalisation, as P29a-3′ asked.
- **P29b-5 (exploratory):** record the best (loop weight × |bias|) per loop and draw, and the share
  of |J| on the loop against off it. No prior.

**Claim limits.** This is a kinematic test of which internal space permits stationary circulation.
It shows nothing about self-binding, mass, charge, or exchange statistics, and 2T labels are not yet
justified by the axiom — only by this requirement. If P29b-3 passes, the claim is "circulation in a
disordered vacuum requires the spin-½ lift", not "we have an electron".

**P29a OUTCOME (2026-09-20, amended protocol; the v1 run is superseded and kept as
`p29a_tail.json`).** Data: `reference/opus_session/data/p29a_tail_v2.json`; code
`examples/p29_tail.py`.

- **P29a-1: PASS.** Divergence ≤ 1.6e-12 for every state examined; the walk is exactly unitary.
- **Symmetry (DERIVED, verified):** K U = U⁻¹ K to 1.4e-15 and K² = +1 to 1.8e-15, with
  K ψ(w→v) = ρ(A_wv)·conj(ψ(v→w)).
- **P29a-2′: PASS.** Every one-dimensional eigenspace has |bias| ≤ 1.3e-11. Circulation needs
  degeneracy.
- **P29a-3′ and -4′: not reachable with generic labels, and that is the finding.**
  - With **identity labels** (39 eigenspaces, none one-dimensional) circulation is easy: maximum
    loop bias 0.652, and the best (loop weight × |bias|) is 0.234, on the L = 5 cycle with loop
    weight 0.516.
  - With **random labels** the spectrum splits: 162 of 165 eigenspaces are one-dimensional, and the
    maximum bias over *every* eigenspace, on every loop and every draw, is **1.3e-11**. There is no
    stationary circulation at all to pay a localisation cost for.
- **Reading.** Because K² = +1, every eigenspace admits a current-free basis, so circulation is
  never forced; it survives only where symmetry supplies degeneracy. A disordered vacuum destroys
  it. This is the walk's version of the standard result that time reversal forbids current in
  non-degenerate stationary states.

**P29b OUTCOME (2026-09-20, appended after the run; predictions untouched).**
Data: `reference/opus_session/data/p29b_spin.json`; code `examples/p29b_spin.py`.

- **P29b-1: PASS.** The spinor walk is unitary to 4.4e-16, K_s U = U⁻¹ K_s to 9.9e-16, and
  **K_s² = −1** to 5.0e-16.
- **P29b-2: PASS, with one bookkeeping note.** No one-dimensional eigenspaces at all (against 162
  of 165 for A4): 54 Kramers pairs plus three flat bands, in every draw. The "odd blocks" counted in
  the raw output are the π flat band split across the −π/+π wrap (63 + 79 = 142); with the wrap
  handled, every block has even dimension.
- **P29b-3: PASS, decisively.** The maximum loop bias per draw is between **0.76 and 0.93**, against
  ≤ 1.3e-11 for A4 labels. Mean maxima by loop: triangle 0.79, axis square 0.71, diagonal square
  0.67, L = 5 cycle 0.65. Divergence 5.3e-16.
- **P29b-4: PASS.** The maximum-bias states are strongly delocalised: loop weight ≤ 0.085, weight
  within one hop of the loop 0.51–0.91, and only ≤ 0.16 of the total |J| sits on the loop's own
  edges. **The circulation lives in the tail, not in the core** — which is the shape the user
  argued for from real matter.
- **P29b-5 (exploratory):** the best (loop weight × |bias|) is 0.061, well below the identity-label
  A4 value of 0.234. Spin-½ buys circulation in a disordered vacuum, not a compact circulating core.

**Reading, and the claim this licenses.** In this architecture, a stationary state can circulate in
a disordered vacuum only if the internal space is the spin-½ lift (2T), because only then does
Kramers degeneracy survive disorder. Circulation and confinement remain in tension: what circulates
is the field around the loop. This says nothing yet about self-binding, mass or charge, and 2T
labels are still motivated only by this requirement, not by the axiom.

## P28 — What a compact loop can do instead of circulating (2026-09-20, Opus; analytic first, registered before computation)

**Where this comes from.** P27 and the §15 theorem close off probability circulation for a state
confined strictly to a loop. The user's reading of what is left: the several internal states can be
taken either as a wavefunction over them, or as a constant, invisible transition between them. P28
derives the answer first and then checks it.

**Derivation (DERIVED, in the declared walk; to be verified numerically).**
Take a state supported only on a cycle v₀ … v_{L−1}, with every cycle vertex also carrying unused
arcs of positive weight. Write a_k for the amplitude on the forward arc v_k → v_{k+1} and c_k for
the backward arc.
1. Keeping the unused arcs empty forces the coin overlap to vanish at every cycle vertex, so the
   coin acts as **−1** on the state. This needs √(w_k)·a_k + √(w_{k−1})·c_{k−1} = 0, i.e. the
   amplitudes scale as 1/√weight. Equal weights are *not* required.
2. The eigen-equation then gives, on each edge, both
   −ρ_k a_k = e^{iθ} c_k and −ρ_k⁻¹ c_k = e^{iθ} a_k, hence **e^{2iθ} = 1**:
   **a compact loop state can only have walk phase θ = 0 or θ = π.**
3. Going once around, a_0 = e^{−iLθ} H a_0 with H the ordered loop holonomy, so
   **H a₀ = e^{iLθ} a₀**:
   - θ = 0 needs a +1 eigenvector of H (every A4 element has one);
   - θ = π needs H a₀ = (−1)^L a₀.
4. In A4's 3-dim irrep the eigenvalues are (1,1,1) for the identity, (1,−1,−1) for the three
   order-2 elements, and (1, ω, ω̄) for the eight order-3 elements. Therefore:
   - **even L:** both phases exist, on the same +1 eigenvectors;
   - **odd L:** θ = π exists only when H is an order-2 element, and then in a 2-dim space.

**Predictions.**
- **P28-1:** over 20 random label draws per loop, every eigenstate supported on the loop has phase
  0 or π to 1e-12. The compact invariant subspace is found exactly (null space of the escape map,
  then diagonalised), not by construction, so the claim is about *all* of them.
- **P28-2:** its dimensions match step 4 exactly: dim(θ = 0) = dim ker(H − I) and
  dim(θ = π) = dim ker(H − (−1)^L I).
- **P28-3:** √(w_k)·|a_k| is constant around the loop, so mixed-weight loops (triangles, with two
  ring-6 edges and one ring-4) carry compact states. P19's equal-weight squares were a special case.
- **P28-4:** every compact eigenstate has zero loop current, ≤ 1e-12 (the §15 theorem).
- **P28-5 (the user's question, made sharp):** an equal superposition of the θ = 0 and θ = π states
  on the same loop is **exactly 2-periodic**: U²ψ = ψ to 1e-12. Its instantaneous current bias is
  non-zero, and its mean over any two consecutive ticks vanishes to 1e-12. Probability sloshes
  back and forth between the two directions of each edge, with no net transport.
- **P28-6:** for an odd loop whose holonomy is order-2, the θ = π state's internal vector returns
  with a minus sign after one traversal: ⟨a₀, H a₀⟩/|a₀|² = −1 to 1e-12. Two traversals are needed
  to come back. No spin claim is attached to this: it is a transport period, not an exchange
  statistic or an angular momentum.

**Loops:** a triangle (L = 3, mixed weights), the axis square (L = 4, ring-6), the face-diagonal
parallelogram (L = 4, ring-4), and an odd cycle of length 5 if the mesh provides one. Closed box,
n = 4, flat vacuum with classical random A4 labels; no quantum record is needed for the structure.

**Claim limits.** These are kinematic statements about compact states in the flat walk. They do not
show binding, mobility, charge, spin, or an electromagnetic field, and the no-current theorem still
applies to every single eigenray.

**P28 OUTCOME (2026-09-20, appended after the run; predictions above untouched).**
Data: `reference/opus_session/data/p28_compact.json` (84 rows: 4 loops × flat labels + 20 random
label draws); code `examples/p28_compact.py`. The compact invariant subspace is found by iterating
S ← {v ∈ S : Uv has no weight off the loop and stays in S} to a fixed point, so the statements
cover *all* compact states, not just constructed ones.

- **P28-1: PASS.** Every compact eigenstate found has phase exactly 0 or π. Worst eigen-residual
  7.1e-15.
- **P28-2: PASS.** Dimensions match ker(H − I) and ker(H − (−1)^L I) in all 84 rows.
  - Odd loops: θ = π states appear only for order-2 holonomies (13 of the 42 odd-loop rows), always
    in a 2-dim space; never for orders 1 or 3.
- **P28-3: PASS.** √(w_k)·|a_k| is constant around each loop to 6.6e-15. Triangles with mixed
  ring-6/ring-4 weights carry compact states, so P19's equal-weight squares were a special case.
- **P28-4: PASS.** Every compact eigenstate's loop current bias is ≤ 3.5e-15.
- **P28-5: PART PASS, PART FAIL — and the failure is the interesting half.**
  - Exact 2-periodicity: PASS. U²ψ = ψ to 3.1e-15 for the 0/π superposition, in all 55 rows where
    both phases exist.
  - Two-tick mean current: PASS, ≤ 4.0e-16.
  - **Non-zero instantaneous current: FAIL.** The bias is zero at *every* tick (≤ 1e-16), not just
    on average.
  - What the superposition does instead: the weight alternates between the two interleaved halves
    of the loop's arcs, e.g. 0.25 on four arcs at even ticks and on the complementary four at odd
    ticks, with forward and backward arcs always carrying equal weight. It is a standing wave of
    two counter-propagating halves, not a circulation.
- **P28-6: PASS.** On odd loops with an order-2 holonomy, the θ = π state's internal vector returns
  with exactly −1 after one traversal (all 13 rows), so it takes two traversals to return. On
  even loops the return is +1.

**Reading.**
- The user's two readings — a wavefunction over the internal states, or a constant invisible
  transition between them — are the same object in two bases, and the model makes that exact: a
  compact loop admits only two phases, 0 and π, and their superposition is exactly 2-periodic.
- Neither reading yields directed probability circulation. The no-current result is stronger than
  §15's theorem: it now covers these time-dependent compact superpositions too.
- What *is* directed, and invisible to probability, is the internal transport: a minus sign per
  traversal on an odd loop with order-2 holonomy, i.e. a two-traversal return. That is a transport
  period, not spin, charge or angular momentum.

## P27 — Vacuum controls and operational current (2026-09-20, Astra; registered before running)

**Question.** Does P26 improve substantially over an already calm seed, and is
there directed probability transport around the cycle? P26's outcomes are known
and motivate this new test; these are new predictions, not independent prior
predictions of the P26 data.

**Unchanged model.** Same L4 geometry, n=5 and n=6, three quantum A4 edges,
couplings (0.1,0.1), all other edges flat. No new dynamics or expansion rule.

**Arms.**
- Cv: compatible vacuum-coefficient seed, sum_c vac_c |c> DF_c. This is generally
  entangled: its reduced record is NOT automatically the pure vacuum. Measure its
  actual vacuum population.
- Iv: imprinted flat dark-loop state times the pure record vacuum.
- F: reproduce P26's Gibbs-seed-1, fraction-0.14, T=256 vacuum-phase filter.
  Report normalized overlaps with Cv and Iv as well as P26 reproduction error.
- D: decoupled flat-walker Iv, an exact stationary ray at the record-vacuum phase;
  check its one-step residual as the known kinematic persistence control.

All three coupled arms get full closed-U target/best-phase residuals, normalized
loop weight and record vacuum population. Release them into the same open boxes
for128 ticks, using P26's isometric embedding and t=0,32,64,128 readouts. Run all
arms even if a prior fails. Keep P26's comparison data unchanged.

**Current (DERIVED for this declared walk).** Let q(v,w)=||(C psi)_(v->w)||^2,
tracing over all internal and record indices, and J(v,w)=q(v,w)-q(w,v), with
missing boundary incoming arcs assigned zero. The coin conserves vertex norm;
transport and record motion conserve each shifted arc's norm. Hence the exact
continuity identity is rho_next(v)-rho(v)=-sum_w J(v,w). Local internal frame
rotations preserve these norms. This is probability current, not electric
current or angular momentum. Unit tests check continuity for both boundary modes,
frame invariance, and an explicitly directed positive control with bias +/-1.

For each open tick, record the four oriented loop-edge currents and traffic
sum_loop(q_forward+q_reverse). Report total signed crossings / total traffic
over ticks0..127, and separately the first/last64 ticks. Orientation reversal
changes only the sign. Also report the largest individual instantaneous bias
and conservation errors; a transient bias is not persistent circulation.

**Predictions (priors, before any P27 campaign data).**
- P27-1: reproduction of P26 F weight, loop weight and full-U residual to1e-10;
  D residual <1e-12; local continuity and cumulative escape errors <1e-10.
- P27-2: each vacuum seed has a target residual <=20% of the noisy P26 raw seed's
  target residual, in both boxes.
- P27-3 (calm selection explains much of P26): F's128-tick loop-weight loss is
  >=half the smaller loss of Cv and Iv in each box. A failure means an additional
  finite-window benefit beyond these calm controls, not a self-binding proof.
- P27-4: F has squared overlap >=0.95 with at least one vacuum seed in each box.
- P27-5: Cv and Iv have initial edge currents <1e-12 in magnitude on the loop.
  Branchwise dark states have opposite transported amplitudes and equal edge
  norms. Subsequent currents and F's current are exploratory, with no direction
  or magnitude prior; every readout is retained.

**Claim limits.** Prepared, pinned partial-record states; finite128-tick loss,
not an asymptotic lifetime. If currents cancel, localization must not be called
directed circulation. Even nonzero probability current alone cannot establish
the target's orientation cycle, spin, charge, or electromagnetic field structure.
Vacuum-state filtering is preparation, not a cooling mechanism.

Code: `examples/p27_vacuum.py`, `src/constraintnet/current.py`.
Planned data: `reference/astra_session/data/p27_vacuum_n{5,6}.json`.

**P27 analytic companion (added while the registered campaign is running, before
the companion computation; campaign protocol/predictions above unchanged).**
For an exact joint eigenray supported only on a loop, assume each loop vertex
has an available exit arc outside that support with positive coin weight. No
amplitude may arrive on a nonloop arc after a tick. Unitary shift/record transport
on each arc is invertible, so the coined amplitude on each exit must vanish.
Its initial amplitude is zero, hence the local coin overlap must vanish. The
coin is therefore minus the identity on the supported state. Stationarity of
each arc's norm then gives equal probabilities on reverse arcs: J=0. This is a
conditional no-current result for strictly compact eigenrays, not for states
with spatial tails, time-dependent superpositions, or electromagnetic fields.

Before checking: construct all twelve one-quantum-edge A4 branch dark loops with
electric coupling zero and magnetic coupling0.1. Each is an exact joint eigenray
at its branch's magnetic phase. Predict eigen-residuals and loop-edge currents
<1e-12, with an exit at every loop vertex. This checks the analytic implication
on explicit nontrivial transport branches; the algebra supplies the general proof.

**P27 OUTCOME (2026-09-20; run by Astra, appended by Opus from Astra's archived data;
predictions above untouched).**
Astra registered and ran P27 but stopped before writing it up. The numbers below are
recomputed from `reference/astra_session/data/p27_vacuum_n{5,6}.json` via
`examples/p27_summary.py` (figure: `out/p27_vacuum.png`). Both runs report
`status: complete`.

| | n = 5 | n = 6 |
|---|---:|---:|
| Full-U target residual, Cv | 0.0741980 | 0.0741980 |
| Full-U target residual, Iv | 0.1259575 | 0.1259575 |
| Full-U target residual, F (P26 filter) | 0.0056421 | 0.0056741 |
| 128-tick loop loss, Cv | 0.0198427 | 0.0091090 |
| 128-tick loop loss, Iv | 0.0192988 | 0.0088427 |
| 128-tick loop loss, F | 0.0210625 | 0.0108675 |
| F loss / best vacuum-seed loss | **1.0914** | **1.2290** |
| Squared overlap of F with Cv / Iv | 0.9554 / 0.9804 | 0.9389 / 0.9640 |
| Integrated current bias (all arms) | ≤ 5.7e-6 | ≤ 8.5e-7 |

- **P27-1: PASS.** P26 is reproduced exactly (filtered weight and loop weight to 0; residual to
  6.1e-18 and 9.5e-17). The decoupled control D is an exact eigenray: residual 3.1e-15 at the
  record-vacuum phase −0.2893245638 rad/tick. Continuity errors ≤ 9.0e-16, escape bookkeeping
  ≤ 6.8e-14.
- **P27-2: FAIL.** The registered bound was 20 % of the raw seed's residual (0.3138), i.e. 0.0628.
  Cv is at 23.6 % and Iv at 40.1 %. Preparing a calm seed does not by itself give a near-eigenray.
- **P27-3: PASS, in the direction that undercuts P26.** F's release loss is not merely at least
  half the better vacuum seed's: it is **larger** than both, by 9 % (n = 5) and 23 % (n = 6). The
  P26 improvement over the *noisy* seed is explained by selecting a calmer component, and the
  filtered candidate is beaten by simply starting calm.
- **P27-4: PASS.** F overlaps a vacuum seed with squared overlap 0.94–0.98, so F is largely the
  same object as the plain calm seeds.
- **P27-5: PASS.** Initial loop currents vanish at 1e-12 or below, as the branchwise dark states
  require. Over 128 open ticks every arm's integrated bias stays at 1e-6 or below, with the
  largest single-tick bias 1.9e-4. **No directed circulation is seen in any arm.**
- **Reading.**
  - The dressed-loop candidate of P26 is not a distinct bound object; it is a calm prepared loop,
    and a slightly worse one than the plain calm seeds.
  - The current readout is consistent with the compact-eigenray theorem (DYNAMICS_DESIGN §15):
    a state confined strictly to the loop, with exits available, carries exactly zero net current.
  - Consequence for the working statement: "matter is trapped circulation" cannot hold in the
    strict form. Perfect trapping excludes probability circulation here. A matter candidate must
    have support outside the loop, be a time-dependent superposition, or carry its circulation in
    an internal variable rather than in probability flow.

## P26 — Phase-resolved dressed-loop diagnostic (2026-09-20, Astra; registered before running)

**Question.** Does finite spectral filtering of P25's compatible loop isolate a
more stationary, still localized joint walker-record state? This is a bounded
search in the existing POSTULATED partial-record model, not a test of spontaneous
formation, mobile matter, or fermionic statistics.

**Analytic checks (DERIVED, checked against exact small spectra in
`tests/test_phase_filter.py`).** For unitary U and z = exp(i theta), define
F_T = (1/T) sum_{t=0}^{T-1} z^(-t) U^t psi. Then
(U-z)F_T = z (z^(-T) U^T psi - psi)/T. Consequently the normalized target
residual is at most 2 ||psi|| / (T ||F_T||). A shrinking raw residual alone is
built into the algorithm. The finite-T filter weight is not an exact spectral
projection probability. An unphased average selects eigenvalue 1; a stationary
ray with nonzero phase can be completely missed.

**Protocol fixed before data.**
- P25 L4 loop, same prepared coordinates, first three loop edges quantum A4;
  all other edges frozen flat. Couplings (0.1, 0.1).
- Compatible branchwise seed from P25, Gibbs proxy-energy fraction 0.14, seed 1.
  This retains P25's unproven bath provenance; it does not repair it by assumption.
- Closed boxes n=5 and n=6, keeping the loop fixed while extending the boundary.
- Two phases only: zero, and the eigenphase of the isolated record vacuum.
  The latter is fixed from U_rec before filtering, not fitted to a favorable result.
- Cesaro windows T=64,128,256. Report full-U target and best-phase residuals,
  filter weight, loop's eight-arc weight, graph-distance distribution from its
  vertices, record configuration probabilities, vacuum population and Wilson mean.
  Measurements use topology and record amplitudes, not coordinates.
- Open-wall release for 128 ticks of BOTH normalized T=256 filters and the raw
  compatible seed. Isometrically embed all closed arcs and zero newly added arcs;
  do not project onto the loop. Save t=0,32,64,128 and escape bookkeeping.
- Controls: frozen compatible seed is a full-walk eigenstate at phase zero;
  flat, decoupled walker loop times record vacuum is an eigenstate at the vacuum
  phase. Check both directly; its filter weights also have an exact geometric-sum
  expression. These are positive controls for known kinematic trapping.

**Predictions (priors).**
- P26-1: both control residuals <1e-12; open escape accounting error <1e-10.
- P26-2: vacuum-phase T=256 target residual <=1/4 the raw seed's target residual,
  with normalized loop weight >=0.80, in both boxes. A pass is only a useful
  filtered candidate, not an eigenstate proof.
- P26-3: its T=256 loop weights differ by <=0.05 between boxes; after open release,
  its loop-weight loss from t=0 to128 is <=1/2 the raw seed's loss in each box.
- P26-4: vacuum-phase filtered weight exceeds zero-phase filtered weight at256
  in both boxes. No all-phase exclusion follows if neither filter succeeds.

**Claim gate.** No exact dressed eigenstate claim unless the full-U normalized
residual is <1e-8 and localization survives boundary and release controls.
Even a pass leaves the three quantum edges pinned and most of the record frozen;
remote flat-cycle eigenstates exist in this model. A stationary joint state's
record marginal is stationary under the coupled dynamics, but need not be a fixed
point of the separate radiative-cooling channel. P25's bath-provenance question
and the Williamson–van der Mark reproduction gates therefore remain separate.

Code: `examples/p26_dressed.py`, `src/constraintnet/phase_filter.py`.
Planned data: `reference/astra_session/data/p26_dressed_n{5,6}.json`.

**P26 OUTCOME (2026-09-20, appended after both runs; predictions untouched).**

The protocol and executable were committed as `29a2f51` before measurement.
Both runs completed. Summary: `reference/astra_session/data/p26_summary.json`;
figure: `python examples/p26_summary.py` produces `out/p26_dressed.png`.

| Vacuum-phase filter, T=256 | n=5 | n=6 |
|---|---:|---:|
| Filtered weight before normalization | 0.592919 | 0.590157 |
| Normalized loop weight | 0.996826 | 0.980437 |
| Full-U target residual | 0.00564205 | 0.00567408 |
| Best-phase residual for the same vector | 0.00535443 | 0.00541077 |
| Record-vacuum population | 0.994562 | 0.977631 |
| Loop-weight loss in 128 open ticks | 0.0210625 | 0.0108675 |
| Raw seed's loop-weight loss in 128 open ticks | 0.0671139 | 0.0462413 |
| Filtered/raw loss ratio | 0.313833 | 0.235018 |

- **P26-1: PASS.** Control residuals <=3.2e-15; maximum escape accounting error
  4.14e-14 across all six release arms.
- **P26-2: PASS.** Raw target residual is 0.313833 in both boxes; filtering lowers
  it by about 55 times while preserving >=98% normalized loop weight.
- **P26-3: PASS.** Loop weights differ by 0.0163894; the filtered/raw release-loss
  ratios are 0.314 and 0.235, below the registered 0.5 threshold. Final absolute
  loop weights after release are 0.975763 and 0.969569, against raw 0.932886 and
  0.953759. The windows and release lengths are finite; no lifetime fit was made.
- **P26-4: PASS.** Zero-phase filtered weights are only 0.000115712 and
  0.000122831, about 4,800–5,100 times below the vacuum-phase weights. Their
  normalized target residuals remain 0.437 and 0.428.
- **Exact-eigenstate gate: NOT PASSED.** Residuals remain over five orders of
  magnitude above 1e-8; even fitting the best phase to each final vector does not
  change that verdict. There is no exact dressed eigenstate demonstrated here.
- **Unregistered interpretation/readout:** filtering selects a record almost in
  its isolated vacuum mode (97.8–99.5%, versus the seed's 60.3%). The record's
  diagonal one-tick L1 changes are 0.000603 and 0.000701, not zero. Improvement
  over the noisy seed cannot be attributed specifically to self-confinement;
  comparison with an unfiltered vacuum seed is still needed, and the decoupled
  flat-loop control is already exactly persistent.

**Reading:** a substantial, highly localized, more persistent prepared component
exists at the record-vacuum phase. This is a useful candidate and a correction to
an eigenvalue-1-only search. It is not evidence yet of autonomous binding, mobile
matter, directed circulation, the Williamson–van der Mark structure, or a bath
produced by radiative cooling. No new dynamics or expansion rule was introduced.

## P25 — Seeding patterns in a compatible cooled bath (2026-09-20, Opus; registered before running)

**The user's framing (verbatim intent):** "with enough noise this happened somewhere", not a
reproduction of the Big Bang. We only make sure the pattern is not imprinted on something
fundamentally incompatible with its existence. Whether it *continues* to persist is a separate
question, and it is the one measured here.

**Bath (the cooled vacuum at freeze-out).**
- **Couplings:** unfolded, (λ_E, λ_B) = (0.1, 0.1).
- **Energy:** the record energy fraction is fixed at P24a's n = 7 point:
  (E − E_vac) = 0.14 × (E_∞ − E_vac), just below the magnetic freeze-out.
- **Form: Gibbs, ρ ∝ exp(−β H_rec).** β is fixed by that energy. This form is POSTULATED;
  checked in P25-2.
- **Bath samples:** typical pure states |b⟩ = Σ_i √p_i e^{iφ_i} |ε_i⟩ with seeded random phases
  (seeds 1, 2, 3).
- **Light bath:** not included. The walker is a single-particle wave, so bath light and pattern
  would share one amplitude. The light's effect enters only through the record statistics it set.
- **Far edges:** flat. At 0.14, curvature is sparse, so this is a stated simplification.

**Compatible provenance (the user's condition).**
- The pattern is instantiated *per record branch*: Ψ = Σ_c b_c |c⟩ ⊗ |DF_c⟩.
- DF_c is the compact loop state built with branch c's own transports. Its internal vector is
  the fixed vector of branch c's loop holonomy that lies nearest the reference vector.
- Every A4 holonomy fixes a vector (in the 3-dim irrep), so no branch is incompatible. The pattern
  simply takes the form the local chop allows.
- **Control, "imprinted":** Ψ = |b⟩ ⊗ |DF_flat⟩, the flat-vacuum form stamped on regardless.

**Patterns (both verified compact eigenstates of the flat walk, residual 6e-17):**
- **L6:** an axis square, 4 ring-6 edges (60° pivots).
- **L4:** a face-diagonal parallelogram, 4 ring-4 edges (90° pivots).
- In both, 3 of the 4 loop edges carry quantum labels.

**Arms (per pattern).**
- **V:** record vacuum ⊗ DF_flat.
- **C:** compatible, × 3 bath seeds.
- **I:** imprinted, × 3 bath seeds.
- **Qc:** compatible with a quenched record, seed 1.

**Run settings.** Open walls, n = 6, T = 600.

**Measured.** Weight on the loop's 8 arcs, W_loop(t). Norm left in the box.

**Predictions (priors).**
- **P25-1 (exact):**
  - DF_c is stationary under the frozen-branch walk for every branch (residual < 1e-12);
  - Ψ is normalised;
  - escape bookkeeping holds to 1e-12.
- **P25-2 (bath provenance):** one flash of lowest-band light at n = 7, run on a Gibbs bath
  sample, changes its energy by |ΔE| ≤ 25 % of the vacuum-point drift at n = 7 (1.26e-5). The
  Gibbs bath is then near-stationary under the light that made it.
- **P25-3 (compatibility matters):** at t = 50, the loop weight lost in C is ≤ ½ the loss in I
  (seed-averaged, both patterns).
- **P25-4 (persistence):** C keeps W_loop(T) ≥ 0.8 for both patterns. V keeps ≥ 0.95. No prior on
  L6 against L4 (exploratory).
- **P25-5:** C against Qc differs by < 10 % in W_loop(T), since the record at λ = 0.1 moves slowly.

**P25 OUTCOME (2026-09-20, appended after the run; predictions above untouched).**
Data: `reference/opus_session/data/p25_{L6,L4,provenance}.json`; code `examples/p25_seeded.py`;
figure `examples/p25_graphics.py` → `out/p25_seeded.png`.

- **P25-1: PASS.** DF_c is stationary in every one of the 1728 branches (residual 2e-16);
  Ψ is normalised; bookkeeping holds to 2e-13.
- **P25-2: FAIL.**
  - Single-flash drifts on two Gibbs bath samples were −1.6e-5 and +4.4e-5, against the
    registered bound of 3.2e-6.
  - The sign depends on the sample's random phases, and the mean (+1.4e-5) is slightly heating.
  - So the Gibbs form of the bath is *not* shown to be the state the light would leave. Two
    samples cannot resolve the ensemble drift, and the true stationary state need not be Gibbs.
    The bath's provenance is therefore approximate.
- **P25-3: PASS.** Loop weight lost by t = 50 is 0.43 × the imprinted loss for L6
  (0.024 vs 0.055) and 0.44 × for L4 (0.015 vs 0.034). Imprinting gives an immediate shock
  (about 4.5 % in the first ticks); compatible seeding does not.
- **P25-4: PASS for C, FAIL for V.**
  - C keeps 0.83–0.85 (L6) and 0.87–0.88 (L4) at T.
  - V keeps 0.926 (L6) and 0.941 (L4), below the registered 0.95. Even the calm quantum vacuum
    wears the loop down slowly.
- **P25-5: FAIL, decisively.** The compatible pattern in a *frozen* bath (Qc) keeps *exactly* 1.0000
  (every branch is an exact eigenstate), against 0.83–0.88 with a moving record. **All of the erosion
  comes from the record's own motion.**
- **Unregistered readouts:**
  - Compatible and imprinted cross near t ≈ 300. Afterwards the compatible form erodes slightly
    *faster*: its internal orientation is branch-dependent, so every record transition
    mismatches it, whereas the imprinted form is the same in every branch.
  - L4 (90° pivots, ring-4) outlasts L6 (60° pivots, ring-6) in every arm.
- **Reading:**
  - Compatible provenance removes the birth shock, as intended.
  - Persistence then depends on whether the pattern can *co-move* with its record. A pattern that
    is an eigenstate of the frozen record but not of the moving one erodes at about 2–3e-4 per tick.
  - A persistent pattern would be a *joint* eigenstate of loop plus record (a dressed loop). That
    is the next thing to look for.

## P24a — Redshift proxy: does colder light hold the record calmer? (2026-09-20, Opus; registered before running)

**Where this came from.** P23d′ (seen) moved the equilibrium E* to about 0.5 × E_hot using
narrow light from the lowest positive band. The lowest walk phase falls as the box grows:
0.523 at n = 5, 0.401 at n = 6, 0.325 at n = 7. A bigger box is the static stand-in for
expansion: its light is redshifted. This is not yet expansion *dynamics*.

**Setup.**
- Unfolded couplings (0.1, 0.1); the quantum square at the box centre; open walls; one flash per
  ladder point.
- The flash is spectrally filtered onto the lowest positive band: a Gaussian time window, width 60
  ticks, on the flat closed walk. The eigen-residual is ≤ 2e-5.
- The same 7-state θ-ladder as P23.
- n = 5 (a cross-check of P23d′), 6 and 7.

**Predictions.**
- **P24a-1:** n = 5 reproduces P23d′ (a crossing between θ = π/4 and π/3).
- **P24a-2:** E*/E_hot falls with n, i.e. as the light's phase falls.
- **P24a-3 (stretch):** at n = 7 the crossing lies below θ = π/4.

**P24a OUTCOME (2026-09-20, appended after the run).**
Data: `reference/opus_session/data/p24a_redshift_n{5,6,7}.json`; figure `examples/p23_graphics.py` →
`out/p23_p24a_radiative.png`.
- **P24a-1: PASS.** At n = 5, E*/E_hot = 0.51 (ΔE = +3e-7 at θ = π/4, −9e-6 at π/3). This matches
  P23d′.
- **P24a-2: PASS.** E*/E_hot = 0.51, 0.22, 0.14 for light at ω₀ = 0.523, 0.401, 0.325.
- **P24a-3: PASS.** At n = 7 the crossing lies between θ = π/12 and π/6.
- **Reading:** colder, redshifted light holds the record at a lower energy.
  - The steep drop between n = 5 and n = 6 comes as ω₀ falls below the magnetic gap
    (λ_B·W ≈ 0.4–0.6 for one flip). The light can no longer create magnetic excitations, so they
    *freeze out*.
  - Caveat: the record's exact vacuum population still falls slightly per flash at every point
    (dP_vac < 0). The light can still make electric excitations (gap about 0.1). So "calmer" here
    means lower energy, not more vacuum.
- **This is a static proxy** (bigger box = redshifted light), not expansion dynamics.

## P23 — Radiative cooling: can a flood of light calm a hot record? (2026-09-20, Opus; registered before running)

The user's order is radiative first, then expanding, then both. P22 showed that one flash cannot
cool the record; here the light is many flashes in sequence.

**Method (exact in expectation).**
- **Box and record:** an open Kuhn box, n = 5 (896 arcs, 338 of them into the boundary). The
  3 quantum edges sit on the central axis square.
- **Flashes:** each flash runs L = 80 ticks.
- **Detection:** escaped light is "detected". That leaves the record in a conditional pure state,
  which becomes the input to the next flash. This is a quantum-trajectory unravelling of the exact
  record channel.
  - The detection event is sampled by weighted reservoir sampling over all escape events.
  - Light still inside at the cut is detected in place.
- **Exact drift:** each flash also gives the exact expected change of the record's energy proxy
  ⟨λ_E L/8 + λ_B W⟩ and of its vacuum population, from its input state.
- **Radiation "temperature":** the flash's ⟨cos ω⟩ on the flat walk.
  - Cold light: σ = 1.2, ⟨cos ω⟩ = 0.84 (mostly long-wave).
  - Hot light: σ = 0.5, ⟨cos ω⟩ = 0.30.

**Parts.**
- **P23a, ladder:** the exact per-flash drift ΔE from 7 record states. The states are
  cos θ |vac⟩ + sin θ |hot⟩, θ from 0 to π/2, for cold and hot light, at λ_E = 0.3 and 1.0 (λ_B = 2).
- **P23b, trajectories:** 20 flashes in sequence from the hot state.
  - Cold light at λ_E = 0.3 and at 1.0: seeds 1 and 2.
  - Hot light at λ_E = 0.3: seeds 1 and 2.

**Predictions (priors).**
- **P23-1 (exact):** unravelling weights sum to 1 to 1e-12 per flash; the conditional states are
  normalised.
- **P23-2 (equilibrium exists):** for cold light, ΔE < 0 from the hot state (θ = π/2) and ΔE > 0
  from the vacuum (θ = 0), with one sign change in between. That sign change is the energy E*
  that the radiation holds the record at. Same for hot light, with E*(hot light) > E*(cold light).
  Medium confidence on the ordering.
- **P23-3 (cooling is slow):** |ΔE| per flash from the hot state is ≤ 1 % of the hot energy.
  Calming the record therefore needs hundreds or more flashes: light must outnumber record
  excitations by a large factor, as photons outnumber baryons.
- **P23-4 (trajectories):** the mean record energy over 20 cold flashes drops, by ≤ 5 % of the hot
  energy. Hot light cools less, or heats. Low confidence; the trajectories are noisy.
- **P23-5 (decoupling):** along the ladder, the light still inside at the cut rises with record
  energy, as in P22. So as the record cools, the box becomes more transparent.

**P23 AMENDMENT (2026-09-20, registered after the P23a ladder at λ_B = 2 was seen, before P23c
is run).**
- **The flaw found.** The P21–P23 couplings put the record deep in the *folded* Floquet regime.
  One order-3 flip on an axis edge costs W = 6, so it advances the phase by λ_B·W = 12 rad per tick,
  far beyond π.
  - Quasi-energy is only defined modulo 2π, so "record energy" (the proxy) has no ordering there.
  - Light then drives the record towards infinite temperature whatever its spectrum. That is
    Floquet heating.
- **P23c (added):** the same ladder in the *unfolded* regime, λ_E = 0.1 and λ_B = 0.1. The whole
  record spectrum spans less than π: the hot state's W is about 18, the maximum 24, times 0.1;
  the electric term is at most 0.45.
- **Predictions:**
  - **P23c-1:** for cold light, ΔE > 0 from the vacuum and ΔE < 0 from the hot state, with a sign
    change at an E* well below the hot state's energy (E* < 0.7 × E_hot).
  - **P23c-2:** E*(hot light) > E*(cold light).
  - **P23c-3:** the λ_B = 2 ladders (P23a) show E* ≈ E_hot for both lights; that is the folding
    signature.

**P23 AMENDMENT 2 (2026-09-20, registered after the P23c ladder was seen, before P23d is run).**
- **P23c result:** even unfolded, light heats the record towards the hot state (E* ≈ E_hot for
  both lights).
- **Diagnosis (analytic):** the walk's quasi-energy band is symmetric, with eigenphases ±arccos λ.
  Light has no lowest state. A photon near ω ≈ 0 can hand a record transition Δ in either
  direction (ω → ω ± Δ), with symmetric matrix elements, so light acts as an infinite-temperature
  bath for anything it touches.
- **P23d (added):** the same unfolded ladder (0.1, 0.1) with a *positive-frequency, narrow* cold
  flash. The flash is projected onto flat closed-box eigenmodes with phase in (0, 0.3], then
  released in the open box.
- **Prediction P23d-1:** heating persists (E* ≈ E_hot), because the band below the flash is still
  available.
- **Consequence if confirmed:** cooling needs light with a ground state, and redshift alone will
  not supply one.

**P23 AMENDMENT 3 (2026-09-20).**
- **P23d as registered cannot be run.** In the closed n = 5 box the lowest non-zero walk phase is
  0.523, so no mode lies in (0, 0.3].
  - n = 6 has 0.401 and n = 7 has 0.325; the λ = 1 uniform mode sits at exactly 0.
  - A first attempt kept 308 "modes" that were the exact-zero flat band split by round-off. That
    output is **discarded**, and the window now starts at 1e-6.
- **Why this matters:** the box is too small to hold light colder than about 0.5 rad. The record's
  gaps at (0.1, 0.1) are about 0.1 (electric) and 0.4–0.6 (magnetic). No light in this box is
  cold relative to the record, and that is itself the motivation for expansion.
- **P23d′ (replacement):** the flash is projected onto the lowest *positive* band, phase in
  (1e-6, 0.55], i.e. the modes at 0.523.
- **Prediction P23d′-1:** heating persists; ΔE ≥ 0 from the hot state.

**P23 OUTCOME (2026-09-20, appended; the amendments above were registered before each part
ran).**
Data: `reference/opus_session/data/p23_ladder_{0.3,1.0,0.1_0.1,0.1_0.1_posfreq}.json`,
`p23_cold03_{1,2}.json` (partial).
- **P23-1: PASS.** Unravelling weights sum to 1 within 7e-15; conditional states are normalised to
  5e-15.
- **P23-2 (λ_B = 2):** the sign change exists (PASS), but sits at E*/E_hot = 0.98–0.99 for every
  light. That is the folding signature. The ordering E*(hot light) > E*(cold light) FAILS
  (0.980 vs 0.991 at λ_E = 0.3).
- **P23-3: PASS.** |ΔE| from the hot state is at most 0.07 % of E_hot per flash.
- **P23-4: STOPPED early.** The cold03 trajectories were stopped after 5 flashes once the folding
  diagnosis made λ_B = 2 uninformative. Their E moved from 33.34 to 33.08 and 33.15 (−0.8 %,
  −0.6 %), in the registered direction. The hot03 and cold10 trajectories were never run.
- **P23-5: PASS.** On every ladder, the light still inside at the cut rises with record energy,
  e.g. 3.3e-4 → 3.3e-3. A cooling record becomes transparent.
- **P23c-1: FAIL.** Unfolded, broad light still holds the record near the hot state:
  E*/E_hot = 0.99 (σ = 1.2) and 0.95 (σ = 0.5).
- **P23c-2: FAIL.** The broad "hot" flash gives the *lower* E*. ⟨cos ω⟩ is not a good temperature
  for a broad flash.
- **P23c-3: PASS.** At λ_B = 2, E* ≈ E_hot for all lights.
- **P23d: not runnable** (see amendment 3); its first output was discarded.
- **P23d′-1: FAIL, and informatively.**
  - Narrow light from the lowest positive band (ω₀ = 0.523) *cools* the record from the hot
    state, with a crossing at E* ≈ 0.51 × E_hot.
  - So my "a symmetric band makes light an infinite-temperature bath" diagnosis was too strong.
    It holds for *broad* light. Narrow light has a real temperature set by its frequency relative
    to the record's gaps.
- **Summary:** radiation can cool the record only if it is narrow and below the record's gaps. The
  small box cannot hold such light (lowest positive phase 0.52 at n = 5), which is what motivates
  expansion.

## P22 — Freeze-out: does trapped light appear only once the chop calms? (2026-09-20, Opus; registered before implementation)

Motivation (the user): the early vacuum was surely not calm. Standard cosmology orders formation
by cooling (nucleons, then nuclei, then atoms, then free light). P21 already shows loops surviving
only in calm chop. Here "hot" means a *state* far above the record vacuum, with the rule fixed,
and cooling means energy carried away by light leaving through open walls.

**Setup.**
- **Model:** as P21 (QuantumRecordWalk, 3 quantum edges on the central axis square, the other
  edges frozen flat, n = 6). **Walls are open** (`mode="open"`): light reaching the boundary
  leaves.
- **Where the record's state goes when light leaves:** the escaped branches' record state is kept
  in the bookkeeping. After escape it evolves under U_rec alone, which conserves its vacuum
  population exactly, so that population is recorded at the moment of escape.
- **Initial state:** |r_θ⟩ ⊗ flash.
  - Record: |r_θ⟩ = cos θ |vac⟩ + sin θ |hot⟩, where |hot⟩ is a seeded random record state
    orthogonal to the vacuum (a typical, near-infinite-temperature state; seed 22).
  - Flash: a Gaussian (σ = 1.2, coin profile, fixed real polarisation) centred on the square.
    It is ordinary light, not a prepared loop.
- **θ ∈ {0, π/8, π/4, 3π/8, π/2}.**
- **Arms:**
  - **A:** dynamic record at (λ_E, λ_B) = (0.3, 2) and (1.0, 2).
  - **Q:** quenched, U_rec replaced by the identity, at θ = π/4 and π/2 for both couplings.
  - **C0:** λ_E = 0, i.e. v4.0 with open walls.
- **Horizon:** T = 600.

**Measured.**
- Norm left in the box, N(t).
- Walker weight on the square's 8 arcs.
- Record calmness P_vac,total(t): the vacuum population of the whole record, box plus escaped
  branches. It is exactly bookkept and starts at cos²θ.
- P_vac,in(t): the weight with the walker still inside and the record in its vacuum.

**Predictions (priors).**
- **P22-1 (exact):**
  - N(t) plus escaped weight = 1 to 1e-12;
  - λ_E = 0 equals v4.0 in open mode to 1e-12;
  - N(t) never increases.
- **P22-2 (cooling is light-limited):** for θ = π/2 in the A arms, P_vac,total rises above 0 but
  stays < 0.05 by T. At least 80 % of the rise happens in the first 100 ticks, while the flash
  is still inside. Without continuing radiation (in reality, expansion), cooling stalls.
- **P22-3 (trapping against hotness):** in the A arms, N(T) falls as θ rises. The fall is smooth,
  with no *sharp threshold*.
  - **Sharp threshold:** one adjacent θ-step accounts for ≥ 60 % of N(0) − N(π/2).
  - Prior: not sharp.
- **P22-4 (retained light sits with a calm record):** for θ ≥ π/4 in the A arms,
  P_vac,in(T) / N(T) ≥ 1.5 × P_vac,total(T). Medium confidence.
  - A retains *less* than Q at equal θ, because the dynamic record disturbs loops (P21).
  - **Formation beyond filtering (a surprise):** A retains ≥ 1.2 × Q at some θ ≥ π/4.

**P22 OUTCOME (2026-09-20, appended after the run; predictions above untouched).**
Data: `reference/opus_session/data/p22_{A03,A10,rest}.json`; code `examples/p22_freezeout.py`;
figure `examples/p22_graphics.py` → `out/p22_freezeout.png`.

- **P22-1: PASS.**
  - Escape bookkeeping holds to 6e-15.
  - N(t) never increases (the largest step is −1e-18).
  - λ_E = 0 open mode equals v4.0 open mode (unit test, 1e-12).
- **P22-2: PASS as worded, and the cooling is negligible.**
  - At θ = π/2 the record's vacuum population rises only to 4e-6 (λ_E = 0.3) or 2e-5 (λ_E = 1),
    all of it before t = 100.
  - Where the record starts partly calm, the flash *heats* it: P_vac,total falls, e.g.
    1 → 0.997 and 1 → 0.986 at θ = 0.
  - Reason: the hot record holds far more energy than one unit of light can carry. The record
    energy proxy is about 30 per unit norm; a unit of light carries at most π of quasi-energy.
    Cooling of this kind needs radiation to dominate the energy budget, as it did in the early
    universe.
- **P22-3: FAIL on direction; the "no threshold" part holds.**
  - Retained light *rises* with hotness.
  - N(T) is proportional to the hot fraction sin²θ to within 4 % at both couplings:
    5.1–5.3e-4 per unit hot fraction at λ_E = 0.3, 1.7–1.8e-4 at λ_E = 1.
  - It is exactly linear, so there is no threshold. Structurally, the hot and vacuum branches of
    the record evolve almost independently.
- **P22-4: FAIL.**
  - Retained light sits with a *hot* record: P_vac,in / N(T) ≤ 0.012, against P_vac,total of
    0.15–0.85.
  - The registered surprise criterion (A ≥ 1.2 × Q at θ ≥ π/4) is met by a wide margin:
    A/Q at T is about 100× (λ_E = 0.3) and about 30× (λ_E = 1).
  - **But this is not formation:**
    - nothing plateaus;
    - the hot dynamic record releases light slowly, as roughly t^−1 (λ_E = 0.3) and t^−1.9
      (λ_E = 1) over t > 200;
    - frozen hot chop releases it exponentially, and the flat vacuum (C0) releases it
      exponentially and fast (1e-18 by T);
    - the retained light sits on the quantum loop's arcs (about 82 %) in every arm.
- **Reading.** A hot, *responsive* record is **opaque**: it absorbs and re-emits light, holding it
  far longer than static disorder of the same statistics. A calm vacuum is transparent. This
  matches the decoupling half of the user's cosmology: light trapped while hot, free when calm.
  It does **not** show matter forming as things calm, because nothing cooled.
- **Caveat:** the record's excitations are pinned by construction (only 3 edges are quantum), so
  the light lingers where the record is.

## P21 — Option A at small scale: a quantum record in a lossless box (2026-09-19, Opus; registered before implementation)

Requested by the user: "implement A on a small scale on one or three of our interesting
geometries/initial conditions … reflective boundary box that echoes losslessly".
Design: `DYNAMICS_DESIGN.md` §10 (written with this entry).

**Model (one fixed unitary; status POSTULATED for the test).**
- **State:** Ψ(g₁,g₂,g₃; arc, i). Three chosen edges carry *quantum* labels (12³ = 1728
  record basis states); every other edge is frozen at the identity (flat vacuum). This is a
  partial quantum record; gauge invariance holds only for gauge moves that do not touch
  frozen edges. Labelled as such.
- **Tick:** U = U_rec · U_walk.
  - U_walk: the v4.0 walk (3-dim irrep, ring weights 1 : ½), *controlled* on the record:
    an arc across a quantum edge is transported by ρ of that basis label.
  - U_rec = e^{−iλ_B W/2} · ⊗_e e^{−iλ_E L_e/8} · e^{−iλ_B W/2}.
    - L_e: group Laplacian on the edge, generated by the 8 order-3 elements (a class
      union, so it commutes with gauge moves). Costs: 0 (trivial), 1 (irrep 3), 3/2 (1′, 1″)
      after the /8.
    - W = Σ over faces touching a quantum edge of (1 − χ₃(hol)/3): the Wilson cost
      argued in conversation (order-3 holonomy 1, order-2 holonomy 4/3).
  - Quasi-energy of the whole is conserved automatically; every tick is exactly invertible.
- **Box:** Kuhn ball n = 6, walk in `closed` mode (induced subgraph on the 125 interior
  vertices, 1208 arcs). Nothing leaves; the walls echo.
- **Record vacuum:** the eigenvector of U_rec (alone) nearest to |e,e,e⟩. Exactly stationary
  without the walker. Initial Ψ = |vac⟩ ⊗ ψ_walker.

**Geometries.**
- **G1, pivot vortex:** the P20 vortex ring shrunk to the box (σ = 1.2, R = 1.2, spin along an
  A4 3-fold axis), centred on the box centre. Quantum edges: the 3 edges carrying the most
  initial walker weight (a relational rule).
- **G2, DF cycle:** the P19 compact cycle state on an axis square at the centre (exactly
  stationary in vacuum), internal vector on an A4 3-fold axis. Quantum edges: 3 of its 4 edges.
- **G3, free flash:** a Gaussian flash (σ = 1, coin profile, fixed real polarisation) placed off
  centre. It expands, crosses a central triangle whose 3 edges are quantum, and echoes off the
  walls. This is the free-photon / sea-of-chop test.

**Arms (per geometry).**
- **C0:** λ_E = 0. The vacuum is exactly |e,e,e⟩ and nothing moves in the record, so the run
  is bit-identical to v4.0.
- **A(λ_E, λ_B):** λ_E ∈ {0.05, 0.3, 1.0} × λ_B ∈ {0.5, 2.0}.
- **Q(λ_E, λ_B), quenched control:** the same initial Ψ, but U_rec is replaced by the identity.
  The walker then sees a static mixture of chop drawn from the vacuum distribution. This
  separates "the record responds" from "the background is noisy".
- **Horizon:** T = 600 ticks (the box crossing is about 12 ticks, so dozens of echoes).

**Measured.** Norm; P_vac(t), the probability the record is still in its vacuum; record energy
⟨λ_E L/8 + λ_B W⟩ − vacuum value, against its infinite-temperature value; walker weight
near the structure (G1: hop ball r = 1 around the centre vertex; G2: on the cycle arcs, plus the
overlap with the DF state; G3: fidelity with the C0 walker); walker–record purity at T/2 and T.
Reversibility: T ticks forward then T back.

**Predictions (priors, stated before running).**
- **P21-1 (exact; must hold):** norm drift < 1e-12; reverse error < 1e-10; C0 equals v4.0 to 1e-12;
  the vacuum is stationary without the walker to 1e-12.
- **P21-2 (free flash, G3):** after the first crossing, 1 − P_vac ≤ 0.05 for λ_E ≤ 0.3 and grows
  ∝ λ_E² at small λ_E. Over T the record energy stays below 10 % of its infinite-temperature
  value for λ_E ≤ 0.3: no runaway heating in this closed system. Low confidence on the second
  half.
- **P21-3 (DF cycle, G2):** the quantum vacuum makes the DF state leak; the leaked weight grows
  ∝ t² at first and ∝ λ_E² in rate. The dynamic arms (A) leak more than the quenched arms (Q)
  at equal λ, because only A can change the holonomy during the run. Medium confidence.
- **P21-4 (pivot trapping, G1): prior negative.** The time-averaged near weight over
  [T/2, T] stays within ±25 % of C0 in every arm.
  - **Surprise criterion:** a positive result would be ≥ 1.5 × C0 *and* ≥ 1.2 × the matching Q,
    at two adjacent grid points.

**P21 OUTCOME (2026-09-19, appended after the run; predictions above untouched).**
Data: `reference/opus_session/data/p21_{G1,G2,G3}.json`; code `examples/p21_quantum_record.py`,
summary `examples/p21_summary.py`, figure `examples/p21_graphics.py` → `out/p21_quantum_record.png`.
Each run took 6–11 minutes; there were 40 runs in all.

- **P21-1: PASS.**
  - Worst norm drift 5.9e-13.
  - 600 ticks forward and back: error 1.4e-13 (G2), 4e-14 (G1, G3).
  - Vacuum stationary to 1.0e-14.
  - λ_E = 0 equals v4.0 (unit test, 1e-12).
- **P21-2 (free flash): PASS.**
  - 1 − P_vac at t = 10 is at most 1.1e-3 (A) or 4.9e-3 (Q) for λ_E ≤ 0.3, against the ≤ 0.05
    threshold.
  - The A arms grow by 38× (λ_B = ½) and 32× (λ_B = 2) from λ_E = 0.05 to 0.3, against 36× for
    λ_E²: consistent.
  - Record energy over the second half is at most 1.1 % of its infinite-temperature value for
    λ_E ≤ 0.3, and it has levelled off.
  - *Unregistered readouts:*
    - Fidelity with flat-vacuum light after 600 ticks (about 50 wall echoes) is ≥ 0.985 when
      the vacuum overlaps |e,e,e⟩ ≥ 0.99, and 0.92 at (0.3, 2).
    - At λ_E = 1 the light keeps heating the record: energy rises linearly to 6 % (λ_B = ½) and
      12 % (λ_B = 2) of the infinite-temperature value by T and has not levelled off. Fidelity
      falls to 0.75 and 0.64.
    - Quenched chop pulls light towards the defect: near weight 1.37–1.70 × C0, against
      1.29–1.30 × for A. That is disorder, not response.
- **P21-3 (DF loop): direction PASS; stated forms NOT confirmed; the reading needs correcting.**
  - The dynamic record disturbs the loop far more than quenched chop does. At λ_E = 1 the mean
    second-half DF overlap is 0.40 (A) vs 0.96 (Q) at λ_B = ½, and 0.19 vs 0.91 at λ_B = 2.
  - The t² onset could not be resolved: samples are every 5 ticks, and the vacuum is not
    |e,e,e⟩, so there is a sudden-quench jump at the first sample.
  - The λ_E² rate is not clean: 18× and 44× against 36×.
  - The loss is also not monotone. At (0.3, 2) the DF overlap falls to 0.34 at t = 355 and
    returns to 0.84 by t = 600: a slow coherent oscillation. At the minimum:
    - 82 % of the walker is still on the loop's 8 arcs (0.66 % of all arcs);
    - the record is 96 % in its vacuum.

    So at moderate coupling "leak" mostly means the loop's internal state rotates while the
    loop stays put: a beat between dressed loop states, not escape.
  - At λ_E = 1 there is real escape: weight on the loop drops to 0.3–0.6, and the record takes
    up to 24 % of its infinite-temperature energy.
- **P21-4 (pivot vortex): prior negative CONFIRMED.** Near weight is 0.967–1.0004 × C0 across all
  A arms. The surprise criterion was not met.
- **Caveat on the energy readout.** The vacuum is an eigenvector of U_rec, not the ground state
  of the generator λ_E L/8 + λ_B W used for the E_rec readout. That is why Q arms can show a
  slightly *negative* E_rec. E_rec is a proxy observable, not the conserved quasi-energy.

## P20 — Does a responsive record hold a pivoting wave together? (2026-09-19, Opus; registered before implementation)

Design: `DYNAMICS_DESIGN.md` §8 (v4.1-sc).

**Setup.**
- **Region:** Kuhn ball n = 16 with an open outer boundary. The A4 3-dim irrep
  carries the internal state.
- **Initial state, a prepared "pivot":**
  - a vortex ring, amplitude exp(−|p−p0|²/2σ²)·((ρ − R) + i(z − z0)), with
    σ = 3 and R = 3 in grid units (coordinates used for preparation only);
  - arcs filled in the coin state φ_v;
  - circularly polarised internal state (u1 + i u2)/√2, spin along one A4
    3-fold axis.
- **Horizon:** 400 ticks.

**Measured:**
- norm left in the region;
- weight inside the graph ball of hop radius 4 around the centre vertex (a
  relational structure, not coordinates);
- number of chops written;
- curvature count H at checkpoints.

**Arms.**
- **C0:** v4.0, no feedback.
- **C1:** random chops, matched in count each tick to the feedback run (seeded,
  random interior edge, random order-3 factor). This separates "the record
  responds to the wave" from "the record is just disordered", since disorder
  alone can localise waves.
- **F(κ):** feedback at the three registered κ.

**Engine check:** 50 ticks forward then 50 back must restore ψ and g exactly
(to round-off).

**P20 WITHDRAWN (2026-09-19), with no valid result produced.**
- **Bug:** the first launch hit a preparation bug. The spin axis was parallel
  to a helper vector, which made the initial state NaN. The run was killed
  before producing numbers. The bug is fixed in `examples/p20_record.py`.
- **Objection accepted:** the user objected to the rule itself. Chop is
  written without costing the wave anything, so the record changes for free.
- **Why that is right:** the norm is conserved, but the wave's evolution
  operator changes whenever the record changes, so its energy (quasi-energy)
  is *not* conserved. Energy appears or vanishes with each chop. That breaks
  the spirit of clause 1 (one conserved quantity), and it is also contrary to
  Landauer: writing a record should cost something.
- **Consequence:** the v4.1-sc rule is retired as physics. Its reversible
  engine (`RecordWalk`: exact forward/backward over 50 ticks and 5,850 chops,
  labels restored bit for bit) is kept as a tested component. P20 will be
  re-registered against an energy-accounted rule.

**Success criterion (registered):** for some κ, ball weight at T = 400 is at
least 10 × max(C0, C1) and at least 1e-3. A pass is only a *candidate*: it
must then show coherent motion and M1 = M2. **No directional prediction.**
My prior, stated for the record: failure is more likely than success for this
first rule.

## P19 — First tests of the v4 dynamics (2026-09-19, Opus; registered, NOT run)

Design: `docs/DYNAMICS_DESIGN.md` (v4.0).
- **The walk:** a gauge-covariant weighted-reflection (Szegedy) walk on arcs,
  with ring-size weights 1 : ½, transport by labels in a representation ρ of A4
  (trivial or the 3-dim irrep), one hop per tick.
- **Labels:** a fixed, prepared record.
- **Reporting:** relational observables only.

The unit-weight walk and the pre-v4 engine are control arms.

- **P19a (identities):** unitarity, gauge covariance and the Szegedy spectrum
  identity hold exactly on finite Kuhn balls with boundary, not just on the torus.
  Prediction: all hold to round-off.
- **P19b (dispersion and flat bands):** on tori of increasing size,
  θ(k)/|k|_emergent → one constant. The direction dependence scales as k^2
  (unit weights) or k^4 (ring weights). The flat-band multiplicity equals
  arcs − 2V (plus corrections at λ = ±1). Prediction: flat-band eigenvectors
  can be chosen supported on bounded cycles (bounded participation as the torus
  grows), i.e. strictly non-propagating.
- **P19c (relational light cone):** the source is a small ball; detectors are
  combinatorially defined shells. Predictions:
  - the median arrival delay grows linearly with emergent distance, with the
    same speed in every direction within 2% at the largest size run;
  - the amplitude outside the emergent cone falls exponentially with distance
    from it;
  - the strict support is the hop cone.
- **P19d (holonomy):** around a prepared single flux loop, with ρ = 3-dim
  irrep, two-route interference contrast equals |χ₃(flux)|/3, as in E015 but
  now inside the walk.
- **P19e (first physics: does a record trap implication?):** fixtures are a
  single A4 flux loop, the P13 linked loops and the P15 tethered link. Start a
  packet on the flux support and measure the long-time weight retained in a
  neighbourhood, minus the vacuum control (same packet, flat labels). Trapping
  counts only if it:
  1. exceeds the vacuum control;
  2. is not carried by the vacuum flat bands (the flat-band projection is
     removed from both runs);
  3. is gauge-invariant.

  **No directional prediction is registered.** Positive and negative outcomes
  are both informative: a negative sends the design to v4.1 (dynamical labels);
  a positive is the first "defect plus trapped light" candidate. It must then
  face M1 = M2 before any matter language is used.

**P19 outcome (2026-09-19, Opus).** Code: `src/constraintnet/walk.py` and
`examples/p19_walk.py`. Data: `reference/opus_session/data/p19_*.json`.

- **P19a HIT.**
  - *Closed:* unitarity to 2e-16 on Kuhn n = 3 and 4. The Szegedy identity
    holds to 5e-8, a limit set by eigen-solver accuracy on the degenerate ±1
    sector; the remainder is all ±1. The gauge-transformed spectrum is
    identical, with random A4 labels and the 3-dim irrep.
  - *Open:* ‖U_R‖₂ = 1 and spectral radius = 1, both to round-off, so the
    norm never increases.
- **P19b HIT.**
  - The momentum blocks reproduce θ = arccos λ(k) to 1e-15, with exactly 12
    flat eigenvalues (±1) at every sampled k.
  - The long-wave speed θ/|k| = 0.42639, against the predicted sqrt(2/11) = 0.42640.
  - Direction spread scales as k^4.00 with ring weights and k^2.00 with unit
    weights.
  - **DF** holds exactly: an axis-square cycle with random labels carries a +1
    eigenstate (residual 2e-16) whenever the holonomy has a fixed vector, which
    in the A4 irrep it always does.
  - Unregistered, sampled over 200,000 k: the maximum group speed anywhere in
    the Brillouin zone equals the long-wave speed (ratio 0.99996). No lattice
    mode outruns the light cone.
- **P19c HIT at the largest size, n = 120.** An n = 40 torus is too small for
  any clean window.
  - The median-arrival speed is 0.4217 (predicted 0.4264, 1.1% low), with a
    spread over 60 directions of 0.32% (criterion ≤ 2%). The peak-arrival speed
    is 0.4267, spread 0.13%.
  - The weight beyond 1.25·c·t falls exponentially: 3e-5 at t = 7, 1e-10 at
    t = 42, then a floor near 1e-11.
  - The first n = 80/120 run had a wrap-around bug: its time window was too
    long by the width of the front's tail. It was fixed and rerun, and the
    buggy numbers are superseded.
  - n = 80 with the corrected short window gives a noisy median fit (spread
    5.7%) but a peak speed of 0.4252.
- **P19d: the detection formula HIT exactly; the contrast clause was mis-registered.**
  - Detection is the coin-symmetric channel at the antipode of an axis square
    whose holonomy is the loop's flux. It gives exactly ½(1 + χ₃/3): 0.5 for
    order-3 flux and 1/3 for V4 flux, with 1 for trivial labels.
  - The registered "contrast = |χ₃|/3" does not follow from that formula; the
    difference from the trivial run is ½(1 − χ₃/3). |χ₃|/3 is the fringe
    visibility you would get by scanning an extra route phase, which the model
    has no parameter for. The error is kept visible; the formula itself is confirmed.
- **P19e NEGATIVE: a static flux record does not trap implication.**
  - *Exact (Kuhn n = 6, single loop, 5,250-dim open walk):* 2,875 trapped
    eigenvalues with the fixture against 2,877 in vacuum, for both order-3 and
    V4 flux. The gap below the trapped sector is identical (0.0246), and so is
    the trapped weight near the flux (0.80). The flux *removes* two trapped
    states, consistent with DF: holonomy cuts the fixed-vector space of cycles
    that link it. Every trapped state is a vacuum-type, non-translating cycle
    state.
  - *Time evolution (Kuhn n = 8: P13 linked, P15 tethered, single loop; 20,000
    ticks):* the coin-state packet on the flux support escapes completely.
    Retained weight is 1e-32 to 4e-32 with fixtures and 1e-32 to 2e-32 in
    vacuum, already below 1e-12 by tick 1,000.

**Consequence (as registered):** v4.0 is a sound propagation engine. It is
exactly conservative, gauge-covariant, sharp and round, and nothing in it
outruns the light cone. But a prepared, frozen record traps nothing beyond the
vacuum's own non-translating cycle states. Trapping must come from the record
*responding* to the implication, i.e. v4.1 (dynamical labels, self-confinement K).

**P19 amendment A2 (2026-09-19, still before any P19 code ran).** The "closed
variant" of P19a becomes the walk on the subgraph induced by the interior
vertices: arcs to boundary vertices are absent, not reflected in place. Reason:
in-place reflection is not of Szegedy form, so the identity would not apply to
it. The open variant is unchanged.

**P19 amendment A1 (2026-09-19, before any P19 code ran): realisations, fixed
now so the outcome cannot steer them.**

- **P19a** runs on finite `kuhn_ball` n = 2, 3 with the walk restricted to
  interior vertices.
  - **Closed variant:** arcs into boundary vertices reflect. Unitarity, gauge
    covariance and the Szegedy identity are checked with degree-dependent
    weights.
  - **Open variant:** arcs into boundary vertices leave, giving a
    sub-unitary U_R, whose norm must never increase.
- **P19b** uses the exact momentum blocks (14×14 per k) of the implemented
  torus walk. It adds one derived statement, DF, to test.
  - **DF:** a closed cycle whose two edges at every vertex have equal weight
    carries an exact, compact eigenstate: eigenvalue +1 for the pattern
    "transported forward amplitude, opposite sign on each reverse arc".
  - With labels, DF exists iff ρ(holonomy) fixes a nonzero vector. In the
    A4 3-dim irrep every element is a rotation and fixes its axis, so flux never
    removes these states.
- **P19c** uses a 3D torus, n = 40, with a Gaussian source of width σ = 3 hops
  shaped by the coin state φ_v. Detectors are vertices, binned by
  emergent-metric radius and direction (the metric of P18, weighted).
  - **Predicted front speed:** sqrt(2/W) per tick in that metric, with W = 11.
  - **Isotropy criterion:** the spread over directions of the median-arrival
    speed is at most 2%.
  - **Cone criterion:** the weight beyond (1.25 × predicted speed × t) falls
    with t. Exponential form is checked, not assumed.
- **P19d** uses an even cycle of the mesh's own 1-skeleton, made of
  equal-weight edges, whose holonomy under a single-loop A4 fixture is
  nontrivial. The walk is restricted to that cycle subgraph, so the two
  routes have equal length. The source is the coin state at one vertex; the
  detector is the antipode at tick L; internal states are averaged (maximally
  mixed).
  - **Prediction:** detection = ½(1 + χ₃(Φ)/3). The contrast relative to the
    trivial-label run is |χ₃(Φ)|/3, i.e. 1/3 for V4 flux and 0 for order-3
    flux. χ₃ is real on A4.
- **P19e** has two parts; fixtures lie strictly inside and outer-boundary
  vertices act as exits.
  - **Exact:** the open walk U_R on `kuhn_ball` n = 6 with one rectangular-disk
    loop. Flux element: order-3, and separately V4. Count eigenvalues with
    |μ| > 1 − 1e-9 (the trapped subspace), fixture versus vacuum. Report the
    trapped weight within one hop of the curved-face vertices, fixture versus
    vacuum.
  - **Time evolution:** n = 8 with the P13 linked loops (order-3 lift), the
    P15 tethered link (N1) and one loop. The packet is the coin state on the
    curved-face vertices, with internal state maximally mixed (average of 3
    basis states). Retained weight is followed to 20,000 ticks, against the
    vacuum control.
  - **Trapping beyond vacuum** means the trapped dimension exceeds the
    vacuum's, or the retained weight exceeds the vacuum's by more than 1e-3
    and is concentrated at the flux support. Given DF, cycle states that avoid
    the flux are expected in both runs and are the control, not the result.

## P18 — Round, sharp light fronts on the project's mesh? (2026-09-19, Opus; derived before execution)

Context: `WORKING_STATEMENT.md` clause 3 (reading 1: influence spreads
isotropically at one speed; sharp fronts in 3D; mass makes a wake). The
derivations D1–D7 are in `docs/PROPAGATION.md` and were written before any
simulation. Wave rule: u_tt = -(L + m^2) u on the mesh graph, leapfrog in time.
Coordinates are used only to prepare pulses and to measure. No constraintnet
dynamics is changed.

**Predictions:**

- **N1 (D4):** Ã^(-1/2) maps the actual Kuhn star onto a BCC star. The 8 short
  vectors (ring 6) have pairwise cosines ±1/3; the 6 long vectors (ring 4) are
  orthogonal and 2/√3 longer.
- **N2 (D2, D4):** front speeds for uniform weights differ by a factor 2 in grid
  coordinates (along (1,1,1) versus perpendicular to it) and by a factor that
  tends to 1 in the emergent metric.
- **N3 (D5):** in the emergent metric, the leftover anisotropy of the front
  radius shrinks as the pulse widens. With ring-size weights 1 : 1/2 it is
  smaller than with unit weights at every width, and it shrinks faster (the
  O(k^4) term is removed). Also measured directly from the dispersion symbol.
- **N4 (D6):** in 3D (Kuhn, massless), the fraction of sum u^2 lying well inside
  the cone (r < t - 4σ at t = 12σ) falls toward the continuum value, which is
  about 0, as the pulse width σ grows. A 2D control (square lattice) keeps a
  finite interior fraction that matches its continuum value.
- **N5 (D6):** with mass (mσ = 0.5, 1), the 3D interior fraction becomes clearly
  nonzero. It converges with σ to a spectral continuum reference (exact
  Klein–Gordon dispersion on a periodic box).
- **N6 (D7):** on Sierpinski level 3 with exit damping, the classical damped
  wave keeps exactly the energy that its initial data put in the dark modes.

A failure of N2–N5 would mean the mesh cannot support round, sharp light
fronts under nearest-neighbour waves. That would be recorded as a strike
against clause 3 on this mesh, not repaired by retuning.

**P18 outcome (2026-09-19, Opus).**

- **N1 HIT (exact).** Ã = 2I + 2J. Under Ã^(-1/2) the 8 ring-6 edges become
  equal-length cube diagonals (cosines ±1/3, −1), and the 6 ring-4 edges become
  cube axes, 2/√3 longer. That is the BCC tetrahedral honeycomb star.
- **N2 HIT.** The grid-coordinate front speed ratio along (1,1,1) versus
  (1,-1,0) is 1.985 at σ = 1.5 and 2.005 at σ = 3 (predicted 2). An
  unregistered readout along the grid axis gave 1.60–1.63. That matches the
  front (ray) speed 1/sqrt(n^T Ã^(-1) n) = 1.633, not the plane-wave speed 2;
  D1's wording was amended accordingly (both coincide on the registered
  eigen-directions).
- **N3 HIT for the exact test, NOT RESOLVED for the front test.**
  - *Exact symbol test:* the direction spread of ω²/k² scales as k^2.00 with
    unit weights and k^4.00 with ring-4 edges at weight ½, as D5 requires.
  - *Front-radius test:* measured anisotropy was smaller with ring weights at
    every width, 0.0019–0.0014 against 0.0045–0.0016 for unit weights. But the
    measurement floor, set by the continuum control, is about 0.001. So the
    faster decrease with width is below resolution and is not claimed.
- **N4 HIT.** In 3D on the project mesh the massless interior fraction is at or
  below 3e-7 for σ = 1.5–4, the same as the continuum, whose Gaussian tails are
  the floor. The 2D control keeps 0.016–0.018, converging to its continuum value
  (0.0180 against 0.0181 at σ = 6).
- **N5 HIT.** With mass, the interior fraction converges to the continuum:
  - mσ = 0.5: 0.0306 → 0.0318 against 0.0321
  - mσ = 1: 0.408 → 0.391 against 0.386

  Mass makes a wake inside the cone; massless 3D fronts do not.
- **N6 HIT.** The classical damped wave on Sierpinski level 3 keeps exactly
  the dark-mode energy for all four starts. The residual difference is 7e-10
  at T = 8e4; T = 4e3 had not yet converged, so the longer run is reported.

**Consequence:** with its own emergent metric, the project mesh supports round
(cubic-symmetric, quartic-isotropic with ring weighting) and sharp light fronts
under nearest-neighbour waves, and mass produces a trailing wake. Trapping needs
signed waves; complex amplitudes are not specifically required.
Data: `reference/opus_session/data/propagation_test.json`; figure
`out/p18_propagation.png`; tests `tests/test_propagation.py`; derivations
`docs/PROPAGATION.md`.

## P17 — Can amplitudes trap where probabilities cannot? (2026-09-19, Opus; derived before execution)

Motivation (user discussion, `docs/BAG_PICTURE.md` §8 and the conversation that
followed): a particle might be a region in which an implication wanders forever
because every outgoing route cancels. This test uses NO model change; it
compares two walks on fixed graphs with a declared exit. Both use the SAME
generator, the graph Laplacian L of the region, and the exit is a set B of
vertices with leak rate Gamma > 0 (P_B = projector onto B):

* classical (probabilities): p(t) = exp(-(L + Gamma P_B) t) p0, survival sum(p)
* amplitude walk: psi(t) = exp(-i K t) psi0 with K = L - i Gamma P_B,
  survival ||psi||^2. (Wide-band exit model: the standard effective description
  of a region coupled to an outgoing channel.)

The only difference between the two is the factor i.

**Derived statements (proofs in `docs/TRAPPING.md`; checked numerically afterwards):**

- **T1 (classical always escapes).** On a connected region,
  x^T (L + Gamma P_B) x = sum over edges (x_i - x_j)^2 + Gamma sum_B x_b^2 > 0,
  so the matrix is positive definite and survival -> 0, at least as fast as
  exp(-lambda_min t), from EVERY start.
- **T2 (leak = flux).** d||psi||^2/dt = -2 Gamma sum_B |psi_b|^2. Every eigenvalue
  of K has Im E = -Gamma sum_B |v_b|^2 / ||v||^2.
- **T3 (exact long-time survival).** Let D be the span of the eigenvectors of L
  that vanish on B (the dark subspace). Then survival -> ||P_D psi0||^2 exactly.
  D and its orthogonal complement are both invariant under K; K has no real
  eigenvalue on the complement. Averaged over starts at single vertices, the
  trapped fraction is exactly dim D / N.
- **T4 (degeneracy bound).** dim D = sum_E (m_E - rank of P_B on eigenspace E)
  >= sum_E max(0, m_E - |B|). Repeated eigenvalues force dark states.
- **T5 (symmetry bound).** If a group of graph automorphisms fixes every exit
  vertex, the vectors orthogonal to all its invariant vectors vanish on B and
  form an L-invariant space. So dim D >= N - (number of orbits of that group).
- **T6 (symmetry breaking; perturbative, not a theorem).** A perturbation of
  size eps that breaks the protecting symmetry gives formerly dark states a
  decay rate proportional to eps^2 (finite lifetime, i.e. decay).

**Predictions per geometry (exit = one vertex unless stated):**

- **path, exit at an end:** trivial stabilizer, simple spectrum; dim D = 0, so
  the amplitude walk escapes completely too. This is the control: amplitudes do
  not ALWAYS trap.
- **cycle C_n:** reflection fixing b, dim D = floor((n-1)/2).
- **complete graph K_n:** dim D = n - 2 exactly.
- **Sierpinski gasket, levels 1-6, exit at a corner:** dim D >= (N - fixed)/2
  from the corner reflection (T5), possibly more from degeneracy (T4). I expect
  a large dark fraction that does not vanish with depth. I make NO prediction for
  how the slowest non-dark decay rate scales with depth; that is measured only.
- **Kuhn ball 1-skeleton (n = 2, 3), exit at the corner (0,0,0):** bound from
  the coordinate permutations that are automorphisms; exact value computed.
- **Symmetry-broken gasket** (random edge weights 1 + eps u): D collapses to
  its accidental part (expected 0), and former dark states decay at rate ~ eps^2.

**Cross-checks:** simulated survival at long times must equal ||P_D psi0||^2.
The explicit-lead control (a 1-D chain of 4,000 sites attached at b in place of
Gamma P_B) must keep dark states exactly stationary. The classical survival must
go to 0 in every case.

**Scope.** This tests whether interference CAN trap on a fixed geometry. It does
not show that the model's own record builds such geometry, and it is not a
particle. If the gasket traps, the cause is symmetry and degeneracy (T4/T5),
not fractality as such. The fractal only supplies a great deal of both.

**P17 outcome (2026-09-19, Opus).** Every derived statement was verified and
every per-geometry prediction HIT.
*T1:* classical survival -> 0 on all 12 graphs; the largest remaining value is 6e-17.
*T3:* simulated amplitude survival equals ||P_D e_j||^2 for every single-vertex
start. Worst error is 1e-9 at long times (4e-6 for gasket level 4 at T = 6.3e8,
from round-off in repeated squaring). Mean trapped fraction = dim D / N exactly.
*Exact dim D* (modular Krylov rank over three primes, confirmed by a 400-digit
Lanczos run):

- path 0 (control: amplitudes escape too)
- C_40 19, C_41 20
- K_12 10
- gasket levels 1–6: 2, 8, 29, 98, 317, 998 of N = 6, 15, 42, 123, 366, 1095 (dark 33% -> 91%)
- Kuhn 1-skeleton n=2: 18/27; n=3: 44/64

T4/T5 bounds hold everywhere; T5 is tight for cycles, K_n and Kuhn n=3.
*Explicit lead control* (6,000-site chain, t = 1,500): the dark state keeps
region norm 0.99999999999999; a bright state falls to 0.37.
*T6:* breaking the gasket symmetry with integer weights 1000 +/- 1 leaves exact
dim D = 0 (from 98). With weights 1 + eps u, the former dark states' median decay
rate scales with log-log slope 1.92 over eps = 1e-3..1e-2 (1.70 including 0.1).
That matches eps^2 at small eps, with departures beyond the perturbative range.

**Unregistered observations, stated as observations:**
(a) For gasket level k (k = 1..6) the non-dark sector has dimension exactly
3·2^(k-1)+1, so the dark fraction tends to 1 with depth. This is a pattern, not a proof.
(b) The slowest decay rate of the NON-dark states falls doubly exponentially
with depth: 5.1e-2, 4.1e-2, 5.7e-4, 6.4e-8, 8.4e-16, 1.5e-31. From level 3 on,
the exponent roughly doubles each level. These are exact 150-digit spectra of
the Jacobi reduction; the rates sum to Gamma exactly (trace identity).
Consequence: with finite depth, "almost trapped" states have finite but rapidly
exploding lifetimes. Unlimited depth would trap everything.
Data: `reference/opus_session/data/trapping_test.json`,
`trapping_depth_rates.json`; figure `out/p17_trapping.png`; tests
`tests/test_trapping.py`; derivations `docs/TRAPPING.md`.

## P16 — The bag test: does anything inside push outward? (2026-09-19, Opus; before execution)

Motivation (user picture, see `docs/BAG_PICTURE.md`): vacuum = cancelling
"wakes" of implications; a particle = a pressurised bubble in that vacuum. A
bubble is stable only if an outward pressure balances the inward surface
tension. H supplies the tension (every curved face costs 1). This test asks
whether the CURRENT model supplies any pressure: an interior quantity that
grows with enclosed volume AND differs between inside and outside.
No model change is made. All regions are whole Kuhn balls with identity boundary.

**M1 — hidden-resolution count of the flat interior.** For n=1,2,3 (Z3; A4
where the exact solver finishes), enumerate all flat interior fillings exactly.
Raw count and physical count = raw / |G|^(interior vertices) (gauge acts freely
because each interior vertex connects to the fixed boundary).
Prediction: physical |I| = 1 at every size (flat connections on a simply
connected ball are unique up to gauge). Raw count = |G|^(V_int): it grows with
volume, but it is pure gauge redundancy, not a pressure.

**M2 — lowest-lying excitations.** For n=2..8 (Z3, A4), enumerate every
single-interior-edge excitation of vacuum. Record its H (the edge's face
degree), the minimum H over these, how many reach it, and the number of
distinct curved-face supports. Prediction: the minimum stays constant and the
count grows in proportion to the interior edges (volume). This is ordinary
configurational entropy, identical inside and outside any sub-region. That
favours dispersal (a gas), not a bubble. It does not determine whether some
multi-edge state has smaller H; only single-edge excitations are enumerated.

**M3 — conserved interior content (derived, no run).** Claim 30: under all
interior moves no nonconstant label invariant exists. So nothing inside can
play the role of the bag model's conserved quark number.

**M4 — arithmetic from M2, not dynamics.** In a Metropolis picture, a single
lowest excitation has free energy F = H_min - ln(N_min)/beta. It goes
negative below beta* = ln(N_min)/H_min, where the vacuum would fill with a
gas of small loops ("wake sea"). Report beta*(n) as an equilibrium estimate
only; no kinetics is run.

**Overall prediction:** no quantity in the current model provides a
volume-scaling pressure that differs between inside and outside. A pressurised
bubble therefore cannot be stable here. This is the precise job any
cone/wake extension would have to do.

**P16 outcome (2026-09-19, Opus).** All registered predictions HIT.
*M1:* physical |I| = 1 exactly for Z3 n=1,2,3 and A4 n=1,2 (raw 1, 3, 6561; 1, 12
= |G|^(V_int), i.e. every raw filling is a gauge copy of vacuum). A4 n=3 was not
completed: raw enumeration lists 12^8 = 4.3e8 gauge copies (an attempt ran >25
min and was stopped). Recorded as skipped. *M2:* for n=2..8, both groups: the
single-edge excitations have H in {4,6}; H_min = 4 at every size. The number of
distinct minimal supports is exactly 3n^2(n-1) (12, 54, 144, 300, 540, 882, 1344),
which grows with volume like n^3. Minimal (edge, multiplier) excitations: Z3 24 -> 2,688, A4 132 -> 14,784.
*M4 (arithmetic):* beta* = ln(N_min)/4 grows only logarithmically: Z3 0.79 -> 1.97,
A4 1.22 -> 2.40 from n=2 to 8. So the equilibrium density of small loops per
unit volume is set by beta alone, and it is the SAME inside and outside any
sub-region. *M3:* unchanged (derived). **Verdict:** the current model has
surface tension and a uniform loop-gas entropy but no inside/outside pressure
difference and no conserved content. A pressurised bubble has nothing to hold
it up. Any cone/wake extension must supply a conserved, trapped content whose
confinement energy grows as the bubble shrinks. Data:
`reference/opus_session/data/bag_test.json`; script `examples/bag_test.py`;
tests `tests/test_bag_test.py`.

## P15 — Do non-commuting linked fluxes resist unlinking? (2026-09-19, Opus; before execution)

Registered before building any fixture below. Motivation: P13/P14 used a cyclic
subgroup, so every flux commuted and Z3 = A4 by construction. Linking was not
protected even by the downhill-or-equal condition (P14). The memo's claim that
knots stabilise matter has not yet been tested with the non-abelian structure
that is the reason for choosing A4. In continuum gauge theory, line defects with
non-commuting fluxes cannot cross freely: crossing creates a connecting string
with commutator flux (Poenaru–Toulouse 1977; the same mechanism appears in
non-abelian cosmic-string and nematic-disclination literature). This experiment
checks whether that mechanism survives in these labels and whether it creates
an action barrier under H.

**Fixture (prepared, not emerged):** Kuhn n=8, identity outer boundary, the same
two P13 rectangular disks. Disk 1 carries element a, disk 2 element b. An edge's
label is the product of a^(+-1)/b^(+-1) factors taken in the order its segment crosses the
disks (sign = crossing direction). An edge that meets a disk boundary is rejected,
as in P13. Arms, all in the full group A4:
C0 a = b = the P13 order-3 element (should reproduce the P13 labels exactly);
C1 a, b distinct commuting involutions in V4;
N1 a, b order-3 elements from different cyclic subgroups;
N2 a an involution in V4, b the P13 order-3 element.

**Derived expectation, stated before measurement.** A small loop around the
arc where the disks intersect crosses disk 1 and disk 2 once each in each
direction, so its holonomy is conjugate to the commutator [a,b]. For C0/C1 this
is trivial. For N1/N2 it is a nonidentity element of V4. The complement of a Hopf
link in the ball has abelian fundamental group Z^2. A flat field elsewhere
therefore requires the two meridian holonomies to commute, whatever labels are
chosen. Predictions: C0/C1 give exactly two disjoint dual loops with |Lk|=1.
N1/N2 give one connected junction component: both loops plus a "tether"
along the intersection arc carrying V4 flux, with initial H larger than C0 by
the tether's face count. If the detector disagrees, report the failure; do not
change the fixture to fit.

**Dynamical questions (outcome open; my guess is recorded, not assumed).**
(i) One-edge census of every initial proposal, as in P13b: count nonincreasing
and uphill proposals and changes of support domain. (ii) The P12/P13 plateau
search with 32 discovered states per plateau, then again with 256. Budget
exhaustion is inconclusive. (iii) The constructive path that sets every interior
label to identity, one move per differing edge. Its moves are on distinct edges,
so their final state does not depend on order. Search for a nonincreasing order
with a greedy scheduler plus bounded backtracking. Report the smallest peak
found above initial H. It is a path upper bound, never a minimal barrier.
**Guess:** continuum tether tension pulls the loops through each other,
so I expect no barrier. N1/N2 would then also have nonincreasing decay to vacuum.
If only the non-commuting arms need an uphill step, this is the first candidate
non-abelian activation barrier. It becomes a claim only after a separate
registered test of whether that step is necessary.

Checks: full-holonomy replay, fixed boundary labels, inverse replay, and
gauge-transported witnesses for every reported path; meridian-commutation
measured on every two-loop state recorded. No new action, move, driver,
constraint or clock. Search order is not time, and nothing here is a nuclear
or particle process.

**P15 amendment (before any support, action or search was measured):** building
the fixture showed 4 edges crossing both disks at the same parameter. These edges
pass exactly through the intersection line, so for N1/N2 the factor order is
ambiguous. (P13 was abelian and did not see this.) Declared resolution: disk-1
factor first, which amounts to an infinitesimal displacement of disk 2. The
opposite convention (disk-2 first) runs as a named control arm. Both are reported.
No other change.

**P15 outcome (2026-09-19, Opus).** *Fixture prediction HIT.* C0 reproduces the P13
A4 labels exactly, with two loops of 52/46 faces and |Lk|=1. C1 (commuting V4
fluxes) gives two loops and |Lk|=1 at H=98. N1 and N2 each give ONE junction
component, H=103: both loops plus a tether of 5 faces carrying V4 (commutator-class)
flux. In N2 the V4 loop and tether together contribute 57 V4 faces. The disk-2-first
tie control gives H=104 with a 6-face tether and the same single-component
topology. So the tie convention moves one tether face and changes no conclusion.
Based meridians in the commuting two-loop fixtures commute, as required.
*Guess about dynamics CONFIRMED; no barrier.* (i) One-edge census (33,352 proposals per arm): C1 gives
8 nonincreasing (all two-loop), 179 uphill two-loop, 2,860 uphill junction and 30,305 uphill
loop-count changes. This is identical to the P13b A4 row. N1 and N2 each give 10
nonincreasing and 33,342 uphill proposals, and every one stays in the single-junction
domain. No single rewrite removes the tether. (ii) Plateau search: every
arm exhausted its budget. With 32 states: C 98->96, N 103->89, tie control
104->102. With 256 states: C 98->90, N 103->72, tie control 104->68. This is
inconclusive, as registered. (iii) Ordered identity-erasure: the greedy
scheduler found a fully nonincreasing 140-move order to flat vacuum in all six
runs, with peak 0 above initial and no backtracking needed. Every path was verified
by full holonomy recomputation, fixed boundary labels, inverse replay, the P12
decay verifier and gauge transport. In N1/N2, under both tie conventions, the
junction persists until step 52 (H=80). It then becomes two loops with Lk=0 whose
based meridians do NOT commute. An unlinked pair is allowed that: its complement
has a free fundamental group. Tether and linking disappear on the same move. The
greedy C0 path is also a second, independently found nonincreasing erasure of the P13 fixture,
which corroborates P14 by a different method. **Consequence:** with non-commuting fluxes,
linking forces a tether, as topology requires. Under H the tether gives no activation
barrier: the loops unlink as the tether shortens, then shrink. Non-abelian
topological entanglement is real in these labels, but under this action it is not
energetic protection. Data: `reference/opus_session/data/noncommuting_link_audit.json`;
figure `out/p15_noncommuting_links.png`; tests `tests/test_link_order_and_noncommuting.py`.

## P14 — Is the P13b uphill step an ordering artifact? (2026-09-19)

Registered before testing reorderings. Keep each archived P13b 140-move erasure
path and all labels unchanged. The sole uphill move was at one-based step 40.
Take exactly steps 33–48 (16 distinct-edge rewrites), keep steps 1–32 and 49–140
fixed, and search all nonincreasing orders of the selected moves with at most
65,536 discovered subset states. Since each selected edge is changed once,
the state after any subset is independent of its ordering, even for A4: products
on different edges are independent; face holonomy products retain their order.

Prediction: some ordering of this fixed window avoids every uphill increment,
yielding a complete nonincreasing erasure witness. Exhaustion of all subset
states would disprove only this reordering possibility, not all permitted decay
paths. A state-budget cutoff is inconclusive. No new action, moves, confinement
constraint, driver, or physical clock is introduced.

Independently replay the resulting complete path with full holonomies, exact
boundary labels, inverse moves and transported gauge witnesses in both Z3 and
A4. Report state counts and the complete ordering. This is a stability control
for the current linked fixture, not a reproduction or refutation of the new
Williamson–van der Mark structural target (`ELECTRON_TARGET.md`).

**P14 outcome (run by Astra/Codex; outcome text by Opus after independent
reproduction):** prediction HIT in both groups. The 16-move window has a
nonincreasing ordering, found after discovering 291 of 65,536 subset states
(2,636 transitions checked). Window order [0,1,2,3,4,6,7,5,8,...,15]: the sole
change is to postpone original step 38 (86 -> 84) until after steps 39–40.
The action path then reads ...86,86,85,85,...,84... in place of ...86,84,84,85....
The resulting complete 140-move erasure is nonincreasing from H=98 to 0 in
both Z3 and A4. Full-holonomy, boundary, inverse and gauge-transport checks pass.
A fresh rerun in a separate Linux checkout reproduces
`topology_decay_order.json` semantically identically. The only difference is the
path separator in its "source" field. **Consequence:** the prepared abelian
linked-loop fixture has NO action barrier to complete erasure under H. Linking
of commuting fluxes gives no energetic protection. The single uphill step of
P13b was an artifact of move order.

## P13 — Are flux links protected by the actual rewrites? (2026-09-19)

Registered before generating the linked mesh fixture or running the new audit.
Code inspection already found a missing over/under factor in `linking_number`
and a missing two-tetrahedra-per-face check in `classify_faces`; their repair is
not a prediction. Validate the linking measurement on Hopf/unlinked controls,
orientation reversal, reflection, subdivision, and rational projection changes.
Degenerate projections must be retried or rejected, never silently rounded away.

**Fixture, not emergence:** Kuhn n=8 with identity boundary. Assign Z3 edge
labels by oriented intersections with two internal rectangular spanning disks:
one at z=17/4 with x in (9/7,37/7), y in (9/7,44/7); one at y=13/4 with
x in (23/7,51/7), z in (16/7,44/7). Coordinates construct this diagnostic input
and measure its embedding only; the rewrite/search rules do not read them.
Lift the same labels into an explicitly declared cyclic order-3 subgroup of A4.
Prediction: the resulting support is two disjoint dual loops with |linking|=1.
If the detector disagrees, report fixture failure without quietly changing it.

**Rewrite test:** apply the existing nonincreasing decay search with at most
32 discovered states per plateau to each fixture. Save all moves and support
classifications, recompute H independently, verify boundary and inverse replay,
and check gauge-transported witnesses. Prediction: the loop-only domain is not
preserved by the permitted rewrites. Whether these linked fixtures decay fully
without an action increase is deliberately open. A budget cutoff is inconclusive.
Save any witnessed junction, split, merger, loop loss, or linking change without
calling it a nuclear reaction. No kinetic rate is inferred from search order.

**Independent exact statement:** with a finite group and all nonidentity right
multipliers allowed on each interior edge, any two assignments sharing boundary
labels are joined by setting differing edges one at a time (multiplier a^-1 b).
This holds on any fixed complex, regardless of knotting; it does not require
every intermediate step to lower H. Thus no nonconstant label observable on
that fixed-boundary space can be invariant under *all* those rewrites. For an
ideal finite-beta Metropolis law all these rates are positive; beta=infinity and
additional constraints require separate analysis. This is a deduction, not a
prediction of experimental survival or exclusion of energetic metastability.

**P13 first outcome:** fixture prediction HIT in both groups: two loops of
lengths 52 and 46 with |linking|=1. The registered search found the action path
98 -> 98 -> 98 -> 96, keeping two linked loops throughout (final lengths 52,44),
then exhausted its 32-state budget. Complete downhill decay and loop-domain
nonpreservation were NOT established by this search. No barrier claim follows.

**P13b follow-up, registered after that outcome and before execution:** audit all
single-edge proposals from the initial linked fixture in both groups. Count
changes in the component-kind/loop-count domain separately for delta-H <= 0 and
delta-H > 0; record the first witness of each kind with full-action replay.
This tests loop-domain closure, not equality of linking for every pair of loops.
Construct the theorem's ascending-edge-order path to identity labels, allowing
uphill steps, and report its peak action as an upper bound for this particular
path only. No numerical barrier or rate is predicted. Preserve the original
32-state cutoff and do not present this follow-up as a successful downhill run.

**P13b outcome:** all 6,064 Z3 and 33,352 A4 initial proposals audited. Each
has eight nonincreasing proposals, all remaining two loops. Uphill proposals
include 367 / 2,860 junction outcomes respectively. Nevertheless the separately
constructed 140-move erasure path has a nonincreasing merger prefix: junction at
move 37 (H=86), one loop at move 38 (H=84), from initial H=98 and |Lk|=1.
Thus the predicted failure of loop-domain preservation IS witnessed by a path,
even though it was not witnessed by the first bounded search or an initial
nonincreasing one-edge move. The full path has exactly one uphill step, 84 -> 85
at move 40, two loops with |Lk|=0 at move 52 (H=80), and flat vacuum at move 140.
Peak H is 98. Necessity of that uphill step remains unproved. Both groups agree
because the prepared labels and erasure path lie in a cyclic subgroup; the A4
one-edge census also included all multipliers outside it. Full data, proof,
controls and scope are in `TOPOLOGY_AUDIT.md` and the two `topology*_audit.json`
records. Complete boundary, inverse, full-action and gauge-transport checks pass.

## P12 — Constructive decay certificates (2026-09-19; before execution)

Use the two archived nonvacuum P11 A4 n=5 endpoints, without rerunning or
changing their initial conditions. Keep H, the mesh, every outer boundary label,
and all nonidentity interior-edge multipliers unchanged. Search equal-H raw-label
states breadth-first until a strict downhill exit is found, then repeat at the
lower action. Limit each plateau search to 1000 discovered states. A reached
budget is inconclusive; only a fully exhausted equal-H component certifies a
closed plateau. No gauge quotient is used for exploration.

Prediction: both endpoints admit a nonincreasing path all the way to H=0.
An immediate downhill exit alone, already known from P11, does not establish this.
Save the complete edge/multiplier witness and independently replay every step
with full holonomy recomputation, exact boundary-label checks, and inverse replay.
This is an existence proof for these endpoints, not a physical scheduler, lifetime,
shortest-path claim, or exclusion of particles in every state of the model.

Controls: vacuum; a single interior-edge excitation in Z3 and A4; independent
vertex-gauge transforms of the archived endpoints with transported witnesses.
No action tuning or replacement particle catalogue is permitted by this experiment.

**P12 outcome:** prediction HIT. Both archived endpoints reach flat vacuum in
two strictly downhill interior-edge moves: seed 0 has H=8 -> 4 -> 0; seed 1 has
H=10 -> 6 -> 0. Full-action forward/inverse replay and independently gauged
witness transport pass, with exact fixed boundary labels. The search did not
need equal-action steps. These are constructive zero-barrier decay certificates;
no shortest-path or decay-rate claim is made. The data are
`reference/astra_session/data/decay_certificates.json`; regenerate with
`python examples/particle_decay_certificates.py`.

---

## P1 — The μ quotient: rigid vs flexible internal-resolution counts (referee item 1)

**Setup.** Cone `v * ∂Δ³` over A₄. Fix boundary labels; declare interior-face flux classes.
Two equivalence relations on admissible interiors `x = (x_0..x_3)`:
- **rigid**: `(x, B) ~ (ν⁻¹x_i, B)` — apex only, boundary labels held pointwise (current code).
- **flex**: quotient additionally by diagonal conjugation `(x, B) -> (μ⁻¹xμ, μ⁻¹Bμ)` — the
  residual freedom when the boundary is fixed only by its gauge-invariant content.

**Predictions (written before running):**
1. The referee's "Klein-four flux drops from 6 to 2" will reproduce under a natural Klein-four
   declaration: rigid count **6**, flex count strictly smaller (**2 or 1**).
2. The full cone census ("patterns with |I|>1 drop from 102 to 45") will NOT reproduce exactly —
   we expect the same *direction* (flex < rigid on every nonabelian pattern) but different
   magnitudes, because our declaration semantics (seeded curvature classes over flat boundary)
   differ from whatever ensemble they used. If flex == rigid for some pattern with nontrivial
   flux, that pattern's interiors are all rigidity-protected and we say why.
3. Z₃ control: flex == rigid on every abelian pattern, by construction (conjugation is trivial).
   This confirms the referee's "the abelian control is blind" point exactly.

**Outcome (run 2025-01-xx, `examples/critique/p1_mu_quotient.py`, 357 s):**

| declaration (flat boundary) | raw | rigid \|I\| (library, corrected) | full-gauge pooled |
|---|---|---|---|
| 3 interior faces V4 / rest flat (star) | 36 | **3** | **1** |
| 5 interior faces V4 / rest flat | 72 | **6** | **2** |
| all 6 faces V4 | 72 | **6** | **2** |
| seeded declaration, all 1728 tree-gauge boundaries | — | **4 (all)** | **1 (sample 40/40)** |

> **Correction during review:** the probe's first rigid column used CONJUGATION (μ⁻¹xμ) for the
> apex action instead of left multiplication (ν⁻¹x); cross-checking against `resolution_space`
> caught it. Corrected values above come from the library itself. With correct semantics the
> referee's exact pair **6 → 2 reproduces verbatim** on the 5-flux-face declaration.

- Prediction 1 **hit after correction**: with library-correct apex gauge, the referee's exact
  "6 → 2" reproduces verbatim on the 5-flux-face declaration; star-3 gives 3 → 1. Mechanism and
  magnitudes both confirmed.
- Prediction 2 **hit**: direction universal (full ≤ rigid everywhere sampled, 40/40 collapses of
  seeded patterns to a single orbit), magnitudes differ per declaration.
- Prediction 3 **hit**: Z₃ control blind by construction (singleton classes).
- Declarations with class-V4-everywhere and *fewer than 3* flux faces are empty: adjacent interior
  faces over a flat boundary cannot both hold order-2 curvature unless the x's differ appropriately;
  K4-coloring obstruction. Nice constraint, unanticipated.

**Verdict:** referee item 1 is CONFIRMED as a convention hazard and REBUTTED as a bug:
`resolutions.py` computes the rigid (apparatus-relative) count correctly; E030's \|I(core)\|=4 is
rigid by definition. The pooled full-gauge count answers a different question (how many gauge-
inequivalent worlds share one appearance — answer: generically one). Fix = state the convention at
every \|I\| quote + ship `pooled_resolution_orbits` for the alternative semantics.

---

## P2 — Spanning-tree root dependence of verdicts (referee item 2)

**Setup.** Kuhn ball n=2, A₄, random labels; region = whole ball so `appearance()` =
boundary face curvatures + probe-cycle classes from a spanning tree of the surface 1-skeleton.
Apply single-edge right-multiplications; record accept/reject verdict under different tree roots.

**Predictions:**
1. Verdict-flip rate across roots is **exactly 0**. Face curvature classes are actual triangle
   holonomies — no basis choice enters them — and any edge move that changes a boundary face
   class is caught identically in every basis.
2. If flips appear, they must come from moves that leave all face classes fixed but shuffle
   cycle charges; the flip rate then measures how much of the predicate's teeth come from the
   (basis-dependent) cycle part versus the (invariant) face part. The referee's 12.4% would be
   evidence for this second mechanism — we will report which it is.
3. Either way: `Appearance.signature()` embeds loop identity and is therefore NOT comparable
   across different bases or between differently-built regions. We predict cross-basis signature
   equality fails on most curved configurations even when the physical state agrees. The fix is a
   simultaneous-conjugacy canonical form of raw based-loop holonomies (complete invariant for
   based loops under vertex gauge).

**Outcome (run, `examples/critique/p2_root_dependence.py`, Kuhn n=2 seed 3):**

- **Prediction 1 MISSED.** Verdict flips across tree roots: **50/294 = 17.0%** — the referee's
  12.4% mechanism reproduces (their number, our sign).
- Attribution exact: all 50 flips are moves where the FACE-only verdict and some bases' full
  verdict disagree; face curvatures behave as predicted (basis-free), the cycle-charge part of
  `Appearance` is basis-dependent and has teeth.
- Within one run (fixed root) Driver A remains self-consistent; cross-basis / cross-region
  signature comparisons are unsound. Fix shipped: `Region.gauge_invariant_state()` =
  simultaneous-conjugacy canonical form of RAW based-loop + face holonomies.

---

## P3 — Gauge equivariance of the proposal dynamics (referee item 3)

**Setup.** Single tetrahedron gauge slice, triples `(A02, A03, A13)`; global conjugation `g`
maps a config to a gauge-equivalent one. For each arm, compute exact accept fractions over all
(free edge × generator) proposals for a config and its conjugate.

**Predictions:**
1. Current arm (`move_generators()` = {s, t, t⁻¹}, not closed under conjugation): equivariance
   FAILS on some configs; we expect discrepancies of order 2/18 (referee reported 4/18 vs 6/18).
2. Class-closed arm (propose uniformly over full conjugacy classes): accept fractions agree
   EXACTLY for every config and every global conjugate — the induced chain descends to orbits.
3. Word cost: with a class-closed generating set, `generator_distance` is invariant under
   conjugation of both endpoints; with the current set it is not (referee's 1 vs 3 example).

**Outcome (run, exhaustive over 1728 triples x 12 conjugators):**

- Predictions 1+2 **HIT hard**. Arm "current" (`move_generators()`, not class-closed):
  **5472/18600 = 29.4%** of gauge-equivalent pairs have DIFFERENT reachable-orbit counts — the
  chain does not descend to orbits; referee item 3 fully confirmed, larger than their example.
- Arm "classes" (all non-identity elements): **0 violations**, exact reachable-orbit-SET
  equality on all sampled pairs. Class-closed proposals make the chain orbit-respecting by
  construction. Shipped as `class_closed_generators()` + equivariance regression test.

---

## P4 — Pachner 2→3 degeneracy claim (referee item 4)

**Predictions:**
1. At HEAD `apply_pachner_2_3` constructs three **4-vertex** tuples `(u,w,a),(u,w,b),(u,w,c)`;
   the claimed "3-vertex tuple" bug does not reproduce in this codebase (it likely came from a
   harness outside it). Round-trip 2→3→2 restores the complex exactly on Kuhn n=2 sites.
2. Boundary (vertices, edges, faces and their labels) is unchanged by the round trip; only the
   interior changes — including the created edge's label surviving as an internal degree of freedom.

**Outcome: PREDICTION 1 WRONG — referee right, we wrong; pre-registration earned its keep.**
HEAD literally built `((u,w,a),(u,w,b),(u,w,c))` — three **3-vertex** tuples — crashing
`add_tetra` mid-mutation (after 2 tets removed + edge added), corrupting the complex; every
later site then failed with cascading MoveErrors. No test had ever exercised the move. Fixed to
`(u,w,a,b),(u,w,b,c),(u,w,c,a)` (new edge x face EDGES) + transactional guard;
`tests/test_pachner.py` pins legality, boundary preservation, exact revert, sequential
stability; 72/72 Kuhn n=2 sites round-trip clean. Commit `1434a1c`.

---

## P5 — Spectral dimension of the mesh (referee item 9)

**Setup.** Diffusion (random walk) on tetra-adjacency and vertex-graph structures of Kuhn balls
n = 1..4; return probability P(n_steps); d_s(t) = −2·dlogP/dlogt estimated locally.

**Predictions:**
1. Long-time spectral dimension ≈ **3** (within ~[2.5, 3.5]) at n≥3 — consistent with the
   3D input; this is a *consistency check*, not an emergence claim, and will be labeled as such.
2. Short-time d_s deviates strongly (lattice effects); we record the full curve rather than one number.
3. Vertex-1-skeleton diffusion gives d_s ≈ 3 as well; if it doesn't, that is a real finding about
   the walk structure and gets its own diary entry.

**Outcome (run, `examples/critique/p5_spectral_dimension.py` + tests/test_spectral.py):**

- Prediction 1 **MISSED at accessible sizes — and so would ANY lattice claim**: the matched
  control Z³ box (6³) reads d_s ≈ 2.0 over t∈[2,8], not 3. Finite-size/backtracking dominance,
  not fractality. Kuhn balls: n=1 → 0.59, n=2 → 1.56, n=3 → 1.76 (tetra graph), rising with
  size as expected for ordinary 3D lattices.
- The defensible statement is the MATCHED-CONTROL one, now pinned by test: Kuhn-ball diffusion
  agrees with a comparable cubic-lattice box within tolerance; no anomalous dimensional
  collapse. Absolute d_s → 3 needs larger meshes or heat-kernel extrapolation (follow-up).
- Prediction 2 hit in spirit: full P(t) curves recorded; odd-time zeros from bipartite structure
  are physics, handled explicitly.
- Methodological note for the referee: their demand "show it returns 3" was itself naive about
  finite-size effects — we return the honest version instead.

---

## P6 — Density normalization artifact (referee item 13)

**Setup.** Kuhn ball n=2, Driver A run ~5000 events; shells around centre; compare raw per-cell
`rho(cell)` with per-vertex `rho/|cell|`; vacuum control = same driver, flat labels.

**Predictions:**
1. Raw per-cell counts show a **size artifact**: outer shells (more vertices) accumulate more
   total events at uniform activity, so raw rho rises with shell size even in featureless runs.
2. Per-vertex normalization flattens the vacuum profile; defect-core excess survives and remains
   positive — i.e. the qualitative gravity-like signal is not an artifact, but its magnitude in
   the old plots was basis-confounded and gets re-measured.

**Outcome (run, 4000 accepted events per arm):**

- Prediction 1 **HIT**: corr(raw rho, shell population) = **+0.41**; raw profile partly census artifact.
- Prediction 2 **MISSED — worse than expected**. Vacuum / charged / neutral arms produce
  **bit-for-bit identical** profiles (20.5 / 637.0 / 376.5 in all three). Under Driver A with
  appearance-only conservation, acceptance depends only on interior-vs-surface edge membership,
  not on labels or defects: **event density carries zero matter information** in this setup.
- Referee item 13 upgraded from "normalize the histogram" to: the M7 gravity claim currently has
  no empirical content beyond acceptance-region geometry (delay was already formula-prescribed,
  backlog item 4). Honest status: awaiting a driver whose event placement depends on curvature
  (Driver B churn does — residue cleanup concentrates events near flux). Nothing tuned, nothing deleted.
- Fix shipped regardless: population-aware `rho_per_vertex`, baseline = total_events /
  total_vertices; regression test pins equal-per-vertex activity -> equal n across shell sizes.

---

## P7 — Softened-predicate confinement pilot (referee item 5; queued as first real physics)

**Status:** NOT YET PRE-REGISTERED — will be written before that experiment runs, with an area-law
scaling prediction for boundary-residue production under penalty λ. Listed here so the queue is visible.

**Design controls adopted from R3 panel (Opus R3 design note; recorded BEFORE any run):**
(1) vary the STARTING CONFIGURATION as well as λ — a near-flat start (71/72 identity surface edges)
is an independent forcing reason for confinement beside the definitional predicate, and a single
flat seed would silently confound the two; (2) report per-start statistics, not pooled ones, so a
confinement signal attributable to seeding cannot masquerade as one attributable to λ;
(3) include λ = 0 (unpenalized appearance-predicate baseline) in every sweep.

---

## P8–P11 — imported from the Astra session (2026-09-18)

Provenance: entries P8–P11 were written, run, and outcome-appended by **Astra** in the sibling
checkout during 2026-09-18; machine-readable records are archived at
`reference/astra_session/data/` (landscape.json, runs.json, candidate_audit.json, scale_runs.json;
full per-event traces regenerate via `examples/particle_search.py`, `particle_candidate_audit.py`,
`particle_scale_search.py`). Imported verbatim 2026-09-19 after code merge; local reproduction of
P11 in this tree recorded under "Reproduction" below.

## P8 — Interaction repair and unfrozen particle baseline (2026-09-18, Astra)

Written before the new interaction census or energy-landscape search. The earlier
class-only counterexample is already known and is not a prediction.

**Interaction convention.** Default matching will require a single relative apex
frame aligning the whole ordered shared-face flux tuple. Raw equality and
individual class equality survive as explicitly named controls. This follows the
existing apex gauge action and preserves its relational information; it is not
a derivation of a collision law. An alignment is an existence witness, not an
extra statistical weight per pair of states.

**Predictions:** independent left-multiplication of either cone's spokes leaves
default compatibility unchanged; the saved class-only counterexample is rejected;
Z3 agrees across all three conventions. The historical A4 phase-independent
12-versus-3 probe counts remain true only in the raw-frame control. Default counts
will vary with the object's simultaneous-conjugation stabilizer; no suppression
factor is predicted for that different experiment.

**Particle baseline.** Enumerate the A4 tetrahedral-boundary gauge slice and all
physical one-edge nonidentity right-multiplication moves (including tree edges,
gauge-fixing after each move). Action H is the number of curved faces. Find connected
equal-H plateaus and whether any move leaves each plateau downhill. A plateau with
no exit is a zero-temperature metastable candidate; a one-state minimum test is
insufficient. Repeat over Z3. No boundary is frozen in this closed-surface diagnostic;
this is a landscape control, not the 3D bulk matter experiment.

**Prediction:** vacuum is the only closed downhill basin in this smallest seed.
If so, neither a nonzero flux nor a D(A4) sector label alone establishes a stable
classical particle under this reduction action. Report that failure before trying
larger complexes or another declared action. Do not change H to favor a desired
catalogue after seeing the result without a new prediction.

The particle/reaction pass criteria are in `PARTICLE_PROGRAM.md`.

**P8 landscape outcome:** prediction HIT. Exhausting all physical edge moves
from 1728 A4 raw slice states gives 178 physical states, zero nonvacuum closed
equal-action plateaus, and a nonincreasing path to vacuum from every state in at
most three moves. Z3: 27/27 states have such a path in at most two moves. This
excludes zero-temperature metastable particles for this action on this seed,
not on larger bulk complexes or under all possible drivers.

**Local verification (this tree, 2026-09-19):** interaction-convention predictions pinned by
`tests/test_interaction_frames.py` (left-multiplication invariance, counterexample rejection,
Z3 agreement across conventions) — suite green after merge.

## P9 — Unpinned 3D curvature dynamics (2026-09-18, Astra; before execution)

**Setup:** Kuhn balls n=2 and n=3, Z3 and A4, fixed identity outer boundary,
all interior edges eligible, no fixed core. Uniform edge proposals and uniform
nonidentity group multipliers; action H = number of curved faces. Metropolis
acceptance min(1, exp(-beta delta-H)) is a declared stochastic driver hypothesis.
Beta is a dimensionless action penalty, not an independently derived temperature.
Controls beta=0 (unweighted), beta=infinity (downhill with equal-action moves),
and beta=1,2. Two starts: uniform interior labels and dilute random interior-edge
perturbations (no prescribed particle shape). Seeds 0,1,2, 10,000 proposals each.

**Predictions:** unweighted runs will remain highly curved; downhill runs will
lose most initial curvature. Larger A4 balls may have long-lived traps, but neither
their existence nor fusion/fission/chemistry is predicted. Finite-beta loops may
be short-lived thermal structures. The outer boundary remains exactly fixed in
every arm, but persistence of a defect's own residue is not imposed.

**Measurements:** H(t), accepted/rejected counts, exact action-change ledger;
dual-face connected components, loop/junction classification, component sizes
and overlap-based lineage. Birth/death/merge/split counts describe support geometry
only. Do not call these particle reactions without independent stability evidence.
Track at every accepted move; rendered frames may be subsampled. Archive all
seed/model/start parameters and aggregate all runs, including zero-particle runs.

**Particle candidate screen:** a branch surviving at least 1000 proposal steps
with at most 20% of the mesh's tetrahedra in its support. This is a declared
screen, not a sufficient particle definition. Test survivors for a downhill exit
and control against system-size-spanning frozen networks before any promotion.

**P9 outcome:** all 96 registered runs completed (960,000 proposals). Across
all arms: 2,461 geometric merges, 2,485 splits, and 57 branches passing the
preliminary lifetime/size screen. These are not particle/reaction identifications.
22/24 downhill runs reached vacuum within 10,000 proposals. The other two (A4,
n=3, uniform seeds 0 and 1) ended at H=17 and H=24, but respectively had six and
five immediately available downhill proposals: neither endpoint is a local minimum.
All outer boundaries and action/bath ledgers stayed exact. Full records:
`reference/astra_session/data/runs.json` and per-run compressed event traces
(regenerable).

## P10 — Audit apparent longevity before naming particles (2026-09-18, Astra)

Registered after P9, before replaying screened branches. P9's fixed 1000-proposal
threshold is mesh/group dependent: any particular destroying move is proposed
only once per E_interior*(|G|-1) proposals on average. This can manufacture apparent
longevity in A4 without an energy barrier. Do not equate proposal age with proper time.

**Test:** reconstruct each of the 57 qualifying branches at age 1000 from saved
event traces; exhaust all permitted moves touching it. Count immediate downhill
moves and single-move erasures (all its curved faces become flat, no other face's
holonomy changes). Record age divided by E_interior*(|G|-1), support changes,
and the local fraction of destroying proposals. Any exact erasure is a zero-barrier
decay witness. Absence of a one-step erasure is not proof of metastability.

**Prediction:** a substantial fraction are simple waiting-time artifacts and admit
immediate erasure; no fraction is predicted. Extend both nonvacuum downhill endpoints
to 200,000 proposals with the same RNG streams and action. Prediction: both eventually
reach vacuum. The extension is a declared follow-up, not extra attempts hidden in P9.

**P10 outcome:** all 57 branches replayed successfully with action checked after
every event. Every branch had an immediate local downhill move; 42/57 had an exact
one-move erasure leaving all other face holonomies unchanged. The 15 remaining
cases are not thereby stable; only this sufficient erasure test failed. The two
extended runs reached absorbing vacuum at proposals 15,157 and 17,523, respectively,
and stopped there (a positive-action proposal cannot leave vacuum at infinite beta).
No stable particle species or binding was established. Records:
`reference/astra_session/data/candidate_audit.json`.

## P11 — Larger-mesh trap search (2026-09-18, Astra; before execution)

The n=2,3 negative result does not exclude larger linked/junction structures.
Keep the same action, fixed outer boundary and class-closed proposal law; change
only size and the declared stopping horizon. A4 and Z3, n=4 and n=5, uniform starts,
seeds 0,1,2; downhill-only, up to 200,000 proposals each. Stop early only at the
provably absorbing vacuum. Every 1000 proposals record action and support components.

**Prediction:** relaxation slows with mesh size and group order; no claim that
nonvacuum endpoints are stable. Exhaust local proposals at every nonvacuum endpoint.
If any endpoint has zero downhill moves, enumerate equal-action connected moves
until a downhill exit is found or a predeclared 100,000-state budget is exhausted.
A budget exhaustion is inconclusive, not evidence of a closed plateau. A reachable
downhill exit excludes that plateau as a zero-temperature stable basin.

**P11 outcome (Astra run, records `reference/astra_session/data/scale_runs.json`):**
prediction HIT on both clauses. Relaxation slows with mesh size AND group order:
Z3 n4/n5 reach vacuum in 6.6k–47.3k proposals; A4 n4 in 45.1k–59.0k; but **A4 n=5
seeds 0 and 1 do NOT reach vacuum within the 200,000-proposal horizon**, ending at
H = 8 and H = 10 (from H0 ≈ 1250) — while A4 n=5 seed 2 finishes at 118.1k steps.
Per protocol both nonvacuum endpoints were audited exhaustively: each has downhill
exits (2 each; equal-action proposals 20 and 2), so NEITHER is a local minimum and
NO stability claim is made. What the horizon captures is **non-abelian critical
slowing-down without metastability**: at identical size, Z3 finishes in ≤47k while
A4 fails to finish in >200k on 2/3 seeds — glassy relaxation near vacuum created by
proposal-dilution of rare destroying moves (at the s0 endpoint only 2 strict-downhill
proposals exist among 665 interior edges × 11 multipliers = 7,315 possible proposals,
≈0.03% per proposal), not by an energy barrier (barrier-free traps, P10's mechanism at scale).

**Reproduction (this tree, 2026-09-19): EXACT.** Local rerun of
`examples/particle_scale_search.py` reproduces all 12 runs bit-for-bit — identical step
counts to vacuum (6,638 / 11,204 / 9,591 / 37,969 / 28,454 / 47,305 / 49,479 / 59,009 /
45,113 / horizon / horizon / 118,093), identical final actions (all 0 except s0→H=8,
s1→H=10 at A4 n=5), identical endpoint audits (downhill 2/2, equal 20/2). Deterministic
seeded streams make the campaign exactly reproducible across checkouts; log:
`out/particle_search/scale_rerun.log`.

---

## E069 — N-ality: does a non-self-dual charge supply the selection rule E068 said was missing?

**Registered 2026-09-21 by local Qwen, BEFORE running `examples/e069_nality_and_dyons.py`.**

**Context.** E068 closed with: *confinement is not persistence* — Gauss protects charge number but
nothing prevents a confined pair from meeting and annihilating, because retracting the string lowers
energy. It concluded that matter needs a **charge-conjugation selection rule**. This experiment asks
where such a rule can come from, in the cheapest available setting: replace the gauge group Z2 by
Z_N (N = 3), so that charges are no longer all self-inverse.

**Construction.** `GaussStateZN`: electric flux a_e ∈ Z_N on each edge (oriented u<v, flow u→v),
charges DEFINED by the solved constraint q_v := div(E)_v mod N. Magnetic sector unchanged
(curvature B_f = face holonomy of connection labels). Energy H = β_B·#{curved faces} +
β_E·Σ_e |a_e| with |a| = min(a, N−a). Dynamics in `drivers.DriverGZN` (RNG lives only there).

**Definitions under test.** Maximal pairwise cancellation of live defect charges {k ↔ N−k} leaves a
residual multiset R (the *N-ality content*). Config with R = ∅ is **mesonic** (pair-cancellable);
R ≠ ∅ is **baryonic** — in Z3 the minimal such object is three like charges (1,1,1), which sum to 0
mod 3 yet contain no cancelling pair.

**Priors, stated before running:**

- **PA (structural, asserted every step).** Σ_v q_v ≡ 0 mod N identically; a flux update on edge e
  changes charges only at the two endpoints of e, by opposite amounts. If either fails it is a bug.
- **PB (Z2 control).** For N = 2 every neutral configuration is pair-cancellable: R = ∅ always, so
  Z2 has NO baryonic content and no selection rule of this kind exists there. Expected to hold
  identically; reproduces E068's annihilation as the generic case rather than an accident.
- **PC (the new physics).** In Z3 a seeded triple (1,1,1) is irreducible: its live-defect count is
  invariant at 3 until an annihilation event drops it to 0, whereas a meson goes 2 → 0 by pairwise
  contact. Prior: **median time-to-vacuum(baryon) > median time-to-vacuum(meson)** at matched β_E,
  because decay requires multi-body coincidence instead of a two-body encounter.
- **PD (dyons).** The abelian model has NO flux–charge coupling: proposals and energies factorise
  between the g-sector and the E-sector, so it is a product chain. Prior: (i) the magnetic observable
  #{curved faces} has the same distribution with an electric string present as absent (within sampling
  error), and (ii) the per-vertex charge–curvature cross-correlation stays at the level of the separated
  control for all t, seeded co-located or not. If a correlation grows, my factorisation claim is wrong
  and that is the interesting result.

**Explicit non-goals.** No cross-coupling term is inserted to manufacture dyons; no particle label,
pinning or trajectory is introduced. A null on PC (baryons decay as fast as mesons) would mean
N-ality does not supply stability either, and will be reported as such.

**E069 OUTCOME (`examples/e069_nality_and_dyons.py`, data `reference/local_qwen/data/e069_nality_dyons.json`):**

* **PA -- HIT.** Held at every step of every run (asserted in the driver): total charge 0 mod N, endpoint-only
  support changes.
* **PB -- HIT.** Z2 exhibits no baryonic content whatsoever (exhaustive classifier test over neutral multisets);
  E068's annihilation was the generic self-dual case.
* **PC -- REFUTED in its strong form; direction partially right, mechanism WRONG.** Baryons do outlive mesons
  (median t_vacuum 2642 vs 1863 at beta_E=12, per-seed delay +1 to +2169 steps) but **all six decay** within
  12,000 steps: [1899, 2261, 3023, 3135, 1833, 3966], 0/6 survivors. The claimed three-body-coincidence barrier
  does not exist: charge is additive at a vertex, so two unit charges fuse into the antiparticle of the third and
  annihilation proceeds by a two-step route. N-ality = kinetic hindrance, NOT selection rule.
* **PD -- HIT (confirmed).** Tail curved-face count identical with/without an electric string (4.508 vs 4.510);
  charge-curvature correlation seeded co-located decays 0.2569 -> 0.0534, i.e. to the merely-present level
  (0.0528). Abelian sectors factorise: no dyons.
* **Unplanned finding.** Plasma threshold: at beta_E=2 the unseeded vacuum carries ~25.6 spontaneous charges and
  reads baryonic 66% of steps; clean only for beta_E >= 8. My first harness run was done below threshold and its
  lifetime numbers were discarded as meaningless -- matched-vacuum discipline is now enforced by seeding asserts.

**Consequence (registered here so the next unit inherits it).** The stability mechanism E068 asked for cannot be
abelian. Next candidates, in order of cheapness: (i) superselection with an inaccessible balancing charge --
decay then requires walking to the boundary reservoir, giving a distance-scaling lifetime that is measurable;
(ii) nonabelian Gauss completion where fusion rules restrict which outcomes exist at all.

---

## E070 -- What would stability actually cost? Superselection and Kramers scaling of a confined charge

**Registered 2026-09-21 by local Qwen, BEFORE writing or running `examples/e070_wall_stability.py`.**

**Why this is the right next question.** E068 demanded a selection rule; E069 showed abelian charge arithmetic does
not supply one. Before hunting for an emergent mechanism, measure which mechanisms *would* work here and what their
signature is. This unit claims NO emergence: the wall is imposed structure, declared as such. The purpose is to learn
what an emergent version must reproduce -- otherwise "stability" is unfalsifiable hand-waving.

**Construction (coordinate-free).** A *wall* is a set of edges defined by graph-distance layers around a chosen seed
charge: W_k = {edges joining BFS layer k to layer k+1 from that charge}. Grid coordinates are not used; the definition
is purely relational. Two variants: **hard wall** -- flux proposals on W_k are structurally disallowed (the driver may
not propose them); **soft wall** -- flux crossing W_k costs an extra lambda per unit |a_e|, i.e. electric weight w_e =
lambda on wall edges and 1 elsewhere. A meson is seeded with one charge inside the wall and its partner outside; Gauss
still holds by construction because only admissibility of rewrites changed.

**Priors, stated before running:**
* **SA (conservation law, asserted every step).** With a hard wall the total charge enclosed is invariant under every
  allowed move: flux cannot cross, so the interior sum of q is frozen. If it changes, the wall leaks and nothing else
  here means anything.
* **SB (hard wall = absolute stability).** An interior charge whose balancing partner sits outside can neither
  annihilate (no antiparticle can enter) nor escape (flux cannot cross). Prior: lifetime = full horizon for every seed,
  at any beta_E, while the no-wall control decays near E069's value (~1800 steps at beta_E = 12).
* **SC (soft wall = Kramers/Arrhenius scaling).** With finite lambda the pair can still annihilate by diffusing around
  or through the wall, and mean first-passage time should grow exponentially in the barrier: log t_vacuum ~ c * lambda
  plus a lambda-independent attempt-time offset. Prior: positive slope, roughly linear over lambda in {1,2,4,8}, with
  censoring (survivors) appearing at the top of the scan.
* **SD (what would falsify the framing).** If the hard wall does NOT stabilize, then restricting admissible rewrites is
  not sufficient here -- annihilation must be proceeding through a channel I have not modelled (a charge riding on the
  wall itself, or my enclosure failing to be a true cut). That would be the most interesting outcome and would be
  reported as such.

**Explicit non-goals.** No claim that walls emerge; no particle label, site-specific pinning potential, or forced
survival. The wall is a boundary condition on admissible rewrites -- the honest analogue of putting the balancing
charge somewhere the dynamics cannot reach.

**E070 OUTCOME (`examples/e070_wall_stability.py`, data `reference/local_qwen/data/e070_wall_stability.json`):**

* **SA -- HIT.** With a hard wall the enclosed charge sum was asserted invariant at every step of every run; no leak.
* **SB -- HIT (absolute stability by superselection).** Hard-wall runs: 3/3 survive the full 8,000-step horizon with
  at least one live defect inside at all times (min live inside = 1), while the identical no-wall control neutralises
  at t = [11, 3393, 2408]. The enclosed sector cannot be emptied because neutrality would require net crossing flux to
  change and crossing flux is frozen. **Stability = the region cannot become neutral.**
* **SC -- REFUTED, with the mechanism identified by census rather than assumed.** The soft-wall scan is exactly flat:
  t_region_neutral identical for lambda in {1,2,4,8} ([11, 3393, 2408] every time; log-log slope 0.000). The census of
  accepted wall-touching moves explains it: **up = 0, down = 3** -- every accepted change to crossing flux is
  RETRACTIVE. Retracting a string lowers energy for every lambda, so weighting crossings pays the system MORE to
  annihilate; no value of lambda can slow a path that never has to go uphill. Kramers scaling requires an uphill
  segment on the decay path, and string retraction has none.
* **SD -- not triggered.** The hard wall did stabilize, so restricting admissible rewrites IS sufficient here.

**The lesson registered for the theory (this is the load-bearing sentence of E070).** In this framework energy can
only bias rates among reductions that exist; it cannot remove a reduction. Cost therefore cannot protect a particle --
**only structure can**: an obstruction that makes the shortening rewrite unavailable, not expensive. That is precisely
what knotting/topological flux-tube closure is supposed to supply, so E070 converts the project's knot hypothesis from
a preference into a requirement: if matter is to be stable, its protection must be a missing move, not a high one.

---

## E071 -- Does link type protect electric flux? (the knot hypothesis put against the move set)

**Registered 2026-09-22 by local Qwen, BEFORE writing or running `examples/e071_link_lifetime.py`.**

**Context.** P13-P15 already established that MAGNETIC flux links give no activation barrier under the curvature
action (linking forces a tether; the tether shortens and the loops unlink and shrink). Untested is the ELECTRIC sector
built in E067-E069: closed electric flux loops with div E = 0, i.e. flux with no charges at all. This is the cleanest
possible test of the project's core claim -- that entanglement in 3D is what makes matter persist -- because a Hopf
link is an exact, computable invariant of the prepared fixture.

**Fixtures (verified before running; grid coordinates used ONLY to build and measure them, never in any rule).** On
the n=4 Kuhn ball: A = an 8-edge square loop at z=2; B = an 8-edge rectangle with linking_number(A,B) = -1 (Hopf);
B' = the same shape displaced with linking_number(A,B') = 0. All three are closed, hence carry zero charge. Arms:
single (A), linked (A+B, Lk=-1), unlinked (A+B', Lk=0); linked and unlinked arms have identical total flux length
(16 edges), so any lifetime difference is topological rather than size.

**Dynamics.** DriverGZN on Z2 and Z3 at beta_B = 6, beta_E = 12 (above the E069 plasma threshold, so vacuum stays
clean and single objects are trackable). Horizon 4000 steps, seeds 0-5.

**Priors, stated before running:**
* **LA -- no topological protection.** Median lifetime(linked) == median lifetime(unlinked) within seed scatter. The
  reason is structural: decay proceeds by deleting one flux edge at a time, and deleting an edge of a loop never
  requires changing the link type of what remains. Sub-prediction: t(pair) > t(single) simply because two components
  are eaten independently (roughly the max of two single lifetimes), with the SAME factor for linked and unlinked.
* **LB -- deletion dominates.** At beta_E = 12 accepted flux-DELETING moves far outnumber creations, and upward
  excursions of total flux length stay small; decay is close to monotone in flux length.
* **LC -- the invariant is mostly undefined along trajectories.** Deleting one edge creates two charges, so the flux
  support stops being a union of closed loops almost immediately; link/knot class exists for the prepared fixture and
  for rare divergence-free slices, not generically during decay. Reported as a measured fraction.
* **LD (proposition, to be tested exhaustively rather than sampled).** Restricting moves to those that keep q = 0
everywhere admits NO single-edge move at all: changing flux on edge (u,v) by delta shifts q_u by -delta and q_v by
+delta, both nonzero for any delta != 0. So "charge-free = protected" is really "charge-free = frozen": a theory with
no dynamics. If some edge/delta pair survives the restriction, my reasoning is wrong and that matters.
* **LE -- what would count as a discovery.** linked >> unlinked by more than seed scatter. That would mean abelian
  electric flux does have topological protection after all, contradicting LA's mechanism argument, and I would report
  it as the headline result rather than explain it away.

**Explicit non-goals.** No new move types inserted to help or hurt knots; no knot label fed into acceptance; fixtures
are prepared states (declared), not claimed emergent.

**E071 OUTCOME (`examples/e071_link_lifetime.py`, data `reference/local_qwen/data/e071_link_lifetime.json`):**
Fixtures verified before use: Lk(A,B) = -1, Lk(A,B') = 0, all three loops 8 edges and charge-free.

* **LA -- HIT (no topological protection).** Z2 medians: linked 1638 vs unlinked 1443 from one decayed seed each,
  with 3/4 survivors in BOTH arms; Z3: 0 decays in either arm within the horizon. Link type changes nothing.
* **LB -- HIT, more strongly than expected.** Creations = 0 and max upward excursion = 0 in every run at beta_E = 12:
  total flux length is monotonically non-increasing. Decay is pure deletion, exactly as the mechanism argument said.
* **LC -- HIT.** Fraction of steps that are divergence-free: 0.028-0.098. The link/knot class exists for under a
  tenth of every trajectory; after the first deletion it is gone entirely. Topological labels are properties of
  prepared fixtures here, not of evolving states.
* **LD -- HIT (with an important limit).** Exhaustive over single-edge moves: Z2 604/604 and Z3 1208/1208 create
  charges; zero preserve q == 0. So the charge-free sector is frozen *against single-edge moves*. It is NOT frozen
  against multi-edge moves -- adding flux along a closed cycle preserves divergence -- and that loophole is the whole
  point of what follows.
* **LE -- not triggered.** No discovery: abelian electric flux has no topological protection in this move set.

**Unplanned finding (the real harvest): apparent longevity here is proposal dilution, not structure.** Deletions are
rare (~6 per 2000 steps) purely because a deleting proposal must hit one of the 8 occupied edges; Z3 lives longer than
Z2 only because 1 of 2 nonzero deltas deletes rather than 1 of 1 -- the same proposal-law confound flagged in E069.
Nothing about the loop's topology entered the accounting.

**The trilemma this closes (register as the standing frame for matter-model work).** For flux in this kind of move set:
(1) if the dynamics can act at all, flux decays by local deletion and link/knot type is irrelevant -- and undefined
most of the time; (2) if you forbid what creates charges, single-edge dynamics vanish and the sector is frozen -- no
physics; (3) therefore protection needs a THIRD option: a *local* move set that preserves divergence so topology is the
only obstruction, while still permitting motion. Concretely: flux updates along boundaries of elementary faces (the
toric-code / string-net local rule). Under such a rule an unlinking event cannot be done by deleting one edge; it must
pass through configurations of greater total length -- a barrier whose origin is topological rather than imposed, which
is precisely what E070 said any real protection must look like. Registered as the next unit (E072), including the
caveat that global cycle-flips would again reduce protection to dilution, so locality of the move is part of the claim.

---

## E072 -- Face-boundary dynamics: does a LOCAL divergence-preserving move set make topology protective?

**Registered 2026-09-22 by local Qwen, BEFORE writing or running `examples/e072_face_flip_links.py`.**

**Move set (the third option from E071's trilemma).** A move adds flux delta in Z_N to the three edges of one
*elementary triangular face*, oriented around it. Because a closed triangle enters and leaves each of its vertices, div E
is unchanged: **charge is conserved identically by construction**, not by penalty, and starting from a charge-free
fixture the support stays a union of closed cycles at every step. That would be the first setting in this project where a
link class is a well-defined observable of the *evolving state* rather than only of a prepared one. Energy is electric
length only (the magnetic sector is untouched by these moves). The complex is a 3-ball, hence contractible: every cycle is
a boundary, so vacuum remains reachable from any loop -- protection, if it appears, must be a barrier along the path, not
a superselection rule.

**Arms.** Same verified fixtures as E071 on the n=4 Kuhn ball: single (A), linked (A+B, Lk = -1), unlinked (A+B',
Lk = 0); groups Z2 and Z3; seeds 0-2; uniform face proposals (no importance sampling -- kinetics reported as they are).

**Observables.** Total flux length L(t) and its upward excursions above L(0); time to vacuum; a cycle decomposition of the
support at each snapshot with pairwise linking numbers, giving linked-fraction rho_link(t) = fraction of snapshots whose
configuration contains a linked pair.

**Priors, stated before running:**
* **FA (structural).** q_v == 0 for every vertex at every step of every run. If any step produces charge the face move is
  implemented wrong and nothing else here counts.
* **FB (barriers appear).** Unlike E071, where upward excursions were exactly zero in every run, decay under face moves
  must pass through LONGER configurations: prior max(L - L0) > 0 in most runs. This is the qualitative signature that we
  have left the monotone-deletion regime behind.
* **FC (the physics question).** Linked pairs outlive matched unlinked pairs, and by more than seed scatter. If this holds
  it is the first positive evidence in this project for topological protection of matter in a local move set. If it fails,
  locality alone does not rescue the knot hypothesis either -- an important negative that would substantially narrow what
  the theory can claim.
* **FD (barrier crossing signature).** The unlinking event -- where rho_link drops from 1 to below 1 -- coincides with a
  local maximum of L(t), specifically L above its running median at that step. Protection should be visible as an event,
  not only in averages.
* **FE (honest kinetics caveat).** Lifetimes remain proposal-dependent; Z2 vs Z3 numbers are compared qualitatively, and
  the rate at which proposals actually hit a support-adjacent face is reported so dilution can be read off directly.

**Explicit non-goals.** No knot label in acceptance; no inserted coupling; fixtures declared as prepared states. If FC
fails I will report it as a failure of the hypothesis, not as a measurement problem.
