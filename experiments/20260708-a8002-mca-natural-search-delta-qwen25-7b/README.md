# MCA Natural Search Delta

日期：2026-07-08

目的：验证自然解题过程中的同题中间状态变化量是否真有搜索信号，而不是普通扰动。

核心约束：

```text
发送方正常解题；
不要求写计划；
不传可见文本；
不使用 peer past_key_values；
只在选定层和选定 decode 截点注入低强度状态变化量；
最多使用一张 GPU。
```

默认首跑：

```text
split = mca_disagreement_v1
limit = 50
layers = 22
checkpoints = 16,32,64,96
conditions = same_question_peer_delta,other_question_peer_delta,random_gaussian_same_norm,same_question_peer_absolute
```
