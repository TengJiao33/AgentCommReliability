# 项目物理管理规则

日期：2026-06-19

## 核心规则

项目当前采用“活跃入口 + 证据总账 + 原始产物保留”的管理方式。旧实验目录暂不大规模移动，避免打断已有路径；当前态通过 `active/` 和 `docs/current_evidence_ledger.md` 管理。

## 目录职责

| 目录 | 职责 | 不该承担 |
| --- | --- | --- |
| `active/` | 当前活跃路线入口和下一步 | 原始输出、大日志、大输入包 |
| `docs/` | 总账、索引、规则、论文表草稿 | 单次运行的完整日志 |
| `experiments/` | 每次运行的事实记录、输入、输出、日志 | 长篇论文解释 |
| `reports/` | 解释结果、判断变化、路线总结 | 替代运行目录 |
| `scripts/` | 可复现构建、运行、编译、评分入口 | 随手临时脚本长期堆放 |
| `papers/` | 外部论文材料和阅读证据 | 项目内部运行结果 |
| `skills/` | 项目工作纪律 | 单次实验说明 |

## 当前入口

| 问题 | 入口 |
| --- | --- |
| 我现在该看什么 | `active/README.md` |
| 当前证据等级是什么 | `docs/current_evidence_ledger.md` |
| A800_2 运行前同步什么 | `docs/remote_sync_manifest.md` |
| HSA 当前停在哪里 | `active/hsa/README.md` |
| PG40 当前停在哪里 | `active/pg40/README.md` |
| 数字表体系在哪里 | `docs/owned_results_table_index.md` |

## 实验目录规范

每个新的 `experiments/<run-id>/README.md` 第一屏必须包含：

```text
状态：
路线：
等级：
本地路径：
远程路径：
输入包：
运行命令：
模型和显卡：
结果摘要：
失败类型：
下一步：
```

状态只使用下列值：

| 状态 | 用法 |
| --- | --- |
| `MAIN_EVIDENCE` | 可进入主表或主叙事 |
| `DIAGNOSTIC_PILOT_COMPLETE` | 小样本或机制诊断完成 |
| `EXECUTION_FAILURE_NO_BEHAVIOR_RESULT` | 运行失败，无行为结果 |
| `DESIGN_FAILURE` | 实验设计没有回答原问题 |
| `EVALUATOR_FAILURE` | 评分、解析或金标问题 |
| `TRUE_NEGATIVE` | 干净设置下没有出现目标效果 |
| `ARCHIVED_BACKGROUND` | 只保留为背景 |

## 报告规范

`reports/` 只在判断变化时新增报告。报告应回答：

```text
现在相信什么？
证据来自哪里？
这说明什么机制？
边界是什么？
下一步最小压力是什么？
```

单次工程失败可以只写在实验目录 README；只有当失败改变工作流时才写报告。

## 脚本规范

脚本命名优先使用固定模式：

| 模式 | 用途 |
| --- | --- |
| `build_<route>_*.py` | 构建输入包 |
| `run_<route>_openai_compatible.py` | 通用模型调用 |
| `run_<route>_a8002.sh` | A800_2 包装运行入口 |
| `compile_<route>*.py` | 编译或后处理 |
| `score_<route>*.py` | 评分 |
| `summarize_<route>*.py` | 汇总和成对差 |

历史脚本暂时不移动。新活跃路线必须在 `active/<route>/README.md` 指向唯一推荐入口。

## 远程运行规范

远程运行前必须完成：

1. 查看 `docs/remote_sync_manifest.md`。
2. 检查 A800_2 是否有人或任务活跃。
3. 确认脚本、输入包、评分依赖在远程存在。
4. 写清楚 run id、显卡、端口、模型路径、输出目录。
5. 使用保守显存配置，除非机器明确空闲。
6. 默认使用 GPU 7；GPU 0 到 6 只在用户明确允许时使用。

远程运行后必须完成：

1. 确认没有本项目残留进程。
2. 拉回运行目录。
3. 更新运行目录 README。
4. 更新 `docs/current_evidence_ledger.md`。
5. 只有判断变化时新增报告。

## 归档策略

当前不大规模搬动旧实验。归档分两阶段：

| 阶段 | 动作 |
| --- | --- |
| 第一阶段 | 用 `active/` 和 `docs/current_evidence_ledger.md` 收束当前态 |
| 第二阶段 | 只移动明确冻结且路径已被总账替代的材料 |

移动文件前必须先确认：

- 是否有报告引用该路径；
- 是否有脚本默认读取该路径；
- 是否有远程镜像需要保留；
- 是否能用新索引找到旧证据。

## 禁止事项

- 不在 A800_2 有他人活跃时抢卡。
- 不自动改用 GPU 0 到 6。
- 不把工程失败写成模型行为。
- 不让本地未同步脚本直接决定远程运行。
- 不让一个实验同时承担多个路线判断。
- 不新增没有 README 的 claim-bearing 实验目录。
