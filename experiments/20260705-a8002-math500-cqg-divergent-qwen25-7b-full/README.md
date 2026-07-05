# CQG Divergent MATH500 full

## Purpose

Run the full MATH-500 Consensus Quarantine Gate diagnostic after smoke tests only validated integration behavior.

## Design

- Task: `math500/test`, full 500 rows.
- Unit: one MATH-500 problem.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- Method: `scripts/run_consensus_quarantine.py`.
- Quarantine mode: `divergent`, meaning non-unanimous initial majorities enter quarantine/review.
- Agents: 3 independent initial solvers.
- Reviewers: 3 blind reviewers for quarantined cases.
- Primary contrast: same-run initial majority accuracy vs CQG final accuracy.
- Secondary readouts: quarantine rate, answer-change rate, wrong-majority recovery rate, correct-majority preservation rate, final tie rate, parse fail rate, valid appeal rate.

## Claim Gate

This run can diagnose whether the current CQG implementation has a full-split signal. It is not a final method claim if the appeal gate still produces few/no valid appeals or if blind review harms correct majorities at a comparable rate to recoveries.

Success signal: final accuracy exceeds same-run initial majority, with non-trivial wrong-majority recoveries and high correct-majority preservation.

Failure signal: final accuracy is at or below initial majority, or correct-majority harms offset recoveries.

Invalidation conditions: final parse failures, wrong gold/evaluator behavior, output directory collision, execution timeout/crash, or review prompts leaking support counts.

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

- Remote evaluator smoke in `run_remote.nohup.log` passed for boxed fractions, mixed fractions, tuple/symbolic answers, symbolic strings, and placeholder-answer rejection.
- Output files were pulled back from `A800_2`:
  - `math500-qwen25-7b-instruct-cqg-divergent/records.jsonl`
  - `math500-qwen25-7b-instruct-cqg-divergent/summary.json`
  - `math500-qwen25-7b-instruct-cqg-divergent/summary.md`
- `records.jsonl` contains 500 rows locally and remotely.
- `summary.json` reports 500 rows.
- Final parse failures: 0/500.
- Remote cleanup check after completion: no matching `run_consensus_quarantine.py` / run-id process remained; GPU 7 returned to 4 MiB used and 0% utilization.

## Result

| Readout | Correct | Accuracy |
| --- | ---: | ---: |
| Same-run initial majority | 320/500 | 0.640 |
| CQG final | 337/500 | 0.674 |

Net delta: +17/500, or +3.4 percentage points, against the same-run initial majority.

Additional metrics:

| Metric | Value |
| --- | ---: |
| Quarantined cases | 189/500 = 0.378 |
| Appeal prompts | 189 |
| Valid appeals | 35/189 = 0.185 |
| Answer changed | 73/500 = 0.146 |
| Wrong-majority recoveries (`MaW_to_C`) | 34 |
| Correct-majority harms (`MaC_to_W`) | 17 |
| Correct-majority preservation | 303/320 = 0.947 |
| Wrong-majority recovery rate | 34/180 = 0.189 |
| Final tie rate | 92/500 = 0.184 |
| Elapsed | 1941.1s |

## Concrete Triage

Representative `MaW_to_C` recoveries:

| Index | Id | Gold | Initial majority | CQG final | Valid appeals |
| ---: | --- | --- | --- | --- | ---: |
| 8 | `test/algebra/2036.json` | `3\sqrt{13}` | `expr:5*sqrt(5)` | `expr:3*sqrt(13)` | 0 |
| 29 | `test/counting_and_probability/666.json` | `225` | `expr:5` | `expr:225` | 0 |
| 32 | `test/counting_and_probability/134.json` | `720` | `expr:120` | `expr:720` | 0 |
| 42 | `test/algebra/2214.json` | `4` | `expr:3` | `expr:4` | 0 |
| 50 | `test/number_theory/1055.json` | `203` | `expr:216` | `expr:203` | 0 |

Representative `MaC_to_W` harms:

| Index | Id | Gold | Initial majority | CQG final | Valid appeals |
| ---: | --- | --- | --- | --- | ---: |
| 19 | `test/intermediate_algebra/1000.json` | `3` | `expr:3` | `expr:4` | 0 |
| 30 | `test/number_theory/864.json` | `52_8` | `expr:8` | `expr:52` | 0 |
| 46 | `test/precalculus/285.json` | `6` | `expr:6` | `expr:12` | 0 |
| 89 | `test/number_theory/357.json` | `21` | `expr:21` | `expr:3` | 1 |
| 130 | `test/number_theory/753.json` | `13` | `expr:13` | `expr:4` | 0 |

## Interpretation

This run shows a positive within-run CQG signal: final accuracy is higher than the same-run initial majority. The mechanism is not yet cleanly attributable to the appeal gate, because most sampled recoveries had no valid appeal. The observed gain currently looks more like the effect of hiding support counts and forcing blind re-solve on divergent cases.

The result also has an important absolute-performance caveat. This CQG run's initial majority is 320/500, while the separately run basic MAD direct baseline was 347/500 and MAD-MM `naive` was 375/500. Those runs are not strictly comparable because prompts, temperatures, rounds, and aggregation differ, but CQG's positive delta does not yet make it a stronger absolute system than the best local baseline.

## Execution Notes

The run used `--disable-tqdm` and `nohup` to avoid foreground SSH/stdout failures observed in earlier full-run attempts.
