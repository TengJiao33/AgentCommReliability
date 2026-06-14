# PACT Field-Selection Case Inspection

## What We Tried

After the question-aware extraction probe left `12` stable-wrong cases, I
pulled out the `9` cases where a gold-matching candidate appeared either in the
final action-state event or in earlier/wider public state.

This is a case-contact step over saved traces. No model call or GPU run was
launched.

## Input

| Source | Path |
| --- | --- |
| Question-aware stable-wrong cases | `experiments/20260614-1450-local-pact-question-aware-stable-wrong/cases.jsonl` |
| PACT trace v1.1 | `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl` |

## Command

```powershell
python scripts\extract_pact_field_selection_focus_cases.py `
  --stable-cases experiments\20260614-1450-local-pact-question-aware-stable-wrong\cases.jsonl `
  --trace experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\comm_trace_pact_v11.jsonl `
  --summary-out experiments\20260614-1507-local-pact-field-selection-case-inspection\summary.json `
  --cases-out experiments\20260614-1507-local-pact-field-selection-case-inspection\focus_cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Mechanical counts over the 9 focus cases. |
| `focus_cases.jsonl` | One row per focus case with public turns and matching candidates. |
| `manual_labels.jsonl` | Manual labels for the observed failure surface. |

## What Happened

The `9` focus cases split mechanically into:

| Mechanical bucket | Count | Samples |
| --- | ---: | --- |
| final event has a matching candidate, but question-aware policy missed it | 7 | `1`, `15`, `25`, `28`, `30`, `31`, `40` |
| matching candidate appears only in earlier/wider public state | 2 | `19`, `23` |

Manual inspection gives a more useful split:

| Manual family | Count | Samples |
| --- | ---: | --- |
| final field or anchor selection conflict | 3 | `1`, `15`, `31` |
| answer contract or extractor priority | 4 | `25`, `28`, `30`, `40` |
| earlier state lost or overwritten | 2 | `19`, `23` |

## Things Noticed

The next pressure point is not another broad answer-extraction variant. The
cases point to a narrower question: how PACT decides which public field, entity
anchor, or answer granularity should survive into the final response.

The `final_answer` field is the current question-aware policy source for all
`9` cases, while the matching candidates appear mostly in `environment_state`
and `action_result`. That makes final-field arbitration more central than
surface normalization alone.

## Caveats

- Manual labels cover only `9` cases from one 50-sample PACT smoke.
- Matching-candidate availability is evaluated against gold labels.
- These labels should guide the next contact point, not become a standalone
  claim about PACT.
