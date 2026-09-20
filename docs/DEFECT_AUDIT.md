# Defect-model audit and first charge configurations — 2026-09-20

The user's newer Opus transcript supersedes the earlier P25 handoff. The pending
P31 work and projector kernel were preserved in `e1daede`, together with the
P32A preregistration. This audit preserves the previous documents as history and
narrows their interpretations to what the implemented operators establish.

## What is implemented

`GaugePatch` has a group-label Hilbert space on edges, vertex gauge averages A_v,
flatness projectors B_f, and H=-sum A_v-sum B_f. This is a **POSTULATED**
commuting-projector Hamiltonian. Its connection to the implication axiom remains
a modelling argument, not a derivation. It is a useful established construction
to test: [Kitaev's original paper](https://arxiv.org/pdf/quant-ph/9707021) describes
the energetic penalties, excited sectors, and string operations (sections 1–3).

Three distinct claims must stay separate:

1. **Probability conservation:** the earlier walk already satisfies an exact
   local continuity equation (`current.py`). It did not create probability at
   vertices. This does not, on its own, impose gauge invariance of the record.
2. **Gauge invariance:** A_v psi=psi is the invariant-sector condition. Restricting
   the physical edge Hilbert space to this condition excludes states with A_v=0.
   To include charged matter while enforcing a Gauss law, one needs an appropriate
   charge-sector or matter-coupled constraint. That construction is not in this kernel.
3. **Finite penalties:** the implemented H allows A_v=0 states at a finite cost.
   A projector appearing in H is not an instruction to project the state after
   every tick. In the unrestricted Hilbert space these violations are electric
   excitations; they do not mean probability has been created or destroyed.

Likewise, a small positive coupling is not evidence of no gap: lambda(I-P) has
gap lambda for any nontrivial projector P and lambda>0. The previous record's
gaps require a spectral/size analysis, not the words "soft" versus "hard".
Neither a chosen integer penalty nor its gap has yet been identified with
inertial mass or derived from the single axiom.

## P32A: explicit electric charge pairs

The matrix-free state operations in `defect_ops.py` use the existing projector
definitions. The fixtures are small enough to enumerate every edge configuration:

| Group | Patch | Hilbert dimension | Nontrivial characters | Ordered pair cases |
|---|---|---:|---|---:|
| Z2 | tetrahedron boundary | 64 | k=1 | 12 |
| Z3 | tetrahedron boundary | 729 | k=1,2 | 24 |
| A4 | one triangular face | 1728 | 1',1'' | 12 |

The vacuum is a normalized uniform sum over flat configurations. A unitary
electric string multiplies each configuration by chi of its oriented path
holonomy. For every tested case:

- A=0 at the two endpoints, A=1 elsewhere, and B=1 on every face;
- energy is E_vac+2, independent of which tested endpoints are selected;
- direct and two-edge paths give the same state on this flat vacuum;
- continuing the string by one edge moves an endpoint at the same energy;
- an inverse direct-edge string annihilates an adjacent pair;
- an operation on an opposite, disjoint edge leaves the original endpoint
  readouts unchanged, although it can create another pair elsewhere.

The largest pair energy-eigenvector residual is 1.09e-15; path differences are
zero in the saved arrays; move/annihilation errors are below 8.3e-16. The finite
patches and one-dimensional character sectors are deliberate limits. These are
48 preparations, not 48 species, and no three-dimensional material body is shown.

Path equality is conditional: a curved configuration supplies a counterexample
to equality of the two string operators on the whole Hilbert space. Local
operations can move defects; protection does not mean immobility. These are
controlled interventions, consistent with the string operations in
[Kitaev's construction](https://arxiv.org/pdf/quant-ph/9707021), not autonomous
motion or an energy-conserving annihilation in an isolated world.

## What "stable" means here

Since every term commutes, [H,A_v]=[H,B_f]=0. Each local defect occupation is
exactly conserved under the newly supplied U(t)=exp(-itH). A pair eigenstate
therefore acquires only a phase. P32A verifies this at t=0.37 and 7.25 (error
below 7.2e-15), with an independent dense-exponential check on Z2.

This is exact frozen-sector stability. It supplies neither propagation nor
self-binding. There is no open-boundary release channel in this state space,
so P32-3 remains untested. A future hopping or interaction rule must be stated,
its conserved quantities verified, and its energy exchange accounted for before
testing lifetimes or bound configurations. A prescribed translation string is
not evidence that H makes a defect travel.

Applying A at a charged endpoint gives the zero vector (norm below 3e-16). Thus
an actual hard all-vertex projection would eliminate these candidate states.
Conversely the all-identity *basis configuration*, despite being flat, has
<A_v>=1/|G|: 1/2, 1/3 and 1/12 in the three fixtures. An old dark walker loop
therefore cannot be declared charge-free merely because its classical labels
are flat. P32-4 needs an explicit map between the old and new state spaces.

## Claims to audit before the dimensional step

- The 14/42 D(G) sector counts are not automatically ground-state degeneracies
  on a spatial three-torus. Untwisted flat gauge states there involve commuting
  triples modulo simultaneous conjugation; use a dimensional calculation, not
  the two-dimensional anyon count. The
  [three-dimensional gauge-model construction](https://archive.ymsc.tsinghua.edu.cn/pacm_download/67/9255-Twisted_Gauge_Theory_Model_of_Topological_Phases_in_Three_Dimensions.pdf)
  treats three-torus degeneracy separately from the two-dimensional model.
- The equation p+q=d-1 concerns the ordinary complementary-dimensional linking
  pairing. By itself it is not a proof that every other kind of linking or
  braiding is impossible in d=4. P32-6 requires a precise invariant and a
  corrected falsification condition before an experiment can settle it.
- A_{d+1} is the even vertex-permutation group of an abstract oriented simplex;
  interpreting it as geometric rotations requires metric assumptions. Also,
  binary icosahedral is not the largest finite subgroup of SU(2): matrices
  diag(exp(2*pi*i/n), exp(-2*pi*i/n)) generate finite cyclic subgroups of
  arbitrarily large order. The special role of three dimensions remains open.

These scope corrections do not undo any archived finite computation. They
prevent a known projector model's properties from being counted as a derivation
of moving matter, an electron, nuclei or chemistry from the axiom.

Evidence: `examples/p32_defects.py`, `reference/astra_session/data/p32a_defects.json`,
`tests/test_defect.py`, `tests/test_defect_ops.py`. Reproduce with:

```powershell
.venv/Scripts/python.exe examples/p32_defects.py --output out/p32a_reproduction.json
```

Outputs must have a new filename. Source claims and priors were retained;
P32A outcomes are appended in PREDICTIONS.

## Follow-up: transport and statistics (P32B/P32C)

The unchanged H0 remains frozen. `P32B_TRANSPORT.md` defines a separate local
Z2 extension K with [K,H0]=[K,N]=[K,B_f]=0 but [K,A_v]!=0. Exact finite-patch
evolution demonstrates motion and number-current continuity. The rule blocks
pair creation and annihilation, so it is a diagnostic of compatible conservation
laws, not an emergent stability mechanism or a hard-Gauss-law completion.

`P32C_EXCHANGE.md` checks the resulting flat-pair hopping algebra against a
fermionic control: the former is bosonic (+1), the latter fermionic (-1), in
all 108 cases. This supplies an explicit statistics gate for future candidates.
