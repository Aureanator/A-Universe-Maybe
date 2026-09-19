# v4 dynamics: design (registered 2026-09-19, before implementation)

Status: **design + derived properties + design checks.**

- The design choices below are POSTULATED and registered before any physics
  run. Changing one later requires a dated amendment here.
- Section 4 lists derived properties, each checked numerically in
  `examples/v4_design_checks.py`.
- The physics tests are registered as P19 in `PREDICTIONS.md` and have NOT been run.

The old engine (static labels, curvature action H, external bath, Drivers A/B)
is kept unchanged as the **pre-v4 control arm**.

## 1. What the dynamics must satisfy (from `WORKING_STATEMENT.md`)

| Requirement | Source clause |
|---|---|
| One conserved quantity (implication); no information destroyed | 1 |
| Every tick moves each active implication one hop; nothing is still | 2 |
| Influence spreads isotropically on the light cone (reading 1) | 3 |
| Every route contributes with signed amplitudes; labels give the transport | 4 |
| Vacuum = complete cancellation; residue = charge | 5 |
| **No mass parameter**: mass must appear as trapped circulation | 6 |
| Reversible globally; local regions are open systems | 9 |
| No hidden memory registers; the only record is the configuration | 10 |
| Observables are relational only | 12 |
| Gauge covariance (labels are defined up to vertex gauge) | existing kernel |

## 2. Design decisions (v4.0)

**D-state.** The state is a complex amplitude ψ(v→w) ∈ V_ρ on every directed
edge (arc) of the mesh, plus the edge labels g_vw ∈ G. V_ρ is the space of a
unitary representation ρ of G. The amplitude on arc v→w is implication at v
committed to w.

- **v4.0 representations:** the trivial representation (scalar control) and
  the 3-dimensional irrep of A4, whose matrices are the rotations of the
  tetrahedron: orientation.
- **Spin ½** needs the binary tetrahedral double cover. Lifting the labels to it
  is deferred to check A/B.

**D-coin (all routes).** At each vertex, a weighted reflection mixes the
outgoing arcs, and the same reflection acts on every internal component:

    C_v = 2|φ_v><φ_v| - I,   φ_v = Σ_w sqrt(w_vw / Σ w) |v→w>.

It is chosen for three reasons:
- It is the unique reflection that turns the classical random walk with
  weights w into a unitary walk (Szegedy).
- It treats all routes symmetrically.
- It uses no coordinates.

**Weights:** by link-ring size, 1 for ring-6 edges and ½ for ring-4 edges
(P18 D5: quartic isotropy). The unit-weight version is a control arm.

**D-shift (one hop, transported).** Each arc's amplitude hops to the reversed
arc and is transported by the label: ψ'(w→v) = ρ(g_vw⁻¹) · (C ψ)(v→w). The
labels act as the orientation transport of clause 12: A4 as rotations.

**D-tick.** U = S_ρ · C, applied once per tick; time is the tick count. There
is no randomness and no scheduler.

**D-labels (v4.0: fixed record).** In v4.0 the labels are a prepared, fixed
record: vacuum, or prepared flux structures from P13/P15. v4.0 therefore
cannot test self-confinement (K). What it can test is whether a prepared
record traps implication, which connects the old defects to the new matter
definition. **v4.1 (not designed yet)** will make labels dynamical, with
reversible, gauge-covariant coupling to passing implication; the leading
candidate is a quantum label space C[G] per edge, as in lattice gauge theory.
Deciding v4.1 is gated on the v4.0 results.

**D-mesh.** v4.0 uses the fixed Kuhn mesh (BCC in its own metric, P18). Mesh
evolution via Pachner moves is deferred. Item L (first arrival faceting)
predicts it will eventually be needed.

**D-observables (relational).**
- Source and detector are structures: vertex sets defined combinatorially,
  such as graph balls or supports of prepared flux.
- Reported quantities are detection probability over ticks, arrival delay,
  and relative orientation (the transported internal state).
- The drawing is never an observable.

## 3. Mass: the two definitions that must agree

- **M1 (inertial, translation rewrite cost).** For a structure that can move,
  the eigenphase θ(p) as a function of relational momentum p (the phase
  gradient between detector structures) near its minimum gives
  θ(p)² ≈ m² + c_eff² p².
- **M2 (maintenance cost).** Compare the internal cycling frequency at rest
  with a free implication crossing the same neighbourhood. For the free one,
  θ → 0 as p → 0.

**Light-clock argument (why they should agree):** every implication moves one
hop per tick. A structure translating at speed v spends a fraction of its hops
on translation, so its internal circulation slows by sqrt(1 - v²/c_eff²),
which is time dilation. The relation θ² = m² + p² follows, with the same m in
both readings. This is **DERIVED (sketch)**; it is tested when a movable
trapped structure exists.

## 4. Derived properties of the v4.0 walk (checked: `examples/v4_design_checks.py`)

| Property | Statement | Check (4×4×4 periodic Kuhn lattice) |
|---|---|---|
| Unitarity / conservation of implication | C_v and S_ρ are unitary, so the norm (total implication) is exact | ‖UU†−I‖ = 2e-16 (scalar), 9e-16 (A4 irrep) |
| Gauge covariance | g_vw → λ_v⁻¹ g_vw λ_w with ψ at v → ρ(λ_v⁻¹)ψ leaves the physics invariant (the coin commutes with ρ) | the spectrum is unchanged under a random A4 gauge transform (difference 0) |
| Szegedy spectrum | the eigenvalues are e^{±i arccos λ} for each eigenvalue λ of the classical walk P = w/W, plus ±1 on the complement | max mismatch 5e-15; remainder 768 = arcs − 2V, all ±1 |
| Massless, relativistic dispersion | near k = 0, θ² = 2L(k)/W: **linear** in \|k\| and round in P18's emergent metric, and quartic-isotropic with ring weights | follows from the Szegedy identity plus P18 D5 |
| No doubled light cone | λ(k) = 1 only at k = 0 and λ > −1 everywhere, because the mesh has triangles, so there is no second low-energy point | λ_min = −5/11; max λ away from 0 is 0.965 |
| Flat bands | eigenvalues ±1 with multiplicity arcs − 2V: circulating patterns that do not translate | 12 per vertex |
| Strict causal cone | support grows by one hop per tick, so the strict cone is faceted (item L); whether the amplitude outside the round emergent cone is exponentially small is tested in P19c | — |

**Two features to watch, not hide.**

- **Flat bands.** Most of the arc space (12 of 14 dimensions per vertex) is made
  of eigenvectors at ±1. They circulate around small cycles without translating.
  In the working statement's terms they are trapped circulation with *no*
  inertia at all: they cannot move, so M1 is undefined. They are therefore not
  particle candidates. Their existence and localisation must be characterised
  (P19b), because a trap built on flat-band states would be a lattice artefact,
  not matter.
- **Spin ½ and chirality.** Fermion doubling (Nielsen–Ninomiya) concerns chiral
  spinor walks. The scalar walk has no second massless point, but that says
  nothing about the spin-½ version, which remains open (B).

## 5. Registered first tests

See **P19** in `PREDICTIONS.md`:

- **P19a:** exact identities on small complexes.
- **P19b:** dispersion, isotropy and flat-band characterisation.
- **P19c:** relational light cone, meaning arrival delays between source and
  detector structures.
- **P19d:** holonomy interference with the A4 irrep around prepared flux.
- **P19e:** first physics. Does a prepared flux structure trap implication,
  beyond the vacuum flat bands?

## 6. Not decided here (explicitly open)

- Label dynamics (v4.1, K).
- The spin-½ lift (A, B).
- Mesh evolution (L).
- Born weight (F).
- Gapless photon: v4.0 is gapless by construction (massless linear dispersion).
  Whether that survives dynamical labels is part of v4.1.
