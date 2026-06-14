# What Should Agents Say? Action-state Communication for Efficient Multi-Agent Systems

## Link

- paper: https://arxiv.org/abs/2606.05304
- code: https://github.com/iNLP-Lab/PACT
- local pdf: pending

## One-Sentence Claim

Agents can communicate more efficiently by exposing compact action-state records rather than unrestricted reasoning traces.

## Problem

Multi-agent systems often forward too much intermediate reasoning, which can inflate context, leak irrelevant or wrong thoughts, and make it hard to tell whether communication itself is helping.

## Method

PACT asks each agent to send a structured public record with what action/fact is required, what environment evidence grounds it, and what result it contributes. Private reasoning may happen inside the model output, but the shared history passed to the next agent is the think-stripped action-state message.

## Communication Variables

| Variable | Value / Design | Notes |
| --- | --- | --- |
| agents | 2 | Agent A and Agent B |
| rounds | 4 alternating turns by default | A, B, A, B; final turn answers |
| topology | fixed pairwise alternating exchange | no learned routing in the demo |
| message content | `Action Required`, `Environment State`, `Action Result`; final adds `Final Answer` | each field is constrained to one sentence |
| memory/context | shared history contains think-stripped public messages | raw output is not fully forwarded |
| routing | deterministic alternating turns | no retention selection |
| confidence/evidence | evidence sentence included in `Environment State` | useful for trace inspection |
| judge/verifier | none observed in demo code | direct final answer extraction |
| stopping rule | fixed `max_turns` | default 4 |

## Baselines

The public repository currently exposes the PACT demo path. Baseline comparisons must be read from the paper or rebuilt locally if needed.

## Datasets / Tasks

- HotpotQA dev-distractor, split-evidence setting.
- Each sample has 10 paragraphs split 5/5 between two agents; each agent receives 1 supporting paragraph and 4 distractors.

## Reported Results

Pending paper extraction. Do not infer method gains from the project smoke run.

## Code And Reproducibility

- repo: https://github.com/iNLP-Lab/PACT
- commit inspected: `91acf820f8a69fc7c181120b3120444a98823230`
- license: no license file observed
- install difficulty: low if a compatible vLLM environment and model are already available
- smallest runnable command: `bash scripts/run_demo.sh`
- expected resource: one CUDA GPU; upstream says Qwen3-14B fits on a single 40GB+ GPU

## Implementation Details Worth Inspecting

- prompt templates: `prompts.py`
- message construction: `methods/pact.py::PACTMethod.run_batch`
- filtering or merging: `strip_think_tags` before appending to shared history
- judge or verifier path: none in demo code
- evaluation script: `run.py::evaluate`
- hidden defaults: `scripts/run_demo.sh` uses `generate_bs=64`, `max_new_tokens=4096`, `max_samples=50`

## Possible Ablations

- Compare PACT action-state messages with answer-only and full-reasoning retained surfaces.
- Remove or relax the one-sentence public field constraint.
- Use identical HotpotQA samples with a single-agent full-context control.
- Inspect cases where final answers are wrong despite both evidence sentences being present.

## Caveats

- The code is a narrow demo; it may not include all experimental variants from the paper.
- The first project run uses Qwen2.5-7B-Instruct, not Qwen3-14B.

## Project Fit

| Question | Answer |
| --- | --- |
| Which project axis does it touch? | communication surface / intermediate-state exposure |
| What would we learn by reproducing it? | whether structured evidence-bearing messages reduce context load without making downstream agents blind |
| What is the cheapest useful check? | 5-sample HotpotQA smoke plus trace inspection of public message compliance |
| Should it be promoted to experiment? | yes, if the A800_2 smoke produces valid per-turn traces |

## Open Questions

- Does PACT's action-state surface behave differently from DAR answer-only on cases that need a short calculation or evidence sentence?
- How often does the model violate the strict field format under Qwen2.5-7B?
- Is token saving mainly from stripping private reasoning, or from shorter public evidence fields?
