# Source-Scoped Evidence Admission Compiler v0

Snapshot date: `2026-06-18`.

## 核心判断

`Source-Scoped Evidence Admission Compiler v0` 是当前应冻结的 `Ours` 条件。它的目标是把模型的语义判断、系统的边界执行、最终裁决前的证据充分性检查拆成三个可测层。

工作缩写：

```text
SSEAC-v0
```

中文名：

```text
带来源与作用域的证据准入编译器 v0
```

它要回答的问题是：当事实带有来源、recipient scope、核验状态、拒绝状态和预算时，系统如何决定哪些证据能进入哪个 role 的可见状态，并在证据不足时阻止下游强制作答。

## 方法边界

SSEAC-v0 的定位是答前准入层，范围不覆盖自由文本多 agent 讨论协议。

SSEAC-v0 也不主张发明新的优化算法。它的可检验贡献是分层：模型提出语义偏好和证据槽位，确定性 executor 执行 hard constraints，sufficiency gate 检查最终裁决是否被完整证据支持。

## 目标失败面

SSEAC-v0 主要压力四类失败：

1. `missing_needed`: 必要事实没有进入目标 role。
2. `over_admission`: 不该进入的事实进入了目标 role。
3. `invalid_admission`: rejected、quarantined、unverified 或 out-of-scope 事实被当成支撑。
4. `forced_commitment`: 证据不足时 final decider 仍输出具体答案。

它不把所有 final answer 错误都算作方法失败。若 direct all-facts 或 oracle-admissible-facts 也不稳定，优先诊断 benchmark / task understanding。

## 输入 Schema

### SourceCard

每条信息进入准入层前统一成 source card：

```json
{
  "card_id": "c001",
  "source_id": "agent_a.note_3",
  "source_role": "field_agent",
  "content": "The west bridge is closed after inspection.",
  "recipient_scope": ["planner", "final_decider"],
  "visibility": "private|shared|role_scoped",
  "verification_state": "verified|unverified|rejected|quarantined",
  "evidence_type": "support|blocker|constraint|background|distractor",
  "cost": 1,
  "depends_on": [],
  "conflicts_with": [],
  "provenance": {
    "benchmark": "HiddenBench",
    "case_id": "HBxx",
    "original_field": "..."
  }
}
```

### TaskSpec

每个 task unit 需要显式给出角色、预算、候选答案和证据槽位：

```json
{
  "task_id": "case_001",
  "roles": ["planner", "safety_reviewer", "final_decider"],
  "final_decider": "final_decider",
  "candidate_options": ["A", "B", "insufficient_evidence"],
  "role_budgets": {
    "planner": 6,
    "safety_reviewer": 4,
    "final_decider": 6
  },
  "required_slots": [
    {
      "slot_id": "hazard_status_B",
      "recipient": "final_decider",
      "option": "B",
      "polarity": "blocker",
      "acceptable_card_ids": ["c004"],
      "required_state": "verified"
    }
  ],
  "decision_rule": "choose exactly one enabled option, otherwise insufficient_evidence"
}
```

## 模型输出 Schema

模型只输出候选判断，不直接拥有最终准入权。

```json
{
  "option_states": [
    {
      "option": "A",
      "state": "enabled|blocked|insufficient|conflict",
      "supporting_slots": ["slot_1"],
      "blocking_slots": [],
      "missing_slots": ["slot_2"],
      "rationale": "short"
    }
  ],
  "candidate_units": [
    {
      "unit_id": "u001",
      "recipient": "final_decider",
      "card_ids": ["c001", "c004"],
      "priority": 0.91,
      "claimed_slots": ["hazard_status_B"],
      "claimed_effect": "blocks option B",
      "rationale": "short"
    }
  ],
  "proposed_rejections": [
    {
      "card_id": "c009",
      "recipient": "final_decider",
      "reason": "out_of_scope|unverified|rejected|quarantined|distractor"
    }
  ]
}
```

## Pipeline

### Step 1: Card normalization

Benchmark-specific facts are normalized into `SourceCard` objects. Normalization must preserve original `source_id` and original benchmark case id.

### Step 2: Model semantic proposal

The model reads `SourceCard` and `TaskSpec`, then proposes:

- option states;
- candidate admission units;
- priority;
- claimed evidence slots;
- proposed rejections.

### Step 3: Deterministic admission executor

The executor applies hard constraints:

1. Reject any card whose `recipient_scope` does not include the recipient.
2. Reject any card with `verification_state` in `rejected` or `quarantined`.
3. Treat `unverified` as non-supporting unless the task explicitly allows unverified metadata.
4. Enforce role budget by sorted priority, with deterministic tie-breaking by `card_id`.
5. Enforce closure: a unit with dependencies is admissible only if dependencies are admissible.
6. Preserve source identity; merged units must retain all original `card_id` and `source_id`.
7. Emit an explicit rejection record for every filtered card.

### Step 4: Evidence sufficiency gate

The gate builds a slot table after executor filtering:

```json
{
  "slot_id": "hazard_status_B",
  "recipient": "final_decider",
  "option": "B",
  "status": "satisfied|missing|blocked_by_rejection|not_visible|conflict",
  "satisfying_cards": ["c004"],
  "blocking_reason": null
}
```

Decision rule:

1. An option can be `enabled` only if all required support slots are satisfied and no verified blocker is satisfied.
2. An option is `blocked` if a required blocker slot is satisfied.
3. The final decision may choose a concrete option only when exactly one option is enabled and every required exclusion slot is resolved.
4. If no option is fully enabled, or multiple options remain enabled without a tie rule, final decision becomes `insufficient_evidence`.
5. The gate records whether the model attempted forced commitment.

### Step 5: Output

Final output contains:

```json
{
  "admitted_units": [],
  "rejected_units": [],
  "slot_table": [],
  "final_state": {
    "decision": "A|B|insufficient_evidence",
    "decision_status": "committed|insufficient|conflict",
    "forced_commitment_detected": false
  },
  "metrics_debug": {
    "budget_used": {},
    "scope_violations_prevented": 0,
    "rejected_support_attempts": 0
  }
}
```

## 与 Baseline 的区别

| Condition | 模型做什么 | 系统做什么 | 缺口 |
| --- | --- | --- | --- |
| `direct_admitted_state_generation` | 直接写 admitted state | 只解析和评分 | 容易过度承认、爆预算、漏 rejection |
| `source_ledger_model_only` | 读 source/scope 后自己分配 | 只评分 | 测模型是否自守边界 |
| `priority_plus_executor` | 给 priority 或候选 units | 执行 scope/budget/rejection | 缺少证据充分性闸门 |
| `ours_sseac_v0` | 给 option-state、units、priority、slot claims | 执行 hard constraints + sufficiency gate | 主方法 |
| `oracle_executor` | 使用 gold units / gold slots | 执行 hard constraints + gate | 上界 |

## Benchmark 映射

### PerspectiveGap / PG40

Mapping:

- fragment -> `SourceCard`
- role -> recipient
- official gold assignment -> required recipient scope
- distractor -> `evidence_type=distractor`
- role budget -> `role_budgets`

Primary readout:

- coverage;
- role precision;
- distractor leak;
- budget pass;
- source/scope pass.

PG40 不天然包含 final downstream decision，所以 sufficiency gate 只作为 optional slot proxy。主读数仍然是 routing/admission。

### HiddenBench / HSA-v0

Mapping:

- private/public facts -> `SourceCard`
- final decision options -> `candidate_options`
- hidden profile constraints -> required slots or blocker slots
- sender visibility perturbations -> verification / scope changes
- original final answer -> downstream decision target

Primary readout:

- downstream_ok;
- insufficient-evidence correctness;
- rejected/quarantined support attempts;
- source-card recall;
- fact leak / over-admission.

HSA-v0 是 SSEAC-v0 的关键 downstream pressure。它需要先从 4-case draft 做人工 gold，不应直接扩成大 benchmark。

### State Admission V2

Mapping:

- existing units/cards -> `SourceCard`
- expected option states -> `required_slots`
- perturbation rows -> verification/rejection/scope pressure

Primary readout:

- option_state_recall;
- unit_recall;
- scope violation;
- rejection recall;
- downstream_ok;
- forced commitment.

SA-V2 只作为机制诊断，不承担外部有效性主证据。

### PACT-style Split Evidence

Mapping:

- each evidence document or extracted support sentence -> `SourceCard`
- answer support requirements -> evidence slots
- agents with split context -> source roles or recipients
- final QA answer -> downstream decision

Primary readout:

- evidence recall;
- answer EM/F1;
- irrelevant evidence admission;
- source fidelity;
- token cost.

PACT-pilot 的首要任务是 gold/parser/contact，暂时不做大规模 claim。

## 第一轮 Claim-Bearing Run 预设

推荐第一轮先压 `PG40`，因为它的 scorer 和 source-ledger contact 最成熟。

```text
purpose:
  判断 SSEAC-v0 是否比 source_ledger_model_only 和 priority_plus_executor 更稳定地控制 role-specific evidence admission。

unit:
  PerspectiveGap source-ledger / tight-budget slice 中的一个 scenario-seed row。

primary_contrast:
  ours_sseac_v0 vs source_ledger_model_only。

secondary_contrasts:
  all_to_all / copy_all, direct_admitted_state_generation, priority_plus_executor, oracle_executor。

success_signal:
  coverage 不明显下降，同时 precision、distractor leak、budget pass 或 source/scope pass 至少两个指标改善。

failure_signal:
  Ours 只靠少分发提高 precision，coverage 明显塌掉；或与 priority_plus_executor 无可解释差异。

invalidation_conditions:
  scorer 与旧 source-ledger runs 不兼容；role budget 或 source scope 泄漏到 prompt 的 oracle label；paired baseline rows 不完整；manual audit 发现 gold assignment 不稳定。

expected_artifacts:
  packet under experiments/<run-id>/;
  outputs under experiments/<run-id>/outputs/;
  summary under experiments/<run-id>/summary.md;
  interpretation under reports/<date>-sseac-v0-pg40-pilot.md。
```

## 最小实现任务

1. 写一个 benchmark-agnostic `SourceCard` / `TaskSpec` JSON schema。
2. 写 `compile_sseac_v0.py`，输入模型候选输出，输出 admitted/rejected/slot/final state。
3. 给 PG40 写 adapter：PerspectiveGap fragments -> SourceCard。
4. 给 HSA-v0 写 4-case draft adapter，先人工审核 slots。
5. 改 scorer，让 `ours_sseac_v0` 能和现有 `source_ledger_model_only`、`priority_plus_executor` 同表比较。
6. 只在 local gold smoke 通过后启动 GPU。

## 当前本地实现

已落盘的最小实现入口：

- Schema: `schemas/sseac_v0.schema.json`
- Compiler: `scripts/compile_sseac_v0.py`
- PG40 adapter: `scripts/build_sseac_from_perspectivegap_tight_budget.py`
- Local smoke: `experiments/20260618-local-sseac-v0-compiler-smoke/`
- PG40 oracle adapter smoke: `experiments/20260618-local-sseac-v0-pg40-adapter/`
- PG40 prediction converter diagnostic: `experiments/20260618-local-sseac-v0-pg40-prediction-converter/`

本地 smoke 已通过：

```text
rows: 2
ok_rows: 2
error_rows: 0
invalid_support_prevented: 1
forced_commitment_rate: 0.5
downstream_ok: 1.0
```

这个 smoke 只验证 compiler 骨架，不支撑方法优于 baseline 的 claim。下一步需要写 `PG40` adapter，让 compiler 接 PerspectiveGap source-ledger / tight-budget slice。

`PG40` adapter 已完成 oracle smoke：

```text
rows: 40
ok_rows: 40
error_rows: 0
budget_rejections: 0
downstream_ok: 1.0
```

这里的 `downstream_ok` 是 synthetic routing-complete 检查，只说明 oracle fixture 满足所有 routing slots。它不代表真实下游任务 accuracy。下一步需要把模型 role-card response 转成 SSEAC `candidate_units`。

PG40 prediction converter diagnostic 已完成，见 `reports/20260618-sseac-v0-pg40-prediction-converter.md`。关键读数是 `utility_density_greedy` after SSEAC compiler 达到 `25/40` strict 和 `0.9825` utility ratio，旧 `source_ledger_14b_fullprompt_budget_compiled` 是 `11/40` strict 和 `0.8707` utility ratio。下一步需要专门的 SSEAC prompt proposal，继续复用旧 source-ledger 输出只适合作为诊断。

## Go / No-Go

Go:

- `PG40` 上 SSEAC-v0 比 source-ledger model-only 更少 leak / budget violation，coverage 保持可接受。
- `HSA-v0` 上 SSEAC-v0 能把 rejected/quarantined facts 从支撑链里排除，并在证据不足时输出 insufficient。
- direct all-facts、oracle-admissible 或 oracle-executor controls 显示任务本身可解。

No-go:

- SSEAC-v0 与 `priority_plus_executor` 无稳定差异。
- evidence sufficiency gate 只是在 prompt 上提醒模型谨慎，没有带来 executor 可解释的指标变化。
- `shared_verified_context` 或 `CICL_style_card_packing` 在同一主表中接近 oracle。
- manual audit 显示 HSA-v0 的 slots 人工性太强，无法说服外部读者。

## 当前禁止项

- 不把 SSEAC-v0 写成新范式。
- 不在没有 oracle/control 的情况下报告 Ours 提升。
- 不用单一 final answer 指标评价 SSEAC-v0。
- 不扩 HSA-v0 样本量，直到 4-case slot schema 通过人工审计。
- 不跳过 `priority_plus_executor`，因为它是判断 compiler 是否真正带来增量的关键 baseline。
