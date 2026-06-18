# Peer Redacted Evidence Disjoint MATH Pressure

## What We Tried

I tried to pressure the redacted-evidence relation-slot taxonomy with a
neighboring random slice.

First attempt:

- DAR seed `61422`: same 14 cases as before because the saved DAR disagreement
  pool only contains those 14 eligible cases.
- MATH seed `61422`: a partly new case list, but the behavior-changing cards
  were still the old MATH postcards `9` and `47`.

So I dry-ran MATH seeds and selected seed `61502`, which excludes the old
behavior-changing MATH cases `9` and `47`.

Run:

- `experiments/_archive/20260616-pruned/20260615-0028-a8002-peer-redacted-evidence-math-disjoint8/`
- local audit:
  - `experiments/_archive/20260616-pruned/20260615-0034-local-peer-disjoint-math-redacted-audit/`
- case `10` surface packet:
  - `experiments/_archive/20260616-pruned/20260615-0040-local-peer-disjoint-math-case10-surface/`

## What Happened

Disjoint MATH seed `61502` cases:

```text
1, 10, 22, 26, 33, 38, 41, 42
```

Condition summary:

| Condition | Correct | Main transitions |
| --- | ---: | --- |
| `no_peer` | `7/8` | 1 unparseable |
| `correct_auto_evidence` | `6/8` | 1 right-to-wrong |
| `correct_redacted_evidence` | `7/8` | stable-right plus 1 unknown |
| `correct_rationale` | `7/8` | stable-right plus 1 unknown |
| `wrong_auto_evidence` | `6/8` | 1 right-to-wrong |
| `wrong_redacted_evidence` | `7/8` | stable-right plus 1 unknown |
| `wrong_rationale` | `7/8` | stable-right plus 1 unknown |

The local audit shows the surface split cleanly:

| Surface | Records | Right-to-wrong | Stable-right | Unknown |
| --- | ---: | ---: | ---: | ---: |
| `auto_evidence` | `16` | `2` | `12` | `2` |
| `answer_redacted_evidence` | `16` | `0` | `14` | `2` |

## Things Noticed

This is a useful pressure case because it does not simply repeat the earlier
claim that redacted wrong evidence was more harmful.

On this disjoint MATH slice, answer redaction was safer than auto-evidence:
`wrong_redacted_evidence` caused no answer-changing harm, while
`wrong_auto_evidence` caused one right-to-wrong case.

Case `10` shows why:

- `wrong_auto_evidence` explicitly says to simplify to `3`. The target
  recomputes `2`, then defers to the peer's stated value and outputs `3`.
- `wrong_redacted_evidence` removes the explicit wrong final value and leaves
  an algebra route with a blank final slot. The target follows the route to
  `2` and stays correct.

The same case also shows that correct auto-evidence is not automatically safe:
`correct_auto_evidence` compresses the correct peer into a substitution surface
that the target mutates into a sign/denominator error and answers `-2`.

## Caveats

This is only one disjoint MATH8 slice. It does not overturn the earlier
redacted-evidence harm observation; it bounds it. Redaction changes the public
surface. Sometimes it preserves the harmful relation slot; sometimes it removes
the harmful final slot and leaves a repairable route.

The DAR seed did not provide a true neighboring slice because the selected DAR
pool is exhausted at 14 cases.

## Loose Threads

The next useful check is not another DAR seed. If this line stays active, use a
larger or different MATH disagreement pool, or build a deterministic surface
transform that explicitly separates:

- final-answer slot;
- relation skeleton;
- numeric/role slots;
- target predicate.
