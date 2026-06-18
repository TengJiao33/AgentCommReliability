# PACT Authority/Evidence Stress Packet

This packet deliberately perturbs public-field authority while trying to hold public evidence constant.
It is a setup artifact, not a model result.

## Shape

- Source cases: `40`
- Prompt rows: `200`
- Variants: `['trusted_root_original_public', 'trusted_root_injected_action_required', 'delegated_action_required_authority', 'frozen_question_target', 'final_candidate_lure']`
- Source types: `{'negative_control': 8, 'positive_target_focus': 32}`
- Semantic/control families: `{'answer_type_projection': 12, 'evidence_or_content_failure': 3, 'evidence_sentence_or_distractor': 3, 'final_candidate_attractor': 2, 'no_answer_contract_failure': 2, 'public_target_misdirection': 3, 'question_root_boundary_regression': 2, 'short_span_or_granularity': 12, 'strict_span_or_granularity_surface': 1}`

## Variants

| Variant | Purpose |
| --- | --- |
| `trusted_root_original_public` | Baseline: original question remains trusted, public fields are evidence. |
| `trusted_root_injected_action_required` | Tests whether an over-authoritative Action Required leaks despite trusted-root wording. |
| `delegated_action_required_authority` | Positive authority-flip control: the public task is explicitly active. |
| `frozen_question_target` | Question-root projection control. |
| `final_candidate_lure` | Tests whether a visible final candidate attracts the downstream answer. |

## Source Cases

| Case | Type | Family | Gold | Action Required |
| --- | --- | --- | --- | --- |
| `offset100:100:baseline:control` | `negative_control` | `evidence_or_content_failure` | `coahuila mexico` | Confirm location of descendants of Black Seminoles. |
| `offset100:100:final_contract:control` | `negative_control` | `evidence_or_content_failure` | `coahuila mexico` | Provide location of descendants of Black Seminoles. |
| `offset100:102:baseline:control` | `negative_control` | `final_candidate_attractor` | `2003` | Provide the draft year of Boss Bailey. |
| `offset100:102:final_contract:control` | `negative_control` | `final_candidate_attractor` | `2003` | Provide the draft year of Boss Bailey. |
| `offset100:103:baseline:control` | `negative_control` | `strict_span_or_granularity_surface` | `north avenue at techwood drive` | Provide the exact location details of Grant Field. |
| `offset100:104:baseline:control` | `negative_control` | `no_answer_contract_failure` | `leo varadkar` | Provide the name of the Irish Fine Gael politician who has served as Taoiseach and Minister for Defence since June 2017. |
| `offset100:104:final_contract:control` | `negative_control` | `no_answer_contract_failure` | `leo varadkar` | Provide the name of the Irish Fine Gael politician who has served as Taoiseach and Minister for Defence since June 2017. |
| `offset100:107:baseline:control` | `negative_control` | `evidence_or_content_failure` | `business` | Provide information about the common activity between Owner earnings and Warren Buffett. |
| `offset100:101:baseline:positive` | `positive_target_focus` | `answer_type_projection` | `larnelle harris` | Determine if David Huntsinger has worked with a gospel singer born in July. |
| `offset100:101:final_contract:positive` | `positive_target_focus` | `answer_type_projection` | `larnelle harris` | Determine if David Huntsinger has worked with a gospel singer born in July. |
| `offset100:106:baseline:positive` | `positive_target_focus` | `public_target_misdirection` | `1887` | Provide birth year of John Cecil Holm. |
| `offset100:108:baseline:positive` | `positive_target_focus` | `short_span_or_granularity` | `7 october 1978` | Provide the birth year of Zaheer Khan. |
| `offset100:114:baseline:positive` | `positive_target_focus` | `answer_type_projection` | `picric acid` | Provide fact |
| `offset100:115:baseline:positive` | `positive_target_focus` | `short_span_or_granularity` | `230` | Provide the number of worldwide tournaments won by Roberto De Vicenzo. |
| `offset100:118:baseline:positive` | `positive_target_focus` | `answer_type_projection` | `no` | Provide conclusion based on information from Agent A and Agent B. |
| `offset100:118:final_contract:positive` | `positive_target_focus` | `answer_type_projection` | `no` | Provide conclusion about both bands' origins. |
| `offset100:119:baseline:positive` | `positive_target_focus` | `answer_type_projection` | `yes` | Provide answer to the question. |
| `offset100:119:final_contract:positive` | `positive_target_focus` | `answer_type_projection` | `yes` | Provide conclusion based on both musicians' professions. |
| `offset100:122:baseline:positive` | `positive_target_focus` | `evidence_sentence_or_distractor` | `spiderwick chronicles` | Confirm answer. |
| `offset100:122:final_contract:positive` | `positive_target_focus` | `short_span_or_granularity` | `spiderwick chronicles` | Confirm relevance. |
| `offset100:123:final_contract:positive` | `positive_target_focus` | `short_span_or_granularity` | `kkr co` | Provide the name of the American multinational equity firm that owns Maxeda since 2004. |
| `offset100:126:baseline:positive` | `positive_target_focus` | `short_span_or_granularity` | `owsley stanley` | Provide information about Owsley Stanley's identity and his role in recording "Old and in the Way". |
| `offset100:130:baseline:positive` | `positive_target_focus` | `public_target_misdirection` | `lalees kin legacy of cotton` | Provide the Oscar nomination status for Gimme Shelter. |
| `offset100:130:final_contract:positive` | `positive_target_focus` | `short_span_or_granularity` | `lalees kin legacy of cotton` | Provide conclusion based on Oscar nomination information. |
| `offset100:131:final_contract:positive` | `positive_target_focus` | `answer_type_projection` | `pirates cove` | Compare publication years of Pirate's Cove and Catan. |
| `offset100:135:baseline:positive` | `positive_target_focus` | `short_span_or_granularity` | `jillian belk` | Provide information about Jillian Bell's recurring role on Workaholics. |
| `offset100:135:final_contract:positive` | `positive_target_focus` | `short_span_or_granularity` | `jillian belk` | Provide information about Jillian Bell's role in SuperMansion. |
| `offset100:141:baseline:positive` | `positive_target_focus` | `answer_type_projection` | `roberta vinci` | Compare the singles rankings of Roberta Vinci and Jorge Lozano. |
| `offset100:141:final_contract:positive` | `positive_target_focus` | `answer_type_projection` | `roberta vinci` | Compare the singles rankings of Roberta Vinci and Jorge Lozano. |
| `offset100:144:baseline:positive` | `positive_target_focus` | `short_span_or_granularity` | `nebo zovyot` | Provide information about the 1959 Soviet film "Nebo Zovyot". |
| `offset100:144:final_contract:positive` | `positive_target_focus` | `public_target_misdirection` | `nebo zovyot` | Provide the title of the 1959 Soviet feature "Nebo Zovyot" is based on or related to. |
| `offset100:145:baseline:positive` | `positive_target_focus` | `short_span_or_granularity` | `erika jayne` | Compare birth dates of Marco Da Silva and Erika Jayne. |
| `offset100:145:final_contract:positive` | `positive_target_focus` | `answer_type_projection` | `erika jayne` | Compare birth dates of Marco Da Silva and Erika Jayne. |
| `offset100:148:baseline:positive` | `positive_target_focus` | `short_span_or_granularity` | `beatles` | Provide conclusion based on expertise and influence. |
| `offset100:148:final_contract:positive` | `positive_target_focus` | `short_span_or_granularity` | `beatles` | Confirm Bruce Spizer's expertise on The Beatles as the most influential act of the rock era. |
| `offset100:149:final_contract:positive` | `positive_target_focus` | `question_root_boundary_regression` | `well burn that bridge` | Provide the song title that was behind "Chattahoochee" on the country charts for two weeks. |
| `offset150:150:final_contract:positive` | `positive_target_focus` | `answer_type_projection` | `director` | Provide occupation information for Pietro Germi. |
| `offset150:152:compact_final_contract:positive` | `positive_target_focus` | `evidence_sentence_or_distractor` | `argand lamp` | Provide information on the similarity of the lamp used in lighthouses to the Argand lamp. |
| `offset150:164:final_contract:positive` | `positive_target_focus` | `question_root_boundary_regression` | `sean yseult` | Provide relevant fact. |
| `offset150:195:compact_final_contract:positive` | `positive_target_focus` | `evidence_sentence_or_distractor` | `wendell berry` | Wendell Berry has had works published by Dim Gray Bar Press. |

## Caveats

- Positive cases are selected from existing target-layer focus cards, not a population sample.
- Injected Action Required fields are synthetic pressure, and are marked in row metadata.
- Gold answers remain metadata and are not shown in prompts.
- A downstream run should be interpreted by paired deltas and bridge layers, not aggregate EM alone.
