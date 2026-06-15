# Scoring Plan

Primary score:

- HotpotQA normalized exact match and token F1 against `evaluation.gold_answer`.

Required slices:

- `source_run`: `baseline` vs `final_contract`.
- `condition`: five field visibility conditions.
- `bridge_layer` and `bridge_family` from the field bridge audit.
- `target_slot_diagnostic.target_slot_drift_candidate`: target-drift candidate vs non-candidate.
- `field_gold_presence_in_source_event`: whether the saved source event has a gold string in action required, environment state, action result, or final answer.

Secondary labels to compute after model output:

- `candidate_copy`: output equals the visible `Final Answer Candidate` under normalization.
- `candidate_correction`: candidate is visible, candidate is wrong, and output is correct.
- `candidate_regression`: candidate is visible, candidate is correct, and output is wrong.
- `target_sensitive_delta`: condition difference between public target, hidden target, and frozen target variants for the same sample/source.
- `question_hidden_failure`: output changes from correct to wrong when moving from question-visible public state to public-target-only state.

Do not treat this packet as a method benchmark until it is run on at least one model and compared against the saved PACT official outputs.
