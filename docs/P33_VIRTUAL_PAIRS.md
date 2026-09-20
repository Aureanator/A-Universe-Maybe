# P33 — Origin of effective hopping and virtual-pair corrections

Registered before execution, 2026-09-20. P32B/C remain unchanged controls.

## Question and assumption ledger

Can P32B's number-preserving hopping be derived as the leading approximation
to a simpler local perturbation, without imposing exact defect-number
conservation? What interaction terms appear at the next order?

Use the existing full Z2 edge Hilbert space and **POSTULATE**

    H(lambda) = H0 + lambda V,   V = -sum_edges W_ab,

where W is the existing one-edge electric string. It is diagonal in the label
basis, not the classical label-multiplication rewrite in moves.py. Neither this
phase action nor H0 or continuous-time quantum evolution follows from the
implication axiom as currently formalized. Classical boundary-appearance
preservation alone specifies no complex amplitudes or exchange phase. Thus this
experiment connects two declared quantum drivers; it does not close that gap.

V commutes with all B_f and changes N by 0 or +/-2. H conserves total energy
and norm but generally not H0 or N. No extra matter variables or exchange minus
sign are introduced. Use finite-dimensional degenerate perturbation theory;
the [Schrieffer–Wolff analysis of Bravyi et al.](https://arxiv.org/abs/1105.0675)
provides a general framework. All formulas below are specialized and checked
algebraically here before the numerical experiment.

## Algebra and predictions before execution

In the flat sector H0=E_vac+N. Let P_m select m defects. Every edge W toggles
the two endpoint occupations. Consequently

    sum_m P_m V P_m = -sum_ab W_ab (I-S_a S_b)/2 = K/kappa.

P32B is exactly the first-order part that stays within a defect-number sector.
At second order in the two-defect sector, in the standard effective basis,

    H_eff,2 = (E_vac+2) I + lambda P_2 V P_2 + lambda^2 C,
    C = P_2 V P_0 V P_2 / 2 - P_2 V P_4 V P_2 / 2.

The relative signs are energy denominators, not particle exchange statistics.
Virtual zero- and four-defect intermediates must both be included. Omitting one
would manufacture a long-range pair-transfer interaction.

For normalized flat pair states |a,b>, the following coefficients are predicted:

1. Ground energy shift at second order: C_vac=-|edges|/2.
2. C_ab,ab = (degree(a)+degree(b)-|edges|)/2. After subtracting C_vac,
   this is the sum of two single-vertex costs; **no diagonal pair potential
   remains at this order in this effective basis**.
3. If |a,b> and |c,b> differ at a,c, their C entry is
   sum over common neighbors v of a,c of (1[v=b]-1/2). This is hopping whose
   coefficient depends on the other defect's location; it can be a two-body
   effect despite the absent diagonal potential.
4. C vanishes between disjoint initial/final pairs: the vacuum and four-defect
   contributions cancel. Both contributions separately need not vanish.

These are local algebraic statements. An absence of diagonal attraction is
not an exclusion of binding via off-diagonal terms or at higher orders.

## Registered numerical protocol

- Same Z2 tetrahedron and two-tetrahedron bipyramid as P32B: full dimensions
  64 and 512. No frozen edges; all faces included. Work in the exact invariant
  flat sector, with full-edge operators used to verify that restriction.
- Enumerate every even vertex-occupation subset. Prepare its edge state by
  pairing its sorted endpoints with graph paths and applying the existing
  strings to the flat vacuum. Verify orthonormality and completeness against
  the directly enumerated flat label configurations, not just a particle graph.
- Independently compare the full-edge action to the even-parity restriction of
  H_dual=E_vac+sum_v n_v-lambda sum_ab X_a X_b. This dual representation is
  a computational equivalence in the tested flat balls, not fundamental spins.
- Check the first-order block equality and all four second-order predictions
  above at tolerance 1e-10; retain the separate P0 and P4 terms in saved data.
- At lambda=0.01, 0.02, 0.04, 0.08, diagonalize H restricted directly to flat
  label configurations. Identify the two-defect band by |E-E_vac-2|<1.
  Since lambda*|edges|<1, the operator-norm bound separates unperturbed number
  bands throughout this sweep. Record every band eigenvalue, first- and
  second-order errors, errors/lambda^2 and errors/lambda^3, and observed error
  ratios as lambda halves. Prediction: second order improves the spectrum at
  the smallest lambda, with asymptotic O(lambda^3) error or smaller; do not
  demand a nonzero cubic coefficient or silently fit another interval.
- Record ground energy, vacuum overlap, <N> and Var(N) for every lambda.
  For every initial bare pair, evolve exactly at t=0,0.25,1,3,7 and save norm,
  total energy, H0, <N>, Var(N), and probability in each number sector.
  Predict nonzero departures from the bare two-defect sector (>1e-8 in at
  least one registered sample), while norm/total energy/flatness are conserved
  to 1e-10. A dressed ground state is stationary, not a movie of vacuum churn.

## Interpretation gate

Success removes exact number conservation as a required fundamental postulate
for the *leading* hopping approximation. It does not derive the perturbation
from reduction, produce fermions, or establish binding/nuclear reactions.
Any later binding test must use a separation/size analysis and a two-particle
threshold, not a low eigenvalue or an apparent finite-box attraction alone.
