# P32B — Conserving transport diagnostic

Protocol and algebra written before execution, 2026-09-20. This is a
**POSTULATED** extension of the projector model, not a derivation from directed
implication reduction. No new matter degrees of freedom are introduced.

## Algebra checked before implementation

Restrict this diagnostic to Z2. Write S_v=2A_v-I (the nonidentity vertex gauge
transformation), n_v=I-A_v, and W_ab for the nontrivial character string on one
edge. W_ab is Hermitian and unitary, anticommutes with S_a and S_b, and commutes
with other S_v and every B_f. The commuting S_v are involutions.

The projector onto exactly one occupied endpoint is

    P_ab = A_a(1-A_b) + (1-A_a)A_b = (I-S_a S_b)/2.
    T_ab = W_ab P_ab,   K = -kappa sum_edges T_ab,   H = H0 + K.

W_ab commutes with P_ab, so T_ab is Hermitian. It exchanges occupied and empty
endpoints and kills the zero/two-occupied endpoint sectors. Thus [T_ab,n_a+n_b]=0,
[T_ab,n_v]=0 away from the endpoints, and [T_ab,B_f]=0. Consequently [K,N]=0
and [K,H0]=0, where N=sum n_v. This holds throughout the edge Hilbert space,
including curved states. Its support includes the endpoint stars, not only the
single edge. It is local on a bounded-degree complex.

The outward current on oriented edge a->b is J_ab=-i[K_ab,n_a]. Then J_ba=-J_ab
and d<n_v>/dt + sum_w <J_vw> = 0 under H. This is defect-number continuity,
distinct from state-norm conservation. Generic [K,A_v] is NONZERO: local gauge
invariance of H is not retained, although the invariant vacuum is annihilated by
K. This is not a construction of mobile matter under a literal local Gauss law.

Since -P_ab <= T_ab <= P_ab and sum P_ab <= d_max N, for kappa>=0,

    H-E_vac >= (1-kappa d_max) N + sum_f (I-B_f).

This gives a positive charge-cost bound if kappa d_max<1. It does not identify
an inertial mass. N conservation explicitly forbids pair annihilation and
creation; persistence is designed into this diagnostic and cannot prove binding.

## Registered fixtures, controls and measurements

- Full Z2 edge Hilbert spaces of one tetrahedron (64 configurations) and the
  two-tetrahedron bipyramid (512). These are finite simplicial 3-balls, not a
  large-volume or continuum limit. Use all edges/faces, kappa=0.2, hbar=1.
- Prepare every unordered pair (6 and 10 respectively) by a string on a
  shortest graph path acting on the flat vacuum. No coordinate measurements.
- Dense diagonalization evolves each pair at t=0, 0.25, 1, 3, 7. Save vertex
  occupations, edge currents, norm, both H0 and total energy, number variance,
  occupation continuity residual, pair-sector leakage, and pair probabilities
  binned by graph distance. No fitted lifetime or binding claim.
- Controls: H0 alone; and the unprojected K_raw=-kappa sum W_ab. Verify that
  the latter fails to conserve N/H0 and creates a pair amplitude from vacuum,
  whereas K annihilates vacuum. Include an arbitrary complex state (seed 3202)
  for the continuity check, so zero-current initial states cannot pass trivially.
- On the full Hilbert space audit Hermiticity, [K,N], [K,H0], [K,B_f], and
  [K,A_v]. Compare the pair-sector restriction to an independently constructed
  configuration graph that moves one endpoint along an edge into an empty
  vertex, with matrix element -kappa. Test invariance of that sector and its
  orthonormality. Compare matrix-free operators to independently built Pauli
  matrices in tests. Tolerance: 1e-10 for reported algebra/evolution residuals.

**Predictions before execution:** exact conservation identities hold; some local
occupations change by more than 1e-3 during the registered times; K_raw fails
the number-conservation control. The flat pair-sector matrix equals the
hard-core boson configuration graph, with no exchange-sign structure supplied
by this rule. The number of defects stays two by construction. No prediction of
self-binding, fermionic exchange, or the Williamson–van der Mark structure.

**Interpretation gate:** success establishes compatibility of local motion with
these selected conservation laws, not that conservation determines the transport
law. kappa, continuous-time unitary evolution, the Z2 restriction, and selection
of number-preserving matrix elements are additional assumptions. The priority
after this test is to justify an admissible transport/reaction rule from the
reduction model; a stable-configuration search must state that rule first.

## Outcome (appended after execution)

Preregistration commit: `644e49a`. All 16 preparations and 80 registered time
samples completed. Maximum local occupation changes were 0.6848 (tetrahedron)
and 0.7166 (bipyramid). Maximum conservation/evolution readout errors were
4.30e-14 and 1.26e-14; full-matrix eigendecomposition residuals were below
5.65e-13. All registered checks passed at the 1e-10 tolerance.

The flat-pair restriction matches the independent hard-core boson graph to
1.37e-16. The unprojected control fails: ||[K_raw,N]|| is 5.54 and 19.2, and
its action on vacuum has nonzero pair amplitudes. Conversely ||[K,A_v]|| reaches
1.96 and 6.4, confirming that this motion does not retain local gauge symmetry.
These Frobenius norms are finite-patch operator diagnostics, not physical units.

This supplies autonomous moving defects under the declared extension, with a
local number current and explicit energy accounting. It supplies no attraction,
isolated energy-conserving reactions, fermions or electron structure. Pair
separation distributions are archived; neither small patch is a binding test.

Evidence: `examples/p32_transport.py`, `src/constraintnet/defect_transport.py`,
`reference/astra_session/data/p32b_transport.json`. Two new tests compare the
operator with independent Pauli matrices, check a finite-difference continuity
equation, and verify the vacuum/annihilation controls. The seven relevant defect
tests pass. Reproduction must use a fresh filename:

```powershell
.venv/Scripts/python.exe examples/p32_transport.py --output out/p32b_reproduction.json
```
