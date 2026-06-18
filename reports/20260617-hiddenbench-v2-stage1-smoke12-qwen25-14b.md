# HiddenBench V2 Stage 1 Smoke12

## Judgment

这次 `LIMIT=12` 烟测支持一个更窄但更干净的判断：旧版 `exchange_then_decide` 的主要失败源，至少在前 12 个 HiddenBench task 上，更像是 agent public message 污染和抢答推荐，而不是 final decider 本身不会整合公开事实。`fact_only_exchange` 已经从 `2/12` 提到 `9/12`，而 `fact_only_constraint_decide` 没有再超过它。

这不是 full65 结论，也不是 typed protocol 结论。它只是说明下一步应该先把 sender message surface 当作主变量，而不是直接堆复杂 typed fact card / admission protocol。

## Run

- Run id: `20260617-162153-a8002-hiddenbench-v2-stage1-smoke12-qwen25-14b`
- Local artifacts: `experiments/20260617-162153-a8002-hiddenbench-v2-stage1-smoke12-qwen25-14b/`
- Remote artifacts: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-162153-a8002-hiddenbench-v2-stage1-smoke12-qwen25-14b/`
- Model: `Qwen2.5-14B-Instruct`
- Host/GPU: `A800_2`, GPU `7`
- Conditions: `shared_only`, `full_info`, `oracle_public_facts`, `exchange_then_decide`, `fact_only_exchange`, `fact_only_constraint_decide`
- Prompt logging: enabled
- Analyzer: `experiments/20260617-162153-a8002-hiddenbench-v2-stage1-smoke12-qwen25-14b/analysis_corrected/corrected_summary.json`

## Metrics

| Condition | Correct / Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: |
| `shared_only` | `1/12` | `0.083` | `0` |
| `full_info` | `9/12` | `0.750` | `0` |
| `oracle_public_facts` | `8/12` | `0.667` | `0` |
| `exchange_then_decide` | `2/12` | `0.167` | `0` |
| `fact_only_exchange` | `9/12` | `0.750` | `0` |
| `fact_only_constraint_decide` | `9/12` | `0.750` | `0` |

Key paired contrasts:

- `fact_only_exchange` vs `exchange_then_decide`: `7` fact-only-only correct, `0` exchange-only correct, `2` both correct, `3` both wrong.
- `fact_only_constraint_decide` vs `fact_only_exchange`: identical on all `12` tasks.
- `full_info` vs `fact_only_constraint_decide`: identical on all `12` tasks.
- `oracle_public_facts` vs `fact_only_exchange`: `0` oracle-only correct, `1` fact-only-only correct, `8` both correct, `3` both wrong.

## Message Audit

| Condition | Messages | Private exact | Recommendation leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `45` | `6` | `41` | `25` | `45` | `0.714` |
| `fact_only_exchange` | `45` | `28` | `0` | `4` | `27` | `0.896` |
| `fact_only_constraint_decide` | `45` | `28` | `0` | `4` | `27` | `0.896` |

`answer mentions` 不能直接读成泄漏，因为 HiddenBench 的 task description 本身经常列出选项，私有事实也会自然提到选项名称。更可靠的信号是 recommendation leakage 从 `41/45` 降到 `0/45`，shared-fact overtalk 从 `25/45` 降到 `4/45`，以及 private fact overlap 上升。

## Case Inspection

Task `10` (`emergency_supply_drop`): old exchange chose `Warehouse B`。Agent messages repeatedly reintroduced `Warehouse B` 的共享优势和 tentative recommendation，虽然 A4 报告了 toxic gas risk。Fact-only messages保留 A/B/C 的关键 blocking facts 后，final decider 选 `Warehouse C`。

Task `11` (`emergency_conference_relocation`): old exchange chose `City Library`，因为 agent messages 反复强调 generator / room size，同时弱化了 generator 只够 `2` 小时、School Gym restroom 即将恢复、Community Center chemical leak。Fact-only 后选 `School Gym`。

Task `12` (`evacuate_park_dilemma`): old exchange chose `Red Lake`，尽管 A2 报告唯一道路 sinkhole closed。Fact-only 后 decider 正确把 Red Lake 和 Blueberry Ridge 都排除，选 `Green Valley`。

## Caveats

- Only first `12` tasks, one model, zero temperature.
- Tasks `2`, `6`, and `8` are not clean protocol evidence in this slice because `full_info` / `oracle_public_facts` / `shared_only` sanity conditions are unstable.
- `oracle_public_facts` losing one case to `fact_only_exchange` means oracle prompt itself still has prompt-sensitivity; full65 should report both raw and solvable-subset metrics.
- Automatic invented-fact detection is only a proxy; case claims still need manual inspection.

## Next Gate

Before any full protocol stack, run Stage 1 full65 with the same six conditions and analyze:

- raw condition accuracy;
- subset where `full_info` is correct;
- subset where both `full_info` and `oracle_public_facts` are correct;
- paired `fact_only_exchange` vs `exchange_then_decide`;
- recommendation leakage and shared overtalk rates;
- task-quality failures where clean information conditions fail.

Only if full65 preserves the sender-pollution pattern should we design a v3 protocol. If `fact_only_exchange` already closes most of the gap, the method story should be about public-message role discipline / no-recommendation sender contracts, not typed admission machinery.
