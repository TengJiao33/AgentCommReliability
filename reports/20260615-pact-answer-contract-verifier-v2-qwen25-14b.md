# PACT Answer-Contract Verifier V2 Qwen2.5-14B Pressure

Date: 2026-06-15

## What We Tried

After the v1 verifier prompt failed, I built a prompt-v2 packet over the same
`74` records and gold labels.

Artifacts:

- prompt-v2 builder:
  `scripts/build_pact_answer_contract_verifier_prompt_v2_packet.py`
- v2 packet:
  `experiments/20260615-local-pact-answer-contract-verifier-packet-v2/`
- run:
  `experiments/20260615-1951-a8002-pact-answer-contract-verifier-v2-qwen25-14b/`
- previous v1 run:
  `experiments/20260615-1938-a8002-pact-answer-contract-verifier-qwen25-14b/`

The v2 prompt adds consistency rules, constrains `soft`, gives a decision
order, and expands surface definitions. It does not change labels or examples.

## What Happened

Execution again passed cleanly:

- completed requests: `74/74`
- request failures: `0`
- JSON parse failures: `0`
- runner/evaluator stderr: empty
- GPU 7 was released after completion

Metric comparison:

| Metric | v1 | v2 |
| --- | ---: | ---: |
| Exact all-fields accuracy | `0.081` | `0.108` |
| Primary-surface accuracy | `0.230` | `0.216` |
| Positive-seed all-fields accuracy | `0.000` | `0.000` |
| Negative-control all-fields accuracy | `0.250` | `0.333` |
| `answer_contract_alarm` F1 | `0.442` | `0.712` |
| `answer_contract_alarm` recall | `0.288` | `0.561` |
| `target_authority_alarm` F1 | `0.688` | `0.526` |
| `answer_type_relation_alarm` F1 | `0.133` | `0.154` |
| `short_span_granularity_alarm` F1 | `0.324` | `0.125` |
| `evidence_adequacy_alarm` F1 | `0.296` | `0.364` |
| `final_candidate_alarm` F1 | `0.174` | `0.154` |

## Things Noticed

The repair moved the model in the intended direction on two surfaces:

- `answer_contract_alarm` predictions changed from `20` yes to `38` yes;
- `target_authority_alarm = soft` predictions dropped from `43` to `12`.

But this came with a different failure pattern:

- target-authority recall fell from `0.702` to `0.426`;
- primary-surface accuracy stayed around chance for this taxonomy (`0.216`);
- short-span/granularity recall fell to `2/29`;
- the model predicted `no_answer_contract_failure` for `33/74` rows, despite
  only `8` gold no-failure rows.

The v2 prompt therefore repaired a calibration symptom, not the core
multi-surface diagnosis problem.

## Interpretation

The current answer-contract verifier should not be used as a runtime router.

The packet is still useful because it makes the failure visible:

- one-shot taxonomy prompting can raise the global alarm;
- it still cannot reliably choose the right failure surface;
- target-authority, evidence adequacy, final-candidate attraction, and
  span/granularity need more separable tests.

This shifts the next design away from "write a better long prompt" and toward a
split verifier protocol:

1. binary answer-contract risk;
2. target-authority classifier;
3. answer-type/relation classifier;
4. span/granularity classifier;
5. evidence adequacy classifier;
6. final-candidate attraction classifier;
7. deterministic combiner for primary surface and consistency.

## Caveats

- Same selected `74`-record seed packet as v1.
- One model and one zero-temperature run per prompt version.
- Gold labels are manual/oracle seed labels.
- Prompt-v2 is longer and more constrained, but not few-shot.
- Results do not say the handle is dead; they say this verifier shape is not
  reliable enough.

## Next Contact

Do not run v3 as another longer taxonomy prompt.

The next useful object is a local split-stage verifier packet or evaluator over
the same records. It should ask one narrow question per pass and then combine
the outputs deterministically. That will test whether Qwen2.5-14B lacks the
signal, or whether the current all-in-one output schema is too entangled.
