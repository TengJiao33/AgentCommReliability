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

## 2026-06-14 DAR Sample 20 Retained Surface Check

- Inspected DAR GSM8K100 sample `20` across:
  - original `filter_critical`;
  - guarded answer-only;
  - answer-only no-guard;
  - guard-full.
- Confirmed the case is not a simple answer-diversity selection failure:
  - first-round Agent1 parsed correct answer `7`;
  - Agent2 parsed wrong answer `120`;
  - Agent3 parsed wrong answer `700`, but its reasoning actually computes `$7.00`.
- The answer-only variants remained right-to-wrong, ending at `12`, even when the guard added Agent1.
- `guard_full` became stable-right because full retained reasoning let Agent2 switch to `7`; Agent3 still emitted `{final answer: 700}` despite reasoning toward `$7.00`.
- Added short note:
  - `reports/20260614-dar-sample20-retained-surface-note.md`
- Working next check:
  - try an intermediate retained surface such as parsed answer plus short calculation/evidence before expanding GSM8K or running a harder matrix.

## 2026-06-14 PACT HotpotQA Smoke

- Added PACT as a tracked upstream submodule:
  - repo: `https://github.com/iNLP-Lab/PACT`
  - commit: `91acf820f8a69fc7c181120b3120444a98823230`
  - local path: `baselines/PACT/upstream`
- Added project records:
  - `baselines/PACT/`
  - `papers/cards/pact.md`
  - `scripts/run_pact_hotpot_smoke_a8002.sh`
- Remote setup on A800_2:
  - cloned upstream source to `/data/xuhaoming/yfy/research_workspace/baselines/PACT`;
  - remote syntax check passed;
  - official CMU HotpotQA download hung and remote Hugging Face access timed out, so the dataset was downloaded locally from Hugging Face, validated as 7,405 JSON items, and copied to A800_2.
- Ran two PACT split-evidence HotpotQA checks on GPU 1:
  - Qwen2.5-7B-Instruct, 5 samples: EM `0.20`, avg F1 `0.344`, avg communication tokens `294.6`, avg total tokens `4129.0`.
  - Qwen2.5-14B-Instruct, 50 samples: EM `0.34`, avg F1 `0.508`, avg communication tokens `339.3`, avg total tokens `4746.8`.
  - GPU 1 was released after completion.
- 50-sample trace diagnostics:
  - `Action Required`, `Environment State`, and `Action Result` appeared in all 200 agent turns;
  - `Final Answer` appeared in all 50 final turns;
  - no `<think>` spans appeared, so this run did not exercise private-reasoning stripping;
  - 7 yes/no wrong-EM cases began with the correct yes/no answer, and 8 non-yes/no wrong-EM cases began with the normalized gold answer but added extra text.
- Added local run records and report:
  - `experiments/20260614-1055-a8002-pact-qwen25-7b-hotpot5/`
  - `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/`
  - `reports/20260614-pact-hotpot-smoke.md`
- Completed follow-up checks:
  - the PACT trace extractor, final-answer surface audit, evidence-field audit, extraction-only audit, and stable-wrong follow-up now exist; inspect the five unrecovered-output cases and one polarity mismatch before treating EM as pure reasoning failure or scaling HotpotQA.

## 2026-06-14 Communication Regimes Synthesis

- Updated the project-level reproduction skill so it explicitly distinguishes contact, literature-pressure, and synthesis modes.
- Added synthesis report:
  - `reports/20260614-communication-regimes-synthesis.md`
- The report reframes the current project away from local message-retention variants as the default next move.
- Current working frame:
  - decide when LLM agents should communicate;
  - identify what public state should be transmitted;
  - preserve silence/routing as possible communication decisions;
  - separate task regime, context alignment, debate dynamics, and public-state surface.
- Added evidence-register row `E-025` to mark this as an active synthesis claim, not a new empirical result.
- Recommended next contact before more GPU:
  - focused cards for Benefits/Limitations, M2CL, and Demystifying MAD;
  - a communication-regime harness sketch;
  - or code-reading contact with M2CL's context generator path.
- Created focused pressure-mode paper cards:
  - `papers/cards/benefits-limitations-communication.md`
  - `papers/cards/m2cl.md`
  - `papers/cards/demystifying-mad.md`
- Updated `papers/reading_queue.md` to mark those first paper-card actions as complete.

## 2026-06-14 M2CL Code Contact

- Added M2CL as a tracked upstream submodule:
  - repo: `https://github.com/HansenHua/M2CL-ICLR26`
  - commit: `ada64a9089731f4d2e2cfd2048329cf50f65031f`
  - local path: `baselines/M2CL/upstream`
- Verified `baselines/M2CL/upstream/main.py` and `baselines/M2CL/upstream/method/M2CL.py` with `py_compile`.
- Inspected the context-generator path:
  - `role_generator.gen_role` generates role/context text from `question + peer responses`;
  - `M2CL.sample` and `M2CL.answer` condition agents on generated role/context plus peer responses;
  - final answer is produced by a leader/summarizer prompt.
- Found public-code blockers:
  - `gen_response` immediately returns `"success generate"`, so intended generation branches are unreachable;
  - `api_key.txt`, `dataset/`, `model/`, and `t5-small/` are absent locally;
  - `main.py` hardcodes proxy `http://127.0.0.1:21882`;
  - README still marks context/generator checkpoint release as TODO;
  - `trl` is imported but missing from `requirements.txt`;
  - several per-agent buffers use list multiplication and may alias inner lists.
- Added baseline notes and report:
  - `baselines/M2CL/README.md`
  - `baselines/M2CL/source.md`
  - `baselines/M2CL/reproduction.md`
  - `reports/20260614-m2cl-code-contact.md`
- Added evidence-register row `E-026`.
- Working interpretation:
  - do not treat M2CL as the next GPU reproduction target yet;
  - use it to add a context-state axis to our trace/harness design.

## 2026-06-14 Communication Trace Context Slots

- Updated `scripts/extract_comm_trace_schema.py` from schema version `acr.comm_trace.v1` to `acr.comm_trace.v1.1`.
- Added optional manual labels:
  - `task_regime`;
  - `public_state.surface`;
  - `public_state.communication_policy`.
- Added reserved `context_events` field for generated or assigned recipient context states.
- Updated `docs/comm_trace_schema.md` with the new fields and example labels.
- At this point the new field was reserved for future context-state data; later v1.1 re-extractions populated derived `context_events` from MAD-MM masks, DAR retention events, and MOC ISM sidecars.
- Verified `scripts/extract_comm_trace_schema.py` with `py_compile`, subcommand help checks, and a no-file-output DAR extraction smoke on `experiments/20260613-1718-a8002-trace-instrumentation-check/dar_history_gsm8k5_filtercritical.jsonl`.
- This is a small compatibility step toward the M2CL/context-alignment axis, not a new experiment result.

## 2026-06-14 Communication-Regime Harness Smoke

- Implemented deterministic CPU-only harness:
  - `harness/communication_regimes.py`
  - updated `harness/README.md`
- Harness regimes:
  - `recall`;
  - `state_tracking`;
  - `k_hop`;
  - `conflict_evidence`;
  - `saturated_arithmetic`.
- Harness protocols:
  - `single_agent`;
  - `independent_majority`;
  - `full_broadcast`;
  - `evidence_state`;
  - `route_or_silence`.
- Ran smoke:
  - run id: `20260614-1214-local-comm-regime-symbolic-smoke`
  - output: `experiments/20260614-1214-local-comm-regime-symbolic-smoke/`
  - records: 100 JSONL rows
  - schema: `acr.comm_trace.v1.1`
  - every record has 3 `context_events`.
- First smoke exposed a duplicate-fact issue in `route_or_silence`: recipient context combined private facts and routed facts without de-duplication, causing `state_tracking` operations to be applied twice. Added `unique_facts` and reran the smoke.
- Validated expected pattern:
  - `recall`, `state_tracking`, `k_hop`, and `conflict_evidence` are wrong under `independent_majority` and correct under `evidence_state` / `route_or_silence`;
  - `saturated_arithmetic` is already correct without communication, so communication changes no final answers and mostly adds token cost.
- Added report:
  - `reports/20260614-communication-regime-harness-smoke.md`
- Added evidence-register row `E-027`.

## 2026-06-14 Real Trace v1.1 Regime Labels

- Re-extracted existing local MAD-MM, DAR, and MOC traces into schema `acr.comm_trace.v1.1` without launching any model or using GPU.
- Added method-specific MAD-MM public-state defaults in `scripts/extract_comm_trace_schema.py`:
  - `cot`: `none` / `none`;
  - `mad_naive`: `full_reasoning` / `broadcast`;
  - `mad_objective`: `masked_full_reasoning` / `objective_memory_mask`;
  - `mad_subjective`: `masked_full_reasoning` / `subjective_memory_mask`.
- Outputs:
  - `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/comm_trace_madmm_math50_v11.jsonl`
  - `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar_v11.jsonl`
  - `experiments/20260613-2038-a8002-dar-guarded-answer-diversity-gsm8k100/comm_trace_dar_guarded_v11.jsonl`
  - `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_answer_only_noguard_v11.jsonl`
  - `experiments/20260613-2143-a8002-dar-retention-split-gsm8k100/comm_trace_guard_full_v11.jsonl`
  - `experiments/20260613-1740-a8002-moc-hopcheck-n5/comm_trace_hop1_v11.jsonl`
  - `experiments/20260613-1740-a8002-moc-hopcheck-n5/comm_trace_hop2_v11.jsonl`
- Labels applied:
  - MAD-MM MATH50: `math_reasoning` plus method-specific defaults for `cot`, `mad_naive`, `mad_objective`, and `mad_subjective`;
  - DAR original: `saturated_arithmetic`, `retained_full_reasoning`, `retained_subset`;
  - DAR guarded answer-only: `saturated_arithmetic`, `retained_answer_only`, `guarded_retained_subset`;
  - DAR answer-only no-guard: `saturated_arithmetic`, `retained_answer_only`, `retained_subset`;
  - DAR guard-full: `saturated_arithmetic`, `retained_full_reasoning`, `guarded_retained_subset`;
  - MOC hop1: `saturated_arithmetic`, `neighbor_context`, `topology_hop1`;
  - MOC hop2: `saturated_arithmetic`, `compressed_summary`, `topology_merge`.
- Validation:
  - all seven traces have schema `acr.comm_trace.v1.1`;
  - row counts are 200/100/100/100/100/5/5;
  - every row has non-empty `task_regime`, `public_state.surface`, and `public_state.communication_policy`;
  - derived `context_events` now appear where source structure supports them:
    - MAD-MM MATH50 debate methods: 150 from `mask_history`;
    - DAR traces: 400 from `retention_events`;
    - MOC hop traces: 40 from `ism_result` sidecar events.
- Caveat:
  - derived context events identify visible/suppressed source agents or represented merge sources, but they are not raw prompt-level recipient context.
- Added report:
  - `reports/20260614-real-trace-v11-regime-labels.md`
- Added evidence-register row `E-028`.

## 2026-06-14 Derived Context Event Audit

- Added context-event summary script:
  - `scripts/summarize_context_events.py`
- Ran local audit without GPU:
  - run id: `20260614-1245-local-derived-context-event-audit`
  - output: `experiments/20260614-1245-local-derived-context-event-audit/summary.json`
  - input traces: 7
  - records: 610
  - rows with context events: 560
  - context events: 590
- Context-event derivations:
  - MAD-MM `mask_history`: 150
  - DAR `retention_events`: 400
  - MOC `ism_result`: 40
- Observed context-size patterns:
  - DAR original `filter_critical`: visible peer count distribution `1:64`, `2:27`, `3:9`;
  - DAR guard variants: visible peer count distribution `1:53`, `2:35`, `3:12`;
  - MOC hop2: 15 of 20 target contexts contain a merge representing two source agents.
- Added report:
  - `reports/20260614-derived-context-event-audit.md`
- Added evidence-register row `E-029`.

## 2026-06-14 DAR Context Failure Audit

- Added local audit script:
  - `scripts/audit_dar_context_failures.py`
- Ran CPU-only audit over four existing DAR schema v1.1 traces:
  - run id: `20260614-1248-local-dar-context-failure-audit`
  - output: `experiments/20260614-1248-local-dar-context-failure-audit/`
  - records: 400
  - no model calls and no GPU use.
- Inputs:
  - original full-reasoning DAR: `comm_trace_dar_v11.jsonl`
  - answer-only no-guard: `comm_trace_answer_only_noguard_v11.jsonl`
  - guarded answer-only: `comm_trace_dar_guarded_v11.jsonl`
  - guard-full: `comm_trace_guard_full_v11.jsonl`
- Trace-level outcomes:
  - original: accuracy `0.93`, `right_to_wrong=3`, `wrong_to_right=1`;
  - answer-only no-guard: accuracy `0.95`, `right_to_wrong=1`, `wrong_to_right=1`;
  - guarded answer-only: accuracy `0.95`, `right_to_wrong=1`, `wrong_to_right=1`;
  - guard-full: accuracy `0.96`, `right_to_wrong=0`, `wrong_to_right=1`.
- Original right-to-wrong cases split into two surfaces:
  - case `5`: correct context was visible, but the next round still lost the answer;
  - cases `20` and `22`: all correct first-round answers were suppressed.
- Paired against original:
  - answer-only no-guard fixes cases `5` and `22`;
  - guarded answer-only fixes cases `5` and `22`, but still fails case `20`;
  - guard-full fixes cases `5`, `20`, and `22`.
- Added report:
  - `reports/20260614-dar-context-failure-audit.md`
- Added evidence-register row `E-030`.

## 2026-06-14 DAR Case 20 Surface Extract

- Added local raw-surface extractor:
  - `scripts/extract_dar_case_surface.py`
- Ran CPU-only extraction for DAR GSM8K100 sample `20`:
  - run id: `20260614-1253-local-dar-case20-surface-extract`
  - output: `experiments/20260614-1253-local-dar-case20-surface-extract/`
  - no model calls and no GPU use.
- Inputs:
  - original `filter_critical` history and v1.1 trace;
  - guarded answer-only history and v1.1 trace;
  - answer-only no-guard history and v1.1 trace;
  - guard-full history and v1.1 trace.
- Confirmed the sample `20` surface mismatch from raw retained messages:
  - answer-only variants represent Agent3 only as `Previous parsed final answer: 700.0`;
  - full-message variants retain Agent3's calculation evidence, including `0.30` and `7.00`, despite parsed final answer `700.0`;
  - guarded answer-only adds Agent1's correct parsed answer but still ends wrong at `12.0`;
  - guard-full adds Agent1's full response and ends correct at `7.0`.
- Updated:
  - `reports/20260614-dar-sample20-retained-surface-note.md`
- Added evidence-register row `E-031`.

## 2026-06-14 DAR Typed Surface Preview

- Added offline typed-surface preview script:
  - `scripts/preview_dar_typed_surface.py`
- Ran CPU-only preview over selected DAR cases:
  - cases: `5`, `20`, `22`, `37`
  - variants: original, guarded answer-only, answer-only no-guard, guard-full
  - run id: `20260614-1258-local-dar-typed-surface-preview`
  - output: `experiments/20260614-1258-local-dar-typed-surface-preview/`
  - no model calls and no GPU use.
- Preview surface:
  - source agent;
  - parsed final answer;
  - two mechanically selected calculation/evidence lines from the retained full response.
- Aggregate over 32 retained messages:
  - average answer-only chars: `33.8`
  - average typed-preview chars: `157.2`
  - average full-response chars: `1089.0`
- Sample `20` preview for Agent3 preserves the key mismatch:
  - parsed final answer: `700.0`
  - evidence includes `4.00 + 3.00 = 7.00`
- Caveat:
  - the line extractor is heuristic and sometimes selects long narrative arithmetic lines, especially in sample `37`; this is a prompt/content preview, not a method result.
- Added report:
  - `reports/20260614-dar-typed-surface-preview.md`
- Added evidence-register row `E-032`.

## 2026-06-14 Public State Surface Alignment

- Added local alignment script:
  - `scripts/align_public_state_surfaces.py`
- Ran CPU-only alignment over:
  - DAR typed preview: `experiments/20260614-1258-local-dar-typed-surface-preview/typed_surface_preview.jsonl`
  - PACT HotpotQA50 result: `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/pact_qwen25_14b_hotpot50.jsonl`
  - run id: `20260614-1304-local-public-state-surface-alignment`
  - output: `experiments/20260614-1304-local-public-state-surface-alignment/`
  - no model calls and no GPU use.
- Produced 232 experimental `acr.public_state_surface.v0` records:
  - DAR typed preview: 32
  - PACT action-state: 200
- Field presence:
  - `Action Required`: 232/232
  - `Environment State`: 232/232
  - `Action Result`: 232/232
  - `Final Answer`: 50/232
- Average public-state length:
  - DAR typed preview: `157.2` chars
  - PACT action-state: `363.9` chars
- Alignment gaps:
  - DAR `Action Required` is synthetic;
  - DAR `Environment State` is extracted from generated retained responses, not original source evidence;
  - PACT has code-level `strip_think_tags` projection, while DAR typed preview is still offline.
- Added report:
  - `reports/20260614-public-state-surface-alignment.md`
- Added evidence-register row `E-033`.

## 2026-06-14 PACT Trace v1.1 Extraction

- Extended `scripts/extract_comm_trace_schema.py` with a `pact` subcommand.
- Re-extracted the existing PACT HotpotQA50 result into schema `acr.comm_trace.v1.1`:
  - output: `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl`
  - no model calls and no GPU use.
- Command:
  - `python scripts/extract_comm_trace_schema.py pact --run-id 20260614-1100-a8002-pact-qwen25-14b-hotpot50-v11 --result-jsonl experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/pact_qwen25_14b_hotpot50.jsonl --method pact_action_state --task-regime split_evidence_qa --public-state-surface action_state --communication-policy alternating_action_state --out experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl`
- Validation:
  - rows: 50
  - communication events: 200
  - derived context events: 150
  - field counts: `Action Required=200`, `Environment State=200`, `Action Result=200`, `Final Answer=50`
  - `<think>` spans: 0/200 turns
  - final exact-match correct count: 17/50
- Later correction:
  - PACT HotpotQA gold answers are now preserved as text in the trace instead of using the arithmetic-oriented numeric normalizer.
  - This fixed cases such as gold `1969 until 1974` being collapsed to `1974` in local trace audits.
  - Re-ran the final-answer surface and evidence-field audits after the correction.
- Added report:
  - `reports/20260614-pact-trace-v11-extraction.md`
- Added evidence-register row `E-034`.

## 2026-06-14 PACT Final-Answer Surface Audit

- Added local audit script:
  - `scripts/audit_pact_final_answer_surface.py`
- Ran CPU-only audit over:
  - `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl`
  - output: `experiments/20260614-1314-local-pact-final-answer-surface-audit/`
  - no model calls and no GPU use.
- Official EM remains `17/50`.
- Among 33 wrong-EM cases:
  - 7 yes/no final answers begin with the correct `yes` or `no`;
  - 8 non-yes/no final answers begin with normalized gold;
  - 2 numeric final answers contain the normalized gold number;
  - 1 action-result field begins with normalized gold;
  - 15 have no simple surface signal.
- Added report:
  - `reports/20260614-pact-final-answer-surface-audit.md`
- Added evidence-register row `E-035`.

## 2026-06-14 PACT Evidence Field Audit

- Added local audit script:
  - `scripts/audit_pact_evidence_fields.py`
- Ran CPU-only field-level audit over:
  - `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl`
  - output: `experiments/20260614-1326-local-pact-evidence-field-audit/`
  - no model calls and no GPU use.
- Official EM remains `17/50`.
- Among 33 wrong-EM cases:
  - 23 have an output-field gold or yes/no polarity signal;
  - 8 have strict gold signal only in environment fields;
  - 1 has yes/no final polarity mismatch or unclear;
  - 1 has no strict gold field signal.
- Among 25 wrong non-yes/no cases:
  - final answer contains normalized gold: `15`;
  - action result contains normalized gold: `15`;
  - final environment state contains normalized gold: `19`;
  - any environment state contains normalized gold: `23`.
- Added report:
  - `reports/20260614-pact-evidence-field-audit.md`
- Added evidence-register row `E-036`.

## 2026-06-14 PACT Extraction-Only Audit

- Added local audit script:
  - `scripts/audit_pact_extraction_only.py`
- Ran CPU-only extraction audit over the corrected trace:
  - `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl`
  - output: `experiments/20260614-1345-local-pact-extraction-only-audit/`
  - no model calls and no GPU use.
- Official EM remains `17/50`.
- Fixed final-answer-only extraction policy:
  - exact matches: `32/50`;
  - stable right: `17`;
  - wrong to right: `15`;
  - stable wrong: `18`;
  - right to wrong: `0`.
- Candidate upper bounds:
  - final-event fields: `39/50`;
  - all public action-state fields: `41/50`.
- Added report:
  - `reports/20260614-pact-extraction-only-audit.md`
- Added evidence-register row `E-037`.

## 2026-06-14 PACT Stable-Wrong After Extraction

- Added local audit script:
  - `scripts/audit_pact_stable_wrong_after_extraction.py`
- Ran CPU-only join over:
  - extraction cases: `experiments/20260614-1345-local-pact-extraction-only-audit/cases.jsonl`
  - evidence cases: `experiments/20260614-1326-local-pact-evidence-field-audit/cases.jsonl`
  - output: `experiments/20260614-1402-local-pact-stable-wrong-after-extraction/`
  - no model calls and no GPU use.
- The fixed final-answer extraction policy leaves `18` stable-wrong cases:
  - final event has a matching candidate but the final-answer-only policy missed it: `7`;
  - matching candidate appears only in earlier/wider public state: `2`;
  - strict environment signal exists but simple candidate extraction missed it: `3`;
  - yes/no polarity mismatch: `1`;
  - wrong output signal not recovered by current extractor: `5`.
- Added report:
  - `reports/20260614-pact-stable-wrong-after-extraction.md`
- Added evidence-register row `E-038`.

## 2026-06-14 PACT Unrecovered Case Inspection

- Added focus-case extraction script:
  - `scripts/extract_pact_unrecovered_focus_cases.py`
- Extracted and manually inspected:
  - five `remaining_wrong_output_signal_not_recovered` cases;
  - one `yes_no_polarity_mismatch` case;
  - output: `experiments/20260614-1418-local-pact-unrecovered-case-inspection/`
  - no model calls and no GPU use.
- Manual labels:
  - answer-contract or extractor-priority problems: samples `14`, `24`, `43`, `44`;
  - semantic polarity/predicate problem: sample `13`;
  - mixed entity-alias and evidence-use conflict: sample `21`.
- Added report:
  - `reports/20260614-pact-unrecovered-case-inspection.md`
- Added evidence-register row `E-039`.

## 2026-06-14 PACT Question-Aware Extraction Probe

- Added local audit script:
  - `scripts/audit_pact_question_aware_extraction.py`
- Ran CPU-only question-aware extraction probe over:
  - `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl`
  - output: `experiments/20260614-1432-local-pact-question-aware-extraction/`
  - no model calls and no GPU use.
- Diagnostic exact-match counts:
  - official PACT extraction: `17/50`;
  - fixed final-answer-only extraction: `32/50`;
  - question-aware extraction: `38/50`.
- Compared with fixed final-answer-only extraction:
  - additional rescues: `6`;
  - regressions: `0`.
- Changed cases:
  - `7`: `3677` -> `3677 seated`;
  - `14`: full sentence -> `from 1986 to 2013`;
  - `18`: rule path changed but answer text remains `1969 until 1974`;
  - `21`: `Sonic the Hedgehog` -> `Sonic`;
  - `24`: `1992` -> `World's Best Goalkeeper`;
  - `43`: full sentence -> `sovereignty`;
  - `44`: `Alfred Balk` -> `Nelson Rockefeller`.
- Caveat:
  - sample `21` is surface-recovered but remains a mixed evidence-use conflict from the manual case inspection.
- Added report:
  - `reports/20260614-pact-question-aware-extraction.md`
- Added evidence-register row `E-040`.

## 2026-06-14 PACT Question-Aware Stable-Wrong Audit

- Added local audit script:
  - `scripts/audit_pact_question_aware_stable_wrong.py`
- Ran CPU-only join over:
  - question-aware cases: `experiments/20260614-1432-local-pact-question-aware-extraction/cases.jsonl`
  - fixed extraction cases: `experiments/20260614-1345-local-pact-extraction-only-audit/cases.jsonl`
  - evidence-field cases: `experiments/20260614-1326-local-pact-evidence-field-audit/cases.jsonl`
  - output: `experiments/20260614-1450-local-pact-question-aware-stable-wrong/`
  - no model calls and no GPU use.
- The question-aware extraction policy leaves `12` stable-wrong cases:
  - final event has a matching candidate but the question-aware policy missed it: `7`;
  - matching candidate appears only in earlier/wider public state: `2`;
  - strict environment signal exists but current candidate extraction misses it: `2`;
  - semantic polarity or predicate failure: `1`.
- Added report:
  - `reports/20260614-pact-question-aware-stable-wrong.md`
- Added evidence-register row `E-041`.

## 2026-06-14 PACT Field-Selection Case Inspection

- Added focus-case extraction script:
  - `scripts/extract_pact_field_selection_focus_cases.py`
- Extracted and manually inspected the `9` question-aware stable-wrong cases
  where a matching candidate appears in final or earlier public state:
  - output: `experiments/20260614-1507-local-pact-field-selection-case-inspection/`
  - no model calls and no GPU use.
- Mechanical buckets:
  - final event has a matching candidate but question-aware policy missed it: `7`;
  - matching candidate appears only in earlier/wider public state: `2`.
- Manual families:
  - final field or anchor selection conflict: samples `1`, `15`, `31`;
  - answer contract or extractor priority: samples `25`, `28`, `30`, `40`;
  - earlier state lost or overwritten: samples `19`, `23`.
- Added report:
  - `reports/20260614-pact-field-selection-case-inspection.md`
- Added evidence-register row `E-042`.

## 2026-06-14 PACT Public-State Arbitration Probe

- Added local postprocessing probe:
  - `scripts/audit_pact_public_state_arbitration.py`
- Ran CPU-only arbitration policies over:
  - trace: `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl`
  - manual labels: `experiments/20260614-1507-local-pact-field-selection-case-inspection/manual_labels.jsonl`
  - output: `experiments/20260614-1518-local-pact-public-state-arbitration-probe/`
  - no model calls and no GPU use.
- Diagnostic counts:
  - official PACT extraction: `17/50`;
  - question-aware policy: `38/50`;
  - naive final-event arbitration: `38/50`, with `6` rescues and `6` regressions versus question-aware;
  - guarded final-event arbitration: `44/50`, with `6` rescues and `0` regressions versus question-aware.
- On the `9` field-selection focus cases, guarded final-event arbitration recovers:
  - final field or anchor selection conflict: `3/3`;
  - answer contract or extractor priority: `3/4`;
  - earlier state lost or overwritten: `0/2`.
- Added report:
  - `reports/20260614-pact-public-state-arbitration-probe.md`
- Added evidence-register row `E-043`.

## 2026-06-14 PACT Final-Answer-Contract GPU Run

- Added an env-gated final-turn prompt control:
  - `baselines/PACT/upstream/prompts.py`
  - flag: `PACT_FINAL_ANSWER_CONTRACT=1`
- Updated the A800_2 runner to log the flag:
  - `scripts/run_pact_hotpot_smoke_a8002.sh`
- Ran a real GPU PACT HotpotQA50 variant on A800_2 GPU 7:
  - model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
  - output: `experiments/20260614-1536-a8002-pact-qwen25-14b-hotpot50-final-contract/`
  - remote result dir: `/data/xuhaoming/yfy/research_workspace/results/pact-qwen25-14b-hotpot50-final-contract-20260614_1536`
  - status: `RC=0`.
- Main metrics:
  - original PACT50 EM/F1: `17/50`, `0.508`;
  - final-answer-contract EM/F1: `34/50`, `0.792`;
  - average final-answer words: `9.92` -> `2.08`;
  - average communication tokens: `339.3` -> `321.9`.
- Case transitions against original PACT50:
  - stable right: `14`;
  - wrong to right: `20`;
  - right to wrong: `3`;
  - stable wrong: `13`.
- Added comparison and post-run diagnostics:
  - `scripts/compare_pact_runs.py`
  - `analysis_summary.json`
  - `changed_cases.jsonl`
  - `question_aware_summary.json`
  - `public_state_arbitration_summary.json`
- Added report:
  - `reports/20260614-pact-final-answer-contract-gpu.md`
- Added evidence-register row `E-044`.

## 2026-06-14 Current Evidence Checkpoint

- Added a state checkpoint:
  - `reports/20260614-current-evidence-checkpoint.md`
- Purpose:
  - preserve the current messy evidence shape before more runs;
  - avoid forcing the PACT final-answer-contract observation into an immediate novelty claim;
  - keep the live threads visible across MAD-MM, DAR, MOC, M2CL, PACT, and the local communication-regime harness.
- Current bias recorded in the checkpoint:
  - small empirical continuation: PACT neighboring-slice check;
  - small local continuation: add a less-oracle router to the communication-regime harness.
- Evidence register:
  - no new row; this is a checkpoint over existing observations, not a new empirical claim.

## 2026-06-14 PACT Neighboring-Slice Runner Prep

- Added offset support for future PACT HotpotQA neighboring-slice checks:
  - `baselines/PACT/upstream/run.py`: new `--start_index` argument;
  - `baselines/PACT/upstream/data.py`: loader yields original HotpotQA `sample_index`;
  - `baselines/PACT/upstream/methods/pact.py`: JSONL output preserves `sample_index`;
  - `scripts/run_pact_hotpot_smoke_a8002.sh`: reads `PACT_START_INDEX`;
  - `scripts/extract_comm_trace_schema.py`: PACT extraction uses preserved `sample_index` when present.
- Important detail:
  - the loader still advances the seeded paragraph splitter through skipped rows, so offset sample `50` keeps the same context split it would have had in a full sequential run.
- Updated PACT source/reproduction notes with the new neighboring-slice command shape.
- Validation:
  - `py_compile` passed for PACT `run.py`, `data.py`, `methods/pact.py`, and `scripts/extract_comm_trace_schema.py`;
  - a temporary local loader smoke confirmed `start_index=2, max_samples=2` yields preserved indices `[2, 3]` and matches the full-run seeded split for sample `2`.
- No model call or GPU run was launched.

## 2026-06-14 PACT Offset50 Final-Answer-Contract Paired Run

- Ran a paired neighboring-slice PACT check on A800_2 GPU 7:
  - samples: HotpotQA zero-based `50-99`;
  - model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`;
  - baseline: `PACT_FINAL_ANSWER_CONTRACT=0`;
  - variant: `PACT_FINAL_ANSWER_CONTRACT=1`;
  - both runs completed with `RC=0`.
- Run record:
  - `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/`
- Main metrics:
  - baseline EM/F1: `26/50`, `0.6469`;
  - final-contract EM/F1: `28/50`, `0.7427`;
  - average final-answer words: `7.62` -> `2.32`;
  - average communication tokens: `327.3` -> `324.0`.
- Case transitions:
  - stable right: `22`;
  - wrong to right: `6`;
  - right to wrong: `4`;
  - stable wrong: `18`.
- Diagnostics:
  - question-aware extraction reaches `29/50` on both baseline and contract traces;
  - guarded final-event arbitration over the contract trace stays at `28/50`, with one rescue and one regression.
- Interpretation:
  - the first-50 final-answer-contract signal does not repeat as a large EM jump on offset50;
  - the answer-surface effect remains visible through F1 and several exact-match rescues;
  - the contract also introduces one clear content regression, sample `58`.
- Added report:
  - `reports/20260614-pact-offset50-final-answer-contract.md`
- Added evidence-register row `E-045`.

## 2026-06-14 PACT Offset50 Case Atlas

- Added a CPU-only case atlas builder:
  - `scripts/build_pact_case_atlas.py`
- Ran it over the offset50 paired PACT outputs:
  - output summary: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/case_atlas_summary.json`
  - all cases: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/case_atlas_cases.jsonl`
  - focus cases: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/case_atlas_focus_cases.jsonl`
- Rough focus-case labels:
  - contract-rescued verbose surface: `5`;
  - contract-rescued content or field: `1`;
  - strict-span regression: `3`;
  - content-drift regression: `1`;
  - final public state contains gold: `10`;
  - recoverable from public-state policy: `1`;
  - near-miss surface/span: `1`;
  - likely evidence or reasoning failure: `6`.
- Added report:
  - `reports/20260614-pact-offset50-case-atlas.md`
- Added evidence-register row `E-046`.

## 2026-06-14 PACT Offset50 Public-State Gold Case Inspection

- Manually inspected the ten offset50 cases mechanically labeled `final_public_state_contains_gold`.
- Added manual labels:
  - `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/public_state_gold_manual_labels.jsonl`
- Manual families:
  - missing required token or qualifier: `3` cases (`50`, `55`, `83`);
  - wrong answer type or slot: `2` cases (`60`, `67`);
  - over-specific answer: `3` cases (`87`, `89`, `92`);
  - alias/name granularity: `1` case (`74`);
  - false-positive string signal: `1` case (`59`).
- Added report:
  - `reports/20260614-pact-offset50-public-state-gold-cases.md`
- Added evidence-register row `E-047`.

## 2026-06-14 PACT Offset50 Sample58 Drift Inspection

- Added a reusable paired-run drift packet builder:
  - `scripts/build_pact_drift_packet.py`
- Ran it on offset50 sample `58`, the clear content-drift right-to-wrong case:
  - packet JSON: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/pact_sample58_drift_packet.json`
  - packet Markdown: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/pact_sample58_drift_packet.md`
- Finding:
  - baseline keeps the target as the population of the city/town in which Kirton End is located and answers `35,124`;
  - the variant trajectory still sees `35,124` at turn `1`, but later retargets to the population of the civil parish of Kirton and answers `273` from the `Kirton, Nottinghamshire` distractor;
  - the first observed divergence is turn `1`, before the final-answer-contract prompt applies, so this is a stochastic trajectory and target-slot drift sentinel, not clean causal evidence that the final-turn contract directly caused the wrong number.
- Added report:
  - `reports/20260614-pact-offset50-sample58-drift.md`
- Added evidence-register row `E-048`.

## 2026-06-14 PACT Offset50 Target-Slot Drift Diagnostic

- Added a rough lexical target-slot preservation diagnostic over PACT
  `Action Required` fields:
  - `scripts/audit_pact_target_slot_drift.py`
- Ran it over the offset50 paired focus cases:
  - focus summary: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/target_slot_drift_summary.json`
  - focus cases: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/target_slot_drift_cases.jsonl`
  - focus candidates: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/target_slot_drift_candidates.jsonl`
- Also ran it over all 50 paired cases:
  - all-case summary: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/target_slot_drift_all_summary.json`
  - all-case candidates: `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/target_slot_drift_all_candidates.jsonl`
- Result:
  - 8 candidates: samples `54`, `55`, `58`, `60`, `82`, `83`, `87`, `89`;
  - candidates include 2 right-to-wrong and 6 stable-wrong cases;
  - running over all 50 cases returns the same 8 candidates and no stable-right candidates.
- Interpretation:
  - sample `58` remains the clean target-migration sentinel;
  - several candidates are target under-specification or target/final-answer mismatch rather than true semantic migration;
  - sample `54` is a useful soft/false-positive warning because the actual failure is mostly strict span surface.
- Added report:
  - `reports/20260614-pact-offset50-target-slot-drift.md`
- Added evidence-register row `E-049`.

## 2026-06-14 PACT Offset100 Target-Contract GPU Run

- Added an env-gated PACT target-slot prompt control:
  - file: `baselines/PACT/upstream/prompts.py`
  - flag: `PACT_TARGET_SLOT_CONTRACT=1`
  - purpose: make the public `Action Required` field preserve the original question target, answer type, qualifier, and anchor entities.
- Synced the patched prompt and runner to A800_2 and verified remote `py_compile` plus `bash -n`.
- First launch attempt used an imperfect wrapper that failed to pass all env vars, fell back to default GPU `1`, and hit vLLM OOM before processing samples. No output samples were produced in that failed attempt.
- Reran successfully on A800_2 GPU `5` with explicit per-command env vars.
- Slice:
  - HotpotQA zero-based samples `100-149`
  - Qwen2.5-14B-Instruct
  - seed `42`
  - 50 samples per arm
- Arms and metrics:
  - baseline: EM `16/50`, avg F1 `0.5517`, avg communication tokens `361.6`, avg total tokens `4477.0`.
  - final-answer contract: EM `26/50`, avg F1 `0.6332`, avg communication tokens `331.5`, avg total tokens `4526.8`.
  - target + final contract: EM `26/50`, avg F1 `0.6494`, avg communication tokens `485.2`, avg total tokens `5266.0`.
- Paired transitions:
  - baseline -> final contract: 12 wrong-to-right, 2 right-to-wrong, 14 stable-right, 22 stable-wrong.
  - final contract -> target + final: 3 wrong-to-right, 3 right-to-wrong, 23 stable-right, 21 stable-wrong.
  - baseline -> target + final: 14 wrong-to-right, 4 right-to-wrong, 12 stable-right, 20 stable-wrong.
- Target-slot diagnostic:
  - baseline -> final contract: 6 candidates over 36 non-stable-right focus cases.
  - baseline -> target + final: 2 candidates over 38 non-stable-right focus cases.
  - final contract -> target + final: 1 candidate over 27 non-stable-right focus cases.
- Interpretation:
  - final-answer contract again gives a real EM lift on a fresh slice.
  - naive target-slot preservation improves the visible target-preservation diagnostic and slightly raises F1, but does not improve EM and substantially increases token cost.
  - this supports target preservation as a separable public-state control surface, not as a finished prompt method.
- Run record:
  - `experiments/20260614-1552-a8002-pact-qwen25-14b-hotpot50-offset100-target-contract/`
- Report:
  - `reports/20260614-pact-offset100-target-contract-gpu.md`
- Added evidence-register row `E-050`.

## 2026-06-14 PACT Offset150 Compact Target-State GPU Run

- Added an env-gated compact target-state prompt control:
  - file: `baselines/PACT/upstream/prompts.py`
  - flag: `PACT_COMPACT_TARGET_STATE=1`
  - field: `Target Slot: [answer type; anchor entity or entities; required qualifier]`
- Updated supporting scripts:
  - `scripts/run_pact_hotpot_smoke_a8002.sh` logs `PACT_COMPACT_TARGET_STATE`;
  - `scripts/extract_comm_trace_schema.py` extracts `Target Slot` into PACT communication events;
  - `scripts/audit_pact_target_slot_drift.py` prefers `Target Slot` when present;
  - `scripts/audit_pact_target_slot_field.py` audits field presence, generic targets, and per-sample target-slot stability.
- Added idea memo:
  - `reports/20260614-public-state-communication-idea-memo.md`
- Synced prompt and runner to A800_2 and verified remote `py_compile` plus `bash -n`.
- Ran three PACT HotpotQA arms on A800_2 GPU `5`:
  - slice: zero-based samples `150-199`
  - model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
  - seed: `42`
  - 50 samples per arm
- Metrics:
  - final-answer contract: EM `25/50`, avg F1 `0.6777`, avg communication tokens `324.6`, avg total tokens `4662.2`.
  - compact target + final contract: EM `22/50`, avg F1 `0.6036`, avg communication tokens `497.3`, avg total tokens `5427.8`.
  - compact target only: EM `19/50`, avg F1 `0.5790`, avg communication tokens `547.4`, avg total tokens `5471.5`.
- Paired transitions:
  - final contract -> compact target + final: 5 wrong-to-right, 8 right-to-wrong, 17 stable-right, 20 stable-wrong.
  - final contract -> compact target only: 3 wrong-to-right, 9 right-to-wrong, 16 stable-right, 22 stable-wrong.
  - compact target only -> compact target + final: 6 wrong-to-right, 3 right-to-wrong, 16 stable-right, 25 stable-wrong.
- Target Slot field audit:
  - compact target + final: `199/200` events with target slot, `49/50` samples have target slot on all turns, `27/50` samples have stable target slot, no generic final target slots.
  - compact target only: `199/200` events with target slot, `49/50` samples have target slot on all turns, `24/50` samples have stable target slot, no generic final target slots.
- Interpretation:
  - compact target-state as generated every turn is not a method win;
  - the model mostly follows the field format, but different agents/turns instantiate different target slots;
  - the next target-preservation intervention should freeze or parse the target state from the original question rather than regenerate it at every turn.
- Run record:
  - `experiments/20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target/`
- Report:
  - `reports/20260614-pact-offset150-compact-target-state.md`
- Added evidence-register row `E-051`.

## 2026-06-14 PACT Target-State Freeze Inspection

- Added local diagnostic script:
  - `scripts/build_pact_target_state_freeze_inspection.py`
- Ran a CPU-only inspection over the offset150 PACT final-contract versus compact-target+final traces:
  - input run: `experiments/20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target/`
  - output: `experiments/20260614-1719-local-pact-target-state-freeze-inspection/`
  - no model calls and no GPU use.
- Mechanical scan over 50 compact-target+final samples:
  - `23/50` records have unstable target slots;
  - `22/50` records have first/final target-slot mismatch;
  - `4/50` records collapse to a literal target-slot template;
  - the 8 right-to-wrong cases split into 4 visible target-drift regressions and 4 stable-target regressions.
- Manual labels over 16 focus cases suggest:
  - question-derived or anchor-checked target state might help samples `189`, `197`, `199`, and `184`;
  - first-turn generated target freeze would hurt or preserve error in samples `193`, `176`, `188`, and `160`;
  - several regressions are answer-surface, extraction, alias, or missing-evidence issues rather than target-state failures.
- Interpretation:
  - freezing the first generated `Target Slot` is too crude;
  - the next local object should be a question-derived target-state projection/checker that allows bridge refinement while flagging anchor, predicate, or answer-type replacement.
- Added report:
  - `reports/20260614-pact-target-state-freeze-inspection.md`
- Added evidence-register row `E-052`.

## 2026-06-14 PACT Target-State Sketchbook

- Added loose case sketchbook:
  - `reports/20260614-pact-target-state-sketchbook.md`
- Purpose:
  - stay with the target-state ambiguity before writing a checker or prompt;
  - distinguish harmful target replacement from useful bridge refinement;
  - avoid treating first-turn generated `Target Slot` as an authority.
- Cases sketched:
  - harmful or likely harmful target movement: samples `199`, `189`, `197`, `184`, and offset50 sample `58`;
  - useful target movement: samples `176`, `188`, and `152`;
  - freeze traps or non-target-state failures: samples `160`, `193`, `153`, `154`, and `182`.
- Working distinction:
  - "preserve the target" is too flat;
  - HotpotQA needs target motion through bridge entities;
  - the next local object, if any, should be a loose question-derived target-state projection that permits bridge refinement while flagging anchor, predicate, object, or granularity replacement.
- Evidence register:
  - no new row; this is a sketchbook over existing evidence, not a new empirical claim.

## 2026-06-14 PACT Question-Target Postcards

- Added an even looser handwritten-style note:
  - `reports/20260614-pact-question-target-postcards.md`
- Purpose:
  - turn the target-state sketchbook into short per-case cards;
  - record what the original question wants, what bridge it must cross, what public state did, and what must not be lost;
  - keep the idea in a flexible form before writing any checker.
- Case clusters that fell out:
  - clue object is not answer object;
  - predicate must survive the bridge;
  - some drift is the task;
  - first target is not sacred;
  - target is not always the problem.
- Working phrase left behind:
  - `target role preservation across bridge movement`
- Evidence register:
  - no new row; these postcards are interpretive notes over existing cases.

## 2026-06-14 Target Role Lens Across Baselines

- Added cross-baseline interpretive note:
  - `reports/20260614-target-role-lens-cross-baseline-notes.md`
- Purpose:
  - step half a pace away from PACT;
  - ask whether the target-role vocabulary has shadows in DAR, MAD-MM, and MOC;
  - avoid turning PACT's explicit `Target Slot` field into a universal solution.
- Working observations:
  - PACT exposes target role as public action-state fields;
  - DAR hides target/evidence role inside retained message surface, where answer-only can flatten useful reasoning evidence;
  - MAD-MM hides target role inside retained memory anchors and reasoning scaffolds;
  - MOC is a plausible compression/summary site for role loss, but current saturated GSM8K hop checks do not expose it.
- Loose next drift:
  - create tiny role cards across systems only if useful, using fields like message, parsed answer, role it played, role it lost, and downstream effect.
- Evidence register:
  - no new row; this is an interpretive alignment note over existing reports.

## 2026-06-14 Cross-System Role Cards

- Added tiny cross-system card note:
  - `reports/20260614-cross-system-role-cards.md`
- Purpose:
  - keep the target-role lens concrete across PACT, DAR, MAD-MM, and MOC;
  - avoid turning PACT's explicit `Target Slot` into a universal abstraction;
  - record where the lens fits, where it changes shape, and where it is currently blank.
- Cards included:
  - PACT `199` and `176`;
  - DAR `20` and `5`;
  - MAD-MM `214` and `1237`;
  - MOC hop2 and an explicit empty card noting that current GSM8K hop smoke does not ask the role-loss question.
- Working observation:
  - PACT shows target-role drift;
  - DAR shows evidence-role flattening;
  - MAD-MM shows memory-role anchoring and scaffold reuse;
  - MOC shows a plausible compression site but not yet a role-loss case.
- Evidence register:
  - no new row; this is a card file over existing evidence.

## 2026-06-14 MAD-MM 1237 Raw Role Card

- Added raw-log follow-up:
  - `reports/20260614-madmm-1237-raw-role-card.md`
- Sources inspected:
  - `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/mad_objective_3agents_2rounds_seed41_debate_log.json`
  - `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/mad_3agents_2rounds_seed41_debate_log.json`
  - `experiments/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/mad_subjective_3agents_2rounds_seed41_debate_log.json`
- What changed:
  - objective masking retained only Agent3's wrong-answer but useful operation scaffold for case `1237`;
  - all objective round-2 agents completed `sqrt(1296)=36`, then `sqrt(64)=8`;
  - naive full retention showed two agents computing the right path in reasoning but still outputting `sqrt(34)`;
  - subjective masking retained no first-round messages and still got a correct majority on a fresh second pass.
- Interpretation:
  - case `1237` should not be treated as clean proof that the retained scaffold caused the fix;
  - it is better read as separating operation scaffold, wrong answer-surface anchor, and fresh second-pass behavior.
- Updated:
  - `reports/20260614-cross-system-role-cards.md` now includes the raw-log caveat.
- Evidence register:
  - no new row; this refines an interpretive card rather than adding a durable empirical claim.

## 2026-06-14 MOC Role-Sensitive Split-Evidence Probe

- Added a CPU-only synthetic MOC-style role-loss probe:
  - `scripts/run_moc_role_loss_probe.py`
- Ran it locally:
  - output: `experiments/20260614-1832-local-moc-role-sensitive-split-evidence-probe/`
  - trace: `comm_trace_moc_role_probe_v11.jsonl`
  - records: `30` records over `6` hand-built split-evidence cases and `5` public-state policies.
- Purpose:
  - fill the previously blank MOC role card with a concrete contact object;
  - inspect whether compressed multi-hop summaries preserve clue, bridge, requested relation, qualifier, answer, and distractor roles;
  - avoid launching another saturated GSM8K MOC run.
- Result:
  - `hop2_unmerged_context`: `6/6`;
  - `hop2_role_aware_merge`: `6/6`;
  - `hop2_flat_entity_merge`: `1/6`;
  - `hop2_answer_only_merge`: `1/6`;
  - the one surviving flat/answer-only case is useful bridge refinement, keeping the caveat that target motion is not automatically drift.
- Added report:
  - `reports/20260614-moc-role-sensitive-split-evidence-probe.md`
- Evidence register:
  - added row `E-053`.

## 2026-06-14 MOC Merge Prompt Role Audit

- Added a merge-only LLM audit for MOC's five structural merge prompt
  strategies:
  - `scripts/run_moc_merge_prompt_role_audit.py`
- Ran it on A800_2 with a temporary vLLM service:
  - model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
  - served name: `qwen2.5-7b-merge-audit`
  - GPU: `1`
  - port: `8022`
  - run record: `experiments/20260614-1913-a8002-moc-merge-prompt-role-audit/`
- Stopped the temporary vLLM service after the run and confirmed GPU `1` was
  released.
- Scope:
  - six synthetic split-evidence role cases from the previous MOC role probe;
  - two surfaces: `labeled_role_messages` and `natural_evidence_messages`;
  - five merge strategies matching the inspected MOC merge prompt families;
  - `60` trace records in `comm_trace_moc_merge_prompt_role_audit_v11.jsonl`.
- Result:
  - labeled role messages preserved all required slots in `19/30` outputs;
  - the labeled `technical_precision` strategy preserved all slots in `6/6`;
  - natural evidence messages preserved all required slots in only `4/30`
    outputs;
  - natural evidence losses concentrated on `forbidden_replacement`,
    `required_qualifier`, `clue_object`, and `requested_relation`.
- Interpretation:
  - MOC's compression site is now a concrete role-preservation audit object;
  - source attribution alone is not enough, since some outputs preserve agent
    attribution while still losing key role slots;
  - this is still merge-prompt-only synthetic evidence, not a full MOC result.
- Added report:
  - `reports/20260614-moc-merge-prompt-role-audit.md`
- Evidence register:
  - added row `E-054`.

## 2026-06-14 ArXiv Digest Pressure Contact

- Added pressure-contact note:
  - `reports/20260614-arxivdigest-pressure-contact.md`
- Source:
  - local `D:\develop\ArXiv_Daily_Digest`
  - directions touched: `multi-agent-consistency`, `agent-skills-harness`, and `factuality-rule-guided-apps`
- Purpose:
  - keep the exploration deliberately loose;
  - use external papers to ask which variables our current traces do not record;
  - avoid turning the MOC role-loss audit or PACT final-answer contract into premature main ideas.
- Pressure axes that emerged:
  - harmful peer exposure and conformity;
  - answer-level consensus hiding reasoning or role misalignment;
  - typed terminal states such as commit, disagree, abort, or needs-evidence;
  - harness/context layers as first-class reliability variables;
  - decision-critical context rather than summary fluency or token cost alone.
- Touchable next objects left behind:
  - a tiny peer-exposure mini-probe;
  - a typed terminal-state probe around PACT-style public state;
  - continued use of the MOC role-loss audit as an instrument rather than a standalone idea;
  - a harness-layer retrospective over saved PACT/DAR cases.
- Evidence register:
  - no new row; this is a pressure-contact note, not a new empirical claim.

## 2026-06-14 Peer Exposure Mini-Probe

- Added script:
  - `scripts/run_peer_exposure_probe.py`
- Purpose:
  - touch the "communication as exposure channel" question from the arXiv digest pressure contact;
  - reuse real DAR round-0 peer outputs from saved GSM8K disagreement cases;
  - separate no-peer answering, wrong/correct answer-only exposure, wrong majority, authority-labeled wrong exposure, and full rationale exposure.
- Source object:
  - DAR full-history GSM8K100 run from `experiments/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/`
  - selected mixed first-round cases: `20`, `78`, `4`, `8`, `37`, `65`
- First run:
  - `experiments/20260614-1956-a8002-peer-exposure-mini-probe/`
  - found a parser/truncation artifact: `max_tokens=360` plus last-number fallback made one truncated output look like a wrong answer.
- Final v2 run:
  - `experiments/20260614-2005-a8002-peer-exposure-mini-probe-v2/`
  - A800_2 GPU `1`, temporary vLLM port `8024`, Qwen2.5-7B-Instruct
  - `42` records over `6` cases and `7` conditions
  - temporary vLLM service was stopped after the run and GPU `1` returned to idle.
- Main small observations:
  - no-peer regenerated baseline: `4/6` correct;
  - `wrong_answer_only`: one clear right-to-wrong case (`37`, `11 -> 12`);
  - `correct_rationale`: one wrong-to-right case (`8`, `27 -> 24`);
  - `correct_answer_only` did not rescue case `8`;
  - case `78` remained wrong even with a correct full rationale, because the target kept a different predicate interpretation of "2 seashells each."
- Added report:
  - `reports/20260614-peer-exposure-mini-probe.md`
- Evidence register:
  - added row `E-055`.

## 2026-06-14 Peer Exposure Follow-Ups

- Updated script:
  - `scripts/run_peer_exposure_probe.py`
  - added `natural` warning mode, relation-only and wrong-relation surfaces,
    terminal-state response mode, and MAD-MM MATH source support.
- Formal runs:
  - `experiments/20260614-2105-a8002-peer-exposure-natural-warning/`
  - `experiments/20260614-2106-a8002-peer-exposure-surface-dissect/`
  - `experiments/20260614-2107-a8002-peer-exposure-terminal-state/`
  - `experiments/20260614-2108-a8002-peer-exposure-madmm-math-contact/`
- Runtime:
  - A800_2 GPU `1`, temporary vLLM port `8024`, Qwen2.5-7B-Instruct
  - stopped the temporary service after the runs and confirmed GPU `1` returned
    to idle.
- Main small observations:
  - removing the anti-conformity warning did not simply increase wrong-answer
    copying; `authority_wrong` flipped DAR case `37`, while plain
    `wrong_answer_only` did not in that run;
  - in the surface dissection, `correct_relation_only` rescued DAR case `8`
    without giving the final answer, while `wrong_answer_wrong_relation` was
    more harmful than wrong answer-only;
  - plausible irrelevant peer text was mostly ignored on the three-case surface
    probe;
  - terminal-state prompting converted wrong peer pressure into `DISAGREE` with
    no final answer, but also blocked useful correction on initially wrong
    cases;
  - MAD-MM MATH case `494` showed the same shape: correct full rationale rescued
    the case to `8`, while correct answer-only did not.
- Added report:
  - `reports/20260614-peer-exposure-followups.md`
- Evidence register:
  - added row `E-056`.

## 2026-06-14 Peer Auto-Evidence Contact

- Updated script:
  - `scripts/run_peer_exposure_probe.py`
  - added schema `acr.peer_exposure.v0.3`;
  - added `correct_auto_evidence` and `wrong_auto_evidence`;
  - added `--selection-mode random`, `--sample-seed`, and
    `auto_evidence_extractions.jsonl`.
- Formal runs:
  - `experiments/20260614-2205-a8002-peer-auto-evidence-dar-random14/`
  - `experiments/20260614-2206-a8002-peer-auto-evidence-math-random8/`
- Runtime:
  - A800_2 GPU `1`, temporary vLLM port `8024`, Qwen2.5-7B-Instruct
  - stopped the temporary service after the runs and confirmed GPU `1` returned
    to idle.
- DAR random14:
  - no-peer: `11/14`;
  - `correct_answer_only`: `11/14`;
  - `correct_auto_evidence`: `12/14`;
  - `correct_rationale`: `13/14`;
  - `wrong_answer_only`: `11/14`;
  - `wrong_auto_evidence`: `9/14`;
  - `wrong_rationale`: `9/14`.
- MATH random8:
  - no-peer: `4/8`, with two no-peer unparseable outputs;
  - `correct_answer_only`: `6/8`;
  - `correct_auto_evidence`: `5/8`;
  - `correct_rationale`: `7/8`;
  - `wrong_answer_only`: `5/8`;
  - `wrong_auto_evidence`: `5/8`;
  - `wrong_rationale`: `4/8`.
- Main small observations:
  - DAR auto evidence partially reproduced the relation-only signal: case `8`
    moved from `14` to `24` without answer adoption;
  - wrong auto evidence caused two DAR right-to-wrong regressions despite
    `peer_answer_adoption_rate = 0.0`;
  - MATH case `47` showed a useful collision: wrong compressed evidence
    preserved a recoverable party-block structure, and the target repaired the
    wrong internal count to reach `28800`;
  - the extractor often leaked the source answer (`9/28` DAR notes, `7/16`
    MATH notes by naive containment), so the current auto-evidence surface is
    not a clean relation-only surface.
- Added report:
  - `reports/20260614-peer-auto-evidence-contact.md`
- Evidence register:
  - added row `E-057`.

## 2026-06-14 Peer Auto-Evidence Audit

- Added local audit script:
  - `scripts/audit_peer_auto_evidence.py`
- Ran a CPU-only audit over the latest auto-evidence sidecars:
  - source runs:
    - `experiments/20260614-2205-a8002-peer-auto-evidence-dar-random14/`
    - `experiments/20260614-2206-a8002-peer-auto-evidence-math-random8/`
  - output: `experiments/20260614-2107-local-peer-auto-evidence-audit/`
  - joined `44/44` auto-evidence notes to downstream revision records.
- Mechanical audit results:
  - `16/44` notes contain source-answer numeric or answer-like leakage under the current heuristic;
  - `2` correct-evidence rescues: DAR `8` and MATH `47`;
  - `2` wrong-evidence harmful-relation cases: DAR `97` and DAR `4`;
  - `1` wrong-evidence recoverable-skeleton case: MATH `47`.
- Parser friction found and patched for future runs:
  - `scripts/run_peer_exposure_probe.py` now handles nested-brace final answers and `\frac{a}{b}` / `a/b` answers;
  - `scripts/audit_peer_auto_evidence.py` uses the same fraction normalizer;
  - `skills/repro-friction-memory/SKILL.md` records the reusable parser rule.
- Caveat:
  - the saved MATH random8 peer-exposure records were generated before the parser patch, so those MATH accuracy and peer-correctness labels should be read as contact evidence with parser caveats.
- Added report:
  - `reports/20260614-peer-auto-evidence-audit.md`
- Evidence register:
  - added row `E-058`.

## 2026-06-14 Peer Redacted Evidence Surface

- Updated scripts:
  - `scripts/run_peer_exposure_probe.py`
    - schema bumped to `acr.peer_exposure.v0.4`;
    - added `correct_redacted_evidence` and `wrong_redacted_evidence`;
    - added exact parsed-answer redaction before evidence compression;
    - fixed numeric answer containment/redaction so sentence-final numbers like
      `28800.` are matched while decimal tails remain protected.
  - `scripts/audit_peer_auto_evidence.py`
    - includes the redacted evidence conditions in the same auto-evidence audit;
    - adds surface-level leakage and transition summaries.
- Local validation:
  - `python -m py_compile scripts/run_peer_exposure_probe.py scripts/audit_peer_auto_evidence.py`;
  - helper check confirmed exact answer redaction on sentence-final numbers;
  - MATH dry-run selected the same random8 cases as the prior run.
- Runtime:
  - A800_2 reached through direct SSH because local `A800_2` alias was absent;
  - A800_2 GPU `1`, temporary vLLM port `8025`, Qwen2.5-7B-Instruct served as
    `qwen2.5-7b-peer-redacted`;
  - stopped the temporary service after the runs and confirmed port `8025` was
    closed and GPU `1` returned to idle.
- Formal runs:
  - `experiments/20260614-2325-a8002-peer-redacted-evidence-dar-random14/`
  - `experiments/20260614-2330-a8002-peer-redacted-evidence-math-random8/`
  - `experiments/20260614-2335-local-peer-redacted-evidence-audit/`
- DAR random14:
  - no-peer: `11/14`;
  - `correct_auto_evidence`: `12/14`;
  - `correct_redacted_evidence`: `12/14`;
  - `correct_rationale`: `13/14`;
  - `wrong_auto_evidence`: `11/14`;
  - `wrong_redacted_evidence`: `9/14`;
  - `wrong_rationale`: `9/14`.
- MATH random8:
  - no-peer: `5/8`, with two no-peer unparseable outputs;
  - `correct_auto_evidence`: `5/8`;
  - `correct_redacted_evidence`: `6/8`;
  - `correct_rationale`: `7/8`;
  - `wrong_auto_evidence`: `5/8`;
  - `wrong_redacted_evidence`: `4/8`;
  - `wrong_rationale`: `5/8`.
- Audit results:
  - joined `88/88` evidence sidecars to downstream revision records;
  - old auto-evidence leakage: `16/44`;
  - answer-redacted evidence leakage: `8/44`;
  - wrong auto-evidence right-to-wrong transitions: `1`;
  - wrong redacted evidence right-to-wrong transitions: `4`;
  - added mechanical target-behavior labels such as
    `copied_wrong_source_answer`, `moved_off_correct_without_source_copy`,
    `repaired_wrong_surface`, and `used_or_copied_correct_source_answer`.
- Main small observations:
  - exact answer redaction reduced obvious leakage but did not make wrong
    evidence safer;
  - redacted correct evidence rescued DAR `78` and MATH `9`;
  - redacted wrong evidence produced harmful relation cases on DAR `4`, DAR
    `65`, DAR `97`, and MATH `47`;
  - DAR `8` remained a recoverable-skeleton case even under wrong evidence.
- Added report:
  - `reports/20260614-peer-redacted-evidence-surface.md`
- Evidence register:
  - added row `E-059`.

## 2026-06-14 Peer Relation-Slot Focus Cards

- Added local focus-card builder:
  - `scripts/build_peer_relation_slot_cards.py`
- Built semantic inspection cards from the redacted-evidence audit:
  - input audit:
    - `experiments/20260614-2335-local-peer-redacted-evidence-audit/cases.jsonl`
  - source runs:
    - `experiments/20260614-2325-a8002-peer-redacted-evidence-dar-random14/`
    - `experiments/20260614-2330-a8002-peer-redacted-evidence-math-random8/`
  - output:
    - `experiments/20260614-2345-local-peer-relation-slot-cards/`
- Focus-card counts:
  - cards: `10`;
  - contact labels:
    - `correct_evidence_rescue`: `3`;
    - `wrong_evidence_harmful_relation`: `5`;
    - `wrong_evidence_recoverable_skeleton`: `2`;
  - transitions:
    - `wrong_to_right`: `5`;
    - `right_to_wrong`: `5`.
- Added manual semantic labels:
  - `experiments/20260614-2345-local-peer-relation-slot-cards/manual_labels.jsonl`
  - label counts:
    - `relation_skeleton`: `correct: 3`, `wrong: 4`, `mixed: 1`,
      `recoverable_wrong: 2`;
    - `numeric_slots`: `correct: 2`, `wrong: 3`, `mixed: 4`,
      `abstract: 1`;
    - `final_slot`: `derivable: 5`, `absent: 4`, `blank: 1`;
    - `answer_copy`: `relation_derived: 3`,
      `relation_derived_not_source_copy: 3`,
      `source_answer_copied_or_derived: 2`, `repaired: 2`.
- Main small observations:
  - all 10 focus cards preserved the target predicate, so the split is not
    whether the target object remained visible;
  - wrong redacted surfaces harmed through wrong rate, duration, average-scope,
    or mixed combinatorics slots, even when the final source answer was absent;
  - recoverable wrong evidence preserved a useful age/time anchor and was
    repaired by the target despite a flawed equation;
  - DAR `65` shows a leakage-audit caveat: source answer `2` appears as a
    coefficient, so the mechanical `source_answer_number_present` label is not
    semantic final-answer leakage.
- Added report:
  - `reports/20260614-peer-relation-slot-cards.md`
- Evidence register:
  - added row `E-060`.

## 2026-06-14 Wrong Redacted Evidence Preserved-Correct Contrast

- Extended local focus-card builder:
  - `scripts/build_peer_relation_slot_cards.py`
    - added optional `--conditions`;
    - added optional `--target-behaviors`.
- Built a contrast packet for cases where wrong redacted evidence did not move
  an already-correct target answer:
  - condition: `wrong_redacted_evidence`;
  - target behavior: `preserved_correct_answer`;
  - output:
    - `experiments/20260614-2355-local-peer-wrong-redacted-preserved-correct-cards/`
- Contrast-card counts:
  - cards: `12`;
  - contact labels:
    - `plain_relation_surface`: `6`;
    - `dense_formula_surface`: `3`;
    - `answer_leak_audit`: `3`.
- Added manual contrast labels:
  - `experiments/20260614-2355-local-peer-wrong-redacted-preserved-correct-cards/manual_contrast_labels.jsonl`
  - rough families:
    - wrong final removed, leaving correct or partial evidence: `6` cases;
    - wrong numeric or role slot rejected/repaired: `4` cases;
    - target predicate or answer-contract guard: `2` cases.
- Main small observations:
  - stable-right under `wrong_redacted_evidence` is not automatically a
    robustness signal;
  - in several cases, answer redaction and evidence compression removed the
    wrong final slot and left a correct or partially correct method surface;
  - the clearest resistance cases are explicit wrong-slot repairs such as
    DAR `76` (`30` students rejected for `40`) and MATH `22` (`24.8` rejected
    for `28.8`);
  - answer-leak flags remain noisy because numbers like equation RHS `0` or
    converted diameter `288` can match the source parsed answer without being
    semantic final-answer leakage.
- Added report:
  - `reports/20260614-peer-wrong-redacted-preserved-correct-contrast.md`
- Evidence register:
  - added row `E-061`.

## 2026-06-15 Peer Redacted Relation-Slot Audit

- Added local merge audit helper:
  - `scripts/audit_peer_relation_slots.py`
  - joins redacted evidence audit rows with manual relation-slot, contrast, and
    non-rescue labels;
  - emits merged records, an unlabeled queue, and summary counts.
- Added non-rescue manual labels:
  - packet:
    - `experiments/20260615-0012-local-peer-redacted-nonrescue-cards/`
  - labels:
    - `experiments/20260615-0012-local-peer-redacted-nonrescue-cards/manual_nonrescue_labels.jsonl`
  - cards: `9`;
  - target behaviors:
    - `preserved_wrong_answer`: `5`;
    - `pre_unparseable_or_unknown`: `2`;
    - `post_unparseable_or_unknown`: `2`.
- Ran the merged redacted relation-slot audit:
  - output:
    - `experiments/20260615-0006-local-peer-redacted-relation-slot-audit/`
  - records: `44`;
  - manual-labeled records: `28`;
  - unlabeled records: `16`.
- Audit helper addendum:
  - `summary.json` now includes machine-checkable coverage fields:
    - `answer_changing_manual_coverage_complete: true`;
    - `answer_changing_records: 7`;
    - `answer_changing_unlabeled_records: 0`;
    - `unlabeled_all_preserved_correct_stable_right: true`;
  - the output directory also includes a compact labeling checklist:
    - `experiments/20260615-0006-local-peer-redacted-relation-slot-audit/labeling_rubric.md`.
- Coverage:
  - all behavior-changing redacted records are now manually covered;
  - the remaining `16` unlabeled rows are all `preserved_correct_answer` /
    `stable_right`.
- Main small observations:
  - behavior-changing `wrong_to_right` cases are covered by correct relation
    surfaces or a recoverable wrong surface;
  - behavior-changing `right_to_wrong` cases are covered by wrong or mixed
    relation/numeric slots;
  - stable-right under wrong redacted evidence remains mixed: wrong final
    removed into a correct/partial surface, wrong slot rejected/repaired,
    target predicate or answer-contract guard, or missing role filled;
  - non-rescue cases show the other edge: correct evidence can be too thin or
    overwritten by the target's prior wrong slot, and dense MATH surfaces can
    stay parse-unknown.
- Added report:
  - `reports/20260615-peer-redacted-relation-slot-audit.md`
- Evidence register:
  - added row `E-062`.

## 2026-06-15 Peer Disjoint MATH Redaction Pressure

- Goal:
  - pressure the redacted relation-slot taxonomy with a neighboring random
    slice, rather than only re-reading the same postcards.
- Remote runtime:
  - machine: A800_2 through direct SSH;
  - GPU: `2`;
  - temporary vLLM port: `8026`;
  - model: Qwen2.5-7B-Instruct served as `qwen2.5-7b-peer-neighbor` and then
    `qwen2.5-7b-peer-disjoint`;
  - stopped the temporary services after use and confirmed GPU `2` returned to
    idle.
- First neighbor attempt:
  - DAR seed `61422`:
    - `experiments/20260615-0008-a8002-peer-redacted-evidence-dar-neighbor14/`
    - selected the same 14 cases as the earlier DAR run, so it is not a true
      neighboring slice;
  - MATH seed `61422`:
    - `experiments/20260615-0012-a8002-peer-redacted-evidence-math-neighbor8/`
    - selected some new cases, but behavior-changing cards were still the old
      MATH cases `9` and `47`.
- Dry-ran MATH seeds and selected disjoint seed `61502`, which excludes old
  behavior-changing MATH cases `9` and `47`.
- Disjoint MATH run:
  - `experiments/20260615-0028-a8002-peer-redacted-evidence-math-disjoint8/`
  - cases: `1`, `10`, `22`, `26`, `33`, `38`, `41`, `42`;
  - no-peer: `7/8`;
  - `correct_auto_evidence`: `6/8`, with 1 right-to-wrong;
  - `correct_redacted_evidence`: `7/8`, no answer-changing transitions;
  - `wrong_auto_evidence`: `6/8`, with 1 right-to-wrong;
  - `wrong_redacted_evidence`: `7/8`, no answer-changing transitions.
- Local audit:
  - `experiments/20260615-0034-local-peer-disjoint-math-redacted-audit/`
  - `auto_evidence`: `16` records, `2` right-to-wrong;
  - `answer_redacted_evidence`: `16` records, `0` right-to-wrong.
- Added case-10 surface packet:
  - `experiments/20260615-0040-local-peer-disjoint-math-case10-surface/`
  - `manual_case10_labels.jsonl`
- Main small observations:
  - this disjoint MATH slice bounds the earlier observation that wrong
    redacted evidence was more harmful;
  - in case `10`, `wrong_auto_evidence` explicitly preserved the wrong final
    value `3`, and the target deferred to it after recomputing `2`;
  - `wrong_redacted_evidence` removed that wrong final slot, leaving a
    repairable algebra route, so the target stayed at `2`;
  - `correct_auto_evidence` also caused a right-to-wrong by producing a
    substitution surface that the target mutated into a sign/denominator error.
- Added report:
  - `reports/20260615-peer-disjoint-math-redaction-pressure.md`
- Evidence register:
  - added row `E-064`.

## 2026-06-15 Research Story Synthesis Skill

- Added the third independent project top-level skill:
  - `skills/research-story-synthesis/SKILL.md`
- Purpose:
  - synthesize bounded research stories, idea memos, mentor updates, and
    contribution shapes from existing evidence;
  - keep synthesis late, artifact-grounded, and caveated;
  - avoid turning selected runs or manual labels into population claims.
- Updated top-level project references:
  - `README.md`
  - `docs/README.md`
  - `project_intake.md`
  - `skills/reproduction-first-research/SKILL.md`
- Current top-level skill split:
  - `reproduction-first-research`: contact with runnable systems, logs,
    traces, failures, and small variations;
  - `research-story-synthesis`: late bounded story synthesis from reports,
    evidence rows, run artifacts, and literature pressure;
  - `repro-friction-memory`: reusable rules for recurring reproduction
    blockers.

## 2026-06-15 Peer Redacted Neighbor Repeat

- Ran neighboring redacted-evidence pressure checks on A800_2:
  - reused task-local vLLM service `qwen2.5-7b-peer-neighbor` on port `8026`;
  - GPU `2`;
  - copied outputs back locally:
    - `experiments/20260615-0008-a8002-peer-redacted-evidence-dar-neighbor14/`
    - `experiments/20260615-0012-a8002-peer-redacted-evidence-math-neighbor8/`
    - `experiments/20260615-0020-a8002-peer-redacted-neighbor-math-random8/`
  - after the jobs completed, port `8026` was closed and GPU `2` returned to
    idle.
- DAR note:
  - changing sample seed did not create a new slice because the saved DAR source
    only exposed the same `14` usable disagreement cases;
  - neighbor DAR reproduced the same broad redacted behavior:
    - `correct_redacted_evidence`: `12/14`, `1` wrong-to-right;
    - `wrong_redacted_evidence`: `9/14`, `3` right-to-wrong and `1`
      wrong-to-right.
- MATH neighbor:
  - full-condition seed `61422`:
    - cases: `9`, `15`, `24`, `26`, `33`, `38`, `41`, `47`;
    - `correct_redacted_evidence`: `5/8`, `1` wrong-to-right;
    - `wrong_redacted_evidence`: `3/8`, `1` right-to-wrong.
  - minimal seed `61521`:
    - cases: `1`, `10`, `22`, `24`, `33`, `38`, `41`, `47`;
    - `wrong_redacted_evidence`: `5/8`, `1` wrong-to-right and no
      right-to-wrong.
- Added local repeat comparison helper:
  - `scripts/compare_peer_redacted_repeats.py`
  - output:
    - `experiments/20260615-0036-local-peer-redacted-repeat-variability/`
- Local audit sidecars:
  - full neighbor redacted audit:
    - `experiments/20260615-0020-local-peer-neighbor-redacted-audit/`
    - `experiments/20260615-0028-local-peer-redacted-neighbor-audit/`
  - full neighbor focus cards:
    - `experiments/20260615-0022-local-peer-neighbor-relation-slot-cards/`
  - minimal MATH neighbor audit:
    - `experiments/20260615-0024-local-peer-redacted-neighbor-math-audit/`
- Repeat comparison:
  - repeated case/condition pairs: `46`;
  - variable post-answer/transition pairs: `2`;
  - both were MATH case `47`, under `correct_redacted_evidence` and
    `wrong_redacted_evidence`;
  - evidence text did not vary for those two pairs, but parsed post answers and
    transitions did.
- Main small observation:
  - MATH `47` is a repeatability sentinel: the same wrong redacted combinatorics
    surface moved `28800 -> 14400` in two full-condition runs, but moved
    `14400 -> 28800` in the minimal seed `61521` run.
- Added report:
  - `reports/20260615-peer-redacted-neighbor-repeat.md`
- Evidence register:
  - added row `E-063`.

## 2026-06-15 Research Story Synthesis Taste Revision

- Revised `skills/research-story-synthesis/SKILL.md` after user feedback that
  the first version was too generic and not close enough to the intended paper
  taste.
- New core distinction:
  - `solid`: a theory- or observation-grounded root-cause story that gives the
    reader a "that is why the previous method failed" insight;
  - `novel`: a higher-threshold story that makes the reader feel that the work
    opens an unexpected way to frame or solve the problem;
  - `known limitation`: an expected or already-known failure that should not be
    inflated into a contribution.
- Added the A/B/C paper spine:
  - prior approach `A` fails;
  - diagnosed cause `B` explains the failure;
  - proposed method `C` targets `B`;
  - experiments must show both performance gain and reduction of `B`.
- Updated:
  - `skills/research-story-synthesis/agents/openai.yaml`
  - `README.md`
  - `docs/README.md`
  - `project_intake.md`

## 2026-06-15 Peer Slot-Control MATH12 Pressure

- Added deterministic slot-control peer surfaces to:
  - `scripts/run_peer_exposure_probe.py`
  - schema bumped to `acr.peer_exposure.v0.5`.
- Added audit helper:
  - `scripts/audit_peer_slot_control.py`
  - reads a completed peer-exposure run directory and emits
    `slot_control_audit.json` plus `slot_transition_cards.jsonl`.
- Remote preflight:
  - machine: A800_2 through direct SSH;
  - GPU `3`;
  - port `8028`;
  - model: Qwen2.5-7B-Instruct served as `qwen2.5-7b-peer-slot`;
  - vLLM log:
    - remote: `/data/xuhaoming/yfy/research_workspace/logs/peer-slot-vllm-20260615_1010.log`;
  - stopped the temporary service after the run and confirmed GPU `3`
    returned to idle.
- Ran slot-control pressure over all available MATH50 mixed-correctness
  candidates from the saved MAD-MM trace:
  - output:
    - `experiments/20260615-1010-a8002-peer-slot-control-math12/`
  - cases: `1`, `9`, `10`, `15`, `22`, `24`, `26`, `33`, `38`, `41`, `42`,
    `47`;
  - records: `132`;
  - auto-evidence extraction calls: `0`.
- Conditions:
  - final-answer slot: `correct_answer_only`, `wrong_answer_only`;
  - full rationale reference: `correct_rationale`, `wrong_rationale`;
  - explicit final-answer slot blanked:
    `correct_redacted_rationale`, `wrong_redacted_rationale`;
  - numeric tokens masked:
    `correct_number_masked_rationale`, `wrong_number_masked_rationale`;
  - equation / number-bearing surface:
    `correct_equation_surface`, `wrong_equation_surface`.
- Main counts:
  - no-peer: `8/12`, with `3` unparseable;
  - `correct_answer_only`: `10/12`, `1` wrong-to-right;
  - `correct_rationale`: `10/12`, `1` wrong-to-right;
  - `correct_redacted_rationale`: `9/12`, no answer-changing transitions;
  - `correct_number_masked_rationale`: `7/12`, `1` right-to-wrong;
  - `wrong_answer_only`: `7/12`, `1` right-to-wrong;
  - `wrong_redacted_rationale`: `7/12`, `1` right-to-wrong;
  - `wrong_equation_surface`: `7/12`, `1` right-to-wrong;
  - `wrong_rationale`: `8/12`, no right-to-wrong;
  - `wrong_number_masked_rationale`: `8/12`, no right-to-wrong.
- Added sidecars:
  - `experiments/20260615-1010-a8002-peer-slot-control-math12/slot_control_audit.json`
  - `experiments/20260615-1010-a8002-peer-slot-control-math12/slot_transition_cards.jsonl`
- Main small observations:
  - MATH `47` remains the key harmful-slot sentinel:
    `wrong_answer_only` moved `28800 -> 14400`, while
    `wrong_redacted_rationale` and `wrong_equation_surface` moved
    `28800 -> 1152`;
  - wrong number/role surfaces can matter beyond the final-answer slot, because
    `wrong_number_masked_rationale` stayed correct on MATH `47`;
  - MATH `26` shows the opposite boundary: `correct_number_masked_rationale`
    moved `156 -> 75`, so stripping numeric slots can itself create an
    unnatural harmful prompt surface;
  - MATH `9` was rescued by `correct_answer_only` and `correct_rationale`, but
    not by correct redacted, masked, or equation-only surfaces.
- Added report:
  - `reports/20260615-peer-slot-control-math12.md`
- Evidence register:
  - added row `E-065`.

## 2026-06-15 Peer Probe Script Decoupling

- Split pure helper code out of the monolithic peer-exposure runner:
  - `scripts/peer_probe/io_utils.py`: JSON / JSONL helpers;
  - `scripts/peer_probe/answers.py`: answer normalization, parsing,
    correctness, transition labels, and terminal-state parsing;
  - `scripts/peer_probe/surfaces.py`: peer-surface condition constants,
    answer-only/full-rationale/relation/auto-evidence/slot-control surface
    construction;
  - `scripts/peer_probe/run_notes.py`: generic experiment README renderer.
- Kept `scripts/run_peer_exposure_probe.py` as the backwards-compatible CLI
  entry point.
- Added reusable slot-control audit script:
  - `scripts/audit_peer_slot_control.py`
  - regenerated:
    - `experiments/20260615-1010-a8002-peer-slot-control-math12/slot_control_audit.json`
    - `experiments/20260615-1010-a8002-peer-slot-control-math12/slot_transition_cards.jsonl`
- Documentation boundary tightened in:
  - `docs/README.md`
  - run facts and commands -> experiment README;
  - chronological facts -> project log;
  - machine-readable joins -> experiment sidecars;
  - bounded interpretation -> reports;
  - durable claims -> evidence register.
- Validation:
  - `py_compile` passed for the peer-exposure runner, slot-control audit
    helper, and all `scripts/peer_probe/` modules;
  - MAD-MM/MATH dry-run selected the same 12 slot-control cases;
  - DAR/GSM8K dry-run selected the existing default six-case order;
  - regenerated slot-control audit files matched the checked-in sidecars.
- Friction memory:
  - added a local PowerShell inline-Python rule to
    `skills/repro-friction-memory/SKILL.md` after a bash-style heredoc failed.

## 2026-06-15 Peer Slot-Control Outside Check

- Ran a narrow outside-check pass before naming the MATH12 slot-control
  observation as a mechanism.
- Checked:
  - local `ArXiv_Daily_Digest` radar;
  - recent public papers around peer influence, conformity, sycophancy,
    groupthink, hidden-profile tasks, debate failure modes, shared context, and
    decision-aware context compression.
- Added bounded report:
  - `reports/20260615-peer-slot-control-outside-check.md`
- Updated reading queue with pressure hits:
  - identity-bias/anonymization;
  - cost-of-consensus / contextual-fragility;
  - Talk Isn't Always Cheap;
  - Kairos peer-pressure benchmark;
  - BenchForm conformity benchmark;
  - Hidden Profile tasks;
  - Can LLM Agents Really Debate?;
  - Decentralized MAS with Shared Context;
  - Decision-Aware Memory Cards.
- Current interpretation:
  - slot-control is not ready as a paper story or novelty claim;
  - it is a useful diagnostic handle inside an already active public
    peer-influence / conformity / debate-process-loss neighborhood;
  - next useful contact is a larger MATH disagreement pool plus utility,
    resistance, robustness, and source-identity/anonymization controls.

## 2026-06-15 Typed Public-State Candidate

- Tried to sharpen the peer slot-control observations into an explicit
  candidate idea instead of another local probe.
- Added typed public-state surfaces to the peer-exposure runner:
  - `correct_typed_public_state`;
  - `wrong_typed_public_state`;
  - implemented in `scripts/peer_probe/surfaces.py`.
- Added source-identity control to the runner:
  - `--peer-source-mode named|anonymous`;
  - implemented in `scripts/run_peer_exposure_probe.py`.
- Added local preview builder:
  - `scripts/build_typed_public_state_preview.py`
  - output:
    - `experiments/20260615-local-typed-public-state-preview/`
- Preview over the 12 MATH slot-control source cases:
  - records: `24`;
  - source identity hidden in all typed records;
  - mechanical source-answer containment remains in `8/12`
    `correct_typed_public_state` records and `6/12`
    `wrong_typed_public_state` records;
  - this makes typed public state a diagnostic surface, not a leakage-free
    method.
- Added synthesis memo:
  - `reports/20260615-typed-public-state-candidate.md`
- Candidate spine:
  - standard peer messages collapse source identity, final-answer authority,
    target predicate, relation skeleton, and numeric/role slots into one
    natural-language blob;
  - field-level public-state controls may be a sharper reliability object than
    answer redaction or message compression alone.
- Validation:
  - `py_compile` passed for the runner, preview builder, and peer-surface
    helpers;
  - dry-run accepted typed public-state conditions over the same 12 MATH cases;
  - sample anonymous prompt construction confirmed `Agent*` labels can be
    hidden while preserving the original source in metadata.

## 2026-06-15 Typed Public-State GPU Check

- Discarded a local CPU Qwen2.5-0.5B smoke as non-evidence:
  - local cache model loaded and generated;
  - on the MATH12 no-peer baseline scan, `11/12` outputs were unparseable;
  - this was useful only for plumbing and should not be used as a research
    signal.
- Synced typed-public-state runner changes to A800_2:
  - `scripts/run_peer_exposure_probe.py`;
  - `scripts/peer_probe/`;
  - `scripts/build_typed_public_state_preview.py`.
- Started temporary vLLM on A800_2:
  - GPU: `2`;
  - port: `8029`;
  - model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`;
  - served model name: `qwen2.5-7b-typed-state`;
  - remote log:
    `/data/xuhaoming/yfy/research_workspace/logs/typed-state-vllm-20260615_1118.log`;
- Ran a 3-case smoke first:
  - output:
    `experiments/20260615-1119-a8002-typed-public-state-mini3/`;
  - cases: `9`, `26`, `47`;
  - key signal: on case `47`, `wrong_equation_surface` moved
    `28800 -> 1152`, while `wrong_typed_public_state` kept `28800`.
- Ran the full saved MATH12 typed-public-state packet:
  - output:
    `experiments/20260615-1124-a8002-typed-public-state-math12-anon/`;
  - records: `132`;
  - peer source mode: `anonymous`;
  - no-peer baseline: `8/12`, with `3` unparseable.
- Main counts:
  - `correct_answer_only`: `10/12`, `1` wrong-to-right;
  - `correct_rationale`: `10/12`, `1` wrong-to-right;
  - `correct_typed_public_state`: `8/12`, no rescues;
  - `wrong_answer_only`: `7/12`, `1` right-to-wrong;
  - `wrong_redacted_rationale`: `7/12`, `1` right-to-wrong;
  - `wrong_equation_surface`: `7/12`, `1` right-to-wrong;
  - `wrong_typed_public_state`: `8/12`, no parseable right-to-wrong, but
    `4` unknown/unparseable rows.
- Case-level signal:
  - MATH `47` is the key sentinel:
    - `wrong_answer_only`: `28800 -> 14400`;
    - `wrong_redacted_rationale`: `28800 -> 1152`;
    - `wrong_equation_surface`: `28800 -> 1152`;
    - `wrong_typed_public_state`: `28800 -> 28800`.
- Added report:
  - `reports/20260615-typed-public-state-math12-gpu.md`
- Updated:
  - `reports/20260615-typed-public-state-candidate.md`;
  - `docs/evidence_register.md` (`E-066`, `E-067`).
- Stopped the temporary vLLM service after the run and confirmed GPU `2`
  returned to idle (`4 MiB` used / `81149 MiB` free).

## 2026-06-15 Typed Public-State MATH200 Statistical Pressure

- Built a larger MATH disagreement pool before making a stronger typed-state
  claim:
  - ran MAD-MM naive on `math:200` with Qwen2.5-7B-Instruct;
  - source accuracy: `120/200 = 0.600`;
  - source token count: `1,559,005`;
  - extracted unified trace:
    `experiments/20260615-1151-a8002-typed-public-state-math200-anon/madmm-qwen25-7b-math200-naive-20260615_1142.comm_trace.jsonl`.
- Selected `59` mixed-correctness source cases from the MATH200 trace and
  reran the anonymous peer-exposure diagnostic with:
  - answer-only;
  - full rationale;
  - redacted rationale;
  - equation surface;
  - typed public state;
  - correct and wrong peer variants.
- Output:
  - `experiments/20260615-1151-a8002-typed-public-state-math200-anon/`;
  - `649` records;
  - `59` source cases;
  - temporary vLLM log:
    `experiments/typed-state-math200-vllm-20260615_1150.log`;
  - probe log:
    `experiments/typed-public-state-math200-probe-20260615_1151.log`.
- Added statistical audit helper:
  - `scripts/audit_peer_exposure_statistics.py`;
  - output:
    `experiments/20260615-1151-a8002-typed-public-state-math200-anon/statistical_audit.md`;
    `experiments/20260615-1151-a8002-typed-public-state-math200-anon/statistical_audit.json`.
- Added parser-sensitivity audit helper:
  - `scripts/audit_math_parser_sensitivity.py`;
  - output:
    `experiments/20260615-1151-a8002-typed-public-state-math200-anon/math_parser_sensitivity_audit.md`;
    `experiments/20260615-1151-a8002-typed-public-state-math200-anon/math_parser_sensitivity_audit.json`.
- Main statistical result:
  - no-peer baseline: `37/59 = 0.627`, with `9/59` unparseable;
  - wrong full rationale caused `9/37` right-to-wrong transitions,
    Wilson 95% `[0.134, 0.401]`;
  - wrong typed public state caused `3/37` right-to-wrong transitions,
    Wilson 95% `[0.028, 0.213]`;
  - wrong equation surface also caused `3/37` right-to-wrong transitions;
  - paired exact sign test for `wrong_typed_public_state` over
    `wrong_rationale`: `9` typed-only-correct vs `2`
    rationale-only-correct cases, `p = 0.0654`;
  - paired tests did not show a typed advantage over wrong redacted rationale,
    wrong equation surface, or wrong answer-only.
- Parser-sensitivity check:
  - `21/59` source cases have non-plain-numeric boxed MATH answers under the
    current numeric normalizer;
  - on the remaining `38` plain-numeric cases, wrong full rationale caused
    `6/24` right-to-wrong transitions, while wrong typed public state caused
    `1/24`;
  - paired exact sign test on the plain-numeric subset:
    `6` typed-only-correct vs `1` rationale-only-correct case,
    `p = 0.1250`.
- Utility boundary:
  - `correct_typed_public_state` rescued only `1/13` baseline-wrong cases;
  - `correct_rationale` and `correct_redacted_rationale` each rescued `5/13`.
- Interpretation:
  - the MATH12 sentinel survives as a bounded diagnostic hint, not a broad method
    claim;
  - typed public state seems to remove part of the full-rationale contamination
    channel;
  - it does not yet beat simpler equation or answer controls and loses much of
    the utility of correct rationale.
- Caveat:
  - current MATH answer parsing/normalization is now a major confound for
    symbolic answers, complex values, radicals, and formatting variants; the
    plain-numeric subset keeps the directional typed-vs-full-rationale contrast
    but leaves smaller sample size and wider uncertainty.
- Added report:
  - `reports/20260615-typed-public-state-math200-statistical-pressure.md`.

## 2026-06-15 MATH Semantic Correctness Audit

- Added conservative MATH answer-equivalence helpers:
  - `scripts/peer_probe/math_eval.py`
  - handles common saved-output forms including explicit `{final answer: ...}`,
    boxed gold answers, fractions, mixed numbers, radicals, `pi`, complex `i`,
    symbolic expressions, units, and thousands separators;
  - returns semantic unknown instead of falling back to the last numeric token
    when comparison is not reliable.
- Added semantic re-audit script:
  - `scripts/audit_math_semantic_correctness.py`.
- Recomputed the existing MATH200 typed-public-state peer-exposure results
  without any new model calls:
  - `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_records.jsonl`
  - `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_audit.md`
  - `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_audit.json`
- Semantic audit facts:
  - source-label-reliable cases: `47/59`;
  - numeric-vs-semantic labels over `649` records:
    - `521` unchanged known records;
    - `29` changed known records;
    - `99` semantic-unknown records;
  - all cases:
    - no-peer baseline: `37/59`, with `13/59` semantic unknown;
    - wrong full rationale: `9/37` right-to-wrong;
    - wrong typed public state: `3/37` right-to-wrong;
    - wrong equation surface: `3/37` right-to-wrong;
  - source-label-reliable cases:
    - no-peer baseline: `32/47`, with `8/47` semantic unknown;
    - wrong full rationale: `9/32` right-to-wrong;
    - wrong typed public state: `3/32` right-to-wrong;
    - wrong equation surface: `3/32` right-to-wrong.
- Interpretation update:
  - semantic re-audit does not overturn the bounded MATH200 result;
  - typed public state still reduces the full-rationale contamination channel
    relative to wrong full rationale;
  - typed public state still does not beat equation surface and still has low
    utility under correct peer information;
  - remaining semantic unknowns and source-label-unreliable cases should be
    inspected before another GPU run.
- Updated:
  - `reports/20260615-typed-public-state-math200-statistical-pressure.md`
  - `experiments/20260615-1151-a8002-typed-public-state-math200-anon/README.md`
  - `docs/evidence_register.md` (`E-068`, `E-069`, `E-070`)

## 2026-06-15 Slot-Level Story And Benchmark Language Revision

- Incorporated external story-pressure analysis from:
  - PACT / action-state communication;
  - DeLM / shared verified context;
  - Decision-Aware Memory Cards;
  - Cost of Consensus;
  - Identity Bias / anonymization;
  - KAIROS peer-pressure benchmark;
  - HiddenBench / Hidden Profile tasks.
- Main story revision:
  - downgraded "typed public state" from possible method/novelty claim to a
    diagnostic surface;
  - reframed the live candidate as slot-level peer-message failure diagnosis:
    relation skeleton, numeric/role slots, target predicate, equation surface,
    source identity, and final-answer authority may carry different revision
    hazards and utilities.
- Benchmark-language alignment:
  - MATH12/MATH200 should be described as peer-influence diagnostics on math
    reasoning cases, not as general multi-agent communication benchmarks;
  - KAIROS/Identity Bias vocabulary fits current peer-exposure probes:
    utility, resistance, robustness, peer-answer adoption, conformity,
    obstinacy, source identity bias;
  - PACT/HotpotQA/2Wiki/MuSiQue vocabulary fits split-evidence public-state
    handoff;
  - HiddenBench vocabulary fits distributed-information integration and
    communication-necessity claims;
  - DeLM/Memory Cards vocabulary fits shared verified context and agentic
    workflow settings.
- Updated:
  - `reports/20260615-typed-public-state-candidate.md`
  - `reports/20260615-peer-slot-control-outside-check.md`
  - `papers/reading_queue.md`
  - `docs/evidence_register.md` (`E-066`, `E-071`)

## 2026-06-15 Peer Influence Protocol Audit

- Added KAIROS-style protocol audit helper:
  - `scripts/audit_peer_influence_protocol.py`
  - reads semantic peer-exposure records without rerunning the model;
  - computes utility, resistance, harm, robustness, semantic-unknown rate, and
    saved peer-answer adoption;
  - reports both all cases and source-label-reliable cases.
- Extended peer-source controls in `scripts/run_peer_exposure_probe.py`:
  - `--peer-source-mode randomized`;
  - replaces displayed peer labels with deterministic seed-based aliases while
    preserving `original_source` metadata;
  - this enables the next named / anonymous / randomized source-content
    disentanglement packet without changing peer content.
- Ran the protocol audit over the MATH200 semantic records:
  - input:
    `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_records.jsonl`;
  - outputs:
    `experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.md`;
    `experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.json`.
- Source-label-reliable protocol readout:
  - wrong full rationale is high-harm: `9/32`;
  - wrong typed public state and wrong equation surface tie at `3/32`;
  - correct typed public state has low utility: `1/7`, versus `5/7` for correct
    full rationale.
- Added bounded synthesis report:
  - `reports/20260615-slot-level-peer-influence-protocol.md`.
- Updated:
  - `reports/20260615-typed-public-state-candidate.md`;
  - `reports/20260615-typed-public-state-math200-statistical-pressure.md`;
  - `experiments/20260615-1151-a8002-typed-public-state-math200-anon/README.md`;
  - `docs/evidence_register.md` (`E-072`).

## 2026-06-15 Peer Source-Label MATH200 Packet

- Ran the next source/content disentanglement packet required by the
  post-pressure story:
  - same MATH200 source cases as the typed-public-state run;
  - same peer content and condition set;
  - varied only displayed source labels.
- Added runner capability before launching:
  - `scripts/run_peer_exposure_probe.py` supports
    `--peer-source-mode named|anonymous|randomized`;
  - `randomized` uses deterministic seed-based aliases and preserves
    `original_source` metadata.
- Added remote launcher:
  - `scripts/run_peer_source_label_packet_a8002.sh`.
- Remote execution:
  - machine: A800_2;
  - GPU: `5`;
  - temporary vLLM port: `8031`;
  - model: Qwen2.5-7B-Instruct served as `qwen2.5-7b-source-label`;
  - temporary service was stopped after the run and GPU `5` returned to idle.
- New run outputs:
  - `experiments/20260615-1404-a8002-source-label-math200-named/`
  - `experiments/20260615-1404-a8002-source-label-math200-randomized/`
  - each has `649` peer-exposure records plus semantic and protocol audits.
- Added packet comparison helper:
  - `scripts/audit_peer_source_label_packet.py`
  - output:
    `experiments/20260615-1404-a8002-source-label-math200-packet/source_label_packet_audit.md`;
    `experiments/20260615-1404-a8002-source-label-math200-packet/source_label_packet_audit.json`.
- Main source-label-reliable readout:
  - wrong full rationale harm:
    anonymous `9/32`, named `9/32`, randomized `8/32`;
  - wrong typed public state harm:
    anonymous `3/32`, named `3/32`, randomized `3/32`;
  - correct typed public state utility:
    anonymous `1/7`, named `1/7`, randomized `0/7`.
- Interpretation:
  - source-label variation does not explain away the main field-level harm
    pattern;
  - typed public state remains a diagnostic surface with low utility, not a
    method win;
  - this is not an identity-bias benchmark because named labels are simple
    agent labels rather than authority titles or social identities.
- Added report:
  - `reports/20260615-peer-source-label-math200-packet.md`.
- Evidence register:
  - added row `E-073`.

## 2026-06-15 MATH200 Peer Claim Hygiene

- Added offline claim-hygiene packet builder:
  - `scripts/build_peer_claim_hygiene_packet.py`;
  - reads saved MATH200 semantic peer-exposure records and source-label audits;
  - does not run a model or recompute correctness.
- Generated local packet:
  - `experiments/20260615-local-math200-peer-claim-hygiene/README.md`;
  - `claim_hygiene_summary.json`;
  - `semantic_unknown_records.jsonl`;
  - `semantic_unknown_cases.jsonl`;
  - `source_label_unreliable_cases.jsonl`;
  - `source_label_sensitive_rows.jsonl`;
  - `baseline_mode_drift_rows.jsonl`;
  - `field_label_packet.jsonl`.
- Main hygiene facts:
  - `99/649` anonymous MATH200 records remain semantic unknown across `16/59`
    cases;
  - `12/59` source cases have semantically unreliable saved correct/wrong peer
    labels;
  - the clean claim-bearing subset has `37/59` cases and `407` records;
  - no-peer baseline rows have `0` drift across anonymous, named, and randomized
    source-label modes.
- Clean subset readout:
  - wrong full rationale harm remains `9/31`;
  - wrong typed public state and wrong equation surface each have `3/31` harm;
  - correct typed public state has `1/6` utility versus `4/6` for correct full
    rationale.
- Added answer-only surface audit:
  - `experiments/20260615-local-math200-peer-claim-hygiene/answer_only_surface_issue_rows.jsonl`;
  - anonymous run has `27` semantic mismatches and `7` unknown-equivalence
    answer-only rows out of `118`;
  - the clean subset has `15` semantic-mismatch case/condition pairs, repeated
    across the three source-label modes as `45` rows.
- Added bounded report:
  - `reports/20260615-math200-peer-claim-hygiene.md`.
- Added manual seed labels for the `21` clean anonymous right-to-wrong rows:
  - `experiments/20260615-local-math200-peer-claim-hygiene/manual_seed_labels.jsonl`;
  - `11/21` labeled harms occur with the final-answer slot hidden;
  - `18/21` are labeled as wrong relation skeletons;
  - `14/21` are labeled as wrong numeric/role slots.
- Added source-label-sensitive seed labels for the `23` clean rows:
  - `experiments/20260615-local-math200-peer-claim-hygiene/manual_source_label_sensitive_seed_labels.jsonl`;
  - categories are `9` rescue-lost, `6` harm-removed, `6` harm-added, and `2`
    rescue-added;
  - `15/23` have the final-answer slot hidden;
  - `1/23` is marked as an answer-only parser-surface confound.
- Evidence register:
  - added rows `E-074`, `E-075`, `E-076`, and `E-077`.

## 2026-06-15 Raw Answer-Only Surface Repair

- Added a raw final-answer text extractor:
  - `scripts/peer_probe/answers.py`
  - `extract_raw_final_answer_text(...)`.
- Added future peer-exposure conditions:
  - `correct_raw_answer_only`;
  - `wrong_raw_answer_only`;
  - implemented in `scripts/peer_probe/surfaces.py`.
- Kept legacy `correct_answer_only` / `wrong_answer_only` unchanged so existing
  MATH200 artifacts remain reproducible.
- Updated audit/protocol scripts to recognize the new raw answer-only
  conditions:
  - `scripts/audit_peer_influence_protocol.py`;
  - `scripts/audit_math_semantic_correctness.py`;
  - `scripts/audit_peer_exposure_statistics.py`;
  - `scripts/audit_peer_source_label_packet.py`.
- Added local preview builder:
  - `scripts/build_raw_answer_only_preview.py`.
- Generated local preview packet without model calls:
  - `experiments/20260615-local-raw-answer-only-preview/`;
  - over the saved MATH200 source cases, legacy answer-only rows are
    `84/118` equivalent to raw peer answers, `27/118` semantic mismatches, and
    `7/118` unknown-equivalence;
  - spot checks now show raw symbolic answers such as `2\sqrt{3}`,
    `1 - 12i`, and `8\pi - 16` instead of old numeric-parser slots `3`,
    `12`, and `16`.
- Added bounded report:
  - `reports/20260615-raw-answer-only-surface-repair.md`.
- Validation:
  - `py_compile` passed for the updated runner, surface helpers, audit scripts,
    and preview builder.
- Interpretation:
  - this repairs a future control surface only;
  - no model was rerun;
  - existing MATH200 answer-only rows remain a legacy/parser-surface diagnostic,
    not clean final-answer-authority evidence.

## 2026-06-15 Peer Field-Label Coverage Summary

- Added manual label summary helper:
  - `scripts/summarize_peer_field_labels.py`;
  - reads the MATH200 claim-hygiene `field_label_packet.jsonl` plus existing
    manual seed labels;
  - does not infer new labels.
- Generated sidecars under:
  - `experiments/20260615-local-math200-peer-claim-hygiene/`
- Outputs:
  - `manual_label_summary.md`;
  - `manual_label_summary.json`;
  - `manual_unlabeled_rows.jsonl`;
  - `merged_manual_seed_labels.jsonl`;
  - `merged_manual_source_label_sensitive_seed_labels.jsonl`.
- Coverage:
  - field-label packet rows: `97`;
  - unique labeled seed rows: `44`;
  - unlabeled rows: `53`;
  - unlabeled behavior-changing rows: `15`;
  - unlabeled source-label-sensitive rows: `38`.
- Seed-label readout remains bounded:
  - anonymous behavior labels: `18/21` wrong relation skeletons and `14/21`
    wrong numeric/role slots;
  - source-label-sensitive seed labels: `15/23` final-answer authority hidden
    and `1/23` parser-surface confound.
- Interpretation:
  - current labels support a bounded field-level diagnostic claim;
  - they are not enough for a population taxonomy;
  - if MATH is continued, the next manual pass should start from
    `manual_unlabeled_rows.jsonl`, especially the remaining `15`
    behavior-changing rows.

## 2026-06-15 Workspace Cleanup

- Removed low-value local/runtime artifacts that do not carry project evidence:
  - `.vscode/settings.json`, because editor-local submodule preferences should
    not be part of the research record;
  - root-level copied vLLM/probe logs under `experiments/*.log`, keeping run
    directories, summaries, manifests, reports, and remote log paths as the
    source of truth;
  - ignored `.tmp/` verification outputs, script bytecode caches, and the local
    ignored MAD-MM `raw_results/` copy already summarized by derived artifacts;
  - obsolete card packet
    `experiments/20260615-0036-local-peer-disjoint-math-relation-slot-cards/`,
    which was superseded by
    `experiments/20260615-0040-local-peer-disjoint-math-case10-surface/`.
- Added `.gitignore` coverage for future root-level `experiments/*.log` copies.

## 2026-06-15 PACT Public-State Field Bridge

- Added an offline bridge audit:
  - `scripts/audit_pact_public_state_field_bridge.py`;
  - reads PACT offset50 `case_atlas_focus_cases.jsonl`, the ten manual
    public-state-gold labels, and the target-slot drift cases.
- Generated a local bridge packet:
  - `experiments/20260615-local-pact-public-state-field-bridge/summary.json`;
  - `experiments/20260615-local-pact-public-state-field-bridge/bridge_cases.jsonl`;
  - `experiments/20260615-local-pact-public-state-field-bridge/bridge_packet.md`.
- Added report:
  - `reports/20260615-pact-public-state-field-bridge.md`.
- Counts over the 28 PACT focus cases:
  - `6` positive contract rescues;
  - `12` final-answer commitment failures;
  - `2` target-contract failures;
  - `2` target/final-alignment failures;
  - `5` likely evidence-carriage failures;
  - `1` diagnostic string false positive.
- Interpretation:
  - typed public state should stay demoted to a diagnostic surface;
  - the larger object is field-level public-state reliability:
    target contract preservation, evidence carriage, and final-answer
    commitment;
  - the next bold move should be a split-evidence/public-state task packet,
    not another small typed/MATH variant.

## 2026-06-15 PACT Public-State Field Packet

- Added packet builder:
  - `scripts/build_pact_public_state_field_packet.py`.
- Generated model-ready packet:
  - `experiments/20260615-local-pact-public-state-field-packet/field_packet.jsonl`;
  - `experiments/20260615-local-pact-public-state-field-packet/summary.json`;
  - `experiments/20260615-local-pact-public-state-field-packet/README.md`;
  - `experiments/20260615-local-pact-public-state-field-packet/scoring_plan.md`.
- Packet shape:
  - `50` HotpotQA offset50 samples;
  - `2` source runs: baseline and final-answer contract;
  - `5` field-visibility conditions per source/sample;
  - `500` prompt rows total.
- Field conditions:
  - question + public state + final-answer candidate;
  - question + public state without final answer;
  - question + evidence without public target;
  - frozen question-derived target + evidence;
  - public target + evidence with original question hidden.
- Added evaluator:
  - `scripts/evaluate_pact_public_state_field_packet.py`;
  - accepts future model outputs keyed by `packet_id`;
  - slices by source run, condition, bridge layer/family, and target-slot
    candidate status.
- Added OpenAI-compatible packet runner:
  - `scripts/run_pact_public_state_field_packet.py`;
  - writes `outputs.jsonl`, optional `failures.jsonl`, and `manifest.json`;
  - supports condition/source/sample filters plus resume mode.
- Smoke evaluation:
  - `experiments/20260615-local-pact-public-state-field-packet/official-final-answer-smoke/`;
  - official-source scoring reproduces known source-run scores:
    baseline EM `0.520`, F1 `0.647`;
    final-contract EM `0.560`, F1 `0.743`.
- Added report:
  - `reports/20260615-pact-public-state-field-packet.md`.
- Evidence register:
  - added `E-081`.

## 2026-06-15 PACT Public-State Field Qwen2.5-14B Pressure

- Added A800_2 packet launcher:
  - `scripts/run_pact_public_state_field_packet_a8002.sh`.
- Ran the full public-state field packet on A800_2:
  - run id `20260615-1655-a8002-pact-public-state-field-qwen25-14b`;
  - Qwen2.5-14B-Instruct served by vLLM on GPU `7`;
  - `500/500` rows completed, `0` failed.
- Synced run artifacts locally:
  - `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/outputs.jsonl`;
  - `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/manifest.json`;
  - `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/evaluation/summary.json`;
  - `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/evaluation/summary.md`.
- Added paired delta audit:
  - `scripts/analyze_pact_public_state_field_results.py`;
  - `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/field_delta_audit/delta_summary.json`;
  - `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/field_delta_audit/delta_summary.md`;
  - `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/field_delta_audit/delta_cards.jsonl`.
- Main condition scores:
  - question + evidence without public target: EM `0.590`, F1 `0.725`;
  - frozen question-derived target + evidence: EM `0.580`, F1 `0.734`;
  - question + public state + final candidate: EM `0.550`, F1 `0.710`;
  - question + public state without final candidate: EM `0.520`, F1 `0.688`;
  - public target + evidence with original question hidden: EM `0.440`, F1 `0.591`.
- Paired deltas against `question_plus_public_state_no_final`:
  - hiding the public target: `11` rescues, `4` regressions;
  - freezing the question-derived target: `10` rescues, `4` regressions;
  - hiding the question while keeping public target: `2` rescues, `10` regressions;
  - showing final-answer candidate: `6` rescues, `3` regressions, candidate-copy rate `0.740`.
- Added run README:
  - `experiments/20260615-1655-a8002-pact-public-state-field-qwen25-14b/README.md`.
- Added report:
  - `reports/20260615-pact-public-state-field-qwen25-14b-pressure.md`.
- Evidence register:
  - added `E-082`.
- Interpretation:
  - the useful object is field-level public-state reliability, not typed public
    state as a method name;
  - public target fields are not reliable task contracts by themselves;
  - the next intervention should verify target/evidence/final-answer licensing
    before exposing public fields.

## 2026-06-15 PACT Field-Contract Quarantine

- Added a first field-contract verifier and packet builder:
  - `scripts/build_pact_field_contract_verifier_packet.py`.
- Generated verifier artifacts:
  - `experiments/20260615-local-pact-field-contract-verifier/verifier_records.jsonl`;
  - `experiments/20260615-local-pact-field-contract-verifier/verified_packet.jsonl`;
  - `experiments/20260615-local-pact-field-contract-verifier/verified_quarantine_packet.jsonl`;
  - `experiments/20260615-local-pact-field-contract-verifier/summary.json`;
  - `experiments/20260615-local-pact-field-contract-verifier/summary.md`.
- First verifier result:
  - candidate licensing was too permissive (`91/100` candidates shown) and
    underperformed fixed target controls;
  - the useful route was stricter target quarantine:
    hide risky public targets, otherwise replace the public target with a
    question-derived frozen contract, and hide final-answer candidates.
- Offline routing over prior pressure outputs:
  - `verifier_hide_risky_else_freeze`: EM `0.610`, F1 `0.759`;
  - always hide public target: EM `0.590`, F1 `0.725`;
  - always freeze question target: EM `0.580`, F1 `0.734`.
- Ran the target-quarantine packet on A800_2:
  - run id `20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b`;
  - Qwen2.5-14B-Instruct served by vLLM on GPU `7`;
  - `100/100` rows completed, `0` failed.
- Model result:
  - overall EM `0.610`, F1 `0.753`;
  - baseline source run EM `0.600`, F1 `0.728`;
  - final-contract source run EM `0.620`, F1 `0.778`.
- Added paired delta audit:
  - `scripts/analyze_pact_field_contract_quarantine_results.py`;
  - `experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/quarantine_delta_audit/quarantine_delta_summary.json`;
  - `experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/quarantine_delta_audit/quarantine_delta_summary.md`;
  - `experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/quarantine_delta_audit/quarantine_delta_cards.jsonl`.
- Paired deltas:
  - vs original public-state/no-final: `12` rescues, `3` regressions;
  - vs always hidden public target: `5` rescues, `3` regressions;
  - vs always frozen target: `5` rescues, `2` regressions;
  - vs final-answer candidate visible: `11` rescues, `5` regressions.
- Added report:
  - `reports/20260615-pact-field-contract-quarantine.md`.
- Evidence register:
  - added `E-083`.
- Interpretation:
  - target quarantine is now a real live handle;
  - final-answer candidate licensing should be paused;
  - the next verifier should remove dependence on paired target-slot diagnostics
    and add a final-span/granularity check before testing a neighboring slice.

## 2026-06-15 Field-Contract Quarantine External Pressure

- Ran an external collision/pressure scan around the current field-contract
  quarantine result.
- Added report:
  - `reports/20260615-field-contract-quarantine-external-pressure.md`.
- Updated reading queue with field-authority pressure hits:
  - PACT / action-state public communication;
  - AgentSecBench / data-flow versus authority;
  - CaMeL / trusted-query-rooted control flow;
  - ARGUS / provenance-aware decision auditing;
  - Toward Secure LLM Agents / trust boundaries and delegated authority;
  - DeLM / shared verified context;
  - Decision-Aware Memory Cards / typed decision-critical context;
  - context-quarantine terminology collision;
  - State-Centric Decision Process / certified states.
- Evidence register:
  - added `E-084`.
- Deletions from the live story:
  - do not claim novelty as structured public state;
  - do not claim novelty as shared verified context;
  - do not claim novelty as typed context cards;
  - do not claim generic context quarantine;
  - pause final-answer-candidate licensing as a near-term route;
  - stop treating "keep good public targets" as the default policy.
- Surviving narrow claim:
  - public-state handoffs contain authority-bearing fields, not only data;
  - downstream agents should not treat upstream `Action Required` as a task
    contract unless it is grounded back into the original question/user intent.
- Next pressure:
  - build a security-style projection baseline;
  - remove dependence on paired target-slot diagnostics;
  - add a standalone target-authority detector and final-span/granularity
    verifier;
  - test a neighboring HotpotQA slice before calling this a method candidate.

## 2026-06-15 Field-Authority Standalone Projection Setup

- Added a standalone field-authority projection packet builder:
  - `scripts/build_pact_field_authority_projection_packet.py`.
- Added a final-span/granularity audit:
  - `scripts/audit_pact_final_span_granularity.py`.
- Parameterized field packet IDs for neighboring slices:
  - `scripts/build_pact_public_state_field_packet.py --packet-prefix`.
- Generated offset50 standalone/projection artifacts:
  - `experiments/20260615-local-pact-field-authority-projection/summary.json`;
  - `experiments/20260615-local-pact-field-authority-projection/security_projection_packet.jsonl`;
  - `experiments/20260615-local-pact-field-authority-projection/standalone_quarantine_packet.jsonl`.
- Offset50 standalone detector:
  - detector actions: hide `30`, project question root `70`;
  - offline route over already-run outputs: standalone hide-risky/project EM
    `0.560`, below always hiding the public target (`0.590`) and below the
    frozen/security projection control (`0.580`).
- Generated neighboring offset100 field packet:
  - `experiments/20260615-local-pact-public-state-field-packet-offset100/field_packet.jsonl`;
  - `50` samples, `500` prompt rows, sample indices `100` through `149`.
- Generated offset100 field-authority packets:
  - `experiments/20260615-local-pact-field-authority-projection-offset100/security_projection_packet.jsonl`;
  - `experiments/20260615-local-pact-field-authority-projection-offset100/standalone_quarantine_packet.jsonl`;
  - detector actions: hide `35`, project question root `65`.
- Final-span audit over the existing offset50 quarantine run:
  - `experiments/20260615-local-pact-final-span-granularity/summary.json`;
  - `13/100` rows are strict-span or granularity misses, separate from `23`
    content mismatches.
- Added report:
  - `reports/20260615-field-authority-standalone-projection.md`.
- Evidence register:
  - added `E-085`.
- Interpretation:
  - the current standalone lexical detector is not method-ready;
  - the next behavioral pressure should run offset100 security projection and
    standalone quarantine, then score with span/granularity labels.

## 2026-06-15 Field-Authority Offset100 Pressure Runs

- Ran offset100 field-authority projection packet on A800_2:
  - run id `20260615-1805-a8002-pact-field-authority-projection-offset100-qwen25-14b`;
  - packet rows: `200`;
  - completed `200/200`, failed `0`;
  - conditions: `security_projection_question_root_no_final` and
    `standalone_authority_quarantine_no_final`.
- Ran offset100 full field-control packet on A800_2:
  - run id `20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b`;
  - packet rows: `500`;
  - completed `500/500`, failed `0`.
- Main condition scores on offset100:
  - frozen target + evidence: EM `0.560`, F1 `0.698`;
  - security projection: EM `0.510`, F1 `0.661`;
  - public state no final: EM `0.500`, F1 `0.648`;
  - hide public target: EM `0.470`, F1 `0.610`;
  - standalone authority quarantine: EM `0.440`, F1 `0.604`;
  - public state with final candidate: EM `0.430`, F1 `0.575`;
  - public target without question: EM `0.300`, F1 `0.481`.
- Delta audits:
  - against public-state/no-final, frozen target gives `9` rescues and `3`
    regressions;
  - public target without question gives `0` rescues and `20` regressions;
  - final-answer candidate visibility gives `3` rescues and `10` regressions;
  - standalone quarantine loses to security projection (`1` rescue, `8`
    regressions) and frozen target (`0` rescues, `12` regressions).
- Span/granularity audits:
  - field controls: `101/500` strict-span or granularity misses;
  - projection run: `42/200` strict-span or granularity misses.
- Added run READMEs:
  - `experiments/20260615-1805-a8002-pact-field-authority-projection-offset100-qwen25-14b/README.md`;
  - `experiments/20260615-1810-a8002-pact-public-state-field-offset100-qwen25-14b/README.md`.
- Added report:
  - `reports/20260615-field-authority-offset100-pressure.md`.
- Evidence register:
  - added `E-086`.
- Interpretation:
  - retire standalone detector as a near-term method route;
  - keep the narrower field-authority claim: public `Action Required` is not a
    reliable task contract by itself, and question-root projection/frozen target
    remains the strongest current control.

## 2026-06-15 Offset100 Field-Bridge Audit

- Added packet-derived field bridge auditor:
  - `scripts/audit_pact_field_bridge_from_packet.py`.
- Generated offset100 bridge artifacts:
  - `experiments/20260615-local-pact-public-state-field-bridge-offset100/summary.json`;
  - `experiments/20260615-local-pact-public-state-field-bridge-offset100/bridge_cases.jsonl`;
  - `experiments/20260615-local-pact-public-state-field-bridge-offset100/bridge_packet.md`.
- Bridge layer counts over `100` sample/source units:
  - `stable_answer`: `26`;
  - `evidence_or_content`: `25`;
  - `target_authority`: `20`;
  - `final_answer_commitment`: `18`;
  - `target_contract`: `10`;
  - `target_field_ablation`: `1`.
- Added report:
  - `reports/20260615-field-authority-offset100-bridge-audit.md`.
- Evidence register:
  - added `E-087`;
  - updated `E-086` caveat to point to the rebuilt bridge labels.
- Interpretation:
  - field-authority is a live diagnostic handle, not a complete failure
    explanation;
  - the next projection test should be judged by movement in target-authority
    and target-contract units, not only by aggregate EM.

## 2026-06-15 Field-Authority Story Audit

- Added bounded story synthesis:
  - `reports/20260615-field-authority-story-audit.md`.
- Classification:
  - live diagnostic / bounded protocol candidate;
  - not yet a solid paper story;
  - not a novelty story around broad public state.
- A/B/C/M/D:
  - A: PACT-style action-state public communication;
  - B: authority-bearing public fields, especially `Action Required`, can
    overtake or distort the original question target;
  - C: trusted-question-root projection/quarantine as a diagnostic protocol,
    not a detector method yet;
  - M: HotpotQA EM/F1 on saved-field re-answering packets;
  - D: field bridge labels and paired deltas by target-authority,
    target-contract, final-commitment, and evidence/content layers.
- Evidence register:
  - added `E-088`.
- Interpretation:
  - retain the handle as live and falsifiable;
  - retire standalone lexical detector as a near-term method route;
  - next pressure should measure bridge-layer movement, not only aggregate EM.

## 2026-06-15 Field-Authority Offset150 Fresh Slice

- Updated `scripts/build_pact_public_state_field_packet.py` so source-run
  labels can be passed explicitly instead of hardcoding `baseline` and
  `final_contract`.
- Built offset150 field packet:
  - `experiments/20260615-local-pact-public-state-field-packet-offset150/field_packet.jsonl`;
  - source runs: `final_contract` and `compact_final_contract`;
  - `50` samples, `500` prompt rows.
- Official-source smoke:
  - `final_contract`: EM `0.500`, F1 `0.678`;
  - `compact_final_contract`: EM `0.440`, F1 `0.604`.
- Ran Qwen2.5-14B field packet on A800_2 GPU `7`:
  - run id `20260615-1840-a8002-pact-public-state-field-offset150-qwen25-14b`;
  - completed `500/500`, failed `0`.
- Main condition scores:
  - frozen target + evidence: EM `0.480`, F1 `0.657`;
  - hide public target: EM `0.450`, F1 `0.623`;
  - public state with final candidate: EM `0.430`, F1 `0.599`;
  - public state no final: EM `0.420`, F1 `0.593`;
  - public target without question: EM `0.310`, F1 `0.495`.
- Delta audits:
  - frozen target gives `10` rescues and `4` regressions versus
    public-state/no-final;
  - public target without question gives `0` rescues and `11` regressions;
  - final-answer candidate visibility gives `6` rescues and `5` regressions.
- Span/granularity audit:
  - `101/500` strict span or granularity misses;
  - `184/500` content mismatches.
- Bridge audit over `100` sample/source units:
  - `evidence_or_content`: `28`;
  - `stable_answer`: `27`;
  - `final_answer_commitment`: `22`;
  - `target_authority`: `11`;
  - `target_contract`: `11`;
  - `target_field_ablation`: `1`.
- Added report:
  - `reports/20260615-field-authority-offset150-fresh-slice.md`.
- Evidence register:
  - added `E-089`.
- Interpretation:
  - fresh-slice pressure keeps field-authority live and bounded;
  - public target without original question remains unsafe as a standalone task
    contract;
  - evidence/content and span/granularity failures still prevent a complete
    method story.

## 2026-06-15 Field-Authority Offset150 Semantic Focus

- Added focus-card extractor:
  - `scripts/build_pact_field_authority_focus_cards.py`.
- Generated offset150 target-focus cards:
  - `experiments/20260615-local-pact-field-authority-focus-offset150/focus_cards.jsonl`;
  - `experiments/20260615-local-pact-field-authority-focus-offset150/focus_cards.md`;
  - `22` cards, `17` unique samples.
- Added manual semantic labels:
  - `experiments/20260615-local-pact-field-authority-focus-offset150/manual_semantic_labels.jsonl`.
- Manual semantic family counts:
  - `answer_type_projection`: `10`;
  - `short_span_or_granularity`: `9`;
  - `evidence_sentence_or_distractor`: `2`;
  - `question_root_boundary_regression`: `1`.
- Target-slot candidate alignment:
  - `21/22` focus cards are not target-slot candidates under the old lexical
    diagnostic.
- Added report:
  - `reports/20260615-field-authority-offset150-semantic-focus.md`.
- Evidence register:
  - added `E-090`.
- Interpretation:
  - offset150 target focus is mostly answer-contract failure, not lexical target
    drift;
  - a future verifier would need answer type, relation, and span-granularity
    checks against the trusted question root.
- Follow-up seed:
  - generated offset100 focus cards with the same extractor at
    `experiments/20260615-local-pact-field-authority-focus-offset100/`;
  - offset100 focus cards: `28`;
  - families: `20` public-target-without-question regressions, `7`
    frozen-question-target rescues, and `1` frozen-question-target regression;
  - old target-slot candidate signal: `0/28` focus cards.

## 2026-06-15 Field-Authority Cross-Slice Semantic Focus

- Added offset100 manual semantic labels:
  - `experiments/20260615-local-pact-field-authority-focus-offset100/manual_semantic_labels.jsonl`.
- Added cross-slice report:
  - `reports/20260615-field-authority-cross-slice-semantic-focus.md`.
- Combined focus-card counts:
  - offset100: `28`;
  - offset150: `22`;
  - combined: `50`.
- Combined manual semantic families:
  - `answer_type_projection`: `21`;
  - `short_span_or_granularity`: `21`;
  - `public_target_misdirection`: `3`;
  - `evidence_sentence_or_distractor`: `3`;
  - `question_root_boundary_regression`: `2`.
- Old target-slot candidate alignment:
  - offset100: `0/28`;
  - offset150: `1/22`;
  - combined: `1/50`.
- Evidence register:
  - added `E-091`.
- Interpretation:
  - across two neighboring slices, the live handle is now better described as
    answer-contract weakness than lexical target-slot drift;
  - the next useful object is an answer-type/span-granularity protocol sketch,
    after checking whether existing QA answer-type or short-answer extraction
    work already covers the same surface.

## 2026-06-15 Field-Authority Answer-Contract Outside Check

- Ran a bounded outside check after the cross-slice semantic focus report.
- Added report:
  - `reports/20260615-field-authority-answer-contract-outside-check.md`.
- Added reading-queue section:
  - `Field-Authority / Answer-Contract Outside Check`.
- Useful external pressure hits:
  - `Learning Question Classifiers`;
  - `Extreme Classification for Answer Type Prediction in Question Answering`;
  - `HotpotQA`;
  - `MultiSpanQA`;
  - `Question-Attended Span Extraction`.
- Evidence register:
  - added `E-092`.
- Interpretation:
  - answer-type prediction and short-answer/span extraction are known QA
    surfaces;
  - the surviving niche is question-rooted answer-contract checking inside
    multi-agent public-state handoff, not generic QA answer typing.

## 2026-06-15 Field-Authority Answer-Contract Audit Seed

- Added manual/oracle audit seed builder:
  - `scripts/build_pact_answer_contract_audit_seed.py`.
- Generated audit seed artifacts:
  - `experiments/20260615-local-pact-answer-contract-audit-seed/audit_seed_records.jsonl`;
  - `experiments/20260615-local-pact-answer-contract-audit-seed/audit_seed.md`;
  - `experiments/20260615-local-pact-answer-contract-audit-seed/summary.json`.
- Audit seed size:
  - `50` records;
  - offset100 `28`, offset150 `22`.
- Contract risk counts:
  - `answer_type_or_relation_mismatch`: `21`;
  - `short_span_or_granularity_mismatch`: `21`;
  - `public_target_misdirects_relation`: `3`;
  - `evidence_sentence_or_distractor_copy`: `3`;
  - `question_root_can_reopen_ambiguity`: `2`.
- Behavioral summary:
  - public-target-only unsafe in `48/50` focus cards;
  - frozen question target sufficient in `43/50`;
  - evidence-adequacy guard needed in `2/50` boundary records.
- Added report:
  - `reports/20260615-field-authority-answer-contract-audit-seed.md`.
- Evidence register:
  - added `E-093`.
- Interpretation:
  - this is a positive-control protocol sketch, not a runtime verifier;
  - next specificity pressure should add matched negative controls from stable,
    evidence/content, and final-answer-commitment bridge units.

## 2026-06-15 Field-Authority Answer-Contract Negative Controls

- Added matched negative-control packet builder:
  - `scripts/build_pact_answer_contract_negative_controls.py`.
- Generated negative-control artifacts:
  - `experiments/20260615-local-pact-answer-contract-negative-controls/negative_control_cards.jsonl`;
  - `experiments/20260615-local-pact-answer-contract-negative-controls/negative_control_seed.jsonl`;
  - `experiments/20260615-local-pact-answer-contract-negative-controls/manual_seed_labels.jsonl`;
  - `experiments/20260615-local-pact-answer-contract-negative-controls/manual_seed_label_summary.json`;
  - `experiments/20260615-local-pact-answer-contract-negative-controls/negative_control_cards.md`;
  - `experiments/20260615-local-pact-answer-contract-negative-controls/negative_control_seed.md`;
  - `experiments/20260615-local-pact-answer-contract-negative-controls/summary.json`.
- Packet size:
  - `146` negative-control cards;
  - `24` deterministic seed cards;
  - offset100 `69`, offset150 `77`.
- Control-layer counts:
  - `stable_answer`: `53`;
  - `evidence_or_content`: `53`;
  - `final_answer_commitment`: `40`.
- Expected primary surfaces:
  - `no_answer_contract_failure`: `53`;
  - `evidence_or_content_failure`: `53`;
  - `strict_span_or_granularity_surface`: `33`;
  - `final_candidate_attractor`: `5`;
  - `final_candidate_helpful_commitment`: `2`.
- Manual seed labels over `24` cards:
  - primary failure surfaces: `8` no answer-contract failure, `8`
    evidence/content failure, `5` final-candidate attractor, `3`
    strict-span/granularity;
  - answer-contract alarm: `16` yes, `8` no;
  - target-authority alarm: `22` no, `2` soft;
  - short-span alarm: `8` yes, `16` no;
  - evidence-adequacy alarm: `8` yes, `16` no.
- Added report:
  - `reports/20260615-field-authority-answer-contract-negative-controls.md`.
- Evidence register:
  - added `E-094` and `E-095`.
- Interpretation:
  - this is a specificity packet, not a verifier result;
  - all `146` cards have `target_authority_alarm_expected = false`, so a
    future answer-contract audit can be falsified if it over-labels these
    controls as target-authority failures;
  - the manual seed labels already expose `2` soft target-authority boundary
    cases, so the verifier should support secondary alarms instead of forcing a
    single primary label.

## 2026-06-15 Field-Authority Answer-Contract Verifier Packet

- Added structured verifier packet builder:
  - `scripts/build_pact_answer_contract_verifier_packet.py`.
- Added verifier output evaluator:
  - `scripts/evaluate_pact_answer_contract_verifier.py`.
- Generated verifier packet artifacts:
  - `experiments/20260615-local-pact-answer-contract-verifier-packet/verifier_packet.jsonl`;
  - `experiments/20260615-local-pact-answer-contract-verifier-packet/gold_labels.jsonl`;
  - `experiments/20260615-local-pact-answer-contract-verifier-packet/summary.json`;
  - `experiments/20260615-local-pact-answer-contract-verifier-packet/scoring_plan.md`.
- Packet size:
  - `74` records;
  - `50` positive target-layer records;
  - `24` negative-control records;
  - offset100 `40`, offset150 `34`.
- Gold primary surfaces:
  - `answer_type_or_relation_mismatch`: `21`;
  - `short_span_or_granularity_mismatch`: `21`;
  - `public_target_misdirection`: `3`;
  - `evidence_sentence_or_distractor_copy`: `3`;
  - `question_root_ambiguity_regression`: `2`;
  - `evidence_or_content_failure`: `8`;
  - `final_candidate_attractor`: `5`;
  - `strict_span_or_granularity_surface`: `3`;
  - `no_answer_contract_failure`: `8`.
- Scoring smokes:
  - `gold` prediction source: `1.000` exact all-fields accuracy and `1.000`
    primary-surface accuracy;
  - `all_no` baseline: `0.108` exact all-fields accuracy and `0.108`
    primary-surface accuracy.
- Added report:
  - `reports/20260615-field-authority-answer-contract-verifier-packet.md`.
- Evidence register:
  - added `E-096`.
- Interpretation:
  - this is a verifier benchmark packet, not a model result;
  - the next executable pressure is to run a low-temperature model over
    `verifier_packet.jsonl` and score by alarm family plus primary surface.

## 2026-06-15 PACT Answer-Contract Verifier Qwen2.5-14B Run

- Added A800_2 launcher:
  - `scripts/run_pact_answer_contract_verifier_a8002.sh`.
- Synced the verifier packet and evaluator to A800_2.
- Ran Qwen2.5-14B-Instruct verifier over the `74`-record answer-contract packet:
  - run id `20260615-1938-a8002-pact-answer-contract-verifier-qwen25-14b`;
  - machine A800_2, GPU `7`, port `8035`;
  - completed `74/74`, failed `0`;
  - all outputs were valid JSON.
- Scoring result:
  - exact all-fields accuracy `0.081`;
  - primary-surface accuracy `0.230`;
  - `target_authority_alarm` binary F1 `0.688`;
  - `answer_contract_alarm` recall `0.288`;
  - `answer_type_relation_alarm` F1 `0.133`;
  - `short_span_granularity_alarm` F1 `0.324`.
- Added run note:
  - `experiments/20260615-1938-a8002-pact-answer-contract-verifier-qwen25-14b/README.md`.
- Added report:
  - `reports/20260615-pact-answer-contract-verifier-qwen25-14b.md`.
- Evidence register:
  - added `E-097`.
- Interpretation:
  - the packet is a useful falsification surface;
  - the current prompt is not a working runtime verifier;
  - the next check should repair prompt/schema calibration on the same packet
    before using the verifier to route public-state fields.

## 2026-06-15 PACT Answer-Contract Verifier Prompt-V2 Run

- Added strict prompt-v2 packet builder:
  - `scripts/build_pact_answer_contract_verifier_prompt_v2_packet.py`.
- Generated prompt-v2 packet:
  - `experiments/20260615-local-pact-answer-contract-verifier-packet-v2/`;
  - same `74` records and gold labels as the v1 verifier packet;
  - only the prompt text and prompt-version metadata changed.
- Gold and all-no evaluator smokes passed on the v2 packet:
  - gold exact all-fields accuracy `1.000`;
  - all-no exact all-fields accuracy `0.108`.
- Ran Qwen2.5-14B-Instruct verifier over v2 packet:
  - run id `20260615-1951-a8002-pact-answer-contract-verifier-v2-qwen25-14b`;
  - machine A800_2, GPU `7`, port `8035`;
  - completed `74/74`, failed `0`;
  - all outputs were valid JSON.
- Main comparison:
  - exact all-fields accuracy moved from `0.081` to `0.108`;
  - primary-surface accuracy moved from `0.230` to `0.216`;
  - `answer_contract_alarm` F1 improved from `0.442` to `0.712`;
  - `target_authority_alarm = soft` predictions dropped from `43` to `12`;
  - `target_authority_alarm` F1 fell from `0.688` to `0.526`;
  - `short_span_granularity_alarm` F1 fell from `0.324` to `0.125`.
- Added run note:
  - `experiments/20260615-1951-a8002-pact-answer-contract-verifier-v2-qwen25-14b/README.md`.
- Added report:
  - `reports/20260615-pact-answer-contract-verifier-v2-qwen25-14b.md`.
- Evidence register:
  - added `E-098`.
- Interpretation:
  - prompt-v2 repaired the global alarm and soft-overuse symptoms;
  - it did not solve primary-surface diagnosis;
  - the next verifier object should be split-stage rather than another longer
    one-shot taxonomy prompt.

## 2026-06-15 PACT Answer-Contract Split-Alarm Run

- Added split-alarm packet builder and evaluator:
  - `scripts/build_pact_answer_contract_split_alarm_packet.py`;
  - `scripts/evaluate_pact_answer_contract_split_alarm.py`.
- Added A800_2 launcher:
  - `scripts/run_pact_answer_contract_split_alarm_a8002.sh`.
- Generated split-alarm packet:
  - `experiments/20260615-local-pact-answer-contract-split-alarm-packet/`;
  - `74` base records expanded into `444` prompt rows across six alarm tasks.
- Gold and all-no evaluator smokes passed:
  - gold exact label accuracy `1.000`;
  - all-no exact label accuracy `0.586`.
- Ran Qwen2.5-14B-Instruct over split-alarm packet:
  - run id `20260615-2002-a8002-pact-answer-contract-split-alarm-qwen25-14b`;
  - machine A800_2, GPU `7`, port `8035`;
  - completed `444/444`, failed `0`;
  - after split-label fallback, parse failures `0`.
- Main split-alarm metrics:
  - exact label accuracy `0.590`;
  - positive/negative accuracy `0.617`;
  - overall binary F1 `0.384`;
  - `answer_contract_alarm` F1 `0.538`;
  - `target_authority_alarm` F1 `0.486`;
  - `answer_type_relation_alarm` F1 `0.125`;
  - `short_span_granularity_alarm` F1 `0.065`;
  - `evidence_adequacy_alarm` F1 `0.424`;
  - `final_candidate_alarm` F1 `0.000`.
- Added run note:
  - `experiments/20260615-2002-a8002-pact-answer-contract-split-alarm-qwen25-14b/README.md`.
- Added report:
  - `reports/20260615-pact-answer-contract-split-alarm-qwen25-14b.md`.
- Evidence register:
  - added `E-099`.
- Interpretation:
  - split prompting does not rescue the current Qwen2.5-14B verifier;
  - evidence adequacy improves modestly, but short-span, final-candidate, and
    answer-type/relation remain weak;
  - the verifier route now needs few-shot contrast, label simplification, a
    stronger verifier model, or demotion to manual-audit benchmark status.

## 2026-06-15 External Pressure Taste Audit

- Added bounded outside-pressure synthesis:
  - `reports/20260615-external-pressure-taste-audit.md`.
- External pressure sources:
  - PACT action-state communication;
  - AgentSecBench and CaMeL for data-flow versus authority separation;
  - DeLM and Decision-Aware Memory Cards for shared verified context and
    decision-critical memory;
  - Benefits and Limitations of Communication, HiddenBench, Demystifying MAD,
    Talk Isn't Always Cheap, and Cost of Consensus for task-regime and
    authority-transfer pressure;
  - answer-type/span QA work for collision pressure.
- Interpretation:
  - the highest-taste surviving handle is not a runtime answer-contract
    verifier;
  - it is the separation of evidence semantics from authority semantics inside
    multi-agent public state;
  - next pressure should deliberately perturb public-field authority while
    holding evidence as constant as possible.

## 2026-06-15 PACT Authority/Evidence Stress Run

- Added authority/evidence stress packet builder and evaluator:
  - `scripts/build_pact_authority_evidence_stress_packet.py`;
  - `scripts/evaluate_pact_authority_evidence_stress_packet.py`;
  - `scripts/run_pact_authority_evidence_stress_a8002.sh`.
- Generated setup packet:
  - `experiments/20260615-local-pact-authority-evidence-stress-packet/`;
  - source cases: `40`;
  - prompt rows: `200`;
  - source mix: `32` positive target-focus cases and `8` negative-control seed
    cases;
  - variants: original trusted-root public state, injected `Action Required`,
    delegated active public authority, frozen question target, and final
    candidate lure.
- Ran Qwen2.5-14B-Instruct on A800_2 GPU `7`:
  - run id `20260615-2040-a8002-pact-authority-evidence-stress-qwen25-14b`;
  - completed `200/200`;
  - GPU 7 released after the run.
- Main result over positive target-focus rows:
  - trusted-root original public state: EM `0.812`, F1 `0.865`;
  - trusted-root with injected `Action Required`: EM `0.594`, F1 `0.695`;
  - delegated public authority active: EM `0.344`, F1 `0.525`;
  - frozen question target: EM `0.844`, F1 `0.911`;
  - final-candidate lure: EM `0.469`, F1 `0.633`.
- Paired deltas over positive target-focus rows:
  - injected `Action Required`: `7` regressions, avg F1 delta `-0.169`;
  - delegated public authority: `15` regressions, avg F1 delta `-0.339`;
  - frozen question target: `5` rescues, `4` regressions, avg F1 delta `+0.046`;
  - final-candidate lure: `11` regressions, avg F1 delta `-0.231`.
- Added report:
  - `reports/20260615-pact-authority-evidence-stress-qwen25-14b.md`.
- Evidence register:
  - added `E-101`.
- Interpretation:
  - the stress packet moves behavior in the predicted direction and strengthens
    the evidence/authority separation handle;
  - this is still a selected saved-field pressure object, not a full PACT method
    result.

## 2026-06-15 PACT Authority/Evidence Case Audit

- Added manual case-level audit:
  - `reports/20260615-pact-authority-evidence-case-audit.md`.
- Audited:
  - `7` positive-case regressions from injected `Action Required`;
  - `5` positive-case rescues from frozen question target;
  - `4` positive-case regressions from frozen question target;
  - `3` sampled controls.
- Interpretation:
  - the stress signal survives, but the clean claim narrows;
  - only `2/7` injected regressions are strong public-field answer-contract
    authority failures, with `2/7` mixed span/result-surface cases and `3/7`
    better treated as answer-type, exact-span, or question-root confounds;
  - frozen-target rescues are cleaner, with `4/5` looking like question-root or
    target-relation repairs and `1/5` mainly a granularity repair.
- Evidence register:
  - added `E-102`.

## 2026-06-15 PACT Authority Injection Arena

- Added public-state authority injection arena scripts:
  - `scripts/build_pact_authority_injection_arena_packet.py`;
  - `scripts/evaluate_pact_authority_injection_arena.py`;
  - `scripts/run_pact_authority_injection_arena_a8002.sh`.
- Generated setup packet:
  - `experiments/20260615-local-pact-authority-injection-arena-packet/`;
  - source cases: `40`;
  - prompt rows: `280`;
  - variants: original untyped public state, evidence-only neutral, neutral
    public summary, imperative public task, wrong-contract public task, forged
    final commitment, and typed-state quarantine.
- Ran Qwen2.5-14B-Instruct on A800_2 GPU `7`:
  - run id `20260615-2130-a8002-pact-authority-injection-arena-qwen25-14b`;
  - completed `280/280`;
  - failed `0`;
  - GPU 7 released after the run.
- Main result over positive target-focus rows:
  - original untyped public state: EM `0.812`, F1 `0.865`;
  - wrong-contract public task: EM `0.188`, F1 `0.393`;
  - forged final commitment: EM `0.375`, F1 `0.552`;
  - typed-state quarantine: EM `0.625`, F1 `0.782`.
- Paired Authority Violation Rate over `26` base-correct positive rows:
  - wrong-contract public task: `21/26`, AVR `0.808`;
  - forged final commitment: `14/26`, AVR `0.538`;
  - imperative public task: `3/26`, AVR `0.115`;
  - typed-state quarantine: `6/26`, AVR `0.231`.
- Interpretation:
  - public-state answer-contract authority is a strong perturbable surface;
  - typed role labels rescue many wrong-contract and forged-candidate failures
    but are not safe by themselves because the visible untrusted candidate can
    become an attraction surface.
- Added report:
  - `reports/20260615-pact-authority-injection-arena-qwen25-14b.md`.
- Evidence register:
  - added `E-103`.

## 2026-06-15 PACT Typed Boundary Split Packet

- Added typed-boundary split setup scripts:
  - `scripts/build_pact_typed_boundary_split_packet.py`;
  - `scripts/evaluate_pact_typed_boundary_split.py`;
  - `scripts/run_pact_typed_boundary_split_a8002.sh`.
- Generated local setup packet:
  - `experiments/20260615-local-pact-typed-boundary-split-packet/`;
  - source cases: `40`;
  - prompt rows: `440`;
  - variants: `3` arena anchors plus `8` typed-boundary variants.
- The packet separates:
  - no candidate;
  - evaluator-hidden candidate;
  - model-visible untrusted candidate;
  - visible candidate with extract-first staging;
  - original suggestion versus wrong-contract suggestion.
- Local validation:
  - `python -m py_compile` passed for builder/evaluator;
  - gold-smoke evaluation produced EM `1.000` and average F1 `1.000` over
    `440/440` rows;
  - hidden-leak check found `0/80` hidden rows with explicit
    `Untrusted Candidate:` and `0/80` with `Candidate surface:`;
  - all `160/160` visible-candidate rows contain `Untrusted Candidate:`.
- Added report:
  - `reports/20260615-pact-typed-boundary-split-packet.md`.
- Evidence register:
  - added `E-104`.

## 2026-06-15 PACT Typed Boundary Split Qwen2.5-14B

- Synced the typed-boundary packet and scripts to A800_2:
  - packet:
    `/data/xuhaoming/yfy/research_workspace/experiments/20260615-local-pact-typed-boundary-split-packet/typed_boundary_split_packet.jsonl`;
  - runner: `scripts/run_pact_typed_boundary_split_a8002.sh`;
  - evaluator: `scripts/evaluate_pact_typed_boundary_split.py`.
- Remote validation:
  - `py_compile` passed for runner dependencies;
  - `bash -n` passed for the runner;
  - remote gold-smoke produced EM/F1 `1.000` over `440` rows.
- Ran Qwen2.5-14B-Instruct on A800_2 GPU `7`:
  - run id `20260615-2223-a8002-pact-typed-boundary-split-qwen25-14b`;
  - completed `440/440`;
  - failed `0`;
  - runner/evaluator stderr logs are empty;
  - GPU 7 released after the run.
- Main positive target-focus result:
  - original untyped public state: EM `0.812`, F1 `0.865`;
  - wrong-contract public task: EM `0.188`, F1 `0.393`;
  - forged final commitment: EM `0.375`, F1 `0.552`;
  - typed no-candidate and typed hidden-candidate: EM `0.875`, F1 `0.914`;
  - typed visible-candidate: EM `0.625`, F1 `0.719`;
  - typed visible-candidate extract-first: EM `0.656`, F1 `0.754`;
  - typed wrong-contract no-candidate/hidden: EM `0.875`, F1 `0.917`.
- Key paired result over `26` base-correct positive cases:
  - wrong-contract anchor AVR: `21/26`;
  - forged-final anchor AVR: `14/26`;
  - typed no-candidate/hidden AVR: `1/26`;
  - typed visible-candidate AVR: `7/26`;
  - typed visible-candidate extract-first AVR: `6/26`;
  - typed wrong-contract visible-candidate extract-first AVR: `4/26`.
- Interpretation:
  - typed roles are useful only when final-answer candidates are not
    model-visible;
  - visible untrusted candidates reintroduce commitment pressure;
  - extract-first instruction helps slightly but does not replace visibility
    control.
- Added report:
  - `reports/20260615-pact-typed-boundary-split-qwen25-14b.md`.
- Evidence register:
  - added `E-105`.

## 2026-06-15 MATH Authority Genesis Ladder Packet

- Added MATH-side Authority Genesis setup scripts:
  - `scripts/build_math_authority_genesis_ladder_packet.py`;
  - `scripts/evaluate_math_authority_genesis_ladder.py`.
- Generated local setup packet:
  - `experiments/20260615-local-math-authority-genesis-ladder-packet/`;
  - source rows: `20`;
  - wrong-artifact instances: `65`;
  - prompt rows: `670`;
  - baseline previous-solution rows: `20`;
  - evaluator-hidden artifact rows: `65`;
  - model-visible artifact rows: `585`.
- The packet starts from clean anonymous MATH200 manual seed rows where wrong
  peer surfaces caused right-to-wrong transitions, then rebuilds wrong
  artifacts as:
  - wrong final answer;
  - wrong relation skeleton;
  - wrong numeric-role binding;
  - wrong equation surface.
- Future signals include hidden metadata, raw mention, answer-shaped span, peer
  claim, majority/consensus, previous final answer, verifier-approved result,
  saved memory, active task requirement, and final-answer commitment.
- Local validation:
  - `python -m py_compile` passed for builder/evaluator;
  - packet has `670/670` unique `packet_id`s;
  - hidden-leak check found `0/65` hidden rows with artifact markers;
  - all `585/585` visible rows contain a `Communication Artifact:` section;
  - gold-smoke semantic evaluation produced `670/670` known-correct rows and
    `0` semantic unknowns.
- Added report:
  - `reports/20260615-math-authority-genesis-ladder-packet.md`.
- Evidence register:
  - added `E-109`.

## 2026-06-16 MATH Authority Genesis Ladder Qwen2.5-14B

- Added and used A800_2 runner:
  - `scripts/run_math_authority_genesis_ladder_a8002.sh`.
- Synced packet/evaluator/runner to A800_2 under:
  - `/data/xuhaoming/yfy/research_workspace`.
- Remote validation:
  - `py_compile` passed for MATH builder/evaluator/math_eval;
  - `bash -n` passed for the runner;
  - remote gold-smoke semantic evaluation produced `670/670` known-correct rows
    and `0` semantic unknowns.
- First diagnostic run:
  - run id `20260616-0001-a8002-math-authority-genesis-ladder-qwen25-14b`;
  - completed `670/670` requests with `0` failures;
  - used `max_tokens=256`;
  - `441/670` outputs hit the token cap and evaluator produced `435` semantic
    unknown rows;
  - recorded as truncation diagnostic only.
- Primary run:
  - run id
    `20260616-0102-a8002-math-authority-genesis-ladder-qwen25-14b-max768`;
  - model path `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`;
  - A800_2 GPU `7`, port `8039`;
  - completed `670/670` requests with `0` failures;
  - `max_tokens=768`, request timeout `420`, run timeout `21600`;
  - `0/670` outputs hit the token cap; max completion tokens `643`, average
    `335.8`;
  - evaluator stderr is empty;
  - GPU 7 released after the run.
- Main result:
  - baseline previous-solution rows: `20/20` correct;
  - hidden metadata control: `0/65` authority violations;
  - overall semantic accuracy: `613/670`, or `0.9149`;
  - semantic unknowns: `0`;
  - visible future-signal authority violations: `57/585`;
  - total violations split into `14` wrong-answer uptake rows and `43`
    operator-uptake candidates.
- By future signal:
  - raw mention: `4/65`, AVR `0.062`;
  - answer-shaped span: `2/65`, AVR `0.031`;
  - peer claim: `3/65`, AVR `0.046`;
  - majority consensus: `8/65`, AVR `0.123`;
  - previous final answer: `6/65`, AVR `0.092`;
  - verifier-approved result: `11/65`, AVR `0.169`, with `6`
    wrong-answer uptake rows;
  - saved memory: `8/65`, AVR `0.123`, with `2` wrong-answer uptake rows;
  - active task required: `9/65`, AVR `0.138`, with `5` wrong-answer uptake
    rows;
  - final-answer commitment: `6/65`, AVR `0.092`, with `1` wrong-answer
    uptake row.
- By artifact type:
  - wrong equation surface: `21` violations, `4` answer uptake, `17` operator
    candidates;
  - wrong final answer: `18` violations, `10` answer uptake, `8` operator
    candidates;
  - wrong numeric-role binding: `10` violations, all operator candidates;
  - wrong relation skeleton: `8` violations, all operator candidates.
- Interpretation:
  - Authority Genesis transfers beyond PACT public-state QA into MATH peer
    influence;
  - the effect is not just exact final-answer copy, because most violations are
    operator candidates;
  - the ladder is non-monotonic and case-concentrated, especially on
    `math159_wrong_rationale`.
- Added report:
  - `reports/20260616-math-authority-genesis-ladder-qwen25-14b.md`.
- Evidence register:
  - added `E-110`.

## 2026-06-16 MATH Authority Genesis Mechanism Audit

- Added local mechanism-audit script:
  - `scripts/build_math_authority_genesis_mechanism_audit.py`.
- Built audit artifact:
  - `experiments/20260616-local-math-authority-genesis-mechanism-audit/`;
  - `summary.json`;
  - `violation_cards.jsonl`;
  - `mechanism_audit.md`.
- Source run:
  - `experiments/20260616-0102-a8002-math-authority-genesis-ladder-qwen25-14b-max768/`.
- Extracted all MATH Authority Genesis right-to-wrong cards:
  - violation cards: `57`;
  - hidden metadata controls: `65`;
  - hidden metadata authority violations: `0`.
- Seed mechanism split:
  - direct wrong-answer uptake: `14`;
  - equation-surface operator uptake: `17`;
  - numeric-role binding operator uptake: `10`;
  - relation-skeleton operator uptake: `8`;
  - final-answer anchor disturbance without exact copy: `8`.
- Artifact split:
  - wrong equation surface: `21` violations, `4` direct answer uptake, `17`
    operator candidates;
  - wrong final answer: `18` violations, `10` direct answer uptake, `8`
    non-copy disturbances;
  - wrong numeric-role binding: `10` violations, all operator candidates;
  - wrong relation skeleton: `8` violations, all operator candidates.
- Case concentration:
  - `math159_wrong_rationale` contributes `25/57` violation cards;
  - only `1/25` of those is direct uptake of the peer wrong answer `7`;
  - `23/25` output `26` while gold/base is `27`, making it the strongest
    current non-copy boundary/operator regression cluster.
- Interpretation:
  - the MATH run supports the cross-task Authority Genesis handle as
    state-transition/operator confusion, not only candidate copying;
  - the result is still selected and case-concentrated, so the next pressure
    should deconcentrate or balance mechanism families before treating counts
    as stable rates.
- Added report:
  - `reports/20260616-math-authority-genesis-mechanism-audit.md`.
- Evidence register:
  - added `E-111`.

## 2026-06-16 Multi-Agent Specificity External PDF Pressure

- Downloaded and extracted text from external PDFs under
  `papers/external-pressure-20260616/`:
  - Benefits and Limitations of Communication in Multi-Agent Reasoning;
  - Demystifying Multi-Agent Debate;
  - Talk Isn't Always Cheap;
  - The Cost of Consensus;
  - When Persuasion Overrides Truth in Multi-Agent LLM Debates;
  - MultiAgent Collaboration Attack;
  - HIDDENBENCH;
  - PACT Action-state Communication;
  - DeLM Shared Context;
  - CaMeL Prompt Injection Defense.
- Added synthesis report:
  - `reports/20260616-multiagent-specificity-external-pdf-pressure.md`.
- Interpretation:
  - the user's objection is important: a static Authority Genesis ladder can
    still look like a generic LLM context-authority problem;
  - external multi-agent papers push the handle toward communication lifecycle
    variables: peer exchange, communication density, majority/plurality,
    confidence, shared-state admission, distributed-information surfacing, and
    downstream reuse;
  - the next pressure should be a multi-agent communication-lifecycle stress
    test rather than another static prompt-label ladder alone.

## 2026-06-16 Authority Genesis Idea Reframing

- Revised the incubation memo:
  - `reports/20260615-authority-genesis-idea.md`.
- Reframing:
  - `Authority Genesis` is no longer treated as the deepest mechanism;
  - it is now one symptom family of `Epistemic Type Erasure in Multi-Agent
    Communication`;
  - the core problem is that one agent's intermediate computational artifact
    crosses the receiver boundary as flat natural language, losing whether it
    was evidence, inference, hypothesis, confidence, candidate, commitment,
    memory, procedural result, or action suggestion.
- Connected the revised idea back to existing evidence:
  - PACT typed-boundary results become candidate/commitment invalid-cast
    evidence;
  - MATH Authority Genesis operator uptake becomes partial-derivation/operator
    invalid-cast evidence;
  - the old authority ladder remains a sub-probe rather than the whole idea.
- Next pressure:
  - extend existing MATH Authority Genesis artifacts into a type-erasure packet
    that compares type-erased peer text with type-preserved channels while
    preserving useful evidence transfer.

## 2026-06-16 MATH Epistemic Type-Erasure Packet

- Built the next pressure object from the existing MATH Authority Genesis
  source artifacts:
  - builder: `scripts/build_math_epistemic_type_erasure_packet.py`;
  - A8002 runner: `scripts/run_math_epistemic_type_erasure_a8002.sh`;
  - packet directory:
    `experiments/20260616-local-math-epistemic-type-erasure-packet/`;
  - report: `reports/20260616-math-epistemic-type-erasure-packet.md`.
- Design:
  - same Agent A artifact is rendered as type-erased peer/shared-context text
    or as type-preserved communication with explicit epistemic type,
    provenance, confidence, and commitment fields;
  - controls include self-revision with no peer content and unrelated
    peer-like context from another MATH problem.
- Packet shape:
  - `15` source rows;
  - `24` selected artifacts;
  - `222` prompt rows;
  - per-MATH-case cap `2` to avoid repeating the prior `math121`/`math159`
    concentration failure.
- Selected artifact split:
  - wrong equation surface: `10`;
  - wrong final answer: `6`;
  - wrong numeric-role binding: `4`;
  - wrong relation skeleton: `4`.
- Prior-ladder linkage:
  - `13/24` selected artifacts had prior ladder violation cards;
  - `8/24` had prior operator-uptake candidate cards.
- Verification:
  - Python compile passed for builder and reused evaluator;
  - shell syntax check passed for the A8002 runner;
  - gold-smoke evaluation: `222/222` semantic correct;
  - packet IDs are unique and there are no duplicate variants within a case.
- Interpretation:
  - this is setup only, not a behavior result;
  - the next model run can test whether the same cross-agent artifact is more
    harmful when the communication boundary erases its epistemic type.

## 2026-06-16 MATH Type-Erasure Run Attempt

- Tried to launch the next model step from the local desktop session.
- Local environment check:
  - no local A8002-style `/data/xuhaoming/yfy/research_workspace`;
  - no local vLLM Python at the expected path;
  - no local Qwen2.5-14B model directory at the expected path;
  - no visible local NVIDIA runtime from WSL;
  - no OpenAI-compatible local endpoint on ports `8000` through `8050`.
- Remote checks:
  - `ssh A800_2` timed out against the configured host/port;
  - direct `ssh -p 10622 xuhaoming@124.128.251.61` also timed out;
  - configured `aliyun`, `falcon-rev`, and `falcon-rev-48175` SSH probes also
    timed out.
- Outcome:
  - no model row was run in this attempt;
  - packet/gold-smoke remain ready;
  - the blocker is machine connectivity/runtime availability, not packet
    construction.

## 2026-06-16 MATH Type-Erasure Proxy Run

- Re-tried A800_2 through the user's local Clash SOCKS5 proxy:
  - Clash SOCKS5 at `127.0.0.1:7890` can reach the A800_2 SSH banner;
  - added a tiny OpenSSH `ProxyCommand` relay:
    `scripts/ssh_socks5_proxy.py`;
  - `ssh A800_2` works through:
    `python scripts/ssh_socks5_proxy.py 127.0.0.1 7890 %h %p`.
- Synced the type-erasure packet, builder, runner, and report to the remote
  workspace.
- Added optional `LIMIT` support to:
  - `scripts/run_math_epistemic_type_erasure_a8002.sh`.
- Smoke runs:
  - `20260616-1109-a8002-math-type-erasure-qwen25-14b-smoke12`:
    `12/12` completed, `0` failures; this only covered baseline/self-control
    due packet ordering;
  - `20260616-1116-a8002-math-type-erasure-artifact-smoke38`:
    `38/38` completed, `0` failures, artifact smoke evaluation `38/38`
    semantic correct.
- Full run:
  - run id:
    `20260616-1123-a8002-math-type-erasure-qwen25-14b-full222`;
  - local mirror:
    `experiments/20260616-1123-a8002-math-type-erasure-qwen25-14b-full222/`;
  - report:
    `reports/20260616-math-epistemic-type-erasure-qwen25-14b.md`;
  - `222/222` rows completed;
  - `0` runner failures;
  - evaluator stderr empty;
  - semantic correctness: `219/222`.
- Main behavior result:
  - controls: `0/39` authority violations;
  - type-erased rows: `2/48` authority violations, both operator candidates
    without exact wrong-answer uptake;
  - type-preserved rows: `1/120` authority violation, exact wrong-answer
    uptake;
  - all three violations are `wrong_equation_surface` rows.
- Interpretation:
  - this supports the boundary/type-erasure handle weakly but specifically:
    `type_erased_shared_workspace_entry` can still induce non-copy equation
    operator shifts;
  - type preservation reduces most pressure in this packet but does not fully
    solve candidate visibility/local validation.

## 2026-06-16 A-Conference Story Synthesis

- Added story synthesis memo:
  - `reports/20260616-a-conference-story-synthesis-epistemic-type-erasure.md`.
- Verdict:
  - the current handle is a live A-conference candidate, not a paper-ready
    story;
  - the viable claim is not generic peer-text influence, but invalid epistemic
    casting at the multi-agent communication boundary.
- Current A/B/C shape:
  - A: multi-agent systems serialize peer messages, shared workspace entries,
    memory, verifier notes, and partial derivations as flat text;
  - B: this erases the object's epistemic type and lets receivers cast
    hypotheses, candidates, or partial derivations as stronger public state;
  - C: typed communication-boundary protocols or diagnostics that preserve
    allowed casts while testing useful information transfer.
- Required next pressure before scaling:
  - build MATH Type-Erasure v2 with a candidate-visibility split:
    typed no-candidate, evaluator-hidden candidate, visible candidate, typed
    derivation with answer removed, typed derivation with answer visible,
    erased peer message, erased shared workspace entry, and unrelated control;
  - then move to a true sender-receiver lifecycle where Agent A emits the
    artifact and Agent B receives it through different boundary protocols.

## 2026-06-16 MATH Type-Erasure v2 Packet

- Built the candidate-visibility split requested by the A-conference synthesis:
  - builder: `scripts/build_math_epistemic_type_erasure_v2_packet.py`;
  - packet directory:
    `experiments/20260616-local-math-epistemic-type-erasure-v2-packet/`;
  - setup report:
    `reports/20260616-math-epistemic-type-erasure-v2-packet.md`.
- Packet shape:
  - `222` prompt rows;
  - `15` source rows represented;
  - `24` selected artifacts;
  - condition rows: baseline `15`, control `39`, erased `48`, typed `120`.
- Candidate-visibility arms:
  - erased peer message: `24`;
  - erased shared workspace entry: `24`;
  - typed no-candidate evidence/inference: `24`;
  - typed hidden-candidate metadata: `24`;
  - typed visible-candidate noncommitment: `24`;
  - typed derivation answer removed: `24`;
  - typed derivation answer visible: `24`;
  - unrelated peer-like control: `24`.
- Local validation:
  - `python -m py_compile` passed for the v2 builder and evaluator;
  - packet has `222` rows and unique `packet_id` values;
  - hidden/no-candidate communication blocks have `0/24` wrong-answer literal
    exposure in each of:
    `typed_no_candidate_evidence_inference`,
    `typed_hidden_candidate_metadata`, and
    `typed_derivation_answer_removed`;
  - gold-smoke evaluation passed with `222/222` semantic correct.
- Interpretation:
  - this is setup evidence, not model behavior;
  - it removes the v1 ambiguity between typed-boundary failure and visible
    candidate-answer anchoring;
  - the next pressure is a v2 A800_2 run using the existing type-erasure runner
    with `PACKET` overridden to the v2 packet path.

## 2026-06-16 MATH Type-Erasure v2 A800_2 Run

- Ran the v2 candidate-visibility packet on A800_2:
  - run id:
    `20260616-1200-a8002-math-type-erasure-v2-qwen25-14b-full222`;
  - local mirror:
    `experiments/20260616-1200-a8002-math-type-erasure-v2-qwen25-14b-full222/`;
  - report:
    `reports/20260616-math-epistemic-type-erasure-v2-qwen25-14b.md`.
- Execution:
  - `222/222` rows completed;
  - `0` runner failures;
  - runner stderr empty;
  - evaluator stderr empty;
  - semantic correctness: `217/222`.
- Main behavior result:
  - controls: `0/39` authority violations;
  - erased peer message: `0/24`;
  - erased shared workspace entry: `2/24`, both non-copy operator candidates
    on `math121`;
  - typed no-candidate evidence/inference: `2/24`, including one hidden-source
    wrong-answer collision and one operator/local re-solve error;
  - typed hidden-candidate metadata: `1/24`, operator/local re-solve error;
  - typed visible-candidate noncommitment: `0/24`;
  - typed derivation answer removed: `0/24`;
  - typed derivation answer visible: `0/24`.
- Interpretation:
  - the v1 erased shared-workspace signal reproduces: the same `math121`
    equation/operator shift appears from `18√3` to `18√2`;
  - candidate visibility alone is not the root cause, because visible-candidate
    typed arms are clean while hidden/no-candidate typed arms still show
    failures;
  - the next story pressure is a sender-receiver micro-protocol plus an
    invalid-cast taxonomy that distinguishes inherited operator state from
    local re-solve and final-answer contract failures.

## 2026-06-16 MATH Sender-Receiver Micro-Protocol

- Added the invalid-cast audit and sender-receiver packet:
  - audit builder:
    `scripts/build_math_type_erasure_v2_invalid_cast_audit.py`;
  - packet builder:
    `scripts/build_math_sender_receiver_micro_protocol_packet.py`;
  - analyzer:
    `scripts/analyze_math_sender_receiver_micro_protocol.py`;
  - packet directory:
    `experiments/20260616-local-math-sender-receiver-micro-protocol-packet/`;
  - full run mirror:
    `experiments/20260616-1338-a8002-math-sender-receiver-full246-qwen25-14b/`;
  - report:
    `reports/20260616-math-sender-receiver-micro-protocol-qwen25-14b.md`.
- Packet shape:
  - `246` prompt rows from `13` source rows and `20` selected sender artifacts;
  - artifact types: wrong equation surface `6`, wrong final answer `6`,
    wrong numeric-role binding `4`, wrong relation skeleton `4`;
  - channel rows: baseline `13`, control `53`, erased `40`, admitted `40`,
    typed `80`, quarantine `20`;
  - gold-smoke semantic evaluation passed with `246/246` correct rows.
- A800_2 full run:
  - run id:
    `20260616-1338-a8002-math-sender-receiver-full246-qwen25-14b`;
  - `246/246` rows completed;
  - semantic correctness: `226/246`;
  - evaluator reported `2` artifact-answer uptake rows.
- Seed invalid-cast taxonomy over full run:
  - `20` authority-violation cards;
  - `4` admitted-state inherited-operator cards;
  - `4` peer-message operator-influence cards;
  - `2` direct visible-answer uptake cards;
  - `4` local re-solve or empty-artifact errors;
  - `6` operator candidates needing manual review.
- Main mechanism read:
  - the cleanest signal is case-concentrated on `math121`: wrong equation
    surfaces repeatedly move the answer from `18√3` to `18√2` without copying
    the peer's wrong final answer `36√2`;
  - the shift appears under peer/admitted/memory and some typed channels, while
    inert scratch, unrelated controls, typed visible-candidate noncommitment,
    and typed inference noncommitment stay clean for this case;
  - direct answer copy remains a separate mechanism on `math96`, where
    peer/admitted rows move from `8` to `128/3`;
  - `math159` still exposes local re-solve background, including a control
    self-revision move from `27` to `26`, so those rows should not be read as
    sender invalid-casts without manual review.
- Interpretation:
  - the handle has moved from static type labels to explicit communication
    lifecycle transitions;
  - typed boundaries are not a single solved condition: visible-candidate
    noncommitment is clean here, but typed hidden-candidate and partial
    derivation channels still preserve enough operator pressure to fail on
    `math121`;
  - the next pressure is manual audit of the six typed/operator-candidate cards
    and a deconcentrated packet that reduces reliance on `math121`,
    `math159`, and `math96`.
