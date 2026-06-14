# PACT Final-Answer Surface Audit

## What We Tried

Ran a postprocessing-only audit over the PACT HotpotQA50 schema v1.1 trace to
separate strict EM failures that look like answer-surface or extraction failures
from failures without a simple surface signal.

No model call or GPU run was launched.

## Input

| Source | Path |
| --- | --- |
| PACT v1.1 trace | `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl` |

## Command

```powershell
python scripts\audit_pact_final_answer_surface.py `
  --trace experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\comm_trace_pact_v11.jsonl `
  --summary-out experiments\20260614-1314-local-pact-final-answer-surface-audit\summary.json `
  --cases-out experiments\20260614-1314-local-pact-final-answer-surface-audit\cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Counts by official EM, surface category, task type, and weak gold-containment diagnostics. |
| `cases.jsonl` | One row per PACT sample with final-answer/action-result fields and audit labels. |

## What Happened

Official EM remains `17/50` (`0.34`). The audit does not change the official
score.

Among the 33 official wrong-EM cases, 18 have a simple final-answer surface
candidate:

| Category | Count |
| --- | ---: |
| correct official EM | 17 |
| wrong yes/no answer begins with correct yes/no | 7 |
| wrong non-yes/no final answer begins with normalized gold | 8 |
| wrong numeric answer contains normalized gold number | 2 |
| wrong action-result field begins with normalized gold | 1 |
| wrong with no simple surface signal | 15 |

Other diagnostics:

- wrong final-answer field contains normalized gold: 22
- wrong action-result field contains normalized gold: 15
- wrong cases by type: `bridge=20`, `comparison=13`

## Caveats

- Surface candidates are postprocessing-only diagnostics, not alternate official scores.
- Prefix/contains checks can over-credit cases where the evidence state is still incomplete or wrong.
- This audit does not judge whether PACT's intermediate evidence transfer was correct.
