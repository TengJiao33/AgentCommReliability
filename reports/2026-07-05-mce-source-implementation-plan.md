# MCE/MCA 源码落地调研与实现方案

日期：2026-07-05

## 核心判断

用户提到的是 `MCA` idea；当前仓库文档里已有对应机制名 `MCE`，即 Metacognitive Cue Exchange。若 `MCA` 指的是 metacognitive cue / cognitive atom 这条方向，本文按 `MCE` 处理。后续如果要改名，建议只改 display name，不要先改机制边界。

我对源码落地的判断是：第一版不要直接改正在跑的 `CPAC-DCAC` runner，而是新增一个 standalone diagnostic runner，例如 `scripts/run_mce.py`。它复用现有 initial solver、candidate card、vLLM batch generation、evaluator、records/summary 写法；等 smoke/full 读数证明 cue-only 分支有信号，再把它合并成 CPAC 的一个 action，例如 `cue_resolve` 或 `metacognitive_cue_resolve`。

理由很简单：CPAC 当前回答的是 candidate-pool state diagnosis 是否能指导协议切换；MCE/MCA 回答的是 answer-free cue 是否能把局部认知贡献从最终答案正确性中解耦。两者相关，但第一轮证据最好分开，不然 full run 一旦涨/跌，很难知道是 CPAC branch 还是 cue intervention 在起作用。

## 当前本地依据

仓库状态显示：

- `scripts/run_cpac_dcac.py` 已实现 CPAC+DCAC runner，包含 candidate pool diagnosis、DCAC claim/certificate、listwise discriminant branch、summary 指标。
- `scripts/run_consensus_quarantine.py` 已提供可复用 helper：`independent_prompt`、`generate_outputs`、`generate_plain_texts`、`reshape`、`build_candidate_cards`、`transition_label`。
- `scripts/run_basic_mad.py` 已提供 evaluator、`majority_vote`、`normalize_numeric`、`is_correct`、`prompt_from_messages`、`load_rows`、`resolve_inside`。
- `reports/2026-07-05-metacognitive-cue-exchange.md` 已定义 MCE：交换 answer-free metacognitive cue，而不是答案或完整 rationale。
- `active/README.md` 明确写到 MCE 可作为 CPAC 通信动作，但还没有 claim-bearing run。

本地轻量测试状态：

- `python -m pytest tests` 失败，因为当前环境没有安装 `pytest`。
- `python -m unittest discover -s tests` 通过，19 个测试全部 OK。

## 外部文献边界

这条 idea 的可发表空间不在“元认知”四个字本身，而在更窄的对象：answer-free、instance-level、cross-agent cue atom。

相关工作已经覆盖了几块邻近区域：

- Metacognitive Prompting 把 self-aware evaluation 放进 single-agent prompt 流程，但不是跨 agent 传播短 cue。来源：https://arxiv.org/abs/2308.05342
- Think2 / Grounded Metacognitive Reasoning 把 Planning、Monitoring、Evaluation 结构化为 single-agent/MetaController 自我纠错框架，但仍不是 peer cue uptake。来源：https://arxiv.org/abs/2602.18806
- Progressive-Hint Prompting 用 previous answers 作为 hint，和 answer-free cue 不同。来源：https://arxiv.org/abs/2304.09797
- Demystifying MAD、DynaDebate、Maestro 已覆盖 diversity-aware initialization、dynamic path generation、divergence/convergence 与 list-wise selection。MCE 不能包装成“更多 diverse paths”。来源：https://arxiv.org/abs/2601.19921 、https://arxiv.org/abs/2601.05746 、https://arxiv.org/abs/2511.06134
- DAR 说明“what agents hear”很重要，但它保留的是原始 disagreeing messages，不是抽取 answer-free cue atoms。来源：https://arxiv.org/abs/2603.20640
- CIPHER、Thought Communication、LatentMAS 说明 latent/embedding communication 是强邻近线。第一版 MCE 应避开 hidden state/KV cache，走 symbolic cue atom，保持可审计。来源：https://arxiv.org/abs/2310.06272 、https://arxiv.org/abs/2510.20733 、https://arxiv.org/abs/2511.20639

因此，MCE/MCA 的源码实现要坚持三个约束：

1. 不传最终答案。
2. 不传完整 rationale。
3. 记录 cue 是否被吸收，以及吸收后是 recovery 还是 harm。

## 建议源码落点

第一版新增：

- `scripts/run_mce.py`
- `tests/test_mce.py`
- `experiments/<run-id>/README.md`

暂时不修改：

- `scripts/run_cpac_dcac.py`
- 正在跑的 CPAC run 目录
- 已生成的 CQG/CPAC result files

`run_mce.py` 应复用现有 helper，而不是复制一套 evaluator：

```python
from run_basic_mad import (
    ROLE_NAMES,
    is_correct,
    load_rows,
    majority_vote,
    normalize_numeric,
    prompt_from_messages,
    resolve_inside,
)
from run_consensus_quarantine import (
    build_candidate_cards,
    generate_outputs,
    generate_plain_texts,
    independent_prompt,
    reshape,
    transition_label,
)
from run_mad_mm import prepare_question
```

## 最小数据结构

建议新增三个小 dataclass：

```python
@dataclass(frozen=True)
class CueAtom:
    cue_id: str
    source_agent_index: int
    source_answer: str | None
    cue_type: str
    cue_text: str
    why_relevant: str
    self_reported_answer_leak: bool

@dataclass(frozen=True)
class FilteredCue:
    cue: CueAtom
    keep: bool
    reasons: tuple[str, ...]

@dataclass(frozen=True)
class CueResolveResult:
    parsed_answer: str | None
    normalized_answer: str | None
    used_cues: tuple[str, ...]
    ignored_cues: tuple[str, ...]
    new_realization: str
    output: str
```

这些字段足够支撑第一版指标，不需要先上复杂 ontology。

## 最小流程

第一版 runner 可以走 6 段：

1. `initial_solve`
   - 复用 `independent_prompt` 和 `generate_outputs`。
   - 得到每题 `initial_outputs`、`initial_majority_answer`、`candidate_cards`、`pool_state`。

2. `cue_extraction`
   - 对每个 initial agent output 单独抽 cue。
   - prompt 要求最多 `k=2` 个 cue，每个 cue 有 `type/text/why/leak`。
   - 明确禁止 final answer、完整解法、候选投票、confidence。

3. `cue_filter`
   - 不用 gold，只用候选答案和文本规则过滤。
   - 删除包含任一 candidate raw/normalized answer 的 cue。
   - 删除 token 太短、太泛、placeholder、重复 cue。
   - 标记 `answer_leak`, `generic`, `duplicate`, `empty`, `too_long`。

4. `cue_resolve`
   - 将保留下来的 cue pool 匿名广播。
   - resolver 只看到 problem + cue pool，不看到 cue source、不看到 source answer、不看到 vote count。
   - resolver 输出 `<answer>`，并额外输出 `<used_cues>`、`<ignored_cues>`、`<new_realization>`。

5. `aggregation`
   - 对 `reviewers` 个 cue-resolve outputs 做 majority vote。
   - final answer 与 same-run initial majority 做 paired contrast。

6. `record_and_summary`
   - 每题 records 写入 initial、cue atoms、filter decisions、cue pool、resolver outputs、final answer、transition。
   - summary 统计 accuracy、coverage、leak、uptake、recovery、harm，并按 pool state 拆分。

## Prompt 形态

Cue extraction 建议用 XML，贴合现有 runner 风格：

```text
Reply with XML only:
<cues>
  <cue>
    <type>formula|representation|invariant|constraint|subgoal|sanity_check|pitfall</type>
    <text>20-40 tokens, no final answer.</text>
    <why>one short sentence</why>
    <answer_leak>yes|no</answer_leak>
  </cue>
</cues>
```

Cue resolve 建议要求：

```text
You are given answer-free metacognitive cues from anonymous agents.
Do not infer vote counts or trust cue sources.
Use only cues that are relevant and independently checkable.

End with:
<used_cues>comma-separated cue ids or NONE</used_cues>
<ignored_cues>comma-separated cue ids or NONE</ignored_cues>
<new_realization>one sentence or NONE</new_realization>
<answer>final answer only</answer>
```

这里的 `used_cues` 只能当 self-report，不要当绝对事实。第一版报告中应把它标为 auxiliary metric。

## CLI 参数

建议第一版参数：

```text
--cue-k 2
--cue-mode cue_filtered
--cue-temperature 0.2
--resolve-temperature 0.2
--cue-max-tokens 512
--resolve-max-tokens 1536
--reviewers 3
--agents 3
--pool-state-scope all|collapse|minority_bearing|no_majority_conflict
--input-records <optional existing records.jsonl>
```

`--input-records` 很重要。它允许直接复用 CPAC/CQG 的 `initial_outputs` 做 paired MCE ablation，省掉 initial sampling 成本，也能和 CPAC 当前 full run 保持同题同初始池比较。没有该参数时，runner 自己生成 initial outputs。

## 第一版指标

必须有：

- `initial_majority_accuracy`
- `mce_final_accuracy`
- `answer_change_rate`
- `cue_coverage_rate`: 每题至少一个 kept cue
- `answer_leak_rate`: 被判泄漏答案的 cue 占比
- `generic_cue_rate`
- `cue_uptake_self_report_rate`
- `wrong_majority_recovery_rate`: `MaW_to_C`
- `correct_majority_harm_rate`: `MaC_to_W`
- `pool_state_metrics`: collapse / minority-bearing / no-majority 分开算

建议有：

- `wrong_source_recovery_cases`: cue 来源 agent 初始答案错，但 cue-resolve final 对。这个不是自动证明 cue 正确，只能说明“错误来源 agent 参与的 cue pool 后发生恢复”。
- `oracle_initial_present`: initial candidate pool 是否已有正确 answer，用于区分 coverage vs identification。
- `kept_cues_per_case`
- `resolver_parse_fail_rate`

不要第一版就强报：

- `correct_cue_rate`。除非加独立 judge 或人工 audit，否则不能从 outcome 直接推出 cue 本身正确。

## 实验门槛

第一轮不要直接 claim-bearing full。

建议顺序：

1. `limit=20` smoke
   - 目标：cue parser、answer-leak filter、resolver XML、summary 指标都可解释。
   - 失败条件：大量 cue 泄漏答案、resolver 不遵守 XML、kept cue 多为泛泛提示。

2. `limit=100` diagnostic
   - 目标：看 MCE 是否在某个 pool state 有信号。
   - 必须输出 transition cards，人工抽查 `MaW_to_C` 和 `MaC_to_W`。

3. MATH500 full
   - 只有在 smoke/100 样本 parser 和 harm 都可接受时跑。
   - 报告仍应写成 diagnostic evidence，不要直接写 final method claim。

## 和 CPAC 的合并方式

若 standalone MCE 有信号，再把 CPAC 的 action 表扩成：

| pool state | CPAC 当前动作 | 可加 MCE 动作 |
|---|---|---|
| collapse | keep initial | suspicious collapse 时 cue scouting / cue resolve |
| minority-bearing | dcac | cue-only resolve 作为 DCAC 前置或对照分支 |
| no-majority conflict | listwise discriminant | cue pool resolve 后再 majority/listwise |
| representation-risk | keep/check | cue 中显式抽 representation pitfall |

代码上可以在 `analyze_candidate_pool` 后新增 action：

```python
if decision.pool_state == "collapse" and should_scout_cues(decision):
    action = "cue_resolve"
elif decision.pool_state == "no_majority_conflict" and args.no_majority_action == "cue_resolve":
    action = "cue_resolve"
```

但这一步应该等 standalone runner 的记录证明 cue branch 能解释 recovery/harm 后再做。

## 当前建议

我建议把 MCE/MCA 第一刀落成 `scripts/run_mce.py`，不是先塞进 `run_cpac_dcac.py`。实现时要把“cue 抽取、cue 过滤、cue-resolve、指标”写成独立函数，并配 `tests/test_mce.py` 覆盖：

- XML cue parser 能解析多 cue。
- answer-leak filter 能拒绝候选答案数字/表达式。
- generic cue filter 能拒绝“be careful / check your work”。
- duplicate cue filter 能去重。
- used_cues parser 能处理 `NONE` 和逗号列表。
- transition metrics 与 `transition_label` 一致。

这样做的好处是：当前 CPAC 正在跑时不会被扰动；MCE/MCA 可以用同一 initial pool 做干净 ablation；如果跑出信号，再作为 CPAC 的通信 action 合并进去，叙事也更自然。
