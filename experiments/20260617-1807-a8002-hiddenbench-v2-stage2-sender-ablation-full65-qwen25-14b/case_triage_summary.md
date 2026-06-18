# HiddenBench Stage 2 Full65 Case Triage

## Clean Subset

Clean subset means both `full_info` and `oracle_public_facts` are correct.

- Clean tasks: `55`
- `exchange_then_decide`: `23/55`
- `no_recommendation_exchange`: `28/55`
- `no_shared_repeat_exchange`: `31/55`
- `fact_only_with_options_exchange`: `53/55`
- `fact_only_exchange`: `55/55`
- `fact_only_constraint_decide`: `55/55`

## Key Paired Counts On Clean Subset

- `no_recommendation_exchange` over old exchange: `11` rescues, `6` regressions.
- `no_shared_repeat_exchange` over old exchange: `10` rescues, `2` regressions.
- `fact_only_exchange` over `no_recommendation_exchange`: `27` rescues, `0` regressions.
- `fact_only_exchange` over `no_shared_repeat_exchange`: `24` rescues, `0` regressions.
- `fact_only_exchange` over `fact_only_with_options_exchange`: `2` rescues, `0` regressions.

## Case Lists

`no_recommendation_exchange` rescues over old exchange:

```text
11 emergency_conference_relocation
12 evacuate_park_dilemma
22 Antarctic Storm Safe Haven
23 community_banquet_venue_decision
26 manuscript_flood_shelter
27 research_station_site_selection
30 the_lead_investor_decision
31 weather_sensor_deployment
44 Choosing the Safe Offsite Venue
47 Find the Missing Prototype
56 Secure the Masterpiece
```

`no_recommendation_exchange` regressions relative to old exchange:

```text
19 city_storm_shelter_decision
24 Critical Data Backup Site Selection
36 datacenter_emergency_migration
45 Safe Lab Choice After Earthquake
57 archaeological_dig_site
60 The Elusive Bird Sighting
```

`no_shared_repeat_exchange` rescues over old exchange:

```text
7 graetz_et_al_1998
10 emergency_supply_drop
21 emergency_transportation_decision
23 community_banquet_venue_decision
26 manuscript_flood_shelter
27 research_station_site_selection
30 the_lead_investor_decision
31 weather_sensor_deployment
52 mountain_storm_shelter
54 island_research_base_choice
```

`no_shared_repeat_exchange` regressions relative to old exchange:

```text
24 Critical Data Backup Site Selection
49 choosing_the_safe_field_station
```

`fact_only_exchange` extra rescues over `no_recommendation_exchange`:

```text
3 evacuation_east_town
5 baker_2010
7 graetz_et_al_1998
10 emergency_supply_drop
14 lunch_group_decision
15 emergency_response_meeting_location
17 Red River Evacuation
18 Park Evacuation Planning
19 city_storm_shelter_decision
21 emergency_transportation_decision
24 Critical Data Backup Site Selection
32 emergency_relocation_site
33 emergency_field_hospital_site
36 datacenter_emergency_migration
38 disaster_response_command_center
41 evacuation_destination_decision
45 Safe Lab Choice After Earthquake
46 Storm Shelter Decision
50 secure_meeting_room_decision
51 choosing_the_safe_storage_site
52 mountain_storm_shelter
54 island_research_base_choice
55 secure_archive_location
57 archaeological_dig_site
58 Mountain Weather Station Decision
59 Choosing the Safe Emergency HQ
60 The Elusive Bird Sighting
```

`fact_only_exchange` extra rescues over `no_shared_repeat_exchange`:

```text
3 evacuation_east_town
5 baker_2010
11 emergency_conference_relocation
12 evacuate_park_dilemma
14 lunch_group_decision
15 emergency_response_meeting_location
17 Red River Evacuation
18 Park Evacuation Planning
22 Antarctic Storm Safe Haven
24 Critical Data Backup Site Selection
32 emergency_relocation_site
33 emergency_field_hospital_site
38 disaster_response_command_center
41 evacuation_destination_decision
44 Choosing the Safe Offsite Venue
46 Storm Shelter Decision
47 Find the Missing Prototype
49 choosing_the_safe_field_station
50 secure_meeting_room_decision
51 choosing_the_safe_storage_site
55 secure_archive_location
56 Secure the Masterpiece
58 Mountain Weather Station Decision
59 Choosing the Safe Emergency HQ
```

`fact_only_exchange` extra rescues over `fact_only_with_options_exchange`:

```text
5 baker_2010
50 secure_meeting_room_decision
```

## Interpretation

Local sender bans recover real cases but introduce regressions and leave many clean tasks unsolved. Fact-only keeps all clean tasks correct in this run and has no clean-subset regressions against either local sender ban. The dominant remaining factor is exact private-fact transfer plus suppression of both preference compression and shared-advantage replay.
