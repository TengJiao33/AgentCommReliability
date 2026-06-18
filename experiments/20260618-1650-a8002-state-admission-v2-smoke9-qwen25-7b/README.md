# State Admission V2 Smoke9 Qwen2.5-7B

日期：2026-06-18

状态：GPU diagnostic run。这个 run 已完成，结果是诊断信号，不是 claim-bearing 结果。

## Purpose

这次 run 回答一个很小的问题：在 3 条 HiddenBench fact-unit row 和 6 个 same-text verification/scope perturbations 上，Qwen2.5-7B 能否从 source-scoped facts 构造正确的 blocker/enabler admission units，并守住 fact-level recipient scope。

## Launch Record

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Local run dir: `experiments/20260618-1650-a8002-state-admission-v2-smoke9-qwen25-7b`
- Remote run dir: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-1650-a8002-state-admission-v2-smoke9-qwen25-7b`
- Packet: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-state-admission-v2-smoke/packet.jsonl`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-state-admission-v2`
- GPU: `7`
- Port: `8072`
- Max tokens: `900`
- Max model len: `16384`
- Temperature: `0`
- Row count: `9`

Launch command:

```bash
RUN_ID=20260618-1650-a8002-state-admission-v2-smoke9-qwen25-7b \
GPU_ID=7 \
PORT=8072 \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
SERVED_MODEL=qwen2.5-7b-state-admission-v2 \
MAX_TOKENS=900 \
RUN_TIMEOUT=1800 \
bash scripts/run_state_admission_v2_a8002.sh
```

Cleanup check: the launcher finished, `predictions.jsonl` has 9 rows, and GPU 7 returned to idle after the script exited.

## Artifacts

- `predictions.jsonl`: model responses.
- `scores.jsonl`: original scorer output from remote run.
- `scores.rescored.jsonl`: local rescoring after adding downstream answer and rejection-reason aliases.
- `scores.option_state.jsonl`: local rescoring after adding `option_state_recall`; the original prompt did not request `option_states`, so this metric is a forward-compatibility baseline for the next schema ablation.
- `summary.md`: original remote summary.
- `summary.rescored.md`: current summary used for interpretation.
- `summary.option_state.md`: same old predictions under the new option-state scorer.
- `run.log`, `runner.stdout.log`, `vllm.log`, `launch.nohup.log`: execution logs.

## Baseline Gate

Local oracle smoke on the same packet reaches:

```text
rows: 9
strict: 1.0000
unit_recall: 1.0000
rejection_recall: 1.0000
scope_violations: 0.0000
absent_unit_violations: 0.0000
downstream_ok: 1.0000
```

Shared-context baseline reaches:

```text
rows: 9
strict: 0.0000
unit_recall: 0.0000
rejection_recall: 0.2222
scope_violations: 7.3333
downstream_ok: 0.6667
```

This means the scorer can distinguish oracle admission from over-shared context on this small packet.

## Model Result

Rescored Qwen2.5-7B result:

```text
rows: 9
strict: 0.0000
unit_recall: 0.2222
rejection_recall: 0.4444
scope_violations: 0.0000
absent_unit_violations: 0.0000
downstream_ok: 0.0000
base: strict=0.0000, unit_recall=0.1111, rejection_recall=0.0000, scope_violations=0.0000, absent_unit_violations=0.0000, downstream_ok=0.0000
perturbation: strict=0.0000, unit_recall=0.2778, rejection_recall=0.6667, scope_violations=0.0000, absent_unit_violations=0.0000, downstream_ok=0.0000
```

## Concrete Diagnosis

The model mostly respected explicit fact-level scope. `scope_violations=0.0000` means it did not simply dump every fact into every role after being shown `eligible_recipients`.

The model did not reliably construct blocker/enabler units. In `hiddenbench_emergency_supply_drop`, it correctly blocked Warehouse A, but treated Warehouse C open service roads as a blocker and still enabled Warehouse B despite the noxious gas fact. The final answer stayed on Warehouse B in all three supply-drop variants.

The model often inverted repair facts. In `hiddenbench_conference_relocation`, it treated the School Gym restroom restoration fact as a blocker, and treated City Library fuel-limit evidence as part of an enabler in one variant. This is a unit-polarity failure around repair and hazard facts.

The model also confused route blockers in the evacuation row. It treated the fire blocking East Town traffic as a West City blocker in one base response, and failed the downstream decision in all variants.

## Caveats

This is a 9-row smoke with one 7B model and one prompt. It should not be used as a model-family claim.

The scorer is still structural. It rewards exact blocker/enabler target option and required fact ids. That is appropriate for this smoke, but future scoring should add a small semantic audit for near-miss rationales.

The prompt may under-specify polarity. A stronger prompt should ask for per-option `blocked`, `enabled`, or `insufficient` status before free-form admission units.

After the reviewer-style adjustment, the scorer now includes `option_state_recall`. The old run scores `0.0000` on that field because the prompt did not ask for `option_states`; use it as a baseline for the next `option_state_first` run, not as a new behavioral claim about this run.

## Next Step

Run a second 9-row smoke with a more constrained option-state schema, then compare Qwen2.5-7B and Qwen2.5-14B. If 14B also inverts blocker/enabler polarity, the packet is exposing a real hidden unit construction pressure. If 14B fixes it with the same schema, V2 should treat 7B as a lower-bound diagnostic rather than the main evidence.
