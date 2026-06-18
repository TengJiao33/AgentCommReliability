# HiddenBench V2 Stage 3 Blind Sender Full65

## 核心判断

这轮给了一个比 admission 更有冲击力的信号：在 HiddenBench clean subset 上，sender 完全看不到任务、shared facts 和答案选项，只用最小 observation 格式报告本地信息，最终表现仍达到 `55/55`，和 `fact_only_exchange` 完全打平。

这支持一个更尖的假设：hidden-profile 协作里，sender 的任务可见信息可能会诱发过早解释和推荐；把 sender 降成局部传感器，反而能恢复公共信息质量。这个说法目前是单模型、单 benchmark 的机制信号，尚未达到 paper claim。

## Run 记录

Smoke run:

- Run id: `20260617-1935-a8002-hiddenbench-v2-stage3-blind-sender-smoke12-qwen25-14b`
- Local artifacts: `experiments/20260617-1935-a8002-hiddenbench-v2-stage3-blind-sender-smoke12-qwen25-14b/`
- Corrected analysis: `experiments/20260617-1935-a8002-hiddenbench-v2-stage3-blind-sender-smoke12-qwen25-14b/analysis_corrected/`

Failed launch:

- Run id: `20260617-1945-a8002-hiddenbench-v2-stage3-blind-sender-full65-qwen25-14b`
- Status: execution failure before model calls
- Cause: vLLM bind failed with `OSError: [Errno 98] Address already in use` on port `8047`
- Interpretation: plumbing failure only; it contributes no behavioral evidence.

Full run:

- Run id: `20260617-1946-a8002-hiddenbench-v2-stage3-blind-sender-full65-qwen25-14b`
- Local artifacts: `experiments/20260617-1946-a8002-hiddenbench-v2-stage3-blind-sender-full65-qwen25-14b/`
- Remote artifacts: `/data/xuhaoming/yfy/research_workspace/experiments/20260617-1946-a8002-hiddenbench-v2-stage3-blind-sender-full65-qwen25-14b/`
- Model: `Qwen2.5-14B-Instruct`
- GPU/port: A800_2 GPU 7, port `8051`
- Status: completed, `520/520` records, failures `0`
- Rescoring changes: `0`
- End state: GPU 7 and port `8051` released

## 全量结果

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `shared_only` | `1` | `65` | `0.015` | `0` |
| `exchange_then_decide` | `24` | `65` | `0.369` | `0` |
| `blind_exchange` | `54` | `65` | `0.831` | `1` |
| `blind_minimal_exchange` | `57` | `65` | `0.877` | `0` |
| `fact_only_with_options_exchange` | `56` | `65` | `0.862` | `0` |
| `fact_only_exchange` | `57` | `65` | `0.877` | `0` |
| `oracle_public_facts` | `56` | `65` | `0.862` | `0` |
| `full_info` | `59` | `65` | `0.908` | `0` |

## Clean Subset

Clean subset 使用 `full_info` 和 `oracle_public_facts` 都正确的 `55` 个 task。

| Condition | Correct | Records | Accuracy | Unparsed |
| --- | ---: | ---: | ---: | ---: |
| `shared_only` | `0` | `55` | `0.000` | `0` |
| `exchange_then_decide` | `23` | `55` | `0.418` | `0` |
| `blind_exchange` | `53` | `55` | `0.964` | `0` |
| `blind_minimal_exchange` | `55` | `55` | `1.000` | `0` |
| `fact_only_with_options_exchange` | `53` | `55` | `0.964` | `0` |
| `fact_only_exchange` | `55` | `55` | `1.000` | `0` |
| `oracle_public_facts` | `55` | `55` | `1.000` | `0` |
| `full_info` | `55` | `55` | `1.000` | `0` |

Paired contrast on clean subset:

- `blind_minimal_exchange` vs `exchange_then_decide`: left-only `32`, right-only `0`, both-correct `23`, both-wrong `0`
- `fact_only_exchange` vs `blind_minimal_exchange`: left-only `0`, right-only `0`, both-correct `55`, both-wrong `0`
- `blind_exchange` vs `exchange_then_decide`: left-only `31`, right-only `1`, both-correct `22`, both-wrong `1`
- `blind_minimal_exchange` vs `blind_exchange`: left-only `2`, right-only `0`, both-correct `53`, both-wrong `0`

## Public Message Audit

| Condition | Messages | Private exact | Rec leakage | Shared overtalk | Answer mentions | Avg private overlap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `exchange_then_decide` | `253` | `6` | `225` | `134` | `247` | `0.656` |
| `blind_exchange` | `253` | `2` | `2` | `4` | `170` | `0.787` |
| `blind_minimal_exchange` | `253` | `238` | `0` | `4` | `158` | `0.991` |
| `fact_only_exchange` | `253` | `198` | `0` | `4` | `162` | `0.951` |
| `fact_only_with_options_exchange` | `253` | `199` | `0` | `4` | `166` | `0.947` |

The `answer mentions` proxy is not a clean leakage measure here, because many private facts naturally contain option names. The stronger readout is recommendation leakage, shared overtalk, exact private-fact transfer, and private-fact token overlap.

## 解释

The live mechanism is now sharper than Stage 2. Stage 2 showed that forbidding recommendation or shared repetition only partially repaired helpful sender communication. Stage 3 shows that a sender with no task, no shared context, and no answer options can still provide enough public information for the decider to reach the fact-only upper bound, provided the sender preserves the local observation with minimal interpretation.

The strongest version is `blind_minimal_exchange`, not free-form `blind_exchange`. Free-form blind still improves massively over helpful exchange (`54/65` vs `24/65`) but loses two clean tasks relative to minimal reporting. This means reduced task visibility is a real candidate mechanism, while message preservation/format still matters.

## Caveats

This remains a project-local HiddenBench protocol, not the official HiddenBench group-interaction harness.

The result is currently one model family, one benchmark, temperature `0`. It should be treated as a strong mechanism lead rather than a stable general claim.

`blind_minimal_exchange` is a strict reporting prompt. Because HiddenBench hidden information is already cleanly packaged as private facts, the condition may partly copy benchmark annotations into public state. The next pressure test must use paraphrased/noisy local observations or another split-evidence task.

## 下一步压力

First, inspect the two clean-subset tasks where `blind_exchange` fails and `blind_minimal_exchange` succeeds. This tells us whether the gap is caused by paraphrase loss, missing exact private fact, or final decider sensitivity.

Second, run a controlled visibility matrix with the same minimal output format: private-only, private+task, private+options, private+shared, and full helpful visibility. This directly tests which extra sender visibility causes harm.

Third, transfer the blind-sender hypothesis to a non-HiddenBench split-evidence setting. The key test is whether blind/minimal local observation also helps when private evidence is not already a curated hidden fact sentence.
