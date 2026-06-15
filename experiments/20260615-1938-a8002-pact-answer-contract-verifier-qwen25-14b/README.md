# 20260615-1938-a8002-pact-answer-contract-verifier-qwen25-14b

## What We Tried

Ran the model-ready PACT answer-contract verifier packet with a
low-temperature Qwen2.5-14B-Instruct verifier.

The packet asks the model to inspect only the original question and public-state
fields, then emit structured alarms for target authority, answer type/relation,
short-span/granularity, evidence adequacy, final-candidate attraction, and the
primary failure surface.

## Machine

- Host: A800_2 (`10-116-90-20`)
- GPU: `7`
- Free memory before launch: `81149 MiB`
- Work dir: `/data/xuhaoming/yfy/research_workspace`

## Code

- Local runner: `scripts/run_pact_public_state_field_packet.py`
- Verifier evaluator: `scripts/evaluate_pact_answer_contract_verifier.py`
- Launcher: `scripts/run_pact_answer_contract_verifier_a8002.sh`
- Local modifications: launcher only; verifier packet and evaluator were synced
  to the remote workspace before launch.

## Environment

- Python: `3.10.20`
- PyTorch: `2.4.0+cu121`
- vLLM: `dev`
- LLM/API backend: vLLM OpenAI-compatible server
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-answer-contract-verifier`

## Data / Task

- Packet:
  `/data/xuhaoming/yfy/research_workspace/experiments/20260615-local-pact-answer-contract-verifier-packet/verifier_packet.jsonl`
- Local packet source:
  `experiments/20260615-local-pact-answer-contract-verifier-packet/verifier_packet.jsonl`
- Size: `74` records
- Label sources: `50` positive target-layer seed records and `24` negative-control seed records

## Command

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=8035 bash scripts/run_pact_answer_contract_verifier_a8002.sh
```

The launcher starts vLLM, runs:

```bash
timeout 7200 "$PY" scripts/run_pact_public_state_field_packet.py \
  --packet "$PACKET" \
  --out-dir "$OUT_DIR" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --model "$SERVED_MODEL" \
  --api-key EMPTY \
  --temperature 0 \
  --max-tokens 192 \
  --timeout 180 \
  --keep-going \
  --progress-every 10
```

Then scores with:

```bash
"$PY" scripts/evaluate_pact_answer_contract_verifier.py \
  --packet "$PACKET" \
  --outputs "$OUT_DIR/outputs.jsonl" \
  --prediction-source outputs \
  --out-dir "$EVAL_DIR"
```

## Outputs

- Remote run log:
  `/data/xuhaoming/yfy/research_workspace/logs/pact-answer-contract-verifier-20260615-1938.log`
- Remote vLLM log:
  `/data/xuhaoming/yfy/research_workspace/logs/pact-answer-contract-verifier-vllm-20260615-1938.log`
- Local run log copies:
  `pact-answer-contract-verifier-20260615-1938.log`
  and `pact-answer-contract-verifier-vllm-20260615-1938.log`
- Outputs: `outputs.jsonl`
- Manifest: `manifest.json`
- Evaluation: `evaluation/summary.md`, `evaluation/summary.json`,
  `evaluation/evaluated_rows.jsonl`

## Result

- Status: passed execution; failed as a verifier prompt.
- Completed: `74/74`
- Failed requests: `0`
- JSON parse failures: `0`
- Exact all-fields accuracy: `0.081`
- Primary-surface accuracy: `0.230`
- Best binary alarm: `target_authority_alarm` F1 `0.688`

Selected alarm F1:

| Alarm | F1 |
| --- | ---: |
| `answer_contract_alarm` | `0.442` |
| `target_authority_alarm` | `0.688` |
| `answer_type_relation_alarm` | `0.133` |
| `short_span_granularity_alarm` | `0.324` |
| `evidence_adequacy_alarm` | `0.296` |
| `final_candidate_alarm` | `0.174` |

## Notes

The model emitted valid JSON for every record, so the low score is not a parser
failure. It overused `target_authority_alarm = soft`, under-fired the global
`answer_contract_alarm`, and often missed answer-type/relation or short-span
alarms even when its primary-surface text pointed at a related failure.

All six all-fields-correct rows were negative-control stable-right cases.

The current packet is useful as a falsification surface. The current prompt is
not ready to route or quarantine public-state fields.
