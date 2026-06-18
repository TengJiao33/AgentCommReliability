# MOC Merge Prompt Role Audit

## What We Tried

I ran the five merge-prompt strategies used by MOC's structural message
compression over the six synthetic split-evidence cases from the previous MOC
role probe.

This was a merge-only LLM audit, not a full MOC run:

- script: `scripts/run_moc_merge_prompt_role_audit.py`
- run record: `experiments/_archive/20260616-pruned/20260614-1913-a8002-moc-merge-prompt-role-audit/`
- trace: `comm_trace_moc_merge_prompt_role_audit_v11.jsonl`
- model: `Qwen2.5-7B-Instruct` served as `qwen2.5-7b-merge-audit`
- machine: `A800_2`, GPU `1`
- records: `60` over `6` cases, `2` message surfaces, and `5` merge strategies

The two message surfaces were:

- `labeled_role_messages`: explicit role-slot labels in the agent messages.
- `natural_evidence_messages`: natural language evidence with the same facts but
  without field-like labels.

## What Happened

| Merge Surface | Records | All Required Slots Preserved | Rate | Avg Preserved Slots |
| --- | ---: | ---: | ---: | ---: |
| `labeled_role_messages` | 30 | 19 | 0.63 | 6.40 |
| `natural_evidence_messages` | 30 | 4 | 0.13 | 5.13 |

Strategy-level results:

| Surface | Strategy | All Slots | Avg Slots | Source Attribution |
| --- | --- | ---: | ---: | ---: |
| `labeled_role_messages` | narrative synthesis | 4/6 | 6.67 | 0/6 |
| `labeled_role_messages` | logical integrity | 4/6 | 6.67 | 0/6 |
| `labeled_role_messages` | technical precision | 6/6 | 7.00 | 6/6 |
| `labeled_role_messages` | actionable intelligence | 2/6 | 5.50 | 5/6 |
| `labeled_role_messages` | dedup structure | 3/6 | 6.17 | 0/6 |
| `natural_evidence_messages` | narrative synthesis | 0/6 | 5.33 | 0/6 |
| `natural_evidence_messages` | logical integrity | 1/6 | 4.33 | 0/6 |
| `natural_evidence_messages` | technical precision | 3/6 | 6.00 | 6/6 |
| `natural_evidence_messages` | actionable intelligence | 0/6 | 5.00 | 6/6 |
| `natural_evidence_messages` | dedup structure | 0/6 | 5.00 | 0/6 |

The natural evidence surface most often lost:

- `forbidden_replacement`: 21 losses across 30 outputs.
- `required_qualifier`: 13 losses.
- `clue_object`: 10 losses.
- `requested_relation`: 8 losses.

## Things Noticed

The MOC compression question is now sharper. The issue is not simply whether a
summary is short or whether it mentions the final answer. It is whether the
merge preserves the role each fact played relative to the question.

Explicit role labels make a large difference. With labeled messages, the
`technical_precision` strategy preserves all audited slots in all six cases.
With natural evidence messages, even the same strategy preserves all slots in
only three of six cases.

Source attribution is helpful but not sufficient. On the natural surface,
`actionable_intelligence` preserves source attribution in all six cases while
preserving all required role slots in none of them. It can still drop the
qualifier, requested relation, or forbidden replacement.

This supports the earlier synthetic role-loss probe without overstating it:
role-aware compression can preserve the needed information, but ordinary
summary surfaces and prompt strategy choices can flatten role information.

## Failures / Friction

Existing remote services on the checked ports were not usable OpenAI-compatible
chat-completion endpoints for this audit, so I started a temporary vLLM service
on A800_2 GPU `1`, port `8022`, and stopped it after the run.

The first local script version missed one audit argument in trace construction;
I patched it before the successful remote run and verified the script with
`py_compile`.

## Caveats

- This does not run the full MOC graph.
- MOC's ISM pair selection and embedding-based strategy selection are not
  exercised.
- The cases are synthetic and hand-built.
- Slot preservation is a deterministic lexical check, not a semantic judge.
- The numbers are audit signals, not benchmark accuracy.

## Loose Threads

The next MOC step should not be another saturated GSM8K hop run.

If this line stays active, the smallest useful next contact is to inspect the
natural-surface failures and design one role-preserving merge surface or prompt
contract. Only after that would it be worth touching a tiny real MOC
split-evidence domain.

## Evidence Register

Added row `E-054`.
