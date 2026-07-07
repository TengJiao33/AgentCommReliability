# MCA-KV / MCA-S implementation notes

日期：2026-07-06

## 目的

把 `active/README.md` 中已经命名但尚未源码化的两个 MCA 版本落成可执行 runner，并在 2026-07-06 修正为 live sender state 语义：

- `MCA-KV`：sender 真实解题生成时捕获 `past_key_values`，receiver 从该 KV cache 后继续生成。
- `MCA-S`：sender 真实解题生成时捕获指定层 residual activation，并用该向量 steering receiver。

本记录只说明源码落地和文献依据；尚未启动 GPU 实验，因此不构成结果证据。

## 文献依据

- CIPHER / embedding debate：自然语言采样会压缩模型在词表上的 belief，embedding/hidden 表示可作为非文本通信介质；本实现沿用“避开可见自然语言消息”的思路，但 2026-07-06 后通信对象改为 sender 真实解题状态，而不是 cue-derived text state。
  - https://arxiv.org/abs/2310.06272
- Activation Addition / activation engineering：通过 forward activation 构造 steering vector，在推理时注入残差流；本实现用 sender 真实解题生成过程中的 residual activation 均值构造 MCA-S steering direction。
  - https://arxiv.org/abs/2308.10248
- EquiMem：强调共享记忆/隐藏状态更新需要零信任校准和 trust discount；本轮代码只落通道，不声称已经解决校准问题。
  - https://arxiv.org/abs/2605.09278
- KG-CFR：把 private planning buffer 与 public speech 分层，支持“内部状态/计划”和“外显论证”解耦；MCA-KV/S 都按这个分层思想避免把 cue 文本直接放进 receiver prompt。
  - https://arxiv.org/abs/2606.10475

## 实现边界

新增源码：

- `scripts/mca_hidden_channel_runner.py`
- `scripts/run_mca_kv_cache.py`
- `scripts/run_mca_activation_steering.py`
- `tests/test_mca_hidden_channels.py`

共同设计：

- 不再把 text-only `records.jsonl` 当成真实 hidden-state 来源；records 没有 KV cache 或 hidden activation。
- 每题按 row 流式执行：生成 sender、捕获真实状态、传给 receiver、立即写出一条 record。
- 复用当前 MATH evaluator、majority vote、transition label 与 summary 口径。
- receiver prompt 不包含 sender text，只提示可能存在不可见 hidden channel。
- `--channel-mode none` 提供 no-channel control。

`MCA-KV`：

- sender 解题 prompt 和已生成 token 的真实 `past_key_values` 会传给 receiver。
- 该通道可能包含 sender CoT/answer 信息，属于强 hidden-state transfer，不再是 answer-free cue。
- summary protocol 为 `mca-kv-cache`。

`MCA-S`：

- 在 sender 真实生成过程中用 hook 捕获指定 transformer layer 的 residual input activation。
- 默认取该 sender pass 中捕获向量的均值作为 steering vector。
- receiver 生成时在同一层把 vector 注入当前 token 的 residual stream。
- summary protocol 为 `mca-activation-steering`。

## 当前验证

- Python compile：通过。
- `run_mca_kv_cache.py --help`：通过。
- `run_mca_activation_steering.py --help`：通过。
- `python -m unittest discover -s tests -p "test_*.py"`：47 tests passed。
- `mca_hidden_channel_runner.py` 已加入可见进度日志：逐 row 的 sender generation、receiver generation 和 records 写入都会打印 `[mca-hidden] ...`。

## GPU smoke

- MCA-KV smoke completed on A800_2 GPU 6:
  - Run: `/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-kv-live-state-qwen25-7b/`
  - Rows: 2
  - Result: completed in 93.0s; records and summary written.
  - Status: runnable plumbing check passed; not claim-bearing.
- MCA-S first smoke failed on A800_2 GPU 6:
  - Run: `/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-s-live-state-qwen25-7b/`
  - Failure: CUDA OOM during row 2 receiver generation.
  - Fix: receiver manual generation now runs under `torch.inference_mode()`; MCA-S sender state no longer retains unused sender KV caches.
- MCA-S rerun completed on A800_2 GPU 6:
  - Run: `/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-smoke-mca-s-live-state-qwen25-7b-rerun1/`
  - Rows: 2
  - Result: completed in 102.1s; records and summary written.
  - Behavioral caveat: this scale/layer setting is not usable as a full experiment yet. It changed both smoke rows, harmed the one initially correct row, and produced format pollution such as parsing `final answer only` as the answer.

## Remaining caveats

- MCA-KV is a strong hidden-state transfer: the receiver's KV continuation may contain sender answer and reasoning information.
- MCA-S is only plumbing-complete. It needs layer/scale/normalization and prompt-format tuning before a full run would be worth GPU time.
- Neither smoke is claim-bearing because both use `--limit 2` and shortened `--max-tokens 512`.

## 最小 smoke 建议

Completed smoke commands were equivalent to:

```bash
python scripts/run_mca_kv_cache.py --work-dir /data/xuhaoming/yfy/research_workspace --run-id 20260706-a8002-smoke-mca-kv-live-state --benchmark math500 --split test --model-key qwen25-7b-instruct --model-path /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct --initial-prompt-style standard-mad --pool-state-scope all --limit 2 --max-tokens 512 --resolve-max-tokens 512 --max-model-len 4096 --dtype bfloat16 --channel-mode state
```

```bash
python scripts/run_mca_activation_steering.py --work-dir /data/xuhaoming/yfy/research_workspace --run-id 20260706-a8002-smoke-mca-s-live-state --benchmark math500 --split test --model-key qwen25-7b-instruct --model-path /mnt/quarkfs/share_model/Qwen2.5-7B-Instruct --initial-prompt-style standard-mad --pool-state-scope all --limit 2 --max-tokens 512 --resolve-max-tokens 512 --max-model-len 4096 --dtype bfloat16 --channel-mode state --steering-layer 16 --steering-scale 1.0
```

smoke 只检查是否能完整写出 `records.jsonl` 和 `summary.json`，不解释准确率。
