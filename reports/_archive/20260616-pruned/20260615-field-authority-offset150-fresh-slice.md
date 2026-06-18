# Field-Authority Offset150 Fresh-Slice Pressure

Date: 2026-06-15

## What We Tried

Following the story audit, I did not build another detector. I used HotpotQA
offset150 as a fresh neighboring slice and built a cleaner field packet with
the stronger frozen-question-target prompt wording.

Source traces:

- `final_contract`: `experiments/_archive/20260616-pruned/20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target/comm_trace_offset150_final_contract_v11.jsonl`
- `compact_final_contract`: `experiments/_archive/20260616-pruned/20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target/comm_trace_offset150_compact_final_v11.jsonl`

Packet:

- `experiments/_archive/20260616-pruned/20260615-local-pact-public-state-field-packet-offset150/field_packet.jsonl`
- `50` samples, `2` source runs, `5` field conditions, `500` prompt rows.
- The source labels are explicit; this is not a baseline/final-contract pair.

GPU run:

- run id: `20260615-1840-a8002-pact-public-state-field-offset150-qwen25-14b`
- model: Qwen2.5-14B-Instruct through vLLM
- GPU: A800_2 GPU `7`
- decoding: temperature `0`, max tokens `64`
- completed `500/500`, failed `0`

## What Happened

Condition scores:

| Condition | EM | F1 |
| --- | ---: | ---: |
| `frozen_target_plus_evidence_no_final` | `0.480` | `0.657` |
| `question_plus_evidence_no_target_no_final` | `0.450` | `0.623` |
| `question_plus_public_state_with_final` | `0.430` | `0.599` |
| `question_plus_public_state_no_final` | `0.420` | `0.593` |
| `public_target_plus_evidence_no_question_no_final` | `0.310` | `0.495` |

Source-run slices:

| Source run | EM | F1 |
| --- | ---: | ---: |
| `compact_final_contract` | `0.436` | `0.606` |
| `final_contract` | `0.400` | `0.580` |

Official-source smoke over the same packet reproduces the old source-run
scores: `final_contract` has EM `0.500` / F1 `0.678`, and
`compact_final_contract` has EM `0.440` / F1 `0.604`.

## Delta Read

Against `question_plus_public_state_no_final`:

| Comparison | Rescues | Regressions | Both right | Both wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze question target | `10` | `4` | `38` | `48` |
| hide public target | `5` | `2` | `40` | `53` |
| hide question, keep public target | `0` | `11` | `31` | `58` |
| show final-answer candidate | `6` | `5` | `37` | `52` |

The important pressure point survives: when the original question is hidden,
the public target and evidence do not recover any base-wrong case and lose
`11` base-right cases.

## Bridge Read

The rebuilt packet-derived bridge over `100` sample/source units:

| Bridge layer | Units |
| --- | ---: |
| `evidence_or_content` | `28` |
| `stable_answer` | `27` |
| `final_answer_commitment` | `22` |
| `target_authority` | `11` |
| `target_contract` | `11` |
| `target_field_ablation` | `1` |

Within the target layers:

- `target_authority`: `11` public-target-without-question regressions.
- `target_contract`: `10` frozen-question-target rescues and `1` frozen-target
  regression.

This is a cleaner survival check for the field-authority handle, not a method
win. The target layers are real on a fresh slice, but they are not the whole
failure surface.

## Span And Granularity

Strict EM is still noisy:

- `101/500` rows are strict span or granularity misses;
- `31` missing required token/qualifier;
- `70` over-specific or sentence-expansion;
- `184` content mismatches.

This means aggregate EM movement should not be read without bridge labels.

## Interpretation

The offset150 fresh slice supports the bounded story:

**Public `Action Required` is not a reliable standalone task contract. The
trusted question root remains important, and frozen question-target projection
is still the strongest fixed control in this packet.**

But the result also keeps the caveats alive:

- this is saved-field re-answering, not a full PACT rerun;
- source runs are `final_contract` versus `compact_final_contract`, not a clean
  baseline pair;
- the target-authority count is smaller than offset100 (`11/100` here versus
  `20/100`);
- evidence/content failures remain the largest non-stable bridge layer;
- span and granularity misses are large enough to distort strict EM.

## Next Pressure

Do not revive the standalone lexical detector.

The next useful pressure is either:

- inspect the `10` frozen-question-target rescues and `11` public-target-only
  regressions to see whether they share a semantic field pattern; or
- move the same field packet idea to a task where public state is necessary,
  not merely available.

