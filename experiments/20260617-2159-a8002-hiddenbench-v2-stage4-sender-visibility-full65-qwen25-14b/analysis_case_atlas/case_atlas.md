# HiddenBench Stage 4 Full65 Case Atlas

## Counts

- Tasks: `65`
- Clean subset (`full_info` and `oracle_public_facts` correct): `55`
- Clean visibility split cases where `blind_minimal_exchange` differs from any visibility-minimal condition: `1`
- Clean old-exchange failures where `blind_minimal_exchange` is correct: `32`

## Visibility Split Cases

### Task 5 `baker_2010`

- Gold: `Roberts`
- Split conditions: `private_plus_options_minimal_exchange, private_plus_shared_minimal_exchange, full_visibility_minimal_exchange`
- Answers: `blind_minimal_exchange`=Roberts OK; `fact_only_exchange`=Roberts OK; `private_plus_task_minimal_exchange`=Roberts OK; `private_plus_options_minimal_exchange`=Jones WRONG; `private_plus_shared_minimal_exchange`=Jones WRONG; `full_visibility_minimal_exchange`=Jones WRONG; `exchange_then_decide`=Jones WRONG
- `blind_minimal_exchange` final: Answer: Roberts - Roberts has extensive experience in higher education, having served as Dean of the College of Arts and Sciences and later as Dean of a large private university, indicating a strong background in academic leadership. - Despite his time as a senator, Roberts is described by previous colleagues as a thoughtful leader and good listener, suggesting a commitment to shared governance and faculty involvemen
- `fact_only_exchange` final: Answer: Roberts - Roberts has extensive experience in higher education, having served as Dean of the College of Arts and Sciences and later as Dean of a large private university in Georgia. - Despite his recent absence from higher education, Roberts' previous roles indicate a commitment to shared governance and a collaborative decision-making style, which aligns with the university's need for a leader who can inspire
- `private_plus_options_minimal_exchange` final: Answer: Jones - Jones has been an active member of Higher Education University's Board of Trustees and is deeply involved in the current $150 million capital campaign, indicating a strong commitment to the university. - Jones' experience as a visiting professor and his well-liked status among students suggest a strong connection with the academic community and a commitment to teaching and scholarship. - Despite some 
- `private_plus_shared_minimal_exchange` final: Answer: Jones - Jones has extensive experience in fundraising, which is critical for a private liberal arts college. His involvement in the $150 million capital campaign and his background in raising significant funds indicate his capability in this area. - Jones has a strong connection to Higher Education University, having served on the Board of Trustees and as a visiting professor, showing his commitment and under
- `full_visibility_minimal_exchange` final: Answer: Jones - Jones has extensive experience with Higher Education University through his role on the Board of Trustees and his involvement in the $150 million capital campaign, indicating a deep understanding of the institution's needs and goals. - His strategic thinking and leadership in a law firm, as well as his success in high-stakes legal cases, suggest strong problem-solving and leadership skills, which are 
- `exchange_then_decide` final: Answer: Jones - Active member of the Board of Trustees and involved in the current capital campaign, showing direct involvement with the university. - Well-liked as a teacher, indicating positive interactions with students and faculty. - Strategic thinker with experience in employment law, aligning with the university's need for leadership and fundraising.

## Old Exchange Failure Pattern

Across clean old-exchange failures, old exchange messages aggregate `recommendation_leakage_count=113`, `shared_fact_overtalk_count=59`, `possible_answer_mention_count=120` over `125` messages.

| Task | Name | Gold | Old Exchange | Blind Minimal | Fact Only | Full Visibility Minimal |
| ---: | --- | --- | --- | --- | --- | --- |
| 3 | `evacuation_east_town` | `East Town` | `West City` | `East Town` | `East Town` | `East Town` |
| 5 | `baker_2010` | `Roberts` | `Jones` | `Roberts` | `Roberts` | `Jones` |
| 7 | `graetz_et_al_1998` | `Starlight Incorporated` | `Franklin Enterprises` | `Starlight Incorporated` | `Starlight Incorporated` | `Starlight Incorporated` |
| 10 | `emergency_supply_drop` | `Warehouse C` | `Warehouse B` | `Warehouse C` | `Warehouse C` | `Warehouse C` |
| 11 | `emergency_conference_relocation` | `School Gym` | `City Library` | `School Gym` | `School Gym` | `School Gym` |
| 12 | `evacuate_park_dilemma` | `Green Valley` | `Red Lake` | `Green Valley` | `Green Valley` | `Green Valley` |
| 14 | `lunch_group_decision` | `Restaurant C` | `Restaurant B` | `Restaurant C` | `Restaurant C` | `Restaurant C` |
| 15 | `artifact_safe_haven` | `Downtown Police Station` | `University Library` | `Downtown Police Station` | `Downtown Police Station` | `Downtown Police Station` |
| 17 | `scientists_animal_base_decision` | `Plateau Camp (D)` | `Deep Jungle Site (A)` | `Plateau Camp (D)` | `Plateau Camp (D)` | `Plateau Camp (D)` |
| 18 | `choosing_base_camp` | `Camp Pinecone` | `Camp Summit` | `Camp Pinecone` | `Camp Pinecone` | `Camp Pinecone` |
| 21 | `emergency_transportation_decision` | `Celestia Airstrip` | `Borealis Bus Terminal` | `Celestia Airstrip` | `Celestia Airstrip` | `Celestia Airstrip` |
| 22 | `Antarctic Storm Safe Haven` | `Main Base` | `Rescue Outpost` | `Main Base` | `Main Base` | `Main Base` |
| 23 | `community_banquet_venue_decision` | `Grand Oak Hotel` | `Heritage Public Library` | `Grand Oak Hotel` | `Grand Oak Hotel` | `Grand Oak Hotel` |
| 26 | `manuscript_flood_shelter` | `Town Hall` | `University Science Library (USL)` | `Town Hall` | `Town Hall` | `Town Hall` |
| 27 | `research_station_site_selection` | `Pine Ridge` | `Copper Lake` | `Pine Ridge` | `Pine Ridge` | `Pine Ridge` |
| 30 | `the_lead_investor_decision` | `Skylake Ventures` | `Peak Capital` | `Skylake Ventures` | `Skylake Ventures` | `Skylake Ventures` |
| 31 | `weather_sensor_deployment` | `Gamma Lake` | `Beta Valley` | `Gamma Lake` | `Gamma Lake` | `Gamma Lake` |
| 32 | `critical_vaccine_route` | `Route C (Old Supply Road)` | `Route B (Frozen Lake)` | `Route C (Old Supply Road)` | `Route C (Old Supply Road)` | `Route C (Old Supply Road)` |
| 33 | `Critical Sample Transfer` | `Lab Nova` | `Lab Gemini` | `Lab Nova` | `Lab Nova` | `Lab Nova` |
| 38 | `storm_recovery_clinic_site_selection` | `Site C (Hilltop park)` | `Site B (Community sports center)` | `Site C (Hilltop park)` | `Site C (Hilltop park)` | `Site C (Hilltop park)` |
| 41 | `Space Evacuation Decision` | `Mars Colony` | `Lunar Base` | `Mars Colony` | `Mars Colony` | `Mars Colony` |
| 44 | `Choosing the Safe Offsite Venue` | `Hilltop Retreat` | `Riverside Conference Center` | `Hilltop Retreat` | `Hilltop Retreat` | `Hilltop Retreat` |
| 46 | `emergency_evacuation_center_choice` | `Riverside School Gym` | `Downtown Library Hall` | `Riverside School Gym` | `Riverside School Gym` | `Riverside School Gym` |
| 47 | `Find the Missing Prototype` | `CEO's Office` | `Storage Room` | `CEO's Office` | `CEO's Office` | `CEO's Office` |
| 50 | `secure_meeting_room_decision` | `Conference Room Gamma` | `Conference Room Beta` | `Conference Room Gamma` | `Conference Room Gamma` | `Conference Room Gamma` |
| 51 | `emergency_supply_distribution` | `Charlie Storage` | `Bravo Storage` | `Charlie Storage` | `Charlie Storage` | `Charlie Storage` |
| 52 | `mountain_storm_shelter` | `Green Valley Outpost` | `Red Cliff Lodge` | `Green Valley Outpost` | `Green Valley Outpost` | `Green Valley Outpost` |
| 54 | `island_research_base_choice` | `Site C` | `Site B` | `Site C` | `Site C` | `Site C` |
| 55 | `emergency_drone_delivery` | `Hospital` | `School` | `Hospital` | `Hospital` | `Hospital` |
| 56 | `Secure the Masterpiece` | `The Government Records Vault` | `The University Science Building's Secure Lab` | `The Government Records Vault` | `The Government Records Vault` | `The Government Records Vault` |
| 58 | `secure_negotiation_site_selection` | `The Old Museum Basement` | `City Hall Annex` | `The Old Museum Basement` | `The Old Museum Basement` | `The Old Museum Basement` |
| 59 | `last_minute_move` | `Bravo Moving Co.` | `Charlie’s Transport` | `Bravo Moving Co.` | `Bravo Moving Co.` | `Bravo Moving Co.` |

## Representative Old Exchange Failures

### Task 3 `evacuation_east_town`

- Gold: `East Town`; old exchange parsed `West City`; blind parsed `East Town`.
- Old audit: recommendation `4`, shared overtalk `4`, answer mentions `4` over `4` messages.
- Old sender example: - The river level is just below the bridge to West City, making it a risky option as the rain could cause the river to rise quickly. - West City's hotels are prepared with food and medical supplies, which is reassuring. - East Town has offered accommodations but there might be a shortage of volunteers, which could affect the care of elderly and children. - North Hill's school can serve as a temporary evacuation cente
- Blind final: Answer: East Town - The dam upstream will release water, making the route to West City dangerous. - The walking trails to North Hill are closed, and a mudslide has blocked the driveway. - East Town, although with concerns about volunteer assistance, remains the safest and most accessible option given the current conditions.

### Task 5 `baker_2010`

- Gold: `Roberts`; old exchange parsed `Jones`; blind parsed `Roberts`.
- Old audit: recommendation `4`, shared overtalk `0`, answer mentions `4` over `4` messages.
- Old sender example: Based on the provided information, here are the key points to consider: - **Stevens**: - Extensive experience in higher education administration, including provost and dean roles. - Strong background in information technology, recognized by both academics and business leaders. - Emphasized collaboration and demonstrated excellent oratory skills. - However, left the Mississippi University before securing funds for the
- Blind final: Answer: Roberts - Roberts has extensive experience in higher education, having served as Dean of the College of Arts and Sciences and later as Dean of a large private university, indicating a strong background in academic leadership. - Despite his time as a senator, Roberts is described by previous colleagues as a thoughtful leader and good listener, suggesting a commitment to shared governance and faculty involvemen

### Task 7 `graetz_et_al_1998`

- Gold: `Starlight Incorporated`; old exchange parsed `Franklin Enterprises`; blind parsed `Starlight Incorporated`.
- Old audit: recommendation `4`, shared overtalk `4`, answer mentions `4` over `4` messages.
- Old sender example: - Franklin Enterprises meets criteria (d), (e), (f), (g), and (h) but fails (b), (c), (i), and (j). - Starlight Incorporated fails criteria (a) and (c) but meets (b) and (d). - Cape Industries meets criteria (a), (d), (e), (i), and (j) but fails (g). - Tentative recommendation: Evaluate Starlight Incorporated and Cape Industries more closely as Franklin Enterprises fails multiple critical criteria.
- Blind final: Answer: Starlight Incorporated - Franklin Enterprises fails to meet criteria (a), (c), (i), and (j). - Cape Industries fails to meet criteria (c), (g), (h), and (i). - Starlight Incorporated meets all criteria except (a) and (c), but these can be potentially addressed through further negotiation or alternative solutions.

### Task 10 `emergency_supply_drop`

- Gold: `Warehouse C`; old exchange parsed `Warehouse B`; blind parsed `Warehouse C`.
- Old audit: recommendation `4`, shared overtalk `0`, answer mentions `4` over `4` messages.
- Old sender example: - Warehouse A is no longer a viable option due to the collapsed bridge, which prevents the distribution of supplies. - Warehouse B has upgraded access roads, making it the fastest to reach from the airstrip. - Warehouse B is adjacent to an emergency response center, which can facilitate quicker distribution and management of supplies. - Given the current situation, Warehouse B seems to be the safest and most efficien
- Blind final: Answer: Warehouse C - Warehouse A is inaccessible due to the collapsed bridge and debris, making it impossible to distribute supplies. - Warehouse B, although upgraded, poses a health risk due to rising levels of noxious gases from the chemical plant. - Warehouse C, while farther by road, has confirmed open elevated service roads leading to temporary shelters, ensuring safe and effective distribution of supplies.

### Task 11 `emergency_conference_relocation`

- Gold: `School Gym`; old exchange parsed `City Library`; blind parsed `School Gym`.
- Old audit: recommendation `4`, shared overtalk `4`, answer mentions `4` over `4` messages.
- Old sender example: - The City Library has a large conference room and a backup generator, but the generator only has enough fuel for 2 hours due to a citywide gasoline shortage. - The Community Center is centrally located and fully accessible, with staff already evacuated in advance of the heat wave. - The School Gym has air conditioning but older facilities, and there are potential restroom issues that a maintenance team is addressing
- Blind final: Answer: School Gym - The City Library's backup generator can only provide power for 2 hours, which is insufficient for a full day of events. - The Community Center has a chemical leak in the basement, making it unsafe for a day-long event. - The School Gym, despite restroom issues, has air conditioning and will have at least two working restrooms available within an hour, making it the safest option for attendees.

### Task 12 `evacuate_park_dilemma`

- Gold: `Green Valley`; old exchange parsed `Red Lake`; blind parsed `Green Valley`.
- Old audit: recommendation `4`, shared overtalk `1`, answer mentions `4` over `4` messages.
- Old sender example: - Green Valley campground has warning signs due to a recent pest outbreak, but local officials have confirmed it is open for emergency evacuations with extra staff on site. - Blueberry Ridge lodge is equipped with emergency power generators and a medical station, and they have started preparing rooms for evacuees. - Red Lake community hall has experience hosting large groups and received bulk food supplies earlier to
- Blind final: Answer: Green Valley - Red Lake is inaccessible due to a closed route caused by a sinkhole. - Blueberry Ridge lost all power and has a collapsed bridge, making it unreachable by vehicle and only accessible to those who can walk long distances. - Green Valley, despite a recent pest outbreak, is confirmed open for emergency evacuations and is preparing to accommodate evacuees with necessary supplies.

### Task 14 `lunch_group_decision`

- Gold: `Restaurant C`; old exchange parsed `Restaurant B`; blind parsed `Restaurant C`.
- Old audit: recommendation `3`, shared overtalk `2`, answer mentions `4` over `4` messages.
- Old sender example: - Restaurant A is offering a new seafood combo, which might not be suitable for the team member with a shellfish allergy. - Restaurant A has received a health department warning about a norovirus outbreak among its cooks. - Restaurant B has recently added more vegetarian options and is known for being quiet at midday. - Given the health warning and the need for a quiet atmosphere and suitable food options, I tentativ
- Blind final: Answer: Restaurant C - Restaurant A is not an option due to the norovirus outbreak warning among its cooks. - Restaurant B is not safe for the person with a shellfish allergy due to kitchen contamination. - Restaurant C, despite a private event and a power outage, still offers a quiet secondary dining room and a cold menu that is safe and available.

### Task 15 `artifact_safe_haven`

- Gold: `Downtown Police Station`; old exchange parsed `University Library`; blind parsed `Downtown Police Station`.
- Old audit: recommendation `4`, shared overtalk `0`, answer mentions `4` over `4` messages.
- Old sender example: - The University Library is built on higher ground and has never experienced flooding, making it a secure location against rising river levels. - The City Bank, while equipped with a modern steel vault and backup generator, is located in an area at risk for both power outages and flooding. - The Downtown Police Station is currently crowded due to its use as an emergency shelter, which may compromise security for the 
- Blind final: Answer: Downtown Police Station - The City Bank's backup generator is not functioning, posing a risk to the artifact's safety in the event of a power outage. - The road to the University Library is blocked, making it inaccessible for at least another 24 hours. - The University Library's security detail will be off-site, leaving the artifact without adequate protection.

