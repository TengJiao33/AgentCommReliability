# MCA-T 运行结果分诊

日期：2026-07-06

## Run

远程输出：

```text
A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-text-audit-standard-madmm-aligned-qwen25-7b-full/math500-qwen25-7b-instruct-mca-text-audit-all/
```

配置：

```text
model = /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct
benchmark = MATH500, 500 rows
initial_prompt_style = standard-mad
temperature = 1.0
max_tokens = 4096
cue_k = 2
min_change_certificates = 2
pool_state_scope = all
audit_temperature = 0.2
```

这次 run 没用 `--input-records`，所以是 prompt/config aligned with Standard MAD，不是 same-initial-pool aligned。

## 总结果

```text
initial majority accuracy = 364/500 = 0.728
final accuracy            = 357/500 = 0.714
accepted changes          = 17/500 = 0.034
admissible certificates   = 81/1458 = 0.0556
```

transition：

```text
MaC_to_C = 356
MaC_to_W = 8
MaW_to_C = 1
MaW_to_W = 135
```

关键比率：

```text
correct-majority harm = 8/364 = 0.0220
wrong-majority recovery = 1/136 = 0.00735
```

pool-state split：

```text
collapse:
  279 rows
  no accepted changes
  accuracy = 264/279

minority_bearing:
  134 rows
  10 accepted changes
  7 harms
  0 recoveries
  accuracy = 86/134 -> 79/134

no_majority_conflict:
  87 rows
  7 accepted changes
  1 harm
  1 recovery
  accuracy = 14/87 -> 14/87
```

## Accepted changes 精度

MCA-T 的 accepted changes 数量较少，且正确占比低。

audit gate 产生：

```text
rows with >=1 admissible-change certificate = 46
rows with >=2 certificates = 25
accepted changes with same normalized alternative = 17
```

这 17 次 accepted changes：

```text
useful correction = 1
harmful flip      = 8
wrong-to-wrong    = 8
```

实现里的 normalized alternative 聚合逻辑按设计工作：忽略等于 initial answer 的 alternative，并按 normalized alternative 计票。

certificate validity 是主要误差来源。`parse_audit_certificate` 接受模型自己写的：

```text
<initial>fail</initial>
<alternative>pass</alternative>
```

这等于让同一个模型自证 alternative 更好，没有外部计算校验。

## 具体变化类型

### 1. 正确 majority 被假 certificate 推翻

例子：

- index 120：gold `even`，initial `even`，final `odd`。三个 certificates 声称 odd alternative 通过 parity substitution test。
- index 145：gold `-2`，initial `-2`，final `130496`。两个 certificates 接受 Fibonacci-style alternative，但它不是目标表达式值。
- index 238：gold `-4`，initial `-4`，final `none`。三个 certificates 声称二次方程没有 common root，但它们共享 `-4`。
- index 323：gold `1/3`，initial `1/3`，final `1/2`。两个 certificates 使用错误 cyclic-order probability check。
- index 351：gold `1/16`，initial `1/16`，final `1/8`。两个 certificates 接受错误 cosine-product simplification。

### 2. 错误 majority 基本留在错误状态

136 个 initial-wrong rows 里，只有 9 次 accepted changes，只有 1 次落到 gold。

很多 wrong rows 没有 admissible certificates，或者只有一个 certificate；有些有多个 certificates，但支持不同错误答案，或者支持原来的错误 initial answer，所以 aggregator 保持 initial answer。

### 3. minority_bearing

`minority_bearing` 的结果：

```text
7 harms
0 recoveries
```

cue/audit pipeline 没有区分：

```text
minority 真的有修正
minority 给了诱人的假检查
```

### 4. 运行状态

MCA-T 完整跑完，耗时约 3042 秒，records 写完。

## 结果摘要

当前 MCA-T audit contract 的观测结果：

```text
两个 self-certified reviewers 可以共同推高同一个 hallucinated alternative。
```

变化率低；accepted changes 中 `MaW_to_C=1`、`MaC_to_W=8`、`MaW_to_W=8`。

## 后续方向

下一版 MCA-T 的待测修改：

```text
加入可执行校验、符号/数值 verifier，或独立 verifier branch；
记录 majority override 的证据来源；
单独统计 `minority_bearing` 的 accepted changes。
```
