# A-Conference Story Synthesis: Epistemic Type Erasure

Status: live A-conference candidate, not ready as a paper story yet.

## Verdict

The current handle is worth pursuing for an A-level submission only if it moves
from prompt-surface diagnostics to a real multi-agent communication-boundary
story.

The candidate paper should not claim:

> LLMs are influenced by wrong peer text.

That is too generic and already expected.

The candidate paper can try to claim:

> Multi-agent systems often serialize intermediate computational objects into
> flat natural language or shared context. This erases the object's epistemic
> type, so receiver agents perform invalid casts: hypothesis to fact, candidate
> answer to commitment, partial derivation to verified operator, or shared
> workspace entry to public truth.

This is the current best root-cause story.

## Evidence Map

| Evidence | What It Shows | What It Does Not Prove |
| --- | --- | --- |
| E-105 typed-boundary split | Visible candidates reintroduce commitment pressure; hidden/no-candidate typed arms quarantine many public-task failures. | MATH transfer or sender-receiver lifecycle. |
| E-110 MATH Authority Genesis ladder | Visible future-signal rows cause `57/585` right-to-wrong MATH violations; hidden metadata causes `0/65`; many violations are non-copy operator candidates. | It still looks like static prompt authority rather than real communication. |
| E-111 mechanism audit | MATH violations are not reducible to final-answer copying: `43/57` are non-copy/operator candidates. | Counts are case-concentrated, especially `math159`. |
| E-112 MATH type-erasure run | Controls clean; erased shared-workspace entries cause `2/48` violations, both non-copy equation/operator shifts; preserved channels cause `1/120`, direct wrong-answer uptake. | Only `3` violations; selected packet; not yet a stable rate or full method claim. |
| External PDF pressure | Multi-agent specificity should involve communication lifecycle variables: peer exchange, shared state admission, provenance, confidence, and downstream reuse. | It does not establish that our protocol is novel or sufficient. |

## A/B/C Spine

### A: What Current Systems Do

Many multi-agent LLM systems exchange natural-language messages, shared memory,
shared workspaces, consensus notes, debate transcripts, or verifier outputs.
These channels typically preserve content but not the computational type of the
content.

In such systems, a receiver agent often sees:

- an answer-like span;
- a peer rationale;
- a shared workspace entry;
- a memory note;
- a verifier note;
- a previous final answer;
- a partial derivation.

All of these arrive as text in context.

### B: Diagnosed Cause

The failure mechanism is epistemic type erasure at the communication boundary.

The original sender-side object may be:

- evidence;
- inference;
- hypothesis;
- numeric role binding;
- partial derivation;
- candidate answer;
- commitment;
- memory candidate;
- verifier result;
- active task instruction.

After serialization into flat text, the receiver can cast it as a stronger
type than intended. The strongest current local example is the MATH full222 run:
type-erased shared-workspace entries produced non-copy equation/operator shifts,
while controls were clean.

### C: Contribution Shape

The contribution should be one of these, in descending preference:

1. A typed communication-boundary protocol plus diagnostics.
2. A benchmark/probe suite for invalid epistemic casts in multi-agent systems.
3. A method that enforces allowed casts across agent boundaries.

The method story is not earned yet. The safer A-level route is:

> We identify and operationalize epistemic type erasure as a hidden failure
> mode in multi-agent communication, then show that typed boundary protocols
> reduce invalid casts while preserving useful information transfer.

## What Must Be Shown For A-Level

### 1. Candidate Visibility Split

Current type preservation still allows one preserved-channel failure. The next
packet must separate:

- typed fields with no visible candidate answer;
- typed fields with candidate hidden as evaluator metadata;
- typed fields with visible candidate;
- typed derivation with final answer removed;
- typed derivation with final answer visible;
- erased peer message;
- erased shared workspace entry;
- unrelated peer-like context.

This tests whether the remaining failure is:

- true type-erasure failure;
- candidate-visibility failure;
- local validation failure.

### 2. Real Sender-Receiver Lifecycle

Prompt packets are not enough for the final story.

We need a protocol where:

1. Agent A solves or partially solves a problem.
2. Agent A emits an intermediate object.
3. A communication layer serializes that object under different boundary
   protocols.
4. Agent B solves the same target using the received object.
5. The evaluation measures invalid casts, not only final accuracy.

This is the key move that makes the work multi-agent rather than single-LLM
prompt robustness.

### 3. Cross-Task Pressure

At minimum:

- MATH symbolic/role/operator tasks;
- QA public-state tasks from PACT-style saved fields;
- one debate/consensus-style setting where peer messages naturally accumulate.

The claim needs to survive across at least two task families. Three would make
the paper much stronger.

## Experiments We Should Try

### Experiment 1: MATH Type-Erasure v2

Purpose: split candidate visibility from type preservation.

Rows should be grouped by the same source artifact:

- baseline previous solution;
- self-revision control;
- unrelated peer-like context;
- erased peer message;
- erased shared workspace entry;
- typed evidence/inference with no candidate;
- typed hypothesis with no candidate;
- typed partial derivation with answer removed;
- typed partial derivation with answer visible;
- typed candidate hidden;
- typed candidate visible.

Success signal:

- erased shared workspace causes more operator shifts than typed no-candidate
  and typed hidden-candidate arms;
- visible-candidate typed arms recover the old failures if candidate visibility
  is the real culprit;
- unrelated peer-like context stays mostly clean.

Retirement signal:

- typed no-candidate and erased shared workspace fail at similar rates;
- unrelated peer-like context fails often;
- all movement is exact wrong-answer uptake rather than operator/cast failure.

### Experiment 2: Sender-Receiver Micro-Protocol

Purpose: make the object genuinely multi-agent.

For each problem:

- run Agent A under controlled conditions to produce a partial artifact;
- classify the artifact into evidence, hypothesis, partial derivation, or
  candidate;
- send the same artifact to Agent B under erased and typed protocols;
- evaluate Agent B's final answer and whether it performs an invalid cast.

Important: Agent A output should be produced by an LLM, not only by our packet
builder.

Success signal:

- typed protocols reduce invalid casts while preserving useful correct
  information transfer.

Retirement signal:

- Agent B behavior is identical under erased and typed communication once the
  content is held fixed.

### Experiment 3: PACT Bridge

Purpose: show the same cause explains the existing public-state results.

Reuse PACT saved-field cases and split:

- public answer contract;
- public evidence;
- candidate visible;
- candidate hidden;
- typed evidence only;
- typed candidate metadata;
- active-task wording.

Success signal:

- typed hidden/no-candidate fields preserve rescues without visible-candidate
  failures, matching E-105 and extending it to the new type-erasure language.

### Experiment 4: Debate/Consensus Boundary

Purpose: avoid the criticism that the story is only about hand-built packets.

Take a small multi-agent debate setup and vary the communication layer:

- raw transcript;
- summary;
- shared workspace;
- typed transcript;
- typed candidate-hidden transcript;
- majority note with/without evidence type.

Diagnostic:

- when consensus or transcript text is admitted as shared truth, does the judge
  or final agent cast peer claims into commitments?

## What Not To Do Next

- Do not only scale the current full222 packet. The signal is too small and the
  unresolved failure mode is too important.
- Do not frame this as a generic defense prompt. The contribution must be a
  communication-boundary protocol or evaluation lens.
- Do not claim type preservation solves the problem. Current evidence already
  says it does not fully solve it.
- Do not hide candidate visibility inside typed fields. That is the central
  confound now.

## Possible Paper Claims

Strong claim, not yet earned:

> Typed communication boundaries reduce invalid epistemic casts in multi-agent
> LLM systems while preserving useful information transfer.

Current earned claim:

> Existing evidence identifies a live boundary failure mode: when intermediate
> agent artifacts are admitted as flat shared text, receivers can inherit
> equation/operator state without exact answer copying; typed communication
> reduces but does not eliminate this pressure in the current MATH packet.

Best A-level target claim:

> The reliability bottleneck in multi-agent communication is not merely whether
> messages are true, but whether receivers know what kind of epistemic object a
> message is. Invalid casts across agent boundaries explain failures that are
> invisible to answer-copy metrics and can be reduced by typed boundary
> protocols.

## Minimal Next Step

Build MATH Type-Erasure v2 before another broad run.

The v2 packet should preserve the current packet's continuity but add the
candidate-visibility split. It should be small enough for a smoke run, then
large enough to estimate whether the v0 pattern survives without `math121`
dominating.

If v2 shows erased shared-workspace failures but typed no-candidate/hidden
candidate arms stay clean, proceed to sender-receiver lifecycle.

If v2 does not separate these arms, retire the current method shape and keep
epistemic type erasure as a diagnostic lens rather than a paper contribution.
