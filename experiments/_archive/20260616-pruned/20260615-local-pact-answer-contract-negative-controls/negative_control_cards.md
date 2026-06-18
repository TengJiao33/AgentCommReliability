# PACT Answer-Contract Negative Controls

These cards are matched controls for the positive answer-contract audit seed.
They come from non-target bridge layers and test whether the audit is selective.

## Counts

- Cards: `146`
- Seed cards: `24`
- Slices: `{'offset100': 69, 'offset150': 77}`
- Control layers: `{'evidence_or_content': 53, 'final_answer_commitment': 40, 'stable_answer': 53}`
- Control families: `{'content_mismatch_after_public_state': 53, 'final_candidate_attractor_regression': 5, 'final_candidate_rescue': 2, 'stable_right_under_public_state': 53, 'strict_span_or_granularity_failure': 33}`
- Expected primary surfaces: `{'evidence_or_content_failure': 53, 'final_candidate_attractor': 5, 'final_candidate_helpful_commitment': 2, 'no_answer_contract_failure': 53, 'strict_span_or_granularity_surface': 33}`

## Seed Cards

| Slice | Sample | Source | Layer | Family | Expected surface | Gold | Public target | Base | Frozen | Target-only |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| offset100 | 100 | baseline | evidence_or_content | content_mismatch_after_public_state | evidence_or_content_failure | coahuila mexico | Confirm location of descendants of Black Seminoles. | Seminole County, Oklahoma | Seminole County, Oklahoma | Seminole County, Oklahoma |
| offset100 | 100 | final_contract | evidence_or_content | content_mismatch_after_public_state | evidence_or_content_failure | coahuila mexico | Provide location of descendants of Black Seminoles. | Seminole County, Oklahoma | Seminole County, Oklahoma | Seminole County, Oklahoma |
| offset100 | 107 | baseline | evidence_or_content | content_mismatch_after_public_state | evidence_or_content_failure | business | Provide information about the common activity between Owner earnings and Warren Buffett. | investment | investment | investment |
| offset100 | 107 | final_contract | evidence_or_content | content_mismatch_after_public_state | evidence_or_content_failure | business | Provide relevant fact | investment analysis | investment analysis | Owner earnings is a valuation method detailed by Warren Buffett in 1986. |
| offset100 | 102 | baseline | final_answer_commitment | final_candidate_attractor_regression | final_candidate_attractor | 2003 | Provide the draft year of Boss Bailey. | 2003 | 2003 | 2003 |
| offset100 | 102 | final_contract | final_answer_commitment | final_candidate_attractor_regression | final_candidate_attractor | 2003 | Provide the draft year of Boss Bailey. | 2003 | 2003 | 2003 |
| offset100 | 103 | baseline | final_answer_commitment | strict_span_or_granularity_failure | strict_span_or_granularity_surface | north avenue at techwood drive | Provide the exact location details of Grant Field. | the corner of North Avenue at Techwood Drive | at the corner of North Avenue at Techwood Drive | The corner of North Avenue at Techwood Drive on the campus of the Georgia Institute of Technology in Atlanta. |
| offset100 | 103 | final_contract | final_answer_commitment | strict_span_or_granularity_failure | strict_span_or_granularity_surface | north avenue at techwood drive | Provide the specific location of the stadium. | at the corner of North Avenue at Techwood Drive | at the corner of North Avenue at Techwood Drive | corner of North Avenue at Techwood Drive |
| offset100 | 104 | baseline | stable_answer | stable_right_under_public_state | no_answer_contract_failure | leo varadkar | Provide the name of the Irish Fine Gael politician who has served as Taoiseach and Minister for Defence since June 2017. | Leo Varadkar | Leo Varadkar | Leo Varadkar |
| offset100 | 104 | final_contract | stable_answer | stable_right_under_public_state | no_answer_contract_failure | leo varadkar | Provide the name of the Irish Fine Gael politician who has served as Taoiseach and Minister for Defence since June 2017. | Leo Varadkar | Leo Varadkar | Leo Varadkar |
| offset100 | 105 | baseline | stable_answer | stable_right_under_public_state | no_answer_contract_failure | george raft | Confirm the American film actor and dancer who starred in the 1945 film Johnny Angel. | George Raft | George Raft | George Raft |
| offset100 | 105 | final_contract | stable_answer | stable_right_under_public_state | no_answer_contract_failure | george raft | Provide the answer about the American film actor and dancer who starred in the 1945 film Johnny Angel. | George Raft | George Raft | George Raft |
| offset150 | 160 | compact_final_contract | evidence_or_content | content_mismatch_after_public_state | evidence_or_content_failure | kathryn jean martin | Provide the name of the person who held the longest service record for a woman in the Australian Parliament. | Kathy Sullivan | Kathy Sullivan | Kathy Sullivan |
| offset150 | 160 | final_contract | evidence_or_content | content_mismatch_after_public_state | evidence_or_content_failure | kathryn jean martin | Provide the name of the woman who held the record for the longest service in the Australian Parliament before it was surpassed. | Kathy Sullivan | Kathy Sullivan | Kathy Sullivan |
| offset150 | 164 | compact_final_contract | evidence_or_content | content_mismatch_after_public_state | evidence_or_content_failure | sean yseult | Request information about Sean Yseult's spouse. | None of the provided paragraphs contain information about Sean Yseult's spouse. | None of the provided paragraphs contain information about Sean Yseult's spouse. | None of the provided paragraphs contain information about Sean Yseult's spouse. |
| offset150 | 165 | compact_final_contract | evidence_or_content | content_mismatch_after_public_state | evidence_or_content_failure | prescription drug user fee act | Provide information about the amount spent by the Center for Veterinary Medicine in 2017. | The provided context does not contain information about the Center for Veterinary Medicine spending in 2017. | The provided context does not contain information about the Center for Veterinary Medicine spending in 2017. | The provided context does not contain information about the Center for Veterinary Medicine spending in 2017. |
| offset150 | 153 | compact_final_contract | final_answer_commitment | final_candidate_attractor_regression | final_candidate_attractor | seven | Provide the number of top 20 US albums for Harry Connick Jr. | seven | seven | seven |
| offset150 | 154 | compact_final_contract | final_answer_commitment | final_candidate_attractor_regression | final_candidate_attractor | yes | Confirm if Broughtonia and Laeliocattleya are both orchids. | Yes | Yes | Yes |
| offset150 | 157 | compact_final_contract | final_answer_commitment | final_candidate_attractor_regression | final_candidate_attractor | lush ltd | Provide information about a retailer headquartered in Poole, Dorset, United Kingdom. | Lush Ltd. | Lush Ltd. | Lush Ltd. |
| offset150 | 157 | final_contract | final_answer_commitment | strict_span_or_granularity_failure | strict_span_or_granularity_surface | lush ltd | Determine if Lush is a retailer in ABQ Uptown. | Lush | Lush | Lush is an anchor tenant in ABQ Uptown, which indicates that Lush is indeed a retailer there. However, based on the instruction to return only the shortest answer span from the given evidence, the answer is: Action Result: Lush |
| offset150 | 150 | compact_final_contract | stable_answer | stable_right_under_public_state | no_answer_contract_failure | director | [confirm the shared occupation of David Yates and Pietro Germi] | director | director | director |
| offset150 | 151 | compact_final_contract | stable_answer | stable_right_under_public_state | no_answer_contract_failure | 1901 | Provide the year the American League was established. | 1901 | 1901 | 1901 |
| offset150 | 151 | final_contract | stable_answer | stable_right_under_public_state | no_answer_contract_failure | 1901 | Provide the year the American League was established. | 1901 | 1901 | 1901 |
| offset150 | 155 | compact_final_contract | stable_answer | stable_right_under_public_state | no_answer_contract_failure | brazil | Provide the location where the 2014 World Cup was held. | Brazil | Brazil | Brazil |

## Boundary

The seed is a labeling packet, not a specificity result. A real verifier still needs manual or model-judged labels over these controls.
