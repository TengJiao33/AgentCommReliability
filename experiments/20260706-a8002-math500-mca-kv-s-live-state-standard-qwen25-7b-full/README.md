# 20260706-a8002-math500-mca-kv-s-live-state-standard-qwen25-7b-full

## Purpose

Run one standard full diagnostic for the two live-state MCA variants:

- MCA-KV: receiver continues from a sender's real generation KV cache.
- MCA-S: receiver is steered by a vector captured during sender real generation.

This run answers whether the live-state implementations can complete on full MATH500 with standard-mad initial prompting and visible row-level progress. It is diagnostic, not claim-bearing, because MCA-S smoke already showed unstable behavior at `layer=16, scale=1.0`.

## Status

Queued on A800_2 with launcher PID `1883987`. The queue waits for a fully empty GPU, then runs MCA-KV followed by MCA-S serially on the same GPU.

As of `2026-07-06T12:59:59+08:00`, no GPU had been selected: `nvidia-smi pmon` showed a process on every GPU, so the strict launcher skipped GPUs 0-7 and continued waiting.

## Configuration

- Remote root: `/data/xuhaoming/yfy/research_workspace`
- Remote run dir: `/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-kv-s-live-state-standard-qwen25-7b-full`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Benchmark: `math500/test/canonical.jsonl`
- Expected rows: 500
- Initial prompt family: `standard-mad`
- State source: live sender generation
- Agents/reviewers: `3/3`
- Pool-state scope: `all`
- Sender max tokens: `4096`
- Receiver max tokens: `1536`
- Max model len: `8192`
- Temperatures: sender `1.0`, receiver `0.2`, top-p `1.0`
- MCA-S steering: layer `16`, scale `1.0`
- Candidate GPUs: `0 1 2 3 4 5 6 7`
- GPU selection threshold: `nvidia-smi pmon` must show no process on that GPU, with at least `80000` MiB free and utilization at most `5%`

## Expected Artifacts

- `run_remote.sh`
- `run_remote.nohup.log`
- `launcher.pid`
- `selected_gpu.txt`
- `math500-qwen25-7b-instruct-mca-kv-cache-state-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-kv-cache-state-all/summary.json`
- `math500-qwen25-7b-instruct-mca-kv-cache-state-all/summary.md`
- `math500-qwen25-7b-instruct-mca-activation-steering-state-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-activation-steering-state-all/summary.json`
- `math500-qwen25-7b-instruct-mca-activation-steering-state-all/summary.md`

## Stop And Cleanup

The launcher exits after both variants finish or after a command timeout/failure. Cleanup command, if needed:

```bash
kill $(cat /data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-kv-s-live-state-standard-qwen25-7b-full/launcher.pid)
```
