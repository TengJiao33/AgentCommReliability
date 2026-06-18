# PACT Final-Span And Granularity Audit

- Label: `pact-field-contract-quarantine`
- Evaluated rows: `100`
- Exact match: `0.610`
- Avg F1: `0.753`
- Strict-span/granularity errors: `13`

## By Condition

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion | partial_overlap_possible_alias_or_type |
| --- | ---: | ---: | ---: | ---: | ---: |
| verified_quarantine_risky_else_frozen_no_final | 23 | 61 | 7 | 6 | 3 |

## By Bridge Layer

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion | partial_overlap_possible_alias_or_type |
| --- | ---: | ---: | ---: | ---: | ---: |
| diagnostic_noise | 2 | 0 | 0 | 0 | 0 |
| evidence_carriage | 8 | 2 | 0 | 0 | 0 |
| final_answer_commitment | 5 | 8 | 4 | 4 | 3 |
| positive_contract_rescue | 4 | 7 | 1 | 0 | 0 |
| stable_right_or_not_focus | 0 | 41 | 2 | 1 | 0 |
| target_contract | 3 | 1 | 0 | 0 | 0 |
| target_final_alignment | 1 | 2 | 0 | 1 | 0 |

## By Source Run

| Slice | content_mismatch | exact | missing_required_token_or_qualifier | over_specific_or_sentence_expansion | partial_overlap_possible_alias_or_type |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline | 13 | 30 | 4 | 2 | 1 |
| final_contract | 10 | 31 | 3 | 4 | 2 |

## Highest-F1 Non-Exact Rows

| Sample | Source | Condition | Family | F1 | Gold | Prediction |
| ---: | --- | --- | --- | ---: | --- | --- |
| 66 | baseline | verified_quarantine_risky_else_frozen_no_final | over_specific_or_sentence_expansion | 0.909 | international boxing hall of fame | International Boxing Hall of Fame (IBHOF) |
| 66 | final_contract | verified_quarantine_risky_else_frozen_no_final | over_specific_or_sentence_expansion | 0.909 | international boxing hall of fame | International Boxing Hall of Fame (IBHOF) |
| 50 | baseline | verified_quarantine_risky_else_frozen_no_final | missing_required_token_or_qualifier | 0.857 | 2009 big 12 conference | 2009, Big 12 |
| 50 | final_contract | verified_quarantine_risky_else_frozen_no_final | missing_required_token_or_qualifier | 0.857 | 2009 big 12 conference | 2009, Big 12 |
| 60 | final_contract | verified_quarantine_risky_else_frozen_no_final | over_specific_or_sentence_expansion | 0.857 | shortest player ever to play in national basketball association | Muggsy Bogues is the shortest player ever to play in the National Basketball Association. |
| 75 | baseline | verified_quarantine_risky_else_frozen_no_final | missing_required_token_or_qualifier | 0.800 | john john florence | John Florence |
| 75 | final_contract | verified_quarantine_risky_else_frozen_no_final | missing_required_token_or_qualifier | 0.800 | john john florence | John Florence |
| 83 | baseline | verified_quarantine_risky_else_frozen_no_final | missing_required_token_or_qualifier | 0.800 | mondelez international inc | Mondelez International |
| 83 | final_contract | verified_quarantine_risky_else_frozen_no_final | missing_required_token_or_qualifier | 0.800 | mondelez international inc | Mondelez International |
| 95 | final_contract | verified_quarantine_risky_else_frozen_no_final | over_specific_or_sentence_expansion | 0.800 | fairfax county | Fairfax County, Virginia |
| 89 | baseline | verified_quarantine_risky_else_frozen_no_final | over_specific_or_sentence_expansion | 0.667 | director | film director |
| 89 | final_contract | verified_quarantine_risky_else_frozen_no_final | over_specific_or_sentence_expansion | 0.667 | director | film director |
| 92 | baseline | verified_quarantine_risky_else_frozen_no_final | partial_overlap_possible_alias_or_type | 0.545 | las vegas strip in paradise | Flamingo Hotel in Las Vegas, Nevada. |
| 85 | baseline | verified_quarantine_risky_else_frozen_no_final | missing_required_token_or_qualifier | 0.500 | april 1 1949 | 1949 |
| 92 | final_contract | verified_quarantine_risky_else_frozen_no_final | partial_overlap_possible_alias_or_type | 0.500 | las vegas strip in paradise | Flamingo Las Vegas |
| 97 | final_contract | verified_quarantine_risky_else_frozen_no_final | partial_overlap_possible_alias_or_type | 0.500 | levni yilmaz | Lev Yilmaz |
| 57 | baseline | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.444 | keith bostic | Keith Bostic is younger than Jerry Glanville. |
| 57 | final_contract | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.444 | keith bostic | Keith Bostic is younger than Jerry Glanville. |
| 74 | baseline | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.400 | william jefferson clinton | Bill Clinton |
| 74 | final_contract | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.400 | william jefferson clinton | Bill Clinton |
| 62 | baseline | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.364 | adeline virginia woolf | Virginia Woolf was born earlier than Emma Bull. |
| 62 | final_contract | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.364 | adeline virginia woolf | Emma Bull was born later than Virginia Woolf. |
| 60 | baseline | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.118 | shortest player ever to play in national basketball association | Muggys Bogues is the shortest answer span as he is the former NBA player mentioned in the question. However, if the question seeks a specific distinction, the relevant span is "shortest player in NBA history," which is a well-known distinction for Muggsy Bogues, though not explicitly stated in the given |
| 58 | final_contract | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.000 | 35124 | 273 |
| 59 | baseline | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.000 | no | Ajuga is a genus, but Cypress is not specified in the given evidence. Therefore, based on the provided information, the answer is partially confirmed as only Ajuga is explicitly stated to be a genus. |
| 59 | final_contract | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.000 | no | Yes |
| 61 | baseline | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.000 | ronald shusett | The executive producer is not mentioned in the provided context. |
| 68 | baseline | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.000 | bill murray | Kenny |
| 68 | final_contract | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.000 | bill murray | Thomas Middleditch |
| 77 | baseline | verified_quarantine_risky_else_frozen_no_final | content_mismatch | 0.000 | apalachees | Ais tribe |

## Caveat

This audit uses gold answers and is an evaluation diagnostic, not a runtime verifier.
It separates strict-span and granularity pressure from clear content errors before another behavioral run.
