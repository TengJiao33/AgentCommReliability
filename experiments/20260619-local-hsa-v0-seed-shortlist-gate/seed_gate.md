# HSA-v0 Seed Shortlist Gate

日期：2026-06-19

## 核心判断

HiddenBench failure seed 池里有 `12` 个推荐 seed。当前已有人工 HSA fact draft 的推荐 seed 有 `12` 个，已经进入 HSA packet 的推荐 seed 有 `12` 个。

推荐 seed 已全量纳入当前 HSA 包。下一步若扩包，应先做 expansion selection gate，从非推荐候选或新增 case 中重新筛选。

## 计数

| 项 | 数量 |
| --- | ---: |
| extracted candidates | `32` |
| recommended seeds | `12` |
| recommended with fact draft | `12` |
| recommended packetized | `12` |
| sanity packetized outside shortlist | `0` |

## 推荐 Seed 状态

| 优先级 | task | name | gold | shared | private | packet rows | 状态 | 下一步 |
| --- | ---: | --- | --- | ---: | ---: | ---: | --- | --- |
| DONE | `3` | evacuation_east_town | East Town | 4 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `5` | baker_2010 | Roberts | 33 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `10` | emergency_supply_drop | Warehouse C | 3 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `11` | emergency_conference_relocation | School Gym | 4 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `12` | evacuate_park_dilemma | Green Valley | 4 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `21` | emergency_transportation_decision | Celestia Airstrip | 3 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `27` | research_station_site_selection | Pine Ridge | 3 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `31` | weather_sensor_deployment | Gamma Lake | 3 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `44` | Choosing the Safe Offsite Venue | Hilltop Retreat | 4 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `51` | emergency_supply_distribution | Charlie Storage | 4 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `54` | island_research_base_choice | Site C | 4 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |
| DONE | `56` | Secure the Masterpiece | The Government Records Vault | 5 | 4 | 3 | `packetized_shortlist_seed` | keep as current HSA packet coverage |

## P0 标注目标

当前没有 P0 推荐 seed 待标注。

## 准入规则

扩 seed 前必须先补人工事实单元和扰动定义。只要缺少 `oracle_admission_units` 或 `expected_downstream_delta`，就不能启动模型真跑。

本 gate 的作用是防止 HSA 从机制表滑回普通 HiddenBench prompt 表。下一轮应先做扩展候选筛选门，再 materialize packet 并做 transparent controls。
