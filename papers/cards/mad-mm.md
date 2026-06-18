# Multi-Agent Debate with Memory Masking

## Link

- arXiv: https://arxiv.org/abs/2603.20215
- PDF: `papers/mad-mm/2603.20215.pdf`
- Code: https://github.com/HongduanTian/MAD-MM

## Bibliographic Info

- Title: Multi-Agent Debate with Memory Masking
- Authors: Hongduan Tian, Xiao Feng, Ziyuan Zhao, Xiangyu Zhu, Rolan Yan, Bo Han
- Venue/comment: ICLR 2026
- Submitted: 2026-03-03
- arXiv ID: `2603.20215`

## One-Sentence Claim

Multi-agent debate can be harmed by erroneous memories from previous debate rounds, and memory masking can improve robustness by pruning unhelpful prior memories before the next round.

## What We Are Reproducing

We are currently reproducing a bounded slice of the paper's reasoning experiments:

- task: `GSM8K`
- model: `Qwen2.5-14B-Instruct` from local A800_2 model storage
- seed: `41`
- samples: upstream default `100`
- methods:
  - CoT baseline
  - MAD baseline with naive full-memory communication
  - MAD-M^2 subjective memory masking
  - MAD-M^2 objective memory masking

This is not yet a full paper reproduction. It is a short-subset reproduction designed to expose communication reliability phenomena.

## Method

The paper frames each agent's previous debate response as memory. Before later debate rounds, MAD-M^2 masks memories judged likely to be erroneous or less useful.

The released code exposes three relevant communication strategies:

- `naive`: keep all previous agent memories.
- `subjective`: ask the model to judge which memories to keep.
- `objective`: use perplexity-based pruning.

## Main Idea In Detail

The paper argues that MAD is not just "more agents = better reasoning." In standard multi-agent debate, every agent in later rounds reads previous agents' responses as context. Those responses can be useful references, but they can also be wrong memories. Once wrong memories enter the context, later agents may copy, rationalize, or be misled by them.

The authors model this as a memory-quality problem. CoT-SC samples several independent answers and votes. MAD also samples multiple reasoning paths, but later paths are not independent because they are conditioned on previous memories. Therefore, MAD's final performance depends not only on the base model's ability but also on how many previous memories are erroneous.

The proposed fix is MAD-M^2: before each later debate round, evaluate the previous memories and mask the potentially wrong ones. Agents then reason with only the retained memories.

## Algorithm Sketch

1. Initial debate round:
   - Each of `N_a` agents independently solves the question.
   - Their responses become the first memory set.

2. Evaluation and masking:
   - Previous responses are evaluated.
   - A binary mask is generated over memories.
   - Masked-out memories are removed from the next prompt.

3. Reasoning with masked memories:
   - Agents debate using only preserved memories.
   - The final answer is selected by majority vote from the final round.

## Masking Strategies

Subjective masking:

- The LLM evaluates each previous solution with `YES`, `NO`, or `NOT SURE`.
- `YES` means preserve, `NO` means remove.
- `NOT SURE` is mapped according to a strict or loose rule.
- This adds many extra model calls, so it is slower and more expensive.

Objective masking:

- The method uses model perplexity as a confidence signal.
- Lower perplexity is treated as more reliable.
- The implementation preserves the response with the lowest perplexity.
- This is cheaper in later debate prompts because fewer memories are retained.

## Paper's Main Experimental Setup

- Baselines: CoT, CoT-SC with 6 reasoning paths, MAD with 3 agents and 2 rounds.
- Proposed methods: MAD-M^2 subjective and MAD-M^2 objective.
- Models: Qwen2.5-7B-Instruct, Qwen2.5-Math-7B-Instruct, DeepSeek-Math-7B-Instruct, QwQ-32B.
- Benchmarks: GSM8K, MATH, AIME24, AIME25, MMLU-Pro.
- Seeds: 41-45.
- Sampling: 100 samples for GSM8K, MATH, and MMLU-Pro; all 30 questions for AIME24/AIME25.

## Paper's Main Findings

- MAD-M^2 usually outperforms naive MAD.
- Subjective masking tends to help weaker models more.
- Objective/perplexity masking tends to help stronger reasoning models more, especially on harder tasks.
- Subjective masking costs more tokens and time because of self-evaluation.
- Objective masking usually reduces token consumption by preserving fewer memories.
- Increasing agents often helps, but increasing debate rounds is not always reliable and can hurt with stronger models.

## Communication Variables

- agents: usually 3 in the main scripts we ran
- rounds: 2
- topology: all agents receive prior memories after the first round
- message content: full chain-of-thought style response plus answer
- memory/context: previous agents' responses
- judge/verifier: subjective LLM mask or objective perplexity mask

## Baselines

- CoT
- CoT-SC
- MAD naive
- MAD-M^2 subjective
- MAD-M^2 objective

## Datasets / Tasks

Paper code supports:

- GSM8K
- MATH
- AIME24
- AIME25
- MMLU-Pro

## Current Local Evidence

Short-subset evidence lives in:

- `experiments/_archive/20260616-pruned/20260612-a8002-madmm-qwen25-14b-gsm8k-short-subset/`
- `reports/_archive/20260616-pruned/20260612-madmm-short-subset-first-insights.md`

Early signal:

- MAD naive and subjective both reach `0.96` accuracy on the 100-sample subset.
- Objective masking reaches `0.95` with lower token cost.
- Subjective masking keeps `296/300` memories and costs the most, so it may be too permissive on this subset.

Our short-subset result is directionally consistent with the paper's cost claims:

- Objective masking is substantially cheaper than naive MAD.
- Subjective masking is much more expensive due to extra evaluation calls.

But our short-subset result also raises a useful caveat:

- Subjective masking barely pruned any memory on this GSM8K subset, so its extra cost did not buy much filtering.
- Objective masking caused one concrete regression (`id=214`), suggesting that aggressive memory compression needs a fallback or risk signal.

## Implementation Details Worth Checking

- How subjective prompts decide to keep or drop memory.
- Why objective pruning keeps exactly one of three memories for every sample in this run.
- Whether mask decisions correlate with correctness or only with fluency/perplexity.
- Whether full communication helps mainly on initially wrong CoT cases or simply stabilizes majority vote.

## Possible Ablations

- Run CoT-SC on the same subset to compare debate against independent sampling.
- Inspect cases `335`, `562`, and `214` before launching more GPU runs.
- Add uncertainty-gated communication: communicate only when initial agents disagree or show low confidence.
- Add fallback for objective pruning when pruning confidence is low.

## Risk / Caveat

Our current result is short-subset evidence only. It should not be described as reproducing the paper's full results.

## Open Questions

- What makes a memory harmful rather than merely redundant?
- Can we predict when communication is worth its token cost?
- Can objective pruning be made risk-aware without adding subjective masking's extra calls?
