# 2026-07-06 MCA-Pre 运行裁剪记录

## 事件

2026-07-06 约 14:50（Asia/Shanghai），按人工指令只保留 `MCA-Pre-KV question_only` 继续运行，其余当前 MCA 远端运行停止。

## 保留运行

- 运行目录：`/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-pre-kv-question-only-standard-qwen25-7b-full`
- 记录文件：`math500-qwen25-7b-instruct-mca-pre-kv-cache-question_only-state/records.jsonl`
- 保留进程：launcher `2388093`，worker `2388133`
- 最近检查点：106/500
- 当时转移计数：`BaC_to_C=73`，`BaC_to_W=2`，`BaW_to_C=10`，`BaW_to_W=21`
- 当时读数：baseline 75/106，final 83/106，delta +8

## 停止运行

- `20260706-a8002-math500-mca-kv-s-live-state-standard-qwen25-7b-full`
- `20260706-a8002-math500-mca-pre-kv-early-plan-standard-qwen25-7b-full`
- `20260706-a8002-math500-mca-pre-s-question-only-standard-qwen25-7b-full`
- `20260706-a8002-math500-mca-pre-s-early-plan-standard-qwen25-7b-full`

停止的进程包括对应 launcher、timeout 包装进程和 worker 进程：

- `1883987`, `1916595`, `1916596`
- `2388100`, `2388134`, `2388135`
- `2388112`, `2388138`, `2388139`
- `2388116`, `2388140`, `2388141`

## 停止后状态

停止后，`MCA-Pre-KV question_only` 仍在 GPU 2 运行。GPU 3、4、7 已释放到空闲状态；GPU 1 仍有非本项目进程占用约 37 GB 显存，因此旧 KV/S 停止后 GPU 1 未变为全空。

## 解释边界

106/500 的 `MCA-Pre-KV question_only` 数字是中间检查点。

## 18:20 异常停止与补跑

2026-07-06 18:20 复查时，`MCA-Pre-KV question_only` 已无远端运行进程，GPU 2 空闲，记录停在 392/500。日志显示启动脚本第 43 行的 `timeout 48h ... run_mca_pre_kv_cache.py` 被系统标记为 `Killed`；日志中未出现 Python traceback 或显式 CUDA out-of-memory 文本。

停止时中间读数：

- rows：392/500
- baseline：273/392
- final：288/392
- delta：+15
- transition：`BaC_to_C=255`，`BaC_to_W=18`，`BaW_to_C=33`，`BaW_to_W=86`

为避免覆盖已完成记录，`scripts/mca_pre_answer_runner.py` 增加 `--resume`：读取已有 `records.jsonl`，重建计数，跳过已完成 `index`，并用 append 模式继续写入。补丁本地通过：

- `python -m py_compile scripts/mca_pre_answer_runner.py scripts/run_mca_pre_kv_cache.py`
- `python -m unittest tests.test_mca_pre_answer_runner`

远端同步后，GPU 2 在补跑前为空闲状态（约 4 MB 显存，0% 利用率）。补跑启动信息：

- resume launcher PID：`700624`
- timeout PID：`700631`
- worker PID：`700632`
- 启动时间：2026-07-06 18:22:48
- 补跑确认：日志显示 `existing_records=392`，随后从 `row 393/500 pre-state generation start` 继续。
