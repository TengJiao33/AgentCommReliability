# CPAC-DCAC MATH500 full

## Purpose

Run the first full MATH-500 diagnostic for the CPAC+DCAC runner after local unit tests validated the state-diagnosis and certificate-parsing logic.

## Design

- Task: `math500/test`, full 500 rows.
- Unit: one MATH-500 problem.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- Method: `scripts/run_cpac_dcac.py`.
- Protocol: Candidate-Pool Adaptive Consensus with DCAC for the minority-bearing branch.
- Agents: 3 independent initial solvers.
- Reviewers: 3 certificate/listwise reviewers.
- No-majority action: `listwise`.
- DCAC flip rule: require 2 admissible flip certificates.
- Primary contrast: same-run initial majority accuracy vs CPAC+DCAC final accuracy.
- Secondary readouts: pool-state distribution, action distribution, DCAC case rate, valid directional claim rate, DCAC flip rate, listwise case rate, answer-change rate, wrong-majority recovery rate, correct-majority preservation rate, final tie rate, parse fail rate, representation-risk rate.

## Claim Gate

This run can diagnose whether the CPAC+DCAC runner has a full-split signal and whether its branch distribution matches the candidate-pool hypothesis. It is not a final method claim.

Success signal: final accuracy exceeds same-run initial majority while keeping correct-majority harms lower than recoveries, and DCAC/listwise branch metrics are interpretable.

Failure signal: final accuracy is at or below initial majority, or parse/tie/branch behavior makes the result uninterpretable.

Invalidation conditions: evaluator smoke failure, wrong gold/evaluator behavior, output directory collision, execution timeout/crash, reviewer prompts leaking support counts, missing output files, or large final parse failure rate.

## Machine

- Host: `A800_2`.
- Remote work dir: `/data/xuhaoming/yfy/research_workspace`.
- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`.
- GPU: `7`.

## Launch

See `run_remote.sh`.

## Status

`COMPLETED`.

## Validation

- Remote evaluator smoke passed for boxed fractions, mixed fractions, tuple-with-pi, symbolic string `p-q`, and placeholder-answer rejection.
- Representation-risk diagnostic confirmed the known base-notation caveat: `52_8` is still normalized incorrectly by the current evaluator.
- Output files were pulled back from `A800_2`:
  - `math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
  - `math500-qwen25-7b-instruct-cpac-dcac/summary.json`
  - `math500-qwen25-7b-instruct-cpac-dcac/summary.md`
  - `run_remote.nohup.log`
- `records.jsonl` contains 500 rows.
- `summary.json` reports 500 rows.
- Final parse failures: 0/500.
- Remote cleanup check after completion: GPU 7 returned to 4 MiB used and 0% utilization.

## Outputs

- `math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- `math500-qwen25-7b-instruct-cpac-dcac/summary.md`
- `run_remote.nohup.log`

## Result

| Readout | Correct | Accuracy |
| --- | ---: | ---: |
| Same-run initial majority | 320/500 | 0.640 |
| CPAC+DCAC final | 325/500 | 0.650 |

Net delta: +5/500, or +1.0 percentage point, against the same-run initial majority.

Additional metrics:

| Metric | Value |
| --- | ---: |
| Collapse / keep-initial cases | 220/500 |
| DCAC cases | 189/500 |
| Listwise discriminant cases | 91/500 |
| Valid directional claims | 65 |
| DCAC flips | 17 |
| Answer changed | 52/500 |
| Wrong-majority recoveries (`MaW_to_C`) | 15 |
| Correct-majority harms (`MaC_to_W`) | 10 |
| Correct-majority preservation | 310/320 = 0.969 |
| Final tie rate | 5/500 = 0.010 |
| Final parse failures | 0/500 |
| Representation-risk cases | 148/500 |
| Elapsed | 1488.4s |

## Branch Triage

| Branch | n | MaW -> C | MaC -> W | Net |
| --- | ---: | ---: | ---: | ---: |
| keep initial / collapse | 220 | 0 | 0 | 0 |
| DCAC | 189 | 4 | 8 | -4 |
| listwise discriminant | 91 | 11 | 2 | +9 |

DCAC flips were conservative in count but not yet high precision: 17 total flips produced 4 recoveries, 8 harms, and 5 wrong-to-wrong transitions. The positive net result came from the no-majority listwise branch, not from DCAC.

## Interpretation

This run supports a narrow diagnostic claim: the CPAC state split executed end to end on MATH-500 full, produced interpretable branch counts, and improved same-run initial majority by 5 questions under the current evaluator.

This run does not support DCAC as currently prompted. The DCAC branch had a negative net effect, while listwise handling of no-majority conflict had the positive branch contribution. The result is therefore stronger evidence for the CPAC outer state controller than for the current DCAC certificate prompt/decision rule.

## Caveats

The current local evaluator has known representation-risk caveats around `\pi`, matrices/vectors, base notation, and function expressions. This run should be interpreted as a diagnostic under the current evaluator until those cases are audited or the evaluator is unified.

This run is not directly comparable to CQG as a method-quality proof. It uses the same model and dataset, but a different prompt contract and an additional listwise branch. The local CQG full run had a larger same-run delta (+17), so CPAC+DCAC is not currently the stronger absolute diagnostic system.
