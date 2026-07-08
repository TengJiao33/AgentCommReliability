# 20260707 A800_2 MCA matrix early-plan source-gated GPU1

## Purpose

Run the next MCA matrix after the question-only Pre-KV null result.

This run replaces zero-token `question_only` sender state with short `early_plan` sender state:

```text
sender reads problem
-> sender privately generates up to 64 pre-answer tokens
-> receiver continues from sender live KV
-> matched A/B first-round and C/D debate comparisons
```

## Why This Exists

The stopped question-only run tested a weak implementation: sender `generated_tokens=0`, so the channel mostly carried a read-pass prompt prefix.

This early-plan version tests whether an actual pre-answer search state has a stronger effect while still auditing answer leakage.

## Matrix

- A: no-channel first round.
- B: early-plan Pre-KV first round.
- C: no-channel first round followed by one Standard MAD text debate round.
- D: early-plan Pre-KV first round followed by one Standard MAD text debate round.

Primary contrasts:

- `B - A`: fixed-parameter early-plan Pre-KV first-round effect.
- `D - C`: early-plan Pre-KV effect after MAD text debate.

## Leak Audit

Each record writes:

- `sender_state_outputs`
- `sender_answer_tag_count`
- `sender_gold_leak_count`

If early-plan improves results but leak counts are nonzero or sender text visibly contains final-answer information, the result is not answer-free MCA evidence.

## Remote

- Host: `A800_2`
- Workspace: `/data/xuhaoming/yfy/research_workspace`
- GPU default: `1`
- Python: `/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-7B-Instruct`

## Output run ids

- `20260707-a8002-gpu1-mca-matrix-early-plan-disagreement-qwen25-7b`
- `20260707-a8002-gpu1-mca-matrix-early-plan-gold-contrast-qwen25-7b`

## Boundary

This is still a packet diagnostic, not a full MATH500 claim. It can only support packet-level comparisons under the matched source gate.
