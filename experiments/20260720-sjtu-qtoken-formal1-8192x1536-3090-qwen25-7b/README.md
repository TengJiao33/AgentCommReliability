# SJTU RTX 3090 原参数单题验证

- 状态：`COMPLETED`
- 作业：`job-178455897190977914939-feiyang-ying`
- 硬件：单张 NVIDIA RTX 3090 24 GB
- 模型：Qwen2.5-7B-Instruct，BF16
- 参数：1 题，3 agents，8192 token 上下文，1536 token 输出上限
- runner 计算时间：297.4 秒
- 调度总时长：5 分 5 秒
- 峰值 CUDA 显存：14.41 GiB

本次运行完整覆盖原实验的上下文和输出预算，作业正常结束。结果证明单张 24 GB RTX 3090 可以运行当前 runner；样本量不足以支持准确率或方法效果判断。

结果位于 `math500-qwen25-7b-instruct-mca-question-token-anchored-delta/`。
