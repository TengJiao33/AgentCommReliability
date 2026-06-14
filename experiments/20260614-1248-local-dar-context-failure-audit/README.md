# DAR Context Failure Audit

## What We Tried

Audited existing DAR schema v1.1 traces to connect answer transitions with derived
recipient-context structure.

This was a local CPU-only analysis. No model call or GPU run was launched.

## Inputs

| Label | Trace |
| --- | --- |
| `original` | `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar_v11.jsonl` |
| `answer_only_no_guard` | `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_answer_only_noguard_v11.jsonl` |
| `guarded_answer_only` | `experiments/20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100/comm_trace_dar_guarded_v11.jsonl` |
| `guard_full` | `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_guard_full_v11.jsonl` |

## Command

```powershell
python scripts\audit_dar_context_failures.py `
  --trace original=experiments\20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory\comm_trace_dar_v11.jsonl `
  --trace answer_only_no_guard=experiments\20260613-2143-a8002-dar-retention-split-gsm8k100\comm_trace_answer_only_noguard_v11.jsonl `
  --trace guarded_answer_only=experiments\20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100\comm_trace_dar_guarded_v11.jsonl `
  --trace guard_full=experiments\20260613-2143-a8002-dar-retention-split-gsm8k100\comm_trace_guard_full_v11.jsonl `
  --baseline-label original `
  --summary-out experiments\20260614-1248-local-dar-context-failure-audit\summary.json `
  --cases-out experiments\20260614-1248-local-dar-context-failure-audit\cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Aggregate and per-trace counts by transition, public state, visible-correct count, suppressed-correct count, and failure-mode label. |
| `cases.jsonl` | Transition cases and paired final-correct changes against the original DAR trace. |

## What Happened

The audit covers 400 DAR records: four traces over the same GSM8K100 slice.

| Trace | Final accuracy | Transitions | right-to-wrong cases | wrong-to-right cases |
| --- | ---: | --- | --- | --- |
| `original` | 0.93 | `right_to_wrong=3`, `stable_right=92`, `stable_wrong=4`, `wrong_to_right=1` | `5`, `20`, `22` | `37` |
| `answer_only_no_guard` | 0.95 | `right_to_wrong=1`, `stable_right=94`, `stable_wrong=4`, `wrong_to_right=1` | `20` | `37` |
| `guarded_answer_only` | 0.95 | `right_to_wrong=1`, `stable_right=94`, `stable_wrong=4`, `wrong_to_right=1` | `20` | `37` |
| `guard_full` | 0.96 | `stable_right=95`, `stable_wrong=4`, `wrong_to_right=1` | none | `37` |

Original DAR right-to-wrong cases split into two surfaces:

| Case | Original surface | Context audit label | What it means |
| ---: | --- | --- | --- |
| `5` | retained full reasoning | `correct_context_retained_but_lost_after_update` | Two correct first-round agents were visible, but round 1 still produced wrong or unparseable answers. |
| `20` | retained full reasoning | `selection_dropped_all_correct` | The only correct first-round answer was suppressed. |
| `22` | retained full reasoning | `selection_dropped_all_correct` | Two correct first-round answers were suppressed and an empty first-round answer was retained. |

Paired against original:

- `answer_only_no_guard` fixes cases `5` and `22`.
- `guarded_answer_only` fixes cases `5` and `22`, but still fails case `20` despite adding the correct `Agent1` answer.
- `guard_full` fixes cases `5`, `20`, and `22`.

## Things Noticed

- The original DAR failures are not one mechanism. Cases `20` and `22` are selection failures, while case `5` is a continuation or formatting failure after correct context was already visible.
- Case `20` is a useful pressure case for message surface. Guarded answer-only makes the correct answer visible, but the final answer remains wrong; guarded full reasoning makes the same sample correct.
- Case `22` is not a clean evidence-transfer win for answer-only no-guard: it becomes correct even though the retained answer-only context still has no correct visible first-round answer. That points to surface, formatting, or second-round resampling rather than simple "the right evidence was passed."

## Caveats

- This is trace analysis over existing runs, not new model behavior.
- Correctness comes from the existing DAR trace extractor and parser.
- `context_events` are derived from `retention_events`; they are not raw prompt-level recipient contexts.
- GSM8K100 is still saturated relative to harder or more distributed-evidence regimes.
