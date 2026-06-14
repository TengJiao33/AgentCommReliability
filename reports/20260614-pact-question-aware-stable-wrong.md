# PACT Question-Aware Stable-Wrong Audit

## What We Tried

After the question-aware extraction probe reached diagnostic `38/50`, I
classified the `12` remaining stable-wrong cases by joining the question-aware
cases with the earlier extraction and evidence-field audits.

No model call or GPU run was launched.

## What Happened

The remaining `12` cases split as:

| Category | Count |
| --- | ---: |
| final event has a matching candidate, but question-aware policy missed it | 7 |
| matching candidate appears only in earlier/wider public state | 2 |
| strict environment signal exists, but simple candidate extraction missed it | 2 |
| semantic polarity or predicate failure | 1 |

The earlier `output_signal_not_recovered` category is gone. In other words,
after question-aware extraction, the remaining failures are mostly not cases
where the answer-bearing surface is absent. They are cases where the extractor
or policy does not choose the right public-state field, or where the saved public
state itself is semantically wrong.

## Things Noticed

The remaining set is small enough to guide the next contact point:

- `7` final-event candidate cases suggest public-state field selection matters,
  not just final-answer text.
- `2` earlier-public-state cases suggest useful evidence can disappear or be
  superseded by the final turn.
- `2` environment-signal cases suggest the candidate extractor is still too
  weak for some answer forms.
- `1` polarity/predicate case is the clearest non-parser failure.

This keeps pushing away from broad scaling. The next useful work is either a
manual pass over these `12` cases or a tiny controlled rerun with a stricter
answer contract, not a larger HotpotQA slice.

## Caveats

- Candidate availability is evaluated against gold labels.
- This is a diagnostic over one 50-sample Qwen2.5-14B PACT smoke.
- The categories are evidence for what to inspect next, not method claims.
