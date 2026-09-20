# Upgrades available from existing work (2026-09-20, Opus)

> **Audit amendment (Astra, 2026-09-20):** this proposal's original wording is
> preserved below. See [DEFECT_AUDIT.md](DEFECT_AUDIT.md) and P32A for implemented
> status and corrections: finite projectors in H are energetic penalties; a
> positive small coupling need not be gapless; defects can move under local
> strings; path independence is conditional on the intervening flat sector;
> and 2D D(G) sector counts are not automatically 3-torus degeneracies.

Written after reading the closest programmes (see `RELATED_WORK.md`). Each entry is: what they
have, what we have, the concrete change, and how we would know it worked. Status of every proposed
change: **POSTULATED, not yet implemented.**

## 1. Matter is a *constraint defect*, not trapped circulation (Kitaev quantum double)

**Theirs.** Hilbert space: a group element on every edge. Two local operators per site:
- **A_v**, the star operator, projects onto states invariant under gauge transformations at the
  vertex v — the **Gauss law**;
- **B_f**, the plaquette operator, projects onto trivial holonomy around the face f — **flatness**.

H = −Σ_v A_v − Σ_f B_f, whose ground state satisfies both constraints. Excitations are exactly the
violations: a **charge** is a vertex where the Gauss law fails, a **flux** is a face whose holonomy
is non-trivial, a **dyon** is both. The model is **gapped**, and the excitations are topologically
protected: a single defect cannot be removed by any local operation, only annihilated against a
partner.

**Ours.** We have soft analogues of both terms — the electric Laplacian and the Wilson cost — but
- we **never imposed the Gauss law**. Our record's gauge sector is unconstrained, and the walker is
  a charge carrier with nothing tying it to the record.
- our terms are exponentials of small couplings, not projectors, so there is **no gap** and no
  protection; everything we have built decays.
- we looked for matter as *trapped circulation*; the quantum double says the particle **is** the
  defect.

**Change.** Add the vertex constraint explicitly; define charge as its violation; make the
constraint terms strong (projector-like) and measure the gap. Self-binding then stops being
something to find: a constraint violation cannot be undone locally, which is what "bound" means
here.

**Test.** With projector-strength terms, a prepared single defect must (i) cost a fixed energy
independent of where it sits, (ii) be immovable by any local unitary, and (iii) survive open-wall
release, unlike every candidate we have built so far.

## 2. The tail is a string, and the particles are its ends (ribbon operators)

**Theirs.** Excitations are created in pairs by **ribbon operators** along a path; the state depends
only on the *endpoints*, not on the path. The string is unobservable; its ends are the particles.

**Ours.** We built *closed* loops. A closed flux loop has no ends, so it is not a particle — which
is exactly why P28 found no current and P31 found no binding. The "tail" the user asked for is the
string, and we were building the wrong object.

**Change.** Implement ribbon operators on the Kuhn mesh and create pairs.

**Test.** Path-independence: the same endpoints via two different ribbons must give the same state
(to round-off). That is a sharp, cheap check, and our current machinery can do it.

## 3. Derrick's theorem explains P14–P16 (Skyrme / Faddeev)

**Theirs.** Derrick's scaling argument forbids stable static localized solutions in three
dimensions for ordinary scalar actions; the standard escapes are a higher-derivative (Skyrme) term,
gauge fields, or time-periodic solutions (Q-balls). The Faddeev–Niemi knotted solitons exist
precisely because of such a term, with proven energy minimisers.

**Ours.** "Tension but no pressure" (P14–P16) *is* Derrick's argument appearing in our action: every
structure shrinks and nothing pushes back. We never had a stabilising term.

**Change.** Two routes: add a Skyrme-like higher-order term, or take the topological-constraint
route of §1, which is native to a finite group and costs no new action terms. Recommend the second.

**Note.** P28's result that the only compact stationary states are at phase 0 or π, with an exactly
2-periodic superposition, is the lattice echo of the third escape (time dependence).

## 4. Learn from braid matter's failure modes (Bilson-Thompson et al.)

**Theirs.** Braids in spin networks as particles; braids are **noiseless subsystems** — conserved
under the evolution moves — with two conserved invariants (an additive "effective twist", charge-like,
and a multiplicative "effective state"). First-generation identifications, and two interaction
mechanisms in the 4-valent scheme.

**Where they stalled**, and it is our position almost exactly:
- in the trivalent scheme braids were **too stable**: they propagate but cannot interact — our dark
  states have the same problem;
- the 4-valent scheme produced a **zoo** of braids with no superselection rules to pick out the
  physical ones — we likewise have an arbitrary catalogue of loops;
- no mass generation, no generations or mixing.

**Change.** Do not chase particle identifications. Chase **superselection rules and interaction
channels** first. The quantum double supplies exactly the rule they lacked: sectors labelled by
(conjugacy class, irrep of its centraliser).

**Numbers for our groups** (computed here, `examples/` not needed — 6-line script):
- **D(A4): 14 sectors** — classes of size 1, 4, 4, 3 with centraliser irrep counts 4, 3, 3, 4.
- **D(2T): 42 sectors** — classes 1, 1, 6, 4, 4, 4, 4 with centraliser irrep counts 7, 7, 4, 6, 6, 6, 6.

If our model ever lands in the quantum-double phase, those are the numbers of stable species and the
ground-state degeneracy on a 3-torus. They are a falsifiable target, unlike anything we currently
predict.

## Order of work implied

1. Gauss law and projector-strength constraints → gap (§1).
2. Ribbon pair creation and path-independence (§2).
3. Sector counting against 14 / 42 (§4).
4. Only then revisit circulation, mass, and the electron target.
