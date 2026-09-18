# Opus audit scripts — reference material

Scripts Claude Opus ran while auditing `Memo.txt` (the theory review thread), pasted
by Satish on 2025-09-17 and preserved here **verbatim** for reproducibility. They are
NOT part of the constraintnet package: standalone, numpy-only, self-contained A4 code.
Run any with `python reference/opus_audit/<name>.py`.

Interpretation notes below include **corrections** — places where a script's printed
number measures something other than what its comment claims. The corrected facts are
what our docs should cite.

## 1. vertex_reweight.py — signature counts under relabeling

Establishes:
- **82 ordered face-class signatures**, confirmed with the true 6-edge holonomy formula
  in tree gauge (matches our enumeration).
- Pure multiset sorting of the 4-tuples gives **20** — this is what "20 coarse curvature
  signatures" actually counts. It is a SORT, not a group quotient.
- True vertex-relabeling orbit counts: **13 under A4-vertex (orientation-preserving),
  11 under full S4**.

Why they differ (the debug sections): relabeling vertices can invert an edge
(`A_ji = A_ij⁻¹` consistency), and inversion swaps the order-3 chirality classes
(3a ↔ 3b). So a single relabeling orbit spans several sorted tuples — e.g.
`('I','I','3a','3a')` reaches `('3a','I','3b','I')`, different sorts, same orbit.

**Consequence for our docs:** "20" must always be labeled *multiset-sort count*; if a
relabeling quotient is ever claimed, the correct numbers are 13 (A4) / 11 (S4).

## 2. gaugefiber.py — the frozen GIF's component

Establishes: V4-move component from the GIF seed in full 6-edge space = **exactly 4096**.
The clean structure (verified): right multiplication by V keeps each edge inside its
right coset seed_e·V4, and BFS reaches every combination, so the component is exactly
∏ₑ (seed_e · V4) = **4⁶ = 4096**. The tree-gauge slice analogue: 4³ = 64 states
(crosscheck2.py).

**Correction:** the printed "orbit size 768" is an artifact — the loop filters
`if d in comp`, so it measures |gauge orbit ∩ component|, not the orbit. Verified
empirically (2025-09-17): the true vertex-gauge orbit of the GIF seed has size
**20736 = 12⁴** with **trivial stabilizer** — Z(A4) is trivial, so the script's
"mod 1 global redundancy" comment does not apply to non-abelian A4 (diagonal
conjugation acts nontrivially; it only collapses for abelian groups or flat data:
the all-identity labeling has orbit size exactly 1728). The component is 4096, so
gauge images mostly escape it. The constancy of the intersection at 768 across
samples is itself an interesting (unexplained) fact — about the intersection,
not about orbits.

## 3. crosscheck.py — order-2 moves from the identity seed

Establishes: raw BFS with order-2 moves = **64** states (= 4³), confirming the
gauge-fix counting identity.

**Correction:** "22 residual-gauge classes" are intersections of conjugation orbits
with the component (sizes [1, 3×21]), not physical classes — same filter artifact as §2.

## 4. crosscheck2.py — order-2 moves from the ACTUAL GIF seed

Establishes: gauge-fixing the GIF's real seed puts all three slice labels in the
order-2 class; BFS reaches raw **64**; quotienting by true global conjugation gives
**exactly 6 physical classes**, sizes [4,12,12,12,12,12].

So the frozen tetra GIF explored precisely 6 of the 178 physical classes — a clean
quantification of the order-2 fragmentation (cf. move-set-relative reachability:
fixed order-3 generator → 27; all order-3 → 1728; order-2 → 64).

## 5. fermion.py — D(A4) topological spins

Establishes the anyon spectrum of the Drinfeld double D(A4): sectors are pairs
(flux conjugacy class, centralizer irrep), with topological spin
**θ = χ_ρ(g_C)/dim ρ** — a charge's character evaluated on its OWN flux
(self-Aharonov–Bohm; in a relational universe this is the native notion of spin:
there is no ambient space to rotate in).

- Order-2 (V4) flux × characters W2, W3 → **θ = −1**: fermionic TWIST candidates,
  self-dual, arriving as a doublet exchanged by relabeling within V4.
- Order-3 flux × Z3 characters → θ ∈ {1, ω, ω²}: anyonic (±1/3 spin), correctly NOT
  flagged as fermions; complex-conjugate pairs across the two inverse classes.

Full spectrum: **14 sectors** = 4 pure charges (θ=1; the 3-dim irrep is a non-abelian
boson) + 4 V4 dyons + 6 order-3 dyons. Quantum dimensions d = |cl(g)|·dim ρ give
Σd² = (1+1+1+9) + 4·9 + 6·16 = **12 + 36 + 96 = 144 = |A4|²** ✓.

**Caveat carried forward:** θ = −1 fixes the ribbon twist, not exchange statistics.
The R-symbol in the W2×W2 vacuum channel must be checked (−1 ⇒ true fermion) before
claiming fermions — this is Layer-2 brief item 1 territory (full S/T/Verlinde data).
