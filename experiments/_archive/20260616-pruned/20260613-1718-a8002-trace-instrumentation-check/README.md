# Trace Instrumentation Check

## What We Tried

Applied the prepared MOC and DAR trace-instrumentation patches on A800_2, then ran tiny checks to confirm that per-sample communication and retention events can be extracted into the unified communication trace schema.

## Scope

- Methods: MOC forced structural merge; DAR `filter_critical`
- Model: Qwen2.5-7B-Instruct
- Dataset: GSM8K
- Samples:
  - MOC: 1
  - DAR: 5
- Comparison target: trace completeness, not benchmark accuracy

## Resource Notes

- Machine: A800_2
- GPU: 7
- MOC vLLM port: `8027`
- MOC timeout: 30 minutes
- DAR timeout: 30 minutes
- GPU 7 was released after the checks.

## Code

- MOC upstream commit: `9c67c92507570704a7df73e452552a3f49e83897`
- DAR upstream commit: `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`
- Applied patches:
  - `baselines/MOC/patches/a8002-comm-trace-events.patch`
  - `baselines/DAR/patches/a8002-filter-retention-history.patch`
- Extractor:
  - `scripts/extract_comm_trace_schema.py`

## Environment

- Env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- MOC used OpenAI-compatible vLLM served as `qwen2.5-7b-trace`.
- DAR loaded the local model through its vLLM path.

## Commands

MOC:

```bash
cd /data/xuhaoming/yfy/research_workspace/baselines/MOC
MOC_USE_HASH_EMBEDDING=1 \
OPENAI_BASE_URL=http://127.0.0.1:8027/v1 \
OPENAI_API_KEY=EMPTY \
MOC_MERGE_LLM_NAME=vllm:qwen2.5-7b-trace \
MOC_COMM_TRACE_JSONL=/data/xuhaoming/yfy/research_workspace/results/moc-trace-check-20260613_1718/moc_comm_events.jsonl \
PYTHONPATH=/data/xuhaoming/yfy/research_workspace/baselines/MOC:$PYTHONPATH \
timeout 30m /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python experiments/run_experiment.py \
  --domain gsm8k \
  --n_size 1 \
  --llm_name vllm:qwen2.5-7b-trace \
  --agent_nums 5 \
  --mode Chain \
  --batch_size 1 \
  --num_rounds 1 \
  --use_cot \
  --neighbor_hops 2 \
  --ism_r 0 \
  --ism_epsilon 0.01 \
  --ism_kppa 45
```

DAR:

```bash
cd /data/xuhaoming/yfy/research_workspace/baselines/DAR
CUDA_VISIBLE_DEVICES=7 \
HF_HOME=/data/xuhaoming/yfy/research_workspace/hf_home \
timeout 30m /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python src/main.py \
  --model qwen2.5-7b \
  --num_agents 3 \
  --data gsm8k \
  --data_size 5 \
  --debate_rounds 1 \
  --uncertainty_prompt True \
  --vote_prompt True \
  --m_role filter_critical \
  --save_full_history \
  --out_dir /data/xuhaoming/yfy/research_workspace/results/dar-trace-check-filtercritical-gsm8k5-20260613_1721/out
```

## Remote Artifacts

| Artifact | Path |
| --- | --- |
| MOC log | `/data/xuhaoming/yfy/research_workspace/logs/moc-trace-check-n1-20260613_1718.log` |
| MOC sidecar events | `/data/xuhaoming/yfy/research_workspace/results/moc-trace-check-20260613_1718/moc_comm_events.jsonl` |
| MOC unified trace | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-trace-instrumentation-n1.comm_trace.jsonl` |
| DAR log | `/data/xuhaoming/yfy/research_workspace/logs/dar-trace-check-filtercritical-gsm8k5-20260613_1721.log` |
| DAR full history | `/data/xuhaoming/yfy/research_workspace/results/dar-trace-check-filtercritical-gsm8k5-20260613_1721/out/history/gsm8k_5__qwen2.5-7b_N=3_R=1_P=True_V=True_K=None_M=filter_critical_S=42.jsonl` |
| DAR unified trace | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-trace-filtercritical-gsm8k5.comm_trace.jsonl` |

Small local copies:

- `moc_comm_events.jsonl`
- `comm_trace_moc.jsonl`
- `comm_trace_dar.jsonl`
- `dar_history_gsm8k5_filtercritical.jsonl`
- `moc_summary_n1.json`
- `moc_detail_n1.json`

## What Happened

| Method | Samples | Accuracy | Trace Rows | Event Signal |
| --- | ---: | ---: | ---: | --- |
| MOC forced merge | 1 | 1/1 | 1 | 7 communication events: 3 `ism_merge`, 4 `ism_result` |
| DAR `filter_critical` | 5 | round 0: 5/5; round 1: 4/5 | 5 | 5 retention events |

MOC recorded per-sample merge sources, represented IDs, retained direct IDs, dropped direct IDs, selected summary strategy, merge similarity, and compressed-token stats.

DAR recorded candidate, retained, and dropped agent IDs plus raw filter responses. One sample flipped from correct to wrong: sample index `1` went from answer `200` to `240` after `filter_critical` retained Agent2 and Agent3 while dropping Agent1.

## Status Timeline

- `2026-06-13 17:18`: started temporary MOC vLLM server on GPU 7.
- `2026-06-13 17:19`: completed MOC n=1 forced-merge trace check.
- `2026-06-13 17:21`: launched DAR GSM8K5 `filter_critical` full-history check on GPU 7.
- `2026-06-13 17:23`: completed DAR check.
- `2026-06-13 17:25`: extracted unified traces and copied small local artifacts.

## Caveats

- MOC used forced merge with `ism_r=0`; this is a trace diagnostic, not a paper-default run.
- MOC used deterministic hash embeddings.
- DAR evidence is only 5 samples.
- DAR still appends some global logs under `result/`, but the history and TSV outputs respected `--out_dir`.

## Loose Threads

- Run a modest shared-sample trace comparison after instrumentation is stable.
- Consider adding retained/dropped correctness counts directly in the DAR extractor by comparing retained IDs with round-0 agent correctness.
