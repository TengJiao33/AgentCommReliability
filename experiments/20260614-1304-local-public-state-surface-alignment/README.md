# Public State Surface Alignment

## What We Tried

Aligned two existing public-message surfaces into a common local JSONL shape:

- DAR typed retained-message previews from selected GSM8K cases.
- PACT action-state messages from the Qwen2.5-14B HotpotQA50 smoke.

This was a local CPU-only text parsing step. No model call or GPU run was
launched.

## Inputs

| Source | Path |
| --- | --- |
| DAR typed preview | `experiments/20260614-1258-local-dar-typed-surface-preview/typed_surface_preview.jsonl` |
| PACT HotpotQA50 result | `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/pact_qwen25_14b_hotpot50.jsonl` |

## Command

```powershell
python scripts\align_public_state_surfaces.py `
  --dar-preview experiments\20260614-1258-local-dar-typed-surface-preview\typed_surface_preview.jsonl `
  --pact-result experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\pact_qwen25_14b_hotpot50.jsonl `
  --summary-out experiments\20260614-1304-local-public-state-surface-alignment\summary.json `
  --records-out experiments\20260614-1304-local-public-state-surface-alignment\public_state_surface_records.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Aggregate counts, field presence, average text lengths, and alignment gaps. |
| `public_state_surface_records.jsonl` | 232 normalized public-state records under schema `acr.public_state_surface.v0`. |

## What Happened

The normalized records cover:

| Source | Records | Surface |
| --- | ---: | --- |
| DAR | 32 | `typed_answer_evidence_preview` |
| PACT | 200 | `action_state` |

Field presence:

| Field | Count |
| --- | ---: |
| `Action Required` | 232/232 |
| `Environment State` | 232/232 |
| `Action Result` | 232/232 |
| `Final Answer` | 50/232 |

Average state length:

| Source | Avg state chars | Avg raw-output chars |
| --- | ---: | ---: |
| DAR typed preview | 157.2 | 1089.0 |
| PACT action-state | 363.9 | 363.9 |

No PACT output in this local result contained a `<think>` span, so raw output
and public state are identical for this run.

## Alignment Gaps

- DAR typed previews map parsed answers to `Action Result` and selected
  calculation lines to `Environment State`, but `Action Required` is synthetic.
- PACT `Environment State` is intended to be a verbatim evidence sentence from
  private context; DAR `Environment State` is heuristic text extracted from a
  generated retained response.
- PACT has an explicit `strip_think_tags` public-history rule in code; DAR
  typed preview currently has only an offline promise not to forward full
  responses.

## Caveats

- This is a schema/content alignment, not model behavior.
- DAR cases are selected diagnostics, while PACT records come from a 50-sample
  HotpotQA smoke.
- `acr.public_state_surface.v0` is an experimental local alignment format, not
  yet part of the main communication trace schema.
