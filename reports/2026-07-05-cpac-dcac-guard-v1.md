# CPAC-DCAC 保守翻盘准入 v1 记录

## 核心事实

2026-07-05 对 `scripts/run_cpac_dcac.py` 做了一版保守优化。优化目标不是提高模型能力，而是堵住原始样本调查中已经明确暴露的 DCAC 翻盘漏洞：证书标签和计算文字矛盾、计算式本身错误、证书没有支撑挑战者答案、base notation 等表示风险下仍然硬翻。

这版改动只影响 DCAC 分支的翻盘准入；CPAC 的候选池状态诊断、collapse 分支、无多数冲突分支没有改。

## 代码变化

- `ParsedCertificate` 仍保留原始标签判断：`decision=flip`、多数 `fail`、挑战者 `pass`。
- 新增 guard 级准入：只有原始标签合格，并且没有触发拒绝原因时，证书才计入翻盘票。
- 新增拒绝原因：
  - `blocked_representation_risk:base_notation`
  - `blocked_representation_risk:matrix_or_vector`
  - `label_text_contradiction`
  - `simple_inequality_contradiction`
  - `challenger_answer_not_supported_by_certificate_text`
  - `arithmetic_mismatch_in_calculation`
  - `negated_challenger_text_answer`
  - `missing_condition`
  - `missing_calculation`
- records 中每个 certificate 会写入：
  - `guarded_admissible_flip`
  - `guard_rejection_reasons`
- branch result 中会写入：
  - `raw_admissible_flip_certificates`
  - guard 后的 `admissible_flip_certificates`
  - `guard_rejection_reasons`
- summary 中新增：
  - `dcac_guard_rejected_certificates`
  - `dcac_guard_blocked_flips`

## 本地验证

- `python -m unittest discover -s tests`
  - 36 tests passed.
- `python -m py_compile scripts\run_cpac_dcac.py tests\test_cpac_dcac.py`
  - passed.

新增测试覆盖了四类来自原始调查的坏形态：

- 标签说 flip，但文字承认多数满足、挑战者不满足。
- 显式乘法等式错误，例如 `26*25*10*9 = 625200`。
- 证书计算得到的值没有支撑挑战者答案。
- base notation 表示风险下禁止硬翻。
- 文本分类答案中，证书文字否定挑战者标签时禁止硬翻。

## 旧 records 离线回放

用已有 full run records 的同一批 claim/certificate 做离线回放，不重新调用模型。该回放只回答一个问题：如果旧 run 的 17 次 DCAC 翻盘经过新 guard，哪些翻盘会被挡住。

原 full run 记录内转移：

| 转移 | 原计数 |
| --- | ---: |
| `MaC_to_C` | 310 |
| `MaW_to_W` | 165 |
| `MaW_to_C` | 15 |
| `MaC_to_W` | 10 |

guard v1 离线回放后的反事实计数：

| 转移 | 反事实计数 |
| --- | ---: |
| `MaC_to_C` | 314 |
| `MaW_to_W` | 165 |
| `MaW_to_C` | 15 |
| `MaC_to_W` | 6 |

如果只按旧 records 的转移标签反事实换算，final correct 会从 325/500 变成 329/500。这个数不是新 run 结果，只是同一批证书经过新准入规则后的离线估计。

被挡住的旧 DCAC 翻盘：

| idx | id | 原转移 | 反事实转移 | 主要拒绝原因 |
| ---: | --- | --- | --- | --- |
| 41 | `test/geometry/627.json` | `MaC_to_W` | `MaC_to_C` | 标签/文字矛盾；简单不等式矛盾 |
| 47 | `test/algebra/305.json` | `MaC_to_W` | `MaC_to_C` | 证书没有支撑挑战者答案 |
| 214 | `test/counting_and_probability/765.json` | `MaW_to_W` | `MaW_to_W` | 计算式错误 |
| 307 | `test/precalculus/695.json` | `MaC_to_W` | `MaC_to_C` | 标签未形成有效翻盘；证书没有支撑挑战者答案 |
| 310 | `test/algebra/1842.json` | `MaW_to_W` | `MaW_to_W` | 证书没有支撑挑战者答案 |
| 338 | `test/number_theory/368.json` | `MaC_to_W` | `MaC_to_C` | base notation 表示风险；计算式错误；证书没有支撑挑战者答案 |
| 343 | `test/counting_and_probability/737.json` | `MaW_to_W` | `MaW_to_W` | 计算式错误；证书没有支撑挑战者答案 |

这版 guard 没有挡住旧 records 中 4 个 DCAC 恢复样本，因此离线回放中恢复数保持 15，伤害数从 10 降到 6。

## 这个结果能说明什么

这版改动支持一个很窄的结论：原始调查里发现的若干 DCAC 伤害，确实可以通过工程级一致性检查挡住。它直接针对的是“模型生成的证书标签不可信”这个实现漏洞，而不是解决少数派识别的完整研究问题。

## 这个结果不能说明什么

这个回放不是新 full run。它没有重新生成 claim 或 certificate，也没有检验新提示词会不会改变模型输出分布。因此不能把 329/500 当作正式实验结果。

这版 guard 也没有解决所有 DCAC 伤害。剩余伤害中有括号最小值、复根模平方、conic 分类等样本，需要真正理解题目语义；这些不属于当前工程 guard 能可靠覆盖的范围。

## 当前缺口

DCAC 仍然需要更硬的证书形式。当前 guard 只是拒绝明显不合格的自然语言证书，还没有把候选差异转成可执行验证器。要让 DCAC 成为 claim-bearing 机制，还需要重新设计证书结构和对照实验。
