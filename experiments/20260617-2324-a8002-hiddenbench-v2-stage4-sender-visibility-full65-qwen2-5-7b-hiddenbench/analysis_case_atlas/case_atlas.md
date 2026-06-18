# HiddenBench Stage 4 7B Full65 Case Atlas

## Counts

- Tasks: `65`
- Clean subset (`full_info` and `oracle_public_facts` correct): `50`
- Clean visibility split cases where `blind_minimal_exchange` differs from any visibility-minimal condition: `1`
- Clean minimal-condition disagreements: `4`
- Clean old-exchange failures where `blind_minimal_exchange` is correct: `32`

## Clean Condition Counts

- `shared_only`: `2/50`
- `full_info`: `50/50`
- `oracle_public_facts`: `50/50`
- `exchange_then_decide`: `16/50`
- `blind_minimal_exchange`: `47/50`
- `fact_only_exchange`: `47/50`
- `private_plus_task_minimal_exchange`: `47/50`
- `private_plus_options_minimal_exchange`: `47/50`
- `private_plus_shared_minimal_exchange`: `47/50`
- `full_visibility_minimal_exchange`: `46/50`

## Visibility Split Cases

### Task 19 `city_storm_shelter_decision`
- Gold: `Oakridge Library`
- Split conditions: `full_visibility_minimal_exchange`
- Answers: `blind_minimal_exchange`=Oakridge Library OK; `fact_only_exchange`=Greenfield High School WRONG; `private_plus_task_minimal_exchange`=Oakridge Library OK; `private_plus_options_minimal_exchange`=Oakridge Library OK; `private_plus_shared_minimal_exchange`=Oakridge Library OK; `full_visibility_minimal_exchange`=Greenfield High School WRONG; `exchange_then_decide`=Greenfield High School WRONG
- `blind_minimal_exchange` final: Answer: Oakridge Library - Oakridge Library is confirmed to be structurally sound and safe for shelter, contrary to earlier doubts. - While it is a newer shelter, it has passed emergency inspections and is recently renovated. - Although it is a smaller shelter, it is currently the most accessible option with no major infrastructure issues blocking access.
- `fact_only_exchange` final: Answer: Greenfield High School - Greenfield High School's backup generators are now inoperable due to flooding, but it is still the largest and best-stocked shelter with essential supplies. - While access to Greenfield High School is currently blocked, an alternate route from South Street is possible, even though it may be slow. - Oakridge Library's roof is still in question due to incomplete repairs, making it a ris
- `full_visibility_minimal_exchange` final: Answer: Greenfield High School - Greenfield High School's backup generators are now inoperable due to flooding, reducing its reliability as a shelter. - The main avenue to Greenfield High School is blocked by fallen trees, and clearing the path could take too long given the approaching storm. - Oakridge Library's roof repairs are incomplete, making it a less secure option despite being recently renovated.
- `exchange_then_decide` final: Answer: Greenfield High School - Greenfield High School is the primary hurricane shelter and well-equipped with backup generators and essential supplies. - While access is currently blocked, it offers the best resources for residents' safety and preparedness. - Alternative routes should be prepared to ensure access once the blockage is cleared.


## Old Exchange Failure Pattern

Across clean old-exchange failures, old exchange messages aggregate `recommendation_leakage_count=55`, `shared_fact_overtalk_count=73`, `possible_answer_mention_count=115` over `124` messages.

| Task | Name | Gold | Old Exchange | Blind Minimal | Fact Only | Full Visibility Minimal |
| ---: | --- | --- | --- | --- | --- | --- |
| 6 | `schulz_hardt_mojzisch_2012` | `Candidate C` | `Candidate D` | `Candidate C` | `Candidate B` | `Candidate C` |
| 10 | `emergency_supply_drop` | `Warehouse C` | `Warehouse B` | `Warehouse C` | `Warehouse C` | `Warehouse C` |
| 11 | `emergency_conference_relocation` | `School Gym` | `City Library` | `School Gym` | `School Gym` | `School Gym` |
| 12 | `evacuate_park_dilemma` | `Green Valley` | `Red Lake` | `Green Valley` | `Green Valley` | `Green Valley` |
| 14 | `lunch_group_decision` | `Restaurant C` | `Restaurant B` | `Restaurant C` | `Restaurant C` | `Restaurant C` |
| 16 | `Crisis Backup Decision` | `Charlie` | `Bravo` | `Charlie` | `Charlie` | `Charlie` |
| 19 | `city_storm_shelter_decision` | `Oakridge Library` | `Greenfield High School` | `Oakridge Library` | `Greenfield High School` | `Greenfield High School` |
| 20 | `meteor_shower_shelter` | `Shelter Alpha` | `Shelter Beta` | `Shelter Alpha` | `Shelter Alpha` | `Shelter Alpha` |
| 21 | `emergency_transportation_decision` | `Celestia Airstrip` | `Borealis Bus Terminal` | `Celestia Airstrip` | `Celestia Airstrip` | `Celestia Airstrip` |
| 24 | `Critical Data Backup Site Selection` | `City HQ Facility` | `Mountain Server Farm` | `City HQ Facility` | `City HQ Facility` | `City HQ Facility` |
| 26 | `manuscript_flood_shelter` | `Town Hall` | `University Science Library (USL)` | `Town Hall` | `Town Hall` | `Town Hall` |
| 28 | `Rescue the Lost Researchers` | `Forest Trail` | `River Route` | `Forest Trail` | `Forest Trail` | `Forest Trail` |
| 30 | `the_lead_investor_decision` | `Skylake Ventures` | `Peak Capital` | `Skylake Ventures` | `Skylake Ventures` | `Skylake Ventures` |
| 32 | `critical_vaccine_route` | `Route C (Old Supply Road)` | `Route A (Mountain Pass)` | `Route C (Old Supply Road)` | `Route C (Old Supply Road)` | `Route C (Old Supply Road)` |
| 33 | `Critical Sample Transfer` | `Lab Nova` | `Lab Gemini` | `Lab Nova` | `Lab Nova` | `Lab Nova` |
| 36 | `datacenter_emergency_migration` | `Datacenter Gamma` | `Datacenter Beta` | `Datacenter Gamma` | `Datacenter Gamma` | `Datacenter Gamma` |
| 37 | `emergency_warehouse_selection` | `Hilltop Storage` | `Bayview Warehouse` | `Hilltop Storage` | `Hilltop Storage` | `Hilltop Storage` |
| 38 | `storm_recovery_clinic_site_selection` | `Site C (Hilltop park)` | `Site D (Library)` | `Site C (Hilltop park)` | `Site C (Hilltop park)` | `Site C (Hilltop park)` |
| 39 | `emergency_aircraft_landing_site` | `LZ Alpha` | `LZ Bravo` | `LZ Alpha` | `LZ Alpha` | `LZ Alpha` |
| 41 | `Space Evacuation Decision` | `Mars Colony` | `Orion Station` | `Mars Colony` | `Mars Colony` | `Mars Colony` |
| 43 | `The Artifact Delivery` | `Canyon Depot` | `Aurora Station` | `Canyon Depot` | `Canyon Depot` | `Canyon Depot` |
| 44 | `Choosing the Safe Offsite Venue` | `Hilltop Retreat` | `Downtown Hotel` | `Hilltop Retreat` | `Hilltop Retreat` | `Hilltop Retreat` |
| 46 | `emergency_evacuation_center_choice` | `Riverside School Gym` | `Downtown Library Hall` | `Riverside School Gym` | `Riverside School Gym` | `Riverside School Gym` |
| 47 | `Find the Missing Prototype` | `CEO's Office` | `Storage Room` | `CEO's Office` | `CEO's Office` | `CEO's Office` |
| 50 | `secure_meeting_room_decision` | `Conference Room Gamma` | `Conference Room Beta` | `Conference Room Gamma` | `Conference Room Gamma` | `Conference Room Gamma` |
| 51 | `emergency_supply_distribution` | `Charlie Storage` | `Alpha Storage` | `Charlie Storage` | `Charlie Storage` | `Charlie Storage` |
| 52 | `mountain_storm_shelter` | `Green Valley Outpost` | `Blue Lake Cabin` | `Green Valley Outpost` | `Green Valley Outpost` | `Green Valley Outpost` |
| 54 | `island_research_base_choice` | `Site C` | `Site B` | `Site C` | `Site C` | `Site C` |
| 57 | `archaeological_dig_site` | `Site C` | `Site B` | `Site C` | `Site C` | `Site C` |
| 58 | `secure_negotiation_site_selection` | `The Old Museum Basement` | `City Hall Annex` | `The Old Museum Basement` | `The Old Museum Basement` | `The Old Museum Basement` |
| 59 | `last_minute_move` | `Bravo Moving Co.` | `Charlie’s Transport` | `Bravo Moving Co.` | `Bravo Moving Co.` | `Bravo Moving Co.` |
| 64 | `Office Outbreak Mystery` | `Airborne Toxin from HVAC` | `Cafeteria Food` | `Airborne Toxin from HVAC` | `Airborne Toxin from HVAC` | `Airborne Toxin from HVAC` |

## Representative Old Exchange Failures

### Task 6 `schulz_hardt_mojzisch_2012`
- Gold: `Candidate C`; old exchange parsed `Candidate D`; blind parsed `Candidate C`.
- Old audit: recommendation `0`, shared overtalk `2`, answer mentions `3` over `3` messages.
- Old sender example: - Candidate A has excellent spatial vision and leadership qualities, which are crucial for long-distance flights. - Candidate B is reliable and good at assessing weather conditions, which are important for flight safety. - Candidate C can make quick decisions and handles stress well, which are beneficial in high-pressure situations. - Candidate D solves problems extremely well and takes responsibility seriously, indi
- Blind final: Answer: Candidate C - Candidate C is described as understanding complicated technology, which is crucial for long-distance flights. - Candidate C puts concern for others above everything, indicating strong teamwork and leadership qualities. - Candidate C has excellent attention skills, which are vital for maintaining focus during long flights.

### Task 10 `emergency_supply_drop`
- Gold: `Warehouse C`; old exchange parsed `Warehouse B`; blind parsed `Warehouse C`.
- Old audit: recommendation `3`, shared overtalk `1`, answer mentions `4` over `4` messages.
- Old sender example: - The bridge near Warehouse A has completely collapsed, making it inaccessible. - Warehouse B has recently upgraded access roads and is the fastest to reach from the airstrip. - Warehouse B is adjacent to an emergency response center, which can help in distributing supplies quickly. - Based on the available information, Warehouse B appears to be the safest and most efficient option for landing the supply plane.
- Blind final: Answer: Warehouse C - Warehouse A is inaccessible due to a collapsed bridge. - Warehouse B has rising levels of noxious gases, posing a risk to personnel. - Warehouse C has open elevated service roads to temporary shelters, ensuring safe and quick distribution of supplies.

### Task 11 `emergency_conference_relocation`
- Gold: `School Gym`; old exchange parsed `City Library`; blind parsed `School Gym`.
- Old audit: recommendation `0`, shared overtalk `3`, answer mentions `4` over `4` messages.
- Old sender example: - The City Library has a large conference room and a backup generator, but the generator's fuel supply is limited to only 2 hours and cannot be refueled due to a citywide gasoline shortage. - The Community Center is centrally located and fully accessible, having already evacuated in advance of the heat wave. - The School Gym has air conditioning but may have issues with restrooms; a city maintenance team is on its wa
- Blind final: Answer: School Gym - The School Gym has air conditioning, which is crucial given the expected high temperatures. - The restrooms are being restored and will be operational within an hour, addressing the initial concern. - While there are some risks, the other venues have significant issues that make them unsuitable for a full day of events.

### Task 12 `evacuate_park_dilemma`
- Gold: `Green Valley`; old exchange parsed `Red Lake`; blind parsed `Green Valley`.
- Old audit: recommendation `1`, shared overtalk `0`, answer mentions `4` over `4` messages.
- Old sender example: - Blueberry Ridge lodge has emergency power generators and a medical station, indicating robust preparedness. - Red Lake community hall has experience hosting large groups and received food supplies, suggesting it is well-equipped. - Green Valley campground, despite recent pest issues, remains open for evacuations and is preparing for arrivals, showing it can accommodate guests. - Based on current information, Red La
- Blind final: Answer: Green Valley - The only road to Red Lake is closed due to a sinkhole. - Blueberry Ridge has lost all power and is inaccessible via vehicle due to a collapsed bridge. - Green Valley is still open for emergency evacuations and is preparing for arrivals, despite the recent pest outbreak.

### Task 14 `lunch_group_decision`
- Gold: `Restaurant C`; old exchange parsed `Restaurant B`; blind parsed `Restaurant C`.
- Old audit: recommendation `4`, shared overtalk `1`, answer mentions `4` over `4` messages.
- Old sender example: - Restaurant A is currently under a health warning due to a norovirus outbreak among its staff. - Restaurant B offers a quiet atmosphere and has updated its menu with more vegetarian options. - Restaurant C, while walkable, is usually noisy and has recently renovated its dining area. - **Tentative recommendation: Restaurant B** seems to be the most suitable option given the health warning at Restaurant A and the need
- Blind final: Answer: Restaurant C - Restaurant A is offering a seafood combo, which is not suitable for the team member with a shellfish allergy. - Restaurant B has cross-contaminated its kitchen with shellfish, making it unsafe for the team member with a severe shellfish allergy. - Restaurant C, while partially booked, still has a secondary dining room available and its cold menu is fully accessible due to emergency backup power

### Task 16 `Crisis Backup Decision`
- Gold: `Charlie`; old exchange parsed `Bravo`; blind parsed `Charlie`.
- Old audit: recommendation `4`, shared overtalk `4`, answer mentions `4` over `4` messages.
- Old sender example: - Data Center Bravo has the best firewall and intrusion protection according to the latest independent audit report. - Alpha is currently the busiest data center but remains within normal usage. - Charlie has no specific information that differentiates it from the other two centers in terms of reliability or current load. - Considering the need for physical security and rapid accessibility, and the current robust sec
- Blind final: Answer: Charlie - Charlie has recently passed an extra security audit following a cable cut incident, indicating a proactive approach to security and resilience. - There are no immediate public or internal alerts suggesting imminent risks to Charlie's operations. - The legal and regulatory concerns are significant, and Charlie's recent security improvements suggest a higher level of physical security and accessibilit

### Task 19 `city_storm_shelter_decision`
- Gold: `Oakridge Library`; old exchange parsed `Greenfield High School`; blind parsed `Oakridge Library`.
- Old audit: recommendation `3`, shared overtalk `2`, answer mentions `4` over `4` messages.
- Old sender example: - Blue River Community Center's backup generators are inoperable due to flooding, making it an unsafe and unsuitable option. - Greenfield High School remains the most reliable choice with backup generators and stocked supplies, aligning with city plans. - Oakridge Library's hurricane readiness is uncertain due to incomplete roof repairs. - Recommendation: Direct residents to Greenfield High School for safety and prep
- Blind final: Answer: Oakridge Library - Oakridge Library is confirmed to be structurally sound and safe for shelter, contrary to earlier doubts. - While it is a newer shelter, it has passed emergency inspections and is recently renovated. - Although it is a smaller shelter, it is currently the most accessible option with no major infrastructure issues blocking access.

### Task 20 `meteor_shower_shelter`
- Gold: `Shelter Alpha`; old exchange parsed `Shelter Beta`; blind parsed `Shelter Alpha`.
- Old audit: recommendation `3`, shared overtalk `2`, answer mentions `4` over `4` messages.
- Old sender example: - Shelter Alpha has undergone full pressure tests after the leak patch, with results indicating 'excellent' performance. - Shelter Beta offers the best shielding against impacts and sufficient supplies for a week. - Shelter Gamma has a new air purification system installed this week. - Based on the repair log, Shelter Alpha appears to be in excellent condition and is the closest to the main base. Recommendation: Cons
- Blind final: Answer: Shelter Alpha - The repair log for Shelter Alpha indicates that after the leak patch, full pressure tests were completed and results were 'excellent', suggesting it is safe to use. - Shelter Beta has a mysterious usage spike in oxygen canisters and an overdue oxygen alarm system, which could be a sign of a potential issue. - Shelter Gamma has a recall notice for a faulty emergency ventilation back-up that has

