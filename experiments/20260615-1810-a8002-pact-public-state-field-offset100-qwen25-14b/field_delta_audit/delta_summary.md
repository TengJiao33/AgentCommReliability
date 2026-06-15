# PACT Field Packet Delta Audit

Base condition: `question_plus_public_state_no_final`

## Condition Deltas

| Slice | base_wrong_to_variant_right | base_right_to_variant_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze_question_target | 9 | 3 | 47 | 41 |
| hide_public_target | 4 | 7 | 43 | 46 |
| hide_question_keep_public_target | 0 | 20 | 30 | 50 |
| show_final_answer_candidate | 3 | 10 | 40 | 47 |

## By Source Run

| Slice | base_wrong_to_variant_right | base_right_to_variant_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze_question_target | baseline | 5 | 2 | 23 | 20 |
| freeze_question_target | final_contract | 4 | 1 | 24 | 21 |
| hide_public_target | baseline | 3 | 5 | 20 | 22 |
| hide_public_target | final_contract | 1 | 2 | 23 | 24 |
| hide_question_keep_public_target | baseline | 0 | 11 | 14 | 25 |
| hide_question_keep_public_target | final_contract | 0 | 9 | 16 | 25 |
| show_final_answer_candidate | baseline | 2 | 6 | 19 | 23 |
| show_final_answer_candidate | final_contract | 1 | 4 | 21 | 24 |

## By Target Candidate

| Slice | base_wrong_to_variant_right | base_right_to_variant_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze_question_target | target_candidate=False | 7 | 3 | 47 | 31 |
| freeze_question_target | target_candidate=True | 2 | 0 | 0 | 10 |
| hide_public_target | target_candidate=False | 3 | 7 | 43 | 35 |
| hide_public_target | target_candidate=True | 1 | 0 | 0 | 11 |
| hide_question_keep_public_target | target_candidate=False | 0 | 20 | 30 | 38 |
| hide_question_keep_public_target | target_candidate=True | 0 | 0 | 0 | 12 |
| show_final_answer_candidate | target_candidate=False | 2 | 10 | 40 | 36 |
| show_final_answer_candidate | target_candidate=True | 1 | 0 | 0 | 11 |

## Hide Public Target Rescues

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 106 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | 1887 | The given context does not provide the birth year of John Cecil Holm. | 1887 |
| 108 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | 7 october 1978 | 1978 | 7 October 1978 |
| 112 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | True | 7 january 1936 | 1936 | 7 January 1936 |
| 130 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | lalees kin legacy of cotton | Gimme Shelter was not nominated for any Oscars. | LaLee's Kin: The Legacy of Cotton |

## Freeze Target Rescues

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 106 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | 1887 | The given context does not provide the birth year of John Cecil Holm. | 1887 |
| 108 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | 7 october 1978 | 1978 | 7 October 1978 |
| 112 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | True | 7 january 1936 | 1936 | 7 January 1936 |
| 118 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | no | Skin Yard is from the U.S., and Ostava is not. | No |
| 119 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | yes | Daryl Hall and Gerry Marsden are both musicians. | Yes |
| 119 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | yes | Both Daryl Hall and Gerry Marsden are musicians. | Yes |
| 123 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | kkr co | KKR & Co. L.P. (Kohlberg Kravis Roberts) | KKR & Co. |
| 130 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | lalees kin legacy of cotton | Gimme Shelter was not nominated for any Oscars. | LaLee's Kin: The Legacy of Cotton |
| 142 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | True | teach controversy campaign | "Teach the Controversy" | The "Teach the Controversy" campaign |

## Public Target Only Regressions

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 101 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | larnelle harris | Larnelle Harris | Yes, Larnelle Harris, born in July. |
| 101 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | larnelle harris | Larnelle Harris | Yes, Larnelle Harris, born in July. |
| 114 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | picric acid | Picric acid | (ON)CHOH |
| 115 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | 230 | 230 | more than 230 |
| 118 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | no | No. | Skin Yard was from the U.S., but Ostava was not. |
| 122 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | spiderwick chronicles | The Spiderwick Chronicles | Sarah Bolger |
| 122 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | spiderwick chronicles | The Spiderwick Chronicles | The Spiderwick Chronicles is a 2008 American fantasy adventure film. |
| 126 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | owsley stanley | Owsley Stanley | Owsley Stanley recorded the album "Old and in the Way". |
| 130 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | lalees kin legacy of cotton | LaLee's Kin: The Legacy of Cotton | LaLee's Kin: The Legacy of Cotton was nominated for Best Documentary Feature at the 74th Academy Awards. |
| 131 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | pirates cove | Pirate's Cove | Catan was first published in 1995. Pirate's Cove was originally published in 2002. |
| 135 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | jillian belk | Jillian Belk | Jillian Bell had a recurring role as Jillian Belk on Workaholics. |
| 135 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | jillian belk | Jillian Belk | Jillian Bell had a recurring role as Jillian Belk on Workaholics. However, based on the instruction and the visible input, there is no mention of Jillian Bell's role in SuperMansion in the provided evidence. The final answer should reflect the information given, which is about her role in " |
| 141 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | roberta vinci | Roberta Vinci | World No. 7 |
| 141 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | roberta vinci | Roberta Vinci | World No. 7 |
| 144 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | nebo zovyot | "Nebo Zovyot" | "Nebo Zovyot" is a 1959 Soviet science fiction film directed by Mikhail Karyukov and Aleksandr Kozyr. |
| 144 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | nebo zovyot | Nebo Zovyot | Queen of Blood |
| 145 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | erika jayne | Erika Jayne | Erika Jayne was born first. |
| 145 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | erika jayne | Erika Jayne | July 10th, 1971 |
| 148 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | beatles | The Beatles | The Beatles were widely regarded as the foremost and most influential act of the rock era. |
| 148 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | beatles | The Beatles | Bruce Spizer is an expert on The Beatles, known as the most influential act of the rock era. |

## Candidate Corrections

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 114 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | picric acid | Picric acid | Picric acid |
| 115 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | 230 | 230 | 230 |
| 119 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | yes | Daryl Hall and Gerry Marsden are both musicians. | Yes |
| 121 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | princess jessica | Princess Jessica | Princess Jessica |
| 127 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | late 12th century | late 12th Century | the late 12th Century |
| 135 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | jillian belk | Jillian Belk | Jillian Belk |
| 141 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | roberta vinci | Roberta Vinci | Roberta Vinci |
| 142 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | True | teach controversy campaign | "Teach the Controversy" | The "Teach the Controversy" campaign |

## Candidate Regressions

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 102 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | 2003 | 2003 | 2003 The question asks for the draft year of Boss Bailey, and the evidence provided indicates that he was drafted in 2003. However, the question specifically asks for the draft year of his brother, which is not provided in the evidence. Since the evidence does not contain information about Boss Bailey |
| 102 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | 2003 | 2003 | The question asks for the draft year of Boss Bailey's brother, not Boss Bailey himself. However, the provided evidence only contains information about Boss Bailey and does not mention his brother or the brother's draft year. Therefore, based on the given evidence, we cannot accurately provide the draft year of Boss Bailey's brother. The |
| 106 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | 1887 | The given context does not provide the birth year of John Cecil Holm. | The given context does not provide the birth year for John Cecil Holm. Therefore, the final answer cannot be 1887, as that is George Abbott's birth year. Since the required information is not available, the final answer is that the birth year of John Cecil Holm is not provided in the given |
| 108 | baseline | stable_right_or_not_focus/stable_right_or_not_focus | False | 7 october 1978 | 1978 | 1978 |
| 118 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | no | Skin Yard is from the U.S., and Ostava is not. | No, Skin Yard is from the U.S., and Ostava is not. |
| 130 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | lalees kin legacy of cotton | LaLee's Kin: The Legacy of Cotton | Gimme Shelter Explanation: The evidence provided states that "LaLee's Kin: The Legacy of Cotton was nominated for Best Documentary Feature at the 74th Academy Awards." However, the question asks about Oscar nominations for "Gimme Shelter, the 1970 Rolling Stones documentary." Given the |
| 149 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | well burn that bridge | "We'll Burn That Bridge" | "Chattahoochee" |
