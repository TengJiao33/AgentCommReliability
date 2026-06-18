# State Admission V2 Option-State Smoke9 Qwen2.5-7B

日期：2026-06-18

状态：GPU schema ablation run。这个 run 已完成，用来判断 `option_state_first` 是否能把 V2 smoke 的失败从 admission-unit 格式层拆到 option-state 语义层。

## Purpose

上一轮 `unit_first` prompt 让模型直接输出 admission units，Qwen2.5-7B 在 9 行上 `strict=0.0000`、`unit_recall=0.2222`、`downstream_ok=0.0000`。这次只改 prompt/schema：模型先为每个候选答案输出 `blocked`、`enabled` 或 `insufficient`，再输出 admission units 和 final answer。

这个 ablation 的审稿人问题是：第一轮失败主要来自 JSON/unit formatting，还是模型确实在 source-scoped facts 到 option-state matrix 的转换上不稳。

## Launch Record

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Local run dir: `experiments/20260618-1710-a8002-state-admission-v2-option-state-smoke9-qwen25-7b`
- Remote run dir: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-1710-a8002-state-admission-v2-option-state-smoke9-qwen25-7b`
- Packet: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-state-admission-v2-smoke/packet.jsonl`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-state-admission-v2-option-state`
- Prompt style: `option_state_first`
- GPU: `7`
- Port: `8072`
- Max tokens: `1100`
- Max model len: `16384`
- Temperature: `0`
- Row count: `9`

Launch command:

```bash
RUN_ID=20260618-1710-a8002-state-admission-v2-option-state-smoke9-qwen25-7b \
GPU_ID=7 \
PORT=8072 \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct \
SERVED_MODEL=qwen2.5-7b-state-admission-v2-option-state \
PROMPT_STYLE=option_state_first \
MAX_TOKENS=1100 \
RUN_TIMEOUT=1800 \
bash scripts/run_state_admission_v2_a8002.sh
```

Cleanup check: the launcher finished, `predictions.jsonl` has 9 rows, and GPU 7 returned to idle after the script exited.

## Artifacts

- `predictions.jsonl`: model responses under the option-state schema.
- `scores.jsonl`: scorer output with `option_state_recall`.
- `summary.md` and `summary.json`: metric summaries.
- `run.log`, `runner.stdout.log`, `vllm.log`, `launch.nohup.log`: execution logs.

## Baseline Gate

Local oracle on the same packet and option-state scorer reaches:

```text
rows: 9
strict: 1.0000
unit_recall: 1.0000
rejection_recall: 1.0000
scope_violations: 0.0000
absent_unit_violations: 0.0000
downstream_ok: 1.0000
option_state_recall: 1.0000
```

Old `unit_first` 7B predictions under the option-state scorer have `option_state_recall=0.0000`, because that prompt did not request `option_states`. This run is the first behavioral measurement for the new field.

## Model Result

```text
rows: 9
strict: 0.0000
unit_recall: 0.2407
rejection_recall: 0.4444
scope_violations: 0.1111
absent_unit_violations: 0.1111
downstream_ok: 0.2222
option_state_recall: 0.6111
base: strict=0.0000, unit_recall=0.2222, rejection_recall=0.0000, scope_violations=0.0000, absent_unit_violations=0.0000, downstream_ok=0.6667, option_state_recall=0.6667
perturbation: strict=0.0000, unit_recall=0.2500, rejection_recall=0.6667, scope_violations=0.1667, absent_unit_violations=0.1667, downstream_ok=0.0000, option_state_recall=0.5833
```

## Concrete Diagnosis

The ablation changed the failure surface. Compared with `unit_first_7b`, downstream answer accuracy improved from `0.0000` to `0.2222`, and the model now recovers 61.11% of expected option states. That is a real schema effect, but it does not repair the run.

The supply-drop row remains the clearest failure. Across all three variants, the model selects Warehouse B while gold is Warehouse C. It blocks Warehouse A correctly, but treats Warehouse B as enabled despite the gas hazard, and often treats Warehouse C's open service roads as insufficient evidence. This is a direct blocker/enabler polarity error.

The conference row shows a different pattern. The final answer is School Gym in all three variants, and option-state recall reaches `0.5000` to `0.6667`, but the model still admits verification-rejected or scope-ineligible facts into units. This separates answer correctness from admission certificate correctness.

The evacuation row shows why strict remains useful. Two variants have `option_state_recall=1.0000`, but strict is still `0.0000` because the model outputs extra absent units or misses required rejections. Option-state success alone is too weak for this benchmark slice.

## Reviewer-Facing Interpretation

This run weakens the simplest "format artifact" objection. A better schema gives partial recovery, yet the model still makes option-level semantic mistakes and certificate mistakes.

It also weakens any broad claim. A 7B model on 9 rows cannot carry a paper result. The value is diagnostic: it tells us the next experiment should be a model-scale control and direct-answer controls, not a larger same-prompt sample.

## Caveats

The packet still lacks an explicit `expected_option_states` field. The scorer derives option-state gold from `expected_units`. Future packets should materialize that field so external readers can inspect the target matrix without reading scorer code.

This run uses one model size, one prompt style, and three HiddenBench-derived sketches. It should be compared with Qwen2.5-14B and direct-answer controls before any expansion.

## Next Step

Run `option_state_first_14b` on the same 9 rows. If 14B keeps the same polarity and certificate failures, expand the packet. If 14B fixes most failures, keep this 7B result as a lower-bound diagnostic and move effort to stronger baselines.
