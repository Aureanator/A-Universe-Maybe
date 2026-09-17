# CONVENTIONS — orders, orientations, indices

Everything here is enforced by code and/or tests; when in doubt, the test wins.
(Referenced from `groups.py`, `holonomy.py`, `complex.py` docstrings.)

## Groups (`groups.py`)

- Elements are plain hashable Python objects: `int` for Zₙ (additive), tuples for
  permutations where `p[i]` is the image of `i`. Equality is `==`.
- **Product order**: `multiply(a, b)` = `a ∘ b`, i.e. `(a*b)(x) = a(b(x))`.
- **Loop products are taken left to right in traversal order**: for loop
  `(v0, v1, ..., vk=v0)`, $Q = A_{v_0 v_1} \cdot A_{v_1 v_2} \cdots A_{v_k v_0}$ with the
  last factor included.
- **Conjugation** is $x \mapsto g^{-1} x g$, matching the gauge law
  $A_{AB} \to \lambda_A^{-1} A_{AB} \lambda_B$.
- **A₄ conjugacy-class index order** (as returned by `conjugacy_classes()`):
  `[identity, order-3 (−), order-3 (+), order-2]`. Class id 0 is always the identity.
  Do not assume textbook ordering anywhere; use `Group.class_name(element)`.
- **Word metric / cost**: `word_length(x)` = minimal number of generators (generators and
  inverses both allowed) with product `x`; `generator_distance(old, new) = word_length(old⁻¹ · new)`.
  This is the primitive that becomes mass. `move_generators()` returns generators **and**
  their inverses — a historical bug returned only inverses and skewed the metric.

## Complex (`complex.py`)

- Each edge is stored **once**, under canonical key `(min(u,v), max(u,v))`. Reading the
  reversed orientation returns the inverse, so $A_{ji} = A_{ij}^{-1}$ holds by construction.
- Canonical orientation of a simplex = vertices sorted ascending.
- Tetrahedron **orientation is explicit state** (`tet_order`), not implied by vertex order;
  `orient_consistently()` propagates orientations combinatorially across shared faces and
  returns the number of flips needed (Kuhn lattices need it).
- Induced-face signs follow the standard alternating convention from the tet's orientation;
  interior faces cancel in pairs inside a region boundary (`Region.boundary_faces_signed`).

## Gauge fixing (`gauge.py`)

- Spanning tree for Δ³: `TETRA_TREE = ((0,1), (1,2), (2,3))` fixed to the identity;
  free labels `A02, A03, A13` → 12³ = 1728 raw gauge-slice configs.
- Residual symmetry after tree fixing = global conjugation by a central element chain;
  quotient orbits give the 178 physical classes. Burnside cross-check: $(12^3 + 3\cdot 4^3 + 8\cdot 3^3)/12 = 178$
  (fixed points of conjugation on $G^3$: identity fixes $12^3$, each order-2 element fixes
  centralizer-size cubed $4^3$, each order-3 element fixes $3^3$).
- **Canonicalize for reporting, never for exploration** (PHYSICS_NOTES §7.1).

## Dynamics (`dynamics.py`, `region.py`)

- A move is accepted iff `Appearance` of every watched region (main + probes) is unchanged.
  `Appearance.signature()` is the superselection sector id — nested tuples only, hashable.
- Rejected moves are reverted exactly; costs are charged only for accepted moves.

## Observer (`observer.py`)

- Cells are **relational**: graph-distance shells around a chosen root vertex, never
  Euclidean grid boxes. `rho0 = total_events / n_cells` (uniform expectation); the earlier
  "emptiest active cell" baseline was degenerate early in runs and hid all delay.

## Visualization (`viz/`)

- Coordinates come from layout algorithms or the decorative `grid=` metadata; **no dynamics
  module may read them**. Frame-snapshot protocol decouples drivers from rendering; the
  GIF-recording path is identical to the interactive path (headless CI runs it).
