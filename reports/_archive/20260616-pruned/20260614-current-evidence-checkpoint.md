# Current Evidence Checkpoint

## What This Is

This is a pause-and-return note for the current messy state of the project.
It is not a novelty claim, not a plan, and not a request to become useful too
quickly.

The project has now made enough contact with MAD-MM, DAR, MOC, M2CL, PACT, and
a local communication-regime harness that the next work can drift without
losing the thread. This note records the living shape of that contact.

## Current Shape

The early object was multi-agent debate and message retention. The current
object is broader:

```text
when agents should communicate,
what public state should enter the shared channel,
and how final answers are selected from that public state.
```

That shift came from reproduction contact rather than from a planned idea.

## Evidence Already On The Table

| Thread | Contact | What It Left Behind |
| --- | --- | --- |
| MAD-MM | GSM8K short subset, MATH/MMLU-Pro/AIME benchmark atlas, trace extraction | Method ranking changes by benchmark; masking can reduce or misselect memories; GSM8K is too saturated for much of the current question. |
| DAR | GSM8K100 full-history, guarded answer diversity, answer-only/full split, typed-surface preview | Retention failures split into selection failures, continuation failures, and message-surface failures; answer-only is cheaper but sometimes too thin. |
| MOC | topology smoke, forced merge, hop-depth trace check | Merge/compression paths are visible, but current GSM8K smoke is too small and saturated to expose multi-hop evidence effects. |
| M2CL | code contact | The useful pressure is context-state generation, but the public checkout is not yet a clean reproduction target. |
| PACT | HotpotQA50 split-evidence smoke, trace v1.1, field audits, final-answer-contract GPU run | Public action-state fields often contain answer signals; strict EM is heavily affected by final-answer contract and public-state-to-answer selection. |
| Harness | deterministic communication-regime smoke | Task regime and public-state labels are now runnable locally without GPU, even though the agents are symbolic. |

## Warm Findings

PACT is the hottest current object. The original Qwen2.5-14B HotpotQA50 run
had `17/50` strict EM. The final-answer-contract run reached `34/50` on the
same first-50 slice while keeping the same action-state communication protocol.
This is strong evidence that final-answer surface is a real confound in the
current reproduction, not only a postprocessing artifact.

The PACT result should still stay bounded. It introduced `3` right-to-wrong
cases, and post-run public-state arbitration did not transfer cleanly from the
earlier saved-output probe. The interesting object is the boundary between
public state and final commitment, not a simple prompt win.

DAR remains useful as a case microscope. It showed that parsed answer,
evidence, and correctness can diverge inside one retained message. Sample `20`
is the clean sentinel: answer-only collapses a message to `700.0`, while the
full text contains calculation evidence for `7.00`.

The communication-regime harness matters because it keeps us from pretending
all tasks ask the same communication question. Saturated arithmetic, split
evidence, k-hop evidence, state tracking, and conflict evidence should not be
collapsed into one "reasoning benchmark" bucket.

## Things Not To Force

Do not force the current PACT observation into a novelty claim yet.

Do not run another DAR retained-surface variant just because the intermediate
surface is tempting. It is probably useful later, but it should not pull the
project back into local prompt-surface gardening too soon.

Do not scale GSM8K unless the reason is trace hygiene or comparison continuity.
It has repeatedly hidden communication effects behind high baseline accuracy.

Do not treat diagnostic postprocessing numbers as method scores. They are
useful because they separate surfaces, not because they are leaderboard
metrics.

## Possible Next Drifts

| Drift | Why It Is Alive | Smallest Honest Move |
| --- | --- | --- |
| PACT neighboring slice | Tests whether final-answer contract remains a real confound outside the inspected first 50 samples. | Run original and final-contract PACT on HotpotQA samples `50-99`, then extract v1.1 traces and compare transitions. |
| Public-state-to-answer boundary | The saved PACT fields often contain usable answer signals. | Inspect the `13` stable-wrong cases from the final-contract run by field family and answer contract. |
| Non-oracle router harness | The symbolic harness currently uses oracle relevance for `evidence_state` and `route_or_silence`. | Add a noisy/confidence-based router and watch how routing mistakes appear in `context_events`. |
| MOC on explicit k-hop evidence | Current MOC traces show merge mechanics but not useful multi-hop pressure. | Design or find a tiny k-hop split-evidence task before another MOC GPU run. |
| DAR typed public state | Case `20` suggests answer plus short evidence may preserve what answer-only loses. | Keep as an offline prompt-inspection object until there is a harder task or a public-state framing. |

## Current Bias

If we keep moving immediately, the cleanest empirical continuation is a small
PACT neighboring-slice check. If we want to stay local and strange, the cleanest
non-GPU continuation is to make the communication-regime harness less oracle.

Both are acceptable. The project does not need to choose usefulness yet.

## Sources

| Source | Path |
| --- | --- |
| Communication-regime synthesis | `reports/_archive/20260616-pruned/20260614-communication-regimes-synthesis.md` |
| PACT final-answer-contract run | `reports/_archive/20260616-pruned/20260614-pact-final-answer-contract-gpu.md` |
| PACT field-level bridge | `reports/20260615-pact-public-state-field-bridge.md` |
| DAR retention split ablation | `reports/_archive/20260616-pruned/20260613-dar-retention-split-ablation.md` |
| Slot-level peer-message candidate | `reports/_archive/20260616-pruned/20260615-typed-public-state-candidate.md` |
| MAD-MM benchmark atlas | `reports/_archive/20260616-pruned/20260613-madmm-benchmark-atlas.md` |
| M2CL code contact | `reports/_archive/20260616-pruned/20260614-m2cl-code-contact.md` |
| Harness smoke | `reports/_archive/20260616-pruned/20260614-communication-regime-harness-smoke.md` |
| Trace schema | `docs/comm_trace_schema.md` |

## Evidence Register Updates

None. This checkpoint carries existing observations forward; it does not add a
new empirical claim.
