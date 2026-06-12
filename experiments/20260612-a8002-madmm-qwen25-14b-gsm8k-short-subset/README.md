# 20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset

## Goal

Bounded short subset for MAD-MM reproduction after the full standard matrix was stopped for shared-GPU courtesy.

This subset keeps the important comparison surface without occupying multiple GPUs for days.

## Scope

- Model: `qwen2.5-14b`
- Dataset: `gsm8k`
- Seed: `41`
- Samples: upstream default `100`
- GPU budget: one A800 only
- Suggested wall-time cap: `60m`

## Methods

- CoT baseline
- CoT self-consistency baseline, 6 paths
- MAD naive communication
- MAD-MM subjective masking
- MAD-MM objective masking

## Remote Launcher

```text
/data/xuhaoming/yfy/research_workspace/scripts/run_madmm_short_subset_a8002.sh
```

Suggested launch command:

```bash
ssh A800_2 'tmux new-session -d -s madmm_short_subset "timeout 60m /data/xuhaoming/yfy/research_workspace/scripts/run_madmm_short_subset_a8002.sh"'
```

Optional GPU override:

```bash
MAD_MM_GPU_ID=7 timeout 60m /data/xuhaoming/yfy/research_workspace/scripts/run_madmm_short_subset_a8002.sh
```

## Status

- Short subset launcher prepared and synced to A800_2.
- First step complete: CoT baseline.
  - Launch method: `nohup env MAD_MM_GPU_ID=6 timeout 25m ...`.
  - PID: `861717`.
  - GPU: `6`.
  - Log: `/data/xuhaoming/yfy/research_workspace/logs/madmm_short_cot_20260612_145518.log`.
  - Result:
    - Accuracy: `0.94`
    - Total tokens: `37990`
    - Evaluation time: `16.21s`
    - Wall time including model load: about `2m 08s`
    - Output: `/data/xuhaoming/yfy/research_workspace/results/mad-mm-short-subset/main/qwen2.5-14b/gsm8k/cot_seed41.json`
- Second step complete: MAD naive communication.
  - Launch method: `nohup env MAD_MM_GPU_ID=6 timeout 30m ...`.
  - PID: `919697`.
  - GPU: `6`.
  - Log: `/data/xuhaoming/yfy/research_workspace/logs/madmm_short_mad_naive_20260612_151044.log`.
  - Result:
    - Accuracy: `0.96`
    - Total tokens: `441846`
    - Evaluation time: `120.66s`
    - Wall time including model load: about `3m 54s`
    - Output: `/data/xuhaoming/yfy/research_workspace/results/mad-mm-short-subset/main/qwen2.5-14b/gsm8k/mad_3agents_2rounds_seed41.json`
- Third step complete: MAD-MM objective masking.
  - Launch method: `nohup env MAD_MM_GPU_ID=7 timeout 35m ...`.
  - PID: `1130231`.
  - GPU: `7`.
  - Log: `/data/xuhaoming/yfy/research_workspace/logs/madmm_short_mad_objective_20260612_161144.log`.
  - Result:
    - Accuracy: `0.95`
    - Total tokens: `304287`
    - Evaluation time: `117.51s`
    - Wall time including model load: about `3m 59s`
    - Output: `/data/xuhaoming/yfy/research_workspace/results/mad-mm-short-subset/main/qwen2.5-14b/gsm8k/mad_objective_3agents_2rounds_seed41.json`
- Fourth step complete: MAD-MM subjective masking.
  - Launch method: `nohup env MAD_MM_GPU_ID=7 timeout 40m ...`.
  - PID: `1159232`.
  - GPU: `7`.
  - Log: `/data/xuhaoming/yfy/research_workspace/logs/madmm_short_mad_subjective_20260612_161732.log`.
  - Result:
    - Accuracy: `0.96`
    - Total tokens: `600499`
    - Evaluation time: `547.44s`
    - Wall time including model load: about `11m 03s`
    - Output: `/data/xuhaoming/yfy/research_workspace/results/mad-mm-short-subset/main/qwen2.5-14b/gsm8k/mad_subjective_3agents_2rounds_seed41.json`
- GPUs `6` and `7` were released after the completed steps.

## Notes

- The previous full matrix run was intentionally stopped after producing partial `qwen2.5-14b/gsm8k/CoT` outputs.
- This short subset should be treated as reproduction-subset evidence, not full paper reproduction.
- Early signal: MAD naive improved accuracy by `+0.02` over CoT on this 100-sample subset, while using about `11.6x` total tokens.
- Objective masking kept a `+0.01` accuracy gain over CoT while reducing tokens by about `31%` versus MAD naive.
- Subjective masking matched MAD naive accuracy but cost about `36%` more tokens than MAD naive and took much longer wall time on this subset.
- Trace-aligned summary: `analysis_short_subset_summary.json`.
- Trace case summary: `trace_cases_summary.json`.
- First insight report: `reports/20260612-madmm-short-subset-first-insights.md`.
- Trace-level message retention report: `reports/20260612-madmm-trace-message-retention.md`.
