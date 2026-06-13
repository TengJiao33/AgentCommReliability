# RuleArena Source Note

## Upstream

- paper: RuleArena: A Benchmark for Rule-Guided Reasoning with LLMs in Real-World Scenarios
- arXiv: https://arxiv.org/abs/2412.08972
- repo: https://github.com/skyriver-2000/RuleArena
- commit: `3b9e2256294644beca66732babc5e1055855a576`
- license: MIT
- local path: `baselines/RuleArena/upstream`
- tracking mode: git submodule, so the benchmark source is portable across local machines.

## Why This Benchmark

RuleArena is not a replacement for original paper benchmarks. It is a pressure benchmark for mechanisms already observed in the reproduction work:

- memory filters can keep wrong but plausible messages;
- full communication can waste tokens;
- compressed or structured communication may drop necessary conditions;
- verifier or judge behavior matters when rules are long and conditional.

The benchmark stresses rule selection, condition tracking, arithmetic, and final-answer formatting across realistic domains. This should create more observable communication failures than saturated GSM8K-style runs while staying close to automatic scoring.

## Smallest Runnable Path

- model: no model for loader smoke; later `vllm:qwen2.5-7b` or official API models.
- dataset/task: `airline`, `nba`, `tax`; start with `airline`, complexity `0`.
- command:

```bash
python scripts/rulearena_loader_smoke.py --root baselines/RuleArena/upstream
```

- expected output: per-domain problem counts and sample metadata.
- expected resource: CPU only; no GPU and no model API calls.

## Installation Notes

- upstream dependencies are in `baselines/RuleArena/upstream/requirements.txt`.
- official scripts call OpenAI, Claude, Qwen DashScope, or Vertex Llama APIs.
- for project A800_2 runs, add or wrap an OpenAI-compatible vLLM backend instead of using local-machine API keys.
- upstream scripts do not expose a clear `--limit` argument; add a small-run wrapper before any model call.

## Code Map

| Component | File / Function | Notes |
| --- | --- | --- |
| airline prompts | `airline/auto_test.py` | Long rule prompt plus cost answer format. |
| airline data | `airline/synthesized_problems/comp_*.jsonl` | JSONL, synthetic passenger cases. |
| airline evaluator | `airline/compute_answer.py`; `airline/micro_evaluation.py` | Computes gold fee and rule-application metrics. |
| nba prompts | `nba/auto_test.py` | NBA transaction legality prompt. |
| nba data | `nba/annotated_problems/comp_*.json` | JSON, annotated legal/illegal operations. |
| nba evaluator | `nba/micro_evaluation.py` | Parses rule applications and final legality. |
| tax prompts | `tax/auto_test.py`; `tax/prompt.py` | IRS forms and fill-in calculations. |
| tax data | `tax/synthesized_problems/comp_*.json` | JSON, taxpayer cases. |
| tax evaluator | `tax/micro_evaluation.py` | Computes tax answer and form/rule metrics. |
| model calls | `*/auto_test.py` | Official API wrappers; needs vLLM adaptation for local A800_2 runs. |

## Known Caveats

- This is a benchmark pressure test, not an original-method reproduction by itself.
- Domain prompts are long, so pilot runs need strict sample limits.
- Upstream official API code should not be used directly for local Qwen unless an OpenAI-compatible endpoint wrapper is added.
- Submodule source is tracked, but generated logs and full run outputs should stay under `experiments/` or remote result paths.

## Next Check

- Run loader smoke locally.
- Add a small-run vLLM wrapper or patch with `--limit`.
- Run a 20-question `airline` pilot only after the wrapper records prompts, outputs, gold answers, and token costs.
