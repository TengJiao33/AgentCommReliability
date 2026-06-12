# 20260612-1403-a8002-madmm-qwen25-standard-main

## Goal

Run the MAD-MM author's standard main-result reproduction path, not a toy smoke setup:

- `scripts/run_all_model_baselines.sh`
- `scripts/run_all_mad_mm_variants.sh`

The separate analysis grid in `scripts/run_all_mad_analyses.sh` is tracked as the next batch because it is much larger than the main-result reproduction.

## Machine

- Host: A800_2 / `10-116-90-20`
- Work dir: `/data/xuhaoming/yfy/research_workspace/baselines/MAD-MM`
- Intended GPUs: `2,3,4,5` through `MAD_MM_GPUS`
- Results root: `/data/xuhaoming/yfy/research_workspace/results/mad-mm-standard-main`
- Logs root: `/data/xuhaoming/yfy/research_workspace/logs`

Preflight on 2026-06-12:

- `/data`: about 1.8T free.
- `/mnt/quarkfs`: about 4.6T free.
- GPUs 2-7 were essentially free at first check.

## Code

- Upstream: `https://github.com/HongduanTian/MAD-MM`
- Commit: `f02069add08280b764d059a2f06ca0043aa093e2`
- Local modifications:
  - Added A800_2 local `model_path` entries for Qwen2.5 7B/14B/32B/72B.
  - Made script GPU IDs configurable through `MAD_MM_GPUS`, preserving author default `0,1`.
  - Made top-level output path configurable through `MAD_MM_SAVE_PATH`, preserving author default `new_results`.

## Environment

- Env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- Python: 3.10
- vLLM: 0.6.3
- PyTorch: 2.4.0+cu121
- Transformers: 4.46.2
- Datasets: 3.1.0
- `pip check`: passed.

## Data / Task

Using upstream `processed_data`:

- `gsm8k`: 1319 test instances
- `math`: 5000 test instances
- `mmlu_pro`: 12032 test instances
- `aime24`: 30 test instances
- `aime25`: 30 test instances

Author standard seeds:

- `gsm8k`, `math`, `mmlu_pro`: 41, 42, 43, 44, 45
- `aime24`, `aime25`: 42

## Model Availability

- `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`: complete, 8 safetensor shards.
- `/mnt/quarkfs/share_model/Qwen2.5-72B-Instruct`: complete, 37 safetensor shards.
- `/mnt/quarkfs/share_model/Qwen2.5-32B-Instruct`: config files present but safetensor shards missing at preflight.

HF completion command was attempted on A800_2:

```bash
HF_HOME=/data/xuhaoming/yfy/research_workspace/hf_home \
/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/hf download \
  Qwen/Qwen2.5-32B-Instruct \
  --local-dir /mnt/quarkfs/share_model/Qwen2.5-32B-Instruct
```

Download log:

```text
/data/xuhaoming/yfy/research_workspace/logs/madmm_download32_20260612_140307.log
```

HF could not reach `huggingface.co` from A800_2. ModelScope is reachable, so the active completion command is now:

```bash
MODELSCOPE_CACHE=/data/xuhaoming/yfy/research_workspace/modelscope_cache \
/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/modelscope download \
  --model Qwen/Qwen2.5-32B-Instruct \
  --local_dir /mnt/quarkfs/share_model/Qwen2.5-32B-Instruct \
  --max-workers 8
```

ModelScope tmux session and log:

```text
session: madmm_ms32
log: /data/xuhaoming/yfy/research_workspace/logs/madmm_modelscope32_20260612_140814.log
```

## Planned Command

```bash
cd /data/xuhaoming/yfy/research_workspace/baselines/MAD-MM
export HF_HOME=/data/xuhaoming/yfy/research_workspace/hf_home
export TORCH_HOME=/data/xuhaoming/yfy/research_workspace/torch_home
export PIP_CACHE_DIR=/data/xuhaoming/yfy/research_workspace/pip_cache
export MAD_MM_GPUS=2,3,4,5
export MAD_MM_SAVE_PATH=/data/xuhaoming/yfy/research_workspace/results/mad-mm-standard-main
export PYTHON=/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python
```

The upstream scripts call `python` directly, so the job should be launched after activating the env or with `PATH` prepended:

```bash
export PATH=/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin:$PATH
bash scripts/run_all_model_baselines.sh
bash scripts/run_all_mad_mm_variants.sh
```

Prepared launcher:

```text
/data/xuhaoming/yfy/research_workspace/scripts/run_madmm_standard_main_a8002.sh
```

## Status

- Setup: complete.
- Qwen2.5-32B completion: complete via ModelScope; 17 safetensor shards present.
- Main reproduction job: launched in tmux session `madmm_standard_main` at 2026-06-12 14:34 CST, then stopped at user request to avoid occupying shared GPUs too long.
- Main log: `/data/xuhaoming/yfy/research_workspace/logs/madmm_standard_main_20260612_143417.log`.
- First observed output: `qwen2.5-14b/gsm8k/cot_seed41`.
- Stopped around 2026-06-12 14:42 CST. GPUs 2-5 were released.

## Notes

- This is standard-reproduction setup evidence, not result evidence.
- The top-level scripts request Qwen2.5 14B/32B/72B, while the upstream `configs.yaml` did not include those keys. The A800_2 patch records local model paths but does not change method logic.
- The upstream evaluator printed `Evaluating on 100 test data` for the first GSM8K CoT run. This appears to be the author's default sampling behavior, not an added local downsampling flag.
- Partial outputs were produced under `/data/xuhaoming/yfy/research_workspace/results/mad-mm-standard-main/main/qwen2.5-14b/gsm8k/` before stopping.
