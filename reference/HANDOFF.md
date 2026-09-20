# Current handoff — 2026-09-20, after P32A

Read this before the older session handoffs. The user supplied a newer Opus
discussion describing P28–P31 and the projector defect model. Those files are
present here. The older `opus_session/HANDOFF_TO_ASTRA_2026-09-20.md` stopped at
P25 and is superseded; P27 is also complete and incorporated in `be046af`.

The correct checkout remains **A universe maybe 2 - Copy**. Commits are allowed;
the previous prohibition was Opus's shell bug. Preserve priors and old outcomes.
Register changed/new experiments before running them. Do not spawn agents unless
the user or applicable instructions explicitly request delegation.

## Current results

- `e1daede` preserves Opus's P31, literature/corrections documents, `defect.py`,
  `spin_record.py` and P32A preregistration. P31's campaign is archived, not
  independently rerun in this continuation.
- P32A is complete: `reference/astra_session/data/p32a_defects.json` contains
  48 charge-pair preparations in Z2/Z3 tetrahedron boundaries and an A4 face.
  Only endpoint stars are violated; cost is E_vac+2; contractible flat-vacuum
  paths agree. Unit-modulus character strings move endpoints and annihilate
  adjacent pairs by explicit interventions.
- `src/constraintnet/defect_ops.py` adds matrix-free actions and exact
  exp(-itH) from commuting projector factors. Under H, every defect location
  is frozen. This is not a mobile particle or binding result.
- `docs/DEFECT_AUDIT.md`, working-statement amendment 3, diary E061, claim 54
  and the P32A outcome explain the interpretation and preserve prior wording.

## Corrections that must not be lost

1. Gauge invariance and probability continuity are distinct. The older walk
   already conserved probability locally.
2. H=-sum A-sum B is a finite penalty model. A literal A_v=1 restriction
   excludes its bare charge-defect states; a charge-sector/matter-coupled Gauss
   constraint needs an explicit construction.
3. The implemented commuting H gives no defect motion. Local string unitaries
   can move charges, contrary to the earlier "immovable by local unitary" claim.
   The external interventions are not an isolated system's autonomous dynamics.
4. Weak nonzero couplings do not by themselves mean no spectral gap.
5. Path independence is conditional on flatness/topology, not an operator identity
   on arbitrary states. An identity-label basis vector is not gauge invariant.
6. Do not copy 2D anyon sector counts into 3-torus degeneracy or call the ordinary
   complementary-dimension linking formula a proof of all higher-dimensional
   unlinking. The P32 dimensional proposal needs a separate precise audit.

## Next concrete work

Define/test admissible charge transport with exact conservation and energy
accounting, using the existing edge degrees of freedom where possible. Distinguish
energetic gauge defects from a literal hard Gauss-law physical subspace. Then
search for mobile configurations and interactions under that specified dynamics.
Do not credit frozen projector occupations as emergent self-binding.

P32-3 cannot run until an open-boundary channel exists for this state space.
P32-4 cannot run until old walker/partial-record states have an explicit embedding.
Do not blindly rerun P19–P31 using operators with incompatible state spaces.
Expansion-rule choice remains unresolved; no new rule was selected here.
Williamson–van der Mark remains a reproduction target, not an achieved structure.

Reproduce the new probe using a fresh output filename:

```powershell
.venv/Scripts/python.exe examples/p32_defects.py --output out/p32a_reproduction.json
```

Validation: the complete suite passed **370 tests in 405.02 seconds**, including
the three inherited defect tests and two new state-operation tests. Command:
`.venv/Scripts/python.exe -X pycache_prefix=out/p32_pycache -m pytest --basetemp out/p32_full_20260920`.
Use a fresh temporary directory for another run. No experiment or test process
remains running.
