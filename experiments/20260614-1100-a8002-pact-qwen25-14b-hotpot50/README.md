# 20260614-1100-a8002-pact-qwen25-14b-hotpot50

## What We Tried

Ran the PACT split-evidence HotpotQA path on the upstream quick-demo scale, using local Qwen2.5-14B-Instruct as the closest available 14B model to the paper's Qwen3-14B setting.

## Scope

- Method: PACT
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Dataset: HotpotQA dev-distractor, first 50 shuffled-by-loader samples
- Seed: 42
- Samples: 50
- Comparison target, if any: upstream quick-demo scale, not paper-scale reproduction

## Resource Notes

- Machine: A800_2
- GPU IDs: 1
- Timeout: 60m
- Expected duration: under 20 minutes including model load
- Started by: Codex

## Code

- Upstream repo: https://github.com/iNLP-Lab/PACT
- Commit: `91acf820f8a69fc7c181120b3120444a98823230`
- Local changes: none on the remote source

## Environment

- Env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- Python: env Python 3.10
- vLLM: `dev` with missing `vllm._version` warning
- PyTorch: `2.4.0+cu121`
- Transformers: `4.46.2`
- NumPy: `1.26.4`
- tqdm: `4.67.0`

## Data

- Data path: `/data/xuhaoming/yfy/research_workspace/baselines/PACT/data/hotpot_dev_distractor_v1.json`
- Split: HotpotQA dev-distractor
- Size available: 7,405 items
- Sampling: upstream loader order after deterministic internal context shuffle, first 50 items

## Command

```bash
PACT_MODEL=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
PACT_MAX_SAMPLES=50 \
PACT_TIMEOUT=60m \
PACT_RUN_ID=pact-qwen25-14b-hotpot50-20260614_1100 \
PACT_OUT_NAME=pact_qwen25_14b_hotpot50.jsonl \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_pact_hotpot_smoke_a8002.sh
```

## Remote Artifacts

- Main log: `/data/xuhaoming/yfy/research_workspace/results/pact-qwen25-14b-hotpot50-20260614_1100/run.log`
- Result JSON: `/data/xuhaoming/yfy/research_workspace/results/pact-qwen25-14b-hotpot50-20260614_1100/pact_qwen25_14b_hotpot50.jsonl`
- Local copies: `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/`

## What Happened

- Status: completed, `RC=0`
- Exact match: `0.34` (`17/50`)
- Average F1: `0.508`
- Average communication tokens: `339.3`
- Average total tokens: `4746.8`
- Average output tokens per turn: `84.8`
- Evaluation time: `388.94s`
- Time per sample: `7.7788s`

## Diagnostics

- All 200 agent turns contained `Action Required`, `Environment State`, and `Action Result`.
- All 50 final turns contained `Final Answer`.
- No `<think>` spans were emitted, so this run mainly tests concise public action-state messaging, not private-thought stripping.
- Among non-EM predictions, 7 yes/no cases began with the correct `yes` or `no` but failed exact match because the model answered in a full sentence.
- Another 8 non-yes/no cases began with the normalized gold answer but added extra words.
- These are not alternate official scores; they indicate an answer-surface and extraction problem worth testing before interpreting EM as pure reasoning failure.

## Unified Trace v1.1

Extracted the local result JSONL into schema `acr.comm_trace.v1.1`:

```powershell
python scripts\extract_comm_trace_schema.py pact `
  --run-id 20260614-1100-a8002-pact-qwen25-14b-hotpot50-v11 `
  --result-jsonl experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\pact_qwen25_14b_hotpot50.jsonl `
  --method pact_action_state `
  --task-regime split_evidence_qa `
  --public-state-surface action_state `
  --communication-policy alternating_action_state `
  --out experiments\20260614-1100-a8002-pact-qwen25-14b-hotpot50\comm_trace_pact_v11.jsonl
```

Validation:

- rows: 50
- communication events: 200
- derived context events: 150
- each sample has 4 action-state communication events;
- each non-final turn creates one shared-history context event;
- all 200 turns have `Action Required`, `Environment State`, and `Action Result`;
- all 50 final turns have `Final Answer`;
- no `<think>` spans were present.
- HotpotQA gold answers are preserved as text in the trace.

## Final-Answer Surface Audit

Ran a postprocessing-only audit over `comm_trace_pact_v11.jsonl`:

- output: `experiments/20260614-1314-local-pact-final-answer-surface-audit/`
- official EM remains `17/50`;
- among 33 wrong-EM cases, 18 have a simple surface candidate:
  - 7 yes/no final answers begin with the correct `yes` or `no`;
  - 8 non-yes/no final answers begin with normalized gold;
  - 2 numeric final answers contain the normalized gold number;
  - 1 action-result field begins with normalized gold;
- 15 wrong-EM cases have no simple surface signal.

These are diagnostics, not alternate official scores.

## Evidence Field Audit

Ran a field-level audit over `comm_trace_pact_v11.jsonl`:

- output: `experiments/20260614-1326-local-pact-evidence-field-audit/`
- official EM remains `17/50`;
- among 33 wrong-EM cases:
  - 23 have an output-field gold or yes/no polarity signal;
  - 8 have strict gold signal only in environment fields;
  - 1 has yes/no final polarity mismatch or unclear;
  - 1 has no strict gold field signal.
- among 25 wrong non-yes/no cases:
  - final answer contains normalized gold: `15`;
  - action result contains normalized gold: `15`;
  - final environment state contains normalized gold: `19`;
  - any environment state contains normalized gold: `23`.

These are field diagnostics, not alternate official scores.

## Extraction-Only Audit

Ran a deterministic extraction-only audit over the corrected `comm_trace_pact_v11.jsonl`:

- output: `experiments/20260614-1345-local-pact-extraction-only-audit/`
- official EM remains `17/50`;
- fixed final-answer-only extraction policy reaches `32/50`;
- policy transitions:
  - stable right: `17`;
  - wrong to right: `15`;
  - stable wrong: `18`;
  - right to wrong: `0`;
- final-event candidate upper bound: `39/50`;
- all-public-state candidate upper bound: `41/50`.

These are postprocessing diagnostics, not replacement scores.

## Stable-Wrong After Extraction Audit

Ran a follow-up over the `18` cases that remain wrong under the fixed
final-answer extraction policy:

- output: `experiments/20260614-1402-local-pact-stable-wrong-after-extraction/`
- category counts:
  - final event has matching candidate but final-answer-only policy missed it: `7`;
  - matching candidate appears only in earlier/wider public state: `2`;
  - strict environment signal exists but simple candidate extraction missed it: `3`;
  - yes/no polarity mismatch: `1`;
  - wrong output signal not recovered by current extractor: `5`.

## Unrecovered Case Inspection

Manually inspected the five unrecovered-output cases and the one polarity case:

- output: `experiments/20260614-1418-local-pact-unrecovered-case-inspection/`
- manual surfaces:
  - answer-contract or extractor-priority problem: samples `14`, `24`, `43`, `44`;
  - semantic polarity/predicate problem: sample `13`;
  - mixed entity-alias and evidence-use conflict: sample `21`.

## Question-Aware Extraction Probe

Ran a question-aware deterministic extraction probe over the corrected trace:

- output: `experiments/20260614-1432-local-pact-question-aware-extraction/`
- official PACT extraction: `17/50`;
- fixed final-answer-only extraction: `32/50`;
- question-aware extraction: `38/50`;
- additional rescues over fixed extraction: `6`;
- regressions over fixed extraction: `0`.

This is diagnostic only. Sample `21` is surface-recovered by extracting `Sonic`
from `Sonic the Hedgehog`, but the manual inspection still marks it as a mixed
evidence-use conflict.

## Question-Aware Stable-Wrong Audit

Classified the `12` cases still wrong under question-aware extraction:

- output: `experiments/20260614-1450-local-pact-question-aware-stable-wrong/`
- category counts:
  - final event has matching candidate but question-aware policy missed it: `7`;
  - matching candidate appears only in earlier/wider public state: `2`;
  - strict environment signal exists but current candidate extractor misses it: `2`;
  - semantic polarity or predicate failure: `1`.
- `output_signal_not_recovered` is now `0`.

## Field-Selection Case Inspection

Manually inspected the `9` matching-candidate cases from the question-aware
stable-wrong audit:

- output: `experiments/20260614-1507-local-pact-field-selection-case-inspection/`
- mechanical buckets:
  - final event has matching candidate but question-aware policy missed it: `7`;
  - matching candidate appears only in earlier/wider public state: `2`.
- manual families:
  - final field or anchor selection conflict: samples `1`, `15`, `31`;
  - answer contract or extractor priority: samples `25`, `28`, `30`, `40`;
  - earlier state lost or overwritten: samples `19`, `23`.

This keeps the next PACT step focused on public-state arbitration and final
answer contract, not broad scaling.

## Public-State Arbitration Probe

Ran a CPU-only postprocessing probe over the saved trace:

- output: `experiments/20260614-1518-local-pact-public-state-arbitration-probe/`
- prior question-aware policy: `38/50`;
- naive final-event arbitration: `38/50`, with `6` rescues and `6`
  regressions versus question-aware policy;
- guarded final-event arbitration: `44/50`, with `6` rescues and `0`
  regressions versus question-aware policy.

On the `9` field-selection focus cases, guarded final-event arbitration
recovers:

- final field or anchor selection conflict: `3/3`;
- answer contract or extractor priority: `3/4`;
- earlier state lost or overwritten: `0/2`.

This is diagnostic only. It suggests that a guard between final public state
and final answer is a real contact point, while earlier-state loss remains a
separate problem.

## Final-Answer-Contract GPU Run

Ran a real Qwen2.5-14B PACT HotpotQA50 variant on A800_2 GPU 7:

- output: `experiments/20260614-1536-a8002-pact-qwen25-14b-hotpot50-final-contract/`
- env flag: `PACT_FINAL_ANSWER_CONTRACT=1`
- exact match: `34/50`;
- average F1: `0.792`;
- average final-answer words: `2.08`, down from original `9.92`.

Against the original PACT50 run:

- stable right: `14`;
- wrong to right: `20`;
- right to wrong: `3`;
- stable wrong: `13`.

This is the first GPU-backed version of the answer-contract signal. It confirms
that the confound affects actual model behavior, not just saved-output
postprocessing. It also shows the risk: samples `4`, `35`, and `49` regress,
and several full-name/granularity/early-state cases remain wrong.

## Caveats

- This is not an author-style reproduction: model is Qwen2.5-14B, not Qwen3-14B.
- It is a 50-sample quick-demo run, not the full 7,405-item dev set.
- The upstream prompt enforces action-state fields well, but the final answer field is still too verbose for strict HotpotQA EM in many cases.

## Loose Threads

- Use the final-answer-contract GPU run before any larger rerun; remaining failures mostly involve public-state arbitration, final answer contract, or earlier-state overwrite.
- If closer reproduction matters, locate Qwen3-14B or run Qwen2.5-14B on a larger slice.
- Use the unified PACT trace to compare public evidence fields against DAR answer-only/full retained surfaces.
