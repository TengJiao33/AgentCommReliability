# PACT Field-Authority Focus Cards

These cards extract target-authority and target-contract focus units from a packet-derived bridge audit.

## Sources

- Bridge cases: `experiments\_archive\20260616-pruned\20260615-local-pact-public-state-field-bridge-offset150\bridge_cases.jsonl`

## Counts

- Cards: `22`
- Unique samples: `17`
- Families: `{'frozen_question_target_regression': 1, 'frozen_question_target_rescue': 10, 'public_target_without_question_regression': 11}`

## Cards

| Sample | Source | Family | Gold | Public target | Base | Frozen | Target only |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 150 | final_contract | public_target_without_question_regression | director | Provide occupation information for Pietro Germi. | director | director | actor, screenwriter, and director |
| 152 | compact_final_contract | frozen_question_target_rescue | argand lamp | Provide information on the similarity of the lamp used in lighthouses to the Argand lamp. | The Lewis lamp, used in lighthouses, had a design similar to the Argand lamp. | Argand lamp | The Lewis lamp had a design similar to the Argand lamp. |
| 152 | final_contract | frozen_question_target_rescue | argand lamp | Provide information about the brightness of the Argand lamp. | 6 to 10 candela | Argand lamp | The Argand lamp is brighter than earlier lamps with an output of 6 to 10 candela. |
| 153 | final_contract | public_target_without_question_regression | seven | Provide the answer to the question. | seven | seven | seven top 20 US albums |
| 154 | final_contract | frozen_question_target_rescue | yes | Provide conclusion based on gathered information. | Laeliocattleya is an orchid. | Yes | Both Broughtonia and Laeliocattleya are orchids. |
| 156 | compact_final_contract | frozen_question_target_rescue | seven days battles | Provide the information that Seven Days Battles is earlier than Battle of Manila. | The Seven Days Battles occurred from June 25 to July 1, 1862, which is earlier than the Battle of Manila (February 3, 1945 – March 3, 1945). | The Seven Days Battles | The Seven Days Battles occurred from June 25 to July 1, 1862, which is earlier than the Battle of Manila (February 3, 1945 – March 3, 1945). |
| 156 | final_contract | public_target_without_question_regression | seven days battles | Compare the dates of the Seven Days Battles and the Battle of Manila. | The Seven Days Battles | The Seven Days Battles occurred earlier than the Battle of Manila. | The Seven Days Battles occurred from June 25 to July 1, 1862. The Battle of Manila took place from February 3 to March 3, 1945. |
| 161 | compact_final_contract | public_target_without_question_regression | frank lowy | [who presented the Australia 2022 FIFA World Cup bid and their birth date] | Frank Lowy | Frank Lowy | Frank P. Lowy (born 22 October 1930) |
| 161 | final_contract | frozen_question_target_rescue | frank lowy | Birth date of Frank Lowy. | 22 October 1930 | Frank Lowy | 22 October 1930 |
| 164 | final_contract | frozen_question_target_regression | sean yseult | Provide relevant fact. | Sean Yseult | Sean Yseultmarried John 5. However, based on the given environment state, the specific marriage mentioned in the question is not detailed. The action result provided does not include who she married, but based on external knowledge not presented in the environment state, Sean Yseult, the Star and Dagger bass player, | Sean Yseult |
| 166 | final_contract | frozen_question_target_rescue | dinosaur | Provide release year of Dinosaur. | 2000 | Dinosaur | 2000 |
| 167 | final_contract | public_target_without_question_regression | wichita | Provide the city where both schools are located. | Wichita | Wichita, Kansas | Wichita, Kansas |
| 173 | compact_final_contract | frozen_question_target_rescue | pasek paul | [Pasek and Paul composed "La La Land"] | Pasek and Paul | Pasek & Paul | Pasek and Paul composed "La La Land". |
| 174 | compact_final_contract | public_target_without_question_regression | city of newcastle | Provide information about the City of Newcastle. | City of Newcastle | City of Newcastle | local government area in the Hunter region of New South Wales, Australia. |
| 175 | compact_final_contract | frozen_question_target_rescue | yes | Confirm Danny Jones is a musician. | Danny Jones is a musician. | Yes | Danny Jones is a musician. |
| 175 | final_contract | frozen_question_target_rescue | yes | Provide information about Danny Jones's profession. | Danny Jones is a musician. | Yes | musician |
| 176 | compact_final_contract | public_target_without_question_regression | drawings | The Albertina houses approximately 65,000 drawings. | drawings | drawings | 65,000 drawings |
| 177 | final_contract | public_target_without_question_regression | between 8th and 16th centuries | [the Western Germanic language spoken from which the small settlement situated on the river Leda opposite Leer derives its name] | between the 8th and 16th centuries | between the 8th and 16th centuries | Old Frisian |
| 181 | final_contract | public_target_without_question_regression | summerlin | Provide the Nevada city where Bishop Gorman High School is located. | Summerlin | Summerlin, Nevada | Summerlin, Nevada |
| 193 | final_contract | frozen_question_target_rescue | murray hill | Provide the city where Bell Labs headquarters are located. | Murray Hill, New Jersey | Murray Hill | Murray Hill, New Jersey |
| 195 | compact_final_contract | public_target_without_question_regression | wendell berry | Wendell Berry has had works published by Dim Gray Bar Press. | Wendell Berry | Wendell Berry | handprinted in editions of usually 100 copies or less |
| 195 | final_contract | public_target_without_question_regression | wendell berry | Provide information on Wendell Berry's publications with Dim Gray Bar Press. | Wendell Berry | Wendell Berry | Wendell Berry has had works published by Dim Gray Bar Press. |

## Caveat

These are extraction cards only. Semantic categories, if added in a report, are manual inspection labels.
