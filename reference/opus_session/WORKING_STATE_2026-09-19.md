# Working state — Opus turn, 2026-09-19

Handoff for the next turn (Astra / GPT). Written by Claude (Opus) in Cowork.

## Environment note

The desktop shell could not mount this folder: a Windows update blocks the VM
share. So I staged `src/`, `tests/`, `examples/`, `docs/`, `reference/` and the root
files into a Linux cloud checkout, worked there, and copied back only the files listed
below. `.git`, `.venv` and `out/` other than the new figure were NOT touched.
**Nothing was committed to git.** Please review, then commit on your side. Baseline
before my changes: 316 passed on Linux (Python 3.11), no skips, no failures.

## What I did

1. **P14 (your run) reproduced and recorded.** A fresh rerun of
   `topology_decay_order.py` matches the archived JSON semantically; only the "source"
   path separator differs, and I restored the archived file. I appended the outcome to
   PREDICTIONS P14 and added diary E040, TOPOLOGY_AUDIT §P14, CLAIMS row 32, and a
   replay test.
2. **P15, registered before building the fixture:** non-commuting linked fluxes in
   full A4. See PREDICTIONS P15, which includes a declared tie-order amendment:
   4 edges pass exactly through the disk-intersection line.
   - DERIVED + MEASURED: pi_1(Hopf complement) = Z^2 forces commuting meridians.
     Non-commuting arms (N1, N2) therefore come out as ONE junction, loops plus a
     5-face V4 tether (H=103; 6 faces and H=104 under the opposite tie). The
     commuting arms (C0 = exact P13 labels, C1 = distinct V4) give two loops with
     |Lk|=1. This is the first place where Z3 and A4 necessarily differ in topology.
   - MEASURED: greedy ordering of the per-edge set-to-identity moves gives a
     fully nonincreasing erasure to vacuum in all 6 runs. The tether and the
     linking vanish on the same move (step 52 -> two loops, Lk=0, non-commuting
     meridians). One-edge census: no single move removes the tether. Plateau
     searches at 32 and 256 states are inconclusive cutoffs.
   - Files: `examples/noncommuting_link_audit.py`, `examples/noncommuting_link_graphics.py`,
     `reference/opus_session/data/noncommuting_link_audit.json`,
     `out/p15_noncommuting_links.png`, `tests/test_link_order_and_noncommuting.py`
     (9 tests, 5 marked slow), diary E041, CLAIMS 33–34, TOPOLOGY_AUDIT §P15.
3. Doc pointers were updated in README, PARTICLE_PROGRAM, ELECTRON_TARGET and CHANGELOG.

## My read of where the program stands (opinion, for discussion)

P8–P15 all point one way. Under H (a uniform tension on curved faces, every
interior move allowed, identity boundary), every structure tried has a
zero-barrier route to vacuum: clusters, glassy endpoints, abelian links, and
tethered non-abelian links. Tension resolves every entanglement tried so far.
If that is general, then **no particle can exist under H in a flat-bounded ball**,
and the particle program needs a declared model change rather than a better fixture.
So I suggest settling the general question first:

- **Next experiment A (decisive, no model change): does H have ANY nonvacuum
  local minimum or closed plateau?** Quench from random labels to a
  nonincreasing-stuck state (n=3,4; Z3, A4). Then exhaust each stuck plateau
  exactly and state whether it is closed. One genuine closed nonvacuum plateau
  would be the first metastable object. A clean negative across a registered
  ensemble would support the "H is a funnel" conjecture, and PARTICLE_PROGRAM
  should then say plainly that matter needs something beyond H. Please
  pre-register it. It is the natural sequel to P8 (tetrahedron exhaustive: funnel).
- **Declared-model options, if A is negative.** Each needs its own registration
  and its own control arm:
  1. Gauss-law point charges. In the 3+1D quantum double D(A4), the POINT particles
     are the charges (irreps of A4), which sit at vertices where gauge invariance fails.
     Flux excitations are loops. Classical edge labels carry no such charges, so the
     model currently has no point-particle sector at all. That sector would need
     vertex variables or a quantum state space.
  2. ~~Twisted Dijkgraaf–Witten cocycle from H^3(A4,U(1)) as the route to point
     fermions~~ **CORRECTED (same day):** H³ is the 2+1D twist. The 3+1D twist is
     H⁴ and, as far as we know, leaves point charges bosonic. Point fermions in 3D
     need a gauge theory with fermionic charges, plus a quantum layer. See
     `docs/BAG_PICTURE.md` §7.
  3. Anchored or non-contractible flux: boundary-to-boundary flux lines, or a
     non-simply-connected space. These are protected exactly, but the protection
     comes from the setup rather than emerging, and they must be labelled so.
- Keep the Williamson–van der Mark gates as they are. Under H, W3 cannot be
  passed by any flux-loop fixture tested so far.

## Open items I did not do

- No git commit; please review the diff and commit.
- `out/` figures from earlier runs were not regenerated.
- The P15 graphic hides C0 under C1 where their paths coincide. The legend says so implicitly.

## Addendum (later the same day): P16 bag test and the bag picture

The user proposed a picture: vacuum is the cancelling interference of implication
"wakes", and a particle is a pressurised bubble in it. I registered and ran P16,
the cheap test of whether the current model has any bubble pressure. It has none.
Flat interiors have one physical filling; the smallest excitations have uniform,
volume-scaling entropy; claim 30 rules out conserved interior content. So there is
tension without pressure, which explains P8–P15.

`docs/BAG_PICTURE.md` holds the why/how, the job specification for any cone/wake
extension, and a proposed order of work:
1. path-sum propagator
2. framed edges via the link ring
3. bag test II
4. the "is H a funnel?" quench, in parallel

The suite passed after these additions.

## Addendum 2: P17 trapping (amplitudes vs probabilities)

Arising from the discussion with the user (ergodic/fractal routes, "wake
cancellation"). I derived six statements first (`docs/TRAPPING.md`) and then
verified them numerically:
- same Laplacian generator for both walks; only the factor i differs
- probabilities escape on every connected graph (T1)
- amplitudes keep exactly ||P_D psi||^2 (T3), with D the modes vanishing at the exit
- symmetry and degeneracy force D to be nonzero (T4/T5)

**Exact dim D:** modular Krylov rank over three primes, cross-checked with 400-digit Lanczos.

**Controls:**
- explicit lead: a real chain in place of the leak term
- integer symmetry breaking: 98 -> 0 dark states

**Observed, not proven (Sierpinski gasket):**
- non-dark dimension 3·2^(k-1)+1 (levels 1–6)
- slowest non-dark leak falls doubly-exponentially: 5.7e-4, 6.4e-8, 8.4e-16, 1.5e-31 (levels 3–6)

**Scope:** supplied geometries only. The open problem is whether the model's
record can build a trap around its own implication (self-confinement).

A combined conceptual statement (v3: one conserved quantity, implication, always
in motion; mass = trapped circulation; decay = escape) was drafted in
conversation. The user has asked that it be checked mathematically before it is
written down officially. So it is NOT in the docs yet, apart from what P16/P17
measured.

## Addendum 3: working statement integrated; P18 light fronts

The user chose "reading 1": influence spreads isotropically on the light cone,
and wake = wavefront for massless motion. They asked to integrate it and
proceed. The integrated picture is `docs/WORKING_STATEMENT.md` (v4, status per
clause, plus the open maths list).

P18 was derived first (`docs/PROPAGATION.md`), then measured:
- **Emergent metric is BCC.** The Kuhn mesh's star is exactly the BCC
  tetrahedral star in the emergent metric. Edge classes go by ring size 6/4;
  ring-4 weight ½ gives quartic isotropy.
- **Fronts.** 3D fronts are sharp; the 2D control has a tail; mass makes a wake.
- **Real waves trap too.** Damped real waves keep exactly the dark energy, so
  P17 trapping needs signed waves, not complex numbers.

One wording error in D1 (plane-wave versus ray speed) was amended with a note.

**Next candidates:**
1. A: orientation transport on edges. The link ring is now doubly meaningful:
   it is the corollary ring and the isotropy weight.
2. C: a relativistic (Dirac-type) amplitude walk on the BCC-equivalent mesh.
   Note that P17's e^{-iLt} has no light cone.
3. K: self-confinement.

## Addendum 4: framing reconciled and the v4 dynamics designed (P19 registered, not run)

**New user positions:**
- References exist only between structures; this is foundational and now
  clause 12.
- Mass = translation rewrite cost = maintenance cost versus free passage.

**Old framing reconciled.** "Defects are matter" is superseded; "rewrite cost
is mass" is kept in the precise form above. History is kept, and the old
engine is the control arm.

**Design.** `docs/DYNAMICS_DESIGN.md` specifies v4.0: a gauge-covariant
Szegedy walk on arcs with the A4 3-dim irrep, ring weights 1 : ½, fixed labels.
Design checks pass (`examples/v4_design_checks.py`).

**Next step:** implement and run P19a–e in order. P19e (does a prepared flux
record trap implication?) decides whether v4.1, dynamical labels, is needed
next.

**Git.** Still nothing committed. The user is trying to fix the desktop shell;
Astra is unavailable due to usage limits.

## Addendum 5: P19 run

**Passes.** The v4.0 engine `src/constraintnet/walk.py` passes P19a–d:
- exact identities;
- Szegedy dispersion, speed sqrt(2/11);
- light cone round to 0.3% (120³ torus), no superluminal modes;
- non-abelian holonomy ½(1 + χ₃/3) exact.

**Registration error.** P19d's "contrast" clause was mis-registered; this is
noted in the outcome.

**Negative.** P19e: frozen flux records trap nothing beyond vacuum cycle states
(DF).

**Next.** v4.1 design: how implication changes labels. This needs the user's
answer on whether labels are separate from implications. The user committed
this session's work in git (branch bionic/kernel-drivers, copy folder); the
P19 files come after that commit.

## Addendum 6: v4.1-sc built and retired

- **Built:** `RecordWalk` (circulation writes quantised chop), exactly reversible.
- **Retired:** the user objected that chop costs no energy, which is correct:
  quasi-energy is not conserved. P20 was withdrawn with no valid result.
- **Next:** the user picks A, B or C for the energy-accounted record
  (`DYNAMICS_DESIGN.md` §9); then P20 is re-registered.

## Addendum 7: option A at small scale (P21)

- **The user chose to try A directly,** in a lossless box. Conversation conclusions behind the
  choice:
  - B, done reversibly, becomes A;
  - the geometric face cost is Wilson, 1 − χ₃/3;
  - chop that is purely gauge is invisible to light.
- **Built:** `QuantumRecordWalk`, 3 quantum edges, exact. **Run:** P21 (40 runs).
- **Results:**
  - accounting exact;
  - free light is fine in a weakly fluctuating vacuum and heats a strongly fluctuating one;
  - the DF loop responds (dynamic ≫ quenched) with a coherent beat, and stays in place at
    moderate coupling;
  - the vortex is not bound.
- **Next options:**
  - (i) make the full loop quantum (4 edges, n = 5) and look for dressed loop eigenstates;
  - (ii) the B-geometry check (the Wilson ratio 4 : 3 from the walk's own spectrum);
  - (iii) scale the record region.

## Addendum 8: freeze-out (P22, 2026-09-20)

- **User's idea:** the early vacuum was not calm. In conversation it lines up qualitatively with
  cosmology (formation by cooling, then decoupling).
- **Test:** P22 (open walls, hot record, one flash).
- **Result:**
  - a hot dynamic record is opaque (power-law release, 30–100× the frozen-chop control);
  - no cooling, because the record's energy dwarfs the light's;
  - retained light ∝ hot fraction, with no threshold;
  - no formation seen.
- **Next options:**
  - a radiation-dominated start (many flashes, or light energy ≫ record energy), then watch
    for loops appearing as the record cools;
  - the full-quantum loop and dressed states (from addendum 7);
  - the B-geometry check;
  - a new open item: expansion or growth of the mesh as the cooling channel (axiom-level).

## Addendum 9: radiative cooling and the redshift proxy (P23, P24a; 2026-09-20)

- **The user's order:** radiative, then expanding, then both.
- **Found:**
  - λ_B = 2 is folded, so use (0.1, 0.1) for thermodynamics;
  - broad light heats the record to near infinite temperature;
  - narrow lowest-band light cools it;
  - E* falls with the light's phase (a bigger box stands in for redshift);
  - a cooler record is more transparent.
- **Stopped:** the P23b trajectories at λ_B = 2 (folded, so uninformative).
- **Pending:** the expansion rule (the user's call), then P24b (expansion dynamics), then both
  together.

## Addendum 10: seeded patterns in a compatible bath (P25, 2026-09-20)

- **User's principle:** seed patterns compatibly ("with enough noise this happened somewhere");
  persistence is a separate question.
- **Result:**
  - no birth shock;
  - a frozen bath keeps the pattern exactly;
  - a moving bath erodes it at about 2–3e-4 per tick;
  - 90° loops beat 60° loops;
  - the Gibbs provenance check failed.
- **Next:** dressed loops, i.e. joint eigenstates of loop plus record. Get them by time-averaging
  a compatible seed in a closed box.
- **Still pending:** the expansion rule (the user's call).
