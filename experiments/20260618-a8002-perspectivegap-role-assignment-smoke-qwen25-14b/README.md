# PerspectiveGap Role-Assignment Smoke on A800_2, Qwen2.5-14B

## Gate

- Purpose: check whether the Qwen2.5-7B under-coverage pattern is a weak-model artifact or also appears in a stronger local model.
- Benchmark unit: PerspectiveGap `role_assignment` task, official upstream runner and scorer.
- Scope: same 4 scenarios as the 7B smoke: `pg_000`, `pg_004`, `pg_006`, `pg_070`; shuffle seed `1`.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`.
- Expected output: 4 prediction rows, official local score rows, and a paired comparison against the 7B smoke.
- Success condition: all 4 requests complete and score cleanly.
- Invalidation guard: this remains a smoke/contact result; no full benchmark ranking claim.

## Machine Preflight

- Machine: `A800_2`, remote root `/data/xuhaoming/yfy/research_workspace`.
- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`.
- GPU: `7`.
- Port: `8062`.
- Existing services on `8014` and `8012` are pre-existing and must not be killed.
- The preceding Qwen2.5-7B smoke cleaned up successfully; GPU `7` returned to about `81149 MiB` free.

