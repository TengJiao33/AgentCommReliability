# Experiments

Create one subfolder per run or small group of related runs.

Large raw outputs should stay on the remote machine under the project-specific `results/` directory. This local folder should keep commands, summaries, small derived files, and run notes that let us return to what happened.

## Current Surface

As of `2026-06-18`, top-level experiment directories are limited to the benchmark-first evidence spine, active external-pressure contact, State Admission / PerspectiveGap pressure runs, and recent diagnostic branches that explain why old MATH / TypeCast scaling stopped. Older reproduction contact, superseded packets, weak probes, and failed intermediate TypeCastArena branches are archived under:

```text
experiments/_archive/20260616-pruned/
```

Archived runs are still evidence. A run becomes top-level again only if it is reopened as active support for the current story.

## Active Runs And Packets

- `20260618-local-state-admission-v2-preflight`
- `20260618-local-state-admission-v2-smoke`
- `20260618-1738-a8002-state-admission-v2-direct-admissible-smoke9-qwen25-14b`
- `20260618-1732-a8002-state-admission-v2-direct-allfacts-smoke9-qwen25-14b`
- `20260618-1724-a8002-state-admission-v2-option-state-smoke9-qwen25-14b`
- `20260618-1710-a8002-state-admission-v2-option-state-smoke9-qwen25-7b`
- `20260618-1650-a8002-state-admission-v2-smoke9-qwen25-7b`
- `20260618-local-state-admission-v1`
- `20260618-a8002-state-admission-v1-full40-qwen25-14b`
- `20260618-a8002-state-admission-v1-budgetfirst-full40-qwen25-14b`
- `20260618-a8002-state-admission-v1-priority-full40-qwen25-14b`
- `20260618-a8002-state-admission-v1-priority-full40-qwen25-7b`
- `20260618-a8002-state-admission-v1-priority-fallback-full40-qwen25-7b`
- `20260618-a8002-state-admission-v1-ledger-full40-qwen25-7b`
- `20260618-local-perspectivegap-contact`
- `20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b`
- `20260617-20260617-095907-a8002-hiddenbench-smoke12-qwen25-14b`
- `20260617-20260617-101316-a8002-hiddenbench-smoke12-answerfirst-qwen25-14b`
- `20260617-20260617-102311-a8002-hiddenbench-full65-answerfirst-qwen25-14b`
- `20260617-162153-a8002-hiddenbench-v2-stage1-smoke12-qwen25-14b`
- `20260617-163732-a8002-hiddenbench-v2-stage1-full65-qwen25-14b`
- `20260617-1752-a8002-hiddenbench-v2-stage2-sender-ablation-smoke12-qwen25-14b`
- `20260617-1807-a8002-hiddenbench-v2-stage2-sender-ablation-full65-qwen25-14b`
- `20260617-local-math-operator-lifecycle-v1-packet`
- `20260617-0900-a8002-math-operator-lifecycle-v1-qwen25-14b`
- `20260615-1151-a8002-typed-public-state-math200-anon`
- `20260615-1655-a8002-pact-public-state-field-qwen25-14b`
- `20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b`
- `20260615-2040-a8002-pact-authority-evidence-stress-qwen25-14b`
- `20260615-2223-a8002-pact-typed-boundary-split-qwen25-14b`
- `20260615-local-math200-peer-claim-hygiene`
- `20260615-local-math-authority-genesis-ladder-packet`
- `20260615-local-pact-public-state-field-bridge`
- `20260615-local-pact-public-state-field-packet`
- `20260615-local-pact-field-contract-verifier`
- `20260615-local-pact-typed-boundary-split-packet`
- `20260616-0102-a8002-math-authority-genesis-ladder-qwen25-14b-max768`
- `20260616-1200-a8002-math-type-erasure-v2-qwen25-14b-full222`
- `20260616-1338-a8002-math-sender-receiver-full246-qwen25-14b`
- `20260616-1751-a8002-typecast-math200-sender200-qwen25-7b`
- `20260616-2001-a8002-typecast-math200-clean-receiver304-qwen25-14b`
- `20260617-0033-a8002-typecast-math200-inert-receiver315-qwen25-14b`
- `20260617-0148-a8002-typecast-repaired-controlstable117-qwen25-14b`
- `20260616-local-math-authority-genesis-mechanism-audit`
- `20260616-local-math-epistemic-type-erasure-v2-packet`
- `20260616-local-math-sender-receiver-micro-protocol-packet`
- `20260616-local-math-type-erasure-v2-invalid-cast-audit`
- `20260616-local-typecast-arena-math200-clean-decisive-receiver-packet`
- `20260616-local-typecast-arena-math200-clean-rawgold-candidatewrong-receiver-packet`
- `20260616-local-typecast-arena-math200-decisive-source-rawgold`
- `20260617-local-typecast-arena-math200-rawgold-candidatewrong-inert-receiver-packet`
- `20260617-local-typecast-arena-math200-repaired-controlstable-receiver-packet`

## Templates

- Run note: `experiments/_templates/run_README.md`
- Machine-readable manifest: `experiments/_templates/manifest.json`

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
