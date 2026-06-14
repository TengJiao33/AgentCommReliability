# MAD-MM And DAR Trace Case Follow-Up

## Short Answer

This follow-up inspects a few concrete trace cases after the MAD-MM MATH50 probe and the DAR GSM8K100 full-history run.

The cases are useful because the same aggregate label can hide different mechanisms. MAD-MM objective masking fixed two MATH cases that naive MAD missed, but one fix came from retaining the only correct first-round answer while another came from retaining an incomplete or wrong-looking scaffold that the next round corrected. DAR `filter_critical` produced three GSM8K right-to-wrong cases, but they are not all simple "dropped correct evidence" failures.

No new GPU run was launched for this note.

## Sources

| Source | Path |
| --- | --- |
| MAD-MM MATH50 run note | `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/README.md` |
| MAD-MM MATH50 trace | `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/comm_trace_madmm_math50.jsonl` |
| MAD-MM debate logs | `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/*_debate_log.json` |
| DAR full-history run note | `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/README.md` |
| DAR full-history trace | `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar.jsonl` |
| DAR full-history raw history | `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/dar_history_gsm8k100_filtercritical.jsonl` |

## What We Checked

MAD-MM cases:

- `494` and `1237`, where objective masking fixed errors that naive MAD did not.
- `2965`, where objective masking dropped all correct first-round agents but still ended correct.

DAR cases:

- `5`, `20`, and `22`, the three `right_to_wrong` cases in the GSM8K100 full-history run.
- `37`, the single `wrong_to_right` case, as a contrast.

## MAD-MM MATH50 Cases

| Case | Gold | CoT | Naive MAD | Objective MAD-MM | Objective Retention | What It Shows |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `494` | 8 | 2 | 4 | 8 | kept `Agent2`, dropped `Agent1` and `Agent3` | clean useful retention: the kept memory was the only correct first-round answer. |
| `1237` | 8 | 34 | 34 | 8 | kept `Agent3`, dropped `Agent1` and `Agent2` | useful but less clean: retained answer was wrong, but retained reasoning scaffold let round 2 recompute `sqrt(1296)=36`, then `sqrt(64)=8`. |
| `2965` | 10 | 0 | 10 | 10 | kept `Agent1`, dropped two correct agents | mechanism warning: the retained answer was not parsed as correct, but the retained partial setup was enough for round 2 to solve. |

Details:

- In `494`, first-round answers were `[2, 8, 4]`. Naive debate ended `[4, 4, 8]`, so full memory did not preserve the correct minority. Objective masking kept the highest-likelihood correct answer and all round-2 agents ended at `8`.
- In `1237`, first-round answers were `sqrt(34)`, `5`, and `sqrt(34)`. Objective masking kept `Agent3`, whose answer was wrong, but whose reasoning began with the right operation: simplify the inner square root first. In round 2, all agents completed that computation and answered `8`.
- In `2965`, objective masking retained an incomplete setup and dropped two correct first-round answers. Round 2 still finished the factorization and returned `10`. This is not a final failure, but it weakens the simple interpretation that objective masking only works by preserving correct answers.

## DAR GSM8K100 Cases

| Case | Transition | Gold | Round 0 Agent Answers | Retained IDs | Round 1 Agent Answers | What It Shows |
| ---: | --- | ---: | --- | --- | --- | --- |
| 5 | right-to-wrong | 5 | `[5, 5, empty]` | `Agent1`, `Agent2` | `[empty, empty, 3]` | retained correct agents, but the next round produced unparseable or wrong final answers. |
| 20 | right-to-wrong | 7 | `[7, 120, 700]` | `Agent2`, `Agent3` | `[7, 700, 700]` | direct wrong-retention case: correct `Agent1` was dropped, wrong `700` propagated. |
| 22 | right-to-wrong | 131250 | `[empty, 131250, 131250]` | `Agent1` | `[empty, empty, empty]` | direct bad retention: two correct agents were dropped and the retained invalid answer led to no parsed final answer. |
| 37 | wrong-to-right | 11 | `[12, 11, 1]` | `Agent2`, `Agent3` | `[11, 1, 11]` | mixed retention can help when one retained agent has the correct answer and the later round moves another agent toward it. |

Details:

- Case `20` is the cleanest DAR failure: `filter_critical` retained two wrong dissenting answers and dropped the only correct first-round answer.
- Case `22` is also a clear retention failure: the filter retained the only invalid first-round answer and dropped both correct answers.
- Case `5` is stranger. The filter retained two correct first-round agents, and its raw filter response described all agents as effectively agreeing on `5`. The final debate still moved to an incorrect or unparseable state. This suggests that a retention trace alone is not enough; parser behavior and second-round response formatting can also turn a correct state into a wrong final record.
- Case `37` is the contrast case: retaining one correct and one wrong message was enough to move the debate answer from wrong `1` to correct `11`.

## Things Noticed

For MAD-MM, a retained memory can matter as:

- a correct answer to imitate;
- a partial reasoning scaffold to complete;
- an incomplete setup that still anchors the next round.

For DAR, a bad final transition can come from at least two surfaces:

- selection surface: the filter keeps wrong or invalid messages and drops correct messages;
- continuation/evaluation surface: the filter keeps apparently useful messages, but later agents produce unparseable or wrong final answers.

This makes the next trace schema need feel sharper. We already record retained/dropped IDs and final answer transitions. The next useful annotation is a per-retained-message role such as `correct_answer`, `wrong_answer_but_useful_scaffold`, `invalid_or_unparseable`, or `format_failure_after_retention`. That label does not need to be automated yet; hand labels on a small case set may be enough.

## Caveats

- This is case inspection, not a rate estimate.
- MAD-MM and DAR use different datasets, model sizes in earlier runs, prompts, and retention mechanisms.
- Correctness labels depend on the project extractors. In DAR case `5`, some generated text appears mathematically close to the right path while the parsed final answer is empty, so parser compatibility remains part of the observed behavior.

## Loose Threads

- The same MAD-MM MATH50 slice now has a subjective masking addendum in the run note.
- For DAR, try a less aggressive retention rule or an answer-format guard on the same GSM8K100 setup before scaling.
- Extend `scripts/extract_comm_trace_schema.py` later with optional derived fields for retained/dropped correctness counts in DAR records; the current report computed those manually from round-0 agent correctness.
