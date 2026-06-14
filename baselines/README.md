# Baselines

This folder tracks cloned or referenced baseline implementations.

Do not commit large repositories, checkpoints, caches, or generated outputs here unless they are intentionally small and needed for documentation.

For each baseline, create:

```text
baselines/<method>/
  README.md
  source.md
  reproduction.md
  patches/
```

If a baseline is tracked as a git submodule, keep project-local patch files outside
the submodule so the parent repository can track them. Current example:
`baselines/MAD-MM-patches/`.

Tracked baselines:

- `MAD-MM`: Memory Masking for multi-agent debate.
- `DAR`: Diversity-Aware Retention for debate message selection.
- `MOC`: Multi-Order Communication with topology-aware message merging.
- `RuleArena`: benchmark pressure / loader smoke.
- `PACT`: action-state communication surface for split-evidence HotpotQA.

Record:

- upstream URL;
- commit hash;
- license if available;
- install steps;
- smallest runnable command;
- expected outputs;
- known caveats.

Templates:

- `baselines/_templates/source.md`
- `baselines/_templates/reproduction.md`
