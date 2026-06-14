# PACT Stable-Wrong After Extraction

## What We Tried

After the extraction-only audit lifted the fixed final-answer policy to `32/50`,
I inspected the `18` cases that still remain wrong. This is still CPU-only
postprocessing over saved PACT outputs.

No model call or GPU run was launched.

## What Happened

The `18` stable-wrong cases are not a single bucket:

| Category | Count |
| --- | ---: |
| final event has a matching candidate, but fixed final-answer policy missed it | 7 |
| matching candidate appears only in earlier/wider public state | 2 |
| strict environment signal exists, but simple candidate extraction missed it | 3 |
| yes/no polarity mismatch | 1 |
| wrong output signal not recovered by current extractor | 5 |

By task type:

| Type | Count |
| --- | ---: |
| bridge | 13 |
| comparison | 5 |

## Things Noticed

The most important part is negative: even after the extraction-only policy,
`stable_wrong` is still not equal to reasoning failure.

Seven cases already have an exact-match candidate somewhere in the final
action-state event, usually in `Environment State` or `Action Result`, but the
fixed policy only reads the final answer field. Two more have matching
candidates in earlier public-state turns. Three have strict environment signal
that the simple candidate extractor misses.

Only one case is a clean yes/no polarity mismatch. The remaining five are a
mixed surface: the output may contain the gold phrase, but current deterministic
rules cannot extract an exact-match answer.

## Loose Threads

- See `reports/20260614-pact-unrecovered-case-inspection.md` for the completed
  manual inspection of the five unrecovered-output cases and the one polarity
  mismatch.
- A tiny PACT rerun, if later justified, should control the final-answer
  contract before changing communication structure.
- This makes `Environment State` selection a more plausible control point than
  another broad prompt variant.

## Caveats

- This audit is heuristic and postprocessing-only.
- Matching candidates are evaluated with gold labels; they are diagnostics, not
  deployable scores.
- The categories are meant to guide contact with cases, not to define a method.
