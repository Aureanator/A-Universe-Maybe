# Flux topology under the actual rewrite law — P13 / P13b

**Result (2026-09-19):** prescribed linked flux loops on a Kuhn n=8 ball
can merge under nonincreasing local edge rewrites. Both Z3 and its explicit
order-3 subgroup embedding in A4 reproduce the witness. This is a geometrical
merger, not particle fusion. Neither fermions nor nuclei are identified.

## Model and exact connectivity statement

Fix a finite labelled simplicial complex and a finite group G. Freeze every
edge belonging to an outer boundary face. Allow right multiplication by every
nonidentity group element on each remaining edge, as in the curvature driver.
No additional core, probe-cycle, loop-number, or no-reconnection predicate applies.
H is the chosen count of nonidentity face holonomies, not derived physical energy.

**Proposition.** Any two edge-label assignments with the same fixed boundary
are connected by these unrestricted moves.

**Proof.** For each interior edge whose source label is a and target label is b,
multiply on the right by a^-1 b. This multiplier is nonidentity exactly when
the labels differ, and a(a^-1 b)=b. It changes no other edge. After at most
E_interior moves all target labels agree, and every boundary label is untouched.
Equivalently the label graph is a Cartesian product of complete graphs on G.
An invariant of every such move is consequently constant on this fixed-boundary
space. Projecting paths to gauge equivalence classes preserves connectivity.

This proof applies to the **unrestricted proposal graph**. The ideal finite-beta
Metropolis law has strictly positive acceptance for each such move; numerical
exponential underflow at very large beta is not topological protection. The
beta=infinity graph deletes uphill moves, so its connectivity is a separate
question. Other actions, forbidden reconnections, or additional constraints
define other models. On a nontrivial boundary, connectivity does not imply that
a flat filling exists. With identity boundary, the all-identity target is flat.

Implementation: `rewrites.py` constructs witnesses and independently verifies
full-holonomy action traces, fixed boundaries, target labels, and inverse replay.
Tests include every pair of labels on the single interior edge for Z3 and A4,
and arbitrary fixed-boundary assignments on a larger mesh.

## A link exists in the actual labels, not just in a drawing

The preregistered fixture assigns labels by oriented primal-edge intersections
with two internal rectangular disks. Its coordinates are used for preparation
and measurement only. The search and rewrite law read incidence and group
labels; they do not read coordinates. The A4 lift uses one cyclic subgroup,
so agreement with Z3 is a control, not intrinsically non-abelian physics.

The actual curved-face support comprises two disjoint dual cycles, of lengths
52 and 46. Each dual edge is routed through the shared face barycenter between
its tetrahedron barycenters. The walk follows adjacency; sorted support is not
a cycle order. Exact rational signed-crossing measurement gives |Lk|=1.

Two prerequisites were repaired:

- A loop now requires two incident tetrahedra per curved face as well as degree
  two at every touched tetrahedron. The old test could accept a boundary-open arc.
- The old linking code omitted the over/under factor in crossing signs. The
  replacement uses rational predicates, retries nongeneric projections, raises
  on uncertified cases, and checks that the signed sum is even. It does not
  silently drop degeneracies or floor a half-integer result. The formerly skipped
  Hopf regression now passes, as do orientation, reflection, subdivision,
  multiple-view, and unlink controls. The definition is the standard half signed
  crossing sum ([Friedl, Definition 1.3.1](https://web.stanford.edu/~sfh/knot.pdf)).

The boundary check also corrects E026: the n=1 vertex-star seeds at six of eight
vertices are three-face open arcs, each with two boundary faces. The central
n=2 twelve-face loop remains closed. The old test asserting n=1 loop closure
was replaced by a full eight-vertex incidence check; the historical claim is
retained with a dated correction in the diary.

These repairs do not validate the separate legacy single-knot Gauss/Alexander
heuristics as a general exact knot classifier. Linking zero also does not, in
general, prove that an arbitrary pair is an unlink. Likewise |Lk|=1 establishes
nontrivial linking, not by itself the full Hopf link isotopy type of a mesh pair.

## Registered experiment and preserved cutoff

The original 32-state-per-plateau downhill search found 98 -> 98 -> 98 -> 96
in both groups, preserving |Lk|=1, then reported `budget_exhausted`. This remains
an inconclusive search outcome, not a closed plateau or a measured barrier.
The follow-up below was registered separately after that result.

The exhaustive initial one-edge census was:

| Group | Proposals | Nonincreasing, two loops | Uphill, two loops | Uphill, junction | Uphill, changed loop count |
|---|---:|---:|---:|---:|---:|
| Z3 | 6,064 | 8 | 179 | 367 | 5,510 |
| A4 | 33,352 | 8 | 179 | 2,860 | 30,305 |

No initial nonincreasing proposal left the two-loop domain. This census tests
component kinds/counts, not every candidate's linking number. That local fact
does not imply domain preservation after several moves.

## Constructive merger and erasure

The ascending-edge-order path setting labels to identity produces identical
action and support histories in the two subgroup-related fixtures:

| Rewrite index | H | Support | Prefix nonincreasing? |
|---|---:|---|---|
| 0 | 98 | Two loops, magnitude Lk=1 | yes |
| 37 | 86 | One junction component | yes |
| 38 | 84 | One loop | yes |
| 40 | 85 | Junction; the sole positive increment is 84 -> 85 | no |
| 52 | 80 | Two loops, Lk=0 | no |
| 140 | 0 | No curved faces | no |

Linking is **undefined** for the intermediate junction or single-loop states;
it is not recorded as zero there. Only magnitudes are compared, because each
new cycle's reporting orientation is chosen independently. The merger prefix
is independently verified by the nonincreasing decay verifier. Full erasure
uses one +1 step and never exceeds initial H=98. This is a path upper bound,
not proof that the +1 step is necessary or that no entirely nonincreasing path
to vacuum exists. Search order and rewrite index are not physical time or rates.

Both complete witnesses have full-action, boundary-label, inverse, and transported
gauge-witness checks. The flux support is also unchanged by independent vertex
gauge transforms. The figure is regenerated from the saved microscopic moves.

## Reproduce

```text
python examples/topology_audit.py
python examples/topology_rewrite_audit.py
python examples/topology_audit_graphics.py
```

Machine-readable records: `reference/astra_session/data/topology_audit.json`
and `topology_rewrite_audit.json`. Figure: `out/topology_audit.png`.
Regression coverage: `tests/test_topology_audit.py`, `test_linking.py`,
`test_knots.py`, `test_strings.py`, `test_rewrites.py`.

The next unresolved question is energetic or dynamical stability under a stated
law, not exact conservation of these loop components. An action-minimizing escape
search must distinguish a true barrier from a search cutoff. Stability, mobility,
exchange statistics, binding, and reaction selectivity still need independent
evidence before this program reaches the requested particles and chemistry.

## P14 — the uphill step was an ordering artifact (2026-09-19)

Reordering steps 33–48 of the P13b erasure yields a fully nonincreasing 140-move
erasure, H=98 -> 0, in both Z3 and A4. The step at 38 (86 -> 84) now comes
after steps 39–40. Checks: full action, boundary, inverse and gauge transport.
`examples/topology_decay_order.py`; `reference/astra_session/data/topology_decay_order.json`.
**The prepared abelian linked pair has no action barrier under H.**

## P15 — non-commuting fluxes: forced tether, still no barrier (2026-09-19, Opus)

The same disks carry a and b in full A4 (`examples/noncommuting_link_audit.py`).
Because pi_1 of a Hopf-link complement is Z^2, a flat field off two Hopf-linked
loops requires commuting meridians. Consequently:

| Arm | a, b | Commute | Initial support | H | Nonincreasing single moves (domain kept) | Ordered erasure |
|---|---|---|---|---:|---|---|
| C0 | same order-3 (= P13 labels) | yes | two loops, abs(Lk)=1 | 98 | — (see P13b) | nonincreasing, peak 0 |
| C1 | distinct V4 | yes | two loops, abs(Lk)=1 | 98 | 8 of 33,352 (two loops) | nonincreasing, peak 0 |
| N1 | order-3 / order-3, different subgroups | no | ONE junction: loops + 5-face V4 tether | 103 | 10 of 33,352 (junction) | nonincreasing, peak 0 |
| N2 | V4 / order-3 | no | ONE junction: loops + 5-face V4 tether | 103 | 10 of 33,352 (junction) | nonincreasing, peak 0 |
| N1/N2 tie control | disk-2 factor first on 4 line-crossing edges | no | ONE junction, 6-face tether | 104 | — | nonincreasing, peak 0 |

In every N run the junction survives to step 52 (H=80). It then becomes two
loops with Lk=0 whose meridians do not commute, which is legal for an unlinked
pair. Tether and linking vanish on the same move. Plateau searches (32/256
states) are inconclusive budget cutoffs. Figure: `out/p15_noncommuting_links.png`.
**Non-abelian entanglement is real in the labels (Z3 and A4 now differ
topologically), but under H it is not an energetic barrier.**
