# HiddenBench Failure Seeds For State Admission V0

日期：2026-06-18

## 选择规则

本次只抽取一种 case：

```text
full_info 正确
+ oracle_public_facts 正确
+ old exchange_then_decide 错
+ fact_only_exchange 正确
```

这个条件说明：最终模型在干净事实条件下有能力答对，但旧自由文本 exchange 没有把私有事实稳定转成可用公共状态。它适合做 `Hidden-State Admission v0` 的自然 seed，因为后续可以围绕同一事实集合构造 source、scope、verification、quarantine 和 evidence sufficiency 扰动。

## 汇总

- 候选 case：`32`
- 推荐 v0 seed：`12`
- source records：`experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/records.jsonl`
- case cards：`experiments/20260618-local-hiddenbench-failure-seeds/case_cards.jsonl`

| Failure label | Count |
| --- | ---: |
| `recommendation_leakage` | 32 |
| `shared_overtalk` | 22 |
| `shared_prior_preserved` | 21 |
| `fact_surface_changes_decision` | 32 |
| `private_fact_not_exact` | 31 |

## 推荐 V0 Seeds

| task_id | task_name | gold | old exchange | fact-only | 价值 |
| ---: | --- | --- | --- | --- | --- |
| 3 | evacuation_east_town | East Town | West City | East Town | 同时有推荐污染、共享事实复述、部分私有事实 exact；适合做 scope/quarantine 扰动。 |
| 11 | emergency_conference_relocation | School Gym | City Library | School Gym | 关键负面事实和修复事实被自由文本压扁；适合 evidence sufficiency。 |
| 21 | emergency_transportation_decision | Celestia Airstrip | Borealis Bus Terminal | Celestia Airstrip | 多路线约束，需要完整排除不可行选项。 |
| 44 | Choosing the Safe Offsite Venue | Hilltop Retreat | Riverside Conference Center | Hilltop Retreat | 典型“共享优势吸引 + 私有阻断事实”结构。 |
| 27 | research_station_site_selection | Pine Ridge | Copper Lake | Pine Ridge | 有正向可行性事实和多个候选阻断事实，适合 admission-unit construction。 |
| 31 | weather_sensor_deployment | Gamma Lake | Beta Valley | Gamma Lake | 含未签名/未核验地质 note，可自然构造 verification 扰动。 |
| 51 | emergency_supply_distribution | Charlie Storage | Bravo Storage | Charlie Storage | 供应/道路/冷链事实能拆成 source cards 和 dependency slots。 |
| 54 | island_research_base_choice | Site C | Site B | Site C | 通信修复事实与污染/风险事实并存，适合 source trust 变化。 |
| 56 | Secure the Masterpiece | The Government Records Vault | University Science Building Secure Lab | Government Records Vault | 安全、通行、化学泄漏、电力依赖交织，适合 downstream decision proxy。 |
| 12 | evacuate_park_dilemma | Green Valley | Red Lake | Green Valley | shared-only、old exchange、fact-only 三者分叉明显，适合测试候选答案排除槽位。 |
| 5 | baker_2010 | Roberts | Jones | Roberts | 经典 hidden-profile 风格，信息多且碎；适合测试压缩与事实保真。 |
| 10 | emergency_supply_drop | Warehouse C | Warehouse B | Warehouse C | 已在 State V2 用作自然 seed；适合 quarantine / hazard verification。 |

## 对 V0 Builder 的启发

这些 case 不应直接复制成一个更长的 HiddenBench prompt。更好的做法是把每个 case 拆成：

- `shared_context`: 所有人可见的背景事实。
- `source_cards`: 每条私有事实带 source id、owner role、verbatim fact。
- `recipient_scope`: 哪些事实能进入最终裁决者或特定角色状态。
- `verification_state`: verified、unverified、quarantined、rejected。
- `evidence_slots`: 每个候选答案需要满足的支撑槽位和排除槽位。
- `downstream_decision`: 在当前准入事实下是否能裁决，或应报告证据不足。

最小 v0 不需要很多行。先从 `HB10`, `HB11`, `HB12`, `HB31` 各做 base + perturbation，就能检查 evidence sufficiency 是否真的可测。

## 边界

这不是新模型结果，也不是官方 HiddenBench 分数。它是对已有 full65 run 的离线 case extraction。它支持后续 benchmark 设计，不单独支撑方法 claim。
