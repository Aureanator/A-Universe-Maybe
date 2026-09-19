# Pre-registration log

Discipline (referee item 15): every experiment below was **written down before it was run**.
Predictions carry the date and mental state of their writing. Outcomes are appended verbatim
after the run, never edited into the predictions. If we are wrong, the wrongness stays visible.

This file is the epistemic shield for the critique-response work (`docs/CRITIQUE_TRIAGE.md`).

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
