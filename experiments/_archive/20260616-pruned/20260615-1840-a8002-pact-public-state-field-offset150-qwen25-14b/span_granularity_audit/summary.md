# PACT Final-Span And Granularity Audit

- Label: `pact-public-state-field-offset150`
- Evaluated rows: `500`
- Exact match: `0.418`
- Avg F1: `0.593`
- Strict-span/granularity errors: `101`

## By Condition

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion | partial_overlap_possible_alias_or_type |
| --- | ---: | ---: | ---: | ---: | ---: |
| frozen_target_plus_evidence_no_final | 29 | 48 | 7 | 15 | 1 |
| public_target_plus_evidence_no_question_no_final | 51 | 31 | 4 | 13 | 1 |
| question_plus_evidence_no_target_no_final | 32 | 45 | 6 | 16 | 1 |
| question_plus_public_state_no_final | 37 | 42 | 6 | 14 | 1 |
| question_plus_public_state_with_final | 35 | 43 | 8 | 12 | 2 |

## By Bridge Layer

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion | partial_overlap_possible_alias_or_type |
| --- | ---: | ---: | ---: | ---: | ---: |
| stable_right_or_not_focus | 184 | 209 | 31 | 70 | 6 |

## By Source Run

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion | partial_overlap_possible_alias_or_type |
| --- | ---: | ---: | ---: | ---: | ---: |
| compact_final_contract | 90 | 109 | 14 | 31 | 6 |
| final_contract | 94 | 100 | 17 | 39 | 0 |

## Highest-F1 Non-Exact Rows

| Sample | Source | Condition | Family | F1 | Gold | Prediction |
| ---: | --- | --- | --- | ---: | --- | --- |
| 177 | final_contract | question_plus_public_state_with_final | missing_required_token_or_qualifier | 0.889 | between 8th and 16th centuries | 8th and 16th centuries |
| 158 | final_contract | question_plus_public_state_with_final | over_specific_or_sentence_expansion | 0.800 | manchester united | Manchester United F.C. |
| 158 | final_contract | question_plus_public_state_no_final | over_specific_or_sentence_expansion | 0.800 | manchester united | Manchester United F.C. |
| 158 | final_contract | question_plus_evidence_no_target_no_final | over_specific_or_sentence_expansion | 0.800 | manchester united | Manchester United F.C. |
| 158 | final_contract | frozen_target_plus_evidence_no_final | over_specific_or_sentence_expansion | 0.800 | manchester united | Manchester United F.C. |
| 163 | compact_final_contract | question_plus_public_state_no_final | missing_required_token_or_qualifier | 0.800 | kelly lee osbourne | Kelly Osbourne |
| 163 | compact_final_contract | question_plus_evidence_no_target_no_final | missing_required_token_or_qualifier | 0.800 | kelly lee osbourne | Kelly Osbourne |
| 163 | compact_final_contract | frozen_target_plus_evidence_no_final | missing_required_token_or_qualifier | 0.800 | kelly lee osbourne | Kelly Osbourne |
| 163 | final_contract | question_plus_public_state_with_final | missing_required_token_or_qualifier | 0.800 | kelly lee osbourne | Kelly Osbourne |
| 163 | final_contract | question_plus_public_state_no_final | missing_required_token_or_qualifier | 0.800 | kelly lee osbourne | Kelly Osbourne |
| 163 | final_contract | frozen_target_plus_evidence_no_final | missing_required_token_or_qualifier | 0.800 | kelly lee osbourne | Kelly Osbourne |
| 163 | final_contract | public_target_plus_evidence_no_question_no_final | missing_required_token_or_qualifier | 0.800 | kelly lee osbourne | Kelly Osbourne |
| 173 | compact_final_contract | question_plus_public_state_no_final | over_specific_or_sentence_expansion | 0.800 | pasek paul | Pasek and Paul |
| 173 | compact_final_contract | question_plus_evidence_no_target_no_final | over_specific_or_sentence_expansion | 0.800 | pasek paul | Pasek and Paul |
| 173 | final_contract | question_plus_public_state_with_final | over_specific_or_sentence_expansion | 0.800 | pasek paul | Pasek and Paul |
| 173 | final_contract | question_plus_public_state_no_final | over_specific_or_sentence_expansion | 0.800 | pasek paul | Pasek and Paul |
| 173 | final_contract | question_plus_evidence_no_target_no_final | over_specific_or_sentence_expansion | 0.800 | pasek paul | Pasek and Paul |
| 173 | final_contract | frozen_target_plus_evidence_no_final | over_specific_or_sentence_expansion | 0.800 | pasek paul | Pasek and Paul |
| 173 | final_contract | public_target_plus_evidence_no_question_no_final | over_specific_or_sentence_expansion | 0.800 | pasek paul | Pasek and Paul |
| 190 | compact_final_contract | question_plus_public_state_with_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 190 | compact_final_contract | question_plus_public_state_no_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 190 | compact_final_contract | question_plus_evidence_no_target_no_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 190 | compact_final_contract | frozen_target_plus_evidence_no_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 190 | compact_final_contract | public_target_plus_evidence_no_question_no_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 190 | final_contract | question_plus_public_state_with_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 190 | final_contract | question_plus_public_state_no_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 190 | final_contract | question_plus_evidence_no_target_no_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 190 | final_contract | frozen_target_plus_evidence_no_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 190 | final_contract | public_target_plus_evidence_no_question_no_final | missing_required_token_or_qualifier | 0.800 | oregon ducks football | Oregon Ducks |
| 157 | compact_final_contract | question_plus_public_state_with_final | missing_required_token_or_qualifier | 0.667 | lush ltd | Lush |

## Caveat

This audit uses gold answers and is an evaluation diagnostic, not a runtime verifier.
It separates strict-span and granularity pressure from clear content errors before another behavioral run.
