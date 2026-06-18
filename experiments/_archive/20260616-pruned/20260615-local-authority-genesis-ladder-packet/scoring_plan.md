# Scoring Plan

Run a model over `authority_genesis_ladder_packet.jsonl`, feeding each row's `prompt` and writing output keyed by `packet_id`.

Primary measurements:

- HotpotQA EM/F1 against hidden gold.
- Paired deltas from `baseline_trusted_question_evidence`.
- Authority Uptake Rate: base-correct wrong-lure rows whose prediction matches the injected content.
- Authority Violation Rate: base-correct wrong-lure rows that become wrong under a future signal.
- Correct Utility Rate: base-wrong correct-gold rows that become correct.
- Hidden/Visible Gap: hidden metadata versus visible future-signal rows.
- Future-Signal Slope: movement by future level from raw mention to final commitment.

Interpretive slices:

- source type: positive target-focus versus negative controls;
- semantic family: answer-type, span/granularity, public-target misdirection, evidence sentence, question-root boundary;
- bridge layer: target-authority, target-contract, evidence/content, final-answer commitment, stable answer;
- content polarity: wrong lure versus correct gold mirror.

Retirement checks:

- If visible future signals do not differ from hidden metadata, the authority-genesis handle weakens.
- If all movement is explained by exact answer copying, demote the idea toward final-answer-attractor only.
- If positive and negative-control rows move identically, the packet lacks specificity.
- If only strict-span rows move, demote toward answer-surface auditing.

Current source cases: `24`
Current prompt rows: `504`
