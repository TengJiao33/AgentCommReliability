# PG40 直接路由五行结果

日期：2026-06-19

## 核心判断

PG40 direct routing 五行已经补上。结果是 `0/5`，utility `0.0987`，budget pass `0.4000`，coverage 和 precision 都只有 `0.1481`。这条基线很弱，说明直接让 Qwen2.5-14B 在紧预算切片上分配碎片，并不能自然学会角色边界和预算选择。

这个结果对我们有用：它补上了公开切片主表的 direct 行。现在 PG40 五行对照可以更完整地读：direct 很弱，structured no compiler 预算崩，card-unit compiled 有明显修复但仍只有 `1/5`，source-ledger 14B compiled 和透明贪心仍然压住当前方法。

## 证据

运行记录：

| 项 | 内容 |
| --- | --- |
| run id | `20260619-a8002-pg40-direct-routing-limit5-qwen25-14b` |
| 远程 | `A800_2` |
| GPU | `7` |
| 模型 | `Qwen2.5-14B-Instruct` |
| packet | `PG40 tight-budget` 前五行 |
| 输出 | `experiments/20260619-a8002-pg40-direct-routing-limit5-qwen25-14b/` |

主结果：

| 条件 | Strict | Coverage | Precision | Budget pass | Utility | Raw utility |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| direct routing limit5 | `0/5` | `0.1481` | `0.1481` | `0.4000` | `0.0987` | `0.1845` |

解析状态是干净的：五行全部返回可解析 JSON。评分失败的第一次尝试来自 scorer 接口只接受字符串，修复后复用同一预测文件重评成功。

## 机制诊断

direct 的主要问题不是乱收干扰项。distractor leakage 是 `0.0000`，reject recall 是 `1.0000`。真正的问题是它拒掉必要碎片、把碎片送错角色、并且在复杂行上超预算。

逐行看，`pg_000` 两个 seed 都漏掉关键共享或角色碎片，并把必要碎片放进 rejected；`pg_002` 和 `pg_003` 的多角色设置里，模型开始把看起来“语义相关”的长片段塞给 reviewer，导致预算崩和目标角色错配。

## 对主表的影响

当前 PG40 主表应这样读：

| 行 | 当前读数 | 角色 |
| --- | --- | --- |
| direct routing limit5 | `0/5`，utility `0.0987` | 直接提示基线 |
| structured no compiler card-unit | `0/5`，utility `0.1803` | 无编译器结构化输出 |
| card-unit compiled | `1/5`，utility `0.8155` | 当前最好 Ours 五行 |
| source-ledger 14B compiled | `11/40`，utility `0.8707` | 旧机制前身 |
| transparent greedy | `25/40`，utility `0.9825` | 强透明基线 |
| oracle | `40/40` | 上界 |

card-unit compiled 相对 direct 有明显提升，但还没有达到发表标准。它说明 hard executor 和单卡候选粒度有价值；它也暴露出当前 proposal 排序仍不够强。

## 下一步

不要扩 direct。下一步应做预算感知单卡重排或成对排序器，在同五行上和 direct、card-unit compiled、source-ledger 14B compiled 对照。只有超过 `1/5` 且 utility 至少接近 `0.8707`，PG40 才值得扩到更大公开切片。
