# lragent-multilora-kv-cache-sharing-2602.01053

- Source PDF: `lragent-multilora-kv-cache-sharing-2602.01053.pdf`
- Extracted at UTC: `2026-07-09T05:57:14.875488+00:00`
- Pages: 25
- Title: LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
- SHA256: `81b3cfa633094962ac02a79d77c70fb0fafe681e114561d8be743552315d8796`

## Page 1

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
Hyesung Jeon 1 Hyeongju Ha 1 Jae-Joon Kim 1
Abstract 1. Introduction
Role specialization in multi-LLM agent systems Recently, LLMs have been widely adopted in agent systems
is often realized via multi-LoRA, where agents due to their long-context understanding ability (Dubey et al.,
share a pretrained backbone and differ only by 2024; Jiang et al., 2023; Yang et al., 2025a), reasoning abil-
lightweight adapters. Despite sharing base model ity (Wei et al., 2022; Yao et al., 2023a; Snell et al., 2024),
weights, each agent independently builds and and external tool interaction capabilities (Yao et al., 2023b;
stores its own KV cache for the same long, Shen et al., 2024; Qin et al., 2024). In particular, multi-LLM
tool-augmented trajectories, incurring substan- agent systems have gained increasing attention for their
tial memory and compute overhead. Existing ability to assign specialized roles to multiple agents that
KV cache sharing methods largely overlook this collaboratively decompose and solve complex tasks (Talebi-
multi-LoRA setting. We observe that, cache dif- rad & Nadiri, 2023; Wu et al., 2024; Rasal, 2024; Zhang
ferences across agents are dominated by adapter et al., 2025). These agents retrieve information from ex-
outputs, while activations from the shared pre- ternal tools, augment it with generated outputs, and pass
trained backbone remain highly similar. Based the accumulated context, referred to as trajectories, to other
on this observation, we propose LRAgent, a KV agents for subsequent steps. To improve accuracy, a com-
cache sharing framework for multi-LoRA agents. mon approach is to fine-tune a pretrained model separately
It decomposes the cache into two components, a for each agent role. These fine-tuned models are typically
shared base component derived from pretrained trained on pre-generated trajectories that reflect role-specific
weights and an adapter-dependent component de- behavior and tool usage patterns (Shinn et al., 2023; Bo
rived from LoRA weights. LRAgent reduces et al., 2024; Liu et al., 2025a; Bai et al., 2025; Fu et al.,
memory overhead by sharing the base component 2025a). Parameter-efficient fine-tuning (PEFT) methods,
across agents and storing the adapter component such as low-rank adaptation (LoRA) (Hu et al., 2022), fur-
in its inherent low-rank form. It also reduces ther enhance scalability by reducing the number of trainable
computational overhead by sharing the low-rank parameters from the full model to a pair of low-rank matri-
cache, enabled by a shared-A multi-LoRA archi- ces. As a result, multi-LoRA architectures enable agents to
tecture. This avoids redundant computations for share the large pretrained backbone during inference while
contexts that have already been processed by other retraining lightweight, role-specific adapters (Wang et al.,
agents. To efficiently reconstruct adapter contri- 2023; Xia et al., 2024). This design has proven effective
butions at runtime, we introduce Flash-LoRA- in practice, consistently outperforming single-model agents
Attention, a kernel that reorders attention compu- and non-fine-tuned baselines in agentic tasks (Qiao et al.,
tation to avoid materializing the low-rank cache 2024; Yu et al., 2024; Liu et al., 2025b; Li et al., 2025).
to full dimension. LRAgent achieves through-
Due to the long trajectories in LLM agent systems, KV
put and time-to-first-token latency close to fully
cache overhead and compute overhead become more se-
shared caching, while preserving accuracy near
vere in multi-agent systems than in single-agent settings,
the non-shared caching baseline across agentic
because each agent maintains its own KV cache and redun-
question-answering benchmarks. Code is avail-
dant prefills occur even though a large portion of the context
able in the official repository.
is shared. This redundancy increases both memory usage
and inference latency. To mitigate the memory issue, recent
1Department of Electrical and Computer Engineering, Seoul Na-
work has explored KV cache sharing across agents. How-
tional University, Seoul, Korea. Correspondence to: Hyesung Jeon
<hjeon2k@snu.ac.kr>, Hyeongju Ha <mnv1009@snu.ac.kr>, ever, existing approaches either require architectural modifi-
Jae-Joon Kim <kimjaejoon@snu.ac.kr>. cations and additional training for cache fusion (Woo et al.,
2025; Fu et al., 2025b), focus mainly on handling positional
Proceedings of the 43 rd International Conference on Machine
misalignment caused by agent-specific prefixes (Yang et al.,
Learning, Seoul, South Korea. PMLR 306, 2026. Copyright 2026
2025b; Pan et al., 2025; Ye et al., 2025), or rely on selective
by the author(s).
1
6202
yaM
13
]GL.sc[
2v35010.2062:viXra

## Page 2

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
recomputation of certain tokens or layers (Yao et al., 2025; parameterizes the weight update as:
Liu et al., 2026). Furthermore, these works focus primarily
W = W + ∆W, ∆W = AB, (1)
on memory reduction but still incur redundant computation 0
to build a hidden state for a context that has already been where W
0
∈ Rdin×dout is the pretrained base weight, A ∈
processed by other agents. Importantly, KV cache sharing Rdin×r is the down-projection matrix, and B ∈ Rr×dout
schemes that explicitly exploit the multi-LoRA architecture
is the up-projection matrix, with rank r ≪ min(d , d ).
in out
remain largely unexplored.
Since only A and B are optimized instead of W , it signifi-
0
In this work, we make a key observation that, for the same cantly reduces the number of trainable parameters, leading
context, cache discrepancies across agents are dominated by to lower memory usage and computation compared to full
task-specific LoRA-induced outputs, while activations pro- fine-tuning. In particular, applying LoRA to the query and
duced by the shared pretrained backbone remain highly simi- value projections yields the best accuracy for a given num-
lar. Motivated by this observation, we propose LRAGENT, a ber of parameters and is therefore widely used in practice.
KV cache sharing framework tailored to multi-LoRA agent Unless otherwise stated, we apply LoRA to the query and
systems. We decompose the cache into two parts: a shared value projections in all experiments.
component computed from the pretrained weights, which
Multi-LoRA A typical multi-LoRA system augments a
we call the base cache, and an agent-dependent component
pretrained base weight with multiple task-specific low-rank
induced by the LoRA weights, which we call the adapter
weights (Xia et al., 2024). For each task index, or agent role
outputs. The next key property we exploit is that the adapter
index in our setting, i ∈ {0, 1, . . . , N − 1}, where N is the
output naturally admits a low-rank representation. Specifi- number of tasks, and given LoRA weights A
i
∈ Rdin×r and
cally, we store the intermediate activations produced right B
i
∈ Rr×dout, the task-specific weight used for inference
after the LoRA down-projection, which have a small rank
is:
dimension. We refer to these activations as the LR cache.
W = W + ∆W , ∆W = A B . (2)
i 0 i i i i
At runtime, we reconstruct the full-dimension adapter con-
tribution from LR cache by multiplying it with the LoRA
Given an input activation tensor for task i, X
i
∈ Rl×din,
up-projection matrix only when needed. As a result, we com-
with sequence length l, the output Y
i
∈ Rl×dout and the
adapter output ∆Y are computed as:
press multiple KV caches into a single shared base cache i
with lightweight LR caches. Based on this concept, we in-
Y = X W = X W + (X A )B ,
i i i i 0 i i i
troduce two cache sharing schemes. BaseShared shares the (3)
∆Y = X ∆W = (X A )B ,
base cache across all agents while maintaining a separate LR i i i i i i
cache per agent, substantially reducing KV cache memory. where X A ∈ Rl×r is the intermediate activation produced
i i
Furthermore, motivated by recent multi-LoRA variants that
by the down-projection.
share the down-projection matrix across tasks (Tian et al.,
2024; Yang et al., 2025c), we extend our idea to BaseLR- Multi-LoRA with Shared-A Recent works report that task-
Shared, which also shares the LR cache as well as the base specific differences in multi-LoRA systems are primarily
cache by aligning agents to use a common down-projection. driven by the up-projection matrices B i , while the down-
This extension further reduces both memory usage and the projection matrices A i encode highly similar intrinsic in-
amount of computation for previously seen contexts. To min- formation. Hence, sharing a down-projection matrix A can
imize the runtime overhead of reconstructing adapter contri- improve accuracy compared to conventional multi-LoRA
bution using LR cache, we design Flash-LoRA-Attention, systems, as A becomes more generalizable across tasks.
which reorders attention computation to avoid materializing This effect is not limited to specific datasets or subtasks, but
low-rank caches to full dimension and implements this strat- is effective across diverse domains and datasets (Tian et al.,
egy efficiently on top of FlashAttention (Dao et al., 2022; 2024; Yang et al., 2025c). We therefore adopt the shared-A
2023). Overall, our approach enables KV cache sharing design for improved accuracy in our setting, while simpli-
tailored to the multi-LoRA architecture, achieving memory fying it to match the conventional multi-LoRA architecture.
and inference efficiency close to fully shared KV caching Specifically, we replace the token-wise LoRA routing used
while preserving accuracy near the non-shared KV baseline. in prior work with a sequence-wise assignment, since agent
roles are predefined and do not require token-dependent
routing. This yields the same overall architecture as conven-
2. Background
tional multi-LoRA, except that the down-projections share
2.1. Multi-LoRA Architecture weights. We design cache sharing strategies that support
both standard multi-LoRA and the shared-A variant, with
LoRA LoRA (Hu et al., 2022) is a PEFT method that
the latter further leveraging the efficiency benefits of our
adapts model weights by adding a pair of low-rank matrices
approach. Overall, our method reduces memory usage and
to the frozen pretrained base weights. Formally, LoRA
latency while preserving each agent’s role-specific behavior.
2

## Page 3

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
2.2. Multi-LLM Agent KV Cache Sharing Table 1. Average cosine similarity across agent pairs for the base
cache, full cache, and adapter output, on the same context.
Multi-LLM Agent Multi-LLM agent systems can be im-
Model Full cache Base cache Adapter output
plemented either with a single model that plays different
roles via role-specific system prompts, which can be viewed LLaMA-3.1-8B-Instruct 0.9576 0.9726 0.0538
Ministral-8B-Instruct 0.9200 0.9530 0.0225
as a form of in-context learning, or with multiple models,
often by fine-tuning the same backbone model for different
roles (Talebirad & Nadiri, 2023; Wu et al., 2024; Shinn et al., system prompts. Other works rely on selective recompu-
2023; Liu et al., 2025a; Fu et al., 2025a). These systems tation. For instance, CacheBlend (Yao et al., 2025) reuses
commonly use three highly heterogeneous and irreplace- KV caches by recomputing a small subset of tokens that
able agent roles: a planning agent for reasoning, an action are critical for accuracy. DroidSpeak (Liu et al., 2026) en-
agent for tool use, and a reflection agent for revising the ables KV cache reuse across fine-tuned LLMs that share the
answer. Methods that incorporate fine-tuning for role spe- same backbone by selectively recomputing KV cache of a
cialization often synthesize agent-trajectory datasets using predefined set of critical layers while reusing the KV cache
instruction-following models (Touvron et al., 2023; OpenAI for the remaining layers, reporting higher accuracy than
et al., 2024; DeepSeek-AI et al., 2024), and then fine-tune token-wise recomputation methods such as CacheBlend.
with PEFT methods such as LoRA. These approaches have In addition, DroidSpeak introduces a hidden state cache
been shown to outperform both single-model agents and to skip recomputation for the initial few non-recomputed
non-fine-tuned baselines (Qiao et al., 2024; Yu et al., 2024; layers and directly feed to the first recomputed layer. How-
Liu et al., 2025b), leading to broad adoption in practice. ever, although DroidSpeak is the closest to our work, it still
In this work, we follow AutoAct (Qiao et al., 2024) and processes hidden states for already seen context, similar to
fine-tune LoRA adapters for the plan, action, and reflection other approaches, so it reduces only the key and value pro-
agents using the provided agent trajectory dataset. jections for cache updates while leaving most computation
unchanged. This highlights that fully reusing KV caches to
KV Cache Sharing Meanwhile, due to long trajectories
eliminate computation for redundant context across models
from multi-step reasoning and multiple retrieval of large con-
remains challenging. Moreover, KV cache sharing tailored
texts from external tools, memory and compute overhead
to multi-LoRA systems remains largely overlooked despite
becomes much more pronounced in multi-agent settings
their wide deployment in practice. To the best of our knowl-
than in single-agent scenarios. This is because each agent
edge, this is the first work that explicitly tailors KV cache
maintains its own KV cache even though much of the con-
sharing to multi-LoRA agent settings and our work is com-
text is shared. Moreover, the same context is processed
plementary to prior cache-sharing methods.
independently by multiple agents, leading to substantial
computation. Together, these effects introduce memory and
compute redundancy, increasing memory usage and latency. 3. Methodology
To mitigate the memory issue, recent works have explored
3.1. Cache Similarity Across the Agents
KV cache sharing for context that is shared across agents.
Most approaches either introduce new model architectures
We first demonstrate that, for the same context, differences
that require additional training to enable cache sharing, or
in cache values mainly arise from the adapter output, which
are limited to handling positional misalignment so that pre-
is small in magnitude (see Appendix A.1) but contains crit-
computed KV caches for overlapping context chunks can be
ical agent-specific information. Applying Equation 3 to
reused within a single model. ICaRus (Woo et al., 2025) pro-
the value projections, we let X denote the hidden states
i
poses a decoder architecture that fine-tunes only the query
obtained by running agent i, which exhibits high similarity
projections for downstream tasks, enabling agents to share
across agents (see Appendix A.2). In this setting, Figure 1
an encoder-generated cache and reconstruct task-specific
and Table 1 show that the base cache Y = X W re-
base,i i 0
additive caches at runtime. Cache2Cache (Fu et al., 2025b)
mains highly similar across agents on the same context. In
adds a trainable linear layer that project and fuse a source
contrast, the adapter output ∆Y = X ∆W acts as a largely
i i i
model’s KV cache into a target model. KVLink (Yang et al.,
decorrelated perturbation, with cosine similarity close to
2025b), KVFlow (Pan et al., 2025), and KVComm (Ye
zero. With these small, decorrelated adapter output, the ex-
et al., 2025) address positional misalignment from agent-
pected cosine similarity of the full cache Y = Y +∆Y
i base,i i
specific prefixes by aligning cache offsets and adjusting
is lower than that of the base cache, empirically by about
positional embedding at runtime, allowing reuse of over-
3% on average, where concrete derivation is provided in
lapping context despite divergent prefixes within a single
Appendix A.3. This motivates sharing only the base cache,
model. We note that these prefix-aware methods rely on
rather than the full cache, to better preserve the small but
differences in input prefixes, and therefore reduce to a naive
critical agent-specific contributions from the adapters. Oth-
fully shared KV cache baseline when agents share identical
erwise, the discrepancy accumulates over iterative agent
3

## Page 4

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
Figure 1. (Left) Relationship between the full cache, base cache, and adapter output. (Right) Layer-wise pairwise cosine similarity of the
base and full caches, measured on the same context across three agent pairs using 128 samples of 2k tokens from the HotpotQA dataset.
executions and can lead to a noticeable accuracy drop. We
also note that the cosine similarity of the key cache remains
above 0.98 on average (see Appendix A.4), suggesting that
value cache management is the key factor for preserving
accuracy in multi-agent inference. we observe a similar pat-
tern in other agent role configurations (see Appendix A.5).
3.2. BaseShared and BaseLRShared
In this section, we present KV cache sharing schemes
tailored to the multi-LoRA architecture. Our key idea
is to decouple the value cache into a shared component
(base cache) produced by the pretrained weights, and an
adapter-dependent component. We reuse the base cache
across agents without recomputation, and store the adapter-
dependent component in a compact low-rank form (LR
cache) that is expanded to full-dimension form on de-
Figure 2. Agent iteration and cache accumulation for Non-Shared,
mand at runtime. We first introduce BaseShared, which BaseShared, and BaseLRShared. T0 denotes the system
primarily reduces memory usage, and then extend it to prompt shared across agents, and Ti denotes trajectory context
BaseLRShared, which leverages shared-A multi-LoRA blocks, formed by concatenating model-generated tokens and
architecture and further reduces both computation and mem- retrieved context from external sources. BaseShared shares
only the base cache and maintains a separate LR cache per agent,
ory usage. Figure 2 illustrates the agent execution flow
whereas BaseLRShared shares both the base and LR caches.
and the corresponding cache management in our methods,
which we discuss in detail in the following paragraphs. cache increases the total cache size to 1 + 1/N times that
of the default non-shared scheme. Instead, we store the
BaseShared We first decouple the value cache into a base
adapter output in its inherent low-rank form as the interme-
component Y and an adapter-dependent component ∆Y .
base i diate output Y = X A , which we call the LR cache, and
lr,i i i
Here, we share a single base cache across agents even
reconstruct the required contribution at runtime via the up-
though the layer inputs X are not exactly identical, mo-
i projection as Y B . In addition, since key cache similarity
lr,i i
tivated by the observations in Section 3.1, which show that
is sufficiently high across agents, we fully share the key
the base cache X W remains highly similar across agents
i 0 cache. While the same idea can also be applied to the key
on the same context and that the remaining differences are
projection when LoRA is used, LoRA is typically applied to
dominated by the adapter contribution. Concretely, for each
the query and value projections for the best accuracy, so we
newly appended context, the agent that processes the con-
focus on the value projection in our main implementation.
text first materializes the base cache and stores it in memory.
Further accuracy and efficiency analysis for LoRA applied
When another agent later processes the same context, it
to the key projection is presented in Appendix D.1.
reuses the stored base cache without recomputation of value
projections as illustrated in Figure 2(b). We refer to this Figure 3 illustrates a forward pass that agent j processes
scheme as BaseShared. a context segment of length L c given a prefilled context
of length L by agent i. Here, the LR cache is accu-
p
For the adapter output, naively storing it in full-dimension
mulated over the sequence, and later expanded into the
form would largely negate the benefit of sharing, since keep-
full-dimension adapter contribution via the up-projection
ing full-dimension cache per agent in addition to the base
B , then added to the base cache. In terms of mem-
i
4

## Page 5

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
Figure 3. Diagram of base and LR cache computation with an initial context of length L prefilled by agent i, followed by an additional
p
context of length L processed by agent j, under (a) BaseShared and (b) BaseLRShared. BaseShared maintains per-agent
c
LR caches and computes the LR cache using hidden states for all context tokens not yet processed by the current agent, whereas
BaseLRShared shares a single LR cache and uses hidden states only for newly appended tokens. Both methods first compute the base
cache from the pretrained weights (⃝1 , ⃝4 ). They then compute the LR cache via the LoRA down-projection (⃝2 , ⃝5 ), and later expand it
to the full dimension via the LoRA up-projection over the full sequence (⃝3 , ⃝6 ). Efficient LR cache expansion is described in Section 3.3.
ory, BaseShared maintains a single shared base cache Table 2. Average cosine similarity of the LR cache across agent
pairs for the same context in shared-A multi-LoRA architectures.
along with lightweight per-agent LR caches. Because
each LR cache is smaller than the full cache by a factor Model (Plan, Action) (Action, Reflect) (Reflect, Plan)
of r/d out ≪ 1, the total KV cache size is reduced to LLaMA-3.1-8B-Instruct 0.9486 0.9634 0.9607
1/N + r/d ≃ 1/N of the non-shared scheme. How- Ministral-8B-Instruct 0.9473 0.9526 0.9498
out
ever, in terms of computation, since only the base cache is
shared, switching agents requires constructing the LR cache
for the entire accumulated context that the new agent has ther eliminates the redundant prefill computation, enabling
not yet processed; we refer to this as the ‘LR prefill’ process, substantially higher throughput and lower latency than prior
as illustrated in Figure 2(b). For example, in Figure 3(a), the approaches. As discussed in Section 2.1, task-specific dif-
hidden states span a sequence of length at least L + L , and ferences in multi-LoRA systems mainly arise from the up-
p c
the LR cache for agent j must be newly computed via the projection matrices B i , making it effective to share A for
down-projection A . At this step, computation of the key improving both parameter efficiency and accuracy (Tian
j
and value projection that produces the shared base cache et al., 2024; Yang et al., 2025c). In this setting, we fur-
for context segment L p can be skipped, but the majority ther observe that the LR cache AX i produced by the shared
of computation (e.g., proceeding MLP layers after the At- down-projection can also be shared across agents. As shown
tention layers) is still required. As a result, the amount of in Table 2, the LR cache in shared-A multi-LoRA exhibits
computation remains similar to the non-shared setting, scal- high cosine similarity across agents, analogous to the base
ing as O(N L2d ), where L is the total trajectory length cache, which motivates sharing the LR cache as well. We
model
and d is the model hidden dimension. We note that therefore maintain a single base cache and a single LR cache
model
this is consistent with prior KV cache sharing methods in- for the entire system, and construct agent-specific outputs
cluding DroidSpeak, since selective recomputation requires via their task-specific up-projections B i .
hidden states for the contexts that were previously processed
Here, the memory usage is reduced by a factor of 1/N +
only by other agents. In summary, BaseShared serves
r/(N d ) ≃ 1/N relative to the non-shared implemen-
out
as a robust and memory-efficient solution applicable to
tation. Moreover, because both the base cache and the
standard multi-LoRA systems. It significantly reduces KV
LR cache are available for all previously seen tokens in
cache memory usage compared to the non-shared baseline
BaseLRShared, an agent does not require recomputation
while preserving higher accuracy than existing prior KV
over context processed by previous agents to construct either
cache sharing methods. As such, BaseShared is particu-
cache or the hidden states. For example, in Figure 3(b), the
larly well-suited for conventional multi-LoRA agents when
base and LR caches for the L tokens that are already avail-
p
memory efficiency is a primary concern.
able, so the forward pass only needs to compute activations
BaseLRShared Building on this foundation, we next in- for newly appended L c contexts. Therefore, across N agents
troduce BaseLRShared to achieve computational ac- over the length-L trajectory, BaseLRShared avoids the
celeration as well as memory savings. By leveraging the N separate prefills required by the non-shared implemen-
shared-A multi-LoRA architecture, BaseLRShared fur- tation. As a result, the overall computational complexity
becomes even comparable to full cache sharing, scaling as
5

## Page 6

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
Algorithm 1 Flash-LoRA-Attention Forward (head-wise) output O:
Require: L = L p + L c , Q ∈ RLc×dhead O = P (V base + V lr B).
Require: K ∈ RL×dhead, base cache V
base
∈ RL×dhead
This expands the LR cache to the full-dimension d for
Require: LR cache V
lr
∈ RL×r, LoRA B ∈ Rr×dhead
all L tokens, so the computation overhead scales wit
o
h
ut
both
Require: Key, Value block size B , T = ⌈L/B ⌉
c c c L and d . Instead, we exploit associativity and compute
Require: Query block size B , T = ⌈L /B ⌉ out
r r c r
Ensure: Attn output block O ∈ RLc×dhead
O = P V + (P V )B,
1: Q, O → T r blocks Q i , O i (i = 0, . . . T r − 1). base lr
2: K, V base → T c blocks K j , V base,j (j = 0, . . . T c − 1). so the length-L multiplication is performed in the low-
3: V lr → T c blocks V lr,j (j = 0, . . . T c − 1). rank space, and the multiplication by B is applied after-
4: for 0 ≤ i < T r do ward. For instance, in a decoding step where the accumu-
5: Initialize O i ← 0 ∈ RBr×dhead, O lr,i ← 0 ∈ RBr×r lated context length was L, the naive implementation adds
6: Initialize m i ← −∞ ∈ RBr , ℓ i ← 0 ∈ RBr Θ(L r d ) computation to form V B already before the
out lr
7: Load Q i to ShrMem attention computation. With reordering, we compute the
8: for 0 ≤ j < T c do low-rank intermediate P V ∈ R1×r in Θ(L r) and apply
lr
9: Load K j , V base,j , V lr√,j to ShrMem the up-projection in Θ(r d ), for a total of Θ(L r + r d )
10: S ← Mask(Q i K j ⊤/ d head ) computation. As a result, o s u in t ce L is the dominant term t o h u a t t
11: mn i ew ← max (cid:0) m i , rowmax(S) (cid:1) grows over agent trajectories, our approach reduces the com-
12: α ← exp(m i − mn i ew) putation of LR cache expansion by approximately a factor of
13: P i ← exp(S − mn i ew) r/d out ≪ 1. Algorithm 1 realizes this idea by augmenting
14: ℓ i ← α ⊙ ℓ i + rowsum(P i ) FlashAttention (Dao et al., 2022; 2023). Here, d is used
head
15: O i ← α ⊙ O i + P i V base,j instead of d to show the head-wise computation explicit.
out
16: O lr,i ← α ⊙ O lr,i + P i V lr,j A generalized analysis of the computation overhead, along
17: m i ← mn i ew with further algorithmic details, is provided in Appendix B.
18: end for
19: O i ← O i + O lr,i B 4. Experiments
20: Write O i ← O i /ℓ i
21: end for 4.1. Implementation Detail
Agent Setup We evaluate the accuracy and efficiency of
O(L2d ), considering that the LR cache expansion cost our cache sharing schemes in a multi-hop agent execution
model
framework, following AutoAct (Qiao et al., 2024). We fine-
is small (discussed in the Section 3.3).
tune three role-specific agents, plan, action, and reflect. The
plan agent performs reasoning and selects which external
3.3. Flash-LoRA-Attention
tool to invoke based on the reasoning. The action agent
Naive runtime expansion of the LR cache introduces non- produces tool-specific arguments and executes the selected
trivial computational overhead compared to fully shared API calls, including web search (Google Developers, 2025)
caching because it scales with both the accumulated se- and Wikipedia lookup (Yao et al., 2023b). The reflect agent
quence length L and the full output dimension d . Unlike reviews the accumulated trajectory and decides whether to
out
prior low-rank cache compression methods (Yuan et al., terminate with a final answer or to continue the interaction.
2023; Tomar et al., 2025; Chang et al., 2025) that treat the
Models and Datasets We evaluate on LLaMA-3.1-8B-
expansion of the compressed caches as an inevitable over-
Instruct and Ministral-8B-Instruct. We fine-tune and evalu-
head, our approach explicitly reduces it via reordered com-
ate on a split of 2.5k HotpotQA (Yang et al., 2018) and 2.0k
putation with the attention weight. Specifically, we reorder
ScienceQA (Lu et al., 2022) datasets, which require external
the matrix multiplications so that the attention-weighted
knowledge and multi-step reasoning to answer. For training,
multiplication is performed directly on the LR cache first,
we use the synthetic and filtered agent trajectories released
and the up-projection is applied afterward, making the over-
by AutoAct. For evaluation, we run multi-hop inference
head scale with the small rank dimension rather than d .
out on the test set with three difficulty levels of HotpotQA and
Concretely, suppose the base cache V
base
∈ RL×dout and
ScienceQA questions, using 20 iterations for each level.
a LR cache V ∈ RL×r for the value projection. Given
lr Agent prompts and trajectory templates are provided in the
the up-projection matrix B, the adapter contribution is
Appendix C.1.
V
lr
B ∈ RL×dout. A straightforward implementation is to
first reconstruct the adapter contribution and then applies Training Settings For shared-A multi-LoRA, we simplify
attention with attention weights P to produce the attention the dynamic token-wise routers used in prior work (Tian
6

## Page 7

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
Table 3. Benchmark accuracy (%) of the default non-sharing scheme and cache sharing schemes on HotpotQA and ScienceQA at each
level. For each model, the tiny value in the Avg. column denotes the difference from the corresponding Non-Shared baseline.
HotpotQA ScienceQA
Model Method Easy Medium Hard Avg. 1-4 5-8 9-12 Avg.
Non-Shared 42.80 41.95 31.90 38.88 0.00 70.63 60.54 76.75 69.31 0.00
FullShared 41.15 39.15 28.90 36.40 -2.48 68.00 55.67 72.00 65.22 -4.08
LLaMA-3.1-8B-Instruct DroidSpeak 40.60 39.55 30.15 36.77 -2.12 68.79 59.25 74.42 67.49 -1.82
BaseShared 42.70 41.95 31.15 38.60 -0.28 70.38 60.75 76.58 69.24 -0.07
BaseLRShared 42.40 40.80 30.55 37.92 -0.97 70.42 60.25 76.71 69.13 -0.18
Non-Shared 41.30 37.75 28.75 35.93 0.00 71.50 63.83 70.92 68.75 0.00
FullShared 39.60 33.95 24.80 32.78 -3.15 68.83 57.33 64.25 63.47 -5.28
Ministral-8B-Instruct DroidSpeak 40.85 35.65 26.95 34.48 -1.45 68.88 59.54 69.96 66.13 -2.63
BaseShared 40.95 37.60 29.00 35.85 -0.08 70.75 63.25 70.25 68.08 -0.67
BaseLRShared 41.10 37.70 27.15 35.32 -0.62 69.71 62.08 70.17 67.32 -1.43
et al., 2024) into a static assignment that selects agent-
specific LoRA weights for each predefined role. Under
this setting, we observe an accuracy gain over naive multi-
LoRA, both with and without cache sharing methods even
in mixed domain settings (see Appendix C.2 and C.3). We
therefore use the shared-A weights for our main accuracy
evaluations. Since shared-A is implemented by duplicating
the same A weights across agents, it does not change the
multi-LoRA architecture, and therefore does not affect ef-
ficiency comparisons. We applied LoRA with rank r = 8
Figure 4. System throughput (tokens per second) of BaseShared
on query and value projections. Accuracy and efficiency and BaseLRShared, with Flash-LoRA-Attention (FLA).
results for LoRA applied to the query, key, value, and output
projections are provided in Appendix D.1, where our setting detailed construction of the emulated trace and the latency
exhibits dominant accuracy. Detailed training hyperparame- analysis on the actual HotpotQA benchmark are presented
ters and loss curves are reported in the Appendix C.4. in Appendix C.6 and Appendix D.2, respectively. We con-
ducted experiments on a single NVIDIA A6000 48GB GPU.
Baselines We compare against the default Non-Shared
baseline, and several cache sharing methods. These include
4.2. Benchmark Accuracy
FullShared, which shares the entire KV cache across
agents without any recomputation, and DroidSpeak. For We demonstrate that both of our cache sharing schemes
DroidSpeak, we follow the official Pareto-optimal configura- preserve accuracy more effectively than prior baselines,
tion in in (Liu et al., 2026) and recompute the top 33% most as shown in Table 3. BaseShared stays close to
sensitive layers at runtime, selected by probing HotpotQA Non-Shared, with an average accuracy drop of at most
accuracy. The selected layers are listed in the Appendix C.5. 0.7%. BaseLRShared also maintains strong accuracy,
We note that prefix-aware positional embedding matching with an average drop of at most 1.5%. In contrast,
methods such as KVLink, KVFlow, and KVComm reduce FullShared and DroidSpeak exhibit larger average
to FullShared in our setup with identical agent prefixes. drops, up to 5.3% and 2.6%, respectively. Overall, these
results indicate that decoupling the cache into a shared base
Efficiency Evaluation We observe that latency in agent sys-
component and a low-rank component is a key factor for
tems depends on both the cache sharing method’s efficiency
robust KV cache sharing, compared with selective recompu-
and the system accuracy, since lower-accuracy methods tend
tation such as DroidSpeak. Additionally, we provide further
to take more steps and accumulate longer contexts. To mea-
analysis of out-of-function incident ratios where the system
sure the intrinsic efficiency of each cache sharing scheme,
fails to produce an answer, rank ablations, and deviation of
we evaluate latency under a controlled trace of sequence
scores in Appendix D.3, D.4, and D.5.
lengths, similar to the evaluation protocol of KVComm (Ye
et al., 2025). We construct this trace by varying the amount
4.3. System Efficiency
of context retrieved from external tools from 1k to 64k to-
kens, and we feed the same trace to all schemes. This yields We report system throughput and time-to-first-token (TTFT)
total sequence lengths ranging from 2k to 66k tokens. The in Table 4 and Table 5, respectively. We define system
7

## Page 8

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
Table 4. System throughput (tokens per second) under each total sequence length of the traces. OOM indicates out-of-memory.
Model Method 1.9k 3.0k 5.0k 9.1k 17.3k 33.7k 66.4k
Non-Shared 176.2 262.4 401.3 592.1 669.2 683.2 OOM
FullShared 193.7 293.4 468.5 808.1 1246.1 1697.6 1826.5
LLaMA-3.1-8B-Instruct DroidSpeak 182.4 263.5 412.3 633.5 844.2 931.0 813.1
BaseShared 169.0 257.0 392.3 617.3 862.8 969.6 823.2
BaseLRShared 188.7 279.4 463.8 785.7 1239.4 1678.1 1790.6
Non-Shared 158.9 231.0 361.5 541.2 610.7 638.4 OOM
FullShared 169.9 251.4 420.3 711.2 1163.9 1538.6 1768.3
Ministral-8B-Instruct DroidSpeak 160.9 251.4 360.3 570.2 785.1 856.0 OOM
BaseShared 157.0 227.4 364.0 552.1 796.5 885.0 870.5
BaseLRShared 164.1 247.9 410.9 703.2 1159.2 1521.9 1757.0
Table 5. TTFT (second) under each total sequence length of the traces. OOM indicates out-of-memory. Lower is better.
Model Method 1.9k 3.0k 5.0k 9.1k 17.3k 33.7k 66.4k
Non-Shared 1.94 2.55 3.72 6.79 16.38 38.87 OOM
FullShared 1.13 1.28 1.63 2.40 4.19 9.13 23.28
LLaMA-3.1-8B-Instruct DroidSpeak 1.62 2.17 3.22 5.55 11.15 25.43 67.80
BaseShared 1.62 2.12 3.06 5.26 10.51 23.91 67.80
BaseLRShared 1.13 1.28 1.64 2.43 4.24 9.19 23.35
Non-Shared 2.02 2.65 3.85 6.84 17.67 41.67 OOM
FullShared 1.19 1.35 1.69 2.50 4.37 9.30 20.84
Ministral-8B-Instruct DroidSpeak 1.65 2.22 3.28 5.69 11.53 26.71 OOM
BaseShared 1.66 2.19 3.17 5.43 10.85 25.57 59.62
BaseLRShared 1.20 1.35 1.71 2.53 4.42 9.38 20.98
throughput as the total processed sequence length divided
by the end-to-end latency. TTFT is the sum of prefill la-
tencies across agent steps, since each step incurs a new
model generation in multi-hop scenarios. We first demon-
strate the impact of Flash-LoRA-Attention in Figure 4. It
yields up to a 1.24× gain in throughput for BaseShared
and up to a 1.35× gain for BaseLRShared. This
shows that reducing LR cache expansion overhead en-
ables substantial speedups. With Flash-LoRA-Attention
enabled, BaseShared achieves up to a 1.42× gain and Figure 5. Memory usage (GB) of cache sharing methods on total
BaseLRShared achieves up to a 2.46× gain in through- sequence length of 66.4k on Ministral-8B-Instruct.
put, approaching the upper bound of full cache sharing
with FullShared. DroidSpeak reaches a similar through- BaseLRShared are negligible in size. We note that under
put gain to BaseShared, up to 1.36×, since both meth- group-query attention (GQA), the hidden state cache used
by DroidSpeak is slightly larger than the KV cache for a
ods compute hidden states for tokens that have not been
layer, which led to near out-of-memory (OOM) behavior
processed by the current agent. A similar trend holds as
in some cases of our experiments. We provide a detailed
the context overlap ratio varies, where our methods con-
memory analysis in Appendix D.7.
sistently exhibit high throughput gain (see Appendix D.6).
For TTFT, BaseShared and BaseLRShared provide
up to 1.63× and 4.44× reductions, respectively, both ex- 5. Conclusion
ceeding DroidSpeak which achieves up to a 1.56× reduction.
BaseLRShared achieves TTFT reductions close to those In this work, we introduce LRAGENT, a KV cache sharing
of FullShared. framework for multi-LoRA agent systems that decouples
the value cache into a shared base cache and an adapter-
Additionally, BaseShared and BaseLRShared re- dependent LR cache. BaseShared reduces KV memory
duce KV cache memory by nearly 1/3 compared to by sharing the base cache, and BaseLRShared further
Non-Shared baseline, as shown in Figure 5, which reduces computation by sharing the LR cache under shared-
is comparable to other cache-sharing baselines and A multi-LoRA variants while preserving role-specific be-
only marginally higher than FullShared within 1GB. haviors. We validate that these methods preserve accuracy
This is because the LR caches in BaseShared and close to the non-shared baseline. Flash-LoRA-Attention pro-
8

## Page 9

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
vides substantial efficiency gains by avoiding full-dimension K.-C., Ceze, L., et al. xkv: Cross-layer svd for kv-
materialization of the LR cache, enabling throughput and cache compression. arXiv preprint arXiv:2503.18893,
TTFT improvements close to fully shared caching. Overall, 2025. doi: 10.48550/arXiv.2503.18893. URL https:
LRAGENT consistently outperforms prior cache sharing //arxiv.org/abs/2503.18893.
baselines in both accuracy and efficiency.
Dao, T., Fu, D. Y., Ermon, S., Rudra, A., and Re, C. Flashat-
tention: Fast and memory-efficient exact attention with
Acknowledgments
io-awareness. In Advances in Neural Information Pro-
cessing Systems, volume 35, pp. 16344–16359, 2022. doi:
This work was supported in part by Institute of Informa-
10.5555/3600270.3601459. URL https://github.
tion & communications Technology Planning & Evalua-
com/Dao-AILab/flash-attention. Paper:
tion (IITP) grant funded by the Korea government (MSIT)
arXiv:2205.14135, code repository linked in url field.
(No.RS-2026-25507427: Development of Efficient Archi-
tectures and Training Techniques for High-Performance Dao, T., Haziza, D., Massa, F., and Sizov, G. Flash-
Lightweight AI Models, No.RS-2025-02273157: Develop- decoding for long-context inference. PyTorch Blog, Oc-
ment of Low Power Training/Inference Technologies based tober 2023. URL https://pytorch.org/blog/
on AI Semiconductors, RS-2023-00256081: artificial intel- flash-decoding/. Updated Nov 16, 2024.
ligence semiconductor support program to nurture the best
talents), and BK21 FOUR program. (Corresponding Author: DeepSeek-AI, Liu, A., Feng, B., Xue, B., Wang, B., Wu,
Jae-Joon Kim). B., et al. Deepseek-v3 technical report. arXiv preprint
arXiv:2412.19437, 2024. doi: 10.48550/arXiv.2412.
19437. URL https://arxiv.org/abs/2412.
Software and Data
19437.
We provide a file upload that reproduces the main results
Dubey, A., Jauhri, A., Pandey, A., Kadian, A., Al-Dahle,
in this paper, including training, evaluation, and latency
A., et al. The llama 3 herd of models. arXiv preprint
measurements under the same experimental settings. De-
arXiv:2407.21783, 2024. doi: 10.48550/arXiv.2407.
tailed descriptions and step-by-step guidelines, such as en-
21783.
vironment setup and commands to run each experiment, are
included in the uploaded file. Fu, D., He, K., Wang, Y., Hong, W., Gongque, Z.,
Zeng, W., et al. Agentrefine: Enhancing agent gen-
eralization through refinement tuning. arXiv preprint
Impact Statement
arXiv:2501.01702, 2025a.
This paper presents work whose goal is to advance the field
Fu, T., Min, Z., Zhang, H., Yan, J., Dai, G., Ouyang, W.,
of deep learning and large language models. There are many
et al. Cache-to-Cache: Direct semantic communica-
potential societal consequences of our work, none of which
tion between large language models. arXiv preprint
we feel must be specifically highlighted here.
arXiv:2510.03215, 2025b. doi: 10.48550/arXiv.2510.
03215. URL https://arxiv.org/abs/2510.
References 03215.
Bai, T., Yang, L., Wong, Z. H., Sun, F., Zhuang, X., Peng,
Google Developers. Custom Search JSON API: Introduc-
J., et al. Efficient pretraining data selection for language
tion. Programmable Search Engine Documentation, 2025.
models via multi-actor collaboration. In Proceedings of URL https://developers.google.com/
the 63rd Annual Meeting of the Association for Compu- custom-search/v1/introduction?hl=ko.
tational Linguistics (Volume 1: Long Papers), pp. 9465–
Last updated 2025-08-31. Accessed 2026-01-06.
9491, Vienna, Austria, jul 2025. Association for Com-
putational Linguistics. doi: 10.18653/v1/2025.acl-long. Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang,
466. URL https://aclanthology.org/2025. S., et al. LoRA: Low-rank adaptation of large lan-
acl-long.466/. guage models. In International Conference on Learn-
ing Representations, 2022. doi: 10.48550/arXiv.2106.
Bo, X., Chen, X., Dai, Q., Feng, X., Li, R., Wang, L., 09685. URL https://openreview.net/forum?
et al. Reflective multi-agent collaboration based on large id=nZeVKeeFYf9.
language models. In Advances in Neural Information Pro-
Jiang, A. Q., Sablayrolles, A., Mensch, A., Bamford, C.,
cessing Systems, volume 37, pp. 138595–138631, 2024.
Chaplot, D. S., de las Casas, D., et al. Mistral 7b. arXiv
doi: 10.52202/079017-4397.
preprint arXiv:2310.06825, 2023. doi: 10.48550/arXiv.
Chang, C.-C., Lin, C.-Y., Akhauri, Y., Lin, W.-C., Wu, 2310.06825.
9

## Page 10

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
Li, B., Wang, Y., Ma, H., Chen, L., Xiao, J., and Wang, Annual Meeting of the Association for Computational
S. Mobilora: Accelerating lora-based llm inference on Linguistics (Volume 1: Long Papers), pp. 3003–3021,
mobile devices via context-aware kv cache optimiza- Bangkok, Thailand, August 2024. Association for Com-
tion. In Proceedings of the 63rd Annual Meeting of putational Linguistics. doi: 10.18653/v1/2024.acl-long.
the Association for Computational Linguistics (Volume 165. URL https://aclanthology.org/2024.
1: Long Papers), pp. 23400–23410, Vienna, Austria, acl-long.165/.
July 2025. Association for Computational Linguistics.
Qin, Y., Liang, S., Ye, Y., Zhu, K., Yan, L., Lu, Y., et al.
doi: 10.18653/v1/2025.acl-long.1140. URL https://
Toolllm: Facilitating large language models to master
aclanthology.org/2025.acl-long.1140/.
16000+ real-world apis. In The Twelfth International
Liu, S., Chen, T., Liang, Z., Lyu, X., and Amato, C. Llm Conference on Learning Representations, 2024.
collaboration with multi-agent reinforcement learning.
Rasal, S. Llm harmony: Multi-agent communication for
arXiv preprint arXiv:2508.04652, 2025a.
problem solving. arXiv preprint arXiv:2401.01312, 2024.
Liu, Y., Lin, K. Q., Chen, C. W., and Shou, M. Z. Video-
Shen, W., Li, C., Chen, H., Yan, M., Quan, X., Chen, H.,
mind: A chain-of-LoRA agent for long video reason-
et al. Small llms are weak tool learners: A multi-llm agent.
ing. arXiv preprint arXiv:2503.13444, 2025b. doi:
In Proceedings of the 2024 Conference on Empirical
10.48550/arXiv.2503.13444. URL https://arxiv.
Methods in Natural Language Processing, pp. 16658–
org/abs/2503.13444.
16680, 2024.
Liu, Y., Huang, Y., Yao, J., Feng, S., Gu, Z., Du, K., et al.
Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., and
DroidSpeak: KV cache sharing for cross-LLM commu-
Yao, S. Reflexion: Language agents with verbal rein-
nication and multi-LLM serving. In Proceedings of the
forcement learning. In Advances in Neural Information
23rd USENIX Symposium on Networked Systems Design
Processing Systems, volume 36, pp. 8634–8652, 2023.
and Implementation (NSDI ’26). USENIX Association,
2026. doi: 10.48550/arXiv.2411.02820. URL https: Snell, C., Lee, J., Xu, K., and Kumar, A. Scaling llm test-
//arxiv.org/abs/2411.02820. Accepted for time compute optimally can be more effective than scal-
NSDI 2026. ing model parameters. arXiv preprint arXiv:2408.03314,
2024. doi: 10.48550/arXiv.2408.03314.
Lu, P., Mishra, S., Xia, T., Qiu, L., Chang, K.-W., Zhu,
S.-C., Tafjord, O., Clark, P., and Kalyan, A. Learn to Stoica, G., Bolya, D., Bjorck, J., Wang, J., Hsiao, J., Fatemi,
explain: Multimodal reasoning via thought chains for M., and Hoffman, J. Model merging with SVD to tie
science question answering. In Advances in Neural Infor- the knots. In The Thirteenth International Conference on
mation Processing Systems, volume 35, pp. 2507–2521, Learning Representations, 2025.
2022.
Subramaniam, V., Du, Y., Tenenbaum, J. B., Torralba,
Luong, H.-C. and Chen, B. Why LoRA fails to forget: A., Li, S., and Mordatch, I. Multiagent finetuning:
Regularized low-rank adaptation against backdoors in Self improvement with diverse reasoning chains. In
language models. arXiv preprint arXiv:2601.06305, 2026. International Conference on Learning Representations,
doi: 10.48550/arXiv.2601.06305. 2025. doi: 10.48550/arXiv.2501.05707. URL https:
//arxiv.org/abs/2501.05707.
OpenAI, Hurst, A., Lerer, A., Goucher, A. P., Perelman, A.,
Ramesh, A., et al. Gpt-4o system card. arXiv preprint Talebirad, Y. and Nadiri, A. Multi-agent collaboration:
arXiv:2410.21276, 2024. doi: 10.48550/arXiv.2410. Harnessing the power of intelligent llm agents. arXiv
21276. URL https://arxiv.org/abs/2410. preprint arXiv:2306.03314, 2023.
21276.
Tian, C., Shi, Z., Guo, Z., Li, L., and Xu, C. Hydralora:
Pan, Z., Patel, A. D., Shen, Y., Hu, Z., Guan, Y., Li, An asymmetric lora architecture for efficient fine-tuning.
W.-L., et al. KVFlow: Efficient prefix caching for In Advances in Neural Information Processing Systems,
accelerating LLM-based multi-agent workflows. In volume 37, pp. 9565–9584, 2024. doi: 10.5555/3737916.
Advances in Neural Information Processing Systems 3738220. URL https://proceedings.neurips.
(NeurIPS 2025), 2025. URL https://arxiv.org/ cc/.
abs/2507.07400.
Tomar, A., Hooper, C., Lee, M., Xi, H., Tiwari, R., Kang,
Qiao, S., Zhang, N., Fang, R., Luo, Y., Zhou, W., Jiang, Y., W., et al. Xquant: Breaking the memory wall for llm
et al. AutoAct: Automatic agent learning from scratch inference with kv cache rematerialization. arXiv preprint
for QA via self-planning. In Proceedings of the 62nd arXiv:2508.10395, 2025. doi: 10.48550/arXiv.2508.
10

## Page 11

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
10395. URL https://arxiv.org/abs/2508. Yang, Z., Qi, P., Zhang, S., Bengio, Y., Cohen, W., Salakhut-
10395. dinov, R., and Manning, C. D. Hotpotqa: A dataset
for diverse, explainable multi-hop question answering.
Touvron, H., Martin, L., Stone, K., Albert, P., Almahairi,
In Proceedings of the 2018 Conference on Empirical
A., Babaei, Y., et al. Llama 2: Open foundation and fine-
Methods in Natural Language Processing, pp. 2369–
tuned chat models. arXiv preprint arXiv:2307.09288,
2380, Brussels, Belgium, 2018. Association for Compu-
2023. doi: 10.48550/arXiv.2307.09288. URL https:
tational Linguistics. doi: 10.18653/v1/D18-1259. URL
//arxiv.org/abs/2307.09288.
https://aclanthology.org/D18-1259/.
Wang, Y., Lin, Y., Zeng, X., and Zhang, G. Multi-
Yao, J., Li, H., Liu, Y., Ray, S., Cheng, Y., Zhang, Q.,
lora: Democratizing lora for better multi-task learn-
et al. CacheBlend: Fast large language model serving
ing. arXiv preprint arXiv:2311.11501, 2023. doi:
for RAG with cached knowledge fusion. In Proceed-
10.48550/arXiv.2311.11501. URL https://arxiv.
ings of the Twentieth European Conference on Com-
org/abs/2311.11501.
puter Systems (EuroSys ’25), pp. 94–109, New York,
NY, USA, 2025. Association for Computing Machin-
Wei, J., Wang, X., Schuurmans, D., Bosma, M., Xia, F., Chi,
ery. doi: 10.1145/3689031.3696098. URL https:
E., et al. Chain-of-thought prompting elicits reasoning in
//arxiv.org/abs/2405.16444.
large language models. In Advances in Neural Informa-
tion Processing Systems, volume 35, pp. 24824–24837,
Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T., Cao, Y.,
2022.
et al. Tree of thoughts: Deliberate problem solving with
large language models. In Advances in Neural Informa-
Woo, S., Kim, H., Kil, J., Kim, M., Kim, J., Seo, A., et al.
tion Processing Systems, volume 36, pp. 11809–11822,
Icarus: Identical cache reuse for efficient multi-model
2023a.
inference. OpenReview, ICLR 2026 Conference Sub-
mission, 2025. URL https://openreview.net/
Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan,
forum?id=qrMo6R7lOS. Accessed 2026-01-02.
K. R., et al. React: Synergizing reasoning and acting in
Wu, Q., Bansal, G., Zhang, J., Wu, Y., Li, B., Zhu, E., et al. language models. In The Eleventh International Confer-
Autogen: Enabling next-gen llm applications via multi- ence on Learning Representations, 2023b.
agent conversations. In First Conference on Language
Ye, H., Gao, Z., Ma, M., Wang, Q., Fu, Y., Chung, M.-
Modeling, jul 2024. URL https://openreview.
Y., et al. KVCOMM: Online cross-context KV-cache
net/forum?id=BAakY1hNKS.
communication for efficient LLM-based multi-agent sys-
Xia, Y., Fu, F., Zhang, W., Jiang, J., and Cui, B. Efficient tems. In Advances in Neural Information Processing Sys-
multi-task LLM quantization and serving for multiple tems (NeurIPS 2025), 2025. doi: 10.48550/arXiv.2510.
LoRA adapters. In Advances in Neural Information Pro- 12872. URL https://arxiv.org/abs/2510.
cessing Systems, volume 37, pp. 63686–63714, 2024. doi: 12872. Accepted for publication in NeurIPS 2025.
10.5555/3737916.3739950.
Yu, X., Luo, T., Wei, Y., Lei, F., Huang, Y., Peng, H.,
Yang, A., Yu, B., Li, C., Liu, D., Huang, F., Huang, H., et al. Neeko: Leveraging dynamic LoRA for efficient
et al. Qwen2.5-1m technical report. arXiv preprint multi-character role-playing agent. In Proceedings of
arXiv:2501.15383, 2025a. doi: 10.48550/arXiv.2501. the 2024 Conference on Empirical Methods in Natu-
15383. ral Language Processing, pp. 12540–12557, Miami,
Florida, USA, November 2024. Association for Compu-
Yang, J., Hou, B., Wei, W., Bao, Y., and Chang, S. tational Linguistics. doi: 10.18653/v1/2024.emnlp-main.
KVLink: Accelerating large language models via effi- 697. URL https://aclanthology.org/2024.
cient KV cache reuse. arXiv preprint arXiv:2502.16002, emnlp-main.697/.
2025b. doi: 10.48550/arXiv.2502.16002. URL https:
//arxiv.org/abs/2502.16002. Yuan, Z., Shang, Y., Song, Y., Wu, Q., Yan, Y., Sun, G., et al.
Asvd: Activation-aware singular value decomposition
Yang, Y., Muhtar, D., Shen, Y., Zhan, Y., Liu, J., for compressing large language models. arXiv preprint
Wang, Y., et al. Mtl-lora: Low-rank adaptation arXiv:2312.05821, 2023. doi: 10.48550/arXiv.2312.
for multi-task learning. In Proceedings of the AAAI 05821. URL https://arxiv.org/abs/2312.
Conference on Artificial Intelligence, volume 39, pp. 05821.
22010–22018, 2025c. doi: 10.1609/aaai.v39i20.
35509. URL https://ojs.aaai.org/index. Zhang, C., Goh, X. D., Li, D., Zhang, H., and Liu, Y. Plan-
php/AAAI/article/view/35509. ning with multi-constraints via collaborative language
11

## Page 12

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
agents. In Proceedings of the 31st International Confer-
ence on Computational Linguistics, pp. 10054–10082,
Abu Dhabi, UAE, jan 2025. Association for Computa-
tional Linguistics. URL https://aclanthology.
org/2025.coling-main.672/.
12

## Page 13

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
A. Base Cache and Adapter Output
A.1. Cache L1 norm
As discussed in Section 3.1, the output contributions from the pretrained base weights and the low-rank adapters differs in
magnitude. We analyze the average output magnitude of the value projection in a multi-LoRA system with three agents,
where the pretrained base-weight contribution is treated as the base cache and the LoRA contribution is treated as the
adapter output. As shown in Figure 6, the base cache and adapter output magnitudes follow similar trends across layers, but
the adapter outputs are much smaller, by factors of 27.3 and 14.77 for LLaMA-3.1-8B-Instruct and Ministral-8B-Instruct,
respectively.
Given that the base cache remains highly similar across agents while the adapter outputs are largely decorrelated, the adapter
output can be viewed as a small but non-trivial, approximately random perturbation to the base cache. This motivates sharing
the base cache rather than the full cache.
Figure 6. L1 norm of the base cache and adapter output across model layers.
A.2. Input Activation Cosine Similarity
We observe consistently high similarity in input activations across agents, which naturally leads to high base cache similarity.
Figure 7 presents the layerwise cosine similarity of input activations across three agents. The activations show high similarity
across agents and exhibit a trend consistent with other forms of cache similarity. Specifically, similarity is higher in earlier
layers and gradually decreases in deeper layers, aligning with the observations in Section 3.1 and Figure 1.
Since the base cache is computed by projecting activations with shared pretrained weights, its similarity scales with activation
similarity. In contrast, the inclusion of adapter weights in the full KV cache introduces additional variations, leading to
lower similarity despite identical input activations.
Figure 7. Input activation cosine similarity across agent pairs in LLaMA-3.1-8B-Instruct.
13

## Page 14

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
A.3. Cosine Similarity Bound
As shown in Section 3.1, the base cache remains highly similar across agents for the same context, while the adapter outputs
are largely decorrelated across agent pairs. This implies that the full cache can be viewed as the base cache perturbed by an
approximately random adapter component. In this section, we formalize the resulting effect on similarity: we show that,
under the approximate orthogonality assumptions on adapter outputs consistent with our empirical observations, the cosine
similarity of the base cache is higher than that of the full cache.
Based on the observed low similarity, or high orthogonality, between the base cache and adapter contributions, as well
as among adapter contributions (Tables 1 and 6, respectively), we derive the following bound showing that the full cache
exhibits lower cosine similarity. We note that the orthogonality between the base cache and adapter contributions is a
practical approximation rather than a strict condition. In multi-LoRA systems with heterogeneous agent roles, the shared
pretrained backbone tends to preserve common representations, whereas LoRA fine-tuning captures more role-specific
variations. This interpretation is consistent with prior work suggesting that LoRA updates are often only weakly aligned
with pretrained directions (Stoica et al., 2025; Luong & Chen, 2026).
Following the multi-LoRA convention in Section 3.1, the base cache and adapter output are defined as:
Y := X W , ∆Y := X ∆W , Y := Y + ∆Y . (4)
base,i i 0 i i i i base,i i
Assuming that the adapter outputs are approximately orthogonal to the base cache and decorrelated across agents:
Y ⊤ ∆Y = 0, Y ⊤ ∆Y = 0, Y ⊤ ∆Y = ∆Y ⊤Y = ∆Y ⊤∆Y = 0, (i ̸= j). (5)
base,i i base,j j base,i j i base,j i j
This satisfies the following:
Y ⊤Y = (Y + ∆Y )⊤(Y + ∆Y ) = Y ⊤ Y . (6)
i j base,i i base,j j base,i base,j
Furthermore, we have
∥Y ∥2 = ∥Y + ∆Y ∥2 = ∥Y ∥2 + ∥∆Y ∥2 ≥ ∥Y ∥2, (7)
i base,i i base,i i base,i
and similarly ∥Y ∥ ≥ ∥Y ∥. Therefore,
j base,j
cos(Y , Y ) = Y i ⊤Y j = Y b ⊤ ase,i Y base,j ≤ Y b ⊤ ase,i Y base,j = cos(Y , Y ), (8)
i j ∥Y ∥ ∥Y ∥ ∥Y ∥ ∥Y ∥ ∥Y ∥ ∥Y ∥ base,i base,j
i j i j base,i base,j
and taking expectation over contexts yields
E(cid:2)
cos(Y , Y )
(cid:3)
≥
E(cid:2)
cos(Y , Y )
(cid:3)
, (9)
base,i base,j i j
which states that the base cache cosine similarity is higher than the full cache cosine similarity.
Table 6. Cosine similarity between base cache and adapter outputs across agent pairs.
Contribution ∆Y plan ∆Y action ∆Y reflect
Y 0.0033 0.0050 -0.0003
base,plan
Y 0.0188 0.0985 0.0006
base,action
Y -0.0076 0.0037 0.0488
base,reflect
14

## Page 15

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
A.4. Key Cache Cosine Similarity
As noted in Section 3.1, in typical multi-LoRA settings the key cache remains highly similar across agents. In particular, the
minimum key cache similarity already exceeds the average base-cache similarity reported in Table 1.
Figure 8 reports pairwise cosine similarity of the key cache for each model. The average similarity is 0.9922 for LLaMA-
3.1-8B-Instruct and 0.9840 for Ministral-8B-Instruct, and even the minimum similarity across agent pairs is higher than the
corresponding average base-cache similarity: 0.9726 and 0.9530, respectively. This indicates that the primary cross-agent
differences come from the value cache, mainly through the adapter-induced component. Therefore, we simply share the
entire key cache across agents in all of our schemes.
Figure 8. K cache Cosine similarity of each agent pairs across the model layers.
A.5. Agent Role Heterogeneity and Cache Similarity
The observations and experiments in our paper consider strongly heterogeneous agent roles (e.g., planning, action, and
reflection), which are functionally distinct in representative multi-agent frameworks (Yao et al., 2023b; Shinn et al., 2023;
Qiao et al., 2024). To further examine generalizability under a different role structure, we additionally evaluate debate-style
agents on the MATH dataset, following a multi-agent fine-tuning setting (Subramaniam et al., 2025). Table 7 shows that the
base cache remains more similar than the full cache, and the LR cache also shows high similarity. These results support our
key observation that base cache similarity is consistently higher than full KV cache similarity across different settings.
We also note that our method does not rely on the absolute level of base cache similarity, but on the relative relationship that
the base cache is more similar than the full KV cache across agents. Since cross-agent differences mainly come from adapter
outputs, increasing agent heterogeneity is expected to reduce full KV cache similarity more than base cache similarity. Our
method, LRAgent, is designed to use this property. In contrast, conventional cache sharing methods do not separate the
shared pretrained component from the agent-specific adapter component, and thus cannot capture this structure as clearly.
Thus in general, we expect our method to exhibit dominant effectivity in various heterogeneous agent role scenarios.
We acknowledge that evaluating on a broader range of datasets would further strengthen the generalizability of our method.
However, due to the lack of open-sourced agent trajectories and evaluation frameworks, our experiments are currently
limited to AutoAct-based settings. Based on the observations presented above, we nevertheless expect our method to remain
effective in diverse heterogeneous scenarios, and we plan to extend our evaluation as more trajectories and benchmarks
become available.
Table 7. Average cosine similarity between two debate agents (e.g. generation and critic) on the MATH dataset in LLaMA-3.1-8B-Instruct.
Results are computed over 128 sampled contexts sequence length of 2k for each.
Contribution Full cache Base cache LR cache
Cosine Similarity 0.9553 0.9766 0.9620
15

## Page 16

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
B. Flash-LoRA-Attention
In this section, we provide a detailed description of Flash-LoRA-Attention, which is introduced in Section 3.3, and analyze
its computational overhead in a general form, following the notation in Section 3.2 and Figure 3.
Setup. We follow the notation in Algorithm 1 and describe the forward pass for a single attention head. Let L = L + L ,
p c
where L is the accumulated context length and L is the context length of the current prefill/decoding step. We denote
p c
the query and key as Q ∈ RLc×dhead and K ∈ RL×dhead, and the base value cache as V
base
∈ RL×dhead. For the LoRA
update on the value projection, we save the LR cache V
lr√
∈ RL×r and keep the up-projection matrix B ∈ Rr×dhead, where
r ≪ d
head
. With attention weight P = softmax (cid:0) QK⊤/ d
head
(cid:1) ∈ RLc×L, the output is
(cid:0) (cid:1)
O = P V + V B = O + O , O = P V , O = P V B (10)
base lr base lr base base lr lr
Matrix Multiplication Reordering Based on Associativity. A straightforward implementation materializes the full-
dimension adapter contribution V
lr
B ∈ RL×dhead for all L tokens and then applies attention:
O = P (V B). (11)
lr lr
This expands the LR cache to the head dimension over the entire trajectory, so the computation grows with both L and d .
head
Instead, we exploit associativity and reorder the computation as
(cid:0) (cid:1)
O = P V B, (12)
lr lr
so the length-L accumulation is performed in rank r, and the head-dimension multiplication by B is applied only once per
query block.
Compute Overhead. We report multiply-add counts up to constant factors and omit the shared base-attention cost for
O . Without reordering, we first form V B and then multiply by P :
base lr
(cid:0) (cid:1)
W/o reorder: L r d + L L d = O L r d + L L d . (13)
head c head head c head
(cid:124) (cid:123)(cid:122) (cid:125) (cid:124) (cid:123)(cid:122) (cid:125)
VlrB P (VlrB)
With reordering, we first accumulate M = P V
lr
∈ RLc×r and then apply B:
(cid:0) (cid:1)
Reorder: L L r + L r d = O L L r + L r d . (14)
c c head c c head
(cid:124) (cid:123)(cid:122) (cid:125) (cid:124) (cid:123)(cid:122) (cid:125)
P Vlr (P Vlr)B
Since r ≪ d , reordering replaces the dominant L L d -scaled expansion with an L L r-scaled low-rank accumula-
head c head c
tion, and the d -dependent multiplication appears only once after the accumulation.
head
Flash-LoRA-Attention Kernel Implementation. Algorithm 1 implements Eq. (12) by extending FlashAttention with
one additional low-rank accumulator. For each
√
query block Q
i
∈ RBr×dhead, the kernel streams over key/value blocks
(K , V ) and computes S = Mask(Q K⊤/ d ), maintaining the online-softmax statistics (m , ℓ ). Using the same
j base,j i j head i i
block-wise weights, it accumulates both O ← O + P V and the low-rank intermediate O ← O + P V , where
i i i base,j lr,i lr,i i lr,j
O
lr,i
∈ RBr×r remains in rank r throughout the streaming pass. After all blocks are processed, the kernel applies a single
post multiplication O ← O + O B and then normalizes by ℓ . This preserves FlashAttention’s memory-efficient I/O
i i lr,i i
pattern while ensuring that the LR cache expansion computation scales primarily with the rank, directly reducing the runtime
overhead in both BaseShared and BaseLRShared.
16

## Page 17

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
C. Implementation Details
C.1. Agent Prompts and Trajectory Templates
We present an example agent prompt and trajectory from our multi-LoRA agent system, based on the AutoAct implementa-
tion (Qiao et al., 2024). As shown in Figure 9, a trajectory accumulates a predefined system prompt, the user question, and
multiple rounds of agent-generated tokens interleaved with rule-based context inserts, such as tool outputs retrieved from
external sources. The example is from HotpotQA, and ScienceQA follows the similar template except for an explanation on
the additional image caption lookup tool.
The system prompt, which specifies the thought, action, and observation format, is identical for all agents and thus fully
shared. As a result, prefix positional alignment based KV cache sharing methods (Yang et al., 2025b; Pan et al., 2025; Ye
et al., 2025) reduce to FullShared in our setup.
The highlighted parts indicate agent-generated outputs, where agents execute in a predefined order (plan-plan-action). The
plan agent first produces reasoning and selects a tool, then the action agent generates the tool arguments. If the selected tool
is either Web search API, Wikipedia lookup, or image caption lookup that retrieves a predefined image caption, the retrieved
context is appended to the trajectory. If the selected tool is Finish, the action agent outputs a final answer and the reflect
agent is invoked to decide whether the answer is sufficient or whether another information retrieval round is needed. The
reflection step is divided into two stages, and it can override an incorrect Finish decision and return control to the plan agent
when the retrieved evidence is insufficient. The total number of agent iterations is limited to 45 per question.
We train the agents using filtered trajectories generated by a single LLaMA-2-70B-Chat model, provided by AutoAct.
Figure 9. Agent prompts and an example of an accumulated trajectory on HotpotQA.
17

## Page 18

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
C.2. Shared-A Multi-LoRA Architecture
We observe that simply sharing the LoRA down-projection matrix A yields higher accuracy than conventional multi-LoRA
training with independent (A , B ) pairs, consistent with prior findings (Tian et al., 2024; Yang et al., 2025c). Table 8 reports
i i
HotpotQA accuracy with and without shared-A. We note that we use the same training conditions and hyperparameters
listed in Appendix C.4, which yield the best results in both settings. Across all methods, the shared-A variant improves the
original (Non-Shared) accuracy and also benefits cache sharing schemes such as FullShared, BaseShared, and
BaseLRShared. In particular, BaseLRShared degrades when A is not shared, since sharing an LR cache computed
with different A matrices and expanding it with a mismatched B introduces large errors.
In our implementation, we duplicate the shared A across agents, which is the same implementation with conventional
multi-LoRA architecture and therefore inference efficiency is unchanged. Since shared-A improves accuracy in all settings
without introducing change of model structure or inference overheads, we conduct our main experiments using shared-A
multi-LoRA trained weights. We note that sharing A also reduces the number of trainable parameters by 33%, providing a
efficiency benefit in training.
Table 8. Accuracy (%) comparison between non-shared-A and shared-A multi-LoRA variants on HotpotQA easy benchmark.
Model Architecture Non-Shared FullShared BaseShared BaseLRShared
Non-shared A 42.05 40.30 41.85 36.25
LLaMA-3.1-8B-Instruct
Shared-A 42.80 +0.75 41.15 +0.85 42.70 +0.85 42.40 +6.15
Non-shared A 41.10 37.40 40.80 36.95
Ministral-8B-Instruct
Shared-A 41.30 +0.20 39.60 +2.20 40.95 +0.15 41.10 +4.15
C.3. Shared-A on Multi-Domain Dataset
Previous studies on multi-task LoRA show that sharing the down-projection across domains does not harm model quality
and can improve accuracy across tasks (Tian et al., 2024; Yang et al., 2025c).
Following this, we further examine whether the shared-A design in our method remains reliable when training data from
different benchmarks are mixed. We conduct an ablation study by mixing trajectories from HotpotQA and ScienceQA and
evaluating accuracy on each test set. We use the same hyperparameters and training setup described in Appendix C.4, and
train on a shuffled combination of the two datasets. Due to limited availability of open-source agent trajectories, we focus
on these two datasets.
As shown in Table 9, training on the mixed dataset does not degrade performance and gives accuracy comparable to training
on each dataset separately. The differences are small and within the reported evaluation variance. These results suggest that
the shared-A design generalizes well to mixed-task settings without loss in benchmark accuracy.
We acknowledge that, in systems where a multi-LoRA model has already been deployed and the model weights cannot
be modified, BaseLRShared may not be directly applicable because it requires shared-A to avoid accuracy degradation.
However, both our results and prior work suggest that shared-A is an effective design choice when building multi-LoRA
systems. From this perspective, we view shared-A not as a limitation, but as an opportunity to improve the multi-task
framework while enabling the more efficient BaseLRShared scheme.
Table 9. Benchmark accuracy (%) of BaseLRShared on HotpotQA and ScienceQA subtasks under separate and mixed-dataset training.
‘Data Mix’ denotes whether trajectories from both datasets are shuffled together during training.
Data Mix HotpotQA (Hard) ScienceQA (9-12)
x 31.15 76.58
o 31.30 76.65
18

## Page 19

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
C.4. Hyperparameter and Loss Curve
We report the training hyperparameters and loss curves for multi-LoRA agents in Table 10 and Figure 10, respectively. Most
hyperparameters, including the optimizer, scheduler, and weight decay, follow AutoAct (Qiao et al., 2024), and we perform
a grid search over learning rates and the number of training epochs. The sum of training time across all agents is 3.9 hours
for HotpotQA and 3.4 hours for ScienceQA on a single 48GB NVIDIA A6000 GPU. We also note that the HotpotQA and
ScienceQA test sets consist of 300 and 360 questions, respectively, and we run 20 iterations for each accuracy evaluation.
Table 10. Hyperparameter settings for multi-LoRA training.
Hyperparameter LLaMA-3.1-8B-Instruct Ministral-8B-Instruct
Optimizer AdamW
Batch Size 32
LR Scheduler cosine
Max Sequence Length 32786
Epochs 10
Warmup Ratio 0.05
Weight Decay 0
Rank 8
LoRA Dropout 0.05
LoRA Scale 16
Plan: 5e-5 Plan: 5e-5
Learning Rate Action: 6e-5 Action: 9e-5
Reflect: 6e-5 Reflect: 9e-5
Figure 10. Train loss and L2 norm of the gradient update for each agent types.
19

## Page 20

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
C.5. DroidSpeak Recomputation Layer Selection
We implement DroidSpeak as a baseline, following the methodology described in (Liu et al., 2026). In the original
implementation, KV caches are selectively recomputed for a set of critical layers, identified by probing the benchmark
accuracy drop when the KV cache is directly reused in each layer while the remaining layers are recomputed. DroidSpeak
provides a Pareto-optimal configuration that balances accuracy degradation and the inference efficiency gains from cache
sharing, corresponding to recomputing 33% of the model layers. Following this guideline, we probe critical layers on
HotpotQA and select 11 layers for LLaMA-3.1-8B-Instruct (32 layers total) and 12 layers for Ministral-8B-Instruct (36
layers total). In addition, since the first layer typically does not require recomputation in Ministral-8B-Instruct, we enable
hidden state caching that can be passed directly from the previous model to the current model to eliminate computation
for these layers. We note that recent models often use group-query attention (GQA), where the hidden state dimension
is typically four times larger than the output dimension of the key or value projections, so the hidden state cache can be
roughly twice as large as the KV cache of a single layer. This additional memory overhead is discussed in Appendix D.7.
Table 11. Selected layers for recomputation in DroidSpeak.
Model Selected layers
LLaMA-3.1-8B-Instruct 0, 2, 16, 19, 20, 22, 23, 24, 26, 30, 31
Ministral-8B-Instruct 1, 4, 5, 12, 14, 15, 17, 21, 22, 25, 29, 31
C.6. Emulated Trace for Efficiency Analysis
In the experiments on HotpotQA or ScienceQA benchmarks, methods with lower accuracy tend to produce longer trajectories
and thus accumulate longer contexts. Therefore, to enable fair efficiency comparisons of only the cache sharing method
itself under the same context length, we construct a fixed trace of context lengths and an agent schedule. This trace is based
on profiled trajectories, including the concatenated context length at each agent step and the number of steps per iteration.
On average, each iteration consists of 17 steps, comprising five plan-plan-action cycles and two reflect steps at the end of the
iteration.
We vary the retrieved context length L from 0.25k to 16k, which results in total trajectory lengths ranging from 1.9k to
ctx
66.4k, as reported in Table 4 and Table 5. We note that the detailed agent trajectory templates are described in Appendix C.1.
Table 12. Agent iteration trace with prefill and generation lengths.
Agent Type Step Prefill Generation
plan 1 512 32
plan 2 8 8
action 3 8 8
plan 4 L 32
ctx
plan 5 8 8
action 6 8 8
plan 7 L 32
ctx
plan 8 8 8
action 9 8 8
plan 10 L 32
ctx
plan 11 8 8
action 12 8 8
plan 13 L 32
ctx
plan 14 8 8
action 15 8 8
reflect 16 32 32
reflect 17 8 8
20

## Page 21

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
D. Ablative Experiments
D.1. Ablation on LoRA Application
Although LoRA is most commonly applied to the query and value projections, which we denote as the qv setting, we also
evaluate an alternative configuration with the same parameter budget by applying LoRA to the query, key, value, and output
projections with rank r = 4, which we denote as qkvo. Following Section 4.3, we measure HotpotQA accuracy along with
system throughput and TTFT under the same emulated trace, where the results are presented in Table 13, 14, and 15.
We find that the non-shared baseline in qkvo achieves lower accuracy than in qv, and this degradation carries over to all
cache sharing methods. Nevertheless, our methods still achieve the best accuracy among the cache sharing approaches,
indicating that decoupling the base cache and the LR cache remains effective when LoRA is applied to the key projection.
In terms of system throughput, the qkvo setting is inherently less favorable because it introduces additional LoRA
computation paths on multiple projections. Moreover, in our schemes, adapter contribution reconstruction from key LR
cache must be performed in the head dimension before applying rotary positional embeddings (RoPE), which limits the same
associativity-based reordering we exploit for the value cache. Concretely, letting the post-RoPE query be Q and the pre-RoPE
key be K′ = K′ + K′ B with K = RoPE(K′), the attention score is QK⊤ = Q (cid:0) RoPE(K′) (cid:1)⊤ = Q (cid:16) RoPE(K′ ) +
base lr base
(cid:17)⊤
RoPE(K′ B) , so the low-rank reordering from Q(B⊤K′⊤) to (QB⊤)K′⊤ is not directly applicable because RoPE(·)
lr lr lr
applies a position-dependent rotation on the head dimension. As a result, both BaseShared and BaseLRShared under
qkvo achieve lower throughput than their qv counterparts reported in Table 4. Still, BaseLRShared remains more
efficient than DroidSpeak. On the other hand, because the adapter output reconstruction primarily affects the generation stage
rather than prefill, TTFT under qkvo increases marginally overall compared to Table 5. Similarly with the previous results,
BaseLRShared remains close to FullShared in TTFT, while BaseShared remains comparable to DroidSpeak.
Overall, our approach maintains the strongest accuracy among cache sharing baselines, and BaseLRShared retains a
clear efficiency advantage, demonstrating the generality and scalability of our design across LoRA configurations, while qv
setting used in this paper is favorable across the as mentioned in Section 4.1.
Table 13. LLaMA-3.1-8B-Instruct average HotpotQA benchmark accuracy (%) under the qkvo scheme.
Method Non-Shared FullShared DroidSpeak BaseShared BaseLRShared
Accuracy (%) 38.43 34.88 36.28 38.12 37.57
Table 14. LLaMA-3.1-8B-Instruct system throughput (tokens per second) under each total sequence length of the traces in qkvo setting.
Method 1.9k 3.0k 5.0k 9.1k 17.3k 33.7k 66.4k
Non-Shared 123.1 184.4 297.1 467.1 525.0 556.0 OOM
FullShared 155.8 215.1 357.2 626.3 1080.6 1544.9 1699.4
DroidSpeak 145.9 211.8 326.2 519.6 739.1 887.2 792.9
BaseShared 127.2 195.6 325.7 484.9 679.3 755.6 673.2
BaseLRShared 150.3 219.7 361.3 560.3 806.7 998.8 1051.9
Table 15. LLaMA-3.1-8B-Instruct TTFT (second) under each total sequence length of the traces in qkvo setting.
Method 1.9k 3.0k 5.0k 9.1k 17.3k 33.7k 66.4k
Non-Shared 4.79 5.00 4.94 10.52 20.73 50.04 OOM
FullShared 1.23 1.40 1.81 2.70 4.82 9.57 24.05
DroidSpeak 1.77 2.29 3.37 5.84 11.54 25.43 67.80
BaseShared 1.78 2.34 3.29 5.59 10.99 26.20 70.57
BaseLRShared 1.27 1.46 1.92 2.89 4.93 10.30 25.30
21

## Page 22

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
D.2. Latency on HotpotQA Benchmark
We report the end-to-end system latency on the HotpotQA benchmark. In real-world scenarios, additional latency other
than model inference arises from function calls such as web search and Wikipedia retrieval. We therefore split latency into
model latency, which includes only the inference (prefill and generation), and end-to-end (E2E) latency, which additionally
includes function call latency and the latency of data processing the retrieved context. We also report time-to-first-token
(TTFT), defined as the sum of model prefill latencies across agent steps, consistent with Table 5 in Section 4.3.
As shown in Table 16 and Table 17, methods with lower accuracy, such as FullShared and DroidSpeak, tend to produce
longer sequences and incur higher latency, sometimes even exceeding the Non-Shared baseline. This occurs despite
their strong efficiency which they have demonstrated in trace-based emulations. These results highlight that overall latency
depends not only on the cache sharing efficiency, but also on accuracy. When cache sharing degrades generation quality,
the agent is more likely to take additional steps to re-reason and retrieve more external context, which increases sequence
length and, in turn, increases E2E latency. Overall, FullShared achieves a low TTFT but incurs substantial E2E latency
overhead compared to Non-Shared on LLaMA-3.1-8B-Instruct. DroidSpeak and BaseShared exhibit end-to-end
latency similar to Non-Shared. BaseLRShared achieves the best efficiency while preserving strong accuracy, making
it empirically optimal for agentic systems.
Table 16. End-to-end (E2E) latency and its breakdown. The lowest latency is highlighted in bold.
Model Latency Level Non-Shared FullShared DroidSpeak BaseShared BaseLRShared
Hard 5.90 7.39 5.75 5.97 5.70
Medium 5.60 6.70 5.30 5.35 5.13
Model Latency (s)
Easy 5.04 6.22 4.69 4.76 4.54
Avg. 5.51 6.77 5.24 5.36 5.12
Hard 13.63 19.73 13.75 13.73 13.59
LLaMA-3.1-8B-Instruct
Medium 12.10 18.48 11.85 12.05 11.73
E2E Latency (s)
Easy 11.10 14.87 10.64 10.89 10.54
Avg. 12.28 17.69 12.08 12.23 11.96
Hard 1.02 0.81 1.00 1.07 0.77
Medium 1.01 0.77 0.98 1.02 0.66
TTFT (s)
Easy 1.05 0.72 0.97 1.03 0.88
Avg. 1.03 0.77 0.98 1.04 0.77
Hard 6.64 7.23 6.82 6.79 6.39
Medium 6.36 6.43 6.23 6.39 6.00
Model Latency (s)
Easy 6.86 6.05 6.11 5.86 5.77
Avg. 6.62 6.57 6.38 6.35 6.05
Hard 14.65 14.36 14.98 15.06 13.91
Ministral-8B-Instruct
Medium 12.66 14.30 12.41 12.25 11.45
E2E Latency (s)
Easy 15.22 12.85 12.98 12.92 12.79
Avg. 14.18 13.83 13.46 13.41 12.72
Hard 1.26 1.30 1.44 1.33 1.26
Medium 1.17 1.07 1.26 1.17 1.12
TTFT (s)
Easy 1.22 1.12 1.24 1.20 1.08
Avg. 1.22 1.16 1.31 1.23 1.15
Table 17. Average of total sequence length (tokens) accumulated during multi-agent execution.
Model Level Non-Shared FullShared DroidSpeak BaseShared BaseLRShared
Hard 1099 1584 1223 1039 1302
Medium 1092 1475 1108 996 1229
LLaMA-3.1-8B-Instruct
Easy 1088 1483 1134 1077 1154
Avg. 1093 1514 1155 1038 1228
Hard 1120 1460 1355 1202 1468
Medium 1019 1398 1347 1144 1406
Ministral-8B-Instruct
Easy 1154 1393 1414 1142 1363
Avg. 1098 1417 1372 1162 1412
22

## Page 23

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
D.3. Out-of-Function Ratio
We define cases where the agent system fails to produce an answer before reaching the maximum number of iterations (e.g.,
45) as out-of-function (OOF). In the benchmark accuracy evaluation, these cases are counted as incorrect. However, from a
user-experience perspective, returning no answer can be qualitatively different from returning an incorrect answer, and may
be considered a more severe failure. We therefore report OOF incidents in addition to benchmark accuracy.
As shown in Table 18, which reports the OOF ratio and its difference from the Non-Shared baseline, methods with
lower accuracy generally exhibit higher OOF ratios. Consistent with the accuracy results where BaseShared and
BaseLRShared achieve the best accuracy among cache sharing methods, our schemes also yield lower OOF ratios in
most cases, except for Ministral-8B-Instruct on ScienceQA.
Table 18. Out-of-function (OOF) rate (%) for each benchmark and difficulty level. The underlying value in the Avg. column denotes the
difference from the corresponding Non-Shared baseline. Lower is better.
HotpotQA ScienceQA
Model Method Easy Medium Hard Avg. 1-4 5-8 9-12 Avg.
Non-Shared 1.50 1.80 1.65 1.65 0.00 0.00 0.13 0.21 0.11 0.00
FullShared 2.05 2.05 3.25 2.45 +0.80 0.29 2.46 0.54 1.10 +0.99
LLaMA-3.1-8B-Instruct DroidSpeak 2.10 3.10 5.15 3.45 +1.80 0.58 1.29 1.71 1.19 +1.08
BaseShared 1.35 1.50 2.65 1.83 +0.18 0.21 1.83 0.13 0.72 +0.61
BaseLRShared 1.25 1.80 2.25 1.77 +0.12 0.29 2.50 0.25 1.01 +0.90
Non-Shared 3.90 5.15 5.80 4.95 0.00 0.38 0.17 0.83 0.46 0.00
FullShared 7.15 7.65 10.95 8.58 +3.63 4.17 2.96 4.92 4.01 +3.56
Ministral-8B-Instruct DroidSpeak 7.05 9.50 8.20 8.25 +3.30 1.79 2.17 3.33 2.43 +1.97
BaseShared 6.45 6.35 9.50 7.43 +2.48 2.75 1.92 3.25 2.64 +2.18
BaseLRShared 4.45 6.55 7.60 6.20 +1.25 1.83 1.67 3.38 2.29 +1.83
D.4. Rank Ablations
Table 19 reports the accuracy of our method, particularly BaseShared, on the QA benchmarks across ranks from 1 to 32.
There is a noticeable accuracy gain from rank 1 to 8 because agentic operation, including planning for the given question
and tool selection, requires precise adaptation to the specific trajectory dataset. However, since the agent-trajectory training
data are relatively small and easy to adapt, we observe only marginal accuracy differences for ranks above 8. Therefore, to
minimize both training and inference overhead, we use rank r = 8 in all experiments. Experiments on ScienceQA shows a
similar trend, indicating the choice of rank 8 is task-independent.
Table 19. Rank ablation on benchmark accuracy (%) in BaseShared.
Benchmark 1 2 4 8 16 32
HotpotQA 31.35 35.98 37.88 38.60 38.43 38.50
ScienceQA (9-12) 71.05 73.98 75.80 76.58 76.54 76.71
23

## Page 24

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
D.5. Accuracy Score Deviation
We report the standard deviation of the average accuracy in Table 3 of Section 4.2 for each baseline and our methods
in Table 20. We note that all experiments use a single random seed (42), but accuracy can still vary due to subtle non-
deterministic characteristics in external tool usage. For each benchmark level, we run 20 iterations. The accuracy gaps
between methods are larger than the observed deviations and therefore we see that the comparisons remain reliable.
Table 20. Standard deviation of average benchmark accuracy (%) with 20 iterations.
Dataset Non-Shared FullShared DroidSpeak BaseShared BaseLRShared
HotpotQA 0.16 0.32 0.21 0.19 0.24
ScienceQA 0.20 0.45 0.25 0.26 0.31
D.6. Ablation on the Context Overlap Ratio
We provide analysis on the system throughput when the context overlap ratio varies across agents. Since context overlap is
the key premise that enables KV cache sharing, lower overlap reduces the amount of reusable cache and gradually makes all
cache sharing methods behave more like the non-shared setting. Table 21 reports throughput under different overlap ratios
while using the emulation trajectory length of 33.7k. An overlap ratio of 100% corresponds to the fully shared setting used
in our main experiments, whereas 0% represents the case where no cross-agent cache can be reused.
As expected, the throughput advantage of KV cache sharing decreases as the overlap ratio becomes smaller and converges
toward the non-shared baseline when the overlap ratio approaches 0%. Nevertheless, across all overlap settings, our methods
consistently achieve higher throughput than conventional cache sharing baselines such as DroidSpeak. Among them,
BaseLRShared performs best overall, demonstrating the effectiveness of our approach even when the amount of reusable
context is reduced.
Table 21. Throughput (tokens/s) under varying context overlap ratios in LLaMA-3.1-8B-Instruct with trajectory length of 33.7k.
Overlap (%) Non-Shared FullShared DroidSpeak BaseShared BaseLRShared
100 683.2 1697.6 931.0 969.6 1678.1
80 683.2 1385.1 859.0 879.9 1375.6
60 683.2 1121.7 789.3 805.2 1108.2
40 683.2 930.3 742.4 752.7 925.0
20 683.2 784.4 703.8 706.3 764.9
0 683.2 682.2 677.9 677.1 681.6
24

## Page 25

LRAgent: Efficient KV Cache Sharing for Multi-LoRA LLM Agents
D.7. Memory Usage
We report the memory usage of each method across traces with diverse trajectory lengths on Ministral-8B-Instruct. We note
that the pretrained model weights consume 14.95 GB of memory, and the three LoRA weights add 0.11 GB of memory.
Beyond these components, KV cache memory becomes severe in long-context scenarios where retrieved contexts accumulate.
Since KV cache sharing methods typically maintain a single shared KV cache for three agents and recompute and overwrite
it when needed, their memory usage is similar within 1 GB difference overall.
In particular, FullShared has the lowest memory usage because it directly reuses the KV cache without additional
components. DroidSpeak additionally maintains a hidden state cache. Since the first layer typically does not require
recomputation, its hidden states can be transferred directly from the previous model to the current model, eliminating
computation for these layers. However, this cache becomes an overhead in modern group-query attention (GQA) models.
The hidden state dimension is often about four times larger than the key or value projection dimension, so the hidden state
cache can be roughly twice as large as the KV cache of a single layer. We note that the OOM observed in Section 4.3 mainly
arises from memory fragmentation, despite the gap between the GPU’s peak capacity and the actual allocated usage. For
BaseShared and BaseLRShared, there exists an additional LR cache, which is three times larger in BaseShared
than in BaseLRShared, but it remains negligible due to its small dimension relative to the base cache. As a result, our
schemes achieve memory usage close to FullShared as well as other cache sharing methods.
Table 22. Memory usage (GB) for each total sequence length trace.
Total Seq. Len. Non-Shared FullShared DroidSpeak BaseShared BaseLRShared
1.9k 15.72 15.25 15.26 15.26 15.25
3.0k 16.10 15.38 15.40 15.40 15.39
5.0k 16.87 15.65 15.68 15.67 15.65
9.1k 18.40 16.18 16.25 16.23 16.19
17.3k 21.46 17.24 17.37 17.34 17.27
33.7k 27.59 19.36 19.62 19.56 19.43
66.4k 39.84 23.61 24.12 23.99 23.74
132.0k 64.34 32.11 33.12 32.87 32.37
25
