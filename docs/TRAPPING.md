# Trapping by interference: amplitudes versus probabilities (P17)

Status: **DERIVED** (proofs below), then **MEASURED** (numerical verification,
`examples/trapping_test.py`). No change to the constraintnet model. This is a
mathematical statement about two walks on a fixed graph with a declared exit.

## Why

In the discussion recorded in `BAG_PICTURE.md`, the proposal was that a particle
is a region where an implication wanders forever along an effectively infinite
(ergodic, fractal) route, because every way out cancels. Two questions follow:

1. Can a walk with *probability* weights ever be trapped this way?
2. Can a walk with *amplitude* weights, i.e. the same walk with a phase, be
   trapped, and exactly when?

## Setup

- R: a connected graph with N vertices; L = D - A its Laplacian (real,
  symmetric, positive semidefinite, L·1 = 0).
- B: a nonempty set of exit vertices. P_B: the diagonal projector onto B.
  Gamma > 0: the leak rate.
- **Classical walk:** dp/dt = -(L + Gamma P_B) p, survival S_c(t) = sum_i p_i(t).
- **Amplitude walk:** dpsi/dt = -i K psi with K = L - i Gamma P_B, survival
  S_q(t) = ||psi(t)||^2.

The generator is the same; only the factor i differs. K is the standard
"wide-band" description of a region coupled to an outgoing channel. The
explicit-lead check at the end removes that modelling step for the dark states.

## T1: probabilities always escape

Let M = L + Gamma P_B. For real x,

    x^T M x = sum over edges ij of (x_i - x_j)^2 + Gamma sum over b in B of x_b^2.

This is zero only if x is constant (connectedness) and vanishes on B, i.e. x = 0.
So M is symmetric positive definite with smallest eigenvalue lambda_min > 0, and
||p(t)|| <= exp(-lambda_min t) ||p0||. Since -M has nonnegative off-diagonal
entries, exp(-Mt) is entrywise nonnegative, so p stays a probability vector.
Hence S_c(t) <= sqrt(N) exp(-lambda_min t) -> 0 **from every initial state, on
every connected geometry**, fractal or not. Ergodic wandering finds the exit.  ∎

## T2: leak equals flux through the exit

d||psi||^2/dt = 2 Re<psi, dpsi/dt> = 2 Re(-i<psi, L psi>) - 2 Gamma <psi, P_B psi>
= -2 Gamma sum_B |psi_b|^2, because <psi, L psi> is real. For an eigenpair
Kv = Ev, taking <v, .> gives E||v||^2 = <v, Lv> - i Gamma sum_B |v_b|^2, so

    Im E = -Gamma sum_B |v_b|^2 / ||v||^2.  ∎

## T3: exact long-time survival

Define the dark subspace D = span{ v : Lv = Ev for some E, and v_b = 0 for all b in B }.
Because L is symmetric, D is the largest L-invariant subspace inside ker P_B.

- On D, K acts as L (P_B v = 0), so D is K-invariant and the evolution there is
  unitary: nothing leaks.
- K^† = L + i Gamma P_B also acts as L on D, so D is K^†-invariant. Hence the
  orthogonal complement D^⊥ is K-invariant.
- K restricted to D^⊥ has no real eigenvalue. If K chi = E chi with E real, T2
  forces chi_B = 0, so L chi = E chi and chi lies in D ∩ D^⊥ = {0}. All its
  eigenvalues therefore have Im E < 0, and exp(-iKt) restricted to D^⊥ -> 0
  (even without diagonalisability).

The decomposition psi = P_D psi + P_{D^⊥} psi is orthogonal and preserved, so

    S_q(t) -> ||P_D psi0||^2  exactly.

Averaged over the N single-vertex starts, sum_j ||P_D e_j||^2 = tr P_D = dim D,
so the **average trapped fraction is exactly dim D / N**.  ∎

## T4: degeneracy forces dark states

For each eigenvalue E of L with eigenspace V_E (multiplicity m_E), the dark part
is V_E ∩ ker P_B, of dimension m_E - rank(P_B restricted to V_E) >= m_E - |B|. So

    dim D = sum_E (m_E - rank P_B|V_E)  >=  sum_E max(0, m_E - |B|).  ∎

## T5: symmetry forces dark states

Let S be a group of graph automorphisms (permutation matrices Π with ΠL = LΠ)
fixing every exit vertex. Let F be the S-invariant vectors (dim F = number of
S-orbits on vertices). F^⊥ is L-invariant, because L commutes with the
averaging projector onto F. Each e_b with b in B is S-invariant, so every vector
in F^⊥ vanishes on B. Hence F^⊥ ⊆ D and

    dim D >= N - (number of orbits of S).  ∎

## T6: breaking the symmetry gives decay (perturbative)

Perturb L to L + eps V, with V breaking the protecting symmetry. A formerly dark
eigenvector acquires components of order eps, including on B (at order eps/Gamma
when the dark and bright states share an eigenvalue: they are separated by
order Gamma in Im E). By T2 its decay rate is then of order Gamma·(eps/Gamma)^2 = eps^2/Gamma. This
is standard perturbation theory, not a theorem: generic V is assumed.

## Consequences for the picture

- **Probability weights cannot make a particle** out of a region with any
  reachable exit. That holds on every geometry, including fractal ones (T1).
- **Amplitude weights can** (T3), exactly when the region supports eigenmodes
  that vanish at every exit. Symmetry (T5) and degeneracy (T4) guarantee them.
  They are wake cancellation made exact.
- **Symmetry-protected trapping lasts forever. Accidental or broken trapping
  decays** at a rate ~ eps^2 (T6). This matches the user's distinction:
  a finite "number" decays, an unbroken one does not.
- Fractality is not itself the mechanism. It helps only because self-similar
  graphs have large automorphism groups and highly degenerate spectra.

## Results (measured; details in PREDICTIONS.md P17 outcome)

| Graph (exit = 1 vertex) | N | dim D exact | bound T4 | bound T5 | classical survival at T | amplitude survival at T (mean) |
|---|---:|---:|---:|---:|---:|---:|
| path | 40 | 0 | 0 | 0 | 0 | 0 |
| cycle | 40 | 19 | 19 | 19 | 1e-73 | 0.475 = 19/40 |
| complete K_12 | 12 | 10 | 10 | 10 | 6e-17 | 0.8333 = 10/12 |
| gasket level 3 | 42 | 29 | 24 | 19 | 2e-310 | 0.6905 = 29/42 |
| gasket level 4 | 123 | 98 | 87 | 59 | 0 | 0.7967 = 98/123 |
| gasket level 6 | 1095 | 998 | 954 | 544 | 0 | 0.915 (plus quasi-dark, see below) |
| Kuhn mesh n=3 | 64 | 44 | 20 | 44 | 0 | 0.6875 = 44/64 |

**Checks.**
- **dim D is exact.** It comes from the rank of the exit's Krylov space over
  three primes near 2^26. Modular rank never exceeds rational rank, so each
  prime alone gives a rigorous upper bound on dim D; three-prime agreement gives
  the rational rank. A 400-digit Lanczos run confirms it for gasket levels 1–6.
- **Explicit lead.** Replacing the leak term with a real 6,000-site chain keeps
  a dark state inside to 14 digits.
- **Symmetry breaking.** Integer weights 1000 ± 1 remove every exact dark state (98 -> 0).

**Depth.** For gasket level k the non-dark sector has dimension 3·2^(k-1)+1
(k = 1..6). Its slowest leak rate is:

| Level | Slowest leak rate |
|---:|---:|
| 1 | 5.1e-2 |
| 2 | 4.1e-2 |
| 3 | 5.7e-4 |
| 4 | 6.4e-8 |
| 5 | 8.4e-16 |
| 6 | 1.5e-31 |

That is doubly-exponential collapse. Both are **observed patterns**, not proofs.
Physically, states localised deep inside the self-similar structure must pass
through bottlenecks at every level to leave, and each level multiplies the
suppression. So finite depth gives finite but exploding lifetimes, and the
infinite-depth limit traps everything. That matches the user's "finite number
decays; infinite does not".

**What this does NOT show.** The geometries were supplied. The model has not
been shown to build such structures from its own record (self-confinement).
These are walks with a declared exit, not particles. Dark states on symmetric
graphs are a known phenomenon in quantum-walk and photonics work (dark states,
bound states in the continuum). What is new here is the exact accounting against
the classical control and the depth scaling on the gasket.

Data: `reference/opus_session/data/trapping_test.json`,
`reference/opus_session/data/trapping_depth_rates.json`. Figure:
`out/p17_trapping.png`. Tests: `tests/test_trapping.py`. Scripts:
`examples/trapping_test.py`, `trapping_depth_rates.py` (needs mpmath),
`trapping_graphics.py`.
