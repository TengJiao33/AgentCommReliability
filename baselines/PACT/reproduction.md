# PACT Reproduction Note

## Short Answer

PACT now runs end to end on A800_2. A 5-sample Qwen2.5-7B setup smoke completed, followed by a 50-sample Qwen2.5-14B HotpotQA quick-demo-scale run. The 50-sample run scored `17/50` exact match with average F1 `0.508`, and all required action-state fields appeared in all 200 agent turns.

## Scope

- method: PACT, Protocolized Action-state Communication and Transmission
- paper: https://arxiv.org/abs/2606.05304
- repo: https://github.com/iNLP-Lab/PACT
- commit: `91acf820f8a69fc7c181120b3120444a98823230`
- local path: `baselines/PACT/upstream`
- project patch: `baselines/PACT/patches/a8002-local-reproduction-controls.patch`
- target setting: two-agent split-evidence HotpotQA
- evidence level: Level 3 short-subset run with concrete metrics and traces

## Environment

- machine: A800_2
- env path: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- model paths:
  - `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
  - `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- paper model: `Qwen/Qwen3-14B`
- data: `data/hotpot_dev_distractor_v1.json`

## Commands

Local syntax check:

```bash
cd baselines/PACT/upstream
python -m py_compile run.py methods/pact.py data.py models.py prompts.py utils.py
```

5-sample A800_2 smoke:

```bash
bash scripts/run_pact_hotpot_smoke_a8002.sh
```

50-sample Qwen2.5-14B run:

```bash
PACT_MODEL=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
PACT_MAX_SAMPLES=50 \
PACT_TIMEOUT=60m \
PACT_RUN_ID=pact-qwen25-14b-hotpot50-20260614_1100 \
PACT_OUT_NAME=pact_qwen25_14b_hotpot50.jsonl \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_pact_hotpot_smoke_a8002.sh
```

Neighboring-slice controls can use `PACT_START_INDEX` while preserving the
same deterministic paragraph shuffle for earlier samples:

```bash
PACT_MODEL=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
PACT_START_INDEX=50 \
PACT_MAX_SAMPLES=50 \
PACT_TIMEOUT=60m \
PACT_RUN_ID=pact-qwen25-14b-hotpot50-offset50-<stamp> \
PACT_OUT_NAME=pact_qwen25_14b_hotpot50_offset50.jsonl \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_pact_hotpot_smoke_a8002.sh
```

## Outputs

- 5-sample local record: `experiments/_archive/20260616-pruned/20260614-1055-a8002-pact-qwen25-7b-hotpot5/`
- 50-sample local record: `experiments/_archive/20260616-pruned/20260614-1100-a8002-pact-qwen25-14b-hotpot50/`
- report: `reports/_archive/20260616-pruned/20260614-pact-hotpot-smoke.md`
- trace: upstream JSONL includes per-turn agent prompts, input token IDs/tokens, raw outputs, and token counts

## What Happened

| Method | Model | Task | Seed | Samples | EM | F1 | Avg comm tokens | Avg total tokens | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| PACT | Qwen2.5-7B-Instruct | HotpotQA split-evidence | 42 | 5 | 0.20 | 0.344 | 294.6 | 4129.0 | complete |
| PACT | Qwen2.5-14B-Instruct | HotpotQA split-evidence | 42 | 50 | 0.34 | 0.508 | 339.3 | 4746.8 | complete |
| PACT + final answer contract | Qwen2.5-14B-Instruct | HotpotQA split-evidence | 42 | 50 | 0.68 | 0.792 | 321.9 | 4811.2 | complete |
| PACT offset50 | Qwen2.5-14B-Instruct | HotpotQA split-evidence | 42 | 50 | 0.52 | 0.647 | 327.3 | 4306.6 | complete |
| PACT offset50 + final answer contract | Qwen2.5-14B-Instruct | HotpotQA split-evidence | 42 | 50 | 0.56 | 0.743 | 324.0 | 4410.2 | complete |

## Deviations From Upstream

- Runs use Qwen2.5-7B/14B because Qwen3-14B was not found on the shared model mount.
- Runs use `generate_bs=1` and `max_new_tokens=1024` to reduce first-run memory risk.
- The 50-sample run matches the upstream quick-demo sample count but not the exact model.
- The project runner adds `PACT_START_INDEX` for neighboring-slice checks. The
  loader still advances the seeded context splitter through skipped rows, so
  sample `50` keeps the same split it would have had in a full sequential run.
- The parent repository records PACT local runner and prompt controls as
  `baselines/PACT/patches/a8002-local-reproduction-controls.patch`; the submodule
  pointer remains on the public upstream commit.

## Failures And Fixes

| Issue | Evidence | Fix | Method Behavior Changed? |
| --- | --- | --- | --- |
| Official CMU HotpotQA download hung on A800_2 and created a 0-byte file. | remote `wget` process stayed active while file size remained 0 | stopped the stalled download, downloaded the same file locally from Hugging Face, validated 7,405 JSON items, and copied it to A800_2 | no |
| A800_2 could not connect to Hugging Face directly. | remote `wget` to Hugging Face timed out during TCP connection | local download plus `scp` transfer | no |

## Diagnostics

- 50-sample format compliance:
  - `Action Required`: 200/200 turns.
  - `Environment State`: 200/200 turns.
  - `Action Result`: 200/200 turns.
  - `Final Answer`: 50/50 final turns.
  - `<think>` spans: 0/200 turns.
- Wrong-EM answer-surface signals:
  - 7 yes/no wrong-EM cases began with the correct yes/no answer but added a sentence.
  - 8 non-yes/no wrong-EM cases began with the normalized gold answer but added extra words.
  - These are diagnostic flags, not alternate official scores.
- Field-level evidence audit:
  - 23/33 wrong-EM cases have an output-field gold or yes/no polarity signal.
  - 8/33 wrong-EM cases have strict gold signal only in environment fields.
  - 1/33 wrong-EM cases has no strict gold field signal.
- Extraction-only audit:
  - a fixed final-answer-only extraction policy reaches 32/50 without changing model outputs;
  - final-event candidate upper bound is 39/50;
  - all-public-state candidate upper bound is 41/50.
- Stable-wrong after extraction:
  - 18 cases remain wrong under the fixed extraction policy;
  - 7 already have a matching candidate in the final action-state event;
  - 2 have a matching candidate only in earlier/wider public state;
  - 1 is a yes/no polarity mismatch.
- Unrecovered case inspection:
  - samples 14, 24, 43, and 44 are mostly answer-contract or extractor-priority problems;
  - sample 13 is a semantic polarity/predicate problem;
  - sample 21 mixes entity aliasing with evidence-use conflict.
- Question-aware extraction probe:
  - a question-aware deterministic extractor reaches diagnostic 38/50 without changing model outputs;
  - it adds 6 rescues over the fixed final-answer-only extraction policy and introduces 0 regressions;
  - sample 21 remains a parser-overcredit sentinel because its public state has an evidence-use conflict.
- Question-aware stable-wrong audit:
  - 12 cases remain wrong;
  - 7 have a matching candidate in the final action-state event;
  - 2 have a matching candidate only in earlier/wider public state;
  - 2 have strict environment signal but no current extracted candidate;
  - 1 is a semantic polarity or predicate failure.
- Field-selection case inspection:
  - the 9 matching-candidate cases split into final field/anchor conflicts (`3`), answer-contract or extractor-priority cases (`4`), and earlier-state lost or overwritten cases (`2`);
  - this points to public-state arbitration and answer contract before any larger HotpotQA run.
- Public-state arbitration probe:
  - naive final-event arbitration stays at diagnostic `38/50` because it adds 6 rescues but also 6 regressions against question-aware extraction;
  - guarded final-event arbitration reaches diagnostic `44/50`, adding 6 rescues and 0 regressions against question-aware extraction;
  - on the 9 field-selection focus cases, the guarded probe recovers 3/3 final field conflicts and 3/4 answer-contract cases, but 0/2 earlier-state lost cases.
- Final-answer-contract GPU run:
  - a real Qwen2.5-14B PACT run with `PACT_FINAL_ANSWER_CONTRACT=1` reaches `34/50` strict EM and average F1 `0.792`;
  - against the original PACT50 run, transitions are 20 wrong-to-right, 3 right-to-wrong, 14 stable-right, and 13 stable-wrong;
  - final-answer text shortens from `9.92` to `2.08` words on average, while average communication tokens decrease from `339.3` to `321.9`;
  - this confirms answer contract as a real model-behavior confound, not just a parser artifact, but also shows regressions and remaining state/anchor failures.
- Offset50 neighboring-slice paired run:
  - baseline reaches `26/50` strict EM and average F1 `0.6469`;
  - final-answer contract reaches `28/50` strict EM and average F1 `0.7427`;
  - transitions are 6 wrong-to-right, 4 right-to-wrong, 22 stable-right, and 18 stable-wrong;
  - the large first-50 EM jump does not repeat, but answer-surface effects remain visible through F1 and exact-match rescues.

## Caveats

- The 50-sample run is a useful setup and trace diagnostic, not a paper-scale reproduction.
- Since Qwen2.5-14B is not Qwen3-14B, do not compare the score directly to the paper.
- The model did not emit `<think>` spans, so this run did not exercise private-reasoning stripping.

## Loose Threads

- Use `experiments/_archive/20260616-pruned/20260614-1536-a8002-pact-qwen25-14b-hotpot50-final-contract/` before scaling; answer-contract and public-state-selection confounds are still too large to interpret EM as pure reasoning failure.
- Use `experiments/_archive/20260616-pruned/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/` as the neighboring-slice check before making any broad claim about the final-answer contract.
- If closer reproduction matters, locate Qwen3-14B or run a larger Qwen2.5-14B slice.
