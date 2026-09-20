# Astra working state — 2026-09-20

## Handoff recovered and preserved

Read `reference/opus_session/HANDOFF_TO_ASTRA_2026-09-20.md` and the associated
P19–P25 code, predictions and outcomes. User explicitly corrected the no-commit
instruction: it was Opus's shell bug, not a user preference. Verified milestones
may be committed here. This remains the correct Copy checkout.

`29a2f51` preserves Opus's pending P19–P25 work, figures and data, plus the new
P26 preregistration and executable. SciPy was missing locally; installed 1.18.1
(NumPy 2.5.3, Python 3.13). `pyproject.toml` now declares `[quantum]`, and README
setup includes it. Full inherited suite: 356 passed in 400.03 seconds. Four new
tests passed separately. A fresh pycache prefix avoids inherited checkout paths.

## P26 completed

Code: `examples/p26_dressed.py`, `src/constraintnet/phase_filter.py`.
Data: `reference/astra_session/data/p26_dressed_n5.json`, `p26_dressed_n6.json`.
Summary: `p26_summary.json`; generator `examples/p26_summary.py` also writes
`out/p26_dressed.png`. Both runs completed, without changing the preregistered
protocol. BLAS/OMP thread counts were set to 2. Commands:

```powershell
$env:OPENBLAS_NUM_THREADS='2'
$env:OMP_NUM_THREADS='2'
.venv/Scripts/python.exe -X pycache_prefix=out/handoff_20260920_pycache examples/p26_dressed.py --n 5 --output reference/astra_session/data/p26_dressed_n5.json
.venv/Scripts/python.exe -X pycache_prefix=out/handoff_20260920_pycache examples/p26_dressed.py --n 6 --output reference/astra_session/data/p26_dressed_n6.json
.venv/Scripts/python.exe examples/p26_summary.py
```

The experiment refuses to overwrite an existing output; use a new path to
reproduce it. Only observables are archived, not the large final state arrays.

- All four diagnostic priors pass. Vacuum-phase filter weight ~0.59; normalized
  loop weight 0.996826/0.980437 for n5/n6. Target residual 0.005642/0.005674,
  versus raw 0.313833. The exact-eigenstate gate at 1e-8 fails.
- After 128 open ticks the filtered loop loses 0.021063/0.010868, versus raw
  0.067114/0.046241. Accounting error <=4.14e-14.
- Unphased filtering retains only about 0.00012 and misses the useful component.
- Record vacuum population becomes 0.994562/0.977631. Do not call the improvement
  self-binding: it may largely select a calmer component of the seed, and the
  decoupled flat-walk dark loop is already exactly persistent.
- Exact full-U checks, boundary dependence and open release are essential.
  Stationary record statistics under coupled U do not establish cooling provenance.

Outcomes are appended to PREDICTIONS; diary E052; claim 46; design section 14.
No new microscopic or expansion rule was introduced.

## Next useful work

1. Preregister an unfiltered vacuum-seed comparison before attributing the
   improvement to joint dressing rather than selecting the calm component.
   Compare compatible-vacuum and imprinted-vacuum states against the filter,
   retaining full-U residuals and open release.
2. Refine the phase/eigenstate search if warranted. P26 only samples two phases
   and finite windows; it neither proves an eigenstate nor excludes others.
   A compression to the loop needs an independent full-space residual check.
3. Define and measure operational directed current and transported orientation.
   A dark loop's support is not proof of circulation, double traversal or spin.
   The Williamson–van der Mark target remains explicitly unreproduced.
4. User's expansion-rule choice is still unresolved; do not silently choose it.
   Three pinned quantum edges and frozen surroundings are still a severe limit.

No experiment or test process remains running after completion of this work.
