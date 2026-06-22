# HiddenBench Failure Seeds Extraction

日期：2026-06-18

## Purpose

从已有 HiddenBench Stage 1 full65 run 中抽取适合构造 `Hidden-State Admission v0` 的自然 case seeds。

本次不启动模型，不改变 evaluator，不报告新 benchmark 分数。目标是把已有结果中最有用的一类 case 物化出来：干净事实条件能答对，旧自由文本 exchange 答错，fact-only exchange 又能答对。

## Source

- Source run: `experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/`
- Source records: `experiments/20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b/records.jsonl`
- Model in source run: Qwen2.5-14B-Instruct
- Original task count: `65`

## Selection Rule

Case unit: one HiddenBench task.

Selection rule:

```text
full_info_correct
+ oracle_public_facts_correct
+ exchange_then_decide_wrong
+ fact_only_exchange_correct
```

Primary contrast:

```text
old exchange_then_decide vs fact_only_exchange
```

Interpretation target:

```text
The final model can use the needed facts when they are cleanly surfaced,
but free-form public messages fail to preserve an admissible decision surface.
```

## Outputs

| Artifact | Role |
| --- | --- |
| `summary.json` | Machine-readable aggregate counts and selected seed ids. |
| `case_cards.jsonl` | All `32` extracted candidate cases with gold, predictions, private facts, old messages, and message audit metadata. |
| `seed_shortlist.md` | Human-readable 12-case shortlist for `Hidden-State Admission v0`. |

## Summary

- Extracted candidates: `32`
- Recommended v0 seeds: `12`
- `recommendation_leakage`: `32/32`
- `shared_overtalk`: `22/32`
- `private_fact_not_exact`: `31/32`
- `fact_surface_changes_decision`: `32/32`
- `shared_prior_preserved`: `21/32`

## Diagnosis

The extracted cases support a narrow design conclusion: HiddenBench can provide natural decision scenarios where public-message form, not final-answer capability, is the active failure surface.

They do not yet support a State Admission method claim. The next step is to convert a small subset of these cases into source cards, scope rules, verification/rejection perturbations, evidence slots, and downstream decision labels.

## Caveats

- This is offline extraction from a project-local HiddenBench runner, not an official HiddenBench submission.
- The case labels come from message audit heuristics and should be manually checked before becoming gold labels.
- `baker_2010` has a very long and dense private-fact surface; it is useful as a stress case but may be too bulky for v0.
- The recommended seed list is a design shortlist, not a statistical sample.

## Next Action

Build a tiny `Hidden-State Admission v0` draft from `HB10`, `HB11`, `HB12`, and `HB31`, each with base plus one or two perturbations.
