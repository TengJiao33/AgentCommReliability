# State Admission V2 Direct All-Facts Smoke9 Qwen2.5-14B

日期：2026-06-18

状态：GPU direct-answer control。这个 run 已完成，用来检查 14B 在不构造 admission units 时，是否能直接从所有 facts 解出原始 HiddenBench gold answer。

## Launch Record

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Local run dir: `experiments/20260618-1732-a8002-state-admission-v2-direct-allfacts-smoke9-qwen25-14b`
- Prompt style: `direct_answer_all_facts`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-state-admission-v2-direct-allfacts`
- GPU: `7`
- Port: `8072`
- Max tokens: `260`
- Row count: `9`

## Model Result

```text
rows: 9
gold_answer_ok: 0.6667
admissible_downstream_ok: 0.2222
base: gold_answer_ok=0.6667, admissible_downstream_ok=0.6667
perturbation: gold_answer_ok=0.6667, admissible_downstream_ok=0.0000
```

## Diagnosis

The model answers all three supply-drop variants as Warehouse B, even when all hidden facts are present. Its rationales cite the tempting shared-context facts and the Warehouse B gas fact together, but still treat Warehouse B as the best option. This means the supply-drop sketch has a strong direct-answer distractor; admission prompting helped 14B recover Warehouse C in the option-state run.

Conference and evacuation are easier under all-facts direct answer. The model returns School Gym and West City in the expected sketches, including perturbations. Those perturbation answers are intentionally wrong under the admissible-evidence story, but they show the original task answer remains salient.

## Caveat

This control should not be scored with admission `strict`. It is a direct-answer diagnostic. Its main metric is `gold_answer_ok`; `admissible_downstream_ok` is included only to show how often raw direct answering disagrees with the admissible final-decider state.
