# ArXiv Digest Pressure Contact

## What This Is

This is a pressure note, not a survey and not a research-plan document.

The goal is to let the local `ArXiv_Daily_Digest` papers disturb our current
reproduction notebook without turning every disturbance into a named idea. The
main question is:

```text
Which variables do these papers make our current traces look blind to?
```

This note should be read next to:

- `reports/_archive/20260616-pruned/20260614-communication-regimes-synthesis.md`
- `reports/_archive/20260616-pruned/20260614-moc-merge-prompt-role-audit.md`
- `docs/comm_trace_schema.md`
- `docs/evidence_register.md`

## Contact Source

Local source:

```text
D:\develop\ArXiv_Daily_Digest
```

Directions touched:

- `multi-agent-consistency`
- `agent-skills-harness`
- `factuality-rule-guided-apps`

This contact used digest metadata, abstracts, extracted fields, and local
weekly/landscape notes. No paper was promoted to a full paper card here.

## Pressure Objects

| Pressure | Papers | What It Makes Us Notice |
| --- | --- | --- |
| Harmful peer exposure | [Easier to Mislead Than to Correct](http://arxiv.org/abs/2606.01637v1); [Not All Flips Are Conformity](http://arxiv.org/abs/2606.00820) | `right_to_wrong` is too flat. A final flip may come from spontaneous instability, majority pressure, authority labels, or reasoning-like persuasion. |
| Consensus can hide misalignment | [The Consistency Illusion](http://arxiv.org/abs/2606.08457v1) | Answer agreement is not enough. We may need to record whether agents agree on evidence roles, predicates, and reasoning anchors. |
| Communication as diffusion risk | [Collective Hallucination in Multi-Agent LLMs](http://arxiv.org/abs/2606.07941); [Modelling Opinion Dynamics at Scale](http://arxiv.org/abs/2606.07487v1) | Multi-agent communication can propagate unsupported claims and social conformity, not just useful evidence. |
| Terminal state is a protocol choice | [Hierarchical Certified Semantic Commitment](http://arxiv.org/abs/2606.07316v1); [FinCom](http://arxiv.org/abs/2606.00939) | The final step should perhaps be typed as `commit`, `disagree`, `abort`, or `needs_evidence`, not forced into one answer string. |
| Harness/context layer matters | [From Model Scaling to System Scaling](http://arxiv.org/abs/2605.26112); [Harness-Bench](http://arxiv.org/abs/2605.27922); [REFLECT](http://arxiv.org/abs/2606.09071v1) | Final prompt, context construction, verification, tracing, and recovery are first-class reliability variables, not implementation details. |
| Decision-critical context | [Decision-Aware Memory Cards](http://arxiv.org/abs/2606.08151v1) | Context compression should be judged by action shift, necessity, and negative-transfer risk, not only by token count or summary fluency. |
| Inference-time control | [Inference-Time Conformal Reasoning](http://arxiv.org/abs/2606.08831v1) | Stopping, abstaining, and coverage-like factuality control may be more relevant than post-hoc cleanup after a bad trajectory. |

## What Moves In Our Local Notebook

### DAR / MAD-MM

Current traces already record `right_to_wrong`, `wrong_to_right`, visible source
agents, and retained/dropped messages. Under this literature pressure, those
events are not enough.

A DAR or MAD-MM flip should be decomposed, when possible, into:

- no-peer self-instability;
- peer answer adoption;
- majority-pressure adoption;
- authority-label adoption;
- reasoning-surface persuasion;
- evidence-grounded correction.

The uncomfortable point is that reducing peer adoption may not improve accuracy
unless we can separate harmful and beneficial influence. That matches our DAR
experience: answer-only and guarded retention helped some right-to-wrong cases,
but sample `20` showed that flattening the retained surface can also remove
useful calculation evidence.

### PACT

PACT's final-answer contract remains the strongest local positive signal, but
the digest makes it look less like a final-answer formatting trick and more like
a terminal-state problem.

Instead of only asking:

```text
Can the final answer be shorter and easier to score?
```

the next PACT contact could ask:

```text
Is the agent ready to commit, disagree, abort, or request more evidence?
```

This is not yet a method. It is a way to touch the successful PACT signal without
pretending that `final answer only` is the research contribution.

### MOC

The MOC role-loss audit should be demoted from "possible main idea" to
"instrument".

Its useful job is to test whether a communication surface preserves the role of
facts relative to the question:

- clue object;
- bridge entity;
- requested relation;
- required qualifier;
- forbidden replacement;
- gold answer.

The new merge audit matters because it shows a summary can preserve source
attribution while still losing role slots. That gives us a reusable microscope
for other communication systems, not a standalone claim about MOC yet.

### Trace Schema

Do not rush a schema bump. For the next contact, it is enough to add these fields
in local experiment notes or sidecar records:

- `peer_exposure_type`: none, answer_only, rationale, evidence, authority_label,
  majority, dissent;
- `pre_exposure_answer`;
- `post_exposure_answer`;
- `flip_source_guess`: instability, conformity, persuasion, evidence_correction,
  parser_surface, unknown;
- `terminal_state`: commit, disagree, abort, needs_evidence, forced_answer;
- `role_preservation`: preserved, lost, conflicted, not_applicable;
- `negative_transfer_risk`: low, medium, high, unknown.

These are sketch fields, not schema commitments.

## Touchable Next Objects

### 1. Peer Exposure Mini-Probe

Use a small slice from an existing object, likely DAR/MAD-MM MATH or GSM8K cases
where first-round answers diverge.

Create controlled second-pass conditions:

- no peer;
- one correct peer answer;
- one wrong peer answer;
- wrong majority;
- authority-labeled wrong peer;
- long confident wrong rationale;
- short evidence-grounded correct peer.

Measure:

- initial answer;
- final answer;
- flip direction;
- harmful vs beneficial revision when gold is known;
- token cost;
- whether the model cites evidence or only echoes the peer answer.

This is the most alive next probe because it directly tests whether
communication is a risk channel.

### 2. Typed Terminal-State Probe

Use a tiny PACT/HotpotQA slice or a synthetic split-evidence slice.

Instead of forcing only a final answer, ask the final agent to emit one of:

- `COMMIT(answer, evidence_anchor)`;
- `DISAGREE(candidates, missing_decision)`;
- `ABORT(reason)`;
- `NEEDS_EVIDENCE(missing_field)`.

Measure:

- strict answer accuracy where it commits;
- abstain/abort rate;
- whether aborts concentrate on genuinely underdetermined or conflicting
  public-state cases;
- whether wrong commits decrease or merely become unscored.

This keeps contact with the successful PACT final-contract result while
separating answer extraction from finality control.

### 3. Role-Loss As Instrument

Do not run a bigger MOC benchmark yet.

Instead, inspect the natural-surface failures from
`experiments/_archive/20260616-pruned/20260614-1913-a8002-moc-merge-prompt-role-audit/` and ask which
role slots were lost before the final answer became wrong.

Possible tiny follow-up:

- one role-preserving natural-language merge surface;
- one no-role-label surface;
- same six cases;
- same lexical audit.

The purpose would be to make the instrument less dependent on artificial labels,
not to claim a new MOC method.

### 4. Harness-Layer Retrospective

Pick a few saved PACT/DAR cases and trace which harness layer moved the outcome:

- message retention;
- recipient context;
- final prompt;
- parser/extractor;
- judge/evaluator;
- public-state overwrite.

This is cheap and may prevent another prompt variant from being mistaken for a
communication result.

## What Not To Claim Yet

- Do not claim role-preserving merge is the paper idea.
- Do not claim PACT final-answer contract is a general method.
- Do not claim communication should always be reduced.
- Do not claim consensus is bad; the sharper claim would be that consensus is an
  unreliable signal unless the influence path is visible.
- Do not treat social-conformity papers as proof about our traces until we run
  a controlled peer-exposure probe.

## Current Felt Direction

The larger object that may be forming is:

```text
LLM-agent communication is not just an information channel.
It is an exposure channel that can correct, persuade, contaminate, or prematurely
commit agents depending on task regime, peer surface, and terminal protocol.
```

The next useful work should therefore touch exposure, silence, disagreement, and
commitment, not just produce another message-compression surface.

