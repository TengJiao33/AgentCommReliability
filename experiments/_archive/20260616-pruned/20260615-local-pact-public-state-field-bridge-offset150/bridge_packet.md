# PACT Field Bridge From Packet

This bridge audit is built from evaluated public-state field packet rows, not from the older offset50 case atlas.

## Sources

- Evaluated rows: `experiments\_archive\20260616-pruned\20260615-1840-a8002-pact-public-state-field-offset150-qwen25-14b\evaluation\evaluated_rows.jsonl`
- Span rows: `experiments\_archive\20260616-pruned\20260615-1840-a8002-pact-public-state-field-offset150-qwen25-14b\span_granularity_audit\span_granularity_rows.jsonl`
- Packet rows: `experiments\_archive\20260616-pruned\20260615-local-pact-public-state-field-packet-offset150\field_packet.jsonl`

## Counts

- Units: `100`
- Unique samples: `50`

| Bridge layer | Count | Sample:source units |
| --- | --- | --- |
| evidence_or_content | 28 | 160:compact_final_contract, 160:final_contract, 164:compact_final_contract, 165:compact_final_contract, 165:final_contract, 168:compact_final_contract, 168:final_contract, 172:compact_final_contract, 172:final_contract, 174:final_contract, 178:compact_final_contract, 178:final_contract, 180:compact_final_contract, 180:final_contract, 183:compact_final_contract, 183:final_contract, 184:compact_final_contract, 184:final_contract, 187:compact_final_contract, 187:final_contract |
| final_answer_commitment | 22 | 153:compact_final_contract, 154:compact_final_contract, 157:compact_final_contract, 157:final_contract, 158:compact_final_contract, 158:final_contract, 163:compact_final_contract, 166:compact_final_contract, 167:compact_final_contract, 169:compact_final_contract, 169:final_contract, 173:final_contract, 176:final_contract, 177:compact_final_contract, 185:compact_final_contract, 185:final_contract, 190:compact_final_contract, 190:final_contract, 192:compact_final_contract, 193:compact_final_contract |
| stable_answer | 27 | 150:compact_final_contract, 151:compact_final_contract, 151:final_contract, 155:compact_final_contract, 155:final_contract, 159:compact_final_contract, 159:final_contract, 162:compact_final_contract, 162:final_contract, 170:compact_final_contract, 170:final_contract, 171:compact_final_contract, 171:final_contract, 179:compact_final_contract, 179:final_contract, 181:compact_final_contract, 182:compact_final_contract, 182:final_contract, 186:compact_final_contract, 186:final_contract |
| target_authority | 11 | 150:final_contract, 153:final_contract, 156:final_contract, 161:compact_final_contract, 167:final_contract, 174:compact_final_contract, 176:compact_final_contract, 177:final_contract, 181:final_contract, 195:compact_final_contract, 195:final_contract |
| target_contract | 11 | 152:compact_final_contract, 152:final_contract, 154:final_contract, 156:compact_final_contract, 161:final_contract, 164:final_contract, 166:final_contract, 173:compact_final_contract, 175:compact_final_contract, 175:final_contract, 193:final_contract |
| target_field_ablation | 1 | 163:final_contract |

| Bridge family | Count | Sample:source units |
| --- | --- | --- |
| content_mismatch_after_public_state | 28 | 160:compact_final_contract, 160:final_contract, 164:compact_final_contract, 165:compact_final_contract, 165:final_contract, 168:compact_final_contract, 168:final_contract, 172:compact_final_contract, 172:final_contract, 174:final_contract, 178:compact_final_contract, 178:final_contract, 180:compact_final_contract, 180:final_contract, 183:compact_final_contract, 183:final_contract, 184:compact_final_contract, 184:final_contract, 187:compact_final_contract, 187:final_contract |
| final_candidate_attractor_regression | 3 | 153:compact_final_contract, 154:compact_final_contract, 157:compact_final_contract |
| final_candidate_rescue | 2 | 166:compact_final_contract, 185:compact_final_contract |
| frozen_question_target_regression | 1 | 164:final_contract |
| frozen_question_target_rescue | 10 | 152:compact_final_contract, 152:final_contract, 154:final_contract, 156:compact_final_contract, 161:final_contract, 166:final_contract, 173:compact_final_contract, 175:compact_final_contract, 175:final_contract, 193:final_contract |
| public_target_hurt_when_question_visible | 1 | 163:final_contract |
| public_target_without_question_regression | 11 | 150:final_contract, 153:final_contract, 156:final_contract, 161:compact_final_contract, 167:final_contract, 174:compact_final_contract, 176:compact_final_contract, 177:final_contract, 181:final_contract, 195:compact_final_contract, 195:final_contract |
| stable_right_under_public_state | 27 | 150:compact_final_contract, 151:compact_final_contract, 151:final_contract, 155:compact_final_contract, 155:final_contract, 159:compact_final_contract, 159:final_contract, 162:compact_final_contract, 162:final_contract, 170:compact_final_contract, 170:final_contract, 171:compact_final_contract, 171:final_contract, 179:compact_final_contract, 179:final_contract, 181:compact_final_contract, 182:compact_final_contract, 182:final_contract, 186:compact_final_contract, 186:final_contract |
| strict_span_or_granularity_failure | 17 | 157:final_contract, 158:compact_final_contract, 158:final_contract, 163:compact_final_contract, 167:compact_final_contract, 169:compact_final_contract, 169:final_contract, 173:final_contract, 176:final_contract, 177:compact_final_contract, 185:final_contract, 190:compact_final_contract, 190:final_contract, 192:compact_final_contract, 193:compact_final_contract, 198:compact_final_contract, 198:final_contract |

## Delta Signals

| Signal | Outcome counts |
| --- | --- |
| freeze_question_target | {'both_right': 38, 'both_wrong': 48, 'regression': 4, 'rescue': 10} |
| hide_public_target | {'both_right': 40, 'both_wrong': 53, 'regression': 2, 'rescue': 5} |
| hide_question_keep_public_target | {'both_right': 31, 'both_wrong': 58, 'regression': 11} |
| show_final_answer_candidate | {'both_right': 37, 'both_wrong': 52, 'regression': 5, 'rescue': 6} |

## Non-Stable Focus Units

| Sample | Source | Layer | Family | Gold | Base prediction |
| --- | --- | --- | --- | --- | --- |
| 150 | final_contract | target_authority | public_target_without_question_regression | director | director |
| 152 | compact_final_contract | target_contract | frozen_question_target_rescue | argand lamp | The Lewis lamp, used in lighthouses, had a design similar to the Argand lamp. |
| 152 | final_contract | target_contract | frozen_question_target_rescue | argand lamp | 6 to 10 candela |
| 153 | compact_final_contract | final_answer_commitment | final_candidate_attractor_regression | seven | seven |
| 153 | final_contract | target_authority | public_target_without_question_regression | seven | seven |
| 154 | compact_final_contract | final_answer_commitment | final_candidate_attractor_regression | yes | Yes |
| 154 | final_contract | target_contract | frozen_question_target_rescue | yes | Laeliocattleya is an orchid. |
| 156 | compact_final_contract | target_contract | frozen_question_target_rescue | seven days battles | The Seven Days Battles occurred from June 25 to July 1, 1862, which is earlier than the Battle of Manila (February 3, 1945 – March 3, 1945). |
| 156 | final_contract | target_authority | public_target_without_question_regression | seven days battles | The Seven Days Battles |
| 157 | compact_final_contract | final_answer_commitment | final_candidate_attractor_regression | lush ltd | Lush Ltd. |
| 157 | final_contract | final_answer_commitment | strict_span_or_granularity_failure | lush ltd | Lush |
| 158 | compact_final_contract | final_answer_commitment | strict_span_or_granularity_failure | manchester united | Manchester United Football Club |
| 158 | final_contract | final_answer_commitment | strict_span_or_granularity_failure | manchester united | Manchester United F.C. |
| 160 | compact_final_contract | evidence_or_content | content_mismatch_after_public_state | kathryn jean martin | Kathy Sullivan |
| 160 | final_contract | evidence_or_content | content_mismatch_after_public_state | kathryn jean martin | Kathy Sullivan |
| 161 | compact_final_contract | target_authority | public_target_without_question_regression | frank lowy | Frank Lowy |
| 161 | final_contract | target_contract | frozen_question_target_rescue | frank lowy | 22 October 1930 |
| 163 | compact_final_contract | final_answer_commitment | strict_span_or_granularity_failure | kelly lee osbourne | Kelly Osbourne |
| 163 | final_contract | target_field_ablation | public_target_hurt_when_question_visible | kelly lee osbourne | Kelly Osbourne |
| 164 | compact_final_contract | evidence_or_content | content_mismatch_after_public_state | sean yseult | None of the provided paragraphs contain information about Sean Yseult's spouse. |
| 164 | final_contract | target_contract | frozen_question_target_regression | sean yseult | Sean Yseult |
| 165 | compact_final_contract | evidence_or_content | content_mismatch_after_public_state | prescription drug user fee act | The provided context does not contain information about the Center for Veterinary Medicine spending in 2017. |
| 165 | final_contract | evidence_or_content | content_mismatch_after_public_state | prescription drug user fee act | $700 million |
| 166 | compact_final_contract | final_answer_commitment | final_candidate_rescue | dinosaur | 2000 |
| 166 | final_contract | target_contract | frozen_question_target_rescue | dinosaur | 2000 |
| 167 | compact_final_contract | final_answer_commitment | strict_span_or_granularity_failure | wichita | Wichita, Kansas |
| 167 | final_contract | target_authority | public_target_without_question_regression | wichita | Wichita |
| 168 | compact_final_contract | evidence_or_content | content_mismatch_after_public_state | united states presidential election of 2016 | 2016 |
| 168 | final_contract | evidence_or_content | content_mismatch_after_public_state | united states presidential election of 2016 | November 8, 2016 |
| 169 | compact_final_contract | final_answer_commitment | strict_span_or_granularity_failure | roman | The Roman Empire. |
| 169 | final_contract | final_answer_commitment | strict_span_or_granularity_failure | roman | Roman Empire |
| 172 | compact_final_contract | evidence_or_content | content_mismatch_after_public_state | 48982 | 646,889 |
| 172 | final_contract | evidence_or_content | content_mismatch_after_public_state | 48982 | 1,324,108 |
| 173 | compact_final_contract | target_contract | frozen_question_target_rescue | pasek paul | Pasek and Paul |
| 173 | final_contract | final_answer_commitment | strict_span_or_granularity_failure | pasek paul | Pasek and Paul |
| 174 | compact_final_contract | target_authority | public_target_without_question_regression | city of newcastle | City of Newcastle |
| 174 | final_contract | evidence_or_content | content_mismatch_after_public_state | city of newcastle | The City of Newcastle is a local government area in the Hunter region of New South Wales, Australia. However, it is not directly south of Shelly Beach. |
| 175 | compact_final_contract | target_contract | frozen_question_target_rescue | yes | Danny Jones is a musician. |
| 175 | final_contract | target_contract | frozen_question_target_rescue | yes | Danny Jones is a musician. |
| 176 | compact_final_contract | target_authority | public_target_without_question_regression | drawings | drawings |

## Caveats

- These are heuristic field-bridge labels over a saved-field re-answering packet.
- Labels use gold correctness and span-family audits, so they are evaluation labels, not runtime verifier decisions.
- A unit can trigger several signals; `bridge_layer` is the highest-priority label for inspection.
