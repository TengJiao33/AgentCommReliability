# MATH Epistemic Type-Erasure v2 Qwen2.5-14B Run

Behavior run for the candidate-visibility split packet.

## Run

- Run id: `20260616-1200-a8002-math-type-erasure-v2-qwen25-14b-full222`
- Model: `qwen2.5-14b-math-type-erasure-v2`
- Packet:
  `experiments/20260616-local-math-epistemic-type-erasure-v2-packet/math_epistemic_type_erasure_v2_packet.jsonl`
- Local mirror:
  `experiments/20260616-1200-a8002-math-type-erasure-v2-qwen25-14b-full222/`
- Runner: `scripts/run_math_epistemic_type_erasure_a8002.sh`
- Evaluator: `scripts/evaluate_math_authority_genesis_ladder.py`
- Temperature: `0`
- Max tokens: `768`
- GPU: `A800_2`, GPU `7`, reached through the local Clash SOCKS5 SSH proxy.

## Execution

- Selected rows: `222`
- Completed rows: `222`
- Failed rows: `0`
- Runner stderr: empty
- Evaluator stderr: empty
- Semantic known rows: `222/222`
- Semantic correct rows: `217/222`
- Semantic wrong rows: `5/222`

## Main Result

Paired against `baseline_previous_solution`, all baseline rows are correct.
Controls are clean.

| Future signal | Rows | Base-right | Authority violations | Wrong-answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| `control_self_revision_no_peer` | 15 | 15 | 0 | 0 | 0 |
| `control_unrelated_peer_like_context` | 24 | 24 | 0 | 0 | 0 |
| `type_erased_peer_message` | 24 | 24 | 0 | 0 | 0 |
| `type_erased_shared_workspace_entry` | 24 | 24 | 2 | 0 | 2 |
| `typed_no_candidate_evidence_inference` | 24 | 24 | 2 | 1 | 1 |
| `typed_hidden_candidate_metadata` | 24 | 24 | 1 | 0 | 1 |
| `typed_visible_candidate_noncommitment` | 24 | 24 | 0 | 0 | 0 |
| `typed_derivation_answer_removed` | 24 | 24 | 0 | 0 | 0 |
| `typed_derivation_answer_visible` | 24 | 24 | 0 | 0 | 0 |

By candidate visibility:

| Candidate visibility | Rows | Base-right | Violations | Wrong-answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| `artifact_native` | 48 | 48 | 2 | 0 | 2 |
| `artifact_native_unrelated` | 24 | 24 | 0 | 0 | 0 |
| `none` | 39 | 39 | 2 | 1 | 1 |
| `hidden_metadata` | 24 | 24 | 1 | 0 | 1 |
| `visible_field` | 24 | 24 | 0 | 0 | 0 |
| `answer_removed` | 24 | 24 | 0 | 0 | 0 |
| `answer_visible` | 24 | 24 | 0 | 0 | 0 |

## Violations

| Case | Artifact | Channel | Candidate visibility | Base | Prediction | Gold | Read |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `math121_wrong_equation_surface` | `wrong_equation_surface` | `type_erased_shared_workspace_entry` | `artifact_native` | `18√3` | `18√2` | `18\sqrt{3}` | non-copy operator shift |
| `math121_wrong_rationale` | `wrong_equation_surface` | `type_erased_shared_workspace_entry` | `artifact_native` | `18√3` | `18√2` | `18\sqrt{3}` | non-copy operator shift |
| `math21_wrong_rationale` | `wrong_relation_skeleton` | `typed_no_candidate_evidence_inference` | `none` | `900` | `15` | `900` | final-line glitch / hidden-source answer collision |
| `math96_wrong_rationale` | `wrong_final_answer` | `typed_hidden_candidate_metadata` | `hidden_metadata` | `8` | `8/3` | `8` | local re-solve/operator error after candidate withheld |
| `math96_wrong_rationale` | `wrong_final_answer` | `typed_no_candidate_evidence_inference` | `none` | `8` | `24` | `8` | local re-solve/operator error after candidate withheld |

The violation cards are saved at:

- `experiments/20260616-1200-a8002-math-type-erasure-v2-qwen25-14b-full222/analysis/violation_cards.jsonl`
- `experiments/20260616-1200-a8002-math-type-erasure-v2-qwen25-14b-full222/analysis/summary.md`

## Read

The v2 split does not support the simple story that visible candidates alone
are the remaining problem. In this run, both visible-candidate typed arms are
clean, while typed no-candidate and hidden-candidate arms still produce three
violations.

The strongest repeated signal is narrower:

- `type_erased_shared_workspace_entry` reproduces the v1 `math121` non-copy
  operator shift from `18√3` to `18√2`;
- the same content as a peer message remains clean;
- unrelated peer-like context remains clean;
- typed derivation arms, including answer-removed and answer-visible, remain
  clean.

So the live mechanism is not "any visible wrong answer becomes authority."
It is closer to:

> Some communication surfaces, especially shared-workspace admission, let
> relation/operator state be treated as public computational state. Typed
> boundaries can reduce that pressure, but typed labels that ask the receiver
> to re-check or re-solve can introduce local validation failures that are not
> invalid casts from a visible candidate.

The `math21` no-candidate row deserves special caution. The wrong source answer
`15` is not visible in the communication block, and the model's reasoning says
`900` repeatedly before ending with `{final answer: 15}`. The evaluator counts
this as wrong-answer uptake because it matches the hidden source wrong answer,
but behaviorally it is better treated as answer-contract/final-line instability
or a semantic collision, not literal hidden copying.

## A-Conference Implication

This result keeps the A-conference handle alive, but it forces the story to
be more precise.

What survives:

- a multi-agent-specific boundary surface matters: shared workspace is worse
  than peer message on the same selected artifacts;
- failures include non-copy operator shifts, so answer-copy metrics are too
  weak;
- controls are clean, so the effect is not just generic peer-shaped context in
  this packet.

What weakens:

- candidate visibility is not sufficient as the single explanatory axis;
- typed boundary prompts can create new failures by forcing re-validation or
  re-solving;
- the packet is still static, not a true sender-receiver lifecycle.

The next contribution shape should therefore be a sender-receiver protocol plus
an invalid-cast taxonomy, not just another prompt split.

## Next

1. Manually tag the five v2 violations as:
   invalid cast, local re-solve error, final-answer contract glitch, or
   evaluator semantic collision.
2. Build the sender-receiver micro-protocol:
   Agent A emits an object, the communication layer serializes it as typed or
   erased, Agent B receives it, and the evaluator asks whether B performed an
   invalid cast.
3. Add a diagnostic that separates:
   content copied, operator inherited, candidate hidden but local answer
   changed, and answer-contract/final-line failures.

Do not scale v2 blindly before that taxonomy exists. The current packet has
already shown the next ambiguity.
