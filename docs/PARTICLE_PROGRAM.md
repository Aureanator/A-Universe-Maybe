# Particle and reaction program

Requested 2026-09-18: continue until particles, fusion, fission, and chemistry are
demonstrated, with graphics and the existing epistemic discipline.

## What must be demonstrated

**Named structural target (user request, 2026-09-19):** the Williamson–van der
Mark electron model. [ELECTRON_TARGET.md](ELECTRON_TARGET.md) records the primary
reference, operational reproduction gates, and missing state/dynamics ingredients.
It is a target, not a claim that this solver already contains electrons.

No particle catalogue, trajectories, attractive force, reaction rules, or valences
will be inserted into the microscopic state. State remains the labelled simplicial
complex. Coordinates remain a rendering choice. Group, complex, boundary condition,
move set, action, scheduler, and ensemble are separate declared model inputs;
choosing them is not a derivation from the basement axiom.

1. **Particle candidate:** a localized, gauge-invariant structure detected from
   labels, without freezing its core or its own boundary. Measure support, lifetime,
   mobility, and external residue independently. A frozen defect or a momentary
   curvature cluster is not evidence of a freely persisting particle.
2. **Fusion/fission candidate:** a recorded microscopic trajectory joining/splitting
   identifiable persistent structures while preserving the enclosing boundary
   state. Cluster merger/split alone is geometric evidence, not a nuclear process.
   Record the inverse route and distinguish possible channels from sampled rates.
3. **Bound composite:** components retain distinguishable structure, separation
   remains bounded under unrestricted permitted dynamics, and an independently
   measured dissociation barrier or lifetime exceeds matched unbound controls.
4. **Chemistry:** reproducible species and bound composites with selective,
   reversible reaction channels, stability and conservation accounting. A fusion
   tensor, a single collision animation, or proximity on a layout is insufficient.

These are toy-model criteria, not identification with Standard Model particles or
real chemical elements. D(A4) fusion data are kinematics; rates and binding still
need a microscopic dynamics experiment. Flux structures in this 3D model may be
loops or junctions; do not relabel them as point fermions.

## Ordered gates

1. Resolve shared-face frame alignment; retain explicitly named legacy controls.
   Repair topology changes and default-driver provenance before using them as
   physical evidence. Close erroneous audit prose without rewriting history.
2. Enumerate or explore a gauge-invariant local-rewrite energy landscape. The
   simplest candidate action is the count of nonidentity face holonomies; it is
   a driver hypothesis, not physical energy or mass. Start with exact small
   complexes, then compare mesh sizes, groups, starts and proposal arms.
3. Search for unpinned persistent structures, report negative controls and failed
   searches. Preserve full event traces so mergers and splits are replayable.
4. Only promote a structure to a species, or a cluster process to chemistry, once
   it passes the criteria above. Publish figures and animations with model and
   claim status visible in the figure, plus machine-readable measurements.

## Current status

**2026-09-19 reframing:** the gates above still stand. What counts as a
particle candidate has changed: it is now trapped circulation of implication
under the v4 dynamics (`WORKING_STATEMENT.md`, `DYNAMICS_DESIGN.md`), not a
defect of the classical action H. Everything below was measured under the
pre-v4 engine and is kept as the control arm.


The interaction convention is repaired and P8-P11 completed the first unpinned
search. No structure passed the particle gate. P12 now supplies exact two-move
decay witnesses for both A4 n=5 endpoints that survived 200,000 proposals:
H=8 -> 4 -> 0 and H=10 -> 6 -> 0, with fixed outer boundary and no raised action.
Frozen-core experiments and category fusion tables still do not pass these gates.

P13/P13b tested this obstruction explicitly: a prescribed pair of linked flux
loops merges through a junction in 38 nonincreasing rewrites (H=98 -> 84) in
Z3 and its A4 subgroup lift. A 140-move erasure path reaches vacuum, with one
uphill increment of +1. The first bounded downhill search remains inconclusive.
The unrestricted fixed-boundary label graph is connected by a constructive
group-theoretic argument, so it cannot supply nonconstant invariants of all
interior-edge rewrites. See [the topology audit](TOPOLOGY_AUDIT.md).

P14 (2026-09-19) answered this for the abelian fixture: it has an entirely
nonincreasing route to vacuum. P15 repeated the test with NON-commuting fluxes in
full A4. Linking then forces a V4 tether, as the topology requires, but a nonincreasing
erasure still exists; the loops unlink as the tether shortens. No barrier has
been found for any closed flux network in a flat-bounded ball under H. The open
directions, all of which change the declared model, are listed in
`reference/opus_session/WORKING_STATE_2026-09-19.md`. P16 (bag test) shows why:
the model has surface tension but no pressure and no conserved interior content.
[BAG_PICTURE.md](BAG_PICTURE.md) gives the job specification for a new ingredient. Broader searches
must measure energetic/dynamical stability, not infer it from knotting alone.
Adding a prohibition on reconnection would be a new model postulate, not a
discovery of stability. Any alternative action or move set needs its additional
assumptions and controls registered in advance.

Bulk point-fermion exchange, stable nuclei, nuclear reactions, atoms, and chemical
bonds remain open. Outcomes and further pre-registrations belong in
`PREDICTIONS.md`; chronology belongs in `RESEARCH_DIARY.md`.
