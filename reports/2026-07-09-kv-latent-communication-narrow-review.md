# KV 与潜状态通信窄综述

日期：2026-07-09

## 做法

1. 将用户提供的四篇 PDF 移入 `papers/`，并保留 arXiv 版本号：
   - `papers/ciphers-embedding-debate-2310.06272v2.pdf`
   - `papers/state-delta-trajectory-2506.19209v2.pdf`
   - `papers/kvcomm-cross-context-2510.12872v2.pdf`
   - `papers/kvcomm-selective-kv-sharing-2510.03346v3.pdf`

2. 使用 `scripts/extract_paper_texts.py` 抽取文字。脚本输出 `.txt`、`.md` 和 `.pages.json` 三类文件；其中 `.md` 按页号分节，头部记录源 PDF、页数、标题和 SHA256。

3. 本轮阅读覆盖四篇文章：
   - `Let Models Speak Ciphers: Multiagent Debate through Embeddings`
   - `Augmenting Multi-Agent Communication with State Delta Trajectory`
   - `KVCOMM: Online Cross-context KV-cache Communication for Efficient LLM-based Multi-agent Systems`
   - `KVComm: Enabling Efficient LLM Communication through Selective KV Sharing`

4. 阅读记录按四个维度整理：通信对象、通信发生位置、接收方融合方式、实验对照。涉及本项目时，只记录机制差异和已有实验读数之间的对应关系。

## 工程细节

抽取产物：

| 文章 | PDF | Markdown | 页数 | 抽取字符数 |
| --- | --- | --- | ---: | ---: |
| CIPHER | `papers/ciphers-embedding-debate-2310.06272v2.pdf` | `papers/text/ciphers-embedding-debate-2310.06272v2.md` | 30 | 91192 |
| State Delta Encoding | `papers/state-delta-trajectory-2506.19209v2.pdf` | `papers/text/state-delta-trajectory-2506.19209v2.md` | 22 | 78152 |
| KVCOMM cross-context | `papers/kvcomm-cross-context-2510.12872v2.pdf` | `papers/text/kvcomm-cross-context-2510.12872v2.md` | 40 | 122484 |
| KVComm selective KV sharing | `papers/kvcomm-selective-kv-sharing-2510.03346v3.pdf` | `papers/text/kvcomm-selective-kv-sharing-2510.03346v3.md` | 28 | 89308 |

版本化 PDF 与此前缓存的无版本号 PDF 的 SHA256 相同：

| 版本化 PDF | SHA256 |
| --- | --- |
| `ciphers-embedding-debate-2310.06272v2.pdf` | `73f2b92dbc12a9697e8f2815b80f1a68a1e540ab025f8af978946b7869ffc044` |
| `state-delta-trajectory-2506.19209v2.pdf` | `3be622362fba548fd941d3acdf442bdedfe6013c711aaca4ccf41da0bcad34a3` |
| `kvcomm-cross-context-2510.12872v2.pdf` | `3acffcc4468b17cf5193a64ec998c6517af42acb247fc230171da92f0f9eb8df` |
| `kvcomm-selective-kv-sharing-2510.03346v3.pdf` | `48b9ee8f1b46e58d729140666243f24f211ea7c55aa85ad9f767cf24cd9f5e9a` |

## 结果

### 一、四篇文章的通信对象和融合位置

| 文章 | 通信对象 | 发送方状态来源 | 接收方融合方式 | 是否依赖自然语言消息 | 是否改变模型权重 |
| --- | --- | --- | --- | --- | --- |
| CIPHER | 下一 token 分布加权得到的 token embedding 期望 | 发送方逐 token 生成时的词表概率分布 | 把生成的 embedding 序列拼入下一轮 debate 输入；结束时用最近邻 token 转回文本 | 否，消息主体是 embedding 序列；最终输出转回文本 | 否 |
| State Delta Encoding | 指定层相邻生成 token 的 hidden state 差值 | 发送方生成自然语言消息时记录 token-wise hidden state 变化 | 接收方处理发送方自然语言 token 时，在对应 token 的同层 hidden state 上加 delta | 是，自然语言 token 仍是消息载体 | 否 |
| KVCOMM cross-context | 可复用共享文本段的 KV-cache 及其 offset | 多智能体系统中不同 agent prompt 的共享文本段、placeholder 和相邻 prefix segment | 通过 RoPE 位置对齐、anchor offset 估计和 cache 拼接，替代部分 prefill 计算 | 是，复用对象来自 prompt 或 agent 输出中的共享文本段 | 否 |
| KVComm selective KV sharing | 发送方 context 在部分层的 KV pairs | 发送方在 prefill 阶段处理 context 后得到的每层 KV pairs | 接收方处理 query 时，在选定层 attention 中拼入发送方 KV pairs | 否，发送方 context 不被采样成自然语言消息后再传递 | 否 |

### 二、CIPHER

CIPHER 的通信单位是概率加权 embedding。发送方在第 `t` 个生成步得到词表分布 `p(t)`，再用该分布对词表 embedding 求加权平均，形成一个 semantic embedding。生成过程不采样单个 token，而是把 semantic embedding 接回模型作为后续生成输入。

CIPHER 的 debate 流程包含初始轮和后续 debate 轮。每一轮把各个 debater 生成的 embedding response 拼到 prompt embedding 后，再输入给 debater 生成下一轮 response。最终步骤把 embedding response 通过最近邻词表 token 转成自然语言，再做聚合。

实现流程记录：

| 步骤 | 输入 | 操作 | 输出 |
| --- | --- | --- | --- |
| Prompt embedding | 问题、指令、few-shot 示例 | tokenizer 把 prompt 转成 embedding 序列 `emb_prompt` | 初始输入 embedding |
| 单步 CIPHER 生成 | `emb_prompt` 和已生成 semantic embeddings `emb^(1:t-1)` | 模型输出 logits，经 temperature `T` softmax 得到词表分布 `p(t)` | 第 `t` 步词表概率分布 |
| Semantic embedding 构造 | `p(t)` 和词表 embedding 矩阵 | 对所有 token embedding 做加权平均：`emb(t)=sum_i p_i(t) * emb_vocab_i` | 第 `t` 个 semantic embedding |
| 自回归递推 | `emb(t)` | 将 `emb(t)` 拼接到已生成 embedding 序列后继续生成 | CIPHER response embedding 序列 |
| 停止判定 | 新生成的 semantic embedding 和词表 embedding | 若最近邻 token 是 EOS，或达到最大长度，则停止 | 一段 CIPHER response |
| Debate 输入更新 | 初始 prompt embedding 和各 debater 的 CIPHER response | `concat(emb_prompt, cipher_1, ..., cipher_n)` | 下一轮输入 embedding |
| 输出转换 | 最后一轮 embedding response | 对 embedding response 做最近邻词表 token 映射 | 自然语言 response |
| 最终聚合 | 最后一轮各 debater response | 论文实验中选低温 debater 的 response；也讨论 majority / tie-breaking | final answer |

公式记录：

| 项 | 论文定义 |
| --- | --- |
| 自然语言采样分布 | `p(t)=softmax(logit(prompt, res^(1:t-1))/T)` |
| CIPHER 分布 | `p(t)=softmax(logit(emb_prompt, emb^(1:t-1))/T)` |
| CIPHER embedding | `emb(t)=sum_i p_vocab_i(t) * emb_vocab_i` |
| 异构 LLaMA embedding 对齐 | 若 sender 和 receiver 共享 tokenizer 但 embedding 矩阵不同，则用 receiver 的 token embedding 空间计算加权平均 |

实现参数和实验口径记录：

| 项 | 记录 |
| --- | --- |
| 主实验 debate 规模 | 2 个 debater，3 轮 debate |
| 温度选择 | 使用 Bayesian optimization 选择各方法温度 |
| 大数据集调温 | GSM8K、Professional Psychology、Arithmetic 使用 200 个 validation samples 调温，再在独立 200 个 test samples 评估 |
| prompt | 初始轮和 debate 轮使用 few-shot CoT 或 zero-shot CoT；附录 E 给出各数据集 prompt |
| CIPHER 输出确定性 | 表 1 中 CIPHER 多项读数标准差为 `0.0`，论文说明来自 deterministic embedding generation |
| partial CIPHER | 论文另做只在高不确定位置启用 CIPHER 的消融；不确定性由概率分布指标衡量，其他位置回到 greedy sampling |

论文实验使用 2 个 debater、3 轮 debate，主要模型包括 LLaMA2-70B、LLaMA-65B、Falcon-40B-Instruct、MPT-30B 和 WizardMath-70B。数据集包括 GSM8K、MMLU High School Math、MMLU Professional Psychology、MMLU Formal Logic 和 Arithmetic。

论文报告的主要读数：

| 模型 | 方法 | GSM8K | H.S. Math | Psychology | Formal Logic | Arithmetic |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| LLaMA2-70B | Natural Language Debate | 64.8 | 39.4 | 74.2 | 49.2 | 81.1 |
| LLaMA2-70B | CIPHER | 66.0 | 41.5 | 75.0 | 52.4 | 85.0 |
| LLaMA-65B | Natural Language Debate | 51.7 | 36.7 | 70.0 | 46.0 | 30.4 |
| LLaMA-65B | CIPHER | 52.9 | 38.5 | 70.9 | 50.8 | 33.0 |

与本项目的机制差异：

| 项目 | CIPHER | 本项目已有 MCA 线 |
| --- | --- | --- |
| 通信发生阶段 | 初始响应生成后，后续 debate 轮读取上一轮 embedding response | 包含答案后文本线索、答案前 Pre-KV、私有思考 latent rounds、普通解题轨迹 delta |
| 通信对象 | response 级 embedding 序列 | 文本 cue、KV cache、hidden state residual、hidden state delta |
| 接收方输入 | 上一轮 embedding response 拼入输入 | Pre-KV 中接在 sender past 后；latent rounds 中注入 residual；natural-search-delta 中在指定生成步注入 delta |
| 对照 | Single Answer、Self-Consistency、Natural Language Debate | 无通道、文本 MAD、随机同范数、无关题状态、绝对状态 |

### 三、State Delta Encoding

State Delta Encoding 把发送方生成自然语言 token 时的 hidden state 变化记为 `state delta`。若发送方生成 token `t_i` 时，在层 `l` 的 hidden state 为 `h_i^l`，则 delta 表示相邻生成步的 hidden state 差值。接收方仍然读取发送方自然语言输出；当接收方处理发送方 token `t_i` 的位置时，在同一层注入对应 delta。

论文的接收方更新方式为：只有与发送方 token 对齐的位置被修改，其他位置 hidden state 保持不变。该设计把自然语言 token 和 token-wise latent delta 绑定在一起。

实现流程记录：

| 步骤 | 输入 | 操作 | 输出 |
| --- | --- | --- | --- |
| 发送方自然语言生成 | 发送方 prompt | 发送方按普通方式逐 token 生成自然语言输出 `output_A={t_1,...,t_n}` | 发送方自然语言消息 |
| Hidden state 记录 | 发送方每个生成 token、指定层 `l` | 记录生成 token `t_i` 时的 hidden state `h^l_{A,i}` | hidden state 轨迹 `H_A^l` |
| Delta 构造 | 相邻 hidden states | 对相邻生成步取差，形成 `s_i^l` | state delta trajectory `S_A^l` |
| 接收方 prompt 构造 | 原任务输入 `X`、发送方自然语言输出 `output_A`、后续指令 `Y` | 形成 `prompt_B={X, t_1, ..., t_n, Y}` | 接收方输入序列 |
| Delta 对齐 | 发送方 token `t_i` 在接收方 prompt 中的位置 `j` | 将 `s_i^l` 对齐到接收方处理 `t_i` 的 token 位置 | token-wise latent augmentation |
| 接收方注入 | 接收方在层 `l` 的 hidden state `h^l_{B,j}` | 若当前位置对应发送方 token `t_i`，则更新为 `h^l_{B,j}+s_i^l`；否则保持不变 | 修改后的 hidden state 传入下一层 |
| 最终生成 | 注入后的接收方 forward | 接收方继续生成自己的回复或更新答案 | 最后一轮 agent response |

实现对象和约束：

| 项 | 记录 |
| --- | --- |
| agent 架构 | 论文聚焦同一个 transformer-based LLM 构造出的多个 agent |
| 状态粒度 | token-wise delta trajectory，不是单个 summary vector |
| 注入层数 | 每个模型选择少量层，7B 选 1 层，8B 选 2 层，14B 选 3 层 |
| 接收方保留信息 | 接收方仍读取发送方自然语言 token；delta 作为辅助状态进入对应 token 位置 |
| 生成限制 | IA 和 workflow 设置中 NL/SDE 使用 greedy decoding；debate 设置中使用默认采样和温度以产生初始回答多样性 |
| 运行重复 | 多智能体 debate 任务结果为 3 次独立运行平均值 |

任务实现记录：

| 设置 | 交互流程 | 停止或计分方式 |
| --- | --- | --- |
| Information asymmetry | 每题检索 6 篇相关文档，均分给 2 个 agents；agents 通过多轮问答补齐信息 | 最多讨论 5 轮；任一 agent 生成 formatted answer 后结束；报告 EM/F1 或 accuracy |
| Multi-agent debate | 每题 2 个 agents；第一轮独立作答；后续轮读取上一轮 peer responses 后更新 | 3 轮 debate；计分为最后一轮所有 agent responses 的平均正确率 |
| Agent workflow | agents 顺序执行 ReAct 风格 Thought/Action/Observation 流程 | 每题最多 7 个 agents；Finish[answer] 作为结束格式 |

论文使用三类任务：

| 设置 | 任务类型 | 数据集 |
| --- | --- | --- |
| Information asymmetry | 不同 agent 拥有不同私有文档，需通过交流补齐信息 | Quasar-T、ComplexWebQuestions、StrategyQA |
| Information symmetry: debate | 多智能体 debate，共享同一题面 | GSM8K、MMLU Abstract Algebra、MMLU College Mathematics、MMLU Formal Logic |
| Agent workflow | 多 agent 顺序完成 ReAct 风格流程 | FEVER、HotpotQA、StrategyQA |

论文报告的 Qwen2.5-7B debate 读数：

| 方法 | GSM8K | Abstract Algebra | College Math | Formal Logic |
| --- | ---: | ---: | ---: | ---: |
| Single | 0.8789 | 0.4767 | 0.3900 | 0.4497 |
| Natural Language | 0.9061 | 0.4583 | 0.3617 | 0.4762 |
| CIPHER | 0.8933 | 0.4850 | 0.3700 | 0.4881 |
| SDE | 0.9178 | 0.5167 | 0.4433 | 0.5198 |

论文的层选择记录：

| 模型 | 层数量 | 选用层 | Top-5 层记录 |
| --- | ---: | --- | --- |
| Qwen2.5-7B-Instruct | 28 | 22 | 22、24、9、20、12 |
| Llama3.1-8B-Instruct | 32 | 17、20 | 17、20、5、8、30 |
| Qwen2.5-14B-Instruct | 48 | 21、23、33 | 33、21、23、19、36 |

论文的消融记录包含两点：

| 消融项 | 记录 |
| --- | --- |
| 使用原始 hidden state 替代 delta | 多个设置中低于完整 SDE；部分设置低于自然语言 |
| 修改全部层 | 图示和文字记录为性能下降，作者解释为干扰模型生成能力 |

与本项目的机制差异：

| 项目 | State Delta Encoding | 本项目 natural-search-delta |
| --- | --- | --- |
| 是否有自然语言载体 | 有，delta 与发送方自然语言 token 对齐 | 无，状态来自普通 CoT 解码轨迹 |
| 注入位置 | 接收方处理发送方 token 的对应位置 | 接收方自身生成到第 16/32/64/96 步时注入 |
| 层 | Qwen2.5-7B 使用第 22 层 | 首跑使用第 22 层 |
| 对照 | Natural Language、CIPHER、w/o delta | 无通道、同题 delta、无关题 delta、随机同范数、同题绝对状态 |
| 首跑结果对应 | 论文显示 SDE 高于 NL 和 CIPHER | 本项目同题 delta `26/50`，随机同范数 `26/50`，无关题 delta `23/50`，同题绝对状态 `23/50` |

### 四、KVCOMM Cross-Context

KVCOMM cross-context 的目标是减少多智能体系统中重复 prefill 计算。文章的问题设定是：不同 agent 的 prompt 中存在共享文本段，但这些共享文本段前面有不同 prefix。相同文本在不同 prefix 后产生的 KV-cache 不相同，文章称为 offset variance。

论文的机制包含以下步骤：

1. 初始化阶段，每个 agent 预计算并保存 prompt template 中 prefix segment 的 KV-cache。
2. 运行时，系统识别 prompt 中的 placeholder 和共享文本段。
3. Anchor prediction 模块根据 embedding proximity 和长度兼容性查找可复用 anchor。
4. 若匹配失败，agent 执行标准 dense prefill，并把实际 offset 存入 anchor pool。
5. 若匹配成功，系统用 anchor offset 估计当前 placeholder 和相邻 prefix segment 的 KV-cache offset。
6. Key cache 先做 RoPE 位置对齐，再加估计 offset；Value cache 直接加估计 offset。
7. 更新后的 placeholder KV 和 prefix KV 被拼接后用于 decoding。

实现数据结构记录：

| 名称 | 内容 | 用途 |
| --- | --- | --- |
| Placeholder | prompt template 中运行时填入的片段，例如 user query、agent response、tool result | 作为 cache 复用和 anchor 管理的基本单位 |
| Prefix segment | placeholder 之前或之后的固定 prompt 片段 | 其 KV-cache 也会受 placeholder context 影响 |
| Base KV-cache | placeholder 或 prefix segment 在 base context / 无外部上下文下的 KV-cache | offset 计算的参考 |
| Placeholder offset | 同一 placeholder 在 agent-specific context 中的 KV-cache 与 base KV-cache 的差值 | 估计外部输入段在新 prefix 下的 KV-cache |
| Prefix offset | placeholder 邻近 prefix segment 的 KV-cache offset | 处理 placeholder 改变后对相邻 prefix 的影响 |
| Anchor | `{placeholder name, base KV, agent placeholder offset, agent prefix offset}` 等字段组成的缓存条目 | 为后续相似 placeholder 提供 offset 估计样本 |
| Anchor pool | 每个 placeholder 对应的 anchor 集合 | 支持匹配、复用、更新和 pruning |

Anchor prediction 和 update 记录：

| 环节 | 论文记录 |
| --- | --- |
| 匹配依据 | token length compatibility 和 embedding proximity |
| 权重计算 | 对候选 anchor 的 embedding 距离取负值后做 softmax：`w=softmax(-||h_phi-h_psi||)` |
| shareability 判定 | 使用长度覆盖条件和 entropy threshold `gamma`；公式中包含 `H > gamma log |A_phi|` |
| 不可复用样本 | 执行 dense prefill，计算真实 KV-cache 与 base KV-cache 的 offset，并存入 anchor pool |
| anchor pool 容量 | 主实验中 anchor pool size `V=20` |
| pruning | 达到容量后，在较早加入的 anchor 中删除 least-frequently-used 条目 |

Cache update 记录：

| 对象 | 更新方式 |
| --- | --- |
| Key cache | 先用 RoPE de-rotation/re-rotation 做位置对齐，再加 anchor 插值得到的 Key offset |
| Value cache | 无 RoPE 位置信息，直接加 anchor 插值得到的 Value offset |
| Placeholder KV | `base KV + sum_psi w_psi * placeholder_offset_psi` |
| Prefix KV | `base KV + sum_psi w_psi * prefix_offset_psi` |
| Decoding 输入 | 更新后的 placeholder KV 和 prefix KV 拼接后进入 decoding |

Algorithm 1 记录的执行路径：

| 分支 | 条件 | 操作 |
| --- | --- | --- |
| 初始化 | agent set `M`、prompt 中 placeholders、anchor pool capacity `V`、entropy threshold `gamma` | 抽取各 agent prompt 的 placeholder tokens；为每个 placeholder 初始化 anchor pool |
| Base cache 缺失 | placeholder sample 不在 shared memory 中 | 计算缺失 placeholder sample 的 base KV-cache |
| 可复用 | 所有 placeholders 按 Eq. (5) 被预测为 shareable | 异步遍历 placeholders；取 base KV、anchor pool、matched anchors；计算权重和 offset；更新 placeholder 与邻近 prefix KV |
| 不可复用 | 任一 placeholder 不满足 shareability | 对输入执行 dense generation；取得真实 KV-cache；为 placeholder 与 prefix 计算 offset 并写入 anchor pool |
| 容量超限 | `|A| > V` | 在较早 anchors 中剪掉 least-frequently-used 条目 |

实现参数记录：

| 项 | 数值或说明 |
| --- | --- |
| 运行硬件 | 单张 NVIDIA H100 GPU |
| 最大生成长度 | 512 tokens |
| 主实验 `gamma` | 0.3 |
| 主实验 anchor pool size `V` | 20 |
| 对照方法 | Original、CacheBlend |
| CacheBlend 复现口径 | recompute top-20% tokens with largest KV deviations |
| TTFT 表格设置 | 5 agents；每 agent prefix token length 512；output length 512 |
| Scalability 表格设置 | 3 agents；prefix 64 到 1024；output 128 到 1024 |

论文的主实验任务和模型：

| 任务 | 数据集 | 模型 |
| --- | --- | --- |
| 检索增强问答 | MMLU | Llama-3.1-8B-Instruct |
| 数学推理 | GSM8K | Llama-3.1-8B-Instruct |
| 代码生成 | HumanEval | Qwen2.5-Coder-7B-Instruct |

论文报告的主表读数：

| 数据集 | 方法 | 2 agents | 3 agents | 4 agents | 5 agents |
| --- | --- | ---: | ---: | ---: | ---: |
| MMLU accuracy | Original | 47.1 | 66.7 | 68.0 | 69.9 |
| MMLU accuracy | CacheBlend | 65.4 | 65.4 | 65.4 | 67.3 |
| MMLU accuracy | KVCOMM | 64.7 | 68.6 | 68.0 | 69.9 |
| GSM8K accuracy | Original | 81.1 | 82.4 | 82.1 | 81.7 |
| GSM8K accuracy | CacheBlend | 82.0 | 75.1 | 65.1 | 57.1 |
| GSM8K accuracy | KVCOMM | 81.5 | 81.7 | 80.6 | 79.6 |
| HumanEval Pass@1 | Original | 86.3 | 83.9 | 84.5 | 85.1 |
| HumanEval Pass@1 | CacheBlend | 31.1 | 21.1 | 30.4 | 32.9 |
| HumanEval Pass@1 | KVCOMM | 81.4 | 83.2 | 83.2 | 83.2 |

论文的对齐消融记录：

| Key 位置旋转 | Placeholder offset | Prefix offset | MMLU accuracy |
| --- | --- | --- | ---: |
| 是 | 否 | 否 | 43.1 |
| 否 | 是 | 否 | 58.8 |
| 否 | 否 | 是 | 60.1 |
| 是 | 是 | 否 | 38.6 |
| 是 | 否 | 是 | 62.1 |
| 否 | 是 | 是 | 56.9 |
| 是 | 是 | 是 | 68.0 |

与本项目 Pre-KV 的机制差异：

| 项目 | KVCOMM cross-context | 本项目 Pre-KV / early-plan Pre-KV |
| --- | --- | --- |
| 目标 | 加速多 agent serving 中共享文本段 prefill | 测试发送方前置状态是否影响接收方解题 |
| 共享对象 | prompt 中 placeholder、共享文本、相邻 prefix segment 的 KV-cache | sender pre-state prompt、题面、assistant 早期草稿形成的 `past_key_values` |
| 位置处理 | RoPE de-rotation/re-rotation 和 offset 估计 | receiver prompt 的 position ids 从 sender `past_token_count` 后继续 |
| 失败风险记录 | 文章记录缺少完整对齐会造成 accuracy 下降 | 本项目审计记录 raw KV channel 同时携带 sender prompt、题面、role text 和 partial reasoning |

### 五、KVComm Selective KV Sharing

KVComm selective KV sharing 的任务设定为：发送方模型 `M_s` 拥有 context `C`，接收方模型 `M_r` 拥有 query `Q`。发送方在 prefill 阶段处理 context 并得到每层 KV pairs。接收方处理 query 时，在选定层把发送方 KV pairs 拼入 attention 机制。

论文将 Baseline 定义为无通信，Skyline 定义为把 context `C` 和 query `Q` 直接拼接输入接收方。KVComm 的目标是在少传层的情况下接近 Skyline。

实现流程记录：

| 步骤 | 输入 | 操作 | 输出 |
| --- | --- | --- | --- |
| Sender prefill | sender model `M_s`、context `C` | `M_s` 对 `C` 做一次 forward / prefill，得到每层 KV pairs `{(k_l^s, v_l^s)}` | sender 全层 KV pairs |
| Calibration | calibration set 中的 context/query 样本 | 计算各层 selection score | 固定层集合 `S` |
| Layer selection | selection ratio `r`，总层数 `L` | 取 top `M=ceil(rL)` 层 | 被共享的层集合 |
| Receiver prefill / decoding | receiver model `M_r`、query `Q` | `M_r` 正常处理 `Q`；若当前层属于 `S`，将 sender KV 拼入 attention 可见 KV 集合 | 融合 sender context 的 receiver hidden states |
| 输出 | receiver 解码结果 | 按任务指标评估 | final answer / generated output |

Attention 融合记录：

| 项 | 记录 |
| --- | --- |
| 层匹配 | 论文只考虑 sender 和 receiver 层索引一一对应的情况 |
| 融合位置 | receiver 的 attention mechanism 内部 |
| 拼接对象 | sender 在选定层中 context token positions `[0, |C|)` 的 KV pairs，以及 receiver 自身 query KV pairs |
| receiver prompt | receiver 处理 query `Q`；不是把 sender context 文本直接拼入 query |
| 与 Skyline 区别 | Skyline 在输入层拼接 `C` 和 `Q`；KVComm 在选定层 attention 中拼接 sender KV |

层选择计算记录：

| 步骤 | 论文记录 |
| --- | --- |
| attention importance | 对每层所有 attention heads，计算 query tokens 对 context tokens 的平均 attention weight |
| score normalize | 将 attention importance 归一到 `[0,1]` |
| Gaussian prior | 以层 `mu` 为中心、标准差 `sigma`，形成深度 prior |
| final score | attention importance 和 Gaussian prior 按权重 `alpha` 组合 |
| top-M selection | 按 final score 取 top `M` 层，`M=ceil(rL)` |
| 固定层 | 每个 model pair 和 dataset 在 calibration set 上选层后，测试集固定使用 |
| calibration size | 附录 H 记录主实验使用 1 个 calibration sample；测试 1 到 128 个 sample 时性能差异不显著 |

论文的层选择方法包含两个部分：

| 组成 | 记录 |
| --- | --- |
| Attention importance score | 根据 prefill 阶段各层各头对 context token 的平均 attention weight 计算 |
| Gaussian prior | 以某一层深度为中心，引入中间层偏好 |
| 最终 selection score | attention importance 和 Gaussian prior 的加权组合 |
| 层选择固定方式 | 在 calibration set 上选层，测试集固定使用同一组层 |
| calibration set 大小记录 | 论文记录单个样本也可得到稳定层选择；具体实验见其 Section H |

实现参数记录：

| 项 | 记录 |
| --- | --- |
| 代码框架 | PyTorch 和 HuggingFace Transformers |
| 数值精度 | bfloat16 |
| 评估模型对 | 9 个 model pairs；包括同一 LLM 的两个实例、同一 base LLM 的 fine-tuned variants、LLaMA/Qwen/Falcon 系列 |
| selection ratios | `0.3`、`0.5`、`0.7` |
| 对照方法 | Baseline、Skyline、Natural Language Debate、CIPHER、AC mean/replace/sum、Random layer selection、contiguous chunk selection |
| 数据集 | Countries、Tipsheets、HotpotQA、QASPER、MuSiQuest、MultiFieldQA-en、2WikiMQA、TMATH |
| TMATH 指标 | ROUGE-L Recall |
| 其他数据集指标 | F1 score |

Compared methods 实现记录：

| 方法 | 实现定义 |
| --- | --- |
| Baseline | receiver `M_r` 只处理 query `Q`，不接收 sender `M_s` 通信 |
| Skyline | receiver 直接处理 `concat(C,Q)`；作为 context 全可见上界 |
| Natural Language Debate | sender 先读 context 后生成自然语言消息，receiver 读取该消息和 query |
| CIPHER | sender 生成 probability-weighted embedding message，receiver 在 embedding space 读取消息 |
| AC mean | 使用 last-token hidden state 通信，并与 receiver hidden state 求均值 |
| AC replace | 用 sender last-token hidden state 替换 receiver last-token hidden state |
| AC sum | sender last-token hidden state 与 receiver last-token hidden state 相加 |
| Random selection | 在相同 selection ratio 下随机选择共享 KV 层 |
| Contiguous chunk | 选择从 `layer_from` 到 `layer_to` 的连续层区间共享 |

论文报告的主表包含三组模型对和八个数据集。以下为其中部分读数：

| 模型对 | 方法 | Countries | Tipsheets | HotpotQA | QASPER | MuSiQuest | MultiFieldQA-en | 2WikiMQA | TMATH |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Llama-3.2-3B pair | Baseline | 0.05 | 0.32 | 0.23 | 0.05 | 0.02 | 0.11 | 0.27 | 0.34 |
| Llama-3.2-3B pair | Skyline | 0.57 | 0.91 | 0.73 | 0.25 | 0.51 | 0.47 | 0.40 | 0.36 |
| Llama-3.2-3B pair | NLD | 0.43 | 0.72 | 0.43 | 0.10 | 0.18 | 0.09 | 0.30 | 0.33 |
| Llama-3.2-3B pair | CIPHER | 0.42 | 0.69 | 0.50 | 0.10 | 0.18 | 0.13 | 0.32 | 0.32 |
| Llama-3.2-3B pair | KVComm 0.3 | 0.46 | 0.45 | 0.46 | 0.09 | 0.28 | 0.15 | 0.28 | 0.35 |
| Llama-3.2-3B pair | KVComm 0.5 | 0.57 | 0.81 | 0.57 | 0.27 | 0.32 | 0.51 | 0.36 | 0.35 |
| Llama-3.2-3B pair | KVComm 0.7 | 0.57 | 0.81 | 0.65 | 0.29 | 0.36 | 0.47 | 0.37 | 0.35 |

随机选层对照记录：

| 方法 | Countries | Tipsheets | HotpotQA | QASPER | MuSiQuest | MultiFieldQA-en | 2WikiMQA | TMATH |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Random 0.3 | 0.05 | 0.32 | 0.18 | 0.07 | 0.01 | 0.06 | 0.17 | 0.33 |
| KVComm 0.3 | 0.46 | 0.45 | 0.46 | 0.09 | 0.28 | 0.15 | 0.28 | 0.35 |
| Random 0.5 | 0.26 | 0.44 | 0.37 | 0.08 | 0.10 | 0.09 | 0.21 | 0.34 |
| KVComm 0.5 | 0.57 | 0.81 | 0.57 | 0.27 | 0.32 | 0.51 | 0.36 | 0.35 |
| Random 0.7 | 0.57 | 0.82 | 0.62 | 0.20 | 0.34 | 0.30 | 0.28 | 0.35 |
| KVComm 0.7 | 0.57 | 0.81 | 0.65 | 0.29 | 0.36 | 0.47 | 0.37 | 0.35 |

与本项目 KV 实现的机制差异：

| 项目 | KVComm selective KV sharing | 本项目 question-only / early-plan Pre-KV |
| --- | --- | --- |
| 接收方 prompt | 接收方处理自己的 query | receiver prompt 接在 sender past 后 |
| sender KV 进入位置 | 选定层 attention 中拼接为额外 KV | 作为完整 past_key_values 的历史前缀 |
| 层选择 | attention importance score 加 Gaussian prior，选择部分层 | question-only Pre-KV 不选层；early-plan Pre-KV 使用完整 sender past |
| 通信强度 | 只传选中层 KV pairs | 传 sender pre-state prompt、题面和可能的 assistant 草稿形成的全部 past |
| 主要对照 | Baseline、Skyline、NLD、CIPHER、AC、Random layer selection | no-channel first、Pre-KV first、Pre-KV + MAD、early-plan 快照、random same-norm delta 等 |

### 六、本项目已有实验与四篇文章的对应事实

| 本项目记录 | 已有读数或审计事实 | 对应文章中的相关机制 |
| --- | --- | --- |
| `MCA-T` 文本线索 | `364/500 -> 357/500`，接受改动 17 次，其中错到对 1 次、对到错 8 次 | CIPHER 和 SDE 都记录自然语言采样或自然语言消息存在信息瓶颈；SDE 保留自然语言但增加 delta |
| `MCA-Pre-KV question_only` 同口径 bridge | no-channel first `347/500`，Pre-KV first `349/500` | KVComm selective 的通信对象是选层 KV；本项目该实验传完整 question-only past |
| `early-plan Pre-KV` 18 条审计 | no-channel `11/18`，Pre-KV `10/18`；错到对 3， 对到错 4 | KVCOMM cross-context 记录不同 prefix 下 KV-cache 需要位置和 offset 对齐；本项目 Pre-KV 使用前缀接续 |
| `hybrid micro-gated` 审计 | 51 个 sender outputs 中 46 个疑似截断；raw hybrid Pre-KV first `13/27`，gated selected first `16/27` | CIPHER 和 SDE 的发送方消息是完整生成序列；本项目 micro commitment 记录存在未完成字段 |
| `latent safe variants` | 四个 50 题 run 净变化范围 `-2` 到 `+1` | SDE 消融记录原始 hidden state 可低于自然语言；SDE 使用 token-wise delta 而非单一 residual 均值 |
| `natural-search-delta` | baseline `24/50`，同题 delta `26/50`，随机同范数 `26/50`，无关题 delta `23/50`，同题绝对状态 `23/50` | SDE 使用 delta，并与自然语言 token 对齐；本项目首跑无自然语言载体，并在固定生成步注入 |

## 备注

1. 四篇文章均属于非文本或潜状态通信相关工作，但通信对象不同：CIPHER 传 embedding expectation，SDE 传 token-wise hidden delta，KVCOMM 传对齐后的可复用 KV-cache，KVComm 传选层 KV pairs。

2. 四篇文章中的两篇仍保留自然语言消息结构：SDE 保留发送方自然语言 token，KVCOMM cross-context 复用 prompt 或 agent 输出中的共享文本段。CIPHER 和 KVComm selective 的主通信对象不是自然语言文本。

3. 本项目 Pre-KV 与 KVComm selective KV sharing 的融合位置不同。Pre-KV 把 receiver prompt 接在 sender past 后；KVComm selective 在 receiver 处理 query 时把 sender KV pairs 拼入选定层 attention。

4. 本项目 natural-search-delta 与 SDE 的状态对象相近，均使用 hidden state delta；二者差异在于 SDE 把 delta 与发送方自然语言 token 对齐，本项目首跑把普通解题轨迹中的 delta 在接收方指定生成步注入。

5. 四篇文章均未直接复现本项目当前的完整问题设置：MATH-500、Qwen2.5-7B-Instruct、3 个 agent、答案生成前通信、无自然语言载体、同题/无关题/随机同范数/绝对状态同场对照。当前报告只记录机制和读数对应。
