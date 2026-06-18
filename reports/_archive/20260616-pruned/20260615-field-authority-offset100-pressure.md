# Field-Authority Offset100 Pressure

Date: 2026-06-15

## What We Ran

I ran the next HotpotQA neighboring slice pressure test on A800_2 with
Qwen2.5-14B-Instruct.

Run artifacts:

- `experiments/_archive/20260616-pruned/20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b/`
- `experiments/_archive/20260616-pruned/20260615-1805-a8002-pact-field-authority-projection-offset100-qwen25-14b/`

Setup artifacts:

- `experiments/_archive/20260616-pruned/20260615-local-pact-public-state-field-packet-offset100/field_packet.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-projection-offset100/projection_packet.jsonl`

New analysis:

- `scripts/analyze_pact_field_authority_projection_results.py`
- `experiments/_archive/20260616-pruned/20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b/field_delta_audit/delta_summary.json`
- `experiments/_archive/20260616-pruned/20260615-1805-a8002-pact-field-authority-projection-offset100-qwen25-14b/projection_delta_audit/projection_delta_summary.json`
- span/granularity audits under both run directories.

Both runs completed with `0` failed rows:

- field controls: `500/500`;
- projection packet: `200/200`.

## Condition Scores

| Condition | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `frozen_target_plus_evidence_no_final` | `100` | `0.560` | `0.698` |
| `security_projection_question_root_no_final` | `100` | `0.510` | `0.661` |
| `question_plus_public_state_no_final` | `100` | `0.500` | `0.648` |
| `question_plus_evidence_no_target_no_final` | `100` | `0.470` | `0.610` |
| `standalone_authority_quarantine_no_final` | `100` | `0.440` | `0.604` |
| `question_plus_public_state_with_final` | `100` | `0.430` | `0.575` |
| `public_target_plus_evidence_no_question_no_final` | `100` | `0.300` | `0.481` |

## Main Read

The offset100 result does not validate the standalone detector.

The best condition is still the simple frozen question-derived target control
(`0.560` EM). Security-style projection is directionally better than the
original public-state/no-final surface (`0.510` versus `0.500`), but it is lower
than the frozen-target control. The standalone quarantine condition falls below
both (`0.440`).

The strongest repeated behavior is still authority separation:

- public target without original question collapses (`0.300` EM);
- frozen question target improves over original public state (`9` rescues,
  `3` regressions);
- final-answer candidate visibility remains risky (`3` rescues, `10`
  regressions, copy rate `0.700`).

## Delta Checks

Against `question_plus_public_state_no_final`:

| Comparison | Rescues | Regressions | Both right | Both wrong |
| --- | ---: | ---: | ---: | ---: |
| freeze question target | `9` | `3` | `47` | `41` |
| hide public target | `4` | `7` | `43` | `46` |
| hide question, keep public target | `0` | `20` | `30` | `50` |
| show final-answer candidate | `3` | `10` | `40` | `47` |

Projection-specific comparisons:

| Comparison | Projection rescues | Projection regressions | Both right | Both wrong |
| --- | ---: | ---: | ---: | ---: |
| security vs frozen target | `0` | `5` | `51` | `44` |
| security vs hide target | `8` | `4` | `43` | `45` |
| security vs public state | `7` | `6` | `44` | `43` |
| standalone vs frozen target | `0` | `12` | `44` | `44` |
| standalone vs security | `1` | `8` | `43` | `48` |

## Span / Granularity Boundary

Strict EM is still noisy:

- field controls: `101/500` strict-span or granularity misses;
- projection run: `42/200` strict-span or granularity misses.

Common examples are answer expansions such as `Erika Jayne was born first`
instead of `erika jayne`, or `KKR & Co. L.P.` instead of `kkr co`.

The span audit does not reverse the ordering, but it warns against over-reading
small EM differences.

## Interpretation

This is a useful pressure result because it kills a tempting story.

Do not claim that the standalone field-authority detector is working. On the
neighboring slice, its routing hurts. The detector should be treated as an audit
surface, not a method component.

What survives is narrower:

**Public `Action Required` is not a reliable task contract by itself. The
trusted question root remains necessary, and replacing public target authority
with a question-derived target is the strongest current control.**

This is now a field-authority reliability story, not a detector story.

## Caveats

- One model, one neighboring HotpotQA offset100 slice.
- The packet is a saved-field re-answering stress test, not a full PACT rerun.
- Offset100 bridge labels were rebuilt afterward in
  `reports/_archive/20260616-pruned/20260615-field-authority-offset100-bridge-audit.md`; this report's
  original aggregate tables still use the field-packet run outputs directly.
- The security projection prompt is not identical to the earlier frozen target
  prompt, and the prompt wording difference appears to matter.
- Span/granularity errors remain a large slice of strict EM failures.

## Next Move

Retire standalone detector as a near-term method route. If this line continues,
the next useful object is a cleaner projection-only packet that uses the
stronger frozen-target prompt wording, then applies the rebuilt offset100 bridge
labels to inspect which units move.
