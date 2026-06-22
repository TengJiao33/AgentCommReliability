# HSA 更大派生包预飞行

日期：2026-06-19

现状修正（2026-06-19）：当前对外报告主线优先补 PG40 / PerspectiveGap 公开切片主表。HSA 更大派生包暂停推进；本文件保留为未来机制附表或错误定位需要时的扩包门禁。

## 核心判断

当前三十六行包已经覆盖全部 `12` 个推荐 seed。若未来扩 HSA，不能继续沿旧推荐队列补标注；应先开扩展候选筛选门，从非推荐候选或新增 case 中选一批能保持 HSA 机制压力的任务。

目标是保持同一个机制压力，避免只追求行数。更大包必须继续测同一个问题：模型提出候选证据后，硬准入和支撑型窄补全能否在基础行补足证据，并在扰动行保持证据不足。

## 已确认状态

| 项 | 当前状态 |
| --- | --- |
| 推荐 seed 总数 | `12` |
| 推荐 seed 已有 fact draft | `12` |
| 推荐 seed 已进入 packet | `12` |
| 推荐 seed 待标注 | `0` |
| 当前 HSA packet | `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl` |
| 当前 seed gate | `experiments/20260619-local-hsa-v0-seed-shortlist-gate/seed_gate.md` |

这意味着若未来恢复扩包，第一动作应是候选筛选；直接构造 packet 或启动 GPU 都应后置。

## 候选筛选标准

优先选择满足以下条件的任务：

| 标准 | 目的 |
| --- | --- |
| 候选答案 `3` 到 `4` 个 | 保持下游选择结构清楚 |
| 共享事实 `3` 到 `5` 条 | 保持共享背景可控 |
| 私有事实 `3` 到 `4` 条 | 保持多来源通信必要性 |
| 平均私有事实长度不超过 `180` 字符 | 避免下一批先被提示长度主导 |
| 至少一个可构造阻断扰动 | 检查硬准入能否拒绝错误承诺 |
| 至少一个可构造支撑扰动 | 检查支撑型窄补全是否过补 |

人工复核时还要排除三类任务：答案别名太多、事实需要外部常识才能判断、候选之间只差措辞没有清晰证据槽。

## 初步候选池

以下候选来自刷新后的 `seed_gate_rows.csv`，只按结构可控性排序，还没有人工写 fact units。

| task | name | gold | shared | private | answers | avg private chars | 初步用途 |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| `18` | `choosing_base_camp` | `Camp Pinecone` | 4 | 4 | 3 | 137.5 | 路线/补给/天气混合压力 |
| `22` | `Antarctic Storm Safe Haven` | `Main Base` | 4 | 4 | 3 | 136.0 | 安全避难和通路阻断 |
| `32` | `critical_vaccine_route` | `Route C (Old Supply Road)` | 4 | 4 | 3 | 156.2 | 路线可达性和隔离风险 |
| `41` | `Space Evacuation Decision` | `Mars Colony` | 4 | 4 | 3 | 139.8 | 可用目的地和生命维持阻断 |
| `52` | `mountain_storm_shelter` | `Green Valley Outpost` | 4 | 4 | 3 | 157.5 | 天气、桥梁、避难能力 |
| `59` | `last_minute_move` | `Bravo Moving Co.` | 4 | 4 | 3 | 155.2 | 供应商可用性和风险权衡 |
| `47` | `Find the Missing Prototype` | `CEO's Office` | 4 | 4 | 3 | 167.8 | 位置证据和排除证据 |
| `14` | `lunch_group_decision` | `Restaurant C` | 3 | 4 | 3 | 137.0 | 卫生、可用性和过敏风险 |
| `15` | `artifact_safe_haven` | `Downtown Police Station` | 3 | 4 | 3 | 154.5 | 安全保管和通路阻断 |
| `38` | `storm_recovery_clinic_site_selection` | `Site C (Hilltop park)` | 4 | 4 | 4 | 140.8 | 场地选择和灾害排除 |
| `46` | `emergency_evacuation_center_choice` | `Riverside School Gym` | 5 | 4 | 3 | 134.0 | 疏散中心可用性 |

第一批已经完成初步人工复核：`18`、`22`、`32`、`41`、`52` 通过，`59` 暂缓。复核细节见 `docs/hsa_larger_derived_candidate_review.md`。

## 预飞行门

进入 packet 构造前，每个新任务必须满足：

| 检查 | 要求 |
| --- | --- |
| source cards | 每条共享和私有事实都有稳定 `card_id`、来源、范围、验证状态和证据类型 |
| oracle units | 基础行能用可见已验证卡片支撑正确答案 |
| rejections | 至少列出一个被阻断的错误候选 |
| perturbation A | 能让某张关键支撑卡变成未验证或不可见 |
| perturbation B | 能让某张阻断卡或范围条件缺失 |
| scorer | 理想准入能闭合，扰动行目标是证据不足 |
| prompt leak | 物化提示不出现评测专用字段 |

只要其中一项缺失，该任务停在候选池，不进入远程运行。

## 若未来恢复

1. 为通过复核的 `18`、`22`、`32`、`41`、`52` 补 fact draft 和 perturbation draft。
2. 暂缓 `59`，等混合证据规则明确后再决定。
3. 构造一个增量包，先做透明控制：理想准入、只给共享信息、全范围信息。
4. 若透明控制闭合，再用 GPU 7 跑同一提示契约。
5. 同表报告模型直出、硬准入、阻断补全和支撑型窄补全。

## 停止条件

若第一批候选中多数无法写出清晰扰动，扩包应暂停，转向新增 case 采样。若透明控制无法区分共享信息下界和全范围上界，扩包应暂停，回到任务构造。若支撑型窄补全在扰动行产生错误承诺，组件降级为诊断工具。
