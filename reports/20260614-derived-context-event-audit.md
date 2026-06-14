# Derived Context Event Audit

## What We Tried

Summarized recipient-context events derived from existing schema v1.1 traces.

This is still a no-GPU step. It asks whether the newly populated `context_events` field gives us useful contact with real reproduced systems before launching another model run.

## What Happened

- run record: `experiments/20260614-1245-local-derived-context-event-audit/`
- script: `scripts/summarize_context_events.py`
- input traces: 7
- records: 610
- rows with context events: 560
- context events: 590

Context-event derivations:

| Derivation | Count |
| --- | ---: |
| `from_mask_history` | 150 |
| `from_retention_event` | 400 |
| `from_ism_result` | 40 |

## Things Noticed

The derived context events make the difference between message surface and recipient context more concrete.

In MAD-MM MATH50, CoT has no context event, while all debate methods have one derived event per row. Objective masking creates a very sparse context distribution: many rows expose only one retained memory. Subjective and naive variants expose more full contexts, but that does not automatically improve final correctness.

In DAR GSM8K100, original `filter_critical` retained:

- 1 visible peer in 64 rows;
- 2 visible peers in 27 rows;
- 3 visible peers in 9 rows.

The guard variants shifted the retained context larger:

- 1 visible peer in 53 rows;
- 2 visible peers in 35 rows;
- 3 visible peers in 12 rows.

This matters because the earlier split ablation is no longer just "guard or answer-only." It is also a recipient-context-size and recipient-context-surface change.

In MOC hop checks, hop1 has 20 target contexts with one represented source each. Hop2 has 15 target contexts where a compressed merge represents two source agents, but the task is too saturated to expose answer impact.

## Caveats

- These are derived context events, not raw prompts.
- Visible source count is not evidence quality.
- The DAR and MOC examples still mostly sit in saturated arithmetic regimes.
- This audit should not be treated as a method result.

## Loose Threads

- Inspect DAR right-to-wrong cases by context surface, visible count, and retained answer correctness.
- Add prompt-level context logging only if a small real run is justified.
- Prefer a k-hop or conflict-evidence task for the next model contact.
