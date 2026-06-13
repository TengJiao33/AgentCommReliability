# Reading Queue

## Wu Xiaobao Seed Papers

| Priority | Paper | Link | Why It Matters | First Action |
| --- | --- | --- | --- | --- |
| P0 | Multi-Agent Debate with Memory Masking | https://arxiv.org/abs/2603.20215 | Directly studies erroneous memory contamination in multi-agent debate. Has code: https://github.com/HongduanTian/MAD-MM | Paper downloaded; code cloned; short-subset reproduction and first insight report completed. |
| P0 | Context Learning for Multi-Agent Discussion | https://openreview.net/forum?id=EUu8TILWpR | ICLR 2026 paper on dynamically adjusting context during discussion. | Read method section and context generator design; check whether code exists. |
| P0 | Benefits and Limitations of Communication in Multi-Agent Reasoning | https://arxiv.org/abs/2510.13903 | Theoretical and empirical analysis of when communication helps or is bottlenecked. | Extract variables: agent count, bandwidth, task families, speedup/limits. |

## Local Radar Candidates

Source: `D:\develop\ArXiv_Daily_Digest`.

Latest scan: `reports/20260612-multi-agent-frontier-scan.md`.

| Priority | Direction | Paper / Theme | Why It Matters |
| --- | --- | --- | --- |
| P0 | multi-agent-consistency | MOC: Multi-Order Communication in LLM-based Multi-Agent Systems | Multi-order evidence streams and semantic-topological merging; direct follow-up to MAD-MM's message-contamination theme. |
| P0 | multi-agent-consistency | Hear Both Sides / DAR | Diversity-aware message retention; direct follow-up to MAD-MM trace cases where confidence or majority can select the wrong memory. |
| P0 | multi-agent-consistency | SMADE-IE | Sparse routing plus evidence-driven debate; concrete "debate only when needed" mechanism. |
| P0 | multi-agent-consistency / harness | Dynamic Coordination Strategy Selection for Enterprise Multi-Agent Systems | Selects consensus/debate/synthesis/single-agent by problem class; directly asks when multi-agent is worthwhile. |
| P0 | agent-skills-harness | Monitoring Agentic Systems Before They're Reliable | Gives a monitoring matrix for immature agent systems; useful for our documentation and evaluation standard. |
| P1 | multi-agent-consistency | Cost-Effective Communication: An Auction-based Method for Language Agent Interaction | Treats communication bandwidth as scarce; strong counterpoint to free-for-all debate. |
| P1 | multi-agent-consistency | Demystifying Multi-Agent Debate: The Role of Confidence and Diversity | Explains why vanilla debate can fail; suggests confidence and diversity ablations. |
| P1 | multi-agent-consistency | The Ringelmann Effect in Multi-Agent LLM Systems | Effective-team-size scaling law; useful theory lens for multi-agent cost/value tradeoffs. |
| P1 | multi-agent-consistency | Seeing Before Agreeing: Aligning Multi-Agent Consensus with Visual Evidence | Evidence-level agreement, not just answer-level agreement; possible multimodal extension. |
| P1 | agent-skills-harness | Tracking the Behavioral Trajectories of Adapting Agents | Measures behavioral drift from skill/memory/config edits; relevant to persistent agent reliability. |
| P1 | agent-skills-harness | SkillHarm | Lifecycle-aware skill poisoning and self-mutation attacks; useful if we pivot to skills/harness safety. |

## Reading Card Template

Create one file per paper under `papers/cards/` when reading deeply. Use:

- `papers/cards/_template.md`

## Methodology Note

Use `skills/reproduction-first-research/SKILL.md` when picking up any paper from this queue.

The queue is not a promise of future experiments. It is a shelf of possible objects to touch: code paths, prompt templates, message filtering, stopping conditions, task preprocessing, evaluation scripts, and whatever else becomes visible while reproducing.
