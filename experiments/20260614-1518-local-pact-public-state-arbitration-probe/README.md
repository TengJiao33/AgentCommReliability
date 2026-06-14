# PACT Public-State Arbitration Probe

## What We Tried

I turned the field-selection case inspection into a CPU-only postprocessing
probe over the saved PACT HotpotQA50 trace.

The probe compares:

- `question_aware_policy`: the prior final-answer-oriented extractor;
- `final_event_arbitration`: always rank candidates from final-turn
  `final_answer`, `action_result`, and `environment_state`;
- `all_public_state_arbitration`: the same ranker over all public turns;
- `guarded_final_event_arbitration`: only arbitrate when the current
  question-aware answer visibly violates the question contract;
- `guarded_all_public_state_arbitration`: guarded arbitration over all public
  turns.

No model call or GPU run was launched.

## Input

| Source | Path |
| --- | --- |
| PACT trace v1.1 | `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl` |
| Manual field-selection labels | `experiments/20260614-1507-local-pact-field-selection-case-inspection/manual_labels.jsonl` |

## Command

```powershell
python scripts\audit_pact_public_state_arbitration.py `
  --trace experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\comm_trace_pact_v11.jsonl `
  --manual-labels experiments\20260614-1507-local-pact-field-selection-case-inspection\manual_labels.jsonl `
  --summary-out experiments\20260614-1518-local-pact-public-state-arbitration-probe\summary.json `
  --cases-out experiments\20260614-1518-local-pact-public-state-arbitration-probe\cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Aggregate counts for naive and guarded arbitration policies. |
| `cases.jsonl` | One row per sample with selected policies and transitions. |

## What Happened

| Policy | Correct | vs question-aware rescues | vs question-aware regressions |
| --- | ---: | ---: | ---: |
| official PACT extraction | `17/50` | n/a | n/a |
| question-aware policy | `38/50` | n/a | n/a |
| final-event arbitration | `38/50` | `6` | `6` |
| all-public-state arbitration | `38/50` | `6` | `6` |
| guarded final-event arbitration | `44/50` | `6` | `0` |
| guarded all-public-state arbitration | `44/50` | `6` | `0` |

Naive arbitration is not enough: simply trusting ranked public-state candidates
rescues some field-selection cases but breaks already-correct question-aware
cases.

Guarded arbitration is more informative. It preserves all `38` question-aware
correct cases and recovers `6` additional cases: `1`, `15`, `25`, `30`, `31`,
and `40`.

On the `9` manually labeled focus cases, guarded final-event arbitration
recovers:

- final field or anchor selection conflict: `3/3`;
- answer contract or extractor priority: `3/4`;
- earlier state lost or overwritten: `0/2`.

## Things Noticed

The signal is not "public state is always better than final answer." The signal
is narrower: arbitration helps when the final answer visibly violates the
question contract, but unrestricted arbitration can overwrite already good
answers.

The all-public-state policy does not improve over final-event policy here. The
two earlier-state cases remain wrong:

- sample `19`: the final state drops the `DSC` suffix and the ranker still
  prefers the final shorter name;
- sample `23`: earlier `Badly Drawn Boy` is present, but the final comparison
  state points to a tie or to `Wolf Alice`.

This suggests the next contact point is not a bigger answer extractor. It is
either:

- a very small final-answer-contract control run; or
- an explicit public-state arbitration/check step that can reject stale or
  wrong field anchors.

## Caveats

- This is postprocessing over one 50-sample saved PACT run.
- The guard was shaped after inspecting these traces, so `44/50` is a
  diagnostic number, not an official score or method claim.
- Gold labels are used only for evaluation, not policy selection.
- Exact-match gains may still include HotpotQA answer-normalization artifacts.
