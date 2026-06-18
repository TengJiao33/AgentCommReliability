# PerspectiveGap Source Perturbation V0

## Purpose

Create a source/scope perturbation gate where fragment text stays fixed but the communication state changes. The goal is to separate semantic content routing from source-ledger routing.

## Packet

- Source packet: `experiments/20260618-local-perspectivegap-hard-routing-v0/hard_packet_stratified20.jsonl`
- Output packet: `source_perturbation_rotated20.jsonl`
- Rows: `40`
- Variant: `rotated_scope`
- Role-count distribution: `2:8`, `3:8`, `4:8`, `5:8`, `6:8`
- Mean fragments: `10.25`
- Mean budget per role: `12.421`

`rotated_scope` keeps each fragment's text fixed and rotates non-reject recipient roles by one position in the row's role list. Reject fragments stay rejected. This makes the old content-based routing behavior wrong while keeping the task structurally close to PerspectiveGap.

## Local Baselines

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Overrun | Visibility acc | Reject recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| oracle | 40/40 | 1.000 | 1.000 | 0.000 | 1.000 | 0.000 | 1.000 | 1.000 |
| legacy Qwen2.5-7B on rotated | 0/40 | 0.076 | 0.135 | 0.050 | 0.300 | 2.950 | 1.000 | 0.000 |
| legacy Qwen2.5-14B on rotated | 0/40 | 0.150 | 0.197 | 0.450 | 0.075 | 8.250 | 1.000 | 0.000 |

The legacy projections are intentionally scored against the rotated source/scope gold. They show that old content-driven role-list predictions collapse when the communication state changes.

## Commands

```powershell
python scripts\build_perspectivegap_source_perturbation_packet.py `
  --packet experiments\20260618-local-perspectivegap-hard-routing-v0\hard_packet_stratified20.jsonl `
  --out experiments\20260618-local-perspectivegap-source-perturbation-v0\source_perturbation_rotated20.jsonl `
  --variant rotated_scope
```

```powershell
python scripts\score_perspectivegap_hard_routing.py `
  --packet experiments\20260618-local-perspectivegap-source-perturbation-v0\source_perturbation_rotated20.jsonl `
  --baseline oracle `
  --out experiments\20260618-local-perspectivegap-source-perturbation-v0\scores_oracle.jsonl `
  --summary-out experiments\20260618-local-perspectivegap-source-perturbation-v0\summary_oracle.md
```

## Next

Use `scripts/run_perspectivegap_source_ledger_router_openai_compatible.py` to test whether models can recover by following the explicit source access ledger.
