# The bag picture: why we are testing it, and how

Status: **working hypothesis (POSTULATED framing), not a result.** Recorded
2026-09-19 from a discussion between the user (Satish) and Claude (Opus).
Measured content is marked as such and points to its evidence. Everything else
is a proposal that needs its own pre-registration before code is written.

## 1. Why this document exists

The project's goal is recognisable matter: particles that persist, bind and react.
Experiments P8–P15 tested every candidate the current model offers under the
declared action H (count of curved faces, all interior edge moves allowed,
identity outer boundary):

- curvature clusters (P8–P10)
- slow "glassy" leftovers at larger mesh sizes (P11–P12)
- linked flux loops with commuting fluxes (P13–P14)
- linked loops with non-commuting A4 fluxes, which topology forces to carry a tether (P15)

Every one has a route to vacuum with no uphill step. Topology decides *which*
intermediate shapes appear. It has not stopped anything from decaying.

The picture below explains why that keeps happening. It also turns "find a
particle" into a specific engineering requirement.

## 2. The picture (user's intuition, in plain words)

1. **Implication with a corollary cone.** Each directed implication has
   a sideways effect that spreads perpendicular to it at the same speed as
   the implication itself. The result is a cone with a 90° opening angle (45°
   half-angle). That is the shape of a light cone.
2. **Vacuum = wake interference.** Space is full of these cones' wakes. Where
   they overlap and cancel, you have vacuum.
3. **Particle = pressurised bubble.** A particle is a pocket where the wakes do
   not cancel. It is held at a finite size by a balance between the vacuum
   outside and something inside.
4. **No choosing among paths** (later addition, see §8). If an implication only
   has to be continuous, and the geometry allows several continuous routes,
   a light-like entity cannot pick one. It must traverse all of them at once,
   in proportion.

## 3. Translation into this model's vocabulary

| Picture | Existing model object | Status |
|---|---|---|
| Implication | Directed edge with a group label | DERIVED/POSTULATED (memo §2–3) |
| Wakes cancel = vacuum | Every closed loop of implications reduces to identity (flat; "full reduction", memo §3) | Matches the existing definition |
| Non-cancelling pocket | Region with nontrivial holonomy (residue = charge) | Exists (E005–E030) |
| Bubble wall | Region boundary; the confinement test rejected 1,108 of 1,108 surface moves (E006, under the appearance-preserving acceptance rule) | Walls CAN hold charge, when the rule forbids changing what the boundary shows |
| Pressure from inside | **Nothing yet** — see §5 | MEASURED absence (P16) |
| Sideways "corollary" direction | The *link* of an edge: the ring of faces and tetrahedra around it (coordinate-free) | Proposal |
| Traverse all paths | Sum over paths with group/representation weights (Wilson lines); `fringe.py` already does the two-path case | Partial (E015 discrete Aharonov–Bohm) |

## 4. Known physics with the same shape

- **MIT bag model of the nucleon.** Quarks sit inside a bubble. The vacuum
  pushes in with a constant pressure; confinement of the quarks pushes out.
  Balance fixes the radius. It gives decent nucleon masses and radii, and
  nucleons are the project's stated holy grail.
- **Q-balls (non-topological solitons).** Stable without topological
  protection because they hold a conserved charge that cannot leak, and
  shrinking would cost more energy than it saves.
- **Casimir effect.** A cavity excludes vacuum modes, so outside and inside push
  differently.
- **Williamson–van der Mark electron** (`ELECTRON_TARGET.md`). Light confined
  in a bubble of its own making.
- **Huygens' principle and the path integral** (§8). Every route contributes,
  and cancellation between routes is what makes empty space look empty.

## 5. Why the current model cannot make a bubble (P16, measured)

A stable bubble needs its energy to have a minimum at a finite size. That takes
two opposing terms. Schematically, E(R) ≈ σR² + N/R: a surface cost that grows
with size, plus a confinement cost of N trapped quanta that grows as the bubble
shrinks. The minimum is at R* ∝ (N/σ)^(1/3).

What the current model supplies (P16; `examples/bag_test.py`,
`reference/opus_session/data/bag_test.json`):

- **Tension: yes.** Every curved face costs 1, so every structure wants to shrink.
- **Hidden internal states: none.** A flat interior has exactly one physical
  filling at every size tested (Z3 n=1–3, A4 n=1–2). The raw count grows like
  |G|^(interior vertices), but every copy is gauge redundancy.
- **Volume-scaling entropy: yes, but uniform.** The number of smallest loop
  excitations is exactly 3n²(n−1), which grows like volume. At finite β the
  vacuum therefore holds a thin gas of small loops. Its density depends on β
  only, so it is identical inside and outside any region. That favours
  dispersal, not a bubble.
- **Conserved interior content: none.** Claim 30: under all interior moves no
  quantity is conserved except the boundary data. Nothing plays the role of the
  bag's conserved quark number, so the N in E(R) is always zero.

**This explains P8–P15.** With only the σR² term, the energy has no minimum
except R = 0, so everything deflates. Those experiments were not failures of
topology. They were measurements of a missing term.

## 6. What an extension must supply (the job specification)

Any cone/wake extension is a **declared model change**. It must be registered in
`PREDICTIONS.md` with controls before it is implemented, and it passes only if it
provides all of the following, each measured, none inserted by hand:

1. **Trapped content.** Something inside the bubble that cannot cancel against the
   vacuum outside. The picture suggests wakes that reflect off the bubble wall, as
   light does in a cavity.
2. **Conservation of that content.** If it can leak or be erased by a permitted
   move, the bubble still deflates. This needs a conserved quantity or a
   measured barrier, reported against the claim-30 theorem.
3. **Confinement energy that grows as the bubble shrinks** (the N/R term).
   Measure E(R) for prepared bubbles of several sizes. A minimum at finite R is
   the pass criterion; a monotone E(R) is a clean fail.
4. **No coordinates in the dynamics.** "Perpendicular" and "same speed" have
   to be combinatorial. The natural candidate is the edge's link ring: each
   implication carries a pointer to a position on the ring around it, and the
   pointer advances one step per step. That gives each edge a framing. Framing is
   the ingredient the project already lacks for the non-abelian Bianchi identity,
   for spin-½ signs, and for gate W2 of the electron target. For spin ½, the
   pointer lives on a double cover of the ring: it must go round twice to return.
5. **Stated speeds.** Equal forward and sideways speed (the 45° cone) is a
   postulate until derived from the axiom. It should be tested against
   alternatives, not assumed.

## 7. Correction recorded in the same discussion: "twisting" and fermions

An earlier handoff suggested a "twisted Dijkgraaf–Witten cocycle from H³(A4,U(1))"
as the route to point fermions. That was imprecise:

- H³ twists belong to 2D space plus time. For 3D space plus time the twist
  lives on 4-dimensional spacetime cells and is classified by H⁴(G,U(1)). It
  changes how flux LOOPS braid (including three-loop braiding).
- To our knowledge (Lan–Kong–Wen classification; not re-derived here), point
  charges in 3+1D Dijkgraaf–Witten theories are bosons whether or not the theory
  is twisted. Point fermions in 3D need a gauge theory whose charges are
  themselves fermions (for example, the "fermionic toric code" or Walker–Wang-type
  models).
- Both routes also need a quantum layer (amplitudes). The current engine is
  classical labels plus a counting action, so a twist would have nothing to act on.

The CLAIMS row 23 "H³ menu check" should be read in this light.

## 8. "It cannot choose, so it takes every path": assessment

This is Huygens' principle, and in quantum form Feynman's sum over paths. It
fits the project well:

- **Vacuum as agreement of all paths.** Two routes between the same endpoints
  differ by the holonomy of the loop they enclose. Where everything is flat, every
  route gives the same answer, so traversing all of them is consistent. That is a
  precise version of "wakes cancel to vacuum". Where a flux is enclosed, the routes
  disagree and interfere. `fringe.py` already measures the two-path case: visibility
  |χ(flux)|/3 (E015, discrete Aharonov–Bohm).
- **"Proportionally" is the decisive word.** If the traversal splits as
  *probabilities* (positive weights that add), you get diffusion, which
  `spectral.py` already computes. Diffusion never cancels, so it cannot produce
  "wake interference is vacuum". Cancellation requires *amplitudes*: weights with
  phases that can subtract. In this model the phase along a path would come from
  a representation of the group. The 3-dimensional irrep of A4 is the memo's own W.
  This is standard lattice-gauge transport (Wilson lines).
- **It removes the need for a scheduler.** A light-like entity that takes every
  route does not need an arbitrary "which path" choice. That matches the
  determinism stance: no probability in the kernel.
- **Honest limit.** Why the weights are amplitudes, and why probability then
  goes as |amplitude|², is the Born-rule question the project marks as
  POSTULATED (CLAIMS row 16). This picture motivates the choice; it does not
  derive it.

## 9. Proposed order of work (each step registered before it runs)

**Update:** the integrated picture is now `WORKING_STATEMENT.md`. It adopts
reading 1: the corollary cone is the light cone, confirmed round and sharp on
the mesh by P18.

**Update (P17, done):** `TRAPPING.md` proves that a walk with probability
weights always escapes a region with an exit. The same walk with amplitudes
traps exactly the modes that vanish at the exit (symmetry and degeneracy force
them). On a fractal the remaining leaks slow doubly-exponentially with depth.
Trapping therefore requires amplitudes. The open step below is self-built geometry.

1. **Path-sum propagator (no new postulate beyond amplitudes).** Generalise
   `fringe.py` from two paths to all paths. Propagate an amplitude through the
   complex using representation matrices on the edges. Check path independence
   in vacuum and interference around prepared flux. This tests §8 directly and
   builds the "wake" machinery without committing to a bubble yet.
2. **Framed edges (link-ring pointer).** Implement §6 point 4 as an optional
   layer. First test: does a 2π pointer rotation have an observable effect in the
   path sum (the −1 of spin ½), with the unframed model as the control arm?
3. **Bag test II.** With steps 1–2 available, prepare bubbles of several sizes
   and measure E(R). Pass means a minimum at finite size, with the content
   conserved under all permitted moves.
4. In parallel, and needing no model change: **is H a funnel?** Look for any
   nonvacuum closed plateau of H by random quench plus exact plateau closure.
   A negative strengthens §5; a positive would be the first metastable object
   under the present action.

None of this is a claim that nucleons or electrons have been made. It says what
a bubble would need, and why the present model cannot provide it.
