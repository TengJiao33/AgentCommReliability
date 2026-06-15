# 20260615-1010-a8002-peer-slot-control-math12

## What We Tried

Ran a deterministic slot-control peer-exposure pressure check over all available
MATH mixed-correctness candidates from the saved MAD-MM MATH50 trace.

The point was not a new method or a benchmark claim. The run separates peer
surface slots more explicitly than the earlier auto-evidence runs:

- final-answer slot: `correct_answer_only`, `wrong_answer_only`;
- full rationale with explicit final-answer slot blanked:
  `correct_redacted_rationale`, `wrong_redacted_rationale`;
- numeric-token-masked rationale:
  `correct_number_masked_rationale`, `wrong_number_masked_rationale`;
- equation / number-bearing surface:
  `correct_equation_surface`, `wrong_equation_surface`;
- full-rationale reference: `correct_rationale`, `wrong_rationale`.

## Machine

- Host: A800_2
- GPU: `3`
- Free memory before launch: about `81149 MiB`
- vLLM port: `8028`
- vLLM log: `/data/xuhaoming/yfy/research_workspace/logs/peer-slot-vllm-20260615_1010.log`

The temporary vLLM service was stopped after the run, and GPU `3` returned to
idle.

## Code

- Runner: `scripts/run_peer_exposure_probe.py`
- Schema: `acr.peer_exposure.v0.5`
- Local change: added deterministic slot-control peer-surface conditions.
- Upstream source: saved MAD-MM MATH50 probe artifacts.

## Data / Task

- Dataset/task: MATH via MAD-MM `mad_naive` trace.
- Source trace:
  `/data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-7b-math50-probe.comm_trace.jsonl`
- Debate log:
  `/data/xuhaoming/yfy/research_workspace/results/mad-mm-benchmark-probe/math_probe50/qwen2.5-7b/math/mad_3agents_2rounds_seed41_debate_log.json`
- Selection: all `12` available mixed-correctness candidates:
  `1`, `9`, `10`, `15`, `22`, `24`, `26`, `33`, `38`, `41`, `42`, `47`.

## Command

```bash
python scripts/run_peer_exposure_probe.py --run-id 20260615-1010-a8002-peer-slot-control-math12 --out-dir /data/xuhaoming/yfy/research_workspace/experiments/20260615-1010-a8002-peer-slot-control-math12 --base-url http://127.0.0.1:8028/v1 --model qwen2.5-7b-peer-slot --source-format madmm_math --madmm-trace-jsonl /data/xuhaoming/yfy/research_workspace/results/unified-traces/madmm-qwen25-7b-math50-probe.comm_trace.jsonl --madmm-debate-log-json /data/xuhaoming/yfy/research_workspace/results/mad-mm-benchmark-probe/math_probe50/qwen2.5-7b/math/mad_3agents_2rounds_seed41_debate_log.json --madmm-method mad_naive --selection-mode first --max-cases 0 --conditions correct_answer_only wrong_answer_only correct_rationale wrong_rationale correct_redacted_rationale wrong_redacted_rationale correct_number_masked_rationale wrong_number_masked_rationale correct_equation_surface wrong_equation_surface --peer-warning natural --machine A800_2 --gpu-ids 3 --server-log /data/xuhaoming/yfy/research_workspace/logs/peer-slot-vllm-20260615_1010.log --include-prompts
```

## Outputs

- `source_cases.jsonl`
- `peer_exposure_records.jsonl`
- `summary.json`
- `manifest.json`
- `slot_control_audit.json`
- `slot_transition_cards.jsonl`

## Result

Records: `132`.

| Condition | Correct | Right->Wrong | Wrong->Right | Stable Right | Stable Wrong | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `no_peer` | 8/12 | 0 | 0 | 0 | 0 | 0 |
| `correct_answer_only` | 10/12 | 0 | 1 | 8 | 0 | 3 |
| `correct_rationale` | 10/12 | 0 | 1 | 8 | 0 | 3 |
| `correct_redacted_rationale` | 9/12 | 0 | 0 | 8 | 1 | 3 |
| `correct_equation_surface` | 8/12 | 0 | 0 | 8 | 1 | 3 |
| `correct_number_masked_rationale` | 7/12 | 1 | 0 | 7 | 1 | 3 |
| `wrong_answer_only` | 7/12 | 1 | 0 | 7 | 1 | 3 |
| `wrong_redacted_rationale` | 7/12 | 1 | 0 | 7 | 1 | 3 |
| `wrong_equation_surface` | 7/12 | 1 | 0 | 7 | 1 | 3 |
| `wrong_rationale` | 8/12 | 0 | 0 | 8 | 1 | 3 |
| `wrong_number_masked_rationale` | 8/12 | 0 | 0 | 8 | 1 | 3 |

## Notes

- Case `47` remains the sharpest harmful slot case:
  `wrong_answer_only` moved `28800 -> 14400`, while
  `wrong_redacted_rationale` and `wrong_equation_surface` moved
  `28800 -> 1152`. The wrong number-bearing role surface, not only the final
  answer slot, can pull the target.
- Case `26` shows a different boundary: `correct_number_masked_rationale`
  moved `156 -> 75` after numeric slots were removed, so number masking itself
  can create a misleading prompt surface.
- Case `9` was rescued by `correct_answer_only` and `correct_rationale`, but
  not by correct redacted, masked, or equation-only surfaces. In that case the
  final answer anchor appears to carry the rescue more than the redacted
  relation surface.

## Caveats

- This uses the complete available MATH50 mixed-correctness pool, but that pool
  has only `12` candidates. It is not a larger upstream disagreement pool.
- Slot-control surfaces are deterministic transforms over saved peer rationales;
  they are diagnostic and sometimes unnatural.
- Three baseline cases were unparseable, so many per-condition rows are
  `unknown` rather than clean transitions.
- Explicit final-answer slot blanking only blanks explicit final-answer lines;
  it does not semantically remove every occurrence of the answer value, because
  values such as `2` can also be legitimate intermediate or relation constants.
