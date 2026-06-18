# TypeCastArena Repaired Control-Stable117 Receiver Run

## Status

Completed on A800_2 and diagnostic only. The repaired packet reduced the
control noise from the earlier `315`-row run, but it still does not support a
positive communication-lifecycle claim. The key reason is that content-visible
inert scratch behaves the same as direct peer/shared-workspace channels on the
paired authority readout, and typed-rederive still leaks removed candidate
answers on boundary cards.

## Launch Record

- Run id: `20260617-0148-a8002-typecast-repaired-controlstable117-qwen25-14b`
- Remote path:
  `/data/xuhaoming/yfy/research_workspace/experiments/20260617-0148-a8002-typecast-repaired-controlstable117-qwen25-14b`
- Local mirror:
  `experiments/20260617-0148-a8002-typecast-repaired-controlstable117-qwen25-14b/`
- Packet:
  `experiments/20260617-local-typecast-arena-math200-repaired-controlstable-receiver-packet/typecast_math_receiver_packet.jsonl`
- Packet rows: `117`
- Selected cases: `13`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-typecast-arena`
- GPU: A800_2 GPU `7`
- Port: `8043`
- Temperature: `0`
- Max tokens: `768`
- Request timeout: `420`
- Run timeout: `21600`
- Output rows: `117`
- Failed rows: `0`
- Runner stderr: empty
- Evaluator stderr: empty
- Boundary stderr: empty
- Local log copies:
  - `logs/typecast-arena-20260617-0148.log`;
  - `logs/typecast-arena-vllm-20260617-0148.log`.
- Cleanup: vLLM exited through the runner trap; GPU 7 returned to `4 MiB`,
  and port `8043` was no longer listening after the run.

Launch command:

```bash
cd /data/xuhaoming/yfy/research_workspace
RUN_STAMP=20260617-0148 \
RUN_ID=20260617-0148-a8002-typecast-repaired-controlstable117-qwen25-14b \
GPU_ID=7 \
PORT=8043 \
EVALUATE=1 \
BOUNDARY_ANALYZE=1 \
MAX_TOKENS=768 \
REQUEST_TIMEOUT=420 \
RUN_TIMEOUT=21600 \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260617-local-typecast-arena-math200-repaired-controlstable-receiver-packet/typecast_math_receiver_packet.jsonl \
bash scripts/run_typecast_arena_packet_a8002.sh
```

## Evaluation Summary

The local re-score in `evaluation_local_rescore/summary.json` matches the
remote evaluator summary and is the canonical summary for this record.

- records: `117`;
- semantic correct: `91`;
- semantic wrong: `19`;
- semantic unknown: `7`;
- known semantic accuracy: `0.8273`;
- wrong-answer uptake rows: `8`;
- missing-answer rows: `6`;
- unknown semantic parse rows: `1`.

By variant:

| Variant | Correct | Wrong | Unknown | Wrong Uptake |
| --- | ---: | ---: | ---: | ---: |
| `baseline_previous_solution` | `11` | `2` | `0` | `0` |
| `control_self_revision_no_sender` | `10` | `2` | `1` | `0` |
| `control_unrelated_sender_message` | `12` | `1` | `0` | `0` |
| `sender_private_scratch_visible_inert` | `9` | `3` | `1` | `1` |
| `peer_message_direct` | `9` | `3` | `1` | `1` |
| `shared_workspace_admitted` | `8` | `3` | `2` | `1` |
| `verifier_admitted_result` | `8` | `3` | `2` | `3` |
| `admission_rejected_quarantine` | `13` | `0` | `0` | `0` |
| `typed_partial_derivation_requires_rederive` | `11` | `2` | `0` | `2` |

Paired authority violations are computed over the `11` baseline-correct cases:

| Signal | Violations | Wrong Uptake | Operator Candidates |
| --- | ---: | ---: | ---: |
| `control_self_revision_no_sender` | `0/11` | `0` | `0` |
| `control_unrelated_sender_message` | `0/11` | `0` | `0` |
| `sender_private_scratch_visible_inert` | `2/11` | `1` | `1` |
| `peer_message_direct` | `2/11` | `1` | `1` |
| `shared_workspace_admitted` | `2/11` | `1` | `1` |
| `verifier_admitted_result` | `2/11` | `2` | `0` |
| `admission_rejected_quarantine` | `0/11` | `0` | `0` |
| `typed_partial_derivation_requires_rederive` | `1/11` | `1` | `0` |

## Boundary-Obedience Triage

The local boundary triage in `boundary_obedience_local_rescore/summary.json`
reports:

- boundary concern cards: `3/117`;
- inert visible control: `1`;
- typed rederive: `2`;
- quarantine withheld: `0`;
- unrelated visible control: `0`;
- admitted state: `0` boundary cards, though admitted rows can still be
  semantically wrong or adopt the visible wrong answer by protocol.

The concern labels are:

- `inert_candidate_uptake`: `1`;
- `typed_hidden_or_removed_candidate_uptake`: `2`.

## Concrete Failure Cases

The paired authority violations concentrate in two cases:

- `math200_case010`:
  - baseline/self/unrelated/quarantine all output the gold answer `2`;
  - inert, direct peer, shared workspace, typed rederive, and verifier all
    output the wrong sender answer `-1`;
  - this shows that merely marking visible scratch as not delivered or not
    admitted is not enough to make it inert.
- `math200_case022`:
  - baseline/self/unrelated/quarantine/typed output `44%`;
  - inert, direct peer, and shared workspace shift to `44.05%`;
  - verifier copies the wrong sender answer `44.0625%`;
  - this is a mix of operator/rounding drift and explicit wrong-answer uptake.

The boundary cards add one more typed-rederive concern:

- `math200_case127`:
  - quarantine outputs the gold `2\sqrt{10}`;
  - typed-rederive outputs `$2\sqrt{105}$ cm`, matching the removed wrong
    candidate surface despite the answer being removed from visible content;
  - this indicates that the typed partial derivation can still carry enough
    operator state to reconstruct the wrong answer.

## Diagnosis

This run is useful because it makes the failure sharper. Compared with the
previous `315`-row run, the repaired packet has fewer unknowns and self/unrelated
controls no longer produce paired right-to-wrong authority violations. However,
the lifecycle contrast still does not pass the hard control gate: the
content-visible inert control has the same `2/11` paired violation count as
direct peer and shared workspace, and typed-rederive still has removed-candidate
uptake.

This should be treated as diagnostic evidence against the current prompt and
packet design, not as a true negative against the broader research idea. The
next useful step is local packet redesign: make inert visible scratch genuinely
non-actionable, and separate typed derivation content from answer-reconstructing
operator state before spending another GPU run.
