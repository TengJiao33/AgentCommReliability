# dense-latent-communication-heterogeneous-agents-2606.13594

- Source PDF: `dense-latent-communication-heterogeneous-agents-2606.13594.pdf`
- Extracted at UTC: `2026-07-09T05:56:31.934250+00:00`
- Pages: 25
- Title: See What I See, Know What I Think: Dense Latent Communication Across Heterogeneous Agents
- SHA256: `2a16cbd2718637baefaa249ffb4d03cadbb2a6aa0ff191ba9eb99b1bdcc516df`

## Page 1

See What I See, Know What I Think: Dense Latent
Communication Across Heterogeneous Agents
Siyi Chen1,2, Xiaoyan Zhang1, Meng Wu1, Jonathan Tremblay2, Valts Blukis2, Stan Birchfield2,
Rene Vidal3, Alvaro Velasquez4, Sijia Liu5, Qing Qu1
1University of Michigan · 2NVIDIA · 3University of Pennsylvania · 4University of Colorado
Boulder · 5Michigan State University
Abstract
Multi-agent systems communicate mostly through text, paying a lossy and expensive decode and
re-encode cost. KV-cache communication is a promising alternative, yet most prior work is homogeneous,
using duplicate copies of the same model, and avoids the central challenge of cross-model latent
alignment; existing heterogeneous methods are also restrictive, typically assuming shared input and
using transferred caches mainly for steering. We study a more fundamental question: can heterogeneous
agents be aligned well enough to perform real “mind reading” and transfer both what one agent sees
and how it thinks? Our information-structure analysis reveals a duality: context-aware transfer is
driven by sparse reasoning signals, while context-unaware transfer, where the receiver sees no input,
requires dense contextual knowledge preservation. Motivated by this, we propose dense alignment
for heterogeneous KV-cache communication via a lightweight cross-model cache transformation and
two-phase training: reconstruction followed by generation. Across all six directions of {Qwen3-4B, 8B,
14B} and six in-domain and out-of-domain benchmarks, our method outperforms prior heterogeneous
baselines, matches or exceeds text communication in context-aware settings at roughly 2 to 3× lower
compute, and remains effective in context-unaware transfer where prior methods collapse.
Keywords: Multi-agent, Latent Communication, Heterogeneous, Alignment
Date: June 12, 2026
Correspondence: siyich@umich.edu
Resources: Project page
TFLOPs per Example ↓
↑
)%(
ycaruccA
Context-Aware Context-Unaware Accuracy-Computation Trade-off
Settings
Context-Aware
Context-Unaware
Methods
Text-to-Text
Cache-to-Cache
Ours
Figure 1: See what I see, know what I think. We study real latent mind reading across heteroge-
neous agents, in which one agent can read both what another agent sees and what it thinks. Guided
by our latent communication information structure analysis, we learn dense alignment between
agents and evaluate context-aware and context-unaware settings. Dense alignment is accurate
and efficient in both regimes, surpassing sparse-steering heterogeneous baselines (cache-to-cache)
while using less compute than text communication.
1
6202
nuJ
11
]AM.sc[
1v49531.6062:viXra

## Page 2

Contents
1 Introduction 3
2 Background and Problem Setup 5
2.1 Latent MAS Communication via KV-Cache . . . . . . . . . . . . . . . . . . . . . . . . 5
2.2 Latent Communication: Homogeneous vs. Heterogeneous Multi-Agent Systems . . 6
2.3 Context-Aware vs. Context-Unaware Latent Communication . . . . . . . . . . . . . . 6
3 The Information Bottleneck: Sparse Reasoning vs. Dense Knowledge 7
3.1 Compressed-Sensing Analysis of Information Bottlenecks . . . . . . . . . . . . . . . . 7
3.2 Sparse Reasoning and Dense Knowledge in KV-Cache Communication . . . . . . . . 8
4 Design of Dense Latent Communication 10
4.1 Two-Phase Training for Dense and Actionable Alignment . . . . . . . . . . . . . . . . 10
4.2 Architecture Design: Heterogeneous Dense Cache Alignment . . . . . . . . . . . . . 11
5 Experiments 13
5.1 Context-aware Results . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
5.2 Context-unaware Results . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
5.3 Latent Space Visualization . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
6 Conclusion 15
A Phase-II Trace Construction 19
B Efficiency Analysis and Per-Side Breakdown 19
B.1 Measurement recipe . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
B.2 Per-side breakdown . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
B.3 Structural observations . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
B.4 Notes . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
C Compressed-Sensing Analysis Across Regimes 23
C.1 Self-communication setup . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
C.2 Stage 1: CS head ranking . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
C.3 Stage 2: 𝐾-sweep on full test . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
C.4 Random-filter baseline . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
C.5 Recovery-limit caveat . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
C.6 Context-Aware and Context-Unaware Results . . . . . . . . . . . . . . . . . . . . . . . 24
C.6.1 Context-aware regime . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
C.6.2 Context-unaware regime . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
C.6.3 Takeaway for model design . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
2

## Page 3

1 Introduction
LLM-based multi-agent systems (MAS) increasingly rely on specialized agents, such as planners,
retrievers, executors, and verifiers, to solve problems beyond the reach of a single model [Tra+25].
Frameworks like AutoGen [Wu+24] and MetaGPT [Hon+24] operationalize this promise through
role assignment and workflow-based collaboration. Yet even as recent work improves coordination
[Che+25; Wan+25; Zha+25a; Wan+26; Zha+25b; Zha+26], modern MAS still communicates
predominantly through text. This text bottleneck is flexible and interpretable, but it forces a decode
and re-encode cycle at every handoff, introducing information loss, substantial generation overhead,
and limited access to rich latent intermediate representations [Zhe+26; Du+25; Zou+25].
This bottleneck motivates as a more efficient and interpretable alternative
latent communication
to text-based message passing [Yu+26]. Instead of exchanging decoded natural language, agents
directly share internal representations. By transmitting embedding-level signals [Pha+24], hidden
state trajectories [Du+25; RL25; Tan+25; Fei+25; Yan+26], or key-value (KV) caches [Shi+25;
Fu+25; Jin+26; LAD26; Liu+24], latent methods reduce decoding overhead, enable computation
reuse, and expose richer context for collaboration [Shi+25; LAD26; Zou+25; Zhe+26]. Among
these representations, KV cache communication has emerged as a particularly compelling approach.
By directly transmitting the Key (𝐾) and Value (𝑉) tensors from transformer attention layers, this
method serves as an instant, pre-computed memory injection for the receiving agent. Rather than
parsing a lossy text summary, the receiver seamlessly integrates the sender’s dense, sequence-
level contextual state. KV caches are especially well-suited for latent communication because they
directly participate in attention during decoding and support selective transmission, compression,
projection, and fusion, preserving task-relevant context while minimizing communication costs
[Shi+25; Fu+25; LAD26].
Existing work, however, leaves two fundamental challenges underexplored. First, latent com-
munication is largely restricted to homogeneous agents, i.e., replicas of the same model whose
latent representations are naturally aligned. In contrast to natural language, which provides a
shared symbolic interface, transferring KV caches across agents is non-trivial due to
heterogeneous
differences in layer depth, head structure, channel geometry, and positional encoding [Liu+24;
Fu+25; RL25]. Recent efforts address heterogeneous communication via signal fusion [Fu+25]
when agents observe the same input. In contrast, we directly learn KV-cache alignment and impose
no such constraint. Second, these existing works typically evaluate the channel under a
context-aware
regime, where the receiver retains access to the original question context [Fei+25; Pha+24; Zhe+26].
In this setting, the transmitted latent message merely steers reasoning over information the receiver
already possesses, allowing the signal to be partial or lossy. It remains unclear whether the latent
channel can carry the input densely enough across heterogeneous architectures. This leads to
itself
our fundamental question:
Can heterogeneous agents be aligned well enough for real latent “mind reading,” to transfer
both what one agent sees and how it thinks?
In contrast to existing works, our method supports direct information transfer in context-unaware
settings, where the receiver solves the task solely from the sender’s transmitted latents. This
demonstrates the potential of dense alignment between heterogeneous agents for knowledge transfer,
allowing the receiver to reuse the sender’s latent representations instead of re-encoding the original
context, thereby improving computational efficiency.
3

## Page 4

Reasoning Only Relatively Efficient
Communication Sparse Alignment
Low Bandwidth
Sparse reasoning Low Info Density Missing Context
signals partially are
Partial Reasoning
transmitted
Sender Agent Heterogeneous KV Cache Alinement Receiver Agent
Full-information High Efficiency
Dense Alignment
Communication
High Bandwidth
High Info Density
Both sparse reasoning Rich Context
and dense context are
Robust Reasoning
transmitted
Figure 2: Sparse vs. dense heterogeneous alignment. Prior sparse methods partially align reasoning
(mainly in context-aware transfer) and do not preserve dense context. Our dense alignment maps
sender caches into receiver-compatible caches to support both robust reasoning and dense context
transfer across context-aware and context-unaware regimes.
Contribution of this work. We revisit the information requirement of latent communication
through compressed-sensing analysis over KV caches (Section 3) in two regimes,
context-aware
(receiver sees the input) and (receiver sees no input), and find a clear duality:
context-unaware
context-aware transfer is sparse in reasoning signal, while context-unaware transfer requires dense
contextual knowledge preservation. Motivated by this, we propose dense alignment for heteroge-
neous latent communication with a lightweight cross-model KV-cache adapter, positional disentan-
glement, fine-grained per-head transformation and selection, and two-stage training (reconstruction
then generation). In context-aware settings, our dense alignment surpasses existing sparse-steering
heterogeneous baselines while running at 2–3× lower compute than text communication, and it
remains effective in the harder context-unaware setting where existing baselines fail. Our core
contributions are summarized as follows:
• Compressed-sensing analysis and context-unaware communication: We provide compressed-
sensing analysis and a stricter protocol, showing that latent communication is
context-unaware
sparse in reasoning signal but dense in knowledge transfer.
• Dense alignment across heterogeneous models: We introduce a dense alignment framework that
enables direct KV-cache transfer across heterogeneous models while preserving both reasoning
and contextual information.
• Efficient and information-preserving transfer: In context-aware communication, dense align-
ment surpasses existing sparse-steering heterogeneous baselines while also being more compute-
efficient than text communication; it further enables robust transfer in the challenging context-
unaware regime.
Organization. The remainder of this paper is organized as follows. Section 2 introduces back-
ground on latent MAS communication, including KV-cache representations and the distinction
between homogeneous and heterogeneous agents. Section 3 presents the compressed-sensing anal-
ysis, which reveals the sparse-versus-dense nature of information transfer across context-aware and
context-unaware regimes. Section 4 describes the dense alignment framework for heterogeneous
4

## Page 5

latent communication composed of the cross-model KV-cache adapter, positional disentanglement,
per-head transformations with gating, and the two-stage reconstruction-then-generation training
strategy. Section 5 evaluates our method across in-domain and out-of-domain benchmarks under
both communication regimes. Finally, Section 6 concludes the paper and discusses future directions.
2 Background and Problem Setup
In this section, we introduce the basic setups of latent MAS communication and distinct communi-
cation regimes.
2.1 Latent MAS Communication via KV-Cache
Large Language Models (LLMs) are increasingly deployed in multi-agent systems (MAS), where
multiple specialized agents collaborate to solve complex tasks that exceed the capabilities of a
single model [Tra+25]. Formally, let ℳ = {𝒜 1 , 𝒜 2 , . . . , 𝒜 𝑛 } denote a MAS consisting of 𝑛 distinct
agents, where 𝒜 represents the 𝑘-th specialized agent. Such systems typically comprise role-
𝑘
specific entities, such as planners, retrievers, executors, and verifiers, that dynamically exchange
information and coordinate actions. For simplicity, let us consider a representative two-agent
setting to study fundamental communication challenges. Existing MAS typically rely on text-based
communication [Wu+24; Che+25; Wan+25; Zha+25a; Wan+26]: the sender decodes its internal
states into discrete text tokens, which are then transmitted and re-encoded by the receiver. While
natural and model-agnostic, this protocol incurs substantial overhead from autoregressive decoding
and redundant receiver-side computation.
As illustrated in Figure 3, latent MAS communication instead transmits intermediate latent
states, such as KV caches [Zou+25; Fu+25], bypassing explicit text generation and reducing
communication overhead. Given an input sequence 𝑿 = (𝒙1 , . . . , 𝒙𝑁 ) of 𝑁 tokens, a transformer
processes the sequence through 𝐿 layers. At each layer 𝑙, token representations are projected into
query, key, and value states. Specifically, for each attention head ℎ ∈ 1, . . . , 𝐻, the input sequence is
mapped to its corresponding head matrices:
𝑸
(𝑙,ℎ)
= 𝑿
(𝑙−1)
𝑾
(𝑙,ℎ),
𝑲
(𝑙,ℎ)
= 𝑿
(𝑙−1)
𝑾
(𝑙,ℎ),
𝑽
(𝑙,ℎ)
= 𝑿
(𝑙−1)
𝑾
(𝑙,ℎ),
𝑄 𝐾 𝑉
where 𝑿 (𝑙−1) ∈ R𝑁×𝑑 model represents the hidden states from the previous (𝑙 − 1)-th layer, and
𝑾𝑄 , 𝑾𝐾 , 𝑾𝑉 ∈ R𝑑 model ×𝑑 head are the head specific projection weights. The scaled dot product at-
tention mechanism then computes a weighted context matrix by evaluating token dependencies
across a softmax-normalized similarity matrix:
(cid:18)
𝑸
(𝑙,ℎ)(𝑲 (𝑙,ℎ))⊤ (cid:19)
Attention(𝑸 (𝑙,ℎ), 𝑲 (𝑙,ℎ), 𝑽 (𝑙,ℎ)) = softmax √ 𝑽 (𝑙,ℎ).
𝑑
head
In autoregressive generation, computing the attention matrix requires context from all preceding
tokens. To avoid the prohibitive 𝑂(𝑁2) recomputation of past key and value vectors at each decoding
step, these matrices are preserved within a key-value (KV) cache. During the prefill stage, the
sender and receiver construct their respective KV caches by storing the key and value tensors
produced at every transformer layer and attention head:
𝒞 𝑆 (𝑿 ) = {(𝑲 𝑆 (𝑙,ℎ)(𝑿 ), 𝑽 𝑆 (𝑙,ℎ)(𝑿 ))} 𝑙,ℎ , 𝒞 𝑅 (𝑿 ) = {(𝑲 𝑅 (𝑙,ℎ)(𝑿 ), 𝑽 𝑅 (𝑙,ℎ)(𝑿 ))} 𝑙,ℎ , (1)
These caches serve as compact summaries of the previously processed context and eliminate the
need to recompute historical attention states during autoregressive decoding.
5

## Page 6

KV caches provide a natural in-
Text
terface for latent communication. As
Communication
Sender !" Text Tokens Receiver !#
shown in Figure 3, the sender 𝒜 Decoding Re-encoding
𝑆
can directly transmit its precomputed Latent $%(') Cache $) *(')
KV cache tensors 𝒞
𝑆
(𝑿 ) to the re- Communication
Sender !" KV Cache
Transformation
Receiver !#
! No Token Decoding ! No Re-encoding
ceiver 𝒜 . Rather than exchanging
𝑅
information through decoded text,
Figure 3: Text communication decodes and re-encodes mes-
the receiver can directly consume
sages between agents, whereas latent communication trans-
the sender’s internal representations,
fers KV caches directly for computation reuse.
forming the basis for latent commu-
nication between language models. The key challenge is latent space alignment, where different
instances of the same model naturally share an aligned latent space, but this is not the case for
heterogeneous models.
2.2 Latent Communication: Homogeneous vs. Heterogeneous Multi-Agent Systems
As shown in recent works [Du+25; Tan+25; Shi+25; Jin+26; Zou+25], the latent communication
framework described in Section 2.1 is natively supported in homogeneous MAS, where all agents
in ℳ share identical model architectures, layer configurations, and hidden dimensions. Given
this architectural symmetry, the key and value tensors generated by the sender 𝒜 are mapped
𝑆
directly to the attention blocks of the receiver 𝒜 . This dimensional alignment enables zero-shot
𝑅
state sharing via direct tensor copy operations, completely bypassing the need for cross-model
projection, feature alignment, or latent space transformations.
However, this direct transfer paradigm fails when applied to heterogeneous MAS, where
individual agents in ℳ differ significantly in their internal architectures, capabilities, information
access, or foundational designs. Unlike natural language, which acts as a universal symbolic
interface, latent representations and key-value (KV) caches are strictly tied to a model’s internal
coordinate space and optimization landscape. Consequently, these representations are severely
misaligned across heterogeneous architectures, rendering direct injection functionally incoherent
without explicit alignment [RL25; Fu+25].
Existing efforts have begun to address latent-space mismatch across heterogeneous agents, but
important limitations remain. One line of work learns projection modules in the relatively simple
text-embedding space [Du+25; Yan+26], rather than aligning the denser and more expressive
KV-cache representations. Another line uses cache-fusion networks [Fu+25], but assumes that
agents process the same input, limiting their flexibility in general communication settings. Finally,
several methods rely on aggressive latent compression or sparsification [Fu+25; Shi+25] to simplify
alignment. While sparse latents can be sufficient for transmitting high-level reasoning signals in
context-aware settings, they may discard the dense contextual information that KV caches are natu-
rally suited to carry. Moreover, such sparsification can introduce inefficient communication patterns,
where fixed-size latent channels carry little useful information after many components are pruned
or suppressed. In contrast, we propose a lightweight and efficient dense-alignment framework
that enables heterogeneous agents to exchange KV-cache representations while preserving both
reasoning-relevant and context-rich information.
2.3 Context-Aware vs. Context-Unaware Latent Communication
To characterize the information dynamics within latent multi-agent channels, we formalize two
distinct communication regimes based on the informational availability at the receiver side. Crucially,
6

## Page 7

while prior literature on latent communication has almost exclusively operated within the
context-
paradigm, this work highlights and investigates the significant yet under-explored
aware context-
setting.
unaware
• Context-Aware Communication: The receiver agent 𝒜 𝑅 has access to the original input context 𝑿
and uses it together with the transferred, aligned cache 𝒞 (cid:101)𝑅 (𝑿 ) for generation: 𝑃(𝒚 | 𝑿 , 𝒞 (cid:101) _𝑅(𝑿 )).
• Context-Unaware Communication: The receiver agent 𝒜 𝑅 has no access to the source context 𝑿
and must generate solely from the transferred latent representations: 𝑃(𝒚 | 𝒞
(cid:101)𝑅
(𝑿 )).
The distinction between these two regimes changes the role of the latent channel. In context-
aware communication, the cache serves primarily as a : the receiver can still consult
reasoning signal
and re-process the original context 𝑿 . In context-unaware communication, the cache must instead
serve as a : it is the receiver’s only access to source-side information.
self-contained information carrier
It must therefore transmit both contextual evidence and reasoning state, enabling the receiver to
see
and . This makes context-unaware communication both
what the sender sees know what the sender thinks
scientifically and practically important. Scientifically, it tests whether dense latent alignment can
preserve task-critical knowledge across heterogeneous models. Practically, it reduces redundant
context re-encoding, enables efficient model switching via transferred KV states, and supports
deployments where source inputs cannot be shared. Overall, context-unaware communication
exposes a stronger requirement for latent MAS: the transferred cache must faithfully carry the dense
information on its own.
3 The Information Bottleneck: Sparse Reasoning vs. Dense Knowledge
To understand the intrinsic information structure of latent communication signals, we conduct a sys-
tematic post-hoc compressed-sensing analysis of KV caches in a homogeneous self-communication
setting. By using architecturally identical sender and receiver models, we eliminate cross-model
misalignment as a confounding factor and isolate the information carried by the transmitted la-
tent representations. This analysis identifies the minimal subset of KV components needed for
accurate reasoning communication in context-aware settings, while also informing lightweight,
information-preserving alignment designs for heterogeneous agents.
We evaluate two communication regimes. In the regime, the receiver has access to
context-aware
the original input, allowing effective performance with only a small, sparse subset of the KV cache.
In the more challenging regime, the receiver has no access to the input and must
context-unaware
rely entirely on the transmitted latent cache, requiring a much denser fraction of the KV cache to
preserve task-critical information. Together, these findings reveal a fundamental duality: latent
communication is sparse in reasoning but dense in knowledge, motivating the heterogeneous dense
alignment framework we developed in Section 4.
3.1 Compressed-Sensing Analysis of Information Bottlenecks
To quantify the contribution of individual components in the sender’s KV cache and identify the
minimal information required for effective latent communication, we employ a post-hoc compressed-
sensing (CS) framework. We consider a homogeneous self-communication setup, 𝒜 → 𝒜 , where
𝑆 𝑅
both the sender 𝒜 and receiver 𝒜 use the same Qwen3-4B model. The sender transformer contains
𝑆 𝑅
𝐻 attention heads across 𝐿 layers. Due to Grouped-Query Attention (GQA), each layer contains 𝐺
Key-Value (KV) groups, with each KV group shared by 𝐶 query heads.
7

## Page 8

1. Head Groups in Sender
𝐺 attention head groups
in each layer
Layer 1 1 2 … G
Layer ℓ 1 2 … G
Layer 𝐿
…
…
…
2. Compressed Measurements
Randomly mask out some heads
and then evaluate task
performance (avg. Acc)
Performance Mask 1 𝚽!,: … 𝑦!
Mask 2 𝚽$,: … 𝑦"
Mask M 𝚽%,: … 𝑦#
Ablate(zero out) Keep
… 1 2 G
Model: 𝒚, = 𝒚 − 𝑦 ! = 𝚽𝜶 + 𝝐
Total Heads: 𝐻 = 𝐿×𝐺×𝐶 𝚽 ∈ 0,1 !×#: Measurement Matrix
… …
3. Sparse Recovery (LASSO)
Solve head importance
scores 𝜶 with Lasso
1 𝜶( = 𝑎𝑟𝑔𝑚𝑖𝑛 2 𝒚2 − 𝚽𝜶 $ $ + 𝜆 𝜶 %
𝜶 ∈ ℝ#: Head Importance
𝛼# erocs
ecnatropmI
&
4. Select Top-K Head Groups
Choose the top-K head
groups with the highest
importance scores
Top-K head groups indices
{𝑖 ", 𝑖 #, 𝑖 $… 𝑖 %}
… Layer 1
Layer ℓ
Layer 𝐿
Head index (sorted by 𝛼#&)
Then aggregate the importance score
per head group
…
…
… …
…
…
𝐶 heads per group
Irrelevant Heads
Selected(remain) Not Selected
𝑦& ∈ ℝ: Baseline Performance
𝐾 < 𝐿×𝐺
Figure 4: Compressed-sensing head selection: random ablation masks estimate sender-head impor-
tance, which is aggregated to KV-group scores and used to keep top-𝐾 groups for communication.
We first sample 𝑁 data points from a benchmark and evaluate the full-cache latent commu-
nication performance, denoted by 𝑦 , measured as mean accuracy over these examples. We then
0
generate 𝑀 random binary retention masks, represented by a matrix 𝚽 ∈ {0, 1}𝑀×𝐻, where each
row corresponds to one ablation experiment. The entry Φ𝑖𝑗 = 1 indicates that the 𝑗-th sender head is
retained in the 𝑖-th experiment, while Φ𝑖𝑗 = 0 indicates that it is ablated. For each mask, we evaluate
the downstream task on the same 𝑁 examples and record the resulting performance, producing
an observation vector 𝒚 ∈ R𝑀. We center these observations by subtracting the full-cache baseline:
𝒚˜ = 𝒚 − 𝑦 0 . We assume that each head contributes independently to the final communication quality
and denote these unknown contributions by the coefficient vector 𝜶 ∈ R𝐻. Recovering 𝜶 from the
observed performances can then be formulated as the following Lasso regression problem:
1
𝜶ˆ = arg m 𝜶 in 2𝑀 ∥𝒚˜ − 𝚽𝜶∥2 2 + 𝜆∥𝜶∥ 1 , (2)
where larger-magnitude positive coefficients indicate higher task relevance. Finally, we aggregate
the per-head coefficients within each KV group to obtain the score for the 𝑔-th KV group in layer 𝑙:
(𝑙,𝑔) (cid:213)
score KV = 𝛼ˆ 𝑙,ℎ . (3)
ℎ∈group(𝑔)
This procedure isolates the importance of KV components in a setting free from cross-model
misalignment, providing a clear measurement of the information bottleneck. We then use the
resulting CS-derived scores to perform KV-group pruning sweeps under both context-aware and
context-unaware regimes. For comparison, we also evaluate random pruning, showing that the
CS-derived ranking more effectively identifies the KV components most critical for task performance.
3.2 Sparse Reasoning and Dense Knowledge in KV-Cache Communication
Our post-hoc CS analysis across multiple benchmarks reveals a fundamental contrast between
context-aware and context-unaware latent communication, reflecting the underlying information
structure of the communicated KV-cache signals.
8

## Page 9

Figure 5: Sparse reasoning signal vs. dense context signal (Qwen3-4B self-communication).
Accuracy is plotted against the number of KV groups kept (𝐾 of 288). Solid blue: context-aware
CS filtering, where the receiver still sees the input; 𝐾 = 0 is the single-agent receiver baseline. Open
blue squares: random KV-group selection. Solid red: context-unaware CS filtering, where the
receiver relies only on transmitted KV caches. Context-aware communication reaches near-ceiling
accuracy with few KV groups, suggesting a sparse reasoning signal. In contrast, context-unaware
communication requires dense context transfer, staying near chance until 𝐾 > 150 and approaching
the ceiling only at 𝐾 = 250 (87% of the cache).
As shown in Figure 5, in the context-aware setting, the receiver has access to the original input
context, and retaining only a small fraction of the KV cache suffices to achieve near-full performance.
This indicates that the channel primarily conveys a sparse reasoning signal, as the receiver’s local
context already provides core task information. Despite the small absolute information volume
required, the redundancy is highly structured: CS-derived rankings significantly outperform
uniform random pruning at low densities, highlighting that correctly identifying the functional
sub-networks of attention heads is critical. In practice, only the statistically reliable, high-importance
KV groups recovered by CS are considered, as lower-ranked groups collapse to the noise floor and
carry no meaningful contribution. These findings suggest that context-aware evaluation provides
a relatively weak test of latent communication: success depends on isolating and prioritizing the
sparse subset of heads carrying reasoning signals, rather than uniformly transmitting the cache.
In contrast, the context-unaware regime removes the receiver’s access to the input, forcing
it to rely entirely on the transmitted latent representations. Here, the information bottleneck
shifts dramatically: performance remains at chance or zero for most levels of dense compression,
exhibiting a sharp phase transition as more KV groups are retained. Unlike the sparse reasoning
case, successful communication in this setting requires a dense fraction of the cache to preserve
both contextual knowledge and reasoning structure. Because this regime directly tests whether
the latent channel faithfully conveys task-critical information without external context, it imposes
stricter constraints on alignment fidelity and motivates architectural mechanisms to preserve dense
knowledge while remaining computationally efficient.
These observations directly inform the design of our heterogeneous latent communication
framework, which addresses the dual demands of sparse reasoning and dense knowledge:
• Two-Stage Training for Density Preservation: Phase I enforces reconstruction of the KV cache
to preserve dense contextual and reasoning information, while Phase II optimizes downstream
generation to make the dense signal actionable for the receiver.
• Per-Head Transformations with Learnable Gating: Each query head is transformed individually
with a learnable gate, allowing the model to recover the structural importance of heads identified
9

## Page 10

by CS analysis and dynamically prioritize sparse reasoning signals.
• Positional Disentanglement: Rotary positional embeddings are explicitly stripped prior to
transformation and restored afterward, ensuring that positional information does not interfere
with content-aligned latent transfer.
4 Design of Dense Latent Communication
The analysis in Section 3 reveals two complementary aspects of the information structure in latent
communication. First, reasoning information is : only a small set of KV groups can provide the
sparse
high-level guidance needed to steer a receiver that already has access to the source context. Second,
knowledge is : when the transferred cache must stand in for the source context itself, task-
dense
critical information is distributed across a much larger fraction of the cache. These two properties
motivate a communication interface that is both density-preserving and structurally selective. As
illustrated in Figure 6, the proposed interface transforms the sender-side KV cache into a receiver-
compatible cache through structured cache operations, including position disentanglement, layer
alignment, head transformation, and information selection. Rather than designing a homogeneous
compression mechanism and later extending it across models, we directly learn a heterogeneous
dense-alignment interface that maps a sender cache into a receiver-compatible cache.
Concretely, for a sender agent 𝒜 and a receiver agent 𝒜 , we learn a cache transformation
𝑆 𝑅
𝒯
𝜽
that maps the sender KV cache 𝒞
𝑆
(𝑿 ), defined in Section 2.1, into a receiver-compatible cache
𝒞 (cid:101)𝑅 (𝑿 ) = 𝒯 𝜽 (𝒞 𝑆 (𝑿 )). The transformation is trained and parameterized so that the same interface
can serve both regimes: in context-aware communication, 𝒞
(cid:101)𝑅
(𝑿 ) provides a structured reasoning
signal alongside the receiver’s access to 𝑿 ; in context-unaware communication, it must act as a
dense surrogate for the missing source context.
4.1 Two-Phase Training for Dense and Actionable Alignment
A heterogeneous adapter trained only through the receiver’s final generation loss is undercon-
strained: many transformed caches may lead to the correct answer on a training example while
failing to preserve the source information in a reusable receiver-native form. We therefore separate
training into two phases. Phase I learns dense latent alignment by reconstructing the receiver’s own
cache. Phase II then tunes the aligned cache for downstream generation.
Phase I: receiver-cache reconstruction. For paired inputs, we run both agents on the same source
context 𝑿 and obtain the sender and receiver caches
(cid:110) (cid:16) (𝑙,𝑔) (𝑙,𝑔) (cid:17) (cid:111)
𝒞 𝑚 (𝑿 ) = 𝑲𝑚 (𝑿 ), 𝑽𝑚 (𝑿 ) , 𝑚 ∈ {𝑆, 𝑅}, (4)
𝑙,𝑔
where 𝑙 indexes transformer layers and 𝑔 indexes KV groups, consistent with the GQA notation in
Section 3.1. The adapter produces 𝒞 (cid:101)𝑅 (𝑿 ) = 𝒯 𝜽 (𝒞 𝑆 (𝑿 )) and is optimized to reconstruct the receiver’s
own cache:
(cid:213) (cid:13) (𝑙,𝑔) (𝑙,𝑔) (cid:13)2 (cid:13) (𝑙,𝑔) (𝑙,𝑔) (cid:13)2
ℒ rec = (cid:13) (cid:13) 𝑲(cid:101)𝑅 − 𝑲 𝑅 (cid:13) (cid:13) + (cid:13) (cid:13) 𝑽(cid:101)𝑅 − 𝑽 𝑅 (cid:13) (cid:13) . (5)
2 2
𝑙,𝑔
This phase teaches the adapter to express sender information in the receiver’s latent language.
It is especially important for context-unaware communication: if 𝒜 𝑅 cannot access 𝑿 , then the
transformed cache must serve as a dense surrogate for what the receiver would otherwise have
encoded from 𝑿 itself.
10

## Page 11

Sender & '
Layer 1 Layer 2
…
Layer )(
… … … … 1 2 3 "( 1 2 3 "( 1 2 3 "( 1 2 3 "#
Sender KV Cache * ( (,)
Head 1 Head 2 Head "(
.( (/,1) 2( (/,1) Layer 1
Layer 2
Layer )( …
Layer 1 Layer 2
…
Layer )#
… 1 2 3 "#
Sender KV Cache *3 # (,)
Head 1 Head 2 Head "#
… Layer 1
… Layer 2
… Layer )# …
Cache Transformation Receiver & 4
Input Generated
Prompt 5 6 Answer
… Dise
P
n
o
ta
s
n
it
g
io
le
n
m ent
1 2 3 … "#
…
*7
(
Layer Alignment
.( (/,8) 2( (/,8) .( (/,9:)2( (/,9:) Head .# (/,1) 2# (/,1) .# (/,8) 2# (/,8) … .# (/,9;)2# (/,9;) Transformation
…
Information Selection …
Figure 6: Overview of dense alignment: transform sender KV caches into receiver-compatible caches
with positional disentanglement, structured per-head transformation, and two-phase training.
Phase II: generation-oriented communication. After reconstruction pretraining, we optimize
the transformed cache for downstream generation under both communication regimes. For each
training example, the receiver-side context 𝑿𝑅 is drawn from a mixture of context-aware and
context-unaware prompts,
(cid:40)
𝑿 , context-aware,
𝑿𝑅 = (6)
∅, context-unaware,
and the same adapter 𝒯 is updated across both cases:
𝜽
(cid:213) (cid:16) (cid:17)
ℒ gen = − log 𝑝 𝒜 𝑦 𝑡 | 𝑦 <𝑡 , 𝒞 (cid:101)𝑅 (𝑿 ), 𝑿𝑅 , (7)
𝑅
𝑡
This joint Phase-II training is important because the two regimes stress different aspects of the
same latent channel: context-aware examples teach the cache to act as a structured reasoning signal
alongside the receiver’s prompt, while context-unaware examples force it to preserve enough dense
knowledge to replace the missing source context. This phase makes the aligned cache actionable:
the receiver must not only host a cache that resembles its own internal states, but also use that cache
to generate the correct output. Together, the two phases implement the main lesson from Section 3:
dense reconstruction preserves task knowledge, while mixed-regime generation tuning calibrates
one shared transformation for both operating regimes.
4.2 Architecture Design: Heterogeneous Dense Cache Alignment
The training objective above defines what 𝒯 should achieve. We now describe how 𝒯 is parame-
𝜽 𝜽
terized to respect the structure of heterogeneous transformer caches. In a heterogeneous MAS, 𝒞
𝑆
and 𝒞 may differ in depth, hidden dimension, KV-group organization, and positional convention.
𝑅
Direct cache injection is therefore ill-defined: even if the tensor shapes can be forced to match, the
sender cache is expressed in the wrong coordinate system for the receiver.
Position-disentangled cache transformation. Rotary positional embeddings entangle content
with model-specific phase rotations. Since dense communication should align the information
stored in the cache rather than copy the sender’s positional convention, 𝒯 first maps caches into a
𝜽
position-disentangled space:
𝒞 (cid:98)𝑚 = RemoveRoPE 𝑚 (𝒞 𝑚 ) , 𝑚 ∈ {𝑆, 𝑅}. (8)
11

## Page 12

The cross-model transformation is applied to 𝒞 to produce a receiver-side content cache 𝒞 ′ . The
(cid:98)𝑆
𝑅
final communicated cache restores the receiver’s positional convention:
𝒞 (cid:101)𝑅 = AddRoPE 𝑅 (cid:0)𝒞 𝑅 ′ (cid:1) . (9)
This makes position handling an architectural component of the interface: the adapter aligns content
in a shared position-disentangled space, then returns a cache that can be consumed by the receiver’s
attention blocks.
Layer alignment across different depths. Let 𝐿 𝑆 and 𝐿 𝑅 denote the sender and receiver depths.
For each receiver layer 𝑙, we pair it with a sender layer through a monotonic depth-preserving map
(cid:18) 𝑙(𝐿 − 1) (cid:19)
𝑎(𝑙) = round 𝐿 𝑆 − 1 , 𝑙 = 0, . . . , 𝐿 𝑅 − 1. (10)
𝑅
This mapping aligns early, middle, and late representations while avoiding a free routing problem
over all layer pairs. The design reflects a useful inductive bias: although two models may have
different depths, their computations still progress from local/token-level features toward more
task-level abstractions.
KV-group transformation with structured gates. After layer alignment, each receiver KV group
is produced from the corresponding sender-side content cache:
(cid:16) 𝑲
𝑅
′(𝑙,𝑔) , 𝑽
𝑅
′(𝑙,𝑔)(cid:17) = 𝛾(𝑙,𝑔) · (cid:16) 𝑇
𝐾
(𝑙
,
,
𝜽
𝑔) (cid:16) 𝑲(cid:98)𝑆 (𝑎(𝑙),𝜋 𝑙 (𝑔))(cid:17) , 𝑇
𝑉
(𝑙
,
,
𝜽
𝑔) (cid:16) 𝑽(cid:98)𝑆 (𝑎(𝑙),𝜋 𝑙 (𝑔))(cid:17) (cid:17) , (11)
where 𝜋 (𝑔) maps receiver KV group 𝑔 to a sender KV group, and 𝛾(𝑙,𝑔) ∈ [0, 1] is a learnable gate.
𝑙
When the two models have the same KV-group layout, 𝜋 reduces to the identity map. In our final
𝑙
(𝑙,𝑔) (𝑙,𝑔)
architecture, 𝑇 and 𝑇 are separate per-KV-group head-dimension MLPs applied token-wise
𝐾,𝜽 𝑉,𝜽
to key and value vectors:
(𝑙,𝑔) (𝑙,𝑔) (cid:16) (𝑙,𝑔) (𝑙,𝑔)(cid:17) (𝑙,𝑔)
𝑇 (𝒛) = 𝑾 𝜎 𝑾 𝒛 + 𝒃 + 𝒃 , (12)
★,𝜽 ★,2 ★,1 ★,1 ★,2
where ★ ∈ {𝐾, 𝑉}, 𝜎(·) is GELU, 𝒛 ∈ R𝑑 𝑆 is a sender key or value vector, 𝑾 (𝑙,𝑔) ∈ R16𝑑 𝑆 ×𝑑 𝑆 expands
★,1
the head dimension by a factor of 16, and 𝑾 (𝑙,𝑔) ∈ R𝑑 𝑅 ×16𝑑 𝑆 projects into the receiver head dimension
★,2
𝑑 . Separate MLP parameters are used for keys, values, and each routed receiver-layer/KV-group
𝑅
pair.
The KV-group-wise parameterization is motivated by the structure revealed in Section 3. Sparse
reasoning signals are not uniformly distributed across the cache; they concentrate in particular
heads or KV groups. At the same time, context-unaware transfer cannot collapse the channel to
only a few sparse groups because dense contextual knowledge is distributed broadly. The gate
therefore should not be viewed as a homogeneous compression trick. It is a structured reliability
weight inside a dense heterogeneous channel: it lets the model emphasize high-utility reasoning
subspaces without abandoning the dense information needed when the receiver cannot see the
source context.
12

## Page 13

In-domain OOD
Pair Method TFLOPs ↓
GSM8K MATH-500 ARC-C MMLU-Redux MedQA OpenBookQA
Receiver-only 81.10 49.20 91.00 72.10 53.00 91.20 19.85
T2T 88.10 76.00 91.74 80.75 67.40 90.40 37.73
4B → 8B
C2C 77.86 44.20 86.09 75.87 56.87 85.60 4.50
Ours 92.95 82.00 93.69 78.52 67.24 91.20 12.56
Receiver-only 83.70 46.40 92.60 71.80 64.70 91.80 31.16
T2T 92.34 77.80 92.00 82.87 71.17 92.00 56.24
4B → 14B
C2C 82.34 44.20 92.43 72.76 63.00 87.00 6.64
Ours 93.86 86.00 94.20 78.57 71.96 93.60 21.54
Receiver-only 82.40 44.20 89.20 65.00 47.70 88.00 9.18
T2T 89.39 63.20 90.96 79.39 66.46 87.00 33.91
8B → 4B
C2C 72.48 37.40 86.78 70.19 55.07 77.20 3.43
Ours 91.81 83.40 93.00 77.86 66.30 89.60 7.95
Receiver-only 83.70 46.40 92.60 71.80 64.70 91.80 31.16
T2T 93.93 75.00 91.74 84.13 72.66 92.80 67.08
8B → 14B
C2C 82.26 43.20 92.43 73.81 64.65 87.00 7.42
Ours 94.09 85.00 94.37 77.38 70.46 93.40 21.79
Receiver-only 82.40 44.20 89.20 65.00 47.70 88.00 9.18
T2T 90.60 60.20 89.83 80.61 69.91 85.00 43.48
14B → 4B
C2C 70.58 36.60 85.83 69.73 53.42 76.40 5.01
Ours 91.13 82.60 91.89 77.66 63.00 88.80 10.18
Receiver-only 81.10 49.20 91.00 72.10 53.00 91.20 19.85
T2T 91.58 73.00 92.35 83.43 72.90 90.20 55.50
14B → 8B
C2C 76.35 43.00 89.39 75.99 62.69 85.60 7.83
Ours 92.95 81.40 93.77 78.04 70.38 92.60 15.64
Table 1: Multi-task context-aware heterogeneous communication results on in-domain and out-
of-domain benchmarks. FLOPs are average total inference cost per example in TFLOPs, including
sender, receiver, and adapter computation when applicable (see Appendix B.2).
5 Experiments
Training Data. All cache transformation models are trained on a mixture of GSM8K [Cob+21],
MATH [Hen+21] (algebra subset), and ARC-Challenge [Cla+18]. Phase I requires only paired
sender and receiver cache states on the same source context. For Phase II, we construct receiver
self-guided reasoning traces, where the receiver model generates step-by-step solutions on the
training split using the ground-truth answer as guidance. Consequently, for a pair 𝒜 → 𝒜 , the
𝑆 𝑅
supervision target follows the reasoning style of the receiver rather than that of the sender or an
external teacher. Additional details are provided in Appendix A.
Experimental Setup. We evaluate our learned cache transformation across all six directions of
the {Qwen3-4B, 8B, 14B [Yan+25a]} pair set. Evaluation is performed on three in-domain tasks
(GSM8K, MATH-500, ARC-C) and three held-out MCQ benchmarks (MMLU-Redux [Gem+25],
MedQA [Yan+25b], OpenBookQA [Mih+18]). We compare three baselines against our method:
Receiver-only (single-agent with the receiver model), T2T (text-based communication), and C2C
[Fu+25] (learned cache transformation via steering). Both regimes from Section 3 are evaluated:
, where the receiver also sees the question, and , where the receiver
context-aware context-unaware
only sees the transferred signal. Inference TFLOPs are reported under a 2-parameters-per-token
estimator (Appendix B.1).
13

## Page 14

Pair Method In-domain OOD TFLOPs ↓
GSM8K MATH-500 ARC-C MMLU-Redux MedQA OpenBookQA
T2T-context-unaware 51.63 74.40 19.48 21.00 18.85 24.00 37.86
4B → 8B C2C-context-unaware 1.90 3.00 22.52 21.91 8.96 27.00 14.94
Ours-context-unaware 91.43 78.80 91.38 74.59 61.82 88.80 9.42
T2T-context-unaware 56.79 75.20 23.39 23.06 27.65 27.20 60.83
4B → 14B C2C-context-unaware 0.00 0.00 10.70 10.26 12.80 16.40 20.05
Ours-context-unaware 82.26 70.60 86.86 62.86 53.26 82.40 17.15
T2T-context-unaware 27.98 69.40 23.74 25.18 22.94 23.20 32.75
8B → 4B C2C-context-unaware 0.38 2.40 10.35 8.20 7.23 10.00 14.76
Ours-context-unaware 91.36 81.60 93.60 77.06 64.57 90.00 6.56
T2T-context-unaware 30.86 70.40 22.96 22.80 27.81 27.40 72.06
8B → 14B C2C-context-unaware 0.00 0.00 7.39 7.14 6.36 7.60 9.84
Ours-context-unaware 81.58 65.00 88.48 54.92 57.74 83.80 15.85
T2T-context-unaware 18.57 66.60 20.61 24.52 21.13 20.20 41.95
14B → 4B C2C-context-unaware 0.68 0.40 4.96 6.11 0.63 6.60 17.93
Ours-context-unaware 82.49 64.00 88.48 67.15 59.54 85.40 8.90
T2T-context-unaware 18.80 66.40 22.87 21.41 25.22 26.20 53.80
14B → 8B C2C-context-unaware 0.00 0.20 2.78 5.34 5.18 2.20 24.77
Ours-context-unaware 84.15 68.40 88.99 67.84 54.20 88.00 13.28
Table 2: Multi-task context-unaware heterogeneous communication results on in-domain and
out-of-domain benchmarks. Only the sender observes the original input; the receiver relies solely
on the communicated signal. T2T-context-unaware transmits a natural-language message, while
C2C-context-unaware and Ours-context-unaware transmit latent KV caches.
5.1 Context-aware Results
Table 1 reports context-aware results, where the receiver still has the question in its prompt and the
channel acts as an auxiliary signal. Our learned cache transformation matches or exceeds T2T on
every in-domain task across all six pairs (GSM8K +0.16 to +4.85 pp; MATH-500 +6.00 to +20.40 pp;
ARC-C +1.34 to +3.94 pp), and is competitive on the held-out OOD benchmarks (within ∼ 5 pp
of T2T on MMLU-Redux/MedQA, and at-or-above T2T on OpenBookQA in 5 of 6 pairs). C2C
underperforms our method on all tasks, confirming the advantage of our dense alignment over
sparse reasoning-signal steering in the same context-aware setting.
The efficiency story is just as strong. Our channel runs 2–3× cheaper than T2T in TFLOPs (e.g.,
4B→14B: 21.5 vs 56.2; 8B→14B: 21.8 vs 67.1), and is cheaper than even the bare Receiver-only
baseline in 5 of 6 directions, because (i) the sender does no autoregressive reasoning (ℓ 𝑆 = 0) and
dec
(ii) the receiver does not re-encode a long natural-language sender message but instead attends to
a compact transferred cache. So the channel is simultaneously more accurate and cheaper than the
natural-text alternative.
5.2 Context-unaware Results
Table 2 reports the context-unaware regime: only the sender observes the question, and the receiver
must produce the answer from the transferred signal alone. This is the strict test of channel
information density. Without our dense transformation, context-unaware communication essentially
fails. T2T-context-unaware drops the receiver to 19–57% on GSM8K and to MCQ-chance on ARC-
C/MedQA/OpenBookQA, because the sender’s free-form text was generated for a question-aware
reader and does not preserve task content end-to-end. C2C-context-unaware performs even worse:
accuracy collapses to 0–2% on every reasoning task, indicating that steering-based KV transfer fails
to preserve or align the contextual information needed by the receiver.
14

## Page 15

Figure 7: PCA of KV cache latents: transformed sender caches directly overlap receiver-native
manifolds, indicating dense geometric alignment rather than sparse shortcuts used for steering.
In stark contrast, our channel sustains accuracy within 0–10 pp of its own context-aware num-
bers across all six pairs and all six benchmarks (GSM8K 81–91, MATH-500 64–82, ARC-C 87–94,
MMLU-Redux 55–77, MedQA 53–65, OpenBookQA 82–90). The TFLOPs are even lower than the
corresponding context-aware row, since the receiver’s prefill shrinks further with no question text
to encode. The 8B → 4B pair illustrates the headline efficiency win: Ours-context-unaware reaches
91.4/81.6/93.6 on the in-domain triple at 6.6 TFLOPs –
cheaper than the bare
4
B receiver
(9.2 TFLOPs)
and within 1–2 pp of T2T context-aware at 5× fewer FLOPs. Dense knowledge transfer through the
learned latent channel is therefore both feasible and substantially more efficient than the natural-text
alternative.
5.3 Latent Space Visualization
To check that our quantitative results reflect a genuine geometric alignment rather than a brittle
decoder-fooling shortcut, we project per-token value vectors of the receiver’s cache space onto their
first two principal components (Figure 7) for an early layer (L7) and a late layer (L34). On identical
inputs, the transformed sender cache lies on the same manifold as the receiver’s native cache at both
depths, while the untransformed sender cache (not shown for clarity) occupies a disjoint region.
The learned transformation 𝑇 thus maps sender activations into the receiver’s geometry rather
𝜃
than producing a representation that only the trained receiver can decode.
6 Conclusion
We studied heterogeneous latent communication through a simple question aligned with our title:
can one agent transfer both what it sees and how it thinks to another agent. Our compressed-sensing
analysis shows a duality: latent channels are sparse in reasoning for context-aware communication,
but dense in knowledge for context-unaware communication where the receiver sees no input. This
clarifies why prior evaluations in mostly context-aware settings are insufficient. Motivated by this
structure, we proposed dense alignment with three components: per-head transformation and
gating, position-disentangled alignment, and two-phase reconstruction-then-generation training.
Across all six directions of {Qwen3-4B, 8B, 14B}, our method surpasses sparse-steering heteroge-
neous baselines, matches or exceeds text communication in context-aware settings at 2–3× lower
15

## Page 16

compute, and remains accurate in context-unaware settings where prior baselines collapse.
Limitations and future work. Our method currently needs one training pass per sender-receiver
pair; scaling to open-set pairings and shared transforms across many senders is a key next step. The
context-unaware regime also raises privacy questions, since transferring task content without the
prompt changes what can be inferred from the channel.
References
[Bai+26] Anish Bair et al. “Identifying Functional Heads of Large Language Models with
Compressed Sensing”. In: (2026).
arXiv preprint arXiv:2603.03335
[Che+25] Weize Chen, Jiarui Yuan, Chen Qian, Cheng Yang, Zhiyuan Liu, and Maosong Sun.
“Optima: Optimizing effectiveness and efficiency for llm-based multi-agent system”.
In: . 2025, pp. 11534–
Findings of the Association for Computational Linguistics: ACL 2025
11557.
[Cla+18] Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa
Schoenick, and Oyvind Tafjord. “Think you have solved question answering? try arc,
the ai2 reasoning challenge”. In: (2018).
arXiv preprint arXiv:1803.05457
[Cob+21] Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz
Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, et al. “Train-
ing verifiers to solve math word problems”. In: (2021).
arXiv preprint arXiv:2110.14168
[Du+25] Zhuoyun Du, Runze Wang, Huiyu Bai, Zouying Cao, Xiaoyong Zhu, Yu Cheng, Bo
Zheng, Wei Chen, and Haochao Ying. “Enabling agents to communicate entirely in
latent space”. In: (2025).
arXiv preprint arXiv:2511.09149
[Fei+25] Jacob Fein-Ashley, Dhruv Parikh, Rajgopal Kannan, and Viktor Prasanna. “Mixture of
thoughts: Learning to aggregate what experts think, not just what they say”. In:
arXiv
(2025).
preprint arXiv:2509.21164
[Fu+25] Tianyu Fu, Zihan Min, Hanling Zhang, Jichao Yan, Guohao Dai, Wanli Ouyang, and
Yu Wang. “Cache-to-cache: Direct semantic communication between large language
models”. In: (2025).
arXiv preprint arXiv:2510.03215
[Gem+25] Aryo Pradipta Gema, Joshua Ong Jun Leang, Giwon Hong, Alessio Devoto, Alberto
Carlo Maria Mancino, Rohit Saxena, Xuanli He, Yu Zhao, Xiaotang Du, Mohammad
Reza Ghasemi Madani, et al. “Are we done with mmlu?” In:
Proceedings of the 2025
Conference of the Nations of the Americas Chapter of the Association for Computational
. 2025, pp. 5069–5096.
Linguistics: Human Language Technologies (Volume 1: Long Papers)
[Hen+21] Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul Arora, Steven Basart, Eric Tang,
Dawn Song, and Jacob Steinhardt. “Measuring mathematical problem solving with
the math dataset”. In: (2021).
arXiv preprint arXiv:2103.03874
[Hon+24] Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu Zheng, Yuheng Cheng, Jinlin
Wang, Ceyao Zhang, Steven Yau, Zijuan Lin, Liyang Zhou, et al. “MetaGPT: Meta
programming for a multi-agent collaborative framework”. In:
International Conference
. Vol. 2024. 2024, pp. 23247–23275.
on Learning Representations
[Jin+26] Haibo Jin, Kuang Peng, Ye Yu, Xiaopeng Yuan, and Haohan Wang. “Agent Primi-
tives: Reusable Latent Building Blocks for Multi-Agent Systems”. In:
arXiv preprint
(2026).
arXiv:2602.03695
16

## Page 17

[LAD26] Yiping Li, Zhiyu An, and Wan Du. “When Less Latent Leads to Better Relay: Information-
Preserving Compression for Latent Multi-Agent LLM Collaboration”. In:
arXiv preprint
(2026).
arXiv:2604.13349
[Liu+24] Yuhan Liu, Yuyang Huang, Jiayi Yao, Shaoting Feng, Zhuohan Gu, Kuntai Du, Hanchen
Li, Yihua Cheng, Junchen Jiang, Shan Lu, et al. “DroidSpeak: KV Cache Sharing for
Cross-LLM Communication and Multi-LLM Serving”. In:
arXiv preprint arXiv:2411.02820
(2024).
[Mih+18] Todor Mihaylov, Peter Clark, Tushar Khot, and Ashish Sabharwal. “Can a Suit of
Armor Conduct Electricity? A New Dataset for Open Book Question Answering”. In:
. 2018.
EMNLP
[Pha+24] Chau Pham, Boyi Liu, Yingxiang Yang, Zhengyu Chen, Tianyi Liu, Jianbo Yuan, Bryan
Plummer, Zhaoran Wang, and Hongxia Yang. “Let models speak ciphers: Multiagent
debate through embeddings”. In: .
International Conference on Learning Representations
Vol. 2024. 2024, pp. 51899–51928.
[RL25] Vignav Ramesh and Kenneth Li. “Communicating activations between language
model agents”. In: (2025).
arXiv preprint arXiv:2501.14082
[Shi+25] Xiangyu Shi, Marco Chiesa, Gerald Q Maguire Jr, and Dejan Kostic. “KVComm:
Enabling Efficient LLM Communication through Selective KV Sharing”. In:
arXiv
(2025).
preprint arXiv:2510.03346
[Tan+25] Yichen Tang, Weihang Su, Yujia Zhou, Yiqun Liu, Min Zhang, Shaoping Ma, and
Qingyao Ai. “Augmenting Multi-Agent Communication with State Delta Trajectory”.
In: .
Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
2025, pp. 10230–10251.
[Tra+25] Khanh-Tung Tran, Dung Dao, Minh-Duong Nguyen, Quoc-Viet Pham, Barry O’Sullivan,
and Hoang D Nguyen. “Multi-agent collaboration mechanisms: A survey of llms”. In:
(2025).
arXiv preprint arXiv:2501.06322
[Wan+25] Zhexuan Wang, Yutong Wang, Xuebo Liu, Liang Ding, Miao Zhang, Jie Liu, and
Min Zhang. “Agentdropout: Dynamic agent elimination for token-efficient and high-
performance llm-based multi-agent collaboration”. In:
Proceedings of the 63rd Annual
. 2025,
Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)
pp. 24013–24035.
[Wan+26] Ziyu Wan, Yunxiang Li, Xiaoyu Wen, Yan Song, Hanjing Wang, Linyi Yang, Mark
Schmidt, Jun Wang, Weinan Zhang, Shuyue Hu, et al. “Rema: Learning to meta-think
for llms with multi-agent reinforcement learning”. In:
Advances in Neural Information
38 (2026), pp. 126621–126667.
Processing Systems
[Wu+24] Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu, Li Jiang,
Xiaoyun Zhang, Shaokun Zhang, Jiale Liu, et al. “Autogen: Enabling next-gen LLM
applications via multi-agent conversations”. In: .
First conference on language modeling
2024.
[Yan+25a] An Yang, Anfeng Li, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen
Yu, Chang Gao, Chengen Huang, Chenxu Lv, et al. “Qwen3 technical report”. In:
arXiv
(2025).
preprint arXiv:2505.09388
17

## Page 18

[Yan+25b] Hang Yang, Hao Chen, Hui Guo, Yineng Chen, Ching-Sheng Lin, Shu Hu, Jinrong Hu,
Xi Wu, and Xin Wang. “Llm-medqa: Enhancing medical question answering through
case studies in large language models”. In:
2025 International Joint Conference on Neural
. IEEE. 2025, pp. 1–8.
Networks (IJCNN)
[Yan+26] Xiyuan Yang, Jiaru Zou, Rui Pan, Ruizhong Qiu, Pan Lu, Shizhe Diao, Jindong Jiang,
Hanghang Tong, Tong Zhang, Markus J Buehler, et al. “Recursive multi-agent systems”.
In: (2026).
arXiv preprint arXiv:2604.25917
[Yu+26] Ye Yu, Heming Liu, Haibo Jin, Xiaopeng Yuan, Peng Kuang, and Haohan Wang. “Learn-
ing to Communicate: Toward End-to-End Optimization of Multi-Agent Language
Systems”. In: (2026).
arXiv preprint arXiv:2604.21794
[Zha+25a] Guibin Zhang, Yanwei Yue, Zhixun Li, Sukwon Yun, Guancheng Wan, Kun Wang,
Dawei Cheng, Jeffrey Yu, and Tianlong Chen. “Cut the crap: An economical commu-
nication pipeline for llm-based multi-agent systems”. In:
International Conference on
. Vol. 2025. 2025, pp. 75389–75428.
Learning Representations
[Zha+25b] Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu, Fengwei Teng, Xionghui Chen, Jiaqi Chen,
Mingchen Zhuge, Xin Cheng, Sirui Hong, Jinlin Wang, et al. “Aflow: Automating
agentic workflow generation”. In: .
International Conference on Learning Representations
Vol. 2025. 2025, pp. 34040–34077.
[Zha+26] Wanjia Zhao, Mert Yuksekgonul, Shirley Wu, and James Zou. “Sirius: Self-improving
multi-agent systems via bootstrapped reasoning”. In:
Advances in Neural Information
38 (2026), pp. 124475–124504.
Processing Systems
[Zhe+26] Yujia Zheng, Zhuokai Zhao, Zijian Li, Yaqi Xie, Mingze Gao, Lizhu Zhang, and Kun
Zhang. “Thought communication in multiagent collaboration”. In:
Advances in Neural
38 (2026), pp. 123389–123418.
Information Processing Systems
[Zou+25] Jiaru Zou, Xiyuan Yang, Ruizhong Qiu, Gaotang Li, Katherine Tieu, Pan Lu, Ke Shen,
Hanghang Tong, Yejin Choi, Jingrui He, et al. “Latent collaboration in multi-agent
systems”. In: (2025).
arXiv preprint arXiv:2511.20639
18

## Page 19

A Phase-II Trace Construction
Phase II trains the cache transformation with a supervised generation loss, so each source context
must be paired with a receiver-side target output. We construct these targets as
receiver-self guided
traces : for each sender–receiver pair 𝒜 𝑆 → 𝒜 𝑅 , the trace generator is the receiver model 𝒜 𝑅 itself.
This choice avoids teaching the receiver to imitate a different model’s wording or reasoning style
after cache transfer; the adapter instead learns to produce receiver-native latent states that decode
into outputs the receiver is already well suited to generate.
Trace-generation tasks. The Phase-II trace pool contains three in-domain training tasks: GSM8K,
MATH-algebra, and ARC-Challenge. These are the same tasks used for multitask Phase-II training
in the main experiments. MATH-500, MMLU-Redux, MedQA, and OpenBookQA are not used for
Phase-II trace generation; they are held for evaluation, with MATH-500 replacing MATH-algebra as
the reported mathematical reasoning benchmark.
Guided trace generation. For each training example (𝑿 , 𝒚), we prompt the receiver model with
the source question and the ground-truth answer, then ask it to produce a step-by-step solution
that arrives at that answer. The resulting JSONL record contains the question, the gold answer, the
generated solution trace, and a trace-mode tag. For multiple-choice tasks such as ARC-Challenge,
the trace is relabeled to end with the canonical answer format Answer: X, matching the receiver-
side evaluation prompt. This relabeling prevents the training target from using a format that the
evaluator later rejects or scores inconsistently.
Pair-specific receiver traces. Because the trace generator is the receiver, different cross-model
directions use different trace files. For example, 14B→ 4B uses Qwen3-4B-self traces, while 4B→ 14B
uses Qwen3-14B-self traces. These traces are generated on the training split with guided decoding
and then matched back to training examples by question text before Phase-II optimization.
Mixed-regime receiver prompts. During Phase II, we train the same adapter on both context-
aware and context-unaware receiver prompts. We set the receiver prompt to be context-aware with
probability 0.5 and context-unaware with probability 0.5. Equivalently, the receiver-side context
variable in Section 4 is sampled as 𝑿𝑅 = 𝑿 half of the time and 𝑿𝑅 = ∅ half of the time. The target
trace is unchanged across these two cases; only the receiver’s direct access to the source context
changes. This forces the transferred cache to support both roles identified in Section 3: a sparse
reasoning signal when the receiver has the context, and a dense knowledge carrier when it does not.
In all main experiments, Phase II starts from the Phase-I reconstruction checkpoint and runs for
2000 optimization steps with cross-entropy on the receiver-self trace tokens.
B Efficiency Analysis and Per-Side Breakdown
We measure system-level compute efficiency under each method’s canonical inference recipe and
break the FLOPs column of Tables 1 and 2 into its four constituent per-side token counts: sender
prefill ℓ 𝑆 , sender decode ℓ 𝑆 , receiver prefill ℓ 𝑅 , and receiver decode ℓ 𝑅 .
pre dec pre dec
19

## Page 20

B.1 Measurement recipe
Sample composition. For each (pair, method, mode) cell we sample 17 examples from each of six
benchmarks (GSM8K, MATH-500, ARC-Challenge, MMLU-Redux, OpenBookQA, MedQA) using
a fixed seed, pooled to ≈102 samples per cell. This is small enough that we report only the mean
per token-count field; per-task and p50/p95 breakdowns are released as a CSV companion to this
paper.
Inference recipe. All methods are evaluated under a shared decoding setup with fixed sampling
parameters and the same token budget, using single-sample inference to avoid batch-padding
artifacts in latency and token counts. Receiver-only and T2T use their standard text-generation
configuration, and Ours uses the same reasoning style as in training. Each method is evaluated in
its strongest canonical configuration for a fair comparison.
FLOPs estimate. We use the standard “2 parameters per token” rule of thumb for the forward
pass:
FLOPs ≈ 2 𝑁 (ℓ 𝑆 + ℓ 𝑆 ) + 2 𝑁 (ℓ 𝑅 + ℓ 𝑅 ),
(cid:155) 𝑆 pre dec 𝑅 pre dec
where 𝑁 , 𝑁 are the (non-embedding) parameter counts of the sender and receiver models. The
𝑆 𝑅
attention term’s 𝑂(𝐿 ) contribution is excluded; at our reasoning lengths it is below 5% of the
kv
linear-projection total and including it does not change any ranking in the headline tables.
Token-count instrumentation. Token counts are exact, not estimated from rendered text. We
record generated token IDs directly and compute per-sample prefill/decode lengths from model
outputs.
Bandwidth disclosure. The KV-cache payload for Ours is approximately 20–30 MB per sample,
whereas an equivalent text message is on the order of hundreds of bytes. This is a network-
bandwidth axis, not a compute axis, so it is excluded from the headline TFLOPs comparison.
B.2 Per-side breakdown
Table 3 reports the four per-side token counts plus the unweighted total All tok for every (pair,
method, mode) cell. The structural mechanism behind each method’s compute profile is then
visible. Both Ours and C2C eliminate the sender’s autoregressive reasoning (ℓ 𝑆 = 0); the receiver
dec
prefill is small for both (ℓ 𝑅 = 220 for Ours, 117 for C2C in w/ctx mode) – substantially below T2T’s
pre
ℓ 𝑅 ∼ 1,100–1,300 tokens of re-encoded sender text. The remaining gap between Ours and C2C
pre
is in the length: Ours produces explicit step-by-step reasoning before the answer
receiver decode
(ℓ 𝑅 ≈ 400–500 in w/ctx mode), whereas C2C emits a more terse answer (ℓ 𝑅 ≈ 80–170). This
dec dec
trades fewer FLOPs for substantially lower accuracy on most benchmarks (see Tables 1 and ??).
B.3 Structural observations
Three observations follow from Table 3.
(i) Both Ours and C2C eliminate sender decoding. T2T spends ∼900–1,080 sender-decode tokens
producing a ∼2,048-token sender CoT. Ours instead encodes the question into a sender KV cache
without autoregressive sender decoding (ℓ 𝑆 = 0); C2C similarly transfers a cache without sender
dec
generation.
20

## Page 21

(ii) Receiver prefill is small for both cache-based methods, ∼6× smaller than T2T. Ours has
ℓ 𝑅 = 220 (w/ctx) / 63 (context-unaware); C2C has 117 / 14. Both stand in sharp contrast to T2T’s
pre
ℓ 𝑅 ∼ 1,100–1,300 tokens of re-encoded sender message: the receiver no longer needs to ingest the
pre
sender’s natural-language reasoning through its embedding pipeline.
(iii) The remaining FLOPs gap between Ours and C2C is in receiver decode, not in the commu-
nication mechanism. In w/ctx mode Ours produces explicit step-by-step reasoning before the
answer (ℓ 𝑅 ∼ 400–500); C2C emits a more terse output (ℓ 𝑅 ∼ 80–170). The lower decode length
dec dec
translates to a ∼2–3× smaller TFLOPs total for C2C w/ctx – but at the cost of substantially lower
accuracy on most benchmarks (Tables 1 and 2). In context-unaware mode C2C’s receiver decode
swings wildly across pairs (ℓ 𝑅 ∈ [270, 1,817]); Ours keeps a stable decode profile across all six
dec
pairs (ℓ 𝑅 ≈ 400), and Ours-context-unaware is the cheapest cell in 5 of 6 pairs.
dec
B.4 Notes
Receiver-only in 14B → 4B. In the one direction with a 4B receiver, the bare Receiver-only baseline
(4B alone, ∼994 receiver-decode tokens) costs 9.18 TFLOPs. Adding our 14B sender prefill (∼184
tokens) makes Ours marginally more expensive at 10.18 TFLOPs in w/ctx mode, although Ours-
context-unaware drops back to 8.90. In every other direction Ours is cheaper than Receiver-only.
Accuracy / FLOPs Pareto. C2C achieves the lowest TFLOPs by emitting short answers, but its
accuracy on most benchmarks trails Receiver-only and Ours by a wide margin (e.g., 14B→4B
GSM8K: C2C 70.58% vs. Ours 91.13%; 4B→8B MATH-500: C2C 44.20% vs. Ours 82.00%). Ours sits
between C2C and T2T on the FLOPs axis while matching or beating T2T on accuracy in nearly every
cell, so the FLOPs-vs-accuracy Pareto frontier of Table 1 is dominated by Ours: it strictly beats T2T
(lower FLOPs and higher accuracy on most cells) and strictly beats C2C on accuracy at moderate
extra FLOPs cost.
21

## Page 22

Pair Method Mode Spre Sdec Rpre Rdec All tok TFLOPs
Receiver-only w/ctx 0 0 154 1,087 1,241 19.85
T2T w/ctx 180 1,033 1,255 497 2,965 37.73
T2T-context-unaware context-unaware 180 1,077 1,180 558 2,995 37.86
4B → 8B C2C w/ctx 117 0 117 106 340 4.50
C2C-context-unaware context-unaware 117 0 14 861 993 14.94
Ours w/ctx 184 0 220 473 877 12.56
Ours-context-unaware context-unaware 184 0 63 433 681 9.42
Receiver-only w/ctx 0 0 154 959 1,113 31.16
T2T w/ctx 180 1,020 1,242 423 2,866 56.24
T2T-context-unaware context-unaware 180 1,052 1,155 666 3,053 60.83
4B → 14B C2C w/ctx 117 0 117 87 321 6.64
C2C-context-unaware context-unaware 117 0 14 668 800 20.05
Ours w/ctx 184 0 220 497 901 21.54
Ours-context-unaware context-unaware 184 0 63 497 744 17.15
Receiver-only w/ctx 0 0 154 994 1,147 9.18
T2T w/ctx 180 1,074 1,296 433 2,984 33.91
T2T-context-unaware context-unaware 180 1,037 1,139 520 2,877 32.75
8B → 4B C2C w/ctx 117 0 117 77 311 3.43
C2C-context-unaware context-unaware 117 0 14 1,597 1,728 14.76
Ours w/ctx 184 0 220 405 810 7.95
Ours-context-unaware context-unaware 184 0 63 388 636 6.56
Receiver-only w/ctx 0 0 154 959 1,113 31.16
T2T w/ctx 180 1,066 1,288 396 2,930 67.08
T2T-context-unaware context-unaware 180 1,073 1,175 682 3,111 72.06
8B → 14B C2C w/ctx 117 0 117 81 315 7.42
C2C-context-unaware context-unaware 117 0 14 270 402 9.84
Ours w/ctx 184 0 220 453 857 21.79
Ours-context-unaware context-unaware 184 0 63 398 645 15.85
Receiver-only w/ctx 0 0 154 994 1,147 9.18
T2T w/ctx 180 923 1,145 430 2,677 43.48
T2T-context-unaware context-unaware 180 886 988 525 2,579 41.95
14B → 4B C2C w/ctx 117 0 117 99 333 5.01
C2C-context-unaware context-unaware 117 0 14 1,817 1,948 17.93
Ours w/ctx 184 0 220 407 811 10.18
Ours-context-unaware context-unaware 184 0 63 405 652 8.90
Receiver-only w/ctx 0 0 154 1,087 1,241 19.85
T2T w/ctx 180 890 1,112 483 2,666 55.50
T2T-context-unaware context-unaware 180 887 989 505 2,562 53.80
14B → 8B C2C w/ctx 117 0 117 167 402 7.83
C2C-context-unaware context-unaware 117 0 14 1,329 1,461 24.77
Ours w/ctx 184 0 220 435 839 15.64
Ours-context-unaware context-unaware 184 0 63 444 692 13.28
Table 3: Per-side efficiency breakdown. Mean per-sample token counts on the sender (Spre /
Sdec = prefill / decode) and receiver (Rpre / Rdec) sides, pooled across the six benchmarks of
Tables 1 and 2. All tok = ℓ 𝑆 + ℓ 𝑆 + ℓ 𝑅 + ℓ 𝑅 (every token that touches either model). TFLOPs
pre dec pre dec
computed via the formula in Appendix B.1. Bold marks the lowest TFLOPs cell within each pair
(across all methods + modes).
22

## Page 23

C Compressed-Sensing Analysis Across Regimes
Section 3 uses post-hoc compressed sensing (CS) [Bai+26] to identify which sender heads carry
the channel’s task-relevant signal and then evaluate accuracy as a function of how many of those
heads are kept. This section documents the setup and results behind Figure 5.
C.1 Self-communication setup
Sender and receiver are the same Qwen3-4B model (homogeneous, identity KV pass-through): the
sender encodes the question into a KV cache with zero sender decoding, and the receiver consumes
that cache directly. Qwen3-4B has 36 layers × 32 query heads = 1152 query heads, organized into
36 × 8 = 288 KV groups under GQA (each KV head shared across 4 query heads). All ablations
target sender-side transmitted KV components, while receiver attention is unchanged.
From query-head importance to KV-group importance. The CS measurements (Stage 1 below)
perturb individual , so the Lasso problem is naturally posed at the 1152-query-head
query heads
granularity. The transmitted KV cache itself, however, has only 288 KV groups. To go from one to
the other, we sum the 4 query-head Lasso coefficients within each GQA group:
score( K 𝑙 V ,ℎ KV ) = (cid:213) 𝑥ˆ 𝑙,ℎ 𝑄 ,
ℎ ∈ group(ℎ )
𝑄 KV
which gives a per-(layer, KV-head) importance score; Stage 2 keeps the top-𝐾 of these.
C.2 Stage 1: CS head ranking
We take 𝑀 = 200 binary ablation masks Φ ∈ {0, 1}𝑀×𝑁 over the 𝑁 = 1152 query heads, with
each row stratified to zero exactly 5% of heads (≈ 58 heads per mask). For each mask 𝑚, we run
the full sender→receiver pipeline on 100 evaluation samples and record the resulting metric 𝑦
𝑚
(accuracy on GSM8K / MATH-algebra / ARC-Challenge), then center it by the unablated baseline,
𝑦˜ 𝑚 = 𝑦 𝑚 − 𝑦 baseline . We then solve a Lasso regression for the per-head importance vector x ∈ R𝑁 :
1
xˆ = arg min 2𝑀 (cid:13) (cid:13)y˜ − Φ x (cid:13) (cid:13) 2 2 + 𝛼 ∥x∥ 1 , 𝛼 = 10−4,
x∈R𝑁
(an intercept is also fit but omitted from the display), and rank heads by −𝑥ˆ (most-negative 𝑥ˆ
𝑖 𝑖
indicates highest importance, since masking it most degrades accuracy).
C.3 Stage 2: 𝐾-sweep on full test
Using the per-head ranking from Stage 1, we evaluate accuracy on the full test split when only the
top-𝐾 KV groups (out of 288) are retained in the transmitted cache and the rest are zeroed. We
sweep 𝐾 ∈ {10, 20, 50, 100, 150, 288} under two regimes:
• : the receiver receives the standard prompt including the question text, on top of the
Context-aware
(filtered) sender KV. This is the regime evaluated by most prior work [Du+25; Shi+25; Fu+25].
• : the receiver’s prompt omits the question, so the filtered sender KV is the only
Context-unaware
task signal it sees.
The two regimes share the same head ranking and the same 𝐾 levels; only receiver access to the
input differs.
23

## Page 24

C.4 Random-filter baseline
For the random-filter markers in Figure 5, we replace the CS-Lasso ranking with a uniform random
selection of 𝐾 KV groups, repeat with 3 seeds, and report the mean. The CS-vs-random gap
measures how much the head ranking is doing beyond uniform sparsity.
C.5 Recovery-limit caveat
The recovery limit applies to the underlying Lasso problem, not to the aggregated KV-group
ranking. With 𝑀 = 200 measurements over 𝑁 = 1152 query heads , standard CS recovery bounds
give 𝑠 ≈ 𝑀/log (𝑁/𝑠) ≈ 70–80 informative coefficients; query-head coefficients past Lasso rank
max 2
∼ 80 are essentially zero. After GQA aggregation to 288 KV groups, this means at most ∼ 70 KV
groups inherit a meaningful ranking, and the remaining ∼ 220 KV groups have aggregated scores
that are tiebreaks over zeros and an arbitrary layer-imbalanced order. Consequently, at 𝐾 = 200
(i.e., keeping all but ∼ 90 KV groups – well into the noise-floor region) CS and random schemes
converge and a small inversion appears. We therefore restrict the headline figure to 𝐾 ≤ 150 on the
CS-Lasso side, where the ranking is statistically reliable.
C.6 Context-Aware and Context-Unaware Results
C.6.1 Context-aware regime
In the context-aware regime (solid blue curve in Figure 5), retaining only 𝐾 = 10 KV groups of
288 already matches the full-KV ceiling on all three tasks: GSM8K [Cob+21] 0.883 (vs. 0.917 at
𝐾 = 288), ARC-Challenge [Cla+18] 0.873 (vs. 0.880), and MATH-algebra [Hen+21] 0.699 (vs. 0.698).
Compared to the single-agent receiver at 𝐾 = 0, the channel’s actual lift over the receiver’s own
reasoning is at most ∼ 10 pp (MATH-algebra) and under 2 pp (ARC-Challenge). The receiver’s
own input already supplies the task content; the channel only needs to carry a small reasoning
signal on top. The redundancy is, however, structured rather than uniform. CS-Lasso head selection
meaningfully outperforms random selection at small 𝐾: at 𝐾 = 50, CS reaches 0.876/0.862/0.577
on the three tasks vs. 0.605/0.583/0.484 for random (+27/+28/+9 pp gaps). On MATH-algebra at
𝐾 = 20, random selection (0.559) actually drops below the receiver-only baseline (0.597) – unguided
pruning actively hurts even when the receiver has the prompt. The absolute information needed is
small, but bits are kept matters substantially.
which
C.6.2 Context-unaware regime
When receiver access to the prompt is removed (solid red curve), the same compression behaves
very differently: the channel becomes the task signal, and the profile shifts from a plateau to a
only
sharp transition zone . Across all three tasks, accuracy stays near chance for 𝐾 ≤ 150 (≤ 52% of the
cache kept), rises sharply between 𝐾 = 150 and 𝐾 = 200 (e.g., ARC-Challenge 0.27 → 0.79, GSM8K
0.00 → 0.28), and approaches the channel ceiling by 𝐾 = 250 (87% kept; 0.834/0.904/0.686, close to
𝐾 = 288 values 0.880/0.901/0.694). Below the transition, chance-level and zero-level points reflect
failure modes rather than meaningful performance gradations. This is the core sparse-vs-dense
contrast. Compared against ??, where 𝐾 = 10 (∼ 3.5% of the cache) was already sufficient under
context-aware evaluation, the context-unaware regime requires roughly 𝐾 = 250 – a ∼ 25× swing
in how much of the channel must be preserved depending on whether the receiver has the input.
Crucially, the channel does not need to carry of the cache to function under context-unaware
all
evaluation (𝐾 = 250 ≈ 𝐾 = 288); it needs an information-preserving fraction of it, which is much larger
than the small reasoning steer that suffices when the input is already with the receiver.
24

## Page 25

C.6.3 Takeaway for model design
Context-aware evaluation is a weak test of latent channels because the receiver can compensate
with its own input. By contrast, context-unaware evaluation is a strict test of information transfer
and alignment fidelity, since the channel is the only task signal. This sparse-vs-dense dichotomy
directly motivates our heterogeneous design (Section 4): two-phase training preserves dense
information and makes it decoder-actionable, while per-head transformation and gating capture
structured sparse reasoning signals. For the dense regime, two-phase training pairs (i) Phase I
cache reconstruction, which forces the transformation to preserve receiver-equivalent information
density, with (ii) Phase II generation training, which makes that dense signal decoder-actionable.
For the sparse regime, we parameterize 𝑇 at per-head granularity with a lightweight learnable
𝜃
gate per head, letting the model recover from data the same head-importance structure CS-Lasso
recovers post-hoc. Position is treated separately via RoPE strip/restore, since the redundancy lives
in content heads, not positional structure.
25
