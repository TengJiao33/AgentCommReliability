# PACT Final-Span And Granularity Audit

- Label: `pact-public-state-field-offset100`
- Evaluated rows: `500`
- Exact match: `0.452`
- Avg F1: `0.602`
- Strict-span/granularity errors: `101`

## By Condition

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion |
| --- | ---: | ---: | ---: | ---: |
| frozen_target_plus_evidence_no_final | 25 | 56 | 4 | 15 |
| public_target_plus_evidence_no_question_no_final | 45 | 30 | 7 | 18 |
| question_plus_evidence_no_target_no_final | 34 | 47 | 5 | 14 |
| question_plus_public_state_no_final | 30 | 50 | 7 | 13 |
| question_plus_public_state_with_final | 39 | 43 | 7 | 11 |

## By Bridge Layer

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion |
| --- | ---: | ---: | ---: | ---: |
| stable_right_or_not_focus | 173 | 226 | 30 | 71 |

## By Source Run

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion |
| --- | ---: | ---: | ---: | ---: |
| baseline | 81 | 111 | 17 | 41 |
| final_contract | 92 | 115 | 13 | 30 |

## Highest-F1 Non-Exact Rows

| Sample | Source | Condition | Family | F1 | Gold | Prediction |
| ---: | --- | --- | --- | ---: | --- | --- |
| 138 | final_contract | question_plus_public_state_no_final | missing_required_token_or_qualifier | 0.889 | seasonal television specials particularly its work in stop motion animation | seasonal television specials, particularly in stop motion animation |
| 138 | final_contract | frozen_target_plus_evidence_no_final | missing_required_token_or_qualifier | 0.889 | seasonal television specials particularly its work in stop motion animation | seasonal television specials, particularly in stop motion animation. |
| 103 | baseline | question_plus_public_state_no_final | over_specific_or_sentence_expansion | 0.833 | north avenue at techwood drive | the corner of North Avenue at Techwood Drive |
| 103 | final_contract | question_plus_public_state_with_final | over_specific_or_sentence_expansion | 0.833 | north avenue at techwood drive | corner of North Avenue at Techwood Drive |
| 103 | final_contract | public_target_plus_evidence_no_question_no_final | over_specific_or_sentence_expansion | 0.833 | north avenue at techwood drive | corner of North Avenue at Techwood Drive |
| 123 | baseline | question_plus_public_state_with_final | over_specific_or_sentence_expansion | 0.800 | kkr co | KKR & Co. L.P. |
| 123 | baseline | question_plus_public_state_no_final | over_specific_or_sentence_expansion | 0.800 | kkr co | KKR & Co. L.P. |
| 123 | baseline | question_plus_evidence_no_target_no_final | over_specific_or_sentence_expansion | 0.800 | kkr co | KKR & Co. L.P. |
| 123 | baseline | frozen_target_plus_evidence_no_final | over_specific_or_sentence_expansion | 0.800 | kkr co | KKR & Co. L.P. |
| 123 | baseline | public_target_plus_evidence_no_question_no_final | over_specific_or_sentence_expansion | 0.800 | kkr co | KKR & Co. L.P. |
| 123 | final_contract | public_target_plus_evidence_no_question_no_final | over_specific_or_sentence_expansion | 0.800 | kkr co | KKR & Co. L.P. |
| 142 | baseline | question_plus_public_state_no_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 142 | baseline | question_plus_evidence_no_target_no_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 142 | baseline | public_target_plus_evidence_no_question_no_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 142 | final_contract | question_plus_public_state_with_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 142 | final_contract | question_plus_public_state_no_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 142 | final_contract | question_plus_evidence_no_target_no_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 142 | final_contract | frozen_target_plus_evidence_no_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 142 | final_contract | public_target_plus_evidence_no_question_no_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 103 | baseline | question_plus_public_state_with_final | over_specific_or_sentence_expansion | 0.769 | north avenue at techwood drive | at the corner of North Avenue at Techwood Drive |
| 103 | baseline | question_plus_evidence_no_target_no_final | over_specific_or_sentence_expansion | 0.769 | north avenue at techwood drive | at the corner of North Avenue at Techwood Drive |
| 103 | baseline | frozen_target_plus_evidence_no_final | over_specific_or_sentence_expansion | 0.769 | north avenue at techwood drive | at the corner of North Avenue at Techwood Drive |
| 103 | final_contract | question_plus_public_state_no_final | over_specific_or_sentence_expansion | 0.769 | north avenue at techwood drive | at the corner of North Avenue at Techwood Drive |
| 103 | final_contract | question_plus_evidence_no_target_no_final | over_specific_or_sentence_expansion | 0.769 | north avenue at techwood drive | at the corner of North Avenue at Techwood Drive |
| 103 | final_contract | frozen_target_plus_evidence_no_final | over_specific_or_sentence_expansion | 0.769 | north avenue at techwood drive | at the corner of North Avenue at Techwood Drive |
| 147 | baseline | question_plus_public_state_no_final | over_specific_or_sentence_expansion | 0.750 | kingdom of isles | Kingdom of Mann and the Isles |
| 147 | baseline | question_plus_evidence_no_target_no_final | over_specific_or_sentence_expansion | 0.750 | kingdom of isles | Kingdom of Mann and the Isles |
| 147 | baseline | frozen_target_plus_evidence_no_final | over_specific_or_sentence_expansion | 0.750 | kingdom of isles | Kingdom of Mann and the Isles |
| 147 | baseline | public_target_plus_evidence_no_question_no_final | over_specific_or_sentence_expansion | 0.750 | kingdom of isles | Kingdom of Mann and the Isles |
| 147 | final_contract | question_plus_public_state_no_final | over_specific_or_sentence_expansion | 0.750 | kingdom of isles | Kingdom of Mann and the Isles |

## Caveat

This audit uses gold answers and is an evaluation diagnostic, not a runtime verifier.
It separates strict-span and granularity pressure from clear content errors before another behavioral run.
