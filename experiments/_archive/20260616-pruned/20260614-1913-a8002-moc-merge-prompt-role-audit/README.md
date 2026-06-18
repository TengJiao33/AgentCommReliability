# 20260614-1913-a8002-moc-merge-prompt-role-audit

## What We Tried

Ran the five MOC merge prompts against the six synthetic split-evidence role
cases from the previous MOC role-loss probe. This only audits the merge prompt;
it does not run the MOC graph.

## Scope

- Method family: `MOCMergePromptRoleAudit`
- Model: `qwen2.5-7b-merge-audit`
- Cases: `6`
- Records: `60`
- Surfaces: `labeled_role_messages, natural_evidence_messages`

## Command

```bash
python scripts/run_moc_merge_prompt_role_audit.py --run-id 20260614-1913-a8002-moc-merge-prompt-role-audit --cases-jsonl cases.jsonl --out-dir out --base-url http://127.0.0.1:8022/v1 --model qwen2.5-7b-merge-audit --api-key EMPTY --temperature 0.1 --max-tokens 220 --request-timeout 120 --kppa 45 --include-prompts --machine A800_2 --gpu-ids 1 --server-log /data/xuhaoming/yfy/research_workspace/logs/moc-merge-prompt-role-audit-vllm-20260614_1913.log
```

## Outputs

- `comm_trace_moc_merge_prompt_role_audit_v11.jsonl`
- `merge_outputs.jsonl`
- `summary.json`
- `manifest.json`

## Surface Summary

| Merge Surface | Records | All Slots Preserved | Rate | Avg Preserved Slots | Slot Loss Counts |
| --- | ---: | ---: | ---: | ---: | --- |
| labeled_role_messages | 30 | 19 | 0.63 | 6.40 | {'answer_type': 1, 'bridge_entity': 1, 'clue_object': 4, 'forbidden_replacement': 6, 'gold_answer': 3, 'requested_relation': 2, 'required_qualifier': 1} |
| natural_evidence_messages | 30 | 4 | 0.13 | 5.13 | {'answer_type': 2, 'bridge_entity': 1, 'clue_object': 10, 'forbidden_replacement': 21, 'gold_answer': 1, 'requested_relation': 8, 'required_qualifier': 13} |

## Strategy Summary

| Merge Surface | Strategy | Name | All Slots Preserved | Avg Preserved Slots | Source Attribution |
| --- | ---: | --- | ---: | ---: | ---: |
| labeled_role_messages | 1 | narrative_synthesis | 4/6 | 6.67 | 0/6 |
| labeled_role_messages | 2 | logical_integrity | 4/6 | 6.67 | 0/6 |
| labeled_role_messages | 3 | technical_precision | 6/6 | 7.00 | 6/6 |
| labeled_role_messages | 4 | actionable_intelligence | 2/6 | 5.50 | 5/6 |
| labeled_role_messages | 5 | dedup_structure | 3/6 | 6.17 | 0/6 |
| natural_evidence_messages | 1 | narrative_synthesis | 0/6 | 5.33 | 0/6 |
| natural_evidence_messages | 2 | logical_integrity | 1/6 | 4.33 | 0/6 |
| natural_evidence_messages | 3 | technical_precision | 3/6 | 6.00 | 6/6 |
| natural_evidence_messages | 4 | actionable_intelligence | 0/6 | 5.00 | 6/6 |
| natural_evidence_messages | 5 | dedup_structure | 0/6 | 5.00 | 0/6 |

## Caveats

- This is a merge-prompt audit, not a MOC run.
- The audit uses lexical slot checks over synthetic cases.
- No claim is made about benchmark accuracy or the full MOC summarizer path.

## Timeline

- `2026-06-14T19:17:07`: launched
- `2026-06-14T19:17:51`: completed
