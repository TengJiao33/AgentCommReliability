# PACT Target-State Freeze Inspection

## What We Tried

After the offset150 compact `Target Slot` run hurt performance, I inspected the
saved traces before trying another prompt or GPU run.

Added:

- `scripts/build_pact_target_state_freeze_inspection.py`

Ran it over:

- `experiments/_archive/20260616-pruned/20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target/comm_trace_offset150_compact_final_v11.jsonl`
- `experiments/_archive/20260616-pruned/20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target/comm_trace_offset150_final_contract_v11.jsonl`
- `experiments/_archive/20260616-pruned/20260614-1642-a8002-pact-qwen25-14b-hotpot50-offset150-compact-target/final_vs_compact_final_cases.jsonl`

Output:

- `experiments/_archive/20260616-pruned/20260614-1719-local-pact-target-state-freeze-inspection/`

No model calls and no GPU use.

## What Happened

The mechanical scan keeps the negative result alive but makes it less blunt:

| Diagnostic | Count |
| --- | ---: |
| records | `50` |
| unstable target-slot records | `23` |
| first/final target-slot mismatch | `22` |
| template-collapse records | `4` |

For the `8` right-to-wrong cases:

| Bucket | Samples |
| --- | --- |
| visible target drift regression | `189`, `193`, `197`, `199` |
| regression despite stable target | `153`, `154`, `164`, `182` |

Manual labels over the first `16` focus cases are more cautious:

| Manual reading | Samples |
| --- | --- |
| question-derived or anchor-checked target state might help | `189`, `197`, `199`, `184` |
| first-turn generated freeze would hurt or preserve an error | `193`, `176`, `188`, `160` |
| not primarily a target-state failure | `153`, `154`, `164`, `182`, `185`, `163` |
| target drift was useful or not needed | `152`, `173` |

## Things Noticed

The useful distinction is between generated target-slot stability and
question-derived target-state preservation.

Freezing the first generated target slot is not a good next method. In several
cases, the first slot is a bridge state, an early wrong commitment, or too
generic. Sample `176` needs refinement from an artist/museum path to
`drawings`. Sample `188` needs aggregation from two individual film genres to a
yes/no comparison.

But the target-state axis is still real. Sample `199` alternates between
`1999 Odisha cyclone` and `Cyclone Gonu`; sample `189` switches from the
Albanian Fascist Party to the Party of Labour of Albania; sample `197` drifts
from `headquartered in what city` toward `founded in what city`.

Those are not solved by asking the model to regenerate a `Target Slot` every
turn. They suggest a stricter interface:

```text
derive target state from the original question;
allow bridge evidence to fill slots;
flag later public states that replace the answer type, anchor, or predicate.
```

## Loose Threads

The next local move should be an offline target-state projection/checker over
existing PACT traces, not another generated field.

A useful checker would separate:

- answer type;
- anchor entity/entities;
- predicate or requested relation;
- required qualifier;
- bridge entity discovered from evidence.

It should explicitly allow bridge refinement, otherwise it will punish the very
multi-hop behavior HotpotQA requires.

## Caveats

- This is postprocessing only.
- The manual labels cover 16 focus cases, not all possible target-state cases.
- HotpotQA exact match still entangles target state with alias granularity,
  strict span choices, and final-answer extraction.
- No claim is made that a frozen target-state method would improve EM.

## Evidence Register

Added row `E-052`.
