# Harness

This folder will hold lightweight wrappers for controlled multi-agent communication experiments.

First harness goals:

- normalize logs across baselines;
- keep model/task/agent/round/message settings explicit;
- make communication modes easy to compare;
- avoid hidden global state and unrecorded prompt changes.

Initial communication modes:

- `none`
- `full`
- `masked`
- `compressed`
- `answer_only`
- `evidence_only`

No harness code has been added yet. Write code only after one baseline has been inspected.

