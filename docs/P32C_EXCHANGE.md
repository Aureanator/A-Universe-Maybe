# P32C — Exchange-algebra control prompted by quantum spin liquids

Registered before execution, 2026-09-20; after the P32B transport run. The user's
[quantum spin liquid link](https://en.wikipedia.org/wiki/Quantum_spin_liquid)
led to the following primary-source diagnostic.

[Levin and Wen, 2003](https://arxiv.org/abs/cond-mat/0302460), section III,
equation (4), relate exchange statistics to directed hopping operators:

    t_il t_ki t_ij = exp(i theta) t_ij t_ki t_il.

Here t_ab moves an excitation from b to a; j,k,l are distinct neighbors of i.
Their analysis includes 3D examples. This supplies an exchange-algebra benchmark
for our excitations, beyond a chosen spinor representation or a loop shape.

## Fixed protocol

Use the same two Z2 fixtures as P32B. For each central vertex i and every ordered
triple (j,k,l) of distinct neighbors, prepare the flat pair at j,l. Define the
directed unit-amplitude hop on the **full edge Hilbert space** by

    t_ab psi = T_ab n_b psi.

Apply the two triple products above, rightmost operator first. Record both final
norms, overlap <right|left>, and residuals ||left-right|| and ||left+right||.
Both products must have norm one; zero products cannot certify an exchange sign.
Each should finish with charges at i,k. There are 24 cases on the tetrahedron
and 84 on the bipyramid (108 total), with no selected subset.

**Independent sign control:** implement canonical fermionic hopping c_a^dag c_b
on sorted vertex-occupation states with the sign (-1)^(number of occupied
vertices strictly between a and b). Apply the same directed sequences. This
control explicitly supplies fermions; it cannot count as their emergence in the
edge model. It verifies the sign and operator-order conventions of the diagnostic.

**Prediction:** edge-model products have relative sign +1, and canonical-fermion
control products have relative sign -1, in all 108 nonzero cases. Final-state
residual tolerance 1e-10. This diagnoses the P32B flat electric-pair sector,
not every excitation of every gauge model, and not the A4/2T walker. The
POSTULATED hopping and finite preparation restrictions remain in force.

## What to learn for the research queue

The spin-liquid connection suggests investigating collective vacuum states and
excitation algebra together. This is a project inference, not a new result.
[Kitaev's honeycomb model](https://arxiv.org/abs/cond-mat/0506438) is an exact
benchmark with a spin Hamiltonian reducible to fermions in a Z2 gauge field.
[Levin–Wen string nets](https://arxiv.org/abs/cond-mat/0404617) provide another
construction relating collective extended structures to gauge fields and
fermions. These models add specified quantum dynamics and algebra; they do not
derive those ingredients from our implication axiom.

For this project, random classical label disorder is not evidence of a quantum
spin liquid. A stationary entangled ground state need not exhibit time-varying
one-point expectations. Neither spin-liquid valence bonds nor string endpoints
alone identify chemical bonds or electrons. Next candidate mechanisms must
declare their local algebra and pass a statistics test before being promoted to
fermions. The Williamson–van der Mark target remains separate and unachieved.

## Outcome (appended after execution)

Preregistration commit: `5c2ef6a`. All 108 cases passed: both edge-model products
have norm one, reach the expected final charge positions, and agree with relative
sign +1. The independent canonical-fermion control gives -1 in every case.
The maximum edge-model residual is 2.23e-16. Thus the tested flat electric-pair
sector of the new transport diagnostic has bosonic exchange algebra. It is a
working negative control for a future fermion search, not a fermion discovery.

Evidence: `examples/p32_exchange.py`,
`reference/astra_session/data/p32c_exchange.json`. Reproduce to a fresh path:

```powershell
.venv/Scripts/python.exe examples/p32_exchange.py --output out/p32c_reproduction.json
```
