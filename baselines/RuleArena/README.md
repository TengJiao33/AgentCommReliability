# RuleArena

RuleArena is tracked as a benchmark-pressure target for rule-guided reasoning.

Project files:

- `source.md`: upstream source, commit, and code map.
- `reproduction.md`: setup status and planned smoke path.
- `upstream/`: git submodule pinned to the RuleArena source repository.

Initialize the submodule after cloning this project on a new machine:

```bash
git submodule update --init --recursive baselines/RuleArena/upstream
```
