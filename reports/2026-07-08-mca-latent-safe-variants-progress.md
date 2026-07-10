# MCA 潜状态安全变体运行记录

日期：2026-07-08

## 做法

1. 安全变体沿用 `scripts/run_mca_latent_rounds.py`。每道题运行基线条件和潜状态条件，两个条件都调用同一个 `_run_condition`。

2. 基线条件中，每个智能体生成 2 轮私有思考，每轮 96 个标记。私有思考只进入本智能体自己的上下文，不展示给同伴。

3. 潜状态条件的第 0 轮与基线相同，也先让每个智能体生成私有思考，不接收同伴消息。

4. 每轮私有思考结束后，脚本用 `_thought_vector` 构造状态向量。它编码“题目 + 私有思考”和“题目 + 空私有思考”，在第 16 层取最后位置隐藏状态差值。

5. residual 模式构造同伴消息时，先把每个同伴状态减去本智能体状态，再对差值求均值，得到 `mean(peer_state - own_state)`。

6. per-peer branch 模式对每个同伴状态单独生成一个短私有分支，再把该分支文本转回状态向量，最后融合多个分支向量。

7. 融合后的同伴向量先归一化，再按范数 1.0 裁剪。记录中保存原始范数、有效范数、是否裁剪和同伴来源数。

8. 从第 1 轮私有思考开始，接收方在第 16 层注册 hook，把同伴向量乘以 0.05 加到当前最后一个标记的隐藏状态。

9. 最终答案阶段默认不注入同伴向量。模型只读取本智能体自己的私有思考轨迹并输出答案。

10. 夜间脚本串行运行四个组合：residual/disagreement、residual/gold-contrast、per-peer-branch/disagreement、per-peer-branch/gold-contrast。GPU 等待器只在空闲 GPU 满足显存条件后启动该串行脚本。

## 工程细节

- 涉及文件包括 `scripts/run_mca_latent_rounds.py`、`tests/test_mca_latent_rounds.py`、`experiments/20260707-a8002-mca-latent-rounds-gpu1-qwen25-7b/run_remote_serial_safe_variants_50.sh` 和 `experiments/20260707-a8002-mca-latent-rounds-gpu1-qwen25-7b/launch_safe_variants_when_gpu_empty.sh`。
- 新增或调整参数包括 `--private-thought-style {natural,deliberative}`、`--peer-mode {mean,residual,per_peer_branch}`、`--normalize-steering`、`--peer-message-max-norm`、`--same-seed-conditions` 和 `--apply-peer-on-final`。
- 默认设置为 `private_thought_style=natural`、`steering_scale=0.05`、`normalize_steering=true`、`peer_fusion=mean`、`peer_message_max_norm=1.0`、`same_seed_conditions=true`、`apply_peer_on_final=false`。
- 每轮每个智能体先生成私有思考，默认 2 轮、每轮 96 个标记；同伴看不到这些文本。
- `_thought_vector` 构造“题目 + 私有思考”和“题目 + 空私有思考”两段输入，在第 16 层取最后位置隐藏状态差值。
- `residual` 模式使用 `mean(peer_state - own_state)` 作为同伴消息。
- `per_peer_branch` 模式对每个同伴状态单独生成短私有分支，再把分支文本转回状态向量并融合。
- `_generate_with_steering` 在指定层注册 hook，把融合后的同伴向量乘以 `0.05` 加到当前最后一个标记的隐藏状态。
- 夜间脚本串行运行四个 50 题组合：`residual x mca_disagreement_v1`、`residual x mca_gold_contrast_v1`、`per_peer_branch x mca_disagreement_v1`、`per_peer_branch x mca_gold_contrast_v1`。
- GPU 等待启动器每 120 秒检查一次空闲 GPU，条件为 `compute_count == 0` 且 `free_mb >= 70000`。日志路径为 `/data/xuhaoming/yfy/research_workspace/experiments/20260708-a8002-mca-latent-safe-variants-wait/wait_launcher.log`。
- 每个 run 输出 `records.jsonl`、`summary.json` 和 `summary.md`，读取字段包括 `baseline.correct`、`latent.correct`、`transition`、`majority_tie`、`thought_answer_marker_count` 和 `thought_gold_suspect_count`。

## 结果

| 检查项 | 结果 |
| --- | --- |
| 最终阶段注入同伴向量 | 6 题小样本中基线 2/6，潜状态 1/6 |
| 最终阶段不注入同伴向量 | 6 题小样本中基线 2/6，潜状态 2/6 |
| 伤害样例 | 金标 `pi`，基线多数答案 `pi`，最终阶段注入后潜状态多数答案 `3*pi/2` |
| GPU 等待器初始检查 | 2026-07-08 00:53 +08:00 未发现完全空闲 GPU |
| 运行启动 | 选中 GPU4，启动 `run_remote_serial_safe_variants_50.sh` |

## 备注

正误转移字段含义为 `BaW_to_C`、`BaC_to_W`、`BaC_to_C`、`BaW_to_W`。其中 `Ba` 表示以基线条件为参照，`C` 表示正确，`W` 表示错误。
