# Field-Authority Offset150 Semantic Focus

Date: 2026-06-15

## What We Inspected

I inspected the offset150 target-focus units from the packet-derived bridge:

- `11` public-target-without-question regressions;
- `10` frozen-question-target rescues;
- `1` frozen-question-target regression.

Extraction artifacts:

- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-focus-offset150/focus_cards.jsonl`
- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-focus-offset150/focus_cards.md`
- `experiments/_archive/20260616-pruned/20260615-local-pact-field-authority-focus-offset150/manual_semantic_labels.jsonl`

The focus-card extractor is:

- `scripts/build_pact_field_authority_focus_cards.py`

## Manual Semantic Families

| Semantic family | Count | Read |
| --- | ---: | --- |
| `answer_type_projection` | `10` | The original question is needed to recover the requested answer type or relation, such as entity vs date, yes/no, choice, shared attribute, or time span. |
| `short_span_or_granularity` | `9` | The public fields contain the right semantic answer, but the model needs the question contract to choose the exact short span or drop qualifiers. |
| `evidence_sentence_or_distractor` | `2` | The model copies a supporting sentence or distractor phrase rather than extracting the answer span. |
| `question_root_boundary_regression` | `1` | The question root reintroduces ambiguity or outside prior and harms a case the public state answered correctly. |

## What This Means

The offset150 focus units are not mostly lexical target-slot drift. They are
mostly answer-contract failures:

- what kind of thing should be returned;
- which relation is being asked;
- whether the answer should be yes/no, an entity, a date, a comparison choice,
  or a short span;
- how much qualifier/context belongs in the final answer.

This sharpens the handle:

**The public `Action Required` field can be useful evidence, but it is a weak
answer contract. The trusted question root supplies answer type and span
granularity, not only a better lexical target.**

## Detector Consequence

The old lexical target-slot candidate signal does not line up with these focus
units:

- focus cards: `22`;
- target-slot candidate true: `1`;
- target-slot candidate false: `21`.

That reinforces the current decision not to revive the standalone lexical
authority detector. A future verifier would need to reason about answer type,
relation, and span granularity against the question, not just lexical overlap
or anchor loss in `Action Required`.

## Boundary

Sample `164:final_contract` is the warning case. The base public-state answer is
correct, but the frozen-question prompt produces a longer ambiguous answer with
outside knowledge. This says the trusted question root is not automatically
safe; it can revive ambiguity when the saved evidence is underspecified.

## Caveats

- Manual labels cover only `22` focus cards from one offset150 saved-field run.
- Exact-match span noise is part of several `short_span_or_granularity` labels.
- This is still saved-field re-answering, not a full PACT rerun.
- The labels are diagnostic vocabulary, not a population taxonomy.

## Next Pressure

The next useful pressure is not another detector. It is a cross-slice semantic
focus comparison: apply the same focus-card extraction to offset100 and ask
whether the same answer-contract families repeat.

