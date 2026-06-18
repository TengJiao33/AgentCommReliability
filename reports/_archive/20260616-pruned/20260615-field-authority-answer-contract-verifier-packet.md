# Field-Authority Answer-Contract Verifier Packet

Date: 2026-06-15

## What This Is

This step turns the answer-contract positive seed and negative-control seed into
a model-ready structured verifier packet.

Artifacts:

- `scripts/build_pact_answer_contract_verifier_packet.py`
- `scripts/evaluate_pact_answer_contract_verifier.py`
- `experiments/_archive/20260616-pruned/20260615-local-pact-answer-contract-verifier-packet/verifier_packet.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-pact-answer-contract-verifier-packet/gold_labels.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-pact-answer-contract-verifier-packet/summary.json`
- `experiments/_archive/20260616-pruned/20260615-local-pact-answer-contract-verifier-packet/scoring_plan.md`
- `experiments/_archive/20260616-pruned/20260615-local-pact-answer-contract-verifier-packet/gold-smoke/summary.json`
- `experiments/_archive/20260616-pruned/20260615-local-pact-answer-contract-verifier-packet/all-no-baseline/summary.json`

The verifier prompt hides gold answers and observed downstream behavior. It sees
only the original question plus public-state fields:

- `Action Required`;
- `Environment State`;
- `Action Result`;
- `Final Answer Candidate`.

## Packet Shape

| Item | Count |
| --- | ---: |
| Total records | `74` |
| Positive target-layer seed | `50` |
| Negative-control seed | `24` |
| offset100 | `40` |
| offset150 | `34` |

Gold primary surfaces:

| Surface | Count |
| --- | ---: |
| `answer_type_or_relation_mismatch` | `21` |
| `short_span_or_granularity_mismatch` | `21` |
| `public_target_misdirection` | `3` |
| `evidence_sentence_or_distractor_copy` | `3` |
| `question_root_ambiguity_regression` | `2` |
| `evidence_or_content_failure` | `8` |
| `final_candidate_attractor` | `5` |
| `strict_span_or_granularity_surface` | `3` |
| `no_answer_contract_failure` | `8` |

Gold alarm counts:

| Alarm | Count |
| --- | ---: |
| `answer_contract_alarm = yes` | `66` |
| `target_authority_alarm = yes` | `45` |
| `target_authority_alarm = soft` | `2` |
| `answer_type_relation_alarm = yes` | `24` |
| `short_span_granularity_alarm = yes` | `29` |
| `evidence_adequacy_alarm = yes` | `13` |
| `final_candidate_alarm = yes` | `5` |

## Scoring Smoke

The `gold` prediction-source smoke reaches `1.000` exact all-fields accuracy
and `1.000` primary-surface accuracy, which checks that the packet and evaluator
agree on schema normalization.

The `all_no` baseline is intentionally weak:

| Metric | Value |
| --- | ---: |
| Exact all-fields accuracy | `0.108` |
| Primary-surface accuracy | `0.108` |
| `answer_contract_alarm` F1 | `0.000` |
| `target_authority_alarm` F1 | `0.000` |
| `short_span_granularity_alarm` F1 | `0.000` |
| `evidence_adequacy_alarm` F1 | `0.000` |
| `final_candidate_alarm` F1 | `0.000` |

This means the packet is not solved by staying quiet. It also means future
model scores should be read by alarm family, not just by one overall accuracy.

## Why This Matters

The previous artifacts showed two things separately:

- positive target-layer cases need answer-contract checks;
- negative controls include real adjacent failures that are not primary
  target-authority failures.

This packet joins them into one scoring object. A future verifier now has to
answer a harder and cleaner question:

> Can it identify the right failure surface, while not stealing evidence,
> final-candidate, or strict-span failures into the target-authority bucket?

## Run Command Template

The existing OpenAI-compatible runner can run this packet because each row has a
`prompt` and `packet_id`:

```powershell
python scripts\run_pact_public_state_field_packet.py `
  --packet experiments\_archive\20260616-pruned\20260615-local-pact-answer-contract-verifier-packet\verifier_packet.jsonl `
  --out-dir experiments\_archive\20260616-pruned\20260615-local-pact-answer-contract-verifier-packet\model-run `
  --base-url <OPENAI_COMPATIBLE_BASE_URL> `
  --model <MODEL_NAME> `
  --max-tokens 192 `
  --temperature 0 `
  --keep-going
```

Score model outputs with:

```powershell
python scripts\evaluate_pact_answer_contract_verifier.py `
  --packet experiments\_archive\20260616-pruned\20260615-local-pact-answer-contract-verifier-packet\verifier_packet.jsonl `
  --outputs experiments\_archive\20260616-pruned\20260615-local-pact-answer-contract-verifier-packet\model-run\outputs.jsonl `
  --prediction-source outputs `
  --out-dir experiments\_archive\20260616-pruned\20260615-local-pact-answer-contract-verifier-packet\model-run-evaluation
```

## Caveats

- This is a verifier benchmark packet, not a model result.
- Gold labels are still manual/oracle labels from positive and negative seeds.
- The positive short-span labels intentionally treat wrong public target
  granularity as target-authority risk; final-span negative controls keep
  target-authority mostly separate.
- `soft` target-authority labels are subjective boundary cases and should be
  inspected in model errors.

