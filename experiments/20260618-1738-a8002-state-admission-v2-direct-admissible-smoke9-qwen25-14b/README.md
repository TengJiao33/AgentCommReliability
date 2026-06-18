# State Admission V2 Direct Admissible-Facts Smoke9 Qwen2.5-14B

日期：2026-06-18

状态：GPU direct-answer control。这个 run 已完成，用来检查 oracle 已经筛出 final_decider admissible facts 后，14B 是否能按 admissible downstream state 作答。

## Launch Record

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Local run dir: `experiments/20260618-1738-a8002-state-admission-v2-direct-admissible-smoke9-qwen25-14b`
- Prompt style: `direct_answer_admissible_facts`
- Model path: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-state-admission-v2-direct-admissible`
- GPU: `7`
- Port: `8072`
- Max tokens: `260`
- Row count: `9`

## Model Result

```text
rows: 9
gold_answer_ok: 0.8889
admissible_downstream_ok: 0.3333
base: gold_answer_ok=1.0000, admissible_downstream_ok=1.0000
perturbation: gold_answer_ok=0.8333, admissible_downstream_ok=0.0000
```

## Diagnosis

Base rows are clean: with oracle-admitted facts, 14B answers Warehouse C, School Gym, and West City.

Perturbations are the key failure. In all six perturbation rows, the scorer expects the final_decider to report insufficient admissible evidence. The model never does. It usually returns the original gold answer anyway; in `hb11_library_fuel_no_final_scope`, it even answers City Library from the remaining partial facts.

This indicates a downstream admissibility failure separate from option-state construction. Even after the evidence set is filtered, the model prefers to force a choice unless the prompt or schema makes abstention unusually salient.

## Caveat

This control uses oracle-admitted facts, so it is not a model admission result. It measures whether the final decision step respects an admissible-evidence boundary once that boundary is provided.
