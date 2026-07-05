# CPAC-DCAC guard-v1 MATH500 full

## Purpose

Run a full MATH-500 diagnostic for CPAC+DCAC after adding conservative DCAC flip admission guards.

The diagnostic question is narrow: whether guard-v1 reduces DCAC harm from bad certificate labels, unsupported challenger answers, arithmetic mismatches, and representation-risk flips.

## Design

- Task: `math500/test`, full 500 rows.
- Unit: one MATH-500 problem.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- Method: `scripts/run_cpac_dcac.py`.
- Protocol: Candidate-Pool Adaptive Consensus with guarded DCAC for the minority-bearing branch.
- Agents: 3 independent initial solvers.
- Reviewers: 3 certificate/listwise reviewers.
- No-majority action: `listwise`.
- DCAC flip rule: require 2 guarded admissible flip certificates.
- Primary contrast: same-run initial majority accuracy vs guard-v1 final accuracy.
- Secondary contrasts:
  - Previous CPAC+DCAC full: final 325/500, DCAC branch net -4, `MaC_to_W=10`.
  - Offline replay over old records: guard-v1 counterfactual final 329/500, `MaC_to_W=6`.
- Key readouts: DCAC branch `MaW_to_C`, `MaC_to_W`, wrong-to-wrong flips, guard-blocked flips, guard rejection reasons, listwise branch net, final parse failures.

## Claim Gate

This run is diagnostic, not a final method claim.

Success signal: final accuracy exceeds the previous CPAC+DCAC full result while DCAC branch harm decreases, especially `MaC_to_W`.

Failure signal: guard-v1 blocks useful recoveries, DCAC remains negative, or the result is not interpretable because of execution/evaluator/output issues.

Invalidation conditions: evaluator smoke failure, code sync failure, wrong or missing dataset, output directory collision, execution timeout/crash, missing records/summary, large parse failure rate, or incompatible evaluator behavior.

## Machine

- Host: `A800_2`.
- Remote work dir: `/data/xuhaoming/yfy/research_workspace`.
- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`.
- GPU: `7`.
- GPU preflight: GPU 7 had 4 MiB used, 81149 MiB free, and 0% utilization.
- Storage preflight: `/data` had 680G available; `/mnt/quarkfs` had 3.3T available.

## Sync

| Local path | Remote path | Purpose | Deletable |
| --- | --- | --- | --- |
| `scripts/run_cpac_dcac.py` | `/data/xuhaoming/yfy/research_workspace/scripts/run_cpac_dcac.py` | Guard-v1 runner source | No, active code |
| `scripts/run_basic_mad.py` | `/data/xuhaoming/yfy/research_workspace/scripts/run_basic_mad.py` | Evaluator/parser dependency | No, active code |
| `scripts/run_consensus_quarantine.py` | `/data/xuhaoming/yfy/research_workspace/scripts/run_consensus_quarantine.py` | Candidate-card and generation dependency | No, active code |
| `scripts/run_mad_mm.py` | `/data/xuhaoming/yfy/research_workspace/scripts/run_mad_mm.py` | Benchmark question preparation dependency | No, active code |
| `experiments/20260705-a8002-math500-cpac-dcac-guard-v1-qwen25-7b-full/run_remote.sh` | `/data/xuhaoming/yfy/research_workspace/experiments/20260705-a8002-math500-cpac-dcac-guard-v1-qwen25-7b-full/run_remote.sh` | Remote launch script | Yes after run record is complete |

## Launch

See `run_remote.sh`.

## Status

`COMPLETED`.

Launched on 2026-07-05 19:31 CST and completed on 2026-07-05 19:57 CST.

- `run_remote.sh` PID: `2912298`.
- Python PID at launch check: `2912373`.
- GPU: `7`.
- Log: `/data/xuhaoming/yfy/research_workspace/experiments/20260705-a8002-math500-cpac-dcac-guard-v1-qwen25-7b-full/run_remote.nohup.log`.
- Completion check: no matching `run_cpac_dcac.py` process remained; GPU 7 was back to idle.

## Expected Outputs

- `math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.md`
- `run_remote.nohup.log`
- `run_remote.pid`

## Result

| Readout | Value |
| --- | ---: |
| Rows | 500 |
| Initial majority correct | 320/500 = 0.640 |
| Guard-v1 final correct | 332/500 = 0.664 |
| Net vs initial majority | +12 |
| Final parse failures | 0 |
| Final majority ties | 2/500 = 0.004 |
| Answer changed | 38/500 = 0.076 |
| `MaC_to_C` | 317 |
| `MaC_to_W` | 3 |
| `MaW_to_C` | 15 |
| `MaW_to_W` | 165 |

Compared with the previous CPAC+DCAC full run, guard-v1 improved final correct from 325/500 to 332/500. The main observed improvement is reduced harm to initially correct majorities: `MaC_to_W` fell from 10 to 3 while `MaW_to_C` stayed at 15.

Branch/action counts:

| Branch/action | Count |
| --- | ---: |
| `keep_initial` | 220 |
| `dcac` | 189 |
| `listwise_discriminant` | 91 |
| DCAC flips | 10 |
| Guard-blocked DCAC flips | 6 |
| Guard-rejected certificates | 161 |
| Valid directional claims | 65 |
| Representation-risk cases | 148 |

## Interpretation

This run supports the narrow diagnostic claim that guard-v1 reduced harmful DCAC flips in the old CPAC+DCAC setting. It does not enter the new main comparison table, because it still uses the old parameter regime: temperature 0.8, top-p 0.95, max tokens 2048, and max model length 8192.
