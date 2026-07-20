# 远程同步清单

日期：2026-07-20

## 当前状态

旧 `A800_2` 同步清单已经作废。后续默认远端改为 `SJTU_HPC`；aTrust、SSH、JumpServer、家目录、配额和调度器已经核验。项目提交 `d21e89b` 已部署，`pdgpu-ezkws` 最小 GPU 作业已经完成；模型仍未上传。

当前入口状态：

```text
用户: feiyang.ying
aTrust: https://trust.aispeech.com.cn:4430
HPC Web: http://js-hpc.aispeech.com.cn/
SSH/JumpServer: js-hpc.aispeech.com.cn:2222
本机别名: sjtu-hpc
家目录: /hpc_stor03/sjtu_home/feiyang.ying
授权资产: d6-hpc-debuggpu-001
调度器: vc 2.0.3
```

项目根目录：`/hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability`（已部署提交 `d21e89b`）。

## 待迁移任务

| 任务 | 源码状态 | 远端状态 |
| --- | --- | --- |
| Question-Token Anchored Delta disagreement50 | runner、测试和启动脚本已存在 | 旧 A800 队列作废；待最小 `vc` 作业完成兼容性检查后首跑 |
| Text-Anchored Delta smoke | runner、测试和 smoke 脚本已存在；旧机只产生 4 行部分记录 | 待新集群完成 5 题 smoke |
| Receiver-Conditioned Complementary Latent Communication | 仅有设计和实验矩阵 | 尚无专用 runner/test，不进入远程同步 |

## 运行前检查

```powershell
<先在 aTrust 连接 https://trust.aispeech.com.cn:4430>
ssh sjtu-hpc
# 在 JumpServer 输入 p，再输入 1
```

登录、代码同步和首个最小作业已经完成。`pdgpu-ezkws` 实测为 RTX 2080 Ti 11 GB；`pdgpu-a10` 探测作业仍在排队。下一步先取得 A10 分区实测结果，再选择适合 7B 模型的卡数和参数；当前不上传模型。

## 新同步规则

只有在新任务明确启动后，才创建同步清单。每条同步项必须写清：

| 本地路径 | 远程路径 | 用途 | 是否可删除 |
| --- | --- | --- | --- |
|  |  |  |  |

同步前必须确认：

- 本地文件属于当前新任务；
- 远程路径位于计划项目根目录 `/hpc_stor03/sjtu_home/feiyang.ying/AgentCommReliability`；
- 不覆盖共享模型、共享环境或其他项目目录；
- 大文件、模型和数据集已经在 `server_resource_inventory.md` 里登记或获准。

## 产物拉回规则

未来每个远程 run 应该有独立目录。拉回时只拉回该 run 的 README、manifest、摘要、小日志和必要样本。大型 raw outputs 默认留在远程，并在 run note 中记录路径。旧 A800 路径只用于解释历史记录，不作为新同步目的地。
