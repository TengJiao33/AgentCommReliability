# Context Learning for Multi-Agent Discussion

## Link

- paper: https://arxiv.org/abs/2602.02350
- OpenReview: https://openreview.net/forum?id=EUu8TILWpR
- code: https://github.com/HansenHua/M2CL-ICLR26
- local pdf: pending

## One-Sentence Claim

Multi-agent discussion fails partly because agents receive misaligned individual contexts, and learned context generators can dynamically shape each agent's per-round context to improve coherence, diversity, and consensus.

## Problem

MAD-style systems often focus on who talks to whom or which messages are retained. M2CL argues that the deeper failure can be discussion inconsistency: agents do not share coherent or appropriately differentiated contexts, so discussion may converge too early on majority noise or fail to reach a coherent solution.

## Method

M2CL learns a context generator for each agent. The generator dynamically produces context instructions per discussion round through information organization and refinement. The method also uses context initialization to assign diverse initial instructions.

For our project, the key shift is from:

```text
which peer messages are visible?
```

to:

```text
what context state should each agent inhabit this round?
```

## Communication Variables

| Variable | Value / Design | Notes |
| --- | --- | --- |
| agents | multiple LLM instances | exact count is task/config dependent |
| rounds | multi-round discussion | context can change by round |
| topology | discussion framework | not yet inspected in code |
| message content | agent answers plus generated context instructions | context instruction is a first-class object |
| memory/context | dynamically generated per-agent context | central mechanism |
| routing | generated/adaptive context, not only static routing | needs code inspection |
| confidence/evidence | not the main axis in abstract | may appear in implementation or tasks |
| judge/verifier | task-dependent final decision | not yet inspected |
| stopping rule | max rounds/config driven | code exposes `--max_rounds` |

## Baselines

Pending full paper read. Expected comparison space:

- vanilla MAD/discussion;
- context initialization without learned dynamic updates;
- learned context generator variants;
- task-specific multi-agent baselines for academic reasoning, embodied tasks, and mobile control.

## Datasets / Tasks

The paper reports evaluation on:

- academic reasoning;
- embodied tasks;
- mobile control.

The repository exposes a configurable `main.py`; exact datasets and paths require code inspection.

## Reported Results

| Setting | Metric | Reported Result | Compared To |
| --- | ---: | --- | --- |
| Paper abstract | task performance | reports 20%-50% improvement | existing MAD methods |
| Paper abstract | transfer/efficiency | reports favorable transferability and computational efficiency | learned context generator setting |

These are paper claims, not local reproduction results.

## Code And Reproducibility

- repo: https://github.com/HansenHua/M2CL-ICLR26
- commit inspected locally: `ada64a9089731f4d2e2cfd2048329cf50f65031f`
- local path: `baselines/M2CL/upstream`
- license: no license file visible in inspected checkout
- install difficulty: high for full reproduction; repository TODO mentions polishing code and checkpoint release status
- smallest runnable command: repository README shows `python main.py`
- current runnable status: syntax check passes, but meaningful execution is blocked by missing data/checkpoints/API assumptions and a stubbed generation function
- expected resource: GPU environment; full training likely expensive; code reading and inference-shape inspection is cheap

## Implementation Details Worth Inspecting

- prompt templates: `Agent.response` and the final leader/summarizer prompt in `method/M2CL.py`;
- message construction: generated role/context plus concatenated peer responses plus question;
- context generator: `role_generator.gen_role(context)` where `context` is `question + peer responses`;
- filtering or merging: contribution filtering and top-k combinations are exposed as CLI flags, but are not clearly active in the inspected path;
- judge or verifier path: `verify_answer` checks boxed answers; final answer uses a summarizer call;
- evaluation script: `main.py`;
- hidden defaults: `--generator_path`, `--top_k`, `--contribution_threshold`, `--alpha`, `--beta`, `--train_rounds`.

## Code-Contact Findings

- `method/M2CL.py::gen_response` immediately returns `"success generate"`, making later Llama/OpenAI generation branches unreachable.
- `main.py` requires `api_key.txt` and hardcodes `http://127.0.0.1:21882` proxy variables.
- `main.py` expects `dataset/<dataset>/question_answer.npy`; no dataset folder is present in the checkout.
- `requirements.txt` omits `trl` even though `method/M2CL.py` imports `PPOTrainer` and `PPOConfig`.
- Several buffers use list multiplication, e.g. `context_buffer = [[]] * len(self.agent_list)`, which can alias per-agent buffers.
- Local `py_compile` passed, so this is not a syntax issue; it is a reproducibility and method-path issue.

## Possible Ablations

- Inspect whether an inference-only run is possible with existing checkpoints.
- Compare M2CL context-generation variables with our DAR/MAD-MM trace fields.
- Add trace fields for `agent_context_instruction`, `context_alignment`, and `context_diversity` before trying to reproduce.
- Use M2CL as a code-contact object rather than a training target.

## Caveats

- The repo may not be cleanly runnable without checkpoints or dataset downloads.
- A full reproduction could be much heavier than our current one-GPU baseline checks.
- The immediate value is conceptual and code-path inspection, not a new metric.
- Current code-contact is pinned to commit `ada64a9089731f4d2e2cfd2048329cf50f65031f`.

## Project Fit

| Question | Answer |
| --- | --- |
| Which project axis does it touch? | context alignment, dynamic context construction, majority-noise avoidance |
| What would we learn by reproducing it? | whether failures we called retention failures are better described as context-state failures |
| What is the cheapest useful check? | clone/read the code path that builds per-agent context instructions |
| Should it be promoted to experiment? | yes as code contact; delay full GPU reproduction until checkpoint/data friction is known |

## Open Questions

- What exactly is a "context instruction" in code?
- Can generated contexts be logged per round and compared with our unified trace?
- Is context diversity independent from answer diversity?
- Can a lightweight, non-training context router approximate the same axis for our current baselines?
