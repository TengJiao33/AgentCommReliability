# PACT Answer-Contract Verifier Qwen2.5-14B Pressure

Date: 2026-06-15

## What We Tried

Ran the structured answer-contract verifier packet with Qwen2.5-14B-Instruct at
temperature `0`.

Run:

- `experiments/20260615-1938-a8002-pact-answer-contract-verifier-qwen25-14b/`
- packet:
  `experiments/20260615-local-pact-answer-contract-verifier-packet/verifier_packet.jsonl`
- records: `74`
- model: Qwen2.5-14B-Instruct through vLLM on A800_2 GPU `7`
- evaluator: `scripts/evaluate_pact_answer_contract_verifier.py`

The packet hides gold answers and observed downstream behavior. The verifier
sees only the original question plus public fields: `Action Required`,
`Environment State`, `Action Result`, and `Final Answer Candidate`.

## What Happened

Execution passed cleanly:

- completed requests: `74/74`
- request failures: `0`
- JSON parse failures: `0`
- runner/evaluator stderr: empty
- GPU 7 was released after completion

But the verifier prompt failed as a structured detector:

| Metric | Value |
| --- | ---: |
| Exact all-fields accuracy | `0.081` |
| Primary-surface accuracy | `0.230` |
| Positive-seed all-fields accuracy | `0.000` |
| Negative-control all-fields accuracy | `0.250` |

Alarm metrics:

| Alarm | Exact acc | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| `answer_contract_alarm` | `0.351` | `0.950` | `0.288` | `0.442` |
| `target_authority_alarm` | `0.203` | `0.673` | `0.702` | `0.688` |
| `answer_type_relation_alarm` | `0.649` | `0.333` | `0.083` | `0.133` |
| `short_span_granularity_alarm` | `0.662` | `0.750` | `0.207` | `0.324` |
| `evidence_adequacy_alarm` | `0.743` | `0.286` | `0.308` | `0.296` |
| `final_candidate_alarm` | `0.743` | `0.111` | `0.400` | `0.174` |

## Things Noticed

This is not a formatting failure. All `74` outputs contained parseable JSON
with the expected fields.

The strongest signal is target-authority, but it is badly calibrated. The model
predicted `target_authority_alarm = soft` for `43/74` rows, while the gold
packet has only `2` soft rows. It produced `16` target-authority false positives
on non-target surfaces and `14` false negatives, mostly inside
`answer_type_or_relation_mismatch` and `short_span_or_granularity_mismatch`.

The global `answer_contract_alarm` under-fired. Gold has `66` yes rows, while
the model predicted only `20` yes rows. There were `47` false negatives,
including `16` answer-type/relation rows and `16` short-span/granularity rows.

Primary-surface predictions collapsed toward a few labels:

- predicted `public_target_misdirection`: `28`
- predicted `no_answer_contract_failure`: `21`
- predicted `evidence_or_content_failure`: `8`
- predicted `short_span_or_granularity_mismatch`: `7`
- predicted `final_candidate_attractor`: `6`
- predicted `answer_type_or_relation_mismatch`: `4`

The six all-fields-correct rows were all stable-right negative controls. The
model did not get any positive target-layer seed exactly right.

## Interpretation

This falsifies the current verifier prompt as a runtime field-contract verifier.

The packet itself looks useful: an all-no baseline was weak, the model produced
valid structured outputs, and the error pattern is diagnostic rather than
random. But the current prompt does not reliably separate:

- target-authority risk from evidence/content or final-candidate failures;
- answer-type/relation mismatch from generic public-target misdirection;
- short-span/granularity failures from no-failure rows;
- global answer-contract risk from its own selected primary failure surface.

The live handle survives, but the current verifier is not ready to control
public-state exposure.

## Caveats

- One model: Qwen2.5-14B-Instruct.
- One prompt, zero temperature, no few-shot examples.
- Gold labels are still manual/oracle seed labels.
- The packet is selected positive and negative controls, not a population
  benchmark.
- `soft` target-authority labels are boundary labels and the model strongly
  overuses them.

## Next Contact

Do not use this verifier to route a field packet yet.

The next useful pressure is a prompt/schema repair on the same `74` records:

- make `answer_contract_alarm` logically consistent with non-`no` primary
  surfaces and subalarms;
- constrain `target_authority_alarm = soft` with contrastive negative controls;
- add explicit distinctions between public-target misdirection, evidence
  inadequacy, final-candidate attraction, and strict span/granularity;
- rerun the same packet before moving to a new slice or a full PACT rerun.

This is a useful failed verifier run, not a method result.
