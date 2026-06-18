# Raw Answer-Only Surface Repair

Date: 2026-06-15

## Why This Exists

The MATH200 claim-hygiene pass found that the legacy `answer_only` surface was
not a clean final-answer-authority control. It displayed the older parsed
numeric answer field, so symbolic peer answers such as `2\sqrt{3}`,
`1 - 12i`, and `8\pi - 16` could be shown as `3`, `12`, or `16`.

This pass fixes the surface construction path without running a model. Existing
`correct_answer_only` and `wrong_answer_only` conditions are left unchanged for
reproducibility. New conditions are added for future runs:

- `correct_raw_answer_only`
- `wrong_raw_answer_only`

These extract the raw final-answer text from the saved peer response and show
that text directly.

## Artifacts

- Surface helper:
  `scripts/peer_probe/answers.py`
- Peer surface implementation:
  `scripts/peer_probe/surfaces.py`
- Runner caveat:
  `scripts/run_peer_exposure_probe.py`
- Protocol/statistical audit metadata:
  `scripts/audit_peer_influence_protocol.py`
  `scripts/audit_math_semantic_correctness.py`
  `scripts/audit_peer_exposure_statistics.py`
  `scripts/audit_peer_source_label_packet.py`
- Local preview builder:
  `scripts/build_raw_answer_only_preview.py`
- Preview packet:
  `experiments/_archive/20260616-pruned/20260615-local-raw-answer-only-preview/`

## Preview Result

The preview reads the saved MATH200 source-case pool and compares the legacy
numeric answer-only text against the raw answer extracted from the same peer
response. It does not call a model.

Input:

- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/source_cases.jsonl`

Output:

- `experiments/_archive/20260616-pruned/20260615-local-raw-answer-only-preview/raw_answer_only_preview.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-raw-answer-only-preview/summary.json`
- `experiments/_archive/20260616-pruned/20260615-local-raw-answer-only-preview/README.md`

Counts over `59` source cases and `118` correct/wrong peer answer-only rows:

| Bucket | Rows |
| --- | ---: |
| Equivalent | `84` |
| Semantic mismatch | `27` |
| Unknown equivalence | `7` |
| Display changed | `38` |

By polarity:

| Polarity | Equivalent | Semantic mismatch | Unknown |
| --- | ---: | ---: | ---: |
| Correct peer | `40` | `14` | `5` |
| Wrong peer | `44` | `13` | `2` |

Spot checks:

- Case `11`: legacy correct answer-only shows `3`; raw shows `2\sqrt{3}`.
- Case `13`: legacy correct answer-only shows `12`; raw shows `1 - 12i`.
- Case `60`: legacy correct answer-only shows `16`; raw shows `8\pi - 16`.

## Interpretation

This repairs a control surface, not a claim. The existing MATH200 conclusions
remain bounded:

- legacy `answer_only` rows should not be used as clean final-answer-authority
  evidence on symbolic MATH;
- full-rationale, redacted-rationale, equation-surface, and typed-state
  readouts from existing runs are not changed by this preview;
- future MATH peer-influence packets should include raw answer-only if they
  need a final-answer-authority baseline.

The new raw surface should still be interpreted through a semantic audit after
any model run, because saved peer-answer adoption remains numeric-parser based
until recomputed.

## Validation

Passed:

```text
python -m py_compile scripts\peer_probe\answers.py scripts\peer_probe\surfaces.py scripts\run_peer_exposure_probe.py scripts\audit_peer_influence_protocol.py scripts\audit_math_semantic_correctness.py scripts\audit_peer_exposure_statistics.py scripts\audit_peer_source_label_packet.py scripts\build_raw_answer_only_preview.py
```

Ran:

```text
PYTHONPATH=scripts python scripts\build_raw_answer_only_preview.py --source-cases-jsonl experiments\20260615-1151-a8002-typed-public-state-math200-anon\source_cases.jsonl --out-dir experiments\_archive\20260616-pruned\20260615-local-raw-answer-only-preview
```

## Next Contact

Do not launch another MATH GPU run solely for this repair. The useful next
steps are:

1. use `correct_raw_answer_only` / `wrong_raw_answer_only` only when a future
   peer-influence packet genuinely needs an answer-authority control;
2. finish or extend field labels on the existing claim-hygiene packet;
3. bridge the protocol to a split-evidence public-state task, where
   communication is necessary rather than injected.
