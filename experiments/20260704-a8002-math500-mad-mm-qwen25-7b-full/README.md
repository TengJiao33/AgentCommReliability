# 20260704-a8002-math500-mad-mm-qwen25-7b-full

## Purpose

Test whether the local MAD-MM/MAD-M2 reproduction shows a useful signal on MATH-500 after the AIME24/25 run showed no positive accuracy delta for Qwen2.5-7B-Instruct.

## Design

- Task: `math500/test`, full 500 rows.
- Unit: one MATH-500 problem.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- Method: local `scripts/run_mad_mm.py`, 3 agents, 2 total rounds, majority vote.
- Primary contrast: `naive` vs `subjective` vs `objective` memory masking.
- Evaluator: shared answer normalizer in `scripts/run_basic_mad.py`; it tries boxed-answer extraction, SymPy/latex2sympy2 equivalence when available, numeric fallback, then short normalized strings for text answers.

## Machine

- Host: `A800_2`
- Work dir: `/data/xuhaoming/yfy/research_workspace`
- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- GPU: `1`
- Runtime: July 4, 2026, about 19:14-22:36 CST.

## Launch

```bash
WORK=/data/xuhaoming/yfy/research_workspace
RUN_ID=20260704-a8002-math500-mad-mm-qwen25-7b-full
GPU_ID=1 nohup bash "$WORK/experiments/$RUN_ID/run_remote.sh" \
  > "$WORK/experiments/$RUN_ID/launcher.out.log" \
  2> "$WORK/experiments/$RUN_ID/launcher.err.log" &
```

## Expected Outputs

- Remote/local run root: `experiments/20260704-a8002-math500-mad-mm-qwen25-7b-full/`
- Per strategy:
  - `math500-qwen25-7b-instruct-naive/records.jsonl`
  - `math500-qwen25-7b-instruct-naive/summary.json`
  - `math500-qwen25-7b-instruct-subjective/records.jsonl`
  - `math500-qwen25-7b-instruct-subjective/summary.json`
  - `math500-qwen25-7b-instruct-objective/records.jsonl`
  - `math500-qwen25-7b-instruct-objective/summary.json`

## Status

`COMPLETED`.

## Validation

- Each strategy produced 500 `records.jsonl` rows.
- Each `summary.json` reports 500 rows.
- Final parse failures: 0 for all three strategies.
- Remote cleanup check after completion: no `run_mad_mm.py` process remained; GPU 1 returned to 4 MiB used and 0% utilization.

## Result

| Strategy | Rows | Initial majority | Final correct | Final acc. | Delta vs initial | Tie rate | Memory retention | Elapsed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `naive` | 500 | 310 | 320 | 0.640 | +0.020 | 0.038 | 1.000 | 4018.8s |
| `subjective` | 500 | 310 | 315 | 0.630 | +0.010 | 0.028 | 0.987 | 4100.0s |
| `objective` | 500 | 310 | 303 | 0.606 | -0.014 | 0.002 | 0.333 | 3940.1s |

Subjective label counts:

| Label | Count |
| --- | ---: |
| `yes` | 1224 |
| `not sure` | 257 |
| `no` | 19 |

## Interpretation

The MATH-500 run gives a clearer diagnostic than AIME because the benchmark is larger and the evaluator now handles common boxed LaTeX answers. In this setting, `naive` MAD-MM/MAD-M2 style debate performed best. `subjective` masking retained 1481/1500 memories, so it mostly behaved like `naive` and landed slightly lower. `objective` masking reduced ties almost completely and retained exactly one memory per row, but the strong pruning reduced final accuracy below the initial majority baseline.

This is diagnostic evidence for the local Qwen2.5-7B setting, not a broad claim about MAD-MM. The most useful current conclusion is that permissive subjective masking does not add much filtering pressure on MATH-500, while objective masking is a real intervention but too lossy here.

## Caveats

- MATH-500 contains symbolic, text, tuple, angle, and numeric answers. The evaluator is stronger than the previous AIME-only numeric checker, but it is still a lightweight local evaluator rather than the official MATH verifier.
- Treat small deltas as diagnostic until concrete rows are inspected.
- `naive` and permissive `subjective` memory use can push an A800 80GB card close to its memory ceiling with 24k context and batch size 8.
