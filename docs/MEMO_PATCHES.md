# MEMO PATCHES (Layer-2 brief item 7)

Concrete, applied-to-text patches for `Memo.txt`. The memo is preserved unmodified as a
historical document; these are the corrections the audit trail requires. Each patch cites
the code/tests that now back it.

## P1 — Section 8 first sentence (name the object)

Replace opening of §8 with:

> "The quantum structure of this framework is the representation category D(A₄) of the
> Drinfeld double — Dijkgraaf–Witten gauge theory / Kitaev's quantum double — newly derived
> from the axiom 'directed implications reduce' plus boundary preservation. The kinematic
> sector (flux-charge sectors, fusion, braiding) is therefore a known mathematical object;
> the derivation from a single logical axiom is the contribution at that level."

Backing: `category.py` + `tests/test_category.py` — full modular data computed and verified
(14 sectors, S/T/Verlinde, (ST)³ identity, class algebra C₂²=3C₁+2C₂ exact, shift rule).

## P2 — Novelty statement (scope it honestly)

Add after P1 sentence: novelty is (i) sectors as internal-resolution spaces of
boundary-preserving dynamics (`resolutions.py`, `entropy.py`), (ii) event-ontology beneath
the gauge data (do-undo/veto semantics, driver hypotheses), (iii) the gravity attempt via
activity-sourced density and holographic entropy. Not novelty: anyon classification,
fusion, braiding themselves.

## P3 — Section 4 reorder (knot anchor first)

Lead §4 with knot-stability (3D as unique dimension for stable PL knots — references no
group), then ∧²W ≅ W as the algebraic confirmation ("geometry must respond to content:
curvature is a 2-form; it can act on the state space only when 2-forms live in the same
representation space as displacements"), then the link-recursion locality axiom (link of a
vertex in C₃ is two disconnected points; first cyclic-at-every-node link is ∂Δ³). The
triangle is demoted, not excluded: it survives as the face cycle / charge fiber.

## P4 — Section 5 provisional flag

Mark "Matter = persistent fixed point F(O) ≅ O" **provisional** pending Driver B:
F := closure of one driver sweep; persistence := σ-cycle membership + invariant constancy.
Operationalized in `drivers.py` (DriverB verified-bijective churn, clock spectrum).

## P5 — Section 7 Born-rule demotion

Reword §8's measurement paragraph: sample space = fusion channels of D(A₄) (canonical);
the probability **measure** remains one declared postulate (equal a priori weight per
micro-resolution). Envariance route (swaps of boundary-indistinguishable resolutions are
boundary-invisible by construction) and Gleason route named as open tasks; pair-state
constructor is the envariance prerequisite, still to be built.

## P6 — Section 9 rewrite against known programs

Credit analog gravity (Unruh 1981; Barceló–Liberati–Visser review) for the refractive half
as solved prior art; name Jacobson 1995 as the field-equation route and state what we have
for it: an entropy functional S(R)=log|I(∂R)| (`entropy.py`) with first measurement —
**vacuum hidden-resolution entropy is exactly zero at every measured radius** (flat fillings
rel boundary unique, ×3 sizes), so horizon entropy must be defect-carried; free-curvature
baseline grows volume-like (S = 0, 2.197, 7.690 for |∂R| = 12, 24, 34). Backreaction is the
missing theorem; Clausius δQ=TδS open.

## P7 — "20 signatures" second-quotient statement (§6/§12)

Replace every bare "20 coarse curvature signatures" with: **82 ordered** face-class
4-tuples; **20 = multiset-sort count** (what the memo's "20" actually is); true vertex-
relabeling orbits are **13 (A₄) / 11 (S₄)** — relabeling can invert edges and flip order-3
chirality, so sorting is not a group quotient. Backing: `reference/opus_audit/` with
corrections applied in its README.

## P8 — Achievements list pruning (§10)

Move to open problems: #7 matter fixed point (P4), Born rule as derivation (P5). Relabel
#10 "quantum sectors" → "D(A₄) kinematics derived and verified (known object, new route)".
Add as new results: confinement exactness; vacuum-twin zero-static-density; accept-rate-
topology identity; Bianchi-as-rank-theorem (isolated flux unrealizable, `strings.py`);
convention-refereed S-matrix ((ST)³ separates chiralities unitarity cannot see).

## P9 — Audit paragraph (the cite-forever block)

Add §15: "D(A₄) supplies 14 sectors, fermionic-twist dyons (θ=−1 on two V₄ dyons), spin-1/3
loops, non-abelian fusion, and ω phases as R-eigenvalues; it supplies no chirality of
fermions, no gapless photon, no bulk point fermions. Electromagnetism requires a deconfined
continuum limit; spectrum reduction 14→few requires anyonic condensation. Verdict: A₄ is an
excellent microscopic skeleton and a definitively insufficient infrared theory — both halves
are results." Caveat kept: θ=−1 is twist, not yet exchange statistics (R-symbol check open).

## P10 — Gapless-photon problem statement (§11 top slot)

"Open problem 1: DW phases for finite G are gapped; the photon is gapless. Candidate
resolutions: critical growth dynamics, anyonic condensation, or a separate-sector origin.
Falsifiable and bounded; the sim is referee."

## P11 — Matter and mass definitions (§5), 2026-09-19

**Matter.** Replace "Matter = persistent relational fixed point of reduction,
protected by topological invariants τ" with: **"Matter = implication trapped in
circulation. It persists because every way out cancels (exit-free modes of a
signed-wave dynamics), not because a topological invariant forbids change."**
The fixed-point language may stay as a description (the circulation is a
fixed point of the dynamics) but not as the mechanism.

Why: under the classical action H no defect or knot persisted (P8–P15).
Knotting constrains *which* intermediates occur, not *whether* decay occurs
(P15). Trapping by cancellation is exact for waves and impossible for
probabilities (P17, P18).

**Mass.** Replace "m ∝ constraint-reconfiguration cost" with: **"inertial mass =
the rewrite cost of translating the structure = its maintenance cost in
implication steps relative to free passage = the energy of its trapped
circulation (in units where the one speed is 1)."** The light-clock argument
supplies the equivalence: every implication moves at the one speed, so
translation borrows steps from internal circulation, and the internal clock
slows by exactly sqrt(1 − v²). The quantitative check is M1/M2 in `DYNAMICS_DESIGN.md`.
