# Public State Surface Alignment

## What We Tried

I aligned the DAR typed retained-message preview with PACT's action-state
messages under one local JSONL shape. The goal was not to claim a new method,
but to check whether the DAR middle surface is really moving toward a public
state representation, or merely becoming another local prompt surface.

No model call or GPU run was launched.

## What Happened

The alignment produced 232 public-state records:

| Source | Records | Surface |
| --- | ---: | --- |
| DAR typed preview | 32 | `typed_answer_evidence_preview` |
| PACT HotpotQA50 | 200 | `action_state` |

All records have `Action Required`, `Environment State`, and `Action Result`.
Only the 50 final PACT turns have `Final Answer`.

Average public-state length:

| Source | Avg public-state chars | Avg raw-output chars |
| --- | ---: | ---: |
| DAR typed preview | 157.2 | 1089.0 |
| PACT action-state | 363.9 | 363.9 |

The PACT raw/public equality here is a caveat: Qwen2.5-14B emitted no
`<think>` spans in this run, so the intended private-reasoning projection path
was not stressed.

## Things Noticed

The DAR typed preview can be made to fit the action-state slots:

- `Action Result`: parsed final answer;
- `Environment State`: selected calculation or evidence lines;
- `Action Required`: a synthetic instruction such as "use this retained peer
  state while revising."

That fit is useful but also exposes the gap. PACT's `Environment State` is a
verbatim sentence from the agent's private evidence context. DAR's typed
`Environment State` is extracted from a generated response. It may contain
calculation evidence, but it is already downstream of the model's reasoning and
formatting mistakes.

So the next durable axis is not simply:

```text
answer_only -> answer_plus_evidence -> full_reasoning
```

It is closer to:

```text
raw answer -> generated evidence state -> source-grounded public state
```

That distinction matters because DAR sample `20` needs a surface that can carry
evidence contradicting a parsed final answer, while PACT pressures us to keep
that evidence tied to an explicit public-state field rather than a free-form
reasoning trace.

## Caveats

- DAR side: selected diagnostic cases only.
- PACT side: HotpotQA50 smoke, not a full reproduction.
- This is a schema/content check, not an accuracy result.
- The alignment format `acr.public_state_surface.v0` is experimental and should
  not be promoted into the main trace schema until one real extractor or run
  uses it cleanly.

## Loose Threads

- Tighten DAR evidence extraction so `Environment State` is less narrative and
  more source-grounded.
- Use the PACT trace extractor in the main communication schema to compare
  field-level failure modes instead of only field compliance.
