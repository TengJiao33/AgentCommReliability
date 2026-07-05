# CPAC-DCAC MATH-500 full 诊断记录

## 核心事实

2026-07-05 跑完了 CPAC+DCAC 在 MATH-500 full split 上的第一轮完整诊断。Qwen2.5-7B-Instruct、500 题、3 initial agents、3 reviewers、no-majority action 为 `listwise`，DCAC 翻盘规则为至少 2 个 admissible flip certificates。同一次 run 内，initial majority 为 320/500，CPAC+DCAC final 为 325/500，净增 5 题，即 +1.0 pp。

## 证据来源

- Run record: `experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/README.md`
- Summary: `experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- Records: `experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- Log: `experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/run_remote.nohup.log`

## 结果

| Readout | Correct | Accuracy |
| --- | ---: | ---: |
| Same-run initial majority | 320/500 | 0.640 |
| CPAC+DCAC final | 325/500 | 0.650 |

| Metric | Value |
| --- | ---: |
| Pool states: collapse / minority / no-majority | 220 / 189 / 91 |
| Actions: keep / DCAC / listwise | 220 / 189 / 91 |
| Valid directional claims | 65 |
| DCAC flips | 17 |
| Answer changed | 52/500 |
| Wrong-majority recoveries | 15 |
| Correct-majority harms | 10 |
| Final ties | 5/500 |
| Final parse failures | 0/500 |
| Representation-risk cases | 148/500 |

## 分支诊断

| Branch | n | MaW -> C | MaC -> W | Net |
| --- | ---: | ---: | ---: | ---: |
| keep initial / collapse | 220 | 0 | 0 | 0 |
| DCAC | 189 | 4 | 8 | -4 |
| listwise discriminant | 91 | 11 | 2 | +9 |

这轮最重要的机制事实是：净增益主要来自 `unique=3` / no-majority conflict 的 listwise 分支，而不是 DCAC。DCAC 分支 17 次 flip 中只有 4 次恢复、8 次伤害、5 次 wrong-to-wrong，当前证书提示和准入规则还没有把 correct minority 与 seductive wrong minority 分开。

## 诊断

这轮支持 CPAC 外层状态拆分是可运行、可观测的：500 题被分到 collapse、minority-bearing、no-majority conflict 三种状态，branch-level 转移也能被记录和解释。尤其是 no-majority conflict 不再被全部当作 tie 放掉，listwise 分支在当前设置下贡献了正净值。

这轮不支持当前 DCAC 作为有效 minority flip 机制。它比原 CQG 更保守，但 flip precision 仍不够，且伤害多于恢复。当前结果更像是在说“候选池状态控制器有价值”，而不是“证书化 minority 翻盘已经成功”。

## 外部基线关系

CPAC+DCAC final 325/500 只比 same-run initial majority 高 5 题，低于同项目已有 CQG full 的 337/500，也低于 basic MAD direct baseline 的 347/500 和 MAD-MM `naive` 的 375/500。这些 run 的 prompt、temperature、round 数和聚合方式不同，不能做严格方法优劣证明；但它们说明当前 CPAC+DCAC 不是最强绝对系统。

## 边界和缺口

当前结果是 diagnostic evidence，不是方法 claim。主要 caveat 有三点：一是 evaluator 仍有 base notation、矩阵/向量、函数表达式等 representation-risk 问题；二是 DCAC 的 certificate 由同一模型生成和裁决，可能只是把错误 minority 包装成结构化证书；三是 listwise 分支虽有正信号，但它的增益可能来自重新求解，而不一定来自真正的 discriminant certificate。
