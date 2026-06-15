# PACT Typed Boundary Split Packet

Date: 2026-06-15

## What We Tried

Turned the Authority Injection Arena's main caveat into a stricter protocol
split. The prior arena showed that typed-state quarantine rescues many
wrong-contract and forged-final failures, but the typed state also included a
model-visible `Untrusted Candidate` field. That made the result ambiguous:
typed roles may help, while visible candidates may become a new authority
surface.

New setup artifacts:

- builder: `scripts/build_pact_typed_boundary_split_packet.py`
- evaluator: `scripts/evaluate_pact_typed_boundary_split.py`
- A800_2 runner template: `scripts/run_pact_typed_boundary_split_a8002.sh`
- local packet:
  `experiments/20260615-local-pact-typed-boundary-split-packet/`

No A800 run was launched in this step.

## Packet Shape

The packet reuses the same `40` source cases as the authority injection arena:

- `32` positive target-focus cases;
- `8` negative-control cases;
- `440` prompt rows;
- `11` variants per case.

Anchor variants:

- `original_untyped_public`;
- `wrong_contract_public_task`;
- `forged_final_commitment`.

Typed-boundary variants:

- `typed_no_candidate`;
- `typed_candidate_hidden`;
- `typed_candidate_visible`;
- `typed_candidate_visible_extract_first`;
- `typed_wrong_contract_no_candidate`;
- `typed_wrong_contract_candidate_hidden`;
- `typed_wrong_contract_candidate_visible`;
- `typed_wrong_contract_candidate_visible_extract_first`.

The hidden-candidate variants deliberately share model-visible prompts with the
matching no-candidate variants. The candidate exists only as evaluator
metadata. This makes the split direct:

```text
hidden/no-candidate gap: evaluator-only lure matching;
visible/hidden gap: effect of showing the candidate field;
extract-first/visible gap: effect of staging the protocol before candidate comparison.
```

## Validation

Local checks passed:

- `python -m py_compile` passed for the builder and evaluator.
- Builder generated `440` packet rows.
- Gold-smoke evaluation produced EM `1.000` and average F1 `1.000` over
  `440/440` rows.
- Candidate scoring split:
  - candidate-available rows: `280`;
  - visible-candidate rows: `200`;
  - hidden-candidate rows: `80`.
- Hidden-leak check:
  - `80/80` hidden rows have no explicit `Untrusted Candidate:` line;
  - `80/80` hidden rows have no `Candidate surface:` phrase;
  - `160/160` visible rows contain an explicit `Untrusted Candidate:` line.

Gold-smoke outputs:

- `experiments/20260615-local-pact-typed-boundary-split-packet/gold-smoke/summary.json`
- `experiments/20260615-local-pact-typed-boundary-split-packet/gold-smoke/summary.md`

## Why This Is The Next Pressure

This is the smallest object that can distinguish three explanations left open
by the arena:

1. Typed roles may be sufficient: `typed_no_candidate` and
   `typed_wrong_contract_no_candidate` rescue anchor failures without adding
   new violations.
2. Candidate visibility may be the culprit: hidden-candidate arms behave like
   no-candidate arms, while visible-candidate arms copy or regress.
3. One-shot labels may be too weak: extract-first arms outperform plain visible
   candidate arms, suggesting the protocol needs staging rather than more
   labels.

The falsification is also clean. If the no-candidate typed variants do not
rescue wrong-contract or forged-final anchor failures, the current typed-role
story weakens. If negative controls move as much as positives, the packet is
mostly prompt pressure rather than target-authority specificity.

## Caveats

- Setup artifact only; no model behavior result yet.
- Selected saved-field cases, not a population estimate.
- Hidden candidates can still naturally appear inside evidence text; what is
  hidden is the candidate-as-candidate field.
- Hidden and no-candidate duplicate prompts are intentional and should not be
  deduplicated during a model run.
- Exact-match span noise will still need a case audit after a real output run.

## Next Pressure

Run Qwen2.5-14B over the packet and score:

- rescue retention against `wrong_contract_public_task` and
  `forged_final_commitment` anchor failures;
- new typed-boundary Authority Violation Rate against
  `original_untyped_public`;
- visible candidate copy versus hidden candidate match;
- positive target-focus specificity versus negative controls.
