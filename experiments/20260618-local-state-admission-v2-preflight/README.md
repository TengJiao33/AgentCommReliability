# State Admission V2 Local Preflight

日期：2026-06-18

状态：local design preflight。这里还没有物化 packet、runner、outputs 或 GPU run。

## Files

- `README.md`: preflight purpose, gates, and next local actions.
- `schema.md`: draft row schema and promotion rules.
- `candidate_rows.jsonl`: structured V2 row candidates. These are design rows, not runnable packet rows.
- `source_cards.preview.jsonl`: short source-card previews for the first manual-audit seeds. These are not model prompts.
- `manual_audit.md`: first local audit of the preview seeds and packet-promotion risks.
- `hiddenbench_fact_units.draft.json`: local extraction draft for three HiddenBench rows. This is evaluator/planning metadata, not a packet or prompt.
- `source_scope_perturbations.draft.json`: local perturbation draft for the three HiddenBench rows. This is not a packet or prompt.

## Purpose

这个 preflight 用来判断 State Admission V2 是否值得实现。V1.1 已经显示 direct admitted-state generation 会破坏 budget 和 empty-role rejection，priority 加 executor 能恢复合法性；V1.1 也暴露了合成压力过强、强符号 baseline 过强、admission units 显式暴露的问题。

V2 的设计目标是把问题推进到 hidden admission-unit construction：模型先从 source ledger、recipient scope、dependency、verification state 和 downstream decision proxy 中提出 candidate admission units，再由 deterministic executor 编译成合法 admitted state 和 rejection certificate。

## Current Evidence Handle

- V1.1 local packet: `experiments/20260618-local-state-admission-v1/README.md`
- V1.1 direct 14B pressure: `reports/20260618-state-admission-v1-qwen25-14b-pressure.md`
- V1.1 priority executor: `reports/20260618-state-admission-v1-priority-executor-pressure.md`
- V1.1 7B replication: `reports/20260618-state-admission-v1-priority-7b-replication.md`
- V1.1 ledger hidden-unit failure: `reports/20260618-state-admission-v1-ledger-hidden-unit-pressure.md`
- V2 synthesis report: `reports/20260618-skill-guided-state-admission-v2-preflight.md`

## Preflight Contract

Purpose：判断 role-scoped evidence admission 是否能在 source/scope/dependency/verification/budget 下构造合法且有 downstream 用处的局部上下文。

Unit：one packet row。每行应包含 roles、sources、recipient eligibility、dependency edges、verification state、global budget、downstream decision proxy、oracle admitted units、oracle rejections。

Primary contrast：two-stage candidate-unit proposal plus executor 对比 direct source-card output、shared-context baseline、CICL-style decision-context packing、PerspectiveGap role assignment baseline、symbolic group-density baseline。

Success signal：two-stage protocol 在 legality 指标上接近 oracle executor，并在 downstream decision proxy 上优于 shared context 和 direct cards；强符号 baseline 不能近似吃满 oracle。

Failure signal：group-density 或 CICL-style baseline 接近 oracle；hidden-unit model 仍接近 V1.1 ledger-first `1/40` collapse；downstream proxy 和 admitted-state metrics 脱钩；source/scope perturbation 不改变 admission。

Invalidation conditions：gold recipients 泄露到 prompt；downstream proxy 只重复 card scorer；dependency closure 人工到无法解释；JSON repair 决定主差异；shared-context baseline 过弱；source/scope perturbation 只换名字不换准入语义。

## Candidate Row Sketches

| Row | Source | Roles | Diagnostic Purpose | Required Manual Check |
| --- | --- | --- | --- | --- |
| `pg_000_scope_flip` | V1.1 `pg_000` seed 1/42 | coder, reviewer | Same-content recipient flip under rotated source scope; tests whether model follows source/scope over semantic role intuition. | Verify the coder bundle is downstream-useful and reviewer empty state is justified by budget/scope rather than arbitrary utility. |
| `pg_002_cross_role_group` | V1.1 `pg_002` seed 1 | dispatcher, coder, reviewer | Cross-role unit where coder/reviewer pair group matters and dispatcher should stay out. | Check whether downstream proxy needs both coder and reviewer evidence, and whether dispatcher rejection is meaningful. |
| `pg_015_verification_gate` | V1.1 `pg_015` seed 1 | medical_writer, regulatory_reviewer | Medical/regulatory surface for verification-gated admission and conservative rejection. | Confirm no sensitive or medical-claim text is used as a real-world medical recommendation; keep it synthetic or benchmark-contained. |
| `pg_022_source_provenance` | V1.1 `pg_022` seed 1 | investigative_journalist, fact_checker | Source ownership and fact-checking admission; tests provenance-aware local state. | Ensure gold depends on source authority/scope, not only semantic relevance. |
| `pg_029_dependency_closure` | V1.1 `pg_029` seed 1 | prover, referee | Formal reasoning/proof surface; tests dependency closure and role-local proof obligations. | Check whether a partial source can look useful while releasing zero downstream value. |
| `pg_066_six_role_budget` | V1.1 `pg_066` seed 1 | six provenance/authentication roles | High-role-count cross-budget conflict; tests whether V2 scales beyond two-role examples. | Audit prompt length and ensure oracle group is human-readable before any GPU. |
| `hiddenbench_evacuation_west_city` | HiddenBench task 1 | route_planner, risk_checker, coordinator | Option-blocking hidden facts; tests source facts entering a decision proxy. | Verify admitted facts support `West City` without exposing gold label or recommendation. |
| `hiddenbench_emergency_supply_drop` | HiddenBench task 10 from prior reports | logistics_planner, hazard_checker, final_decider | Negative constraint should block a tempting option; tests rejection of recommendation leakage. | Compare against old exchange failure where Warehouse B was over-recommended despite hazard fact. |
| `hiddenbench_conference_relocation` | HiddenBench task 11 from prior reports | facilities_checker, recovery_checker, final_decider | Repairing fact and blocking fact must be combined; tests enabling plus disabling evidence units. | Confirm downstream decision can be scored from facts alone, not sender recommendation. |
| `hiddenbench_baker_2010_visibility` | HiddenBench Stage 4 `baker_2010` case | option_reader, fact_reporter, final_decider | Candidate/shared visibility anchoring case; tests whether source/scope admission reduces answer anchoring. | Reconstruct exact record from Stage 4 outputs before using it; do not rely on report prose alone. |

Structured candidate metadata is recorded in `candidate_rows.jsonl`. Current status:

- `exact_source_ref`: 9 rows have source paths and row ids sufficient for extraction.
- `needs_record_extraction`: 1 row, `hiddenbench_baker_2010_visibility`, still needs exact Stage 4 condition records before packet use.
- `manual_audit_status=hold`: 1 row, `pg_000_scope_flip`, because its downstream proxy is not independent enough for the first V2 packet.
- `manual_audit_status=partial`: 4 rows still need full source extraction, oracle unit schema, rejection certificate, and baseline fairness checks.
- `manual_audit_status=passed`: 0 rows. No row is claim-bearing yet.

The first source preview covers `pg_000_scope_flip`, `hiddenbench_emergency_supply_drop`, and `hiddenbench_conference_relocation`. The manual audit in `manual_audit.md` holds `pg_000_scope_flip` and keeps the HiddenBench rows as `partial` seeds. `hiddenbench_fact_units.draft.json` now sketches the full source facts, oracle admission units, rejection/inert units, and downstream scoring obligations for three HiddenBench rows. `source_scope_perturbations.draft.json` adds same-text verification and recipient-scope perturbations for those rows.

## Required Baselines

1. `oracle_executor`: gold candidate units plus deterministic executor.
2. `shared_verified_context`: all admitted verified facts compressed into one shared state for all roles.
3. `direct_source_cards`: model directly outputs role-to-source cards.
4. `cicl_style_card_packing`: utility-ranked evidence cards under budget, without recipient-specific legality beyond obvious eligibility.
5. `perspectivegap_role_assignment`: role-fragment assignment scorer style, with no downstream decision proxy.
6. `source_density`: source-level utility or hint density.
7. `group_density_symbolic`: strongest transparent symbolic group baseline.
8. `ledger_first_model`: model outputs role-to-source priority without proposed units.
9. `exposed_unit_priority`: V1.1-style exposed bundles/groups, kept as upper diagnostic.
10. `two_stage_model_units`: model proposes units, executor validates and compiles.

## Packet Gate Checklist

- [ ] Every row has a downstream decision or action proxy independent of the source-card scorer.
- [ ] Every row has at least one rejection whose reason is source/scope/verification/budget, not only irrelevance.
- [ ] Same-content source/scope perturbation changes gold admission in at least several rows.
- [ ] Dependency closure is explainable by a human reader.
- [ ] Shared-context and CICL-style baselines are implemented before any method claim.
- [ ] Gold recipients, oracle units, and oracle groups are absent from model prompts.
- [ ] JSON parser failures are tracked separately from behavioral failures.
- [ ] Prompt length is audited for the largest row before launch.
- [ ] A gold-smoke or oracle-executor smoke reaches `100%` expected legality.
- [ ] No A800 run starts until at least three concrete rows are manually inspected end to end.

## Draft Extraction Status

`hiddenbench_fact_units.draft.json` is a planning artifact for three rows:

- `hiddenbench_emergency_supply_drop`: extracts Warehouse A distribution blockers, Warehouse B hazard blocker, Warehouse C distribution enabler, and recommendation-leakage rejection for tempting Warehouse B context.
- `hiddenbench_conference_relocation`: extracts City Library fuel blocker, Community Center chemical-leak blocker, School Gym restroom-restoration enabler, and off-option handling for College Hall.
- `hiddenbench_evacuation_west_city`: extracts East Town tunnel/fire blockers, North Hill trail/driveway blockers, West City bridge/accommodation enabler, and recommendation-leakage rejection for tempting East Town and North Hill context.

These rows are still not packet-ready. They still need source/scope perturbation, prompt rendering rules, and oracle/baseline smokes before any model prompt exists.

## Perturbation Draft Status

`source_scope_perturbations.draft.json` now gives each drafted HiddenBench row a base variant plus two perturbations:

- `hiddenbench_emergency_supply_drop`: quarantines the Warehouse B gas sensor fact, then removes final_decider scope from the Warehouse C enabler.
- `hiddenbench_conference_relocation`: quarantines the School Gym restroom-repair fact, then removes final_decider scope from the City Library fuel blocker.
- `hiddenbench_evacuation_west_city`: quarantines the West City bridge accessibility fact, then splits North Hill blockers across roles without a group edge.

These perturbations are meant to make gold admission change without changing the fact text. They still need a renderer audit and oracle/baseline smoke before they can become packet rows.

## No-GPU Rule

This directory is a preflight surface only. Do not launch GPU from this artifact. The next valid action is to materialize a tiny local packet sketch with 8 to 12 rows and run oracle/baseline smokes locally.

## Next Local Actions

1. Audit whether the perturbations change gold admission for the intended reason rather than by making the row undecidable in a trivial way.
2. Decide whether `hiddenbench_evacuation_west_city` is only a sanity row or can be strengthened with verification/source-owner pressure.
3. Draft V2 row schema fields in code only after at least three rows pass manual audit.
4. Build only oracle and transparent baselines first.
5. Manually inspect at least three rows before writing a model prompt.
