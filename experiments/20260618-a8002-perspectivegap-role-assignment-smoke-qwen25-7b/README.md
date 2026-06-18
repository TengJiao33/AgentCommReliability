# PerspectiveGap Role-Assignment Smoke on A800_2

## Gate

- Purpose: make first real model contact with the external PerspectiveGap benchmark after local official reproduction and deterministic baselines.
- Benchmark unit: PerspectiveGap `role_assignment` task, dynamic render from upstream scenarios and distractors.
- Scope: `pg_000`, `pg_004`, `pg_006`, `pg_070`; shuffle seed `1`; one request per scenario.
- Contrast available before model run: oracle, all-to-all, no-distractor all-to-all, shared-intersection-only, and role-name heuristic scored locally in `experiments/20260618-local-perspectivegap-contact/`.
- Success condition: runner completes all 4 requests, local scorer parses the outputs, and we can inspect whether failures are routing/role-boundary errors rather than plumbing.
- Failure condition: API/server failures, unparseable outputs, or scoring mismatch. In those cases this run is plumbing evidence only.
- Invalidation guard: do not treat 4 rows as a benchmark score; use it only to decide whether PerspectiveGap gives a useful mechanism surface.

## Machine Preflight

- Machine: `A800_2`, hostname `10-116-90-20`.
- Remote root: `/data/xuhaoming/yfy/research_workspace`.
- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- GPU: `7`.
- Port: `8061`.
- GPU check at `2026-06-18T00:50:13+08:00`: GPUs `1-7` were idle with about `81149 MiB` free; GPU `0` had pre-existing memory use.
- Existing services: ports `8014` and `8012` are pre-existing swift rollout services and must not be killed.
- Disk: `/data` had `1.4T` available; `/mnt/quarkfs` had `4.4T` available.

## Planned Command

Run a temporary vLLM server with an exit cleanup trap, then call upstream `scripts/run_model_predictions.py` with:

```bash
OPENAI_API_KEY=EMPTY PYTHONPATH=src timeout 1800s \
  /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python \
  scripts/run_model_predictions.py \
  --provider openai-compatible \
  --base-url http://127.0.0.1:8061/v1 \
  --api-key-env OPENAI_API_KEY \
  --model qwen2.5-7b-perspectivegap \
  --scenario-id pg_000,pg_004,pg_006,pg_070 \
  --shuffle-seed 1 \
  --tasks role_assignment \
  --out /data/xuhaoming/yfy/research_workspace/experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-7b/predictions.jsonl
```

