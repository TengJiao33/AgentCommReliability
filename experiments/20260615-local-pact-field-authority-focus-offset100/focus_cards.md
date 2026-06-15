# PACT Field-Authority Focus Cards

These cards extract target-authority and target-contract focus units from a packet-derived bridge audit.

## Sources

- Bridge cases: `experiments\20260615-local-pact-public-state-field-bridge-offset100\bridge_cases.jsonl`

## Counts

- Cards: `28`
- Unique samples: `18`
- Families: `{'frozen_question_target_regression': 1, 'frozen_question_target_rescue': 7, 'public_target_without_question_regression': 20}`

## Cards

| Sample | Source | Family | Gold | Public target | Base | Frozen | Target only |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 101 | baseline | public_target_without_question_regression | larnelle harris | Determine if David Huntsinger has worked with a gospel singer born in July. | Larnelle Harris | Larnelle Harris | Yes, Larnelle Harris, born in July. |
| 101 | final_contract | public_target_without_question_regression | larnelle harris | Determine if David Huntsinger has worked with a gospel singer born in July. | Larnelle Harris | Larnelle Harris | Yes, Larnelle Harris, born in July. |
| 106 | baseline | frozen_question_target_rescue | 1887 | Provide birth year of John Cecil Holm. | The given context does not provide the birth year of John Cecil Holm. | 1887 | The given context does not provide John Cecil Holm's birth year. |
| 108 | baseline | frozen_question_target_rescue | 7 october 1978 | Provide the birth year of Zaheer Khan. | 1978 | 7 October 1978 | 1978 |
| 114 | baseline | public_target_without_question_regression | picric acid | Provide fact | Picric acid | Picric acid | (ON)CHOH |
| 115 | baseline | public_target_without_question_regression | 230 | Provide the number of worldwide tournaments won by Roberto De Vicenzo. | 230 | more than 230 | more than 230 |
| 118 | baseline | public_target_without_question_regression | no | Provide conclusion based on information from Agent A and Agent B. | No. | No | Skin Yard was from the U.S., but Ostava was not. |
| 118 | final_contract | frozen_question_target_rescue | no | Provide conclusion about both bands' origins. | Skin Yard is from the U.S., and Ostava is not. | No | Skin Yard is from the U.S., and Ostava is not. |
| 119 | baseline | frozen_question_target_rescue | yes | Provide answer to the question. | Daryl Hall and Gerry Marsden are both musicians. | Yes | Gerry Marsden is an English musician. |
| 119 | final_contract | frozen_question_target_rescue | yes | Provide conclusion based on both musicians' professions. | Both Daryl Hall and Gerry Marsden are musicians. | Yes | Both Daryl Hall and Gerry Marsden are musicians. |
| 122 | baseline | public_target_without_question_regression | spiderwick chronicles | Confirm answer. | The Spiderwick Chronicles | The Spiderwick Chronicles | Sarah Bolger |
| 122 | final_contract | public_target_without_question_regression | spiderwick chronicles | Confirm relevance. | The Spiderwick Chronicles | The Spiderwick Chronicles | The Spiderwick Chronicles is a 2008 American fantasy adventure film. |
| 123 | final_contract | frozen_question_target_rescue | kkr co | Provide the name of the American multinational equity firm that owns Maxeda since 2004. | KKR & Co. L.P. (Kohlberg Kravis Roberts) | KKR & Co. | KKR & Co. L.P. |
| 126 | baseline | public_target_without_question_regression | owsley stanley | Provide information about Owsley Stanley's identity and his role in recording "Old and in the Way". | Owsley Stanley | Owsley Stanley | Owsley Stanley recorded the album "Old and in the Way". |
| 130 | baseline | frozen_question_target_rescue | lalees kin legacy of cotton | Provide the Oscar nomination status for Gimme Shelter. | Gimme Shelter was not nominated for any Oscars. | LaLee's Kin: The Legacy of Cotton | Gimme Shelter was not nominated for any Oscars. |
| 130 | final_contract | public_target_without_question_regression | lalees kin legacy of cotton | Provide conclusion based on Oscar nomination information. | LaLee's Kin: The Legacy of Cotton | LaLee's Kin: The Legacy of Cotton | LaLee's Kin: The Legacy of Cotton was nominated for Best Documentary Feature at the 74th Academy Awards. |
| 131 | final_contract | public_target_without_question_regression | pirates cove | Compare publication years of Pirate's Cove and Catan. | Pirate's Cove | Pirate's Cove | Catan was first published in 1995. Pirate's Cove was originally published in 2002. |
| 135 | baseline | public_target_without_question_regression | jillian belk | Provide information about Jillian Bell's recurring role on Workaholics. | Jillian Belk | Jillian Belk | Jillian Bell had a recurring role as Jillian Belk on Workaholics. |
| 135 | final_contract | public_target_without_question_regression | jillian belk | Provide information about Jillian Bell's role in SuperMansion. | Jillian Belk | Jillian Belk | Jillian Bell had a recurring role as Jillian Belk on Workaholics. However, based on the instruction and the visible input, there is no mention of Jillian Bell's role in SuperMansion in the provided evidence. The final answer should reflect the information given, which is about her role in " |
| 141 | baseline | public_target_without_question_regression | roberta vinci | Compare the singles rankings of Roberta Vinci and Jorge Lozano. | Roberta Vinci | Roberta Vinci | World No. 7 |
| 141 | final_contract | public_target_without_question_regression | roberta vinci | Compare the singles rankings of Roberta Vinci and Jorge Lozano. | Roberta Vinci | Roberta Vinci | World No. 7 |
| 144 | baseline | public_target_without_question_regression | nebo zovyot | Provide information about the 1959 Soviet film "Nebo Zovyot". | "Nebo Zovyot" | "Nebo Zovyot" | "Nebo Zovyot" is a 1959 Soviet science fiction film directed by Mikhail Karyukov and Aleksandr Kozyr. |
| 144 | final_contract | public_target_without_question_regression | nebo zovyot | Provide the title of the 1959 Soviet feature "Nebo Zovyot" is based on or related to. | Nebo Zovyot | Nebo Zovyot | Queen of Blood |
| 145 | baseline | public_target_without_question_regression | erika jayne | Compare birth dates of Marco Da Silva and Erika Jayne. | Erika Jayne | Erika Jayne was born first. | Erika Jayne was born first. |
| 145 | final_contract | public_target_without_question_regression | erika jayne | Compare birth dates of Marco Da Silva and Erika Jayne. | Erika Jayne | Erika Jayne | July 10th, 1971 |
| 148 | baseline | public_target_without_question_regression | beatles | Provide conclusion based on expertise and influence. | The Beatles | The Beatles | The Beatles were widely regarded as the foremost and most influential act of the rock era. |
| 148 | final_contract | public_target_without_question_regression | beatles | Confirm Bruce Spizer's expertise on The Beatles as the most influential act of the rock era. | The Beatles | The Beatles | Bruce Spizer is an expert on The Beatles, known as the most influential act of the rock era. |
| 149 | final_contract | frozen_question_target_regression | well burn that bridge | Provide the song title that was behind "Chattahoochee" on the country charts for two weeks. | "We'll Burn That Bridge" | "Chattahoochee" | "We'll Burn That Bridge" |

## Caveat

These are extraction cards only. Semantic categories, if added in a report, are manual inspection labels.
