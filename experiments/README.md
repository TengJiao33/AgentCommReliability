# Experiments

本目录保存当前 live workspace 的实验 run 记录、日志和结果文件。

## 本地已归档的当前标准配置 Run

- `standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/`：标准 MAD 4096 输出预算基线，完成；initial majority 364/500，final 378/500。
- `cpac-dcac-guard-v1-math500-20260706-standard-fixed-qwen25-7b-full-4096-a8002/`：CPAC/DCAC guard-v1 standard-fixed 诊断，完成；initial majority 364/500，final 368/500。

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
