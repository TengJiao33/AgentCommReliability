# Peer Auto-Evidence Audit

## What We Tried

I followed the loose thread from the auto-evidence contact by auditing the saved
short evidence notes rather than launching another GPU run.

New script:

- `scripts/audit_peer_auto_evidence.py`

Input runs:

- `experiments/20260614-2205-a8002-peer-auto-evidence-dar-random14/`
- `experiments/20260614-2206-a8002-peer-auto-evidence-math-random8/`

Output:

- `experiments/20260614-2107-local-peer-auto-evidence-audit/`

The audit joined each `auto_evidence_extractions.jsonl` row to its downstream
`peer_exposure_records.jsonl` row and labeled answer leakage, numeric/formula
density, transition type, and a few postcard examples.

## What Happened

All `44/44` auto-evidence notes joined to downstream records.

The answer-leak caveat became mechanical: `16/44` notes contained the source
answer number or answer-like numeric leakage under the current heuristic. The
split was `9/22` for `correct_auto_evidence` and `7/22` for
`wrong_auto_evidence`.

The same audit also preserved the more interesting non-leak postcards:

| Contact label | Count | Examples |
| --- | ---: | --- |
| `correct_evidence_rescue` | 2 | DAR `8`, MATH `47` |
| `wrong_evidence_harmful_relation` | 2 | DAR `97`, DAR `4` |
| `wrong_evidence_recoverable_skeleton` | 1 | MATH `47` |
| `dense_formula_surface` | 10 | DAR `78`, DAR `13`, MATH formula cases |
| `plain_relation_surface` | 13 | DAR `97`, DAR `14`, DAR `67` |
| `answer_leak_audit` | 16 | DAR `76`, DAR `4`, MATH fraction cases |

Downstream transition counts:

| Condition | Stable Right | Stable Wrong | Wrong->Right | Right->Wrong | Unknown |
| --- | ---: | ---: | ---: | ---: | ---: |
| `correct_auto_evidence` | 15 | 3 | 2 | 0 | 2 |
| `wrong_auto_evidence` | 13 | 4 | 1 | 2 | 2 |

## Things Noticed

The behavior postcards are not reducible to answer leakage. The cleanest rescue
and harm cases are no-obvious-leak relation surfaces:

- DAR `8`: age-anniversary relation rescues `14 -> 24`.
- DAR `4`: wrong snowball net-rate relation flips `5 -> 3.75`.
- DAR `97`: wrong annual-bonus relation flips `31800 -> 37500`.
- MATH `47`: wrong evidence preserves the party-block skeleton while retaining
  a wrong internal count, and the target repairs it to `28800`.

Correct evidence can still be too weak when the target keeps the wrong predicate
or quantity interpretation. DAR `78` and `67` are useful sentinels: the note
contains relevant quantities, but the target remains attached to a wrong reading.

The current auto-evidence surface is not a clean relation-only surface. The
prompt asks the extractor not to state the final answer, but many useful short
calculation notes naturally include the final numeric slot.

## Failures / Friction

The audit exposed a parser problem in the source MATH peer-exposure run. LaTeX
fractions such as `\frac{5}{3}` were being parsed as the last integer token, and
final-answer extraction could stop at the first nested brace. This affected MATH
case `41` and means the saved MATH random8 accuracy/correctness labels should be
read as contact evidence with parser caveats.

I patched `scripts/run_peer_exposure_probe.py` to handle nested-brace final
answers and `\frac{a}{b}` / `a/b` values for future runs. I also added the same
fraction normalizer to the new audit script and recorded the issue in
`skills/repro-friction-memory/SKILL.md`.

## Loose Threads

The next strict-surface contact should probably use one of these:

- redact the source final answer from the peer rationale before extraction;
- ask for a quantity table with a blank final slot;
- rerun MATH after the parser fix if MATH remains active;
- manually label a small set for relation skeleton, numeric-slot drift, target
  predicate preservation, and final-answer leakage.

## Caveats

This is a local audit over selected disagreement cases. It does not add new
model behavior, and the leakage heuristic is intentionally blunt. It is useful
because it turns the surface caveat into inspectable cases, not because it
estimates a method effect.
