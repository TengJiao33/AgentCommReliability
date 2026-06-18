# State Admission V2 Abstention-Explicit Smoke9 Qwen2.5-14B

日期：2026-06-18

状态：GPU schema ablation run。这个 run 已完成，用来测试显式最终裁决闸门能否修复扰动行里的强制作答倾向。

## Purpose

上一轮 `option_state_first` 显示，Qwen2.5-14B 大多能恢复候选答案状态，但在扰动行中仍倾向给出原始答案。这个 run 加入显式 `final_decider_gate`：只有唯一候选答案可行，且其他候选都被最终裁决者可见的已核验事实排除时，才允许输出答案。

这个 run 的问题是：强制模型先写“唯一可行答案”检查，是否足以把扰动行从强制作答拉回证据不足。

## Launch Record

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Local run dir: `experiments/20260618-1848-a8002-state-admission-v2-abstention-explicit-smoke9-qwen25-14b`
- Remote run dir: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-1848-a8002-state-admission-v2-abstention-explicit-smoke9-qwen25-14b`
- Packet: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-state-admission-v2-smoke/packet.jsonl`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-state-admission-v2-abstention-explicit`
- Prompt style: `abstention_explicit`
- GPU: `7`
- Port: `8072`
- Max tokens: `1200`
- Max model len: `16384`
- Temperature: `0`
- Row count: `9`

Launch command:

```bash
RUN_ID=20260618-1848-a8002-state-admission-v2-abstention-explicit-smoke9-qwen25-14b \
GPU_ID=7 \
PORT=8072 \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
SERVED_MODEL=qwen2.5-14b-state-admission-v2-abstention-explicit \
PROMPT_STYLE=abstention_explicit \
MAX_TOKENS=1200 \
RUN_TIMEOUT=1800 \
bash scripts/run_state_admission_v2_a8002.sh
```

Execution caveat: one aborted launch expanded `RUN_ID` incorrectly and wrote only partial logs to the remote default directory `experiments/20260618-a8002-state-admission-v2-smoke9-qwen25-7b`. It was stopped before producing predictions. The run recorded here is the corrected run id above.

Cleanup check: `predictions.jsonl` has 9 rows, the launcher finished, and GPU 7 returned to idle after the script exited.

## Artifacts

- `predictions.jsonl`: model responses under the abstention-explicit schema.
- `scores.jsonl`: remote scorer output.
- `scores.local_rescore.jsonl`: local rescore; it matches the remote summary.
- `summary.md` and `summary.local_rescore.md`: metric summaries.
- `summary.json`: machine-readable summary.
- `run.log`, `runner.stdout.log`, `vllm.log`, `launch.nohup.log`: execution logs.

## Preflight Gate

Local dry-run prompt materialization:

```text
rows=9
prompt chars min=6908 max=7323 avg=7064.2
forbidden-field leaks=0
```

Oracle predictions under the same scorer still reach:

```text
strict=1.0000
unit_recall=1.0000
rejection_recall=1.0000
scope_violations=0.0000
absent_unit_violations=0.0000
downstream_ok=1.0000
option_state_recall=1.0000
```

## Model Result

```text
rows: 9
strict: 0.1111
unit_recall: 0.5741
rejection_recall: 0.5556
scope_violations: 0.0000
absent_unit_violations: 0.1111
downstream_ok: 0.4444
option_state_recall: 0.8148
base: strict=0.0000, unit_recall=0.6667, rejection_recall=0.0000, scope_violations=0.0000, absent_unit_violations=0.0000, downstream_ok=1.0000, option_state_recall=0.8889
perturbation: strict=0.1667, unit_recall=0.5278, rejection_recall=0.8333, scope_violations=0.0000, absent_unit_violations=0.1667, downstream_ok=0.1667, option_state_recall=0.7778
```

Compared with `option_state_first_14b`, strict stays at `0.1111`, downstream stays at `0.4444`, and option-state recall drops from `0.9259` to `0.8148`.

## Concrete Diagnosis

The explicit gate fixes one perturbation: `hb10_b_hazard_quarantined` now sets `gate_passes=false`, answers null, and reaches strict success.

Most perturbations still force a choice. In `hb10_c_enabler_no_final_scope`, the model admits the Warehouse C enabler only to `logistics_planner`, but its gate still marks Warehouse C as enabled for final_decider and answers Warehouse C.

The conference perturbations show certificate inconsistency. In `hb11_school_repair_quarantined`, the model rejects the School Gym repair fact, then still uses that same fact in an enabled School Gym unit and passes the gate.

The evacuation perturbations show visibility reconstruction failure. In `hb01_west_bridge_unverified`, the model rejects the unverified West City route fact, but substitutes or cites hidden route facts and still passes the gate. In `hb01_north_hill_split_scope_no_group_edge`, it treats split-scope North Hill facts as a complete final-decider blocker.

## Interpretation

This run weakens the hypothesis that one stronger natural-language abstention instruction is enough. The model can fill the gate field, but it often computes the gate over the wrong admissible evidence set.

The next pressure point should therefore move from natural-language final checks to explicit materialized views: provide or require a `final_decider_visible_verified_facts` table, then force option states to cite only that table. If the model still force-chooses after that, the evidence for an admissible-state consistency failure becomes stronger.

## Caveats

This is still a 9-row diagnostic slice. It should not be used as a stable model estimate.

The scorer ignores `final_decider_gate` directly and scores the downstream state, units, rejections, scope, absent units, and option states. Manual inspection of the gate is therefore required for the diagnosis above.

The prompt is longer than the previous option-state prompt, which may partly explain the lower option-state recall.

## Next Step

Build a stricter schema that either materializes the final-decider visible facts in the prompt or requires the model to output that set before option states. The key test is whether errors remain after the admissible evidence set is made explicit as a table.
