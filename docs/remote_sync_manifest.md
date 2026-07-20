# 远程同步清单

日期：2026-07-12

## 当前状态

旧 `A800_2` 同步清单已经作废。后续默认远端改为逻辑目标 `X_LANCE_HPC`；较新的 Wiki 指向需要单独 VPN 的贵州超算，但 VPN 租户/网关、SSH 首登、GPU 节点、项目根目录、配额和环境尚未核验，因此当前禁止执行批量同步或上传模型。

当前入口状态：

```text
用户: fyy05
VPN: 待提供贵州超算租户/网关
SSH: 待提供现行主机和端口
```

项目根目录：待在具体 GPU 节点上确认。

## 待迁移任务

| 任务 | 源码状态 | 远端状态 |
| --- | --- | --- |
| Question-Token Anchored Delta disagreement50 | runner、测试和启动脚本已存在 | 旧 A800 队列作废；待新集群首登后做兼容性检查和首跑 |
| Text-Anchored Delta smoke | runner、测试和 smoke 脚本已存在；旧机只产生 4 行部分记录 | 待新集群完成 5 题 smoke |
| Receiver-Conditioned Complementary Latent Communication | 仅有设计和实验矩阵 | 尚无专用 runner/test，不进入远程同步 |

## 运行前检查

```powershell
<先登录贵州超算 VPN>
ssh -p <confirmed-port> fyy05@<confirmed-host>
```

只有设备委员确认 VPN 和 SSH 入口后才执行。登录后先查看调度分区、GPU 型号和使用规则，再申请最小测试资源；随后检查 `hostname`、`nvidia-smi`、`df -h`、配额和活跃进程。

## 新同步规则

只有在新任务明确启动后，才创建同步清单。每条同步项必须写清：

| 本地路径 | 远程路径 | 用途 | 是否可删除 |
| --- | --- | --- | --- |
|  |  |  |  |

同步前必须确认：

- 本地文件属于当前新任务；
- 远程路径位于首登后确认的项目根目录；
- 不覆盖共享模型、共享环境或其他项目目录；
- 大文件、模型和数据集已经在 `server_resource_inventory.md` 里登记或获准。

## 产物拉回规则

未来每个远程 run 应该有独立目录。拉回时只拉回该 run 的 README、manifest、摘要、小日志和必要样本。大型 raw outputs 默认留在远程，并在 run note 中记录路径。旧 A800 路径只用于解释历史记录，不作为新同步目的地。
