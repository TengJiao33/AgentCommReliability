# Guarded Retention Offline Simulation

## What We Tried

I added `scripts/simulate_guarded_retention.py` and ran it over existing unified traces.

The script does not rerun a model. It audits saved first-round retention decisions and simulates a small post-filter guard:

- empty retention becomes explicit `reset`;
- do not keep only unparseable messages when parseable candidates exist;
- add representatives from missing parseable answer buckets up to a cap;
- prefer answer diversity over duplicate retained answer buckets.

Sources:

| Source | Path |
| --- | --- |
| MAD-MM MATH50 trace | `experiments/_archive/20260616-pruned/20260613-1855-a8002-madmm-qwen25-7b-math50-probe/comm_trace_madmm_math50.jsonl` |
| DAR GSM8K100 trace | `experiments/_archive/20260616-pruned/20260613-1730-a8002-dar-filtercritical-gsm8k100-fullhistory/comm_trace_dar.jsonl` |
| Output summary | `experiments/_archive/20260616-pruned/20260613-guarded-retention-offline-simulation/summary_max3.json` |
| Changed cases | `experiments/_archive/20260616-pruned/20260613-guarded-retention-offline-simulation/changed_cases_max3.jsonl` |

## What Happened

With `max_retained=3`, the guard changed 55 retained sets across the two traces.

| Trace / Method | Retention Records | Changed By Guard | Recovered Any Correct Message | Right-to-Wrong Cases Recovered |
| --- | ---: | ---: | ---: | ---: |
| DAR `filter_critical` | 100 | 17 | 13 | 2 / 3 |
| MAD-MM objective | 50 | 25 | 1 | 0 / 0 |
| MAD-MM subjective | 50 | 11 | 1 | 0 / 1 |
| MAD naive | 50 | 0 | 0 | 0 / 0 |

The guard hits the selection failures we expected:

- DAR `20`: original retained `120` and `700`, dropping correct `7`; guard adds the `7` bucket.
- DAR `22`: original retained only an unparseable answer, dropping two parseable correct `131250` answers; guard replaces it with a parseable `131250` representative.
- MAD-MM subjective `570`: original retained wrong `288` and `8`, dropping correct `1152`; guard adds the `1152` bucket.

It also clarifies what the guard cannot solve:

- DAR `5` was already retaining two correct messages, so selection was not the failure surface.
- MAD-MM subjective right-to-wrong `4616` was also not a dropped-correct selection failure in this audit.
- MAD-MM `494` remains a warning that retaining a correct answer plus wrong full reasoning can still end wrong.

## Things Noticed

For DAR, the simple parseable-diversity guard looks locally useful. It recovers a correct retained message in all 13 cases where the original `filter_critical` retained no correct message despite a correct first-round message being available. Two of those are the observed right-to-wrong cases `20` and `22`.

For MAD-MM objective masking, the guard mostly makes the method less sparse: 25 of 50 objective retained sets expand because objective originally keeps exactly one memory. Only one expansion recovers a missing correct message (`2965`), and that run was already final-correct. So this is not obviously a better objective-mask variant unless the message surface is shortened.

For MAD-MM subjective masking, the guard catches the clean dropped-correct-minority case `570`, but it cannot address cases where full retained reasoning lets wrong alternatives dominate.

The `max_retained=2` comparison is weaker for the visible DAR failure: it misses case `20` because two wrong parseable answers already fill the cap. On these three-agent traces, `max_retained=3` is the safer diagnostic rule.

## Caveats

- This is a retention-decision audit, not an accuracy result.
- Correctness labels are used only for after-the-fact audit metrics; the simulated guard itself uses parseability and answer diversity.
- Parseability comes from the existing unified trace normalizer.
- Retaining more buckets may raise token cost and may preserve harmful reasoning. A real run should probably test answer-only or answer-plus-short-rationale retention, not blindly pass full messages forward.

## Loose Threads

- Try an actual small DAR guarded-retention run on GSM8K100 only if the retained message surface is controlled.
- For MAD-MM, compare full-reasoning retention against answer-only retention on the known cases before launching a broader run.
- Keep DAR `5` as a separate parser/continuation failure, not a selection failure.
