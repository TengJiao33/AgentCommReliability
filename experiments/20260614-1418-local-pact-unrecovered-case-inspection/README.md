# PACT Unrecovered Case Inspection

## What We Tried

Extracted the six PACT cases that remained most relevant after the stable-wrong
audit:

- five `remaining_wrong_output_signal_not_recovered` cases;
- one `yes_no_polarity_mismatch` case.

Then I manually labeled the failure surface from the saved action-state fields.

No model call or GPU run was launched.

## Input

| Source | Path |
| --- | --- |
| Stable-wrong cases | `experiments/20260614-1402-local-pact-stable-wrong-after-extraction/cases.jsonl` |
| Corrected PACT trace | `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl` |

## Command

```powershell
python scripts\extract_pact_unrecovered_focus_cases.py `
  --stable-cases experiments\20260614-1402-local-pact-stable-wrong-after-extraction\cases.jsonl `
  --trace experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\comm_trace_pact_v11.jsonl `
  --summary-out experiments\20260614-1418-local-pact-unrecovered-case-inspection\summary.json `
  --cases-out experiments\20260614-1418-local-pact-unrecovered-case-inspection\focus_cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Mechanical counts and sample IDs. |
| `focus_cases.jsonl` | The six focus cases with all public action-state turns. |
| `manual_labels.jsonl` | Manual surface labels for the six focus cases. |

## Manual Labels

| Sample | Manual category |
| ---: | --- |
| 13 | semantic polarity or predicate failure |
| 14 | timeframe span contract |
| 21 | entity alias with evidence conflict |
| 24 | answer type priority error |
| 43 | overlong object span |
| 44 | relation-tail entity extraction |

## Caveats

- Manual labels are case-contact notes, not a benchmark metric.
- The labels use only saved PACT outputs and gold answers; no new evidence was
  retrieved.
- Sample 21 is mixed: it has an answer-surface alias problem and an evidence-use
  conflict in the public state.
