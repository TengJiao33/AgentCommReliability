# PACT Final-Span And Granularity Audit

- Label: `pact-field-authority-projection-offset100`
- Evaluated rows: `200`
- Exact match: `0.475`
- Avg F1: `0.633`
- Strict-span/granularity errors: `42`

## By Condition

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion |
| --- | ---: | ---: | ---: | ---: |
| security_projection_question_root_no_final | 27 | 51 | 4 | 18 |
| standalone_authority_quarantine_no_final | 36 | 44 | 4 | 16 |

## By Bridge Layer

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion |
| --- | ---: | ---: | ---: | ---: |
| stable_right_or_not_focus | 63 | 95 | 8 | 34 |

## By Source Run

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion |
| --- | ---: | ---: | ---: | ---: |
| baseline | 30 | 48 | 4 | 18 |
| final_contract | 33 | 47 | 4 | 16 |

## Highest-F1 Non-Exact Rows

| Sample | Source | Condition | Family | F1 | Gold | Prediction |
| ---: | --- | --- | --- | ---: | --- | --- |
| 138 | final_contract | standalone_authority_quarantine_no_final | missing_required_token_or_qualifier | 0.889 | seasonal television specials particularly its work in stop motion animation | seasonal television specials, particularly in stop motion animation. |
| 123 | baseline | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.800 | kkr co | KKR & Co. L.P. |
| 123 | baseline | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.800 | kkr co | KKR & Co. L.P. |
| 142 | final_contract | security_projection_question_root_no_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 142 | final_contract | standalone_authority_quarantine_no_final | missing_required_token_or_qualifier | 0.800 | teach controversy campaign | "Teach the Controversy" |
| 130 | baseline | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.769 | lalees kin legacy of cotton | LaLee's Kin: The Legacy of Cotton was Oscar nominated. |
| 147 | baseline | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.750 | kingdom of isles | Kingdom of Mann and the Isles |
| 147 | baseline | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.750 | kingdom of isles | Kingdom of Mann and the Isles |
| 147 | final_contract | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.750 | kingdom of isles | Kingdom of Mann and the Isles |
| 147 | final_contract | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.750 | kingdom of isles | Kingdom of Mann and the Isles |
| 130 | baseline | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.714 | lalees kin legacy of cotton | LaLee's Kin: The Legacy of Cotton was nominated for an Oscar. |
| 116 | baseline | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.667 | marvel | Marvel Comics |
| 116 | final_contract | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.667 | marvel | Marvel Comics |
| 123 | final_contract | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.667 | kkr co | KKR & Co. L.P. (KKR) |
| 125 | baseline | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.667 | richmond | Richmond River |
| 125 | baseline | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.667 | richmond | Richmond River |
| 125 | final_contract | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.667 | richmond | Richmond River |
| 125 | final_contract | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.667 | richmond | Richmond River |
| 140 | baseline | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.667 | oxford | Oxford University |
| 140 | baseline | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.667 | oxford | Oxford University |
| 140 | final_contract | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.667 | oxford | Oxford University |
| 140 | final_contract | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.667 | oxford | Oxford University |
| 103 | baseline | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.625 | north avenue at techwood drive | The stadium is located at the corner of North Avenue at Techwood Drive. |
| 103 | final_contract | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.625 | north avenue at techwood drive | The stadium is located at the corner of North Avenue at Techwood Drive. |
| 127 | baseline | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.600 | late 12th century | The palace was founded in the late 12th Century. |
| 127 | final_contract | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.600 | late 12th century | The palace was founded in the late 12th Century. |
| 145 | baseline | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.571 | erika jayne | Erika Jayne was born first. |
| 145 | baseline | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.571 | erika jayne | Erika Jayne was born first. |
| 145 | final_contract | security_projection_question_root_no_final | over_specific_or_sentence_expansion | 0.571 | erika jayne | Erika Jayne was born first. |
| 145 | final_contract | standalone_authority_quarantine_no_final | over_specific_or_sentence_expansion | 0.571 | erika jayne | Erika Jayne was born first. |

## Caveat

This audit uses gold answers and is an evaluation diagnostic, not a runtime verifier.
It separates strict-span and granularity pressure from clear content errors before another behavioral run.
