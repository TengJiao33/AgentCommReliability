# Consensus Quarantine Gate MATH500 smoke

## Purpose

Run a small integration smoke for `scripts/run_consensus_quarantine.py` before any claim-bearing benchmark run.

## Design

- Machine: A800_2.
- Remote work dir: `/data/xuhaoming/yfy/research_workspace`.
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`.
- Dataset: `math500/test/canonical.jsonl`.
- Limit: first 20 rows.
- GPU: 7.
- Primary baseline: same-run `initial_majority_accuracy` inside CQG summary.
- Sanity baseline: `--quarantine-mode never`, which disables quarantine and only returns the initial majority path.
- Method smoke: `--quarantine-mode divergent`, which quarantines non-unanimous initial majorities.

## Readout

This run can show whether the runner executes end to end and writes metrics. It is not a benchmark-level method claim.

Main diagnostic metrics:

- `initial_majority_accuracy`
- `final_accuracy`
- `quarantine_rate`
- `wrong_majority_recovery_rate`
- `correct_majority_preservation_rate`
- `answer_change_rate`
- `final_parse_fail_rate`

## Launch Command

See `run_remote.sh`.

## Results

Status: diagnostic smoke only. This run validates code paths and surfaces prompt/parser issues; it is not claim-bearing evidence for CQG quality.

### Baseline Definition

The primary baseline is the same-run `initial_majority_accuracy` written by `run_consensus_quarantine.py`. It represents three independent initial agent answers aggregated by majority vote before any quarantine/review intervention.

The sanity baseline is `--quarantine-mode never`, which disables quarantine and should match the initial majority path except for independent sampling effects if run separately.

### Smoke Chronology

| Run | Mode | Rows | Initial majority | Final | Quarantine | Answer changed | MaW->C | MaC->W | Parse fail | Note |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `20260705-a8002-math500-cqg-smoke-qwen25-7b-l20` | `never` | 20 | 16/20 | 16/20 | 0/20 | 0/20 | 0 | 0 | 0 | sanity baseline |
| `20260705-a8002-math500-cqg-smoke-qwen25-7b-l20` | `divergent` | 20 | 16/20 | 16/20 | 3/20 | 0/20 | 0 | 0 | 0 | first CQG smoke; appeal prompt echoed placeholder |
| `20260705-a8002-math500-cqg-smoke-qwen25-7b-l20-v2` | `divergent` | 20 | 16/20 | 16/20 | 3/20 | 1/20 | 0 | 0 | 0 | fixed appeal sentinel; reviewer still echoed answer placeholder in one case |
| `20260705-a8002-math500-cqg-smoke-qwen25-7b-l20-v3` | `divergent` | 20 | 14/20 | 14/20 | 8/20 | 4/20 | 1 | 1 | 0 | fixed XML placeholders; integration path is clean enough for further prompt work |

### Concrete Triage Notes

- v3 `MaW->C`: `test/algebra/2036.json`, gold `3\sqrt{13}`. Initial majority was `5*sqrt(5)`, and blind reviewers produced `3\sqrt{13}` even though no valid appeal was generated. This supports that the blind re-solve path can recover an error, but it does not yet validate the appeal gate.
- v3 `MaC->W`: `test/algebra/1349.json`, gold `Evelyn`. Initial majority was correct, no valid appeal was generated, but blind reviewers changed the final answer to `Briana`. This is a concrete harm case and shows the gate currently over-triggers when no admissible appeal exists.
- The most important plumbing fixes from this smoke were: mixed-fraction evaluation must run before `latex2sympy2`, and XML placeholder strings such as `YOUR FINAL ANSWER ONLY` must be treated as parse failures rather than text answers.

### Local Artifacts

- `math500-qwen25-7b-instruct-cqg-never/summary.json`
- `math500-qwen25-7b-instruct-cqg-never/records.jsonl`
- `math500-qwen25-7b-instruct-cqg-divergent/summary.json`
- `math500-qwen25-7b-instruct-cqg-divergent/records.jsonl`
- sibling result directories:
  - `../20260705-a8002-math500-cqg-smoke-qwen25-7b-l20-v2/`
  - `../20260705-a8002-math500-cqg-smoke-qwen25-7b-l20-v3/`
