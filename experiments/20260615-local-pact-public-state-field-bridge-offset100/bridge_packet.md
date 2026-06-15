# PACT Field Bridge From Packet

This bridge audit is built from evaluated public-state field packet rows, not from the older offset50 case atlas.

## Sources

- Evaluated rows: `experiments\20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b\evaluation\evaluated_rows.jsonl`
- Span rows: `experiments\20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b\span_granularity_audit\span_granularity_rows.jsonl`
- Packet rows: `experiments\20260615-local-pact-public-state-field-packet-offset100\field_packet.jsonl`

## Counts

- Units: `100`
- Unique samples: `50`

| Bridge layer | Count | Sample:source units |
| --- | --- | --- |
| evidence_or_content | 25 | 100:baseline, 100:final_contract, 107:baseline, 107:final_contract, 108:final_contract, 111:final_contract, 113:baseline, 113:final_contract, 116:final_contract, 117:baseline, 117:final_contract, 120:baseline, 120:final_contract, 128:final_contract, 129:baseline, 129:final_contract, 131:baseline, 134:baseline, 134:final_contract, 137:baseline |
| final_answer_commitment | 18 | 102:baseline, 102:final_contract, 103:baseline, 103:final_contract, 112:baseline, 115:final_contract, 116:baseline, 123:baseline, 125:baseline, 125:final_contract, 128:baseline, 138:baseline, 138:final_contract, 140:baseline, 140:final_contract, 142:final_contract, 147:baseline, 147:final_contract |
| stable_answer | 26 | 104:baseline, 104:final_contract, 105:baseline, 105:final_contract, 106:final_contract, 109:baseline, 109:final_contract, 110:baseline, 110:final_contract, 111:baseline, 114:final_contract, 121:baseline, 121:final_contract, 124:baseline, 124:final_contract, 126:final_contract, 127:baseline, 127:final_contract, 132:baseline, 132:final_contract |
| target_authority | 20 | 101:baseline, 101:final_contract, 114:baseline, 115:baseline, 118:baseline, 122:baseline, 122:final_contract, 126:baseline, 130:final_contract, 131:final_contract, 135:baseline, 135:final_contract, 141:baseline, 141:final_contract, 144:baseline, 144:final_contract, 145:baseline, 145:final_contract, 148:baseline, 148:final_contract |
| target_contract | 10 | 106:baseline, 108:baseline, 112:final_contract, 118:final_contract, 119:baseline, 119:final_contract, 123:final_contract, 130:baseline, 142:baseline, 149:final_contract |
| target_field_ablation | 1 | 149:baseline |

| Bridge family | Count | Sample:source units |
| --- | --- | --- |
| content_mismatch_after_public_state | 25 | 100:baseline, 100:final_contract, 107:baseline, 107:final_contract, 108:final_contract, 111:final_contract, 113:baseline, 113:final_contract, 116:final_contract, 117:baseline, 117:final_contract, 120:baseline, 120:final_contract, 128:final_contract, 129:baseline, 129:final_contract, 131:baseline, 134:baseline, 134:final_contract, 137:baseline |
| final_candidate_attractor_regression | 2 | 102:baseline, 102:final_contract |
| frozen_question_target_regression | 1 | 149:final_contract |
| frozen_question_target_rescue | 7 | 106:baseline, 108:baseline, 118:final_contract, 119:baseline, 119:final_contract, 123:final_contract, 130:baseline |
| public_target_helped_when_question_visible | 1 | 149:baseline |
| public_target_without_question_regression | 20 | 101:baseline, 101:final_contract, 114:baseline, 115:baseline, 118:baseline, 122:baseline, 122:final_contract, 126:baseline, 130:final_contract, 131:final_contract, 135:baseline, 135:final_contract, 141:baseline, 141:final_contract, 144:baseline, 144:final_contract, 145:baseline, 145:final_contract, 148:baseline, 148:final_contract |
| stable_right_under_public_state | 26 | 104:baseline, 104:final_contract, 105:baseline, 105:final_contract, 106:final_contract, 109:baseline, 109:final_contract, 110:baseline, 110:final_contract, 111:baseline, 114:final_contract, 121:baseline, 121:final_contract, 124:baseline, 124:final_contract, 126:final_contract, 127:baseline, 127:final_contract, 132:baseline, 132:final_contract |
| strict_span_or_granularity_failure | 16 | 103:baseline, 103:final_contract, 112:baseline, 115:final_contract, 116:baseline, 123:baseline, 125:baseline, 125:final_contract, 128:baseline, 138:baseline, 138:final_contract, 140:baseline, 140:final_contract, 142:final_contract, 147:baseline, 147:final_contract |
| target_drift_rescued_by_question_projection | 2 | 112:final_contract, 142:baseline |

## Delta Signals

| Signal | Outcome counts |
| --- | --- |
| freeze_question_target | {'both_right': 47, 'both_wrong': 41, 'regression': 3, 'rescue': 9} |
| hide_public_target | {'both_right': 43, 'both_wrong': 46, 'regression': 7, 'rescue': 4} |
| hide_question_keep_public_target | {'both_right': 30, 'both_wrong': 50, 'regression': 20} |
| show_final_answer_candidate | {'both_right': 40, 'both_wrong': 47, 'regression': 10, 'rescue': 3} |

## Non-Stable Focus Units

| Sample | Source | Layer | Family | Gold | Base prediction |
| --- | --- | --- | --- | --- | --- |
| 100 | baseline | evidence_or_content | content_mismatch_after_public_state | coahuila mexico | Seminole County, Oklahoma |
| 100 | final_contract | evidence_or_content | content_mismatch_after_public_state | coahuila mexico | Seminole County, Oklahoma |
| 101 | baseline | target_authority | public_target_without_question_regression | larnelle harris | Larnelle Harris |
| 101 | final_contract | target_authority | public_target_without_question_regression | larnelle harris | Larnelle Harris |
| 102 | baseline | final_answer_commitment | final_candidate_attractor_regression | 2003 | 2003 |
| 102 | final_contract | final_answer_commitment | final_candidate_attractor_regression | 2003 | 2003 |
| 103 | baseline | final_answer_commitment | strict_span_or_granularity_failure | north avenue at techwood drive | the corner of North Avenue at Techwood Drive |
| 103 | final_contract | final_answer_commitment | strict_span_or_granularity_failure | north avenue at techwood drive | at the corner of North Avenue at Techwood Drive |
| 106 | baseline | target_contract | frozen_question_target_rescue | 1887 | The given context does not provide the birth year of John Cecil Holm. |
| 107 | baseline | evidence_or_content | content_mismatch_after_public_state | business | investment |
| 107 | final_contract | evidence_or_content | content_mismatch_after_public_state | business | investment analysis |
| 108 | baseline | target_contract | frozen_question_target_rescue | 7 october 1978 | 1978 |
| 108 | final_contract | evidence_or_content | content_mismatch_after_public_state | 7 october 1978 | 1981 |
| 111 | final_contract | evidence_or_content | content_mismatch_after_public_state | three centuries | 3 |
| 112 | baseline | final_answer_commitment | strict_span_or_granularity_failure | 7 january 1936 | 1936 |
| 112 | final_contract | target_contract | target_drift_rescued_by_question_projection | 7 january 1936 | 1936 |
| 113 | baseline | evidence_or_content | content_mismatch_after_public_state | george archainbaud | Ralph Murphy |
| 113 | final_contract | evidence_or_content | content_mismatch_after_public_state | george archainbaud | Ralph Murphy died first. |
| 114 | baseline | target_authority | public_target_without_question_regression | picric acid | Picric acid |
| 115 | baseline | target_authority | public_target_without_question_regression | 230 | 230 |
| 115 | final_contract | final_answer_commitment | strict_span_or_granularity_failure | 230 | more than 230 |
| 116 | baseline | final_answer_commitment | strict_span_or_granularity_failure | marvel | Marvel Comics character |
| 116 | final_contract | evidence_or_content | content_mismatch_after_public_state | marvel | Ghost Rider |
| 117 | baseline | evidence_or_content | content_mismatch_after_public_state | united states senator | U.S. Senator from Maryland |
| 117 | final_contract | evidence_or_content | content_mismatch_after_public_state | united states senator | U.S. Representative |
| 118 | baseline | target_authority | public_target_without_question_regression | no | No. |
| 118 | final_contract | target_contract | frozen_question_target_rescue | no | Skin Yard is from the U.S., and Ostava is not. |
| 119 | baseline | target_contract | frozen_question_target_rescue | yes | Daryl Hall and Gerry Marsden are both musicians. |
| 119 | final_contract | target_contract | frozen_question_target_rescue | yes | Both Daryl Hall and Gerry Marsden are musicians. |
| 120 | baseline | evidence_or_content | content_mismatch_after_public_state | a41 | A41/A5117 |
| 120 | final_contract | evidence_or_content | content_mismatch_after_public_state | a41 | A5117 |
| 122 | baseline | target_authority | public_target_without_question_regression | spiderwick chronicles | The Spiderwick Chronicles |
| 122 | final_contract | target_authority | public_target_without_question_regression | spiderwick chronicles | The Spiderwick Chronicles |
| 123 | baseline | final_answer_commitment | strict_span_or_granularity_failure | kkr co | KKR & Co. L.P. |
| 123 | final_contract | target_contract | frozen_question_target_rescue | kkr co | KKR & Co. L.P. (Kohlberg Kravis Roberts) |
| 125 | baseline | final_answer_commitment | strict_span_or_granularity_failure | richmond | Richmond River |
| 125 | final_contract | final_answer_commitment | strict_span_or_granularity_failure | richmond | Richmond River |
| 126 | baseline | target_authority | public_target_without_question_regression | owsley stanley | Owsley Stanley |
| 128 | baseline | final_answer_commitment | strict_span_or_granularity_failure | san luis obispo california | the 700 block of Higuera Street in downtown San Luis Obispo, California |
| 128 | final_contract | evidence_or_content | content_mismatch_after_public_state | san luis obispo california | Bubblegum Alley is located in the 700 block of Higuera Street in downtown San Luis Obispo. |

## Caveats

- These are heuristic field-bridge labels over a saved-field re-answering packet.
- Labels use gold correctness and span-family audits, so they are evaluation labels, not runtime verifier decisions.
- A unit can trigger several signals; `bridge_layer` is the highest-priority label for inspection.
