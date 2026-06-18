# PerspectiveGap Reproduction Note

## Short Answer

Local benchmark contact succeeded. The upstream repo was cloned, the bundled scorer fixture passed, the full 220-row release was rendered locally, transparent non-model baselines show the benchmark strongly penalizes over-sharing, and a first A800_2 model smoke exposed a coverage/precision tradeoff between Qwen2.5-7B and Qwen2.5-14B.

## Scope

- method: PerspectiveGap
- paper: PerspectiveGap: A Benchmark for Multi-Agent Orchestration Prompting
- paper link: https://arxiv.org/abs/2606.08878
- dataset: https://huggingface.co/datasets/sun1245/PerspectiveGap
- repo: https://github.com/WhymustIhaveaname/PerspectiveGap
- commit: `60b1dcaaeeb40619075f6cd8779c47fa4b344391`
- local path: `baselines/PerspectiveGap/upstream`
- target setting: 220 rendered evaluations over 110 scenarios, seeds 1 and 42, with role-fragment assignment and prompt-writing tasks

## Environment

- machine: local Windows workstation
- Python: `3.13.11`
- dependency path: direct `PYTHONPATH=src` execution
- uv: not installed locally
- venv: `baselines/PerspectiveGap/.venv`
- model paths for local contact: no model calls
- model paths for A800_2 smoke:
  - `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`

## Commands

```powershell
git clone --depth 1 https://github.com/WhymustIhaveaname/PerspectiveGap.git D:\develop\AgentCommReliability\baselines\PerspectiveGap\upstream

$env:PYTHONPATH='src'
python scripts\score_predictions.py --predictions tests\fixtures\example_predictions.jsonl

$run='D:\develop\AgentCommReliability\experiments\20260618-local-perspectivegap-contact'
New-Item -ItemType Directory -Force -Path $run | Out-Null
python scripts\build_hf_evaluations.py --out "$run\evaluations.jsonl"
python scripts\score_predictions.py --predictions tests\fixtures\example_predictions.jsonl --out "$run\fixture_scores.jsonl"

python -m venv D:\develop\AgentCommReliability\baselines\PerspectiveGap\.venv
D:\develop\AgentCommReliability\baselines\PerspectiveGap\.venv\Scripts\python.exe -m pip install -e D:\develop\AgentCommReliability\baselines\PerspectiveGap\upstream pytest
D:\develop\AgentCommReliability\baselines\PerspectiveGap\.venv\Scripts\python.exe -m pytest -q
```

Additional local baseline generation and scoring produced:

```text
experiments/20260618-local-perspectivegap-contact/baseline_predictions/*.jsonl
experiments/20260618-local-perspectivegap-contact/baseline_scores_*.jsonl
experiments/20260618-local-perspectivegap-contact/baseline_summary.md
experiments/20260618-local-perspectivegap-contact/structure_summary.json
```

## Outputs

- contact run: `experiments/20260618-local-perspectivegap-contact/`
- rendered evaluations: `experiments/20260618-local-perspectivegap-contact/evaluations.jsonl`
- fixture score rows: `experiments/20260618-local-perspectivegap-contact/fixture_scores.jsonl`
- structure summary: `experiments/20260618-local-perspectivegap-contact/structure_summary.json`
- baseline summary: `experiments/20260618-local-perspectivegap-contact/baseline_summary.md`
- upstream tests: `experiments/20260618-local-perspectivegap-contact/pytest.txt`
- Qwen2.5-7B role-assignment smoke: `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-7b/`
- Qwen2.5-14B role-assignment smoke: `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-14b/`
- paired smoke diff: `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-14b/case_diffs.md`
- paired smoke summary: `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-14b/paired_summary.json`
- stratified 20-scenario A800_2 run: `experiments/20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b/`
- stratified summary: `experiments/20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b/stratified_summary.md`

## What Happened

| Baseline | Task | Samples | Strict Pass | Coverage | Precision | Distractor Leak / Eval | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| oracle | role assignment | 220 | 220/220 | 1.000 | 1.000 | 0.000 | scorer/gold sanity pass |
| oracle | prompt writing | 220 | 220/220 | 1.000 | 1.000 | 0.000 | scorer/gold sanity pass |
| all-to-all | role assignment | 220 | 0/220 | 1.000 | 0.318 | 3.800 | over-sharing fails hard |
| all-to-all | prompt writing | 220 | 0/220 | 1.000 | 0.318 | 3.800 | over-sharing fails hard |
| no-distractor all-to-all | role assignment | 220 | 0/220 | 1.000 | 0.350 | 0.000 | role boundary still fails |
| no-distractor all-to-all | prompt writing | 220 | 0/220 | 1.000 | 0.350 | 0.000 | role boundary still fails |
| shared-intersection only | role assignment | 220 | 0/220 | 0.031 | 1.000 | 0.000 | precision-only under-informs |
| shared-intersection only | prompt writing | 220 | 0/220 | 0.031 | 1.000 | 0.000 | precision-only under-informs |
| role-name heuristic | role assignment | 220 | 0/220 | 0.568 | 0.280 | 3.714 | cheap lexical routing fails |
| role-name heuristic | prompt writing | 220 | 0/220 | 0.568 | 0.280 | 3.714 | cheap lexical routing fails |

The dataset structure is also useful for our project: 220 rows, 110 scenarios, role counts from 2 to 6, fragment counts from 7 to 13, and a mean of 13 role-fragment need events per row.

## First Model Smoke

The first A800_2 smoke used the upstream `run_model_predictions.py` runner on the `role_assignment` task only, with scenarios `pg_000`, `pg_004`, `pg_006`, `pg_070` and shuffle seed `1`.

| Model | Samples | Strict Pass | Coverage | Precision | Distractor Leak / Eval | Counts |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen2.5-7B-Instruct | 4 | 0/4 | 0.549 | 0.903 | 0.000 | tp=28, fp=3, fn=23, leak=0 |
| Qwen2.5-14B-Instruct | 4 | 0/4 | 0.667 | 0.872 | 0.250 | tp=34, fp=5, fn=17, leak=1 |

The small paired result suggests a useful failure surface: the 7B model is conservative and often under-routes needed fragments, while 14B recovers more needed fragments but adds more false positives and one distractor leak. This is only a smoke result, but it is a better next-step target than a generic debate prompt tweak.

I then ran a zero-temperature stratified subset with 20 scenarios and seeds `1, 42`, for 40 requests per model:

| Model | Samples | Strict Pass | Coverage | Precision | Distractor Leak / Eval | Counts |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Qwen2.5-7B-Instruct | 40 | 0/40 | 0.443 | 0.786 | 0.050 | tp=239, fp=65, fn=301, leak=2 |
| Qwen2.5-14B-Instruct | 40 | 0/40 | 0.615 | 0.808 | 0.450 | tp=332, fp=79, fn=208, leak=18 |

The broader subset preserves the main smoke signal: 14B recovers many more required role-fragment events, but it also admits far more distractors. The result is a routing aggressiveness phenomenon, not a stable benchmark ranking.

## Deviations From Upstream

- Used direct `python` with `PYTHONPATH=src` because `uv` is not installed.
- Did not run any provider/model API calls.
- The first `python -m pytest -q` attempt used the active Python environment and failed because `pytest` was missing.
- An isolated `.venv` was then created under `baselines/PerspectiveGap/.venv`; upstream tests passed there with `18 passed`.

## Failures And Fixes

| Issue | Evidence | Fix | Method Behavior Changed? |
| --- | --- | --- | --- |
| `uv` missing | `uv : The term 'uv' is not recognized` | Ran scripts directly with `PYTHONPATH=src` | No |
| `pytest` missing in active env | `No module named pytest` | Created ignored `.venv`, installed upstream package plus `pytest`, and reran tests | No |
| SCR-Bench git clone timeout during scouting | Two `git clone` attempts timed out and were cleaned up | Switched P0 contact to PerspectiveGap, which cloned cleanly | No |

## Caveats

- This is benchmark contact and deterministic baseline scoring, not a model result.
- The A800_2 model smoke covers only 4 scenarios, and the upstream runner does not expose a temperature flag. Treat it as behavior contact, not a stable benchmark score.
- The prompt-writing scorer is deterministic but n-gram based, with inclusion and exclusion thresholds in `src/perspective_gap/scoring.py`.
- PerspectiveGap evaluates orchestration prompt construction and context routing. It is not an end-to-end multi-agent execution benchmark.
- The scenarios are curated English engineering workflows; transfer to HiddenBench-style social/private-information tasks still needs a bridge.
- Dependency installation saw one SSL retry while fetching `pytest`, but installation completed and tests passed.

## Loose Threads

- Run one small model contact on `role_assignment` before spending GPU or API budget on the full 220 rows.
- Build a typed-router baseline that emits role-specific fact cards, then score it against the role-fragment assignment task.
- Compare PerspectiveGap leakage metrics with HiddenBench sender overtalk/recommendation leakage metrics.
