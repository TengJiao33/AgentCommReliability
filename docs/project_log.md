# Project Log

## 2026-06-12

- Created local project at `D:\develop\AgentCommReliability`.
- Established initial documentation:
  - README;
  - project intake;
  - machine handbook;
  - experiment protocol;
  - reading queue;
  - mentor/senior sync drafts.
- Distilled compute rules from `D:\develop\RA-Internship-Tasks`.
- Connected project direction to `D:\develop\ArXiv_Daily_Digest`.

Next:

- Pick first baseline, likely MAD-M2 if code/environment is manageable.
- Create `papers/cards/` and write first paper card.
- Decide whether first smoke run can happen locally or should use `A800_2`.

## 2026-06-12 MAD-MM Standard Reproduction Setup

- Selected MAD-MM as the first standard reproduction target.
- Prepared A800_2 workspace under `/data/xuhaoming/yfy/research_workspace`.
- Synced upstream MAD-MM commit `f02069add08280b764d059a2f06ca0043aa093e2`.
- Created project-local env `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`.
- Verified core versions: vLLM 0.6.3, PyTorch 2.4.0+cu121, Transformers 4.46.2, Datasets 3.1.0.
- Added local model-path config for Qwen2.5 7B/14B/32B/72B and environment-variable overrides for GPU/result paths.
- Found Qwen2.5-14B and Qwen2.5-72B complete under `/mnt/quarkfs/share_model`.
- Found Qwen2.5-32B incomplete under `/mnt/quarkfs/share_model/Qwen2.5-32B-Instruct`; HF was unreachable from A800_2, so completed it through ModelScope.
- Launched standard main reproduction in tmux session `madmm_standard_main`.
- Main log: `/data/xuhaoming/yfy/research_workspace/logs/madmm_standard_main_20260612_143417.log`.
- First observed result: `qwen2.5-14b/gsm8k/cot_seed41`.
- Stopped `madmm_standard_main` shortly after launch because the estimated full run would occupy shared GPUs too long. GPUs 2-5 were released.
- Run note: `experiments/20260612-1403-a8002-madmm-qwen25-standard-main/README.md`.
- Prepared a bounded short subset launcher using one GPU only: `/data/xuhaoming/yfy/research_workspace/scripts/run_madmm_short_subset_a8002.sh`.
- Short subset note: `experiments/20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset/README.md`.
- Completed short-subset CoT on `qwen2.5-14b/gsm8k`, seed `41`, 100 samples: accuracy `0.94`, total tokens `37990`.
- Completed short-subset MAD naive communication on the same setup: accuracy `0.96`, total tokens `441846`.
- Completed short-subset MAD-MM objective masking on the same setup: accuracy `0.95`, total tokens `304287`.
- Completed short-subset MAD-MM subjective masking on the same setup: accuracy `0.96`, total tokens `600499`.
- Current evidence is short-subset evidence only; next useful work is trace-level case analysis before launching more GPU jobs.
- Added first insight report: `reports/20260612-madmm-short-subset-first-insights.md`.
- Downloaded MAD-MM arXiv PDF to `papers/mad-mm/2603.20215.pdf`.
- Added paper card: `papers/cards/mad-mm.md`.
- Expanded MAD-MM paper card with method, masking strategies, experimental setup, main findings, and how the paper maps to our short-subset results.
- Pulled `D:\develop\ArXiv_Daily_Digest` with `git pull --ff-only`; fast-forwarded to commit `8f754e1`.
- Scanned `multi-agent-consistency`, `agent-skills-harness`, and `agent-policy-optimization` for 2026-W23/W24 multi-agent candidates.
- Added frontier scan report: `reports/20260612-multi-agent-frontier-scan.md`.
- Updated reading queue with P0 follow-ups: MOC, SMADE-IE, Dynamic Coordination Strategy Selection, and Monitoring Agentic Systems Before They're Reliable.
- Reorganized the documentation system around objective evidence:
  - added `docs/documentation_system.md`;
  - added `docs/README.md`;
  - added `docs/research_map.md`;
  - added `docs/evidence_register.md`;
  - added `papers/cards/_template.md`;
  - added `baselines/_templates/source.md` and `baselines/_templates/reproduction.md`;
  - added `reports/_templates/objective_research_report.md`;
  - updated README, reports README, experiments README, experiment protocol, and reproduction recording standard to point to the new structure.
- Copied MAD-MM short-subset raw result JSONs from A800_2 to local ignored `raw_results/` for trace inspection only.
- Added `scripts/extract_madmm_trace_cases.py` and generated `trace_cases_summary.json`.
- Added trace-level report: `reports/20260612-madmm-trace-message-retention.md`.
- Trace inspection found that objective masking selected only wrong memory in cases `214` and `1227`; subjective masking also dropped the only correct first-round memory in `1227`.
- Selected DAR / Diversity-Aware Retention as the next candidate to inspect because its code exposes an explicit disagreement-oriented retention rule.
- Added DAR paper card and baseline notes.
- Cloned DAR on A800_2 at commit `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`.
- Applied documented remote patches for local Qwen paths, escaped-brace arithmetic parsing, and output directory placement.
- Completed DAR smoke checks:
  - Qwen2.5-1.5B non-Instruct smoke completed but produced invalid outputs.
  - Qwen2.5-7B-Instruct basic smoke completed on 2 arithmetics samples.
  - Qwen2.5-7B-Instruct `filter_critical` smoke completed on 2 arithmetics samples and wrote retained-ID token logs.
- Added DAR smoke run record: `experiments/20260612-a8002-dar-qwen25-7b-arithmetics-smoke/`.
- Completed DAR 100-sample arithmetics short matrix on A800_2 with Qwen2.5-7B-Instruct:
  - Basic MAD: round accuracies `[0.99, 0.98]`.
  - Top-K uncertainty `0.5`: round accuracies `[0.97, 0.94]`.
  - DAR `filter_critical`: round accuracies `[0.99, 0.99]`.
- Added DAR short matrix run record: `experiments/20260612-a8002-dar-qwen25-7b-arithmetics-short-matrix/`.
- Added short matrix report: `reports/20260612-dar-arithmetics-short-matrix.md`.
- Started DAR GSM8K continuation preflight:
  - A800_2 reachable as `10-116-90-20`.
  - GPU 4 was observed mostly free.
  - DAR remote checkout remained at commit `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0` with documented local patches for model paths, parser compatibility, and output paths.
  - Data-only GSM8K smoke failed because A800_2 could not reach `huggingface.co` and no `openai/gsm8k` dataset cache entry existed.
  - Confirmed MAD-MM processed GSM8K test JSONL exists remotely at `/data/xuhaoming/yfy/research_workspace/baselines/MAD-MM/processed_data/gsm8k/gsm8k_test.jsonl`; this is the likely offline fallback for DAR GSM8K reproduction.
- Added project skill `skills/repro-friction-memory/SKILL.md` to record small solved reproduction blockers and reusable prevention rules.
- Updated `skills/reproduction-first-research/SKILL.md`, root `README.md`, and `docs/README.md` to point to the new friction-memory skill.
- Added DAR GSM8K offline JSONL fallback patch: `baselines/DAR/patches/a8002-gsm8k-local-jsonl-fallback.patch`.
- Completed DAR GSM8K 2-sample smoke on A800_2 with Qwen2.5-7B-Instruct:
  - Basic MAD: round accuracies `[1.0, 1.0]`.
  - DAR `filter_critical`: round accuracies `[1.0, 0.5]`.
- Added launcher `scripts/run_dar_gsm8k_short_matrix_a8002.sh` and synced it to A800_2.
- Completed DAR 100-sample GSM8K short matrix on A800_2 with Qwen2.5-7B-Instruct:
  - Basic MAD: round accuracies `[0.95, 0.95]`.
  - Top-K uncertainty `0.5`: round accuracies `[0.95, 0.94]`.
  - DAR `filter_critical`: round accuracies `[0.95, 0.93]`.
  - `filter_critical` retained-ID distribution: 1 retained ID for 64 samples, 2 for 27 samples, 3 for 9 samples.
  - `filter_critical` filter-token total: `113,657`.
- Added DAR GSM8K short matrix run record: `experiments/20260612-a8002-dar-qwen25-7b-gsm8k-short-matrix/`.
- Added short matrix report: `reports/20260612-dar-gsm8k-short-matrix.md`.

## 2026-06-13 MOC Smoke Reproduction

- Selected MOC as the next reproduction target because it directly exposes topology, hop depth, and message consolidation as communication variables.
- Confirmed upstream paper/code:
  - arXiv: `https://arxiv.org/abs/2606.02359`
  - repo: `https://github.com/yao-guan/MOC`
  - inspected commit: `9c67c92507570704a7df73e452552a3f49e83897`
- Remote `git clone` on A800_2 failed with HTTP/2 framing errors, so the source was cloned locally and transferred to A800_2 via `git archive`.
- Installed minimal missing packages into the project env `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063` rather than installing the full heavy upstream requirements.
- Added and applied MOC environment/backend patches:
  - `baselines/MOC/patches/a8002-smoke-embedding-fallback.patch`
  - `baselines/MOC/patches/a8002-vllm-openai-adapter.patch`
- Started temporary vLLM server on A800_2 GPU 1 for `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`; stopped it after the run and confirmed GPU 1 was released.
- Completed 1-sample GSM8K smoke:
  - Chain, 2 agents, 1 round, Qwen2.5-7B-Instruct: accuracy `1/1`, total tokens `2,991`, runtime `9.187s`.
- Completed 5-sample GSM8K topology smoke:
  - Chain: accuracy `5/5`, total tokens `14,529`, runtime `34.474s`.
  - FullConnected: accuracy `5/5`, total tokens `14,042`, runtime `26.863s`.
  - Random: accuracy `5/5`, total tokens `13,967`, runtime `26.208s`.
- Added MOC baseline notes, paper card, run record, and report:
  - `papers/cards/moc.md`
  - `baselines/MOC/source.md`
  - `baselines/MOC/reproduction.md`
  - `experiments/20260613-a8002-moc-qwen25-7b-gsm8k-topology5/`
  - `reports/20260613-moc-gsm8k-topology-smoke.md`
- Caveat: this is setup/topology smoke evidence only. The run used `neighbor_hops=1`, hash embeddings, and did not trigger structural message consolidation.
- Next useful check: adapt `merge_multiple_messages` away from hard-coded Ollama and run a forced-merge `neighbor_hops=2` smoke.

## 2026-06-13 MOC Forced Merge And Unified Trace

- Added MOC structural merge patch:
  - `baselines/MOC/patches/a8002-vllm-structural-merge.patch`
  - routes `Graph.merge_multiple_messages` through the configured `LLMRegistry` / `VLLMChat` instead of hard-coded Ollama `gemma2:9b`.
  - moves merge-call vLLM usage into MOC compressed-token counters.
- Applied the patch on A800_2 and verified `src/graph/graph.py` with `py_compile`.
- Started vLLM on GPU 1. The first 4096-context service reached the structural merge branch but failed at final decision because the merged prompt exceeded the context budget.
- Restarted vLLM with `--max-model-len 8192`.
- Completed MOC forced-merge smoke:
  - run record: `experiments/20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke/`
  - setting: GSM8K, `Chain`, 5 agents, `neighbor_hops=2`, `ism_r=0`, `ism_kppa=45`.
  - n=1 preflight: accuracy `1/1`, total tokens `5,894`, compressed tokens `13,846`.
  - n=5 run: accuracy `5/5`, total tokens `22,718`, compressed tokens `50,906`.
  - n=5 log showed 15 merged pairs and 75 summary-strategy calls.
- Stopped the vLLM service and confirmed GPU 1 was released.
- Added unified communication trace extractor:
  - `scripts/extract_comm_trace_schema.py`
  - docs: `docs/comm_trace_schema.md`
- Verified the extractor on real outputs:
  - MOC forced merge: 5 JSONL rows.
  - MAD-MM short subset: 400 JSONL rows; baseline comparison against COT includes `wrong_to_right=6` and `right_to_wrong=1`.
  - DAR filter-critical GSM8K history: 10 JSONL rows; limited by the saved first-10 histories, with 1 observed `right_to_wrong`.
- Added short report: `reports/20260613-moc-forced-merge-smoke.md`.

## 2026-06-13 RuleArena Benchmark Pressure Setup

- Added RuleArena as a portable project submodule at `baselines/RuleArena/upstream` instead of relying on a machine-local clone.
- Pinned upstream commit `3b9e2256294644beca66732babc5e1055855a576`.
- Added baseline notes:
  - `baselines/RuleArena/README.md`
  - `baselines/RuleArena/source.md`
  - `baselines/RuleArena/reproduction.md`
- Added CPU-only loader smoke script:
  - `scripts/rulearena_loader_smoke.py`
- Loader smoke passed locally without model calls:
  - airline: `100/100/100` examples for complexity `0/1/2`
  - NBA: `81/89/46` examples for complexity `0/1/2`
  - tax: `100/100/100` examples for complexity `0/1/2`
- Next useful check: create a small-run wrapper with `--limit` and OpenAI-compatible vLLM support before launching any model evaluation.
- Kept benchmark-pressure guidance in the root README/current focus instead of maintaining a separate planning document.

## 2026-06-13 Documentation Simplification

- Simplified the active documentation surface around the top-level `reproduction-first-research` skill.
- Deleted redundant planning/process documents:
  - `docs/benchmark_pressure_suite.md` (briefly drafted, then folded into README/current focus)
  - `docs/documentation_system.md`
  - `docs/reproduction_recording_standard.md`
  - `docs/research_map.md`
- Kept factual and operational references:
  - `docs/machine_handbook.md`
  - `docs/server_resource_inventory.md`
  - `docs/machine_quickstart.md`
- Current rule: facts go into experiment notes or `docs/project_log.md`; durable claims go into `docs/evidence_register.md`; workflow decisions defer to `skills/reproduction-first-research/SKILL.md`.

## 2026-06-13 Open-Ended Reproduction Posture

- Corrected the project posture away from a narrowed current loop, benchmark-pressure framing, and forced idea production.
- Made `skills/reproduction-first-research/SKILL.md` the top-level posture document for open-ended reproduction rather than a workflow for turning reproductions into evidence-backed ideas.
- Updated the root `README.md` to state that the project does not need a narrowed research question, planned contribution, or current narrow loop before continuing.
- Updated `project_intake.md`, `docs/evidence_register.md`, report templates, and experiment notes guidance to preserve observations, failures, and loose threads without requiring every run to become a claim or next action.

## 2026-06-13 Trace Instrumentation Prep

- Verified the current local checkpoint:
  - `scripts/extract_comm_trace_schema.py`, `scripts/rulearena_loader_smoke.py`, `scripts/extract_madmm_trace_cases.py`, and `scripts/analyze_madmm_short_subset.py` pass `py_compile`.
  - `scripts/rulearena_loader_smoke.py --root baselines/RuleArena/upstream` still reads all RuleArena airline/NBA/tax files.
  - local MOC forced-merge detail/summary files still extract to communication trace JSONL.
- Added MOC trace instrumentation patch:
  - `baselines/MOC/patches/a8002-comm-trace-events.patch`
  - intended to write per-sample ISM sidecar events through `MOC_COMM_TRACE_JSONL`.
  - captures source IDs, merged IDs, retained direct IDs, dropped-direct IDs, merge similarity, and compressed-token deltas.
- Added DAR retention instrumentation patch:
  - `baselines/DAR/patches/a8002-filter-retention-history.patch`
  - writes per-round `retention_events` with candidate/retained/dropped IDs and raw filter response.
  - adds `--save_full_history` for non-debug full history output.
- Updated `scripts/extract_comm_trace_schema.py`:
  - MOC extractor accepts `--comm-events-jsonl`.
  - DAR extractor reads `retention_events` when present.
- Validation:
  - DAR instrumentation patch applies after `a8002-respect-out-dir.patch` on a clean upstream checkout and `src/dev.py` / `src/main.py` pass `py_compile`.
  - MOC instrumentation patch is prepared for the A800_2 MOC checkout after the existing vLLM structural-merge adaptation; local Windows `git apply` validation is noisy around old MOC patch context and should be repeated on the remote Linux checkout before rerunning.
- Next useful check: apply both instrumentation patches on A800_2 and run tiny MOC/DAR checks before any larger comparison.

## 2026-06-13 Trace Instrumentation Check

- Repaired `baselines/MOC/patches/a8002-comm-trace-events.patch` hunk counts so it is valid unified diff.
- Added `baselines/MAD-MM-patches/a8002-local-qwen-and-runtime-overrides.patch` to preserve the current MAD-MM submodule A800_2 local-path/runtime override changes from the parent repository.
- Updated `baselines/README.md` to document external patch placement for git submodules.
- Applied instrumentation patches on A800_2:
  - MOC: `a8002-comm-trace-events.patch`; applied with `git apply --ignore-whitespace --recount` because the transferred MOC source has CRLF line endings; `experiments/common.py` and `src/graph/graph.py` pass `py_compile`.
  - DAR: `a8002-filter-retention-history.patch`; `src/dev.py` and `src/main.py` pass `py_compile`.
- Started temporary MOC vLLM server on GPU 7, port `8027`, served as `qwen2.5-7b-trace`; stopped it after the MOC check and confirmed GPU 7 was released.
- Completed MOC trace instrumentation n=1 forced-merge check:
  - run record: `experiments/20260613-1718-a8002-trace-instrumentation-check/`
  - accuracy `1/1`, total tokens `5,822`, compressed tokens `13,602`.
  - sidecar `moc_comm_events.jsonl` has 7 events: 3 `ism_merge`, 4 `ism_result`.
  - unified trace has 1 row with 7 `communication_events`.
- Completed DAR `filter_critical` GSM8K5 full-history trace check:
  - round 0 accuracy `5/5`; round 1 accuracy `4/5`.
  - history JSONL has 5 rows, each with `retention_events`.
  - unified trace has 5 rows: 4 `stable_right`, 1 `right_to_wrong`.
  - the right-to-wrong sample retained Agent2 and Agent3 while dropping Agent1, shifting the debate answer from correct `200` to wrong `240`.
- Synced the latest `scripts/extract_comm_trace_schema.py` to A800_2 and extracted:
  - `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-trace-instrumentation-n1.comm_trace.jsonl`
  - `/data/xuhaoming/yfy/research_workspace/results/unified-traces/dar-trace-filtercritical-gsm8k5.comm_trace.jsonl`

## 2026-06-13 DAR Full-History And MOC Hop Trace Checks

- Reran DAR GSM8K 100-sample `filter_critical` with `--save_full_history` on A800_2 GPU 7:
  - run record: `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/`
  - round 0 accuracy `0.95`; round 1 accuracy `0.93`.
  - unified trace has 100 rows and 100 retention events.
  - transition counts: 92 `stable_right`, 3 `right_to_wrong`, 1 `wrong_to_right`, 4 `stable_wrong`.
  - retention-size distribution: 1 retained ID for 64 samples, 2 for 27, 3 for 9.
  - `filter_critical` dropped at least one correct first-round agent in 84 samples and all correct first-round agents in 13 samples.
  - filter-token total matched the earlier short matrix: `113,657`.
- Ran MOC n=5 hop-depth trace check on A800_2 GPU 7 with temporary vLLM port `8028`; stopped vLLM and confirmed GPU 7 was released:
  - run record: `experiments/20260613-1740-a8002-moc-hopcheck-n5/`
  - hop1: `5/5`, total tokens `20,977`, compressed tokens `0`, 20 `ism_result` events and no merge.
  - hop2 forced merge: `5/5`, total tokens `22,422`, compressed tokens `50,699`, 20 `ism_result` events and 15 `ism_merge` events.
  - unified traces:
    - `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-hopcheck-hop1-n5.comm_trace.jsonl`
    - `/data/xuhaoming/yfy/research_workspace/results/unified-traces/moc-hopcheck-hop2-n5.comm_trace.jsonl`

## 2026-06-13 MAD-MM MATH Benchmark Probe

- Added a MAD-MM sample-count override patch:
  - `baselines/MAD-MM-patches/a8002-sample-count-override.patch`
  - adds `--sample_count` to `src/args.py`;
  - routes `math`, `gsm8k`, and `mmlu_pro` default bounded sample counts through `args.sample_count or 100`.
- Added one-GPU MATH probe launcher:
  - `scripts/run_madmm_math_probe_a8002.sh`
- Applied the patch on A800_2 MAD-MM checkout and verified:
  - `chain_of_thoughts.py`, `multi_agent_debate.py`, and `src/args.py` pass `py_compile`.
- Ran MAD-MM on A800_2 GPU 7:
  - model: Qwen2.5-7B-Instruct
  - dataset: MATH
  - seed: 41
  - samples: 50
  - methods: CoT, MAD naive, MAD-MM objective masking
  - GPU 7 was released after completion.
- Results:
  - CoT: accuracy `0.46`, total tokens `28,790`.
  - MAD naive: accuracy `0.60`, total tokens `410,691`.
  - MAD-MM objective: accuracy `0.66`, total tokens `273,177`.
  - objective masking used `66.5%` of naive MAD tokens while improving accuracy by 6 points on this probe.
- Supplemental subjective masking run on the same 50-sample slice:
  - accuracy `0.60`, total tokens `494,163`, runtime `228.879s`.
  - tied naive MAD accuracy, used `120.3%` of naive MAD tokens, and used `180.9%` of objective masking tokens.
  - GPU 7 was released after completion.
- Unified trace:
  - `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-7b-math50-probe.comm_trace.jsonl`
  - 200 rows: 50 samples x 4 methods.
- Trace-level transitions:
  - MAD naive vs CoT: 7 `wrong_to_right`, 0 `right_to_wrong`.
  - MAD-MM objective vs CoT: 9 `wrong_to_right`, 0 `right_to_wrong`.
  - MAD-MM objective vs MAD naive: 2 `wrong_to_right`, 0 `right_to_wrong`.
  - MAD-MM subjective vs CoT: 7 `wrong_to_right`, 1 `right_to_wrong`.
  - MAD-MM subjective vs MAD naive: 1 `wrong_to_right`, 2 `right_to_wrong`.
  - MAD-MM subjective vs MAD-MM objective: 0 `wrong_to_right`, 3 `right_to_wrong`.
  - caveat: transition counts use the local trace normalizer, while accuracy above is the MAD-MM official MATH evaluator.
- Objective mask behavior:
  - retained 1 memory in all 50 samples.
  - dropped at least one correct round-0 agent in 29 samples.
  - dropped all correct round-0 agents in 1 sample (`2965`), but that sample still ended correct.
- Subjective mask behavior under the local trace normalizer:
  - retained 128 of 150 round-0 memories, averaging 2.56 retained memories per sample.
  - retained all 3 memories in 35 samples; retained none in 2 samples.
  - dropped at least one correct round-0 agent in 1 sample and all correct round-0 agents in the same sample.
- Added run record:
  - `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/`
- Working interpretation:
  - This MATH probe exposed a much wider communication-method spread than the earlier saturated GSM8K short subset, so benchmark pressure is a faster way to see gaps before spending time on larger matrices.
  - Subjective masking remained a poor tradeoff on this slice: it was the most expensive method and did not beat naive MAD, while objective masking was both cheaper and more accurate.

## 2026-06-13 MAD-MM And DAR Trace Case Follow-Up

- Inspected local trace cases without launching a new GPU run:
  - MAD-MM MATH50 cases `494`, `1237`, and `2965`.
  - DAR GSM8K100 full-history cases `5`, `20`, `22`, and contrast case `37`.
- Added short report:
  - `reports/20260613-madmm-dar-trace-case-followup.md`
- Case-level observations:
  - MAD-MM objective masking can help by retaining the only correct first-round answer, but it can also help by retaining an incomplete or wrong-looking reasoning scaffold that the next round completes.
  - DAR `filter_critical` right-to-wrong cases include direct bad-retention failures and continuation/parser failures after apparently useful retention.
- Next useful non-GPU check:
  - hand-label a few retained messages by role, such as correct answer, useful scaffold, invalid answer, or post-retention format failure.

## 2026-06-13 Retained Message Role Audit

- Hand-labeled retained/dropped message roles for selected MAD-MM MATH50 and DAR GSM8K100 trace cases.
- Added report:
  - `reports/20260613-retained-message-role-audit.md`
- Cases covered:
  - MAD-MM: objective cases `494`, `1237`, `2965`; subjective cases `570`, `843`, `1237`, `494`.
  - DAR: `5`, `20`, `22`, `37`.
- Labels used:
  - `correct_answer`, `useful_scaffold`, `wrong_answer`, `format_or_parse_failure`, `harmful_majority`, `zero_retention_reset`.
- Observations:
  - MAD-MM `570` is a clean subjective dropped-correct-minority failure: retained wrong `288` and `8`, dropped correct `1152`.
  - MAD-MM `494` shows that retaining a correct minority is not enough when full retained reasoning lets wrong alternatives dominate the next round.
  - MAD-MM `843` and `1237` show empty subjective masks behaving like a fresh solve; both ended correct, so zero retention should be logged as reset behavior rather than silently treated as filtering.
  - DAR `20` and `22` expose parser-compatibility failures: the filter can retain malformed or unparseable answers while dropping parseable correct alternatives.
  - DAR `37` shows mixed retention can help when a parseable correct dissenting answer remains visible.
- Candidate next check:
  - implement an offline post-filter wrapper on existing traces that preserves answer diversity and parseable answers before spending another GPU run.

## 2026-06-13 Guarded Retention Offline Simulation

- Added offline audit script:
  - `scripts/simulate_guarded_retention.py`
  - simulates a post-filter guard over unified traces without rerunning any model.
  - rule: record empty retention as reset, avoid retaining only unparseable messages when parseable alternatives exist, and add representatives from missing parseable answer buckets.
- Ran the script over:
  - `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/comm_trace_madmm_math50.jsonl`
  - `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar.jsonl`
- Added local run record:
  - `experiments/20260613-guarded-retention-offline-simulation/`
- Added short report:
  - `reports/20260613-guarded-retention-offline-simulation.md`
- Main `max_retained=3` results:
  - DAR `filter_critical`: 17 of 100 retained sets changed; 13 cases recovered at least one correct first-round message that the original filter missed; 2 of 3 right-to-wrong cases were selection failures addressed by the guard.
  - MAD-MM objective: 25 of 50 retained sets changed; 1 case recovered a correct first-round message, but this mostly makes objective masking less sparse.
  - MAD-MM subjective: 11 of 50 retained sets changed; case `570` recovered the dropped correct answer bucket.
- Caveat:
  - this is a retention-decision audit, not an accuracy result. DAR `5` and MAD-MM subjective right-to-wrong `4616` remain downstream continuation/parser or full-reasoning failures rather than simple selection failures.

## 2026-06-13 DAR Guarded Variant Prep

- Prepared an experimental DAR patch:
  - `baselines/DAR/patches/a8002-guarded-answer-diversity.patch`
  - applies after the existing A800_2 DAR patch stack.
  - adds `--retention_guard answer_diversity`, `--retention_guard_max`, and `--retention_message_mode`.
  - records `original_retained_agent_ids`, guard-added/removed IDs, guard notes, and message mode inside DAR `retention_events`.
  - supports `--retention_message_mode answer_only` so retained peer context can pass parsed answers instead of full prior reasoning.
- Added launcher:
  - `scripts/run_dar_guarded_retention_a8002.sh`
  - target: Qwen2.5-7B-Instruct, GSM8K100, 3 agents, 1 debate round, `filter_critical` plus answer-diversity guard, answer-only retained-message surface, full history.
- Updated `scripts/extract_comm_trace_schema.py` so DAR unified traces preserve guard metadata from `retention_events`.
- Local validation:
  - the new patch applies after the existing DAR A800_2 patch stack on a fresh upstream checkout.
  - `src/dev.py` and `src/main.py` pass `py_compile` in the patched temp checkout.

## 2026-06-13 DAR Guarded Answer-Diversity Run

- Applied `baselines/DAR/patches/a8002-guarded-answer-diversity.patch` on the A800_2 DAR checkout after the existing local patches.
- Verified remote `src/dev.py` and `src/main.py` with `py_compile`.
- Launched bounded run on A800_2 GPU 7:
  - launcher: `scripts/run_dar_guarded_retention_a8002.sh`
  - run id: `20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100`
  - model: Qwen2.5-7B-Instruct
  - dataset: GSM8K100
  - seed: 42
  - setting: 3 agents, 1 debate round, `filter_critical`, `--retention_guard answer_diversity`, `--retention_guard_max 3`, `--retention_message_mode answer_only`, `--save_full_history`
  - wall time: about 2m04s
  - GPU 7 was released after completion.
- Results:
  - round 0 accuracy `0.95`; round 1 accuracy `0.95`.
  - transition counts: 94 `stable_right`, 1 `right_to_wrong`, 1 `wrong_to_right`, 4 `stable_wrong`.
  - changed retained sets: 17/100.
  - guard recovered at least one correct retained first-round message in 13 cases and lost none.
  - generation-plus-filter total tokens: `418,427`, about `77.1%` of the original DAR `filter_critical` full-history run's `542,498`.
- Case notes:
  - original right-to-wrong sample `22` became stable-right after replacing unparseable retained `Agent1` with parseable correct `Agent2`.
  - original right-to-wrong sample `5` became stable-right even though retained IDs did not change, suggesting the answer-only message surface helped with the prior continuation/parser failure.
  - original right-to-wrong sample `20` remained right-to-wrong even after adding correct `Agent1`, so answer diversity alone is not sufficient.
- Added run record and report:
  - `experiments/20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100/`
  - `reports/20260613-dar-guarded-answer-diversity-run.md`

## 2026-06-13 MAD-MM Benchmark Sweep

- Added one-GPU benchmark sweep launcher:
  - `scripts/run_madmm_benchmark_sweep_a8002.sh`
  - default scope: MATH50, MMLU-Pro50, AIME24 full local set, AIME25 full local set.
  - methods: CoT, MAD naive, MAD-MM objective.
- Ran on A800_2 GPU 7 with Qwen2.5-7B-Instruct, seed 41:
  - stamp: `20260613_205520`
  - run window: 2026-06-13 20:55:20 to 21:23:27 CST
  - GPU 7 was released after completion.
- Official accuracy results:
  - MATH50: CoT `0.46`, naive `0.60`, objective `0.66`.
  - MMLU-Pro50: CoT `0.26`, naive `0.36`, objective `0.34`.
  - AIME24: CoT `0.1667`, naive `0.1667`, objective `0.1333`.
  - AIME25: CoT `0.10`, naive `0.0667`, objective `0.10`.
- Extracted unified traces:
  - `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-math-50.comm_trace.jsonl`
  - `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-mmlu_pro-50.comm_trace.jsonl`
  - `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-aime24-all.comm_trace.jsonl`
  - `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-benchmark-sweep-20260613_205520-aime25-all.comm_trace.jsonl`
- Added local run record and report:
  - `experiments/20260613-2055-a8002-madmm-benchmark-sweep/`
  - `reports/20260613-madmm-benchmark-atlas.md`
- Updated `scripts/extract_comm_trace_schema.py` to compare textual labels case-insensitively, fixing MMLU-Pro trace correctness for lower-case model predictions against upper-case gold labels.

## 2026-06-13 DAR Retention Split Ablation

- Added split-ablation launcher:
  - `scripts/run_dar_retention_ablation_a8002.sh`
  - variants: `answer_only_no_guard` and `guard_full`.
- Added summary helper:
  - `scripts/summarize_dar_retention_ablation.py`
  - summarizes DAR unified traces, token totals, transitions, guard metadata, and paired final-correct changes.
- Ran on A800_2 GPU 7 with Qwen2.5-7B-Instruct, seed 42:
  - stamp: `20260613_2143`
  - `answer_only_no_guard`: `--retention_guard none`, `--retention_message_mode answer_only`
  - `guard_full`: `--retention_guard answer_diversity`, `--retention_guard_max 3`, `--retention_message_mode full`
  - GPU 7 was released after completion.
- Results on the same GSM8K100 slice:
  - original DAR `filter_critical`: round 1 `0.93`, 3 `right_to_wrong`, generation-plus-filter tokens `542,498`.
  - `answer_only_no_guard`: round 1 `0.95`, 1 `right_to_wrong`, tokens `419,180`.
  - guarded answer-only: round 1 `0.95`, 1 `right_to_wrong`, tokens `418,427`.
  - `guard_full`: round 1 `0.96`, 0 `right_to_wrong`, tokens `545,520`.
- Case notes:
  - `answer_only_no_guard` recovered original right-to-wrong samples `5` and `22`, matching the earlier guarded answer-only run.
  - `guard_full` recovered samples `5`, `20`, and `22`.
  - sample `20` stayed wrong under answer-only but became correct when the guard added correct `Agent1` and full retained reasoning was visible.
- Added local run record and report:
  - `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/`
  - `reports/20260613-dar-retention-split-ablation.md`
