#!/usr/bin/env python3
"""Build HSA draft annotations for the P0/P1 HiddenBench seed expansion."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


BENCHMARK_PATH = Path("data/external/hiddenbench/benchmark.json")
EXISTING_FACT_DRAFTS = [
    Path("experiments/20260618-local-state-admission-v2-preflight/hiddenbench_fact_units.draft.json"),
    Path("experiments/20260619-local-hsa-v0-hb12-hb31-draft/hb12_hb31_fact_units.draft.json"),
]
EXISTING_PERT_DRAFTS = [
    Path("experiments/20260618-local-state-admission-v2-preflight/source_scope_perturbations.draft.json"),
    Path("experiments/20260619-local-hsa-v0-hb12-hb31-draft/hb12_hb31_perturbations.draft.json"),
]
KEEP_EXISTING_TASK_IDS = {10, 11, 12, 31}


NEW_SEED_SPECS: dict[int, dict[str, Any]] = {
    3: {
        "roles": ["route_checker", "shelter_checker", "final_decider"],
        "shared_roles": [
            ["shelter_checker", "final_decider"],
            ["shelter_checker", "final_decider"],
            ["shelter_checker", "final_decider"],
            ["route_checker", "final_decider"],
        ],
        "hidden_roles": [
            ["route_checker", "final_decider"],
            ["route_checker", "final_decider"],
            ["route_checker", "final_decider"],
            ["route_checker", "final_decider"],
        ],
        "hidden_treatments": ["admit_blocker", "admit_blocker", "admit_blocker", "admit_blocker"],
        "hidden_kinds": [
            "verified_flood_report",
            "verified_flood_alert",
            "verified_route_notice",
            "verified_route_report",
        ],
        "shared_treatments": [
            "context_not_recommendation",
            "admit_enabler",
            "context_not_recommendation",
            "context_with_caveat",
        ],
        "units": [
            {
                "suffix": "west_city_flood_blocked",
                "unit_type": "option_blocker",
                "target_option": "West City",
                "required": ["H0", "H1"],
                "rationale": "West City depends on a bridge threatened by imminent upstream water release.",
            },
            {
                "suffix": "north_hill_access_blocked",
                "unit_type": "option_blocker",
                "target_option": "North Hill",
                "required": ["H2", "H3"],
                "rationale": "North Hill has both walking trail and driveway access blocked.",
            },
            {
                "suffix": "east_town_shelter_enabled",
                "unit_type": "option_enabler",
                "target_option": "East Town",
                "required": ["S1"],
                "rationale": "East Town has offered accommodations despite a volunteer caveat.",
            },
        ],
        "rejections": [
            {
                "suffix": "reject_west_hotels",
                "facts": ["S0"],
                "reason": "recommendation_leakage_reject",
                "rationale": "West City hotel capacity should not override bridge flood risk.",
            },
            {
                "suffix": "reject_north_school",
                "facts": ["S2"],
                "reason": "recommendation_leakage_reject",
                "rationale": "North Hill supplies should not override blocked access.",
            },
        ],
        "obligations": [
            "must name the West City bridge flood risk",
            "must name both North Hill access blockers",
            "must keep East Town viable from admitted facts",
        ],
        "perturbations": [
            {
                "variant_suffix": "west_dam_unverified",
                "fact": "H1",
                "kind": "unverified_flood_alert",
                "recipients": ["route_checker", "final_decider"],
                "drop": ["west_city_flood_blocked"],
                "reason": "verification_reject",
            },
            {
                "variant_suffix": "north_mudslide_no_final_scope",
                "fact": "H3",
                "kind": "verified_route_report",
                "recipients": ["route_checker"],
                "drop": ["north_hill_access_blocked"],
                "reason": "recipient_scope_reject_for_final_decider",
            },
        ],
    },
    21: {
        "roles": ["access_checker", "readiness_checker", "final_decider"],
        "shared_roles": [
            ["access_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["readiness_checker", "final_decider"],
        ],
        "hidden_roles": [
            ["access_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["readiness_checker", "final_decider"],
        ],
        "hidden_treatments": ["admit_blocker", "admit_blocker", "admit_blocker", "admit_enabler"],
        "hidden_kinds": [
            "verified_route_alert",
            "verified_route_notice",
            "verified_delay_report",
            "verified_readiness_report",
        ],
        "shared_treatments": [
            "context_not_recommendation",
            "context_not_recommendation",
            "stale_or_overridden_context",
        ],
        "units": [
            {
                "suffix": "aurora_access_blocked",
                "unit_type": "option_blocker",
                "target_option": "Aurora Train Station",
                "required": ["H0", "H1"],
                "rationale": "Aurora is unreachable by train and road.",
            },
            {
                "suffix": "borealis_delay_blocked",
                "unit_type": "option_blocker",
                "target_option": "Borealis Bus Terminal",
                "required": ["H2"],
                "rationale": "Borealis cannot arrive in time because the bus route is delayed until the next day.",
            },
            {
                "suffix": "celestia_ready_enabled",
                "unit_type": "option_enabler",
                "target_option": "Celestia Airstrip",
                "required": ["H3"],
                "rationale": "Celestia has emergency upgrades, supplies, and mobile shelter.",
            },
        ],
        "rejections": [
            {
                "suffix": "reject_aurora_safety",
                "facts": ["S0"],
                "reason": "recommendation_leakage_reject",
                "rationale": "Aurora track safety should not override current route closures.",
            }
        ],
        "obligations": [
            "must name Aurora train and road closures",
            "must name Borealis next-day delay",
            "must name Celestia emergency upgrades",
        ],
        "perturbations": [
            {
                "variant_suffix": "borealis_delay_unverified",
                "fact": "H2",
                "kind": "unverified_delay_report",
                "recipients": ["access_checker", "final_decider"],
                "drop": ["borealis_delay_blocked"],
                "reason": "verification_reject",
            },
            {
                "variant_suffix": "celestia_ready_no_final_scope",
                "fact": "H3",
                "kind": "verified_readiness_report",
                "recipients": ["readiness_checker"],
                "drop": ["celestia_ready_enabled"],
                "reason": "recipient_scope_reject_for_final_decider",
            },
        ],
    },
    27: {
        "roles": ["access_checker", "stability_checker", "final_decider"],
        "shared_roles": [
            ["access_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["access_checker", "final_decider"],
        ],
        "hidden_roles": [
            ["access_checker", "final_decider"],
            ["stability_checker", "final_decider"],
            ["stability_checker", "final_decider"],
            ["stability_checker", "final_decider"],
        ],
        "hidden_treatments": ["admit_enabler", "admit_blocker", "admit_blocker", "admit_blocker"],
        "hidden_kinds": [
            "verified_access_report",
            "verified_soil_report",
            "verified_geology_report",
            "verified_community_report",
        ],
        "shared_treatments": [
            "stale_or_overridden_context",
            "context_not_recommendation",
            "context_with_caveat",
        ],
        "units": [
            {
                "suffix": "maple_valley_blocked",
                "unit_type": "option_blocker",
                "target_option": "Maple Valley",
                "required": ["H2", "H3"],
                "rationale": "Maple Valley has both geological and community risk for a long-term station.",
            },
            {
                "suffix": "copper_lake_blocked",
                "unit_type": "option_blocker",
                "target_option": "Copper Lake",
                "required": ["H1"],
                "rationale": "Copper Lake cannot support heavy infrastructure.",
            },
            {
                "suffix": "pine_ridge_access_enabled",
                "unit_type": "option_enabler",
                "target_option": "Pine Ridge",
                "required": ["H0"],
                "rationale": "Pine Ridge has a repaired access road usable by trucks.",
            },
        ],
        "rejections": [
            {
                "suffix": "reject_maple_infrastructure",
                "facts": ["S0"],
                "reason": "recommendation_leakage_reject",
                "rationale": "Maple Valley infrastructure should not override fault-line and protest risks.",
            }
        ],
        "obligations": [
            "must name Maple Valley fault or construction-risk evidence",
            "must name Copper Lake soil blocker",
            "must name Pine Ridge repaired road",
        ],
        "perturbations": [
            {
                "variant_suffix": "copper_soil_unverified",
                "fact": "H1",
                "kind": "unverified_soil_report",
                "recipients": ["stability_checker", "final_decider"],
                "drop": ["copper_lake_blocked"],
                "reason": "verification_reject",
            },
            {
                "variant_suffix": "pine_access_no_final_scope",
                "fact": "H0",
                "kind": "verified_access_report",
                "recipients": ["access_checker"],
                "drop": ["pine_ridge_access_enabled"],
                "reason": "recipient_scope_reject_for_final_decider",
            },
        ],
    },
    44: {
        "roles": ["access_checker", "service_checker", "final_decider"],
        "shared_roles": [
            ["access_checker", "final_decider"],
            ["service_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["service_checker", "final_decider"],
        ],
        "hidden_roles": [
            ["service_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["access_checker", "final_decider"],
        ],
        "hidden_treatments": ["admit_blocker", "admit_blocker", "admit_blocker", "admit_enabler"],
        "hidden_kinds": [
            "verified_power_report",
            "verified_bridge_report",
            "verified_transit_alert",
            "verified_access_report",
        ],
        "shared_treatments": [
            "stale_or_overridden_context",
            "context_not_recommendation",
            "context_with_caveat",
            "context_not_recommendation",
        ],
        "units": [
            {
                "suffix": "downtown_hotel_blocked",
                "unit_type": "option_blocker",
                "target_option": "Downtown Hotel",
                "required": ["H0", "H2"],
                "rationale": "Downtown Hotel has both power and transit access risks.",
            },
            {
                "suffix": "riverside_bridge_blocked",
                "unit_type": "option_blocker",
                "target_option": "Riverside Conference Center",
                "required": ["H1"],
                "rationale": "Riverside Conference Center's main bridge is closed.",
            },
            {
                "suffix": "hilltop_access_enabled",
                "unit_type": "option_enabler",
                "target_option": "Hilltop Retreat",
                "required": ["H3"],
                "rationale": "Hilltop remains reachable because the main highway is still passable.",
            },
        ],
        "rejections": [
            {
                "suffix": "reject_riverside_backup_power",
                "facts": ["S1"],
                "reason": "recommendation_leakage_reject",
                "rationale": "Riverside backup power should not override bridge closure.",
            }
        ],
        "obligations": [
            "must name Downtown power or subway blocker",
            "must name Riverside bridge closure",
            "must name Hilltop remaining passable highway",
        ],
        "perturbations": [
            {
                "variant_suffix": "riverside_bridge_unverified",
                "fact": "H1",
                "kind": "unverified_bridge_report",
                "recipients": ["access_checker", "final_decider"],
                "drop": ["riverside_bridge_blocked"],
                "reason": "verification_reject",
            },
            {
                "variant_suffix": "hilltop_access_no_final_scope",
                "fact": "H3",
                "kind": "verified_access_report",
                "recipients": ["access_checker"],
                "drop": ["hilltop_access_enabled"],
                "reason": "recipient_scope_reject_for_final_decider",
            },
        ],
    },
    51: {
        "roles": ["supply_quality_checker", "access_checker", "final_decider"],
        "shared_roles": [
            ["supply_quality_checker", "final_decider"],
            ["supply_quality_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["supply_quality_checker", "final_decider"],
        ],
        "hidden_roles": [
            ["supply_quality_checker", "final_decider"],
            ["supply_quality_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["supply_quality_checker", "final_decider"],
        ],
        "hidden_treatments": ["admit_blocker", "admit_blocker", "admit_enabler", "admit_blocker"],
        "hidden_kinds": [
            "verified_inventory_report",
            "verified_temperature_report",
            "verified_access_report",
            "verified_generator_report",
        ],
        "shared_treatments": [
            "stale_or_overridden_context",
            "context_not_recommendation",
            "context_with_access_gap",
            "context_with_caveat",
        ],
        "units": [
            {
                "suffix": "alpha_storage_blocked",
                "unit_type": "option_blocker",
                "target_option": "Alpha Storage",
                "required": ["H1", "H3"],
                "rationale": "Alpha has spoiled perishables and failed refrigeration backup.",
            },
            {
                "suffix": "bravo_storage_not_needed_blocked",
                "unit_type": "option_blocker",
                "target_option": "Bravo Storage",
                "required": ["H0"],
                "rationale": "Bravo lacks urgent hospital and shelter supplies.",
            },
            {
                "suffix": "charlie_access_enabled",
                "unit_type": "option_enabler",
                "target_option": "Charlie Storage",
                "required": ["H2"],
                "rationale": "Charlie access delay has been cleared.",
            },
        ],
        "rejections": [
            {
                "suffix": "reject_alpha_closest",
                "facts": ["S0"],
                "reason": "recommendation_leakage_reject",
                "rationale": "Alpha proximity should not override spoilage and generator failure.",
            }
        ],
        "obligations": [
            "must name Alpha spoilage and generator failure",
            "must name Bravo inventory mismatch",
            "must name Charlie access clearance",
        ],
        "perturbations": [
            {
                "variant_suffix": "alpha_generator_unverified",
                "fact": "H3",
                "kind": "unverified_generator_report",
                "recipients": ["supply_quality_checker", "final_decider"],
                "drop": ["alpha_storage_blocked"],
                "reason": "verification_reject",
            },
            {
                "variant_suffix": "charlie_access_no_final_scope",
                "fact": "H2",
                "kind": "verified_access_report",
                "recipients": ["access_checker"],
                "drop": ["charlie_access_enabled"],
                "reason": "recipient_scope_reject_for_final_decider",
            },
        ],
    },
    54: {
        "roles": ["site_safety_checker", "communications_checker", "final_decider"],
        "shared_roles": [
            ["site_safety_checker", "final_decider"],
            ["site_safety_checker", "final_decider"],
            ["communications_checker", "final_decider"],
            ["site_safety_checker", "final_decider"],
        ],
        "hidden_roles": [
            ["site_safety_checker", "final_decider"],
            ["communications_checker", "final_decider"],
            ["site_safety_checker", "final_decider"],
            ["site_safety_checker", "final_decider"],
        ],
        "hidden_treatments": ["admit_blocker", "admit_enabler", "admit_blocker", "admit_blocker"],
        "hidden_kinds": [
            "verified_flood_report",
            "verified_comms_report",
            "verified_gas_report",
            "verified_ground_report",
        ],
        "shared_treatments": [
            "stale_or_overridden_context",
            "context_not_recommendation",
            "context_with_caveat",
            "context_not_recommendation",
        ],
        "units": [
            {
                "suffix": "site_a_hazard_blocked",
                "unit_type": "option_blocker",
                "target_option": "Site A",
                "required": ["H2", "H3"],
                "rationale": "Site A has gas and ground instability hazards.",
            },
            {
                "suffix": "site_b_flood_blocked",
                "unit_type": "option_blocker",
                "target_option": "Site B",
                "required": ["H0"],
                "rationale": "Site B has flooding, contamination, and equipment access risk.",
            },
            {
                "suffix": "site_c_comms_enabled",
                "unit_type": "option_enabler",
                "target_option": "Site C",
                "required": ["H1"],
                "rationale": "Site C communications can be restored with portable equipment.",
            },
        ],
        "rejections": [
            {
                "suffix": "reject_site_a_harbor",
                "facts": ["S0"],
                "reason": "recommendation_leakage_reject",
                "rationale": "Site A harbor access should not override gas and sinkhole risk.",
            }
        ],
        "obligations": [
            "must name Site A gas or ground hazard",
            "must name Site B flooding and contamination",
            "must name Site C communications workaround",
        ],
        "perturbations": [
            {
                "variant_suffix": "site_b_flood_unverified",
                "fact": "H0",
                "kind": "unverified_flood_report",
                "recipients": ["site_safety_checker", "final_decider"],
                "drop": ["site_b_flood_blocked"],
                "reason": "verification_reject",
            },
            {
                "variant_suffix": "site_c_comms_no_final_scope",
                "fact": "H1",
                "kind": "verified_comms_report",
                "recipients": ["communications_checker"],
                "drop": ["site_c_comms_enabled"],
                "reason": "recipient_scope_reject_for_final_decider",
            },
        ],
    },
    56: {
        "roles": ["environment_checker", "access_checker", "final_decider"],
        "shared_roles": [
            ["environment_checker", "final_decider"],
            ["environment_checker", "final_decider"],
            ["environment_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["environment_checker", "final_decider"],
        ],
        "hidden_roles": [
            ["environment_checker", "final_decider"],
            ["access_checker", "final_decider"],
            ["environment_checker", "final_decider"],
            ["environment_checker", "final_decider"],
        ],
        "hidden_treatments": ["admit_blocker", "admit_enabler", "admit_blocker", "admit_blocker"],
        "hidden_kinds": [
            "verified_power_report",
            "verified_access_report",
            "verified_wind_report",
            "verified_evacuation_alert",
        ],
        "shared_treatments": [
            "context_with_hazard",
            "stale_or_overridden_context",
            "context_not_recommendation",
            "context_with_access_gap",
            "context_with_requirement",
        ],
        "units": [
            {
                "suffix": "art_museum_chemical_blocked",
                "unit_type": "option_blocker",
                "target_option": "The City Art Museum's Disaster-Proof Storage",
                "required": ["H2"],
                "rationale": "The chemical leak will move directly toward the art museum block.",
            },
            {
                "suffix": "science_lab_environment_blocked",
                "unit_type": "option_blocker",
                "target_option": "The University Science Building's Secure Lab",
                "required": ["H0", "H3"],
                "rationale": "The science building lacks HVAC backup and is being evacuated.",
            },
            {
                "suffix": "records_vault_access_enabled",
                "unit_type": "option_enabler",
                "target_option": "The Government Records Vault",
                "required": ["H1"],
                "rationale": "The records vault access issue is a bounded delay rather than a safety blocker.",
            },
        ],
        "rejections": [
            {
                "suffix": "reject_art_museum_disaster_proof",
                "facts": ["S1"],
                "reason": "recommendation_leakage_reject",
                "rationale": "General disaster-proof storage should not override direct chemical-leak exposure.",
            }
        ],
        "obligations": [
            "must name chemical leak risk to the art museum",
            "must name science building HVAC or evacuation blocker",
            "must keep the records vault viable despite bounded access delay",
        ],
        "perturbations": [
            {
                "variant_suffix": "art_museum_wind_unverified",
                "fact": "H2",
                "kind": "unverified_wind_report",
                "recipients": ["environment_checker", "final_decider"],
                "drop": ["art_museum_chemical_blocked"],
                "reason": "verification_reject",
            },
            {
                "variant_suffix": "science_generator_no_final_scope",
                "fact": "H0",
                "kind": "verified_power_report",
                "recipients": ["environment_checker"],
                "drop": ["science_lab_environment_blocked"],
                "reason": "recipient_scope_reject_for_final_decider",
            },
        ],
    },
}


TASK5_PROFILE_ROLES = ["academic_fit_checker", "governance_checker", "advancement_checker", "final_decider"]

TASK5_PROFILE_SOURCE_FACTS: list[dict[str, Any]] = [
    {
        "fact_id": "hb05_shared_0",
        "channel": "shared",
        "text": "Stevens' CV highlights: currently provost and executive vice president; previous business dean and IT chair roles; associated with business-school building plans and a Florida business-college gift; full professor of Information Technology.",
        "candidate_recipients": ["academic_fit_checker", "advancement_checker", "final_decider"],
        "expected_treatment": "shared_profile_context",
        "pressure": "shared Stevens credentials can tempt a profile-only recommendation",
    },
    {
        "fact_id": "hb05_shared_1",
        "channel": "shared",
        "text": "Roberts' CV highlights: recently completed a term as U.S. Senator for Georgia; raised significant campaign funds; previously Dean of Arts and Sciences in Virginia and later dean of a large private university in Georgia; full professor of public administration before becoming senator.",
        "candidate_recipients": ["academic_fit_checker", "advancement_checker", "final_decider"],
        "expected_treatment": "shared_profile_context",
        "pressure": "shared Roberts credentials are relevant but not sufficient alone",
    },
    {
        "fact_id": "hb05_shared_2",
        "channel": "shared",
        "text": "Jones' CV highlights: senior managing partner in a large Atlanta law firm; five years on Higher Education University's Board of Trustees; steering committee for the current $150 million capital campaign; employment-law expertise and Supreme Court experience; visiting professor of law.",
        "candidate_recipients": ["governance_checker", "advancement_checker", "final_decider"],
        "expected_treatment": "context_not_recommendation",
        "pressure": "Jones' local board and campaign credentials can dominate the shared-only prior",
    },
    {
        "fact_id": "hb05_shared_3",
        "channel": "shared",
        "text": "Stevens' shared information: nationally recognized for information-technology research and expertise; emphasized collaboration in interview; demonstrated excellent oratory skills; someone else was primarily responsible for the $15 million in Florida.",
        "candidate_recipients": ["academic_fit_checker", "advancement_checker", "final_decider"],
        "expected_treatment": "shared_profile_context",
        "pressure": "Stevens has visible academic strengths but also a fundraising caveat",
    },
    {
        "fact_id": "hb05_shared_4",
        "channel": "shared",
        "text": "Roberts' shared information: faculty feedback said Roberts seemed aloof in the presentation; has not worked in higher education for six years; owns a condo in Pensacola; has little direct campus-student-life experience; was accused as senator of changing positions for political gain.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "shared_profile_context",
        "pressure": "shared Roberts negatives make the hidden positive profile necessary",
    },
    {
        "fact_id": "hb05_shared_5",
        "channel": "shared",
        "text": "Jones' shared information: pleasant in social settings; law partners call Jones strategic about firm direction; litigation success rate fell after the Supreme Court appearance; active trustee; well-liked as a teacher by student enrollment and evaluations.",
        "candidate_recipients": ["governance_checker", "academic_fit_checker", "final_decider"],
        "expected_treatment": "context_not_recommendation",
        "pressure": "shared Jones positives can preserve the wrong prior",
    },
    {
        "fact_id": "hb05_hidden_stevens_no_fundraising",
        "channel": "hidden",
        "text": "Stevens left the Mississippi dean position before raising any funds for the building campaign.",
        "candidate_recipients": ["advancement_checker", "final_decider"],
        "expected_treatment": "admit_blocker",
        "pressure": "hidden profile evidence weakens Stevens on fundraising execution",
    },
    {
        "fact_id": "hb05_hidden_stevens_teaches_one_class",
        "channel": "hidden",
        "text": "As provost, Stevens teaches one class per year.",
        "candidate_recipients": ["academic_fit_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "contextual teaching fact",
    },
    {
        "fact_id": "hb05_hidden_stevens_spouse_spanish",
        "channel": "hidden",
        "text": "Stevens' spouse has a PhD in Spanish and teaches a class or two at college level.",
        "candidate_recipients": ["academic_fit_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_stevens_discourages_innovation",
        "channel": "hidden",
        "text": "Faculty in Florida and Mississippi say Stevens tends to discourage new, innovative ideas.",
        "candidate_recipients": ["academic_fit_checker", "governance_checker", "final_decider"],
        "expected_treatment": "admit_blocker",
        "pressure": "hidden profile evidence blocks Stevens on innovation and shared governance",
    },
    {
        "fact_id": "hb05_hidden_stevens_family_atlanta",
        "channel": "hidden",
        "text": "Stevens has family in Atlanta.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "local-tie distractor",
    },
    {
        "fact_id": "hb05_hidden_stevens_married_children",
        "channel": "hidden",
        "text": "Stevens is married with three children.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_stevens_sports",
        "channel": "hidden",
        "text": "Stevens enjoys sports and goes to football and basketball games.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_stevens_fitness",
        "channel": "hidden",
        "text": "Stevens stays fit by biking and running.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_stevens_public_drinking",
        "channel": "hidden",
        "text": "Stevens has been observed drinking heavily in public, including at university events.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "admit_blocker",
        "pressure": "hidden profile evidence weakens Stevens on presidential conduct",
    },
    {
        "fact_id": "hb05_hidden_stevens_consulting",
        "channel": "hidden",
        "text": "Stevens does consulting work in IT.",
        "candidate_recipients": ["academic_fit_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "private profile context",
    },
    {
        "fact_id": "hb05_hidden_stevens_garden",
        "channel": "hidden",
        "text": "Stevens likes to garden.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_roberts_contacts",
        "channel": "hidden",
        "text": "Roberts has made numerous influential contacts as senator.",
        "candidate_recipients": ["advancement_checker", "final_decider"],
        "expected_treatment": "admit_enabler",
        "pressure": "hidden profile evidence supports external constituency and fundraising capacity",
    },
    {
        "fact_id": "hb05_hidden_roberts_nonprofits",
        "channel": "hidden",
        "text": "Roberts frequently volunteers for respected nonprofits, including affordable housing and human-rights organizations.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "service and community profile support",
    },
    {
        "fact_id": "hb05_hidden_roberts_vegetarian",
        "channel": "hidden",
        "text": "Roberts is a vegetarian.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_roberts_thoughtful_listener",
        "channel": "hidden",
        "text": "Previous faculty members describe Roberts as a thoughtful leader and good listener.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "admit_enabler",
        "pressure": "hidden profile evidence supports shared governance",
    },
    {
        "fact_id": "hb05_hidden_roberts_collaborative",
        "channel": "hidden",
        "text": "Previous colleagues say Roberts uses a collaborative decision-making style.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "admit_enabler",
        "pressure": "hidden profile evidence supports shared governance",
    },
    {
        "fact_id": "hb05_hidden_roberts_golf_tennis",
        "channel": "hidden",
        "text": "Roberts enjoys golf and tennis.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_roberts_excellent_teacher",
        "channel": "hidden",
        "text": "Previous students and faculty say Roberts is an excellent teacher.",
        "candidate_recipients": ["academic_fit_checker", "final_decider"],
        "expected_treatment": "admit_enabler",
        "pressure": "hidden profile evidence supports academic leadership",
    },
    {
        "fact_id": "hb05_hidden_roberts_family",
        "channel": "hidden",
        "text": "Roberts is divorced and remarried and has two children.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_roberts_research_productivity",
        "channel": "hidden",
        "text": "Faculty research productivity increased while Roberts served as dean in Georgia.",
        "candidate_recipients": ["academic_fit_checker", "final_decider"],
        "expected_treatment": "admit_enabler",
        "pressure": "hidden profile evidence supports academic administration",
    },
    {
        "fact_id": "hb05_hidden_roberts_diversity",
        "channel": "hidden",
        "text": "Roberts increased the diversity of the faculty while dean in Georgia.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "admit_enabler",
        "pressure": "hidden profile evidence supports stated diversity criterion",
    },
    {
        "fact_id": "hb05_hidden_roberts_federal_grant",
        "channel": "hidden",
        "text": "Roberts was instrumental in securing a multimillion-dollar federal grant for a Georgia-based nonprofit institution.",
        "candidate_recipients": ["advancement_checker", "final_decider"],
        "expected_treatment": "admit_enabler",
        "pressure": "hidden profile evidence supports fundraising and outside constituency capacity",
    },
    {
        "fact_id": "hb05_hidden_jones_lives_area",
        "channel": "hidden",
        "text": "Jones already lives in the area.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "local-tie distractor",
    },
    {
        "fact_id": "hb05_hidden_jones_married_child",
        "channel": "hidden",
        "text": "Jones is married with a grown child.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_jones_abrasive_turnover",
        "channel": "hidden",
        "text": "Sources at Jones' law firm attribute high turnover at the firm to Jones' somewhat abrasive leadership style.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "admit_blocker",
        "pressure": "hidden profile evidence blocks Jones on leadership climate",
    },
    {
        "fact_id": "hb05_hidden_jones_pets",
        "channel": "hidden",
        "text": "Jones has two dogs and two cats.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_jones_spouse_physician",
        "channel": "hidden",
        "text": "Jones' spouse is a physician specializing in internal medicine.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_jones_bridge",
        "channel": "hidden",
        "text": "Jones plays bridge as a hobby.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_jones_overseas_travel",
        "channel": "hidden",
        "text": "Jones enjoys traveling overseas on vacation.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_jones_provost_tension",
        "channel": "hidden",
        "text": "Feedback from other trustees indicates tension between the current provost and Jones.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "admit_blocker",
        "pressure": "hidden profile evidence blocks Jones on campus governance",
    },
    {
        "fact_id": "hb05_hidden_jones_strategic",
        "channel": "hidden",
        "text": "Law partners say Jones is a strategic thinker with respect to the direction of the firm.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "positive Jones distractor",
    },
    {
        "fact_id": "hb05_hidden_jones_reads",
        "channel": "hidden",
        "text": "Jones reads mystery novels and biographies.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
    {
        "fact_id": "hb05_hidden_jones_cooking",
        "channel": "hidden",
        "text": "Jones loves to cook.",
        "candidate_recipients": ["governance_checker", "final_decider"],
        "expected_treatment": "profile_context",
        "pressure": "irrelevant private profile detail",
    },
]

TASK5_PROFILE_UNITS: list[dict[str, Any]] = [
    {
        "unit_id": "hb05_unit_stevens_profile_blocked",
        "unit_type": "option_blocker",
        "target_option": "Stevens",
        "required_fact_ids": [
            "hb05_hidden_stevens_no_fundraising",
            "hb05_hidden_stevens_discourages_innovation",
            "hb05_hidden_stevens_public_drinking",
        ],
        "supporting_fact_ids": [],
        "admit_to": ["academic_fit_checker", "advancement_checker", "governance_checker", "final_decider"],
        "rationale": "Stevens has hidden fundraising, innovation, and conduct concerns that undercut the shared credentials.",
    },
    {
        "unit_id": "hb05_unit_jones_governance_blocked",
        "unit_type": "option_blocker",
        "target_option": "Jones",
        "required_fact_ids": [
            "hb05_hidden_jones_abrasive_turnover",
            "hb05_hidden_jones_provost_tension",
        ],
        "supporting_fact_ids": [],
        "admit_to": ["governance_checker", "final_decider"],
        "rationale": "Jones has hidden leadership-climate and provost-tension concerns despite strong shared local credentials.",
    },
    {
        "unit_id": "hb05_unit_roberts_academic_governance_enabled",
        "unit_type": "option_enabler",
        "target_option": "Roberts",
        "required_fact_ids": [
            "hb05_hidden_roberts_collaborative",
            "hb05_hidden_roberts_excellent_teacher",
            "hb05_hidden_roberts_research_productivity",
        ],
        "supporting_fact_ids": [],
        "admit_to": ["academic_fit_checker", "governance_checker", "final_decider"],
        "rationale": "Roberts has hidden evidence for collaborative governance, teaching, and academic productivity.",
    },
    {
        "unit_id": "hb05_unit_roberts_advancement_diversity_enabled",
        "unit_type": "option_enabler",
        "target_option": "Roberts",
        "required_fact_ids": [
            "hb05_hidden_roberts_contacts",
            "hb05_hidden_roberts_diversity",
            "hb05_hidden_roberts_federal_grant",
        ],
        "supporting_fact_ids": [],
        "admit_to": ["advancement_checker", "governance_checker", "final_decider"],
        "rationale": "Roberts has hidden evidence for external contacts, diversity work, and grant acquisition.",
    },
]

TASK5_PROFILE_REJECTIONS: list[dict[str, Any]] = [
    {
        "rejection_id": "hb05_reject_jones_board_campaign",
        "source_fact_ids": ["hb05_shared_2", "hb05_shared_5"],
        "reason": "recommendation_leakage_reject",
        "rationale": "Jones' board and campaign roles should not override hidden governance blockers.",
    },
    {
        "rejection_id": "hb05_reject_stevens_it_reputation",
        "source_fact_ids": ["hb05_shared_0", "hb05_shared_3"],
        "reason": "recommendation_leakage_reject",
        "rationale": "Stevens' IT reputation should not override hidden fundraising, innovation, and conduct blockers.",
    },
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, blob: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sketch_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return f"hiddenbench_{slug}"


def fact_id(task_id: int, ref: str) -> str:
    prefix = f"hb{task_id:02d}"
    kind = "shared" if ref.startswith("S") else "hidden"
    index = int(ref[1:])
    return f"{prefix}_{kind}_{index}"


def unit_id(task_id: int, suffix: str) -> str:
    return f"hb{task_id:02d}_unit_{suffix}"


def rejection_id(task_id: int, suffix: str) -> str:
    return f"hb{task_id:02d}_{suffix}"


def load_benchmark(path: Path) -> dict[int, dict[str, Any]]:
    obj = read_json(path)
    rows = obj if isinstance(obj, list) else obj.get("data", obj.get("examples", []))
    return {int(row["id"]): row for row in rows}


def load_existing_fact_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in EXISTING_FACT_DRAFTS:
        for row in read_json(path):
            task_id = int(row["source_ref"]["task_id"])
            if task_id in KEEP_EXISTING_TASK_IDS:
                rows.append(row)
    return sorted(rows, key=lambda row: int(row["source_ref"]["task_id"]))


def load_existing_pert_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in EXISTING_PERT_DRAFTS:
        for row in read_json(path):
            sketch_id = row["sketch_id"]
            if any(existing["sketch_id"] == sketch_id for existing in load_existing_fact_rows()):
                rows.append(row)
    return sorted(rows, key=lambda row: int(row["base_variant"]["variant_id"][2:4]))


def build_source_facts(task_id: int, row: dict[str, Any], spec: dict[str, Any]) -> list[dict[str, Any]]:
    source_facts: list[dict[str, Any]] = []
    for index, text in enumerate(row["shared_information"]):
        source_facts.append(
            {
                "fact_id": f"hb{task_id:02d}_shared_{index}",
                "channel": "shared",
                "text": text,
                "candidate_recipients": spec["shared_roles"][index],
                "expected_treatment": spec["shared_treatments"][index],
                "pressure": "shared context that can tempt an unsupported option",
            }
        )
    for index, text in enumerate(row["hidden_information"]):
        source_facts.append(
            {
                "fact_id": f"hb{task_id:02d}_hidden_{index}",
                "channel": "hidden",
                "text": text,
                "candidate_recipients": spec["hidden_roles"][index],
                "expected_treatment": spec["hidden_treatments"][index],
                "pressure": "role-scoped evidence required for final admission",
            }
        )
    return source_facts


def build_units(task_id: int, spec: dict[str, Any]) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for unit in spec["units"]:
        units.append(
            {
                "unit_id": unit_id(task_id, unit["suffix"]),
                "unit_type": unit["unit_type"],
                "target_option": unit["target_option"],
                "required_fact_ids": [fact_id(task_id, ref) for ref in unit.get("required", [])],
                "supporting_fact_ids": [fact_id(task_id, ref) for ref in unit.get("supporting", [])],
                "admit_to": sorted({role for ref in unit.get("required", []) + unit.get("supporting", []) for role in spec["hidden_roles"][int(ref[1:])] if ref.startswith("H")} | {"final_decider"}),
                "rationale": unit["rationale"],
            }
        )
    return units


def build_rejections(task_id: int, spec: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rejection in spec.get("rejections", []):
        out.append(
            {
                "rejection_id": rejection_id(task_id, rejection["suffix"]),
                "source_fact_ids": [fact_id(task_id, ref) for ref in rejection["facts"]],
                "reason": rejection["reason"],
                "rationale": rejection["rationale"],
            }
        )
    return out


def build_fact_row(task_id: int, row: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "sketch_id": sketch_name(row["name"]),
        "draft_status": "local_extraction_draft_not_packet",
        "source_ref": {
            "source_family": "hiddenbench",
            "source_path": str(BENCHMARK_PATH),
            "task_id": task_id,
            "name": row["name"],
        },
        "prompt_visibility_policy": {
            "allowed": ["task_description", "possible_answers", "source_facts", "source_scope", "role_names"],
            "forbidden": ["correct_answer", "oracle_admission_units", "oracle_rejections", "downstream_scoring_obligations", "verdict"],
        },
        "evaluator_metadata": {
            "possible_answers": row["possible_answers"],
            "correct_answer": row["correct_answer"],
            "metadata_visibility": "evaluator_only_never_prompt",
        },
        "roles": spec["roles"],
        "source_facts": build_source_facts(task_id, row, spec),
        "oracle_admission_units": build_units(task_id, spec),
        "oracle_rejections": build_rejections(task_id, spec),
        "downstream_scoring_obligations": spec["obligations"],
        "draft_caveat": "P0/P1 seed expansion draft; requires transparent controls before model execution.",
    }


def base_state(task_id: int, spec: dict[str, Any]) -> dict[str, str]:
    state: dict[str, str] = {}
    for index, roles in enumerate(spec["hidden_roles"]):
        state[f"hb{task_id:02d}_hidden_{index}"] = f"{spec['hidden_kinds'][index]}:{','.join(roles)}"
    return state


def build_pert_row(task_id: int, row: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    base_variant_id = f"hb{task_id:02d}_base_verified_role_scoped"
    variants: list[dict[str, Any]] = []
    for perturb in spec["perturbations"]:
        fid = fact_id(task_id, perturb["fact"])
        variants.append(
            {
                "variant_id": f"hb{task_id:02d}_{perturb['variant_suffix']}",
                "same_text_fact_ids": [fid],
                "changed_only": "verification_state" if "unverified" in perturb["kind"] else "recipient_scope",
                "source_scope_state_overrides": {
                    fid: f"{perturb['kind']}:{','.join(perturb['recipients'])}"
                },
                "expected_admission_delta": {
                    "drop_units": [unit_id(task_id, suffix) for suffix in perturb["drop"]],
                    "add_rejections": [
                        {
                            "source_fact_ids": [fid],
                            "reason": perturb["reason"],
                            "rationale": "This fact should not support final_decider admission under the perturbed source state.",
                        }
                    ],
                },
                "expected_downstream_delta": "The row should become insufficient_admissible_evidence because final_decider lacks a required verified admission unit.",
                "baseline_pressure": "A semantic candidate packer may still use the text if it ignores verification or recipient scope.",
            }
        )
    return {
        "sketch_id": sketch_name(row["name"]),
        "draft_status": "local_perturbation_draft_not_packet",
        "source_fact_draft": "p0p1_fact_units.draft.json",
        "perturbation_goal": "Check whether each seed obeys verification and final_decider recipient scope.",
        "base_variant": {
            "variant_id": base_variant_id,
            "content_policy": "same_source_facts_as_fact_unit_draft",
            "source_scope_state": base_state(task_id, spec),
            "expected_admission_units": [unit_id(task_id, unit["suffix"]) for unit in spec["units"]],
            "expected_downstream_state": "decidable_from_admitted_facts",
        },
        "perturbation_variants": variants,
        "packet_gate_note": "Do not score this seed only by final option; perturbations must change admitted evidence obligations.",
    }


def task5_base_state() -> dict[str, str]:
    state: dict[str, str] = {}
    for fact in TASK5_PROFILE_SOURCE_FACTS:
        if fact["channel"] != "hidden":
            continue
        source_kind = "verified_profile_report"
        if "roberts" in fact["fact_id"]:
            source_kind = "verified_reference_profile"
        elif "stevens" in fact["fact_id"]:
            source_kind = "verified_reference_profile"
        elif "jones" in fact["fact_id"]:
            source_kind = "verified_workplace_profile"
        state[fact["fact_id"]] = f"{source_kind}:{','.join(fact['candidate_recipients'])}"
    return state


def build_task5_fact_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "sketch_id": sketch_name(row["name"]),
        "draft_status": "local_profile_extraction_draft_not_packet",
        "source_ref": {
            "source_family": "hiddenbench",
            "source_path": str(BENCHMARK_PATH),
            "task_id": 5,
            "name": row["name"],
        },
        "prompt_visibility_policy": {
            "allowed": ["task_description", "possible_answers", "source_facts", "source_scope", "role_names"],
            "forbidden": ["correct_answer", "oracle_admission_units", "oracle_rejections", "downstream_scoring_obligations", "verdict"],
        },
        "evaluator_metadata": {
            "possible_answers": row["possible_answers"],
            "correct_answer": row["correct_answer"],
            "metadata_visibility": "evaluator_only_never_prompt",
        },
        "roles": TASK5_PROFILE_ROLES,
        "source_facts": TASK5_PROFILE_SOURCE_FACTS,
        "oracle_admission_units": TASK5_PROFILE_UNITS,
        "oracle_rejections": TASK5_PROFILE_REJECTIONS,
        "downstream_scoring_obligations": [
            "must name Stevens hidden fundraising, innovation, or conduct blockers",
            "must name Jones hidden governance blockers",
            "must name Roberts collaborative academic-governance support",
            "must name Roberts diversity or advancement support",
            "must not treat Jones board or campaign credentials as sufficient",
        ],
        "draft_caveat": "P2 profile-level seed; hidden profile paragraphs are split into candidate-level cards before packetization.",
    }


def build_task5_pert_row(row: dict[str, Any]) -> dict[str, Any]:
    sketch_id = sketch_name(row["name"])
    base_variant_id = "hb05_base_verified_profile_scoped"
    return {
        "sketch_id": sketch_id,
        "draft_status": "local_profile_perturbation_draft_not_packet",
        "source_fact_draft": "p0p1p2_fact_units.draft.json",
        "perturbation_goal": "Check whether profile-level evidence obeys verification and final_decider recipient scope.",
        "base_variant": {
            "variant_id": base_variant_id,
            "content_policy": "profile paragraphs split into candidate-level source cards",
            "source_scope_state": task5_base_state(),
            "expected_admission_units": [unit["unit_id"] for unit in TASK5_PROFILE_UNITS],
            "expected_downstream_state": "decidable_from_admitted_facts",
        },
        "perturbation_variants": [
            {
                "variant_id": "hb05_roberts_grant_unverified",
                "same_text_fact_ids": ["hb05_hidden_roberts_federal_grant"],
                "changed_only": "verification_state",
                "source_scope_state_overrides": {
                    "hb05_hidden_roberts_federal_grant": "unverified_grant_claim:advancement_checker,final_decider",
                },
                "expected_admission_delta": {
                    "drop_units": ["hb05_unit_roberts_advancement_diversity_enabled"],
                    "add_rejections": [
                        {
                            "source_fact_ids": ["hb05_hidden_roberts_federal_grant"],
                            "reason": "verification_reject",
                            "rationale": "The same grant text should not support final_decider admission while unverified.",
                        }
                    ],
                },
                "expected_downstream_delta": "The row should become insufficient_admissible_evidence because final_decider lacks a required verified Roberts advancement unit.",
                "baseline_pressure": "A profile summarizer may still use the grant text if it ignores verification state.",
            },
            {
                "variant_id": "hb05_jones_tension_no_final_scope",
                "same_text_fact_ids": ["hb05_hidden_jones_provost_tension"],
                "changed_only": "recipient_scope",
                "source_scope_state_overrides": {
                    "hb05_hidden_jones_provost_tension": "verified_workplace_profile:governance_checker",
                },
                "expected_admission_delta": {
                    "drop_units": ["hb05_unit_jones_governance_blocked"],
                    "add_rejections": [
                        {
                            "source_fact_ids": ["hb05_hidden_jones_provost_tension"],
                            "reason": "recipient_scope_reject_for_final_decider",
                            "rationale": "This Jones governance blocker should not support final_decider admission without final_decider scope.",
                        }
                    ],
                },
                "expected_downstream_delta": "The row should become insufficient_admissible_evidence because final_decider lacks a required verified Jones governance blocker.",
                "baseline_pressure": "A profile summarizer may still use the tension text if it ignores recipient scope.",
            },
        ],
        "packet_gate_note": "Do not score this profile seed only by Roberts selection; perturbations must change admitted profile evidence obligations.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=Path("experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft"))
    parser.add_argument("--include-p2-profile", action="store_true", help="include the bulky HB05 profile seed and emit a 36-row package")
    args = parser.parse_args()

    benchmark = load_benchmark(BENCHMARK_PATH)
    fact_rows = load_existing_fact_rows()
    pert_rows = load_existing_pert_rows()
    for task_id in sorted(NEW_SEED_SPECS):
        spec = NEW_SEED_SPECS[task_id]
        source = benchmark[task_id]
        fact_rows.append(build_fact_row(task_id, source, spec))
        pert_rows.append(build_pert_row(task_id, source, spec))
    if args.include_p2_profile:
        source = benchmark[5]
        fact_rows.append(build_task5_fact_row(source))
        pert_rows.append(build_task5_pert_row(source))

    fact_rows = sorted(fact_rows, key=lambda row: int(row["source_ref"]["task_id"]))
    pert_rows = sorted(pert_rows, key=lambda row: int(row["base_variant"]["variant_id"][2:4]))

    args.out_dir.mkdir(parents=True, exist_ok=True)
    prefix = "p0p1p2" if args.include_p2_profile else "p0p1"
    fact_path = args.out_dir / f"{prefix}_fact_units.draft.json"
    pert_path = args.out_dir / f"{prefix}_perturbations.draft.json"
    write_json(fact_path, fact_rows)
    write_json(pert_path, pert_rows)
    summary = {
        "fact_rows": len(fact_rows),
        "perturbation_rows": len(pert_rows),
        "task_ids": [int(row["source_ref"]["task_id"]) for row in fact_rows],
        "included_p2_profile_task_ids": [5] if args.include_p2_profile else [],
        "excluded_recommended_task_ids": [] if args.include_p2_profile else [5],
        "exclusion_reason": None if args.include_p2_profile else "task 5 is a bulky profile-comparison seed and needs a separate annotation pass",
        "fact_path": str(fact_path),
        "perturbation_path": str(pert_path),
    }
    write_json(args.out_dir / "draft_summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
