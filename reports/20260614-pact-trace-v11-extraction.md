# PACT Trace v1.1 Extraction

## What We Tried

Added PACT support to the unified communication trace extractor and re-extracted
the existing Qwen2.5-14B HotpotQA50 PACT run into schema `acr.comm_trace.v1.1`.

No model call or GPU run was launched.

## What Happened

Output:

- `experiments/20260614-1100-a8002-pact-qwen25-14b-hotpot50/comm_trace_pact_v11.jsonl`

Validation:

| Check | Result |
| --- | ---: |
| records | 50 |
| schema rows | 50 `acr.comm_trace.v1.1` |
| communication events | 200 |
| context events | 150 |
| `Action Required` present | 200/200 turns |
| `Environment State` present | 200/200 turns |
| `Action Result` present | 200/200 turns |
| `Final Answer` present | 50/200 turns |
| `<think>` spans | 0/200 turns |
| HotpotQA gold preserved as text | yes |

Each PACT agent output is represented as a `communication_event`. The first
three turns of each sample also produce derived `context_events`, because those
public action-state messages are appended to the shared history for the next
agent. The final turn is not represented as a recipient context update.

## Things Noticed

PACT now sits inside the same trace surface as MAD-MM, DAR, and MOC. That makes
the comparison with DAR typed previews less hand-wavy:

- DAR retention traces expose which peer messages are visible.
- PACT traces expose which public state fields are visible.
- Both now use `context_events` to say what the next agent can see.

The caveat from the original PACT smoke remains important. The run has strong
field compliance, but no `<think>` spans were emitted, so it does not test
private-reasoning stripping. It mostly tests structured public action-state
messaging and final-answer surface behavior.

## Caveats

- This is a trace extraction over an existing 50-sample smoke, not new behavior.
- PACT transitions remain `unknown` because there is no first-round independent
  answer baseline in the result JSONL.
- The extractor does not copy full prompts or token ID lists into the trace.
- PACT gold answers are preserved as text. This corrects an earlier local trace
  normalization bug that collapsed text/date gold answers to the last number.

## Loose Threads

- Use `experiments/20260614-1345-local-pact-extraction-only-audit/` before any
  larger rerun.
