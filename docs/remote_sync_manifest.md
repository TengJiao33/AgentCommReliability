# 远程同步清单

日期：2026-06-20

## 作用

这份文件规定本地仓库和远程 A800_2 工作区之间的最小同步集合。运行前先检查这里，避免本地脚本、输入包和远程工作区错位。

远程工作区：

```text
A800_2:/data/xuhaoming/yfy/research_workspace
```

## 运行前检查

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "hostname; whoami; pwd; nvidia-smi --query-gpu=index,name,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits"
```

如果 A800_2 有其他用户或任务活跃，暂停模型运行。

GPU 使用默认规则：

- 默认使用 GPU 7。
- GPU 0 到 6 尽量不用；只有用户明确允许时才使用。
- 如果 GPU 7 忙，先暂停并汇报，不自动切到前面的卡。

## 必须同步的脚本

| 本地路径 | 远程路径 | 用途 |
| --- | --- | --- |
| `scripts/run_hsa_v0_sseac_a8002.sh` | `scripts/run_hsa_v0_sseac_a8002.sh` | HSA A800_2 包装入口 |
| `scripts/run_sseac_v0_pg40_a8002.sh` | `scripts/run_sseac_v0_pg40_a8002.sh` | PG40 A800_2 包装入口 |
| `scripts/run_pg40_direct_routing_a8002.sh` | `scripts/run_pg40_direct_routing_a8002.sh` | PG40 direct routing A800_2 包装入口 |
| `scripts/run_pg40_pairwise_role_card_selector_a8002.sh` | `scripts/run_pg40_pairwise_role_card_selector_a8002.sh` | PG40 pairwise role-card selector A800_2 包装入口 |
| `scripts/run_perspectivegap_official_fullgrid_a8002.sh` | `scripts/run_perspectivegap_official_fullgrid_a8002.sh` | PerspectiveGap 官方全量公开 benchmark direct baseline 包装入口 |
| `scripts/run_hsa_v0_sseac_openai_compatible.py` | `scripts/run_hsa_v0_sseac_openai_compatible.py` | HSA 通用模型调用 |
| `scripts/run_sseac_v0_pg40_openai_compatible.py` | `scripts/run_sseac_v0_pg40_openai_compatible.py` | PG40 通用模型调用 |
| `scripts/run_pg40_direct_routing_openai_compatible.py` | `scripts/run_pg40_direct_routing_openai_compatible.py` | PG40 direct routing 通用模型调用 |
| `scripts/run_pg40_pairwise_role_card_selector_openai_compatible.py` | `scripts/run_pg40_pairwise_role_card_selector_openai_compatible.py` | PG40 pairwise role-card selector 通用模型调用 |
| `scripts/compile_sseac_v0.py` | `scripts/compile_sseac_v0.py` | SSEAC 编译器 |
| `scripts/augment_hsa_predictions.py` | `scripts/augment_hsa_predictions.py` | HSA 后置补全器 |
| `scripts/audit_hsa_seed_shortlist.py` | `scripts/audit_hsa_seed_shortlist.py` | HSA seed 准入审计 |
| `scripts/merge_hsa_packet_artifacts.py` | `scripts/merge_hsa_packet_artifacts.py` | HSA 包和透明控制合并 |
| `scripts/build_hsa_p0p1_seed_expansion_drafts.py` | `scripts/build_hsa_p0p1_seed_expansion_drafts.py` | HSA P0/P1 33 行与 P0/P1/P2 36 行草包构建 |
| `scripts/score_hsa_v0_compiled.py` | `scripts/score_hsa_v0_compiled.py` | HSA 评分器 |
| `scripts/score_sseac_pg40_compiled.py` | `scripts/score_sseac_pg40_compiled.py` | PG40 评分器 |
| `scripts/score_perspectivegap_tight_budget.py` | `scripts/score_perspectivegap_tight_budget.py` | PG40 原始评分依赖 |

同步命令：

```powershell
scp scripts/run_hsa_v0_sseac_a8002.sh scripts/run_sseac_v0_pg40_a8002.sh scripts/run_pg40_direct_routing_a8002.sh scripts/run_pg40_pairwise_role_card_selector_a8002.sh scripts/run_perspectivegap_official_fullgrid_a8002.sh scripts/run_hsa_v0_sseac_openai_compatible.py scripts/run_sseac_v0_pg40_openai_compatible.py scripts/run_pg40_direct_routing_openai_compatible.py scripts/run_pg40_pairwise_role_card_selector_openai_compatible.py scripts/compile_sseac_v0.py scripts/augment_hsa_predictions.py scripts/audit_hsa_seed_shortlist.py scripts/merge_hsa_packet_artifacts.py scripts/build_hsa_p0p1_seed_expansion_drafts.py scripts/score_hsa_v0_compiled.py scripts/score_sseac_pg40_compiled.py scripts/score_perspectivegap_tight_budget.py A800_2:/data/xuhaoming/yfy/research_workspace/scripts/
```

远程校验：

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "cd /data/xuhaoming/yfy/research_workspace && chmod +x scripts/run_hsa_v0_sseac_a8002.sh scripts/run_sseac_v0_pg40_a8002.sh scripts/run_pg40_direct_routing_a8002.sh scripts/run_pg40_pairwise_role_card_selector_a8002.sh scripts/run_perspectivegap_official_fullgrid_a8002.sh && bash -n scripts/run_hsa_v0_sseac_a8002.sh scripts/run_sseac_v0_pg40_a8002.sh scripts/run_pg40_direct_routing_a8002.sh scripts/run_pg40_pairwise_role_card_selector_a8002.sh scripts/run_perspectivegap_official_fullgrid_a8002.sh"
```

## PerspectiveGap 官方全量评分缓存

PerspectiveGap 的 prompt-writing scorer 需要 `Qwen/Qwen3.5-0.8B` tokenizer。A800_2 不能直接访问 Hugging Face 时，需要先同步本地 cache：

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 'mkdir -p ~/.cache/huggingface/hub'
scp -r "$env:USERPROFILE\.cache\huggingface\hub\models--Qwen--Qwen3.5-0.8B" A800_2:~/.cache/huggingface/hub/
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 'cd /data/xuhaoming/yfy/research_workspace/baselines/PerspectiveGap/upstream && PY=/data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python; PYTHONPATH=src HF_HUB_OFFLINE=1 "$PY" scripts/score_predictions.py --predictions tests/fixtures/example_predictions.jsonl'
```

## 必须同步的输入包

| 本地路径 | 远程路径 | 用途 |
| --- | --- | --- |
| `experiments/20260619-local-hsa-v0-extended15-packet/hsa_v0_packet.jsonl` | 同路径 | HSA-v0 15 行输入包 |
| `experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/packet/hsa_v0_packet.jsonl` | 同路径 | HSA-v0 33 行 P0/P1 输入包 |
| `experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl` | 同路径 | HSA-v0 36 行 P0/P1/P2 输入包 |
| `experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl` | 同路径 | PG40 SSEAC 输入包 |
| `experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl` | 同路径 | PG40 原始评分包 |

同步命令：

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "WORK=/data/xuhaoming/yfy/research_workspace; mkdir -p `$WORK/experiments/20260619-local-hsa-v0-extended15-packet `$WORK/experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/packet `$WORK/experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet `$WORK/experiments/20260618-local-sseac-v0-pg40-adapter `$WORK/experiments/20260618-local-perspectivegap-tight-budget-v0"
scp experiments/20260619-local-hsa-v0-extended15-packet/hsa_v0_packet.jsonl A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-extended15-packet/
scp experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/packet/hsa_v0_packet.jsonl A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/packet/
scp experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/
scp experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-sseac-v0-pg40-adapter/
scp experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl A800_2:/data/xuhaoming/yfy/research_workspace/experiments/20260618-local-perspectivegap-tight-budget-v0/
```

## 远程文件存在性检查

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 'WORK=/data/xuhaoming/yfy/research_workspace; cd "$WORK" && for p in scripts/run_hsa_v0_sseac_a8002.sh scripts/run_sseac_v0_pg40_a8002.sh scripts/run_pg40_direct_routing_a8002.sh scripts/run_pg40_pairwise_role_card_selector_a8002.sh scripts/run_hsa_v0_sseac_openai_compatible.py scripts/run_sseac_v0_pg40_openai_compatible.py scripts/run_pg40_direct_routing_openai_compatible.py scripts/run_pg40_pairwise_role_card_selector_openai_compatible.py scripts/compile_sseac_v0.py scripts/augment_hsa_predictions.py scripts/audit_hsa_seed_shortlist.py scripts/merge_hsa_packet_artifacts.py scripts/build_hsa_p0p1_seed_expansion_drafts.py scripts/score_hsa_v0_compiled.py scripts/score_sseac_pg40_compiled.py scripts/score_perspectivegap_tight_budget.py experiments/20260619-local-hsa-v0-extended15-packet/hsa_v0_packet.jsonl experiments/20260619-local-hsa-v0-p0p1-seed-expansion33-draft/packet/hsa_v0_packet.jsonl experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl experiments/20260618-local-sseac-v0-pg40-adapter/sseac_pg40_packet.jsonl experiments/20260618-local-perspectivegap-tight-budget-v0/tight_budget_rotated20.jsonl; do if [ -s "$p" ]; then echo PRESENT "$p"; else echo MISSING "$p"; fi; done'
```

## 产物拉回规则

每次远程运行结束后拉回整个运行目录：

```powershell
scp -r A800_2:/data/xuhaoming/yfy/research_workspace/experiments/<run-id> experiments/
```

拉回后必须更新：

| 文件 | 更新内容 |
| --- | --- |
| `experiments/<run-id>/README.md` | 运行状态、命令、结果或失败类型 |
| `docs/current_evidence_ledger.md` | 证据等级和下一步 |
| `active/<route>/README.md` | 当前停点 |
| `reports/<date>-<topic>.md` | 只有当结果改变判断时才写 |

## 当前保守运行建议

HSA P0/P1/P2 36 行复现：

```bash
cd /data/xuhaoming/yfy/research_workspace
PROMPT_CONTRACT=constraint_recall GPU_ID=7 PORT=<free-port> RUN_ID=<new-run-id> LIMIT=0 PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl GPU_MEMORY_UTILIZATION=0.80 MAX_MODEL_LEN=16384 MAX_TOKENS=3072 bash scripts/run_hsa_v0_sseac_a8002.sh
```

HSA 默认提示契约是 `baseline`。已跑过的 full9 变体包括 `recall_sweep`、`focused_recall`、`constraint_recall`；复现或继续压力测试时需要显式设置：

```bash
PROMPT_CONTRACT=constraint_recall GPU_ID=7 PORT=<free-port> RUN_ID=<new-run-id> LIMIT=0 PACKET=/data/xuhaoming/yfy/research_workspace/experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl GPU_MEMORY_UTILIZATION=0.80 MAX_MODEL_LEN=16384 MAX_TOKENS=3072 bash scripts/run_hsa_v0_sseac_a8002.sh
```

PG40 五行：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=<free-port> RUN_ID=<new-run-id> LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 bash scripts/run_sseac_v0_pg40_a8002.sh
```

PG40 direct routing 五行：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=<free-port> RUN_ID=20260619-a8002-pg40-direct-routing-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=2048 bash scripts/run_pg40_direct_routing_a8002.sh
```

PG40 pairwise role-card selector 五行负结果复现：

```bash
cd /data/xuhaoming/yfy/research_workspace
GPU_ID=7 PORT=<free-port> RUN_ID=20260620-a8002-pg40-pairwise-selector-limit5-qwen25-14b LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 bash scripts/run_pg40_pairwise_role_card_selector_a8002.sh
```

该 run 已完成，读数是 model-only/compiler `0/5`、utility `0.0000`、parse clean。当前不扩 pairwise full40；下一步先修 role/recipient interface，或转回 PerspectiveGap official role-assignment arms。

PG40 默认提示契约是 `cardunit`。只有复现已退休的角色计划诊断时才加：

```bash
PROMPT_CONTRACT=roleplan GPU_ID=7 PORT=<free-port> RUN_ID=<new-run-id> LIMIT=5 GPU_MEMORY_UTILIZATION=0.75 MAX_MODEL_LEN=8192 MAX_TOKENS=3072 bash scripts/run_sseac_v0_pg40_a8002.sh
```

如果 GPU 7 已有明显占用，暂停运行并汇报。
