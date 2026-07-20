# SJTU RTX 3090 512-token 运行验证

- 状态：`COMPLETED`
- 作业：`job-178455824669699451936-feiyang-ying`
- 硬件：单张 NVIDIA RTX 3090 24 GB
- 模型：Qwen2.5-7B-Instruct，BF16
- 参数：1 题，3 agents，4096 token 上下文，512 token 输出上限
- runner 计算时间：165.8 秒
- 调度总时长：2 分 53 秒
- 峰值 CUDA 显存：14.30 GiB

三个 baseline agent 均生成到 512 token 上限，任务仍稳定完成。该结果验证更长生成预算的显存与运行稳定性，不用于判断方法效果。

结果位于 `math500-qwen25-7b-instruct-mca-question-token-anchored-delta/`。
