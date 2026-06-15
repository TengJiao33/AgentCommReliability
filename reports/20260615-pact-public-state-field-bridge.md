# PACT Public-State Field Bridge

## What We Tried

I stopped treating the MATH typed-public-state surface as the center of the
story and re-read the saved PACT HotpotQA offset50 focus cases as a
field-level public-state reliability problem.

The audit joins three existing artifacts:

- `case_atlas_focus_cases.jsonl`: 28 non-stable-right PACT focus cases.
- `public_state_gold_manual_labels.jsonl`: manual labels for the ten
  `final_public_state_contains_gold` cases.
- `target_slot_drift_cases.jsonl`: lexical target-slot drift diagnostics over
  final `Action Required` fields.

New artifacts:

- `scripts/audit_pact_public_state_field_bridge.py`
- `experiments/20260615-local-pact-public-state-field-bridge/summary.json`
- `experiments/20260615-local-pact-public-state-field-bridge/bridge_cases.jsonl`
- `experiments/20260615-local-pact-public-state-field-bridge/bridge_packet.md`

## What Happened

The 28 focus cases split into these bridge layers:

| Bridge layer | Count | Samples |
| --- | ---: | --- |
| `positive_contract_rescue` | 6 | `57`, `61`, `78`, `85`, `93`, `99` |
| `final_answer_commitment` | 12 | `50`, `54`, `55`, `62`, `64`, `66`, `74`, `83`, `87`, `89`, `92`, `97` |
| `target_contract` | 2 | `58`, `82` |
| `target_final_alignment` | 2 | `60`, `67` |
| `evidence_carriage` | 5 | `68`, `71`, `77`, `88`, `94` |
| `diagnostic_noise` | 1 | `59` |

The bridge-family view is sharper:

| Family | Count | Samples |
| --- | ---: | --- |
| `contract_rescued_verbose_surface` | 5 | `57`, `78`, `85`, `93`, `99` |
| `contract_rescued_content_or_field` | 1 | `61` |
| `missing_required_token_or_qualifier` | 3 | `50`, `55`, `83` |
| `over_specific_answer` | 3 | `87`, `89`, `92` |
| `wrong_answer_type_or_slot` | 2 | `60`, `67` |
| `strict_span_regression` | 2 | `64`, `66` |
| `strict_span_regression_with_soft_target_shift` | 1 | `54` |
| `target_migration_regression` | 1 | `58` |
| `target_under_specification_or_anchor_loss` | 1 | `82` |
| `recoverable_from_public_state_policy` | 1 | `62` |
| `near_miss_surface_or_span` | 1 | `97` |
| `alias_or_name_granularity` | 1 | `74` |
| `likely_evidence_or_reasoning_failure` | 5 | `68`, `71`, `77`, `88`, `94` |
| `false_positive_string_signal` | 1 | `59` |

The target-slot diagnostic still flags eight candidates:

`54`, `55`, `58`, `60`, `82`, `83`, `87`, `89`.

But the bridge audit keeps them in context. Only sample `58` is a clean
target-migration regression. Samples `60` and `67` are better read as
target/final-answer alignment failures. Several other target candidates are
really final-answer granularity failures or soft lexical warnings.

## Interpretation

This makes the larger object clearer:

**Field-level public-state reliability.**

The method question is not "typed public state" by itself. Typed state is just
one diagnostic surface. The real object is whether a multi-agent system can:

1. preserve the target contract in public state;
2. carry the necessary evidence without drifting into distractors;
3. commit the final answer to the requested slot and granularity.

That object connects the PACT split-evidence traces with the MATH peer-message
diagnostics. MATH shows that peer messages collapse final-answer authority,
relation skeletons, numeric/role slots, and source identity into one surface.
PACT shows that, even when the public state is already structured, failures
still happen at target, evidence, and final-commitment layers.

So the next step should not be another small typed/MATH variant. The useful
large move is a communication-necessity benchmark or intervention where these
three field layers are stressed directly.

## Caveats

- This is an offline re-read of one saved 50-sample PACT slice, not a new
  model result.
- Bridge labels combine mechanical atlas labels, ten manual labels, and a
  lexical target-slot diagnostic.
- The taxonomy is an inspection scaffold, not a population estimate.
- HotpotQA exact match still mixes genuine reasoning errors with answer-surface
  and granularity issues.

## Next Move

Build a split-evidence/public-state task packet around field preservation
rather than MATH answer revision:

- freeze or derive the original target contract from the question;
- expose or perturb `Action Required`, `Environment State`, `Action Result`,
  and `Final Answer` separately;
- score target preservation, evidence carriage, final-answer commitment, and
  final task accuracy.

That is the path with enough pressure to produce a real idea. It is larger
than another typed-public-state run and closer to the project's actual taste.
