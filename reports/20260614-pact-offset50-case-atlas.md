# PACT Offset50 Case Atlas

## What We Tried

I built a small case atlas over the PACT HotpotQA offset50 paired run.

This is a specimen table, not a theory. The goal was to keep the weird cases
visible after the paired metric summary:

- 6 wrong-to-right cases;
- 4 right-to-wrong cases;
- 18 stable-wrong cases.

The atlas builder writes rough mechanical labels, then leaves the examples
available for inspection.

## Sources

| Source | Path |
| --- | --- |
| paired run | `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/` |
| atlas builder | `scripts/build_pact_case_atlas.py` |
| atlas summary | `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/case_atlas_summary.json` |
| focus cases | `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/case_atlas_focus_cases.jsonl` |

## What Happened

The rough labels over the 28 non-stable-right cases:

| Label | Count | Samples |
| --- | ---: | --- |
| `contract_rescued_verbose_surface` | 5 | `57`, `78`, `85`, `93`, `99` |
| `contract_rescued_content_or_field` | 1 | `61` |
| `strict_span_regression` | 3 | `54`, `64`, `66` |
| `content_drift_regression` | 1 | `58` |
| `final_public_state_contains_gold` | 10 | `50`, `55`, `59`, `60`, `67`, `74`, `83`, `87`, `89`, `92` |
| `recoverable_from_public_state_policy` | 1 | `62` |
| `near_miss_surface_or_span` | 1 | `97` |
| `likely_evidence_or_reasoning_failure` | 6 | `68`, `71`, `77`, `82`, `88`, `94` |

These labels are deliberately soft. They are handles for returning to cases,
not ground truth.

## Things Noticed

The contract rescues mostly look like answer-surface rescues:

| Sample | Gold | Baseline final text | Contract final text |
| ---: | --- | --- | --- |
| `57` | `keith bostic` | `Keith Bostic is younger than Jerry Glanville` | `Keith Bostic` |
| `78` | `british` | `Alfred Gell and Edmund Leach were both British` | `British` |
| `85` | `april 1 1949` | long Paul Manafort sentence | `April 1, 1949` |
| `93` | `no` | `No, the drinks Gibson and Zurracapote do not both contain gin` | `No` |
| `99` | `no` | `No, Yingkou and Fuding are not the same level of city` | `No` |

Sample `61` is different. The baseline says the executive producer is not
mentioned, while the contract run produces `Ronald Shusett`. That is not merely
shortening a verbose answer; the final-turn behavior changed.

The right-to-wrong cases split into strict-span regressions and one real
content drift:

| Sample | Gold | Baseline final text | Contract final text | Note |
| ---: | --- | --- | --- | --- |
| `54` | `max martin savan kotecha and ilya salmanzadeh` | includes all names with `and` | drops explicit `and` | high-F1 strict-span regression |
| `64` | `more than 70 countries` | `More than 70 countries` | `more than 70` | high-F1 strict-span regression |
| `66` | `international boxing hall of fame` | exact span | adds `(IBHOF)` | high-F1 strict-span regression |
| `58` | `35124` | `35,124` | `273` | content drift |

Sample `58` is the clean sentinel. The contract run's final public state
selects the civil parish population `273`, while the baseline selected the town
population `35,124`.

The stable-wrong cases are the strangest part. Ten stable-wrong cases have the
gold answer text visible somewhere in the final public action-state fields, but
the final answer still does not match exactly.

Examples:

| Sample | Gold | Contract final answer | Where the gold-like signal appears |
| ---: | --- | --- | --- |
| `50` | `2009 big 12 conference` | `2009 Big 12` | environment state says `2009 Big 12 Conference` |
| `83` | `mondelez international inc` | `Mondelez International` | environment state says `Mondelez International, Inc.` |
| `87` | `canary islands spain` | `Tenerife, La Gomera, Canary Islands, Spain` | final answer contains the gold span plus extra islands |
| `89` | `director` | `film director` | answer type is present but over-specified |

This makes the PACT failure surface feel less like one thing. Some failures are
public-state absence, some are public-state selection, some are exact-answer
contract, and some are span granularity.

## Interpretation

The offset50 atlas makes the final-answer-contract story less shiny and more
useful.

The contract is real because it rescues several verbose final-answer failures
and raises F1. It is not clean because it can alter content, lose required
span tokens, or over-compress.

The public-state boundary remains alive. The most interesting stable-wrong
cases are not "the agents never found the evidence"; they are cases where the
final public state contains a useful answer signal, but the final commitment
does not land on the exact answer.

## Caveats

- Labels are mechanical and intentionally rough.
- `final_public_state_contains_gold` is a string-signal bucket, not proof that
  the model semantically used the evidence correctly.
- HotpotQA exact match is strict enough that some regressions are mostly span
  formatting while others are real content changes.
- This is still one 50-sample neighboring slice.

## Loose Threads

- See `reports/20260614-pact-offset50-sample58-drift.md` for the sample `58`
  target-slot drift inspection.
- See `reports/20260614-pact-offset50-public-state-gold-cases.md` for the ten
  `final_public_state_contains_gold` hand labels.
- Compare these buckets against the first-50 PACT case families.
