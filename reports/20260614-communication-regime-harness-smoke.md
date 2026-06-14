# Communication-Regime Harness Smoke

## What We Tried

Implemented and ran a deterministic CPU-only harness for small distributed-evidence communication regimes.

This is the first concrete step after the M2CL/code-contact pressure: instead of adding another DAR message-surface variant, we created a small runnable object that can represent task regime, public state, routing/silence, and recipient context.

## What Happened

- code: `harness/communication_regimes.py`
- run: `experiments/20260614-1214-local-comm-regime-symbolic-smoke/`
- records: 100 JSONL rows
- schema: `acr.comm_trace.v1.1`
- regimes: `recall`, `state_tracking`, `k_hop`, `conflict_evidence`, `saturated_arithmetic`
- protocols: `single_agent`, `independent_majority`, `full_broadcast`, `evidence_state`, `route_or_silence`

Validation passed:

- all 100 rows use schema `acr.comm_trace.v1.1`;
- every row has 3 `context_events`;
- distributed regimes are wrong under `independent_majority` and correct under `evidence_state` / `route_or_silence`;
- saturated arithmetic is already correct under no-communication settings.

## Things Noticed

The harness makes the current framing concrete.

On the toy distributed regimes, communication changes final correctness:

- `recall`: one agent has the answer, others have distractors;
- `state_tracking`: each agent has part of the ordered update sequence;
- `k_hop`: the answer requires chaining facts across agents;
- `conflict_evidence`: the majority label is wrong but high-confidence evidence is correct.

On `saturated_arithmetic`, communication does not change correctness and only adds token cost unless the protocol stays silent.

This is not surprising, and that is the point. The harness makes the regime distinction explicit enough that future model runs can be chosen against it rather than hidden inside another prompt-surface ablation.

## Failures / Friction

The first smoke exposed a small implementation bug: `route_or_silence` concatenated an agent's private facts with routed public facts without de-duplication. In `state_tracking`, this duplicated an operation and produced a wrong final state.

Fix:

- added `unique_facts`;
- reran the same smoke;
- `route_or_silence` on `state_tracking` became `4/4`.

This is a useful warning for real systems: public-state routing needs recipient-context hygiene, not only fact selection.

## Caveats

- Symbolic agents are not LLM agents.
- `evidence_state` and `route_or_silence` use oracle relevance.
- Token counts are rough word-count proxies.
- The run is schema/contact evidence, not method evidence.

## Loose Threads

- Add a non-oracle router or confidence-based selector.
- Map one existing real trace into `task_regime` / `public_state` labels.
- Use a k-hop or conflict-evidence task for the next model run rather than saturated GSM8K-style arithmetic.
