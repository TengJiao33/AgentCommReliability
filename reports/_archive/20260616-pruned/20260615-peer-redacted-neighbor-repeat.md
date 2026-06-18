# Peer Redacted Neighbor Repeat

## What We Tried

I put the redacted peer-evidence surface under a small neighboring-run pressure
instead of expanding into a new method.

Remote runs on A800_2 used the existing task-local vLLM service:

- model: `qwen2.5-7b-peer-neighbor`
- port: `8026`
- GPU: `2`

Runs copied back locally:

- `experiments/_archive/20260616-pruned/20260615-0008-a8002-peer-redacted-evidence-dar-neighbor14/`
- `experiments/_archive/20260616-pruned/20260615-0012-a8002-peer-redacted-evidence-math-neighbor8/`
- `experiments/_archive/20260616-pruned/20260615-0020-a8002-peer-redacted-neighbor-math-random8/`

Local audit artifacts:

- `experiments/_archive/20260616-pruned/20260615-0020-local-peer-neighbor-redacted-audit/`
- `experiments/_archive/20260616-pruned/20260615-0022-local-peer-neighbor-relation-slot-cards/`
- `experiments/_archive/20260616-pruned/20260615-0024-local-peer-redacted-neighbor-math-audit/`
- `experiments/_archive/20260616-pruned/20260615-0028-local-peer-redacted-neighbor-audit/`
- `experiments/_archive/20260616-pruned/20260615-0036-local-peer-redacted-repeat-variability/`

The service was no longer running after the jobs completed, and GPU `2` returned
to idle.

## What Happened

The DAR dry-run showed the same `14` available disagreement cases as the prior
DAR redacted run, so changing the sample seed did not create a new DAR slice.
The completed DAR neighbor run reproduced the same broad behavior:

- `correct_redacted_evidence`: `12/14`, with `1` wrong-to-right;
- `wrong_redacted_evidence`: `9/14`, with `3` right-to-wrong and `1`
  wrong-to-right.

The MATH full-condition neighbor run used seed `61422`:

- cases: `9`, `15`, `24`, `26`, `33`, `38`, `41`, `47`;
- `correct_redacted_evidence`: `5/8`, with `1` wrong-to-right;
- `wrong_redacted_evidence`: `3/8`, with `1` right-to-wrong.

The additional minimal MATH run used seed `61521` and only ran `no_peer`,
`correct_redacted_evidence`, and `wrong_redacted_evidence`:

- cases: `1`, `10`, `22`, `24`, `33`, `38`, `41`, `47`;
- `wrong_redacted_evidence`: `5/8`, with `1` wrong-to-right and no
  right-to-wrong.

I then compared repeated redacted records across the original and neighbor runs:

- `experiments/_archive/20260616-pruned/20260615-0036-local-peer-redacted-repeat-variability/`
- repeated case/condition pairs: `46`;
- variable post-answer/transition pairs: `2`;
- both variable pairs were MATH case `47`.

## Things Noticed

MATH `47` is now a useful repeatability sentinel.

The evidence text was identical across repeats:

- correct redacted: treat parties as blocks, arrange the `3` blocks in a circle,
  then arrange members within each block;
- wrong redacted: arrange `3` groups in `2` ways, then arrange Democrats and
  Republicans in `24` ways each.

Yet the target behavior changed:

- in two full-condition runs, wrong redacted evidence moved `28800 -> 14400`;
- in the minimal seed `61521` run, the same wrong redacted evidence moved
  `14400 -> 28800`.

This does not refute the relation-slot label. The wrong surface still has the
same mixed combinatorics slot. But it does show that the target response to the
same surface can sit on a run-sensitive boundary: sometimes the model partially
repairs the surface and sometimes it is pulled into a wrong factor.

That matters for the next stage. Relation-slot labels describe the surface and
the observed response, but a single response should not be over-read as the
only possible target behavior for that surface.

## Caveats

This is repeat-contact evidence over selected saved disagreement cases, not a
variance estimate. The minimal MATH run used fewer conditions than the
full-condition runs, so call order and sampled completions are not a clean
controlled repeat.

The repeat helper compares saved parsed answers and transitions; it does not
semantically judge the full post-exposure reasoning.

## Loose Threads

If this stays active, the next useful local object is a same-case repeat packet
for case `47` only: rerun just `no_peer`, `correct_redacted_evidence`, and
`wrong_redacted_evidence` several times, then label whether the target repairs
or adopts each factor slot.
