# Experiment Protocol

This is a neutral template for future work. It does not preserve any old experiment line.

## Principle

Every future run should be understandable from its own notes. A result without task, code state, command, resource, output path, and caveat is not a durable result.

## Run ID Format

Use:

```text
YYYYMMDD-HHMM-<machine>-<task>-<short-note>
```

## Required Run Note

Create one note per run under `experiments/<run-id>/README.md`.

```markdown
# <run-id>

## Question

What are we trying to decide?

## Scope

- Task:
- Method or intervention:
- Baseline:
- Model:
- Dataset or input source:
- Sample count:

## Machine

- Host:
- GPU:
- Free memory before launch:
- Work dir:

## Code

- Repo or script:
- Commit:
- Local modifications:

## Environment

- Python:
- Key packages:
- Backend:

## Command

```bash
```

## Outputs

- Remote directory:
- Logs:
- Raw results:
- Summary:

## Result

- Status:
- Main metric:
- Wall time:
- Token or compute cost:

## Caveats

- 

## Cleanup

- Keep:
- Delete:
```

## Status Values

Use one of:

- `PREPARED`
- `RUNNING`
- `COMPLETED`
- `FAILED_NO_RESULT`
- `FAILED_EVALUATION`
- `STOPPED_BY_RESOURCE`
- `ARCHIVED`

## Report Rule

Most facts stay in the run README. Write a top-level report only when a result changes what to do next.
