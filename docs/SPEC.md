# SPEC — the theory and how it maps to code

The verbatim original specification (basement-to-capstone derivation *and* programming
spec, including the 7 strict tests and 8 milestones) lives in [`../Prompt.txt`](../Prompt.txt).
This document is the condensed map: axiom → structure → module. Nothing here overrides
`Prompt.txt`; it exists so a reader can find the code for each idea quickly.

## The derivation in one screen

| Step | Claim | Where it lives in code |
| --- | --- | --- |
| Basement axiom | Directed implications reduce; nothing else assumed | — (philosophical ground) |
| Events + directed implication | $\mathcal{E}$, $A \to B$ | `complex.py` vertices / oriented edges |
| Reduction → causal order | $A \prec B$ from realized chains | `Edge.realized`, event log in `dynamics.py` |
| Constraint labels from group $G$ | $A_{AB} \in G$ on every edge | `groups.py` (Z₃, A₄; generic interface) |
| Holonomy of a cycle | $\Phi_C = \prod A_{ij}$ | `holonomy.py` (`triangle_holonomy`, `loop_holonomy`) |
| Charge = nontrivial holonomy residue | $Q_C = \Phi_C$ | `region.py` probe-cycle charges (see PHYSICS_NOTES §2) |
| Gauge transform, class is invariant | $A_{AB} \to \lambda_A^{-1} A_{AB} \lambda_B$ | `gauge.py`, tested in `test_gauge_invariance.py` |
| Conservation = legitimacy of a rewrite | $\Phi_{\partial R}^{\text{before}} \sim \Phi_{\partial R}^{\text{after}}$ | `region.Appearance` + `dynamics.Simulation.attempt()` |
| Tetrahedron selects 3D | $\wedge^2 W \cong W$, $d(d-1)/2 = d$ | theory only; A₄ = ∂Δ³ symmetries via `groups.AlternatingGroup4` |
| Matter = persistent fixed point | $F(O) \cong O$ | M4: curvature-cluster persistence, `objects.py` |
| Mass = reconfiguration cost | $m \propto \mathcal{C}(\Delta O)$ | word metric in `groups.py`, `moves.generator_distance`; M5 |
| Hidden internal resolutions | $\mathcal{I}(B)$, $|\mathcal{I}|>1$ ⇔ matter-like | `resolutions.py` (cone over tetrahedron), M3 ✅ |
| Quantum sectors = irreps of centralizer | $H = C_G(q)$, phases $1,\omega,\omega^2$ | `groups.centralizer`, little-group classification in `gauge.py` |
| Born rule from resolution counting | $P(k)=|c_k|^2$ as normalized counts | not yet implemented (post-M6; see CHANGELOG "Planned") |
| Gravity = event density | $\rho(x)$, $n=\rho/\rho_0$, propagation delay | `observer.py` (relational cells), M7 |
| Visualization only | coordinates never drive dynamics | `viz/`; enforced by label-independence tests |

## The 8 milestones and their status

1. **Tetrahedral seed** ✅ — A₄ engine, gauge fixing, 1728 raw → **178** classes (Burnside cross-checked).
2. **Boundary-preserving dynamics** ✅ — generator moves accepted iff watched `Appearance` preserved; canonical transition graph on the 178 physical states (one connected component).
3. **Cone internal resolution** ✅ — $|\mathcal{I}(B)|$ computed exactly; vacuum is the unique light-like interior of a flat boundary; uniform Klein-four flux hides 6 states.
4. **Persistent defect** ✅ — charged defect persists (100 % survival, zero gaps), external signature strictly conserved through 1500 steps; surface moves rejected 1108/1108 (**confinement is exact**), interior moves accepted 392/392; neutral lump correctly classified as virtual fluctuation, not matter.
5. **Motion cost / mass proxy** ⬜ — minimum accepted-rewrite cost to translate (or reconfigure) a defect; see PHYSICS_NOTES §6 for the region-relativity question this must settle.
6. **Interaction** ⬜ — gluing along shared faces, charge conservation on glue, fiber product $\mathcal{I}_1 \times_F \mathcal{I}_2$ (empty ⇒ forbidden).
7. **Observer density / gravity-like delay** ⬜ — quantitative delay vs density near persistent defects.
8. **3D visualization polish** ⬜ — cone demo with flickering hidden interiors, live Pachner moves.

## The 7 strict tests and where they are

| Spec test | Status | Location |
| --- | --- | --- |
| 1 group correctness | ✅ | `tests/test_groups.py` |
| 2 gauge invariance | ✅ | `tests/test_gauge_invariance.py` |
| 3 tetrahedron enumeration (1728 → 178) | ✅ | `tests/test_tetrahedron_enumeration.py`, `examples/milestone1.py` |
| 4 boundary conservation | ✅ | `tests/test_boundary_conservation.py` |
| 5 persistent-defect conservation | ✅ | `tests/test_persistence.py`, `examples/milestone4.py` |
| 6 no coordinate teleportation | partial (layout label-independence) | `tests/test_viz.py`; dedicated test planned |
| 7 interaction conservation | ⬜ M6 | — |
