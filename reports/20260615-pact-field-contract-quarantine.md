# PACT Field-Contract Quarantine

## What We Tried

After the public-state field pressure run, I built a first deterministic
field-contract verifier and used it to generate a gated PACT packet.

New scripts:

- `scripts/build_pact_field_contract_verifier_packet.py`
- `scripts/analyze_pact_field_contract_quarantine_results.py`

Local verifier artifacts:

- `experiments/20260615-local-pact-field-contract-verifier/summary.json`
- `experiments/20260615-local-pact-field-contract-verifier/summary.md`
- `experiments/20260615-local-pact-field-contract-verifier/verifier_records.jsonl`
- `experiments/20260615-local-pact-field-contract-verifier/verified_packet.jsonl`
- `experiments/20260615-local-pact-field-contract-verifier/verified_quarantine_packet.jsonl`

Model run:

- `experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/outputs.jsonl`
- `experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/evaluation/summary.json`
- `experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/evaluation/summary.md`
- `experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/quarantine_delta_audit/quarantine_delta_summary.json`
- `experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/quarantine_delta_audit/quarantine_delta_summary.md`

## The Failed First Verifier

The first verifier tried to keep good public targets, freeze risky targets, and
show final-answer candidates when they looked licensed by evidence.

That was not good enough.

Offline routing over the already-run five-condition pressure outputs:

| Strategy | EM | Avg F1 |
| --- | ---: | ---: |
| `always_hide_public_target` | `0.590` | `0.725` |
| `always_freeze_question_target` | `0.580` | `0.734` |
| `verifier_freeze_risky_else_base` | `0.540` | `0.685` |
| `verifier_hide_risky_else_base` | `0.570` | `0.710` |
| `verifier_licensed_final_else_hide` | `0.550` | `0.689` |

So the first lesson is deletion:

**Do not continue the final-answer-candidate licensing route for now.**

The surface-level candidate verifier showed `91/100` candidates, and the
candidate-routed strategies underperformed. Candidate visibility is still too
much of an attractor.

## The Stronger Move

The useful route was more severe:

**Quarantine the public target.**

Policy:

- if the public target is risky, hide `Action Required`;
- otherwise replace `Action Required` with a question-derived frozen contract;
- never expose the original public target;
- never expose the final-answer candidate.

The offline route for this policy was:

| Strategy | EM | Avg F1 | Chosen conditions |
| --- | ---: | ---: | --- |
| `verifier_hide_risky_else_freeze` | `0.610` | `0.759` | hide target `33`, freeze target `67` |

I then generated a real 100-row packet:

- `50` HotpotQA offset50 samples;
- `2` source runs: baseline and final-contract;
- one condition: `verified_quarantine_risky_else_frozen_no_final`.

## Model Result

The A800_2 Qwen2.5-14B run completed all `100/100` rows with `0` failures.

| Condition | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `verified_quarantine_risky_else_frozen_no_final` | `100` | `0.610` | `0.753` |

By source run:

| Source run | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `baseline` | `50` | `0.600` | `0.728` |
| `final_contract` | `50` | `0.620` | `0.778` |

This is the best behavioral condition so far on this packet:

| Prior condition | EM | Avg F1 |
| --- | ---: | ---: |
| `question_plus_evidence_no_target_no_final` | `0.590` | `0.725` |
| `frozen_target_plus_evidence_no_final` | `0.580` | `0.734` |
| `question_plus_public_state_with_final` | `0.550` | `0.710` |
| `question_plus_public_state_no_final` | `0.520` | `0.688` |
| `public_target_plus_evidence_no_question_no_final` | `0.440` | `0.591` |

## Paired Deltas

Against the original public-state/no-final base:

| Comparison | Rescues | Regressions | Both right | Both wrong |
| --- | ---: | ---: | ---: | ---: |
| quarantine vs base public state | `12` | `3` | `49` | `36` |

Against the strongest fixed prior controls:

| Comparison | Rescues | Regressions | Both right | Both wrong |
| --- | ---: | ---: | ---: | ---: |
| quarantine vs hide public target | `5` | `3` | `56` | `36` |
| quarantine vs freeze question target | `5` | `2` | `56` | `37` |

The useful cases are not just formatting:

- sample `55`: `1961` -> `Marion, South Australia`;
- sample `67`: `"Yeah!"` -> `Usher`;
- sample `71`: `276,170` -> `276,170 inhabitants`;
- sample `85`: `1949` -> `April 1, 1949`;
- sample `87`: over-specific island answers -> `Canary Islands, Spain`;
- sample `99`: verbose administrative comparison -> `No`.

There are still real regressions:

- sample `57`: `Keith Bostic` -> `Keith Bostic is younger than Jerry Glanville`;
- sample `60`: answer-type expansion to a sentence about Muggsy Bogues;
- sample `75`: `John John Florence` -> `John Florence`;
- sample `95`: `Fairfax County` -> `Fairfax County, Virginia`.

These regressions say the next verifier needs a final-span/granularity check,
not a final-answer-candidate field.

## Bridge-Layer Reading

| Bridge layer | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `stable_right_or_not_focus` | `44` | `0.932` | `0.986` |
| `positive_contract_rescue` | `12` | `0.583` | `0.699` |
| `target_final_alignment` | `4` | `0.500` | `0.744` |
| `final_answer_commitment` | `24` | `0.333` | `0.731` |
| `target_contract` | `4` | `0.250` | `0.250` |
| `evidence_carriage` | `10` | `0.200` | `0.200` |
| `diagnostic_noise` | `2` | `0.000` | `0.000` |

Target-drift candidate rows improved but remain hard:

| Target-drift candidate | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `False` | `84` | `0.643` | `0.767` |
| `True` | `16` | `0.438` | `0.682` |

## Interpretation

This is the first intervention-shaped result for the field-level story.

The result does not say "structured public state helps." It says something more
specific:

**A public target field should be treated as untrusted unless it is grounded
back into the original question.**

The strongest current behavior comes from refusing to expose the original
public target at all:

- risky public target: hide it;
- non-risky public target: replace it with a frozen question-derived contract.

That is a sharper idea than typed public state. It also connects cleanly to the
earlier MATH peer-message diagnostics: the harmful unit is not just a wrong
answer, but an unverified field that carries target/role/slot authority.

## What This Deletes

- Delete the naive "keep good public target" route for now.
- Delete final-answer-candidate licensing as a near-term intervention.
- Do not present public-state structure as inherently reliable.
- Do not scale another public-state run without target quarantine or a stronger
  final-span verifier.

## Caveats

- One model, one HotpotQA offset50 slice, `100` re-answering rows.
- The target-risk detector uses lexical overlap, generic target patterns, and
  the existing target-slot diagnostic; it is not yet a fully standalone runtime
  verifier.
- The run tests saved PACT fields, not a full multi-agent rerun.
- HotpotQA exact match still penalizes granularity, aliases, and verbose
  correct statements.
- Offline route selection and actual gated prompting happen on the same slice,
  so this is a live handle, not a general method claim.

## Next Move

Make the verifier standalone:

1. remove dependence on the existing paired target-slot diagnostic;
2. add a final-span/granularity verifier for outputs like `John Florence`,
   `Fairfax County, Virginia`, and full-sentence answers;
3. run the same quarantine policy on a neighboring HotpotQA slice.

If it survives that, the project has a real protocol candidate:

**field-contract quarantine for public-state communication.**
