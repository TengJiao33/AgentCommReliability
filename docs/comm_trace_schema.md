# Communication Trace Schema

`scripts/extract_comm_trace_schema.py` normalizes DAR, MAD-MM, MOC, and PACT outputs into JSONL using schema version `acr.comm_trace.v1.1`.

Each line is one problem instance for one method/run.

## Core Fields

- `run_id`, `method_family`, `method`
- `instance_id`, `sample_index`, `question`, `gold_answer`
- `task_regime`: optional manual label such as `recall`, `state_tracking`, `k_hop`, `conflict_evidence`, or `saturated_arithmetic`
- `public_state`: optional manual labels for transmitted state surface and communication policy
- `final`: final answer and correctness
- `transition`: `right_to_wrong`, `wrong_to_right`, `stable_right`, `stable_wrong`, or `unknown`
- `rounds`: per-round agent answers, correctness, confidence when available, and token stats when available
- `retention_events`: retained/dropped/merged agent IDs when the source exposes them
- `communication_events`: structural merge or other communication events
- `context_events`: generated or assigned recipient context states when the source exposes them
- `token_cost`: input/output/total tokens plus compressed-token counters when available
- `method_comparison`: optional baseline comparison, currently used by MAD-MM against COT
- `source`: raw file paths used to build the record

Missing source data is represented as `null`, not omitted.

Schema version `acr.comm_trace.v1.1` adds regime/context slots after the M2CL code-contact check. Current MAD-MM, DAR, and MOC v1.1 traces may include derived `context_events` from masks, retention events, or MOC ISM sidecars. These are recipient-context proxies, not raw prompt-level generated context.

Gold-answer handling is method-aware. Arithmetic-oriented extractors keep the
older numeric normalization behavior, while PACT preserves HotpotQA gold answers
as text so span/date answers such as `1969 until 1974` are not collapsed to the
last number.

## Commands

MAD-MM:

```bash
python scripts/extract_comm_trace_schema.py madmm \
  --run-id 20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset \
  --results-dir /data/xuhaoming/yfy/research_workspace/results/mad-mm-short-subset/main/qwen2.5-14b/gsm8k \
  --task-regime saturated_arithmetic \
  --public-state-surface full_reasoning \
  --communication-policy broadcast_or_mask \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-14b-gsm8k-short-subset.comm_trace.jsonl
```

Verified MAD-MM MATH50 probe:

```bash
python scripts/extract_comm_trace_schema.py madmm \
  --run-id 20260613-1855-a8002-madmm-qwen25-7b-math50-probe \
  --results-dir /data/xuhaoming/yfy/research_workspace/results/mad-mm-benchmark-probe/math_probe50/qwen2.5-7b/math \
  --methods cot mad_naive mad_objective mad_subjective \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-7b-math50-probe.comm_trace.jsonl
```

DAR:

```bash
python scripts/extract_comm_trace_schema.py dar \
  --run-id 20260612-a8002-dar-qwen25-7b-gsm8k-filtercritical-short \
  --method filter_critical \
  --history-jsonl /data/xuhaoming/yfy/research_workspace/results/dar-short-filtercritical-qwen25-7b-gsm8k100-20260612_193240/out/history/gsm8k_100__qwen2.5-7b_N=3_R=1_P=True_V=True_K=None_M=filter_critical_S=42.jsonl \
  --task-regime saturated_arithmetic \
  --public-state-surface retained_full_reasoning \
  --communication-policy retained_subset \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-qwen25-7b-gsm8k-filtercritical-short.comm_trace.jsonl
```

Future DAR runs with `baselines/DAR/patches/a8002-filter-retention-history.patch` should include `retention_events` in each filtered round. The extractor reads those events when present; older histories leave retention fields empty.

If `baselines/DAR/patches/a8002-guarded-answer-diversity.patch` is also applied, DAR `retention_events` can additionally include `original_retained_agent_ids`, `guard_mode`, `guard_added_agent_ids`, `guard_removed_agent_ids`, `guard_notes`, `guard_parseable_buckets`, `guard_missing_parseable_buckets`, and `retention_message_mode`.

Verified instrumented DAR check:

```bash
python scripts/extract_comm_trace_schema.py dar \
  --run-id 20260613-1721-a8002-dar-trace-filtercritical-gsm8k5 \
  --method filter_critical \
  --history-jsonl /data/xuhaoming/yfy/research_workspace/results/dar-trace-check-filtercritical-gsm8k5-20260613_1721/out/history/gsm8k_5__qwen2.5-7b_N=3_R=1_P=True_V=True_K=None_M=filter_critical_S=42.jsonl \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-trace-filtercritical-gsm8k5.comm_trace.jsonl
```

MOC:

```bash
python scripts/extract_comm_trace_schema.py moc \
  --run-id 20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke \
  --detail-json /data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_2026-06-13-14-21-39_detail.json \
  --summary-json /data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b_Chain_2026-06-13-14-21-39.json \
  --log-path /data/xuhaoming/yfy/research_workspace/logs/moc-forcedmerge-chain5-hop2-n5-20260613_1425_forcedmerge8192.log \
  --task-regime saturated_arithmetic \
  --public-state-surface compressed_summary \
  --communication-policy topology_merge \
  --out /data/xuhaoming/yfy/research_workspace/experiments/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/comm_trace_moc.jsonl
```

Future MOC runs with `baselines/MOC/patches/a8002-comm-trace-events.patch` should set `MOC_COMM_TRACE_JSONL` during the run and pass it back into extraction:

```bash
python scripts/extract_comm_trace_schema.py moc \
  --run-id <run-id> \
  --detail-json <detail.json> \
  --summary-json <summary.json> \
  --comm-events-jsonl <moc_comm_events.jsonl> \
  --out <comm_trace.jsonl>
```

Verified instrumented MOC check:

```bash
python scripts/extract_comm_trace_schema.py moc \
  --run-id 20260613-1718-a8002-moc-trace-instrumentation-n1 \
  --detail-json /data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b-trace_2026-06-13-17-19-41_detail.json \
  --summary-json /data/xuhaoming/yfy/research_workspace/baselines/MOC/result/gsm8k/vllm:qwen2.5-7b-trace_Chain_2026-06-13-17-19-41.json \
  --comm-events-jsonl /data/xuhaoming/yfy/research_workspace/results/moc-trace-check-20260613_1718/moc_comm_events.jsonl \
  --out /data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-trace-instrumentation-n1.comm_trace.jsonl
```

PACT:

```bash
python scripts/extract_comm_trace_schema.py pact \
  --run-id 20260614-1100-a8002-pact-qwen25-14b-hotpot50-v11 \
  --result-jsonl experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/pact_qwen25_14b_hotpot50.jsonl \
  --method pact_action_state \
  --task-regime split_evidence_qa \
  --public-state-surface action_state \
  --communication-policy alternating_action_state \
  --out experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl
```

## Current Verified Outputs

| Method family | Rows | Output |
| --- | ---: | --- |
| MOC | 5 | `/data/xuhaoming/yfy/research_workspace/experiments/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/comm_trace_moc.jsonl` |
| MOC instrumented | 1 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-trace-instrumentation-n1.comm_trace.jsonl` |
| MOC hop1 instrumented | 5 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-hopcheck-hop1-n5.comm_trace.jsonl` |
| MOC hop2 instrumented | 5 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-hopcheck-hop2-n5.comm_trace.jsonl` |
| MAD-MM | 400 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-14b-gsm8k-short-subset.comm_trace.jsonl` |
| MAD-MM MATH probe | 200 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-7b-math50-probe.comm_trace.jsonl` |
| MAD-MM benchmark sweep MATH50 | 150 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-math-50.comm_trace.jsonl` |
| MAD-MM benchmark sweep MMLU-Pro50 | 150 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-mmlu_pro-50.comm_trace.jsonl` |
| MAD-MM benchmark sweep AIME24 | 90 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-aime24-all.comm_trace.jsonl` |
| MAD-MM benchmark sweep AIME25 | 90 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-aime25-all.comm_trace.jsonl` |
| DAR | 10 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-qwen25-7b-gsm8k-filtercritical-short.comm_trace.jsonl` |
| DAR instrumented | 5 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-trace-filtercritical-gsm8k5.comm_trace.jsonl` |
| DAR full-history instrumented | 100 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-trace-filtercritical-gsm8k100-fullhistory.comm_trace.jsonl` |
| DAR guarded answer-only | 100 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-guarded-answer-diversity-gsm8k100-20260613_2038.comm_trace.jsonl` |
| DAR answer-only no guard | 100 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-answer-only-noguard-gsm8k100-20260613_2143.comm_trace.jsonl` |
| DAR guard full | 100 | `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-guard-full-gsm8k100-20260613_2143.comm_trace.jsonl` |
| CommunicationRegimeHarness | 100 | `experiments/20260614-1214-local-comm-regime-symbolic-smoke/communication_regime_records.jsonl` |
| MOCRoleCompressionProbe | 30 | `experiments/20260614-1832-local-moc-role-sensitive-split-evidence-probe/comm_trace_moc_role_probe_v11.jsonl` |
| MOCMergePromptRoleAudit | 60 | `experiments/20260614-1913-a8002-moc-merge-prompt-role-audit/comm_trace_moc_merge_prompt_role_audit_v11.jsonl` |
| DAR original v1.1 labels | 100 | `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar_v11.jsonl` |
| DAR guarded answer-only v1.1 labels | 100 | `experiments/20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100/comm_trace_dar_guarded_v11.jsonl` |
| DAR answer-only no-guard v1.1 labels | 100 | `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_answer_only_noguard_v11.jsonl` |
| DAR guard-full v1.1 labels | 100 | `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_guard_full_v11.jsonl` |
| MOC hop1 v1.1 labels | 5 | `experiments/20260613-1740-a8002-moc-hopcheck-n5/comm_trace_hop1_v11.jsonl` |
| MOC hop2 v1.1 labels | 5 | `experiments/20260613-1740-a8002-moc-hopcheck-n5/comm_trace_hop2_v11.jsonl` |
| MAD-MM MATH50 v1.1 labels | 200 | `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/comm_trace_madmm_math50_v11.jsonl` |
| PACT HotpotQA50 v1.1 labels | 50 | `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl` |

The older DAR trace has only 10 rows because that run saved only the first 10 histories. The instrumented DAR check confirms full-history saving and per-round retention events.

## Current Limits

- Older MOC detail JSON lacks per-agent round traces and per-sample merge source IDs, so pre-instrumentation MOC records include run-level merge counts parsed from logs. Instrumented MOC runs should pass `--comm-events-jsonl`.
- Older DAR history lacks retained/dropped IDs for `filter_critical`, so pre-instrumentation DAR retention fields are `null`. Instrumented DAR runs should use `--save_full_history`.
- MAD-MM exposes masks directly, so retained/dropped IDs and right/wrong retention counts are available.
- MAD-MM aggregate accuracy should still be read from the upstream result JSONs. The unified trace normalizer now compares textual labels case-insensitively, which is required for MMLU-Pro lower-case predictions against upper-case gold labels.
- `task_regime`, `public_state.surface`, and `public_state.communication_policy` are manual labels for now. They should be used sparingly and only when the run note makes the label obvious.
- MAD-MM extraction auto-fills per-method public-state labels when no explicit public-state arguments are passed: `cot` -> no communication, `mad_naive` -> full-reasoning broadcast, `mad_objective` -> objective memory mask, and `mad_subjective` -> subjective memory mask.
- Current MAD-MM, DAR, and MOC v1.1 traces may include derived `context_events` from masks, retention events, or MOC ISM sidecars. These derived events identify visible/suppressed source agents or represented merge sources, but they are not raw prompt logs.
- `MOCRoleCompressionProbe` is a synthetic CPU-only contact artifact, not an extractor over upstream MOC output. It uses the same schema shape to stress role-slot preservation under compressed multi-hop public-state surfaces.
- `MOCMergePromptRoleAudit` is a merge-prompt-only LLM audit over synthetic role cases. It calls OpenAI-compatible chat completions with MOC-style merge prompts, but it does not run the MOC graph, ISM pair selection, or embedding-based strategy selection.
- PACT v1.1 traces include action-state `communication_events` for every agent turn and derived `context_events` for non-final turns appended to shared history. The local Qwen2.5-14B run emitted no `<think>` spans, so it does not stress the private-reasoning stripping path.
- Future PACT offset runs can preserve original HotpotQA sample indices when the upstream JSONL includes `sample_index`; older PACT JSONL files without that field still fall back to row order.
- Prompt-level or generated recipient context is still reserved for systems like M2CL or future instrumentation that explicitly records it.
