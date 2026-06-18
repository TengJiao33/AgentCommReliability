# PerspectiveGap Local Contact

## Purpose

Test whether PerspectiveGap is a usable external benchmark contact for the project's benchmark-first reset, especially for multi-agent information routing, role-specific context assignment, and leakage measurement.

## Unit

One rendered PerspectiveGap evaluation row. Each row has one scenario, one shuffle seed, a set of roles, visible fragments, one distractor, answer-keyed role need sets, and two task prompts.

## Primary Contrast

This contact does not compare model methods yet. The primary contrast is between oracle routing and transparent non-model routing baselines:

- oracle role-specific routing;
- all fragments to all roles;
- all non-distractor fragments to all roles;
- only fragments needed by every role;
- a cheap role-name heuristic.

## Success Signal

PerspectiveGap is worth bringing into the active benchmark surface if:

- the repo can be cloned and inspected;
- official scorer fixture passes locally;
- the 220-row release can be rendered locally;
- oracle reaches 100 percent under the scorer;
- naive all-to-all and shared-only baselines expose a real routing tradeoff rather than trivially passing.

## Failure Signal

The benchmark contact would be weak if:

- renderer or scorer cannot run without provider keys;
- answer keys cannot be audited locally;
- all-to-all or no-distractor routing passes many rows;
- prompt-writing scoring is too opaque to diagnose.

## Invalidation Conditions

- local rendered rows mismatch the released HF data shape;
- scorer depends on remote model calls;
- role_assignment and prompt_writing use incompatible answer semantics;
- deterministic baselines accidentally use hidden answer keys except for the oracle sanity row.

## Commands

Run from `baselines/PerspectiveGap/upstream`:

```powershell
$env:PYTHONPATH='src'
python scripts\score_predictions.py --predictions tests\fixtures\example_predictions.jsonl
python scripts\build_hf_evaluations.py --out D:\develop\AgentCommReliability\experiments\20260618-local-perspectivegap-contact\evaluations.jsonl
python scripts\score_predictions.py --predictions tests\fixtures\example_predictions.jsonl --out D:\develop\AgentCommReliability\experiments\20260618-local-perspectivegap-contact\fixture_scores.jsonl
```

Local deterministic baseline generation produced prediction files under `baseline_predictions/`, then scored them with the upstream scorer.

## Results

The scorer fixture passed:

- role-fragment assignment: `1/1`;
- prompt writing: `1/1`.

The renderer wrote `220` evaluations.

Upstream tests passed in an isolated venv:

```text
18 passed in 3.11s
```

Baseline summary:

| baseline | task | strict pass | coverage | precision | distractor leak/eval | net match |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| oracle | role_assignment | 220/220 (1.000) | 1.000 | 1.000 | 0.000 | 1.000 |
| oracle | prompt_writing | 220/220 (1.000) | 1.000 | 1.000 | 0.000 | 1.000 |
| all_to_all | role_assignment | 0/220 (0.000) | 1.000 | 0.318 | 3.800 | 0.000 |
| all_to_all | prompt_writing | 0/220 (0.000) | 1.000 | 0.318 | 3.800 | 0.000 |
| no_distractor_all_to_all | role_assignment | 0/220 (0.000) | 1.000 | 0.350 | 0.000 | 0.057 |
| no_distractor_all_to_all | prompt_writing | 0/220 (0.000) | 1.000 | 0.350 | 0.000 | 0.057 |
| shared_intersection_only | role_assignment | 0/220 (0.000) | 0.031 | 1.000 | 0.000 | 0.000 |
| shared_intersection_only | prompt_writing | 0/220 (0.000) | 0.031 | 1.000 | 0.000 | 0.000 |
| role_name_heuristic | role_assignment | 0/220 (0.000) | 0.568 | 0.280 | 3.714 | 0.001 |
| role_name_heuristic | prompt_writing | 0/220 (0.000) | 0.568 | 0.280 | 3.714 | 0.001 |

## Interpretation

PerspectiveGap is a strong benchmark contact for information-boundary work. The all-to-all baseline gets full required coverage but zero strict pass and low precision, while the shared-intersection baseline has perfect precision but almost no coverage. The no-distractor all-to-all baseline still gets zero strict pass, so the benchmark is not merely asking models to remove a generic prompt-engineering distractor.

This is a better external pressure point than another local HiddenBench sender-format ablation. It directly evaluates role-specific routing: which fragments should enter each sub-agent prompt, and which fragments should stay out.

## Caveats

- No model was run in this contact.
- `pytest` was missing from the active environment, so tests were rerun in an ignored local `.venv`.
- The prompt-writing scorer uses distinctive n-gram matching and thresholds, so future model runs should include role_assignment first for cleaner parsing.
- This is orchestration prompt construction, not an end-to-end agent execution benchmark.

## Next Artifact

Build `PerspectiveGap` role-assignment model contact:

- run a small slice such as `pg_000,pg_004,pg_006,pg_070` with `role_assignment`;
- compare raw model output to oracle, all-to-all, and no-distractor baselines;
- inspect errors as leak, missing-needed-fragment, or role-confusion cases;
- only then decide whether to run the full 220-row slice.
