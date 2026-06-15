# PACT Field-Contract Quarantine Delta Audit

## Comparisons

| Slice | reference_wrong_to_quarantine_right | reference_right_to_quarantine_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| base_public_state | 12 | 3 | 49 | 36 |
| freeze_question_target | 5 | 2 | 56 | 37 |
| hide_public_target | 5 | 3 | 56 | 36 |
| show_final_answer_candidate | 11 | 5 | 50 | 34 |

## By Source Run

| Slice | reference_wrong_to_quarantine_right | reference_right_to_quarantine_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| base_public_state \| baseline | 3 | 1 | 27 | 19 |
| base_public_state \| final_contract | 9 | 2 | 22 | 17 |
| freeze_question_target \| baseline | 2 | 2 | 28 | 18 |
| freeze_question_target \| final_contract | 3 | 0 | 28 | 19 |
| hide_public_target \| baseline | 1 | 0 | 29 | 20 |
| hide_public_target \| final_contract | 4 | 3 | 27 | 16 |
| show_final_answer_candidate \| baseline | 3 | 3 | 27 | 17 |
| show_final_answer_candidate \| final_contract | 8 | 2 | 23 | 17 |

## By Target Action

| Slice | reference_wrong_to_quarantine_right | reference_right_to_quarantine_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| base_public_state \| freeze | 6 | 1 | 14 | 12 |
| base_public_state \| keep | 6 | 2 | 35 | 24 |
| freeze_question_target \| freeze | 4 | 1 | 16 | 12 |
| freeze_question_target \| keep | 1 | 1 | 40 | 25 |
| hide_public_target \| freeze | 1 | 1 | 19 | 12 |
| hide_public_target \| keep | 4 | 2 | 37 | 24 |
| show_final_answer_candidate \| freeze | 7 | 3 | 13 | 10 |
| show_final_answer_candidate \| keep | 4 | 2 | 37 | 24 |

## Rescues vs Base Public State

| Sample | Source | Bridge | Target action | Gold | Reference | Quarantine |
| ---: | --- | --- | --- | --- | --- | --- |
| 52 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | keep | indianapolis motor speedway | Indianapolis Motor Speedway hosts a 500 mile race every May in the Midwest. | Indianapolis Motor Speedway |
| 54 | final_contract | final_answer_commitment/strict_span_regression_with_soft_target_shift | freeze | max martin savan kotecha and ilya salmanzadeh | Max Martin, Savan Kotecha, Ilya Salmanzadeh | Max Martin, Savan Kotecha and Ilya Salmanzadeh |
| 55 | final_contract | final_answer_commitment/missing_required_token_or_qualifier | freeze | marion south australia | 1961 | Marion, South Australia |
| 64 | final_contract | final_answer_commitment/strict_span_regression | freeze | more than 70 countries | 70 | more than 70 countries |
| 67 | final_contract | target_final_alignment/wrong_answer_type_or_slot | keep | usher | "Yeah!" | Usher |
| 71 | baseline | evidence_carriage/likely_evidence_or_reasoning_failure | keep | 276170 inhabitants | 276,170 | 276,170 inhabitants |
| 71 | final_contract | evidence_carriage/likely_evidence_or_reasoning_failure | keep | 276170 inhabitants | 276,170 | 276,170 inhabitants |
| 85 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | freeze | april 1 1949 | 1949 | April 1, 1949 |
| 87 | baseline | final_answer_commitment/over_specific_answer | freeze | canary islands spain | La Gomera, Canary Islands, Spain | Canary Islands, Spain |
| 87 | final_contract | final_answer_commitment/over_specific_answer | freeze | canary islands spain | Tenerife, Canary Islands, Spain and La Gomera, Canary Islands, Spain | Canary Islands, Spain |
| 99 | baseline | positive_contract_rescue/contract_rescued_verbose_surface | keep | no | Yingkou is at a higher administrative level than Fuding. | No |
| 99 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | keep | no | Fuding is a county-level city. | No |

## Regressions vs Base Public State

| Sample | Source | Bridge | Target action | Gold | Reference | Quarantine |
| ---: | --- | --- | --- | --- | --- | --- |
| 57 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | keep | keith bostic | Keith Bostic | Keith Bostic is younger than Jerry Glanville. |
| 60 | final_contract | target_final_alignment/wrong_answer_type_or_slot | freeze | shortest player ever to play in national basketball association | shortest player ever to play in the National Basketball Association | Muggsy Bogues is the shortest player ever to play in the National Basketball Association. |
| 75 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | keep | john john florence | John John Florence | John Florence |

## Rescues vs Hide Public Target

| Sample | Source | Bridge | Target action | Gold | Reference | Quarantine |
| ---: | --- | --- | --- | --- | --- | --- |
| 56 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | keep | drifting | oversteering technique | Drifting |
| 71 | final_contract | evidence_carriage/likely_evidence_or_reasoning_failure | keep | 276170 inhabitants | 276,170 | 276,170 inhabitants |
| 93 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | freeze | no | Zurracapote does not contain gin. | No |
| 99 | baseline | positive_contract_rescue/contract_rescued_verbose_surface | keep | no | Yingkou is at a higher administrative level than Fuding. | No |
| 99 | final_contract | positive_contract_rescue/contract_rescued_verbose_surface | keep | no | Yingkou is not the same level of city as Fuding. | No |

## Regressions vs Hide Public Target

| Sample | Source | Bridge | Target action | Gold | Reference | Quarantine |
| ---: | --- | --- | --- | --- | --- | --- |
| 50 | final_contract | final_answer_commitment/missing_required_token_or_qualifier | keep | 2009 big 12 conference | 2009 Big 12 Conference | 2009, Big 12 |
| 60 | final_contract | target_final_alignment/wrong_answer_type_or_slot | freeze | shortest player ever to play in national basketball association | shortest player ever to play in the National Basketball Association | Muggsy Bogues is the shortest player ever to play in the National Basketball Association. |
| 95 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | keep | fairfax county | Fairfax County | Fairfax County, Virginia |
