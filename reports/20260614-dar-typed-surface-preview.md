# DAR Typed Surface Preview

## What We Tried

After the case `20` raw-surface extract, I built a local preview of an
intermediate retained-message surface:

```text
source_agent
parsed_final_answer
one or two calculation/evidence lines
```

This is not a DAR method run. It is a prompt/content preview over existing raw
histories for cases `5`, `20`, `22`, and `37`.

No model call or GPU run was launched.

## What Happened

The preview covers 16 case variants and 32 retained messages.

| Surface | Average characters |
| --- | ---: |
| answer-only | 33.8 |
| typed preview | 157.2 |
| full response | 1089.0 |

For sample `20`, the preview preserves the exact problem that answer-only
destroyed:

```text
source_agent: Agent3
parsed_final_answer: 700.0
evidence:
- Five lollipops cost \(5 \times 0.40 = 2.00\) dollars.
- \[4.00 + 3.00 = 7.00\] dollars.
```

That is the desired middle surface: it does not pass the whole chain of thought,
but it also does not reduce the peer to a misleading parsed answer.

## Things Noticed

This preview makes the emerging handle more precise. The useful contrast is not
only `answer_only` versus `full_reasoning`; it is whether the public state can
separate:

- parsed final answer;
- evidence or calculation supporting the answer;
- parser/format failure in the final marker.

For sample `20`, the typed surface would expose a contradiction inside Agent3:
parsed answer `700.0`, evidence line ending in `7.00`. That is exactly the kind
of state an answer-only surface cannot represent.

The preview also keeps the project honest. The current line extractor is rough.
In sample `37`, it sometimes selects long narrative arithmetic lines. That
means the next step should be another offline prompt-inspection pass or a tiny
patch preview, not a broad GPU run.

## Caveats

- No model behavior was generated.
- The evidence extractor is heuristic and arithmetic-oriented.
- This is selected-case contact, not a rate estimate.
- The preview includes parsed correctness in JSON for audit, but does not use
  correctness to select evidence lines.

## Loose Threads

- Tighten the evidence-line extractor before turning it into a DAR patch.
- Compare the typed surface against PACT's action-state framing so this does
  not collapse back into local prompt-surface tinkering.
