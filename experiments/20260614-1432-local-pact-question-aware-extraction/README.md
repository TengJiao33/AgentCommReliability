# PACT Question-Aware Extraction Probe

## What We Tried

Ran a CPU-only question-aware deterministic extraction probe over the corrected
PACT HotpotQA50 trace. The policy uses saved PACT outputs plus question text to
choose answer-type-specific spans, without using gold labels to generate
candidates. Gold is used only for exact-match evaluation.

No model call or GPU run was launched.

## Input

| Source | Path |
| --- | --- |
| Corrected PACT v1.1 trace | `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl` |

## Command

```powershell
python scripts\audit_pact_question_aware_extraction.py `
  --trace experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\comm_trace_pact_v11.jsonl `
  --summary-out experiments\20260614-1432-local-pact-question-aware-extraction\summary.json `
  --cases-out experiments\20260614-1432-local-pact-question-aware-extraction\cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Official, fixed-policy, and question-aware diagnostic exact-match counts. |
| `cases.jsonl` | One row per sample with baseline policy, question-aware policy, transitions, and final action-state fields. |

## What Happened

| Policy | Exact matches |
| --- | ---: |
| official PACT extraction | `17/50` |
| fixed final-answer-only policy | `32/50` |
| question-aware policy | `38/50` |

Compared with the fixed final-answer-only policy:

- additional rescues: `6`
- regressions: `0`

Changed cases:

| Sample | Baseline policy | Question-aware policy |
| ---: | --- | --- |
| 7 | `3677` | `3677 seated` |
| 14 | full sentence | `from 1986 to 2013` |
| 18 | `1969 until 1974` | `1969 until 1974` |
| 21 | `Sonic the Hedgehog` | `Sonic` |
| 24 | `1992` | `World's Best Goalkeeper` |
| 43 | full sentence | `sovereignty` |
| 44 | `Alfred Balk` | `Nelson Rockefeller` |

## Caveats

- This remains a postprocessing diagnostic, not a replacement score.
- Sample `21` is surface-recovered but still has a public-state evidence-use
  conflict from the manual inspection.
- The policy is HotpotQA-shaped and should not be treated as a general answer
  extractor without broader tests.
