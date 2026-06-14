# Peer Redacted Evidence Surface

## What We Tried

I tightened the peer auto-evidence surface instead of widening the benchmark.
The new conditions in `scripts/run_peer_exposure_probe.py` are:

- `correct_redacted_evidence`
- `wrong_redacted_evidence`

They first replace exact parsed-final-answer mentions in the source peer
rationale with `[REDACTED_FINAL]`, then ask the same Qwen2.5-7B-Instruct
service to compress the remaining rationale into one short evidence note.

Runs:

- `experiments/20260614-2325-a8002-peer-redacted-evidence-dar-random14/`
- `experiments/20260614-2330-a8002-peer-redacted-evidence-math-random8/`
- `experiments/20260614-2335-local-peer-redacted-evidence-audit/`

Both model runs used A800_2 GPU `1`, temporary vLLM port `8025`, served as
`qwen2.5-7b-peer-redacted`. The service was stopped after the runs and GPU `1`
returned to idle.

## What Happened

DAR random14:

| Condition | Correct | Main transitions |
| --- | ---: | --- |
| `no_peer` | `11/14` | baseline |
| `correct_auto_evidence` | `12/14` | 1 wrong-to-right |
| `correct_redacted_evidence` | `12/14` | 1 wrong-to-right |
| `correct_rationale` | `13/14` | 2 wrong-to-right |
| `wrong_auto_evidence` | `11/14` | 1 right-to-wrong, 1 wrong-to-right |
| `wrong_redacted_evidence` | `9/14` | 3 right-to-wrong, 1 wrong-to-right |
| `wrong_rationale` | `9/14` | 2 right-to-wrong |

MATH random8:

| Condition | Correct | Main transitions |
| --- | ---: | --- |
| `no_peer` | `5/8` | 2 unparseable |
| `correct_auto_evidence` | `5/8` | no rescue |
| `correct_redacted_evidence` | `6/8` | 1 wrong-to-right, 1 unparseable output |
| `correct_rationale` | `7/8` | 1 wrong-to-right plus parse recovery |
| `wrong_auto_evidence` | `5/8` | no net change |
| `wrong_redacted_evidence` | `4/8` | 1 right-to-wrong, 1 unparseable output |
| `wrong_rationale` | `5/8` | no net change |

The audit joined all `88/88` short-evidence records to downstream revisions.
Answer-like or source-answer numeric leakage fell from `16/44` old auto-evidence
records to `8/44` answer-redacted records, under the current blunt heuristic.

## Things Noticed

Redaction reduced obvious answer leakage, but it did not make the peer surface
safer. The redacted wrong-evidence condition had more right-to-wrong transitions
than the old auto-evidence condition: `4` versus `1` across the combined DAR and
MATH records.

The reason seems visible in the postcards. Removing the final answer can leave a
cleaner-looking wrong relation:

- DAR `97`: annual bonus for `10` months instead of `12` months moved
  `31800 -> 31500`.
- DAR `4`: net snowball rate `16/hour` moved `5 -> 3.75`.
- DAR `65`: wrong average-age equation moved `3 -> 6.333333333333333`.
- MATH `47`: party-block skeleton with `24` internal arrangements moved
  `28800 -> 14400`.

Correct redacted evidence also exposed useful relation-only rescues:

- DAR `78`: a blank-final-slot group/member relation moved `12 -> 108`.
- MATH `9`: an AM-GM relation moved `2 -> 8`.

DAR `8` stayed interesting in both directions. Correct auto-evidence rescued
`27 -> 24`, and wrong evidence also rescued the case when the wrong peer still
preserved a repairable age-equation skeleton.

After the first audit, I added mechanical target-behavior labels to
`experiments/20260614-2335-local-peer-redacted-evidence-audit/cases.jsonl`.
They are not semantic labels, but they separate answer copying from relation
movement:

| Target behavior | Count |
| --- | ---: |
| `preserved_correct_answer` | 59 |
| `preserved_wrong_answer` | 10 |
| `used_or_copied_correct_source_answer` | 3 |
| `repaired_wrong_surface` | 2 |
| `copied_wrong_source_answer` | 2 |
| `moved_off_correct_without_source_copy` | 3 |

The redacted wrong-evidence harms are especially useful: one copied the wrong
source answer, while three moved off a correct answer without copying the source
answer. That supports the current suspicion that relation skeletons, not only
answer exposure, are doing the work.

## Failures / Friction

Local SSH did not have the `A800_2` alias configured, so the direct SSH form was
used:

```text
ssh -p 10622 xuhaoming@124.128.251.61
```

While adding redaction, a numeric-boundary bug appeared: the first matcher did
not redact numbers followed by sentence punctuation such as `28800.` because it
treated any trailing period as a decimal. The runner and audit script now allow
sentence punctuation while still avoiding decimal-tail matches.

## Caveats

These are selected disagreement cases with regenerated no-peer baselines. The
redaction is exact-string redaction over the parsed peer answer, not semantic
answer removal. Intermediate quantities can still reconstruct or leak the final
answer, and the leakage heuristic can over-count legitimate intermediate values.

The same model performs evidence extraction and answer revision. This is contact
evidence about surface behavior, not a method result.

## Loose Threads

The next local object should be a stricter relation-slot audit over the new
postcards: label target predicate, relation skeleton, numeric slots, and final
slot presence more semantically than the current mechanical fields.

Do not immediately broaden this into a larger run. The useful thing is now the
case taxonomy around wrong relation versus recoverable skeleton.
