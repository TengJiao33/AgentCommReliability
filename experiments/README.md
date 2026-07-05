# Experiments

本目录保存当前 live workspace 的实验 run 记录、日志和结果文件。

## 当前标准配置 Run

- `20260705-a8002-math500-standard-mad-qwen25-7b-full-4096/`：标准 MAD 4096 输出预算基线。
- `20260705-a8002-math500-cpac-dcac-guard-v1-standard-qwen25-7b-full-4096/`：CPAC/DCAC guard-v1 标准配置诊断。
- `20260705-a8002-math500-mca-text-audit-standard-qwen25-7b-full-4096/`：MCA-T audit 标准配置诊断。
- `20260705-a8002-math500-mca-soft-prefix-standard-qwen25-7b-full-4096/`：MCA-P soft-prefix 标准配置诊断。

## 旧复现和基线

- `20260704-a8002-math500-mad-mm-qwen25-7b-full/`：MAD-MM/MAD-M2 MATH-500 local reproduction。
- `20260704-a8002-aime24-25-mad-mm-qwen25-7b-full/`：MAD-MM/MAD-M2 AIME24/25 local reproduction。
- `20260704-a8002-aime24-25-basic-mad-full/`：basic MAD AIME24/25 baseline。
- `20260704-a8002-aime24-25-cot-sc-full/`：CoT self-consistency AIME24/25 baseline。
- `20260704-a8002-gsm8k-basic-mad-full/`：basic MAD GSM8K baseline。

## Templates

- `experiments/_templates/run_README.md`
- `experiments/_templates/manifest.json`
