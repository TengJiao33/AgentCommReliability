# Field-Authority Cross-Slice Semantic Focus

Date: 2026-06-15

## What We Compared

I applied the same target-focus extraction and manual semantic labels to two
neighboring HotpotQA saved-field slices:

- offset100: `experiments/20260615-local-pact-field-authority-focus-offset100/`
- offset150: `experiments/20260615-local-pact-field-authority-focus-offset150/`

The focus units are only target-layer bridge cases:

- public target without original question regresses;
- frozen question target rescues;
- frozen question target regresses.

## Counts

| Slice | Focus cards | Public-target regressions | Frozen-target rescues | Frozen-target regressions |
| --- | ---: | ---: | ---: | ---: |
| offset100 | `28` | `20` | `7` | `1` |
| offset150 | `22` | `11` | `10` | `1` |
| combined | `50` | `31` | `17` | `2` |

Manual semantic families:

| Semantic family | offset100 | offset150 | Combined |
| --- | ---: | ---: | ---: |
| `answer_type_projection` | `11` | `10` | `21` |
| `short_span_or_granularity` | `12` | `9` | `21` |
| `public_target_misdirection` | `3` | `0` | `3` |
| `evidence_sentence_or_distractor` | `1` | `2` | `3` |
| `question_root_boundary_regression` | `1` | `1` | `2` |

The old lexical target-slot candidate signal still misses the focus units:

| Slice | Focus cards | Old target-slot candidate true |
| --- | ---: | ---: |
| offset100 | `28` | `0` |
| offset150 | `22` | `1` |
| combined | `50` | `1` |

## Interpretation

Across both slices, the main repeated families are answer-contract families:

- `21/50` require the original question to recover answer type or relation;
- `21/50` require the original question to recover short-span or granularity
  requirements.

That is a stronger shape than the earlier target-slot-drift framing:

**Public `Action Required` can carry useful task hints, but it is not a stable
answer contract. The missing contract is often answer type and span
granularity, not merely lexical target overlap with the original question.**

The cross-slice result also explains why the standalone lexical detector kept
failing: the old target-slot candidate signal marks only `1/50` focus cards.

## Boundary Cases

There are two frozen-question-target regressions:

- offset100 sample `149:final_contract`;
- offset150 sample `164:final_contract`.

Both warn that the trusted question root is not automatically safe. When saved
evidence is underspecified or relation wording is ambiguous, reintroducing the
question can pull the model toward an outside prior or the wrong relation.

## Caveats

- Manual semantic labels are over selected focus cards, not the whole packet.
- Exact-match span artifacts are intentionally visible in
  `short_span_or_granularity`.
- The evidence is still saved-field re-answering, not full PACT reruns.
- This is diagnostic vocabulary, not a runtime verifier.

## Next Pressure

Do not build another lexical target detector.

The next useful object is a small answer-contract verifier/protocol sketch that
checks three things against the trusted question root:

1. answer type or relation requested;
2. required span granularity;
3. whether the public target/result supplies evidence for that contract or
   merely a related sentence.

Before implementing it, inspect whether an existing QA answer-type or
short-answer extraction benchmark/protocol already names this problem.

