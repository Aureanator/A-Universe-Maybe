# Handoff to Astra (from Opus, 2026-09-20)

Welcome back. This covers everything since your last turn. The detailed logs are:
- `docs/PREDICTIONS.md`: P20–P25, each with its registration, amendments and outcome;
- `docs/RESEARCH_DIARY.md`: entries E047–E051;
- `reference/opus_session/WORKING_STATE_2026-09-19.md`: addenda 1–10.

## 0. How the user works (please keep this)

- **Pre-register** every prediction in `docs/PREDICTIONS.md` before running anything.
  - If the design changes after seeing data, append a dated **AMENDMENT** before running the
    changed part.
  - Outcomes are appended, never edited in.
- **Prefer analytic results checked by computation.**
- **Never delete history;** amend with dates. Label claims AXIOM / POSTULATED / DERIVED /
  MEASURED / OPEN.
- **Relational quantities only.** References exist only between structures (working statement,
  clause 12). Coordinates may prepare states but never define a measurement.
- **Discuss ideas conversationally first;** write them into official docs when the maths checks
  out or the user says "integrate".
- **The user commits git themselves.** The correct folder is "A universe maybe 2 - Copy". The
  non-Copy folder belongs to local Qwen.

> **Superseded handoff:** the project advanced through P31 and P32A after this
> document. Start with `reference/HANDOFF.md` and `docs/DEFECT_AUDIT.md`; the
> historical P25 next steps below are no longer the current work queue.

## 1. Where the physics stands

The picture is `docs/WORKING_STATEMENT.md` (v4):
- implication is the one conserved quantity, always moving;
- matter is trapped circulation;
- mass is the translation rewrite cost (equivalently, maintenance cost);
- decay is escape;
- the world is reversible globally and irreversible locally.

The central open problem is **K, self-confinement.**

| Step | Result |
|---|---|
| P19 | The v4.0 walk (`src/constraintnet/walk.py`) is a sound light engine. Compact loop states (DF) exist. A *frozen* record traps nothing. |
| P20 / v4.1-sc | A rule where circulation writes chop. **Retired:** the user objected that chop cost no energy, which was correct (quasi-energy was not conserved). P20 withdrawn. |
| Options A/B/C | Laid out in `DYNAMICS_DESIGN.md` §9. Conversation conclusions: B (an energy ledger), made reversible, becomes A; the geometric face cost is Wilson, 1 − χ₃/3; purely gauge chop is invisible to light. |
| **P21 (A)** | `src/constraintnet/qrecord.py` `QuantumRecordWalk`: 3 edges carry quantum A4 labels (1728 states), with an electric term (A4 Laplacian on order-3 elements, /8) and a magnetic (Wilson) term. One fixed unitary; the rest of the mesh is frozen flat. Exact to 1e-13. Free light is coherent in a calm quantum vacuum. The DF loop responds to the *dynamic* record far more than to frozen chop. No binding. |
| P22 | Open walls, hot record. A hot dynamic record is **opaque**: light is released as a power law. One flash cannot cool it. |
| **P23** | Radiative cooling, via a quantum-trajectory unravelling (see §3). **Key lesson:** λ_B = 2 is *folded* (one flip costs 12 rad per tick, beyond π, so light heats the record to infinite temperature). Use **unfolded (0.1, 0.1)** for anything thermodynamic. Broad light heats; narrow lowest-band light cools. |
| P24a | Redshift proxy: a bigger box allows a lower band. E*/E_hot = 0.51, 0.22, 0.14 at ω₀ = 0.52, 0.40, 0.33 (n = 5, 6, 7). Magnetic excitations freeze out below their gap; a cooler record is more transparent. |
| **P25** | User's principle: "with enough noise this happened somewhere". Loops are seeded *compatibly* in a cooled (Gibbs, 0.14) bath, one compatible loop form per record branch. Results: no birth shock; exactly permanent if the bath is frozen; erodes at about 2–3e-4 per tick if the bath moves, all from record motion; 90° loops (ring-4) outlast 60° loops (ring-6). The Gibbs-bath provenance check failed (P25-2). |

## 2. Open decisions and next steps (in the user's order)

1. **Dressed loops (my recommended next test).** Look for a joint loop-plus-record eigenstate:
   time-average a compatibly seeded loop in a *closed* box (`mode="closed"`) and keep the
   component with eigenvalue near 1.
   - Measure how much survives and how much of it sits on the loop.
   - That record's statistics *are* the back-calculated bath (the user's provenance condition
     made exact).
   - Register it first.
2. **Expansion rule: the user's call, not yet answered.** Three candidates are in my last
   messages and in `DYNAMICS_DESIGN.md` §12:
   - (i) uniform refinement: an exact redshift of ½, but relationally just a change of units if
     matter refines too;
   - (ii) only calm vacuum grows: matter keeps its size; growth ∝ volume gives exponential
     expansion;
   - (iii) implication creates the new structure: growth follows activity, radiation-driven.

   Then P24b (expansion dynamics), then radiation and expansion together, watching for loops
   forming.
3. **Older pending items:**
   - the B-geometry check (does the walk's own spectrum give the Wilson ratio 4 : 3?);
   - the working statement's open items A (spin-½ lift), B (fermion doubling), L (irregular mesh
     and first-arrival provenance);
   - the M1 = M2 mass test once something persists and moves.

## 3. Code map (new this stretch)

- **`src/constraintnet/qrecord.py`, `QuantumRecordWalk(cx, qedges, lam_E, lam_B, mode="closed"|"open")`.**
  - State layout: `Psi[arc, record_config, 3]`.
  - `step` = `walk_step` then `apply_rec`. `unstep` works in closed mode only.
  - Open mode exposes `self.escaped` after each `walk_step`.
  - Also: `vac` (the eigenvector of U_rec nearest flat), `apply_H` (a *proxy* energy: the Trotter
    generator, not the exact Floquet quasi-energy), `rec_matrix()`.
  - Tests: `tests/test_qrecord.py` (3).
- **`examples/p21_quantum_record.py`**: three geometries × coupling grid, plus quenched controls.
- **`examples/p22_freezeout.py`**: open walls with escape bookkeeping. The record state of
  escaped branches is tracked exactly through its vacuum population.
- **`examples/p23_radiative.py`**:
  - `episode()`: one flash with trajectory unravelling (weighted reservoir sampling of the
    detection event, so the conditional record state is exact in expectation);
  - `ladder*()`: exact per-flash drifts;
  - `lowest_band_filter()`: a Gaussian time-window spectral filter on the flat closed walk;
  - `setup(..., n=)`: centres the loop in a box of size n.
- **`examples/p25_seeded.py`**: `gibbs_bath()`, `df_branches()` (the compatible loop form per
  branch), and the arms V/C/I/Qc.
- **Figures** in `out/` (gitignored): p21, p22, p23_p24a, p25.

## 4. Practical gotchas

- **Runtime.** One tick at 1728 record states in the n = 6 box takes about 0.4 s (buffers are
  reused in `walk_step`). A 600-tick run takes 5–11 minutes; the cloud box has 2 cores. Budget
  accordingly, and run the arms as parallel background processes.
- **Folding.** Keep λ_B·(the largest single-flip Wilson cost, 6 on an axis edge) well under π for
  any thermodynamic reading.
- **E_rec is a proxy.** In quenched arms it can come out slightly negative; the vacuum population
  P_vac is the exact readout.
- **Small boxes cannot hold cold light.** The lowest positive walk phase is 0.52 at n = 5, 0.40
  at n = 6 and 0.33 at n = 7. There is also an exact-zero flat band, which round-off can split, so
  exclude phases below 1e-6.
- **Device bridge.** The desktop shell never mounted the folder. I staged and committed files
  through the bridge with mtime guards. The user may have fixed this since.
- **Test suite.** 355 passed at the last full run. After that, one qrecord test was added and
  the qrecord tests pass (3); the full suite was not rerun.

Good luck, and over to you.

## Astra resumption amendment (2026-09-20)

The user explicitly corrected the commit instruction above: the limitation was
Opus's broken shell, not a preference to commit personally. Astra may commit
verified milestones from this checkout. The earlier instruction is retained as
handoff history and is superseded by this clarification.

The local virtual environment initially lacked SciPy. After installation, all
eight tests in `test_walk.py` and `test_qrecord.py` passed. The `quantum` optional
dependency group and README setup command now declare NumPy and SciPy.

Full handoff suite: **356 passed in 400.03 s** locally. P26 was subsequently
registered before measurement, with four additional passing tests for the
phase-resolved filter, exact-spectrum controls and closed-to-open embedding.
Its two fixed phases and finite windows are a bounded diagnostic, not a complete
eigenstate search. Stationary record marginals do not establish radiative-cooling
provenance; that part of the proposed next-step interpretation remains open.
