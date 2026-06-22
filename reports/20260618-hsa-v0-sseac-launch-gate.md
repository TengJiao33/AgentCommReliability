# HSA-v0 SSEAC Limit3 Launch Gate

日期：2026-06-18

现状修正（2026-06-19）：这个 launch gate 已被后续 9 行、15 行、33 行和 36 行 HSA 真跑吸收。当前对外报告主线已经转向 PG40 / PerspectiveGap 公开切片主表；本报告只作为 HSA 历史运行门记录。

## 核心判断

`HSA-v0 model row` 在当时已经推进到 launch gate。runner、packet、limit3 prompt、transparent controls 和 leak check 都已准备好；2026-06-19 已补上项目惯用的 A800_2 包装运行脚本 `scripts/run_hsa_v0_sseac_a8002.sh`。这个状态当时足以发起远程 A800_2 三行模型预测，但还没有产生方法效果；后续已经被更大 HSA 诊断链路吸收。

修正说明：本报告原先写“只缺 openai-compatible endpoint”。这个词来自 runner 参数名，不属于研究概念。项目实际工作流一直是远程 A800_2 上临时启动 vLLM，再由脚本调用远程机器本地的 `127.0.0.1:<port>/v1`。因此真实缺口是 A800_2 包装运行路径；“端点”只是接口参数名。

这一步的价值是让 HSA-v0 和 PG40 同时进入“A800_2 小样本即可执行”的状态。PG40 负责外部 routing / budget baseline 压力，HSA-v0 负责 HiddenBench-derived downstream decision、insufficient evidence 和 over-admission 指标。

## 证据链

本地静态检查通过：

```powershell
python -m py_compile scripts\run_hsa_v0_sseac_openai_compatible.py scripts\build_hsa_v0_sseac_packet.py scripts\score_hsa_v0_compiled.py scripts\compile_sseac_v0.py
```

`limit 3` dry-run prompt 生成成功：

```json
{
  "rows": 3,
  "dry_run_prompts_out": "experiments\\20260618-local-hsa-v0-sseac-launch-gate\\dry_run_prompts_limit3.jsonl"
}
```

prompt 规模：

| Metric | Value |
| --- | ---: |
| rows | 3 |
| base rows | 1 |
| perturbation rows | 2 |
| prompt chars min | 5548 |
| prompt chars max | 5575 |
| prompt chars avg | 5565.67 |
| source cards | 7 per row |

精确 evaluator-only 字段检查无命中：

```text
required_slots
acceptable_card_ids
slot_id
expected_final_decision
gold_answer
oracle_unit_ids
downstream_scoring_obligations
hsa_meta
```

## A800_2 执行路径状态

历史检查只说明本地 Windows 环境没有正在监听的模型服务：

```text
OPENAI_API_KEY=<unset>
OPENAI_BASE_URL=<unset>
VLLM_BASE_URL=<unset>
LOCAL_OPENAI_BASE_URL=<unset>
A8002_BASE_URL=<unset>
```

常用本地 vLLM 端口 `8000`、`8001`、`8002`、`8008`、`8010`、`8047`、`8051`、`8053` 均未监听。因此本轮没有发起模型调用；这不影响远程 A800_2 工作流。

## 对主表的意义

HSA-v0 现在有一组明确 transparent controls：

| Condition | Strict | Base strict | Perturb strict | Slot recall | Extra final cards | Forced commitment |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `oracle_admissible_facts` | 9/9 | 1.0000 | 1.0000 | 0.8333 | 0 | 0.0000 |
| `shared_only_verified` | 6/9 | 0.0000 | 1.0000 | 0.1759 | 24 | 0.3333 |
| `all_scoped_verified` | 9/9 | 1.0000 | 1.0000 | 0.8333 | 24 | 0.0000 |

这意味着 future model row 不能只看 strict。它必须同时报告 base strict、perturbation strict、slot recall、extra final cards 和 forced commitment。尤其是 `all_scoped_verified` 的 strict 是 `9/9`，但 extra final cards 是 `24`，这会暴露“全塞进去”的过度准入。

## 下一步压力

A800_2 小样本执行时只跑 `limit 3`。第一轮读数只看：

1. JSON schema 是否稳定；
2. compiler error rows 是否为 0；
3. base row 是否比 shared-only 更能支持正确答案；
4. 两个 perturbation rows 是否能维持 insufficient evidence；
5. extra final cards 是否低于 all-scoped。

若模型只是全收 facts 或扰动行强制作答，先改 prompt 或 scorer 表达。若 `limit 3` 出现可解释正信号，再扩到 9 行并填入 `docs/hsa_v0_numeric_rows.csv`。

## Artifacts

- Run record: `experiments/20260618-local-hsa-v0-sseac-launch-gate/README.md`
- Dry-run prompts: `experiments/20260618-local-hsa-v0-sseac-launch-gate/dry_run_prompts_limit3.jsonl`
- Runner: `scripts/run_hsa_v0_sseac_openai_compatible.py`
- Compiler: `scripts/compile_sseac_v0.py`
- Scorer: `scripts/score_hsa_v0_compiled.py`
- Numeric table: `docs/hsa_v0_numeric_main_table.md`
