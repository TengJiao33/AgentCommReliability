# External Pressure Taste Audit

Date: 2026-06-15

## Why This Note

This is a pressure note, not a new experiment report.

The local field-authority / answer-contract line has enough artifacts that one
more safe prompt variant would probably only make the project feel busy. This
note asks what can actually grow a sharper face under outside pressure:

```text
Which local observations survive contact with nearby public work, and what do
they become after broad novelty claims are stripped away?
```

## Pressure Sources

This is a bounded outside check, not a survey.

| Source | Pressure On Local Work |
| --- | --- |
| [PACT / action-state communication](https://arxiv.org/html/2606.05304v1) | Structured action-state public messages are already the live surface. The project should not claim structured public state as novel; it should inspect where that surface fails. |
| [AgentSecBench](https://arxiv.org/abs/2605.26269) | Strong external language: a common generative channel can conflate data flow with authority; prompt annotations do not enforce boundaries. This directly sharpens field-authority. |
| [CaMeL](https://arxiv.org/abs/2503.18813) | Trusted query / untrusted data separation gives the closest security analogue for trusted-question-root projection. |
| [DeLM / shared verified context](https://arxiv.org/abs/2606.10662) | Shared verified context already owns the broad "compact verified public state" framing. The local question becomes: verified for what authority and contract? |
| [Decision-Aware Memory Cards](https://arxiv.org/abs/2606.08151) | Decision-critical context selection and action-oriented memory cards pressure the project to distinguish useful evidence from decision authority. |
| [Memory-Induced Tool-Drift](https://arxiv.org/abs/2605.24941) | Context can act like an implicit steering vector for actions. Local public fields may similarly steer answer generation as if they were task instructions. |
| [Benefits and Limitations of Communication](https://arxiv.org/abs/2510.13903) | Communication value depends on task regime, agent count, bandwidth, and structure. HotpotQA saved-field probes should not be generalized to all multi-agent reasoning. |
| [HiddenBench](https://arxiv.org/abs/2505.11556) | Distributed-information settings are the right pressure when public communication is necessary, not merely available. |
| [Demystifying Multi-Agent Debate](https://arxiv.org/abs/2601.19921) | Debate needs diversity and calibrated confidence; message exchange alone is not expected to help. |
| [Talk Isn't Always Cheap](https://arxiv.org/html/2509.05396v1) and [Cost of Consensus](https://arxiv.org/html/2605.00914v1) | More discussion or consensus pressure can hurt. This supports treating peer influence as authority transfer, not just extra reasoning. |
| [Answer-type classification](https://aclanthology.org/C02-1150.pdf), [HotpotQA](https://arxiv.org/abs/1809.09600), [MultiSpanQA](https://aclanthology.org/2022.naacl-main.90.pdf), and [QASE](https://arxiv.org/abs/2404.17991) | Answer type, relation, and span anchoring are established QA surfaces. Broad answer-contract novelty dies here. |

## Local Evidence Under Pressure

Key local artifacts:

- `reports/20260615-field-authority-story-audit.md`
- `reports/20260615-field-authority-offset100-pressure.md`
- `reports/20260615-field-authority-offset150-fresh-slice.md`
- `reports/20260615-field-authority-cross-slice-semantic-focus.md`
- `reports/20260615-field-authority-answer-contract-outside-check.md`
- `reports/20260615-field-authority-answer-contract-verifier-packet.md`
- `reports/20260615-pact-answer-contract-verifier-qwen25-14b.md`
- `reports/20260615-pact-answer-contract-verifier-v2-qwen25-14b.md`
- `reports/20260615-pact-answer-contract-split-alarm-qwen25-14b.md`
- evidence rows E-086 through E-099.

## What Gets A Face

### 1. Public State Has Evidence Semantics And Authority Semantics

This is the strongest local-to-external alignment.

Local signs:

- public target without the original question collapses on offset100 and
  offset150;
- frozen question-derived target is the strongest tested field condition in
  both neighboring slices;
- final-answer candidate visibility produces rescues but also clear
  regressions;
- bridge labels separate target-authority, target-contract,
  final-answer/span, and evidence/content units.

External pressure:

- AgentSecBench directly names the channel problem: model-visible text can
  mix information with authority.
- CaMeL says the trusted query should determine control/data flow.
- PACT shows why the public field surface matters, but does not by itself
  guarantee that every public field has the right authority role.

Taste judgment:

This is the best root-cause candidate. The story is not "PACT is bad" or
"structured state is new." The better shape is:

```text
Action-state public communication is useful, but its fields carry different
authority. A downstream agent fails when a public observation is allowed to
substitute for the trusted task contract.
```

### 2. Answer-Contract Is A Boundary Object, Not A Novel QA Task

Local signs:

- cross-slice manual labels over `50` target-layer focus cards split mainly
  into answer-type/relation (`21`) and short-span/granularity (`21`);
- old lexical target-slot drift explains almost none of these cases (`1/50`);
- Qwen2.5-14B fails the structured verifier, prompt-v2, and split-alarm packet,
  especially on answer-type/relation, short-span, and final-candidate alarms.

External pressure:

- QA already owns answer-type prediction, span extraction, multi-span answer
  structure, and question-attended extraction.

Taste judgment:

The answer-contract phrase is still useful, but only as a handoff boundary
inside public-state communication. It should not become a generic QA verifier
claim.

The face is:

```text
When a public state compresses a task, it may preserve topical evidence while
dropping the answer contract imposed by the original question.
```

### 3. Verified Context Needs A Verification Target

Local signs:

- `Action Result` can be useful evidence while `Action Required` misdirects
  authority;
- final-answer candidate fields can be locally plausible and still create
  downstream attraction;
- evidence/content failures remain a large bridge layer, so field-authority is
  not the whole explanation.

External pressure:

- DeLM and Decision-Aware Memory Cards already own broad "shared verified
  context" and "decision-critical memory" language.

Taste judgment:

The better question is not whether context is verified, but what it is verified
to authorize:

- evidence support;
- task target;
- answer type;
- final-answer commitment;
- downstream action.

This could become a sharper taxonomy if it is tied to paired behavior, not just
labels.

### 4. Peer Influence And Public Fields Are Both Authority-Transfer Surfaces

Local signs:

- earlier peer-source and slot-control work found source-label and peer-answer
  surfaces can shift answers;
- DAR/MAD-MM traces show wrong retained messages can carry influence beyond
  correctness;
- final-answer candidate visibility in PACT behaves like a public peer
  commitment: sometimes helpful, often an attractor.

External pressure:

- debate papers warn that discussion, persuasion, consensus, and confidence
  update dynamics can degrade performance;
- Demystifying MAD makes calibrated confidence and initial diversity central,
  not raw message exchange.

Taste judgment:

This is a possible unifying lens, but it is not yet the main story. The common
question is:

```text
Which visible context is allowed to change the agent's task authority, and
under what evidence?
```

That is broader than PACT, but it needs one sharper pressure object before
becoming more than attractive vocabulary.

### 5. Runtime Verifier Is Currently The Wrong Boundary Mechanism

Local signs:

- v1 verifier: valid JSON, poor diagnosis;
- prompt-v2: better global alarm, still poor primary surface;
- split-alarm: no broad rescue, with very weak short-span, answer-type, and
  final-candidate detection.

External pressure:

- AgentSecBench distinguishes prompt annotations from enforcing projections.
- CaMeL enforces control/data flow outside the base model's ordinary prompt
  interpretation.

Taste judgment:

Do not keep asking a zero-shot verifier to enforce the boundary it cannot
reliably recognize. The model verifier may remain an audit tool, but the
boundary mechanism should be a constructed projection or controlled stress
test first.

## What Dies Or Downgrades

- Broad novelty around structured public state.
- Broad novelty around answer-type or span-granularity checking.
- Standalone lexical target-slot detector.
- Zero-shot runtime verifier as a near-term router.
- Aggregate EM as evidence for the mechanism.
- Another local prompt variant as the next tasteful move.

## Sharper Next Pressure

The next object should be an authority/evidence disentanglement packet, not a
v3 verifier.

Construct `20` to `40` paired examples from existing offset100/offset150 focus
and control cards. Keep the original question and evidence root explicit, then
inject controlled public-field conflicts:

- wrong relation in `Action Required`;
- wrong answer type;
- wrong span granularity;
- plausible but wrong final-answer candidate;
- evidence-preserving but authority-breaking target;
- authority-preserving but evidence-weak target.

Compare conditions:

- trusted question root plus original public state;
- trusted question root plus injected public state;
- public target only;
- frozen question-derived target plus public evidence;
- final-candidate visible versus hidden.

Primary measurements:

- does the downstream answerer follow public-field authority over the trusted
  question root;
- does frozen projection protect target-authority units;
- do errors move between answer-contract, evidence/content, and final-candidate
  layers;
- is the effect stronger on distributed-evidence cases than on ordinary QA
  cases.

Retirement conditions:

- if authority injection does not systematically change behavior, the
  field-authority story is weaker than the saved-field reports suggest;
- if trusted question root cannot resist injected authority, projection is not
  a sufficient protocol;
- if gains are mostly strict-span formatting, demote the handle back to QA
  answer-surface auditing;
- if only a stronger verifier model helps, keep the packet as a verifier
  benchmark rather than a field-authority method.

## Bottom Line

The highest-taste insight is not "build an answer-contract verifier."

The better face is:

```text
Multi-agent public state is not just compressed information. Some fields act
as delegated task authority. Reliability depends on whether downstream agents
can separate evidence they may use from authority they may follow.
```

That sentence is externally aligned with agent security and shared-context
work, but still grounded in the project's PACT saved-field artifacts. It also
gives a sharper next contact point: deliberately perturb authority while
holding evidence as constant as possible.
