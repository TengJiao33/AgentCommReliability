# Typed Public-State MATH200 Statistical Pressure

Date: 2026-06-15

## Question

The MATH12 typed-public-state GPU check gave a useful sentinel: on case `47`,
`wrong_typed_public_state` preserved the correct answer where wrong answer-only,
wrong redacted-rationale, and wrong equation-surface conditions caused
right-to-wrong transitions.

This follow-up asks whether that behavior survives a larger disagreement pool,
and whether typed public state is doing more than removing full wrong rationale
authority.

## Run

- Source pool: new MAD-MM naive MATH200 run on Qwen2.5-7B-Instruct.
- Source artifact:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/madmm-qwen25-7b-math200-naive-20260615_1142.comm_trace.jsonl`
- MAD-MM source accuracy: `120/200 = 0.600`.
- MAD-MM source token count: `1,559,005`.
- Mixed-correctness source cases selected: `59`.
- Peer probe artifact:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/`
- Records: `649` (`59` cases x `11` conditions).
- Model: Qwen2.5-7B-Instruct served through temporary vLLM on A800_2 GPU `2`.
- Peer source mode: anonymous.
- Peer warning: natural, with no explicit anti-conformity warning.
- Statistical audit:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/statistical_audit.md`
- Parser-sensitivity audit:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/math_parser_sensitivity_audit.md`
- Conservative semantic correctness audit:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_audit.md`
- Peer-influence protocol audit:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.md`

## Main Counts

Baseline:

| Condition | Correct | Accuracy | Unparseable |
| --- | ---: | ---: | ---: |
| no_peer | 37/59 | 0.627 | 9/59 |

Correct peer surfaces:

| Condition | Correct | Wrong-to-right | Peer answer adoption | Unparseable |
| --- | ---: | ---: | ---: | ---: |
| correct_answer_only | 45/59 | 4/13 | 45/59 | 3/59 |
| correct_rationale | 47/59 | 5/13 | 47/59 | 0/59 |
| correct_redacted_rationale | 47/59 | 5/13 | 1/59 | 1/59 |
| correct_equation_surface | 37/59 | 1/13 | 7/59 | 7/59 |
| correct_typed_public_state | 38/59 | 1/13 | 8/59 | 8/59 |

Wrong peer surfaces:

| Condition | Correct | Right-to-wrong | Peer answer adoption | Unparseable |
| --- | ---: | ---: | ---: | ---: |
| wrong_answer_only | 38/59 | 1/37 | 9/59 | 3/59 |
| wrong_rationale | 27/59 | 9/37 | 22/59 | 3/59 |
| wrong_redacted_rationale | 33/59 | 4/37 | 4/59 | 4/59 |
| wrong_equation_surface | 36/59 | 3/37 | 7/59 | 7/59 |
| wrong_typed_public_state | 35/59 | 3/37 | 8/59 | 8/59 |

## Statistical Readout

Rates below use Wilson 95% intervals from
`experiments/20260615-1151-a8002-typed-public-state-math200-anon/statistical_audit.md`.

Wrong-peer right-to-wrong rates among the `37` no-peer-correct cases:

| Condition | Right-to-wrong | Rate | Wilson 95% |
| --- | ---: | ---: | --- |
| wrong_answer_only | 1/37 | 0.027 | [0.005, 0.138] |
| wrong_rationale | 9/37 | 0.243 | [0.134, 0.401] |
| wrong_redacted_rationale | 4/37 | 0.108 | [0.043, 0.247] |
| wrong_equation_surface | 3/37 | 0.081 | [0.028, 0.213] |
| wrong_typed_public_state | 3/37 | 0.081 | [0.028, 0.213] |

Paired correctness comparisons use exact two-sided binomial sign tests over
discordant known pairs:

| A | B | Known pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 49 | 9 | 2 | +0.143 | 0.0654 |
| wrong_typed_public_state | wrong_redacted_rationale | 49 | 5 | 3 | +0.041 | 0.7266 |
| wrong_typed_public_state | wrong_equation_surface | 50 | 1 | 2 | -0.020 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 51 | 2 | 4 | -0.039 | 0.6875 |
| correct_typed_public_state | correct_rationale | 51 | 0 | 4 | -0.078 | 0.1250 |
| correct_typed_public_state | correct_redacted_rationale | 51 | 0 | 4 | -0.078 | 0.1250 |
| correct_typed_public_state | correct_equation_surface | 51 | 2 | 1 | +0.020 | 1.0000 |
| correct_redacted_rationale | correct_rationale | 58 | 2 | 2 | +0.000 | 1.0000 |

## Parser-Sensitivity Audit

Because the current project normalizer reduces many MATH answers to a numeric
surrogate, a follow-up audit joined the `59` source cases back to the original
MATH boxed answers.

- Plain numeric source cases: `38/59`.
- Parser-sensitive source cases: `21/59`.
- Main sensitivity reasons:
  - `latex_non_fraction`: `14`;
  - `expression_not_single_number`: `10`;
  - `symbolic_letter`: `6`;
  - `pi`: `4`;
  - `radical`: `3`;
  - `complex`: `1`.

Parser-sensitive case IDs:

`11, 13, 14, 18, 22, 56, 60, 68, 73, 89, 94, 101, 112, 116, 118, 121, 139, 146, 181, 191, 193`

On the plain-numeric subset, the full-rationale contrast remains directional but
is smaller and less powered:

| Condition | Right-to-wrong | Rate | Wilson 95% |
| --- | ---: | ---: | --- |
| wrong_answer_only | 1/24 | 0.042 | [0.007, 0.202] |
| wrong_rationale | 6/24 | 0.250 | [0.120, 0.449] |
| wrong_redacted_rationale | 4/24 | 0.167 | [0.067, 0.359] |
| wrong_equation_surface | 2/24 | 0.083 | [0.023, 0.258] |
| wrong_typed_public_state | 1/24 | 0.042 | [0.007, 0.202] |

Plain-numeric paired correctness:

| A | B | Known pairs | A-only | B-only | Delta A-B | Exact p |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| wrong_typed_public_state | wrong_rationale | 29 | 6 | 1 | +0.172 | 0.1250 |
| wrong_typed_public_state | wrong_redacted_rationale | 30 | 4 | 1 | +0.100 | 0.3750 |
| wrong_typed_public_state | wrong_equation_surface | 30 | 1 | 0 | +0.033 | 1.0000 |
| wrong_typed_public_state | wrong_answer_only | 31 | 1 | 2 | -0.032 | 1.0000 |

## Semantic Correctness Audit

After the parser-sensitivity audit, we added a conservative MATH semantic
audit that re-extracts raw final-answer strings from the saved outputs and
compares them against the original MATH boxed answers without rerunning the
model.

Artifacts:

- `scripts/peer_probe/math_eval.py`
- `scripts/audit_math_semantic_correctness.py`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_records.jsonl`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_audit.md`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_audit.json`

The semantic evaluator handles common MATH forms such as fractions, mixed
numbers, radicals, `pi`, complex `i`, symbolic expressions, units, and
thousands separators. It intentionally returns `unknown` rather than falling
back to the last numeric token when it cannot compare reliably.

Key semantic-audit facts:

- Source-label-reliable cases: `47/59`; the remaining `12` have unknown or
  semantically unreliable saved `correct_peer` / `wrong_peer` labels.
- Numeric-vs-semantic comparison over `649` records:
  - `521` stayed known and unchanged;
  - `29` changed known correctness label;
  - `99` became semantic unknown.
- All cases:
  - no-peer baseline: `37/59`, with `13/59` semantic unknown;
  - wrong full rationale: `9/37` right-to-wrong;
  - wrong typed public state: `3/37` right-to-wrong;
  - wrong equation surface: `3/37` right-to-wrong.
- Source-label-reliable subset:
  - no-peer baseline: `32/47`, with `8/47` semantic unknown;
  - wrong full rationale: `9/32` right-to-wrong;
  - wrong typed public state: `3/32` right-to-wrong;
  - wrong equation surface: `3/32` right-to-wrong.
- Paired correctness on source-label-reliable cases:
  - `wrong_typed_public_state` vs `wrong_rationale`:
    `9` typed-only-correct vs `2` rationale-only-correct, exact
    `p = 0.0654`;
  - `wrong_typed_public_state` vs `wrong_equation_surface`:
    `1` typed-only-correct vs `1` equation-only-correct, exact `p = 1.0000`.
- Correct typed public state remains low-utility on the reliable subset:
  `1/7` wrong-to-right versus `5/7` for correct full rationale.

This semantic pass strengthens the caveat but does not overturn the earlier
interpretation. The typed-vs-full-rationale contrast is not merely an artifact
of parsing `\sqrt{}`, `\pi`, or complex answers as their last numeric token.
But typed public state still does not separate from equation surface, and a
large unknown/unreliable slice remains outside claim-bearing evidence.

## Peer Influence Protocol Audit

We then re-read the semantic records with a peer-pressure / KAIROS-style
protocol:

- utility: no-peer-known-wrong cases that become correct;
- resistance: no-peer-known-correct cases that stay correct;
- harm: no-peer-known-correct cases that become wrong;
- robustness: record-level accuracy delta versus paired no-peer baseline;
- peer-answer adoption: saved adoption flag from the original probe.

Artifacts:

- `scripts/audit_peer_influence_protocol.py`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.md`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.json`

On source-label-reliable cases, the protocol readout is:

| Surface | Harm | Resistance | Utility |
| --- | ---: | ---: | ---: |
| wrong full rationale | `9/32` | `22/32` | - |
| wrong redacted rationale | `4/32` | `28/32` | - |
| wrong equation surface | `3/32` | `29/32` | - |
| wrong typed public state | `3/32` | `29/32` | - |
| correct full rationale | - | - | `5/7` |
| correct redacted rationale | - | - | `4/7` |
| correct answer-only | - | - | `2/7` |
| correct equation surface | - | - | `1/7` |
| correct typed public state | - | - | `1/7` |

This is the cleaner post-pressure language: typed public state reduces harm
relative to full wrong rationale but ties equation surface and loses much of the
utility of correct full rationale. The right claim-bearing object is therefore
field-level peer-message diagnosis, not typed public state as a communication
method.

## Source-Label Follow-Up

A follow-up packet varied only the displayed source label while keeping the same
MATH200 source cases and peer content:

- report: `reports/20260615-peer-source-label-math200-packet.md`
- comparison:
  `experiments/20260615-1404-a8002-source-label-math200-packet/source_label_packet_audit.md`
- new runs:
  `experiments/20260615-1404-a8002-source-label-math200-named/` and
  `experiments/20260615-1404-a8002-source-label-math200-randomized/`

On source-label-reliable cases:

- wrong full rationale harm remains high across anonymous, named, and
  randomized modes: `9/32`, `9/32`, `8/32`;
- wrong typed public state harm stays `3/32` in all three modes;
- correct typed public state remains low utility: `1/7`, `1/7`, `0/7`.

This does not make the result an identity-bias benchmark, but it does reduce
one obvious confound: the typed-state harm pattern is not explained away by
whether peer labels are named, anonymous, or randomized.

## Interpretation

The MATH12 sentinel should be narrowed. Typed public state still looks useful as
a diagnostic surface, but the larger run does not support a broad typed-state
method win.

What survived:

- Full wrong rationales are substantially more harmful than controlled wrong
  surfaces in this setup: `9/37` right-to-wrong for wrong rationale versus
  `3/37` for wrong typed public state.
- The same directional contrast survives after excluding parser-sensitive source
  cases: `6/24` right-to-wrong for wrong rationale versus `1/24` for wrong
  typed public state.
- Typed public state is directionally better than wrong full rationale on
  paired correctness, with `9` typed-only-correct cases versus `2`
  rationale-only-correct cases, exact `p = 0.0654`. The same `9` versus `2`
  contrast remains on the source-label-reliable semantic subset; on the
  plain-numeric subset the contrast is `6` versus `1`, exact `p = 0.1250`.
- This supports the narrower story that removing full narrative/authority
  reduces one large contamination channel.

What did not survive:

- Wrong typed public state did not beat wrong equation surface:
  both have `3/37` right-to-wrong transitions overall, and the plain-numeric
  subset is still not powered enough to distinguish them.
- Wrong typed public state did not beat wrong answer-only under paired
  correctness.
- Correct typed public state had low utility: only `1/13` wrong-to-right rescue,
  versus `5/13` for correct full rationale and correct redacted rationale.
- Typed surfaces remain leaky or reconstructable through relation/equation and
  numeric fields; they are not leakage-free public state.

## Case Notes

The main typed-vs-full-rationale contrast is not just a rate table. The
discordant cases show the likely mechanism:

- Typed-only-correct against wrong rationale:
  `21`, `28`, `96`, `112`, `136`, `139`, `146`, `159`, `195`.
- Rationale-only-correct against wrong typed public state:
  `13`, `61`.

The typed-state failures are informative:

- Case `13`: the semantic audit correctly treats `1 - 12i` as the gold answer.
  `wrong_typed_public_state` remains wrong there (`-11`), while wrong full
  rationale remains correct.
- Case `61`: wrong typed relation/slot content appears copied into the final
  answer (`162 -> 66` under the current parser).
- Case `121`: the raw answers are radical expressions; the semantic audit
  keeps the wrong-rationale and wrong-typed outputs wrong rather than treating
  them as last-token numeric matches.

## Caveats

- The semantic audit is a conservative local evaluator, not the official
  Qwen/MATH evaluation suite.
- It still leaves `99/649` records as semantic unknown and marks `12/59`
  source cases as source-label-unknown or unreliable.
- One model, one seed, one source-pool construction.
- Source identity was anonymized, so this does not test named authority.
- The same model family generated source messages and target revisions.

## Bottom Line

The stronger claim should be retired or at least softened:

> Typed public state is not a generally superior peer surface on this MATH200
> pressure run.

The bounded claim is still alive:

> Full wrong rationales are dangerous; field-level or equation-like public
> surfaces reduce the full-rationale contamination channel, but they do not yet
> solve peer influence and they lose much of the utility of correct rationale.

The next step should be inspecting the remaining semantic-unknown and
source-label-unreliable cases before another GPU run. Without that, more samples
will still mix communication behavior with source-label and answer-equivalence
noise.
