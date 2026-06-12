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
