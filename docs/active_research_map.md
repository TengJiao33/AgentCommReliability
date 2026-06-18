# Active Research Map

Snapshot date: `2026-06-17`.

This file defines the active reading surface after pruning and the benchmark-first reset. It is not a claim summary; it is a navigation rule for the repository.

## Live Spine

The current live story is:

```text
multi-agent communication reliability
-> externally defined tasks must first require communication or role-separated information movement
-> private facts need to become reliable public state before final commitment
-> protocols should preserve, type, admit, and merge task-relevant facts under benchmark pressure
```

The old authority genesis / epistemic type-erasure line is no longer the main story. It remains a mechanism microscope: useful for explaining how a receiver may inherit wrong equation surfaces, numeric roles, relation skeletons, or final-answer artifacts, but not sufficient to choose the benchmark or support the paper claim by itself.

## Active Evidence Families

| Family | Role | Keep Active |
| --- | --- | --- |
| Benchmark-first reset | Current navigation rule and retirement boundary. | `reports/20260617-benchmark-first-reckoning.md`. |
| HiddenBench communication necessity | Best currently runnable external pressure: hidden/private information, full-info and oracle-public-facts controls, project-local full65 probe, and Stage 1 full65 sender-message pollution diagnostic. | HiddenBench full65 report, Stage 1 full65 report, corrected analysis, local dataset under `data/external/hiddenbench/`. |
| PerspectiveGap orchestration routing | New external benchmark contact for role-specific information routing and leakage in multi-agent orchestration prompts. It has answer-keyed role-fragment assignment, deterministic prompt-writing scoring, a local 220-row contact run, first Qwen2.5 7B/14B smoke evidence, and a zero-temperature 40-row stratified subset showing higher 14B coverage with much higher distractor leakage. | `baselines/PerspectiveGap/reproduction.md`; `experiments/20260618-local-perspectivegap-contact/`; `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-7b/`; `experiments/20260618-a8002-perspectivegap-role-assignment-smoke-qwen25-14b/`; `experiments/20260618-a8002-perspectivegap-role-assignment-stratified20-qwen25-7b14b/`; `reports/20260618-perspectivegap-benchmark-contact.md`; `reports/20260618-perspectivegap-model-smoke-and-paper-story.md`. |
| PACT-style split evidence | Benchmark-style setting, not the PACT method name itself: HotpotQA / 2Wiki evidence split where agents must exchange supporting facts. | PACT reproduction notes, future split-evidence protocol packets, public-state field lessons only as design background. |
| TeamBench feasibility | Hard engineering benchmark for OS-enforced role separation, currently blocked by missing Docker/rootless container support. | Docker feasibility report and future admin-permission check. |
| MATH / TypeCast microscopes | Diagnostic vocabulary for invalid cast and operator uptake. | MATH operator lifecycle v1, authority mechanism audit, sender-receiver micro-protocol; no scaling unless an external benchmark motivates it. |
| Model-family pressure | Guardrail against Qwen2.5-14B-only stories. | model-family gap report and future cross-model matrix. |

## Pruned Branches

The following branches are archived rather than active:

- early MAD-MM, DAR, MOC reproduction contact and benchmark atlas work;
- old communication-regime schema contact that is now background context;
- old PACT offset50/100/150 scans and postcard/sketchbook reports;
- peer-redacted and source-label probes that were useful for taste but not decisive;
- PACT answer-contract verifier variants superseded by field/authority framing;
- MATH type-erasure v1 and smoke runs superseded by v2;
- MATH / TypeCast re-answer variants as main-story evidence;
- TypeCastArena live sender12/receiver204, shard001, bootstrap, non-rawgold source, non-clean receiver, inert315, and repaired117 branches as scalable benchmark evidence;
- failed or superseded planning notes that no longer decide what to run.

Their reports live under `reports/_archive/20260616-pruned/`.
Their run records live under `experiments/_archive/20260616-pruned/`.

## What Counts As Active

A top-level report or experiment should satisfy at least one of these:

- it directly supports the benchmark-first reset;
- it defines or runs an external communication-necessity benchmark;
- it defines or runs an external role-specific information routing benchmark;
- it defines a reusable packet or evaluator for HiddenBench, PACT-style split evidence, or another externally motivated benchmark;
- it records a recent failure that prevents repeating the same mistaken experiment;
- it is a synthesis or external-pressure note needed for paper positioning;
- it is a mechanism microscope that explains a failure observed under an external benchmark.

Everything else should live in archive unless reopened with a concrete reason.

## Cleanup Boundary

This pruning intentionally avoids deleting raw evidence. The active surface is cleaned by moving files into dated archive folders, then rewriting Markdown paths so older claims remain traceable. Only obvious temporary files or caches should be deleted outright.

## Current Warning

The MATH / TypeCast line is retired as the main paper story. Treat it as a mechanism vocabulary and a postmortem source, not as a benchmark. Do not spend another large GPU run on MATH / TypeCast variants unless HiddenBench, PACT-style split evidence, TeamBench, SOTOPIA-TOM, or another external benchmark exposes a concrete mechanism question that those microscopes can answer.
