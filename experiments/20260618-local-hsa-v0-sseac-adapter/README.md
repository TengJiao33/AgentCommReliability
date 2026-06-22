# HSA-v0 SSEAC Adapter Smoke

日期：2026-06-18

## 目的

这次本地 smoke 把 `HiddenBench` 的三条 fact-unit draft 转成 `Hidden-State Admission v0` 的 SSEAC packet，并用三个透明条件跑通 compiler 和 HSA scorer。

本记录没有调用模型。它只验证 HSA-v0 的 packet/gold/scorer 入口是否能承接后续 `ours_sseac_v0` 小样本模型 run。

## Preflight Contract

```text
purpose:
  将 HiddenBench-derived fact-unit drafts 转成 source cards、required slots、expected final decision，并验证本地 oracle / baseline 闭环。

unit:
  一个 HiddenBench-derived HSA-v0 packet row。当前包含 3 个 base rows 和 6 个同文本 source/scope/verification perturbation rows。

primary contrast:
  oracle_admissible_facts vs shared_only_verified vs all_scoped_verified。

secondary contrasts:
  后续接 direct state generation 与 ours_sseac_v0。

success_signal:
  packet 能通过 SSEAC compiler；oracle_admissible_facts 得到 9/9 strict；shared_only_verified 在 base rows 暴露不足；perturbation rows 能返回 insufficient_evidence。

failure_signal:
  oracle_admissible_facts 低于 9/9；packet_id 对不齐；perturbation rows 仍输出 gold answer；compiler/scorer 不能区分 base 与 perturbation。

invalidation_conditions:
  required_slots、gold_answer、oracle_unit_ids 被渲染进模型 prompt；same-text perturbation 改动了事实文本；score 只看 final answer strict 而忽略 extra admitted cards。
```

## 输入

- Fact draft: `experiments/20260618-local-state-admission-v2-preflight/hiddenbench_fact_units.draft.json`
- Perturbation draft: `experiments/20260618-local-state-admission-v2-preflight/source_scope_perturbations.draft.json`
- Builder: `scripts/build_hsa_v0_sseac_packet.py`
- Compiler: `scripts/compile_sseac_v0.py`
- Scorer: `scripts/score_hsa_v0_compiled.py`

## 命令

```powershell
python -m py_compile scripts/build_hsa_v0_sseac_packet.py scripts/score_hsa_v0_compiled.py scripts/compile_sseac_v0.py
python scripts/build_hsa_v0_sseac_packet.py --out-dir experiments/20260618-local-hsa-v0-sseac-adapter

$out='experiments/20260618-local-hsa-v0-sseac-adapter'
$packet="$out/hsa_v0_packet.jsonl"
$conds=@('oracle_admissible_facts','shared_only_verified','all_scoped_verified')
foreach($c in $conds){
  python scripts/compile_sseac_v0.py --packet $packet --predictions "$out/predictions_$c.jsonl" --out "$out/compiled_$c.jsonl" --summary-out "$out/summary_compile_$c.json"
  python scripts/score_hsa_v0_compiled.py --packet $packet --compiled "$out/compiled_$c.jsonl" --out "$out/scores_$c.jsonl" --summary-out "$out/summary_hsa_$c.md"
}
```

## 结果

| Condition | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `oracle_admissible_facts` | 9/9 | 1.0000 | 1.0000 | 0.8333 | 0 | 0.0000 |
| `shared_only_verified` | 6/9 | 0.0000 | 1.0000 | 0.1759 | 24 | 0.3333 |
| `all_scoped_verified` | 9/9 | 1.0000 | 1.0000 | 0.8333 | 24 | 0.0000 |

## 读法

`oracle_admissible_facts` 9/9 说明 HSA-v0 adapter、SSEAC compiler、HSA scorer 的闭环成立。base rows 能选择 gold answer；verification/scope perturbation rows 能返回 `insufficient_evidence`。

`shared_only_verified` 在 base rows 为 0/3，说明只给共享事实不足以支持 HiddenBench 的正确决策。它在 perturbation rows 为 6/6，因为这些 rows 的预期本来就是证据不足。

`all_scoped_verified` 9/9 暴露出当前 HSA-v0 的重要边界：只要把所有已核验且可给 final_decider 的事实都塞进去，answer strict 可以满分。但它带来 `24` 张额外 final cards，说明最终主表必须同时报告 over-admission / evidence discipline，不能只报告 answer strict。

## Artifacts

- Packet: `hsa_v0_packet.jsonl`
- Predictions: `predictions_oracle_admissible_facts.jsonl`, `predictions_shared_only_verified.jsonl`, `predictions_all_scoped_verified.jsonl`
- Compiled: `compiled_oracle_admissible_facts.jsonl`, `compiled_shared_only_verified.jsonl`, `compiled_all_scoped_verified.jsonl`
- Scores: `scores_oracle_admissible_facts.jsonl`, `scores_shared_only_verified.jsonl`, `scores_all_scoped_verified.jsonl`
- Summaries: `summary_hsa_oracle_admissible_facts.md`, `summary_hsa_shared_only_verified.md`, `summary_hsa_all_scoped_verified.md`

## 下一步

下一步应补 HSA-v0 prompt runner，让模型在看不到 `required_slots`、`gold_answer`、`oracle_unit_ids` 的情况下输出 SSEAC `candidate_units`。第一轮只跑 3-5 行，重点看 schema adherence、slot recall、insufficient handling 和 extra final cards。
