# Field-Authority Standalone Projection

Date: 2026-06-15

## What We Tried

I followed the field-contract quarantine pressure note and built the next local
objects without changing the old verifier artifacts.

New scripts:

- `scripts/build_pact_field_authority_projection_packet.py`
- `scripts/audit_pact_final_span_granularity.py`

New offset50 artifacts:

- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-projection/summary.json`
- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-projection/summary.md`
- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-projection/detector_records.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-projection/security_projection_packet.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-projection/standalone_quarantine_packet.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-pact-final-span-granularity/summary.json`
- `experiments/_archive/20260616-pruned/20260615-local-pact-final-span-granularity/summary.md`

New neighboring-slice setup artifacts:

- `experiments/_archive/20260616-pruned/20260615-local-pact-public-state-field-packet-offset100/field_packet.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-pact-public-state-field-packet-offset100/summary.json`
- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-projection-offset100/security_projection_packet.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-projection-offset100/standalone_quarantine_packet.jsonl`

I also parameterized `scripts/build_pact_public_state_field_packet.py` with
`--packet-prefix`, so offset100 packets do not keep offset50 packet IDs.

## Standalone Detector Result

The new detector uses only the original question and current public fields. It
does not read the old paired `target_slot_diagnostic`.

On the offset50 packet:

| Detector action | Count |
| --- | ---: |
| `hide` | `30` |
| `project_question_root` | `70` |

Offline routing over the already-run five-condition outputs is not encouraging:

| Strategy | EM | Avg F1 |
| --- | ---: | ---: |
| always hide public target | `0.590` | `0.725` |
| always security projection / frozen question target | `0.580` | `0.734` |
| standalone hide-risky else project | `0.560` | `0.719` |
| original public state | `0.520` | `0.688` |

This is useful mostly as a deletion signal. Removing the paired diagnostic is
possible, but the current lexical standalone detector is not claim-ready.

## Neighboring Slice Packet

I generated an offset100 field packet from the existing PACT offset100 baseline
and final-contract traces:

- `50` HotpotQA samples, indices `100` through `149`;
- `2` source runs, `baseline` and `final_contract`;
- `5` public-state field conditions, `500` prompt rows;
- target-slot diagnostics flag `6` sample indices:
  `107`, `112`, `139`, `140`, `142`, and `147`.

From that packet, the field-authority builder produced:

- `100` security-projection rows;
- `100` standalone-quarantine rows;
- detector split: `35` hide, `65` project.

There are no offset100 model outputs for these packets yet, so no behavior claim
is attached to them.

## Final-Span / Granularity Audit

The existing offset50 quarantine model run is still EM `0.610`, but the new
span audit shows that strict answer-surface pressure is non-trivial:

| Family | Count |
| --- | ---: |
| exact | `61` |
| content mismatch | `23` |
| missing required token or qualifier | `7` |
| over-specific or sentence expansion | `6` |
| partial overlap / possible alias or type issue | `3` |

So `13/100` rows are strict-span or granularity misses rather than clean content
failures. Examples include:

- `International Boxing Hall of Fame (IBHOF)` versus
  `international boxing hall of fame`;
- `2009, Big 12` versus `2009 big 12 conference`;
- `John Florence` versus `john john florence`;
- `Fairfax County, Virginia` versus `fairfax county`.

This does not erase the quarantine result, but it bounds how much strict EM can
be read as field-authority behavior.

## Interpretation

The project should not promote the current standalone detector as a method.

The stronger next pressure is simpler:

- run the offset100 security-projection packet;
- run the offset100 standalone-quarantine packet only as a detector stress test;
- compare both to fixed hide/freeze controls on the same neighboring slice;
- keep final-span/granularity labels near the score.

If security projection survives offset100 while the standalone detector still
lags fixed controls, the story should shift away from "detector chooses good
targets" and toward "upstream authority fields must be blocked or projected to
the trusted question root."

## Caveats

- No new model behavior was generated in this step.
- Offset50 routing reuses previously generated outputs and is diagnostic only.
- Offset100 bridge labels are not rebuilt yet; all rows currently fall into the
  default stable bridge bucket.
- The final-span audit uses gold answers and is an evaluation diagnostic, not a
  runtime verifier.

## Next Move

Run the offset100 `security_projection_packet.jsonl` and
`standalone_quarantine_packet.jsonl` with the same low-temperature Qwen2.5-14B
runner, then evaluate against HotpotQA EM/F1 plus the final-span/granularity
audit.
