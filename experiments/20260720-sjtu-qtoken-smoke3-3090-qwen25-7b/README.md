# SJTU RTX 3090 三题稳定性验证

- 状态：`COMPLETED`
- 作业：`job-178453932333648706749-feiyang-ying`
- 硬件：单张 NVIDIA RTX 3090 24 GB
- 模型：Qwen2.5-7B-Instruct，BF16
- 参数：3 题，3 agents，4096 token 上下文，256 token 输出上限
- runner 计算时间：238.1 秒
- 调度总时长：4 分 5 秒
- 峰值 CUDA 显存：14.30 GiB

三题连续运行没有 OOM、崩溃或显存增长。256 token 上限会截断部分输出，因此本次结果只用于运行稳定性验收，不用于判断方法效果。

结果位于 `math500-qwen25-7b-instruct-mca-question-token-anchored-delta/`。
