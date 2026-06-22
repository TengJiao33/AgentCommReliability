# 自有结果附表地图

Snapshot date: `2026-06-18`.

机器可筛选版本见 `docs/appendix_owned_results_rows.csv`。

## 核心判断

主表已经优先承接 `State Admission V1.1`、`PG40 tight-budget`、`HSA-v0` 三条线。剩下的大量自有结果仍然有价值，但它们的价值主要在附表层：提示 output contract 风险、gold/parser 风险、operator uptake 机制、retention/compression 失败面，以及 benchmark 选择如何改变 method ranking。

这些结果不该继续散在归档里。它们也不该挤进主表抢主张。更合适的位置是三张附表：`Output Contract Warning`、`Mechanism Microscope`、`Historical Baseline Map`。

## 附表 A：Output Contract Warning

| Family | Result | Metric | 读法 | 附表位置 |
| --- | --- | --- | --- | --- |
| PACT | HotpotQA50 final-answer contract | EM `17/50 -> 34/50`; F1 `0.508 -> 0.792`; wrong-to-right `20`; right-to-wrong `3` | final-answer surface 可以大幅改变分数，后续 PACT-style pilot 不能只看最终字符串 | output contract warning |
| PACT | HotpotQA offset50 final-answer contract | EM `26/50 -> 28/50`; F1 `0.6469 -> 0.7427`; wrong-to-right `6`; right-to-wrong `4` | 邻近 slice 的收益小很多，说明 contract gain 不稳定 | output contract warning |
| Peer-redacted evidence | redacted vs auto evidence | leakage `16/44 -> 8/44`; wrong redacted evidence right-to-wrong `4` vs wrong auto `1` | 移除答案字符串会降低显式泄漏，但错误结构仍可能影响 receiver | redaction warning |

## 附表 B：Mechanism Microscope

| Family | Result | Metric | 读法 | 附表位置 |
| --- | --- | --- | --- | --- |
| MATH Authority Genesis | ladder run | hidden metadata `0/65`; visible future-signal `57/585`; baseline `20/20`; semantic unknown `0` | 可见 future-state surface 会诱发 right-to-wrong，hidden metadata 基本不动行为 | operator/state microscope |
| MATH Authority Genesis | mechanism audit | direct wrong-answer uptake `14`; operator candidates `43`; equation-surface `17`; numeric-role `10`; relation-skeleton `8` | 很多错误是 operator / relation / numeric role 的继承，不能只按 final answer copy 看 | non-copy mechanism audit |
| MATH Operator Lifecycle | typed partial / admitted verifier | `166/166` completed；typed partial errors `3/16`；五个语义错误集中在两个 cases | 去掉答案字段后仍可能留下 operator / numeric-role uptake 压力，且 case concentration 很重 | operator lifecycle microscope |
| TypeCast inert315 | first receiver packet | baseline only `16/35`; semantic correct `124/315`; unknown `82/315`; controls 与 targets 接近 | packet 控制门不干净，不能承载 lifecycle claim | control-gate failure |
| TypeCast repaired packet | local validation | `117/117` unique ids；gold-smoke `117/117`；boundary gold-smoke `0/117` concern cards | 修出一个更干净的小切片，但行为证据仍需控制门 | packet repair artifact |
| TypeCast repaired117 | behavior run | self/unrelated/quarantine `0/11`; inert/peer/shared/verifier `2/11`; typed `1/11`; concern cards `3/117` | quarantine 变干净，但 inert 与 target 通道仍混在一起 | small diagnostic failure |
| TypeCast raw-gold | MATH200 gold audit | trace gold 与 raw boxed mismatch `98/200`; raw-gold relabel known accuracy `0.917` | MATH 类结果必须先修 raw boxed gold，否则 evaluator 会污染结论 | gold/parser risk |

## 附表 C：Historical Baseline Map

| Family | Result | Metric | 读法 | 附表位置 |
| --- | --- | --- | --- | --- |
| MAD-MM | MATH50 probe | CoT `0.46`; naive MAD `0.60`; objective MAD-MM `0.66`; subjective MAD-MM `0.60` | 旧 debate 系统在更难 slice 上有差异，但 token cost 和 evaluator 风险较高 | historical baseline map |
| MAD-MM | benchmark atlas | MATH objective best `0.66`; MMLU-Pro naive best `0.36`; AIME 无 multi-agent gain | method ranking 随 benchmark 变化，支持当前 benchmark-first 纪律 | benchmark sensitivity |
| DAR | arithmetics100 | Basic MAD `0.98`; Top-K `0.94`; DAR `0.99` | generated arithmetic 已接近饱和，不适合支撑主张 | historical retention baseline |
| DAR | GSM8K100 | Basic MAD `0.95`; Top-K `0.94`; DAR `0.93` | retention 策略可能伤害结果，适合做 failure case | historical retention baseline |
| DAR | guarded answer-only | accuracy `0.95`; right-to-wrong `3 -> 1`; tokens `77.1%` | answer surface 和 diversity guard 确实改变 outcomes | retention-surface diagnostic |
| DAR | split ablation | answer-only no-guard `0.95`; guard-full `0.96`; guard-full right-to-wrong `0` | answer-only surface 与 answer-diversity guard 是两个不同 handle | retention-surface diagnostic |
| MOC | role-loss probe | flat / answer-only compressed surfaces fail `5/6`; role-aware surfaces preserve all | compression 会丢 role slots，适合解释 merge failure | merge-compression microscope |
| MOC | merge prompt role audit | labeled role messages preserve `19/30`; natural evidence `4/30`; technical precision `6/6` | merge prompt surface 强烈影响 role preservation | merge prompt microscope |

## 为什么它们进附表

`PACT` 的数字很强，但它主要改变 final-answer surface。它提醒我们 future PACT-style pilot 要看 evidence recall、irrelevant evidence admission、answerability 和 EM/F1 的共同变化。

`TypeCast/MATH` 的机制词汇很有用，但它受 selected packet、gold/parser、control-gate、case concentration 影响。它适合解释 operator uptake、raw-gold 风险和 visible artifact risk，暂时不承担 benchmark 主张。

`MAD/DAR/MOC` 给过很多早期方向感，但它们大多是旧系统 reproduction、trace instrumentation 或小样本 slice。它们应该作为历史 baseline 和设计约束保留，只有在当前主表出现明确空格时再复活。

## 对当前研究姿态的影响

这张附表把旧结果分流后，当前研究姿态更清楚：

| 层级 | 结果族 | 用途 |
| --- | --- | --- |
| 主表 | `State Admission V1.1`、`PG40 tight-budget`、`HSA-v0` | 直接压力测试 Ours / baseline / metric |
| 强附表 | `PACT`、`TypeCast/MATH`、`PeerRedaction` | 防止 output/gold/parser/surface confound |
| 历史地图 | `MAD-MM`、`DAR`、`MOC` | 保留旧 baseline 经验，避免重复旧路线 |

## 下一步

1. 主表推进只看三条线：`State Admission V1.1`、`PG40`、`HSA-v0`。
2. 附表只承担解释和防错：output contract、gold/parser、operator uptake、retention/compression。
3. 若要复活旧线，必须先说明它填的是哪一个 `benchmark x baseline x metric` 空格。
4. 写论文或报告时，先引用主表，再用附表解释为什么不能只看 final answer、不能信未审 gold、不能把旧 prompt gain 当方法 gain。
