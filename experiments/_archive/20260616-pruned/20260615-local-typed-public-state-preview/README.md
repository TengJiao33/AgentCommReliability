# Typed Public-State Preview

## What This Is

A local preview of deterministic typed-public-state peer surfaces built from
saved mixed-correctness source cases. It does not call a model.

## Command

```bash
python scripts/build_typed_public_state_preview.py --source-cases-jsonl experiments\_archive\20260616-pruned\20260615-1010-a8002-peer-slot-control-math12\source_cases.jsonl --out-dir experiments\_archive\20260616-pruned\20260615-local-typed-public-state-preview
```

## Summary

| Condition | Records | Contains Source Answer | Anonymous Source | Avg Chars | Max Chars |
| --- | ---: | ---: | ---: | ---: | ---: |
| `correct_typed_public_state` | 12 | 8 | 12 | 929.8 | 1358 |
| `wrong_typed_public_state` | 12 | 6 | 12 | 903.4 | 1617 |

## Notes

- This preview does not call a model; it only checks the deterministic surface shown to a future target model.
- contains_source_answer is a mechanical containment check, not semantic leakage judging.
- Typed-public-state surfaces hide source identity and explicit final-answer slots, but intentionally preserve copied equation/numeric fields for diagnostic pressure.
