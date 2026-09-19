# Referee synthesis (external audit, frontier-model panel: Opus + Astra + online-Qwen)

Unified referee report received February 2026: 17 claims across code bugs, tautologies,
axiomatic schisms, missing physics, and epistemics. Kept verbatim as the audit artifact that
shaped this arc; an earlier external pass lives in ../opus_audit/.

**Responses are item-by-item in `docs/CRITIQUE_TRIAGE.md`** (verdicts + evidence links), with
pre-registrations and outcomes in `docs/PREDICTIONS.md`. Headlines: Pachner 2->3 was genuinely
broken at HEAD; proposal dynamics were gauge-variant (fixed via class-closed arm); appearance
basis-dependence confirmed (fixed via canonical raw-holonomy state); density normalization fixed
and found *worse* than claimed (Driver A density is label-blind - gravity claim parked); the
rigid-vs-pooled |I| convention settled with the exact 6->2 reproduced.

## Round 2 file (`synthesized_referee_report_R2.md`) — the Round-3 memorandum

Independent reconstruction of the closed results (all confirmed, including gauge_invariant_state
completeness on the tetrahedron slice: exactly 178) plus findings F1-F8. Dispositions:

- **F1 stands and is fixed**: pointwise stabilizers of symmetric boundaries act INSIDE a fixed
  fibre (flat B: constant lambda_i = mu fixes B pointwise, acts x -> nu^-1 x mu;
  raw 72 -> apex-only 6 -> stabilizer-complete 2). The rigid count survives as an explicit
  apparatus convention; the old justification sentence did not.
- **F2 RETRACTED by online-Qwen** (author of the synthesis): "a bad compression of Opus's table".
  The docstring numbers it accused were correct; F1's prose defect is separate and real.
- F3-F8: Driver A wiring/provenance, gluing gauge-variance, Pachner bookkeeping + reverse
  revert, cavity domain, Driver B equivariance labelling, word-cost/property suite — see diary
  E036 and docs/CRITIQUE_TRIAGE.md item 18.
