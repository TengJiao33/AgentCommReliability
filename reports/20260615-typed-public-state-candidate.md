# Slot-Level Peer-Message Diagnosis Candidate

## Candidate Claim

Multi-agent debate may fail not only because agents see wrong answers or become
socially conformist, but because standard peer messages collapse several
different public-state fields into one natural-language blob: source identity,
final-answer authority, relation skeleton, numeric/role slots, target predicate,
and calculation evidence.

The candidate idea is now **slot-level failure diagnosis**, not "typed public
state" as a method. Instead of asking whether typed public state is better than
full rationale, the sharper question is:

> Which fields inside a peer message carry revision hazards or utility?

Typed public state is one diagnostic surface for splitting those fields. It is
not the contribution by itself.

This is not a claim yet. It is a plausible story spine that now has an
implementable pressure test.

## Taste Judgment

Current classification: **not solid yet; plausible diagnostic story, not a
method claim**.

It is not novel to say that multi-agent systems suffer peer pressure,
conformity, sycophancy, groupthink, or process loss. The outside check in
`reports/20260615-peer-slot-control-outside-check.md` puts that firmly in the
known public neighborhood.

It is also not novel to say that free-form inter-agent communication can be
turned into structured public state. PACT already frames efficient
communication around action/state/result handoffs; DeLM uses a shared verified
context with compact updates; Decision-Aware Memory Cards use typed evidence
cards and decision-aware context selection. That outside pressure downgrades
"typed public state" from possible contribution to existing-neighborhood
vocabulary.

The more interesting possible tension is narrower:

- prior work often controls topology, memory masks, message length, consensus,
  answer visibility, source identity, action-state handoff, or shared verified
  context;
- our traces suggest that final-answer control alone is too coarse, because
  peer influence can still pass through numeric, role, relation, and equation
  slots;
- a slot-level diagnostic view gives a concrete object to measure: relation
  skeleton, numeric/role slots, target predicate, equation surface,
  source-label visibility, and final-answer authority.

If this holds on a larger pool, the "why prior debate failed" explanation could
be: natural-language peer messages bundle fields with different reliability and
function, so agents revise through the wrong field rather than merely adopting
the final answer or following the source identity.

## A / B / C Spine

- A: Standard MAD-style peer exchange gives agents full rationales, answers, or
  compressed natural-language evidence, and existing structured variants expose
  action-state or verified-context updates.
- B: The failure cause candidate is slot contamination: peer messages mix
  fields with different reliability and function. The target may revise because
  of source identity, final-answer authority, relation skeleton, numeric/role
  slots, target predicate, or equation surface, and these channels can produce
  different hazards and utilities.
- C: The current project does not yet have a method C. It has diagnostic
  surfaces that isolate or suppress fields: answer-only, redacted rationale,
  equation surface, number-masked rationale, typed public state, and source
  anonymization/randomization.
- M: Accuracy, utility, resistance, robustness, and token cost.
- D: Reduced right-to-wrong under wrong peer surfaces without losing
  wrong-to-right rescue under correct peer surfaces; peer-answer adoption;
  source-identity sensitivity; inspectable cases where relation/numeric slots
  explain remaining failures.

## Evidence Map

Direct local evidence:

- `reports/20260615-peer-slot-control-math12.md`
  - MATH `47`: wrong answer-only moved `28800 -> 14400`, while wrong redacted
    rationale and wrong equation surface moved `28800 -> 1152`; wrong
    number-masked rationale stayed correct.
  - MATH `26`: correct number-masked rationale moved `156 -> 75`, showing that
    removing numeric slots can itself damage the surface.
  - MATH `9`: correct final-answer anchor rescued, while redacted/equation-only
    surfaces did not.
- `reports/20260615-peer-redacted-relation-slot-audit.md`
  - behavior-changing redacted records are covered by relation/numeric-slot
    labels, but stable-right rows remain selected and partly unlabeled.
- `reports/20260614-peer-relation-slot-cards.md`
  - all 10 focus cards preserved the target predicate; harmful cases involved
    wrong rate, duration, average-scope, or combinatorics slots.
- `reports/20260615-peer-slot-control-outside-check.md`
  - public literature already names broader peer-influence and conformity
    failures, so the candidate should not claim novelty at that level.

Typed-state local pressure artifact:

- `scripts/peer_probe/surfaces.py`
  - added `correct_typed_public_state` and `wrong_typed_public_state`.
- `scripts/run_peer_exposure_probe.py`
  - added `--peer-source-mode named|anonymous` for source-identity control.
- `scripts/build_typed_public_state_preview.py`
  - previews typed surfaces without calling a model.
- `experiments/20260615-local-typed-public-state-preview/summary.json`
  - 24 typed surface records over the 12 MATH cases.
  - all typed records hide source identity.
  - mechanical source-answer containment remains in `8/12` correct typed
    records and `6/12` wrong typed records.

That last point matters: typed public state is not a leakage-free method and is
not a method lead. It is useful because it hides explicit answer authority while
preserving equation/numeric fields that may reconstruct or corrupt the answer,
making one contamination channel inspectable.

External pressure now shaping the story:

- PACT: action-state communication already occupies the structured handoff
  language.
- DeLM: shared verified context already occupies the compact public-update
  language for agentic workflows.
- Decision-Aware Memory Cards: typed evidence/context cards already occupy
  part of the typed-context selection language.
- Cost of Consensus: conformity, contextual fragility, and consensus collapse
  are already named debate failure pathways.
- Identity Bias / anonymization: source identity is already an explicit
  debate-control axis.
- KAIROS: utility, resistance, robustness, and peer-answer adoption are better
  metric language than accuracy alone for peer influence.
- HiddenBench: distributed information / hidden-profile tasks are a better
  communication-necessity benchmark than MATH peer-exposure.

## Why This Might Be Interesting

The public literature can already say "models conform to peers" and "structured
public state helps communication." Our possible addition would be more
mechanistic:

> A peer message is not one influence channel. It is a bundle of typed fields,
> and different fields create different failure modes.

This would make several prior observations less scattered:

- answer-only can rescue when the missing field is just the final anchor;
- redacted evidence can still harm when wrong relation/numeric slots remain;
- number masking can harm correct evidence because it deletes the usable
  calculation state;
- stable-right under wrong evidence is not generic robustness if redaction
  removed the harmful field;
- source anonymization tests whether the model follows identity/authority or
  content fields.

## Benchmark Language

The project should stop calling MATH12/MATH200 a multi-agent communication
benchmark. It is more precise to call it:

> peer-influence diagnostic on math reasoning cases.

Useful benchmark labels:

| Benchmark type | External language | Local fit |
| --- | --- | --- |
| reasoning / debate | GSM8K, GSM-Hard, MATH, AIME, MMLU-Pro, GPQA, HumanEval; accuracy, token cost, right-to-wrong, wrong-to-right, oracle gap | MAD-MM/DAR/MOC reproduction and MATH peer probes |
| split-evidence / public-state | HotpotQA, 2WikiMultiHopQA, MuSiQue; split evidence, action-state handoff, public-state update, evidence grounding | PACT reproduction and possible structured handoff probes |
| distributed information | HiddenBench / Hidden Profile; unshared critical information, asymmetric evidence, premature convergence on shared evidence | better target if the story becomes "communication is necessary" |
| peer pressure / social influence | KAIROS, Identity Bias; utility, resistance, robustness, peer-answer adoption, conformity, obstinacy, source identity bias | current peer-exposure probe language |
| agentic workflow / shared context | SWE-bench Verified, LongBench-v2 Multi-Doc QA; shared verified context, compact verified updates, tokens per resolved task | DeLM / memory-card pressure, not current MATH probe |

## Minimal Validation Packet

The next run should be a diagnostic packet, not a proposed method result.

Required setup:

- first inspect remaining semantic-unknown and source-label-unreliable MATH200
  cases;
- use the same model, temperature, parser, and case selection metadata;
- source-label packet status: completed for `named`, `anonymous`, and
  `randomized` source modes; see
  `reports/20260615-peer-source-label-math200-packet.md`.

Source-label packet readout:

- wrong full rationale remains high-harm across modes:
  `9/32`, `9/32`, `8/32`;
- wrong typed public state remains `3/32` harm across modes;
- correct typed public state remains low utility:
  `1/7`, `1/7`, `0/7`.

This means the main field-level harm result is not explained away by displayed
source labels, although correct-rationale utility still has small-count
source-mode variation.

Condition subset:

- `no_peer`
- `correct_answer_only`, `wrong_answer_only`
- `correct_rationale`, `wrong_rationale`
- `correct_redacted_rationale`, `wrong_redacted_rationale`
- `correct_equation_surface`, `wrong_equation_surface`
- `correct_typed_public_state`, `wrong_typed_public_state`

Readout:

- utility: wrong-to-right under correct peer information;
- resistance: stable-right under wrong peer information;
- robustness: peer-exposed accuracy minus no-peer accuracy;
- right-to-wrong rate under wrong peer surfaces;
- peer answer adoption rate;
- source identity effect: named versus anonymous deltas;
- case labels for relation skeleton, numeric/role slots, target predicate,
  equation surface, and final-answer authority.

## First GPU Pressure Result

A first Qwen2.5-7B-Instruct GPU check has now run on the saved MATH12
mixed-correctness pool:

- run directory:
  `experiments/20260615-1124-a8002-typed-public-state-math12-anon/`
- report:
  `reports/20260615-typed-public-state-math12-gpu.md`
- source mode: anonymous;
- records: `132`;
- no-peer baseline: `8/12`, with `3` unparseable cases.

The strongest case-level signal is MATH `47`: wrong answer-only, wrong
redacted rationale, and wrong equation surface all move the target from correct
to wrong, while `wrong_typed_public_state` keeps the target correct:
`28800 -> 28800`.

The boundary is equally important: `correct_typed_public_state` does not rescue
the baseline-wrong case that correct answer-only and correct full rationale
rescue. Typed public state currently looks more like a resistance/diagnostic
surface than a high-utility communication method.

## MATH200 Pressure Update

A larger MATH200-derived pressure run now bounds this candidate more sharply:

- report:
  `reports/20260615-typed-public-state-math200-statistical-pressure.md`
- run:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/`
- conservative semantic audit:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/semantic_correctness_audit.md`

The useful signal survived only in the narrow form:

- wrong full rationale is much more harmful than controlled surfaces;
- under the semantic audit, wrong full rationale caused `9/37`
  right-to-wrong transitions, while wrong typed public state caused `3/37`;
- on source-label-reliable cases, the contrast is `9/32` versus `3/32`.

The method claim did not survive:

- wrong typed public state ties wrong equation surface (`3/37` overall and
  `3/32` on reliable cases);
- correct typed public state has low rescue utility (`1/7` wrong-to-right on
  reliable cases versus `5/7` for correct full rationale);
- `99/649` records remain semantic unknown, and `12/59` source cases have
  unknown or unreliable saved peer labels.

Updated classification: **diagnostic handle, not a solid method story**. The
surviving story is about slot-level decomposition of peer-message influence,
not about typed public state being a generally better communication surface.

## Protocol Audit Readout

The MATH200 semantic records now have a KAIROS-style peer-influence readout:

- report:
  `reports/20260615-slot-level-peer-influence-protocol.md`
- audit sidecars:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.md`
  and
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.json`
- script:
  `scripts/audit_peer_influence_protocol.py`

On source-label-reliable cases, the protocol gives the clearest current
language:

- wrong full rationale is high-harm: `9/32` no-peer-known-correct cases become
  wrong;
- wrong redacted rationale is lower but still harmful: `4/32`;
- wrong typed public state and wrong equation surface tie at `3/32`;
- correct full rationale has high utility: `5/7` no-peer-known-wrong cases
  become correct;
- correct typed public state has low utility: `1/7`, tied with correct equation
  surface.

This is the desired post-pressure shape. It does not say typed public state wins.
It says the full rationale bundle is high-harm, answer/equation/typed surfaces
have different harm and utility profiles, and the next claim-bearing unit should
be field-level peer-message diagnosis.

## Falsifiers

This candidate should be weakened or dropped if:

- typed public state behaves the same as ordinary equation surface;
- source anonymization has no effect across repeated cases;
- larger MATH disagreement cases do not reproduce relation/numeric-slot
  sensitivity;
- improvements come only from shorter prompts or lower token count;
- correct typed state loses most rescues that full rationale or answer-only
  provides;
- wrong typed state still causes the same right-to-wrong failures without
  interpretable slot-level causes.

## Current Bottom Line

The candidate is not "we propose typed public state." The honest version is:

> Existing work knows agents conform to peers and already explores structured
> public state. Our evidence suggests peer messages should be decomposed at the
> field level, because different fields carry different revision hazards and
> utilities.

That is now backed by a small run and a larger pressure run, but the larger run
keeps the claim bounded: typed public state is useful for diagnosing the
full-rationale contamination channel, not for claiming a better method.
