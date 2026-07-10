# MCA idea 演化记录

日期：2026-07-08

## 做法

1. 第一阶段以 Standard MAD 作为基线。每道题先让 3 个智能体独立作答，再把第一轮可读答案和理由交给其他智能体，第二轮生成修正答案，最后对第二轮答案做多数投票。

2. 第二阶段加入 CPAC/DCAC guard-v1。该阶段不改变智能体内部通信，而是在答案已经出现后，用候选池、证书和守门规则决定是否保留初始多数或接受替代答案。

3. 第三阶段运行 MCA-T。脚本从初始答案池抽取文本线索，用证书审计判断是否接受替代答案。该阶段的通信对象是可读文本 cue，发生在答案已经生成之后。

4. 第四阶段运行 Question-only Pre-KV。发送方只读题，不生成新标记，保存题目阅读过程中的 KV prefix；接收方接入这段 KV 后生成第一轮答案。

5. 第五阶段运行 Early-plan Pre-KV。发送方先生成短私有早期草稿，保留 live KV；接收方提示词接在 sender past 后面生成第一轮答案。案例审计记录救回和被半截轨迹锚定的伤害。

6. 第六阶段运行 Hybrid micro-gated。发送方早期草稿被改成 `REPRESENTATION`、`FIRST_MOVE`、`CHECK` 三个结构化字段；脚本同时记录 raw Pre-KV 分支和门控选择后的 first-round 来源。

7. 第七阶段运行 latent rounds。每个智能体生成私有思考，脚本把“题目 + 私有思考”和“题目 + 空私有思考”的隐藏状态差值作为同伴向量；之后的私有轮次接收该向量，最终答案阶段默认不注入同伴向量。

8. 第八阶段运行 safe variants。它沿用 latent rounds，但把同伴消息改成 residual 或 per-peer branch，并固定低强度注入、范数裁剪、匹配种子和最终阶段不注入。

9. 第九阶段运行 natural-search-delta。发送方按普通 CoT prompt 解题，不写显式草稿；脚本在第 22 层、第 16/32/64/96 个生成步捕获 last-token hidden，用 `h_t - h_{t-1}` 构造同题、无关题、随机同范数和绝对状态对照。

10. 这条脉络的工程对象从可读文本转向非文本状态，从答案后修正转向答案前影响，从发送方主动写显式草稿转向普通解题轨迹中的隐藏状态变化量。

## 工程细节

- Standard MAD 基线来自 `experiments/standard-mad-math500-20260705-qwen25-7b-full-4096-a8002/`。它先让 3 个智能体独立作答，再让智能体读取其他人的可读答案和理由进行第二轮修正。
- CPAC/DCAC guard-v1 来自 `experiments/cpac-dcac-guard-v1-math500-20260706-standard-fixed-qwen25-7b-full-4096-a8002/`。它在答案已经出现后使用候选池、证书和守门规则保护部分正确答案。
- MCA-T 文本线索实验见 `reports/2026-07-06-mca-t-failure-triage.md`。它把文本 cue 注入第二阶段生成，观察模型是否被线索救回或带偏。
- Question-only Pre-KV 让 sender 只读题并保留 KV cache，receiver 接入这段 `past_key_values` 后生成第一轮答案。sender 不生成新 token，因此通信对象主要是题目阅读状态。
- Early-plan Pre-KV 让 sender 生成短私有早期草稿，再把 live KV 交给 receiver。该版本出现过错到对案例，也出现过被半截轨迹锚定的对到错案例。
- Hybrid micro-gated 让 sender 输出 `REPRESENTATION`、`FIRST_MOVE`、`CHECK` 等结构化字段，并尝试用门控保留较安全的候选。审计显示大量发送方输出停在半截结构化文本中。
- Latent rounds 使用 `scripts/run_mca_latent_rounds.py`，让每个智能体生成私有思考，并把“题目 + 私有思考”和“题目 + 空私有思考”的隐藏状态差值作为同伴向量。默认低强度注入私有轮次，最终答案阶段不注入同伴向量。
- Natural-search-delta 使用 `scripts/run_mca_natural_search_delta.py` 和 `tests/test_mca_natural_search_delta.py`。发送方按普通 CoT prompt 解题，不写显式草稿；脚本在第 22 层和第 16、32、64、96 个生成步捕获 last-token hidden，并用 `h_t - h_{t-1}` 作为主要通信对象。
- Natural-search-delta 的对照包括 `same_question_peer_delta`、`other_question_peer_delta`、`random_gaussian_same_norm` 和 `same_question_peer_absolute`。记录字段固定 `sender_prompt_intervention=false`、`uses_peer_past_key_values=false`、`state_source=ordinary_cot_decode_trace`。

## 结果

| 阶段 | 工程对象 | 主要结果 | 记录含义 |
| --- | --- | --- | --- |
| Standard MAD | 第二轮可读文本讨论 | 初始多数 364/500，final 378/500 | 文本讨论是有效基线 |
| CPAC/DCAC guard-v1 | 答案后候选池守门 | 初始多数 364/500，守门后 368/500 | 可保护部分正确答案，但发生在答案后 |
| MCA-T | 文本线索注入 | 初始 364/500，线索后 357/500 | 文本 cue 容易带来错误传播 |
| Question-only Pre-KV | 读题 KV prefix | no-channel first 347/500，Pre-KV first 349/500 | 缓存路径可运行，收益接近零 |
| Early-plan Pre-KV | 短私有草稿 live KV | 18 条审计中同时出现救回和伤害 | 中间轨迹有信号，也有锚定污染 |
| Hybrid micro-gated | 结构化字段和门控候选 | raw hybrid first 13/27，gated selected first 16/27 | 门控能筛部分候选，但通信对象被结构化提示塑形 |
| Latent safe variants | 私有思考差向量 | 四个 50 题 run 净变化 -2 到 +1 | 低强度潜向量未形成稳定增益 |
| Natural-search-delta | 普通解题轨迹 hidden delta | 同题 delta 26/50，随机同范数 26/50，无关题 delta 23/50，绝对状态 23/50 | 同题 delta 与随机扰动未拉开准确率差距 |

## 备注

这份记录用于说明 idea 和工程对象的演化，不替代各实验的详细报告。详细结果分别见 `2026-07-06-mca-t-failure-triage.md`、`2026-07-07-early-plan-pre-kv-case-audit.md`、`2026-07-07-hybrid-micro-gated-failure-audit.md`、`2026-07-08-mca-latent-safe-variants-results.md` 和 `2026-07-08-natural-search-delta-results.md`。
