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
