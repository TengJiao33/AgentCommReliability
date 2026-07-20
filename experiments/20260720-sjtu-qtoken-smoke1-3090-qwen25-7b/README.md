# SJTU RTX 3090 单题运行验证

- 状态：`COMPLETED`
- 作业：`job-178453914363235342497-feiyang-ying`
- 硬件：单张 NVIDIA RTX 3090 24 GB
- 模型：Qwen2.5-7B-Instruct，BF16
- 参数：1 题，3 agents，4096 token 上下文，256 token 输出上限
- runner 计算时间：95.4 秒
- 调度总时长：1 分 51 秒
- 峰值 CUDA 显存：14.30 GiB

本次运行验证 RTX 3090 可以执行当前 runner。样本量不足以支持准确率或方法效果判断。

结果位于 `math500-qwen25-7b-instruct-mca-question-token-anchored-delta/`。
