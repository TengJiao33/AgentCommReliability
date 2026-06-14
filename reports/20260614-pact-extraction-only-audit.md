# PACT Extraction-Only Audit

## What We Tried

After fixing the PACT trace to preserve HotpotQA gold answers as text, I ran a
deterministic extraction-only audit over saved PACT action-state outputs. The
audit does not generate new model outputs. It asks whether a parser operating
on the existing public fields could recover concise HotpotQA answers.

No model call or GPU run was launched.

## What Happened

Official EM remains `17/50`.

A fixed final-answer-only extraction policy reaches `32/50`:

| Transition under fixed extraction policy | Count |
| --- | ---: |
| official correct stays correct | 17 |
| official wrong becomes correct | 15 |
| official wrong stays wrong | 18 |
| official correct becomes wrong | 0 |

The candidate upper bounds are larger:

| Candidate scope | Upper-bound exact matches | Wrong cases with matching candidate |
| --- | ---: | ---: |
| final event fields only | 39/50 | 22/33 |
| all public action-state fields | 41/50 | 24/33 |

These are diagnostics, not replacement scores. The policy candidates are
generated without gold labels, but the upper-bound rows use gold to check
whether any candidate happened to match.

## Things Noticed

The largest easy recoveries come from answer-contract surfaces:

- yes/no final answers that start with the correct polarity but continue as a
  sentence;
- entity answers where the final answer starts with the gold span and then
  explains;
- simple numeric answers where the final answer contains one number.

The field-level upper bound is higher than the fixed policy because some cases
need `Environment State` or earlier public-state fields, not just the final
answer. That means answer extraction can help, but it does not fully replace
public-state selection and evidence-use analysis.

## Loose Threads

- Treat PACT HotpotQA50 EM as confounded until the answer contract is controlled.
- If a tiny rerun is justified later, change the final-answer instruction or
  parser contract first, before changing the communication method.
- See `reports/20260614-pact-stable-wrong-after-extraction.md` for the
  completed follow-up on the remaining `stable_wrong` cases.

## Caveats

- This audit is postprocessing over a 50-sample smoke.
- The fixed extraction policy is heuristic and task-shaped.
- Candidate upper bounds are not deployable scores.
