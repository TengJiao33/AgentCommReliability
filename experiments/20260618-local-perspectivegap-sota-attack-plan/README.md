# PerspectiveGap SOTA Attack Plan Local Smoke

Date: `2026-06-18`.

## Purpose

Test whether the PerspectiveGap `prompt_writing` task can be handled as a deterministic expansion of a role-fragment assignment, using only rendered fragment text and role-assignment predictions.

This is a local diagnostic smoke. It is not a leaderboard submission and does not use a model endpoint.

## Artifacts

| Artifact | Description |
| --- | --- |
| `oracle_assignment_to_prompt_predictions.jsonl` | Prompt-writing predictions generated from oracle role assignments. |
| `oracle_assignment_to_prompt_scores.jsonl` | Official scorer output for the oracle-derived prompt-writing rows. |
| `stratified20_qwen25_7b_assignment_to_prompt_predictions.jsonl` | Prompt-writing rows generated from prior Qwen2.5-7B role-assignment predictions. |
| `stratified20_qwen25_7b_assignment_to_prompt_scores.jsonl` | Official prompt-writing scores for the 7B converted rows. |
| `stratified20_qwen25_14b_assignment_to_prompt_predictions.jsonl` | Prompt-writing rows generated from prior Qwen2.5-14B role-assignment predictions. |
| `stratified20_qwen25_14b_assignment_to_prompt_scores.jsonl` | Official prompt-writing scores for the 14B converted rows. |
| `stratified20_qwen25_7b14b_union_role_predictions.jsonl` | No-gold union ensemble of prior 7B and 14B role-assignment rows. |
| `stratified20_qwen25_7b14b_union_role_scores.jsonl` | Official role-assignment scores for the no-gold union ensemble. |
| `stratified20_qwen25_7b14b_union_prompt_predictions.jsonl` | Deterministic prompt-writing rows generated from the union ensemble. |
| `stratified20_qwen25_7b14b_union_prompt_scores.jsonl` | Official prompt-writing scores for the union-derived prompt rows. |
| `stratified20_qwen25_7b14b_intersection_role_predictions.jsonl` | No-gold intersection ensemble of prior 7B and 14B role-assignment rows. |
| `stratified20_qwen25_7b14b_intersection_role_scores.jsonl` | Official role-assignment scores for the no-gold intersection ensemble. |
| `stratified20_qwen25_7b14b_intersection_prompt_predictions.jsonl` | Deterministic prompt-writing rows generated from the intersection ensemble. |
| `stratified20_qwen25_7b14b_intersection_prompt_scores.jsonl` | Official prompt-writing scores for the intersection-derived prompt rows. |

## Commands

Syntax check:

```powershell
python -m py_compile scripts\perspectivegap_assignment_to_prompt_predictions.py
```

Oracle assignment to prompt-writing rows:

```powershell
python scripts\perspectivegap_assignment_to_prompt_predictions.py `
  --oracle `
  --out experiments\20260618-local-perspectivegap-sota-attack-plan\oracle_assignment_to_prompt_predictions.jsonl
```

Official scorer:

```powershell
$env:PYTHONPATH='src'
python scripts\score_predictions.py `
  --predictions D:\develop\AgentCommReliability\experiments\20260618-local-perspectivegap-sota-attack-plan\oracle_assignment_to_prompt_predictions.jsonl `
  --out D:\develop\AgentCommReliability\experiments\20260618-local-perspectivegap-sota-attack-plan\oracle_assignment_to_prompt_scores.jsonl
```

Prior stratified20 role-assignment predictions to prompt-writing rows:

```powershell
python scripts\perspectivegap_assignment_to_prompt_predictions.py `
  --assignments experiments\20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b\predictions_qwen25_7b.jsonl `
  --out experiments\20260618-local-perspectivegap-sota-attack-plan\stratified20_qwen25_7b_assignment_to_prompt_predictions.jsonl

python scripts\perspectivegap_assignment_to_prompt_predictions.py `
  --assignments experiments\20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b\predictions_qwen25_14b.jsonl `
  --out experiments\20260618-local-perspectivegap-sota-attack-plan\stratified20_qwen25_14b_assignment_to_prompt_predictions.jsonl
```

No-gold 7B/14B role-assignment ensemble:

```powershell
python scripts\perspectivegap_ensemble_role_assignments.py `
  --strategy union `
  --model-name qwen25_7b14b_union_no_gold `
  --predictions experiments\20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b\predictions_qwen25_7b.jsonl `
  --predictions experiments\20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b\predictions_qwen25_14b.jsonl `
  --out experiments\20260618-local-perspectivegap-sota-attack-plan\stratified20_qwen25_7b14b_union_role_predictions.jsonl

python scripts\perspectivegap_ensemble_role_assignments.py `
  --strategy intersection `
  --model-name qwen25_7b14b_intersection_no_gold `
  --predictions experiments\20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b\predictions_qwen25_7b.jsonl `
  --predictions experiments\20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b\predictions_qwen25_14b.jsonl `
  --out experiments\20260618-local-perspectivegap-sota-attack-plan\stratified20_qwen25_7b14b_intersection_role_predictions.jsonl
```

## Result

| Source assignment | Rows | Prompt-writing strict | Coverage | Precision | Distractor leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| Oracle role assignment | 220 | 220/220 | 1.0000 | 1.0000 | 0.0000 |
| Qwen2.5-7B stratified20 role assignment | 40 | 0/40 | 0.4426 | 0.8536 | 0.0500 |
| Qwen2.5-14B stratified20 role assignment | 40 | 0/40 | 0.6148 | 0.8078 | 0.4500 |
| 7B/14B union role assignment | 40 | 0/40 | 0.6648 | 0.7606 | 0.4500 |
| 7B/14B intersection role assignment | 40 | 0/40 | 0.3926 | 0.9680 | 0.0500 |

The oracle result initially scored `219/220` because directly concatenating fragments created one cross-fragment n-gram false positive. Wrapping each fragment in a neutral `<fragment id="...">...</fragment>` boundary fixed the scorer artifact while preserving full fragment text.

## Interpretation

The deterministic prompt writer is a valid technical component for a system route: if role assignment is correct, prompt writing can reach the official scorer ceiling.

This shifts the SOTA pressure toward role assignment. For a full official PerspectiveGap run, the current leaderboard target is greater than `273/440` combined passes, so a pure assignment-to-prompt route would need more than `137/220` role-assignment strict passes before any extra gains from direct prompt-writing are considered.

The no-gold 7B/14B ensemble shows useful complementarity but no strict-pass breakthrough. Union raises coverage over 14B (`0.6648` vs `0.6148`) and slightly improves net match, while intersection raises precision to `0.9680`; neither creates exact rows. The next route needs more diverse prompt arms or a stronger model, not simple two-model set voting.

## Integrity Boundary

Do not use `reference_need_sets`, scenario frontmatter answers, PG40 `recipient_scope`, SSEAC `required_slots`, or any derived oracle fields at prediction time for an official or paper-facing run. The `--oracle` mode exists only to validate the conversion and scorer path.
