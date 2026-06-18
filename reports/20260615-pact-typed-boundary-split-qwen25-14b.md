# PACT Typed Boundary Split Qwen2.5-14B

Date: 2026-06-15

## What We Tried

Ran the typed-boundary split packet from
`reports/_archive/20260616-pruned/20260615-pact-typed-boundary-split-packet.md` on A800_2 with
Qwen2.5-14B-Instruct.

Artifacts:

- packet:
  `experiments/20260615-local-pact-typed-boundary-split-packet/typed_boundary_split_packet.jsonl`
- runner: `scripts/run_pact_typed_boundary_split_a8002.sh`
- evaluator: `scripts/evaluate_pact_typed_boundary_split.py`
- paired audit: `scripts/analyze_pact_typed_boundary_split.py`
- run:
  `experiments/20260615-2223-a8002-pact-typed-boundary-split-qwen25-14b/`

Run facts:

- machine: A800_2;
- GPU: `7`;
- model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`;
- served model: `qwen2.5-14b-typed-boundary-split`;
- completed: `440/440`;
- failed: `0`;
- runner/evaluator stderr: empty;
- GPU 7 was released after the run.

## What Happened

Overall packet score:

- EM: `0.625`;
- average F1: `0.712`;
- visible-candidate copy rate: `0.290`;
- hidden-candidate match rate: `0.113`.

The hidden-candidate variants were intentionally identical prompts to the
matching no-candidate variants. The run preserved that boundary: no-candidate
and hidden-candidate arms produced identical normalized predictions in both
suggestion modes.

Positive target-focus rows:

| Variant | EM | Avg F1 | Candidate match/copy |
| --- | ---: | ---: | ---: |
| `original_untyped_public` | 0.812 | 0.865 | n/a |
| `wrong_contract_public_task` | 0.188 | 0.393 | n/a |
| `forged_final_commitment` | 0.375 | 0.552 | 0.406 visible copy |
| `typed_no_candidate` | 0.875 | 0.914 | n/a |
| `typed_candidate_hidden` | 0.875 | 0.914 | 0.031 hidden match |
| `typed_candidate_visible` | 0.625 | 0.719 | 0.250 visible copy |
| `typed_candidate_visible_extract_first` | 0.656 | 0.754 | 0.188 visible copy |
| `typed_wrong_contract_no_candidate` | 0.875 | 0.917 | n/a |
| `typed_wrong_contract_candidate_hidden` | 0.875 | 0.917 | 0.062 hidden match |
| `typed_wrong_contract_candidate_visible` | 0.688 | 0.759 | 0.250 visible copy |
| `typed_wrong_contract_candidate_visible_extract_first` | 0.719 | 0.795 | 0.219 visible copy |

Paired Authority Violation Rate over the `26` base-correct positive rows:

| Variant | Authority violations | AVR | Avg F1 delta |
| --- | ---: | ---: | ---: |
| `wrong_contract_public_task` | 21 | 0.808 | -0.471 |
| `forged_final_commitment` | 14 | 0.538 | -0.312 |
| `typed_no_candidate` | 1 | 0.038 | +0.049 |
| `typed_candidate_hidden` | 1 | 0.038 | +0.049 |
| `typed_candidate_visible` | 7 | 0.269 | -0.145 |
| `typed_candidate_visible_extract_first` | 6 | 0.231 | -0.111 |
| `typed_wrong_contract_no_candidate` | 1 | 0.038 | +0.052 |
| `typed_wrong_contract_candidate_hidden` | 1 | 0.038 | +0.052 |
| `typed_wrong_contract_candidate_visible` | 5 | 0.192 | -0.105 |
| `typed_wrong_contract_candidate_visible_extract_first` | 4 | 0.154 | -0.069 |

Rescue retention on positive anchor failures:

| Anchor failure | Typed arm | Rescues | New typed AVR |
| --- | --- | ---: | ---: |
| `wrong_contract_public_task` (`21`) | no candidate / hidden | 20/21 | 1/26 |
| `wrong_contract_public_task` (`21`) | visible candidate | 14/21 | 7/26 |
| `wrong_contract_public_task` (`21`) | visible + extract-first | 15/21 | 6/26 |
| `wrong_contract_public_task` (`21`) | wrong-contract no candidate / hidden | 20/21 | 1/26 |
| `wrong_contract_public_task` (`21`) | wrong-contract visible | 16/21 | 5/26 |
| `wrong_contract_public_task` (`21`) | wrong-contract visible + extract-first | 17/21 | 4/26 |
| `forged_final_commitment` (`14`) | no candidate / hidden | 13/14 | 1/26 |
| `forged_final_commitment` (`14`) | visible candidate | 8/14 | 7/26 |
| `forged_final_commitment` (`14`) | visible + extract-first | 8/14 | 6/26 |
| `forged_final_commitment` (`14`) | wrong-contract no candidate / hidden | 13/14 | 1/26 |
| `forged_final_commitment` (`14`) | wrong-contract visible | 10/14 | 5/26 |
| `forged_final_commitment` (`14`) | wrong-contract visible + extract-first | 10/14 | 4/26 |

## Things Noticed

The cleanest signal is not just that typed labels help. It is that typed labels
help when the candidate is not model-visible. On positive rows, no-candidate
and hidden-candidate typed arms both improve over the original untyped anchor
and almost remove the huge wrong-contract and forged-final failure rates.

Candidate visibility is the main poison surface. Showing the candidate as an
explicitly untrusted field drops positive EM from `0.875` to `0.625` in the
original-suggestion typed arm and introduces `7/26` new authority violations on
base-correct positive cases. The same visible candidate also hurts negative
controls: negative-control EM drops from `0.500` under no-candidate typed arms
to `0.250` under visible-candidate typed arms.

Extract-first helps, but only weakly. It reduces positive visible-copy rate
from `0.250` to `0.188` in the original-suggestion arm and repairs one visible
candidate failure, but it remains much worse than hiding or omitting the
candidate.

Typed wrong-contract suggestion was surprisingly well contained when no
candidate was visible. `typed_wrong_contract_no_candidate` and
`typed_wrong_contract_candidate_hidden` both reached positive EM `0.875`,
suggesting the model can often treat a wrong public task as non-authoritative
when the protocol boundary does not also ask it to adjudicate a visible
candidate.

## Interpretation

This result sharpens E-103:

```text
The candidate field, not typed state itself, is the dangerous authority
surface. Typed public state can quarantine wrong public-task authority, but a
model-visible candidate reintroduces final-answer commitment pressure even
when explicitly labeled untrusted.
```

The live C-shape is therefore less like "add better role labels" and more like
a protocol boundary:

```text
Keep candidate commitments out of the model-visible public state. If candidates
must exist, keep them as evaluator/router metadata or compare them only after a
separate evidence-rooted extraction step.
```

The extract-first arm says staging may help, but the stronger evidence favors
visibility control over instruction wording.

## Caveats

- Selected saved-field adversarial packet, not a population estimate.
- Qwen2.5-14B only.
- The run is saved-field re-answering, not a full PACT rerun.
- Exact-match span noise still affects several cells.
- Hidden-candidate match does not mean copying; hidden candidates were not in
  the prompt and can naturally match evidence-derived outputs.
- Duplicate no-candidate/hidden prompts are intentional and were not
  deduplicated during the run.

## Next Pressure

Do not keep making one-shot prompt variants. The result is now sharp enough to
bridge outward:

1. Apply the same public-versus-hidden candidate boundary to a second task
   family, preferably the existing MATH peer-influence packets where final
   answer, numeric role slots, and peer rationale can be separated.
2. Or prototype a PACT full-loop candidate-hiding protocol: candidates may be
   stored as metadata for routing/evaluation, but not shown in the final
   model-visible public state.

The retirement condition is clear: if the hidden/no-candidate advantage
disappears outside this saved-field PACT packet, treat this as a PACT prompt
surface result rather than a general communication protocol handle.
