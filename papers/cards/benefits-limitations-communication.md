# Benefits and Limitations of Communication in Multi-Agent Reasoning

## Link

- paper: https://arxiv.org/abs/2510.13903
- code: https://github.com/michaelrizvi/coa-algorithmic
- local pdf: pending

## One-Sentence Claim

Communication in multi-agent reasoning has task-dependent benefits and limits; the right amount and structure of communication depends on whether a task behaves like recall, state tracking, or k-hop reasoning.

## Problem

Many applied multi-agent papers treat communication as a generic improvement mechanism. This paper asks a more structural question: when does splitting work across agents and exchanging messages actually reduce depth, extend context, or hit an unavoidable communication bottleneck?

## Method

The paper formalizes multi-agent systems as communication graphs and analyzes resource tradeoffs over controlled algorithmic task families. It derives bounds for:

- number of agents;
- communication budget;
- computation depth;
- speedup as context and problem size scale.

The empirical side implements controlled synthetic benchmarks that correspond to the theoretical regimes.

## Communication Variables

| Variable | Value / Design | Notes |
| --- | --- | --- |
| agents | variable | agents process input chunks or communicate with a manager |
| rounds | protocol-dependent | depth is treated as a core cost |
| topology | graph/protocol based | includes worker-manager and chain-like communication structures |
| message content | task-specific tokens/intermediate values | not free-form debate as in MAD |
| memory/context | each agent receives an input partition plus received messages | strong fit to long-context and shard-based tasks |
| routing | protocol-defined | communication structure depends on task family |
| confidence/evidence | not the main axis | the paper focuses on structural communication needs |
| judge/verifier | manager/final output role | not primarily a judge-prompt paper |
| stopping rule | task/protocol bounded | analyzed through depth and communication budget |

## Baselines

- Single-agent CoT or majority-vote style baselines.
- Chain-of-Agent style protocols for long-context processing.
- Task-specific optimal or near-optimal protocols from the theory.

## Datasets / Tasks

The paper's core task families:

- associative recall;
- state tracking, including parity and permutation-style tracking;
- k-hop reasoning.

These are controlled synthetic or algorithmic tasks, not standard natural-language QA only.

## Reported Results

| Setting | Metric | Reported Result | Compared To |
| --- | ---: | --- | --- |
| Theory | communication/depth bounds | different task families fall into different communication regimes | generic multi-agent assumptions |
| Experiments | accuracy and token/resource curves | empirical outcomes align with predicted tradeoffs | majority vote / CoA-style baselines |

## Code And Reproducibility

- repo: https://github.com/michaelrizvi/coa-algorithmic
- commit inspected: not cloned yet; GitHub page observed
- license: repository has a `LICENSE` file, exact license not inspected locally
- install difficulty: moderate if using Together API and W&B; likely easier to inspect than to fully reproduce
- smallest runnable command: pending code clone; visible scripts include `run_khop.py`, `run_parity.py`, and `run_permutations.py`
- expected resource: API-backed LLM calls by default; CPU-only task generation may be possible after code inspection

## Implementation Details Worth Inspecting

- prompt templates: `chain_of_agents/*`, especially task runner prompts;
- message construction: worker-manager messages and task-specific communication;
- filtering or merging: not the main mechanism;
- judge or verifier path: manager/final answer extraction;
- evaluation script: `run_khop.py`, `run_parity.py`, `run_permutations.py`, Pareto scripts;
- hidden defaults: Together API model, W&B logging, task sizes, chunking.

## Possible Ablations

- Recreate a tiny local synthetic task without API to validate task-regime labels.
- Use the task taxonomy to label our current benchmarks: GSM8K, MATH, MMLU-Pro, AIME, HotpotQA.
- Add `task_regime` and `evidence_locality` fields to the unified trace schema before more model runs.

## Caveats

- This is more theory/control-task oriented than our current baseline code.
- It may not directly reproduce MAD-MM/DAR/PACT behavior.
- The value is likely in the taxonomy and variables, not immediate leaderboard numbers.

## Project Fit

| Question | Answer |
| --- | --- |
| Which project axis does it touch? | task regime, communication necessity, bandwidth/depth tradeoff |
| What would we learn by reproducing it? | when communication should be expected to help, hurt, or merely cost tokens |
| What is the cheapest useful check? | code-read the task generators and map their regimes onto our existing benchmark choices |
| Should it be promoted to experiment? | yes, but first as a harness/taxonomy source rather than a GPU run |

## Open Questions

- Can our existing benchmarks be decomposed into recall, state-tracking, k-hop, and conflict-evidence slices?
- Should the unified trace schema record task-regime labels before another model run?
- Is a small synthetic regime harness more useful than another paper-specific reproduction right now?

