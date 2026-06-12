# Experiment Protocol

## Principle

Every experiment should be resumable by another person from the notes alone. A result without model, code commit, command, resource, and log path is not usable evidence.

Use `docs/documentation_system.md` for artifact boundaries and `docs/evidence_register.md` for claims that outlive a single report.

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

## Required Run Metadata

Create one note per run under `experiments/<run-id>/README.md`.

Template:

```markdown
# <run-id>

## Goal

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
```

## First Ablation Grid

Keep the first grid small. The goal is to find whether communication effects are visible, not to publish a benchmark.

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

## Analysis Checklist

For each ablation, answer:

- Did performance change or only token cost change?
- Did communication change the final answer?
- Did agents copy a wrong memory?
- Did any agent correct another agent?
- Did the judge follow evidence or majority?
- Is the gain explained by extra samples rather than communication?
- Is the setup deterministic enough to repeat?

## Report Structure

Use `reports/_templates/objective_research_report.md` for most interpreted reports. A compact version is:

```markdown
# Title

## Short Answer

## Setup

## What Reproduced

## What Failed

## Ablations

## Observations

## Caveats

## Open Questions
```

## Evidence Language

Preferred wording:

- "This run reproduces the code path under a small controlled setup."
- "This is smoke evidence, not benchmark evidence."
- "The observed trend holds for this model/task subset."
- "The run suggests a failure mode worth testing, but does not establish a general claim."

Avoid:

- "This proves communication is useful."
- "This method is better."
- "The paper is wrong."
- "The model understands the debate."
