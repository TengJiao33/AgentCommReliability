# Multi-Agent Frontier Scan

Date: 2026-06-12

Source: `D:\develop\ArXiv_Daily_Digest` after `git pull --ff-only` to commit `8f754e1`.

## Why MAD-MM May Still Matter

My current read: MAD-MM is not important because the method is elegant. It is important because it names a small, reproducible failure mode: in multi-agent debate, wrong peer memory can contaminate later reasoning. That makes it a useful entry point for our project, but probably not the final research object.

The more interesting question for Wu Xiaobao's idea is broader:

- when should agents communicate;
- what should they expose;
- which peer messages deserve trust;
- how do we prevent debate from becoming expensive conformity;
- how do we monitor agent systems before final task accuracy is reliable.

So the next stage should not be full MAD-MM reproduction by default. It should use MAD-MM as a short baseline, then compare it with newer communication/control papers.

## Strongest Candidates

| Priority | Paper | Link | Core Idea | Why It Fits Us | First Action |
| --- | --- | --- | --- | --- | --- |
| P0 | MOC: Multi-Order Communication in LLM-based Multi-Agent Systems | http://arxiv.org/abs/2606.02359v1 | Replace first-order neighbor concatenation with multi-order evidence streams and semantic-topological merging. | Directly attacks information dilution and token cost in agent communication. Good follow-up to MAD-MM. | Download paper and code; inspect prompt/message-merging details before running. |
| P0 | SMADE-IE: Sparse Multi-Agent Framework with Evidence-Driven Debate for Zero-Shot Information Extraction | http://arxiv.org/abs/2606.04691v1 | Route easy cases to global extraction; use type-centric agents and evidence-driven debate only for conflicts. | Gives a concrete "debate only when needed" design. Very aligned with token-cost and reliability. | Read method; check whether debate/evidence scoring can be generalized beyond IE. |
| P0 | Dynamic Coordination Strategy Selection for Enterprise Multi-Agent Systems | http://arxiv.org/abs/2606.00804 | Select consensus/debate/synthesis/single-agent strategy by problem class. | Asks the exact practical question: not "is multi-agent good", but "which coordination mode fits this task". | Read for task taxonomy and routing metrics; likely easier than GPU reproduction. |
| P0 | Monitoring Agentic Systems Before They're Reliable | http://arxiv.org/abs/2606.02494v1 | Monitor quality, suitability, efficiency across within-run, cross-run, and structural scopes; use variance as signal. | Useful as our documentation/evaluation spine. Helps avoid only reporting final accuracy. | Turn its monitoring matrix into our experiment template. |
| P1 | Cost-Effective Communication: An Auction-based Method for Language Agent Interaction | http://arxiv.org/abs/2511.13193 | Treat communication bandwidth as scarce; agents bid to speak based on message value density. | Strong conceptual counterpoint to free-for-all debate. | Read after MOC; compare with sparse communication ideas. |
| P1 | Demystifying Multi-Agent Debate: The Role of Confidence and Diversity | http://arxiv.org/abs/2601.19921 | Debate needs diverse initial answers and calibrated confidence; vanilla homogeneous debate can underperform majority vote. | Gives a clean explanation for why MAD often feels intuitive/crude. | Extract confidence/diversity ablations as baseline dimensions. |
| P1 | The Ringelmann Effect in Multi-Agent LLM Systems | http://arxiv.org/abs/2606.02646 | Effective team size can saturate or collapse as more nominal agents are added. | Useful theory lens for "more agents are not more evidence". | Read for scaling-law variables; maybe no reproduction first. |
| P1 | Seeing Before Agreeing: Aligning Multi-Agent Consensus with Visual Evidence | http://arxiv.org/abs/2605.30698 | Multi-agent VQA consensus should align supporting visual evidence, not just answers. | Good extension of our reliability idea to evidence-level agreement. | Keep as multimodal branch, not first reproduction. |
| P1 | Tracking the Behavioral Trajectories of Adapting Agents | http://arxiv.org/abs/2606.02536v1 | Score skill/memory/config edits as behavior trait shifts. | Strong if Wu Xiaobao's idea touches evolving agent memory or skill files. | Read for "agent update audit" framing. |
| P1 | SkillHarm: Lifecycle-Aware Skill-Based Attacks via Automated Construction | http://arxiv.org/abs/2606.02540v1 | Skill files can be poisoned or self-mutated across an agent lifecycle. | Important safety-adjacent branch for persistent agents. | Read if we pivot toward skills/harness security. |

## What This Suggests

The useful direction is probably not "standard reproduce every multi-agent debate paper". It is:

1. Keep MAD-MM as a cheap baseline and symptom generator.
2. Reproduce or at least inspect one communication-structure paper, likely MOC.
3. Add one "debate should be conditional" paper, likely SMADE-IE or Dynamic Coordination Strategy Selection.
4. Use Monitoring Agentic Systems Before They're Reliable to define our run records:
   - within-run failures;
   - cross-run variance;
   - structural issues such as prompt drift, message bloat, judge instability, and evidence loss.

## Proposed Immediate Next Step

Do one paper-read sprint before more GPU:

- Download/read MOC and SMADE-IE.
- Create paper cards for both.
- Inspect whether either has runnable code and whether the reproduction can be a short CPU/API or one-GPU subset.
- Design a tiny comparison grid:
  - CoT;
  - naive MAD;
  - MAD-MM masking;
  - sparse/conditional communication;
  - confidence/evidence-aware arbitration.

This gives us a better chance of finding "treasure" than burning cards on full standard reproductions too early.
