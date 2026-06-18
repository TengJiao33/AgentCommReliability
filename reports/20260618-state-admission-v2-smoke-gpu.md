# State Admission V2 GPU Smoke

日期：2026-06-18

## 核心判断

这次终于上了 GPU。结果给了一个清楚但很早期的信号：Qwen2.5-7B 在 9 行 V2 smoke 上能遵守显式 recipient scope，却不能稳定从事实中构造正确的 blocker/enabler admission units。当前证据支持继续压 hidden unit construction，但还不支持方法级结论。

## 证据链

本地先物化了 `experiments/20260618-local-state-admission-v2-smoke/packet.jsonl`，包含 3 条 HiddenBench row，每条 1 个 base variant 和 2 个 same-text source/scope perturbations。Oracle baseline 在重算后达到 `9/9` strict、`unit_recall=1.0000`、`rejection_recall=1.0000`、`downstream_ok=1.0000`。Shared-context baseline 是 `0/9` strict，平均 `scope_violations=7.3333`。

GPU run 是 `experiments/20260618-1650-a8002-state-admission-v2-smoke9-qwen25-7b/`。模型是 `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`，A800_2 GPU 7，temperature 0，9 rows 全部完成，runner 正常退出，GPU 已释放。

重算后的模型结果是 `strict=0.0000`、`unit_recall=0.2222`、`rejection_recall=0.4444`、`scope_violations=0.0000`、`downstream_ok=0.0000`。Base rows 的 `unit_recall` 只有 `0.1111`，perturbation rows 是 `0.2778`。

## 机制解释

这个 run 的主要信号不是 over-sharing。模型输出的 `admitted_facts` 基本守住了 `eligible_recipients`，所以 `scope_violations=0.0000`。这说明显式字段能约束 fact-level admission。

真正断在 unit construction。Supply-drop row 里，模型能挡掉 Warehouse A，但把 Warehouse C 的 open service roads 写成 blocker，并在 noxious gas 已验证时继续选择 Warehouse B。Conference row 里，模型把 School Gym restroom restoration 这种 repair fact 写成 blocker，也把 City Library fuel-limit evidence 混进 enabler。Evacuation row 里，它把 East Town fire blocker 错接到 West City。

## 对论文故事的影响

这个结果让 V2 的问题更具体。V1.1 ledger-first collapse 说明模型不会从 source ledger 自己恢复 bundle/group；V2 smoke 进一步提示，即使把 facts、verification 和 eligible recipients 显式给出，7B 也可能守住准入边界但搞错 admission unit 的语义极性。这个切口比“模型不会路由信息”更窄，也更像可被 packet 和 baseline 压住的机制问题。

外部压力下，这仍然避开 shared context、CICL-style card packing、PerspectiveGap role assignment 和 ProvenanceGuard answer verification 的正面重叠。它关注的是答前、接收者局部、带 verification/scope/rejection certificate 的事实单元构造。

## 失败和边界

这不是一个可发表结果。样本只有 9 行，模型只有 Qwen2.5-7B，prompt 也可能没有充分要求 per-option polarity。当前结果只能说明这个 smoke 暴露了一个可诊断失败面。

Scorer 仍偏结构化。它要求 target option、unit type 和 fact ids 对齐，这对 smoke 是合理的，但下一轮应该对 near-miss rationale 做人工抽样，防止把格式偏差误读成机制失败。

## 下一步压力测试

下一步应做第二个 GPU smoke，而不是扩大样本。把 prompt/schema 改成先输出每个 option 的 `blocked/enabled/insufficient` 状态，再输出 admission units。然后用同一 9 行对比 Qwen2.5-7B 和 Qwen2.5-14B。若 14B 在同一 schema 下仍然出现 polarity 错接，这个方向更值得扩到 30-50 行；若 14B 明显修复，7B run 应作为 lower-bound diagnostic 保留。
