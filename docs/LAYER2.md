# LAYER-2 NOTES — category, knots, measurement (brief from Qwen cloud + Opus review)

Branch tip work after `6e2bdbd`. Items numbered per the Layer-2 brief. Status as of
each commit; tests are authoritative.

## Item 1 — D(A4) modular data: COMPLETE (`category.py`, `tests/test_category.py`)

Fourteen sectors ([flux class], centralizer irrep), canonical order
`[id, 3−, 3+, 2] × irreps`: pure charges (1, 1′, 1″, 3; θ=1 — the 3 is a non-abelian
boson), six order-3 dyons (θ ∈ {1, ω, ω²} per class), four V4 dyons (two with θ = −1).

All brief pass criteria green: S unitary + symmetric; vacuum row d_a/|G|; S² = charge
conjugation (involution); **(ST)³ = (τ/D)S² with τ/D = 1 exactly** (untwisted D(G) has
c ≡ 0 mod 8 — verified, not assumed); Σd² = 144; Verlinde nonneg integers; quantum-dim
homomorphism d_a·d_b = ΣN·d_c; vacuum appears exactly once in every a×ā.

Sub-rules: pure charges fuse as Rep(A₄) (cross-checked against `reps.py` decompose);
**shift rule 1′ × F₁ = F₂ exact**; twisted action for ρ=3 on a Z₃-flux sector matches
the explicit restriction Res 3|⟨c₁⟩ = χ₀+χ₁+χ₂.

Class algebra (flux level), class order [id, 3−, 3+, 2], structure constants K[i][j]:
- C₂² = (3,0,0,2) — the quoted **3C₁ + 2C₂**, exact
- C₃·C₄ = (4,0,0,4) — the quoted **4C₁ + 4C₂**, exact; no flux term survives
- C₃² = (0,0,4,0): squares land in the *opposite chirality class only* — cleaner than
  the quoted "⊂ C₄" (there is no identity term because a 3-cycle's inverse never lies
  in its own class)

### The convention discovery (worth more than the table itself)

The S-matrix sum has two conjugation-direction conventions. They are **indistinguishable
by every "obvious" check** — both give unitary symmetric matrices with correct vacuum row,
and they produce *identical fusion coefficients* — yet only the asymmetric form

    S_{(C,A),(D,B)} ∝ Σ_x χ̄_A(x b x⁻¹) · χ̄_B(x⁻¹ a x)   [first factor by x, second by x⁻¹]

satisfies (ST)³ = (τ/D)S². The symmetric variant fails with error O(1). Two "universes"
with the same fusion and different chirality, separated by exactly one identity — the
brief's formula was right, and we now know *why* it had to be: unitarity sees the
representation ring; (ST)³ sees the ribbon structure. Guarded by
`test_st3_identity_referees_convention`.

Normalization note: the prefactor is |C_A||C_B|/|G|², pinned by a hand-built toric-code
Z₂ control (`test_toric_code_Z2_control_pins_normalization`). The (1/|G|) form quoted in
older notes gives vacuum row dim(π) instead of d_a/D and fails the control.

### What twist is NOT

θ = −1 on W2/W3 is a ribbon TWIST, not exchange statistics. The R-symbol check in the
W₂×W₂ → vacuum channel (does R = −1 there?) needs F/R data — next task below. Until then:
"fermionic twist candidates", never "fermions".

## Item 2 — excitation geometry / dimensional audit: DETECTOR v1 LANDED (`strings.py`)

Dual-skeleton clustering of curved faces with loop-vs-sheet classification (loop = every
touched tet carries exactly two component faces; pure classifier unit-tested against
synthetic cycle/branch/endpoint structures). GF(3) solvability engine decides realizability
of any prescribed curvature pattern by rank over Z₃, with tests:
**isolated single-face flux has no preimage under d** (Bianchi re-derived as linear algebra),
every exact pattern is solvable, and the realizable single-tet alternating bubble detects as
sheet/junction — a "charge" made of one face cannot exist, smallest supports are closed.
Remaining: dimensional-audit test on detected candidates (needs A₄ loop configurations),
knot/link invariants via barycentric PL embedding (recipe below), interferometry, braiding.

## Item 5 — entropy measurements landed (`entropy.py`)

Region-generalized |I(∂R)| with cone conventions reproduced exactly (spot-checks: vacuum
12→1, uniform V₄ flux 72→6). First data (Z₃ Kuhn n=2, nested balls r=1,2,3):
**S_flat ≡ 0 at every radius** — vacuum hidden-resolution entropy is exactly zero (flat
fillings rel boundary unique); **S_free = E_int·log 3 = 0, 2.197, 7.690** vs |∂R| = 12, 24, 34
— volume-like, not area-linear. Consequence for the Jacobson route: entropy is entirely
defect-carried; horizon entropy must come from defect resolution degeneracy. The defect
ensemble awaits seeded flux loops (strings.py constructions) — honest dependency, recorded.

**Follow-up (this session): CORE ENTROPY MEASURED — prediction confirmed.** E027 sharpened
the question to core-containing regions; the slice solver (`enumerate_region_resolutions_slice`,
E029: MRV backtracking with conjugacy-class propagation, exact vs brute force on cone controls
+ 24 random regions) makes Kuhn n=2 A₄ cores tractable (12¹⁴ → ~0.1 s). Measurement (E030,
`examples/core_entropy.py`, `tests/test_core_entropy.py`): order-3 core star(13) raw |Sol| = 48
→ **|I| = 4**; field balls rigid |I| = 1; full ball (E_int 26) identical — entropy localizes at
the core; involution control raw = |G| pure gauge; Z₃ twin |I| = 1. State structure: one
geometry-fixed support (7 of 14 star edges), filled by exactly one conjugacy class's four
elements — hidden state space ≅ flux class for this geometry (cone V₄ case gave 6 ≠ |class|;
relation open).

---
Original brief specs follow (kept for the pass criteria; status is recorded above them).

## Item 2 spec — excitation geometry / dimensional audit

The audit statement (to encode as a test when the detector lands): in 3+1D untwisted
D(G), point excitations are pure charges only, and those are all bosonic; every flux-
carrying sector is a LOOP excitation (magnetic flux in 3+1D is a string). θ=ω sectors
(spin 1/3) are forbidden as points by SO(3) quantization but fine on loops; the θ=−1
dyons are fermionic *loops* in bulk (point fermions only on a 2+1D boundary, or with a
twisted cocycle / spin structure — H³(A₄,U(1)) menu check pending).

Detector spec: find closed loops of curved faces in the dual 1-skeleton (nodes = tets,
dual edges = shared primal faces; flux string = cycle through curved faces). Per candidate:
flux class, charge irrep, loop length, twist, statistics prediction, point-vs-loop flag.
Pass: every candidate carries a consistent (dimension, twist) pair under the audit.

## Item 3 — knot observables: SPECCED, not started

Knot type of a flux string is a PL invariant of the pair (loop in triangulated ball);
we use the barycentric PL embedding of the Kuhn ball as representative (documented choice
— coordinates enter *invariants of the combinatorics*, never dynamics). Plan: Gauss code
from segment crossings, Reidemeister I/II reduction, crossing number + Alexander at
t = −1. Measurements: (a) probe charge loop linked with flux string → AB phase χ_π(g)
(in-sim sector identification by interferometry); (b) loop-through-spanning-surface
braiding vs category R-eigenvalue. Hypothesis to log, not tune: m ∝ crossing number at
fixed flux class.

## Item 5 spec — entropy S(R) = log|I(∂R)|

Generalizing the cone machinery: for region R with fixed boundary data B, Ext(B) = interior
assignments flat on all non-boundary faces, quotiented by vertex gauges trivial on ∂R.
For abelian G this is linear algebra over Z_p — exact counts via Gaussian elimination at
any region size (A₄ brute force only for spot-checks). Ensembles: defect-confined curvature
(bulk flat) vs free curvature; compare growth of S against |∂R| and |R|. Vacuum control is
itself a measurement: flat B on a 3-ball gives S = topological (h¹(R,∂R)), not area-extensive.

## Item 7 — memo patches: DONE (`docs/MEMO_PATCHES.md`)

Ten concrete patches P1–P10: D(A₄) naming, novelty scoping, §4 reorder (knot anchor first),
F(O)≅O provisional flag, Born demotion (measure-postulated), analog-gravity/Jacobson credit
with our entropy measurement inserted, the 82/20-sort/13/11 signature correction,
achievements pruning, the cite-forever audit paragraph, gapless-photon as open problem 1.
Memo.txt itself preserved unmodified as history; patches applied-to-text live in the doc.

## Items 4, 6 — queued (end-of-session state)

Pair-state constructor for envariance (small, next up); move-set reachability harness
(numbers measured in earlier sessions — codify as assertions: 27 / 1728 / 64+4sig).
Suite at session end: **197 tests green** on `bionic/kernel-drivers`.
