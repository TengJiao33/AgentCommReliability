# Harness

This folder holds lightweight wrappers for controlled multi-agent communication experiments.

Harness goals:

- normalize logs across baselines;
- keep model/task/agent/round/message settings explicit;
- make communication modes easy to compare;
- avoid hidden global state and unrecorded prompt changes.

Initial communication modes:

- `none`
- `full`
- `masked`
- `compressed`
- `answer_only`
- `evidence_only`

## Communication Regimes

`communication_regimes.py` is a CPU-only deterministic toy harness. It is not a model benchmark. It exists so the project can touch task regimes and public-state surfaces before spending GPU time.

It generates small distributed-evidence instances for:

- `recall`
- `state_tracking`
- `k_hop`
- `conflict_evidence`
- `saturated_arithmetic`

It compares:

- `single_agent`
- `independent_majority`
- `full_broadcast`
- `evidence_state`
- `route_or_silence`

Example:

```bash
python harness/communication_regimes.py \
  --run-id 20260614-local-comm-regime-symbolic-smoke \
  --out-dir experiments/20260614-local-comm-regime-symbolic-smoke \
  --samples-per-regime 4 \
  --seed 7
```

Outputs:

- `communication_regime_records.jsonl`
- `summary.json`
- `manifest.json`
- `README.md`

The records use `acr.comm_trace.v1.1` and populate `task_regime`, `public_state`, `communication_events`, and `context_events`.
