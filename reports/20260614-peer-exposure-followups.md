# Peer Exposure Follow-Up Notes

## What We Tried

We extended the peer-exposure probe from the first DAR GSM8K mini-run into four
small follow-up contacts:

- `experiments/20260614-2105-a8002-peer-exposure-natural-warning/`
  - same six DAR GSM8K disagreement cases as v2: `20`, `78`, `4`, `8`, `37`, `65`
  - no explicit anti-conformity warning
  - `42` records over seven peer-exposure conditions
- `experiments/20260614-2106-a8002-peer-exposure-surface-dissect/`
  - three DAR cases with hand-written surface variants: `8`, `37`, `78`
  - answer-only, correct relation-only, wrong answer plus wrong relation, plausible irrelevant note, and full rationale
  - `21` records
- `experiments/20260614-2107-a8002-peer-exposure-terminal-state/`
  - same six DAR cases
  - terminal response mode with `COMMIT`, `DISAGREE`, `NEEDS_EVIDENCE`, or `ABORT`
  - `42` records
- `experiments/20260614-2108-a8002-peer-exposure-madmm-math-contact/`
  - four MAD-MM MATH disagreement cases from the unified trace: `1`, `9`, `10`, `22`
  - answer-only and rationale exposure only
  - `20` records

All four runs used Qwen2.5-7B-Instruct through a temporary A800_2 vLLM service
on GPU `1`, port `8024`. The service was stopped after the runs and GPU `1`
returned to idle.

## What Happened

In the natural-warning DAR rerun, the no-peer regenerated baseline was again
`4/6` correct. Correct full-rationale exposure reached `6/6`, rescuing cases
`20` (`12 -> 7`) and `8` (`21 -> 24`). Correct answer-only stayed at `4/6`.
Wrong answer-only and wrong-majority stayed at `4/6`; authority-labeled wrong
exposure dropped to `3/6` by flipping case `37` from `11` to `12`.

In the surface dissection, correct relation-only reached `3/3` and rescued case
`8` from `14` to `24` without giving the final answer. Correct full-rationale
also reached `3/3`. Correct answer-only stayed at `2/3`. Wrong answer-only
dropped to `1/3` by flipping case `37`. Wrong answer plus wrong relation dropped
to `0/3`, flipping cases `37` and `78`. A plausible but irrelevant note did not
create new flips and stayed at `2/3`.

In the terminal-state run, no-peer produced `COMMIT` on all six cases and was
`4/6` correct. Wrong answer-only, wrong-majority, and authority-wrong produced
`DISAGREE` on all six cases, usually with `Answer: NONE`; these are disagreement
or abstention events, not wrong-answer adoption events. Correct answer-only and
correct-rationale committed on the stable-right cases but still produced
`DISAGREE` with no final answer on the two initially wrong cases, so they did
not rescue cases `20` or `8` under this terminal contract.

In the MAD-MM MATH contact, no-peer was `3/4` correct with one unparseable
case (`494`, case index `9`). Correct full-rationale exposure reached `4/4` by
recovering that trigonometric minimum case to `8`. Correct answer-only stayed at
`3/4`; wrong answer-only also stayed at `3/4`; wrong-rationale stayed at `3/4`
but moved case `9` toward the wrong answer `2`.

## Things Noticed

The strongest small signal is not "models copy peer answers." Answer-only effects
are inconsistent across prompts and cases. The more durable-looking handle is
whether the peer message supplies a usable relation or mechanism.

Case `8` is the cleanest positive example: a correct relation-only message
rescued the answer without giving the number. Case `37` and case `78` are the
cleanest negative examples: a wrong answer becomes much more harmful when paired
with the wrong relation, while a plausible irrelevant note is mostly ignored.

The terminal-state probe turns wrong social pressure into `DISAGREE` rather than
wrong adoption, but it also blocks useful correction when the model notices a
conflict and refuses to commit. Its accuracy column is therefore a poor summary;
the useful object is the decision distribution and the missing final-answer
contract.

The MAD-MM MATH contact is a small cross-task collision with the DAR surface
signal: full rationale can rescue a case that answer-only cannot, and wrong
rationale can steer toward a wrong answer.

## Failures / Friction

Local copies of the original DAR and MATH input traces were incomplete, so the
dry-run validation and formal runs used A800_2 paths directly. The MATH source
used the remote unified trace at
`/data/xuhaoming/yfy/research_workspace/results/unified-traces/`.

The first formal command batch omitted `--base-url` and `--model`; dry-runs did
not catch that because they do not require a model endpoint.

Terminal-state outputs are parsed correctly as fields, but summary accuracy
counts `DISAGREE` with `Answer: NONE` as unknown/unparseable. That is fine as a
mechanical record, but it should not be read as a method score.

## Loose Threads

The next contact should probably not be another named method yet. Better loose
probes:

- repeat relation-only and wrong-relation exposure on a larger random set of
  disagreement cases;
- replace hand-written relation notes with an automatic short-evidence or
  relation extractor, then inspect the failures;
- split terminal-state evaluation from answer accuracy: does the model identify
  conflict, does it ask for evidence, and can a second step resolve the conflict;
- try the same exposure surfaces on MATH and MMLU-Pro disagreement cases before
  treating GSM8K as representative.

## Caveats

These are small, selected cases with regenerated no-peer baselines. Prompt
surface clearly matters. The run is useful because it makes peer exposure,
relation content, and terminal-state behavior inspectable; it is not yet a rate
estimate or a method claim.
