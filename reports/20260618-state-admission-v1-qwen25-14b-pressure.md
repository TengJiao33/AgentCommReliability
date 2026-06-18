# State Admission V1.1 Qwen2.5-14B Pressure

## 核心判断

这轮给了一个更有用的信号：Qwen2.5-14B 能识别大量必要 source，但会把局部可用证据过度承认进角色上下文。默认 prompt 下，oracle 需要非空的 `78` 个角色全部被覆盖，oracle 应该为空的 `82` 个角色也全部被填；结果是 `0/40` strict，`global_budget_pass=0.000`。

budget-first prompt control 没有救活这个 benchmark。它把空角色填充从 `82/82` 降到 `68/82`，把 per-role 过预算从 `44/160` 降到 `10/160`，但开始漏掉必要 bundle，required coverage 从 `1.000` 掉到 `0.7914`，strict 仍是 `0/40`。

## 证据链

| Run | Strict | Coverage | Precision | Global budget pass | Global overrun | Utility | Raw utility | 空角色被填 | Oracle 非空角色 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| default Qwen2.5-14B | 0/40 | 1.0000 | 0.4025 | 0.0000 | 15.3250 | 0.0000 | 1.0307 | 82/82 | 63 exact + 15 superset / 78 |
| budget_first Qwen2.5-14B | 0/40 | 0.7914 | 0.4464 | 0.1000 | 7.1500 | 0.0203 | 0.8114 | 68/82 | 57 exact + 3 superset + 18 missing / 78 |
| eligible_all baseline | 0/40 | 1.0000 | 0.3019 | 0.0000 | 31.9250 | 0.0000 | 1.0307 | n/a | n/a |
| bundle_density_global baseline | 14/40 | 0.5092 | 0.3739 | 1.0000 | 0.0000 | 0.4492 | 0.4492 | n/a | n/a |
| group_density_global baseline | 32/40 | 0.9018 | 1.0000 | 1.0000 | 0.0000 | 0.9666 | 0.9666 | n/a | n/a |

Artifacts:

- `experiments/20260618-a8002-state-admission-v1-full40-qwen25-14b/`
- `experiments/20260618-a8002-state-admission-v1-budgetfirst-full40-qwen25-14b/`
- `experiments/20260618-local-state-admission-v1/summary_group_density_global.md`
- `experiments/20260618-local-state-admission-v1/prompt_audit_budget_first_stratified5.jsonl`

## 机制解释

默认 prompt 的失败形态很集中：模型会拿到必要 source，也会正确拒绝显然无资格的 source，但它几乎无法选择“这个角色这轮应该为空”。两个 full40 run 都完成 `40/40` 且没有 parse crash，所以 parser 错误解释不强。更合适的解释是 admission-boundary 问题：局部角色 bundle 一旦看起来有 utility，模型倾向于把它承认进上下文，即使全局预算要求只服务少数角色或少数组合。

budget-first control 把这个解释压得更实。提示显式要求先选 role set、允许空角色、额外角色会使答案 invalid；模型确实减少了过度承认，但同时牺牲必要覆盖。更准确地说，它读到了预算压力，却没有稳定执行“全局选择 -> 局部填充 -> 拒绝其余”的结构。

## 边界

这还不能支撑方法 claim。`group_density_global` 在同一 packet 上有 `32/40` strict 和 `0.967` utility ratio，所以当前 V1.1 更适合作为 model-vs-symbolic-admission pressure test。它还不能说明组合优化本身困难。

这个 packet 仍是 synthetic over PerspectiveGap fragments。bundle、pair group、density-trap utility 和 global budget 都由 builder 施加；目前没有 downstream task success，也没有 7B/32B 或其它模型复现。

## 下一步压力

我会把下一步放在三个更锋利的检查上：

1. 做一个规则执行器对照：模型只输出 bundle 或 role 的优先级，规则执行器负责全局预算、closure 和拒绝集合。若它恢复明显，故事转为“LLM 提供偏好，规则层负责 admission legality”。
2. 做一个空角色 probe：固定 source 文本，只改变 source/scope 和 global budget，让两个或多个正 utility 角色竞争同一预算，看模型是否持续填满所有可用角色。
3. 加 7B/14B 或更多模型的同 packet 对照，只记录空角色填充率、oracle 非空角色覆盖、global budget pass，不急着扩 full benchmark。

当前最像 live handle 的名字可以叫：local usefulness versus admissibility。更人话一点：模型知道东西有用，但不会自然判断“有用也不该给”。
