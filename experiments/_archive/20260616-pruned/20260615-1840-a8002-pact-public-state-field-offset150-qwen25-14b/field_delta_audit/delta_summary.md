# PACT Field Packet Delta Audit

Base condition: `question_plus_public_state_no_final`

## Condition Deltas

| Slice | base_wrong_to_variant_right | base_right_to_variant_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze_question_target | 10 | 4 | 38 | 48 |
| hide_public_target | 5 | 2 | 40 | 53 |
| hide_question_keep_public_target | 0 | 11 | 31 | 58 |
| show_final_answer_candidate | 6 | 5 | 37 | 52 |

## By Source Run

| Slice | base_wrong_to_variant_right | base_right_to_variant_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze_question_target | compact_final_contract | 4 | 0 | 21 | 25 |
| freeze_question_target | final_contract | 6 | 4 | 17 | 23 |
| hide_public_target | compact_final_contract | 2 | 0 | 21 | 27 |
| hide_public_target | final_contract | 3 | 2 | 19 | 26 |
| hide_question_keep_public_target | compact_final_contract | 0 | 4 | 17 | 29 |
| hide_question_keep_public_target | final_contract | 0 | 7 | 14 | 29 |
| show_final_answer_candidate | compact_final_contract | 5 | 3 | 18 | 24 |
| show_final_answer_candidate | final_contract | 1 | 2 | 19 | 28 |

## By Target Candidate

| Slice | base_wrong_to_variant_right | base_right_to_variant_wrong | both_right | both_wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze_question_target | target_candidate=False | 10 | 4 | 37 | 31 |
| freeze_question_target | target_candidate=True | 0 | 0 | 1 | 17 |
| hide_public_target | target_candidate=False | 4 | 2 | 39 | 37 |
| hide_public_target | target_candidate=True | 1 | 0 | 1 | 16 |
| hide_question_keep_public_target | target_candidate=False | 0 | 10 | 31 | 41 |
| hide_question_keep_public_target | target_candidate=True | 0 | 1 | 0 | 17 |
| show_final_answer_candidate | target_candidate=False | 6 | 4 | 37 | 35 |
| show_final_answer_candidate | target_candidate=True | 0 | 1 | 0 | 17 |

## Hide Public Target Rescues

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 152 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | argand lamp | The Lewis lamp, used in lighthouses, had a design similar to the Argand lamp. | Argand lamp |
| 152 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | argand lamp | 6 to 10 candela | Argand lamp |
| 156 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | seven days battles | The Seven Days Battles occurred from June 25 to July 1, 1862, which is earlier than the Battle of Manila (February 3, 1945 – March 3, 1945). | The Seven Days Battles |
| 161 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | frank lowy | 22 October 1930 | Frank Lowy |
| 163 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | True | kelly lee osbourne | Kelly Osbourne | Kelly Lee Osbourne |

## Freeze Target Rescues

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 152 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | argand lamp | The Lewis lamp, used in lighthouses, had a design similar to the Argand lamp. | Argand lamp |
| 152 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | argand lamp | 6 to 10 candela | Argand lamp |
| 154 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | yes | Laeliocattleya is an orchid. | Yes |
| 156 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | seven days battles | The Seven Days Battles occurred from June 25 to July 1, 1862, which is earlier than the Battle of Manila (February 3, 1945 – March 3, 1945). | The Seven Days Battles |
| 161 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | frank lowy | 22 October 1930 | Frank Lowy |
| 166 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | dinosaur | 2000 | Dinosaur |
| 173 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | pasek paul | Pasek and Paul | Pasek & Paul |
| 175 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | yes | Danny Jones is a musician. | Yes |
| 175 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | yes | Danny Jones is a musician. | Yes |
| 193 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | murray hill | Murray Hill, New Jersey | Murray Hill |

## Public Target Only Regressions

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 150 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | director | director | actor, screenwriter, and director |
| 153 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | seven | seven | seven top 20 US albums |
| 156 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | seven days battles | The Seven Days Battles | The Seven Days Battles occurred from June 25 to July 1, 1862. The Battle of Manila took place from February 3 to March 3, 1945. |
| 161 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | frank lowy | Frank Lowy | Frank P. Lowy (born 22 October 1930) |
| 167 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | wichita | Wichita | Wichita, Kansas |
| 174 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | city of newcastle | City of Newcastle | local government area in the Hunter region of New South Wales, Australia. |
| 176 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | drawings | drawings | 65,000 drawings |
| 177 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | True | between 8th and 16th centuries | between the 8th and 16th centuries | Old Frisian |
| 181 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | summerlin | Summerlin | Summerlin, Nevada |
| 195 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | wendell berry | Wendell Berry | handprinted in editions of usually 100 copies or less |
| 195 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | wendell berry | Wendell Berry | Wendell Berry has had works published by Dim Gray Bar Press. |

## Candidate Corrections

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 167 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | wichita | Wichita | Wichita |
| 182 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | george harrison | George Harrison | George Harrison |
| 197 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | golden valley minnesota | Golden Valley, Minnesota | Golden Valley, Minnesota |

## Candidate Regressions

| Sample | Source | Bridge | Target candidate | Gold | Base | Variant |
| ---: | --- | --- | --- | --- | --- | --- |
| 150 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | director | director | actor, screenwriter, and director |
| 152 | compact_final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | argand lamp | The Lewis lamp, used in lighthouses, had a design similar to the Argand lamp. | Lewis lamp |
| 154 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | yes | Laeliocattleya is an orchid. | No Explanation: The provided evidence only confirms that Laeliocattleya is an orchid, but there is no information given about Broughtonia. Therefore, based on the available evidence, we cannot conclude that both are orchids. The final answer should reflect the limitations of the provided evidence. |
| 161 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | frank lowy | 22 October 1930 | 22 October 1930 |
| 166 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | dinosaur | 2000 | 2000 |
| 174 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | city of newcastle | The City of Newcastle is a local government area in the Hunter region of New South Wales, Australia. However, it is not directly south of Shelly Beach. | The final answer should not be "City of Newcastle" as it does not meet the criteria of being south of Shelly Beach. There is no information provided that matches a city south of Shelly Beach that is also a local government area in the Hunter region. Therefore, based on the given evidence, we cannot provide a |
| 175 | final_contract | stable_right_or_not_focus/stable_right_or_not_focus | False | yes | Danny Jones is a musician. | Danny Jones is a musician. |
