# HSA-v0 种子短表准入门

日期：2026-06-19

## 核心判断

修正说明：这份报告最初对应九行 HSA 阶段，当时仅有 HB10 和 HB11 进入 packet。当前 seed gate 已刷新到三十六行状态：12 个推荐 HiddenBench seed 已经全部有人工 fact draft，并全部进入当前 HSA packet。再后续的候选复核已经完成，但 HSA 扩包现在暂停；对外报告主线转向 PG40 / PerspectiveGap 公开切片。

这一步把 HSA 的扩展压力从“继续跑模型”压回“先补可评分 seed”。这是好事，因为它能防止我们把普通 HiddenBench 选择题误当成 admission 机制实验。

## 证据

审计产物在：

- `experiments/20260619-local-hsa-v0-seed-shortlist-gate/README.md`
- `experiments/20260619-local-hsa-v0-seed-shortlist-gate/seed_gate.md`
- `experiments/20260619-local-hsa-v0-seed-shortlist-gate/seed_gate_rows.csv`
- `experiments/20260619-local-hsa-v0-seed-shortlist-gate/seed_gate_summary.json`

审计结果：

| 项 | 数量 |
| --- | ---: |
| extracted candidates | `32` |
| recommended seeds | `12` |
| recommended with fact draft | `12` |
| recommended packetized | `12` |
| recommended unpacketized | `0` |
| sanity packetized outside shortlist | `0` |

推荐 seeds 已经被当前三十六行 HSA packet 全量覆盖。HB12 和 HB31 是历史 P0 扩展目标，已经进入 15 行扩展包；HB05 `baker_2010` 已经作为 P2 长档案任务进入三十六行包。

## 历史 P0 的作用

HB12 `evacuate_park_dilemma` 的 gold 是 `Green Valley`。它有四条 shared facts 和四条 private facts，主要机制是路线排除：Red Lake 受 sinkhole 阻断，Blueberry Ridge 同时有断电和桥梁坍塌，Green Valley 的 pest closure 只影响游客。它适合测试 blocker completion 和 shared temptation。

HB31 `weather_sensor_deployment` 的 gold 是 `Gamma Lake`。它的机制更贴近当前补全器边界：Beta Valley 有桥梁坍塌，Alpha Ridge 有未签名地质 note 和急风阻断，Gamma Lake 有船只可达路径。它适合测试 verification 边界和 support completion。

## 对论文故事的影响

HSA 的当前最强诊断已经推进到三十六行：模型直出 `16/36`，硬准入 `34/36`，支撑型窄补全后硬准入 `36/36`，extra final cards `42`。seed gate 的当前作用也变了：它不再指向推荐 seed 补标注，而是提醒下一轮扩包要重新筛候选，先补人工 gold 层：source cards、oracle units、rejections、base variant、perturbations。

候选 `18/22/32/41/52/59` 的人工复核后来已经完成，其中 `18/22/32/41/52` 通过，`59` 暂缓。这个分支当前只作为 HSA 机制扩展储备，不作为对外报告主线。

## 下一步

1. 保留本报告作为 HSA seed gate 历史记录。
2. 公开基准主表优先，先补 PG40 / PerspectiveGap 同模型对照。
3. HSA 扩包只在需要机制附表或错误定位时恢复。
