# PACT Source Note

## Upstream

- paper: https://arxiv.org/abs/2606.05304
- repo: https://github.com/iNLP-Lab/PACT
- commit inspected: `91acf820f8a69fc7c181120b3120444a98823230`
- license: no license file observed in the upstream repository
- local path: `baselines/PACT/upstream`
- project patch: `baselines/PACT/patches/a8002-local-reproduction-controls.patch`

## Why This Baseline

PACT directly targets the project's current question: what should an agent expose to other agents when full reasoning can contaminate, distract, or waste context? It is a useful counterpoint to MAD-MM, DAR, and MOC because the main intervention is the public communication surface itself: an action-state record rather than unrestricted chain-of-thought or full retained reasoning.

## Smallest Runnable Path

Upstream demo:

```bash
bash scripts/download_hotpotqa.sh
bash scripts/run_demo.sh
```

Direct upstream command:

```bash
python run.py \
  --model_name Qwen/Qwen3-14B \
  --data_path data/hotpot_dev_distractor_v1.json \
  --use_vllm --tensor_parallel_size 1 \
  --seed 42 --generate_bs 64 --max_new_tokens 4096 --max_turns 4 \
  --max_samples 50 \
  --output_path results/pact_qwen3_14b_hotpot.jsonl
```

Project A800_2 smoke target:

```bash
bash scripts/run_pact_hotpot_smoke_a8002.sh
```

## Installation Notes

- environment target: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063`
- remote source target: `/data/xuhaoming/yfy/research_workspace/baselines/PACT`
- upstream dependencies: `torch`, `transformers`, `accelerate`, `vllm`, `tqdm`, `numpy`
- data download: `scripts/download_hotpotqa.sh` fetches HotpotQA dev-distractor to `data/hotpot_dev_distractor_v1.json`
- paper model: `Qwen/Qwen3-14B`
- available local model for first smoke: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`

## Code Map

| Component | File / Function | Notes |
| --- | --- | --- |
| entrypoint | `run.py` | CLI, data load, batch loop, summary metrics, JSONL output |
| dataset loader | `data.py::load_hotpotqa` | splits each HotpotQA item into two 5-paragraph contexts, each with 1 gold + 4 distractors; project copy supports `start_index` for neighboring slices |
| method loop | `methods/pact.py::PACTMethod.run_batch` | alternates Agent A and B for `max_turns`; final turn extracts answer |
| communication surface | `methods/pact.py::strip_think_tags` call | raw output is counted, but only think-stripped action-state text enters shared history |
| prompts | `prompts.py::build_prompt_pact` | requires `Action Required`, `Environment State`, `Action Result`; final turn adds `Final Answer` |
| model wrapper | `models.py::ModelWrapper` | supports HF and vLLM paths; vLLM path loads local model directly |
| evaluation | `utils.py`, `run.py::evaluate` | exact match, token F1, communication tokens, total tokens |

## Known Caveats

- The repository is a focused demo for split-evidence HotpotQA, not a broad benchmark harness.
- Upstream README says the Table 1 reproduction row is Qwen3-14B / HotpotQA; the shared A800_2 model mount currently has Qwen2.5-7B/14B but not Qwen3-14B.
- The upstream quick demo defaults to `generate_bs=64`; the project smoke intentionally lowers this to `1` to reduce first-run memory risk.
- PACT's central metric depends on a distinction between raw generated output tokens and the smaller think-stripped public history. We should inspect per-turn traces, not just final EM/F1.
- The project patch adds a `--start_index` CLI flag and preserves original
  HotpotQA `sample_index` values in JSONL outputs so offset runs can be compared
  without renumbering samples.

## Loose Threads

- Compare PACT's action-state surface against DAR's `answer_only` and `full` retained surfaces on a shared conceptual axis: what information is forwarded, what is hidden, and when correctness changes.
- Add a postprocessing-only final-answer audit for the Qwen2.5-14B HotpotQA50 run.
- If closer reproduction matters, locate Qwen3-14B or scale Qwen2.5-14B beyond the 50-sample quick-demo run.
