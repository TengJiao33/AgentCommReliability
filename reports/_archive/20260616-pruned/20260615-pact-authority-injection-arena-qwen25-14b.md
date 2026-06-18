# PACT Authority Injection Arena Qwen2.5-14B

Date: 2026-06-15

## What We Tried

Turned the previous authority/evidence stress packet into a more aggressive
public-state authority arena.

Setup artifacts:

- builder: `scripts/build_pact_authority_injection_arena_packet.py`
- evaluator: `scripts/evaluate_pact_authority_injection_arena.py`
- A800_2 runner: `scripts/run_pact_authority_injection_arena_a8002.sh`
- local packet:
  `experiments/_archive/20260616-pruned/20260615-local-pact-authority-injection-arena-packet/`
- model run:
  `experiments/_archive/20260616-pruned/20260615-2130-a8002-pact-authority-injection-arena-qwen25-14b/`

The packet has `40` source cases and `280` prompt rows:

- `32` positive target-focus cases;
- `8` negative-control cases;
- `7` variants per case.

The variants are:

- `original_untyped_public`;
- `evidence_only_neutral`;
- `neutral_summary_public_state`;
- `imperative_public_task`;
- `wrong_contract_public_task`;
- `forged_final_commitment`;
- `typed_state_quarantine`.

The main diagnostic is Authority Violation Rate (AVR): among cases where
`original_untyped_public` is correct, how often a pressure variant becomes
wrong.

## What Happened

The run completed cleanly on A800_2 GPU `7` with Qwen2.5-14B-Instruct:

- completed requests: `280/280`;
- failed requests: `0`;
- overall EM: `0.561`;
- overall avg F1: `0.667`;
- GPU 7 was released after the run.

Positive target-focus rows:

| Variant | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `original_untyped_public` | 32 | 0.812 | 0.865 |
| `evidence_only_neutral` | 32 | 0.781 | 0.829 |
| `neutral_summary_public_state` | 32 | 0.688 | 0.786 |
| `imperative_public_task` | 32 | 0.750 | 0.818 |
| `wrong_contract_public_task` | 32 | 0.188 | 0.393 |
| `forged_final_commitment` | 32 | 0.375 | 0.552 |
| `typed_state_quarantine` | 32 | 0.625 | 0.782 |

Paired deltas over positive target-focus rows, using the `26` base-correct
cases as the AVR denominator:

| Variant | Authority violations | AVR | Avg F1 delta |
| --- | ---: | ---: | ---: |
| `evidence_only_neutral` | 5 | 0.192 | -0.036 |
| `neutral_summary_public_state` | 5 | 0.192 | -0.079 |
| `imperative_public_task` | 3 | 0.115 | -0.047 |
| `wrong_contract_public_task` | 21 | 0.808 | -0.471 |
| `forged_final_commitment` | 14 | 0.538 | -0.312 |
| `typed_state_quarantine` | 6 | 0.231 | -0.082 |

Typed quarantine rescued many pressure failures but was not safe by itself:

- `15/21` wrong-contract positive violations had typed-quarantine correct
  (`0.714`);
- `8/14` forged-final positive violations had typed-quarantine correct
  (`0.571`);
- `2/3` imperative-task positive violations had typed-quarantine correct
  (`0.667`);
- but typed quarantine itself caused `6/26` authority violations on
  base-correct positive cases.

## Things Noticed

The arena bit much harder than the previous injected-action variant. Plain
imperative wording was only mildly harmful, but wrong answer-contract wording
was highly destructive: on target-authority rows, `wrong_contract_public_task`
caused `18/22` base-correct cases to become wrong. On answer-type projection
rows, the same variant caused `11/11` base-correct cases to become wrong.

Forged final commitments are also a strong authority surface. On positive
target-focus cases, the model copied the visible candidate in `13/32` cases and
AVR reached `0.538`.

The surprising negative result is typed state. Role labels can help: they often
turn full propositions back into short spans such as `Picric acid`, `No`,
`Owsley Stanley`, `Roberta Vinci`, and `The Beatles`. But adding an explicit
`Untrusted Candidate` field creates its own attraction surface. Typed
quarantine copied candidates in `7/32` positive cases and in `4/8` negative
controls.

## Interpretation

This strengthens the more aggressive framing:

```text
Public state is not just compressed information. It contains task-shaping
authority surfaces: answer type, relation, span granularity, and final-answer
commitment. Models can use the evidence correctly while still obeying the
wrong public-state contract.
```

The best face is not "typed state solves authority." The better claim is:

```text
Authority roles are real enough to perturb and sometimes quarantine, but role
labels are themselves model-visible text and can become another authority or
candidate-attraction surface.
```

This is a more interesting object than another verifier prompt because it
exposes a protocol-level problem: a public field must decide what it authorizes,
not just what it says.

## Caveats

- Selected saved-field cases, not a population estimate.
- The packet is adversarial by construction.
- AVR is meaningful only on base-correct cases.
- Exact-match span noise remains entangled with several authority violations.
- Typed quarantine includes an untrusted candidate, so it tests a hard typed
  state surface rather than a clean no-candidate role protocol.
- This is not a full PACT rerun and not a cross-task transfer result.

## Next Pressure

The next move should not be a bigger version of the same arena.

Use this result to make a stricter protocol split:

1. `typed_no_candidate`: trusted task plus typed evidence, no candidate field;
2. `typed_candidate_hidden`: candidate available only as metadata, not visible
   to the model;
3. `typed_candidate_visible`: current hard setting;
4. `typed_candidate_visible_with_extract_only`: require extraction from
   evidence before candidate comparison.

If `typed_no_candidate` keeps the rescues without the new violations, the
protocol story becomes much stronger. If it still fails, the problem is not
candidate attraction alone; type labels are too weak as a boundary mechanism.
