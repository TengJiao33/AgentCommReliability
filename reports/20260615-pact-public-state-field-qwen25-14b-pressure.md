# PACT Public-State Field Qwen2.5-14B Pressure

## What We Ran

I ran the full PACT public-state field packet on A800_2 with
Qwen2.5-14B-Instruct served through vLLM.

Run artifacts:

- `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/outputs.jsonl`
- `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/manifest.json`
- `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/evaluation/summary.json`
- `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/evaluation/summary.md`
- `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/field_delta_audit/delta_summary.json`
- `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/field_delta_audit/delta_summary.md`

Launcher:

- `scripts/run_pact_public_state_field_packet_a8002.sh`

Delta audit:

- `scripts/analyze_pact_public_state_field_results.py`

The run completed all `500/500` packet rows with `0` failed rows.

Configuration:

| Field | Value |
| --- | --- |
| Model path | `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct` |
| Served model | `qwen2.5-14b-pact-field` |
| GPU | `7` |
| Port | `8034` |
| Temperature | `0.0` |
| Max tokens | `64` |
| Packet rows | `500` |

## Top-Line Result

Overall packet score:

| Records | EM | Avg F1 |
| ---: | ---: | ---: |
| `500` | `0.536` | `0.689` |

The condition split is the useful result:

| Condition | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `question_plus_evidence_no_target_no_final` | `100` | `0.590` | `0.725` | n/a | `0` | `0` |
| `frozen_target_plus_evidence_no_final` | `100` | `0.580` | `0.734` | n/a | `0` | `0` |
| `question_plus_public_state_with_final` | `100` | `0.550` | `0.710` | `0.740` | `6` | `5` |
| `question_plus_public_state_no_final` | `100` | `0.520` | `0.688` | n/a | `0` | `0` |
| `public_target_plus_evidence_no_question_no_final` | `100` | `0.440` | `0.591` | n/a | `0` | `0` |

The pressure result is not "public state wins." It is sharper and colder:

**Public-state fields are only useful when the target contract, evidence, and
final-answer commitment stay coupled.**

Removing the public `Action Required` while keeping the original question and
evidence improved EM over the full public-state/no-final condition
(`0.590` versus `0.520`). Freezing a question-derived target also improved it
(`0.580` versus `0.520`). But keeping the public target while hiding the
original question collapsed performance (`0.440`).

So the public target field is not a stable task contract by itself. Sometimes it
is a helpful compression; sometimes it is a lossy or misleading substitute for
the original question.

## Source-Run Split

The source run split is also uncomfortable in a productive way:

| Source run | Records | EM | Avg F1 | Candidate copy | Corrections | Regressions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | `250` | `0.560` | `0.701` | `0.680` | `5` | `1` |
| `final_contract` | `250` | `0.512` | `0.677` | `0.800` | `1` | `4` |

The earlier final-answer-contract source run had better original source answers,
but its public state did not transfer cleanly into this re-answer packet. In the
candidate-visible condition, it copied more often and regressed more often.

This matters because it rejects an easy story: improving the previous final
answer is not the same thing as making the public state reliably reusable.

## Delta Audit

The delta audit compares every condition against the base condition:

Base condition: `question_plus_public_state_no_final`.

| Comparison | Base wrong to variant right | Base right to variant wrong | Both right | Both wrong |
| --- | ---: | ---: | ---: | ---: |
| `hide_public_target` | `11` | `4` | `48` | `37` |
| `freeze_question_target` | `10` | `4` | `48` | `38` |
| `hide_question_keep_public_target` | `2` | `10` | `42` | `46` |
| `show_final_answer_candidate` | `6` | `3` | `49` | `42` |

The strongest pressure signal is the asymmetry:

- Hiding the public target while keeping question/evidence produced `11`
  rescues against `4` regressions.
- Freezing the target from the question produced `10` rescues against `4`
  regressions.
- Hiding the original question while keeping public target produced only `2`
  rescues against `10` regressions.

This says the field object should not be "make a better target field" in the
abstract. The object should be **target-contract reliability under
question/evidence coupling**.

## Target-Drift Slice

The target-slot candidate slice is much harder than the rest:

| Target drift candidate | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `False` | `420` | `0.588` | `0.720` |
| `True` | `80` | `0.263` | `0.530` |

But the delta is not one-directional:

| Comparison on target candidates | Base wrong to variant right | Base right to variant wrong | Both right | Both wrong |
| --- | ---: | ---: | ---: | ---: |
| `hide_public_target` | `4` | `0` | `4` | `8` |
| `freeze_question_target` | `1` | `2` | `2` | `11` |
| `hide_question_keep_public_target` | `0` | `1` | `3` | `12` |
| `show_final_answer_candidate` | `0` | `1` | `3` | `12` |

The important point is that target-drift candidates are not fixed simply by
showing more public state. On this slice, removing the public target is cleaner
than trusting it, while a frozen target helps less than expected.

That pushes the next design toward explicit target-contract verification, not
just target-field replacement.

## Bridge-Layer Reading

Bridge-layer scores show where the packet is carrying signal:

| Bridge layer | Records | EM | Avg F1 | Candidate copy |
| --- | ---: | ---: | ---: | ---: |
| `stable_right_or_not_focus` | `220` | `0.905` | `0.958` | `0.932` |
| `target_final_alignment` | `20` | `0.500` | `0.560` | `0.250` |
| `positive_contract_rescue` | `60` | `0.467` | `0.538` | `0.500` |
| `target_contract` | `20` | `0.250` | `0.250` | `0.750` |
| `final_answer_commitment` | `120` | `0.192` | `0.647` | `0.625` |
| `diagnostic_noise` | `10` | `0.100` | `0.110` | `0.000` |
| `evidence_carriage` | `50` | `0.040` | `0.132` | `0.800` |

The evidence-carriage cases are especially harsh: the model often copies the
visible candidate when available, but the task remains mostly wrong. That means
candidate visibility can be a surface attractor without being evidence use.

## Interpretation

This pressure test makes the larger idea more credible by making it less
romantic.

The project should not center on typed public state as a method name. It should
center on field-level public-state reliability:

1. target contract preservation;
2. evidence carriage without distractor migration;
3. final-answer commitment to the required slot and granularity;
4. verification that a field remains usable when the original task context is
   partially hidden.

The result gives a real next object: build an intervention or benchmark that
does not merely expose structured fields, but checks whether each field remains
semantically licensed by the question and evidence.

## What This Deletes

This run deletes several weaker directions:

- Do not keep chasing "typed public state" as the big claim.
- Do not assume PACT-style structured public state is automatically reusable.
- Do not treat final-answer-contract gains as equivalent to communication
  reliability.
- Do not scale a larger HotpotQA run before adding target/evidence/commitment
  field checks.

The productive direction is narrower and stronger: public state needs field
contracts, not prettier fields.

## Caveats

- One model, one 50-sample HotpotQA offset slice expanded into 500 prompt rows.
- The packet is a re-answering stress test over saved PACT fields, not a full
  retrieval or full multi-agent rerun.
- HotpotQA exact match still penalizes granularity and aliasing.
- Bridge labels inherit the earlier bridge audit limits: mechanical atlas
  labels, ten manual labels, and lexical target-slot diagnostics.
- Condition differences are behavioral pressure, not a final method result.

## Next Move

Build a field-contract verifier around this object.

The verifier should explicitly score whether `Action Required`,
`Environment State`, `Action Result`, and `Final Answer` remain licensed by the
original question and evidence. Then rerun the packet with one intervention:
only expose public fields that pass target/evidence/commitment checks, while
holding the original answer-only decoding constant.

That is large enough to matter, and it follows the skill: do not hide behind
miniatures; make a bold move that can kill a weak idea or expose a real one.
