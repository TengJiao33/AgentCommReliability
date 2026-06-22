# HSA-v0 HB12/HB31 扩展包草案

日期：2026-06-19

现状修正（2026-06-19）：这份草案已经被后续 15 行、33 行和 36 行 HSA 诊断链路吸收。当前对外报告主线转向 PG40 / PerspectiveGap 公开切片主表；本报告只作为 HSA 扩包历史记录。

## 核心判断

HB12 和 HB31 已经从 seed gate 进入 HSA-v0 draft packet。新包共 6 行，透明控制闭合：oracle `6/6`，shared-only base `0/2`，all-scoped `6/6` 且 extra final cards `15`。这说明它们能延续 HSA 的两个关键压力：通信必要性和过度准入风险。

这份记录本身只是扩展 HSA 前的 packet gate。后续合并、透明控制和模型真跑已经完成；当前不从这里继续安排 HSA 扩包。

## 证据

产物路径：

- `experiments/20260619-local-hsa-v0-hb12-hb31-draft/README.md`
- `experiments/20260619-local-hsa-v0-hb12-hb31-draft/hb12_hb31_fact_units.draft.json`
- `experiments/20260619-local-hsa-v0-hb12-hb31-draft/hb12_hb31_perturbations.draft.json`
- `experiments/20260619-local-hsa-v0-hb12-hb31-draft/packet/hsa_v0_packet.jsonl`
- `experiments/20260619-local-hsa-v0-hb12-hb31-draft/dry_run_constraint_recall.jsonl`

透明控制：

| Control | Strict | Base strict | Perturb strict | Slot recall | Extra final cards |
| --- | ---: | ---: | ---: | ---: | ---: |
| oracle_admissible_facts | `6/6` | `1.0000` | `1.0000` | `0.8500` | `0` |
| shared_only_verified | `4/6` | `0.0000` | `1.0000` | `0.2250` | `15` |
| all_scoped_verified | `6/6` | `1.0000` | `1.0000` | `0.8500` | `15` |

dry-run prompt 共 6 行，长度 `8115` 到 `8380` 字符，未命中 evaluator-only 字段。

## 机制解释

HB12 主要压路线排除：Red Lake 需要 sinkhole blocker，Blueberry Ridge 需要 power/access blockers，Green Valley 需要 emergency-opening support。它适合检查 blocker completion 是否能补齐成组选项排除。

HB31 主要压 verification 和 support 边界：Beta Valley 需要 bridge blocker，Alpha Ridge 需要 wind blocker，Gamma Lake 需要 boat access support；同时有一个 unsigned geology note，应该被记录为不可靠 concern，不能当作 verified blocker。

这两行比继续扩当前三 seed 更有价值，因为它们能分别测试补全器的两个风险：漏掉必要 blocker，以及把未核验证据误收进最终状态。

## 边界

HB12/HB31 是人工草案，还需要合并后再跑一次完整透明控制。HB12 的 Blueberry blocker 是否必须同时要求 power 和 bridge 两张卡，需要在 15 行包前复核一次。当前结果只能证明 draft packet 形状可用。

## 后续状态

这条分支后续已经推进到 HSA 15 行、33 行和 36 行诊断。当前暂停继续扩包；若未来恢复，只服务机制附表、错误定位或案例解释。
