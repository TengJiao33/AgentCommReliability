# MAD-MM Trace-Level Message Retention Analysis

## Short Answer

The MAD-MM short subset exposes a concrete communication-reliability problem: a memory filter can reduce context cost while still selecting the wrong message when confidence is misaligned with correctness.

This is short-subset evidence only. The report records trace observations and defines a follow-up check for disagreement-aware message retention.

## Scope

- Method family: MAD naive, MAD-MM objective masking, MAD-MM subjective masking
- Model: `qwen2.5-14b`
- Dataset: `gsm8k`
- Seed: `41`
- Samples: `100`
- Evidence level: Level 3, short-subset trace evidence

## Sources

| Source | Type | Path |
| --- | --- | --- |
| short subset run note | run record | `experiments/_archive/20260616-pruned/20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset/README.md` |
| metric summary | generated summary | `experiments/_archive/20260616-pruned/20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset/analysis_short_subset_summary.json` |
| trace case summary | generated summary | `experiments/_archive/20260616-pruned/20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset/trace_cases_summary.json` |
| trace extractor | script | `scripts/extract_madmm_trace_cases.py` |
| objective masking code path | implementation | `baselines/MAD-MM/src/reasoning_models.py` |
| confidence score code path | implementation | `baselines/MAD-MM/src/models.py` |

## Results

Initial first-round answer correctness distribution:

| Correct agents in round 1 | Cases |
| ---: | ---: |
| 3 / 3 | 90 |
| 2 / 3 | 5 |
| 1 / 3 | 2 |
| 0 / 3 | 3 |

Mask behavior:

| Method | Kept memories | Kept correct | Kept wrong | Dropped correct | Dropped wrong |
| --- | ---: | ---: | ---: | ---: | ---: |
| objective | 100 / 300 | 95 | 5 | 187 | 13 |
| subjective | 296 / 300 | 280 | 16 | 2 | 2 |

## Observations

Case `335`: CoT predicted `250`; round 1 debate had answers `[250, 310, 310]`; all debate variants ended at `310`, the ground truth. Objective masking kept only the third memory and still ended correctly.

Case `562`: CoT predicted `140`; round 1 debate had `[140, 82, 82]`; all debate variants ended at `82`, the ground truth. Objective masking kept one correct memory.

Case `214` shows a concrete objective-masking regression. Round 1 debate had `[8, 8, 24]`, where `8` is correct. Objective masking kept `[False, False, True]`, exposing only the wrong `24` memory to round 2. All three round 2 agents then answered `24`. Naive and subjective masking both ended at `8`.

Case `1227` shows the minority-correct problem. Round 1 debate had `[5, 5, 66]`, where `66` is correct. Naive debate kept all messages but still collapsed to the majority wrong answer `5`. Objective masking kept only the second wrong memory. Subjective masking dropped the one correct memory and kept the two wrong memories.

The implementation detail matters: `src/models.py` labels the score as `perplexity`, but computes `exp(mean(logprob))`, so larger is higher average token likelihood. Objective masking in `src/reasoning_models.py` sorts these scores descending, sets a median threshold, and keeps entries where `score > threshold`. With three agents, this keeps exactly one memory.

## Follow-Up Criterion

The trace creates a measurable follow-up question: when first-round agents disagree, which retention rule preserves correct minority or dissenting evidence without retaining every message?

Observed failure modes in this subset:

- majority support can be wrong;
- model-likelihood-based selection can keep a wrong answer;
- LLM subjective judging can keep nearly all messages or discard a correct minority message;
- full-memory debate can still collapse to a wrong majority.

DAR is a candidate follow-up because its paper and code define `filter_critical`, a retention rule intended to keep messages that challenge or diversify consensus. This does not imply that DAR solves the MAD-MM failure cases; it only makes the comparison testable.

## Caveats

- This uses one model, one dataset, one seed, and 100 examples.
- The trace summary does not prove DAR will solve these cases.
- The raw result JSON was copied locally for analysis, but large raw artifacts should remain treated as run outputs rather than central documentation.

## Next Small Check

Create a DAR paper card, inspect the code path for `filter_critical`, and run a bounded short reproduction on `arithmetics` first. If setup is clean, run the same short matrix on `gsm8k` and compare retained-message traces against MAD-MM objective masking.
