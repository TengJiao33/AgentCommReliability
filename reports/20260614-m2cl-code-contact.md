# M2CL Code Contact

## What We Tried

We added M2CL as a pinned upstream submodule and inspected the code path that should create per-agent context/role updates.

The goal was not to run a full training reproduction. The goal was to check whether M2CL can serve as a concrete next contact after the communication-regimes synthesis, especially for the concern that our recent DAR variants are only local message-surface probes.

## What Happened

- submodule path: `baselines/M2CL/upstream`
- upstream commit: `ada64a9089731f4d2e2cfd2048329cf50f65031f`
- syntax check: `main.py` and `method/M2CL.py` pass `py_compile`
- execution status: not launched, because the inspected public checkout is blocked before meaningful reproduction

The most important blocker is that `method/M2CL.py::gen_response` immediately returns `"success generate"`. That makes the later local Llama/OpenAI generation branches unreachable, so a naive run would not test the intended method.

## Things Noticed

M2CL's useful pressure is real: it places generated per-agent context at the center of discussion. In code, `role_generator.gen_role` creates role text from `question + peer responses`, and the agent's next message is conditioned on that generated role/context plus the other agents' responses.

That is a stronger axis than our current retained-message variants. It suggests our trace schema is missing fields like:

- `agent_context_instruction`;
- `context_source_messages`;
- `context_diversity`;
- `context_drift_from_base_role`;
- `context_alignment_with_question`;
- whether final changes came from peer answers or from changed recipient context.

## Failures / Friction

| Friction | Why It Matters |
| --- | --- |
| `gen_response` is stubbed | A launch would not exercise the LLM generation path. |
| required `api_key.txt` is absent | Even local-model runs hit an API-key assumption. |
| proxy is hardcoded | Environment behavior is machine-specific. |
| dataset folder is absent | README does not pin the exact `question_answer.npy` artifact. |
| generator/model checkpoints are absent | README marks checkpoint release as TODO. |
| `trl` is imported but not listed | Environment reproduction is incomplete. |
| buffer lists are created with list multiplication | Per-agent buffers may alias each other. |

## Interpretation

M2CL should not be our next GPU reproduction target in its current public-code state.

It should be our next conceptual/code-contact pressure target: it tells us to stop treating communication only as "which message survives" and start recording the context state that receives and interprets messages.

This resolves part of the contradiction around the top-level skill. The skill should prevent premature idea forcing, but it should not trap us in shallow variants. M2CL is useful because it gives a deeper variable to carry back into our own traces without pretending we already have a new method.

## Recommended Next Move

Do not patch M2CL into a full runnable training job yet.

Instead, add a small communication-regime harness or trace extension that can represent:

- public state surface: answer, evidence, action-state, confidence, full reasoning;
- recipient context: static role, generated role, task-local context, peer-derived context;
- task regime: recall, state tracking, k-hop evidence, conflict evidence, saturated arithmetic;
- communication decision: speak, route, summarize, stay silent.

If we touch M2CL code again, the smallest honest target is a non-training synthetic smoke that logs generated context states after explicitly removing the generation stub and documenting that this changes the public checkout.

## Caveats

- This note is pinned to upstream commit `ada64a9089731f4d2e2cfd2048329cf50f65031f`.
- It is not a reproduction of paper results.
- The upstream repository may become more runnable if checkpoints/data are released later.
