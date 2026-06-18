# DAR Case 20 Surface Extract

## What We Tried

Extracted raw retained-message surfaces for DAR GSM8K100 sample `20` across
four existing variants.

This was a local CPU-only read of existing history and trace files. No model
call or GPU run was launched.

## Inputs

| Label | History | Trace |
| --- | --- | --- |
| `original` | `experiments/_archive/20260616-pruned/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/dar_history_gsm8k100_filtercritical.jsonl` | `experiments/_archive/20260616-pruned/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar_v11.jsonl` |
| `guarded_answer_only` | `experiments/_archive/20260616-pruned/20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100/dar_history_guarded_answer_diversity_gsm8k100.jsonl` | `experiments/_archive/20260616-pruned/20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100/comm_trace_dar_guarded_v11.jsonl` |
| `answer_only_no_guard` | `experiments/_archive/20260616-pruned/20260613-2143-a8002-dar-retention-split-gsm8k100/dar_history_answer_only_noguard_gsm8k100.jsonl` | `experiments/_archive/20260616-pruned/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_answer_only_noguard_v11.jsonl` |
| `guard_full` | `experiments/_archive/20260616-pruned/20260613-2143-a8002-dar-retention-split-gsm8k100/dar_history_guard_full_gsm8k100.jsonl` | `experiments/_archive/20260616-pruned/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_guard_full_v11.jsonl` |

## Command

```powershell
python scripts\extract_dar_case_surface.py `
  --case-index 20 `
  --history original=experiments\_archive\20260616-pruned\20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory\dar_history_gsm8k100_filtercritical.jsonl `
  --history guarded_answer_only=experiments\_archive\20260616-pruned\20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100\dar_history_guarded_answer_diversity_gsm8k100.jsonl `
  --history answer_only_no_guard=experiments\_archive\20260616-pruned\20260613-2143-a8002-dar-retention-split-gsm8k100\dar_history_answer_only_noguard_gsm8k100.jsonl `
  --history guard_full=experiments\_archive\20260616-pruned\20260613-2143-a8002-dar-retention-split-gsm8k100\dar_history_guard_full_gsm8k100.jsonl `
  --trace original=experiments\_archive\20260616-pruned\20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory\comm_trace_dar_v11.jsonl `
  --trace guarded_answer_only=experiments\_archive\20260616-pruned\20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100\comm_trace_dar_guarded_v11.jsonl `
  --trace answer_only_no_guard=experiments\_archive\20260616-pruned\20260613-2143-a8002-dar-retention-split-gsm8k100\comm_trace_answer_only_noguard_v11.jsonl `
  --trace guard_full=experiments\_archive\20260616-pruned\20260613-2143-a8002-dar-retention-split-gsm8k100\comm_trace_guard_full_v11.jsonl `
  --summary-out experiments\_archive\20260616-pruned\20260614-1253-local-dar-case20-surface-extract\summary.json `
  --messages-out experiments\_archive\20260616-pruned\20260614-1253-local-dar-case20-surface-extract\retained_messages.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Compact per-variant transition, retained IDs, parsed answers, constructed surface lengths, and term snippets from retained full responses. |
| `retained_messages.jsonl` | One row per retained peer with full raw response and the constructed surface passed under the variant's message mode. |

## What Happened

Sample `20` has first-round parsed answers:

| Agent | Parsed answer | Parsed correct |
| --- | ---: | --- |
| Agent1 | `7.0` | true |
| Agent2 | `120.0` | false |
| Agent3 | `700.0` | false |

Variant outcomes:

| Variant | Mode | Retained IDs | Guard added | Round 1 answers | Transition |
| --- | --- | --- | --- | --- | --- |
| `original` | full | Agent2, Agent3 | none | `7.0`, `700.0`, `700.0` | `right_to_wrong` |
| `answer_only_no_guard` | answer-only | Agent2, Agent3 | none | `7.0`, `12.0`, `700.0` | `right_to_wrong` |
| `guarded_answer_only` | answer-only | Agent2, Agent3, Agent1 | Agent1 | `7.0`, `12.0`, `700.0` | `right_to_wrong` |
| `guard_full` | full | Agent2, Agent3, Agent1 | Agent1 | `7.0`, `7.0`, `700.0` | `stable_right` |

The extraction confirms the key surface mismatch:

- In answer-only variants, Agent3 is represented only as `Previous parsed final answer: 700.0`.
- In full-message variants, Agent3's retained response contains correct calculation evidence including `0.30` and `7.00`, even though its final marker is parsed as `700.0`.
- Guarded answer-only makes Agent1's correct parsed answer visible, but still ends wrong; guard-full makes Agent1's full response visible and lets Agent2 switch to `7.0`.

## Caveats

- This is one case, not a rate estimate.
- The script extracts raw surfaces; it does not semantically judge the reasoning.
- `answer_only` construction follows the project DAR patch: retained peer text is replaced with `Previous parsed final answer: <answer>`.
