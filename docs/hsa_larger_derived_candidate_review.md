# HSA 更大派生包候选复核

日期：2026-06-19

现状修正（2026-06-19）：这份复核保留为 HSA 扩包储备。当前对外报告主线优先补 PG40 / PerspectiveGap 公开切片主表，暂不继续构造这些候选的派生包。

## 核心判断

第一批六个候选中，`18`、`22`、`32`、`41`、`52` 若未来恢复扩包，可以进入 fact draft 草稿构造。`59` 先暂缓，原因是 Bravo 的隐藏事实同时包含负面损坏记录和无迟到记录，容易把支撑卡、阻断卡和混合 caveat 混在一起。

这次复核没有启动模型，也没有产生新分数。它只回答一个门禁问题：这些任务能不能写出基础行和两个能让下游变成证据不足的扰动。

## 复核结果

| task | name | gold | 结论 | 理由 |
| ---: | --- | --- | --- | --- |
| `18` | `choosing_base_camp` | `Camp Pinecone` | 通过 | Summit 和 Meadow 都有清晰阻断，Pinecone 有补给支撑和熊风险解除支撑 |
| `22` | `Antarctic Storm Safe Haven` | `Main Base` | 通过 | Retreat 和 Rescue 都有清晰阻断，Main Base 有直接电力、通信、食物支撑 |
| `32` | `critical_vaccine_route` | `Route C (Old Supply Road)` | 通过 | Route A 和 Route B 都有清晰阻断，Route C 有桥梁安全和救援支撑 |
| `41` | `Space Evacuation Decision` | `Mars Colony` | 通过 | Orion 和 Lunar 都有清晰阻断，Mars 有已验证着陆和生命维持支撑 |
| `52` | `mountain_storm_shelter` | `Green Valley Outpost` | 通过 | Blue Lake 和 Red Cliff 都有清晰阻断，Green Valley 有极端天气 shelter 支撑 |
| `59` | `last_minute_move` | `Bravo Moving Co.` | 暂缓 | Alpha 和 Charlie 阻断清楚，但 Bravo 的隐藏事实是混合 caveat，支撑型补全边界不够干净 |

## 逐案草稿方向

### `18` choosing_base_camp

建议角色：`weather_checker`、`supply_checker`、`wildlife_checker`、`final_decider`。

建议证据单元：

| 单元 | 类型 | 事实 |
| --- | --- | --- |
| `camp_summit_avalanche_blocked` | 阻断 | glacier cracks make avalanche possible |
| `camp_meadow_gale_blocked` | 阻断 | revised wind projections make tents unsafe |
| `camp_pinecone_food_enabled` | 支撑 | only Camp Pinecone has emergency food rations |
| `camp_pinecone_bear_risk_cleared` | 支撑 | no recent bear sightings near Camp Pinecone |

建议扰动：

| 扰动 | 改动 | 预期 |
| --- | --- | --- |
| `pinecone_food_unverified` | food rations 事实变为未验证 | 正确答案缺关键支撑，输出证据不足 |
| `summit_glacier_no_final_scope` | glacier cracks 不给最终决策者 | Summit 阻断不完整，输出证据不足 |

### `22` Antarctic Storm Safe Haven

建议角色：`supply_checker`、`route_checker`、`shelter_checker`、`final_decider`。

建议证据单元：

| 单元 | 类型 | 事实 |
| --- | --- | --- |
| `retreat_access_blocked` | 阻断 | ice bridge to Retreat Camp collapsed |
| `retreat_supply_uncertain` | 阻断 | recent supply delivery delayed |
| `rescue_route_blocked` | 阻断 | route to Rescue Outpost fully snowed in |
| `main_base_ready_enabled` | 支撑 | Main Base has power, communications, and rations |

建议扰动：

| 扰动 | 改动 | 预期 |
| --- | --- | --- |
| `main_base_ready_unverified` | Main Base readiness 事实变为未验证 | 正确答案缺关键支撑，输出证据不足 |
| `retreat_bridge_no_final_scope` | Retreat bridge collapse 不给最终决策者 | Retreat 阻断不完整，输出证据不足 |

### `32` critical_vaccine_route

建议角色：`route_safety_checker`、`medical_risk_checker`、`rescue_checker`、`final_decider`。

建议证据单元：

| 单元 | 类型 | 事实 |
| --- | --- | --- |
| `route_a_landslide_blocked` | 阻断 | landslide risk across Route A within 6 hours |
| `route_b_quarantine_blocked` | 阻断 | Route B quarantine forbids transit |
| `route_c_bridge_safe_enabled` | 支撑 | Route C bridge certified safe |
| `route_c_rescue_enabled` | 支撑 | rescue unit available only for Route C |

建议扰动：

| 扰动 | 改动 | 预期 |
| --- | --- | --- |
| `route_c_bridge_unverified` | Route C bridge safety 事实变为未验证 | 正确答案缺关键支撑，输出证据不足 |
| `route_b_quarantine_no_final_scope` | quarantine 事实不给最终决策者 | Route B 阻断不完整，输出证据不足 |

### `41` Space Evacuation Decision

建议角色：`launch_checker`、`life_support_checker`、`destination_checker`、`final_decider`。

建议证据单元：

| 单元 | 类型 | 事实 |
| --- | --- | --- |
| `orion_shuttle_blocked` | 阻断 | docking clamps jammed |
| `orion_oxygen_blocked` | 阻断 | real oxygen lasts only 3 hours |
| `lunar_airlock_blocked` | 阻断 | Lunar Base airlocks cannot fully seal |
| `mars_life_support_enabled` | 支撑 | Mars landing pads and backup life support verified safe |

建议扰动：

| 扰动 | 改动 | 预期 |
| --- | --- | --- |
| `mars_life_support_unverified` | Mars safety 事实变为未验证 | 正确答案缺关键支撑，输出证据不足 |
| `lunar_airlock_no_final_scope` | Lunar airlock damage 不给最终决策者 | Lunar 阻断不完整，输出证据不足 |

### `52` mountain_storm_shelter

建议角色：`route_checker`、`weather_checker`、`shelter_checker`、`final_decider`。

建议证据单元：

| 单元 | 类型 | 事实 |
| --- | --- | --- |
| `blue_lake_bridge_blocked` | 阻断 | bridge to Blue Lake washed out |
| `blue_lake_dam_risk_blocked` | 阻断 | dam release will worsen water levels |
| `red_cliff_wind_blocked` | 阻断 | Red Cliff will be hit directly by structural-damaging winds |
| `green_valley_shelter_enabled` | 支撑 | Green Valley is underground and rated for emergency weather |

建议扰动：

| 扰动 | 改动 | 预期 |
| --- | --- | --- |
| `green_valley_shelter_unverified` | Green Valley emergency rating 事实变为未验证 | 正确答案缺关键支撑，输出证据不足 |
| `blue_lake_bridge_no_final_scope` | bridge washout 不给最终决策者 | Blue Lake 阻断不完整，输出证据不足 |

### `59` last_minute_move

暂缓原因：Alpha 和 Charlie 的阻断可以写清楚，但 Bravo 的关键隐藏事实是“损坏过钢琴，但没有迟到记录”。如果把它标成支撑卡，支撑型窄补全可能会补入带负面含义的卡；如果把它标成阻断卡，gold 又会被削弱。这个任务更适合以后专门测试 mixed caveat，暂不放进下一批主扩包。

## 若未来恢复

若未来需要机制附表或错误定位，再给 `18`、`22`、`32`、`41`、`52` 写 fact draft 和 perturbation draft。每个任务先保持一个基础行和两个扰动行，合计新增 `15` 行。`59` 暂留候选池，等混合证据规则明确后再决定。
