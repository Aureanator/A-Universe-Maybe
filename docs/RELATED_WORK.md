# Related work — positioning constraintnet against the literature

Written per referee audit item 17. The honest one-line position: **constraintnet is a
Dijkgraaf–Witten / lattice-gauge-shaped toy of a relational metaphysics, with causal-set
overtones in its observer layer and Regge-like discreteness in its geometry claims — none of
which it has yet earned as derived results.** Below: module-by-module mapping and the theorems
our claims must not contradict.

## 1. Module → literature map

| Module | Closest established framework | Relationship |
| --- | --- | --- |
| `groups.py`, edge labels, holonomy | Wilson lattice gauge theory (Wilson 1974); Kogut-Susskind | Standard LGT variables on a simplicial complex; nothing claimed novel here. Novelty claim is only the *dynamics* (boundary-preserving rewrites), not the kinematics. |
| `category.py`, `doubles.py` (D(A₄) anyons, S/T/Verlinde, monodromy = θ-ratio) | Dijkgraaf–Witten TQFT (1989); Drinfeld double / quantum double of a finite group (Kitaev 2003 toric code generalization: Müger/Graña et al.); Kitaev's exactly soluble models | Our spectrum computations reproduce known D(G) structure — deliberately. The novel claim is *interpretive*: sectors as internal-resolution spaces of boundary-preserving dynamics, and θ as self-entailment (self-Aharonov–Bohm). The category math itself is not new and we say so. |
| `resolutions.py`, `entropy.py` (|I(B)|, S(R)=log\|I(∂R)\|) | Gauge-fixing moduli spaces in LGT; entanglement/edge-mode entropy literature; Jacobson's thermodynamic gravity (1995); Van Raamsdonk / Ryu-Takayanagi popular lineage | The area-law test on log\|I(∂R)\| is an honest analog experiment, not a derivation of Einstein equations. Clausius step remains open and is declared so. |
| `observer.py` (event density → effective geometry, propagation delay) | Causal sets (Sorkin): order + number = geometry; Myrheim–Meyer early proposals; Unruh's dumb holes / analog gravity (1981); Barceló–Liberati–Visser (2001+) | Our "spacetime is the event mesh, density is geometry" thesis is closest to causal-set numerology minus the Lorentz-invariance machinery. The referee correctly notes a scalar density gives at most a conformal factor; analog-gravity refractive index is the honest precedent for the delay layer. Post-P6 status: no measured matter-density coupling under Driver A — claim withdrawn to "awaiting dynamic delay" (backlog item 4). |
| `spectral.py` (d_s via diffusion) | Spectral dimension of causal dynamical triangulations (Ambjørn–Jurkiewicz–Loll), quantum-graph literature, Lausannnois et al. on discrete Laplacians | Standard estimator; our matched-control finding (finite-size dominance at small meshes) echoes known CDT short-time d_s running. |
| `moves.py` Pachner moves | Pachner's theorem (1991): bistellar moves connect triangulations of PL manifolds; dynamical triangulations (Ambjørn et al.) | We use Pachner moves as internal-resolution moves with labels — combinatorics standard; label-preserving-boundary dynamics is our addition. |
| `knots.py`, `linking.py` (PL knot/link observables of flux loops) | Classical oriented-link theory; knot states in gauge theory / loop quantum gravity; anyon knot statistics literature | P13 repairs linking with exact rational signed crossings and enables the Hopf regression. This standard invariant is not novel. Prepared mesh links have replayable merger/erasure witnesses; general single-knot classification and categorical braiding correspondence remain open. See `TOPOLOGY_AUDIT.md`. |
| `fringe.py` (two-path visibility by counting) | Sorkin's co-productive class / decoherence-histories program; discrete quantum mechanics on graphs | Our "no amplitudes, count histories" is closest to Sorkin's quantum mechanics-as-counting programme — genuine kinship, acknowledged. |
| Axioms (directed implications reduce; time = causal order) | Process philosophy (Whitehead); causal set theory (order fundamental); 't Hooft's cellular automorphism interpretation; Wolfram physics project (with the credibility caveats it has earned) | Interpretive layer only. The math is neutral between these readings; we cite them as ancestry, not endorsement of their stronger claims. |

## 2. Do-not-contradict checklist

Claims in this repo must respect, or explicitly confront:

1. **Elitzur's gauge invariance theorem (1975):** local gauge symmetry cannot break spontaneously;
   any "order parameter" built from non-gauge-invariant data is meaningless. Our conservation and
   detection primitives are conjugacy-class/ canonical-form based — consistent by construction, but
   no claim may be phrased in terms of raw-label order parameters.
2. **Elban–Gowda (1984):** naive lattice discretizations of non-abelian constraints acquire
   spurious solutions; coarse-graining constraint algebras is delicate. Our boundary-class
   preservation is exact at the micro-level, so this bites only when continuum claims are made —
   none currently are.
3. **Fermion doubling (Nielsen–Ninomiya 1981):** no naive lattice fermions. Our "fermions" are
   D(A₄) dyons with θ = −1 (twist), NOT lattice fermion doublers; the dimensional audit (flux = loops
   in 3+1D, point-fermion verdict requires spin structure / H³ twist) already confronts this. Keep it that way.
4. **No-signalling:** any "measurement by dual coupling" language must not enable superluminal
   transfer; our measurement layer is classical counting over resolutions — verify no claim smuggles
   signalling when Born postulate is applied.
5. **Coleman–Mandula & its loopholes:** combining spacetime and internal symmetries is constrained;
   our e(3)-from-∂Δ⁴ story is a kinematic observation about automorphism groups, not an S-matrix
   symmetry claim — keep the language honest.
6. **Lorentz invariance of causal sets:** event-density-based geometry without a sprinkling
   mechanism will be read as breaking Lorentz invariance; if gravity claims ever return, address
   why a graph-based density need not pick a frame (or admit it picks one — lattice artifact).

## 3. What we owe the literature (honest gaps)

- Continuum limit: none constructed. LGT's continuum story (renormalization group, asymptotic
  freedom) has no counterpart here; "emergent smooth geometry" is aspirational at our mesh sizes.
- Unitarity of any proposed quantum dynamics from counting: unproven beyond the fringe test.
- Born rule: sample space derived (fusion channels), measure POSTULATED — declared open problem,
  consistent with the mainstream view that no derivation exists.
- Gravity: currently zero empirical content under Driver A (P6 finding); the program's gravity
  section stands or falls with dynamic delay (backlog item 4) and an entropy functional with teeth.

## 4. What may be genuinely ours (modest claims only)

1. Boundary-preserving rewrite dynamics as a *definition* of legitimate reduction, with fate
   trichotomy logging — a concrete, testable alternative to Hamiltonian evolution on fixed graphs.
2. Internal-resolution spaces I(B) (rigid vs pooled conventions now explicitly separated and both
   computed) as a hidden-state bookkeeping device with exact counts on finite seeds.
3. The P6 negative result: in appearance-only-conserved stochastic dynamics, event density is
   label-blind — a clean no-go-flavored observation for event-geometry programs (density ≠ matter
   unless the driver's acceptance couples to curvature).
4. Matched-control spectral consistency as the honest replacement for "d_s returns 3" at toy scale.


## Literature check of the P19–P31 work (2026-09-20, Opus; searched, not from memory)

Done at the user's request, to separate what is ours from what is standard. Verdicts are about
*priority*, not about whether the results are correct or useful here.

### Already established — we re-derived it

1. **Gauge-covariant coined quantum walks.** Arnault, Di Molfetta, Brachet and Debbasch,
   *Quantum walks and non-Abelian discrete gauge theory*, Phys. Rev. A 94, 012335 (2016)
   (arXiv:1605.01605): discrete-time walks with exact discrete U(N) gauge invariance, a discrete
   curvature, and a Dirac continuum limit. That is our v4.0 engine's idea. Differences: they work
   in 1+1 dimensions with background fields; we are on a 3D simplicial (Kuhn) mesh with a finite
   group and, in option A, a *quantised* record.
2. **A discrete-time single-particle framework for lattice gauge theory** (arXiv:2208.14997) adds a
   lattice action for the gauge field but keeps it classical and abelian. A fully quantum record
   coupled to a walk, as in P21, is closer to Hamiltonian lattice-gauge quantum simulation than to
   the walk literature.
3. **The binary tetrahedral group as a gauge group.** Standard practice for digitising SU(2):
   *Primitive quantum gates for an SU(2) discrete subgroup: binary tetrahedral*, Phys. Rev. D 106,
   114501 (2022) (arXiv:2208.12309), with a binary octahedral sequel. Our arrival at 2T is
   independent but not new as a choice.
4. **Compact localized states and flux conditions.** Flat-band compact localized states, and
   Aharonov–Bohm caging where the flux decides localisation, are a large literature; the
   non-abelian version exists too (*Non-abelian Aharonov–Bohm caging in photonic lattices*,
   Phys. Rev. A 102, 023524 (2020), with trapped-ion proposals since). Our P28 existence law
   H a = e^{iLθ} a is the coined-walk instance of that genre.
5. **Trapping in coined walks.** "Trapped"/localized states of Grover-type walks are studied in
   detail, e.g. Štefaňák, Kollár et al., *Strongly trapped two-dimensional quantum walks*,
   Phys. Rev. A 91, 022308 (2015). Our compact loop states are trapped states in that sense.
6. **Symmetry classification of discrete-time walks.** The tenfold-way classification of DTQWs
   (Kitagawa; Asbóth and Obuse; Cedzich et al. on the topological classification of 1D symmetric
   quantum walks) is built on exactly the antiunitary symmetries we found, with T² = ±1 separating
   classes AI and AII. Our K is that symmetry; a specialist would call P29 a class-AI → class-AII
   change.
7. **No-current no-go theorems.** Bloch's theorem for lattice models (Watanabe,
   J. Stat. Phys. 177, 717 (2019), arXiv:1904.02700) forbids persistent U(1) current in ground and
   thermal states. Ours is a different statement (single-particle, exact, per edge, compact
   support) but the same family.
8. **Electron-as-circulating-light.** Williamson and van der Mark, *Is the electron a photon with
   toroidal topology?*, Ann. Fond. L. de Broglie 22, 133 (1997) — outside the mainstream; and
   Hestenes' zitterbewegung interpretation (Found. Phys. 40, 1 (2010); arXiv:1910.11085), which is
   the mainstream-adjacent version of the same intuition, including the 4π structure. Our
   two-traversal internal return is structurally the same idea reached from walk kinematics.
   Wheeler's geons are gravitational and need enormous mass-energy, so they are not a competitor at
   electron scale.

### Plausibly ours (none found in the search; none is a new physical principle)

- **The construction:** a gauge-covariant walk on the Kuhn/Freudenthal mesh with ring weights 1 : ½,
  its emergent BCC metric, 60°/90° pivots, coupled to a quantised A4 or 2T record with an exact
  one-tick unitary (P18, P21, `spin_record.py`).
- **The compact-loop package (P28)** stated for gauge-covariant coined walks: coin = −1 forcing,
  phases restricted to 0 and π, the existence law on the holonomy, the 1/√weight amplitude law, and
  zero current *including* time-dependent 0/π superpositions. Old genre, specific statement.
- **The requirement argument (P29–P30):** that stationary circulation in such a walk needs a
  degenerate eigenspace, that generic disorder removes it when T² = +1, and that the double cover
  restores it with T² = −1, with a measured churn threshold. The ingredients are textbook (Kramers;
  DTQW symmetry classes); using them as a *requirement on the internal space of a matter candidate*
  is, as far as this search goes, not stated elsewhere.
- **The negative results:** frozen records trap nothing (P19e); a hot record is opaque but one flash
  cannot cool it (P22–P23); the phase-filtered dressed loop is just a calm loop (P27); circulation
  does no work on its surroundings (P31).

### What would make a defensible external claim

The compact-loop package plus the no-current theorem, framed as a short note on gauge-covariant
coined walks, with the class AI/AII requirement as the physical corollary. That needs a proper
literature review (this was a single search pass) and a referee's eye on the AB-caging and
trapped-state literature, which may already contain the same statements in other language.

### Why the lattice-gauge community uses 2T, and why that matters to us (2026-09-20)

Their route is **approximation under a resource budget**: SU(2) has only the binary polyhedral
groups as finite subgroups (binary dihedral, tetrahedral 24, octahedral 48, icosahedral 120 — that
list is from background knowledge, not from this search), and the Fermilab paper states its reasons
plainly: 2T costs "five qubits or one quicosotetrit per gauge link" and is "a crude approximation to
SU(2) lattice gauge theory". The known cost of that crudeness is the **freezing transition**: a
subgroup discretisation stops tracking SU(2) at weak coupling, because the finite set of group
elements cannot resolve small field fluctuations (Hartung, Jakobs et al., *Digitising SU(2) gauge
fields and the freezing transition*, EPJ C 82 (2022), arXiv:2201.09625; the 1980s antecedents are
Bhanot–Rebbi and Petcher–Weingarten).

Our route is the opposite: the mesh's tetrahedral symmetry gives A4, and the double cover is
**forced** by P29 — stationary circulation in a disordered vacuum requires T² = −1. We did not pick
2T to stand in for anything.

**Two consequences worth keeping.**
1. For them freezing is an artefact; for us the discreteness is the claim, so "freezing" is a
   *prediction*: gauge angles come in fixed steps (our 60°/90° pivots, 120° label steps), and the
   subgroup literature's maps of where subgroup theories part company with SU(2) are effectively
   maps of where this framework must differ from continuum Yang–Mills.
2. A finite group is closed under multiplication, so no amount of coarse-graining makes a large
   loop's holonomy continuous. Continuum gauge fields cannot emerge here the way the metric did
   (P18). The only route left in our framework is the quantum record: in option A the labels are in
   superposition, so expectation values move continuously even though every basis label is one of
   24. That should be stated as a working position, not assumed.


## Proof-theoretic roots: has anyone looked at it this way? (2026-09-20, Opus; searched)

The project began from the user's question: *what would a mathematical derivation look like from
inside, as logic is progressively applied?* That question has a formal counterpart, and it is older
and more developed than our model.

### The closest existing object: Girard's Geometry of Interaction (GoI)

- Cut elimination — the act of actually carrying out a derivation — is modelled as **paths (Girard's
  "trips") through a proof net**, with the *execution formula* turning a proof into an operator.
  Later versions represent proofs as operators in von Neumann algebras (GoI V works in the
  hyperfinite factor); Seiller's *interaction graphs* generalise this.
- **Token machines** make it concrete: a token travels the net carrying internal state, transformed
  at each node (Laurent, *A Token Machine for Full Geometry of Interaction*, CSL 2001).
- **Causality has been studied there:** *The Geometry of Causality: multi-token GoI and its causal
  unfolding*, PACMPL/POPL 2023.
- **It already touches quantum dynamics:** Hasuo and Hoshino, *Semantics of higher-order quantum
  computation via geometry of interaction* (LICS 2011; Inf. & Comp. 2016, arXiv:1605.05079), and
  *Measurements in proof nets as higher-order quantum circuits* (ESOP 2014).

**The map to our engine is almost one-to-one:** our arcs are the net's edges, our walker is the
token, our group labels are the operators picked up along a path, our tick is one step of the token
machine, and our interference of paths is the execution formula's sum over alternating paths.

**Two differences, and both are useful.**
1. **GoI's algebra is not unitary.** Its dynamic algebra is generated by *partial isometries* (p, q
   with p*p = 1 but pp* ≠ 1) implementing a stack discipline: information is pushed and popped, not
   rotated. Our transport is group-valued and invertible. This matters directly:
   **Astra's no-current theorem (§15) assumes invertible transport** — with a partial isometry the
   "an empty exit must stay empty" step fails. A GoI-style stack is therefore a candidate escape
   from the no-circulation result, and the stack is itself a record, which is an independent
   argument for why a record must exist at all.
2. **In GoI the net is consumed.** Cut elimination *rewrites the proof*; the graph is the thing that
   changes. Our mesh never changes: our dynamics only moves amplitude across a fixed complex. That
   is exactly the gap where the expansion rule belongs (the user's open decision), and it suggests
   the proof-theoretic form of the rule: reduction should consume or rewrite mesh structure
   (Pachner-type moves), not merely transport amplitude.

### Other programs that ask "why" rather than "what"

- **Logical-inference derivations of quantum theory.** De Raedt, Katsnelson and Michielsen derive
  the Schrödinger, Klein–Gordon, Dirac and Pauli equations from premises about robust experiments
  and plausible reasoning (Ann. Phys. 2014–2018; Phil. Trans. R. Soc. A 374, 20150233 (2016)).
  Closest in spirit to the user's question, but their inference is Bayesian/epistemic, not
  proof-theoretic, and space is assumed rather than derived.
- **The Wolfram Physics Project** (hypergraph rewriting; Gorard's papers on relativistic and quantum
  properties of the model) is the most direct competitor in spirit: a rewriting system whose
  internal view is supposed to be physics, with multiway/branchial structure playing the role of
  quantum mechanics. Widely criticised for the scarcity of falsifiable predictions — a criticism
  that applies to us as well.
- **Tegmark's mathematical universe hypothesis** is the philosophical precedent for "the inside view
  of a mathematical structure", with no dynamics attached.

### Verdict

The *framing* is not new — GoI is fifty years of work on exactly "a derivation seen from inside",
and Wolfram's project is the best-funded modern attempt at "physics as the inside of a rewriting
system". What appears not to have been done is the specific combination we have: a token walk on a
**3D simplicial complex** with **finite-group labels** and an energy-accounted **quantum record**,
asked to produce matter. That is a narrow claim to novelty, and the two leads above are worth more
than the claim.


### Topologically constrained loops: who is doing that? (2026-09-20, searched)

**In proof theory: the topology is a correctness condition, not a particle.** Non-commutative and
cyclic linear logic require proof nets to be *planar*; there are surface/genus criteria and ribbon
formulations (Abrusci–Ruet; Melliès, *A topological correctness criterion for multiplicative
non-commutative logic*; "Surface proofs for linear logic"). So topology constrains which graphs
count as derivations — nobody there asks whether a knotted or linked sub-net is a *stable object*.
That question appears to be unasked on the logic side.

**In physics it is a live field, and three programmes are close to us.**

1. **Kitaev's quantum double models** — the closest technical match. A finite group on the edges of
   a lattice, with star (electric) and plaquette (magnetic) terms; the excitations are **flux**
   (a conjugacy class: the holonomy of a loop) and **charge** (an irrep), and their composites are
   dyons, with topological protection and a spectral gap (classification of the anyon sectors:
   Comm. Math. Phys. 2025; Kitaev's model as an error-correcting code: Quantum 4, 331 (2020)).
   Our curved faces *are* fluxes and our walker carries an irrep of the same group, so our matter
   candidate is a flux–charge composite in D(A4) or D(2T). This literature already answers
   questions we have been asking blind: whether flux sectors are superselected, whether charge
   binds to flux, and where the gap comes from.
2. **Braided ribbon networks / "braid matter"** (Bilson-Thompson; with Markopoulou, Smolin, Hackett,
   Kauffman; arXiv:0804.0037, 1109.0080) — braids in spin networks proposed as Standard Model
   particles, inside a quantum-gravity graph model. This is the closest existing programme to our
   holy grail, and its key technical notion — braids as *noiseless subsystems*, conserved by the
   evolution moves — is our dark/trapped states under another name. Worth knowing that it stalled
   at the same place we are: identifications without dynamics, no masses.
3. **Knotted solitons** (Faddeev–Niemi; Hopfions), where a knotted loop is stabilised by a
   topological charge, with genuine existence proofs of energy minimisers (Comm. Math. Phys. 2004).
   That is the continuum statement of "topology holds matter together", and the contrast with our
   P14–P16 result (topology gives no barrier under our action) is informative: their stability comes
   from a Skyrme-type term in the action, which our action does not have.

Also structurally adjacent: **loop quantum gravity spin networks** are SU(2)-labelled graphs, i.e.
our mesh with labels, though the dynamics and the questions differ.

**What this suggests for us.** The quantum-double literature is the one to read next, because it is
the same mathematical object with a finished theory attached. A concrete test: does our model
reproduce quantum-double phenomenology — flux superselection, charge–flux binding, a gap, and
topological degeneracy on a torus? If it does, we inherit their results and our "self-binding"
question becomes "where is our Gauss-law constraint and gap?". If it does not, that is a real
negative about our dynamics rather than another inconclusive run.
