# Reproduction Recording Standard

This project uses a reproduction-first workflow. Every result should be traceable from a short local note to exact remote logs and raw outputs.

## Record Types

Use four layers:

1. Paper card: why the method matters and what communication variables it exposes.
2. Baseline note: upstream repo, commit, install details, local patches, and standard commands.
3. Experiment run note: one concrete run or bounded run group.
4. Report: interpretation after multiple comparable runs exist.

Do not put interpretation into raw run notes unless it is clearly labeled as a hypothesis.

Longer artifact boundaries and evidence levels are defined in `docs/documentation_system.md`.

## Run ID

Use:

```text
YYYYMMDD-HHMM-<machine>-<method>-<model>-<task>-<scope>
```

Examples:

```text
20260612-1455-a8002-madmm-qwen25-14b-gsm8k-cot-short
20260612-1508-a8002-madmm-qwen25-14b-gsm8k-mad-naive-short
```

Recommended scope tags:

- `setup`: environment, model, or data preparation only.
- `short`: bounded subset intended to finish quickly.
- `standard`: author-provided main path or full matrix.
- `analysis`: extra ablation or diagnostic run.
- `failed`: preserved failure evidence.

## Required Files

Each run directory under `experiments/<run-id>/` should contain:

```text
README.md
manifest.json
```

Optional, when useful:

```text
config.yaml
summary.json
notes.md
```

Large logs and raw outputs can stay on the remote machine, but their absolute paths must be recorded locally.

## README Sections

Use this order:

```markdown
# <run-id>

## Short Answer

## Scope

## Resource Budget

## Code

## Environment

## Data

## Command

## Remote Artifacts

## Result

## Status Timeline

## Caveats

## Next Step
```

## Manifest Fields

`manifest.json` is for quick parsing and comparison. Keep it small and factual.

Required fields:

- `run_id`
- `status`
- `method`
- `model`
- `dataset`
- `seed`
- `machine`
- `gpu_ids`
- `timeout_minutes`
- `started_at`
- `ended_at`
- `upstream_repo`
- `upstream_commit`
- `local_changes`
- `command`
- `log_path`
- `result_paths`
- `metrics`
- `caveats`

Allowed statuses:

- `prepared`
- `running`
- `stopped`
- `failed`
- `complete`

## Resource Rules

Before launch, record:

- intended GPU IDs;
- timeout;
- expected method and dataset;
- whether the job is one step or a multi-step matrix.

Default for shared A800 work:

- prefer one GPU;
- use `timeout`;
- run one method step at a time;
- start the next step only after checking logs and GPU state.

Do not launch full author matrices without a written resource estimate.

## Evidence Language

Use precise labels:

- `setup evidence`: environment/model/code path prepared.
- `short-subset evidence`: one bounded method/task/model subset ran.
- `standard-subset evidence`: author settings for a reduced matrix.
- `full reproduction evidence`: complete claimed reproduction matrix finished.

Avoid saying "reproduced the paper" unless the full target matrix has finished and metrics were compared.

## Result Summary

For each completed method, record:

```text
method:
model:
dataset:
seed:
samples:
accuracy:
total_tokens:
eval_time:
wall_time:
result_json:
trace_log:
```

For stopped or failed runs, record:

```text
where stopped:
why stopped:
gpu released:
partial outputs:
next safer command:
```

## Artifact Policy

Local repo keeps:

- concise run notes;
- manifests;
- small summaries;
- report drafts.

Remote workspace keeps:

- raw logs;
- full JSON outputs;
- model caches;
- generated intermediate traces.

Never record passwords, private tokens, SSH keys, or proxy contents.
