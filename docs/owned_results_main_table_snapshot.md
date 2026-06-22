# 自有结果主表快照

Snapshot date: `2026-06-19`.

## 核心判断

我们自己的重要结果还没有全部压进主表。当前项目已经有多组强信号，但它们散在 `reports/`、`experiments/`、`docs/evidence_register.md` 和归档报告里。现在最需要的动作，是把这些结果从“报告叙事”压成“benchmark x baseline x metric x claim role”的行级表。

目前没有可对外宣称的 SOTA。对外报告主线应优先回到 PerspectiveGap / PG40 公开基准或公开切片：同一模型、同一预算、同一评价器，把 direct、source-ledger、structured no compiler、compiled、transparent greedy 和 oracle 放进同一张表。`State Admission V1.1` 仍是最接近方法形状的内部结果，14B priority + executor 到 `33/40` strict，7B fallback-required 到 `31/40` strict；但它受 synthetic packet、暴露 bundle/group 表、强符号 `group_density_global` baseline 的限制。HSA-v0 保留为机制诊断和附表材料。

## 行角色

| 角色 | 含义 |
| --- | --- |
| `主表候选` | 可进入最终 main table 或 main-table ablation 的直接证据。 |
| `主表背景` | 支撑 benchmark 选择、baseline ladder 或机制方向，但还缺 Ours 同表结果。 |
| `方法管线` | builder、adapter、runner、scorer 已经打通，尚未产生模型效果。 |
| `强附表` | 数值强、机制有价值，但任务或 evaluator 形态限制主张承载力。 |
| `显微镜` | 用来解释 failure surface、parser/gold/contract 风险。 |
| `归档地图` | 历史探索结果，需要留痕，当前只在明确填补主表空格时复活。 |

## A 层：应该优先压进主表或主表背景

| 结果族 | 证据来源 | 条件 / 对照 | Benchmark / Slice | 模型 | 主指标 | 次指标 | 当前主表状态 | Claim role | 下一步 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `HiddenBench Stage 1` | `reports/20260617-hiddenbench-v2-stage1-full65-qwen25-14b.md`; E-121 | `shared_only` / `full_info` / `oracle_public_facts` / old exchange / fact-only | HiddenBench full65 | Qwen2.5-14B | `1/65`, `59/65`, `56/65`, `24/65`, `57/65` | clean subset old `23/55` vs fact-only `55/55`; recommendation leakage `225/253 -> 0/253`; shared overtalk `134/253 -> 4/253` | 已进入主线报告，主表未压完整行 | 主表背景 | 作为 HSA-v0 seed 与 communication-necessity ladder，保留 clean subset 指标。 |
| `HiddenBench Stage 2` | `reports/20260617-hiddenbench-v2-stage2-sender-ablation-full65-qwen25-14b.md`; E-123 | old exchange / no-recommendation / no-shared-repeat / fact-only | HiddenBench full65 | Qwen2.5-14B | all65: `24/65`, `30/65`, `33/65`, `57/65` | clean subset: `23/55`, `28/55`, `31/55`, `55/55`; fact-only 对两个局部禁令无 clean regression | 已进入信号审计，主表未压完整行 | 主表背景 | 用来定义 public fact-state contract 的 baseline，不继续堆 prompt variant。 |
| `HiddenBench Stage 3` | `reports/20260617-hiddenbench-v2-stage3-blind-sender-full65-qwen25-14b.md` | blind sender / blind minimal / fact-only / old exchange | HiddenBench full65 | Qwen2.5-14B | blind minimal `57/65`; fact-only `57/65`; old exchange `24/65` | clean subset blind minimal `55/55`，fact-only `55/55`，old exchange `23/55` | 已入报告，主表缺行 | 主表背景 | 写进 HSA 设计依据：sender 先作为局部事实传感器。 |
| `HiddenBench Stage 4` | `reports/20260617-hiddenbench-v2-stage4-sender-visibility-full65-qwen25-14b.md` | visibility-minimal matrix | HiddenBench full65 | Qwen2.5-14B | fact-only / blind-minimal / private+task minimal clean `55/55` | options/shared/full visibility minimal `54/55`; 旧 exchange `23/55` | 已入报告，主表缺行 | 主表背景 | 把主机制收束到 public-message output contract，而非 sender visibility hiding。 |
| `HiddenBench Stage 4 7B` | `reports/20260617-hiddenbench-v2-stage4-qwen25-7b-pressure.md` | cross-model visibility pressure | HiddenBench full65 clean subset | Qwen2.5-7B | old exchange `16/50`; minimal 条件约 `47/50`; full-visibility minimal `46/50` | 旧 exchange recommendation leakage `104/253`; shared overtalk `150/253`; minimal recommendation leakage `0` | 已补入差集审计 | 主表背景 | 作为 7B robustness caveat，支持 public-message pollution 并非 14B 天花板现象。 |
| `HSA-v0 diagnostic series` | `reports/20260618-hsa-v0-sseac-adapter.md`; `reports/20260619-hsa-v0-full9-a8002.md`; `reports/20260619-hsa-v0-constraint-completion-postfilter.md`; `docs/hsa_v0_numeric_main_table.md`; `reports/20260619-public-benchmark-report-reset.md` | oracle / shared-only / all-scoped / model-only / compiled / blocker completion / support completion | HSA-v0 36 rows | transparent controls + Qwen2.5-14B + local postfilter | model-only `16/36`; compiled `34/36`; blocker completion `35/36`; support completion `36/36` | all-scoped extra final cards `195`; support completion extra final cards `42`; perturb strict `24/24` | 已入机制数字表 | 内部机制诊断 | 暂停扩包；只作为机制附表、错误定位和对外 caveat。 |
| `PerspectiveGap contact` | `reports/20260618-perspectivegap-benchmark-contact.md`; E-124 | oracle / all-to-all / no-distractor / shared-intersection | PerspectiveGap 220 evals | deterministic baselines | oracle `220/220`; all over-sharing baselines `0/220` | all-to-all precision `0.318`，leak `3.800`; shared-intersection precision `1.000`，coverage `0.031` | 已入近场 benchmark 表 | 主表背景 | 作为 role-specific routing 外部压力，继续只跑同一 stratified slice。 |
| `PerspectiveGap raw model routing` | `reports/20260618-perspectivegap-model-smoke-and-paper-story.md`; E-125/E-126 | 7B vs 14B raw role assignment | PerspectiveGap stratified20 x seeds 1,42 = 40 evals | Qwen2.5-7B / 14B | 两者 strict `0/40`; 7B coverage `0.443`; 14B coverage `0.615` | 7B precision `0.786`, leak `0.050`; 14B precision `0.808`, leak `0.450` | 已入主线报告，主表未作为 baseline 行 | 主表背景 | 保留为 raw model baseline，后续同表加入 typed-router、budget-router、SSEAC。 |
| `PerspectiveGap source-ledger rotated20` | `reports/20260618-perspectivegap-source-ledger-rotated20.md` | old role-list vs source-ledger | PG rotated20, 40 rows | Qwen2.5-7B / 14B | 14B source-ledger strict `3/40`, coverage `0.854`; 7B coverage `0.574` | 14B precision `0.779`, budget pass `0.225`; 7B precision `0.745`, budget pass `0.350`; reject recall `1.000` | 已入主线报告，主表缺 numeric row | 主表候选背景 | 作为 source/scope ledger 机制信号，不能代表最终 Ours。 |
| `PerspectiveGap budget compiler` | `reports/20260618-perspectivegap-budget-compiled-source-ledger.md`; E-131 | raw source-ledger -> deterministic compiler | PG rotated20, 40 rows | Qwen2.5-7B / 14B | 14B strict `3/40 -> 12/40`; 7B strict `0/40` | 14B coverage 保持 `0.854`，precision/budget/reject 到 `1.000`; 7B precision/budget 到 `1.000` | 已入信号审计，主表缺行 | 主表候选背景 | 保留为 compiler 有效性的旧证据；进入 tight-budget 后只作 background。 |
| `PG40 tight-budget` | `reports/20260618-perspectivegap-tight-budget-source-ledger.md`; `reports/20260618-sseac-v0-pg40-prediction-converter.md`; `reports/20260619-pg40-direct-routing-limit5.md`; `reports/20260619-pg40-sseac-cardunit-limit5.md`; `reports/20260619-pg40-sseac-roleplan-limit5.md` | oracle / eligible / utility greedy / source-ledger compiled / direct routing limit5 / true SSEAC card-unit limit5 / role-plan diagnostic | PG40 tight-budget | deterministic + reused model outputs + Qwen2.5-14B | oracle `40/40`; utility-density greedy `25/40`; source-ledger 14B compiled `11/40`; direct routing limit5 `0/5`; card-unit compiled limit5 `1/5`; role-plan compiled limit5 `1/5` | direct utility `0.0987`; card-unit utility `0.8155`; role-plan utility `0.7811`; source-ledger 14B utility `0.8707` | 已入数字专表 | 诊断证据 / 强压力表 | direct 已补齐；role-plan 已退休；PG40 后续只做预算感知排序机制。 |
| `State Admission V1.1 local baselines` | `reports/20260618-state-admission-v1-local-baselines.md`; E-135 | oracle / item density / bundle density / group density | SA-V1.1 full40 | deterministic baselines | oracle `40/40`; group-density `32/40`; bundle-density `14/40` | group-density utility `0.9666`; item baselines `0/40` | 已入数字专表 | 主表候选 | 作为 State Admission 强 baseline ladder，必须和所有 model rows 同表。 |
| `State Admission V1.1 direct 14B` | `reports/20260618-state-admission-v1-qwen25-14b-pressure.md`; E-137 | direct default / budget-first / group-density | SA-V1.1 full40 | Qwen2.5-14B | direct default `0/40`; budget-first `0/40`; group-density `32/40` | default coverage `1.000` 但 global budget `0.000`; 空角色 `82/82` 被填 | 已入数字专表 | 主表候选 | 保留为 direct admitted state failure baseline。 |
| `State Admission V1.1 priority executor 14B` | `reports/20260618-state-admission-v1-priority-executor-pressure.md` | direct -> priority + executor -> pair-group-primary | SA-V1.1 full40 | Qwen2.5-14B | priority greedy `28/40`; pair-group-primary `33/40` | budget pass `1.000`; closure violations `0`; utility `0.9014`; group-density `32/40`, utility `0.9666` | 已入数字专表 | 主表候选 | 当前最强 method-shaped result；必须与 group-density 同表，语气限定为 legal admission decomposition。 |
| `State Admission V1.1 priority executor 7B` | `reports/20260618-state-admission-v1-priority-7b-replication.md`; E-139/E-141 | pair-group-primary / normalized / fallback-required | SA-V1.1 full40 | Qwen2.5-7B | `25/40 -> 26/40 -> 31/40` | fallback coverage `0.8344`; precision `0.8718`; budget pass `1.000`; closure `0`; utility `0.8431` | 已入数字专表 | 主表候选 | 作为跨模型 protocol-shape 证据，下一步压 unit-construction。 |
| `State Admission V1.1 ledger-first` | `reports/20260618-state-admission-v1-ledger-hidden-unit-pressure.md`; E-142 | source ledger -> compiler | SA-V1.1 full40 | Qwen2.5-7B | ledger-first `1/40`; oracle compiler `40/40` | required coverage `0.4417`; precision `0.4645`; utility `0.0409`; closure violations `1.6750` | 已入数字专表 | 主表候选的失败边界 | 说明 admission-unit construction 是下一瓶颈；指导 HSA/SA-V2 设计。 |

## B 层：方法管线已经有入口，但还缺模型效果

| 结果族 | 证据来源 | 当前已有 | 缺口 | Claim role | 下一步 |
| --- | --- | --- | --- | --- | --- |
| `SSEAC-v0 spec/compiler` | `docs/source_scoped_evidence_admission_compiler_v0.md`; `schemas/sseac_v0.schema.json`; `scripts/compile_sseac_v0.py` | schema、compiler、PG40 adapter、HSA-v0 adapter 已存在 | 还没有冻结的模型输出结果 | 方法管线 | 冻结 Ours 后只跑小样本，不开新宽分支。 |
| `SSEAC-v0 PG40 runner` | `reports/20260618-sseac-v0-pg40-runner-preflight.md`; `reports/20260619-pg40-direct-routing-limit5.md`; `reports/20260619-pg40-sseac-cardunit-limit5.md`; `reports/20260619-pg40-sseac-roleplan-limit5.md` | 40 个 prompts dry-run；direct、true prompt、card-unit、role-plan 四轮 limit5 已跑完；无金标泄漏；runner 已支持 `cardunit/roleplan` 契约选择 | direct strict `0/5`，card-unit strict `1/5`，role-plan utility 更低 | 诊断管线 | PG40 暂停扩跑；若重启需预算感知重排或成对排序器。 |
| `SSEAC-v0 HSA runner` | `reports/20260618-hsa-v0-sseac-runner-preflight.md`; `reports/20260619-hsa-v0-full9-a8002.md`; `reports/20260619-hsa-v0-constraint-completion-postfilter.md`; `docs/hsa_v0_numeric_main_table.md` | 9 行、15 行、33 行、36 行诊断链路已打通；36 行 support completion 到 strict `36/36`，extra final cards `42`，低于 all-scoped `195` | 它是内部派生诊断包，公开基准有效性仍需 PG40 / PerspectiveGap 承接 | 诊断管线 | 暂停扩包；保留为机制附表和错误定位工具。 |

## C 层：强附表和机制显微镜

| 结果族 | 证据来源 | 条件 / 对照 | Benchmark / Slice | 模型 | 主指标 | 当前主表状态 | Claim role | 下一步 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `State Admission V2 option-state` | `reports/20260618-state-admission-v2-option-state-and-direct-controls.md` | unit-first / option-state-first / direct controls | SA-V2 smoke9 | Qwen2.5-7B / 14B | 7B option-state downstream `0.2222`; 14B option-state strict `0.1111`, downstream `0.4444` | 已入主表骨架 diagnostic | 强附表 | 写成 HSA/SA 设计依据：option-state recall 高于 downstream consistency。 |
| `State Admission V2 visible facts` | `reports/20260618-state-admission-v2-visible-facts-ablation.md` | visible facts first | SA-V2 smoke9 | Qwen2.5-14B | strict `0.0000`; downstream `0.3333`; perturb downstream `0.0000` | 已入 diagnostic | 强附表 | 转为证据充分性失败附表；别扩同款 9-row prompt。 |
| `State Admission V2 smoke GPU` | `reports/20260618-state-admission-v2-smoke-gpu.md` | oracle / shared-context / unit-first model | SA-V2 smoke9 | Qwen2.5-7B | oracle `9/9`; shared-context `0/9`; model strict `0.0000` | unit recall `0.2222`; rejection recall `0.4444`; scope violations `0.0000`; downstream `0.0000` | 已补入差集审计 | 强附表 | 作为 hidden-unit construction 的 diagnostic floor，不扩大为主结果。 |
| `State Admission V2 abstention gate` | `reports/20260618-state-admission-v2-abstention-gate-ablation.md` | explicit abstention gate | SA-V2 smoke9 | Qwen2.5-14B | strict `0.1111`; downstream `0.4444` | option-state recall `0.8148`，低于上一轮 `0.9259` | 已补入差集审计 | 强附表 | 作为 contract ablation，提示显式闸门没有解决 downstream consistency。 |
| `PACT final-answer contract` | `reports/_archive/20260616-pruned/20260614-pact-final-answer-contract-gpu.md`; E-044/E-045 | original vs final-answer contract | HotpotQA50 + offset50 | Qwen2.5-14B | original `17/50` EM, F1 `0.508`; contract `34/50`, F1 `0.792` | 只在 PACT-pilot 占位 | 强附表 | 作为 output-surface 警报；未来 PACT pilot 必须报告 evidence metrics。 |
| `PACT offset50 contract` | E-045 | neighboring offset50 original vs contract | HotpotQA offset50 | Qwen2.5-14B | EM `26/50 -> 28/50`; F1 `0.6469 -> 0.7427` | 未入主表 | 强附表 | 说明 contract gain 不稳定，不能靠 final string 讲通信改善。 |
| `MATH Authority Genesis` | `reports/20260616-math-authority-genesis-ladder-qwen25-14b.md`; E-110/E-111 | hidden metadata vs visible future-signal | selected MATH packet, 670 rows | Qwen2.5-14B | hidden metadata `0/65` violations; visible future-signal `57/585` violations | 信号审计里只做背景 | 显微镜 | 保留 operator uptake 词汇，不扩为主 benchmark。 |
| `MATH Operator Lifecycle V1` | `reports/20260617-math-operator-lifecycle-v1-qwen25-14b.md` | typed partial / admitted verifier | MATH operator lifecycle 166 rows | Qwen2.5-14B | `166/166` completed；typed partial errors `3/16` | 五个语义错误集中在两个 cases；admitted/verifier 错误含 visible final-answer artifact | 已补入附表 | 显微镜 | 保留为 operator / numeric-role uptake 警报。 |
| `TypeCastArena inert315` | `reports/20260617-typecast-math200-inert-receiver315-qwen25-14b.md`; E-116 | self/unrelated/inert/peer/shared/verifier/quarantine | MATH receiver315 | Qwen2.5-14B | baseline previous-solution only `16/35`; controls 与 targets 都有 violations | 已退主线 | 显微镜 | 作为 control-gate 失败样例，提醒 parser/gold/surface 风险。 |
| `TypeCast repaired117` | `reports/20260617-typecast-repaired-controlstable117-qwen25-14b.md`; E-117/E-118 | repaired control-stable receiver | MATH receiver117 | Qwen2.5-14B | self/unrelated/quarantine `0/11`; inert/peer/shared/verifier `2/11`; typed `1/11` | 已退主线 | 显微镜 | 保留为小切片诊断，禁止直接扩 GPU。 |
| `MATH raw-gold diagnosis` | `reports/20260616-typecast-math200-clean-rawgold-diagnosis.md` | trace gold vs raw boxed answer | MATH200 | local audit | raw-gold mismatch `98/200` | 已入信号审计 | 显微镜 | 所有 MATH 类结果只在 gold/parser 兼容后才可比较。 |

## D 层：历史结果地图，保留但降级

附表层的完整数字地图见 `docs/appendix_owned_results_map.md`，机器可筛选版本是 `docs/appendix_owned_results_rows.csv`。

| 结果族 | 证据来源 | 代表结果 | 当前角色 | 何时复活 |
| --- | --- | --- | --- | --- |
| `MAD-MM MATH50` | E-017; `reports/_archive/20260616-pruned/20260613-madmm-benchmark-atlas.md` | CoT `0.46`; naive MAD `0.60`; objective MAD-MM `0.66`; subjective MAD-MM `0.60` 且 token cost 最高 | 归档地图 | 只在需要 old multi-agent debate baseline 时回填。 |
| `DAR arithmetics/GSM8K` | E-010/E-011/E-021/E-023 | arithmetics100: Basic MAD `0.98`, DAR filter_critical `0.99`; GSM8K100: Basic MAD `0.95`, DAR `0.93`; guarded answer-only 到 `0.95`; guard-full 到 `0.96` | 归档地图 | 只作为 retention / answer-surface control，不开主线。 |
| `MOC smoke and merge role audit` | E-012/E-016/E-053/E-054 | hop2 forced merge 5/5 saturated；role-sensitive synthetic flat/answer-only 5/6 fail；merge prompt labeled roles `19/30` preserve slots，natural evidence `4/30` | 归档地图 | 只有在主 benchmark 出现 merge/compression failure 时复活。 |
| `Trace schema v1.1` | E-013/E-028/E-029 | MAD/DAR/MOC traces 可抽成统一 schema；610 trace rows 有 recipient-context events | 工具性资产 | 若重跑旧 baseline，需要沿用统一 trace schema。 |
| `Peer-redacted evidence` | E-059 | leakage `16/44 -> 8/44`，但 wrong redacted evidence right-to-wrong 更多 | 显微镜 / 退役边界 | 可作为 answer removal 风险引用。 |
| `typed public-state / source-label / authority probes` | `docs/evidence_register.md` 中 E-066、E-080、E-110 到 E-118 近邻条目 | 多数是小样本 field/authority/source surface 压力 | 显微镜 | 只在 HSA/SA benchmark 需要解释 source/scope/admission terminology 时引用。 |

## 现在最该补进主表的结果

第一优先级是 `State Admission V1.1`。它目前承担“经典机制改善”的核心证据，数字专表已经补在 `docs/state_admission_v1_numeric_main_table.md`，机器可筛选版本是 `docs/state_admission_v1_numeric_rows.csv`。最终主表至少包含：

| 条件 | 主指标 | 角色 |
| --- | ---: | --- |
| oracle | `40/40` | 上界 |
| group-density global | `32/40`, utility `0.9666` | 强符号 baseline |
| direct 14B default | `0/40` | direct admitted state failure |
| direct 14B budget-first | `0/40` | budget-aware prompt failure |
| priority 14B greedy executor | `28/40` | protocol candidate |
| priority 14B pair-group-primary | `33/40` | 当前最强 method-shaped row |
| priority 7B pair-group-primary | `25/40` | 跨模型复现 |
| priority 7B normalized | `26/40` | parser friction control |
| priority 7B fallback-required | `31/40` | executable schema gain |
| ledger-first 7B | `1/40` | unit-construction bottleneck |

第二优先级是 `PG40 tight-budget`，也是当前对外报告的公开切片主表。数字专表已经补在 `docs/pg40_tight_budget_numeric_main_table.md`，机器可筛选版本是 `docs/pg40_tight_budget_numeric_rows.csv`。它会直接告诉我们 SSEAC 是否能跨过透明贪心 baseline。当前已有 oracle `40/40`、utility-density greedy `25/40`、source-ledger 14B compiled `11/40`、direct routing limit5 `0/5`、card-unit limit5 compiled `1/5`。role-plan limit5 没有超过 card-unit，下一次只有在排序机制发生实质变化时才值得重启。

第三优先级是 `HSA-v0` 机制附表。数字专表已经补在 `docs/hsa_v0_numeric_main_table.md`，机器可筛选版本是 `docs/hsa_v0_numeric_rows.csv`。它承接 HiddenBench 的通信必要性和 public fact-state signal，但当前只作为内部机制诊断。三十六行结果显示：模型直出 `16/36`，硬准入 `34/36`，阻断补全后 `35/36`，支撑型窄补全后 `36/36`；多余最终卡片 `42`，低于 all-scoped 的 `195`。下一步不继续扩 HSA，除非对外报告需要机制附表、错误定位或案例解释。

## SOTA 状态

现在没有 SOTA 结果。更准确的状态是：

| 线 | 当前最高价值 | 为什么还不能宣称 SOTA |
| --- | --- | --- |
| `State Admission V1.1` | priority + executor 14B `33/40`，略高于 group-density strict `32/40` | synthetic packet；暴露 admission units；utility 低于 group-density；无真实 downstream task |
| `HiddenBench / HSA` | HSA 36 行中 model-only `16/36`，compiled `34/36`，support completion `36/36` | HSA 是内部派生诊断包，不能承接公开基准方法胜利 |
| `PerspectiveGap / PG40` | direct routing limit5 `0/5`；source-ledger + compiler 14B `11/40`；tight-budget greedy `25/40`；card-unit limit5 compiled `1/5`；role-plan limit5 compiled `1/5` | 强透明 baseline 压住当前方法；role-plan 未超过 card-unit，下一步要做排序机制 |
| `PACT` | final-answer contract `17/50 -> 34/50` | 主要改变 output surface，不能代表 evidence exchange 改善 |
| `TypeCast/MATH` | operator / authority uptake 有清晰机制词汇 | gold/parser/selected packet 风险太高，已降为显微镜 |

## 直接行动

1. 把本文件里的 `A 层` 表拆成可机器更新的 CSV/JSONL，列名固定为 `result_family, run_or_report, condition, benchmark_or_slice, model, primary_metric, secondary_metrics, main_table_status, claim_role, next_action`。
2. 先生成 `State Admission V1.1` 数字主表，因为它最接近方法结果，也最容易被 baseline 质疑。
3. `PG40 tight-budget` 公开切片主表已补 direct 五行；下一步做预算感知重排或成对排序器。
4. `HSA-v0` 暂停扩包，只维护机制附表；需要解释来源、范围、验证、证据不足和补全边界时再恢复。
5. 把 `PACT`、`TypeCast/MATH`、`MAD/DAR/MOC` 固定为附表和归档地图，除非它们能填入当前 baseline ladder 的明确空格。
