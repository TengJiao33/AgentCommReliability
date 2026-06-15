# Field-Authority Answer-Contract Negative Controls

Date: 2026-06-15

## What This Is

This is a matched negative-control packet for the answer-contract audit seed.
It uses non-target bridge layers from the offset100 and offset150 saved-field
audits:

- stable-answer units;
- evidence/content mismatch units;
- final-answer commitment or strict-span units.

Artifacts:

- `scripts/build_pact_answer_contract_negative_controls.py`
- `experiments/20260615-local-pact-answer-contract-negative-controls/negative_control_cards.jsonl`
- `experiments/20260615-local-pact-answer-contract-negative-controls/negative_control_seed.jsonl`
- `experiments/20260615-local-pact-answer-contract-negative-controls/manual_seed_labels.jsonl`
- `experiments/20260615-local-pact-answer-contract-negative-controls/manual_seed_label_summary.json`
- `experiments/20260615-local-pact-answer-contract-negative-controls/negative_control_cards.md`
- `experiments/20260615-local-pact-answer-contract-negative-controls/negative_control_seed.md`
- `experiments/20260615-local-pact-answer-contract-negative-controls/summary.json`

This is not a verifier result. It is a specificity packet: a future
answer-contract audit should be tested against these controls before it is
treated as selective.

## Counts

| Item | Count |
| --- | ---: |
| Negative-control cards | `146` |
| Manual seed cards | `24` |
| offset100 cards | `69` |
| offset150 cards | `77` |

Control layers:

| Control layer | Count |
| --- | ---: |
| `stable_answer` | `53` |
| `evidence_or_content` | `53` |
| `final_answer_commitment` | `40` |

Control families:

| Control family | Count |
| --- | ---: |
| `stable_right_under_public_state` | `53` |
| `content_mismatch_after_public_state` | `53` |
| `strict_span_or_granularity_failure` | `33` |
| `final_candidate_attractor_regression` | `5` |
| `final_candidate_rescue` | `2` |

Expected primary surfaces:

| Expected surface | Count |
| --- | ---: |
| `no_answer_contract_failure` | `53` |
| `evidence_or_content_failure` | `53` |
| `strict_span_or_granularity_surface` | `33` |
| `final_candidate_attractor` | `5` |
| `final_candidate_helpful_commitment` | `2` |

All `146` cards have `target_authority_alarm_expected = false`.

## Manual Seed Labels

The deterministic `24`-card seed has a first manual label pass:

| Label field | Counts |
| --- | --- |
| `primary_failure_surface` | `evidence_or_content_failure: 8`; `final_candidate_attractor: 5`; `strict_span_or_granularity_surface: 3`; `no_answer_contract_failure: 8` |
| `answer_contract_alarm` | `yes: 16`; `no: 8` |
| `target_authority_alarm` | `no: 22`; `soft: 2` |
| `short_span_alarm` | `yes: 8`; `no: 16` |
| `evidence_adequacy_alarm` | `yes: 8`; `no: 16` |

The useful outcome is not that every negative control is clean. Two seed cards
have a soft target-authority boundary:

- offset150 sample `165`, where the public target drifts toward Center for
  Veterinary Medicine spending rather than the asked spending object;
- offset150 sample `157` from `final_contract`, where the public target
  pre-identifies `Lush` and reframes the task as verification, while the primary
  error is still `Lush` versus `Lush Ltd.` granularity.

These soft cases are a warning for verifier design: a future audit should be
allowed to report secondary target-authority contamination without stealing the
primary label from evidence/content or final-span failures.

## Positive Versus Negative Seed

The positive audit seed has `50` selected target-layer focus records with
explicit contract risks:

- `21` answer-type or relation mismatches;
- `21` short-span or granularity mismatches;
- `3` public-target misdirections;
- `3` evidence-sentence or distractor copies;
- `2` question-root ambiguity regressions.

The negative seed changes the design target. It shows that an
answer-contract-aware audit can legitimately fire outside target-layer failures:
evidence/content controls need evidence-adequacy alarms, and final-answer
controls need final-candidate or short-span alarms. The selectivity target is
therefore not "alarm only on positives." It is:

- do not label stable controls as failures;
- do not label evidence/content failures as primary target-authority failures;
- do not label final-candidate or span failures as primary target-authority
  failures;
- allow soft secondary target-authority notes when public targets are visibly
  contaminated.

## Spot Check Read

The seed cards expose three distinct non-target surfaces:

- Stable controls should usually stay quiet. In the seed, examples such as
  offset100 sample `104` and offset150 sample `150` stay correct under
  public-state, frozen-target, and target-only conditions.
- Evidence/content controls are not fixed by the answer-contract lens. For
  example, offset100 sample `100` remains `Seminole County, Oklahoma` against
  gold `coahuila mexico` under public-state, frozen-target, and target-only
  conditions; this is an evidence/content adequacy problem.
- Final-answer controls are adjacent but different. Several
  `final_candidate_attractor_regression` rows are exact under no-final and
  target-only conditions, then fail only when the final candidate is visible.
  This should not be explained as target-authority failure.

The seed therefore gives a falsification path for the protocol: if a future
audit marks many stable controls or final-candidate controls as target-authority
failures, it is not selective enough.

## Caveats

- The packet carries selectivity expectations, not manual verifier labels.
- The seed is deterministic and small: four records per control layer per
  slice.
- Some final-answer controls are still legitimate answer-surface failures,
  especially strict span/granularity rows; they are negative controls only for
  target-authority overreach.
- Saved-field re-answering is still not a full PACT rerun.

## Next Pressure

Compare these `24` negative-control labels with the `50` positive target-layer
audit records before drafting a non-oracle verifier prompt. The first verifier
should predict a structured surface, not a single binary failure:

- target-authority alarm;
- answer type or relation alarm;
- short-span or granularity alarm;
- evidence-adequacy alarm;
- final-candidate commitment alarm.
