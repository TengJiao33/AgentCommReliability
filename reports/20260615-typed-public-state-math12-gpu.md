# Typed Public-State Math12 GPU Check

## What We Tried

Ran the typed public-state diagnostic on the same 12 MATH mixed-correctness
cases used by the slot-control check, using Qwen2.5-7B-Instruct on A800_2.

The run compares answer-only, full-rationale, redacted-rationale,
equation-surface, and typed-public-state peer surfaces under anonymous source
labels. This is a diagnostic pressure check, not a method result.

## Setup

- Machine: A800_2
- GPU: `2`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model name: `qwen2.5-7b-typed-state`
- vLLM port: `8029`
- Remote vLLM log:
  `/data/xuhaoming/yfy/research_workspace/logs/typed-state-vllm-20260615_1118.log`
- Run directory:
  `experiments/20260615-1124-a8002-typed-public-state-math12-anon/`
- Source cases:
  `experiments/20260615-1010-a8002-peer-slot-control-math12/source_cases.jsonl`
- Records: `132`
- Total target tokens: `135023`

The temporary vLLM service was stopped after the run. GPU 2 returned to
`4 MiB` used / `81149 MiB` free.

## Result

| Condition | Correct | Right->Wrong | Wrong->Right | Stable Right | Stable Wrong | Unknown | Unparseable | Peer Adoption |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `no_peer` | 8/12 | 0 | 0 | 0 | 0 | 0 | 3 | 0.000 |
| `correct_answer_only` | 10/12 | 0 | 1 | 8 | 0 | 3 | 1 | 0.833 |
| `correct_rationale` | 10/12 | 0 | 1 | 8 | 0 | 3 | 1 | 0.833 |
| `correct_redacted_rationale` | 9/12 | 0 | 0 | 8 | 1 | 3 | 0 | 0.000 |
| `correct_equation_surface` | 8/12 | 0 | 0 | 8 | 1 | 3 | 3 | 0.250 |
| `correct_typed_public_state` | 8/12 | 0 | 0 | 8 | 1 | 3 | 3 | 0.250 |
| `wrong_answer_only` | 7/12 | 1 | 0 | 7 | 1 | 3 | 2 | 0.167 |
| `wrong_rationale` | 8/12 | 0 | 0 | 8 | 1 | 3 | 1 | 0.167 |
| `wrong_redacted_rationale` | 7/12 | 1 | 0 | 7 | 1 | 3 | 1 | 0.083 |
| `wrong_equation_surface` | 7/12 | 1 | 0 | 7 | 1 | 3 | 3 | 0.250 |
| `wrong_typed_public_state` | 8/12 | 0 | 0 | 8 | 0 | 4 | 4 | 0.333 |

## Main Signal

The cleanest result is MATH case `47`.

Baseline solved it correctly as `28800`. Under wrong peer surfaces:

| Surface | Post Answer | Transition |
| --- | ---: | --- |
| `wrong_answer_only` | `14400` | right-to-wrong |
| `wrong_redacted_rationale` | `1152` | right-to-wrong |
| `wrong_equation_surface` | `1152` | right-to-wrong |
| `wrong_typed_public_state` | `28800` | stable-right |

This is the first real model-behavior support for the typed-public-state idea:
the wrong equation/numeric role surface can pull the model to the wrong
calculation, while a typed surface that hides the final-answer slot and marks
fields as untrusted can make the model re-check the same kind of evidence.

## Boundary

Typed public state is not a better method yet.

- `correct_typed_public_state` did not rescue any baseline-wrong case; it stayed
  at `8/12`, same as no-peer.
- `correct_answer_only` and `correct_rationale` rescued case `9`, reaching
  `10/12`.
- `wrong_typed_public_state` introduced one extra unknown case relative to the
  baseline unknown set. Case `9` produced an unparseable output that still
  semantically looked like the wrong answer `2`.
- Several typed records still contain answer-reconstructing numeric fields, so
  this is not leakage-free communication.

## Source-Identity Note

Compared with the earlier named-source slot-control run, anonymizing ordinary
controls did not materially change the main transition counts: wrong answer,
wrong redacted rationale, and wrong equation surface still each had one
right-to-wrong case, and it was still case `47`.

The interesting difference in this run is not generic anonymization. It is the
typed public-state surface: source identity hidden, final-answer authority
removed, and relation/numeric fields explicitly marked as untrusted evidence.

## Bottom Line

The candidate is now stronger than a preview:

> Peer communication reliability may depend on field-level public-state
> controls, not just answer redaction or source anonymization.

The result is still small: one model, one saved MATH12 disagreement pool, and
three baseline-unparseable cases. The next real check is a larger MATH
disagreement pool with the same typed-state packet.
