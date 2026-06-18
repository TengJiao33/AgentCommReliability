# HiddenBench V2 Stage 1 Full65

## 核心判断

Full65 保住了 smoke12 的主信号：旧 `exchange_then_decide` 在 65 题上只有 `24/65`，`fact_only_exchange` 到 `57/65`，接近 `full_info` 的 `59/65`。在更干净的 `full_info + oracle_public_facts` 同时正确的 55 题子集上，`fact_only_exchange` 是 `55/55`，旧 exchange 是 `23/55`。

这个结果把下一步 idea 推向 sender public-state discipline：标准 exchange prompt 让 sender 把私有事实、共享优势和 tentative recommendation 混成 public message，事实表面被污染；只让 sender 报告自己的 private fact 后，final decider 在 clean-info 任务上几乎完全恢复。

## Run

- Run id: `20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b`
- Local artifacts: `experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/`
- Remote artifacts: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/`
- Model: `Qwen2.5-14B-Instruct`
- Host/GPU: `A800_2`, GPU `7`
- Conditions: `shared_only`, `full_info`, `oracle_public_facts`, `exchange_then_decide`, `fact_only_exchange`, `fact_only_constraint_decide`
- Prompt logging: enabled
- Corrected analyzer: `experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/analysis_corrected/corrected_summary.json`
- Subset analyzer: `experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/analysis_corrected/subset_summary.json`

## Raw Metrics

| Condition | Correct / Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: |
| `shared_only` | `1/65` | `0.015` | `0` |
| `full_info` | `59/65` | `0.908` | `0` |
| `oracle_public_facts` | `56/65` | `0.862` | `0` |
| `exchange_then_decide` | `24/65` | `0.369` | `0` |
| `fact_only_exchange` | `57/65` | `0.877` | `0` |
| `fact_only_constraint_decide` | `56/65` | `0.862` | `0` |

Primary paired contrast:

- `fact_only_exchange` vs `exchange_then_decide`: `34` fact-only-only correct, `1` exchange-only correct, `23` both correct, `7` both wrong.
- `fact_only_constraint_decide` vs `fact_only_exchange`: `0` constraint-only correct, `1` fact-only-only correct, `56` both correct, `8` both wrong.

## Clean Subsets

On `full_info_correct` tasks:

| Condition | Correct / Records | Accuracy |
| --- | ---: | ---: |
| `exchange_then_decide` | `24/59` | `0.407` |
| `fact_only_exchange` | `57/59` | `0.966` |
| `fact_only_constraint_decide` | `56/59` | `0.949` |
| `oracle_public_facts` | `55/59` | `0.932` |

On `full_info_and_oracle_correct` tasks:

| Condition | Correct / Records | Accuracy |
| --- | ---: | ---: |
| `exchange_then_decide` | `23/55` | `0.418` |
| `fact_only_exchange` | `55/55` | `1.000` |
| `fact_only_constraint_decide` | `55/55` | `1.000` |

This subset is the cleanest readout: when the model can solve the task from all facts and from clean public private facts, fact-only sender messages close the gap completely, while old exchange leaves `32/55` tasks on the table.

## Message Audit

| Condition | Messages | Private exact | Recommendation leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `253` | `6` | `225` | `134` | `247` | `0.656` |
| `fact_only_exchange` | `253` | `198` | `0` | `4` | `162` | `0.951` |
| `fact_only_constraint_decide` | `253` | `198` | `0` | `4` | `162` | `0.951` |

`answer mentions` is a weak proxy because HiddenBench descriptions and private facts naturally mention option names. The stronger audit signal is recommendation leakage dropping from `225/253` to `0/253`, shared-fact overtalk dropping from `134/253` to `4/253`, and average private-fact overlap rising from `0.656` to `0.951`.

## Boundary Cases

The only exchange-only task is `13` (`Laboratory Theft Deduction`): old exchange gets `Lab Gamma`, while fact-only chooses `Lab Alpha`. This task is not clean evidence against fact-only because `oracle_public_facts` also chooses `Lab Alpha`; the clean public-fact prompt itself is unstable.

The two `full_info` correct but `fact_only_exchange` wrong tasks are `13` and `29` (`Safe Shelter Selection`). Both are also `oracle_public_facts` wrong, so the failure is more plausibly a prompt/task interpretation boundary than a sender-message regression.

The only `fact_only_constraint_decide` regression is `53` (`sensor_placement_decision`): fact-only exchange chooses the gold `Mountain Ridge`, while the constraint table chooses `Ocean Bluff`. This weakens the case for adding a heavier final-integration prompt now.

The unstable clean-information set has `10` tasks: `full_info` is wrong on `6`, and `oracle_public_facts` is wrong on `9`. Those tasks should be quarantined or separately diagnosed before any paper-facing rate claim.

## Interpretation

The live idea should move from typed/admission machinery to sender public-state discipline. The current strongest mechanism is premature recommendation pollution: partial agents turn local private facts into option advocacy, repeat attractive shared facts, and cause the final decider to optimize over noisy recommendations rather than over the hidden-profile facts.

Fact-only messaging is a surprisingly strong intervention because it holds the final decision prompt almost constant while cleaning the sender surface. The constraint final prompt does not improve over the same fact-only messages, so the next design step should isolate which sender rule matters: no recommendation, no shared-fact repetition, exact private-fact reporting, or forbidding option ranking.

## Caveats

- This is a project-local HiddenBench protocol, not the official group-interaction harness.
- One model family, one model size, zero temperature.
- Prompt logging and automatic message audits make the failure visible, but invented-fact and option-mention labels remain proxy measurements.
- Clean-subset results are strong for diagnosis, but raw benchmark reporting must keep the unstable `full_info` / `oracle_public_facts` tasks visible.
- The result supports a benchmark-grounded direction, not a complete method claim.

## Next Gate

Before building a complex v3 protocol, run a small sender-ablation packet that separates:

- old exchange with tentative recommendation;
- no-recommendation exchange while still allowing concise decision-relevant facts;
- fact-only exchange;
- fact-only exchange with no answer-option list in the sender prompt if the task text permits it.

If no-recommendation alone recovers most of fact-only, the paper handle is premature recommendation. If exact private-fact reporting is required, the handle is reliable public fact state. If neither transfers to PACT-style split evidence or another benchmark, HiddenBench remains a diagnosis rather than the main story.
