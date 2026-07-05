# Basic MAD MATH500 full

## Purpose

Run a full MATH-500 basic MAD baseline for Qwen2.5-7B-Instruct so CQG and MAD-MM results have a direct local MAD reference.

## Design

- Task: `math500/test`, full 500 rows.
- Unit: one MATH-500 problem.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- Method: `scripts/run_basic_mad.py`.
- Agents: 3.
- Rounds: 1 revision round after independent initial answers.
- Aggregation: final majority vote over agent answers.
- Direct baseline: same script, same model, direct single-agent CoT-style answer before debate.
- Primary readout: direct accuracy vs basic MAD final majority accuracy.
- Secondary readout: final majority tie rate, parse fail rate, agent-level final accuracy.
- Generation: `max_tokens=2048`, `max_model_len=8192`, direct temperature `0.0`, debate temperature `0.7`, `top_p=0.95`, batch size `16`, seed `7`.

## Machine

- Host: `A800_2`.
- Remote work dir: `/data/xuhaoming/yfy/research_workspace`.
- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`.
- GPU: `7`.

## Launch

See `run_remote.sh`.

## Status

`COMPLETED`.

## Validation

- Remote evaluator smoke in `run_remote.nohup.log` passed for boxed fractions, mixed fractions, tuple/symbolic answers, symbolic strings, and placeholder-answer rejection.
- Output files were pulled back from `A800_2`:
  - `qwen25-7b-instruct/records.jsonl`
  - `qwen25-7b-instruct/summary.json`
  - `qwen25-7b-instruct/summary.md`
- `records.jsonl` contains 500 rows locally and remotely.
- `summary.json` reports 500 rows.
- Direct parse failures: 0/500.
- MAD majority parse failures: 0/500.
- Remote cleanup check after completion: no matching `run_basic_mad.py` / run-id process remained; GPU 7 returned to 4 MiB used and 0% utilization.

## Result

| Readout | Correct | Accuracy | Parse fail | Notes |
| --- | ---: | ---: | ---: | --- |
| Direct | 347/500 | 0.694 | 0 | Same model/script before debate |
| Basic MAD final majority | 333/500 | 0.666 | 0 | 3 agents, 1 revision round |

Additional metrics:

| Metric | Value |
| --- | ---: |
| Agent 1 final accuracy | 0.666 |
| Agent 2 final accuracy | 0.656 |
| Agent 3 final accuracy | 0.658 |
| Majority tie rate | 23/500 = 0.046 |
| Elapsed | 2470.7s |

## Interpretation

This full MATH-500 run does not support the hypothesis that the CQG smoke result was negative only because the smoke set was too small. In this local basic MAD setting, debate reduced accuracy relative to the direct baseline by 14 problems, from 69.4% to 66.6%.

This is still a configuration-specific diagnostic rather than a broad claim about MAD. The basic MAD runner uses a different prompt, number of rounds, temperature, context length, and max-token budget from the MAD-MM run in `experiments/20260704-a8002-math500-mad-mm-qwen25-7b-full/`.

## Execution Notes

The first foreground SSH attempt did not produce result files because the connection closed while vLLM progress output was still active and the runner writes `summary.json` only after all generations finish. `scripts/run_basic_mad.py` was updated with `--disable-tqdm`, and the successful run used `nohup` plus `run_remote.nohup.log`.
