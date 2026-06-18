# PACT HotpotQA Smoke

## Short Take

PACT now runs end to end on A800_2 and produced a useful 50-sample HotpotQA trace with Qwen2.5-14B-Instruct. The run is good setup evidence and a good communication-surface diagnostic; it is not evidence that PACT improves reasoning.

## Runs

| Run | Model | Samples | EM | Avg F1 | Avg comm tokens | Avg total tokens | Status |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `20260614-1055-a8002-pact-qwen25-7b-hotpot5` | Qwen2.5-7B-Instruct | 5 | 0.20 | 0.344 | 294.6 | 4129.0 | complete |
| `20260614-1100-a8002-pact-qwen25-14b-hotpot50` | Qwen2.5-14B-Instruct | 50 | 0.34 | 0.508 | 339.3 | 4746.8 | complete |

## What Worked

- Remote source clone succeeded at upstream commit `91acf820f8a69fc7c181120b3120444a98823230`.
- PACT syntax compilation passed locally and remotely.
- HotpotQA dev-distractor was obtained through a local Hugging Face download and transferred to A800_2 after the official CMU source and remote Hugging Face access stalled or timed out.
- vLLM loaded both Qwen2.5-7B-Instruct and Qwen2.5-14B-Instruct directly from `/mnt/quarkfs/share_model`.
- GPU 1 was released after both runs.

## Communication Surface Observation

The 50-sample run followed the action-state format very cleanly:

- `Action Required`: 200/200 agent turns.
- `Environment State`: 200/200 agent turns.
- `Action Result`: 200/200 agent turns.
- `Final Answer`: 50/50 final turns.
- `<think>` spans: 0/200 turns.

So this run mostly tests whether a short public action-state surface is usable. It does not yet test the intended private-reasoning stripping path, because the model did not emit hidden reasoning.

## Main Failure Shape

Strict EM is low at `17/50`, but a visible part of the loss is final-answer surface mismatch:

- 7 wrong-EM yes/no cases began with the correct `yes` or `no`, then added a sentence.
- 8 wrong-EM non-yes/no cases began with the normalized gold answer, then added extra words.

These are not alternate official scores. They say the next serious check should separate:

- reasoning/evidence failure;
- final answer formatting failure;
- extraction failure.

## Relation To Answer-Only And Full Reasoning

In our DAR language, `answer_only` means downstream agents see just the retained parsed answer surface. `full` means they see the selected agent's full retained message or reasoning surface. PACT is an intermediate surface: it forwards a compact evidence-bearing record with the required action, the key evidence sentence, and the result. That is why the middle state is worth testing: answer-only can be too thin for cases needing calculation or evidence, while full reasoning can be too noisy or contaminating.

## Caveats

- This is Qwen2.5-14B, not Qwen3-14B.
- This is 50 samples, not the full 7,405-item dev set.
- No paper comparison should be made from these numbers.
- The prompt's field compliance is strong, but final answer brevity is weak enough to affect EM.

## Next Check

PACT trace extraction, the postprocessing-only final-answer audit, the evidence-field audit, the extraction-only audit, the stable-wrong follow-up, and the unrecovered-case inspection are now available. Do not scale HotpotQA until the answer-contract and public-state-selection confounds are controlled.
