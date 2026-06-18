# PACT Qwen2.5-14B HotpotQA Offset50 Paired Run

## What We Tried

Ran a neighboring-slice paired check for PACT on HotpotQA samples `50-99`.

The pair compares:

- baseline PACT action-state communication;
- the same PACT setup with `PACT_FINAL_ANSWER_CONTRACT=1`.

This run tests whether the first-50 final-answer-contract signal survives away
from the inspected first slice.

## Machine

- Host: `A800_2`
- GPU: `7`
- Free memory before launch: about `81149 MiB`
- Work dir: `/data/xuhaoming/yfy/research_workspace/baselines/PACT`
- Timeout: `60m` per run

## Code

- Baseline repo: `https://github.com/iNLP-Lab/PACT`
- Upstream commit: `91acf820f8a69fc7c181120b3120444a98823230`
- Local modifications:
  - `baselines/PACT/upstream/prompts.py`: env-gated final-answer contract.
  - `baselines/PACT/upstream/run.py`: `--start_index`.
  - `baselines/PACT/upstream/data.py`: offset loader that preserves seeded context splitting.
  - `baselines/PACT/upstream/methods/pact.py`: preserves original `sample_index`.
  - `scripts/run_pact_hotpot_smoke_a8002.sh`: logs `PACT_START_INDEX` and passes `--start_index`.
  - `scripts/extract_comm_trace_schema.py`: PACT extractor preserves JSONL `sample_index`.

## Data / Task

- Dataset: HotpotQA dev-distractor
- Data path: `data/hotpot_dev_distractor_v1.json`
- Slice: zero-based samples `50-99`
- Seed: `42`
- Agents/turns: two agents, `4` turns

## Commands

Baseline:

```bash
PACT_MODEL=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
PACT_START_INDEX=50 \
PACT_MAX_SAMPLES=50 \
PACT_TIMEOUT=60m \
PACT_GPU_ID=7 \
PACT_FINAL_ANSWER_CONTRACT=0 \
PACT_RUN_ID=pact-qwen25-14b-hotpot50-offset50-baseline-20260614_1458 \
PACT_OUT_NAME=pact_qwen25_14b_hotpot50_offset50_baseline.jsonl \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_pact_hotpot_smoke_a8002.sh
```

Final-answer contract:

```bash
PACT_MODEL=/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct \
PACT_START_INDEX=50 \
PACT_MAX_SAMPLES=50 \
PACT_TIMEOUT=60m \
PACT_GPU_ID=7 \
PACT_FINAL_ANSWER_CONTRACT=1 \
PACT_RUN_ID=pact-qwen25-14b-hotpot50-offset50-final-contract-20260614_1458 \
PACT_OUT_NAME=pact_qwen25_14b_hotpot50_offset50_final_contract.jsonl \
bash /data/xuhaoming/yfy/research_workspace/scripts/run_pact_hotpot_smoke_a8002.sh
```

## Outputs

| File | Contents |
| --- | --- |
| `pact_qwen25_14b_hotpot50_offset50_baseline.jsonl` | Raw baseline PACT outputs. |
| `pact_qwen25_14b_hotpot50_offset50_final_contract.jsonl` | Raw final-answer-contract PACT outputs. |
| `baseline_run.log` | Remote baseline run log. |
| `contract_run.log` | Remote contract run log. |
| `outer.log` | Paired tmux wrapper log. |
| `comm_trace_pact_offset50_baseline_v11.jsonl` | Baseline unified trace. |
| `comm_trace_pact_offset50_final_contract_v11.jsonl` | Contract unified trace. |
| `analysis_summary.json` | Baseline-vs-contract paired comparison. |
| `changed_cases.jsonl` | One row per sample with transition and token deltas. |
| `baseline_question_aware_summary.json` | Question-aware extraction audit for baseline. |
| `contract_question_aware_summary.json` | Question-aware extraction audit for contract. |
| `contract_public_state_arbitration_summary.json` | Public-state arbitration audit for contract. |
| `case_atlas_summary.json` | Rough mechanical case-label summary. |
| `case_atlas_cases.jsonl` | One atlas row per sample. |
| `case_atlas_focus_cases.jsonl` | Non-stable-right cases for inspection. |
| `public_state_gold_manual_labels.jsonl` | Manual labels for the ten final-public-state gold-string cases. |
| `pact_sample58_drift_packet.json` | Paired turn-level drift packet for the content-regression sentinel. |
| `pact_sample58_drift_packet.md` | Human-readable view of the sample `58` drift packet. |
| `target_slot_drift_summary.json` | Rough target-slot drift summary over non-stable-right focus cases. |
| `target_slot_drift_cases.jsonl` | One target-slot diagnostic row per focus case. |
| `target_slot_drift_candidates.jsonl` | Lexical target-slot drift candidates among focus cases. |
| `target_slot_drift_all_summary.json` | Same diagnostic summary over all 50 paired cases. |
| `target_slot_drift_all_cases.jsonl` | One target-slot diagnostic row per paired case. |
| `target_slot_drift_all_candidates.jsonl` | Lexical target-slot drift candidates among all 50 cases. |

## Result

Both runs completed with `RC=0`.

| Metric | Offset50 baseline | Offset50 final-contract |
| --- | ---: | ---: |
| Exact match | `26/50` | `28/50` |
| Avg F1 | `0.6469` | `0.7427` |
| Avg final-answer words | `7.62` | `2.32` |
| Avg communication tokens | `327.3` | `324.0` |
| Avg total tokens | `4306.6` | `4410.2` |

Case transitions:

| Transition | Count |
| --- | ---: |
| stable right | `22` |
| wrong to right | `6` |
| right to wrong | `4` |
| stable wrong | `18` |

The wrong-to-right cases are samples `57`, `61`, `78`, `85`, `93`, and `99`.
The right-to-wrong cases are samples `54`, `58`, `64`, and `66`.

## Things Noticed

The neighboring slice weakens the first-50 story. The final-answer contract no
longer doubles strict EM; it adds only `2` exact matches.

The signal does not disappear. Average F1 rises by about `0.096`, and final
answers become much shorter. Several rescues are exactly the expected answer
surface failures:

- sample `57`: full sentence -> `Keith Bostic`;
- sample `78`: full sentence -> `British`;
- sample `93`: full sentence -> `No`;
- sample `99`: full sentence -> `No`.

The regressions are also informative. Three of the four right-to-wrong cases
still have high F1 after the contract and mainly fail strict span matching:

- sample `54`: dropped the explicit `and`;
- sample `64`: dropped `countries`;
- sample `66`: added `(IBHOF)`.

Sample `58` is a real content regression: `35,124` becomes `273`.

Question-aware extraction reaches `29/50` on both baseline and contract traces.
For the contract trace, it adds only one rescue over the official output. The
public-state arbitration probes do not reproduce the earlier large ceiling:
guarded final-event arbitration stays at `28/50`, with one rescue and one
regression.

The follow-up case atlas labels the 28 non-stable-right cases as:

- 5 contract-rescued verbose surfaces;
- 1 contract-rescued content or field case;
- 3 strict-span regressions;
- 1 content-drift regression;
- 10 stable-wrong cases where the final public state contains the gold string;
- 1 policy-recoverable public-state case;
- 1 near-miss surface/span case;
- 6 likely evidence or reasoning failures.

Manual inspection of the ten `final_public_state_contains_gold` cases split
them into: 3 missing required token/qualifier cases, 2 wrong answer type or
slot cases, 3 over-specific answers, 1 alias/name-granularity case, and 1
false-positive string signal.

Sample `58` was inspected separately as the one clear content-drift
regression. The variant run still carries the correct `35,124` evidence at
turn `1`, but the public action-state target later migrates from the
population of the city/town in which Kirton End is located to the population
of the civil parish of Kirton. The final answer then selects `273` from the
`Kirton, Nottinghamshire` distractor. The earliest observed divergence is at
turn `1`, before the final-answer-contract prompt applies, so this case is a
stochastic trajectory/target-slot drift sentinel rather than clean causal proof
that the final-turn contract directly produced the wrong number.

A rough lexical target-slot diagnostic over `Action Required` fields flags 8
candidate cases across the focus set: `54`, `55`, `58`, `60`, `82`, `83`,
`87`, and `89`. Running the same diagnostic over all 50 cases returns the same
8 candidates and no stable-right candidates. These are not all true semantic
drifts: sample `54` is mostly a strict-span/surface case. The useful split is
layered: sample `58` is target migration, samples like `82`/`83`/`87`/`89`
look like target under-specification, and samples `55`/`60` show target versus
final-answer mismatch.

## Caveats

- This is a 50-sample neighboring-slice smoke, not benchmark evidence.
- Qwen2.5-14B is not the PACT paper's Qwen3-14B.
- The two runs are paired by slice and seed but executed sequentially.
- The final-answer contract changes generation behavior, not just extraction.
- Some right-to-wrong cases are strict-EM surface regressions rather than fully
  wrong reasoning.

## Loose Threads

- Inspect the `18` stable-wrong cases to separate evidence absence from final
  commitment failure.
- Hand-label the 8 target-slot candidates if the target-preservation axis
  becomes central.
- Treat final-answer contract as a real confound, but not as a standalone
  method.
