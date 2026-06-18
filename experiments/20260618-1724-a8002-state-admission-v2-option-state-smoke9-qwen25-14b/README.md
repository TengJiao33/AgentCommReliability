# State Admission V2 Option-State Smoke9 Qwen2.5-14B

日期：2026-06-18

状态：GPU model-scale control run。这个 run 已完成，用来和 `option_state_first_7b` 对照，判断 V2 smoke 的失败是否主要来自 7B 能力边界。

## Purpose

这次 run 使用同一 9 行 packet、同一 `option_state_first` prompt、同一 scorer，只把模型从 Qwen2.5-7B 换成 Qwen2.5-14B。

审稿人问题是：如果模型规模增加后 option-state matrix 明显恢复，但 strict 仍然低，主断点就不该再写成“不会判选项状态”，而应拆成 option-state、admission unit、rejection certificate 和 downstream admissibility 四层。

## Launch Record

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Local run dir: `experiments/20260618-1724-a8002-state-admission-v2-option-state-smoke9-qwen25-14b`
- Remote run dir: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-1724-a8002-state-admission-v2-option-state-smoke9-qwen25-14b`
- Packet: `/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-state-admission-v2-smoke/packet.jsonl`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-state-admission-v2-option-state`
- Prompt style: `option_state_first`
- GPU: `7`
- Port: `8072`
- Max tokens: `1100`
- Max model len: `16384`
- Temperature: `0`
- Row count: `9`

Launch command:

```bash
RUN_ID=20260618-1724-a8002-state-admission-v2-option-state-smoke9-qwen25-14b \
GPU_ID=7 \
PORT=8072 \
MODEL_PATH=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
SERVED_MODEL=qwen2.5-14b-state-admission-v2-option-state \
PROMPT_STYLE=option_state_first \
MAX_TOKENS=1100 \
RUN_TIMEOUT=1800 \
bash scripts/run_state_admission_v2_a8002.sh
```

Cleanup check: `predictions.jsonl` has 9 rows, the launcher finished, and GPU 7 returned to idle after the script exited.

## Artifacts

- `predictions.jsonl`: model responses.
- `scores.jsonl`: remote scorer output.
- `scores.local_rescore.jsonl`: local rescore after scorer compatibility update.
- `summary.md` and `summary.local_rescore.md`: metric summaries.
- `summary.json`: machine-readable summary.
- `run.log`, `runner.stdout.log`, `vllm.log`, `launch.nohup.log`: execution logs.

## Model Result

Local rescore matches the remote summary:

```text
rows: 9
strict: 0.1111
unit_recall: 0.5926
rejection_recall: 0.5556
scope_violations: 0.0000
absent_unit_violations: 0.1111
downstream_ok: 0.4444
option_state_recall: 0.9259
base: strict=0.0000, unit_recall=0.5556, rejection_recall=0.0000, scope_violations=0.0000, absent_unit_violations=0.0000, downstream_ok=1.0000, option_state_recall=0.8889
perturbation: strict=0.1667, unit_recall=0.6111, rejection_recall=0.8333, scope_violations=0.0000, absent_unit_violations=0.1667, downstream_ok=0.1667, option_state_recall=0.9444
```

Compared with Qwen2.5-7B under the same schema, `option_state_recall` rises from `0.6111` to `0.9259`, `unit_recall` from `0.2407` to `0.5926`, and `downstream_ok` from `0.2222` to `0.4444`. Strict remains low at `0.1111`.

## Concrete Diagnosis

The 14B model usually recovers the option-state matrix. Supply-drop base is fully correct at the option-state and unit layers, and final answer is Warehouse C. The remaining base strict failures come from missing expected rejections or imperfect unit roles, not from answer choice.

Perturbations expose the harder object. In `hb10_c_enabler_no_final_scope`, the model outputs the correct units and recognizes that Warehouse C's enabler is not visible to `final_decider`, but still answers Warehouse C. This is an admissibility-to-decision failure.

In `hb11_school_repair_quarantined`, the model rejects the quarantined repair fact, but still outputs an absent School Gym enabler and answers School Gym. That is a certificate inconsistency: the rejection and final state disagree.

In evacuation variants, option states are often correct, but units omit required recipient roles or include option units that should be absent under the perturbation. The model can describe the decision surface while failing the certificate contract.

## Reviewer-Facing Interpretation

This run weakens the “only 7B is weak” objection, but it also narrows the claim. The strongest current signal is not that models cannot find the right option state. The stronger signal is that even when a larger model nearly recovers option states, it can fail to maintain consistency among source/scope admissibility, admission units, rejections, and final decider state.

That is a more defensible benchmark object than a broad communication-protocol claim. It also demands direct-answer controls before expansion, because some perturbation rows intentionally make the original gold answer unavailable to the final decider.

## Caveats

This is still a 9-row smoke. The model-scale contrast is useful for diagnosis, but it should not be treated as a stable model-family estimate.

`strict` combines several contracts: option state, unit construction, rejection, scope, absent units, and downstream state. Reports should show component metrics before using strict.

The current packet was generated before `expected_option_states` became an explicit field. The scorer remains backward compatible, and future materialized packets should expose that gold matrix directly.

## Next Step

Run direct-answer controls on the same 9 rows:

- `direct_answer_all_facts_14b`: all facts are available; checks whether the underlying HiddenBench decision is semantically easy for the model.
- `direct_answer_admissible_facts_14b`: only oracle-admitted final-decider facts are available; checks whether perturbation rows are genuinely insufficient under the admission story.

Only after those controls should this packet expand beyond 9 rows.
