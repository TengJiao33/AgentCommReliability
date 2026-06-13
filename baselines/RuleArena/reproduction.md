# RuleArena Reproduction Note

## Short Answer

RuleArena is configured as a portable project submodule and the CPU-only loader smoke passes. No model evaluation has been launched yet.

## Scope

- method: RuleArena benchmark
- paper: https://arxiv.org/abs/2412.08972
- repo: https://github.com/skyriver-2000/RuleArena
- commit: `3b9e2256294644beca66732babc5e1055855a576`
- local path: `baselines/RuleArena/upstream`
- target setting: rule-guided benchmark-discrimination pilot
- evidence level: import/data-loader evidence only until a limited model run passes.

## Environment

- local machine: transient; should not be treated as source of truth.
- fixed remote: A800_2, preferred root `/data/xuhaoming/yfy/research_workspace`.
- benchmark source: tracked through project git submodule.
- model paths: planned local Qwen on A800_2 through vLLM, not local workstation APIs.

## Commands

Initialize after cloning this project on any machine:

```bash
git submodule update --init --recursive baselines/RuleArena/upstream
```

CPU-only loader smoke:

```bash
python scripts/rulearena_loader_smoke.py --root baselines/RuleArena/upstream
```

Upstream official example, not yet our planned run path:

```bash
cd baselines/RuleArena/upstream/airline
python auto_test.py --llm claude-3-5-sonnet-20241022 --complexity 1 --use_example
```

## Outputs

- loader smoke: completed; stdout summary showed all `airline`, `nba`, and `tax` problem files are readable.
- future pilot logs: place under `experiments/<run-id>/` locally and `/data/xuhaoming/yfy/research_workspace/results/rulearena-*` remotely.

## Result Snapshot

| Method | Model | Task | Seed | Samples | Metric | Tokens | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| loader smoke | none | airline/nba/tax | n/a | 100/100/100 airline, 81/89/46 nba, 100/100/100 tax | file counts | 0 | complete |

## Deviations From Upstream

- The source is tracked as a submodule inside this project for portability across changing local machines.
- Planned A800_2 runs should use a local vLLM endpoint rather than official external APIs.
- Planned pilot must add a sample limit before calling a model.

## Failures And Fixes

| Issue | Evidence | Fix | Method Behavior Changed? |
| --- | --- | --- | --- |
| Initial clone was placed outside the project at `D:\develop\RuleArena`, which would not sync with this repository. | user correction during setup | added RuleArena as `baselines/RuleArena/upstream` git submodule | no benchmark behavior change |

## Caveats

- No accuracy result exists yet.
- Upstream scripts are single-agent benchmark runners; multi-agent communication variants will need a wrapper that reuses their prompts and evaluators.
- Benchmark pressure tests should remain anchored to original reproduction traces from MAD-MM, DAR, and MOC.

## Next Small Check

- Create a small-run wrapper with `--limit` and OpenAI-compatible vLLM support.
