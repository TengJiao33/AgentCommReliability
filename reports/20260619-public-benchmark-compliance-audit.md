# 公开基准合规口径审计

日期：2026-06-19

## 结论

对外报告必须以公开基准或清楚标注的公开切片为主。PG40 可以作为从 PerspectiveGap 派生出来的公开切片压力表，但不能被写成 PerspectiveGap 官方全量结果，也不能支撑 SOTA 或接近 SOTA 的口径。

当前项目应该采用两层证据：

| 层级 | 可承担的结论 | 不可承担的结论 |
| --- | --- | --- |
| PerspectiveGap 官方全量网格 | 对外可比的 benchmark 结果 | 若未跑全量，不得声称官方 leaderboard 可比 |
| PG40 公开切片 | 机制压力、排序失败、预算控制诊断 | 不得包装成完整 PerspectiveGap / SOTA 结论 |
| HSA-v0 内部诊断 | 机制解释、错误定位、附表 | 不得单独证明公开方法有效性 |

## 外部做法

PerspectiveGap 官方提交要求很明确：主榜需要跑全部 `110` 个 scenarios、shuffle seeds `1` 和 `42`、`role_assignment` 与 `prompt_writing` 两个任务，总计 `440` 个 model requests 和 `440` 个 score rows。官方还要求提交 raw prediction JSONL、score JSONL、summary text、模型和 provider、运行日期、PerspectiveGap commit、命令行、非默认 decoding、wrapper、post-processing 等元数据。

Hugging Face Open LLM Leaderboard 的公开文档也采用类似逻辑：公开列出任务、few-shot 设置、evaluation harness，并给出复现命令和详细结果位置。重点不是只报一个数字，而是让读者知道 score 是在哪个公开任务集、哪个 harness、哪些参数下来的。

Evaluation Cards 这类 evaluation-reporting 工作指出，模型评测结果如果缺少 benchmark metadata、evaluation run data、model metadata、generation config 和 detailed results，读者就无法判断可比性、完整性和来源。这个方向和我们现在的问题完全同构：小切片可以报告，但必须把 scope 和不可比边界写出来。

HELM 的报告范式也强调 broad coverage、multi-metric 和 transparency。它不是只挑一个最好数字，而是把 scenario、metric、缺失项和 trade-off 摆出来。

## 对我们意味着什么

第一，PG40 不能叫 full public benchmark。它最多叫 `PerspectiveGap-derived public slice` 或 `public-slice pressure table`。如果保留 PG40 表，标题、caption、摘要和正文必须同时写清楚 sample scope、强透明基线、source-ledger baseline、direct baseline 和 oracle。

第二，对外主表若要 claim benchmark effectiveness，必须优先使用 PerspectiveGap 官方全量网格。最低合规门槛是：

| 项 | 要求 |
| --- | --- |
| scenarios | `110/110` |
| seeds | `1, 42` |
| tasks | `role_assignment`, `prompt_writing` |
| prediction rows | `440` |
| score rows | `440` |
| scorer | official `scripts/score_predictions.py` |
| artifacts | raw predictions, scores, summary, metadata |
| metadata | model ID, provider/route, run date, commit SHA, commands, decoding, wrapper/postprocess |

第三，任何未达到上述门槛的结果都要降级：

| 情况 | 允许写法 |
| --- | --- |
| 五行 PG40 | pilot / diagnostic / public-slice pressure |
| 四十行 PG40 | public-derived slice, not official leaderboard |
| HSA-v0 | internal mechanism diagnostic |
| prompt variant smoke | plumbing or ablation, not benchmark result |

## 当前动作

已经启动 A800_2 的 PerspectiveGap 官方全量 direct baseline：

| 项 | 内容 |
| --- | --- |
| run id | `20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b` |
| model | `Qwen2.5-14B-Instruct` via local vLLM |
| runner | official `scripts/run_model_predictions.py` |
| scorer | official `scripts/score_predictions.py` |
| grid | `110 scenarios × 2 seeds × 2 tasks = 440 requests` |
| local preflight | official scorer fixture passed; oracle assignment-to-prompt scored `220/220` |
| status | complete on A800_2 GPU 7 |
| validation | predictions `440`, scores `440`, status `ok: 440` |
| official direct result | role assignment `0/220`; prompt writing `2/220`; combined `2/440` |

## 写作红线

不能写“我们在 PerspectiveGap 上取得方法优势”，除非官方全量或清楚可比的公开切片表支持。

不能写“SOTA”或“接近 SOTA”，除非与公开 leaderboard 同网格、同 scorer、同 metric、同披露标准比较。

不能把 PG40 五行或四十行的结果隐藏成完整 benchmark。必须在表题、caption 和正文里写出 `slice`、`row count`、`baseline set` 和 `limitation`。

可以写：“当前公开切片结果显示，编译器能修复预算合法性，但候选排序仍未跨过 source-ledger 和 transparent greedy；因此公开基准方法优势尚未成立。”

## 参考来源

- PerspectiveGap paper: https://arxiv.org/html/2606.08878v1
- PerspectiveGap collection and leaderboard: https://huggingface.co/collections/sun1245/perspectivegap-benchmark
- Local official submission guide: `baselines/PerspectiveGap/upstream/SUBMIT_RESULTS.md`
- Evaluation Cards: https://arxiv.org/html/2606.09809v1
- Hugging Face Open LLM Leaderboard archive: https://huggingface.co/docs/leaderboards/en/open_llm_leaderboard/archive
- HELM: https://crfm.stanford.edu/helm/
