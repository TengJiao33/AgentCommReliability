# MATH200 Peer Claim Hygiene

Date: 2026-06-15

## Why This Exists

The MATH200 peer-influence packet already had a useful protocol readout, but
two caveats were still too close to the claim:

- semantic unknowns in MATH answer equivalence;
- source cases where the saved `correct_peer` / `wrong_peer` labels were not
  semantically reliable.

This pass does not run a model and does not introduce a new surface. It builds a
review packet that separates claim-bearing cases from cases that should be
quarantined or manually inspected before the story is sharpened.

Artifacts:

- Script: `scripts/build_peer_claim_hygiene_packet.py`
- Packet: `experiments/20260615-local-math200-peer-claim-hygiene/`
- Main summary: `experiments/20260615-local-math200-peer-claim-hygiene/README.md`
- Machine summary: `experiments/20260615-local-math200-peer-claim-hygiene/claim_hygiene_summary.json`
- Field-label packet: `experiments/20260615-local-math200-peer-claim-hygiene/field_label_packet.jsonl`

## What The Packet Separates

The packet reads the anonymous, named, and randomized MATH200 semantic
peer-exposure records plus the existing semantic source-case audit.

It writes:

- `semantic_unknown_records.jsonl`: one row per semantic-unknown output.
- `semantic_unknown_cases.jsonl`: case-level grouping of unknowns.
- `source_label_unreliable_cases.jsonl`: source cases whose saved correct/wrong
  peer labels are not semantically reliable.
- `source_label_sensitive_rows.jsonl`: peer-condition rows whose result changes
  between anonymous and named/randomized source-label modes.
- `baseline_mode_drift_rows.jsonl`: no-peer drift across modes.
- `field_label_packet.jsonl`: behavior-changing and source-label-sensitive rows
  with blank manual label fields for relation, numeric/role, equation,
  final-answer authority, source identity, and target revision behavior.

## Main Counts

The noisy surface is concentrated:

| Bucket | Count |
| --- | ---: |
| Source cases | `59` |
| Semantic-unknown records | `99/649` |
| Semantic-unknown cases | `16/59` |
| Source-label-unreliable cases | `12/59` |
| Clean claim-bearing cases | `37/59` |
| Source-label-sensitive rows | `61` |
| Field-label packet rows | `97` |
| No-peer baseline drift across source modes | `0` |

The semantic unknowns are not evenly spread. Cases `14`, `18`, and `118` are
unknown under all `11` anonymous conditions; case `198` is unknown under `9`;
case `12` is unknown under `8`. This means the current unknown problem is partly
a case-level evaluator/source-label problem, not just scattered output noise.

Unknown statuses:

| Status | Records |
| --- | ---: |
| `missing_answer` | `53` |
| `unknown_semantic_parse` | `46` |

Source-label-unreliable reasons:

| Reason | Cases |
| --- | ---: |
| `correct_peer_not_correct` | `4` |
| `both_labels_unreliable` | `3` |
| `wrong_peer_unknown` | `3` |
| `wrong_peer_not_wrong` | `1` |
| `correct_peer_unknown` | `1` |

## Clean Subset Readout

Clean means:

- the source case is source-label reliable;
- the anonymous peer-exposure packet has no semantic-unknown record for any of
  its `11` conditions.

That leaves `37` cases and `407` records.

On this stricter subset, the core protocol shape survives:

| Condition | Correct / Records | Harm | Utility | Unknown |
| --- | ---: | ---: | ---: | ---: |
| `wrong_answer_only` | `30/37` | `1/31` | `0/6` | `0/37` |
| `wrong_rationale` | `22/37` | `9/31` | `0/6` | `0/37` |
| `wrong_redacted_rationale` | `27/37` | `4/31` | `0/6` | `0/37` |
| `wrong_equation_surface` | `29/37` | `3/31` | `1/6` | `0/37` |
| `wrong_typed_public_state` | `29/37` | `3/31` | `1/6` | `0/37` |
| `correct_rationale` | `35/37` | `0/31` | `4/6` | `0/37` |
| `correct_redacted_rationale` | `34/37` | `0/31` | `3/6` | `0/37` |
| `correct_typed_public_state` | `32/37` | `0/31` | `1/6` | `0/37` |

This keeps the same bounded conclusion as the larger semantic audit:

- wrong full rationale remains the highest-harm surface;
- typed public state and equation surface tie on wrong-peer harm;
- correct typed public state still has low utility;
- typed public state remains a diagnostic surface, not a method win.

## Source-Label Sensitivity

The source-label packet had no no-peer baseline drift: the saved no-peer rows
match across anonymous, named, and randomized runs for all `59` cases.

There are still `61` peer-condition rows whose result changes across source
label modes. This is useful for field labeling, but not enough for an identity
bias claim:

- there is one run per source-label mode;
- named labels are simple agent labels, not authority or social identities;
- many changes are condition-specific and should be read as pressure cases.

The packet therefore treats these rows as manual-review candidates, not as
population estimates.

The clean source-label-sensitive rows have now received seed labels:

- file:
  `experiments/20260615-local-math200-peer-claim-hygiene/manual_source_label_sensitive_seed_labels.jsonl`;
- rows: `23`;
- categories:
  - `rescue_lost`: `9`;
  - `harm_removed`: `6`;
  - `harm_added`: `6`;
  - `rescue_added`: `2`;
- final-answer authority hidden in `15/23` rows;
- parser-surface confound marked in `1/23` rows.

These labels keep the interpretation bounded. The rows show source-mode
sensitivity under same peer content and no no-peer baseline drift, but they do
not prove identity bias. Most of the clean source-sensitive cases are better
read as pressure rows where relation, equation, or numeric-role fields are used
differently across independent source-label-mode runs.

## Answer-Only Surface Confound

While inspecting source-label-sensitive rows, case `11` exposed a plumbing
confound: the `correct_answer_only` surface displayed `3`, but the raw semantic
peer answer was `2\sqrt{3}`. The source-label audit correctly marks the peer as
semantically correct, but the answer-only surface was built from the older
numeric parser field.

The packet now includes:

- `answer_only_surface_issue_rows.jsonl`

This compares the displayed answer-only slot against the raw semantic peer
answer from the source-case audit.

Counts:

| Scope | Equivalent | Semantic mismatch | Unknown equivalence |
| --- | ---: | ---: | ---: |
| Anonymous run | `84` | `27` | `7` |
| Clean cases, all source modes | `177` | `45` | `0` |

Because the three source-label modes use the same peer content, the clean
semantic mismatches correspond to `15` clean case/condition pairs repeated
across anonymous, named, and randomized modes.

This means `answer_only` should not be treated as a clean final-answer-authority
control on symbolic MATH. It is partly a lossy numeric-parser surface. The
field-level story can still use answer-only as a diagnostic condition, but any
claim involving answer-only must separate:

- true final-answer authority;
- numeric-parser truncation or symbolic answer loss;
- downstream model sensitivity to the shortened surface.

Follow-up repair:

- added `correct_raw_answer_only` and `wrong_raw_answer_only` as future
  conditions that display raw final-answer text extracted from the saved peer
  response rather than the older numeric parser field;
- added local preview packet:
  `experiments/20260615-local-raw-answer-only-preview/`;
- preview counts over the same source cases match the confound audit:
  `84/118` legacy answer-only rows are equivalent to raw peer answers,
  `27/118` semantically mismatch, and `7/118` remain unknown-equivalence;
- no model was rerun, so this repairs future controls but does not alter the
  existing MATH200 peer-influence result.

## Field-Label Packet

The generated field-label packet has `97` rows:

- `36` anonymous behavior-changing rows;
- `61` source-label-sensitive rows.

For the next manual pass, the highest-priority clean right-to-wrong rows are:

`13`, `21`, `25`, `28`, `29`, `61`, `96`, `112`, `121`, `136`, `139`, `159`,
`165`, and `195`.

These cover the current live surfaces:

- full rationale harm;
- redacted rationale harm;
- equation-surface harm;
- typed-public-state harm;
- the answer-only boundary.

## Manual Seed Labels

A first manual seed pass labels the `21` clean anonymous right-to-wrong rows:

- file:
  `experiments/20260615-local-math200-peer-claim-hygiene/manual_seed_labels.jsonl`;
- by condition:
  - `wrong_rationale`: `9`;
  - `wrong_redacted_rationale`: `4`;
  - `wrong_typed_public_state`: `3`;
  - `wrong_equation_surface`: `3`;
  - `wrong_answer_only`: `1`;
- `correct_equation_surface`: `1`.

Clean source-label-sensitive seed labels add another `23` rows:

- `rescue_lost`: `9`;
- `harm_removed`: `6`;
- `harm_added`: `6`;
- `rescue_added`: `2`.

The seed labels are case-local notes, not rate estimates. They do make one
boundary concrete: final-answer authority is not the whole channel.

Among the `21` labeled harms:

- `10` have visible final-answer authority;
- `11` occur with the final-answer slot hidden;
- `18` are labeled as wrong relation skeletons;
- `14` are labeled as wrong numeric/role slots.

The hidden-final harms include:

- case `13`: wrong rotation operator in typed state;
- case `61`: opposing-team handshake multiplicity lost in equation/typed
  surfaces;
- case `121`: square side versus diagonal role error across equation, redacted,
  and typed surfaces;
- case `165`: rationalization sign error in equation/redacted surfaces;
- case `195`: wrong candidate-ordering relation after final-slot redaction.

This pushes the next label pass toward relation/numeric-role failure families,
not only answer copying.

## Manual Label Coverage

A follow-up helper now makes the seed-label coverage auditable:

- script:
  `scripts/summarize_peer_field_labels.py`;
- outputs:
  `experiments/20260615-local-math200-peer-claim-hygiene/manual_label_summary.md`;
  `experiments/20260615-local-math200-peer-claim-hygiene/manual_label_summary.json`;
  `experiments/20260615-local-math200-peer-claim-hygiene/manual_unlabeled_rows.jsonl`.

Coverage:

| Bucket | Rows |
| --- | ---: |
| Field-label packet rows | `97` |
| Unique labeled seed rows | `44` |
| Unlabeled rows | `53` |
| Unlabeled behavior-changing rows | `15` |
| Unlabeled source-label-sensitive rows | `38` |

The existing seed labels remain enough to support the bounded claim that
final-answer authority is not the whole channel. They are not enough for a
population taxonomy. If the MATH diagnostic needs to be carried further, the
next label pass should start from `manual_unlabeled_rows.jsonl`, especially the
remaining `15` behavior-changing rows.

## Interpretation

This pass strengthens the project posture in a quiet way. It does not make the
story bigger; it makes the denominator more honest.

The earlier MATH200 readout can still be used, but the cleaner language is now:

> On a 37-case source-label-reliable and semantic-known subset, wrong full
> rationale remains high-harm (`9/31`), while wrong typed public state and wrong
> equation surface tie at lower harm (`3/31` each). Correct typed public state
> remains low-utility (`1/6`) compared with correct full rationale (`4/6`).

That supports field-level peer-message diagnosis as a live handle. It does not
support a general typed-public-state method claim.

## Next Contact

Do not launch another MATH GPU run yet.

Next useful work:

1. Use the new raw answer-only surface only when a future MATH packet needs a
   clean final-answer-authority control; do not rerun MATH solely for this
   repair.
2. Manually label the `field_label_packet.jsonl` rows, starting with the clean
   source-label-sensitive rows not covered by the seed labels.
3. Keep semantic-unknown and source-label-unreliable cases out of claim-bearing
   denominators unless a focused evaluator fix makes them reliable.
4. After the label pass, bridge the same protocol to a split-evidence
   public-state task such as PACT/HotpotQA, where communication is needed
   rather than artificially injected.
