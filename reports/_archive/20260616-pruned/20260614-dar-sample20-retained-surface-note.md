# DAR Sample 20 Retained Surface Note

## What We Checked

Inspected DAR GSM8K100 sample `20` across four variants:

- original `filter_critical`
- guarded answer-only
- answer-only no-guard
- guard-full

The goal was to understand why `guard_full` fixed the case while answer-only variants did not.

The manual note is now backed by a reproducible local extraction:

- script: `scripts/extract_dar_case_surface.py`
- output: `experiments/_archive/20260616-pruned/20260614-1253-local-dar-case20-surface-extract/`
- full retained-message rows: `experiments/_archive/20260616-pruned/20260614-1253-local-dar-case20-surface-extract/retained_messages.jsonl`

## What Happened

| Variant | Retained IDs | Message Mode | Round 1 Agent Answers | Final |
| --- | --- | --- | --- | --- |
| original `filter_critical` | Agent2, Agent3 | full | 7, 700, 700 | wrong, 700 |
| guarded answer-only | Agent2, Agent3, Agent1 | answer-only | 7, 12, 700 | wrong, 12 |
| answer-only no-guard | Agent2, Agent3 | answer-only | 7, 12, 700 | wrong, 12 |
| guard-full | Agent2, Agent3, Agent1 | full | 7, 7, 700 | correct, 7 |

The first round had three parsed answers:

- Agent1: `7`, correct, with correct reasoning.
- Agent2: `120`, wrong, caused by treating `$3.20` as the cost of four candies rather than subtracting lollipops first.
- Agent3: `700`, parsed wrong, but its reasoning actually computes `$7.00`.

So this is not a clean answer-correctness case. Agent3 is a parser/format false negative: the reasoning says `7.00`, but the final marker is `{final answer: 700}`.

## Things Noticed

Answer-only retained context loses the distinction between a genuinely wrong answer and a parsed-wrong-but-useful reasoning scaffold.

In guarded answer-only, the guard adds Agent1, so the retained answer buckets include `7`, `120`, and `700`. That still leaves Agent2 repeating the `$3.20 / 4 = $0.80` mistake and ending at `12`.

In guard-full, Agent2 sees enough full reasoning context to switch from `120/12` to `7`. Agent3 still outputs `{final answer: 700}`, but its visible reasoning explicitly says the correct total is `$7.00`, so the final majority becomes correct.

The code path for the answer-only variant is also narrower than "short
reasoning": the DAR patch replaces each retained peer response with
`Previous parsed final answer: <answer>` before calling `build_normal_msg`.
For sample `20`, that collapses Agent3 from a parsed-wrong-but-useful full
message into only `Previous parsed final answer: 700.0`.

## Interpretation

The useful handle is not simply answer diversity. The missing middle is an evidence-preserving retained surface:

```text
parsed answer + short calculation/evidence
```

This case argues against expanding GSM8K before trying a small intermediate message mode. Full reasoning can recover parser/continuation failures, but it gives back much of the token saving. Answer-only is cheap, but can erase the evidence needed to reinterpret malformed final answers.

## Caveats

- One case only.
- The case is unusually parser-sensitive because `7.00` and `700` are semantically close but parsed differently.
- It is still useful because the same pattern can appear whenever retained messages include final-answer formatting errors or unparseable final markers.

## Loose Thread

Try a small DAR variant that passes each retained peer as parsed answer plus a compact evidence line, then compare it against answer-only and guard-full before running a larger GSM8K or harder-task matrix.
