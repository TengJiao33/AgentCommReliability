# MCA 潜状态安全变体进展

日期：2026-07-08

## 本次改动范围

涉及文件：

```text
scripts/run_mca_latent_rounds.py
tests/test_mca_latent_rounds.py
experiments/20260707-a8002-mca-latent-rounds-gpu1-qwen25-7b/run_remote_serial_safe_variants_50.sh
experiments/20260707-a8002-mca-latent-rounds-gpu1-qwen25-7b/launch_safe_variants_when_gpu_empty.sh
```

已加入或调整的参数：

```text
--private-thought-style {natural,deliberative}
--peer-mode {mean,residual,per_peer_branch}
--normalize-steering / --no-normalize-steering
--peer-message-max-norm
--same-seed-conditions / --no-same-seed-conditions
--apply-peer-on-final / --no-apply-peer-on-final
```

默认设置：

```text
private_thought_style = natural
steering_scale = 0.05
normalize_steering = true
peer_fusion = mean
peer_message_max_norm = 1.0
same_seed_conditions = true
apply_peer_on_final = false
```

## 已完成的小样本检查

最终阶段同伴注入开关的 6 条对照：

```text
apply_peer_on_final = true
baseline_correct = 2/6
latent_correct = 1/6
transitions = 4 BaW_to_W, 1 BaC_to_C, 1 BaC_to_W

apply_peer_on_final = false
baseline_correct = 2/6
latent_correct = 2/6
transitions = 4 BaW_to_W, 2 BaC_to_C
```

出现变化的样例：

```text
gold = pi
baseline majority = pi
latent majority with final steering = 3*pi/2
```

该对照之后，`apply_peer_on_final` 默认值改为 `false`。

## 新增 peer_mode

`residual`：

```text
message = mean(peer_state - own_state)
```

`per_peer_branch`：

```text
for each peer:
  generate a short private branch under that peer state
  convert branch thought back to state

message = mean(branch state vectors)
```

## 夜间运行脚本

脚本：

```text
experiments/20260707-a8002-mca-latent-rounds-gpu1-qwen25-7b/run_remote_serial_safe_variants_50.sh
```

串行 run：

```text
residual        x mca_disagreement_v1  LIMIT=50
residual        x mca_gold_contrast_v1 LIMIT=50
per_peer_branch x mca_disagreement_v1  LIMIT=50
per_peer_branch x mca_gold_contrast_v1 LIMIT=50
```

共同设置：

```text
agents = 3
latent_rounds = 2
thought_tokens_per_round = 96
private_thought_style = natural
final_max_tokens = 1536
thought_temperature = 0.7
final_temperature = 0.2
top_p = 1.0
steering_layer = 16
steering_scale = 0.05
normalize_steering = true
peer_fusion = mean
peer_message_max_norm = 1.0
same_seed_conditions = true
apply_peer_on_final = false
seed = 42
```

## GPU 等待启动器

脚本：

```text
experiments/20260707-a8002-mca-latent-rounds-gpu1-qwen25-7b/launch_safe_variants_when_gpu_empty.sh
```

日志：

```text
/data/xuhaoming/yfy/research_workspace/experiments/20260708-a8002-mca-latent-safe-variants-wait/wait_launcher.log
```

选择规则：

```text
compute_count == 0
free_mb >= 70000
poll every 120 seconds
```

运行记录：

```text
2026-07-08 00:53 +08:00:
  no fully empty GPU found

later:
  GPU4 selected
  run_remote_serial_safe_variants_50.sh started
```

## 结果读取位置

每个 run 的输出目录：

```text
experiments/<run_id>/math500-qwen25-7b-instruct-mca-latent-rounds/
```

主要文件：

```text
records.jsonl
summary.json
summary.md
```

读取字段：

```text
baseline.correct
latent.correct
transition
baseline.majority_tie
latent.majority_tie
thought_answer_marker_count
thought_gold_suspect_count
```

transition 解释：

```text
BaW_to_C = baseline wrong, latent correct
BaC_to_W = baseline correct, latent wrong
BaC_to_C = baseline correct, latent correct
BaW_to_W = baseline wrong, latent wrong
```
