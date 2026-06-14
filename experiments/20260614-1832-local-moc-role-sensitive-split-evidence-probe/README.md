# 20260614-1832-local-moc-role-sensitive-split-evidence-probe

## What We Tried

Ran a CPU-only MOC-style role-loss probe over six split-evidence cases. The
probe compares one-hop direct context, two-hop unmerged context, and three
compressed summary surfaces.

## Scope

- Method family: `MOCRoleCompressionProbe`
- Model: deterministic synthetic policies
- Dataset: hand-built split-evidence role cases
- Samples: `6`
- GPU: none
- Evidence level: contact/schema pressure only

## Command

```bash
python scripts/run_moc_role_loss_probe.py --run-id 20260614-1832-local-moc-role-sensitive-split-evidence-probe --out-dir experiments\20260614-1832-local-moc-role-sensitive-split-evidence-probe --include-text
```

## Outputs

- `comm_trace_moc_role_probe_v11.jsonl`
- `cases.jsonl`
- `summary.json`
- `manifest.json`

## Result

| Policy | Correct | Accuracy | Role-Loss Records | Avg Total Tokens | Avg Compressed Tokens | Transitions vs Hop2 Unmerged |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| hop1_direct_context | 0/6 | 0.00 | 6 | 34.0 | 0.0 | {"right_to_wrong": 6} |
| hop2_unmerged_context | 6/6 | 1.00 | 0 | 51.3 | 0.0 | {"stable_right": 6} |
| hop2_role_aware_merge | 6/6 | 1.00 | 0 | 44.7 | 29.8 | {"stable_right": 6} |
| hop2_flat_entity_merge | 1/6 | 0.17 | 6 | 26.7 | 11.8 | {"right_to_wrong": 5, "stable_right": 1} |
| hop2_answer_only_merge | 1/6 | 0.17 | 6 | 21.5 | 6.5 | {"right_to_wrong": 5, "stable_right": 1} |

## Case Surface

| Sample | Case | Family | Gold | Wrong Policies |
| ---: | --- | --- | --- | --- |
| 0 | `moc-role-city-population` | granularity_switch | `35124` | `hop1_direct_context`, `hop2_flat_entity_merge`, `hop2_answer_only_merge` |
| 1 | `moc-role-mentor-instrument` | clue_object_replaces_answer_object | `viola` | `hop1_direct_context`, `hop2_flat_entity_merge`, `hop2_answer_only_merge` |
| 2 | `moc-role-company-headquarters` | predicate_drift | `Riverton` | `hop1_direct_context`, `hop2_flat_entity_merge`, `hop2_answer_only_merge` |
| 3 | `moc-role-archive-collection` | useful_bridge_refinement | `drawings` | `hop1_direct_context` |
| 4 | `moc-role-genre-comparison` | comparison_aggregation_loss | `yes` | `hop1_direct_context`, `hop2_flat_entity_merge`, `hop2_answer_only_merge` |
| 5 | `moc-role-cyclone-film` | distractor_anchor_switch | `Cyclone Odra` | `hop1_direct_context`, `hop2_flat_entity_merge`, `hop2_answer_only_merge` |

## Things Noticed

- A role-aware compressed surface preserves all cases in this probe.
- Flat entity compression and answer-only compression fail when they erase the
  distinction between clue object, bridge entity, requested relation, and
  answer object.
- The archive/collection case stays correct under flat compression, which keeps
  the important caveat alive: target movement can be useful bridge refinement,
  not only drift.

## Caveats

- This is not a MOC benchmark or an LLM result.
- The deterministic policies are stress surfaces for trace/schema design.
- The useful output is the role-loss audit shape, not the accuracy number.

## Timeline

- `2026-06-14T18:37:29`: launched
- `2026-06-14T18:37:29`: completed
