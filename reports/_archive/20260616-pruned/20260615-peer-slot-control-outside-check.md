# Peer Slot-Control Outside Check

## Why This Check

After the MATH12 slot-control run, the tempting story is that peer influence is
not only final-answer leakage. The project skill says to check public names and
nearby work before naming a mechanism, so this note keeps the claim bounded.

Local artifacts:

- `reports/_archive/20260616-pruned/20260615-peer-slot-control-math12.md`
- `experiments/_archive/20260616-pruned/20260615-1010-a8002-peer-slot-control-math12/summary.json`
- `experiments/_archive/20260616-pruned/20260615-1010-a8002-peer-slot-control-math12/slot_transition_cards.jsonl`
- evidence row `E-065`

## Useful Outside Hits

The closest public vocabulary is already about peer influence, conformity,
sycophancy, groupthink, contextual fragility, hidden-profile information
integration, and process-level debate analysis.

Direct pressure papers:

- [When Identity Skews Debate: Anonymization for Bias-Reduced Multi-Agent Reasoning](https://arxiv.org/html/2510.07517v4)
  frames multi-agent debate failures through identity bias, conformity, and
  obstinacy; it suggests separating content influence from source-label
  influence.
- [The Cost of Consensus: Isolated Self-Correction Prevails Over Unguided Homogeneous Multi-Agent Debate](https://arxiv.org/html/2605.00914v1)
  names sycophantic conformity, contextual fragility, and consensus collapse as
  debate failure pathways; this is a close warning against overclaiming small
  peer-exposure effects.
- [Talk Isn't Always Cheap: Understanding Failure Modes in Multi-Agent Debate](https://arxiv.org/html/2509.05396v1)
  reports correct-to-incorrect shifts after agents see peer reasoning, which is
  directly adjacent to our right-to-wrong slot-control cases.
- [LLMs Can't Handle Peer Pressure: Crumbling under Multi-Agent Social Interactions](https://arxiv.org/html/2508.18321v1)
  uses accuracy, utility, resistance, and robustness under controlled peer
  reliability/social influence; these metrics fit the next peer-exposure audit
  better than accuracy alone.
- [Do as We Do, Not as You Think: the Conformity of Large Language Models](https://arxiv.org/html/2501.13381v1)
  provides conformity-oriented benchmark framing and mitigation ideas such as
  stronger personas and reflection.
- [Assessing Collective Reasoning in Multi-Agent LLMs via Hidden Profile Tasks](https://arxiv.org/html/2505.11556v1)
  gives a theory-grounded distributed-information testbed where communication
  succeeds only if agents integrate unshared critical information.
- [Can LLM Agents Really Debate? A Controlled Study of Multi-Agent Debate in Logical Reasoning](https://arxiv.org/html/2511.07784v1)
  emphasizes process-level debate behaviors, including majority pressure and
  whether agents identify mistakes or adopt peer suggestions.

Radar/context-surface hits:

- [PACT: What Should Agents Say? Action-state Communication for Efficient Multi-Agent Systems](https://arxiv.org/html/2606.05304v1)
  is the strongest pressure against claiming "typed public state" as novelty:
  it already treats inter-agent communication as structured action/state/result
  handoff and evaluates performance-cost tradeoffs.
- [Decentralized Multi-Agent Systems with Shared Context](https://arxiv.org/abs/2606.10662)
  uses a shared verified context with compact updates; this pressures our
  "what should be visible" question toward verified public-state surfaces.
- [Decision-Aware Memory Cards](https://arxiv.org/abs/2606.08151)
  is not a debate paper, but its typed memory-card and negative-transfer framing
  is close to our evidence-surface selection question.
- [Beyond Tokens: A Unified Framework for Latent Communication in LLM-based Multi-Agent Systems](https://arxiv.org/html/2606.05711v2)
  is mostly a taxonomy, but it reminds us that natural-language slot surfaces
  are one communication substrate among many.

## What This Does To The Story

Classification: not ready as a paper story.

The current slot-control observation is not novel by itself. It sits inside a
known public neighborhood: conformity, peer pressure, sycophancy, and debate
process loss. What may be useful is a narrower diagnostic handle: when the
source answer is controlled or blanked, peer influence can still move through
numeric, role, equation, or relation slots.

The larger "typed public state" language is also already occupied. PACT,
DeLM/shared context, and Decision-Aware Memory Cards all pressure us away from
claiming structured public state as the contribution. Typed public state should
therefore remain a diagnostic surface in this project, not the method story.

The surviving possible story is narrower:

> Existing work knows that agents conform to peers; our evidence suggests the
> peer message should be decomposed at field level, because different fields
> carry different revision hazards and utilities.

That handle is not yet a solid root-cause story because:

- the MATH pool has only 12 mixed-correctness cases;
- slot transforms are heuristic and sometimes unnatural;
- source identity, call order, and repeated-generation variance are not
  isolated;
- we have not shown that a proposed surface reduces the diagnosed failure mode
  on a broader sample.

## Benchmark Language

We should be careful about benchmark naming:

| Benchmark type | External language | How to describe our current artifacts |
| --- | --- | --- |
| reasoning / debate | GSM8K, GSM-Hard, MATH, AIME, MMLU-Pro, GPQA, HumanEval; accuracy, token cost, right-to-wrong, wrong-to-right, oracle gap | MAD-MM/DAR/MOC reproduction; MATH peer-exposure is a reasoning-case diagnostic, not a full communication benchmark |
| split-evidence / public-state | HotpotQA, 2WikiMultiHopQA, MuSiQue; split evidence, action-state handoff, public-state update, evidence grounding | PACT-style communication surfaces and public-state handoff probes |
| distributed information | HiddenBench / Hidden Profile; asymmetric evidence, unshared critical information, premature convergence on shared evidence | best future pressure if we want to test whether communication is necessary |
| peer pressure / social influence | KAIROS, Identity Bias; utility, resistance, robustness, peer-answer adoption, conformity, obstinacy, source identity bias | current peer-exposure probe should use this language |
| agentic workflow / shared context | SWE-bench Verified, LongBench-v2 Multi-Doc QA; shared verified context, compact verified updates, tokens per resolved task | DeLM/memory-card pressure if the project moves toward real agent workflows |

Short internal naming rule:

- MATH12/MATH200: peer-influence diagnostic on math reasoning cases.
- HotpotQA/2Wiki/MuSiQue: split-evidence public-state handoff setting.
- HiddenBench: distributed-information integration setting.
- KAIROS/Identity Bias: source/content peer-pressure setting.

## Next Contact Point

Before adding another hand-designed surface, inspect the semantic-unknown and
source-label-unreliable MATH200 cases, then keep the evaluation closer to the
public pressure vocabulary:

- utility: wrong-to-right under correct peer information;
- resistance: stable-right under wrong or misleading peer information;
- robustness: accuracy shift between no-peer and peer-exposed settings;
- content/source split: same content with source labels removed or randomized;
- surface split: final answer, relation/numeric slots, equation-bearing lines,
  and full rationale.

The smallest useful next run is not a new method. It is either a source/content
disentanglement packet over already-cleaned peer-exposure cases, or a move to a
split-evidence / distributed-information benchmark where communication is
actually needed.
