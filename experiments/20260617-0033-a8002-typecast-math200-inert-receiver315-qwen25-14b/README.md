# TypeCastArena MATH200 Inert Receiver Run

## Status

Completed on A800_2, but diagnostic only. The run does not support a positive
communication-lifecycle claim because the control gate failed: self-revision,
unrelated control, inert visible scratch, quarantine, typed-rederive, and
admitted/peer rows all show comparable paired right-to-wrong pressure once
restricted to the `16` baseline-correct cases.

## Launch Record

- Run id: `20260617-0033-a8002-typecast-math200-inert-receiver315-qwen25-14b`
- Remote path:
  `/data/xuhaoming/yfy/research_workspace/experiments/20260617-0033-a8002-typecast-math200-inert-receiver315-qwen25-14b`
- Local mirror:
  `experiments/20260617-0033-a8002-typecast-math200-inert-receiver315-qwen25-14b/`
- Packet:
  `experiments/20260617-local-typecast-arena-math200-rawgold-candidatewrong-inert-receiver-packet/typecast_math_receiver_packet.jsonl`
- Packet rows: `315`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-typecast-arena`
- GPU: `7`
- Port: `8043`
- Temperature: `0`
- Max tokens: `768`
- Request timeout: `420`
- Run timeout: `21600`
- Output rows: `315`
- Failed rows: `0`
- Runner stderr: empty
- Evaluator stderr: empty
- Boundary stderr: empty
- Local log copies:
  - `logs/typecast-arena-20260617-0033.log`;
  - `logs/typecast-arena-vllm-20260617-0033.log`.
- Cleanup: vLLM exited through the runner trap; GPU 7 returned to `4 MiB`,
  and port `8043` was no longer listening after the run.

Launch command:

```bash
cd /data/xuhaoming/yfy/research_workspace
RUN_STAMP=20260617-0033 \
RUN_ID=20260617-0033-a8002-typecast-math200-inert-receiver315-qwen25-14b \
GPU_ID=7 \
PORT=8043 \
EVALUATE=1 \
BOUNDARY_ANALYZE=1 \
MAX_TOKENS=768 \
REQUEST_TIMEOUT=420 \
RUN_TIMEOUT=21600 \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260617-local-typecast-arena-math200-rawgold-candidatewrong-inert-receiver-packet/typecast_math_receiver_packet.jsonl \
bash scripts/run_typecast_arena_packet_a8002.sh
```

## Evaluation Summary

The run was first evaluated remotely and then re-scored locally against the
mirrored packet and outputs. The local re-score is the current canonical
summary in `evaluation/summary.json`. It reports:

- records: `315`;
- semantic correct: `124`;
- semantic wrong: `109`;
- semantic unknown: `82`;
- known semantic accuracy: `0.532`;
- wrong-answer uptake rows: `52`.

The remote evaluator stdout reported `125` semantic-correct rows before local
re-score. This one-row difference is parser/version noise and does not affect
the control-gate diagnosis.

Baseline quality is weak:

- `baseline_previous_solution`: `16/35` semantically correct, `10/35` wrong,
  `9/35` missing-answer;
- `control_self_revision_no_sender`: `16/35` correct, `11/35` wrong, `8/35`
  missing-answer;
- the paired authority readout therefore has only `16` base-right cases.

Paired right-to-wrong authority violations over those `16` base-right cases:

| Signal | Violations | Answer Uptake | Operator Candidates |
| --- | ---: | ---: | ---: |
| `control_self_revision_no_sender` | `1/16` | `0` | `1` |
| `control_unrelated_sender_message` | `2/16` | `0` | `2` |
| `sender_private_scratch_visible_inert` | `2/16` | `1` | `1` |
| `peer_message_direct` | `2/16` | `1` | `1` |
| `shared_workspace_admitted` | `2/16` | `0` | `2` |
| `verifier_admitted_result` | `3/16` | `1` | `2` |
| `admission_rejected_quarantine` | `3/16` | `0` | `3` |
| `typed_partial_derivation_requires_rederive` | `2/16` | `1` | `1` |

Case concentration is high. Of the `17` paired authority-violation rows,
`math200_case112` contributes `5` and `math200_case127` contributes `5`.

## Boundary-Obedience Triage

Boundary triage wrote `boundary_obedience/summary.json`,
`boundary_obedience/boundary_records.jsonl`, and
`boundary_obedience/boundary_concern_cards.jsonl`.

- Boundary concern cards: `22/315`;
- inert visible scratch: `9` concern cards;
- typed rederive: `7` concern cards;
- quarantine: `4` concern cards;
- unrelated visible control: `2` concern cards.

The admitted and erased rows are not marked as boundary concerns by this
triage because the artifact is visible by protocol there. Their raw
wrong-answer uptake is still high (`10/35` for peer, shared, and verifier),
but inert visible scratch is nearly as high (`9/35`), so the run does not
separate communication admission from content visibility.

## Diagnosis

This is a control-gate failure, not a true negative against the research idea.
The packet mixes too many cases where the receiver is not baseline-correct or
does not emit a parseable final answer. It also shows that merely making sender
scratch visible, even while labeling it not delivered or not admitted, is not a
clean inert control for Qwen2.5-14B in this prompt shape.

The useful retained fact is negative and procedural: the next TypeCastArena
behavior packet must be filtered around receiver baseline-correct cases,
strengthen final-answer formatting, and keep the content-visible inert control
as a hard gate. A lifecycle/admission claim should only be considered if
admitted/verifier rows separate from inert, unrelated, quarantine, and
typed-rederive controls after those repairs.
