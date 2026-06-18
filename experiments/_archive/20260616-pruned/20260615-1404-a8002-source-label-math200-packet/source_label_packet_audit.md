# Peer Source-Label Packet Audit

Reference mode: `anonymous`.

This compares protocol-audit outputs across source-label modes. It does not rerun semantic evaluation or the model.

## Source-Label-Reliable Metrics

| Mode | Condition | Surface | Utility | Resistance | Harm | Robustness | Adoption | Unknown |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| anonymous | wrong_answer_only | answer_only | 0/7 (0.000) | 31/32 (0.969) | 1/32 (0.031) | +0.021 | 6/47 (0.128) | 3/47 (0.064) |
| anonymous | wrong_rationale | full_rationale | 0/7 (0.000) | 22/32 (0.688) | 9/32 (0.281) | -0.213 | 17/47 (0.362) | 3/47 (0.064) |
| anonymous | wrong_redacted_rationale | redacted_rationale | 0/7 (0.000) | 28/32 (0.875) | 4/32 (0.125) | -0.085 | 3/47 (0.064) | 4/47 (0.085) |
| anonymous | wrong_equation_surface | equation_surface | 1/7 (0.143) | 29/32 (0.906) | 3/32 (0.094) | -0.043 | 5/47 (0.106) | 6/47 (0.128) |
| anonymous | wrong_typed_public_state | typed_public_state | 1/7 (0.143) | 29/32 (0.906) | 3/32 (0.094) | -0.043 | 6/47 (0.128) | 7/47 (0.149) |
| anonymous | correct_answer_only | answer_only | 2/7 (0.286) | 32/32 (1.000) | 0/32 (0.000) | +0.128 | 41/47 (0.872) | 2/47 (0.043) |
| anonymous | correct_rationale | full_rationale | 5/7 (0.714) | 32/32 (1.000) | 0/32 (0.000) | +0.255 | 43/47 (0.915) | 0/47 (0.000) |
| anonymous | correct_redacted_rationale | redacted_rationale | 4/7 (0.571) | 32/32 (1.000) | 0/32 (0.000) | +0.213 | 1/47 (0.021) | 2/47 (0.043) |
| anonymous | correct_equation_surface | equation_surface | 1/7 (0.143) | 31/32 (0.969) | 1/32 (0.031) | +0.000 | 6/47 (0.128) | 7/47 (0.149) |
| anonymous | correct_typed_public_state | typed_public_state | 1/7 (0.143) | 32/32 (1.000) | 0/32 (0.000) | +0.021 | 7/47 (0.149) | 8/47 (0.170) |
| named | wrong_answer_only | answer_only | 0/7 (0.000) | 31/32 (0.969) | 1/32 (0.031) | +0.021 | 5/47 (0.106) | 4/47 (0.085) |
| named | wrong_rationale | full_rationale | 0/7 (0.000) | 23/32 (0.719) | 9/32 (0.281) | -0.191 | 17/47 (0.362) | 1/47 (0.021) |
| named | wrong_redacted_rationale | redacted_rationale | 0/7 (0.000) | 27/32 (0.844) | 5/32 (0.156) | -0.106 | 0/47 (0.000) | 1/47 (0.021) |
| named | wrong_equation_surface | equation_surface | 0/7 (0.000) | 31/32 (0.969) | 1/32 (0.031) | -0.021 | 6/47 (0.128) | 6/47 (0.128) |
| named | wrong_typed_public_state | typed_public_state | 1/7 (0.143) | 29/32 (0.906) | 3/32 (0.094) | -0.043 | 6/47 (0.128) | 7/47 (0.149) |
| named | correct_answer_only | answer_only | 3/7 (0.429) | 32/32 (1.000) | 0/32 (0.000) | +0.128 | 41/47 (0.872) | 2/47 (0.043) |
| named | correct_rationale | full_rationale | 3/7 (0.429) | 32/32 (1.000) | 0/32 (0.000) | +0.213 | 41/47 (0.872) | 0/47 (0.000) |
| named | correct_redacted_rationale | redacted_rationale | 3/7 (0.429) | 32/32 (1.000) | 0/32 (0.000) | +0.149 | 2/47 (0.043) | 4/47 (0.085) |
| named | correct_equation_surface | equation_surface | 0/7 (0.000) | 31/32 (0.969) | 1/32 (0.031) | -0.021 | 5/47 (0.106) | 6/47 (0.128) |
| named | correct_typed_public_state | typed_public_state | 1/7 (0.143) | 32/32 (1.000) | 0/32 (0.000) | +0.021 | 7/47 (0.149) | 8/47 (0.170) |
| randomized | wrong_answer_only | answer_only | 0/7 (0.000) | 29/32 (0.906) | 2/32 (0.062) | -0.021 | 6/47 (0.128) | 4/47 (0.085) |
| randomized | wrong_rationale | full_rationale | 0/7 (0.000) | 24/32 (0.750) | 8/32 (0.250) | -0.170 | 16/47 (0.340) | 2/47 (0.043) |
| randomized | wrong_redacted_rationale | redacted_rationale | 1/7 (0.143) | 27/32 (0.844) | 5/32 (0.156) | -0.064 | 1/47 (0.021) | 1/47 (0.021) |
| randomized | wrong_equation_surface | equation_surface | 0/7 (0.000) | 29/32 (0.906) | 3/32 (0.094) | -0.043 | 4/47 (0.085) | 4/47 (0.085) |
| randomized | wrong_typed_public_state | typed_public_state | 0/7 (0.000) | 29/32 (0.906) | 3/32 (0.094) | -0.043 | 5/47 (0.106) | 6/47 (0.128) |
| randomized | correct_answer_only | answer_only | 2/7 (0.286) | 32/32 (1.000) | 0/32 (0.000) | +0.085 | 39/47 (0.830) | 3/47 (0.064) |
| randomized | correct_rationale | full_rationale | 4/7 (0.571) | 31/32 (0.969) | 0/32 (0.000) | +0.191 | 40/47 (0.851) | 2/47 (0.043) |
| randomized | correct_redacted_rationale | redacted_rationale | 4/7 (0.571) | 32/32 (1.000) | 0/32 (0.000) | +0.213 | 2/47 (0.043) | 2/47 (0.043) |
| randomized | correct_equation_surface | equation_surface | 2/7 (0.286) | 31/32 (0.969) | 1/32 (0.031) | +0.021 | 5/47 (0.106) | 6/47 (0.128) |
| randomized | correct_typed_public_state | typed_public_state | 0/7 (0.000) | 32/32 (1.000) | 0/32 (0.000) | +0.000 | 7/47 (0.149) | 8/47 (0.170) |

## Deltas Vs Reference

| Mode | Subset | Condition | Harm delta | Utility delta | Resistance delta | Adoption delta | Robustness delta-delta |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| named | Source-Label-Reliable Cases | wrong_answer_only | +0.000 | +0.000 | +0.000 | -0.021 | +0.000 |
| named | Source-Label-Reliable Cases | wrong_rationale | +0.000 | +0.000 | +0.031 | +0.000 | +0.021 |
| named | Source-Label-Reliable Cases | wrong_redacted_rationale | +0.031 | +0.000 | -0.031 | -0.064 | -0.021 |
| named | Source-Label-Reliable Cases | wrong_equation_surface | -0.062 | -0.143 | +0.062 | +0.021 | +0.021 |
| named | Source-Label-Reliable Cases | wrong_typed_public_state | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 |
| named | Source-Label-Reliable Cases | correct_answer_only | +0.000 | +0.143 | +0.000 | +0.000 | +0.000 |
| named | Source-Label-Reliable Cases | correct_rationale | +0.000 | -0.286 | +0.000 | -0.043 | -0.043 |
| named | Source-Label-Reliable Cases | correct_redacted_rationale | +0.000 | -0.143 | +0.000 | +0.021 | -0.064 |
| named | Source-Label-Reliable Cases | correct_equation_surface | +0.000 | -0.143 | +0.000 | -0.021 | -0.021 |
| named | Source-Label-Reliable Cases | correct_typed_public_state | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 |
| randomized | Source-Label-Reliable Cases | wrong_answer_only | +0.031 | +0.000 | -0.062 | +0.000 | -0.043 |
| randomized | Source-Label-Reliable Cases | wrong_rationale | -0.031 | +0.000 | +0.062 | -0.021 | +0.043 |
| randomized | Source-Label-Reliable Cases | wrong_redacted_rationale | +0.031 | +0.143 | -0.031 | -0.043 | +0.021 |
| randomized | Source-Label-Reliable Cases | wrong_equation_surface | +0.000 | -0.143 | +0.000 | -0.021 | +0.000 |
| randomized | Source-Label-Reliable Cases | wrong_typed_public_state | +0.000 | -0.143 | +0.000 | -0.021 | +0.000 |
| randomized | Source-Label-Reliable Cases | correct_answer_only | +0.000 | +0.000 | +0.000 | -0.043 | -0.043 |
| randomized | Source-Label-Reliable Cases | correct_rationale | +0.000 | -0.143 | -0.031 | -0.064 | -0.064 |
| randomized | Source-Label-Reliable Cases | correct_redacted_rationale | +0.000 | +0.000 | +0.000 | +0.021 | +0.000 |
| randomized | Source-Label-Reliable Cases | correct_equation_surface | +0.000 | +0.143 | +0.000 | -0.021 | +0.021 |
| randomized | Source-Label-Reliable Cases | correct_typed_public_state | +0.000 | -0.143 | +0.000 | +0.000 | -0.021 |

## Notes

- Large deltas here indicate source-label sensitivity; stable rows support content-field rather than identity-label influence.
- Adoption is the saved peer-answer adoption flag from each protocol audit, not semantic recomputation.
