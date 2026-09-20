# Corrections to the rules (2026-09-20, Opus, from the user's restatement + the literature)

**The axiom, as the user restated it:** *causality travels to local effect, and it is always
travelling as a conserved quantity.* And: *a multidimensional causal structure can enumerate
irreducible, self-referential links.*

Read literally, the first sentence is a **per-vertex constraint**, not a cost. Our rules did not
have it. Below: what was wrong, what replaces it, and what is already implemented
(`src/constraintnet/defect.py`, `tests/test_defect.py`).

## C1. Local conservation is a constraint, not a soft cost — **implemented**

- **Was:** an electric term exp(−iλ_E L) that *penalises* record excitation. Nothing forbade
  creation at a vertex.
- **Now:** A_v = (1/|G|) Σ_g A_v^g, the projector onto invariance under a gauge move at v. This
  says exactly "nothing originates at a vertex; what arrives, leaves".
- **Checked:** A_v and B_f are exact projectors, [A_v, B_f] = 0 and [A_v, A_w] = 0 to 0.0
  (machine zero) for Z2, Z3 and A4 patches.

## C2. Constraints must be hard, so the theory has a gap — **implemented**

- **Was:** soft couplings (λ ≈ 0.1) with no gap; everything we built decayed, and P25/P31 measured
  the decay.
- **Now:** H = −Σ_v A_v − Σ_f B_f. Measured on the tetrahedron boundary: unique ground state,
  **gap = 1 per violated constraint** (Z2, Z3: gap 2 in their normalisation; A4 single-face patch:
  gap 1). A defect now costs a fixed amount and cannot be dissipated by rearrangement.

## C3. Matter is a point defect; a loop is flux — **rules corrected, tests pending**

- **Was:** "matter is trapped circulation" (working statement clause 6). P27–P31 killed it: compact
  loops carry no current, do no work on their surroundings, and do not bind.
- **Now:** a **charge** is a vertex where A_v fails — a point defect. A **flux** is a face where
  B_f fails.
- **Checked on our own mesh:** flipping a single edge label disturbs exactly the ring of faces
  around that edge, and for every interior edge that ring is **closed**, of size 6 (axis and body
  diagonals) or 4 (face diagonals). So in three dimensions a flux is a *loop*, never a point, and
  our ring-6/ring-4 structure was the flux-loop structure all along. The "pivot edge" of the v4.1
  work was a flux-loop generator.

## C4. Particles come in pairs, at the ends of strings — **pending**

Ribbon/string operators create two defects, and the state depends only on the endpoints. A closed
loop has no endpoints, which is why every closed-loop candidate we built failed. The "tail" is the
string; the particles are its ends.

## C5. Our action never had a stabilising term (Derrick) — **superseded by C1–C2**

P14–P16's "tension but no pressure" is Derrick's scaling argument. The escapes are a Skyrme-type
term, gauge fields, or time dependence. The constraint route above is the cheap one and is native
to a finite group: a defect is stable because it cannot be removed locally, not because a force
balances.

## C6. "Always travelling" disqualifies our old candidates — **rule clarified**

A compact stationary state carries exactly zero current (P28) and is therefore *not travelling*. By
the axiom as stated, it cannot be matter. A defect can move; a dark loop cannot. This is the axiom
doing work rather than the model.

---

# Next stop but one: more dimensions

**Our foundation is not 3-dimensional.** The Kuhn/Freudenthal subdivision cuts a d-cube into d!
simplices in any dimension; the cell is a d-simplex whose rotation group is **A_{d+1}** (3D → A4, as
we have; 4D → A5), and the spin lift is its double cover (4D → the binary icosahedral group, 120
elements — the largest finite subgroup of SU(2)).

**And there is an argument that three dimensions are special, in exactly the user's terms.** In d
dimensions, gauge flux is codimension-2, i.e. a (d−2)-dimensional object: a loop in 3D, a sheet in
4D. Two closed objects of dimensions p and q can link only when p + q = d − 1. So:

- **flux links flux** ⟺ (d−2) + (d−2) = d − 1 ⟺ **d = 3**;
- charge–flux braiding (a point's worldline, dimension 1, around a flux) needs 1 + (d−2) = d − 1,
  which holds in **every** dimension.

If "irreducible, self-referential links" means flux linking flux, **three dimensions is the only
dimension that supports it**. That is a pre-registered prediction for the higher-dimensional work,
not a result: it follows from standard linking arithmetic, and the test is whether our model's
flux objects behave that way when we actually build d = 4.
