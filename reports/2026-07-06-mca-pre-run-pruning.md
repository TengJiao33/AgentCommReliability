# MCA-Pre 运行裁剪记录

## 做法

1. 远端原本同时存在多条 MCA 运行：live-state MCA-KV/S、`MCA-Pre-KV question_only`、`MCA-Pre-KV early_plan`、`MCA-Pre-S question_only` 和 `MCA-Pre-S early_plan`。

2. 2026-07-06 约 14:50（Asia/Shanghai）检查远端进程和 GPU 占用后，只保留 `MCA-Pre-KV question_only`。这一条运行的发送方只读题并保存 KV，接收方接入该 KV 生成答案。

3. 其他运行被停止，对应 launcher、timeout 和 worker 进程逐一结束，GPU 3、4、7 被释放为空闲。

4. 保留运行继续在 GPU 2 上写 `records.jsonl`。14:50 检查时已有 106/500 行；报告记录了当时的 baseline、final、delta 和正误转移。

5. 18:20 再次检查时，`MCA-Pre-KV question_only` 已无远端运行进程，GPU 2 空闲，记录停在 392/500。启动脚本中的 `timeout 48h ... run_mca_pre_kv_cache.py` 被系统标记为 `Killed`，日志没有 Python traceback 或显式 CUDA out-of-memory 文本。

6. 本地随后给 `scripts/mca_pre_answer_runner.py` 增加 `--resume`。resume 逻辑先读取已有 `records.jsonl`，重建计数，识别已完成 `index`，再以 append 模式继续写入未完成题目。

7. 补跑启动后，日志显示 `existing_records=392`，随后从 `row 393/500 pre-state generation start` 继续。补跑进程包括 launcher、timeout 和 worker。

8. 这份记录只保存裁剪、停止和补跑状态，不把 106/500 或 392/500 当成完整 MATH-500 结果。

## 工程细节

- 保留运行目录：`/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-pre-kv-question-only-standard-qwen25-7b-full`。
- 记录文件：`math500-qwen25-7b-instruct-mca-pre-kv-cache-question_only-state/records.jsonl`。
- 保留进程：launcher `2388093`，worker `2388133`。
- 停止运行：`20260706-a8002-math500-mca-kv-s-live-state-standard-qwen25-7b-full`、`20260706-a8002-math500-mca-pre-kv-early-plan-standard-qwen25-7b-full`、`20260706-a8002-math500-mca-pre-s-question-only-standard-qwen25-7b-full`、`20260706-a8002-math500-mca-pre-s-early-plan-standard-qwen25-7b-full`。
- 停止进程：`1883987`、`1916595`、`1916596`、`2388100`、`2388134`、`2388135`、`2388112`、`2388138`、`2388139`、`2388116`、`2388140`、`2388141`。
- 14:50 后状态：`MCA-Pre-KV question_only` 仍在 GPU 2 运行；GPU 3、4、7 释放为空闲；GPU 1 仍有非本项目进程占用约 37 GB 显存。
- 18:20 复查：`MCA-Pre-KV question_only` 无远端运行进程，GPU 2 空闲，记录停在 392/500。
- 异常停止日志：启动脚本第 43 行的 `timeout 48h ... run_mca_pre_kv_cache.py` 被系统标记为 `Killed`；日志中没有 Python traceback 或显式 CUDA out-of-memory 文本。
- 补跑实现：`scripts/mca_pre_answer_runner.py` 增加 `--resume`，读取已有 `records.jsonl`，重建计数，跳过已完成 `index`，以 append 模式继续写入。
- 本地验证：`python -m py_compile scripts/mca_pre_answer_runner.py scripts/run_mca_pre_kv_cache.py`；`python -m unittest tests.test_mca_pre_answer_runner`。
- 补跑进程：resume launcher `700624`，timeout `700631`，worker `700632`。
- 补跑启动时间：2026-07-06 18:22:48。
- 补跑确认：日志显示 `existing_records=392`，随后从 `row 393/500 pre-state generation start` 继续。

## 结果

| 检查点 | rows | baseline | final | delta | transition |
| --- | ---: | ---: | ---: | ---: | --- |
| 14:50 中间检查 | 106/500 | 75/106 | 83/106 | +8 | `BaC_to_C=73`, `BaC_to_W=2`, `BaW_to_C=10`, `BaW_to_W=21` |
| 18:20 异常停止 | 392/500 | 273/392 | 288/392 | +15 | `BaC_to_C=255`, `BaC_to_W=18`, `BaW_to_C=33`, `BaW_to_W=86` |

## 备注

106/500 和 392/500 均为中间检查点，不是完整 MATH-500 结果。补跑前 GPU 2 空闲，约 4 MB 显存占用，0% 利用率。
