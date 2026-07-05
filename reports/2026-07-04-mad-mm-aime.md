# MAD-M2 AIME 复现诊断

## Decision

当前 7B AIME 复现没有给出继续扩大 MAD-M2 的正向信号。subjective memory masking 在 AIME24/25 上与 same-run naive MAD 正确数相同，objective memory masking 在 AIME24 降低正确数、在 AIME25 持平；后续若继续压这个方向，优先改成更强过滤设置或换更能分辨机制的任务。

## Question

- Original question: MAD-M2 的 memory masking 是否能在 harder AIME setting 上相对同 runner 的 naive MAD 提升。
- Expected decision boundary: 在同模型、同 prompt、同温度、同 agent/round 配置下，subjective 或 objective 的 final accuracy 高于 naive，且没有 parser/gold 异常。

## Scope

- Task: AIME24 train + AIME25 test.
- Compared methods: MAD-M2 `naive`, `subjective`, `objective`.
- Model: Qwen2.5-7B-Instruct.
- Sample size: 60 total questions, 30 + 30.
- Evidence level: diagnostic full split for AIME24/25, single model and single seed.

## Sources

| Source | Type | Path / Link |
| --- | --- | --- |
| Multi-Agent Debate with Memory Masking | Paper | https://arxiv.org/abs/2603.20215 |
| MAD-MM upstream code | Repository | https://github.com/HongduanTian/MAD-MM |
| Local source note | Method note | `baselines/mad-mm/source.md` |
| Run record | Experiment | `experiments/20260704-a8002-aime24-25-mad-mm-qwen25-7b-full/README.md` |

## Results

| Method | Model | Task | Samples | Correct | Accuracy | Status |
| --- | --- | --- | ---: | ---: | ---: | --- |
| naive | Qwen2.5-7B-Instruct | AIME24 train + AIME25 test | 60 | 5 | 0.0833 | completed |
| subjective | Qwen2.5-7B-Instruct | AIME24 train + AIME25 test | 60 | 5 | 0.0833 | completed |
| objective | Qwen2.5-7B-Instruct | AIME24 train + AIME25 test | 60 | 4 | 0.0667 | completed |

## Observations

- Parser health was clean: final parse fail rate was 0 for all six method/dataset jobs.
- Subjective masking barely filtered memory: it retained 176/180 memories overall. Its label counts were yes 163, not sure 13, no 4.
- Objective masking retained 60/180 memories overall and sharply reduced majority ties: combined tie rate fell from 0.3167 for naive to 0.0333 for objective.
- The lower tie rate did not translate into higher accuracy in this run.
- Two failed launches happened before claim-bearing output: one split-path mistake and one local runner field-name bug. Both are recorded in the run README.

## Interpretation

The main signal is that this faithful small reproduction path runs end to end, but the AIME result does not support scaling this exact setting as a promising method claim. Subjective masking behaved too permissively under the non-strict setting, so it mostly reproduced naive MAD with small tie-rate changes. Objective masking applied a much stronger filter, but the retained single memory per row was not reliably better for final correctness.

## Next Action

Use this run as the local MAD-M2 integration baseline. If we continue, the sharpest next test is either strict subjective masking on the same AIME packet or a MATH500 run with a stronger evaluator, rather than immediately expanding the same permissive subjective setting to more models.
