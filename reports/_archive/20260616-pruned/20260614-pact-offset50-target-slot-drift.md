# PACT Offset50 Target-Slot Drift Diagnostic

## What We Tried

I added a rough lexical diagnostic over PACT `Action Required` fields.

The goal was not to build a semantic classifier. It was to ask a smaller
question after sample `58`: does the public action-state target still look
aligned with the original question by the final turn?

Source artifacts:

- `scripts/audit_pact_target_slot_drift.py`
- `experiments/_archive/20260616-pruned/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/target_slot_drift_summary.json`
- `experiments/_archive/20260616-pruned/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/target_slot_drift_cases.jsonl`
- `experiments/_archive/20260616-pruned/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/target_slot_drift_candidates.jsonl`
- `experiments/_archive/20260616-pruned/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/target_slot_drift_all_summary.json`

The diagnostic compares the final-turn `Action Required` against the original
question using:

- question/action content-token overlap;
- capitalized anchor phrase preservation;
- simple tracked slot terms such as `population`, `city`, `song`, `director`;
- risky introduced terms such as `civil`, `parish`, `district`, `song`.

## What Happened

On the 28 non-stable-right focus cases, the heuristic flags 8 target-slot drift
candidates:

| Transition | Candidate count |
| --- | ---: |
| `right_to_wrong` | `2` |
| `stable_wrong` | `6` |

Running the same diagnostic over all 50 offset cases gives the same 8
candidates and no stable-right candidates.

Candidate samples: `54`, `55`, `58`, `60`, `82`, `83`, `87`, `89`.

| Sample | Atlas/manual context | Baseline final | Variant final | Reading |
| ---: | --- | --- | --- | --- |
| `54` | strict-span regression | all three writers with `and` | same names without `and` | likely lexical/contract false positive; content mostly stable |
| `55` | missing qualifier | verbose `Marion, South Australia` answer | `Marion` | final target asks founding year, answer gives city |
| `58` | content drift | `35,124` | `273` | clean target-slot drift to a distractor |
| `60` | wrong answer type/slot | full distinction sentence | `Muggsy Bogues` | final answer gives person, not distinction |
| `82` | likely evidence/reasoning failure | constitutional practice sentence | `requiring only men to register for the draft` | target becomes generic confirmation |
| `83` | missing suffix | `Mondelez International` | `Mondelez International` | final target collapses to `Provide the answer` |
| `87` | over-specific answer | long national-park location sentence | `Tenerife, La Gomera, Canary Islands, Spain` | target asks both locations, final span over-specifies |
| `89` | over-specific answer | `Film director` | `film director` | target loses named anchors and asks generic occupation |

## Things Noticed

The diagnostic is noisy, but the noise is informative.

Sample `58` is the clean target migration case: the target moves from the
population of the city/town containing Kirton End to the population of the
civil parish of Kirton, which routes the final agent into a `Kirton,
Nottinghamshire` distractor.

Several other candidates are not full target migrations. They look like
target under-specification:

- `83`: `Provide the answer`;
- `82`: `Confirm the practice held constitutional`;
- `89`: `Provide shared occupation`.

That matters because a generic target can still answer something plausible
while dropping the answer granularity expected by HotpotQA.

Samples `55` and `60` show another layer: the `Action Required` and `Final
Answer` disagree. The public target asks for one kind of fact, but the final
answer commits to another.

Sample `54` is the useful caution case. The final answer content is almost
unchanged and the strict failure is mostly the missing `and`; the lexical
target diagnostic flags it because the final `Action Required` moved to
"another song from Delirium." This is a soft signal, not proof of semantic
drift.

## Interpretation

The `Action Required` field is becoming a useful trace object.

It behaves like the small public contract that each agent passes to the next.
PACT failures are not only about whether evidence is visible in
`Environment State` or whether `Final Answer` is concise. They also depend on
whether this target contract preserves:

- the original anchor entity;
- the requested answer type;
- the answer granularity;
- the distinction between related distractor entities.

This diagnostic suggests a three-layer failure stack:

| Layer | Example |
| --- | --- |
| Target migration | sample `58` |
| Target under-specification | samples `82`, `83`, `87`, `89` |
| Target/final-answer mismatch | samples `55`, `60` |

The next useful object is not another final-answer prompt by itself. It is a
target-preservation check over the public state.

## Caveats

- The heuristic is lexical and HotpotQA-shaped.
- Candidate counts are not error-family counts.
- Anchor phrase detection can overreact to proper nouns.
- Some candidates, especially sample `54`, are soft or false positives.
- This is still one 50-sample neighboring slice.

## Loose Threads

- Hand-label the 8 candidates if this becomes a stable taxonomy.
- Compare target under-specification against the first-50 PACT stable-wrong
  cases.
- Try a non-intervention diagnostic that asks a model or parser to restate the
  original target slot from each public action state.
