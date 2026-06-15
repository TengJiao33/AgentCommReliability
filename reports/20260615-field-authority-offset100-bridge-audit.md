# Field-Authority Offset100 Bridge Audit

Date: 2026-06-15

## What We Tried

After the offset100 pressure run, all rows still carried the default bridge
bucket from packet construction. I rebuilt a bridge audit directly from the
evaluated field-control packet.

New script:

- `scripts/audit_pact_field_bridge_from_packet.py`

Artifacts:

- `experiments/20260615-local-pact-public-state-field-bridge-offset100/summary.json`
- `experiments/20260615-local-pact-public-state-field-bridge-offset100/bridge_cases.jsonl`
- `experiments/20260615-local-pact-public-state-field-bridge-offset100/bridge_packet.md`

Inputs:

- `experiments/20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b/evaluation/evaluated_rows.jsonl`
- `experiments/20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b/span_granularity_audit/span_granularity_rows.jsonl`
- `experiments/20260615-local-pact-public-state-field-packet-offset100/field_packet.jsonl`

This is not a new model run. It is an evaluation-side bridge label pass over
the `100` sample/source units.

## Bridge Counts

| Bridge layer | Units |
| --- | ---: |
| `stable_answer` | `26` |
| `evidence_or_content` | `25` |
| `target_authority` | `20` |
| `final_answer_commitment` | `18` |
| `target_contract` | `10` |
| `target_field_ablation` | `1` |

The bridge families are:

| Bridge family | Units |
| --- | ---: |
| `content_mismatch_after_public_state` | `25` |
| `stable_right_under_public_state` | `26` |
| `public_target_without_question_regression` | `20` |
| `strict_span_or_granularity_failure` | `16` |
| `frozen_question_target_rescue` | `7` |
| `target_drift_rescued_by_question_projection` | `2` |
| `final_candidate_attractor_regression` | `2` |
| `frozen_question_target_regression` | `1` |
| `public_target_helped_when_question_visible` | `1` |

## What The Labels Add

The earlier offset100 report already showed the aggregate pattern:

- frozen target beats public state;
- public target without question collapses;
- standalone detector underperforms.

The bridge audit makes the failure surfaces inspectable:

- `20` units are directly about target authority: the base public-state answer
  is correct, but the public target plus evidence fails when the original
  question is removed.
- `10` units are target-contract cases, including `9` frozen-target rescues and
  `1` frozen-target regression under the bridge priority.
- `18` units are final-answer commitment or span/granularity issues, including
  `16` strict-span/granularity failures and `2` final-candidate attractor
  regressions.
- `25` units remain content/evidence failures, where field authority controls
  do not explain the wrong answer.

That last bucket matters. The field-authority story is not a universal PACT
failure explanation.

## Interpretation

This strengthens the bounded story but keeps it narrow.

The useful object is not "public state helps" and not "the detector works." The
useful object is:

**which public fields are allowed to carry task authority when downstream
generation answers from a saved public state.**

The offset100 bridge audit says the authority problem is large enough to inspect
(`20` direct target-authority units plus `10` target-contract units), but it is
not the only failure mode (`25` content/evidence units remain).

## Caveats

- The labels are heuristic evaluation labels, not runtime verifier decisions.
- Labels use gold correctness and span-family audits.
- A unit can trigger several signals; the recorded bridge layer is the
  highest-priority inspection label.
- The packet is a saved-field re-answering stress test, not a full PACT rerun.

## Next Move

Do not build another standalone detector yet. If continuing this line, first
make a cleaner projection-only packet with the stronger frozen-target prompt
wording, then use these bridge labels to inspect which units move.
