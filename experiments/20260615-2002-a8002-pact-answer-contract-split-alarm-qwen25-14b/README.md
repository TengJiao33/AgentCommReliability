# 20260615-2002-a8002-pact-answer-contract-split-alarm-qwen25-14b

## What We Tried

Ran a split-alarm verifier packet over the same `74` PACT answer-contract seed
records. Instead of asking the model to emit all alarms and a primary surface in
one JSON object, this packet asks one narrow alarm question per prompt.

The six alarm tasks are:

- `answer_contract_alarm`
- `target_authority_alarm`
- `answer_type_relation_alarm`
- `short_span_granularity_alarm`
- `evidence_adequacy_alarm`
- `final_candidate_alarm`

## Machine

- Host: A800_2 (`10-116-90-20`)
- GPU: `7`
- Free memory before launch: `81149 MiB`
- Work dir: `/data/xuhaoming/yfy/research_workspace`

## Code

- Split packet builder:
  `scripts/build_pact_answer_contract_split_alarm_packet.py`
- Split evaluator:
  `scripts/evaluate_pact_answer_contract_split_alarm.py`
- Local runner: `scripts/run_pact_public_state_field_packet.py`
- Launcher: `scripts/run_pact_answer_contract_split_alarm_a8002.sh`

## Environment

- Python: `3.10.20`
- PyTorch: `2.4.0+cu121`
- vLLM: `dev`
- LLM/API backend: vLLM OpenAI-compatible server
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-answer-contract-split-alarm`

## Data / Task

- Packet:
  `/data/xuhaoming/yfy/research_workspace/experiments/20260615-local-pact-answer-contract-split-alarm-packet/split_alarm_packet.jsonl`
- Local packet source:
  `experiments/20260615-local-pact-answer-contract-split-alarm-packet/split_alarm_packet.jsonl`
- Base records: `74`
- Prompt rows: `444`
- Label sources: `50` positive target-layer seed records and `24` negative-control seed records, expanded across `6` alarm tasks

## Command

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 \
PORT=8035 \
RUN_STAMP=20260615-2002 \
RUN_ID=20260615-2002-a8002-pact-answer-contract-split-alarm-qwen25-14b \
bash scripts/run_pact_answer_contract_split_alarm_a8002.sh
```

The launcher uses `max_tokens=64` and evaluates with:

```bash
"$PY" scripts/evaluate_pact_answer_contract_split_alarm.py \
  --packet "$PACKET" \
  --outputs "$OUT_DIR/outputs.jsonl" \
  --prediction-source outputs \
  --out-dir "$EVAL_DIR"
```

## Outputs

- Remote run log:
  `/data/xuhaoming/yfy/research_workspace/logs/pact-answer-contract-split-alarm-20260615-2002.log`
- Remote vLLM log:
  `/data/xuhaoming/yfy/research_workspace/logs/pact-answer-contract-split-alarm-vllm-20260615-2002.log`
- Local run log copies:
  `pact-answer-contract-split-alarm-20260615-2002.log`
  and `pact-answer-contract-split-alarm-vllm-20260615-2002.log`
- Outputs: `outputs.jsonl`
- Manifest: `manifest.json`
- Evaluation: `evaluation/summary.md`, `evaluation/summary.json`,
  `evaluation/evaluated_rows.jsonl`

## Result

- Status: passed execution; split alarms did not solve verifier reliability.
- Completed: `444/444`
- Failed requests: `0`
- Parse failures after split-label fallback: `0`
- Exact label accuracy: `0.590`
- Positive/negative accuracy: `0.617`

By alarm:

| Task | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| `answer_contract_alarm` | `0.926` | `0.379` | `0.538` |
| `target_authority_alarm` | `0.667` | `0.383` | `0.486` |
| `answer_type_relation_alarm` | `0.250` | `0.083` | `0.125` |
| `short_span_granularity_alarm` | `0.500` | `0.034` | `0.065` |
| `evidence_adequacy_alarm` | `0.350` | `0.538` | `0.424` |
| `final_candidate_alarm` | `0.000` | `0.000` | `0.000` |

## Notes

Split prompting did not reveal hidden strong verifier competence. Evidence
adequacy improved relative to the one-shot verifier, but the other alarm
families stayed weak or worsened.

The result suggests that the current seed packet may require either stronger
few-shot contrast, better label definitions, or a different verifier model. A
simple decomposition into one alarm per prompt is not enough.
