# 20260706-a8002-smoke-mca-s-live-state-qwen25-7b-rerun1

## Purpose

Rerun the MCA-S live-state smoke after fixing two memory issues:

- receiver manual generation now runs under `torch.inference_mode()`;
- MCA-S sender state no longer retains unused sender KV caches.

## Status

Completed on A800_2 GPU 6. This is not claim-bearing; it checks whether the activation-steering path can complete with row-level progress after the OOM fix.

## Previous failure

The first MCA-S smoke at:

```text
A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-s-live-state-qwen25-7b/
```

failed during row 2 receiver generation with CUDA OOM. Row 1 had completed but produced a malformed parsed answer (`str:finalansweronly`), so behavioral readout remains invalid even if this rerun completes.

## Configuration

- Remote root: `/data/xuhaoming/yfy/research_workspace`
- Remote run dir: `/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-s-live-state-qwen25-7b-rerun1`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Benchmark: `math500/test/canonical.jsonl`
- Unit: benchmark row
- Rows: `--limit 2`
- Protocol: `mca-activation-steering`
- State source: live sender generation
- GPU: `CUDA_VISIBLE_DEVICES=6`
- Agents/reviewers: `3/3`
- Prompt family: `standard-mad`
- Steering: layer `16`, scale `1.0`
- Max tokens: sender `512`, receiver `512`, max model len `4096`
- Temperatures: sender `1.0`, receiver `0.2`, top-p `1.0`

## Expected Artifacts

- `run_remote.sh`
- `run_remote.nohup.log`
- `launcher.pid`
- `math500-qwen25-7b-instruct-mca-activation-steering-state-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-activation-steering-state-all/summary.json`
- `math500-qwen25-7b-instruct-mca-activation-steering-state-all/summary.md`

## Result

- Started: `2026-07-06T12:44:24+08:00`
- Finished: `2026-07-06T12:46:08+08:00`
- Rows: 2
- Elapsed seconds: 102.1
- Initial majority accuracy: 0.5000
- Final accuracy: 0.0000
- Hidden channel rate: 1.0000
- Wrong-majority recovery rate: 0.0000
- Correct-majority harm rate: 1.0000

Interpretation: the OOM fix worked and the MCA-S path can complete with visible progress. The current `layer=16, scale=1.0` behavior is not usable for a full claim-bearing run: it harmed the initially correct smoke row and produced prompt-format pollution such as parsing `final answer only` as the answer.
