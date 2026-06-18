# Field-Authority Answer-Contract Outside Check

Date: 2026-06-15

## Why This Check

The cross-slice semantic focus report suggests that field-authority failures are
mostly answer-contract failures: answer type, relation, and short-span
granularity. Before sketching a protocol, I checked whether this is already
ordinary QA territory.

## Useful Hits

| Hit | What It Owns | Pressure On This Project |
| --- | --- | --- |
| [Learning Question Classifiers](https://aclanthology.org/C02-1150.pdf) | Classic answer-type classification for QA with a coarse/fine answer hierarchy. | Do not claim answer-type prediction as novel. Our `answer_type_projection` label is rediscovering a core QA control variable. |
| [Extreme Classification for Answer Type Prediction in Question Answering](https://arxiv.org/abs/2304.12395) | Modern semantic answer type prediction at large KG type scale. | Confirms answer-type prediction remains an active named QA task; our detector should not be framed as a generic answer-type predictor. |
| [HotpotQA](https://arxiv.org/abs/1809.09600) | Multi-hop QA with diverse questions, supporting facts, and comparison questions. | The target failures are unsurprising under HotpotQA: comparison and bridge questions often require answer type and relation recovery beyond one public field. |
| [MultiSpanQA](https://aclanthology.org/2022.naacl-main.90.pdf) | Single-span limits, multi-span answer semantics, and span-structure labels. | Useful language for span structure and answer semantics, but our current failures are mostly short-answer contract and qualifier control, not multi-span QA. |
| [Question-Attended Span Extraction](https://arxiv.org/html/2404.17991v1) | Uses the question to direct span extraction from text. | Nearby mechanism: the question can anchor answer spans. Our variant is not extraction from a passage, but validating public-state fields against a question root. |

Local radar check:

- The existing reading queue already has field-authority collision hits around
  trusted/untrusted channels, shared verified context, and PACT action-state
  handoff.
- I did not find a local radar item that directly owns answer-contract checking
  inside multi-agent public-state handoff.

## Interpretation

This outside check downgrades any broad naming around answer type or short
answer extraction. Those are established QA surfaces.

The surviving niche is narrower:

**In multi-agent public-state handoff, a public `Action Required` field may
carry useful evidence but fail to preserve the original question's answer
contract. A downstream protocol should check answer type, relation, and span
granularity against the trusted question root before treating public fields as
task authority.**

This is not a novelty claim yet. It is a protocol-shaped live handle.

## What Not To Claim

- Do not claim answer-type prediction as new.
- Do not claim short-answer/span extraction as new.
- Do not call the next object a generic QA verifier.
- Do not revive the lexical target-slot detector as the main route.

## Next Protocol Shape

A minimal answer-contract audit should record, for each public-state unit:

1. question-root answer type or relation;
2. expected short-span granularity;
3. public `Action Required` answer type or relation;
4. public `Action Result` evidence adequacy;
5. whether a downstream answer should freeze, hide, or accept the public target.

The key diagnostic is not aggregate EM. It is whether the audit predicts the
target-layer focus families already observed across offset100 and offset150.

