# PACT Stable-Wrong After Extraction Audit

## What We Tried

Ran a CPU-only follow-up over the PACT extraction-only audit. The audit looks
only at official-wrong cases that remain wrong under the fixed final-answer
extraction policy, then joins them with the evidence-field audit.

No model call or GPU run was launched.

## Input

| Source | Path |
| --- | --- |
| Extraction-only cases | `experiments/20260614-1345-local-pact-extraction-only-audit/cases.jsonl` |
| Evidence-field cases | `experiments/20260614-1326-local-pact-evidence-field-audit/cases.jsonl` |

## Command

```powershell
python scripts\audit_pact_stable_wrong_after_extraction.py `
  --extraction-cases experiments\20260614-1345-local-pact-extraction-only-audit\cases.jsonl `
  --evidence-cases experiments\20260614-1326-local-pact-evidence-field-audit\cases.jsonl `
  --summary-out experiments\20260614-1402-local-pact-stable-wrong-after-extraction\summary.json `
  --cases-out experiments\20260614-1402-local-pact-stable-wrong-after-extraction\cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Counts by stable-wrong category and task type. |
| `cases.jsonl` | One row per stable-wrong case with policy candidate, evidence category, matching candidates, and final event fields. |

## What Happened

There are `18` stable-wrong cases after fixed final-answer extraction:

| Stable-wrong category | Count |
| --- | ---: |
| final event has a matching candidate, but the final-answer-only policy missed it | 7 |
| matching candidate appears only in earlier/wider public state | 2 |
| strict environment signal exists, but the simple candidate extractor missed it | 3 |
| yes/no polarity mismatch | 1 |
| wrong output signal not recovered by current extractor | 5 |

By task type:

- bridge: `13`
- comparison: `5`

## Caveats

- These are postprocessing diagnostics over saved outputs.
- The categories depend on the current extraction and evidence-field heuristics.
- `final_event_candidate_available_policy_missed` often means the candidate is
  in final `Environment State` or `Action Result`, not necessarily in the final
  answer text.
