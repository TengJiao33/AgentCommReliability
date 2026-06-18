# Field-Contract Quarantine External Pressure Test

Date: 2026-06-15

## Purpose

This is an outside collision and pressure test for the current strongest handle:

**field-contract quarantine for public-state communication.**

The goal is not to make the idea sound larger. The goal is to delete weak
claims before they become project mythology.

## Current Internal Result Under Test

Internal anchor:

- `reports/20260615-pact-field-contract-quarantine.md`
- `experiments/20260615-1807-a8002-pact-field-contract-quarantine-qwen25-14b/`
- evidence row: `E-083`

The internal result is real but narrow:

- one model: Qwen2.5-14B-Instruct;
- one saved-field HotpotQA offset50 packet;
- `100` rows, built from `50` samples x `2` PACT source runs;
- best condition so far: EM `0.610`, F1 `0.753`;
- prior fixed controls: hide public target EM `0.590`, freeze question target EM
  `0.580`, original public-state/no-final EM `0.520`.

The behavior to explain:

**The public `Action Required` field is useful only after its authority is
quarantined.**

## Collision Map

| Collision | Source | What It Already Owns | Pressure On Us |
| --- | --- | --- | --- |
| Action-state public communication | [PACT](https://arxiv.org/html/2606.05304v1) | PACT frames MAS communication as a public state-update problem and uses action, state, and result fields. | We cannot claim "structured public state" or "action-state communication" as the idea. |
| Shared verified context | [DeLM](https://arxiv.org/abs/2606.10662) | DeLM uses parallel agents, a shared verified context, a task queue, and compact verified updates. | We cannot claim "shared verified context" broadly. |
| Decision-critical typed context | [Decision-Aware Memory Cards](https://arxiv.org/abs/2606.08151) | CICL scores evidence by action shift, outcome uplift, necessity, and negative-transfer risk, then packs typed memory cards. | We cannot claim "typed context cards" or "decision-aware evidence packaging" broadly. |
| Data flow vs authority | [AgentSecBench](https://arxiv.org/html/2605.26269v1) | It explicitly separates trusted instructions from untrusted observations and says prompt boundaries do not enforce policy projections. | Our public target field should be framed as an authority channel problem, not a prompt-format problem. |
| Trusted query controls flow | [CaMeL](https://arxiv.org/abs/2503.18813) | CaMeL extracts control/data flow from the trusted query so untrusted retrieved data cannot affect program flow. | Our "original question beats public target" rule is a reliability analogue of trusted-root control flow. |
| Provenance-aware decision auditing | [ARGUS](https://arxiv.org/html/2605.03378v1) | ARGUS tracks untrusted context propagation and checks whether decisions are justified by trustworthy evidence before execution. | We need provenance and trust-root language if we keep this direction. |
| Agent security trust boundaries | [Toward Secure LLM Agents](https://arxiv.org/abs/2606.10749) | This survey frames agent security around information flow, delegated authority, persistent state, explicit trust boundaries, privilege control, and provenance-aware state management. | The broad intellectual neighborhood is security/trust-boundary work, not just multi-agent prompting. |
| Context quarantine terminology | [How to Fix Your Context](https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html) | "Context quarantine" already exists as context/thread isolation vocabulary. | Avoid claiming the word "quarantine" as novel; say field-authority quarantine if needed. |
| Certified state trajectories | [State-Centric Decision Process](https://arxiv.org/abs/2605.12755) | SDP turns observations into certified predicate states and evaluates HotpotQA with certified hop findings. | "Certified state" is also occupied; our niche is field-level authority in inter-agent public handoff. |

## What Dies

These claims should be deleted from the live story:

- "We invented structured public state."
- "Typed public state is the big idea."
- "Public state helps if formatted well."
- "Context quarantine" as a generic novelty phrase.
- "Final-answer candidate licensing" as the next near-term intervention.
- "Keep good public targets" as the default route.

PACT already owns the action-state handoff surface. DeLM already owns shared
verified context. Decision-Aware Memory Cards already owns typed
decision-critical evidence packaging. Security work already owns the general
trusted/untrusted channel distinction.

## What Survives

The surviving claim is narrower and harder:

**In public-state multi-agent handoffs, some fields carry authority, not just
information. A downstream agent should not treat an upstream `Action Required`
field as a task contract unless that field is grounded in the original
question/user intent.**

This is not "better prompting." It is an authority-control problem over
public-state fields.

Better name options:

- Field-authority quarantine
- Public-state authority control
- Intent-grounded public-state projection

The current project name can still say "field-contract quarantine," but the
report language should clarify that this means **quarantining field authority**,
not generic context quarantine.

## Strongest External Pressure

The hardest pressure comes from security, not from MAS papers.

AgentSecBench is especially close because it states the exact structural risk:
agents place trusted instructions, retrieved records, and tool observations into
one generative channel, which lets untrusted strings influence responses or
actions unless an enforcing projection closes the channel.

Our packet is the reliability version of that problem:

- trusted root: original HotpotQA question;
- untrusted or partially trusted observation: upstream PACT public state;
- dangerous coordinate: `Action Required`;
- protected object: final short answer span;
- intervention: hide or replace the public target before generation.

That means the next version should be compared against a security-style
projection baseline, not only against PACT-style field visibility baselines.

## Why The Result Still Matters

PACT itself shows that action-state fields matter. Its ablation reports that
removing Action or State hurts HotpotQA interaction performance, and it defines
the public message as Action, State, and Result.

Our run pressures the inside of that field set:

- PACT asks what public fields should be exposed.
- Our result asks which exposed fields are allowed to carry authority.

That is a smaller object than PACT, but it is also a sharper object. It turns a
message-format question into a field-authority question.

## Current Verdict

This is not yet a paper idea.

It is a credible idea embryo if stated narrowly:

> Public-state communication needs authority separation: evidence fields may be
> consumed as data, but target/action fields must be projected back to the
> original user intent before they are allowed to steer downstream generation.

The current result is the strongest project handle because it has:

- a direct upstream collision target: PACT;
- a specific field failure mode: public target drift/over-authority;
- an intervention, not just an audit;
- a positive paired result over the same packet;
- a clear next falsification path.

But the broad story is not safe. External work already occupies most of the
nearby conceptual territory.

## Next Pressure Test

The next experiment should be designed to fail this idea if it is only a slice
artifact.

Required next checks:

1. Remove dependence on the paired target-slot diagnostic.
2. Build a standalone target-authority detector from only the original question
   and current public fields.
3. Add a final-span/granularity verifier for cases like `Fairfax County,
   Virginia`, `John Florence`, and full-sentence answer expansions.
4. Run the same policy on a neighboring HotpotQA slice.
5. Add a security-style projection baseline:
   - trusted root: original question;
   - allowed observations: evidence/result fields;
   - projected authority: question-derived target only;
   - blocked authority: upstream `Action Required`.
6. If it survives, test 2WikiMultiHopQA or MuSiQue before calling it a
   multi-hop public-state protocol.

## One-Sentence Carry Forward

**Do not ask whether public state helps. Ask which public fields are allowed to
carry authority.**
