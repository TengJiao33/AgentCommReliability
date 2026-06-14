# PACT Evidence Field Audit

## What We Tried

Ran a CPU-only field-level audit over the saved PACT HotpotQA50 schema v1.1
trace. The audit checks where strict gold-answer signals appear inside PACT's
public action-state fields:

- `Environment State`
- `Action Result`
- `Final Answer`

No model call or GPU run was launched.

## Input

| Source | Path |
| --- | --- |
| PACT v1.1 trace | `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl` |

## Command

```powershell
python scripts\audit_pact_evidence_fields.py `
  --trace experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\comm_trace_pact_v11.jsonl `
  --summary-out experiments\20260614-1326-local-pact-evidence-field-audit\summary.json `
  --cases-out experiments\20260614-1326-local-pact-evidence-field-audit\cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Counts by official EM, evidence-field category, task type, and field-signal totals. |
| `cases.jsonl` | One row per PACT sample with final event fields, strict/relaxed gold signals, and category. |

## What Happened

Official EM remains `17/50` (`0.34`). Among 33 official wrong-EM cases:

| Field category | Count |
| --- | ---: |
| output field already has gold/polarity signal | 23 |
| environment-only strict gold signal | 8 |
| yes/no polarity mismatch or unclear | 1 |
| no strict gold field signal | 1 |

For the 25 wrong non-yes/no cases:

- final answer contains the normalized gold span: `15`
- action result contains the normalized gold span: `15`
- final environment state contains the normalized gold span: `19`
- any environment state contains the normalized gold span: `23`

## Caveats

- Strict field signals are diagnostics, not alternate official scores.
- Yes/no cases use final-answer first-token polarity rather than literal gold
  containment in evidence fields.
- Relaxed signals only flag simple possessive/plural mismatches; they are not
  scoring rules.
