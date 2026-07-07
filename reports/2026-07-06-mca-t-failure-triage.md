# MCA-T failure triage

Date: 2026-07-06

## Run

Remote output:

```text
A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-text-audit-standard-madmm-aligned-qwen25-7b-full/math500-qwen25-7b-instruct-mca-text-audit-all/
```

Configuration from `run_remote.sh`:

- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`
- Benchmark: MATH500, 500 rows
- Initial sampling: `--initial-prompt-style standard-mad`, `--temperature 1.0`, `--max-tokens 4096`
- MCA-T audit: `--cue-k 2`, `--min-change-certificates 2`, `--pool-state-scope all`, `--audit-temperature 0.2`
- Important caveat: this run did not use `--input-records`; it is prompt/config aligned with Standard MAD, not same-initial-pool aligned.

## Aggregate result

Summary:

- Initial majority accuracy: 364/500 = 0.728
- Final accuracy: 357/500 = 0.714
- Accepted changes: 17/500 = 0.034
- Admissible change certificates: 81/1458 = 0.0556
- Transitions: `MaC_to_C=356`, `MaC_to_W=8`, `MaW_to_C=1`, `MaW_to_W=135`
- Correct-majority harm: 8/364 = 0.0220
- Wrong-majority recovery: 1/136 = 0.00735

Pool-state split:

- `collapse`: 279 rows, no accepted changes; accuracy stayed 264/279 = 0.946
- `minority_bearing`: 134 rows, 10 accepted changes; 7 harms and 0 recoveries; accuracy fell 86/134 to 79/134
- `no_majority_conflict`: 87 rows, 7 accepted changes; 1 harm and 1 recovery; accuracy stayed 14/87

## What failed

MCA-T did not fail by changing too often. It failed because it changed rarely, and the rare accepted changes had poor precision.

The audit gate produced 46 rows with at least one admissible-change certificate, 25 rows with at least two, and 17 rows where at least two certificates supported the same normalized alternative answer. Those 17 accepted changes split as:

- 1 useful correction: `MaW_to_C`
- 8 harmful flips: `MaC_to_W`
- 8 wrong-to-wrong flips: `MaW_to_W`

The implementation aggregates certificate votes by normalized alternative answer, and ignores alternatives equal to the initial answer. That aggregation is working as coded. The weak link is certificate validity: `parse_audit_certificate` accepts the model's own `<initial>fail</initial>` and `<alternative>pass</alternative>` labels as proof. There is no external verifier for the calculation.

## Concrete failure modes

1. Correct majority overturned by false audit certificates.

Examples:

- Index 120: gold `even`, initial `even`, final `odd`. Three certificates claimed the odd alternative passes a parity substitution test.
- Index 145: gold `-2`, initial `-2`, final `130496`. Two certificates accepted a Fibonacci-style alternative that is not the target expression value.
- Index 238: gold `-4`, initial `-4`, final `none`. Three certificates claimed the quadratics have no common root, but they do share `-4`.
- Index 323: gold `1/3`, initial `1/3`, final `1/2`. Two certificates used a flawed cyclic-order probability check.
- Index 351: gold `1/16`, initial `1/16`, final `1/8`. Two certificates accepted a wrong cosine-product simplification.

2. Wrong majority usually stayed wrong.

Among 136 initial-wrong rows, only 9 accepted changes occurred, and only one landed on gold. Many wrong rows had either no admissible certificates or only one certificate. Some had multiple certificates, but they supported different wrong answers or the same wrong initial answer, so the aggregator correctly kept the initial answer.

3. Minority-bearing cases are especially dangerous.

`minority_bearing` is where the method should be most valuable, but this run shows 7 harms and 0 recoveries there. The cue/audit pipeline is not distinguishing "minority has a real correction" from "minority supplied a tempting but false check."

4. This is not a vLLM slowness issue.

MCA-T completed in about 3042 seconds and wrote complete records. The observed failure is behavioral/evaluator design: the audit certificate is self-attested by the same model, not independently checked.

## Interpretation

This result should be treated as a diagnostic failure of the current MCA-T audit contract, not as evidence that text metacognitive cues cannot help. The current rule is conservative in rate but not conservative enough in validity: two self-certified reviewers can jointly promote the same hallucinated alternative.

The next MCA-T variant should require externally checkable or cross-agent-independent validation before a change can override a majority, especially in `minority_bearing` cases.
