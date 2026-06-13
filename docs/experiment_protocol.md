# Experiment Protocol

## Principle

Every experiment should be returnable by another person from the notes alone. A result without model, code commit, command, resource, and log path is hard to revisit.

Use `docs/evidence_register.md` only for observations or claims that outlive a single run. Keep ordinary facts in the run note or `docs/project_log.md`.

## Run ID Format

Use:

```text
YYYYMMDD-HHMM-<machine>-<method>-<model>-<task>-<short-note>
```

Examples:

```text
20260628-1430-a8002-madmm-qwen25-gsm8k-memory-mask-smoke
20260629-1015-a8002-moc-qwen25-synthetic-khop-topology-ablation
```

## Run Metadata

Create one note per run under `experiments/<run-id>/README.md`.

Template:

```markdown
# <run-id>

## What We Tried

## Machine

- Host:
- GPU:
- Free memory before launch:
- Work dir:

## Code

- Baseline repo:
- Commit:
- Local modifications:

## Environment

- Python:
- PyTorch:
- Transformers:
- LLM/API backend:

## Data / Task

- Dataset:
- Size:
- Split:
- Preprocessing:

## Command

```bash
```

## Outputs

- Log:
- Raw results:
- Summary:

## Result

- Status:
- Main metric:
- Token cost:
- Wall time:

## Notes

- Failure:
- Fix:
- Caveat:
- Loose thread:
```

## Small Variant Menu

When variants feel useful, keep the first grid small so the run remains understandable.

| Axis | Values |
| --- | --- |
| agents | 1, 2, 3 |
| rounds | 1, 2, 3 |
| communication | none, full, masked |
| message type | answer only, evidence, full reasoning |
| judge | none, majority, verifier |
| memory noise | clean, injected wrong memory |

## Minimum Logging Schema

Store one JSON object per problem instance.

```json
{
  "run_id": "",
  "instance_id": "",
  "method": "",
  "model": "",
  "task": "",
  "agent_count": 0,
  "rounds": 0,
  "communication_mode": "",
  "message_type": "",
  "judge_mode": "",
  "memory_noise": "",
  "final_answer": "",
  "gold_answer": "",
  "correct": false,
  "token_input": 0,
  "token_output": 0,
  "round_logs": [],
  "conflicts": [],
  "judge_trace": "",
  "error": ""
}
```

## Observation Prompts

For any run or variant, optionally ask:

- Did performance change or only token cost change?
- Did communication change the final answer?
- Did agents copy a wrong memory?
- Did any agent correct another agent?
- Did the judge follow evidence or majority?
- Is the gain explained by extra samples rather than communication?
- Is the setup deterministic enough to return to later?

## Report Structure

Use report templates only when they help preserve the encounter. A compact shape is:

```markdown
# Title

## Short Answer

## Setup

## What Reproduced

## What Failed

## Ablations

## Observations

## Caveats

## Loose Threads
```

## Evidence Language

Preferred wording:

- "This run reproduces the code path under a small controlled setup."
- "This is smoke evidence, not benchmark evidence."
- "The observed trend holds for this model/task subset."
- "This looks like something to return to later."

Avoid:

- "This proves communication is useful."
- "This method is better."
- "The paper is wrong."
- "The model understands the debate."
- "This must be the next research direction."
