# Retained Message Role Audit

## What We Tried

Hand-labeled a small set of retained and dropped messages after the MAD-MM MATH50 probe and DAR GSM8K100 full-history trace.

The goal was not to estimate rates. The goal was to see what retained messages are doing: carrying correct answers, useful scaffolds, malformed answers, wrong majorities, or format failures.

Sources:

| Source | Path |
| --- | --- |
| MAD-MM MATH50 run note | `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/README.md` |
| MAD-MM MATH50 trace | `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/comm_trace_madmm_math50.jsonl` |
| MAD-MM debate logs | `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/*_debate_log.json` |
| DAR full-history trace | `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar.jsonl` |
| DAR full-history raw log | `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/dar_history_gsm8k100_filtercritical.jsonl` |

## Labels

| Label | Meaning |
| --- | --- |
| `correct_answer` | Parsed answer is correct and the message gives enough support to reuse it. |
| `useful_scaffold` | Parsed answer is wrong, missing, or incomplete, but the reasoning contains a reusable setup or key step. |
| `wrong_answer` | Answer and main reasoning path point to the wrong result. |
| `format_or_parse_failure` | Reasoning may be mathematically usable, but the answer format makes the evaluator/parser lose it. |
| `harmful_majority` | Multiple retained messages reinforce a wrong answer or wrong final formatting. |
| `zero_retention_reset` | The mask keeps no first-round messages, so the next round is effectively a fresh solve. |

## Case Labels

| System | Case | Method | Retained Message Roles | Dropped Message Roles | Outcome | What It Shows |
| --- | --- | --- | --- | --- | --- | --- |
| MAD-MM | `494` | objective | Agent2: `correct_answer` | Agent1: `wrong_answer` (`2`); Agent3: `wrong_answer` (`4`) | final correct `8` | Clean retention win: the mask kept the only correct answer and removed wrong alternatives. |
| MAD-MM | `1237` | objective | Agent3: `useful_scaffold` with wrong/incomplete parsed answer | Agent1: similar `useful_scaffold`; Agent2: partial scaffold with wrong answer | final correct `8` | Correctness of the retained answer is not the whole story; a scaffold can be enough for round 2 to finish. |
| MAD-MM | `2965` | objective | Agent1: `useful_scaffold` plus incomplete parsed answer | Agent2/Agent3: `correct_answer` (`10`) | final correct `10` | Dropping correct answers did not hurt here because the retained equation setup was sufficient, but it is still a mechanism warning. |
| MAD-MM | `570` | subjective | Agent1: `wrong_answer` (`288`); Agent2: `wrong_answer` (`8`) | Agent3: `correct_answer` (`1152`) | final wrong `288` | Direct dropped-correct-minority failure under subjective masking. |
| MAD-MM | `843` | subjective | none: `zero_retention_reset` | Agent3: `correct_answer` (`144`); Agent1/Agent2: useful but wrong parsed answer (`288`) | official final correct `144` | Zero retention can behave like a fresh solve; not every empty mask is harmful, but it loses communication as an intervention. |
| MAD-MM | `1237` | subjective | none: `zero_retention_reset` | all first-round messages were wrong or incomplete scaffolds | final correct `8` | Empty memory can help when all visible memories are weak; this is closer to reset than filtering. |
| MAD-MM | `494` | subjective | Agent1: `wrong_answer`; Agent2: `correct_answer`; Agent3: `wrong_answer` | none | final wrong `2` | Full retention can let long wrong reasoning overpower a correct minority, behaving like costly naive debate. |
| DAR | `5` | `filter_critical` | Agent1/Agent2: `correct_answer` (`5`) | Agent3: `format_or_parse_failure` / incomplete | round 1 wrong or unparseable | Not a selection failure; later continuation or parser behavior can destroy a correct retained state. |
| DAR | `20` | `filter_critical` | Agent2: `wrong_answer` (`120`); Agent3: `format_or_parse_failure` (`700` from `7.00`) | Agent1: `correct_answer` (`7`) | final wrong `700` | Bad retention plus malformed numeric formatting propagates a wrong majority. |
| DAR | `22` | `filter_critical` | Agent1: mathematically right but `format_or_parse_failure` | Agent2/Agent3: parseable `correct_answer` (`131250`) | final unparseable | The filter selected the least parser-compatible correct reasoning and dropped two parseable correct answers. |
| DAR | `37` | `filter_critical` | Agent2: `correct_answer` (`11`); Agent3: `wrong_answer` (`1`) | Agent1: `wrong_answer` (`12`) | final correct `11` | Mixed retention can rescue a wrong majority if a parseable correct dissenting answer stays visible. |

## Things Noticed

Answer correctness alone is too coarse. The cases separate into at least four surfaces:

- answer surface: whether a visible answer is numerically right;
- scaffold surface: whether the reasoning contains the right equation or key transformation;
- parse surface: whether the final answer can be extracted reliably;
- social surface: whether wrong retained messages form a local majority or dominate the next prompt.

The parser surface matters more than expected. DAR cases `20` and `22` are not just wrong math. In `20`, an agent writes the right dollar amount as `7.00`, but the extracted answer becomes `700`. In `22`, the retained response contains the right computation but not in the accepted final-answer form, while two parseable correct responses are dropped.

The empty-mask cases are ambiguous. MAD-MM subjective cases `843` and `1237` both end correct after retaining nothing. That is useful evidence against "always retain something," but it also means subjective masking sometimes stops being a communication method and becomes a fresh re-solve.

## Candidate Baseline

The smallest next variant worth trying is a guarded retention rule, not another broad judge prompt.

Candidate rule:

1. Group first-round messages by normalized parsed answer, including an `unparseable` bucket.
2. Preserve answer diversity before confidence: keep at least one parseable message from each distinct answer bucket up to a small cap.
3. Penalize `unparseable` messages unless they are the only messages with unique reasoning, and never keep only unparseable messages when parseable alternatives exist.
4. If a learned or LLM filter returns an empty set, treat that as an explicit `reset` mode and record it separately from filtered communication.

This rule would have avoided the visible failures in MAD-MM `570`, DAR `20`, and DAR `22` by keeping parseable dissenting answers. It would not automatically solve MAD-MM `494`, where the correct answer was retained but still lost to wrong reasoning; that case may need answer-only summaries or a verifier rather than more memory.

## Caveats

- This is hand-labeling on selected cases, not a frequency estimate.
- Some labels use the project trace parser, and the parser differs from MAD-MM official MATH evaluation on a few samples.
- The candidate rule uses parseability and answer diversity, not oracle correctness.

## Loose Threads

- Try the guarded retention rule first as a post-filter wrapper on existing traces, before launching a model run.
- For MAD-MM `494`, compare full-reasoning retention against answer-only retention to see whether the wrong long reasoning is the contaminating surface.
- For DAR `20` and `22`, add a parser-compatibility guard before `filter_critical` output is accepted.
