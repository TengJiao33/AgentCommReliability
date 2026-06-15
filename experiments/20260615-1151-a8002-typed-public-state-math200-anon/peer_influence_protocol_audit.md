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
| correct_answer_only | correct | answer_only | 44/59 (0.746) | 44/53 (0.830) | 6/59 (0.102) | 2/9 (0.222) | 37/37 (1.000) | 0/37 (0.000) | +0.119 | 45/59 (0.763) |
| wrong_answer_only | wrong | answer_only | 38/59 (0.644) | 38/51 (0.745) | 8/59 (0.136) | 0/9 (0.000) | 36/37 (0.973) | 1/37 (0.027) | +0.017 | 9/59 (0.153) |
| correct_rationale | correct | full_rationale | 49/59 (0.831) | 49/56 (0.875) | 3/59 (0.051) | 5/9 (0.556) | 37/37 (1.000) | 0/37 (0.000) | +0.203 | 47/59 (0.797) |
| wrong_rationale | wrong | full_rationale | 27/59 (0.458) | 27/51 (0.529) | 8/59 (0.136) | 0/9 (0.000) | 27/37 (0.730) | 9/37 (0.243) | -0.169 | 22/59 (0.373) |
| correct_redacted_rationale | correct | redacted_rationale | 47/59 (0.797) | 47/54 (0.870) | 5/59 (0.085) | 4/9 (0.444) | 37/37 (1.000) | 0/37 (0.000) | +0.169 | 1/59 (0.017) |
| wrong_redacted_rationale | wrong | redacted_rationale | 32/59 (0.542) | 32/49 (0.653) | 10/59 (0.169) | 0/9 (0.000) | 32/37 (0.865) | 4/37 (0.108) | -0.085 | 4/59 (0.068) |
| correct_equation_surface | correct | equation_surface | 37/59 (0.627) | 37/48 (0.771) | 11/59 (0.186) | 1/9 (0.111) | 36/37 (0.973) | 1/37 (0.027) | +0.000 | 7/59 (0.119) |
| wrong_equation_surface | wrong | equation_surface | 35/59 (0.593) | 35/48 (0.729) | 11/59 (0.186) | 1/9 (0.111) | 34/37 (0.919) | 3/37 (0.081) | -0.034 | 7/59 (0.119) |
| correct_typed_public_state | correct | typed_public_state | 38/59 (0.644) | 38/47 (0.809) | 12/59 (0.203) | 1/9 (0.111) | 37/37 (1.000) | 0/37 (0.000) | +0.017 | 8/59 (0.136) |
| wrong_typed_public_state | wrong | typed_public_state | 35/59 (0.593) | 35/47 (0.745) | 12/59 (0.203) | 1/9 (0.111) | 34/37 (0.919) | 3/37 (0.081) | -0.034 | 8/59 (0.136) |

## All Source Cases Readout

Wrong-peer harm ranking:
- `wrong_rationale` / `full_rationale`: harm 9/37 (0.243); resistance 27/37 (0.730)
- `wrong_redacted_rationale` / `redacted_rationale`: harm 4/37 (0.108); resistance 32/37 (0.865)
- `wrong_equation_surface` / `equation_surface`: harm 3/37 (0.081); resistance 34/37 (0.919)
- `wrong_typed_public_state` / `typed_public_state`: harm 3/37 (0.081); resistance 34/37 (0.919)
- `wrong_answer_only` / `answer_only`: harm 1/37 (0.027); resistance 36/37 (0.973)

Correct-peer utility ranking:
- `correct_rationale` / `full_rationale`: utility 5/9 (0.556)
- `correct_redacted_rationale` / `redacted_rationale`: utility 4/9 (0.444)
- `correct_answer_only` / `answer_only`: utility 2/9 (0.222)
- `correct_equation_surface` / `equation_surface`: utility 1/9 (0.111)
- `correct_typed_public_state` / `typed_public_state`: utility 1/9 (0.111)

- `wrong_typed_public_state` vs `wrong_rationale` harm delta: -0.162
- `wrong_typed_public_state` vs `wrong_equation_surface` harm delta: +0.000
- `correct_typed_public_state` vs `correct_rationale` utility delta: -0.444

Protocol flags:
- `no_peer`: `unknown_heavy` 0.220 (threshold 0.20)
- `wrong_rationale`: `high_harm` 0.243 (threshold 0.20)
- `correct_equation_surface`: `low_utility` 0.111 (threshold 0.15)
- `correct_typed_public_state`: `low_utility` 0.111 (threshold 0.15)
- `correct_typed_public_state`: `unknown_heavy` 0.203 (threshold 0.20)
- `wrong_typed_public_state`: `unknown_heavy` 0.203 (threshold 0.20)

## Source-Label-Reliable Cases

- Cases: `47`
- Records: `517`

| Condition | Peer | Surface | Correct / records | Known acc | Unknown | Utility | Resistance | Harm | Robustness | Adoption |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| no_peer | none | no_peer | 32/47 (0.681) | 32/39 (0.821) | 8/47 (0.170) | - | - | - | +0.000 | - |
| correct_answer_only | correct | answer_only | 38/47 (0.809) | 38/45 (0.844) | 2/47 (0.043) | 2/7 (0.286) | 32/32 (1.000) | 0/32 (0.000) | +0.128 | 41/47 (0.872) |
| wrong_answer_only | wrong | answer_only | 33/47 (0.702) | 33/44 (0.750) | 3/47 (0.064) | 0/7 (0.000) | 31/32 (0.969) | 1/32 (0.031) | +0.021 | 6/47 (0.128) |
| correct_rationale | correct | full_rationale | 44/47 (0.936) | 44/47 (0.936) | 0/47 (0.000) | 5/7 (0.714) | 32/32 (1.000) | 0/32 (0.000) | +0.255 | 43/47 (0.915) |
| wrong_rationale | wrong | full_rationale | 22/47 (0.468) | 22/44 (0.500) | 3/47 (0.064) | 0/7 (0.000) | 22/32 (0.688) | 9/32 (0.281) | -0.213 | 17/47 (0.362) |
| correct_redacted_rationale | correct | redacted_rationale | 42/47 (0.894) | 42/45 (0.933) | 2/47 (0.043) | 4/7 (0.571) | 32/32 (1.000) | 0/32 (0.000) | +0.213 | 1/47 (0.021) |
| wrong_redacted_rationale | wrong | redacted_rationale | 28/47 (0.596) | 28/43 (0.651) | 4/47 (0.085) | 0/7 (0.000) | 28/32 (0.875) | 4/32 (0.125) | -0.085 | 3/47 (0.064) |
| correct_equation_surface | correct | equation_surface | 32/47 (0.681) | 32/40 (0.800) | 7/47 (0.149) | 1/7 (0.143) | 31/32 (0.969) | 1/32 (0.031) | +0.000 | 6/47 (0.128) |
| wrong_equation_surface | wrong | equation_surface | 30/47 (0.638) | 30/41 (0.732) | 6/47 (0.128) | 1/7 (0.143) | 29/32 (0.906) | 3/32 (0.094) | -0.043 | 5/47 (0.106) |
| correct_typed_public_state | correct | typed_public_state | 33/47 (0.702) | 33/39 (0.846) | 8/47 (0.170) | 1/7 (0.143) | 32/32 (1.000) | 0/32 (0.000) | +0.021 | 7/47 (0.149) |
| wrong_typed_public_state | wrong | typed_public_state | 30/47 (0.638) | 30/40 (0.750) | 7/47 (0.149) | 1/7 (0.143) | 29/32 (0.906) | 3/32 (0.094) | -0.043 | 6/47 (0.128) |

## Source-Label-Reliable Cases Readout

Wrong-peer harm ranking:
- `wrong_rationale` / `full_rationale`: harm 9/32 (0.281); resistance 22/32 (0.688)
- `wrong_redacted_rationale` / `redacted_rationale`: harm 4/32 (0.125); resistance 28/32 (0.875)
- `wrong_equation_surface` / `equation_surface`: harm 3/32 (0.094); resistance 29/32 (0.906)
- `wrong_typed_public_state` / `typed_public_state`: harm 3/32 (0.094); resistance 29/32 (0.906)
- `wrong_answer_only` / `answer_only`: harm 1/32 (0.031); resistance 31/32 (0.969)

Correct-peer utility ranking:
- `correct_rationale` / `full_rationale`: utility 5/7 (0.714)
- `correct_redacted_rationale` / `redacted_rationale`: utility 4/7 (0.571)
- `correct_answer_only` / `answer_only`: utility 2/7 (0.286)
- `correct_equation_surface` / `equation_surface`: utility 1/7 (0.143)
- `correct_typed_public_state` / `typed_public_state`: utility 1/7 (0.143)

- `wrong_typed_public_state` vs `wrong_rationale` harm delta: -0.188
- `wrong_typed_public_state` vs `wrong_equation_surface` harm delta: +0.000
- `correct_typed_public_state` vs `correct_rationale` utility delta: -0.571

Protocol flags:
- `wrong_rationale`: `high_harm` 0.281 (threshold 0.20)
- `correct_equation_surface`: `low_utility` 0.143 (threshold 0.15)
- `correct_typed_public_state`: `low_utility` 0.143 (threshold 0.15)

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
