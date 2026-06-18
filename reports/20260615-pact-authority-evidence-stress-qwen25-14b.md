# PACT Authority/Evidence Stress Qwen2.5-14B

Date: 2026-06-15

## What We Tried

Built and ran an authority/evidence disentanglement packet after the external
pressure audit suggested that the live handle was not a generic
answer-contract verifier, but a public-state authority boundary.

Setup artifacts:

- builder: `scripts/build_pact_authority_evidence_stress_packet.py`
- evaluator: `scripts/evaluate_pact_authority_evidence_stress_packet.py`
- A800_2 runner: `scripts/run_pact_authority_evidence_stress_a8002.sh`
- local packet:
  `experiments/_archive/20260616-pruned/20260615-local-pact-authority-evidence-stress-packet/`
- model run:
  `experiments/20260615-2040-a8002-pact-authority-evidence-stress-qwen25-14b/`

The packet has `40` source cases and `200` prompt rows:

- `32` positive target-focus cases from offset100/offset150 focus cards;
- `8` negative-control seed cases;
- `5` variants per case.

The variants test:

- original question trusted, original public fields;
- original question trusted, injected over-authoritative `Action Required`;
- delegated `Action Required` as active task;
- frozen question-derived target;
- final-answer candidate lure.

## What Happened

The run completed cleanly on A800_2 GPU `7` with Qwen2.5-14B-Instruct:

- completed requests: `200/200`;
- evaluation rows: `200`;
- overall EM: `0.570`;
- overall avg F1: `0.679`;
- GPU 7 was released after the run.

Positive target-focus rows:

| Variant | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `trusted_root_original_public` | 32 | 0.812 | 0.865 |
| `trusted_root_injected_action_required` | 32 | 0.594 | 0.695 |
| `delegated_action_required_authority` | 32 | 0.344 | 0.525 |
| `frozen_question_target` | 32 | 0.844 | 0.911 |
| `final_candidate_lure` | 32 | 0.469 | 0.633 |

Bridge-layer view:

| Layer | Original EM | Injected EM | Frozen EM | Delegated EM |
| --- | ---: | ---: | ---: | ---: |
| `target_authority` | 1.000 | 0.727 | 0.909 | 0.364 |
| `target_contract` | 0.400 | 0.300 | 0.700 | 0.300 |
| `stable_answer` controls | 1.000 | 1.000 | 1.000 | 1.000 |
| `evidence_or_content` controls | 0.000 | 0.000 | 0.000 | 0.000 |

Paired deltas versus original trusted-root public state on positive focus cases:

| Variant | Outcomes | Avg F1 delta |
| --- | --- | ---: |
| `trusted_root_injected_action_required` | `7` regressions, `19` stable-right, `6` stable-wrong | -0.169 |
| `delegated_action_required_authority` | `15` regressions, `11` stable-right, `6` stable-wrong | -0.339 |
| `frozen_question_target` | `5` rescues, `4` regressions, `22` stable-right, `1` stable-wrong | +0.046 |
| `final_candidate_lure` | `11` regressions, `15` stable-right, `6` stable-wrong | -0.231 |

## Things Noticed

The packet bit into the intended mechanism. Injecting delegated authority into
`Action Required` caused regressions even though the prompt still declared the
original question as the trusted root. Making the delegated public task the
active task hurt more, which is the expected positive-control behavior.

Frozen question-root projection was the strongest tested condition on positive
focus cases. It was especially helpful on `target_contract` cases, where EM
moved from `0.400` under original public state to `0.700` under frozen target.

The movement is not only aggregate EM noise. Stable controls stayed stable
across the authority variants, while evidence/content controls stayed wrong
across variants, as expected.

The strongest boundary remains question-root ambiguity. The small
`question_root_boundary_regression` family still shows that frozen target is not
automatically safe when evidence is underspecified or the root itself reopens
ambiguity.

## Interpretation

This upgrades the field-authority handle from a saved-field observation to a
more falsifiable pressure object.

The current best face is:

```text
Public state fields can carry evidence and delegated task authority at the same
time. Downstream reliability depends on whether the model follows the trusted
question root or lets public-field authority rewrite the answer contract.
```

This is still not a complete method story. But it is a stronger mechanism
candidate than another answer-contract verifier prompt, because the controlled
perturbation changes behavior in the predicted direction.

## Caveats

- Selected `40` source cases, not a population estimate.
- Positive cases are target-layer focus cards, so the packet is intentionally
  enriched for authority sensitivity.
- `Action Required` perturbations are synthetic and adversarial.
- The run is saved-field re-answering, not a full PACT rerun.
- Strict-span and evidence/content failures remain outside the authority story.
- Qwen2.5-14B is not PACT's original reported Qwen3-14B setting.

## Next Pressure

Do not immediately scale this packet as a leaderboard.

The useful next checks are:

1. Inspect the `7` injected-authority regressions and `5` frozen-target rescues
   by hand to label whether they are real authority failures or span/evidence
   artifacts.
2. Add a slightly larger negative-control slice before claiming specificity.
3. If manual inspection holds, build the same authority/evidence perturbation
   on a task where public state is necessary, such as HiddenBench-style
   distributed information or another split-evidence QA task.
