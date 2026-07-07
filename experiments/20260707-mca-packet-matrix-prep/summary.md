# MCA packet matrix prep

This prep run materializes benchmark splits for the next MCA matrix diagnostics.

## mca_disagreement_v1

- Type: `label_free_disagreement`
- Rows: 221
- Selection uses gold: `false`
- Counts:
  - `dropped`: 279
  - `minority_bearing`: 134
  - `no_majority_conflict`: 87
  - `selected`: 221
  - `source_records`: 500

## mca_gold_contrast_v1

- Type: `gold_stratified_diagnostic`
- Rows: 142
- Selection uses gold: `true`
- Counts:
  - `dropped`: 358
  - `majority_correct_minority_wrong`: 84
  - `majority_wrong_minority_correct`: 20
  - `no_majority_mixed`: 38
  - `selected`: 142
  - `source_records`: 500

## Runner Readiness

- These packets can be consumed by existing runners with `--benchmark math500` and `--split <packet_split>`.
- Existing `run_mca_pre_kv_then_mad.py` already produces low-temperature no-channel first answers, Pre-KV first answers, and Pre-KV-fed MAD final answers.
- Existing `run_mca_pre_kv_then_mad.py` does not yet produce the no-channel-first-fed MAD final condition needed for the full A/B/C/D matrix.
- Existing runners set a global seed at run start. They do not yet record per-row/per-condition/per-agent local seeds, so matrix comparisons remain sensitive to generation order until that is fixed.
