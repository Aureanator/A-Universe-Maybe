# PHYSICS NOTES — what we verified, and where the bodies are buried

Findings that changed the design. Each was *measured or derived*, not asserted; the
referenced tests are the authoritative record. Conventions (orders, orientations, class
indices) live in [CONVENTIONS.md](CONVENTIONS.md).

## 1. Notation

$G$ finite group (A₄ primary, Z₃ control). Labels $A_{ij} \in G$ on oriented edges with
$A_{ji} = A_{ij}^{-1}$. Face curvature $\Phi_{ijk} = A_{ij} A_{jk} A_{ki}$. Cycle charge
$Q_C$ = ordered product around a closed loop, read left-to-right in traversal order.

## 2. Charge cannot be surface flux — it lives on cycles

The spec's `boundaryHolonomy(region)` reads like a surface integral. It cannot be a
charge: for $\Phi = dA$ and abelian $G$, the signed sum of face curvatures over **any
closed surface is identically zero** — every edge of a closed surface lies in exactly two
faces with opposite induced orientations, so all labels cancel:

    Phi_[123] - Phi_[023] + Phi_[013] - Phi_[012] == 0   for every labelling.

(`tests/test_bianchi.py`; this is $d^2 = 0$ read additively.) Curvature here is
"magnetic": no monopole flux. The usable Gauss law is the **open-disk** one — flux
through a disk equals the holonomy of its boundary loop (up to an inversion from the
orientation convention; see `test_bianchi.py` for the exact statement). Hence charge =
holonomy conjugacy class of *cycles*, and `region.Appearance` records exactly those:
per-boundary-face curvature classes + probe-cycle charge classes.

## 3. Non-abelian Bianchi does NOT hold naively

For A₄, transporting each face curvature to a common basepoint and taking an ordered
product around the tetrahedron surface is **not** identically the identity (checked
empirically). `holonomy.bianchi_defect()` therefore raises `TypeError` for non-abelian
groups rather than returning a framing-dependent number. A correct non-abelian Bianchi
needs 2-group/framing data we deliberately do not invent.

## 4. ∂Δ³ has zero internal dynamics under conservation

Every edge of the bare tetrahedral boundary is externally observed, so from the vacuum
**0 moves are accepted**: any relabelling changes some observed face's curvature class.
This is a result, not a bug — it is exactly why the spec escalates to cones and lattices:
dynamics needs interior edges that no outside observer can see directly.

## 5. Hidden interiors (cone $v * \partial\Delta^3$, M3)

- Flat boundary + no flux ⇒ $|\mathcal{I}| = 1$ (raw count exactly $|G| = 12$, all gauge copies).
- Curved boundary + flat-interior requirement ⇒ $|\mathcal{I}| = 0$: one interior vertex cannot
  cap arbitrary curvature. Curvature cannot be hidden by a single vertex.
- Uniform Klein-four flux ⇒ raw 72, $|\mathcal{I}| = 6$; representative: the three nontrivial
  V₄ elements on apex edges.
- Flux census (flat B): 103 realisable patterns of 4096; $|\mathcal{I}| \in \{1,3,4,6,12,16,24,36,48\}$.
  **The vacuum is the unique light-like interior**; everything else hides ≥ 3 states.
- Z₃ control: all 27 patterns give $|\mathcal{I}| = 1$ — hidden internal ambiguity requires
  non-abelian-ness. Matter needs A₄ (or another non-abelian group).
- Chirality: uniform order-3 flux is *unrealisable* (three equal order-3 curvatures do not
  close around a triangle) while uniform Klein-four is. Not every "charge distribution" exists.

## 6. Legitimacy is region-relative — OPEN QUESTION

"A rewrite is physical iff it preserves the appearance of the watched region $R$" makes
"what counts as outside" part of the setup. Two readings:

- **Feature**: observers are physical; a probe region *is* an apparatus, and charge is
  always measured relative to one (charge at infinity). In a closed universe with no
  boundary, `Appearance` of the whole complex is empty — conservation must come from
  internal probe regions or there is no constraint at all.
- **Bug-ish**: the mass proxy of M5 then depends on the chosen enclosing region; costs
  become finite-size dependent and must be reported as a function of $R$.

Current stance: feature, with region size always reported alongside any cost. This was
flagged in-session and **not yet settled by the user**; M5 must state its choice explicitly.

## 7. Counting traps (each one cost real debugging time)

1. **Canonicalize for reporting, never for exploration.** Right-multiplication does not
   commute with conjugation; exploring from canonical orbit representatives *loses
   transitions* — we found 174 orbits instead of 178, missing exactly the four pure
   Klein-four configs whose only incoming edges come from non-canonical neighbours. Fix:
   explore raw gauge-slice configs, project to orbits afterwards (`tests/test_states.py`).
2. **Re-gauge-fix after every move** before recording a state id, else counts inflate by
   up to $|G|$ gauge copies.
3. **A₄ conjugacy-class indices are `[identity, order-3(−), order-3(+), order-2]`**, not the
   textbook listing order. Never hand-write class-name lists; derive them via `Group.class_name`.

## 8. Verified numbers (as of v0.3.0)

| Result | Value |
| --- | --- |
| A₄ elements / classes | 12; sizes 1, 3, 4, 4 |
| Gauge-fixed d(Δ³): raw → classes | **1728 → 178**; Burnside $(12^3 + 3\cdot 4^3 + 8\cdot 3^3)/12 = 178$ |
| Physical state graph | 178 states, one connected component |
| Little groups of the 178 | trivial ×130, Z₃ ×26, V₄ ×21, A₄ ×1 (only the vacuum is fully symmetric) |
| Cone $v*\partial\Delta^3$ | V=5, E=10, F=10, T=4, χ=1 |
| Conservation filter acceptance | ~36% on ∂Δ³ from random state; ~21% on 48-tet Kuhn ball; interior moves 100%, boundary moves generically rejected |
| Tests | 114 passing (~19 s) |
