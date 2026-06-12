# Experiments

Create one subfolder per run or ablation group.

Example:

```text
experiments/
  20260628-1430-a8002-madmm-qwen25-gsm8k-memory-mask-smoke/
    README.md
    config.yaml
    summary.json
```

Large raw outputs should stay on the remote machine under the project-specific `results/` directory. This local folder should keep commands, summaries, and small evidence files.

## Templates

- Run note: `experiments/_templates/run_README.md`
- Machine-readable manifest: `experiments/_templates/manifest.json`

## Minimum Standard

Each run should state:

- exact command;
- model, task, seed, and sample count;
- machine and GPU IDs;
- timeout or resource budget;
- upstream repo and commit;
- local changes;
- remote artifact paths;
- metric snapshot;
- evidence level;
- caveats.

If a run is stopped or fails, preserve it. A stopped run is often useful evidence about cost, missing assumptions, or unsafe resource use.
