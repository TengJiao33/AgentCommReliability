# M2CL Reproduction Note

## Short Answer

M2CL was added and syntax-checked locally, but the inspected public checkout is not currently a clean runnable reproduction target because the main generation function is stubbed and required data/checkpoint/API files are absent.

## Scope

- method: Context Learning for Multi-Agent Discussion
- paper: https://arxiv.org/abs/2602.02350
- OpenReview: https://openreview.net/forum?id=EUu8TILWpR
- repo: https://github.com/HansenHua/M2CL-ICLR26
- commit: `ada64a9089731f4d2e2cfd2048329cf50f65031f`
- local path: `baselines/M2CL/upstream`
- target setting: code contact only; no GPU reproduction launched

## Environment

- machine: local Windows workspace
- env path: not created
- Python: project-local default Python used for syntax check
- key packages: not installed for execution
- model paths: default upstream paths only, not present locally

## Commands

```bash
git submodule add https://github.com/HansenHua/M2CL-ICLR26.git baselines/M2CL/upstream
git submodule status
python -m py_compile baselines/M2CL/upstream/main.py baselines/M2CL/upstream/method/M2CL.py
```

Additional local checks:

```powershell
Test-Path baselines\M2CL\upstream\api_key.txt
Test-Path baselines\M2CL\upstream\dataset
Test-Path baselines\M2CL\upstream\model
Test-Path baselines\M2CL\upstream\t5-small
```

All four path checks returned `False`.

## Outputs

- log: none
- result: syntax check passed
- trace: none
- summary: public code path inspected; runnable reproduction deferred

## What Happened

| Method | Model | Task | Seed | Samples | Metric | Tokens | Status |
| --- | --- | --- | --- | ---: | ---: | ---: | --- |
| M2CL code contact | none | none | n/a | 0 | n/a | n/a | syntax check passed; execution blocked before meaningful reproduction |

## Deviations From Upstream

- No code changes were made inside the upstream submodule.
- No attempt was made to remove the `gen_response` stub, provide dummy datasets, or bypass API/proxy assumptions.

## Failures And Fixes

| Issue | Evidence | Fix | Method Behavior Changed? |
| --- | --- | --- | --- |
| Missing API key file | `main.py::gen_api_key` reads `api_key.txt`; local path check returned `False` | none | no |
| Hardcoded proxy | `main.py` sets proxy to `http://127.0.0.1:21882` | none | no |
| Missing dataset | `main.py` loads `dataset/<dataset>/question_answer.npy`; local `dataset` folder absent | none | no |
| Missing model/generator checkpoints | default `./model/llama-7b` and `./t5-small` absent; README checkpoint release is TODO | none | no |
| Generation is stubbed | `method/M2CL.py::gen_response` immediately returns `"success generate"` | none | no |
| Missing declared dependency | `method/M2CL.py` imports `trl`, but `requirements.txt` does not include it | none | no |
| Possible shared-list buffer aliasing | `context_buffer = [[]] * len(self.agent_list)` and similar buffers | none | no |

## Caveats

- This is a local code-contact note, not an author-style reproduction.
- The upstream repository may change; current note is pinned to commit `ada64a9089731f4d2e2cfd2048329cf50f65031f`.
- The blocked status is about the inspected public checkout, not a claim about the paper's method.

## Loose Threads

- Add trace vocabulary for generated context state before copying any M2CL mechanism.
- Decide whether to build a tiny synthetic context-alignment harness rather than patching this code directly.
- Revisit M2CL execution if checkpoints and concrete dataset artifacts are released.
