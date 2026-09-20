# Light fronts on the project's mesh (P18)

Status: **DERIVED** statements D1–D7 (written before any simulation), then
**MEASURED** checks (`examples/propagation_test.py`). No change to the
constraintnet dynamics. This asks what *any* nearest-neighbour wave rule on the
project's own mesh would do. It is the check behind clause 3 of
`WORKING_STATEMENT.md` (round, sharp light cones; mass makes a wake).

## Setup

Wave rule on a graph: u_tt = -(L + m^2) u, where L is the weighted graph
Laplacian. On an infinite lattice whose vertex star is the set of displacement
vectors d, with weights w_d (both ±d present), plane waves exp(i(k·x - ωt)) obey

    ω^2 = m^2 + L(k),   L(k) = sum_d w_d (1 - cos k·d)
                             = (1/2) k^T S k - (1/24) sum_d w_d (k·d)^4 + O(k^6),
    S = sum_d w_d d d^T.

## D1: leading-order speed

At long wavelength, ω^2 = m^2 + k^T Ã k with Ã = S/2. A plane wave whose
wavevector points along n moves at sqrt(n^T Ã n).  ∎

*Amendment, recorded after the run:* the speed of a **front** (a ray) along n
is different: 1/sqrt(n^T Ã^(-1) n). Fronts are the ellipsoids x^T Ã^(-1) x = t^2.
The two speeds coincide along the eigen-directions of Ã, which are the only
directions the registered N2 ratio used: (1,1,1) and (1,-1,0). The unregistered
readout along the grid axis (1,0,0) measured 1.60–1.63. That matches the ray
formula, sqrt(8/3) = 1.633, not the plane-wave value 2.

## D2: in grid coordinates the Kuhn mesh has a preferred axis

The Kuhn (Freudenthal) mesh `seeds.kuhn_ball` has 14 neighbours per interior
vertex (read from the code):

- the 6 axis directions ±e_i
- the 6 face diagonals ±(e_i + e_j)
- the 2 body diagonals ±(1,1,1)

With unit weights, Ã = 2I + 2J (J is the all-ones matrix), with eigenvalues
2, 2, 8. So in the rendering grid, waves travel twice as fast along the (1,1,1)
diagonal as perpendicular to it.  ∎

## D3: no nonnegative reweighting fixes it in grid coordinates

Each off-diagonal entry Ã_ij receives only nonnegative contributions: from the
face diagonals ±(e_i+e_j) and from the body diagonal. It vanishes only if all
of those weights are zero, which amounts to deleting the diagonals and leaving
the cubic lattice.  ∎

## D4: but grid coordinates are not physical, and the mesh is secretly BCC

Architecture rule 4 says coordinates are rendering only. The physical metric is
whatever the dynamics defines. At leading order that is g = Ã^(-1), in which
propagation is round by construction.

The nontrivial statement concerns the transformed star, y = Ã^(-1/2) d:

- **8 short vectors along cube diagonals**, all the same length. These are the
  6 axis edges and the 2 body-diagonal edges. Each has a link ring of 6
  tetrahedra.
- **6 long vectors along cube axes**, 2/√3 times longer. These are the face
  diagonals. Each has a link ring of 4.

This is exactly the vertex star of the body-centred-cubic (BCC) tetrahedral
honeycomb, whose cells are tetragonal disphenoids. So in its own emergent metric
the project's mesh has full cubic symmetry. (This matches the classical fact
that the Freudenthal–Kuhn triangulation is affinely the Ã₃ alcove triangulation,
whose vertex lattice A₃* is BCC. That fact is recalled, not re-derived; the star
mapping itself is checked numerically.) The two edge classes are told apart
combinatorially, by ring size 6 or 4, the same quantity that gave H = 6 or 4 in P16.  ∎

## D5: removing fourth-order anisotropy with a ring-size weighting

In the emergent frame (short length 1), give ring-6 edges weight w6 and ring-4
edges weight w4. Cubic symmetry keeps Ã ∝ I. The quartic term is proportional to

    (8 w6/9)(Σ k_i^4 + 6 Σ_{i<j} k_i^2 k_j^2) + (32 w4/9) Σ k_i^4.

It is isotropic (∝ |k|^4 = Σk_i^4 + 2Σ_{i<j} k_i^2 k_j^2) **iff w4 = w6/2**.
Unit weights leave an O(k^4) anisotropy. The 1 : 1/2 weighting removes it,
leaving O(k^6).  ∎

## D6: continuum fronts (standard results)

- **3 space dimensions, massless:** the Green's function δ(t-r)/(4πr) lives
  exactly on the cone. Initial data supported within radius R vanish inside
  r < t - R: the sharp Huygens principle.
- **2 space dimensions:** the Green's function θ(t-r)/(2π sqrt(t^2-r^2)) fills
  the whole cone interior (a tail).
- **3D with mass m:** the Green's function is the sharp term minus
  (m/4π) θ(t-r) J1(m s)/s, with s = sqrt(t^2 - r^2). So mass puts a tail inside
  the cone (a wake).  ∎

## D7 (T3′): real waves trap exactly like the amplitude walk

Take the damped wave u_tt + Γ P_B u_t + L u = 0, with energy
E = ½(|u_t|^2 + u^T L u). Then dE/dt = -Γ Σ_B u_t^2.

- Every eigenvector v of L with v_B = 0 gives an undamped solution v cos(√λ t).
- An undamped solution must keep u_t = 0 on B forever. Expanding in eigenmodes,
  only the dark modes and the zero-energy constant mode can do so.

So the long-time energy is the initial energy in the dark subspace D. Trapping
needs *signed* interference (waves); complex numbers as such are not needed.
Probabilities (P17, T1) never trap. (Sketch-level proof; checked numerically.)  ∎

## Predictions registered with D1–D7 (P18 in `PREDICTIONS.md`)

N1–N6; see the registration.

## Results (measured; full record in PREDICTIONS.md P18 outcome)

| Check | Result |
|---|---|
| N1 star | exact BCC: 8 ring-6 edges → equal cube diagonals; 6 ring-4 edges → axes, ratio 2/√3 |
| N2 grid speeds | ratio (1,1,1)/(1,-1,0) = 1.985 (σ=1.5), 2.005 (σ=3); predicted 2 |
| N3 symbol | anisotropy ∝ k^2.00 (unit weights), ∝ k^4.00 (ring-4 at ½) |
| N4 3D massless | interior fraction ≤ 3e-7 (continuum Gaussian floor ~2.5e-7) |
| N4 2D control | interior fraction 0.018 at σ=6 (continuum 0.0181) |
| N5 mass mσ=1 | interior 0.408 → 0.391 (σ 1.5→3), continuum 0.386 |
| N6 damped wave | kept energy = dark-mode energy to 7e-10 |

Figure: `out/p18_propagation.png`. Data: `reference/opus_session/data/propagation_test.json`.
Tests: `tests/test_propagation.py`.

**Scope.** The rule tested is the ordinary scalar wave equation on the mesh
graph. It has no polarisation or spin and no group labels, and the mesh is
fixed. This settles check D (round, sharp light cones) for scalar waves only.
Checks A (carrying orientation along edges), B (fermion doubling) and C
(unitarity of the relativistic amplitude walk) remain open.
