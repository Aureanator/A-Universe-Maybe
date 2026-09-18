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
| `knots.py` (PL knot/link invariants of flux loops) | Knot states in gauge theory / loop quantum gravity (Rovelli–Smolin 1995); anyon knot statistics literature | Early-stage tooling; linking-number bug documented openly (skipped test). No claim until fixed. |
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
