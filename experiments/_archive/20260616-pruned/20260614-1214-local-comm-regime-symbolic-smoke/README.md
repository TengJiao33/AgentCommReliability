# 20260614-1214-local-comm-regime-symbolic-smoke

## What We Tried

Ran the deterministic communication-regime harness as a CPU-only smoke check.

## Scope

- Method: CommunicationRegimeHarness
- Model: deterministic symbolic agents
- Dataset: generated toy regimes
- Seed: 7
- Samples: 4 per regime
- Comparison target: protocol differences across task regimes

## Resource Notes

- Machine: local Windows workspace
- GPU IDs: none
- Timeout: none
- Started by: Codex

## Code

- Upstream repo: local project harness
- Commit: local working tree
- Local changes: `harness/communication_regimes.py`

## Environment

- Env path: local default Python
- Backend: CPU-only Python standard library

## Data

- Data path: generated in memory
- Regimes: `recall, state_tracking, k_hop, conflict_evidence, saturated_arithmetic`
- Sampling: deterministic seed `7`

## Command

```bash
python harness/communication_regimes.py --run-id 20260614-1214-local-comm-regime-symbolic-smoke --out-dir experiments\_archive\20260616-pruned\20260614-1214-local-comm-regime-symbolic-smoke --samples-per-regime 4 --seed 7
```

## Outputs

- Records: `communication_regime_records.jsonl`
- Summary: `summary.json`
- Manifest: `manifest.json`

## Result

| Regime | Protocol | Correct | Accuracy | Avg Total Tokens | Avg Communication Tokens | Changed vs Independent |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| conflict_evidence | evidence_state | 4/4 | 1.00 | 84.0 | 15.0 | 4 |
| conflict_evidence | full_broadcast | 4/4 | 1.00 | 84.0 | 15.0 | 4 |
| conflict_evidence | independent_majority | 0/4 | 0.00 | 39.0 | 0.0 | 0 |
| conflict_evidence | route_or_silence | 4/4 | 1.00 | 84.0 | 15.0 | 4 |
| conflict_evidence | single_agent | 0/4 | 0.00 | 29.0 | 0.0 | 0 |
| k_hop | evidence_state | 4/4 | 1.00 | 85.0 | 10.0 | 4 |
| k_hop | full_broadcast | 4/4 | 1.00 | 105.0 | 15.0 | 4 |
| k_hop | independent_majority | 0/4 | 0.00 | 60.0 | 0.0 | 0 |
| k_hop | route_or_silence | 4/4 | 1.00 | 90.0 | 10.0 | 4 |
| k_hop | single_agent | 0/4 | 0.00 | 53.0 | 0.0 | 0 |
| recall | evidence_state | 4/4 | 1.00 | 50.0 | 5.0 | 4 |
| recall | full_broadcast | 4/4 | 1.00 | 90.0 | 15.0 | 4 |
| recall | independent_majority | 0/4 | 0.00 | 45.0 | 0.0 | 0 |
| recall | route_or_silence | 4/4 | 1.00 | 60.0 | 5.0 | 4 |
| recall | single_agent | 0/4 | 0.00 | 35.0 | 0.0 | 0 |
| saturated_arithmetic | evidence_state | 4/4 | 1.00 | 78.0 | 15.0 | 0 |
| saturated_arithmetic | full_broadcast | 4/4 | 1.00 | 78.0 | 15.0 | 0 |
| saturated_arithmetic | independent_majority | 4/4 | 1.00 | 33.0 | 0.0 | 0 |
| saturated_arithmetic | route_or_silence | 4/4 | 1.00 | 33.0 | 0.0 | 0 |
| saturated_arithmetic | single_agent | 4/4 | 1.00 | 23.0 | 0.0 | 0 |
| state_tracking | evidence_state | 4/4 | 1.00 | 119.0 | 20.0 | 4 |
| state_tracking | full_broadcast | 4/4 | 1.00 | 119.0 | 20.0 | 4 |
| state_tracking | independent_majority | 0/4 | 0.00 | 59.0 | 0.0 | 0 |
| state_tracking | route_or_silence | 4/4 | 1.00 | 119.0 | 20.0 | 4 |
| state_tracking | single_agent | 0/4 | 0.00 | 50.0 | 0.0 | 0 |

## Notes

- This is a contact harness, not benchmark evidence.
- `evidence_state` and `route_or_silence` use oracle relevance so we can inspect the communication variable before adding model noise.
- `context_events` are populated for every record. Later v1.1 real-trace re-extractions also populate derived context events where masks, retention events, or ISM sidecars expose enough structure.
- First smoke exposed a duplicate-fact issue in `route_or_silence` for `state_tracking`; the harness now de-duplicates recipient facts before solving.
- A validation check confirmed 100 records, schema `acr.comm_trace.v1.1`, 3 context events per record, and the expected regime/protocol correctness pattern.

## Status Timeline

- `2026-06-14T12:14:32`: launched
- `2026-06-14T12:14:32`: completed

## Caveats

- Symbolic agents are not LLM agents.
- Token counts are rough word-count proxies.
- This run is useful for schema pressure and regime separation, not method superiority.

## Loose Threads

- Add a non-oracle router later, or map one real baseline trace into the same regime labels.
- Decide whether the next model run should target k-hop/conflict evidence rather than saturated arithmetic.
