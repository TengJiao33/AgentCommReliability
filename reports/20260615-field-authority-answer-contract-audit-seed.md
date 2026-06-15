# Field-Authority Answer-Contract Audit Seed

Date: 2026-06-15

## What This Is

This is a manual/oracle seed for an answer-contract audit. It converts the
cross-slice semantic focus labels into protocol fields:

- required contract checks;
- contract risk;
- recommended downstream action;
- observed behavior under public-state, frozen-target, target-only, and
  hide-target conditions.

Artifacts:

- `scripts/build_pact_answer_contract_audit_seed.py`
- `experiments/20260615-local-pact-answer-contract-audit-seed/audit_seed_records.jsonl`
- `experiments/20260615-local-pact-answer-contract-audit-seed/audit_seed.md`
- `experiments/20260615-local-pact-answer-contract-audit-seed/summary.json`

This is not a runtime verifier. It is a positive-control protocol sketch over
already selected target-layer focus cards.

## Counts

| Item | Count |
| --- | ---: |
| Audit seed records | `50` |
| offset100 records | `28` |
| offset150 records | `22` |
| public-target-only unsafe | `48` |
| frozen question target sufficient | `43` |
| needs evidence-adequacy guard | `2` |

Contract risks:

| Contract risk | Count |
| --- | ---: |
| `answer_type_or_relation_mismatch` | `21` |
| `short_span_or_granularity_mismatch` | `21` |
| `public_target_misdirects_relation` | `3` |
| `evidence_sentence_or_distractor_copy` | `3` |
| `question_root_can_reopen_ambiguity` | `2` |

Recommended actions:

| Action | Count |
| --- | ---: |
| `keep_question_root_or_freeze_question_target` | `21` |
| `keep_question_root_and_short_span_constraint` | `21` |
| `hide_public_target_or_freeze_question_target` | `3` |
| `question_attended_short_answer_extraction` | `3` |
| `do_not_freeze_without_evidence_adequacy_check` | `2` |

## What It Shows

The protocol seed clarifies the current live handle:

**The unsafe object is not merely a bad `Action Required` string. The missing
object is an answer contract: answer type or relation, short-span granularity,
and evidence adequacy against the trusted question root.**

The frozen question root is usually useful on these focus cards, but not always:

- `43/50` focus cards are solved by the frozen-question target condition;
- `2/50` are explicit boundary regressions where question-root projection hurts;
- several span/granularity records need more than just freezing, because the
  answer must also be constrained to the expected short span.

## Why This Matters

This turns the next intervention from a vague detector into a falsifiable audit
surface. A future non-oracle verifier should try to predict these contract-risk
fields before seeing the model outcome.

The first real specificity test should add negative controls:

- stable public-state units;
- evidence/content mismatch units;
- final-answer commitment units.

If the same audit fires on everything, it is just vocabulary. If it separates
target-layer focus units from non-target units, it becomes a useful protocol
candidate.

## Caveats

- The records are manually seeded from focus cards; this is not automatic.
- The focus cards are already positive target-layer cases, so this does not
  measure specificity.
- HotpotQA exact-match span artifacts remain mixed into
  `short_span_or_granularity`.
- Saved-field re-answering is still not a full PACT rerun.

## Next Pressure

Build a matched negative-control audit packet from offset100/offset150 bridge
cases:

- stable-answer units;
- evidence/content units;
- final-answer commitment units.

Then test whether the answer-contract audit fields stay concentrated in
target-layer failures.

