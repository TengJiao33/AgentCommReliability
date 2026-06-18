# MATH Operator Lifecycle V1 Packet

## 核心判断

下一轮实验已经从设计推进到可启动状态。这个 packet 只做一个问题：同一个错误 sender artifact 在 direct peer、shared workspace、verifier-admitted、quarantine、typed metadata、typed partial derivation 等生命周期状态下，是否诱发不同程度的 invalid cast / operator uptake。

本轮没有启动 GPU。准备产物已经在本地和 A800_2 同步完成。

## 本地产物

- builder: `scripts/build_math_operator_lifecycle_packet.py`
- local packet dir: `experiments/20260617-local-math-operator-lifecycle-v1-packet/`
- packet: `experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl`
- packet rows: `166`
- source rows represented: `11`
- selected sender artifacts: `16`
- selected artifacts by type: `wrong_equation_surface=5`, `wrong_final_answer=5`, `wrong_numeric_role_binding=3`, `wrong_relation_skeleton=3`
- selected artifacts by MATH case: max `2` per case; cases `21, 25, 28, 61, 96, 112, 121, 136, 139, 159`

## 设计约束

主要对比：

- `peer_message_direct`
- `shared_workspace_admitted`
- `verifier_admitted_result`
- `quarantine_withheld`
- `typed_inference_metadata_only`
- `typed_partial_derivation_dependency_check`

控制和压力项：

- `baseline_previous_solution`: 真实 prior Agent B solution
- `control_self_revision_no_peer`: 无 sender 的 self revision
- `metadata_only_hidden_control`: 只暴露 metadata，不暴露 artifact 内容
- `control_unrelated_sender_message`: 可见但不相关的 sender message
- `visible_inert_archived_content`: visibility stress；它故意暴露 sender 内容，不能当干净 hidden control

## 本地审计

packet materialization 通过了三个硬门槛：

- baseline gate: selected source rows 都有真实 `baseline_output`，没有近期 TypeCastArena 中的 placeholder baseline。
- uniqueness gate: `packet_id` 唯一；channel variant 带 `aXX_<artifact_type>`，不会被 evaluator 的 `case_id + variant` 配对覆盖。
- hidden gate: `metadata_only_hidden_control`、`quarantine_withheld`、`typed_inference_metadata_only` 的 communication block 没有 visible artifact，也没有 wrong-answer literal；`hard_gate_leak_count=0`。

gold-smoke 也通过：

- command: `python scripts/evaluate_math_authority_genesis_ladder.py --packet experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl --prediction-source gold --out-dir experiments/20260617-local-math-operator-lifecycle-v1-packet/gold_smoke`
- result: `166/166` semantic correct, `0` semantic unknown

boundary gold-smoke 通过：

- command: `python scripts/analyze_typecast_boundary_obedience.py --packet experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl --run-dir experiments/20260617-local-math-operator-lifecycle-v1-packet/gold_smoke --out-dir experiments/20260617-local-math-operator-lifecycle-v1-packet/boundary_obedience_gold_smoke`
- result: `166` records, `boundary_concern_count=0`
- analyzer note: `control_self_revision_no_peer` 已归入 `no_sender`；`metadata_only_hidden_control` 已归入 withheld/quarantine 类别。更新后的 analyzer 已同步到 A800_2。

## 远端资源

A800_2 check time: `2026-06-17T08:52:03+08:00`

- host: `10-116-90-20`
- project root: `/data/xuhaoming/yfy/research_workspace`
- project footprint: `11G`
- `/data`: `3.5T` total, `2.0T` used, `1.4T` available
- `/mnt/quarkfs`: `10T` total, `5.7T` used, `4.4T` available
- model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`, size `28G`
- runner/evaluator/boundary analyzer: present on remote
- boundary analyzer update: synced after adding the new channel categories
- new builder copied to remote: yes
- new packet copied to remote: yes
- remote packet line count: `166`
- remote packet SHA256: `53c5e6a8056a8e41b16b8900baa4e65666cea44dcacf5e877de3258b97dc769d`
- packet dir size on remote: `2.9M`
- checked ports `8047`, `8051`, `8055`: no listener observed

GPU snapshot:

| GPU | Used MiB | Free MiB | Util |
| ---: | ---: | ---: | ---: |
| 0 | 3139 | 78013 | 0 |
| 1 | 4 | 81149 | 0 |
| 2 | 4 | 81149 | 0 |
| 3 | 4 | 81149 | 0 |
| 4 | 4 | 81149 | 0 |
| 5 | 4 | 81149 | 0 |
| 6 | 4 | 81149 | 0 |
| 7 | 4 | 81149 | 0 |

Observed pre-existing services:

- port `8014`: swift/vLLM service on `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- port `8012`: swift/vLLM service on `/mnt/quarkfs/share_model/Qwen3.5-9B`

Do not kill those processes.

## Launch Command

Recommended first launch:

```bash
ssh A800_2
cd /data/xuhaoming/yfy/research_workspace
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260617-local-math-operator-lifecycle-v1-packet/math_operator_lifecycle_v1_packet.jsonl \
RUN_ID=20260617-a8002-math-operator-lifecycle-v1-qwen25-14b \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
SERVED_MODEL=qwen2.5-14b-math-operator-lifecycle-v1 \
GPU_ID=7 \
PORT=8047 \
EVALUATE=1 \
BOUNDARY_ANALYZE=1 \
bash scripts/run_typecast_arena_packet_a8002.sh
```

Expected remote output:

```text
/data/xuhaoming/yfy/research_workspace/experiments/20260617-a8002-math-operator-lifecycle-v1-qwen25-14b/
```

The runner starts a temporary vLLM server and has an exit cleanup trap. If an interruption leaves a process behind, inspect exact PIDs before killing:

```bash
ps -eo pid,cmd | grep qwen2.5-14b-math-operator-lifecycle-v1 | grep -v grep
```

## 判读标准

这个实验能推进故事的信号：

- hard controls 接近稳定，尤其 `metadata_only_hidden_control`、`quarantine_withheld`、`typed_inference_metadata_only` 不出现同量级失败；
- `shared_workspace_admitted` 或 `verifier_admitted_result` 相比 `peer_message_direct` 有更高 base-right to wrong delta；
- 失败样本里存在非直接答案复制的 operator uptake，尤其 equation / numeric role / relation skeleton 被继承。

这个实验会削弱当前方向的信号：

- self revision、metadata-only、quarantine、unrelated control 出现同量级错误；
- 大多数错误来自 direct answer copy、parser、local re-solve、final-line contract；
- leave-one-case-out 后信号主要由 `math121`、`math159`、`math96` 之一支撑。

## Caveats

- selected artifacts 仍偏向 `full_rationale` source surface：`13/16`。这有利于 operator signal，但会让后续需要一个 surface-balanced follow-up。
- prompt audit 中 full prompt 的 wrong-answer literal 计数包含原题或 prior solution 中的巧合字面匹配；hard-gate 判定只看 communication block 和 visible artifact。
- `typed_partial_derivation_dependency_check` 暴露 operator 内容，属于 dependency stress，不能作为 typed metadata hard control。
- `visible_inert_archived_content` 暴露 sender 内容，属于 visibility stress，不能作为干净 negative control。
