# Idea Novelty Timing Audit

日期：2026-07-09

## 结论先行

如果把创新点写成“在最终答案生成前，让多智能体进行一次非文本通信”，立不住。已有工作已经覆盖了多种 pre-final-answer / pre-receiver-generation 的非文本通信形式：activation grafting、KV sharing、latent working memory、dense KV-cache transfer、weight-space perturbation 等。

换句话说，`transcriptcast` / cache transfer / KV transfer 只能做背景或系统手段，不适合作为主要创新点。更可能成立的新切口是 latent/KV 通信的质量控制、触发时机、选择性共享、错误传播诊断。

## 需要区分的四种“时机”

| 类别 | 通信发生位置 | 代表工作 | 对本 idea 的含义 |
| --- | --- | --- | --- |
| A. 先答后辩 | agent 先生成 initial response / answer，再进入 debate | Multiagent Debate, MAD, CIPHER, HyLaT 的 debate 数据 | 这类工作支持“传统 debate 常常先出答案再交流”这个背景句 |
| B. receiver 生成前接收非文本状态 | sender 先处理 context，receiver 在生成 final output 前融合 activation/KV/latent | Communicating Activations, KVComm, Dense Latent Communication, TFLOW | 直接冲掉宽口径“答案前非文本通信没人做过” |
| C. 中间 agent 不产 final answer，只产 plan / latent thoughts | planner / critic / intermediate agent 被要求不要输出 final answer，信息通过 latent/KV 给最终 agent | LatentMAS, Agent Primitives | 冲掉“发送方不产 final answer 的提前通信没人做过” |
| D. 边思考边通信 / CoT-state 通信 | 通信从 final output 前移到 CoT-state / thinking state | COTIE / Communicate While Thinking | 高风险撞车点，需要拿到全文精读 |

## 本地论文证据

### 1. 传统 MAD / CIPHER 多是先 initial answer，再交流

这部分对我们是有利证据：不是所有 prior work 都做了“未形成答案前通信”。

- `papers/text/multiagent-debate-factuality-reasoning-2305.14325.txt`：Du et al. 明确说 after initial responses are generated，再发起 debate；初始 prompt 也要求 final answer。
- `papers/text/ciphers-embedding-debate-2310.06272v2.txt`：CIPHER 写道 debate 开始时 LLMs independently provide initial responses，之后各 agent 接收对方 answer refine previous answer；其 initial round prompt 明确要求写 final answer。
- `papers/text/hylat-hybrid-latent-text-2605.25421.txt`：HyLaT 的训练/推理 prompt 也要求 first explain reasoning and provide final answer，然后多轮 hybrid response 收敛到 final answer。

### 2. Communicating Activations 已经是 receiver 生成完成前融合 activation

`papers/text/communicating-activations-lm-agents-2501.14082.txt` 的方法是暂停 receiver LM B 在中间层的 computation，把 sender LM A 的 activation 融合进去，然后继续 forward pass 直到 decoding complete。arXiv 摘要也明确写了这个过程。

来源：arXiv `2501.14082`, Communicating Activations Between Language Model Agents, ICML 2025。

## 3. KVComm 已经做了 selected KV 在 receiver final output 前融合

`papers/text/kvcomm-selective-kv-sharing-2510.03346v3.txt` 里，sender 处理 context 得到每层 KV pairs，选择部分层传给 receiver；receiver 处理 query 时把 sender KV 拼入 attention，之后生成 final output。

这说明“传 KV/cache 给 receiver，让 receiver 在最终输出前使用”已经被 KVComm 明确占住。我们如果做 raw KV continuation 或 selected KV side-channel，都必须和它对齐。

来源：arXiv `2510.03346`, KVComm: Enabling Efficient LLM Communication through Selective KV Sharing, ICLR 2026。

## 4. LatentMAS 已经覆盖“中间 agent 不产 final answer，latent memory 给最终 agent”

`papers/text/latentmas-latent-collaboration-2511.20639.txt` 很关键：

- 每个 agent 先通过 last-layer hidden embeddings 生成 latent thoughts；
- shared latent working memory 保存并转移内部表示；
- 最终 agent 聚合 preceding latent thoughts 后再 decode final response；
- planner prompt 明确写了：Do not produce the final answer。

这直接威胁“我们在答案前通信一次”的 novelty。

来源：arXiv `2511.20639`, Latent Collaboration in Multi-Agent Systems, ICML 2026 Spotlight。

## 5. Dense Latent Communication 更进一步：receiver 可不看题，只靠 sender KV

`papers/text/dense-latent-communication-heterogeneous-agents-2606.13594.txt` 区分 context-aware 与 context-unaware：

- context-aware：receiver 自己也看到输入，cache 主要是 reasoning signal；
- context-unaware：receiver 不看 source context，只靠 transferred latent/KV representations 生成答案；
- 附录还写到 sender encodes the question into a KV cache with zero sender decoding，receiver consumes that cache directly。

这比“答案前通信”更强：sender 甚至不需要 decode 文本，receiver 可以仅靠 latent/KV 通道答题。

来源：arXiv `2606.13594`, See What I See, Know What I Think: Dense Latent Communication Across Heterogeneous Agents。

## 6. TFLOW / Agentic Friends 占住 weight-space pre-answer communication

`papers/text/agentic-friends-weight-update-2605.13839.txt` 中，sender agents 处理输入后把 hidden states 编译成 receiver-specific LoRA perturbations，只在 receiver generation 期间注入；receiver 不看到 sender-written message 就生成答案。

这不是 KV/cache，但属于广义非文本通信，而且时机也是 receiver final answer generation 前。

来源：arXiv `2605.13839`, Good Agentic Friends Do Not Just Give Verbal Advice: They Can Update Your Weights。

