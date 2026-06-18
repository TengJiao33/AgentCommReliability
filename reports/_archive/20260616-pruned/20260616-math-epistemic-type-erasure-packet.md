# MATH Epistemic Type-Erasure Packet

Status: local setup artifact plus gold-smoke verification. This is not a model
behavior result yet.

## Why This Step

The previous MATH Authority Genesis ladder showed that visible peer artifacts
can turn a correct second pass into a wrong answer, but the mechanism was still
too easy to read as "LLM influenced by authoritative-looking text."

This packet keeps the same MATH peer artifacts and asks a sharper multi-agent
question: when Agent A sends an intermediate artifact to Agent B, does the
boundary erase its epistemic type? The intervention is no longer "make the text
sound more authoritative." It is:

- type-erased channel: the artifact enters as flat peer/shared-context text;
- type-preserved channel: the same content carries type, provenance,
  confidence, and commitment fields;
- controls: self-revision with no peer content, and unrelated peer-like context
  from another MATH problem.

## Artifacts

- Builder: `scripts/build_math_epistemic_type_erasure_packet.py`
- A8002 runner: `scripts/run_math_epistemic_type_erasure_a8002.sh`
- Packet directory:
  `experiments/_archive/20260616-pruned/20260616-local-math-epistemic-type-erasure-packet/`
- Packet:
  `experiments/_archive/20260616-pruned/20260616-local-math-epistemic-type-erasure-packet/math_epistemic_type_erasure_packet.jsonl`
- Source-artifact manifest:
  `experiments/_archive/20260616-pruned/20260616-local-math-epistemic-type-erasure-packet/source_artifacts.jsonl`
- Gold-smoke:
  `experiments/_archive/20260616-pruned/20260616-local-math-epistemic-type-erasure-packet/gold-smoke/`

## Packet Shape

The packet represents `15` source rows and `24` selected artifacts, producing
`222` prompt rows.

Selection is deliberately deconcentrated: the previous mechanism audit was
dominated by `math121` and `math159`, so this packet caps each MATH case at
`2` selected artifacts.

Selected artifacts by type:

| Artifact type | Count |
| --- | ---: |
| `wrong_equation_surface` | 10 |
| `wrong_final_answer` | 6 |
| `wrong_numeric_role_binding` | 4 |
| `wrong_relation_skeleton` | 4 |

Rows by channel condition:

| Channel condition | Rows |
| --- | ---: |
| `baseline` | 15 |
| `control` | 39 |
| `erased` | 48 |
| `preserved` | 120 |

Prior-linkage to the MATH Authority Genesis ladder:

- `13/24` selected artifacts had prior ladder violation cards;
- `8/24` had prior operator-uptake candidate cards.

## Channel Contrast

| Level | Channel | Family |
| ---: | --- | --- |
| -2 | `control_self_revision_no_peer` | control |
| -1 | `control_unrelated_peer_like_context` | control |
| 0 | `type_erased_peer_message` | erased |
| 1 | `type_erased_shared_workspace_entry` | erased |
| 10 | `type_preserved_evidence_inference_split` | preserved |
| 11 | `type_preserved_hypothesis_low_confidence` | preserved |
| 12 | `type_preserved_partial_derivation_check_required` | preserved |
| 13 | `type_preserved_candidate_noncommitment` | preserved |
| 14 | `type_preserved_provenance_missing_context` | preserved |

The preserved channels are not intended as a generic safety prompt. They are a
typed boundary representation: Agent B receives the same content but is told
what type of object it is allowed to treat the content as.

## Verification

Local checks passed:

```powershell
python -m py_compile .\scripts\build_math_epistemic_type_erasure_packet.py .\scripts\evaluate_math_authority_genesis_ladder.py
bash -n scripts/run_math_epistemic_type_erasure_a8002.sh
python .\scripts\build_math_epistemic_type_erasure_packet.py
python .\scripts\evaluate_math_authority_genesis_ladder.py --packet .\experiments\_archive\20260616-pruned\20260616-local-math-epistemic-type-erasure-packet\math_epistemic_type_erasure_packet.jsonl --prediction-source gold --out-dir .\experiments\_archive\20260616-pruned\20260616-local-math-epistemic-type-erasure-packet\gold-smoke
```

Gold-smoke result:

- `222/222` rows semantically correct under `--prediction-source gold`;
- `222/222` unique `packet_id`;
- no duplicate variants within a case.

## Next Run

On A8002, run:

```bash
bash scripts/run_math_epistemic_type_erasure_a8002.sh
```

The key behavior readout is not raw accuracy. It is whether the same artifact
causes more paired baseline-to-wrong transitions when type-erased than when
type-preserved, especially for equation, numeric-role, and relation-skeleton
artifacts that previously looked like operator uptake rather than answer copy.

## Current Caveat

This is still a prompt-level simulation of a communication boundary. It is more
multi-agent-specific than the authority ladder because it manipulates the type
metadata lost at the sender-receiver boundary, but a later stronger version
should use actual sender/receiver turns rather than only serialized artifacts.
