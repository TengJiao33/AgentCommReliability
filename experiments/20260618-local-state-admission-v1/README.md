# State Admission V1.1 Local Packet

## Purpose

This packet turns the rotated PerspectiveGap source/scope task into a role-scoped evidence-admission diagnostic with three extra constraints:

- role evidence is a bundle with dependency closure;
- singleton fragments can look attractive but release no bundle utility alone;
- a row-level global budget forces coupled selection across roles;
- pair-group utility includes density-trap decoys, so item and bundle greedy baselines can be separated from the exact oracle.

The intended readout is whether item-level, bundle-level, and group-level greedy baselines still nearly solve the packet. This is a local benchmark-shape diagnostic, not a model result.

## Packet

- Source packet: `experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl`
- Output packet: `state_admission_v1_rotated20.jsonl`
- Rows: `40`
- Role rows: `160`
- Roles with bundles: `160`
- Oracle-served roles: `92`
- Mean oracle-served role rate: `0.575`
- Cross-role oracle rows: `32/40`
- Single-role fallback rows: `8/40` (`2`-role rows where the global budget cannot fit the full pair group)
- Target pair groups: `32`
- Overlap decoy pair groups: `127`
- Full bundle cost: `1020`
- Global budget sum: `673`
- Global budget ratio: `0.660`
- Oracle utility: `33561`
- Role-count distribution: `2/3/4/5/6 roles`, `8` rows each

## Local Baselines

| Condition | Strict | Coverage | Precision | Utility ratio | Global budget pass | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| oracle | 40/40 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| eligible_all | 0/40 | 1.000 | 0.302 | 0.000 | 0.000 | 0.000 |
| item_density_per_role | 0/40 | 0.816 | 0.383 | 0.000 | 0.000 | 1.150 |
| item_density_global | 0/40 | 0.564 | 0.327 | 0.041 | 1.000 | 2.000 |
| bundle_density_global | 14/40 | 0.509 | 0.374 | 0.449 | 1.000 | 0.000 |
| cheapest_bundle_global | 14/40 | 0.485 | 0.350 | 0.424 | 1.000 | 0.000 |
| group_density_global | 32/40 | 0.902 | 1.000 | 0.967 | 1.000 | 0.000 |

## Commands

```powershell
python scripts\build_state_admission_v1_packet.py `
  --packet experiments\20260618-local-perspectivegap-tight-budget-v0\tight_budget_rotated20.jsonl `
  --out experiments\20260618-local-state-admission-v1\state_admission_v1_rotated20.jsonl `
  --global-budget-fraction 0.68
```

```powershell
python scripts\generate_state_admission_v1_baselines.py `
  --packet experiments\20260618-local-state-admission-v1\state_admission_v1_rotated20.jsonl `
  --baseline bundle_density_global `
  --out experiments\20260618-local-state-admission-v1\predictions_bundle_density_global.jsonl
```

```powershell
python scripts\score_state_admission_v1.py `
  --packet experiments\20260618-local-state-admission-v1\state_admission_v1_rotated20.jsonl `
  --predictions experiments\20260618-local-state-admission-v1\predictions_bundle_density_global.jsonl `
  --out experiments\20260618-local-state-admission-v1\scores_bundle_density_global.jsonl `
  --summary-out experiments\20260618-local-state-admission-v1\summary_bundle_density_global.md
```

## Generated Files

- `predictions_<baseline>.jsonl`
- `scores_<baseline>.jsonl`
- `summary_<baseline>.md`
- `predictions_priority_<baseline>.jsonl`
- `scores_priority_<baseline>.jsonl`
- `summary_priority_<baseline>.md`
- `prompt_audit_sample5.jsonl`
- `prompt_audit_stratified5.jsonl`
- `prompt_audit_budget_first_stratified5.jsonl`
- `prompt_audit_priority_stratified5.jsonl`

Baselines generated: `oracle`, `eligible_all`, `item_density_per_role`, `item_density_global`, `bundle_density_global`, `cheapest_bundle_global`.
`group_density_global` is also generated as a stronger symbolic baseline that can see pair-group utility.

Priority-executor local smokes:

| Condition | Strict | Coverage | Precision | Utility ratio | Global budget pass | Closure violations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| priority_oracle | 40/40 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| priority_group_density | 32/40 | 0.902 | 1.000 | 0.967 | 1.000 | 0.000 |
| ledger_oracle | 40/40 | 1.000 | 1.000 | 1.000 | 1.000 | 0.000 |
| ledger_utility_density | 4/40 | 0.736 | 0.511 | 0.493 | 1.000 | 1.050 |
| ledger_hint_density | 4/40 | 0.706 | 0.477 | 0.402 | 1.000 | 1.100 |

## Prompt Audit

The state-admission runner is available at `scripts/run_state_admission_v1_openai_compatible.py`.
The A800 launch wrapper is available at `scripts/run_state_admission_v1_a8002.sh`; by default it runs the same stratified 5-row smoke with Qwen2.5-14B, `MAX_MODEL_LEN=16384`, and `MAX_TOKENS=1536`.

Prompt dry run command:

```powershell
python scripts\run_state_admission_v1_openai_compatible.py `
  --packet experiments\20260618-local-state-admission-v1\state_admission_v1_rotated20.jsonl `
  --dry-run-prompts-out experiments\20260618-local-state-admission-v1\prompt_audit_stratified5.jsonl `
  --hard-evaluation-id pg_000__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1 `
  --hard-evaluation-id pg_002__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1 `
  --hard-evaluation-id pg_006__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1 `
  --hard-evaluation-id pg_004__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1 `
  --hard-evaluation-id pg_005__seed_1__source_rotated_scope_v0__tightbf55_rank_scope_v0__state_admission_v1
```

Prompt audit summary:

| Role count | Prompt chars | Bundles | Pair groups |
| ---: | ---: | ---: | ---: |
| 2 | 5611 | 2 | 1 |
| 3 | 8358 | 3 | 3 |
| 4 | 12547 | 4 | 6 |
| 5 | 13288 | 5 | 10 |
| 6 | 15065 | 6 | 15 |

The prompt exposes budgets, bundles, pair groups, source eligibility, standalone hints, and payload previews. It does not include `oracle_roles`, `oracle_groups`, or target recipients.

Launch-wrapper static checks:

```powershell
python -m py_compile scripts\run_state_admission_v1_openai_compatible.py scripts\score_state_admission_v1.py
bash -n scripts/run_state_admission_v1_a8002.sh
```

## Qwen2.5-14B Model Pressure

Two full40 A800 runs were launched on `A800_2`, GPU `7`, port `8071`, using `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`, `temperature=0`, `MAX_MODEL_LEN=16384`, and `MAX_TOKENS=1536`. Both runs completed `40/40` rows and the launch script cleaned up vLLM after scoring.

| Run | Prompt style | Strict | Coverage | Precision | Global budget pass | Global overrun | Utility ratio | Raw utility ratio |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `20260618-a8002-state-admission-v1-full40-qwen25-14b` | `default` | 0/40 | 1.0000 | 0.4025 | 0.0000 | 15.3250 | 0.0000 | 1.0307 |
| `20260618-a8002-state-admission-v1-budgetfirst-full40-qwen25-14b` | `budget_first` | 0/40 | 0.7914 | 0.4464 | 0.1000 | 7.1500 | 0.0203 | 0.8114 |
| `20260618-a8002-state-admission-v1-priority-full40-qwen25-14b` | `priority + greedy executor` | 28/40 | 0.8957 | 0.8202 | 1.0000 | 0.0000 | 0.9067 | 0.9067 |
| same priority responses, offline recompile | `priority + pair_group_primary executor` | 33/40 | 0.8712 | 0.9103 | 1.0000 | 0.0000 | 0.9014 | 0.9014 |
| `20260618-a8002-state-admission-v1-priority-full40-qwen25-7b` | `priority + pair_group_primary executor` | 25/40 | 0.7546 | 0.9044 | 1.0000 | 0.0000 | 0.8530 | 0.8530 |
| same 7B priority responses, normalized offline recompile | `priority + pair_group_primary executor` | 26/40 | 0.7853 | 0.9078 | 1.0000 | 0.0000 | 0.8828 | 0.8828 |
| `20260618-a8002-state-admission-v1-priority-fallback-full40-qwen25-7b` | `priority fallback_required + pair_group_primary executor` | 31/40 | 0.8344 | 0.8718 | 1.0000 | 0.0000 | 0.8431 | 0.8431 |
| `20260618-a8002-state-admission-v1-ledger-full40-qwen25-7b` | `ledger-first source priority + budget compiler` | 1/40 | 0.4417 | 0.4645 | 1.0000 | 0.0000 | 0.0409 | 0.0409 |

Default prompt triage:

- expected nonempty roles: `63/78` exact, `15/78` supersets, `0/78` misses;
- expected empty roles filled: `82/82`;
- per-role over-budget roles: `44/160`;
- global-budget-valid rows: `0/40`.

Budget-first prompt triage:

- expected nonempty roles: `57/78` exact, `3/78` supersets, `18/78` misses;
- expected empty roles filled: `68/82`;
- per-role over-budget roles: `10/160`;
- global-budget-valid rows: `4/40`;
- strict rows: `0/40`.

Interpretation: Qwen2.5-14B recognizes many useful source bundles, but does not reliably execute the global admission decision. Stronger budget wording reduces over-admission while losing necessary coverage.

Priority-executor interpretation: changing the model output from source cards to group/bundle priorities and enforcing admission with deterministic rules removes budget and closure failures. The 7B replication keeps legality intact, but drops strict and coverage relative to 14B. Conservative unit-id normalization rescues only one additional strict row, while a `fallback_required` schema raises 7B strict to `31/40`; the remaining gap is priority quality and the dependence on exposed admission-unit tables.

Ledger-first interpretation: when the group/bundle tables are hidden and the model must construct admission units from source ledger plus payload, strict collapses to `1/40` despite clean budget and reject behavior. This makes admission-unit construction the next pressure point.

See `reports/20260618-state-admission-v1-qwen25-14b-pressure.md`, `reports/20260618-state-admission-v1-priority-executor-pressure.md`, and `reports/20260618-state-admission-v1-priority-7b-replication.md`.

## Caveats

This packet is synthetic over PerspectiveGap-derived fragments. The dependency bundle, density-trap utility, and cross-role group objectives are imposed by the benchmark builder, so this run only validates the pressure shape. It does not show that an LLM can solve the task, or that a compiler method improves real task outcomes.

Eight `2`-role rows fall back to single-role oracle selection because the global budget cannot fit their full cross-role pair. The packet is therefore a mixed pressure object: all `3`- to `6`-role rows use cross-role group utility, while `2`-role rows mainly test bundle closure and global scarcity.

The `group_density_global` baseline remains strong at `32/40` strict and `0.967` utility ratio. This means V1.1 is not yet a hard combinatorial-optimization benchmark; it is more useful as a model-facing test of whether LLMs can follow explicit structured admission constraints as well as a simple symbolic planner.

The next useful step is a packet audit over concrete rows, then a small 7B/14B run with strict JSON output. If the prompt cannot expose bundle and group constraints clearly, the benchmark needs a schema-facing redesign before GPU scaling.
