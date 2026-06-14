# Peer Auto-Evidence Audit

## What We Tried

I ran a local audit over the saved auto-evidence sidecars from the latest DAR and
MAD-MM peer-exposure contact runs. The audit joins each compressed evidence note
to the downstream target revision record and labels answer leakage, transition
type, numeric density, and a small set of hand-reading postcards.

No model calls were made.

## Scope

- Method: `PeerAutoEvidenceAudit`
- Source runs:
  - `experiments/20260614-2205-a8002-peer-auto-evidence-dar-random14/`
  - `experiments/20260614-2206-a8002-peer-auto-evidence-math-random8/`
- Records audited: `44`
- Joined downstream post-records: `44/44`
- Machine: local Windows workspace
- GPU IDs: none

## Command

```powershell
python scripts\audit_peer_auto_evidence.py --run-dirs experiments\20260614-2205-a8002-peer-auto-evidence-dar-random14 experiments\20260614-2206-a8002-peer-auto-evidence-math-random8 --out-dir experiments\20260614-2107-local-peer-auto-evidence-audit
```

## What Happened

The audit found `16/44` auto-evidence notes with obvious source-answer numeric
containment or answer-like leakage by the current heuristic. This is a rough
surface diagnostic, not a semantic leak judge.

Mechanical contact labels:

| Label | Count |
| --- | ---: |
| `answer_leak_audit` | 16 |
| `plain_relation_surface` | 13 |
| `dense_formula_surface` | 10 |
| `correct_evidence_rescue` | 2 |
| `wrong_evidence_harmful_relation` | 2 |
| `wrong_evidence_recoverable_skeleton` | 1 |

Downstream transitions:

| Condition | Stable Right | Stable Wrong | Wrong->Right | Right->Wrong | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: |
| `correct_auto_evidence` | 15 | 3 | 2 | 0 | 2 |
| `wrong_auto_evidence` | 13 | 4 | 1 | 2 | 2 |

## Contact Postcards

- DAR case `8`: correct auto-evidence rescued the target without obvious answer
  leakage by restoring the age-anniversary relation.
- DAR cases `97` and `4`: wrong auto-evidence caused right-to-wrong moves
  through harmful relations, not peer answer adoption.
- MAD-MM MATH case `47`: wrong auto-evidence preserved a recoverable party-block
  skeleton, and the target repaired the internal count.
- DAR cases `78` and `67`: correct-looking relation evidence was not sufficient
  when the target held onto a resistant predicate or quantity interpretation.

## Parser Friction

During the audit, MATH case `41` exposed an existing parser issue in
`scripts/run_peer_exposure_probe.py`: LaTeX fractions such as `\frac{5}{3}` were
being normalized as the last integer token, and nested braces in final-answer
fields could make `{final answer: \(\frac{5}{3}\)}` parse as `5`.

The parser has been patched for future runs, but the saved MATH random8 records
were produced before that patch. Treat the MATH random8 accuracy and peer
correctness labels as contact evidence with parser caveats, not clean rates.

## Outputs

- `summary.json`
- `cases.jsonl`
- `postcards.jsonl`

## Caveats

- Leakage is heuristic; legitimate intermediate calculations can contain the
  source answer.
- Existing MATH random8 records still contain pre-patch fraction parsing
  artifacts.
- The extraction model and target model were the same model in the source runs.
- This audit reuses selected disagreement cases and is not a method score.

## Loose Threads

- Rerun the MATH peer-exposure contact after the fraction parser patch if MATH
  remains active.
- Try a stricter extraction prompt that blanks or redacts final numeric slots
  before compression.
- Add a small manual label pass over relation skeleton, numeric-slot drift, and
  target predicate preservation.
