# MATH Epistemic Type-Erasure v2 Packet

Setup packet for the candidate-visibility split proposed in the A-conference
story synthesis.

## Why This Exists

The v1 MATH type-erasure run found a small but specific signal:

- erased shared-workspace entries caused `2/48` authority violations, both
  non-copy equation/operator shifts;
- typed channels caused `1/120` authority violation, but it was exact
  wrong-answer uptake.

That leaves a central confound: did type preservation fail, or did the typed
channel still expose a candidate answer that Agent B could cast into a stronger
object?

v2 keeps the same selected MATH artifacts and evaluator contract, but splits
typed communication by candidate-answer visibility.

## Built Artifacts

- Builder:
  `scripts/build_math_epistemic_type_erasure_v2_packet.py`
- Packet directory:
  `experiments/20260616-local-math-epistemic-type-erasure-v2-packet/`
- Packet:
  `experiments/20260616-local-math-epistemic-type-erasure-v2-packet/math_epistemic_type_erasure_v2_packet.jsonl`
- Source artifact manifest:
  `experiments/20260616-local-math-epistemic-type-erasure-v2-packet/source_artifacts.jsonl`
- Gold-smoke evaluation:
  `experiments/20260616-local-math-epistemic-type-erasure-v2-packet/gold-smoke/`

## Packet Shape

- Source rows represented: `15`
- Selected artifacts: `24`
- Prompt rows: `222`
- Rows by condition:
  - baseline: `15`
  - control: `39`
  - erased: `48`
  - typed: `120`
- Selected artifacts by type:
  - `wrong_equation_surface`: `10`
  - `wrong_final_answer`: `6`
  - `wrong_numeric_role_binding`: `4`
  - `wrong_relation_skeleton`: `4`
- Prior ladder-violation-linked artifacts: `13`
- Prior operator-candidate-linked artifacts: `8`

## Candidate-Visibility Arms

| Future signal | Rows | Candidate visibility |
| --- | ---: | --- |
| `type_erased_peer_message` | 24 | artifact-native |
| `type_erased_shared_workspace_entry` | 24 | artifact-native |
| `typed_no_candidate_evidence_inference` | 24 | no candidate field |
| `typed_hidden_candidate_metadata` | 24 | candidate exists only in hidden metadata |
| `typed_visible_candidate_noncommitment` | 24 | visible candidate field, non-committed |
| `typed_derivation_answer_removed` | 24 | answer/candidate removed |
| `typed_derivation_answer_visible` | 24 | visible candidate inside typed derivation |
| `control_unrelated_peer_like_context` | 24 | unrelated artifact-native peer-like text |

The hidden/no-candidate arms are deliberately not allowed to show the wrong
candidate answer in the communication block.

## Validation

Commands run:

```bash
python -m py_compile scripts/build_math_epistemic_type_erasure_v2_packet.py scripts/evaluate_math_authority_genesis_ladder.py
python scripts/build_math_epistemic_type_erasure_v2_packet.py
python scripts/evaluate_math_authority_genesis_ladder.py \
  --packet experiments/20260616-local-math-epistemic-type-erasure-v2-packet/math_epistemic_type_erasure_v2_packet.jsonl \
  --prediction-source gold \
  --out-dir experiments/20260616-local-math-epistemic-type-erasure-v2-packet/gold-smoke
```

Checks:

- packet rows: `222`
- unique `packet_id`: yes
- hidden/no-candidate communication leakage:
  - `typed_no_candidate_evidence_inference`: `0/24`
  - `typed_hidden_candidate_metadata`: `0/24`
  - `typed_derivation_answer_removed`: `0/24`
- visible-candidate typed arms expose candidate as intended:
  - `typed_visible_candidate_noncommitment`: `24/24`
  - `typed_derivation_answer_visible`: `24/24`
- gold-smoke semantic accuracy: `222/222`

## Interpretation Before Model Run

This is not behavioral evidence yet. It is a cleaner pressure object.

The packet directly tests the v1 ambiguity:

- if erased shared-workspace rows fail while hidden/no-candidate typed rows stay
  clean, the boundary type-erasure story gains support;
- if visible-candidate typed rows fail while hidden/no-candidate rows stay
  clean, the remaining v1 failure is mostly candidate visibility;
- if answer-removed derivations still fail, then the failure is not answer
  copying but operator/relation inheritance;
- if unrelated peer-like context fails, the story weakens toward generic
  context susceptibility rather than multi-agent communication boundaries.

## Next

Run v2 on A800_2 with the existing type-erasure runner by overriding `PACKET`.
If v2 separates the hidden/no-candidate and visible-candidate arms, the next
escalation should be the true sender-receiver micro-protocol: Agent A emits an
object, the communication layer serializes it under typed/erased policies, and
Agent B receives it as a boundary object rather than as a hand-built packet.
