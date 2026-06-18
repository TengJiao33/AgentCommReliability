# PACT Qwen2.5-14B HotpotQA50 Final-Answer-Contract Run

## What We Tried

Ran PACT on A800_2 with the same Qwen2.5-14B HotpotQA50 setup as the prior
smoke, but enabled an env-gated final-turn prompt control:

```text
PACT_FINAL_ANSWER_CONTRACT=1
```

The communication protocol stayed PACT action-state: `Action Required`,
`Environment State`, `Action Result`, and final `Final Answer`. The change only
adds a stricter final answer contract asking for the minimal answer span.

This is a GPU model run, not a postprocessing-only audit.

## Machine

- Host: `A800_2`
- GPU: `7`
- Free memory before launch: about `81149 MiB`
- Work dir: `/data/xuhaoming/yfy/research_workspace/baselines/PACT`
- Timeout: `60m`

## Code

- Baseline repo: `https://github.com/iNLP-Lab/PACT`
- Upstream commit: `91acf820f8a69fc7c181120b3120444a98823230`
- Local modifications:
  - `baselines/PACT/upstream/prompts.py`: env-gated final answer contract.
  - `scripts/run_pact_hotpot_smoke_a8002.sh`: logs `PACT_FINAL_ANSWER_CONTRACT`.

## Environment

- Python: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Backend: vLLM, tensor parallel size `1`

## Data / Task

- Dataset: HotpotQA dev-distractor
- Data path: `data/hotpot_dev_distractor_v1.json`
- Size: first `50` samples under seed `42`
- Agents/turns: two agents, `4` turns

## Command

```bash
cd /data/xuhaoming/yfy/research_workspace
PACT_MODEL=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
PACT_MAX_SAMPLES=50 \
PACT_TIMEOUT=60m \
PACT_GPU_ID=7 \
PACT_FINAL_ANSWER_CONTRACT=1 \
PACT_RUN_ID=pact-qwen25-14b-hotpot50-final-contract-20260614_1536 \
PACT_OUT_NAME=pact_qwen25_14b_hotpot50_final_contract.jsonl \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_pact_hotpot_smoke_a8002.sh
```

## Outputs

| File | Contents |
| --- | --- |
| `pact_qwen25_14b_hotpot50_final_contract.jsonl` | Raw per-sample PACT outputs from the GPU run. |
| `run.log` | Remote run log with vLLM load and per-sample prints. |
| `outer.log` | Remote wrapper stdout/stderr including `RC=0`. |
| `comm_trace_pact_final_contract_v11.jsonl` | Unified trace schema v1.1 extraction. |
| `analysis_summary.json` | Baseline-vs-contract comparison. |
| `changed_cases.jsonl` | One row per sample with transition and token deltas. |
| `question_aware_summary.json` | Question-aware post-run audit over this trace. |
| `public_state_arbitration_summary.json` | Public-state arbitration audit over this trace. |

## Result

The run completed with `RC=0`.

| Metric | Original PACT50 | Final-answer-contract PACT50 |
| --- | ---: | ---: |
| Exact match | `17/50` | `34/50` |
| Avg F1 | `0.508` | `0.792` |
| Avg final-answer words | `9.92` | `2.08` |
| Avg communication tokens | `339.3` | `321.9` |
| Avg total tokens | `4746.8` | `4811.2` |

Compared with the original PACT50 run:

| Transition | Count |
| --- | ---: |
| stable right | `14` |
| wrong to right | `20` |
| right to wrong | `3` |
| stable wrong | `13` |

The three right-to-wrong cases are samples `4`, `35`, and `49`.

On the nine field-selection focus cases from the prior inspection:

| Transition | Count |
| --- | ---: |
| wrong to right | `4` |
| stable wrong | `5` |

## Post-Run Diagnostics

The question-aware postprocessing audit over the new trace reaches diagnostic
`37/50`, adding `3` rescues with `0` regressions over the run's official
extraction.

The guarded public-state arbitration audit over the new trace reaches
diagnostic `39/50`, but now has `3` rescues and `1` regression relative to the
question-aware policy. This means the earlier offline `44/50` arbitration
ceiling does not directly transfer to the prompted model behavior.

## Things Noticed

This is the first strong GPU-backed signal that the final answer contract is a
real confound in the PACT reproduction: strict EM doubles from `17/50` to
`34/50` without changing the PACT communication topology.

It is not a clean win. The prompt control also changes model behavior, not only
surface form. Three previously correct samples become wrong, and several
field-selection cases remain unresolved:

- sample `1`: answer becomes `Chief of Protocol of the United States`, still
  not exact `chief of protocol`;
- sample `19`: final output still drops the `DSC` suffix;
- sample `25`: final output still uses `Lee Hazlewood`, not full
  `Barton Lee Hazlewood`;
- sample `30`: final output keeps `March 14, 2000` instead of year-only
  `2000`;
- sample `31`: final output still coarsens `Fujioka, Gunma` to `Japan`.

## Caveats

- This is still a 50-sample smoke, not benchmark evidence.
- The comparison uses the prior baseline run with the same model, seed, and
  first 50 samples; it is not a same-process paired rerun.
- Qwen2.5-14B is not the paper's Qwen3-14B.
- The prompt control was motivated by prior postprocessing/case inspection, so
  it should be tested on a neighboring slice before making a method claim.
