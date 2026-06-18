# PerspectiveGap Hard Routing Smoke4 PromptV2 Qwen2.5-7B

## Status

Diagnostic smoke completed. Do not scale this exact setup to stratified20/full220 yet.

## Purpose

Test the corrected hard-card prompt contract after the first smoke showed ambiguity in `rejected` and `visibility`.

## Preflight

- Unit: one PerspectiveGap hard-routing evaluation row.
- Scope: `4` rows from `pg_000` and `pg_002`, seeds `1` and `42`.
- Primary readout: whether direct hard-card prompting produces parseable state cards with nonzero reject behavior while preserving coverage and budget.
- Success signal: parseable `4/4`, nonzero strict or visibly improved coverage over legacy projection, high reject recall without rejecting needed fragments, and non-collapsed visibility labels.
- Failure signal: parse errors, continued needed-fragment rejection, or visibility labels dominated by a default label.
- Invalidation guard: this is a 4-row smoke on one local 7B model.

## Run

- Remote host: `A800_2`
- Remote workspace: `/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Served model: `qwen2.5-7b-perspectivegap-hard-smoke4`
- GPU: `7`
- Port: `8065`
- Packet: `experiments/20260618-local-perspectivegap-hard-routing-v0/hard_packet_smoke4_promptv2.jsonl`
- Rows: `4`
- Temperature: `0`
- Max tokens: `1536`
- Runner: `scripts/run_perspectivegap_hard_routing_openai_compatible.py`
- Scorer: `scripts/score_perspectivegap_hard_routing.py`
- Launch script: `scripts/run_perspectivegap_hard_routing_smoke_a8002.sh`

Remote command:

```bash
WORKSPACE=/data/xuhaoming/yfy/research_workspace \
GPU_ID=7 \
PORT=8065 \
RUN_ID=20260618-a8002-perspectivegap-hard-routing-smoke4-promptv2-qwen25-7b \
PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-perspectivegap-hard-routing-v0/hard_packet_smoke4_promptv2.jsonl \
bash scripts/run_perspectivegap_hard_routing_smoke_a8002.sh
```

GPU 7 was clean before launch and returned to `4 MB` used after cleanup. No vLLM process remained.

## Results

| Condition | Strict | Coverage | Precision | Leak/eval | Budget pass | Source acc | Visibility acc | Reject recall | Needed rejected |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| direct hard-card promptv2 | 0/4 | 0.433 | 0.929 | 0.000 | 1.000 | 1.000 | 0.154 | 0.750 | 1.250 |
| legacy Qwen2.5-7B projection | 0/4 | 0.500 | 0.577 | 0.250 | 0.500 | 1.000 | 1.000 | 0.000 | 0.000 |

One direct hard-card output was malformed JSON: `pg_002__seed_1` has a nested object inside `rejected`, so the scorer treated that row as parse failure.

## Diagnosis

The corrected prompt changes the failure shape but does not make the setup scale-ready. Direct hard-card prompting improves boundary behavior compared with legacy projection: no distractor leakage, full budget pass, and perfect source copy on true positives. The cost is recall: coverage falls to `0.433`, and the model still rejects needed fragments.

The strongest live signal is recipient-scope confusion. The model often assigns `shared_all` to role-private fragments, even after the prompt explicitly defines `shared_all`, `shared_subset`, and `role_private`.

## Next Check

Before running stratified20/full220, add a parser gate and split the task into two arms:

- a guided/strict JSON output arm to remove malformed JSON as a confound;
- a two-stage routing arm where the model first selects role-fragment edges, then labels visibility for selected fragments.

If recipient-scope errors survive those gates, source perturbation becomes a cleaner mechanism test than more prompt tuning.
