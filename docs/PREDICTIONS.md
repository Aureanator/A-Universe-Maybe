# Pre-registration log

Discipline (referee item 15): every experiment below was **written down before it was run**.
Predictions carry the date and mental state of their writing. Outcomes are appended verbatim
after the run, never edited into the predictions. If we are wrong, the wrongness stays visible.

This file is the epistemic shield for the critique-response work (`docs/CRITIQUE_TRIAGE.md`).

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
