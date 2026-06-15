# PACT Public-State Field Packet

## What We Tried

I turned the PACT HotpotQA offset50 traces into a model-ready packet for
testing field-level public-state reliability.

This is the concrete next step after the bridge audit. Instead of another
typed/MATH mini-variant, the packet stresses the split-evidence public-state
surface directly.

New scripts:

- `scripts/build_pact_public_state_field_packet.py`
- `scripts/run_pact_public_state_field_packet.py`
- `scripts/evaluate_pact_public_state_field_packet.py`

New packet:

- `experiments/20260615-local-pact-public-state-field-packet/field_packet.jsonl`
- `experiments/20260615-local-pact-public-state-field-packet/summary.json`
- `experiments/20260615-local-pact-public-state-field-packet/README.md`
- `experiments/20260615-local-pact-public-state-field-packet/scoring_plan.md`

Smoke evaluation:

- `experiments/20260615-local-pact-public-state-field-packet/official-final-answer-smoke/summary.json`
- `experiments/20260615-local-pact-public-state-field-packet/official-final-answer-smoke/summary.md`
- `experiments/20260615-local-pact-public-state-field-packet/official-final-answer-smoke/evaluated_rows.jsonl`

## What Happened

The builder generated `500` model-ready prompt rows:

| Axis | Count |
| --- | ---: |
| PACT samples | `50` |
| Source runs | `2` |
| Field conditions | `5` |
| Prompt rows | `500` |

Source runs:

| Source run | Rows |
| --- | ---: |
| `baseline` | `250` |
| `final_contract` | `250` |

Field conditions:

| Condition | Rows | Axis |
| --- | ---: | --- |
| `question_plus_public_state_with_final` | `100` | final-answer commitment |
| `question_plus_public_state_no_final` | `100` | evidence-to-answer commitment |
| `question_plus_evidence_no_target_no_final` | `100` | target-field ablation |
| `frozen_target_plus_evidence_no_final` | `100` | frozen target contract |
| `public_target_plus_evidence_no_question_no_final` | `100` | public-target sufficiency |

Bridge coverage:

| Bridge layer | Samples |
| --- | ---: |
| `stable_right_or_not_focus` | `22` |
| `positive_contract_rescue` | `6` |
| `final_answer_commitment` | `12` |
| `target_contract` | `2` |
| `target_final_alignment` | `2` |
| `evidence_carriage` | `5` |
| `diagnostic_noise` | `1` |

The packet also carries the eight target-slot drift candidates:

`54`, `55`, `58`, `60`, `82`, `83`, `87`, `89`.

## Smoke Check

I ran the evaluator in `official_final_answer` mode. This does not evaluate a
new model. It simply confirms that the scoring and slicing pipeline can recover
the source-run scores from the packet metadata.

| Source run | Rows | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `baseline` | `250` | `0.520` | `0.647` |
| `final_contract` | `250` | `0.560` | `0.743` |

Those match the known offset50 PACT baseline/final-contract run summaries once
each source answer is repeated across the five field conditions.

The target-slot candidate slice is also visible:

| Target drift candidate | Rows | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `False` | `420` | `0.619` | `0.733` |
| `True` | `80` | `0.125` | `0.492` |

This is still source-output smoke, not a new intervention result.

## Why This Is The Right Next Object

The packet gives the project a real communication-necessity contact surface.
It can now ask model-behavior questions that typed/MATH could not answer:

- Does a visible final-answer candidate cause copying, correction, or regression?
- Does `Action Required` help when the original question is already visible?
- Can a frozen question-derived target repair public target drift?
- Does public target alone preserve enough task information when the original
  question is hidden?
- Are target-slot candidate cases especially sensitive to field visibility?

This is closer to the actual idea: field-level public-state reliability across
target contract, evidence carriage, and final-answer commitment.

## How To Run A Model Later

Run the packet against an OpenAI-compatible endpoint:

```powershell
python scripts\run_pact_public_state_field_packet.py `
  --packet experiments\20260615-local-pact-public-state-field-packet\field_packet.jsonl `
  --base-url http://127.0.0.1:8000/v1 `
  --model <served-model-name> `
  --api-key EMPTY `
  --out-dir experiments\20260615-local-pact-public-state-field-packet\model-runs\<run-id> `
  --keep-going
```

Then evaluate:

```powershell
python scripts\evaluate_pact_public_state_field_packet.py `
  --packet experiments\20260615-local-pact-public-state-field-packet\field_packet.jsonl `
  --outputs experiments\20260615-local-pact-public-state-field-packet\model-runs\<run-id>\outputs.jsonl `
  --prediction-source outputs `
  --out-dir <evaluation-output-dir>
```

The runner writes `outputs.jsonl`, `failures.jsonl` if needed, and
`manifest.json`.

## Caveats

- No model was run for the packet conditions yet.
- The prompts use saved PACT public-state fields and do not retrieve evidence.
- This tests final-answer extraction/commitment from public-state surfaces, not
  full HotpotQA solving from scratch.
- Field labels inherit the bridge audit's limits: one offset50 slice, mechanical
  atlas labels, ten manual labels, and a lexical target-slot diagnostic.

## Next Move

Run this packet on one model with low-temperature final-answer-only decoding,
then slice by condition, bridge layer, bridge family, and target-slot candidate.
That would finally test whether the field-level story has behavioral bite in a
split-evidence public-state regime.
