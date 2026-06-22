# PerspectiveGap full-grid 低分复核

日期：2026-06-19

## 核心判断

这次 `2/440` 不是脚本算错。更准确的判断是：Qwen2.5-14B direct prompt 在 PerspectiveGap 官方 full grid 上有局部 routing 信号，但几乎不能完成 strict exact routing。

scorer 本身可以给满分。我们用同一个 official scorer 跑 full-grid oracle，role assignment 和 prompt writing 都是 `220/220`。

## 复核证据

| 检查 | 结果 |
| --- | --- |
| 官方 scorer 本地重跑 direct predictions | summary 数字一致 |
| 本地重跑 score JSON 与远端 score JSON | 结构完全一致 |
| official full-grid oracle | role assignment `220/220`，prompt writing `220/220` |
| direct predictions | `440` rows，status `ok: 440` |
| upstream commit | `60b1dcaaeeb40619075f6cd8779c47fa4b344391` |

这排除了三类主要 plumbing 风险：远端 scorer 跑错、score 文件损坏、evaluator 本身不给任何样本过。

## role assignment 具体错在哪里

Direct role assignment 的格式其实很稳：`220/220` 都是直接可解析 JSON，role keys 全部匹配，没有 invalid fragment id。

失败来自 fragment set 不精确：

| 项 | 数字 |
| --- | ---: |
| strict pass | `0/220` |
| loose all-role exact rows | `0/220` |
| role instances exact | `155/836` |
| rows with missing and extra | `152` |
| rows with missing only | `57` |
| rows with full coverage but extra only | `11` |
| rows with distractor leak | `54` |

一个具体例子是 `pg_000__seed_1`。gold 要 coder 拿 `f1,f5,f6,f7`，reviewer 拿 `f3,f4,f5`。模型输出 coder `f6,f7`，reviewer `f2,f3,f4,f5`，其中 `f2` 是 distractor。这是可解析的错误答案。

## prompt writing 具体错在哪里

Prompt-writing 也不是 header parser 崩。`218/220` 行找到 exact role headers，`0` 行完全找不到 section。

失败来自 required fragment 没被完整放进对应 role，部分还夹带 extra：

| 项 | 数字 |
| --- | ---: |
| strict pass | `2/220` |
| exact headers | `218/220` |
| role sections exact | `163/836` |
| rows with missing only | `127` |
| rows with missing and extra | `91` |
| rows with distractor leak | `42` |

有些行只输出 `<f3>` 这类 fragment tag，没有粘贴全文。官方 prompt 明确要求 paste FULL block verbatim，所以这类输出按官方规则必须失败。我额外做了非官方 tag salvage：`105` 行含 `<f...>` 标签，但即使把 tag 当选择结果，也没有一行全 role exact。

## 对当前结论的边界

这证明的是 recorded direct baseline 在官方 full grid 上不行。它不证明 Qwen2.5-14B 在更强 prompt、温度控制、role-specific system route 或 no-gold repair 下也做不出来。

所以这条结果的正确用途是当公开基准 direct baseline 和失败面诊断。下一步要压 role assignment route 本身，不能只换 deterministic writer。

## 证据路径

| 证据 | 路径 |
| --- | --- |
| direct run | `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/` |
| score audit | `experiments/20260619-local-perspectivegap-fullgrid-score-audit/` |
| role-to-prompt control | `experiments/20260619-local-perspectivegap-fullgrid-direct-role-to-prompt-qwen25-14b/` |
