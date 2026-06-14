# PACT Final-Answer Surface Audit

## What We Tried

Using the new PACT v1.1 trace, I audited strict EM failures without generating
any new model outputs. The question was whether the HotpotQA50 score is mostly
reasoning failure, or whether final-answer surface and extraction are visibly
mixed in.

No model call or GPU run was launched.

## What Happened

Official EM remains `17/50`. The audit only labels failure surfaces.

Among 33 wrong-EM samples:

| Surface category | Count |
| --- | ---: |
| yes/no answer begins with the correct `yes` or `no` | 7 |
| non-yes/no final answer begins with normalized gold | 8 |
| numeric final answer contains normalized gold number | 2 |
| action-result field begins with normalized gold | 1 |
| no simple surface signal | 15 |

So `18/33` wrong-EM cases have a simple surface candidate. This should not be
reported as a new score, but it is strong evidence that strict EM is not a clean
reasoning-failure signal for this PACT smoke.

## Things Noticed

The audit makes the earlier PACT caveat sharper. PACT's public action-state
format is highly compliant, but final-answer brevity is weak. Examples include:

- gold `yes`, final answer begins "Yes, ..." and then explains;
- gold `Animorphs`, final answer begins "Animorphs is ...";
- gold `3677`, final answer says "can seat 3,677 people";
- gold `Henry J. Kaiser`, action result begins with the correct name while the
  final answer begins with "Yes, ...".

This means a next PACT run should not be larger by default. The cheaper check is
to test answer extraction or final-answer instruction changes on saved outputs
or a tiny slice, while using the trace to separate:

- public evidence field quality;
- final answer extraction;
- actual reasoning/evidence failure.

## Caveats

- These labels are postprocessing diagnostics, not alternate official scores.
- Prefix and numeric containment checks can over-credit ambiguous cases.
- The current run emitted no `<think>` spans, so private-reasoning stripping is
  still not tested.

## Loose Threads

- See `reports/20260614-pact-evidence-field-audit.md` for the completed
  field-level follow-up.
- Avoid scaling HotpotQA before the answer-surface confound is controlled.
