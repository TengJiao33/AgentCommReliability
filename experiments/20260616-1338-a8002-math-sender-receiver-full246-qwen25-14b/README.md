# MATH Sender-Receiver Full246 Qwen2.5-14B

Behavior run for the first MATH sender-receiver micro-protocol packet.

## Run

- Run id: `20260616-1338-a8002-math-sender-receiver-full246-qwen25-14b`
- Remote path:
  `A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260616-1338-a8002-math-sender-receiver-full246-qwen25-14b/`
- Local mirror:
  `experiments/20260616-1338-a8002-math-sender-receiver-full246-qwen25-14b/`
- Packet:
  `experiments/20260616-local-math-sender-receiver-micro-protocol-packet/math_sender_receiver_micro_protocol_packet.jsonl`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-sender-receiver-full246`
- GPU: A800_2 GPU `7`
- Max tokens: `768`

Remote command:

```bash
cd /data/xuhaoming/yfy/research_workspace
RUN_STAMP=20260616-1338 \
RUN_ID=20260616-1338-a8002-math-sender-receiver-full246-qwen25-14b \
SERVED_MODEL=qwen2.5-14b-sender-receiver-full246 \
GPU_ID=7 \
PORT=8042 \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260616-local-math-sender-receiver-micro-protocol-packet/math_sender_receiver_micro_protocol_packet.jsonl \
MAX_TOKENS=768 \
RUN_TIMEOUT=21600 \
bash scripts/run_math_epistemic_type_erasure_a8002.sh
```

## Outputs

- Raw model outputs: `outputs.jsonl`
- Runner stdout: `runner.stdout.jsonl`
- Runner stderr: `runner.stderr.log`
- Evaluator summary: `evaluation/summary.json`
- Evaluated rows: `evaluation/evaluated_rows.jsonl`
- Paired deltas: `evaluation/paired_deltas.jsonl`
- Lifecycle analysis: `analysis/summary.json`
- Violation cards: `analysis/violation_cards.jsonl`

## Execution

- Completed rows: `246/246`
- Runner stderr: empty
- Evaluator stderr: empty
- Semantic known rows: `246/246`
- Semantic correct rows: `226/246`
- Semantic wrong rows: `20/246`

## Short Read

The run produced `20` authority-violation cards. The seed taxonomy splits them
into:

- `4` admitted-state inherited-operator cards;
- `4` peer-message operator-influence cards;
- `2` direct visible answer-uptake cards;
- `4` local re-solve or empty-artifact cards;
- `6` operator candidates needing manual review.

The cleanest mechanism signal is `math121`: wrong equation-surface content
moves the receiver from `18√3` to `18√2` under peer/admitted/memory and some
typed channels, while inert scratch and unrelated sender controls stay clean.

See:

- `reports/20260616-math-sender-receiver-micro-protocol-qwen25-14b.md`
