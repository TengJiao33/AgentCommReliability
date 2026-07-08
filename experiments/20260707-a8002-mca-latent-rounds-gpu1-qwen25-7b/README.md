# MCA 潜状态多轮交换实验

这个实验测试答案收敛前的潜状态消息传递。

和 Pre-KV bridge 不同：

- 不展示同伴文本；
- 不使用 `REPRESENTATION/FIRST_MOVE/CHECK` 这类显式协议；
- 不拼接同伴 KV；
- 同伴状态通过 activation steering 进入下一轮私有思考；
- 最终答案只在潜状态轮次之后生成；
- 默认不在最终答案阶段继续注入同伴状态。

## 主脚本

```text
run_remote_serial_latent_rounds.sh
```

主 run id：

```text
20260707-a8002-gpu1-mca-latent-rounds-disagreement-qwen25-7b
20260707-a8002-gpu1-mca-latent-rounds-gold-contrast-qwen25-7b
```

## 停止后的安全默认值

第一次远程尝试跑了 6 条后停止。原因是当时用了未归一化同伴 activation steering：

```text
--steering-scale 1.0
```

观测到同伴向量范数大约 60-80，注入太强。

现在运行器和启动脚本使用：

```text
--steering-scale 0.05
--normalize-steering
--peer-message-max-norm 1.0
--same-seed-conditions
--private-thought-style natural
--no-apply-peer-on-final
```

## 最终阶段注入小样本测试

两个 6 条小样本测试对比最终阶段同伴注入：

```text
apply_peer_on_final=true:  baseline 2/6, latent 1/6, one BaC_to_W
apply_peer_on_final=false: baseline 2/6, latent 2/6, zero BaC_to_W
```

`BaC_to_W` 样例中，正确 majority 从：

```text
pi
```

被最终阶段同伴注入推成：

```text
3*pi/2
```

所以当前默认使用：

```text
--no-apply-peer-on-final
```

`--apply-peer-on-final` 只用于诊断，不用于主实验。

## 安全变体夜间脚本

```text
run_remote_serial_safe_variants_50.sh
```

跑两个机制：

```text
peer_mode=residual:
  使用 mean(peer_state - own_state)

peer_mode=per_peer_branch:
  对每个同伴状态单独生成 branch
  再融合 branch states
  生成下一轮私有思考
```

共同设置：

```text
--no-apply-peer-on-final
--private-thought-style natural
匹配种子
相同温度
相同 token 预算
LIMIT=50
```

覆盖两个数据子集：

```text
mca_disagreement_v1
mca_gold_contrast_v1
```

## GPU 等待启动

```text
launch_safe_variants_when_gpu_empty.sh
```

选择规则：

```text
compute_count == 0
free_mb >= 70000
poll every 120 seconds
```

日志：

```text
experiments/20260708-a8002-mca-latent-safe-variants-wait/wait_launcher.log
```

这个启动器等到 GPU4 空出来后自动开始跑安全变体。
