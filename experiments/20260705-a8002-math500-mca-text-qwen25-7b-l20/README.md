# MCA-T MATH500 smoke

## Purpose

Run the first remote integration smoke for `scripts/run_mca_text.py`.

## Design

- Task: `math500/test`, first 20 rows.
- Unit: one MATH-500 problem.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- Method: MCA-T, answer-free text cue extraction and anonymous cue-only re-solve.
- Agents: 3 independent initial solvers.
- Reviewers: 3 cue resolvers.
- Pool-state scope: `all`.
- Primary contrast: same-run initial majority accuracy vs MCA-T final accuracy.
- Main diagnostic readouts: cue coverage, answer-leak rejection, generic cue rejection, cue uptake self-report, recovery/harm transitions, final parse/tie rate.

## Claim Gate

This is an integration smoke only. It can show whether the remote runner, XML parsing, cue filtering, and summary writing work. It is not a method-quality claim.

Success signal: job completes, summary files are written, cue/filter/resolve fields are populated, and parse/tie rates are interpretable.

Failure signal: crash, output collision, bad XML compliance, no kept cues, high parser failure, or missing summary artifacts.

Invalidation conditions: wrong GPU binding, evaluator/import failure, output directory collision, timeout/crash, or vLLM environment failure.

## Machine

- Host: `A800_2`.
- Remote work dir: `/data/xuhaoming/yfy/research_workspace`.
- Python/env: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`.
- GPU: `7`.

## Launch

See `run_remote.sh`.

## Status

`COMPLETED`.

## Result

- Remote PID: `2630939` for launcher, child Python `2630953`.
- Wall time: 163.7 seconds.
- Rows: 20.
- Initial majority accuracy: 14/20 = 0.7000.
- MCA-T final accuracy: 11/20 = 0.5500.
- Transitions: `MaC_to_C=10`, `MaC_to_W=4`, `MaW_to_C=1`, `MaW_to_W=5`.
- Cue atoms: 120 generated, 82 kept after filtering.
- Cue coverage: 20/20.
- Filter rejections: `candidate_answer_leak=13`, `duplicate=10`, `generic=19`.
- Final parse fail: 0/20.
- Final majority ties: 1/20.

## Diagnosis

The remote integration path works: script import, vLLM loading, cue extraction, cue filtering, cue-only re-solving, records writing, and summary writing all completed.

This smoke does not support MCA-T as a quality improvement under the current prompt/filter setting. It recovered 1 initially wrong-majority case but harmed 4 initially correct-majority cases. The main actionable signal is that cue-only re-solving is too willing to change correct initial majorities.

## Expected Outputs

- `math500-qwen25-7b-instruct-mca-text-all/records.jsonl`
- `math500-qwen25-7b-instruct-mca-text-all/summary.json`
- `math500-qwen25-7b-instruct-mca-text-all/summary.md`
- `run_remote.nohup.log`

## Caveats

MCA-T explicitly exposes text cues to the resolver, so a positive signal would only support answer-free cue communication as a diagnostic mechanism. It would not yet support the lower-level soft-prefix/KV/activation versions.
