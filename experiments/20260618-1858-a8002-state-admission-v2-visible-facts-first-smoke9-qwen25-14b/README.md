# State Admission V2 Visible-Facts-First Smoke9 Qwen2.5-14B

日期：2026-06-18

状态：GPU schema ablation run。这个 run 已完成，用来测试显式列出最终裁决者可见且已核验事实集合，是否能修复扰动行的强制作答。

## Purpose

上一轮 `abstention_explicit` 显示，模型会填写最终裁决闸门，但仍常常把不可见、未核验或已拒绝事实算进最终裁决。这个 run 进一步要求模型先输出 `final_decider_visible_verified_facts` 和 `excluded_facts`，再生成候选答案状态、准入单元和最终答案。

这个 run 的问题是：如果先把最终裁决者可见且已核验事实集合显式列出来，模型是否会在扰动行中承认证据不足。

## Launch Record

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Local run dir: `experiments/20260618-1858-a8002-state-admission-v2-visible-facts-first-smoke9-qwen25-14b`
- Remote run dir: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-1858-a8002-state-admission-v2-visible-facts-first-smoke9-qwen25-14b`
- Packet: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-state-admission-v2-smoke/packet.jsonl`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-state-admission-v2-visible-facts-first`
- Prompt style: `visible_facts_first`
- GPU: `7`
- Port: `8072`
- Max tokens: `1300`
- Max model len: `16384`
- Temperature: `0`
- Row count: `9`

Launch command:

```bash
RUN_ID=20260618-1858-a8002-state-admission-v2-visible-facts-first-smoke9-qwen25-14b \
GPU_ID=7 \
PORT=8072 \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
SERVED_MODEL=qwen2.5-14b-state-admission-v2-visible-facts-first \
PROMPT_STYLE=visible_facts_first \
MAX_TOKENS=1300 \
RUN_TIMEOUT=1800 \
bash scripts/run_state_admission_v2_a8002.sh
```

Cleanup check: `predictions.jsonl` has 9 rows, the launcher finished, and GPU 7 returned to idle after the script exited.

## Artifacts

- `predictions.jsonl`: model responses under the visible-facts-first schema.
- `scores.jsonl`: remote scorer output.
- `scores.local_rescore.jsonl`: local rescore; it matches the remote summary.
- `summary.md` and `summary.local_rescore.md`: metric summaries.
- `visible_fact_diagnostics.jsonl`: per-row expected and predicted final-decider visible fact sets.
- `visible_fact_summary.md`: aggregate visible-fact precision and recall.
- `run.log`, `runner.stdout.log`, `vllm.log`, `launch.nohup.log`: execution logs.

## Preflight Gate

Local dry-run prompt materialization:

```text
rows=9
prompt chars min=7165 max=7580 avg=7321.2
forbidden-field leaks=0
```

## Model Result

Main scorer:

```text
rows: 9
strict: 0.0000
unit_recall: 0.5926
rejection_recall: 0.5556
scope_violations: 0.2222
absent_unit_violations: 0.0000
downstream_ok: 0.3333
option_state_recall: 0.7778
base: strict=0.0000, unit_recall=0.5556, rejection_recall=0.0000, scope_violations=0.0000, absent_unit_violations=0.0000, downstream_ok=1.0000, option_state_recall=0.7778
perturbation: strict=0.0000, unit_recall=0.6111, rejection_recall=0.8333, scope_violations=0.3333, absent_unit_violations=0.0000, downstream_ok=0.0000, option_state_recall=0.7778
```

Visible-fact diagnostics:

```text
rows: 9
visible_precision: 0.9544
visible_recall: 0.9861
base: visible_precision=0.9583, visible_recall=0.9583
perturbation: visible_precision=0.9524, visible_recall=1.0000
```

## Concrete Diagnosis

The model can mostly list the final-decider visible verified facts. Perturbation recall is `1.0000`, and average precision is above `0.95`.

This did not fix abstention. Perturbation `downstream_ok` is `0.0000`: all six perturbation rows still receive a concrete answer when the expected downstream state is evidence-insufficient.

In `hb10_b_hazard_quarantined`, the visible fact set is exactly correct, and the quarantined hazard fact is excluded. The model still answers Warehouse B using shared-context facts as if they were positive recommendation evidence.

In `hb11_school_repair_quarantined`, the visible fact set is exactly correct and the repair fact is rejected. The model still answers School Gym, using weaker shared-context support as if it completed the missing enabler.

In `hb01_west_bridge_unverified`, the visible fact set is correct and the unverified bridge fact is rejected. The model still answers West City and incurs scope violations in the unit layer.

## Interpretation

This run moves the failure later in the pipeline. The main issue is no longer just whether the model can list visible facts. It can mostly do that. The harder issue is whether it treats those facts as sufficient or insufficient for a final decision.

The evidence now points toward a sufficiency criterion failure: the model mistakes context, partial support, or remaining plausible facts for a complete admissible certificate.

## Caveats

The visible-fact metric is a local diagnostic, not part of the main scorer's strict metric.

The prompt is longer and asks for more fields, which may reduce option-state quality.

The packet still uses only three source sketches and six perturbations. It is a diagnostic slice, not a complete benchmark.

## Next Step

The next schema should force per-option required evidence slots: for each candidate, list required blocker or enabler slots, mark each slot as present, missing, rejected, or not visible, then derive final state from that slot table. The current visible-fact table is too permissive because the model still decides from plausibility rather than completed evidence slots.
