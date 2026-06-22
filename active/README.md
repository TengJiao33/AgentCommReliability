# 当前活跃入口

日期：2026-06-20

## 作用

这个目录是项目当前态入口。它只索引当前活跃路线，不存放大实验产物，也不替代 `experiments/` 和 `reports/`。

使用顺序：

1. 先看本文件，确认当前活跃路线。
2. 再看对应路线目录，例如 `active/hsa/README.md` 或 `active/pg40/README.md`。
3. 需要数字和证据等级时，看 `docs/current_evidence_ledger.md`。
4. 需要远程运行前检查时，看 `docs/remote_sync_manifest.md`。
5. 需要整理规则时，看 `docs/project_physical_management.md`。

## 当前活跃路线

| 路线 | 状态 | 当前判断 | 下一步 |
| --- | --- | --- | --- |
| `pg40` | 公开基准主线 | direct 五行 `0/5`、utility `0.0987`；单卡候选契约五行 `1/5`、utility `0.8155`；scope projection 后处理五行 `5/5`、full40 14B `17/40`；no-scope 规则 selector full40 `0/40`；pairwise selector 五行 `0/5`、utility `0.0000`、parse clean | 不扩 pairwise full40；修 role/recipient interface，或回到 official role-assignment arms |
| `hsa` | 内部机制诊断 | 三十六行真跑支撑型窄补全后硬准入 `36/36`，extra final cards `42`，全范围控制为 `195`；旧包重放干净 | 暂停扩包；保留为机制表和附表 |

## 冻结路线

以下路线暂时不新开实验，只作为背景、附表或防错材料：

| 路线 | 当前用途 |
| --- | --- |
| `state_admission_v1` | 方法候选背景和失败/成功边界 |
| `pact` | 分裂证据和公共状态设计背景 |
| `typecast_math` | 机制显微镜和解析/金标防错 |
| `hiddenbench_large` | 通信必要性背景和 HSA 来源 |
| `mad_dar_moc` | 早期复现经验和附表背景 |

## 更新规则

- 新实验先更新对应路线的 `active/<route>/README.md`，再启动远程运行。
- 运行结束后更新 `experiments/<run-id>/README.md` 和 `docs/current_evidence_ledger.md`。
- 失败必须标明类型：工程失败、设计失败、数据失败、评测失败或真负结果。
- 不再把本地环境没有模型服务当作研究阻塞；远程运行默认走 A800_2 包装脚本。
- 后续远程运行默认使用 GPU 7；GPU 0 到 6 只在用户明确允许时使用。
