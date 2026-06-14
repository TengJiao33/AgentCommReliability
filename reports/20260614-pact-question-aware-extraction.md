# PACT Question-Aware Extraction Probe

## What We Tried

Using the saved PACT HotpotQA50 trace, I tested a question-aware deterministic
extractor. It uses question wording plus saved final action-state fields to pick
spans for answer types such as yes/no, timeframe, seated capacity, voted title,
secured object, and vice-president relation tail.

No model call or GPU run was launched.

## What Happened

The diagnostic count rises again:

| Policy | Exact matches |
| --- | ---: |
| official PACT extraction | 17/50 |
| fixed final-answer-only extraction | 32/50 |
| question-aware extraction | 38/50 |

Compared with the fixed final-answer policy, the question-aware probe adds six
rescues and introduces no regressions.

The rescued/changed cases are:

| Sample | Rule | Output |
| ---: | --- | --- |
| 7 | seated capacity | `3677 seated` |
| 14 | timeframe | `from 1986 to 2013` |
| 21 | hedgehog alias | `Sonic` |
| 24 | voted title | `World's Best Goalkeeper` |
| 43 | secured object | `sovereignty` |
| 44 | under-vice-president tail | `Nelson Rockefeller` |

Sample `18` also changes rule path but keeps the same answer text, `1969 until
1974`, which is useful as a guard against overzealous timeframe extraction.

## Things Noticed

This strengthens the answer-contract diagnosis. A large part of the apparent
PACT HotpotQA failure is recoverable without changing communication behavior or
generating new model outputs.

But the probe also shows why this should remain diagnostic. Sample `21` becomes
exact-match correct by extracting `Sonic` from `Sonic the Hedgehog`, while the
manual inspection showed the public state confuses Sonic with Dr. Robotnik. That
means exact-match recovery can hide evidence-use errors.

## Loose Threads

- Keep sample `21` as a sentinel for parser over-credit.
- A tiny rerun, if later justified, should control answer contract explicitly
  before changing the communication method.
- See `reports/20260614-pact-question-aware-stable-wrong.md` for the completed
  follow-up on the remaining `12` stable-wrong cases.

## Caveats

- This is postprocessing over a 50-sample smoke.
- Rules are HotpotQA-shaped and use question wording.
- Gold is used for evaluation, not candidate generation.
