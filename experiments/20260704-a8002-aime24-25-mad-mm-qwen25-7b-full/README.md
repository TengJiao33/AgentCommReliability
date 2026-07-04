# 20260704-a8002-aime24-25-mad-mm-qwen25-7b-full

## What We Tried

Prepared a full AIME24/AIME25 reproduction slice for MAD-M2 with Qwen2.5-7B-Instruct, comparing upstream-style naive MAD, subjective memory masking, and objective memory masking under the same runner.

## Scope

- Method: MAD-M2 memory masking (`naive`, `subjective`, `objective`).
- Model: Qwen2.5-7B-Instruct.
- Dataset: AIME24 test and AIME25 test.
- Seed: 42.
- Samples: all rows in both splits, 30 + 30.
- Comparison target: same-run naive MAD, plus earlier local AIME basic MAD and CoT-SC runs as contextual references.

## Preflight Contract

- Purpose: test whether upstream-style memory masking improves over same-run naive MAD on the harder AIME setting.
- Unit: benchmark row/question.
- Primary contrast: `subjective` and `objective` final accuracy versus `naive` final accuracy with the same model, prompts, temperature, seed, agent count, and round count.
- Secondary contrasts: initial-round majority accuracy, final tie rate, memory retention rate, subjective label distribution.
- Success signal: either masking strategy improves final accuracy on the combined 60 AIME questions without obvious parser failure.
- Failure signal: masking matches or trails naive MAD, or gains are explained by parser/gold issues.
- Invalidation conditions: missing rows, wrong gold labels, broken XML/answer parsing, model path mismatch, output truncation, GPU interruption, or accidental non-full `--limit`.
- Expected artifacts: this README, `run_remote.sh`, per-method `summary.json`, `summary.md`, and `records.jsonl` under this experiment directory.

## Resource Notes

- Machine: A800_2.
- Remote work dir: `/data/xuhaoming/yfy/research_workspace`.
- GPU IDs: planned GPU 7 if free.
- Timeout: 12h launcher timeout.
- Expected duration: several hours for all six method/dataset jobs.
- Started by: Codex.

## Code

- Upstream repo: https://github.com/HongduanTian/MAD-MM
- Upstream commit inspected: `f02069a`.
- Local script: `scripts/run_mad_mm.py`.
- Local changes: new local runner and source note.

## Environment

- Env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`.
- Python: to be recorded after launch.
- vLLM: expected 0.6.3.
- PyTorch: to be recorded after launch.
- Transformers: to be recorded after launch.

## Data

- Data paths:
  - `/data/xuhaoming/yfy/research_workspace/data/benchmarks/aime24/train/canonical.jsonl`
  - `/data/xuhaoming/yfy/research_workspace/data/benchmarks/aime25/test/canonical.jsonl`
- Split: AIME24 `train`, AIME25 `test`.
- Sampling: full split, no `--limit`.

## Command

```bash
bash experiments/20260704-a8002-aime24-25-mad-mm-qwen25-7b-full/run_remote.sh
```

## Remote Artifacts

- Main log: `experiments/20260704-a8002-aime24-25-mad-mm-qwen25-7b-full/launcher.out.log`
- Error log: `experiments/20260704-a8002-aime24-25-mad-mm-qwen25-7b-full/launcher.err.log`
- Results: `experiments/20260704-a8002-aime24-25-mad-mm-qwen25-7b-full/*/summary.json`
- Traces: `experiments/20260704-a8002-aime24-25-mad-mm-qwen25-7b-full/*/records.jsonl`

## What Happened

- Status: PREPARED.
- Accuracy: pending.
- Memory retention: pending.
- Evaluation time: pending.
- Wall time: pending.

## Status Timeline

- `2026-07-04`: prepared.
- `2026-07-04 16:45 CST`: first launcher failed before generation because it looked for `aime24/test/canonical.jsonl`; no result was produced.
- `2026-07-04 16:53 CST`: second launcher failed before writing result summaries because the local runner referenced `context["parsed"]` before storing that field; no claim-bearing result was produced.

## Caveats

- This run follows the upstream code behavior for objective masking rather than only the paper prose description.
- AIME has only 60 total questions across the two sets, so differences should be treated as diagnostic until replicated or expanded.
- The local numeric evaluator is appropriate for AIME integer answers but is not a full symbolic MATH evaluator.

## Loose Threads

- If 7B shows a real signal, extend to Qwen2.5-14B-Instruct or the upstream math-specialized model if available.
