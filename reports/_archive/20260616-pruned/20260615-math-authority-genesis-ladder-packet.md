# MATH Authority Genesis Ladder Packet

Date: 2026-06-15

Status: setup artifact / no new model behavior yet.

## What We Tried

Built a MATH-side pressure packet for the Authority Genesis handle. The packet
starts from the clean anonymous MATH200 peer-influence manual seed rows where a
wrong peer surface caused a right-to-wrong transition, then rebuilds the wrong
artifact under different inferred-future signals.

Artifacts:

- builder: `scripts/build_math_authority_genesis_ladder_packet.py`
- evaluator: `scripts/evaluate_math_authority_genesis_ladder.py`
- local packet:
  `experiments/20260615-local-math-authority-genesis-ladder-packet/`
- packet file:
  `experiments/20260615-local-math-authority-genesis-ladder-packet/math_authority_genesis_ladder_packet.jsonl`
- gold smoke:
  `experiments/20260615-local-math-authority-genesis-ladder-packet/gold-smoke/`

Inputs:

- `experiments/20260615-local-math200-peer-claim-hygiene/field_label_packet.jsonl`
- `experiments/20260615-local-math200-peer-claim-hygiene/manual_seed_labels.jsonl`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/source_cases.jsonl`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_audit.json`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_records.jsonl`

## Packet Shape

The packet contains:

- `20` source rows;
- `65` wrong-artifact instances;
- `670` prompt rows;
- `20` baseline previous-solution rows;
- `65` evaluator-hidden artifact rows;
- `585` model-visible artifact rows.

Source rows by original harmful condition:

| Condition | Rows |
| --- | ---: |
| `wrong_answer_only` | 1 |
| `wrong_equation_surface` | 3 |
| `wrong_rationale` | 9 |
| `wrong_redacted_rationale` | 4 |
| `wrong_typed_public_state` | 3 |

Artifact types:

| Artifact type | Prompt rows |
| --- | ---: |
| `wrong_final_answer` | 100 |
| `wrong_relation_skeleton` | 190 |
| `wrong_numeric_role_binding` | 190 |
| `wrong_equation_surface` | 170 |

Each artifact is placed under:

- hidden metadata;
- raw mention;
- answer-shaped or solution-shaped span;
- peer claim;
- majority/consensus;
- previous final answer or committed working answer;
- verifier-approved result;
- saved memory;
- active task requirement;
- final-answer commitment.

## Validation

Local checks passed:

- `python -m py_compile` passed for builder and evaluator;
- builder produced `670` rows with `670` unique `packet_id`s;
- hidden rows: `65`;
- visible rows: `585`;
- hidden rows with artifact markers such as `Artifact type:`,
  `Action Required:`, or `Verifier result:`: `0`;
- visible rows missing a `Communication Artifact:` section: `0`;
- gold-smoke semantic evaluation reached `670/670` known-correct rows with
  `0` semantic unknowns.

## Things Noticed

The packet is now a real cross-task pressure object rather than another PACT
wording tweak. It tests whether MATH relation skeletons, numeric-role bindings,
equation surfaces, and final-answer strings become more behavior-shaping as
they are made to look like peer claims, memory, verifier output, task
requirements, or final commitments.

The first build surfaced a redaction friction point: some peer excerpts are
stored as one compact line, so dropping any line containing `Final answer from
this peer:` can delete the whole rationale. The builder now removes only the
final-answer phrase/span and keeps the preceding rationale text.

## Caveats

- This is setup only; no model has been run on the packet.
- Source rows come from manual seed labels, not a population sample.
- Relation, numeric-role, and equation artifacts are heuristic decompositions
  of saved peer surfaces.
- Artifact types overlap because MATH solutions naturally mix equations,
  role bindings, and relation skeletons.
- The baseline is a second-pass previous-solution prompt, not the original
  no-peer prompt exactly.
- The evaluator marks non-copy authority failures as
  `operator_uptake_candidate`; those require manual audit after a model run.

## Next Pressure

The next useful step is a small Qwen run over this packet, then a mechanism
audit that separates:

- exact wrong-answer uptake;
- relation-skeleton uptake;
- numeric-role uptake;
- equation-surface uptake;
- authority violations without final-answer copying.

If MATH movement is only exact wrong-answer copying, Authority Genesis should
shrink toward candidate attraction. If hidden-final relation or numeric-role
artifacts move behavior under stronger future signals, the handle becomes a
stronger cross-task story candidate.
