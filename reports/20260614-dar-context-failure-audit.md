# DAR Context Failure Audit

## What We Tried

This note audits existing DAR schema v1.1 traces through the new derived
`context_events` field. It asks whether right-to-wrong and wrong-to-right cases
can be separated by what was visible to the second round, rather than only by
aggregate accuracy.

No model call or GPU run was launched.

Sources:

| Source | Path |
| --- | --- |
| Audit run | `experiments/20260614-1248-local-dar-context-failure-audit/` |
| Script | `scripts/audit_dar_context_failures.py` |
| Original DAR v1.1 | `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar_v11.jsonl` |
| Answer-only no-guard v1.1 | `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_answer_only_noguard_v11.jsonl` |
| Guarded answer-only v1.1 | `experiments/20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100/comm_trace_dar_guarded_v11.jsonl` |
| Guard-full v1.1 | `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_guard_full_v11.jsonl` |

## What Happened

Across four DAR traces, the audit covers 400 records. Final accuracies match the
earlier split-ablation records:

| Trace | Accuracy | right-to-wrong | wrong-to-right |
| --- | ---: | ---: | ---: |
| `original` | 0.93 | 3 | 1 |
| `answer_only_no_guard` | 0.95 | 1 | 1 |
| `guarded_answer_only` | 0.95 | 1 | 1 |
| `guard_full` | 0.96 | 0 | 1 |

The original right-to-wrong cases divide cleanly:

| Case | Visible first-round correctness | Suppressed first-round correctness | Audit label |
| ---: | ---: | ---: | --- |
| `5` | 2 correct visible | 0 correct suppressed | `correct_context_retained_but_lost_after_update` |
| `20` | 0 correct visible | 1 correct suppressed | `selection_dropped_all_correct` |
| `22` | 0 correct visible | 2 correct suppressed | `selection_dropped_all_correct` |

Paired against the original trace:

- `answer_only_no_guard` fixes `5` and `22`.
- `guarded_answer_only` fixes `5` and `22`, but still fails `20`.
- `guard_full` fixes `5`, `20`, and `22`.

## Things Noticed

The useful distinction is no longer simply "retention was too aggressive." DAR
has at least two failure surfaces on this slice:

- selection surface: correct first-round answers are not visible in the next
  round, as in cases `20` and `22`;
- continuation or format surface: correct context is visible, but the next
  round still loses the answer, as in case `5`.

Case `20` is the sharpest pressure point for message surface. The guarded
answer-only trace adds the correct first-round answer to the visible context,
but the sample still ends wrong. The guarded full-reasoning trace makes the same
sample correct. That does not prove full reasoning is generally better, but it
does show that "make a correct answer visible" is not sufficient for this case.

Case `22` is the useful caveat in the other direction. Answer-only no-guard
fixes it even though the visible answer-only context still has no correct
first-round answer. That improvement is probably not clean evidence transfer;
it may come from simpler surface, formatting, or second-round resampling.

## Failures / Friction

- The audit still cannot see the exact prompt assembled for each recipient.
- It classifies visible/suppressed correctness from round-0 parsed answers, not
  from semantic reasoning quality.

## Loose Threads

- Inspect case `20` prompt text or raw retained message content across
  answer-only and guard-full runs.
- If another DAR run is justified later, the next retained surface should be
  between answer-only and full reasoning: answer plus short calculation or
  evidence, not just a prompt wording variant.

## Caveats

- Existing runs only; no new behavior was generated.
- One model, seed, and GSM8K100 slice.
- GSM8K arithmetic remains a saturated regime, so this is best treated as
  contact with failure surfaces rather than method evidence.
