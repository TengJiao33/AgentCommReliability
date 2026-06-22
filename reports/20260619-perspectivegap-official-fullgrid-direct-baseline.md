# PerspectiveGap 官方全量 direct baseline

日期：2026-06-19

## 结论

PerspectiveGap 官方全量公开 benchmark 已经跑完一条同模型 direct baseline。Qwen2.5-14B 在官方 runner 默认提示下得到 `2/440` combined strict pass，其中 role assignment 是 `0/220`，prompt writing 是 `2/220`。

这个结果的意义不是“我们有方法优势”，而是把公开基准锚点补上了。PG40 五行和四十行继续只能作为 public-slice pressure；对外方法有效性必须回到这种 full-grid 证据。

## 合规状态

| 项 | 结果 |
| --- | --- |
| 官方网格 | `110` scenarios x seeds `1,42` x `2` tasks |
| prediction rows | `440` |
| score rows | `440` |
| request status | `ok: 440` |
| scorer | official `scripts/score_predictions.py` |
| runner | official `scripts/run_model_predictions.py` |
| upstream commit | `60b1dcaaeeb40619075f6cd8779c47fa4b344391` |
| run record | `experiments/20260619-a8002-perspectivegap-official-fullgrid-direct-qwen25-14b/README.md` |

## 官方分数

| Task | Strict pass | Net match | Required coverage | Boundary precision | Distractor leakage |
| --- | ---: | ---: | ---: | ---: | ---: |
| role-fragment assignment | `0/220` | `0.1953` | `0.6063` | `0.7714` | `0.3409` |
| free-form prompt writing | `2/220` | `0.2816` | `0.5483` | `0.8970` | `0.3136` |

Combined pass:

```text
2/440 = 0.45%
```

## 怎么读

第一，direct prompt 很弱。模型能覆盖一部分 needed fragments，也有相对高的 boundary precision，但严格全对几乎没有。这说明 PerspectiveGap 的 full grid 对 role-specific routing 有真实压力，不是一个普通 free-form prompt 能顺手解决的任务。

第二，这条 baseline 不能单独支撑方法 claim。若下一条 system route 只是从 `2/440` 提高到一个低数字，仍然要和更强 route、source-ledger、transparent heuristic、oracle/control gap 同表比较。

第三，PG40 不能再承担主证据幻想。PG40 的正确位置是开发切片和压力表：它暴露预算、排序、角色分配和强透明基线压力；它不等同于 PerspectiveGap 官方 leaderboard 网格。

## 追加对照

我又补了一个不烧 GPU 的 full-grid control：把 direct baseline 的 `220` 行 role-assignment 预测 deterministic 转成 prompt-writing rows，再交给官方 scorer。结果是 role assignment `0/220`，converted prompt writing `0/220`，combined `0/440`。

这说明瓶颈在 role-fragment assignment 本身。单纯把模型已选 fragments 渲染成更干净的 prompt，不会救 direct route。

记录见 `experiments/20260619-local-perspectivegap-fullgrid-direct-role-to-prompt-qwen25-14b/README.md`。

## 下一步

下一条应该是 full-grid no-gold system route：

```text
role_assignment system predictions
-> deterministic assignment-to-prompt conversion
-> official scorer
```

最低门槛不是“赢 direct baseline 就庆祝”，而是同网格、同 scorer、同模型下形成可解释增益，并且没有 prediction-time gold leakage、oracle-derived fields、scorer artifact 或 post-processing 偷换。
