# DAR Typed Surface Preview

## What We Tried

Constructed an offline typed retained-message surface from existing DAR raw
histories for selected cases `5`, `20`, `22`, and `37`.

This was a local CPU-only preview. No model call or GPU run was launched.

The preview surface is:

```text
source_agent: <agent>
parsed_final_answer: <parsed answer>
evidence:
- <selected calculation/evidence line>
- <selected calculation/evidence line>
```

The extraction heuristic does not use gold answers or parsed correctness. It
keeps the last calculation-looking line and one high-scoring earlier
calculation/evidence line from each retained full response.

## Command

```powershell
python scripts\preview_dar_typed_surface.py `
  --case-index 5 `
  --case-index 20 `
  --case-index 22 `
  --case-index 37 `
  --history original=experiments\20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory\dar_history_gsm8k100_filtercritical.jsonl `
  --history guarded_answer_only=experiments\20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100\dar_history_guarded_answer_diversity_gsm8k100.jsonl `
  --history answer_only_no_guard=experiments\20260613-2143-a8002-dar-retention-split-gsm8k100\dar_history_answer_only_noguard_gsm8k100.jsonl `
  --history guard_full=experiments\20260613-2143-a8002-dar-retention-split-gsm8k100\dar_history_guard_full_gsm8k100.jsonl `
  --trace original=experiments\20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory\comm_trace_dar_v11.jsonl `
  --trace guarded_answer_only=experiments\20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100\comm_trace_dar_guarded_v11.jsonl `
  --trace answer_only_no_guard=experiments\20260613-2143-a8002-dar-retention-split-gsm8k100\comm_trace_answer_only_noguard_v11.jsonl `
  --trace guard_full=experiments\20260613-2143-a8002-dar-retention-split-gsm8k100\comm_trace_guard_full_v11.jsonl `
  --evidence-lines-per-agent 2 `
  --summary-out experiments\20260614-1258-local-dar-typed-surface-preview\summary.json `
  --preview-out experiments\20260614-1258-local-dar-typed-surface-preview\typed_surface_preview.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Case/variant summary plus aggregate character counts. |
| `typed_surface_preview.jsonl` | One row per retained peer with answer-only, full, and typed preview surfaces. |

## What Happened

The preview covers 16 case variants and 32 retained messages.

| Surface | Average characters per retained message |
| --- | ---: |
| answer-only | 33.8 |
| typed preview | 157.2 |
| full response | 1089.0 |

For sample `20`, the preview keeps the central mismatch:

```text
source_agent: Agent3
parsed_final_answer: 700.0
evidence:
- Five lollipops cost \(5 \times 0.40 = 2.00\) dollars.
- \[4.00 + 3.00 = 7.00\] dollars.
```

This is exactly the information answer-only removed: Agent3 is parsed as
`700.0`, but the retained reasoning contains the correct `$7.00` computation.

## Things Noticed

- Typed preview is much shorter than full reasoning while preserving some
  calculation evidence that answer-only deletes.
- Sample `20` remains the sharpest diagnostic: a typed surface can expose both
  the parsed final answer and contradictory evidence in the same message.
- Sample `22` shows why this should remain a preview for now. The retained
  answer can be empty, but the raw response still contains extractable
  calculation lines; whether those lines are useful requires prompt inspection
  before a model run.
- Sample `37` shows the heuristic is still rough: it sometimes selects long
  narrative arithmetic lines, so the surface needs tightening before becoming
  a DAR patch.

## Caveats

- This is not model evidence and does not prove an accuracy gain.
- The evidence-line extractor is heuristic and arithmetic-oriented.
- Parsed correctness is included in the JSON only for audit; it is not used to
  choose evidence lines.
