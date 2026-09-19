# Working state — 2026-09-18

This checkout is based on `70a36ca` and already contained unfinished referee-round
changes when this session began. Existing changes include the theory-memo moves,
the Round 3 memorandum (file named R2), within-fibre stabilizer enumeration,
disconnected-surface canonicalization, and class-only gluing compatibility.
These are working-tree changes, not a completed audit response.

## Completed in this session

Fixed a defect in the pending disconnected-surface canonicalization: sorting
component states by their measured holonomies identified a configuration with
curvature on the first shell with one having curvature on the second shell.
Vertex gauge transformations cannot exchange labelled shells. Components now
retain their deterministic minimum-vertex order while each is independently
canonicalized under conjugation. The return shape is unchanged.

`test_curvature_cannot_swap_surface_components` failed before the fix; all eight
tests in `tests/test_gauge_canonical.py` passed afterward, including independent
component gauge invariance and the exact 178-class tetrahedron census.

Repaired the README link to the relocated theory memo.

Full-suite verification (including slow tests and renderer tests): **262 passed,
1 skipped, 2 failed** in 228.54 seconds. The two failures are the interaction
claims detailed below. Command: `.venv/Scripts/python.exe -X
pycache_prefix=out/orientation_pycache -m pytest` (on one line). A fresh bytecode
cache avoids copied cache filenames pointing tracebacks at the sibling checkout.
The first run's three renderer-fixture errors were temporary-directory permission
errors; those tests passed on the authorized rerun. One pre-existing invalid-escape
warning remains in `spectral.py`.

## Gluing issue to resolve next

The pending change in `compatible_on_shared_face` replaces raw equality with
per-edge conjugacy-class equality. This fixes independent apex-frame dependence,
but discards correlations between fluxes. It is a coarser compatibility convention
than requiring one common frame alignment for the entire shared-face tuple.
That choice must be stated explicitly before updating absorption claims.

A concrete A4 counterexample, in the library's permutation representation:

```python
e = (0, 1, 2, 3)
x = (e, (0, 2, 3, 1), (1, 2, 0, 3))
y = (e, (0, 2, 3, 1), (0, 3, 1, 2))
shared_edges = [((0, 1), e), ((1, 2), e), ((0, 2), e)]
index = {0: 0, 1: 1, 2: 2}
```

The current predicate returns True. Exhausting all 12 conjugators shows that
the tuples of `face_flux` values are not simultaneously conjugate. A single
apex frame acts on all three fluxes together, not independently on each edge.
Reproduce with `PYTHONPATH=src python examples/critique/gluing_frame_counterexample.py`.
An apex gauge test must transform labels by left multiplication,
`x_i -> nu^-1 x_i`; conjugating each spoke while fixing a curved boundary is
not the apex-only gauge action.

The initial suite run found two existing interaction failures:
`test_full_ensemble_absorption_is_phase_invariant` and
`test_curvature_suppresses_cross_section_x4`. For the latter's fixed object,
the pending class-only predicate counts 12 compatible flat probes and 36 curved
probes, contradicting the documented legacy result 12 versus 3. Do not treat
that legacy result as verified for the changed predicate. README, R_TRACK,
and the phase-locking example still describe the older convention.

## Audit queue

1. Decide and document gluing compatibility (common-frame matching versus an
   explicitly coarser class-only observable), then pin independent apex gauge
   invariance and relational information with tests and recompute channel counts.
2. Finish F1 documentation: the E034 diary explanation still incorrectly denies
   within-fibre merging. The new stabilizer implementation contradicts that prose.
3. Address F3 driver wiring and provenance; fixes in helper functions alone do
   not establish that the default driver uses them.
4. Reproduce F5 orphan-face bookkeeping and reverse Pachner undo failures.
5. Only then start the queued P7 experiment, with predictions and controls for
   both the penalty and the initial configuration.

The referee README currently references E036 and triage item 18, which do not
exist in this checkout. Those references are not evidence that F3–F8 are closed.
Gravity remains parked; no new physics claim was established in this session.
