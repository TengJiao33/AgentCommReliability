# State Admission V2 Sketch Schema

This schema is for a local design sketch, not a runnable packet. A row becomes
eligible for packet materialization only after its source text, downstream
proxy, oracle units, and rejection certificate have been manually audited.

## Row Fields

`sketch_id`: Stable local id for the proposed V2 row.

`status`: One of `exact_source_ref`, `needs_record_extraction`, or
`needs_manual_audit`.

`source_family`: Source benchmark or local packet family, for example
`perspectivegap_v1_1` or `hiddenbench`.

`source_path`: Local authoritative file or directory containing the source row.

`source_row_ref`: Exact row identifier in the source artifact. For
PerspectiveGap-derived rows, this is usually a `hard_evaluation_id`. For
HiddenBench rows, this is `task_id:name`.

`roles`: Recipient roles to use in the V2 sketch. Roles may come from the
source row or be a minimal role decomposition for HiddenBench facts.

`downstream_proxy`: The decision, action, or prompt-writing outcome the admitted
state should support. This must not merely restate the source-card scorer.

`source_scope_pressure`: What source/scope condition should change the correct
admission decision.

`unit_construction_pressure`: What bundle, dependency, or cross-role unit the
model must infer or propose.

`verification_pressure`: Whether any source needs verified, unverified,
quarantined, or reject-only treatment.

`budget_pressure`: The budget conflict or scarcity condition.

`oracle_expectation`: Current expected gold behavior. This is a design
expectation, not a validated packet label until manually audited.

`baselines_to_check`: Required transparent baselines for this row.

`manual_audit_status`: One of `todo`, `partial`, `hold`, `passed`, or
`retired`.

`caveat`: The most important reason this row may fail the packet gate.

## Promotion Rules

A sketch row can be promoted into a materialized V2 packet only if:

- its source text can be reconstructed from `source_path` and `source_row_ref`;
- its downstream proxy can be scored independently from admitted-card strict;
- at least one rejection is source/scope/verification/budget-driven;
- oracle units and rejections are human-readable;
- shared-context and CICL-style baselines have a fair representation;
- no oracle recipient, oracle unit, or gold answer is visible in the model
  prompt except through allowed source facts.

Rows that raise a live design risk should be marked `hold` until redesigned.
Rows that fail these checks after redesign should remain in the sketch or be
retired.

## HiddenBench Fact-Unit Draft Fields

`hiddenbench_fact_units.draft.json` is a local extraction draft. It is not a
packet schema and must not be rendered directly into a model prompt.

`prompt_visibility_policy`: separates allowed prompt fields from evaluator-only
gold, oracle units, and scoring obligations.

`source_facts`: source-level facts reconstructed from HiddenBench shared and
hidden information, with candidate recipients and expected treatment.

`oracle_admission_units`: human-readable blocker, enabler, context, dependency,
or repair units expected after manual audit.

`oracle_rejections`: facts or interpretations that should be rejected, treated
as inert, or prevented from becoming recommendations.

`downstream_scoring_obligations`: evaluator-only checks that should make a final
decision score depend on admitted facts, not only on choosing the gold option.

## Source/Scope Perturbation Draft Fields

`source_scope_perturbations.draft.json` is a local perturbation draft. It is not
a packet schema and must not be rendered directly into a model prompt.

`base_variant`: the verified, role-scoped state expected to admit the fact-unit
draft's oracle units.

`perturbation_variants`: same-text variants that change only verification state,
recipient scope, dependency edge, or source owner. The expected admission must
change for a reason that a human can inspect.

`same_text_fact_ids`: source facts whose text must remain byte-identical to the
fact-unit draft while their source/scope state changes.

`expected_admission_delta`: evaluator-only oracle changes such as dropped units,
modified recipients, or added rejection reasons.

`expected_downstream_delta`: the downstream decision or insufficiency state
created by the admission change. This is evaluator metadata, not prompt text.
