# Experiments

Create one subfolder per run or small group of related runs.

Example:

```text
experiments/
  20260628-1430-a8002-madmm-qwen25-gsm8k-memory-mask-smoke/
    README.md
    config.yaml
    summary.json
```

Large raw outputs should stay on the remote machine under the project-specific `results/` directory. This local folder should keep commands, summaries, and small files that help us return to what happened.

## Templates

- Run note: `experiments/_templates/run_README.md`
- Machine-readable manifest: `experiments/_templates/manifest.json`

## Recent Runs

- `20260613-1425-a8002-moc-qwen25-7b-gsm8k-hop2-forcedmerge-smoke`: MOC `neighbor_hops=2` forced structural-merge smoke with unified trace output.

## Useful Run Notes

Each run should usually state:

- exact command;
- model, task, seed, and sample count;
- machine and GPU IDs;
- timeout or resource budget;
- upstream repo and commit;
- local changes;
- remote artifact paths;
- metric snapshot;
- caveats.

If a run is stopped or fails, preserve it. A stopped run is often the most honest record of cost, missing assumptions, or unsafe resource use.
