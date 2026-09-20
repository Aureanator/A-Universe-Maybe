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

## 7. Results of P19 (2026-09-19)

Full record: the P19 outcome in `PREDICTIONS.md`.

- **Walk properties:**
  - identities exact (a)
  - dispersion exactly Szegedy, with long-wave speed sqrt(2/11) and quartic
    isotropy under ring weights (b)
  - relational light cone round to 0.3%, with exponentially small weight
    outside it (c)
  - non-abelian holonomy interference matches ½(1 + χ₃/3) exactly (d)
- **No superluminal modes:** the maximum group speed over the zone equals the
  long-wave speed.
- **DF:** compact cycle states exist whenever the holonomy fixes a vector. They
  make up the large, non-translating trapped sector of every open region.
- **P19e (negative):** a frozen flux record traps nothing beyond those vacuum
  cycle states, and flux slightly *reduces* them.

**Decision gate reached:** v4.1 (dynamical labels) is required for
self-confinement. Its design is the next registered step and is not started here.

## 8. v4.1-sc: the record responds (registered 2026-09-19, before implementation)

**Source: the user's answers.**
- *Free light* reads whatever chop it meets, link by link.
- *Contained light* is a pivoting wave: one side of the wave turns about the
  other, at loci the geometry dictates, in steps. Pinning in all six degrees
  of freedom was withdrawn as too strong: the pivot must be able to move with
  the structure.

**Geometry fact (checked).** In the emergent metric every interior edge has a
single dihedral angle:
- **60°** on ring-6 edges;
- **90°** on ring-4 edges.

So pivoting about an edge is intrinsically stepwise, in 6 or 4 steps per turn.

**Rule (a POSTULATED hypothesis, semi-classical: labels stay classical A4 elements).**

Each tick first runs the v4.0 walk step ψ ← U(g)ψ, then a label step. For every
interior edge e = (a,b) whose link ring c_1 … c_k (cyclically ordered by the
oriented tetrahedra around a→b) consists of interior vertices:

- **Spatial circulation (pivoting around e):**
  K_e = Σ_i (|ψ(c_i→c_{i+1})|² − |ψ(c_{i+1}→c_i)|²).
  It uses only norms, so it is gauge-invariant, and reversing the edge flips its sign.
- **Internal spin at each end:**
  S_v = Σ over arcs out of v of Im(ψ̄ × ψ), a real 3-vector. Under ρ it
  transforms as a rotation vector.
- **Quantised chop:**
  Q(y) is the order-3 element of A4, a +120° rotation, whose rotation axis
  best aligns with y. Q is equivariant under A4 and Q(−y) = Q(y)⁻¹.
- **Update, if |K_e| ≥ κ:** g_ab ← s_a · g_ab · s_b, with
  s_v = Q(sign(K_e) · S_v). Otherwise g_ab is unchanged.

**Why this form.**
- *Gauge-covariant:* s_a is based at a and s_b at b.
- *Consistent under edge reversal:* the update of g_ba is the inverse.
- *Writes chop even from vacuum:* s² ≠ e.
- *Free light writes nothing:* a straight-moving wave has no net circulation
  around any edge, so it only reads.
- *Stepwise:* the chop is always a 120° rotation.

**Reversibility.**
- The label step depends only on ψ after the walk, never on labels, so it is
  inverted from (ψ_{t+1}, g_{t+1}).
- The walk step is then inverted with the recovered g_t.
- Exact reversal is a registered engine check.

**Accounting caveat. RETIRED on this ground (2026-09-19, user objection accepted).**
The norm is conserved, but chop costs the wave nothing. Because the walk
operator changes with the record, the wave's quasi-energy is not conserved.
A record must carry, and cost, implication. See §9.

**Parameters.**
- κ ∈ {0.5, 0.2, 0.05} × max_e |K_e| at t = 0, all three runs reported.
- No other free parameter; ring weights as in v4.0.

## 9. Energy-accounted record: options (for decision; nothing registered yet)

**Requirement:** writing a record costs implication, and unwriting it returns
the implication. One conserved total is required.

- **(A) Quantum record (lattice gauge theory).**
  - *How:* labels become quantum, a superposition of group elements on each
    edge. Wave and record evolve by one fixed unitary.
  - *Energy:* a conserved quasi-energy exists automatically, and every chop
    trades energy between the wave and the record. This is how
    electromagnetism stores energy in fields.
  - *Pros:* principled.
  - *Cons:* the state space grows exponentially with the number of dynamical
    edges, so it is testable only on small regions.
- **(B) Explicit ledger: curvature is stored implication.**
  - *How:* each curved face holds a fixed quantum ε of implication, so
    ‖ψ‖² + ε·H is conserved exactly. A chop that creates curvature must draw
    ε from the local wave; one that removes curvature returns it. Chops the
    local wave cannot pay for do not happen. The rule can be made reversible
    by construction.
  - *Pros:* answers the earlier mapping question ("is a curved face a trapped
    implication?") with yes, and reconnects the old curvature count H as real
    stored energy. Closest to the current engine.
  - *Cons:* adds one constant, ε.
- **(C) No separate record.**
  - *How:* the chop is itself implication circulating around small loops (the
    DF cycle states of P19). The only field is ψ, with a local norm- and
    energy-preserving self-interaction.
  - *Pros:* "one quantity" taken literally; nonlinear walks are known to
    carry self-trapped solitons.
  - *Cons:* the group labels become a fixed background, and charge would have
    to be re-derived.

## 10. Option A at small scale: a quantum record (registered 2026-09-19 as P21)

**Why A first.** The user sees merit in A: in a sea of chop, a structure can reshape the
landscape by redistributing what is already sloshing (the buoy picture) without new energy.
A single fixed unitary over walker *and* record conserves quasi-energy automatically, so the
objection that retired v4.1-sc cannot arise. The conversation also noted that B, run reversibly,
turns into A (a ledger that must give energy back exactly has to keep a phase, i.e. become a
field), so A is the principled form of both.

**What is implemented** (`src/constraintnet/qrecord.py`, `QuantumRecordWalk`).
- **Record:** k = 3 edges carry quantum labels, basis |g₁g₂g₃⟩, 1728 states. All other
  edges are frozen at the identity. It is a *partial* quantum record, chosen for size: a full
  one needs 12^E states.
- **Tick:** U = U_rec · U_walk.
  - U_walk is the v4.0 walk controlled on the record basis.
  - U_rec = e^{−iλ_B W/2} (⊗ e^{−iλ_E L/8}) e^{−iλ_B W/2}.
- **Record terms:**
  - **Electric term L:** the Laplacian on A4 generated by the 8 order-3 elements. It is a class
    union, so it commutes with gauge moves at both ends of the edge. After the /8 its costs are
    0, 1 and 3/2 for the trivial, 3 and 1′/1″ irreps.
  - **Magnetic term W:** the Wilson cost Σ (1 − χ₃(hol)/3) over faces touching a quantum edge:
    1 per order-3 holonomy, 4/3 per order-2 holonomy. This is the geometric form of option B's
    ε, argued in conversation (the hopping expansion gives Tr ρ(hol)).
  - This is the Kogut–Susskind structure (the standard Hamiltonian form of lattice gauge
    theory), in discrete time, with A4 as the gauge group.
- **Box:** a closed Kuhn ball n = 6. The walk is on the induced interior subgraph, so every arc
  has its reverse and nothing is lost: the walls echo losslessly.
- **Vacuum:** the eigenvector of U_rec nearest to |e,e,e⟩. It is not |e,e,e⟩ itself: the vacuum
  is a sea of virtual chop, which is exactly the user's "sea of chop".
- **Checked** (`tests/test_qrecord.py`):
  - unitarity and exact reversal;
  - vacuum stationarity;
  - λ_E = 0 reproduces v4.0 bit for bit;
  - the label/transport convention matches `ArcWalk`.

**Results (P21, 2026-09-19; details in PREDICTIONS P21 outcome).**
1. **Accounting holds.** Norm, reversibility and vacuum stationarity are all exact to about
   1e-13. The chop now costs what it holds: when the record takes energy, the light loses
   fidelity by a matching amount.
2. **The free photon and the sea of chop.** In a weakly fluctuating vacuum (overlap with flat
   ≥ 0.99), light echoing for 600 ticks through a quantum triangle stays ≥ 98.5 % identical to
   flat-vacuum light. It deposits energy ∝ λ_E², and the amount levels off. In a strongly
   fluctuating vacuum the light heats the record steadily, which is the Floquet concern made
   visible. *Constraint on A:* the vacuum must fluctuate weakly for light to stay coherent.
3. **Trapped loops talk to the record; free structures barely do.**
   - The DF loop is disturbed far more by the *dynamic* record than by quenched chop drawn from
     the same vacuum, so this is response, not noise.
   - At moderate coupling the loop keeps 82–99 % of its weight on its 8 arcs. Its internal state
     beats slowly against the record, with a revival to 0.84 within 600 ticks.
   - At strong coupling it partly dissolves.
4. **No binding.** The pivot vortex is unaffected (±3 %). With 3 quantum edges this was the
   expected outcome.
5. **Limitations.** A partial record (3 quantum edges, the rest frozen); a small box (n = 6);
   E_rec is a proxy readout.
   - *Next scale-up:* make every edge of one loop quantum. The 4 square edges give
     12⁴ = 20736 basis states, feasible at n = 5. Then look for *dressed* loop states:
     eigenvectors of the joint U localised on loop + record.

## 11. Freeze-out test (P22, 2026-09-20)

**Setup.** The user's idea: the early vacuum was not calm, and formation followed cooling. The
test is P21 with open walls (`QuantumRecordWalk(mode="open")`). The record starts hot (a typical
excited state mixed with the vacuum at weight sin²θ), and a flash of ordinary light is released at
the quantum loop. The record state of the escaped light is bookkept.

**Results.**
- A hot, dynamic record is **opaque**. It releases light slowly, roughly as a power law.
  - Frozen hot chop releases light exponentially; the flat vacuum releases it exponentially and
    fast.
  - Retained light ∝ hot fraction, with no threshold.
- **No cooling:** the hot record holds about 10× more energy than the light can carry, so the
  light cannot calm it. The flash even heats a calm vacuum slightly.
- **What this does and doesn't show:** it reproduces "opaque when hot, transparent when calm"
  (decoupling). It does *not* yet show formation on calming.

**What is missing:** a cooling channel that dominates the energy budget. That means either a
radiation-dominated start (much more light than record energy) or growth or expansion of the mesh.
The second is a new axiom-level question and is logged as open.

## 12. Radiative cooling and redshift (P23, P24a; 2026-09-20)

1. **Folding.** With λ_B·W ≫ π (P21/P22 used λ_B = 2, so one flip costs 12 rad per tick), the record's
   quasi-energy is folded. "Energy" has no order, and light drives the record to infinite
   temperature. Thermodynamic questions need the *unfolded* regime, where the whole record
   spectrum spans less than π; (0.1, 0.1) qualifies.
2. **Broad light is an infinite-temperature bath.** Even unfolded, a broad flash holds the record
   near the hot state.
3. **Narrow, low light has a temperature.** Light from one band at phase ω₀ holds the record at an
   E* that falls steeply with ω₀: 0.51, 0.22 and 0.14 × E_hot at ω₀ = 0.52, 0.40 and 0.33.
   Excitations whose gap exceeds ω₀ freeze out.
4. **Transparency.** A record at lower energy holds less light (P23-5): cooling and decoupling go
   together.
5. **Why expansion is needed.** A finite box cannot hold light below its lowest mode, and in our
   box that mode (0.52 at n = 5) is above the record's gaps. Redshift, i.e. more hops between
   structures, is what lowers ω₀.

**Next, expansion dynamics (P24b), needs a rule.** Open, axiom-level: where do new vertices come
from? Candidates are set out in conversation (2026-09-20).

## 13. Seeded patterns in a compatible cooled bath (P25, 2026-09-20)

**The user's principle.** "With enough noise this happened somewhere." A pattern is seeded
*compatibly*: never imprinted on a bath that is fundamentally incompatible with its existence.
Persistence is a separate question, and it is what the test measures.

**Implementation.**
- Each record branch c carries its own compatible version of the pattern, DF_c. It is built from
  that branch's transports, with the internal vector fixed by that branch's loop holonomy.
- Every A4 holonomy fixes a vector, so no branch is excluded.
- The bath is a Gibbs sample of the record at the freeze-out energy (P24a, n = 7).

**Findings.**
1. **Compatible seeding has no birth shock.** Imprinting a flat-vacuum pattern costs about 4.5 % at
   once.
2. **With the bath frozen,** a compatible pattern is exactly permanent.
3. **With the bath moving** (λ = 0.1), every seeding erodes at about 2–3e-4 per tick, the calm
   vacuum included, at about 1e-4.
4. **Loop geometry:** 90° loops outlast 60° loops.

**Next: dressed loops.** Look for joint eigenstates of U restricted to loop plus record. Extract the
stationary part of a compatible seed by time-averaging in a closed box: the component with
eigenvalue near 1. If a large component exists, a persistent pattern exists, and its record
statistics *are* the back-calculated bath.

## 14. Dressed-state search: phase and claim controls (P26, 2026-09-20, Astra)

**Amendment to the proposed search in section 13 (earlier wording preserved).**
A stationary quantum ray satisfies U psi = exp(i theta) psi. Its phase need not
be zero; plain time-averaging can erase an exactly persistent ray. P26 therefore
uses two preregistered phases: zero and the isolated record-vacuum eigenphase.
The latter is a choice of rotating frame, not a phase fitted after the run.

For F_T(theta) = (1/T) sum_{t=0}^{T-1} exp(-i theta t) U^t psi, the exact identity
is (U-z)F_T = z (z^(-T) U^T psi - psi)/T, where z = exp(i theta). Thus a small
unnormalized residual is guaranteed as T grows; the normalized bound includes
1/||F_T||. Report the discarded weight and check the full U, never merely its
compression to the chosen loop. The implementation and exact-spectrum tests are
`phase_filter.py` and `test_phase_filter.py`.

A closed finite box has eigenstates whether or not it confines anything. P26
therefore measures loop weight, topological distance from the loop, boundary-size
dependence and subsequent open-wall escape. The frozen-loop and decoupled flat-walk
controls are exactly persistent kinematic modes already present in this model.
Improvement over a noisy seed alone does not establish binding caused by a
responsive record. Also, a persistent localized superposition can beat within a
localized invariant subspace; searching for one eigenray is a sufficient strategy,
not the only possible form of persistence.

**Bath provenance remains a separate gate.** An exact joint eigenray has a
stationary reduced record under the *coupled* step. This does not make that record
a fixed point of P23's distinct incoming-light and escape channel. For a normalized
unitary one-tick residual r, the trace-norm change of any reduced state is bounded
by 2r (pure-state distance followed by partial-trace contraction). P26 reports the
record's configuration probabilities and their one-tick change as accessible
readouts; those diagonal statistics alone do not characterize the reduced state.

The search remains on three prescribed quantum edges with the rest frozen flat.
No mobile particle, electron orientation cycle, spin/exchange result, or
radiatively established bath follows from passing this diagnostic.
