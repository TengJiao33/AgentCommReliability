# 远程同步清单

日期：2026-07-03

## 当前状态

当前没有需要同步到远程的实验脚本、输入包或运行目录。旧同步清单已经作废。

远程项目根仍保留为：

```text
A800_2:/data/xuhaoming/yfy/research_workspace
```

## 运行前检查

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "hostname; whoami; pwd; nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits"
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "df -h /data /mnt/quarkfs"
```

如果 A800_2 有其他用户或任务活跃，暂停模型运行并先汇报。

## 新同步规则

只有在新任务明确启动后，才创建同步清单。每条同步项必须写清：

| 本地路径 | 远程路径 | 用途 | 是否可删除 |
| --- | --- | --- | --- |
|  |  |  |  |

同步前必须确认：

- 本地文件属于当前新任务；
- 远程路径位于 `/data/xuhaoming/yfy/research_workspace`；
- 不覆盖共享模型、共享环境或其他项目目录；
- 大文件、模型和数据集已经在 `server_resource_inventory.md` 里登记或获准。

## 产物拉回规则

未来每个远程 run 应该有独立目录。拉回时只拉回该 run 的 README、manifest、摘要、小日志和必要样本。大型 raw outputs 默认留在远程，并在 run note 中记录路径。
