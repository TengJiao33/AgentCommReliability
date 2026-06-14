# PACT Question-Aware Stable-Wrong Audit

## What We Tried

Joined the question-aware extraction cases with the earlier fixed-extraction and
evidence-field audits to classify the cases that remain wrong after the
question-aware extraction probe.

No model call or GPU run was launched.

## Input

| Source | Path |
| --- | --- |
| Question-aware extraction cases | `experiments/20260614-1432-local-pact-question-aware-extraction/cases.jsonl` |
| Fixed extraction cases | `experiments/20260614-1345-local-pact-extraction-only-audit/cases.jsonl` |
| Evidence-field cases | `experiments/20260614-1326-local-pact-evidence-field-audit/cases.jsonl` |

## Command

```powershell
python scripts\audit_pact_question_aware_stable_wrong.py `
  --question-aware-cases experiments\20260614-1432-local-pact-question-aware-extraction\cases.jsonl `
  --extraction-cases experiments\20260614-1345-local-pact-extraction-only-audit\cases.jsonl `
  --evidence-cases experiments\20260614-1326-local-pact-evidence-field-audit\cases.jsonl `
  --summary-out experiments\20260614-1450-local-pact-question-aware-stable-wrong\summary.json `
  --cases-out experiments\20260614-1450-local-pact-question-aware-stable-wrong\cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Counts by remaining stable-wrong category and task type. |
| `cases.jsonl` | One row per question-aware stable-wrong case with candidate counts, evidence category, and final event fields. |

## What Happened

There are `12` stable-wrong cases after question-aware extraction:

| Category | Count |
| --- | ---: |
| matching candidate exists in final event, but question-aware policy missed it | 7 |
| matching candidate exists only in earlier/wider public state | 2 |
| strict environment signal exists, but current candidate extractor misses it | 2 |
| semantic polarity or predicate failure | 1 |

By task type:

- bridge: `7`
- comparison: `5`

Notably, the earlier `output_signal_not_recovered` bucket disappears under the
question-aware probe.

## Caveats

- This is postprocessing over saved outputs.
- Matching-candidate categories use gold labels for evaluation, not for
  candidate generation.
- The categories depend on current extraction/evidence heuristics.
