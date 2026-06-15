# PACT Field Packet Delta Audit

Base condition: `question_plus_public_state_no_final`

## Condition Deltas

| Slice | base_wrong_to_variant_right | base_right_to_variant_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze_question_target | 10 | 4 | 48 | 38 |
| hide_public_target | 11 | 4 | 48 | 37 |
| hide_question_keep_public_target | 2 | 10 | 42 | 46 |
| show_final_answer_candidate | 6 | 3 | 49 | 42 |

## By Source Run

| Slice | base_wrong_to_variant_right | base_right_to_variant_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze_question_target | baseline | 4 | 2 | 26 | 18 |
| freeze_question_target | final_contract | 6 | 2 | 22 | 20 |
| hide_public_target | baseline | 2 | 1 | 27 | 20 |
| hide_public_target | final_contract | 9 | 3 | 21 | 17 |
| hide_question_keep_public_target | baseline | 1 | 6 | 22 | 21 |
| hide_question_keep_public_target | final_contract | 1 | 4 | 20 | 25 |
| show_final_answer_candidate | baseline | 4 | 2 | 26 | 18 |
| show_final_answer_candidate | final_contract | 2 | 1 | 23 | 24 |

## By Target Candidate

| Slice | base_wrong_to_variant_right | base_right_to_variant_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze_question_target | target_candidate=False | 9 | 2 | 46 | 27 |
| freeze_question_target | target_candidate=True | 1 | 2 | 2 | 11 |
| hide_public_target | target_candidate=False | 7 | 4 | 44 | 29 |
| hide_public_target | target_candidate=True | 4 | 0 | 4 | 8 |
| hide_question_keep_public_target | target_candidate=False | 2 | 9 | 39 | 34 |
| hide_question_keep_public_target | target_candidate=True | 0 | 1 | 3 | 12 |
| show_final_answer_candidate | target_candidate=False | 6 | 2 | 46 | 30 |
| show_final_answer_candidate | target_candidate=True | 0 | 1 | 3 | 12 |

## Hide Public Target Rescues

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 50 | final_contract | final_answer_commitment/missing_required_token_or_qualifier | False | 2009 big 12 conference | 2009, Big 12 | 2009 Big 12 Conference |
| 52 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | indianapolis motor speedway | Indianapolis Motor Speedway hosts a 500 mile race every May in the Midwest. | Indianapolis Motor Speedway |
| 54 | final_contract | final_answer_commitment/strict_span_regression_with_soft_target_shift | True | max martin savan kotecha and ilya salmanzadeh | Max Martin, Savan Kotecha, Ilya Salmanzadeh | Max Martin, Savan Kotecha and Ilya Salmanzadeh |
| 55 | final_contract | final_answer_commitment/missing_required_token_or_qualifier | True | marion south australia | 1961 | Marion, South Australia |
| 64 | final_contract | final_answer_commitment/strict_span_regression | False | more than 70 countries | 70 | more than 70 countries |
| 67 | final_contract | target_final_alignment/wrong_answer_type_or_slot | False | usher | "Yeah!" | Usher |
| 71 | baseline | evidence_carriage/likely_evidence_or_reasoning_failure | False | 276170 inhabitants | 276,170 | 276,170 inhabitants |
| 85 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | False | april 1 1949 | 1949 | April 1, 1949 |
| 87 | baseline | final_answer_commitment/over_specific_answer | True | canary islands spain | La Gomera, Canary Islands, Spain | Canary Islands, Spain |
| 87 | final_contract | final_answer_commitment/over_specific_answer | True | canary islands spain | Tenerife, Canary Islands, Spain and La Gomera, Canary Islands, Spain | Canary Islands, Spain |
| 95 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | fairfax county | Fairfax County, Virginia | Fairfax County |

## Freeze Target Rescues

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 52 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | indianapolis motor speedway | Indianapolis Motor Speedway hosts a 500 mile race every May in the Midwest. | Indianapolis Motor Speedway |
| 54 | final_contract | final_answer_commitment/strict_span_regression_with_soft_target_shift | True | max martin savan kotecha and ilya salmanzadeh | Max Martin, Savan Kotecha, Ilya Salmanzadeh | Max Martin, Savan Kotecha and Ilya Salmanzadeh |
| 59 | baseline | diagnostic_noise/false_positive_string_signal | False | no | Ajuga is a genus. | No |
| 64 | final_contract | final_answer_commitment/strict_span_regression | False | more than 70 countries | 70 | more than 70 countries |
| 67 | final_contract | target_final_alignment/wrong_answer_type_or_slot | False | usher | "Yeah!" | Usher |
| 71 | baseline | evidence_carriage/likely_evidence_or_reasoning_failure | False | 276170 inhabitants | 276,170 | 276,170 inhabitants |
| 85 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | False | april 1 1949 | 1949 | April 1, 1949 |
| 93 | baseline | positive_contract_rescue/contract_rescued_verbose_surface | False | no | Only Gibson contains gin. | No |
| 99 | baseline | positive_contract_rescue/contract_rescued_verbose_surface | False | no | Yingkou is at a higher administrative level than Fuding. | No |
| 99 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | False | no | Fuding is a county-level city. | No |

## Public Target Only Regressions

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 52 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | indianapolis motor speedway | Indianapolis Motor Speedway | The race location is on the corner of 16th Street and Georgetown Road, approximately 6 mi west of Downtown Indianapolis. |
| 55 | baseline | final_answer_commitment/missing_required_token_or_qualifier | True | marion south australia | Marion, South Australia | Robert Menzies opened Westminster School. Westminster School in Marion, South Australia is named after the Westminster School in London. |
| 56 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | drifting | Drifting | oversteer |
| 57 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | False | keith bostic | Keith Bostic | Jerry Glanville is older based on the given information, implying Keith Bostic, born in 1961, is younger. However, the direct answer to who is younger as per the action result is: Keith Bostic |
| 67 | baseline | target_final_alignment/wrong_answer_type_or_slot | False | usher | Usher | The song "Yeah!" by Usher was stuck behind another song for eight consecutive weeks. |
| 75 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | john john florence | John John Florence | John Florence |
| 93 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | False | no | No | Zurracapote does not contain gin. |
| 96 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | it products and services | IT products and services | Viglen Ltd provides IT products and services, including storage systems, servers, workstations and data/voice communications equipment and services. |
| 96 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | it products and services | IT products and services | Viglen Ltd provides IT products and services, including storage systems, servers, workstations and data/voice communications equipment and services. |
| 98 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | beijing | Beijing | The ambassador of the Rabat-Salé-Kénitra administrative region to China is based in Beijing. |

## Candidate Corrections

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 60 | final_contract | target_final_alignment/wrong_answer_type_or_slot | True | shortest player ever to play in national basketball association | shortest player ever to play in the National Basketball Association | shortest player ever to play in the National Basketball Association |
| 67 | baseline | target_final_alignment/wrong_answer_type_or_slot | False | usher | Usher | Usher |
| 78 | baseline | positive_contract_rescue/contract_rescued_verbose_surface | False | british | British | British |
| 85 | baseline | positive_contract_rescue/contract_rescued_verbose_surface | False | april 1 1949 | 1946 | April 1, 1949 |
| 93 | baseline | positive_contract_rescue/contract_rescued_verbose_surface | False | no | Only Gibson contains gin. | No |
| 99 | baseline | positive_contract_rescue/contract_rescued_verbose_surface | False | no | Yingkou is at a higher administrative level than Fuding. | No |

## Candidate Regressions

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 52 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | indianapolis motor speedway | Indianapolis Motor Speedway hosts a 500 mile race every May in the Midwest. | Indianapolis Motor Speedway hosts a 500 mile race every May in the Midwest. |
| 57 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | False | keith bostic | Keith Bostic | Jerry Glanville |
| 75 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | john john florence | John John Florence | John Florence |
| 75 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | john john florence | John Florence | John Florence |
| 85 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | False | april 1 1949 | 1949 | 1949 |
