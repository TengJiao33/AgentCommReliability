# 20260615-2318-a8002-authority-genesis-ladder-qwen25-14b

## What We Tried

Ran the first Authority Genesis Ladder packet on A800_2 with
Qwen2.5-14B-Instruct.

The packet holds the trusted question/evidence prompt constant and varies the
future signal attached to the same injected content: hidden metadata, raw
mention, answer-shaped span, peer claim, majority consensus, previous final
answer, verifier-approved result, saved memory, active task, and final-answer
commitment.

## Machine

- Host: A800_2 (`10-116-90-20`)
- GPU: `7`
- Work dir: `/data/xuhaoming/yfy/research_workspace`
- GPU after completion: GPU 7 returned to `4 MiB` used and `0%` utilization.

## Code

- Local branch at launch: `codex/authority-injection-arena`
- Local base commit: `dd18951`
- Local uncommitted scripts/packet were copied into the remote file workspace
  before launch.

## Environment

- Python: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- Backend: vLLM OpenAI-compatible server
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-authority-genesis-ladder`

## Data / Task

- Packet:
  `experiments/_archive/20260616-pruned/20260615-local-authority-genesis-ladder-packet/authority_genesis_ladder_packet.jsonl`
- Source cases: `24`
- Prompt rows: `504`
- Positive target-focus cases: `20`
- Negative-control cases: `4`

## Command

```bash
cd /data/xuhaoming/yfy/research_workspace
RUN_STAMP=20260615-2318 GPU_ID=7 PORT=8038 \
  bash scripts/run_authority_genesis_ladder_a8002.sh
```

The command was launched through `nohup` from the local Windows machine and
then polled until completion.

## Outputs

- Raw outputs: `outputs.jsonl`
- Manifest: `manifest.json`
- Evaluation: `evaluation/summary.json`
- Evaluation markdown: `evaluation/summary.md`
- Paired deltas: `evaluation/paired_deltas.jsonl`
- Evaluated rows: `evaluation/evaluated_rows.jsonl`
- Runner log: `authority-genesis-ladder-20260615-2318.log`
- vLLM log: `authority-genesis-ladder-vllm-20260615-2318.log`

## Result

- Status: completed
- Completed requests: `504/504`
- Failed requests: `0`
- Overall EM: `0.687`
- Overall F1: `0.747`
- Baseline EM/F1: `0.750` / `0.799`

Wrong-lure paired readout over the `18` baseline-correct rows:

| Future signal | AVR | Exact AUR |
| --- | ---: | ---: |
| `hidden_metadata` | 0.000 | 0.000 |
| `raw_mention` | 0.111 | 0.000 |
| `answer_shaped_span` | 0.167 | 0.000 |
| `peer_claim` | 0.333 | 0.167 |
| `majority_consensus` | 0.222 | 0.056 |
| `previous_final_answer` | 0.111 | 0.000 |
| `verifier_approved_result` | 0.333 | 0.111 |
| `saved_memory` | 0.278 | 0.056 |
| `active_task_required` | 0.611 | 0.444 |
| `final_answer_commitment` | 0.389 | 0.111 |

## Notes

- The strongest wrong-lure pressure is `active_task_required`.
- Hidden metadata exactly matches baseline behavior for wrong-lure paired
  violations.
- The curve is not monotonic: `previous_final_answer` and
  `majority_consensus` are weaker than expected in this prompt surface, while
  peer/verifier/task/final-commitment signals are stronger.
- This is saved-field PACT pressure evidence, not a full multi-agent rerun.
