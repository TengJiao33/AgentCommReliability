# Experiments

本目录保存当前 live workspace 的实验 run 记录、日志和结果文件。

## 当前待迁移与待跑

自 `2026-07-12` 起，新实验默认目标为新获批的逻辑远端 `X_LANCE_HPC`，账号 `fyy05`。较新的 Wiki 线索指向需要单独 VPN 的贵州超算；当前缺少该 VPN 租户/网关和现行 SSH 地址，因此具体调度系统、GPU 节点、项目根目录和可用环境待设备委员确认及首登核验。旧 `A800_2` 公钥已失效，历史 run 中的主机、路径、PID 和队列状态不再视为当前可执行状态。

- `20260709-a8002-mca-question-token-anchored-delta-disagreement50-qwen25-7b/`：源码、测试和 50 题启动合同已存在，但没有结果；旧 A800 等待器状态作废，迁移后优先做硬件兼容性检查和小样本预检。
- `20260709-a8002-mca-text-anchored-delta-smoke-qwen25-7b/`：旧机运行在第 5 题前被外部终止，只留下 4 行部分记录；迁移后需要完整跑完 5 题 smoke，不能把部分读数当作结果。

## 本地已归档的当前标准配置 Run

- `standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/`：标准 MAD 4096 输出预算基线，完成；initial majority 364/500，final 378/500。
- `cpac-dcac-guard-v1-math500-20260706-standard-fixed-qwen25-7b-full-4096-a8002/`：CPAC/DCAC guard-v1 standard-fixed 诊断，完成；initial majority 364/500，final 368/500。
- `20260708-a8002-mca-natural-search-delta-disagreement50-qwen25-7b/`：natural-search-delta 首跑记录，远端完成 50 条；同题 delta 为 26/50，和随机同范数同分，不支撑扩大运行。
- `20260707-a8002-mca-latent-rounds-gpu1-qwen25-7b/`：latent safe variants 启动与汇总记录，四个 50 条远端 run 已补齐；未触发 full MATH500 扩大条件。

## 本地启动记录，远端状态需另查

- `cpac-dcac-guard-v1-math500-20260705-standard-qwen25-7b-full-4096-a8002/`：旧 CPAC/DCAC guard-v1 标准配置诊断。本地只有启动记录；远端 summary 显示 initial majority 313/500，final 327/500。
- `mca-text-audit-math500-20260705-standard-qwen25-7b-full-4096-a8002/`：MCA-T audit 启动记录。本地无 summary。
- `mca-soft-prefix-math500-20260705-standard-qwen25-7b-full-4096-a8002/`：MCA-P soft-prefix 启动记录。本地无 summary。

## 远端已观察但本地未归档

- `A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-text-audit-standard-madmm-aligned-qwen25-7b-full/`：MCA-T audit aligned 完成；initial majority 364/500，final 357/500。
- `A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260706-a8002-math500-mca-soft-prefix-standard-madmm-aligned-qwen25-7b-full/`：MCA-P soft-prefix aligned 运行中，当前本地没有 summary。

## 旧复现

- `mad-mm-math500-20260704-qwen25-7b-full-a8002/`：MAD-MM/MAD-M2 MATH-500 local reproduction。
- `mad-mm-aime24-25-20260704-qwen25-7b-full-a8002/`：MAD-MM/MAD-M2 AIME24/25 local reproduction。

## Templates

- `experiments/_templates/run_README.md`
- `experiments/_templates/manifest.json`
