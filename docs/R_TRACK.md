# R-TRACK NOTES (kernel/driver refactor — design by Satish + Qwen cloud)

Milestones here are **R1..R5** to avoid collision with the physics spec's M1..M8.
Branch: `bionic/kernel-drivers` (off `main`). Suite at R3: 145 tests.

## Architecture rule (enforced)

KERNEL = complexes, groups, labels, holonomy, gauge/canonicalization, resolutions,
fiber products, protocol scans — **no RNG, no scheduler** (`tests/test_drivers.py::test_kernel_module_has_no_rng`).
DRIVERS implement `DynamicsDriver` (advance / event_ontology / reversible / inverse_advance)
and are swappable. DriverA = stochastic veto (`counterfactual-veto`); DriverB =
deterministic churn on the raw gauge slice (`do-undo-churn`). Randomness lives ONLY in A.

## Findings so far (all measured, deterministic unless noted)

1. **The canonicalization trap is real**: "multiply then re-canonicalize" fails
   equivariance on gauge orbits (`orbit_sigma_well_definedness` asserts it). Kernel rule:
   explore raw slice; canonicalize only for observables. DriverB's sigma verified
   bijective at init (exhaustive).
2. **T3 consistency, first number**: Z₃ flat cone pair — exact meshable fraction 1/9 by
   full phase sweep; DriverA random-glue reproduces 0.1118 ± 6e-4. Same set, two measures.
3. **Full-ensemble absorption is phase-invariant** (A₄: constant across all object
   phases for both flat and curved shared faces). It is an invariant of object+face:
   A₄ flat = 12/1728 compatible probes; **curved = 3/1728 — curvature suppresses the
   cross-section exactly ×4**. Z₃: 0.1111 regardless of curvature — *abelian blindness*.
4. **Prepared-probe absorption IS phase-dependent** (0 ↔ 1/3 gating with a 3-state probe
   family): clock-gating is real physics for individual probes; ensemble averaging hides
   it. This validates the D1 equidistribution warning.
5. **D1 stride scan**: mesh rate depends on gcd(p, L) exactly (same-gcd periods give
   identical rates — coset identity); different-gcd coincidences happen and must never
   be asserted as structure.
6. Protocol semantics implemented over all phase pairs: duty cycle / deferred waits /
   scatter fractions + wait histogram (`phase_locked_outcomes`), deterministic.

## Honest caveats

- "Temperature" in the kick experiment = statistical Metropolis parameter over a chosen
  action, NOT physical T (see kick.py honesty note).
- Odometer sigma is a SCHEDULER choice (single equidistributed cycle); clock spectrum
  depends on it — D1 measures this dependence, don't reify it.
- DriverA declared non-invertible at the map level (counterfactuals discarded), even
  though accepted moves are individually undoable.

## Next (queue)

R4: full D1-D4 report (D2 fringe test = two-path probe around a knot; needs path
holonomy across two routes). R5: Bell-type glued-pair CHSH under both drivers — the
referee experiment. Also pending: RNG migration out of dynamics/persistence/seeds to
widen kernel purity; physics M5-M8 wait on `main`.
