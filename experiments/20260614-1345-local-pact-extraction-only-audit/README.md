# PACT Extraction-Only Audit

## What We Tried

Ran a CPU-only deterministic extraction audit over the corrected PACT HotpotQA50
schema v1.1 trace. Candidates are generated from saved PACT action-state fields
without using gold labels; gold is used only afterward to evaluate whether a
candidate would exact-match.

No model call or GPU run was launched.

## Input

| Source | Path |
| --- | --- |
| Corrected PACT v1.1 trace | `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl` |

## Command

```powershell
python scripts\audit_pact_extraction_only.py `
  --trace experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\comm_trace_pact_v11.jsonl `
  --summary-out experiments\20260614-1345-local-pact-extraction-only-audit\summary.json `
  --cases-out experiments\20260614-1345-local-pact-extraction-only-audit\cases.jsonl
```

## Outputs

| File | Contents |
| --- | --- |
| `summary.json` | Official EM, deterministic final-answer policy result, candidate upper bounds, rule counts, transitions. |
| `cases.jsonl` | One row per sample with policy candidate, matching candidates, and transition label. |

## What Happened

Official EM remains `17/50` (`0.34`).

The fixed final-answer-only extraction policy reaches `32/50` (`0.64`):

- `15` official wrong-EM samples become exact matches;
- `17` official correct samples stay exact matches;
- `18` samples remain wrong;
- `0` official correct samples regress.

Candidate upper bounds:

| Candidate scope | Correct if any candidate is allowed | Wrong cases with a matching candidate |
| --- | ---: | ---: |
| final event fields only | `39/50` | `22/33` |
| all public action-state fields | `41/50` | `24/33` |

## Caveats

- Candidate upper bounds are not deployable scores because they use gold during
  evaluation to decide whether any generated candidate matched.
- The fixed final-answer policy is a heuristic diagnostic, not a new PACT
  method.
- The result says extraction/answer contract is a major confound in this smoke;
  it does not prove the remaining wrong cases are all reasoning failures.
