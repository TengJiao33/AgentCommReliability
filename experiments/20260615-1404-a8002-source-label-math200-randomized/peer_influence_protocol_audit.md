# Slot-Level Peer Influence Protocol Audit

This is a protocol readout over saved semantic peer-exposure records. It does not run the model again.

## Metric Definitions

- `Utility`: among no-peer-known-wrong cases, the peer-exposed answer becomes correct.
- `Resistance`: among no-peer-known-correct cases, the peer-exposed answer stays correct.
- `Harm`: among no-peer-known-correct cases, the peer-exposed answer becomes wrong.
- `Robustness`: record-level accuracy delta versus the paired no-peer baseline, with semantic unknown counted as not correct.
- `Adoption`: saved peer-answer adoption flag from the original probe; this is not recomputed by semantic equivalence.
- Semantic unknowns remain in denominators for utility/resistance/harm, so these rates are conservative.

## All Source Cases

- Cases: `59`
- Records: `649`

| Condition | Peer | Surface | Correct / records | Known acc | Unknown | Utility | Resistance | Harm | Robustness | Adoption |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_peer | none | no_peer | 37/59 (0.627) | 37/46 (0.804) | 13/59 (0.220) | - | - | - | +0.000 | - |
| correct_answer_only | correct | answer_only | 42/59 (0.712) | 42/52 (0.808) | 7/59 (0.119) | 2/9 (0.222) | 37/37 (1.000) | 0/37 (0.000) | +0.085 | 43/59 (0.729) |
| wrong_answer_only | wrong | answer_only | 36/59 (0.610) | 36/51 (0.706) | 8/59 (0.136) | 0/9 (0.000) | 34/37 (0.919) | 2/37 (0.054) | -0.017 | 9/59 (0.153) |
| correct_rationale | correct | full_rationale | 46/59 (0.780) | 46/54 (0.852) | 5/59 (0.085) | 4/9 (0.444) | 36/37 (0.973) | 0/37 (0.000) | +0.153 | 44/59 (0.746) |
| wrong_rationale | wrong | full_rationale | 29/59 (0.492) | 29/52 (0.558) | 7/59 (0.119) | 0/9 (0.000) | 29/37 (0.784) | 8/37 (0.216) | -0.136 | 21/59 (0.356) |
| correct_redacted_rationale | correct | redacted_rationale | 47/59 (0.797) | 47/54 (0.870) | 5/59 (0.085) | 4/9 (0.444) | 37/37 (1.000) | 0/37 (0.000) | +0.169 | 2/59 (0.034) |
| wrong_redacted_rationale | wrong | redacted_rationale | 34/59 (0.576) | 34/54 (0.630) | 5/59 (0.085) | 1/9 (0.111) | 32/37 (0.865) | 5/37 (0.135) | -0.051 | 2/59 (0.034) |
| correct_equation_surface | correct | equation_surface | 38/59 (0.644) | 38/49 (0.776) | 10/59 (0.169) | 2/9 (0.222) | 36/37 (0.973) | 1/37 (0.027) | +0.017 | 6/59 (0.102) |
| wrong_equation_surface | wrong | equation_surface | 35/59 (0.593) | 35/50 (0.700) | 9/59 (0.153) | 0/9 (0.000) | 34/37 (0.919) | 3/37 (0.081) | -0.034 | 6/59 (0.102) |
| correct_typed_public_state | correct | typed_public_state | 37/59 (0.627) | 37/46 (0.804) | 13/59 (0.220) | 0/9 (0.000) | 37/37 (1.000) | 0/37 (0.000) | +0.000 | 9/59 (0.153) |
| wrong_typed_public_state | wrong | typed_public_state | 35/59 (0.593) | 35/48 (0.729) | 11/59 (0.186) | 0/9 (0.000) | 34/37 (0.919) | 3/37 (0.081) | -0.034 | 7/59 (0.119) |

## All Source Cases Readout

Wrong-peer harm ranking:
- `wrong_rationale` / `full_rationale`: harm 8/37 (0.216); resistance 29/37 (0.784)
- `wrong_redacted_rationale` / `redacted_rationale`: harm 5/37 (0.135); resistance 32/37 (0.865)
- `wrong_equation_surface` / `equation_surface`: harm 3/37 (0.081); resistance 34/37 (0.919)
- `wrong_typed_public_state` / `typed_public_state`: harm 3/37 (0.081); resistance 34/37 (0.919)
- `wrong_answer_only` / `answer_only`: harm 2/37 (0.054); resistance 34/37 (0.919)

Correct-peer utility ranking:
- `correct_rationale` / `full_rationale`: utility 4/9 (0.444)
- `correct_redacted_rationale` / `redacted_rationale`: utility 4/9 (0.444)
- `correct_answer_only` / `answer_only`: utility 2/9 (0.222)
- `correct_equation_surface` / `equation_surface`: utility 2/9 (0.222)
- `correct_typed_public_state` / `typed_public_state`: utility 0/9 (0.000)

- `wrong_typed_public_state` vs `wrong_rationale` harm delta: -0.135
- `wrong_typed_public_state` vs `wrong_equation_surface` harm delta: +0.000
- `correct_typed_public_state` vs `correct_rationale` utility delta: -0.444

Protocol flags:
- `no_peer`: `unknown_heavy` 0.220 (threshold 0.20)
- `wrong_rationale`: `high_harm` 0.216 (threshold 0.20)
- `correct_typed_public_state`: `low_utility` 0.000 (threshold 0.15)
- `correct_typed_public_state`: `unknown_heavy` 0.220 (threshold 0.20)

## Source-Label-Reliable Cases

- Cases: `47`
- Records: `517`

| Condition | Peer | Surface | Correct / records | Known acc | Unknown | Utility | Resistance | Harm | Robustness | Adoption |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_peer | none | no_peer | 32/47 (0.681) | 32/39 (0.821) | 8/47 (0.170) | - | - | - | +0.000 | - |
| correct_answer_only | correct | answer_only | 36/47 (0.766) | 36/44 (0.818) | 3/47 (0.064) | 2/7 (0.286) | 32/32 (1.000) | 0/32 (0.000) | +0.085 | 39/47 (0.830) |
| wrong_answer_only | wrong | answer_only | 31/47 (0.660) | 31/43 (0.721) | 4/47 (0.085) | 0/7 (0.000) | 29/32 (0.906) | 2/32 (0.062) | -0.021 | 6/47 (0.128) |
| correct_rationale | correct | full_rationale | 41/47 (0.872) | 41/45 (0.911) | 2/47 (0.043) | 4/7 (0.571) | 31/32 (0.969) | 0/32 (0.000) | +0.191 | 40/47 (0.851) |
| wrong_rationale | wrong | full_rationale | 24/47 (0.511) | 24/45 (0.533) | 2/47 (0.043) | 0/7 (0.000) | 24/32 (0.750) | 8/32 (0.250) | -0.170 | 16/47 (0.340) |
| correct_redacted_rationale | correct | redacted_rationale | 42/47 (0.894) | 42/45 (0.933) | 2/47 (0.043) | 4/7 (0.571) | 32/32 (1.000) | 0/32 (0.000) | +0.213 | 2/47 (0.043) |
| wrong_redacted_rationale | wrong | redacted_rationale | 29/47 (0.617) | 29/46 (0.630) | 1/47 (0.021) | 1/7 (0.143) | 27/32 (0.844) | 5/32 (0.156) | -0.064 | 1/47 (0.021) |
| correct_equation_surface | correct | equation_surface | 33/47 (0.702) | 33/41 (0.805) | 6/47 (0.128) | 2/7 (0.286) | 31/32 (0.969) | 1/32 (0.031) | +0.021 | 5/47 (0.106) |
| wrong_equation_surface | wrong | equation_surface | 30/47 (0.638) | 30/43 (0.698) | 4/47 (0.085) | 0/7 (0.000) | 29/32 (0.906) | 3/32 (0.094) | -0.043 | 4/47 (0.085) |
| correct_typed_public_state | correct | typed_public_state | 32/47 (0.681) | 32/39 (0.821) | 8/47 (0.170) | 0/7 (0.000) | 32/32 (1.000) | 0/32 (0.000) | +0.000 | 7/47 (0.149) |
| wrong_typed_public_state | wrong | typed_public_state | 30/47 (0.638) | 30/41 (0.732) | 6/47 (0.128) | 0/7 (0.000) | 29/32 (0.906) | 3/32 (0.094) | -0.043 | 5/47 (0.106) |

## Source-Label-Reliable Cases Readout

Wrong-peer harm ranking:
- `wrong_rationale` / `full_rationale`: harm 8/32 (0.250); resistance 24/32 (0.750)
- `wrong_redacted_rationale` / `redacted_rationale`: harm 5/32 (0.156); resistance 27/32 (0.844)
- `wrong_equation_surface` / `equation_surface`: harm 3/32 (0.094); resistance 29/32 (0.906)
- `wrong_typed_public_state` / `typed_public_state`: harm 3/32 (0.094); resistance 29/32 (0.906)
- `wrong_answer_only` / `answer_only`: harm 2/32 (0.062); resistance 29/32 (0.906)

Correct-peer utility ranking:
- `correct_rationale` / `full_rationale`: utility 4/7 (0.571)
- `correct_redacted_rationale` / `redacted_rationale`: utility 4/7 (0.571)
- `correct_answer_only` / `answer_only`: utility 2/7 (0.286)
- `correct_equation_surface` / `equation_surface`: utility 2/7 (0.286)
- `correct_typed_public_state` / `typed_public_state`: utility 0/7 (0.000)

- `wrong_typed_public_state` vs `wrong_rationale` harm delta: -0.156
- `wrong_typed_public_state` vs `wrong_equation_surface` harm delta: +0.000
- `correct_typed_public_state` vs `correct_rationale` utility delta: -0.571

Protocol flags:
- `wrong_rationale`: `high_harm` 0.250 (threshold 0.20)
- `correct_typed_public_state`: `low_utility` 0.000 (threshold 0.15)

## Field Inventory

| Condition | Visible slots | Hidden slots |
| --- | --- | --- |
| `no_peer` | - | - |
| `correct_answer_only` | final_answer_authority | relation_skeleton, numeric_role_slots, equation_surface |
| `wrong_answer_only` | final_answer_authority | relation_skeleton, numeric_role_slots, equation_surface |
| `correct_rationale` | final_answer_authority, relation_skeleton, numeric_role_slots, equation_surface, natural_language_rationale | - |
| `wrong_rationale` | final_answer_authority, relation_skeleton, numeric_role_slots, equation_surface, natural_language_rationale | - |
| `correct_redacted_rationale` | relation_skeleton, numeric_role_slots, equation_surface | explicit_final_answer_slot |
| `wrong_redacted_rationale` | relation_skeleton, numeric_role_slots, equation_surface | explicit_final_answer_slot |
| `correct_equation_surface` | numeric_role_slots, equation_surface | explicit_final_answer_slot, full_natural_language_rationale |
| `wrong_equation_surface` | numeric_role_slots, equation_surface | explicit_final_answer_slot, full_natural_language_rationale |
| `correct_typed_public_state` | target_predicate, relation_or_equation_evidence, numeric_role_slots | source_identity, explicit_final_answer_slot |
| `wrong_typed_public_state` | target_predicate, relation_or_equation_evidence, numeric_role_slots | source_identity, explicit_final_answer_slot |

## Notes

- MATH here should be read as a peer-influence diagnostic on math reasoning cases, not a general multi-agent communication benchmark.
- Typed public state is treated as one diagnostic surface in the field inventory, not as a method claim.
- Source-label-reliable cases require the saved correct peer to be semantically correct and the saved wrong peer to be semantically wrong against the original boxed answer.
