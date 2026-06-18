# PerspectiveGap Hard Routing V0

## Purpose

This local packet makes the existing PerspectiveGap role-assignment task harder before spending GPU/API budget. Each evaluation becomes a state-card routing task: for every role, a valid response must choose fragment cards, copy `source_id`, assign a visibility label, stay within a per-role budget, and explicitly reject distractors.

## Status

Local benchmark prototype and deterministic baseline scoring are complete. No new model calls were made for this packet.

## Files

- `hard_packet.jsonl`: full `220` rendered PerspectiveGap evaluations.
- `hard_packet_stratified20.jsonl`: `40` evaluations from the same `20` scenario stratified set used by the earlier Qwen2.5 role-assignment run.
- `hard_packet_smoke4.jsonl`: first 4-row direct prompting smoke packet with the original V0 prompt.
- `hard_packet_smoke4_promptv2.jsonl`: same 4 rows with clarified `rejected` and `visibility` prompt contract.
- `summary_*.json` and `summary_*.md`: scorer outputs for deterministic baselines and legacy-projected Qwen2.5 outputs.
- `scores_*.jsonl`: per-evaluation hard-routing score records.

## Preflight

- Unit: one rendered PerspectiveGap evaluation row.
- Main contrast: oracle vs all-to-all vs no-distractor all-to-all vs shared-only vs budget-cheapest.
- Extra diagnostic: legacy projection of earlier Qwen2.5 7B/14B stratified20 role-list predictions.
- Success signal: over-sharing and precision-only cheap strategies fail under budget/reject/scope pressure.
- Failure signal: the scorer only catches format errors and leaves all routing strategies behaviorally tied.

## Build

```powershell
python scripts\build_perspectivegap_hard_routing_packet.py `
  --out experiments\20260618-local-perspectivegap-hard-routing-v0\hard_packet.jsonl
```

```powershell
python scripts\build_perspectivegap_hard_routing_packet.py `
  --out experiments\20260618-local-perspectivegap-hard-routing-v0\hard_packet_stratified20.jsonl `
  --scenario-id pg_000 --scenario-id pg_002 --scenario-id pg_003 --scenario-id pg_004 --scenario-id pg_005 `
  --scenario-id pg_006 --scenario-id pg_007 --scenario-id pg_015 --scenario-id pg_022 --scenario-id pg_029 `
  --scenario-id pg_049 --scenario-id pg_062 --scenario-id pg_066 --scenario-id pg_069 --scenario-id pg_072 `
  --scenario-id pg_076 --scenario-id pg_079 --scenario-id pg_089 --scenario-id pg_099 --scenario-id pg_109
```

Full packet summary: `220` evaluations; role-count distribution `2:44`, `3:66`, `4:22`, `5:66`, `6:22`; mean fragments `10.000`; mean budget per role `13.346`.

Stratified20 packet summary: `40` evaluations; role-count distribution `2:8`, `3:8`, `4:8`, `5:8`, `6:8`; mean fragments `10.250`; mean budget per role `12.421`.

## Deterministic Baselines

| Baseline | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Reject recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| oracle | 220/220 | 1.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 |
| all_to_all | 0/220 | 1.000 | 0.318 | 3.800 | 0.000 | 128.464 | 0.000 |
| no_distractor_all_to_all | 0/220 | 1.000 | 0.350 | 0.000 | 0.000 | 117.064 | 1.000 |
| shared_only | 0/220 | 0.031 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 |
| budget_cheapest | 0/220 | 0.577 | 0.419 | 2.845 | 1.000 | 0.000 | 0.000 |

`shared_only` also rejects needed fragments at `8.800` per evaluation on average. This is why high precision alone is not a useful success signal for the harder task.

## Legacy Projection

The earlier Qwen2.5 role-assignment outputs emitted only `role -> fragment_id` lists. The hard scorer can project these legacy predictions into state cards to compare coverage, precision, leakage, and budget pressure. This projection auto-fills `source_id` and `visibility` from the selected fragment id, so source and visibility accuracy are upper-bound diagnostics only.

| Source | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Reject recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-7b legacy projected | 0/40 | 0.443 | 0.786 | 0.050 | 0.625 | 1.275 | 0.000 |
| qwen2.5-14b legacy projected | 0/40 | 0.615 | 0.808 | 0.450 | 0.400 | 4.725 | 0.000 |

The projection preserves the upstream role-assignment scorer counts exactly: 7B has `tp=239`, `fp=65`, `fn=301`, `leak=2`; 14B has `tp=332`, `fp=79`, `fn=208`, `leak=18`.

## Interpretation

This V0 benchmark surface separates at least four cheap behaviors:

- all-to-all maximizes recall but collapses precision, budget, and rejection;
- no-distractor all-to-all removes leakage but still collapses budget and precision;
- shared-only maximizes precision but destroys coverage;
- budget-cheapest passes budget but keeps poor coverage, poor precision, and high leakage.

The legacy Qwen2.5 projection adds a useful warning: the 7B result that looked relatively precise under the original scorer is conservative under-routing under the harder scorer, while 14B gains coverage with more leakage and more budget failure.

## Next Step

Run direct hard-card prompting on the same stratified20 subset for Qwen2.5 7B/14B. The output format should require model-generated `fragment_id`, `source_id`, `visibility`, and `rejected` cards instead of using legacy projection. A useful signal would be nonzero strict passes, nonzero reject recall, higher budget pass, and no coverage collapse.

If direct hard-card prompting produces parseable outputs and differentiated failures, scale to full220. If it collapses to all-zero strict scores, add one constrained arm before scaling: either a typed provenance router, a DALA-style budgeted routing auction, or a source-perturbation variant that makes source identity behaviorally necessary.

Update after `20260618-a8002-perspectivegap-hard-routing-smoke4-promptv2-qwen25-7b`: direct hard-card prompting is not scale-ready yet. The 4-row smoke produced differentiated failures, but it also had `1/4` malformed JSON and severe visibility confusion. Add a parser gate and a two-stage routing/visibility arm before stratified20.
