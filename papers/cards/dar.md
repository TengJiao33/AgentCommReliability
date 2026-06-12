# Hear Both Sides: Efficient Multi-Agent Debate via Diversity-Aware Message Retention

## Link

- paper: https://arxiv.org/abs/2603.20640
- code: https://github.com/DA2I2-SLM/DAR
- local pdf: `papers/dar/2603.20640.pdf`

## One-Sentence Claim

The paper claims that retaining messages that preserve disagreement or challenge the majority can reduce redundant debate communication and improve multi-agent debate outcomes.

## Problem

The paper isolates a communication-selection problem in multi-agent debate: broadcasting all peer responses can add noise and cost, while confidence-based filtering can be unreliable when confidence is miscalibrated or threshold-sensitive.

## Method

DAR uses a filtering step before later debate rounds. Agents first produce answers, optional uncertainty signals, and optional votes. A filtering rule then chooses a subset of peer messages for the next round. The main DAR setting uses `filter_critical`, which asks for agent messages that differ most and differ from the majority-vote answer.

## Communication Variables

| Variable | Value / Design | Notes |
| --- | --- | --- |
| agents | default examples use 4 agents | configurable with `--num_agents` |
| rounds | default examples use 2 debate rounds | configurable with `--debate_rounds` |
| topology | full, sparse, or centralized | flags: `--sparse`, `--centralized` |
| message content | natural-language agent responses, optionally with uncertainty and votes | controlled by `--uncertainty_prompt`, `--vote_prompt` |
| memory/context | retained peer responses from the previous round | constructed in `src/dev.py` |
| routing | optional topology and filtering | `filter_critical`, `filter_certain`, `filter_support`, `filter_nonvote`, etc. |
| confidence/evidence | uncertainty scores and majority-vote answer can be included | uncertainty metric defaults to `anll` |
| judge/verifier | no external verifier in default DAR; optional separate moderator model exists | `--separate_moderator` |
| stopping rule | fixed number of rounds | no early stop inspected yet |

## Baselines

- Basic MAD: full peer-message communication.
- Top-K uncertainty filtering: retain a fixed fraction of most certain messages.
- Uncertainty prompt only: adds confidence-style signal without DAR filtering.
- Vote prompt only: adds majority-vote context without DAR filtering.
- DAR variants: `filter_critical`, `filter_certain`, `filter_support`, `filter_nonvote`, `filter_nonindex`.

## Datasets / Tasks

The repository README lists:

- Math: Arithmetics, GSM8K.
- QA: MMLU subsets, HH-RLHF, CommonSenseQA.
- Planned or TODO support: AIME24 / AIME25.

The cheapest project check is `arithmetics`, `data_size=100`, `qwen2.5-1.5b`.

## Reported Results

These are paper/repository claims, not local reproduction results.

| Setting | Metric | Reported Result | Compared To |
| --- | --- | --- | --- |
| DAR repository overview | inference speed | vLLM-backed library described as faster than older MAD libraries | existing MAD frameworks |
| DAR method overview | communication volume | README reports 30-40% message-volume reduction | full message propagation |
| DAR paper abstract | debate performance | selective message propagation reported to improve debate performance, especially with more agents | full broadcast / filtering baselines |

## Code And Reproducibility

- repo: https://github.com/DA2I2-SLM/DAR
- commit inspected: `f3c6e9d7c5f9805113f4398c20cbf7d732d60dd0`
- license: MIT, per repository README/license badge
- install difficulty: likely moderate; requirement pins `vllm==0.16.0`, which may require a fresh environment
- smallest runnable command:

```bash
python src/main.py --model qwen2.5-1.5b --num_agents 4 --data arithmetics --data_size 100 --debate_rounds 2
```

- DAR command:

```bash
python src/main.py --model qwen2.5-1.5b --num_agents 4 --data arithmetics --data_size 100 --debate_rounds 2 \
  --uncertainty_prompt True --vote_prompt True --m_role filter_critical
```

- expected resource: one A800 GPU for short runs, if vLLM setup succeeds with local model paths

## Implementation Details Worth Inspecting

- prompt templates: `src/evaluator.py` and message builders in `src/dev.py`.
- message construction: `get_new_message_global` and `build_normal_msg_with_ids_batch`.
- filtering or merging: `run_filter_batch_across_samples`; `filter_critical` criteria.
- judge or verifier path: optional moderator through `--separate_moderator`.
- evaluation script: `src/main.py` writes TSV metrics and JSONL histories.
- hidden defaults: non-debug history saves only first 10 samples; use `--debug` for complete quick inspection.

## Possible Ablations

- Basic MAD vs DAR `filter_critical`.
- Top-K uncertainty filtering vs DAR.
- `filter_certain` vs `filter_critical` on cases with minority correct answers.
- Full topology vs sparse topology at the same agent count.
- With and without `--vote_prompt`.

## Caveats

- No local run has been completed yet.
- Repository defaults use model names, while A800_2 should use local model paths to avoid downloads.
- The code README notes that vLLM and Hugging Face backends may produce different results.
- The project should not treat arithmetics results as evidence for GSM8K until a separate GSM8K short run exists.

## Project Fit

| Question | Answer |
| --- | --- |
| Which project axis does it touch? | message retention, disagreement preservation, token efficiency, confidence failure |
| What would we learn by reproducing it? | whether an explicit disagreement-oriented filter preserves useful minority messages in short debate traces |
| What is the cheapest useful check? | 100-sample arithmetics smoke with Basic MAD, Top-K uncertainty, and DAR |
| Should it be promoted to experiment? | yes, after source card creation, because the repo exposes runnable commands and retained-message logs |

## Open Questions

- Does `filter_critical` return stable retained IDs across seeds?
- Does the filter preserve correct minority answers on GSM8K-style arithmetic disagreement cases?
- How much of DAR's effect comes from voting, uncertainty prompting, or the filter itself?
- Does local Qwen2.5-1.5B support the expected chat-template path, or should the short run use Qwen2.5-7B-Instruct?
