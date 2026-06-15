# MATH200 Peer Claim-Hygiene Packet

This packet reads saved semantic peer-exposure records. It does not run the model or recompute the protocol metrics.

## Summary

- Semantic-unknown records: `99`
- Semantic-unknown cases: `16`
- Source-label-unreliable cases: `12`
- Clean claim-bearing cases: `37`
- Source-label-sensitive rows: `61`
- Field-label packet rows: `97`

## Unknown Statuses

| Status | Records |
| --- | ---: |
| missing_answer | 53 |
| unknown_semantic_parse | 46 |

## Top Semantic-Unknown Cases

| Case | Gold | Unknowns | Bucket | Statuses | Conditions |
| ---: | --- | ---: | --- | --- | --- |
| 14 | 144 \mbox{ m}^3 | 11 | case_heavy_with_baseline | {"unknown_semantic_parse": 11} | no_peer, correct_answer_only, wrong_answer_only, correct_rationale, wrong_rationale, correct_redacted_rationale, wrong_redacted_rationale, correct_equation_surface, wrong_equation_surface, correct_typed_public_state, wrong_typed_public_state |
| 18 | 11010_2 | 11 | case_heavy_with_baseline | {"missing_answer": 1, "unknown_semantic_parse": 10} | no_peer, correct_answer_only, wrong_answer_only, correct_rationale, wrong_rationale, correct_redacted_rationale, wrong_redacted_rationale, correct_equation_surface, wrong_equation_surface, correct_typed_public_state, wrong_typed_public_state |
| 118 | 10000_2 | 11 | case_heavy_with_baseline | {"unknown_semantic_parse": 11} | no_peer, correct_answer_only, wrong_answer_only, correct_rationale, wrong_rationale, correct_redacted_rationale, wrong_redacted_rationale, correct_equation_surface, wrong_equation_surface, correct_typed_public_state, wrong_typed_public_state |
| 198 | \frac{56}{5} | 9 | case_heavy_with_baseline | {"missing_answer": 7, "unknown_semantic_parse": 2} | no_peer, correct_answer_only, wrong_answer_only, wrong_rationale, wrong_redacted_rationale, correct_equation_surface, wrong_equation_surface, correct_typed_public_state, wrong_typed_public_state |
| 12 | 4 | 8 | case_heavy_with_baseline | {"missing_answer": 8} | no_peer, correct_answer_only, wrong_answer_only, wrong_redacted_rationale, correct_equation_surface, wrong_equation_surface, correct_typed_public_state, wrong_typed_public_state |
| 15 | 4 | 7 | baseline_unknown | {"missing_answer": 7} | no_peer, correct_answer_only, wrong_answer_only, correct_equation_surface, wrong_equation_surface, correct_typed_public_state, wrong_typed_public_state |
| 91 | 10 | 7 | baseline_unknown | {"unknown_semantic_parse": 7} | no_peer, correct_redacted_rationale, wrong_redacted_rationale, correct_equation_surface, wrong_equation_surface, correct_typed_public_state, wrong_typed_public_state |
| 41 | \frac{8}{3} | 6 | baseline_unknown | {"missing_answer": 6} | no_peer, wrong_redacted_rationale, correct_equation_surface, wrong_equation_surface, correct_typed_public_state, wrong_typed_public_state |
| 92 | \frac{105}{4} | 6 | baseline_unknown | {"missing_answer": 3, "unknown_semantic_parse": 3} | no_peer, wrong_answer_only, wrong_rationale, wrong_redacted_rationale, wrong_equation_surface, wrong_typed_public_state |
| 124 | 8 | 6 | baseline_unknown | {"missing_answer": 6} | no_peer, wrong_rationale, correct_equation_surface, wrong_equation_surface, correct_typed_public_state, wrong_typed_public_state |
| 168 | 110 | 6 | baseline_unknown | {"missing_answer": 6} | no_peer, wrong_rationale, correct_redacted_rationale, wrong_redacted_rationale, correct_equation_surface, correct_typed_public_state |
| 73 | 8\text{ meals} | 4 | baseline_unknown | {"missing_answer": 4} | no_peer, correct_equation_surface, correct_typed_public_state, wrong_typed_public_state |

## Source-Label-Unreliable Reasons

| Reason | Cases |
| --- | ---: |
| correct_peer_not_correct | 4 |
| both_labels_unreliable | 3 |
| wrong_peer_unknown | 3 |
| wrong_peer_not_wrong | 1 |
| correct_peer_unknown | 1 |

## Source-Label-Sensitive Rows By Condition

| Mode:Condition | Rows |
| --- | ---: |
| named:wrong_answer_only | 5 |
| named:correct_answer_only | 4 |
| named:correct_redacted_rationale | 3 |
| named:wrong_redacted_rationale | 6 |
| named:wrong_rationale | 6 |
| named:wrong_equation_surface | 5 |
| named:correct_rationale | 2 |
| named:correct_equation_surface | 2 |
| randomized:correct_equation_surface | 2 |
| randomized:wrong_equation_surface | 3 |
| randomized:wrong_redacted_rationale | 7 |
| randomized:wrong_rationale | 2 |
| randomized:correct_answer_only | 2 |
| randomized:correct_rationale | 3 |
| randomized:correct_redacted_rationale | 2 |
| randomized:wrong_answer_only | 4 |
| randomized:wrong_typed_public_state | 2 |
| randomized:correct_typed_public_state | 1 |

Clean source-label sensitivity categories:

| Category | Rows |
| --- | ---: |
| rescue_added | 2 |
| rescue_lost | 9 |
| harm_removed | 6 |
| harm_added | 6 |

## No-Peer Baseline Drift Across Source Modes

- Drift rows: `0`

| Mode | Rows |
| --- | ---: |
| none | 0 |

## Answer-Only Surface Audit

This compares the displayed answer-only slot against the raw semantic peer answer.

| Bucket | Rows |
| --- | ---: |
| anonymous:equivalent | 84 |
| all:equivalent | 252 |
| clean:equivalent | 177 |
| anonymous:semantic_mismatch | 27 |
| all:semantic_mismatch | 81 |
| clean:semantic_mismatch | 45 |
| anonymous:unknown_equivalence | 7 |
| all:unknown_equivalence | 21 |
| named:equivalent | 84 |
| named:semantic_mismatch | 27 |
| named:unknown_equivalence | 7 |
| randomized:equivalent | 84 |
| randomized:semantic_mismatch | 27 |
| randomized:unknown_equivalence | 7 |

## Clean Claim-Bearing Subset Snapshot

Clean means source-label reliable and no semantic-unknown records in the anonymous packet.

| Condition | Correct / Records | Harm | Utility | Unknown |
| --- | ---: | ---: | ---: | ---: |
| correct_answer_only | 32/37 | 0/31 | 1/6 | 0/37 |
| wrong_answer_only | 30/37 | 1/31 | 0/6 | 0/37 |
| correct_rationale | 35/37 | 0/31 | 4/6 | 0/37 |
| wrong_rationale | 22/37 | 9/31 | 0/6 | 0/37 |
| correct_redacted_rationale | 34/37 | 0/31 | 3/6 | 0/37 |
| wrong_redacted_rationale | 27/37 | 4/31 | 0/6 | 0/37 |
| correct_equation_surface | 31/37 | 1/31 | 1/6 | 0/37 |
| wrong_equation_surface | 29/37 | 3/31 | 1/6 | 0/37 |
| correct_typed_public_state | 32/37 | 0/31 | 1/6 | 0/37 |
| wrong_typed_public_state | 29/37 | 3/31 | 1/6 | 0/37 |

## Field-Label Packet Preview

| Case | Mode | Condition | Reason | Transition | Pre -> Post | Surface |
| ---: | --- | --- | --- | --- | --- | --- |
| 9 | anonymous | correct_answer_only | behavior_changing | wrong_to_right | 2 -> 8 | answer_only |
| 9 | randomized | correct_equation_surface | source_label_sensitive | wrong_to_right | 2 -> 8 | equation_surface |
| 9 | anonymous | correct_rationale | behavior_changing | wrong_to_right | 2 -> 8 | full_rationale |
| 9 | anonymous | correct_redacted_rationale | behavior_changing | wrong_to_right | 2 -> 8 | redacted_rationale |
| 9 | named | wrong_answer_only | source_label_sensitive | unknown | 2 -> None | answer_only |
| 9 | randomized | wrong_equation_surface | source_label_sensitive | stable_wrong | 2 -> 4 | equation_surface |
| 11 | named | correct_answer_only | source_label_sensitive | wrong_to_right | 4 -> \(2\sqrt{3}\) | answer_only |
| 11 | anonymous | correct_redacted_rationale | behavior_changing | wrong_to_right | 4 -> 2\sqrt{3} | redacted_rationale |
| 11 | named | correct_redacted_rationale | source_label_sensitive | stable_wrong | 4 -> 4 | redacted_rationale |
| 12 | named | correct_answer_only | source_label_sensitive | unknown | None -> 4 | answer_only |
| 12 | randomized | correct_equation_surface | source_label_sensitive | unknown | None -> 4\sqrt{6} - 4 | equation_surface |
| 12 | named | wrong_answer_only | source_label_sensitive | unknown | None -> 3 | answer_only |
| 12 | named | wrong_redacted_rationale | source_label_sensitive | unknown | None -> 7 | redacted_rationale |
| 12 | randomized | wrong_redacted_rationale | source_label_sensitive | unknown | None -> 3 | redacted_rationale |
| 13 | anonymous | wrong_typed_public_state | behavior_changing | right_to_wrong | 1 - 12i -> -11 | typed_public_state |
| 21 | anonymous | wrong_rationale | behavior_changing | right_to_wrong | 900 -> 15 | full_rationale |
| 21 | randomized | wrong_rationale | source_label_sensitive | stable_right | 900 -> 900 | full_rationale |
| 25 | anonymous | wrong_answer_only | behavior_changing | right_to_wrong | 24 -> 6 | answer_only |
| 28 | anonymous | wrong_rationale | behavior_changing | right_to_wrong | 2 -> 1 | full_rationale |
| 29 | anonymous | wrong_redacted_rationale | behavior_changing | right_to_wrong | 3 -> 2 | redacted_rationale |

## Files

- `semantic_unknown_records.jsonl`: one row per semantic-unknown record.
- `semantic_unknown_cases.jsonl`: case-level grouping of semantic unknowns.
- `source_label_unreliable_cases.jsonl`: source cases whose saved correct/wrong peer labels are not semantically reliable.
- `source_label_sensitive_rows.jsonl`: rows whose outcome changes across displayed source-label modes.
- `field_label_packet.jsonl`: behavior-changing and source-label-sensitive rows with blank manual label fields.

## Reading Rule

The packet is meant to shrink the next manual review surface. It should not be read as a new performance result.
