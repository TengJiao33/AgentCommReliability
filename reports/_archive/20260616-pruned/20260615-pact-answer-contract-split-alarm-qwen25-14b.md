# PACT Answer-Contract Split-Alarm Qwen2.5-14B Pressure

Date: 2026-06-15

## What We Tried

After the all-in-one verifier and prompt-v2 both failed, I decomposed the same
`74` seed records into one narrow alarm question per prompt.

Artifacts:

- split packet builder:
  `scripts/build_pact_answer_contract_split_alarm_packet.py`
- split evaluator:
  `scripts/evaluate_pact_answer_contract_split_alarm.py`
- split packet:
  `experiments/_archive/20260616-pruned/20260615-local-pact-answer-contract-split-alarm-packet/`
- run:
  `experiments/_archive/20260616-pruned/20260615-2002-a8002-pact-answer-contract-split-alarm-qwen25-14b/`

Packet shape:

- base records: `74`
- alarm tasks: `6`
- prompt rows: `444`
- model: Qwen2.5-14B-Instruct through vLLM on A800_2 GPU `7`
- temperature: `0`

## What Happened

Execution passed:

- completed requests: `444/444`
- request failures: `0`
- parse failures after split-label fallback: `0`
- GPU 7 was released after completion

Main result:

| Metric | Value |
| --- | ---: |
| Exact label accuracy | `0.590` |
| Positive/negative accuracy | `0.617` |
| Overall binary F1 | `0.384` |

By alarm:

| Alarm | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| `answer_contract_alarm` | `0.926` | `0.379` | `0.538` |
| `target_authority_alarm` | `0.667` | `0.383` | `0.486` |
| `answer_type_relation_alarm` | `0.250` | `0.083` | `0.125` |
| `short_span_granularity_alarm` | `0.500` | `0.034` | `0.065` |
| `evidence_adequacy_alarm` | `0.350` | `0.538` | `0.424` |
| `final_candidate_alarm` | `0.000` | `0.000` | `0.000` |

## Comparison

Compared with the all-in-one prompts, split prompting did not produce a broad
rescue.

| Alarm | v1 F1 | v2 F1 | split F1 |
| --- | ---: | ---: | ---: |
| `answer_contract_alarm` | `0.442` | `0.712` | `0.538` |
| `target_authority_alarm` | `0.688` | `0.526` | `0.486` |
| `answer_type_relation_alarm` | `0.133` | `0.154` | `0.125` |
| `short_span_granularity_alarm` | `0.324` | `0.125` | `0.065` |
| `evidence_adequacy_alarm` | `0.296` | `0.364` | `0.424` |
| `final_candidate_alarm` | `0.174` | `0.154` | `0.000` |

Evidence adequacy is the only alarm that improved under splitting. The other
families stayed weak or worsened.

## Things Noticed

The model remained conservative on several positive labels:

- answer-contract gold yes: `66`; predicted yes: `27`;
- short-span gold yes: `29`; predicted yes: `2`;
- final-candidate gold yes: `5`; predicted yes: `8`, but none were true
  positives;
- target-authority gold positive: `47`; predicted positive: `27`.

This means the all-in-one failure was not only output-schema entanglement.
Qwen2.5-14B does not reliably recognize several gold alarm families under
zero-shot narrow prompts.

## Interpretation

The answer-contract handle remains live, but the verifier route is weaker than
the packet-building route made it look.

Three increasingly generous checks now say the same thing:

- v1 all-in-one prompt: valid JSON but poor diagnosis;
- v2 stricter all-in-one prompt: better global alarm, still poor diagnosis;
- split-alarm prompts: no broad recovery, only evidence adequacy improves.

The next useful move is not another zero-shot prompt variant. It should be one
of:

- add few-shot contrastive examples per alarm family;
- simplify or relabel the hardest families, especially short-span and
  final-candidate;
- try a stronger verifier model on the same packet;
- use these packets as a manual audit benchmark rather than a runtime verifier.

## Caveats

- Same selected `74` base records and manual/oracle labels.
- One model, one zero-temperature run.
- Split prompts do not produce a primary surface; they only test alarm
  separability.
- One output was truncated after the label field; the evaluator fallback reads
  the completed label and records `0` parse failures after re-evaluation.

## Bottom Line

Splitting the verifier into narrow alarm prompts does not rescue the current
Qwen2.5-14B verifier. The field-authority / answer-contract phenomenon remains
useful as an audit handle, but this model-prompt setup is not reliable enough
for automated routing.
