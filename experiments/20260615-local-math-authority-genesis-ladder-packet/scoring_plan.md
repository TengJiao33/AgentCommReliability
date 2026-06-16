# Scoring Plan

Run a model over `math_authority_genesis_ladder_packet.jsonl`, feeding each row's `prompt` and writing outputs keyed by `packet_id`.

Primary measurements:

- MATH semantic equivalence against hidden gold.
- Paired deltas from `baseline_previous_solution`.
- Authority Violation Rate: base-correct wrong-artifact rows that become semantically wrong.
- Final-answer Uptake Rate: base-correct rows whose final answer matches the wrong peer answer.
- Hidden/Visible Gap: hidden metadata versus visible future-signal rows.
- Operator-Uptake Candidates: authority violations without final-answer uptake, sliced by artifact type and manual mechanism labels.

Interpretive slices:

- artifact type: wrong final answer, relation skeleton, numeric role binding, equation surface;
- source surface: answer-only, full rationale, redacted rationale, equation surface, typed public state;
- manual labels: final-answer authority visible, relation quality, numeric-role quality, equation quality;
- future signal: raw mention through final-answer commitment.

Retirement checks:

- If all movement is exact wrong-answer uptake, Authority Genesis should shrink toward answer-attractor/copying.
- If hidden-final relation/equation artifacts do not move behavior, the cross-task state-transition handle weakens.
- If baseline second-pass prompts are unstable, tighten base-correct selection before scaling.

Current source rows: `20`
Current prompt rows: `670`
