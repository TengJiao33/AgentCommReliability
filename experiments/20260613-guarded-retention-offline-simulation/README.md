# 20260613-guarded-retention-offline-simulation

## What We Tried

Ran an offline guarded-retention simulation over existing unified traces from MAD-MM MATH50 and DAR GSM8K100.

No model was rerun. The check asks whether a simple post-filter guard would have changed which first-round messages were retained.

## Scope

- Method families: MAD-MM, DAR
- Model: inherited from source runs, Qwen2.5-7B-Instruct for both traces used here
- Datasets:
  - MAD-MM MATH50 probe
  - DAR GSM8K100 `filter_critical` full-history run
- Samples:
  - MAD-MM: 50 samples x retained methods
  - DAR: 100 samples
- Comparison target: original retained IDs vs guarded retained IDs

## Rule

The simulated guard is a post-filter wrapper:

1. Treat an empty retained set as `reset`.
2. Never keep only unparseable messages when parseable candidates exist.
3. Add one representative from missing parseable answer buckets until the configured cap is reached.
4. Prefer answer diversity over duplicate retained answer buckets when a replacement is needed.

The guard does not use correctness labels. Correctness labels are used only after the fact for audit metrics.

## Command

```powershell
python scripts\simulate_guarded_retention.py `
  --max-retained 3 `
  --trace madmm_math50=experiments\20260613-1855-a8002-madmm-qwen25-7b-math50-probe\comm_trace_madmm_math50.jsonl `
  --trace dar_gsm8k100=experiments\20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory\comm_trace_dar.jsonl `
  --summary-out experiments\20260613-guarded-retention-offline-simulation\summary_max3.json `
  --cases-out experiments\20260613-guarded-retention-offline-simulation\changed_cases_max3.jsonl
```

The same command was also run with `--max-retained 2` as a lower-retention comparison.

## Local Artifacts

- `summary_max3.json`
- `changed_cases_max3.jsonl`
- `summary_max2.json`
- `changed_cases_max2.jsonl`

## What Happened

With `max_retained=3`:

| Trace / Method | Retention Records | Changed By Guard | Recovered Any Correct Message | Right-to-Wrong Cases Recovered |
| --- | ---: | ---: | ---: | ---: |
| DAR `filter_critical` | 100 | 17 | 13 | 2 / 3 |
| MAD-MM objective | 50 | 25 | 1 | 0 / 0 |
| MAD-MM subjective | 50 | 11 | 1 | 0 / 1 |
| MAD naive | 50 | 0 | 0 | 0 / 0 |

Known case behavior:

- DAR `20`: guard adds the dropped correct `Agent1` answer `7`.
- DAR `22`: guard replaces unparseable retained `Agent1` with parseable correct `Agent2` answer `131250`.
- DAR `5`: unchanged because the original filter already retained two correct messages; the failure is downstream generation or parsing, not selection.
- MAD-MM subjective `570`: guard adds dropped correct `Agent3` answer `1152`.
- MAD-MM objective `2965`: guard adds a dropped correct `Agent2` answer `10`, even though the original run still ended correct.

With `max_retained=2`, DAR still recovered 12 cases but missed DAR `20`, because the two originally retained wrong-but-parseable answers already filled the cap.

## Caveats

- This is not an accuracy result; no second-round model responses were regenerated.
- The guard may increase context length and may reintroduce wrong long reasoning.
- The audit uses trace-level normalized answers; MAD-MM official MATH evaluation can differ on a few string-answer cases.
- The result supports a small online variant only if the next run also controls the message surface, for example answer-only or answer-plus-short-rationale retention.

## Loose Threads

- Try a guarded answer-diversity variant as an actual DAR or MAD-MM small run only after deciding whether to retain full reasoning or answer-only snippets.
- Inspect failures like DAR `5` and MAD-MM subjective right-to-wrong `4616` separately; guarded selection does not address those surfaces.
