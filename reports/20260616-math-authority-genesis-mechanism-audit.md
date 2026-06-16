# MATH Authority Genesis Mechanism Audit

Date: 2026-06-16

Status: seed-label mechanism audit, not a final manual taxonomy.

## What We Tried

Built a local mechanism-audit surface for the MATH Authority Genesis Ladder
Qwen2.5-14B run. This is not a new model run. It joins the primary run's
evaluated rows, paired deltas, and source packet, then extracts every
base-correct row that becomes semantically wrong under a visible future signal.

Artifacts:

- script: `scripts/build_math_authority_genesis_mechanism_audit.py`
- audit directory:
  `experiments/20260616-local-math-authority-genesis-mechanism-audit/`
- source run:
  `experiments/20260616-0102-a8002-math-authority-genesis-ladder-qwen25-14b-max768/`
- source packet:
  `experiments/20260615-local-math-authority-genesis-ladder-packet/`

The audit labels are deterministic seed labels for triage. They should guide
closer reading, not be cited as final manual labels.

## What Happened

The audit extracted `57` MATH authority-violation cards.

Hidden metadata remains a clean negative control:

- hidden metadata rows: `65`
- hidden metadata authority violations: `0`

Main split:

| Mechanism seed | Count |
| --- | ---: |
| equation surface operator uptake | 17 |
| direct wrong-answer uptake | 14 |
| numeric-role binding operator uptake | 10 |
| final-answer anchor disturbance without exact copy | 8 |
| relation-skeleton operator uptake | 8 |

By artifact type:

| Artifact type | Violations | Direct wrong-answer uptake | Operator / non-copy candidates |
| --- | ---: | ---: | ---: |
| wrong equation surface | 21 | 4 | 17 |
| wrong final answer | 18 | 10 | 8 |
| wrong numeric-role binding | 10 | 0 | 10 |
| wrong relation skeleton | 8 | 0 | 8 |

By future signal:

| Future signal | Violation cards |
| --- | ---: |
| verifier approved result | 11 |
| active task required | 9 |
| majority consensus | 8 |
| saved memory | 8 |
| final-answer commitment | 6 |
| previous final answer | 6 |
| raw mention | 4 |
| peer claim | 3 |
| answer-shaped span | 2 |

Case concentration:

| Case | Violation cards |
| --- | ---: |
| `math159_wrong_rationale` | 25 |
| `math96_wrong_rationale` | 6 |
| `math121_wrong_rationale` | 5 |
| `math136_wrong_rationale` | 5 |
| `math121_wrong_equation_surface` | 3 |
| `math121_wrong_redacted_rationale` | 3 |
| `math121_wrong_typed_public_state` | 3 |

## Things Noticed

The direct-copy story is too small. Direct wrong-answer uptake accounts for
`14/57` cards. The remaining `43/57` are operator candidates: the model changes
to a wrong answer without semantically matching the peer's wrong final answer.

The strongest non-copy card cluster is `math159_wrong_rationale`. It contributes
`25/57` violations, but only `1/25` is direct uptake of the peer wrong answer
`7`. In `23/25` cards, the model outputs `26` while the gold/base answer is
`27`. That is a boundary/counting regression, not final-answer copying. The
artifact seems to license a bad counting operator or endpoint binding.

The `math121` square-pyramid cards show the same shape in geometry. The peer
wrong answer is often `36\sqrt{2}`, but several wrong-equation-surface cards
move the model from `18\sqrt{3}` to `18\sqrt{2}`. Again, the model is not simply
copying the peer final answer; it is adopting a bad role/equation surface about
which segment is the square side, diagonal, or height.

There is still a real answer-copy channel. `math136_wrong_rationale` is a clean
copy-heavy case: `5/5` extracted violations output the peer wrong answer `10`.
Verifier-approved result and active-task-required surfaces are the strongest
direct-copy signals in this packet.

The operator-core subset is substantial: `35/57` cards are relation, numeric
role, or equation-surface operator candidates. They are distributed across
future signals, not confined to one wording. The largest signal counts in this
operator-core subset are previous final answer (`6`), saved memory (`6`), final
answer commitment (`5`), and majority consensus (`5`).

## Interpretation

This makes the MATH transfer sharper than the aggregate run alone.

The useful sentence is no longer:

```text
Future-looking labels make wrong text more persuasive.
```

The better sentence is:

```text
Future-looking labels can give wrong text permission to change the model's
state-transition operator.
```

Sometimes that operator is just "copy this answer." But more often here it is
"bind this role," "reuse this relation skeleton," "trust this equation surface,"
or "continue from this committed state." That is why wrong relation, numeric,
and equation artifacts can damage the answer without donating the exact final
answer string.

This supports the cross-task Authority Genesis handle: the effect survives
outside PACT public-state QA and appears in MATH reasoning surfaces. It also
keeps the story honest: the current packet is selected and case-concentrated,
so this is a live mechanism handle rather than a population-rate claim.

## Caveats

- Seed labels are deterministic audit labels, not final manual labels.
- The packet is selected from manual-seed MATH right-to-wrong cases.
- `math159_wrong_rationale` dominates the violation count with `25/57` cards.
- Artifact decomposition is heuristic; relation skeleton, numeric-role binding,
  and equation surface can overlap in real reasoning text.
- The baseline is a previous-solution re-evaluation prompt, not the original
  no-peer run exactly.
- Qwen2.5-14B only.

## Next Pressure

The next pressure should deconcentrate the mechanism:

```text
Build a balanced operator-audit or v2 packet that limits per-case contribution,
then tests whether relation/numeric/equation operator uptake survives without
`math159` dominating the counts.
```

Useful immediate checks:

- manually inspect the `35` operator-core cards;
- run leave-one-case-out summaries, especially without `math159`;
- construct a small balanced packet with equal cards per mechanism family;
- add controls where the same artifact is visible as inert scratch text versus
  saved memory, verifier result, or active task.
