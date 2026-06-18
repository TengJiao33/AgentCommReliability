# Raw Answer-Only Preview

## What This Is

A local preview comparing legacy numeric `answer_only` surfaces with
new raw-answer-only surfaces built from saved peer responses. It does
not call a model.

## Command

```bash
python scripts/build_raw_answer_only_preview.py --source-cases-jsonl experiments\20260615-1151-a8002-typed-public-state-math200-anon\source_cases.jsonl --out-dir experiments\_archive\20260616-pruned\20260615-local-raw-answer-only-preview
```

## Summary

| Bucket | Rows |
| --- | ---: |
| `equivalent` | 84 |
| `semantic_mismatch` | 27 |
| `display_changed` | 38 |
| `unknown_equivalence` | 7 |

By polarity:

| Polarity | Equivalent | Semantic mismatch | Unknown |
| --- | ---: | ---: | ---: |
| `correct` | 40 | 14 | 5 |
| `wrong` | 44 | 13 | 2 |

## Notes

- This preview does not call a model; it only compares the legacy numeric answer-only surface with the raw final-answer text extracted from the saved peer response.
- The raw answer-only surface is meant for future peer-influence controls on symbolic MATH answers; existing answer-only runs remain reproducible as legacy parser surfaces.
- Equivalence is conservative and may remain unknown for forms such as base notation or hard-to-parse generated answer strings.
