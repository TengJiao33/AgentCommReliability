# PACT Field-Authority Projection Delta Audit

## Condition Scores

| Condition | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `frozen_target_plus_evidence_no_final` | 100 | 0.560 | 0.698 |
| `public_target_plus_evidence_no_question_no_final` | 100 | 0.300 | 0.481 |
| `question_plus_evidence_no_target_no_final` | 100 | 0.470 | 0.610 |
| `question_plus_public_state_no_final` | 100 | 0.500 | 0.648 |
| `question_plus_public_state_with_final` | 100 | 0.430 | 0.575 |
| `security_projection_question_root_no_final` | 100 | 0.510 | 0.661 |
| `standalone_authority_quarantine_no_final` | 100 | 0.440 | 0.604 |

## Projection Versus Controls

| Slice | projection_rescue | projection_regression | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| security_vs_frozen_target | 0 | 5 | 51 | 44 |
| security_vs_hide_target | 8 | 4 | 43 | 45 |
| security_vs_public_state | 7 | 6 | 44 | 43 |
| standalone_vs_frozen_target | 0 | 12 | 44 | 44 |
| standalone_vs_hide_target | 3 | 6 | 41 | 50 |
| standalone_vs_public_state | 5 | 11 | 39 | 45 |
| standalone_vs_security | 1 | 8 | 43 | 48 |

## By Detector Action

| Slice | projection_rescue | projection_regression | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| security_vs_frozen_target \| hide | 0 | 0 | 18 | 17 |
| security_vs_frozen_target \| project_question_root | 0 | 5 | 33 | 27 |
| security_vs_hide_target \| hide | 3 | 0 | 15 | 17 |
| security_vs_hide_target \| project_question_root | 5 | 4 | 28 | 28 |
| security_vs_public_state \| hide | 2 | 0 | 16 | 17 |
| security_vs_public_state \| project_question_root | 5 | 6 | 28 | 26 |
| standalone_vs_frozen_target \| hide | 0 | 2 | 16 | 17 |
| standalone_vs_frozen_target \| project_question_root | 0 | 10 | 28 | 27 |
| standalone_vs_hide_target \| hide | 1 | 0 | 15 | 19 |
| standalone_vs_hide_target \| project_question_root | 2 | 6 | 26 | 31 |
| standalone_vs_public_state \| hide | 1 | 1 | 15 | 18 |
| standalone_vs_public_state \| project_question_root | 4 | 10 | 24 | 27 |
| standalone_vs_security \| hide | 0 | 2 | 16 | 17 |
| standalone_vs_security \| project_question_root | 1 | 6 | 27 | 31 |

## Security Regressions Versus Frozen Target

| Sample | Source | Detector | Gold | Reference | Projection |
| ---: | --- | --- | --- | --- | --- |
| 102 | baseline | project_question_root: | 2003 | 2003 | 2001 |
| 102 | final_contract | project_question_root: | 2003 | 2003 | 2002 |
| 123 | final_contract | project_question_root: | kkr co | KKR & Co. | KKR & Co. L.P. (KKR) |
| 130 | baseline | project_question_root: | lalees kin legacy of cotton | LaLee's Kin: The Legacy of Cotton | LaLee's Kin: The Legacy of Cotton was Oscar nominated. |
| 145 | final_contract | project_question_root: | erika jayne | Erika Jayne | Erika Jayne was born first. |

## Standalone Regressions Versus Security

| Sample | Source | Detector | Gold | Reference | Projection |
| ---: | --- | --- | --- | --- | --- |
| 118 | baseline | hide:generic_low_overlap_target,under_specified_target,unsupported_target_terms | no | No | Skin Yard was from the U.S., but Ostava was not. |
| 118 | final_contract | project_question_root: | no | No. | Skin Yard is from the U.S., and Ostava is not. |
| 119 | baseline | hide:generic_low_overlap_target,under_specified_target | yes | Yes | Daryl Hall and Gerry Marsden are both musicians. |
| 127 | baseline | project_question_root: | late 12th century | late 12th Century | The palace was founded in the late 12th Century. |
| 127 | final_contract | project_question_root: | late 12th century | late 12th Century | The palace was founded in the late 12th Century. |
| 131 | final_contract | project_question_root: | pirates cove | Pirate's Cove | Pirate's Cove was published more recently than Catan. |
| 141 | baseline | project_question_root: | roberta vinci | Roberta Vinci | Roberta Vinci had a better singles ranking than Jorge Lozano. |
| 141 | final_contract | project_question_root: | roberta vinci | Roberta Vinci | Roberta Vinci had a better singles ranking than Jorge Lozano. |
