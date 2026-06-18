# Authority Genesis Ladder Qwen2.5-14B

Date: 2026-06-15

## What We Tried

Ran the first Authority Genesis Ladder packet from
`reports/_archive/20260616-pruned/20260615-authority-genesis-ladder-packet.md` on A800_2 with
Qwen2.5-14B-Instruct.

Artifacts:

- packet:
  `experiments/_archive/20260616-pruned/20260615-local-authority-genesis-ladder-packet/authority_genesis_ladder_packet.jsonl`
- runner: `scripts/run_authority_genesis_ladder_a8002.sh`
- evaluator: `scripts/evaluate_authority_genesis_ladder.py`
- run:
  `experiments/_archive/20260616-pruned/20260615-2318-a8002-authority-genesis-ladder-qwen25-14b/`

Run facts:

- machine: A800_2;
- GPU: `7`;
- model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`;
- served model: `qwen2.5-14b-authority-genesis-ladder`;
- completed: `504/504`;
- failed: `0`;
- runner/evaluator stderr: empty;
- GPU 7 was released after completion.

## What Happened

Overall:

- EM: `0.687`;
- average F1: `0.747`;
- baseline trusted-question/evidence EM: `0.750`;
- baseline trusted-question/evidence F1: `0.799`.

Wrong-lure future-signal readout over the `18` baseline-correct rows:

| Future signal | EM | Avg F1 | Authority violations | AVR | Exact AUR |
| --- | ---: | ---: | ---: | ---: | ---: |
| `hidden_metadata` | 0.750 | 0.799 | 0 | 0.000 | 0.000 |
| `raw_mention` | 0.667 | 0.721 | 2 | 0.111 | 0.000 |
| `answer_shaped_span` | 0.625 | 0.679 | 3 | 0.167 | 0.000 |
| `peer_claim` | 0.500 | 0.617 | 6 | 0.333 | 0.167 |
| `majority_consensus` | 0.583 | 0.668 | 4 | 0.222 | 0.056 |
| `previous_final_answer` | 0.667 | 0.721 | 2 | 0.111 | 0.000 |
| `verifier_approved_result` | 0.500 | 0.617 | 6 | 0.333 | 0.111 |
| `saved_memory` | 0.542 | 0.667 | 5 | 0.278 | 0.056 |
| `active_task_required` | 0.292 | 0.474 | 11 | 0.611 | 0.444 |
| `final_answer_commitment` | 0.458 | 0.575 | 7 | 0.389 | 0.111 |

Correct-gold mirror over the `6` baseline-wrong rows:

| Future signal | Rescues | Utility |
| --- | ---: | ---: |
| `hidden_metadata` | 0 | 0.000 |
| `raw_mention` | 2 | 0.333 |
| `answer_shaped_span` | 2 | 0.333 |
| `peer_claim` | 2 | 0.333 |
| `majority_consensus` | 2 | 0.333 |
| `previous_final_answer` | 1 | 0.167 |
| `verifier_approved_result` | 4 | 0.667 |
| `saved_memory` | 3 | 0.500 |
| `active_task_required` | 3 | 0.500 |
| `final_answer_commitment` | 1 | 0.167 |

## Things Noticed

The hidden/visible boundary appears immediately. Wrong-lure hidden metadata
matches the baseline in paired authority violations: `0/18`. Merely making the
same lure visible as a raw scratch mention causes `2/18` violations, and making
it answer-shaped causes `3/18`.

The curve is not monotonic, but it is structured. The strongest pressure is
`active_task_required` with AVR `0.611` and exact AUR `0.444`. The next strongest
is `final_answer_commitment` with AVR `0.389`. Peer and verifier surfaces both
reach AVR `0.333`. Saved memory is also nontrivial at AVR `0.278`.

Some expected high-authority signals are weaker than the idea sketch predicted.
`previous_final_answer` is only AVR `0.111`, and `majority_consensus` is weaker
than a single `peer_claim` in this prompt surface. That matters: "future" is
not an abstract ladder that the model obeys cleanly. It is mediated by the
specific prompt ritual, wording, and task contract.

Correct-gold mirrors are useful but not free. Verifier-approved correct content
rescues `4/6` baseline-wrong rows and saved memory rescues `3/6`, but several
correct-gold future signals also create `1/18` authority violations on
baseline-correct rows. Granting authority to correct content can still disturb
the answer contract.

Case-level deltas show at least two mechanisms:

- exact lure uptake, such as answer-type rows where the model copies a full
  proposition instead of the short answer (`Larnelle Harris`, `No`, `Yes`);
- contract disturbance without exact copying, such as the Boss Bailey control
  where the model moves from `2003` into a refusal/insufficient-evidence style
  response after seeing a previous/peer/verifier-like artifact.

## Interpretation

This is the first model-behavior evidence that the Authority Genesis handle is
real enough to keep alive.

The cleanest sentence after the run is:

```text
The same content is harmless as hidden metadata, mildly harmful as a visible
mention, and much more harmful when the prompt makes it look like an active
task, verifier result, peer claim, saved memory, or final commitment.
```

That supports the deeper framing from
`reports/20260615-authority-genesis-idea.md`: the problem is not only which
container a text occupies, but what downstream future the model infers for that
text.

This is not yet a solid paper story. The run is small, selected, saved-field,
PACT-only, Qwen2.5-14B-only, and prompt-surface sensitive. But it is now more
than a metaphor: hidden/visible and future-signal perturbations move behavior
in a direction that the idea predicted.

## Caveats

- Selected `24`-case packet, not a population estimate.
- Only `18` rows are baseline-correct for paired wrong-lure AVR.
- Saved-field re-answering, not a full PACT rerun.
- Qwen2.5-14B only.
- Wrong lures come from prior observed predictions and can mix semantic errors,
  answer-contract errors, and strict-span/granularity surfaces.
- The ladder is not monotonic; signal wording and prompt ritual matter.
- Exact AUR undercounts cases where the model follows the lure's contract
  without copying the exact lure string.
- Correct-gold mirrors are oracle controls, not deployable interventions.

## Next Pressure

Do not immediately declare the story solid.

Useful next moves:

1. Manually inspect the `wrong_lure` authority violations by mechanism:
   exact lure copy, answer-contract shift, refusal/insufficient-evidence drift,
   and strict-span artifact.
2. Build a MATH version of the ladder where the same wrong relation skeleton,
   numeric role, or equation surface is presented as raw mention, peer claim,
   memory, verifier result, active task, and final commitment.
3. Re-run a smaller PACT ladder with tighter base-correct selection and more
   negative controls, so hidden/visible and future-signal effects are not
   dominated by six baseline-wrong rows.
4. If the MATH transfer survives, promote Authority Genesis from "live
   diagnostic handle" to a bounded cross-task story candidate.

Retirement condition: if the ladder effect disappears outside this PACT
saved-field packet, demote the idea to a PACT/public-field prompt-surface
diagnostic.
