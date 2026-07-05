# Active

当前有一条活跃研究路线：MATH 多 agent reasoning 中的 candidate-pool state diagnosis 与证书化共识机制。

## 核心问题

当前证据指向一个分解：多 agent 失败不只来自 agent 是否会 debate，还来自候选池状态是否适配后续决策协议。

- `unique=1`：候选池 collapse。若全体同错，CQG/DCAC 这类分歧机制没有可用抓手。
- `unique=2`：majority/minority。当前 CQG 证明这里有可恢复空间，但也会释放错误 minority。
- `unique=3+`：no-majority conflict。当前 CQG 基本没有处理这一块。

## 当前机制假说

`CPAC` 可以作为外层控制器：先诊断候选池状态，再决定使用哪个协议。

`DCAC` 可以作为 CPAC 的 `unique=2` 分支：只有当 minority 通过由 answer delta 生成的 discriminant certificate，才允许推翻 majority。

`MCE` 可以作为 CPAC 的通信动作：当答案候选本身不可靠时，交换 answer-free 的认知 cue，用来测试局部认知贡献是否能被其他 agent 吸收。

## 证据状态

- CQG full MATH-500：记录内 same-run initial majority 320/500，CQG final 337/500，净增 17 题。
- CQG 的增益不能归因于 appeal gate：valid appeal rate 只有 35/189，抽样恢复更多来自 blind re-solve/review。
- CPAC+DCAC full MATH-500：记录内 same-run initial majority 320/500，CPAC+DCAC final 325/500，净增 5 题。分支分解显示正净值来自 no-majority listwise 分支，DCAC 分支本身为负。
- Candidate-space 调查显示，初始 3-agent 池有 `unique=1/2/3` 三态；`unique=2` 和 `unique=3` 都存在 identification 空间，`unique=1` 中存在 coverage collapse。
- MAD-MM/MATH500 复现没有支持 memory masking 优于 naive debate。

## 边界

当前路线已有 CPAC+DCAC diagnostic full run，但还没有支持方法 claim 的结果。CQG 是已实现并跑过 full split 的诊断基线；CPAC+DCAC 已有 `scripts/run_cpac_dcac.py` runner 和 full-run 记录；MCE 仍是由 CQG 失败模式和候选池调查推出来的机制草图。

当前 evaluator 对 representation-risk 格式仍需统一口径，尤其是 `\pi`、矩阵/列向量、base notation、函数表达式等答案类型。
