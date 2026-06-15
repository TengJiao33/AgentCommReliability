# Reading Queue

## Wu Xiaobao Seed Papers

| Priority | Paper | Link | Why It Matters | First Action |
| --- | --- | --- | --- | --- |
| P0 | Multi-Agent Debate with Memory Masking | https://arxiv.org/abs/2603.20215 | Directly studies erroneous memory contamination in multi-agent debate. Has code: https://github.com/HongduanTian/MAD-MM | Paper downloaded; code cloned; short-subset reproduction and first insight report completed. |
| P0 | Context Learning for Multi-Agent Discussion | https://openreview.net/forum?id=EUu8TILWpR | ICLR 2026 paper on dynamically adjusting context during discussion. | Paper card created: `papers/cards/m2cl.md`; next inspect context generator code path. |
| P0 | Benefits and Limitations of Communication in Multi-Agent Reasoning | https://arxiv.org/abs/2510.13903 | Theoretical and empirical analysis of when communication helps or is bottlenecked. | Paper card created: `papers/cards/benefits-limitations-communication.md`; next inspect synthetic task generators. |

## Local Radar Candidates

Source: `D:\develop\ArXiv_Daily_Digest`.

Latest scan: `reports/20260612-multi-agent-frontier-scan.md`.

| Priority | Direction | Paper / Theme | Why It Matters |
| --- | --- | --- | --- |
| P0 | multi-agent-consistency | MOC: Multi-Order Communication in LLM-based Multi-Agent Systems | Multi-order evidence streams and semantic-topological merging; direct follow-up to MAD-MM's message-contamination theme. |
| P0 | multi-agent-consistency | Hear Both Sides / DAR | Diversity-aware message retention; direct follow-up to MAD-MM trace cases where confidence or majority can select the wrong memory. |
| P0 | multi-agent-consistency | PACT: What Should Agents Say? Action-state Communication for Efficient Multi-Agent Systems | Directly tests which intermediate communication surface should be exposed between agents. |
| P0 | multi-agent-consistency | SMADE-IE | Sparse routing plus evidence-driven debate; concrete "debate only when needed" mechanism. |
| P0 | multi-agent-consistency / harness | Dynamic Coordination Strategy Selection for Enterprise Multi-Agent Systems | Selects consensus/debate/synthesis/single-agent by problem class; directly asks when multi-agent is worthwhile. |
| P0 | agent-skills-harness | Monitoring Agentic Systems Before They're Reliable | Gives a monitoring matrix for immature agent systems; useful for our documentation and evaluation standard. |
| P1 | multi-agent-consistency | Cost-Effective Communication: An Auction-based Method for Language Agent Interaction | Treats communication bandwidth as scarce; strong counterpoint to free-for-all debate. |
| P1 | multi-agent-consistency | Demystifying Multi-Agent Debate: The Role of Confidence and Diversity | Paper card created: `papers/cards/demystifying-mad.md`; use as confidence/diversity diagnostic lens. |
| P1 | multi-agent-consistency | The Ringelmann Effect in Multi-Agent LLM Systems | Effective-team-size scaling law; useful theory lens for multi-agent cost/value tradeoffs. |
| P1 | multi-agent-consistency | Seeing Before Agreeing: Aligning Multi-Agent Consensus with Visual Evidence | Evidence-level agreement, not just answer-level agreement; possible multimodal extension. |
| P1 | agent-skills-harness | Tracking the Behavioral Trajectories of Adapting Agents | Measures behavioral drift from skill/memory/config edits; relevant to persistent agent reliability. |
| P1 | agent-skills-harness | SkillHarm | Lifecycle-aware skill poisoning and self-mutation attacks; useful if we pivot to skills/harness safety. |

## Peer Influence / Slot-Surface Pressure Hits

Source: 2026-06-15 outside check after `reports/20260615-peer-slot-control-math12.md`.

| Priority | Paper / Theme | Link | Why It Matters |
| --- | --- | --- | --- |
| P0 | When Identity Skews Debate: Anonymization for Bias-Reduced Multi-Agent Reasoning | https://arxiv.org/html/2510.07517v4 | Separates content influence from source-label influence through identity bias, conformity, and obstinacy; directly useful for adding anonymized/source-randomized controls. |
| P0 | The Cost of Consensus | https://arxiv.org/html/2605.00914v1 | Names sycophantic conformity, contextual fragility, and consensus collapse; strong caution against overclaiming small peer-exposure gains. |
| P0 | Talk Isn't Always Cheap | https://arxiv.org/html/2509.05396v1 | Reports correct-to-incorrect shifts after peer reasoning, adjacent to the slot-control right-to-wrong cases. |
| P0 | Kairos / peer pressure benchmark | https://arxiv.org/html/2508.18321v1 | Uses utility, resistance, and robustness metrics under controlled peer reliability; good metric vocabulary for the next diagnostic packet. |
| P1 | BenchForm / conformity benchmark | https://arxiv.org/html/2501.13381v1 | Provides conformity-oriented protocols and mitigation ideas; useful if the peer-exposure probe becomes a social-influence audit. |
| P1 | Hidden Profile tasks for multi-agent LLMs | https://arxiv.org/html/2505.11556v1 | Theory-grounded distributed-information setting; useful counterpoint to answer-sharing math debate. |
| P1 | Can LLM Agents Really Debate? | https://arxiv.org/html/2511.07784v1 | Process-level debate analysis; asks whether agents identify mistakes, adopt peer suggestions, or just follow majority pressure. |
| P1 | Decentralized MAS with Shared Context | https://arxiv.org/abs/2606.10662 | Recent shared-verified-context design; pressures the slot-surface work toward public-state/verified-update surfaces. |
| P1 | Decision-Aware Memory Cards | https://arxiv.org/abs/2606.08151 | Typed context units and negative-transfer risk are close to evidence-surface selection, even though the domain is tool-using agents rather than debate. |

## Benchmark / Language Alignment

Use this as vocabulary, not as a forced benchmark plan.

| Benchmark Type | Common Benchmarks / Papers | Language To Reuse | Project Alignment |
| --- | --- | --- | --- |
| reasoning / debate | GSM8K, GSM-Hard, MATH, AIME24/25, MMLU-Pro, MMLU-Hard, GPQA, ARC-C, OpenBookQA, HumanEval; MAD-MM; Cost of Consensus | accuracy, token cost, right-to-wrong, wrong-to-right, oracle gap, cost-accuracy tradeoff | MAD-MM/DAR/MOC reproduction; MATH peer-exposure should be called a peer-influence diagnostic on math reasoning cases |
| split-evidence / public-state | HotpotQA, 2WikiMultiHopQA, MuSiQue; PACT | split evidence, action-state handoff, public-state update, evidence grounding, result field | best language for structured handoff and public-state probes |
| distributed information / collective reasoning | HiddenBench / Hidden Profile tasks | distributed information integration, latent information asymmetry, unshared critical information, premature convergence on shared evidence | best pressure if the story becomes "communication is necessary" |
| peer pressure / social influence | KAIROS, Identity Bias / anonymization, BenchForm | utility, resistance, robustness, peer-answer adoption, conformity, obstinacy, source identity bias | current peer-exposure probe should use this metric language |
| agentic workflow / shared context | SWE-bench Verified, LongBench-v2 Multi-Doc QA; DeLM; Decision-Aware Memory Cards | shared verified context, compact verified updates, decision-aware context cards, tokens per resolved task | useful if the project moves from debate probes toward real agent workflows |

## Field-Authority / Public-State Pressure Hits

Source: 2026-06-15 external collision check after
`reports/20260615-pact-field-contract-quarantine.md`.

| Priority | Paper / Theme | Link | Why It Matters |
| --- | --- | --- | --- |
| P0 | PACT: action-state public communication | https://arxiv.org/html/2606.05304v1 | Direct collision. PACT already owns action-state public handoff and the Action/State/Result field surface; our claim must move inside that surface to field authority. |
| P0 | AgentSecBench | https://arxiv.org/html/2605.26269v1 | Strongest language for the problem: common generative channel conflates data flow with authority; prompt annotation is not enforcement. |
| P0 | CaMeL / Defeating Prompt Injections by Design | https://arxiv.org/abs/2503.18813 | Trusted query determines control/data flow; untrusted data cannot affect program flow. Useful analogue for original-question-rooted target projection. |
| P0 | ARGUS | https://arxiv.org/html/2605.03378v1 | Provenance-aware decision auditing; tracks how untrusted context propagates into decisions and checks trustworthy evidence before execution. |
| P0 | Toward Secure LLM Agents | https://arxiv.org/abs/2606.10749 | Broad trust-boundary survey: information flow, delegated authority, persistent state, provenance-aware state management, and multi-agent propagation. |
| P0 | DeLM / shared verified context | https://arxiv.org/abs/2606.10662 | Shared verified context and compact verified updates already occupy the broad shared-context framing. |
| P1 | Decision-Aware Memory Cards | https://arxiv.org/abs/2606.08151 | Typed decision-critical context and negative-transfer risk already occupy much of the typed-card framing. |
| P1 | Context quarantine terminology | https://www.dbreunig.com/2025/06/26/how-to-fix-your-context.html | Terminology collision. Keep "quarantine" only if qualified as field-authority quarantine, not generic context quarantine. |
| P1 | State-Centric Decision Process | https://arxiv.org/abs/2605.12755 | Certified predicate states and HotpotQA certified hop findings pressure any broad "certified state" framing. |

Current naming rule:

- do not call MATH12/MATH200 a general multi-agent communication benchmark;
- call it a peer-influence diagnostic on math reasoning cases;
- reserve stronger communication-necessity language for split-evidence,
  distributed-information, or shared-context settings.
- do not call field-contract quarantine novel as structured public state,
  shared verified context, typed context cards, or generic context quarantine;
  call the surviving object field-authority control inside public-state handoff.


## Reading Card Template

Create one file per paper under `papers/cards/` when reading deeply. Use:

- `papers/cards/_template.md`

## Methodology Note

Use `skills/reproduction-first-research/SKILL.md` when picking up any paper from this queue.

The queue is not a promise of future experiments. It is a shelf of possible objects to touch: code paths, prompt templates, message filtering, stopping conditions, task preprocessing, evaluation scripts, and whatever else becomes visible while reproducing.
