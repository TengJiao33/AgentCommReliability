# kvcomm-cross-context-2510.12872

- Source PDF: `kvcomm-cross-context-2510.12872.pdf`
- Extracted at UTC: `2026-07-09T04:27:06.075417+00:00`
- Pages: 40
- Title: KVCOMM: Online Cross-context KV-cache Communication for Efficient LLM-based Multi-agent Systems
- SHA256: `3acffcc4468b17cf5193a64ec998c6517af42acb247fc230171da92f0f9eb8df`

## Page 1

KVCOMM: Online Cross-context KV-cache
Communication for Efficient LLM-based Multi-agent
Systems
Hancheng Ye1, Zhengqi Gao2, Mingyuan Ma1,
Qinsi Wang1, Yuzhe Fu1, Ming-Yu Chung1, Yueqian Lin1,
Zhijian Liu3, Jianyi Zhang1, Danyang Zhuo1, Yiran Chen1
1Duke University, 2MIT, 3NVIDIA
hancheng.ye@duke.edu
Abstract
Multi-agent large language model (LLM) systems are increasingly adopted for
complex language processing tasks that require communication and coordination
among agents. However, these systems often suffer substantial overhead from
repeated reprocessing of overlapping contexts across agents. In typical pipelines,
once an agent receives a message from its predecessor, the full context-including
prior turns-must be reprocessed from scratch, leading to inefficient processing.
While key-value (KV) caching is an effective solution for avoiding redundant
computation in single-agent settings where prefixes remain unchanged, it cannot
be directly reused in multi-agent scenarios due to diverging prefixes introduced by
agent-specific context extensions. We identify that the core challenge lies in the
offset variance of KV-caches across agents. To address this, we propose KVCOMM,
a training-free framework that enables efficient prefilling in multi-agent inference
by reusing KV-caches and aligning cache offsets of overlapping contexts under
diverse prefix contexts. KVCOMM estimates and adjusts KV-caches for shared
content by referencing a pool of cached examples—termed anchors—that store
observed cache deviations under varying prefixes. The anchor pool is maintained
and updated online, allowing dynamic adaptation to distinct user requests and
context structures. KVCOMM achieves over 70% reuse rate across diverse multi-
agent workloads, including retrieval-augmented generation, math reasoning, and
collaborative coding tasks, all without quality degradation. Particularly, when each
fully-connected agent receives 1K input tokens with 512 prefix tokens and 512
output tokens under a five-agent setting, KVCOMM achieves up to 7.8× speedup
compared to the standard prefill pipeline, reducing TTFT from ∼430ms to ∼55ms.
Code is available at https://github.com/FastMAS/KVCOMM.
1 Introduction
Large Language Models (LLMs) such as GPT-4o [1] and Llama-3 [11] have triggered a surge of
interest in collaborative multi-agent systems, where several specialized agents exchange messages to
collaboratively solve complex tasks such as retrieval-augmented question answering, mathematical
reasoning, and tool-augmented program synthesis [63, 9, 51, 38, 49, 60, 54, 18]. In these settings,
every message processed by LLM agents must first go through the prefill stage prior to decoding,
during which the model encodes the full conversation history and constructs key–value (KV) caches.
Although multiple agents often share overlapping context (e.g., retrieved passages or peer outputs),
they always redundantly recompute KV-caches for all input tokens, resulting in significant inefficiency
of prefilling computation [27, 56, 30], which is defined as a multi-context redundancy issue in the
39th Conference on Neural Information Processing Systems (NeurIPS 2025).
5202
voN
1
]AM.sc[
2v27821.0152:viXra

## Page 2

12
9
6
3
0
0 5 10 15 20 25 30
Layer
tesffo
yeK
2.4
1.8
1.2
0.6
0.0
tesffo
eulaV
16
12
8
4
K
V
0
0 5 10 15 20 25 30
Layer
(a)
tesffo
yeK
K1 w/ rot K1 w/o rot V1 4
K2 w/ rot K2 w/o rot V2
3
2
1
0
tesffo
eulaV
(b)
Figure 1: (a) Mean KV-cache offset (measured by ℓ norm) from the base-context cache for the same token
2
across ten distinct prefixes. Shaded regions indicate standard deviation across these prefixes. (b) KV-cache
offset comparison between two embedding-similar tokens from the base-context caches when both tokens are
prefixed with a new context. “∆K1 w/ rot” and “∆K2 w/ rot” represent Key offsets of two tokens with position
alignment, respectively. “∆K1 w/o rot” and “∆K2 w/o rot” refer to Key offsets without alignment. “∆V 1”
and “∆V 2” denote Value offsets of two tokens.
multi-agent system. For example, a single 8B Llama needs ∼430 ms to prefill a 3K-token prompt
on one H100 GPU. If each of M agents receives messages from all of its peers, the total prefilling
complexity of these repeated computations scales as O(M 2), posing inefficiency in the utilization of
computation and a major challenge for real-time multi-agent collaboration.
Recent works attempt to reduce prefilling overhead primarily through four techniques: prompt-level
reuse [10], selective recomputation [58, 27, 56], cache compression [28], kernel-level optimiza-
tions [67, 46]. While effective in their target scenarios, these methods share a fixed acceleration
policy crafted for a particular workload. However, our empirical study reveals that the same shared
text can incur vastly different KV deviations once it is preceded by different prefix contexts, e.g.,
system messages with different roles or upstream agents with different output lengths (see Figure 1a).
When the acceleration policy fails to model such an offset-variance problem, cache reuse becomes
misaligned, causing either large accuracy drops or a fallback to full recomputation that erodes the
speed benefits.
This observation motivates a prompt-adaptive paradigm that (i) dynamically determines how to
reuse KV-caches at runtime for each incoming prompt given diverse prefix contexts, and (ii) requires
no additional training, profiling, or model modifications, allowing easy adoption on various tasks and
agent workloads. To our knowledge, no existing method simultaneously satisfies both desiderata.
In this paper, we introduce training-free online KV-cache communication (KVCOMM), a drop-in
framework that accelerates multi-agent systems through shared-context reuse with adaptive KV
offsetting. The key insight is to treat every reuse attempt as an approximate translation problem,
where the KV-cache of overlapping text becomes reusable for a new prefix once the positional shift
and cache offsets from similar samples are identified. As illustrated in Figure 1b, the KV-cache
offsets of two similar tokens prefixed with two different prompts present similar distributions across
layers, where the deviation of the rotated Key cache is significantly smaller than the unrotated
one. Therefore, KVCOMM proposes an anchor pool of previously shared samples along with their
measured offsets under diverse prefixes. At inference time, the framework first locates the nearest
anchor(s) for the requested segment via token similarity (Anchor Matching) and then predicts the
offset by interpolating their stored deviations, avoiding a replay through the prefilling stage (Offset
Approximation). For the Key cache update, the cache will first be encoded to the correct position
and then biased by the estimated offset, while for the Value cache update, since it has no positional
information, the offset is directly added to the cache. Meanwhile, the anchor pool is updated online to
catch up with the new input distribution. That is, once the cache of an input segment is predicted as
unshareable, it will be marked as an anchor and measure the cache offset under each prefix to extend
the reusing range for the subsequent input samples. For the least matched anchors, they would be
periodically freed up to save memory consumption and computation cost.
In summary, KVCOMM represents a substantial advancement in adaptively efficient KV-cache sharing
in the LLM-based multi-agent system without training or recomputation, offering a practical path
toward efficient agent communication. The main contribution is threefold:
• We identify the multi-context redundancy as a key challenge for efficient prefilling in the
multi-agent scenario, and characterize the offset-variance problem that limits traditional KV
sharing in such a setting, which to our knowledge, has not been covered by prior work.
• We propose KVCOMM, the first training-free, prompt-adaptive cache-sharing framework
for efficient prefilling of multi-agent systems, requiring only a few anchors to effectively
2

## Page 3

K C V o o n f t e P x r t e 1 fix T K e V xt o in f S A h g a e r n e t d 1 K C V o o n f t e P x r t e 2 fix KV f S r o h in m a A r A e g d g e e n T n e t t x 2 1 t of K 1 V t T o e O 2 x f t f f s f o r e r o t m R o e f A q S g u h e e a n s r t t e 1 d A A g S p e p h n r a t o r 1 x e i f d m o T r a e R te x e d t q f K r u o V e m s o t f 2
Request 1: Prefix Context 1 Text 1
Try to prove 1 x 1 =
1.
Agent 1
Send
Message Prefix Context 2 Text 1 from Agent 1
Agent 2
Request 2: Prefix Context 1 Text 2
Find a way to prove
1 + 1 = 2.
Agent 1
Send
Message Prefix Context 2 Text 2 from Agent 1
Agent 2
Decoding Flow
Prefill Flow Original: No Cache Reuse S P e ri l o e r c : t i C ve a c R h e e c R om eu p s u e ta w tio ith n KVC C O a M c M he : C O o ff n s t e e t x ti t n -a g ware
KVCOMM Flow
Figure 2: Comparisons with existing KV-cache reuse methods. (Left) The original no-cache-reuse baseline
method densely prefills the tokens of all requests. (Middle) Selective recomputation methods [58, 27] select
the most critical part of KV-cache for recomputation and reuse the remaining cache of each request. (Right)
KVCOMM reuses all KV-caches of the shared context and introduces context-aware cache offsets to align with
different prefix contexts, where the context-aware offset refers to the KV-cache deviation induced by the changed
prefix context. Such an offset is approximated by the ground-truth ones of previous similar requests. After
approximation, the model runner directly starts decoding without prefill.
approximate KV-cache offsets across different prefix. In KVCOMM, an efficient KV-cache
management system is designed to support fast anchor lookup.
• Extensive experiments on three representative tasks with different models, including re-
trieval augmented generation (RAG), math reasoning, and programming, demonstrate that
KVCOMM can achieve ∼ 6.7× average prefill speed-up where each agent is deployed by
Llama-3.1-8B-instruct [11] on an NVIDIA H100 GPU. Meanwhile, as the reuse rate reaches
95% across 1,319 samples in a four-agent system for GSM8K [7], KVCOMM achieves
comparable performance to the original workload (less than 2.5% accuracy drop).
2 Related Work
2.1 LLM-Based Multi-Agent Systems
The idea of distributing a complex task across multiple specialized LLM agents has rapidly progressed,
from early frameworks such as AutoGPT [35] to mature tool-augmented systems for retrieval, coding,
and robotics [17, 26, 39, 63, 9, 48, 22, 50, 51, 62, 55, 3, 31, 52, 24, 15, 42, 19, 40, 23]. Recent
studies propose curriculum fine-tuning to promote role specialization [66], graph-structured message
routing [57, 69], and hierarchical decision making [32]. Yet practically, each agent still performs a full
prefill pass for every turn, recomputing the KV tensors over large shared contexts. As agent graphs
grow wider or deeper, the prefill complexity of these repeated computations scales quadratically,
posing inefficiency in computation utilization. Addressing the prefill bottleneck is thus a prerequisite
for scaling multi-agent LLM applications to real-time settings.
2.2 KV-cache Acceleration and Reuse
KV-cache Sharing Scenario. Prior research has identified three principal patterns for reusing the
KV-cache in transformers. (i) Multi-request sharing exploits identical prefixes across requests from
different users; by copying the KV-cache of the shared prefix, servers can bypass most of the prefill
compute when only the tail differs. (ii) Multi-turn sharing keeps the cache alive throughout the
turns of a single conversation, thus avoiding recomputation of the history. (iii) Multi-context sharing
handles inputs whose overlapping segment appears at different contexts, which aims to filter out
the impact of the prefixed prompt in the KV-cache and to combine current context information
into the reused KV-cache. Most of these techniques assume that every agent runs the same model
architecture—typically a vanilla RoPE-based decoder—so that a cached key can be translated by
a simple rotation without re-encoding [37, 47]. DroidSpeak [27] extends the sharing from the base
model to the fine-tuned one by profiling which layers remain shareable. Current industrial serving
3

## Page 4

Agent 1 KV-cache Communication Module
Prefix KV Anchor Matching Offset Approximation Anchor Prediction
Placeholder KV Pool Pool Each Anchor Unmatched Matched
{
All placeholders ? Query Hit w ( 1 1) (2 w ) 2
No Yes
P D re e f n ill s in e g C P
P
a
F
H che Update Pool Pool + = w2 +w1 Length O U R ncover Lengt A h N Co D vered
= +w1
Decoding
[
R
P
e
H
s
,
p
P
o
F
n
]
se Ca
R
c
es
h
p
e
onse
+w2
Anchor Prediction of Response KV
Agent 2 Agent 3 You are a math expert. You will be given a math Legend
problem ...Q:
Prefix KV Prefix KV A A n g s e w nt e 2 rs a f s ro a m m o a th th e e r m ag a e tic n a ts l a a n re a : lyst: , Q Pl u a e c r e ie h d o l ( d e e x r ternal input)
the execution result is . Queried (response)
Placeholder KV Placeholder KV Example Placeholder
KV Anchor of the
Estimated KV of the i-th (external input) Placeholder
All placeholders ? All placeholders ? Placeholder of Agent m Anchor Hit Range
Estimated KV of the i-th (response)
Placeholder of Agent m Add as a New Anchor
(N) Dense (Y) Sharing (Y) Sharing (N) Dense
Reuse E S s e t g im m a e t n e t d o K f V A g o e f n th t e m i-th Prefix Sharable placeholder
Figure 3: Overview of the KVCOMM framework in a three-agent scenario. Initially, each agent precomputes
and stores the KV-cache of prefix segments from its prompt template for future reuse. At runtime, upon receiving
a new request, agents check placeholder shareability and query matched anchors. Matched anchors help
approximate KV-cache offsets for placeholders and subsequent prefixes through embedding-based interpolation.
The matching criteria consider length compatibility and embedding proximity. The updated KV-caches are
concatenated for efficient decoding. After decoding, the KV-cache Communication module assesses newly
generated caches for potential sharing with other agents based on the established matching rules.
stacks [21, 68, 5] expose the same constraint that architectural identity is a prerequisite for cache
reuse.
Existing methods on KV-cache acceleration primarily explore four paradigms. (1) Prompt-Level
Reuse [10]. PromptCache [10] introduces Prompt Markup Language to explicitly define reusable text
segments whose KV-caches are precomputed offline and directly fetched at inference, eliminating
recomputation but restricted to fixed prompt structures. (2) Selective Recomputation [58, 27, 56].
CacheBlend [58] dynamically identifies and updates tokens exhibiting high variance in KV-caches.
DroidSpeak [27] leverages profiling to identify critical attention layers whose KV-caches must
be refreshed to maintain accuracy. KVLink [56] further extends it by fine-tuning special tokens
and adjusting positional embeddings, enabling KV reuse across multiple document contexts. (3)
Cache Compression [28]. CacheGen [28] compresses KV-caches into adaptive bit-streams based on
available bandwidth; however, the entire token sequence still undergoes compression computations,
limiting latency improvements. (4) Kernel-Level Optimizations [67, 46]. PrePacking [67] employs
a bin-packing strategy to batch variable-length prompts into unified sequences. LoongServe [46]
designs Elastic Sequence Parallelism to dynamically manage parallelism strategies and overlap cache
migration with decoding steps to enhance GPU utilization. Figure 2 compares the main difference
between KVCOMM and existing KV-cache sharing methods. Generally, KVCOMM explores a
completely novel paradigm that can reuse all shareable KV-caches regardless of diverse prefix
contexts, and align them by leveraging the context-aware cache offsets observed in previous samples.
3 Proposed Approach
3.1 Preliminaries
Large Language Models and KV-cache. Let x = [h1, . . . , hL] denote a list of token embedding
sequences, with hl ∈ RN×D representing the input token embedding of the l-th transformer layer,
where N is the number of tokens and D is the feature dimension. For hl (where n = 1, 2, . . . , N ),
n
it is projected by the l-th transformer layer to Query, Key, and Value vectors for the subsequent
attention computation using: ql = R W l hl , kl = R W l hl , vl = W l hl , where ql , kl , vl ∈
n n Q n n n K n n V n n n n
Rd denotes the Q, K, V values for the n-th input token, W l , W l , W l refer to the corresponding
Q K V
projection weight matrices, and R is the position embedding at position n, such as rotary position
n
embedding (RoPE) [37]. During autoregressive decoding, the model repeatedly attends to all past
positions, and stores every (kl , vl ) pair in GPU memory, known as KV-cache. Therefore, prefilling
n n
a prompt of N tokens costs O(N 2d) multiply-adds per layer, dominating inference latency for long
contexts. Since RoPE applies the fixed rotation matrix to both Key and Query at each position, cached
4

## Page 5

keys remain valid across subsequent steps with no further arithmetic modification, making KV-cache
reuse the primary source of speed-ups in subsequent prefilling and decoding.
Directed-Graph Multi-agent Systems. Following [57, 69, 65], we model a multi-agent system
as a directed graph G = (M, E) whose nodes m ∈ M are agents and edges e = (m → m ) ∈ E
s t
denote one-way message passing from the m -th agent to the m -th agent. At interaction step t, the
s t
m-th agent composes an input prompt s(t) in the template consisting of (i) fixed prefix segments
m
shared across all turns, and (ii) placeholder segments filled at runtime with user queries, tool results,
or upstream agent outputs, as formulated as follows, where p is usually a role-specific system
(m,0)
prompt, p is the subsequent prefix segment of the i-th placeholder ϕ(t) .
(m,i) (m,i)
s(t) = (cid:2) p , ϕ(t) , p , ϕ(t) , p , . . . , ϕ(t) , p (cid:3) . (1)
m (m,0) (m,1) (m,1) (m,2) (m,2) (m,i) (m,i)
Our work targets a distinct yet practical setting: a directed multi-agent graph in which each node is
an identical RoPE-based LLM checkpoint instantiated with a role-specific system template. Since
agents differ in the length of both prefixes and incoming messages, none of the existing static policies
can predict the correct positional and contextual shifts; misalignment either forces full recomputation
or yields steep accuracy loss. We therefore develop a training-free, prompt-adaptive cache-sharing
mechanism, termed KVCOMM, which estimates the true offset on the fly and maintains an online
anchor pool to accommodate rapidly changing interaction patterns, reducing prefilling latency without
sacrificing task performance. The overall workload of KVCOMM is illustrated in Figure 3, which
proceeds as follows.
0. Initialization Before any user requests, all agents precompute and store the KV-caches for
all prefix segments defined in their prompt templates.
1. Placeholder Readiness When a request arrives, each agent checks whether all placeholders’
base KV-caches are available. Missing bases are precomputed in parallel. Newly generated
placeholder KV-caches are then sent to the anchor prediction module to search the anchor pool
for similar samples and enable reuse.
2. Reuse or Fallback Once all placeholder KV-caches are ready, the agent determines whether
reusable KV-cache deviations exist for each placeholder. If none are found, standard dense pre-
filling is used. For placeholders without reusable deviations, the agent computes the difference
between their actual and base KV-caches and stores this deviation in the anchor pool to expand
anchor coverage.
3. Offset Approximation If all placeholders have reusable deviations, the agent fetches the
matched anchors, estimates the KV-cache deviations via Eq. (6) and Eq. (7), and updates the
placeholder and prefix KV-caches in parallel.
4. Decoding The agent concatenates the updated placeholder and prefix KV-caches and initiates
response decoding.
5. Anchor Update After decoding, the produced KV-cache is passed through the anchor
prediction module. If a similar anchor exists, the cache is stored in shared memory for future
retrieval. The agent then waits for the next request.
6. Fallback Storage If no similar anchor exists, the response KV-cache is stored in the anchor
pool so dependent agents can subsequently fill in deviations under their respective contexts; the
agent then awaits the next request.
All inter-agent interactions occur through the KV-cache Communication Module. When multiple
agents share the same user text but use different agent-specific prefixes, we avoid re-running
prefilling by treating the KV-cache of the shared text under a new prefix as a context-dependent
offset from its base KV-cache. We estimate this offset by interpolating from a small set of
anchor examples, aligning Key positions via RoPE de-rotation/re-rotation, adding the estimated
Key/Value offsets, then concatenating the adjusted segments and decoding.
Positional Alignment is Indispensable. Before analyzing two arbitrary tokens’ cache correlation,
we should first solve the position mismatch induced by RoPE. If a token is at position n in one prompt
but at n + ∆ in another, the raw keys differ by an orthogonal rotation R , whose difference can be
∆
orders of magnitude larger than the contextual deviation we care about, as demonstrated in Figure 1b.
Hence, KVCOMM always de-rotates the stored key by R
−∆
before measuring similarity between
5

## Page 6

40
30
20
10
0
0 5 10 15 20 25 30
Layer
ecnatsiD
yeK
Knear Kmid Kfar 20
Vnear Vmid Vfar
15
10
5
0
ecnatsiD
eulaV
1
0.75
0.50
0.25
0 5 10 15 20 25 30
Layer
(a)
namraepS
Key Value
(b)
30
22
15
7
0
0 5 10 15 20 25 30
Layer
ecnatsiD
yeK
Knear Kmid Kfar 10
Vnear Vmid Vfar 7
5
2
0
ecnatsiD
eulaV
1
0.75
0.50
0.25
0
0 5 10 15 20 25 30
Layer
(c)
namraepS
K V
(d)
Figure 4: (a)(b) KV-cache proximity experiments for token pairs sharing identical prefixes: (a) shows the
KV-cache distances (measured by ℓ norm) across layers of the token pairs, which are grouped into “near”,
2
“mid”, and “far” by embedding distance between the two tokens in the token pairs. (b) shows the Spearman [36]
correlation between embedding distances and KV-cache proximity across layers. (c)(d) KV-cache offset
proximity experiments for token pairs prefixed by two distinct contexts: (c) shows the layer-wise KV-cache
offset distances between tokens grouped by embedding proximity. (d) shows the Spearman correlation between
embedding distance and KV-cache offset proximity. Experimental details are shown in Appendix 6.3.1.
Key cache offsets of two tokens under the same context change. The following analysis assumes this
alignment as completed so that the remaining deviations stem mainly from token identity and context.
3.2 Token-level Key/Value Similarity for KV Reuse
Motivation. KVCOMM hinges on the empirical observation that per-token KV vectors remain
remarkably similar across distinct conversational contexts as long as the model parameters are shared.
Intuitively, the residual pathway in every Transformer block keeps a copy of the input representation
and adds the attention (Attn) and feed-forward (FFN) refinements:
hl+1 = hl + FFNl(cid:0) hl + Attnl(hl) (cid:1) , (2)
n n n n
where FFNl and Attnl refer to the FFN and Attn modules in the l-th layer. Hence, the identity
information carried by the original embedding h1 is never overwritten but accumulates across layers,
n
suppressing the variation of the projected keys/values. Below we make this insight precise and
quantify how far two distinct tokens are when prefixed with the same contexts.
Proposition 1 (KV-Distance Between Different Tokens). Let kl and k˜l be the key vectors of two
n n
different tokens at position n at layer l that are prefixed with the same token sequence. Assume Attnl
is αl-Lipschitz, FFNl is βl-Lipschitz [20]. Define σl ≜ βl(1 + nαl). Then
(cid:13) (cid:13)kl n − k˜l n (cid:13) (cid:13) ≤ C R C K l (cid:81) j l = − 1 1(cid:0) 1 + σj(cid:1) δ n , δ n = max k≤n (cid:13) (cid:13)h1 k − h˜1 k (cid:13) (cid:13), (3)
where C > 0 is related to RoPE and Cl > 0 is related to l-th layer projection key matrix W l .
R K K
Similarly, the inequality also holds for the value caches of the two tokens.
The proof is deferred to Appendix 6.2.2. It can be observed that Eq. (3) bounds the KV distance by
the embedding gap scaled through layers, so tokens that start closer in embedding space have tighter
bounds and greater cache-reuse potential. Figure 4a and 4b empirically demonstrate this insight,
where the KV-caches of “near” token pairs are consistently closer to each other than the other two
groups, and the KV-cache proximity is highly correlated to the token embedding distance.
We now examine this relation in multi-agent settings, where two similar tokens face different prefixes.
Proposition 2 (Deviation Proximity With Different Prefixes). Let kl and k˜l be the key vectors of
two different tokens at position n at layer l that are prefixed with pro n m a pt p . n S a imilarly, k¯l and k ˜¯l
a a nb nb
are the key vectors of the two tokens at position n at layer l that are prefixed with prompt p . We
b b
denote the key cache deviation of each token at layer l by ∆l = k¯l − kl , ∆˜ l = k ˜¯l − k˜l . Under
nb na nb na
the same Lipschitz assumptions as Proposition 1 and after positional alignment,
∥∆l − ∆˜ l∥ ≤ 2 C
R
C
K
l (cid:81)l
j
−
=
1
1
(1 + σj)δ
na
, δ
na
= max
k≤na
(cid:13) (cid:13)h1
k
− h˜1
k
(cid:13) (cid:13). (4)
Similarly, the inequality also holds for the value caches of the two tokens.
6

## Page 7

Proof is in Appendix 6.2.2. Eq. (4) shows that tighter embedding gaps again yield smaller deviation
bounds, supporting cross-context offset reuse. Figs. 4c and 4d validate this under the same setup as
Figure 4a, with each token evaluated under two distinct prefixes, where the KV-cache offsets of “near”
token pairs are also consistently closer to each other than the other two groups, and the KV-cache
offset proximity is also highly correlated to the token embedding distance.
The above propositions motivate an anchor-based KV-sharing scheme that stores representative offsets
as reusable anchors for future agent interactions to reduce all redundant prefilling latency of agents.
3.3 Anchor-based KV-cache Communication
We now introduce our anchor-based communication framework to unify the KV-cache sharing
mechanism in multi-agent systems. During setup, each agent extracts placeholder information
from its role-specific prompt into a structured dictionary, indicating token positions. The naming
conventions for placeholders are detailed in Appendix 6.2.3. Each placeholder initializes an individual
anchor pool upon receiving the first sample.
At runtime, subsequent input samples trigger a reuse check across agent placeholders. Agents reuse
KV-caches directly from corresponding anchor pools if reuse conditions are satisfied, significantly
speeding up inference by skipping redundant prefilling. Otherwise, agents revert to standard prefilling,
updating anchor pools with newly computed KV-caches to enrich future reuse opportunities.
Anchor Pool Design. An anchor pool stores key information for each placeholder sample: (1)
the base KV-cache, computed independently without external contexts; (2) offsets between the base
and actual KV-caches within each agent’s context; and (3) offsets of subsequent neighboring prefix
segment’s KV-cache. Thus, an anchor is represented as {ph_name: base KV, agent_id_ph:
placeholder offset, agent_id_pf: prefix offset}. Neighboring prefix offsets are
crucial due to position-dependent KV-cache shifts introduced by the placeholder’s context changes, as
highlighted by the sink attention mechanism [53], which emphasizes local contextual dependencies.
Anchor Prediction. Determining whether newly-generated KV-caches, e.g., responses, user inputs,
etc., could be shared or treated as new anchors involves evaluating the embedding-based proximity [61,
29, 64, 59] and token length compatibility with existing anchors. The prediction criterion is designed
as follows:
(cid:80)
P (ϕ) = (L > max L ) ∪ (H > γ log |A |), H = w log w , (5)
anchor ϕ ψ∈A ψ ϕ|A ϕ ϕ|A ψ∈Aϕ ϕ→ψ ϕ→ψ
where A refers to the anchor pool that the placeholder ϕ belongs to, ψ denotes an anchor in A, L
⋆
represents the sequence length of the sample ⋆, H measures entropy of the embedding-distance-
ϕ|A
based weights among longer anchors in the anchor pool, w = softmax(−∥h −h ∥), ψ ∈ A ,
ϕ→ψ ϕ ψ ϕ
|A | refers to the number of anchors longer than ϕ in |A|, and γ is a threshold to determine how far a
ϕ
shareable sample could be away from the anchors of A in the embedding space. Intuitively, anchors
closer in embedding space yield more reliable offset predictions (validated by Prop. 2 and Figure 4c),
and length compatibility ensures correct positional alignment (see Figure 1b).
Anchor Update. When KV-cache sharing criteria are unmet, the newly-generated cache becomes
a new anchor’s base KV-cache. Agents relying on this unshareable placeholder revert to regular
prefilling, providing agent-specific offsets for both the placeholder and its neighboring prefix segments
to populate the new anchor entry. Due to GPU memory constraints, we implement an adaptive anchor
pruning strategy: once anchor pools reach a predefined size V, the least frequently accessed anchor
among the earliest-added entries is discarded, maintaining a relevant and efficient anchor repository.
3.4 Anchor-based Cache Update
When placeholders in an agent’s prompt are predicted shareable, we efficiently update their KV-caches
via anchor matching and offset approximation.
Anchor Matching. We retrieve reliable anchors identified during prediction, performing parallel
reads due to independent addressing, leading to negligible overhead compared to traditional prefilling.
Offset Approximation. Using matched anchors, we approximate placeholders’ KV-caches within
agent-specific contexts. Neighboring prefix segments are updated similarly based on the placeholder
7

## Page 8

Table 1: Performance of three cache-management strategies under different numbers of collaborating
agents. Accuracy is reported for MMLU and GSM8K (Llama-3.1-8B-Instruct); Pass@1 is reported
for HumanEval (Qwen-2.5-coder-7B). Higher is better. In addition, the Reuse Rate is reported for both
KVCOMM and CacheBlend. Note that the Reuse Rate for CacheBlend is defined as the proportion of
tokens reusing KV-caches in whole token sequences, while the Reuse Rate of KVCOMM is defined
as the frequency of agents reusing all KV-caches in the whole serving procedure.
# Agents
Dataset Metric Method
2 3 4 5
Original 47.1 66.7 68.0 69.9
Accuracy (%) CacheBlend 65.4 65.4 65.4 67.3
MMLU KVCOMM 64.7 68.6 68.0 69.9
Original 0 0 0 0
Reuse Rate (%) CacheBlend 80 80 80 80
KVCOMM 74.5 69.9 70.1 67.6
Original 81.1 82.4 82.1 81.7
Accuracy (%) CacheBlend 82.0 75.1 65.1 57.1
GSM8K KVCOMM 81.5 81.7 80.6 79.6
Original 0 0 0 0
Reuse Rate (%) CacheBlend 80 80 80 80
KVCOMM 79.6 77.0 73.4 71.0
Original 86.3 83.9 84.5 85.1
Pass@1 (%) CacheBlend 31.1 21.1 30.4 32.9
HumanEval KVCOMM 81.4 83.2 83.2 83.2
Original 0 0 0 0
Reuse Rate (%) CacheBlend 80 80 80 80
KVCOMM 87.6 84.7 81.1 77.8
sample’s embedding proximity. Formally, the KV-cache of the i-th placeholder in the m-th agent is
approximated as follows:
(kˆ/vˆ) = (k/v) + (cid:80) w · ∆(k/v)ϕ , (6)
ϕ(m,i) ϕ(m,i) ψ∈Aϕ(m,i) ϕ(m,i)→ψ (m,ψ)
where (kˆ/vˆ) refers to the approximated K/V cache for the placeholder ϕ . (k/v) is the
ϕ(m,i) (m,i) ϕ(m,i)
base K/V cache for the placeholder ϕ . w is the softmax mapping of −∥h − h ∥
across the anchor dimension. ∆(k/v ( ) m ϕ ,i) i ϕ s (m th , e i)→ pl ψ aceholder ϕ’s cache offsets in the m ϕ -t ( h m, a i) gent f ψ or
(m,ψ)
the anchor ψ. Prefix segment updates follow an analogous process:
(kˆ/vˆ) = (k/v) + (cid:80) w · ∆(k/v)p , (7)
p(m,i) p(m,i) ψ∈Aϕ(m,i) ϕ(m,i)→ψ (m,ψ)
where (kˆ/vˆ) refers to the approximated K/V cache for the prefix segment p . (k/v)
is the base K p / ( V m,i c ) ache for the prefix segment p . ∆(k/v)p is the corr ( e m s , p i) onding p p r ( e m fi ,i x )
(m,i) (m,ψ)
segment’s cache offset in the m-th agent for the anchor ψ.
After approximation, updated caches are concatenated and directly fed into decoding, substantially
reducing prefilling latency via parallel processing. The overall algorithm is listed in Appendix 6.2.5.
4 Experiments
4.1 Experimental Setup
Multi-agent System. Following GPTSwarm [69] and AgentPrune [65], we construct a fully-
connected multi-agent system with established techniques including few-shot prompting [2], chain-
of-thought [45], function calling [33], and structured outputs [34]. To precisely analyze KV-cache
behaviors, we deploy open-source models using HuggingFace’s framework rather than closed-source
APIs used by AgentPrune. Specifically, we employ Llama-3.1-8B-Instruct [11] (Llama-3.1) for
retrieval-augmented generation (RAG) and math reasoning, and Qwen-Coder-2.5-7B-Instruct [16]
for programming tasks. We evaluate performance across scenarios ranging from two to five agents.
Benchmark Datasets. We assess RAG performance using MMLU [13], math reasoning with
GSM8K [7], and programming capability via HumanEval [4].
8

## Page 9

Table 2: Per-agent TTFT breakdown and speedup. Table 3: Mean TTFT speedup using Llama-3.1.
(Prefix token length per agent: 512; Output token (#Agents = 3)
length: 512; Model: Llama-3.1; #Agents = 5)
In_len (Prefix sequence)
Out_len
TTFT (ms) Agent 1 Agent 2 Agent 3 Agent 4 Agent 5 64 128 256 512 1024
Original 125.8 192.4 258.3 330.9 428.6
128 2.24x 2.31x 2.56x 3.07x 4.45x
1 K st V T C ok O e M n M Decode 2 5 1 .5 .4 2 7 1 . . 7 2 2 1 1 0 . . 2 2 1 2 3 1 . . 5 3 1 2 7 1 . . 5 1 256 2.50x 2.51x 2.83x 3.44x 4.75x
Others 86.6 9.1 10.7 13.5 16.2 512 3.05x 3.18x 3.49x 4.09x 5.34x
1024 4.40x 4.48x 4.75x 5.35x 6.72x
Speedup 1.11x 5.06x 6.14x 6.85x 7.82x
Comparison Baselines. To our knowledge, KVCOMM is the first method enabling comprehensive
KV-cache sharing tailored for open-source multi-agent frameworks. Hence, we compare primarily
against CacheBlend [58], which selectively recomputes sensitive tokens’ caches for partial reuse.
Given CacheBlend’s tight integration with vLLM [21], we faithfully replicate its selective recomputa-
tion strategy within our experimental setup, consistently recomputing the top-20% tokens exhibiting
the largest KV deviations, ensuring fair baseline alignment.
Evaluation Metrics. We report Accuracy scores on MMLU and GSM8K, and Pass@1 for coding
tasks. Efficiency metrics include Reuse Rate (meaning the proportion of agents employing the cache
reuse scheme), individual agent Time-To-First-Token (TTFT), and average TTFT across agents.
Implementation Details. Experiments are executed on a single NVIDIA H100 GPU. The maximum
generation length is uniformly set to 512 tokens, with hyperparameters selected as γ = 0.3 and
anchor pool size V = 20. Further implementation specifics are detailed in Appendix 6.3.
4.2 Main Results
Table 1 compares our KVCOMM approach with the Original (no cache reuse) and CacheBlend [58]
strategies across multiple agent configurations. Although our agent prompts were initially opti-
mized for closed-source models, causing some performance drops with open-source deployments,
KVCOMM still maintains or improves upon baseline accuracy.
On MMLU, KVCOMM achieves competitive accuracy (64.7%–69.9%), consistently outperforming or
matching CacheBlend and closely tracking the original baseline. This indicates robust cross-context
KV-cache alignment by KVCOMM, CacheBlend fluctuates significantly with increasing agents. The
reason why the baseline method performs poorly on the MMLU benchmark under the two-agent
setting is that the first agent is designed as the knowledgeable expert to produce the related key words
about the user question, and the second agent is designed as the Final Refer to analyze the predecessor
agents’ output and give the answer based on the previous agent’s output, where the failure cases
mainly occur when the second agent only output the answer without analysis. The prompt of each
agent can be found in Appendix 6.3.2.
For GSM8K math reasoning, KVCOMM’s accuracy remains stable, only declining by 1.9%
(81.5%→79.6%) from two to five agents, maintaining within ±2% of the original baseline. In
contrast, CacheBlend’s accuracy drops dramatically from 82.0% to 57.1%, highlighting the necessity
for precise KV-cache reuse in numerical tasks.
In the HumanEval coding benchmark, KVCOMM delivers stable Pass@1 scores (81.4%–83.2%),
significantly surpassing CacheBlend by an average margin of 53%. This underscores KVCOMM’s
ability to preserve task-critical dependencies essential for programming tasks. The severe performance
degradation of CacheBlend on Humaneval attributes to the diverse syntax separators involved in the
generation process (e.g., ., ;, !), which induce diverse and prefix-sensitive KV-cache distributions.
Reuse Rate. Unlike CacheBlend’s fixed reuse strategy (80%), KVCOMM adaptively determines
KV-cache reuse, consistently achieving high reuse rates (70%–87.6%). This rate naturally declines
as agent number increases due to more diverse contexts, but KVCOMM still effectively identifies
shareable caches, confirming that adaptive reuse avoids context degradation.
4.3 Results of TTFT Speedup1
Table 2 reports TTFT per agent receiving 1K tokens from user input with 512 prefix tokens and
sharing the 512 response tokens with succeeding agents. The first agent, lacking upstream caches
1In the original submission, the TTFT calculation for KVCOMM omitted the first token’s decoding latency.
The final version rectifies this.
9

## Page 10

(costing 86.6ms in “other” operations), shows modest acceleration (1.11×). Subsequent agents reduce
prefilling dramatically to 26.9–38.6 ms via KVCOMM, achieving up to 7.82× speedup (Agent 5).
Scalability in Context Length. We further examine scalability in Table 3, varying prefix (64–1K
tokens) and output lengths (128–1K tokens) among three collaborating agents. KVCOMM achieves a
minimum mean speedup of 2.24× (shortest setting) and scales effectively to 6.72× (longest setting),
validating the approach’s efficiency gain as context length and complexity increase.
4.4 Discussion and Ablation Study
Robustness to Request Order. Table 4 Table 4: Study on the robustness to varying request
examines how request ordering affects KV- orders. Accuracy is reported. (#Agent = 4, Baseline
COMM’s cache alignment using MMLU. Acc = 68.0%; Model: Llama3.1)
We test two random orders (Rand-1, Rand-
Method Rand-1 Rand-2 Ascending Descending
2), ascending and descending length orders.
It can be observed that performance is cor- KVCOMM 68.0 72.5 67.3 66.0
related with request order due to the designed anchor prediction criterion. Results confirm KV-
COMM is robust across diverse ordering strategies, achieving consistent or slightly improved accuracy
compared to the baseline, demonstrating minimal sensitivity to request sequence variability.
Contribution of Each Alignment Step. Table 5: Ablation study on MMLU under four-agent
Table 5 details ablation results for three setting. (Model: Llama-3.1)
alignment components on MMLU under a
k w/ rot ϕ w/ offset p w/ offset Acc (%)
four-agent setting: (1) position alignment
via key rotation, (2) placeholder KV-cache ✓ 43.1%
offset, and (3) prefix segment KV-cache off- ✓ 58.8%
✓ 60.1%
set. The results reveal that each alignment
✓ ✓ 38.6%
step is critical; omitting any severely de-
✓ ✓ 62.1%
grades accuracy. Although combining key
✓ ✓ 56.9%
rotation and prefix offset achieves 62.1%
accuracy, the response of each agent is visi- ✓ ✓ ✓ 68.0%
bly less coherent with the original one (See
Appendix 6.4.6). Therefore, complete alignment is essential for robust cross-context performance.
Sensitivity to Hyperparameters. Ta- Table 6: Hyperparameter analysis on GSM8K under the
ble 6 explores KVCOMM’s sensitivity to four-agent setting using Llama-3.1.
the entropy threshold γ and anchor pool
size V using GSM8K with four agents. Threshold γ (V = 20)
γ = 0 / V = 0 refers to the original no- Metric 0 0.1 0.3 0.5 0.7 0.9
cache-sharing method. It can be observed
Accuracy (%) 82.1 83.1 80.6 80.0 78.9 78.8
that with conservative reuse (γ = 0.1), ac-
Reuse rate (%) N/A 34.3 73.4 94.9 97.5 98.2
curacy improves slightly (1%), while mod-
Maximum Anchor Num V (γ = 0.3)
erate relaxation significantly boosts reuse
Metric
(up to 98.2%) at minimal accuracy cost 0 5 10 15 20 25
(3.3%). For V, performance is relatively Accuracy (%) 82.1 82.0 81.4 81.2 80.6 80.6
stable with the increase of stored anchors, Reuse rate (%) N/A 44.0 60.3 66.2 73.4 73.4
while the reuse rate finally becomes stable
at 73.4%, indicating that V = 20 effectively balances efficiency and task performance.
5 Conclusion
In this paper, we explore KV-cache sharing for efficient communication in collaborative LLM-based
MAS and introduce KVCOMM, a drop-in framework to enable efficient agent communication through
shared KV-cache reuse and context-aware cache offsetting. Besides, we perform analyses of KV-cache
deviation across varying prefix contexts, and propose an anchor-based offset estimator to effectively
align and reuse shared context KV-caches. Extensive experiments conducted on Retrieval-Augmented
Generation (RAG), Math Reasoning, and Programming-related multi-agent systems demonstrate
that our method provides an effective trade-off between prefilling efficiency and system accuracy,
continuously reducing average latency as the number of agents increases. Specifically, KVCOMM can
achieve ∼6.7× average prefilling speedup under the three-agent setting on a single H100 GPU,
significantly improving the deployment efficiency of collaborative multi-agent language models.
10

## Page 11

Acknowledgments
Hancheng Ye, Jianyi Zhang, and Yiran Chen disclose the support from NSF 2112562, ARO W911NF-
23-2-0224, and NAIRR Pilot project NAIRR240270. Danyang Zhuo discloses the support from
NSF 2503010. We sincerely thank the program chairs, area chair, and reviewers for their valuable
comments.
References
[1] Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman,
Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, et al. Gpt-4 technical report. arXiv
preprint arXiv:2303.08774, 2023.
[2] Tom Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared D Kaplan, Prafulla Dhariwal, Arvind
Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, et al. Language models are few-shot learners.
Advances in neural information processing systems, 33:1877–1901, 2020.
[3] Chen-Chia Chang, Chia-Tung Ho, Yaguang Li, Yiran Chen, and Haoxing Ren. Drc-coder: Automated drc
checker code generation using llm autonomous agent. In Proceedings of the 2025 International Symposium
on Physical Design, pages 143–151, 2025.
[4] Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde de Oliveira Pinto, Jared Kaplan,
Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, Alex Ray, Raul Puri, Gretchen Krueger,
Michael Petrov, Heidy Khlaaf, Girish Sastry, Pamela Mishkin, Brooke Chan, Scott Gray, Nick Ryder,
Mikhail Pavlov, Alethea Power, Lukasz Kaiser, Mohammad Bavarian, Clemens Winter, Philippe Tillet,
Felipe Petroski Such, Dave Cummings, Matthias Plappert, Fotios Chantzis, Elizabeth Barnes, Ariel Herbert-
Voss, William Hebgen Guss, Alex Nichol, Alex Paino, Nikolas Tezak, Jie Tang, Igor Babuschkin, Suchir
Balaji, Shantanu Jain, William Saunders, Christopher Hesse, Andrew N. Carr, Jan Leike, Josh Achiam,
Vedant Misra, Evan Morikawa, Alec Radford, Matthew Knight, Miles Brundage, Mira Murati, Katie Mayer,
Peter Welinder, Bob McGrew, Dario Amodei, Sam McCandlish, Ilya Sutskever, and Wojciech Zaremba.
Evaluating large language models trained on code. 2021.
[5] Yihua Cheng, Yuhan Liu, Jiayi Yao, Yuwei An, Xiaokun Chen, Shaoting Feng, Yuyang Huang, Samuel
Shen, Kuntai Du, and Junchen Jiang. Lmcache: An efficient kv cache layer for enterprise-scale llm
inference. arXiv preprint arXiv:2510.09665, 2025.
[6] ChuGyouk. Aime-22-25. Hugging Face Dataset, 2025. https://huggingface.co/datasets/
ChuGyouk/AIME-22-25.
[7] Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias
Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, Christopher Hesse, and John Schulman. Training
verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021.
[8] Yuzhe Fu, Changchun Zhou, Tianling Huang, Eryi Han, Yifan He, and Hailong Jiao. Softact: A high-
precision softmax architecture for transformers supporting nonlinear functions. IEEE Transactions on
Circuits and Systems for Video Technology, 34(9):8912–8923, 2024.
[9] Yingqiang Ge, Wenyue Hua, Kai Mei, Jianchao Ji, Juntao Tan, Shuyuan Xu, Zelong Li, and Yongfeng
Zhang. Openagi: When llm meets domain experts. In Advances in Neural Information Processing Systems
(NeurIPS), 2023.
[10] In Gim, Guojun Chen, Seung-seob Lee, Nikhil Sarda, Anurag Khandelwal, and Lin Zhong. Prompt
cache: Modular attention reuse for low-latency inference. Proceedings of Machine Learning and Systems,
6:325–338, 2024.
[11] Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-
Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Alex Vaughan, et al. The llama 3 herd of models.
arXiv preprint arXiv:2407.21783, 2024.
[12] Daya Guo, Dejian Yang, Haowei Zhang, Junxiao Song, Ruoyu Zhang, Runxin Xu, Qihao Zhu, Shirong
Ma, Peiyi Wang, Xiao Bi, et al. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement
learning. arXiv preprint arXiv:2501.12948, 2025.
[13] Dan Hendrycks, Collin Burns, Steven Basart, Andy Zou, Mantas Mazeika, Dawn Song, and Jacob
Steinhardt. Measuring massive multitask language understanding. In International Conference on Learning
Representations.
11

## Page 12

[14] Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul Arora, Steven Basart, Eric Tang, Dawn Song,
and Jacob Steinhardt. Measuring mathematical problem solving with the math dataset. In Thirty-fifth
Conference on Neural Information Processing Systems Datasets and Benchmarks Track (Round 2).
[15] Matthew Ho, Chen Si, Zhaoxiang Feng, Fangxu Yu, Zhijian Liu, Zhiting Hu, and Lianhui Qin. Arcmemo:
Abstract reasoning composition with lifelong llm memory. arXiv preprint arXiv:2509.04439, 2025.
[16] Binyuan Hui, Jian Yang, Zeyu Cui, Jiaxi Yang, Dayiheng Liu, Lei Zhang, Tianyu Liu, Jiajun Zhang, Bowen
Yu, Kai Dang, et al. Qwen2. 5-coder technical report. arXiv preprint arXiv:2409.12186, 2024.
[17] Chao Huang Jiabin Tang, Tianyu Fan. AutoAgent: A Fully-Automated and Zero-Code Framework for
LLM Agents, 2025.
[18] Ting Jiang, Yixiao Wang, Hancheng Ye, Zishan Shao, Jingwei Sun, Jingyang Zhang, Zekai Chen, Jianyi
Zhang, Yiran Chen, and Hai Li. Sada: Stability-guided adaptive diffusion acceleration. arXiv preprint
arXiv:2507.17135, 2025.
[19] YICHEN JIANG, SUORONG YANG, SHENGJI TANG, SHENGHE ZHENG, and JIANJIAN CAO. A
comprehensive survey of llm-driven collective intelligence: Past, present, and future. 2025.
[20] Hyunjik Kim, George Papamakarios, and Andriy Mnih. The lipschitz constant of self-attention. In
International Conference on Machine Learning, pages 5562–5571. PMLR, 2021.
[21] Woosuk Kwon, Zhuohan Li, Siyuan Zhuang, Ying Sheng, Lianmin Zheng, Cody Hao Yu, Joseph E.
Gonzalez, Hao Zhang, and Ion Stoica. Efficient memory management for large language model serving
with pagedattention. In Proceedings of the ACM SIGOPS 29th Symposium on Operating Systems Principles,
2023.
[22] Guohao Li, Hasan Abed Al Kader Hammoud, Hani Itani, Dmitrii Khizbullin, and Bernard Ghanem.
Camel: Communicative agents for "mind" exploration of large language model society. In Thirty-seventh
Conference on Neural Information Processing Systems, 2023.
[23] Yueqian Lin, Yuzhe Fu, Jingyang Zhang, Yudong Liu, Jianyi Zhang, Jingwei Sun, Hai Li, Yiran Chen,
et al. Speechprune: Context-aware token pruning for speech information retrieval. arXiv preprint
arXiv:2412.12009, 2024.
[24] Yueqian Lin, Qinsi Wang, Hancheng Ye, Yuzhe Fu, Hai Li, Yiran Chen, et al. Hippomm: Hippocampal-
inspired multimodal memory for long audiovisual event understanding. arXiv preprint arXiv:2504.10739,
2025.
[25] Aixin Liu, Bei Feng, Bin Wang, Bingxuan Wang, Bo Liu, Chenggang Zhao, Chengqi Dengr, Chong
Ruan, Damai Dai, Daya Guo, et al. Deepseek-v2: A strong, economical, and efficient mixture-of-experts
language model. arXiv preprint arXiv:2405.04434, 2024.
[26] Jijia Liu, Chao Yu, Jiaxuan Gao, Yuqing Xie, Qingmin Liao, Yi Wu, and Yu Wang. Llm-powered
hierarchical language agent for real-time human-ai coordination. arXiv preprint arXiv:2312.15224, 2023.
[27] Yuhan Liu, Yuyang Huang, Jiayi Yao, Zhuohan Gu, Kuntai Du, Hanchen Li, Yihua Cheng, Junchen
Jiang, Shan Lu, Madan Musuvathi, et al. Droidspeak: Kv cache sharing for cross-llm communication and
multi-llm serving. arXiv preprint arXiv:2411.02820, 2024.
[28] Yuhan Liu, Hanchen Li, Yihua Cheng, Siddhant Ray, Yuyang Huang, Qizheng Zhang, Kuntai Du, Jiayi
Yao, Shan Lu, Ganesh Ananthanarayanan, et al. Cachegen: Kv cache compression and streaming for fast
large language model serving. In Proceedings of the ACM SIGCOMM 2024 Conference, pages 38–56,
2024.
[29] Diego Mesquita, Amauri Souza, and Samuel Kaski. Rethinking pooling in graph neural networks. Advances
in Neural Information Processing Systems, 33:2220–2231, 2020.
[30] Mozhgan Navardi, Romina Aalishah, Yuzhe Fu, Yueqian Lin, Hai Li, Yiran Chen, and Tinoosh Mohsenin.
Genai at the edge: Comprehensive survey on empowering edge devices. In Proceedings of the AAAI
Symposium Series, volume 5, pages 180–187, 2025.
[31] Joon Sung Park, Joseph O’Brien, Carrie Jun Cai, Meredith Ringel Morris, Percy Liang, and Michael S
Bernstein. Generative agents: Interactive simulacra of human behavior. In Proceedings of the 36th annual
acm symposium on user interface software and technology, pages 1–22, 2023.
[32] Bharat Prakash, Tim Oates, and Tinoosh Mohsenin. Llm augmented hierarchical agents. In NeurIPS 2023
Foundation Models for Decision Making Workshop.
12

## Page 13

[33] Yujia Qin, Shihao Liang, Yining Ye, Kunlun Zhu, Lan Yan, Yaxi Lu, Yankai Lin, Xin Cong, Xiangru Tang,
Bill Qian, et al. Toolllm: Facilitating large language models to master 16000+ real-world apis. arXiv
preprint arXiv:2307.16789, 2023.
[34] Connor Shorten, Charles Pierse, Thomas Benjamin Smith, Erika Cardenas, Akanksha Sharma, John
Trengrove, and Bob van Luijt. Structuredrag: Json response formatting with large language models. arXiv
preprint arXiv:2408.11061, 2024.
[35] Significant Gravitas. AutoGPT.
[36] Charles Spearman. The proof and measurement of association between two things. The American journal
of psychology, 100(3/4):441–471, 1987.
[37] Jianlin Su, Murtadha Ahmed, Yu Lu, Shengfeng Pan, Wen Bo, and Yunfeng Liu. Roformer: Enhanced
transformer with rotary position embedding. Neurocomputing, 568:127063, 2024.
[38] Khanh-Tung Tran, Dung Dao, Minh-Duong Nguyen, Quoc-Viet Pham, Barry O’Sullivan, and Hoang D
Nguyen. Multi-agent collaboration mechanisms: A survey of llms. arXiv preprint arXiv:2501.06322,
2025.
[39] Guanzhi Wang, Yuqi Xie, Yunfan Jiang, Ajay Mandlekar, Chaowei Xiao, Yuke Zhu, Linxi Fan, and Anima
Anandkumar. Voyager: An open-ended embodied agent with large language models. Transactions on
Machine Learning Research.
[40] Qinsi Wang, Jinghan Ke, Masayoshi Tomizuka, Yiran Chen, Kurt Keutzer, and Chenfeng Xu. Dobi-svd:
Differentiable svd for llm compression and some new perspectives. arXiv preprint arXiv:2502.02723,
2025.
[41] Qinsi Wang, Jinghan Ke, Hancheng Ye, Yueqian Lin, Yuzhe Fu, Jianyi Zhang, Kurt Keutzer, Chenfeng Xu,
and Yiran Chen. Angles don’t lie: Unlocking training-efficient rl through the model’s own signals. arXiv
preprint arXiv:2506.02281, 2025.
[42] Qinsi Wang, Bo Liu, Tianyi Zhou, Jing Shi, Yueqian Lin, Yiran Chen, Hai Helen Li, Kun Wan, and Wentian
Zhao. Vision-zero: Scalable vlm self-improvement via strategic gamified self-play, 2025.
[43] Qinsi Wang, Saeed Vahidian, Hancheng Ye, Jianyang Gu, Jianyi Zhang, and Yiran Chen. Coreinfer:
Accelerating large language model inference with semantics-inspired adaptive sparse activation. arXiv
preprint arXiv:2410.18311, 2024.
[44] Qinsi Wang, Hancheng Ye, Ming-Yu Chung, Yudong Liu, Yueqian Lin, Martin Kuo, Mingyuan Ma, Jianyi
Zhang, and Yiran Chen. Corematching: A co-adaptive sparse inference framework with token and neuron
pruning for comprehensive acceleration of vision-language models. arXiv preprint arXiv:2505.19235,
2025.
[45] Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Fei Xia, Ed Chi, Quoc V Le, Denny
Zhou, et al. Chain-of-thought prompting elicits reasoning in large language models. Advances in neural
information processing systems, 35:24824–24837, 2022.
[46] Bingyang Wu, Shengyu Liu, Yinmin Zhong, Peng Sun, Xuanzhe Liu, and Xin Jin. Loongserve: Efficiently
serving long-context large language models with elastic sequence parallelism. In Proceedings of the ACM
SIGOPS 30th Symposium on Operating Systems Principles, pages 640–654, 2024.
[47] Chengyue Wu, Hao Zhang, Shuchen Xue, Zhijian Liu, Shizhe Diao, Ligeng Zhu, Ping Luo, Song Han,
and Enze Xie. Fast-dllm: Training-free acceleration of diffusion llm by enabling kv cache and parallel
decoding. arXiv preprint arXiv:2505.22618, 2025.
[48] Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu, Beibin Li, Erkang Zhu, Li Jiang, Xiaoyun Zhang,
Shaokun Zhang, Jiale Liu, et al. Autogen: Enabling next-gen llm applications via multi-agent conversations.
In First Conference on Language Modeling.
[49] Yongji Wu, Yechen Xu, Jingrong Chen, Zhaodong Wang, Ying Zhang, Matthew Lentz, and Danyang Zhuo.
Mccs: A service-based approach to collective communication for multi-tenant cloud. In Proceedings of the
ACM SIGCOMM 2024 Conference, pages 679–690, 2024.
[50] Chunqiu Steven Xia, Yinlin Deng, Soren Dunn, and Lingming Zhang. Agentless: Demystifying llm-based
software engineering agents. arXiv preprint arXiv:2407.01489, 2024.
[51] Renqiu Xia, Haoyang Peng, Hancheng Ye, Mingsheng Li, Xiangchao Yan, Peng Ye, Botian Shi, Yu Qiao,
Junchi Yan, and Bo Zhang. Structchart: On the schema, metric, and augmentation for visual chart
understanding. arXiv e-prints, pages arXiv–2309, 2023.
13

## Page 14

[52] Renqiu Xia, Bo Zhang, Hancheng Ye, Xiangchao Yan, Qi Liu, Hongbin Zhou, Zijun Chen, Peng Ye, Min
Dou, Botian Shi, et al. Chartx & chartvlm: A versatile benchmark and foundation model for complicated
chart reasoning. arXiv preprint arXiv:2402.12185, 2024.
[53] Guangxuan Xiao, Yuandong Tian, Beidi Chen, Song Han, and Mike Lewis. Efficient streaming language
models with attention sinks. In The Twelfth International Conference on Learning Representations.
[54] Yechen Xu, Xinhao Kong, Tingjun Chen, and Danyang Zhuo. Conveyor: Efficient tool-aware llm serving
with tool partial execution. arXiv preprint arXiv:2406.00059, 2024.
[55] Xiangchao Yan, Shiyang Feng, Jiakang Yuan, Renqiu Xia, Bin Wang, Bo Zhang, and Lei Bai. Surveyforge:
On the outline heuristics, memory-driven generation, and multi-dimensional evaluation for automated
survey writing. arXiv preprint arXiv:2503.04629, 2025.
[56] Jingbo Yang, Bairu Hou, Wei Wei, Yujia Bao, and Shiyu Chang. Kvlink: Accelerating large language
models via efficient kv cache reuse. arXiv preprint arXiv:2502.16002, 2025.
[57] Yuhao Yang, Jiabin Tang, Lianghao Xia, Xingchen Zou, Yuxuan Liang, and Chao Huang. Graphagent:
Agentic graph language assistant. arXiv preprint arXiv:2412.17029, 2024.
[58] Jiayi Yao, Hanchen Li, Yuhan Liu, Siddhant Ray, Yihua Cheng, Qizheng Zhang, Kuntai Du, Shan Lu, and
Junchen Jiang. Cacheblend: Fast large language model serving for rag with cached knowledge fusion. In
Proceedings of the Twentieth European Conference on Computer Systems, pages 94–109, 2025.
[59] Hancheng Ye, Chong Yu, Peng Ye, Renqiu Xia, Yansong Tang, Jiwen Lu, Tao Chen, and Bo Zhang.
Once for both: Single stage of importance and sparsity search for vision transformer compression. In
Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 5578–5588,
2024.
[60] Hancheng Ye, Jiakang Yuan, Renqiu Xia, Xiangchao Yan, Tao Chen, Junchi Yan, Botian Shi, and Bo Zhang.
Training-free adaptive diffusion with bounded difference approximation strategy. Advances in Neural
Information Processing Systems, 37:306–332, 2024.
[61] Zhitao Ying, Jiaxuan You, Christopher Morris, Xiang Ren, Will Hamilton, and Jure Leskovec. Hierarchical
graph representation learning with differentiable pooling. Advances in neural information processing
systems, 31, 2018.
[62] Jiakang Yuan, Xiangchao Yan, Botian Shi, Tao Chen, Wanli Ouyang, Bo Zhang, Lei Bai, Yu Qiao, and
Bowen Zhou. Dolphin: Closed-loop open-ended auto-research through thinking, practice, and feedback.
arXiv preprint arXiv:2501.03916, 2025.
[63] Aohan Zeng, Mingdao Liu, Rui Lu, Bowen Wang, Xiao Liu, Yuxiao Dong, and Jie Tang. Agenttuning:
Enabling generalized agent abilities for llms. In Findings of the Association for Computational Linguistics
ACL 2024, pages 3053–3077, 2024.
[64] Bo Zhang, Hancheng Ye, Gang Yu, Bin Wang, Yike Wu, Jiayuan Fan, and Tao Chen. Sample-centric feature
generation for semi-supervised few-shot learning. IEEE Transactions on Image Processing, 31:2309–2320,
2022.
[65] Guibin Zhang, Yanwei Yue, Zhixun Li, Sukwon Yun, Guancheng Wan, Kun Wang, Dawei Cheng, Jef-
frey Xu Yu, and Tianlong Chen. Cut the crap: An economical communication pipeline for LLM-based
multi-agent systems. In The Thirteenth International Conference on Learning Representations, 2025.
[66] Lingzhe Zhang, Yunpeng Zhai, Tong Jia, Xiaosong Huang, Chiming Duan, and Ying Li. Agentfm:
Role-aware failure management for distributed databases with llm-driven multi-agents. arXiv preprint
arXiv:2504.06614, 2025.
[67] Siyan Zhao, Daniel Israel, Guy Van den Broeck, and Aditya Grover. Prepacking: A simple method for fast
prefilling and increased throughput in large language models. arXiv preprint arXiv:2404.09529, 2024.
[68] Lianmin Zheng, Liangsheng Yin, Zhiqiang Xie, Chuyue Livia Sun, Jeff Huang, Cody Hao Yu, Shiyi
Cao, Christos Kozyrakis, Ion Stoica, Joseph E Gonzalez, et al. Sglang: Efficient execution of structured
language model programs. Advances in Neural Information Processing Systems, 37:62557–62583, 2024.
[69] Mingchen Zhuge, Wenyi Wang, Louis Kirsch, Francesco Faccio, Dmitrii Khizbullin, and Jürgen Schmid-
huber. Gptswarm: Language agents as optimizable graphs. In Forty-first International Conference on
Machine Learning, 2024.
14

## Page 15

6 Appendix
Due to the ten-page limitation of the manuscript, we provide more details and visualizations from the
following aspects:
• Sec. 6.1: Limitations and Broader Impacts.
• Sec. 6.2: Method Explanation.
– Sec. 6.2.1: Glossary.
– Sec. 6.2.2: Theoretical Proof of Proposition 1 and 2.
– Sec. 6.2.3: Placeholder Naming Rules.
– Sec. 6.2.4: KV-cache Management System.
– Sec. 6.2.5: Algorithm of KVCOMM.
• Sec. 6.3: More Experimental Details.
– Sec. 6.3.1: Statistical Analysis of KV-cache Proximity and Offset Proximity.
– Sec. 6.3.2: Prompts on Three Benchmarks.
• Sec. 6.4: More Experimental Analysis.
– Sec. 6.4.1: Evaluations on Harder Reasoning Benchmarks
– Sec. 6.4.2: Analysis on the Matching Criterion.
– Sec. 6.4.3: Analysis on the Approximation Method.
– Sec. 6.4.4: Analysis on the Overhead in Long-context Anchor Matching.
– Sec. 6.4.5: Analysis on the Memory Cost of KVCOMM.
– Sec. 6.4.6: Visualization of Responses Generated by Different Combinations of Align-
ment Strategies.
– Sec. 6.4.7: Visualization of Anchor Distribution.
– Sec. 6.4.8: Visualization of Difference between Prefix and Placeholder Offset Distribu-
tions.
– Sec. 6.4.9: Visualization of Distance between Approximated and Real Offsets.
6.1 Limitations and Broader Impacts
Currently, KVCOMM is evaluated on LLM-based multi-agent systems that process text inputs. A
long-term vision of multi-agent systems is to achieve lossless acceleration on any modality input,
such as image, video, or audio input. Besides, although KVCOMM can accelerate the prefilling
process of each agent, the decoding latency as another bottleneck for efficient collaboration between
agents cannot be accelerated by KVCOMM, which will be the future work to co-optimize these two
stages.
Furthermore, as mentioned in Sec. 3.1, KVCOMM is directly applicable for groups of homogeneous
agents. For agents with identical architectures but different weights, KVCOMM holds promise
but is pending further exploration. Also, in principle, KVCOMM can be applied wherever context
change patterns recur, provided shared text segmentation is feasible (as with techniques similar to
automatic prefix caching in vLLM). Although currently KVCOMM does not cover fully dynamic,
unstructured cases, we recognize this as a meaningful direction and will extend KVCOMM for more
dynamic agentic and debate-style benchmarks in future work. For the heterogeneous multi-agent
systems with different attention formulations [25, 8], it remains underexplored how to use KV-cache
communication to facilitate efficiency.
6.2 Method Explanation
6.2.1 Glossary
Base KV-cache KV-cache for a prefix/placeholder under its initial context or without external input;
serves as the reference for offsets.
KV-cache offset / deviation The difference between a shared text’s KV-cache under a new prefix
and its base KV-cache (Keys require RoPE-based alignment before offsetting).
15

## Page 16

Placeholder / Prefix offset Offsets for the placeholder segment (external input) and its adjacent
prefix segment (predefined context), respectively, relative to their base KV-caches.
Offset variance problem KV-cache offsets for the same text can vary substantially across contexts,
so static reuse is unreliable.
Positional alignment / Key de-rotation RoPE de-rotation/re-rotation to align Keys before offset-
ting.
Shareability Whether a request can skip prefill under anchor criteria; if not, dense prefilling is used.
Shared memory / KV-cache The shared storage that holds base KV-caches across agents.
Dense prefilling / generation The full computation path (prefill + decode) used when reuse is not
possible.
Anchor (pool) A small set of representative examples, each storing placeholder and prefix offsets,
used to interpolate offsets for new contexts.
6.2.2 Theoretical Proof of Proposition 1 and 2
Throughout the proofs, we reuse the per-layer update defined in Eq. (2):
hl+1 = hl + FFNl(cid:0) hl + Attnl(hl) (cid:1) . (A.1)
n n n n
We introduce the Lipschitz conditions for attention and FFN modules [20, 43, 44, 41]:
n
∥ Attnl(hl) − Attnl(h˜l) ∥ ≤ αl (cid:88) ∥hl − h˜l∥, (A.2)
n n i i
i=1
∥ FFNl(hl ) − FFNl(h˜l )∥ ≤ βl∥hl − h˜l ∥. (A.3)
j j j j
Proof of Proposition 1 Define the maximum divergence between two hidden states hl, h˜l at layer
l:
∆l = max ∥hl − h˜l ∥, with ∆1 = δ . (A.4)
k k n
k≤n
Subtracting two instances of Eq. (A.1) and applying Eq. (A.2) yields:
(cid:16) (cid:17)
∥hl+1 − h˜l+1∥ ≤ ∥hl − h˜l ∥ + βl ∥hl − h˜l ∥ + ∥ Attnl(hl) − Attnl(h˜l) ∥ (A.5)
n n n n n n n n
n
≤ (1 + βl)∆l + βlαl (cid:88) ∥hl − h˜l∥ (A.6)
i i
i=1
≤ (1 + βl + nβlαl)∆l. (A.7)
Thus, we derive:
∆l+1 ≤ (1 + σl)∆l, where σl = (1 + n)βlαl. (A.8)
Unrolling this recursion from layer 1 to l, we have:
l−1
(cid:89)
∆l ≤ δ (1 + σj). (A.9)
n
j=1
Projecting to the key space via linear mapping W l and RoPE, whose spectral norms are bounded by
K
constants Cl and C respectively, we have:
K R
l−1
∥kl − k˜l ∥ ≤ C Cl δ (cid:89) (1 + σj), (A.10)
n n R K n
j=1
which completes the proof of Proposition 1. Due to analogous reasoning, the bound for value vectors
is similar except for the absence of RoPE projection.
16

## Page 17

Proof of Proposition 2 Let two different prompts p and p be prefixed to both tokens u and
a b
v. Denote their key vectors at positions n when prefixed by p as kl , k˜l for token u and v
a a na na
respectively, and at positions n when prefixed by p as k¯l , k ˜¯l respectively. Define the two key
b b nb nb
vector deviations as follows:
∆l = k¯l − kl , ∆˜ l = k ˜¯l − k˜l . (A.11)
nb na nb na
Then we have:
∥∆l − ∆˜ l∥ = ∥k¯l − kl − (k ˜¯l − k˜l )∥ (A.12)
nb na nb na
≤ ∥kl − k˜l ∥ + ∥k¯l − k ˜¯l ∥. (A.13)
na na nb nb
Applying Proposition 1 to each term, we have:
l−1
∥kl − k˜l ∥ ≤ C Cl δ (cid:89) (1 + σj), (A.14)
na na R K na
j=1
l−1
∥k¯l − k ˜¯l ∥ ≤ C Cl δ (cid:89) (1 + σj), (A.15)
nb nb R K nb
j=1
where δ = max ∥h1 − h˜1∥, δ = max ∥h¯1 − h ˜¯1∥. Since h1 = h˜1 for k ≤ n − 1
na k≤na k k nb k≤nb k k k k a
(the same prefix p ), h¯1 = h ˜¯1 for k ≤ n − 1 (the same prefix p ), h1 = h¯1 (the same token u),
a k k b b na nb
h˜1 = h ˜¯1 (the same token v), we have δ = δ = ∥h1 − h˜1 ∥. Thus, we conclude:
na nb na nb na na
l−1
∥∆l − ∆˜ l∥ ≤ 2 C Cl δ (cid:89) (1 + σj), (A.16)
R K na
j=1
completing the proof of Proposition 2. The proof of the bound for value vectors is similar, except for
the absence of RoPE projection.
Table A.1: KV-cache management strategy for both anchor pools and current requests’ KV-cache
sharing among agents.
Anchor Manager
1st level 2nd level 3rd level
Indices Placeholder ID, e.g., Anchor Index, e.g., Agent ID / embedding, e.g.,
user_question anchor[0] agent_1_ph_∆
Values Anchor List Dict of different KV-cache off- KV-cache / embedding ten-
set in different agents and the an- sor
chor embedding tensor
Shared KV-cache Manager
1st level 2nd level 3rd level
Indices Agent ID / User In- Placeholder id, e.g., response Turn Index, e.g.,
put, e.g., agent_1 response[-1]
Values Dict of different Dict of response and prefix KV- KV-cache list
agents’ response caches
KV and outside
input KV
6.2.3 Placeholder Naming Rules
The placeholder in each agent’s prompt template in a multi-agent system can be divided into three
categories: user input, tool execution results, and responses from other agents [48, 69, 65]. Conse-
quently, we design the name of each placeholder in the prompt template according to its category.
17

## Page 18

Algorithm 1: Anchor-based KV-cache Communication in Multi-Agent Systems (KVCOMM)
Input: Agent set M with prompts containing placeholders {ϕ }; Anchor pool capacity V;
(m,i)
Entropy threshold γ.
Output: Efficiently updated KV-caches for all agents and responses from all agents.
foreach agent m ∈ M do
Extract placeholder tokens {ϕ } from prompt;
(m,i)
Initialize anchor pool A for each placeholder ϕ if not exist;
ϕ (m,i)
foreach new input sample do
foreach agent m ∈ M do
if any placeholder sample is not in the shared memory then
Compute the base KV-caches for the placeholder samples absent in the shared
memory and store them in the shared memory;
if all placeholders in the template are predicted as shareable according to Eq. (5) then
// Reuse Placeholder KV-caches
async foreach placeholder ϕ in agent m do
(m,i)
// Anchor Matching and Offset Approximation
Retrieve base KV-cache in the shared memory; Retrieve anchor pool A ;
ϕ(m,i)
Identify matched anchors ψ ∈ A ;
ϕ(m,i)
Compute weights w = softmax(−∥h − h ∥) across anchors;
ϕ(m,i)→ψ ϕ(m,i) ψ
Approximate KV-cache using Eq. (6);
Similarly, update neighboring prefix segments using Eq. (7);
Concatenate all updated {(kˆ/vˆ) , (kˆ/vˆ) } for agent m;
ϕ(m,i) p(m,i)
Response and its KV-cache←Decoding based on the concatenated KV-cache;
if the response’s KV-cache is reusable according to Eq. (5) then
Store the response KV-cache in the shared memory for reference of other agents;
else
Store the response KV-cache in the anchor pool of the response placeholder as the
base KV-cache of a new anchor;
else
// Add as a new anchor
Response, Real KV-cache of all placeholders←Dense generation for the input
sample;
async foreach placeholder ϕ in agent m do
(m,i)
Retrieve the base KV-cache of ϕ from the shared memory;
(m,i)
∆(k/v)ϕ ←the offset between the real KV-cache and the base KV-cache
(m,ϕ(m,i))
of ϕ ;
(m,i)
∆(k/v)p ←the offset between the real KV-cache and the base KV-cache
(m,ϕ(m,i))
of p ;
(m,i)
A ←
ϕ(m,i)
(cid:110) (cid:111)
A ∪ (ϕ , (k/v) , ∆(k/v)ϕ , ∆(k/v)p ) ;
ϕ(m,i) (m,i) ϕ(m,i) (m,ϕ(m,i)) (m,ϕ(m,i))
if |A | > V then
ϕ(m,i)
Prune least-frequently-used among earliest anchors in A ;
ϕ(m,i)
Suppose an agent is assigned a unique agent id as xxx, and is succeeded to the other two agents,
whose agent id are yyy and zzz respectively, the naming rule of the placeholders in Agent xxx’s
prompt template is defined as follows:
• User input: {user_question};
• Tool execution results at the current turn: {condition_xxx_current};
• Tool execution results at the previous t-th turn: {condition_xxx_history_t};
• Response from Agent yyy at the current turn: {agent_yyy_current};
18

## Page 19

• Response from Agent zzz at the current turn: {agent_zzz_current};
• Response from itself at the previous t-th turn: {agent_xxx_history_t};
• Response from Agent yyy at the previous t-th turn: {agent_yyy_history_t};
• Response from Agent zzz at the previous t-th turn: {agent_zzz_history_t};
Based on the above rule, it helps easily insert potential placeholders in each agent’s initial prompt
template and unify the addressing rule for all agents’ placeholders in the shared anchor pools.
6.2.4 KV-cache Management Strategy
Regarding the cache management strategy in KVCOMM, we designed two three-level cache managers
to achieve efficient writing and retrieving anchors’ KV-caches and the current shared KV-caches,
respectively. As shown in Table A.1, based on these two cache managers, each agent can quickly
retrieve their intended KV-caches and also store their generated KV-caches. Meanwhile, we conduct
the process of KV-cache storage and retrieval asynchronously, thus further improving the efficiency.
6.2.5 Algorithm of KVCOMM
The specific details of KVCOMM are shown in Algorithm 1.
6.3 More Experimental Details
6.3.1 Statistical Analysis of KV-cache Proximity and Offset Proximity
In Figure 4, we aim to evaluate the correlation between the KV-cache proximity and the token
embedding proximity, as well as the correlation between the KV-cache offset proximity and the token
embedding proximity. This evaluation is crucial to validate the effectiveness of our approach in
accurately approximating the KV-cache offsets of tokens by the embedding-closest anchors. For
Figure 4a and 4b, we randomly sample 4000 distinct vocabulary tokens and then select 300 token
pairs that are closest in the embedding space to form three equally-sized distance bins (“near”, “mid”,
and “far”). For all token pairs, we prepend them with the same prefix context, test their K/V distance
between each other, and compute the Spearman correlation coefficients [36] between the token
distance and their K/V distances. For Figure 4c and 4d, we adopt the same setting, further prepend
each token with two different prefixes, and test the cache deviation distance between different tokens.
6.3.2 Prompt Design on Three Benchmarks
We show the detailed prompt template of each agent that is deployed in our experiments, which
follows GPTSwarm [69] and AgentPrune [65].
MMLU We cycle through the following roles for multi-agent reasoning:
• Knowledgeable Expert
• Wiki Searcher
• Critic
• Mathematician
• FinalRefer
Below, we show the prompt template for each role:
Knowledgeable Expert
You are a knowledgeable expert in question answering. Please give at most six key entities that need to be
searched in wikipedia to solve the problem. Key entities that need to be searched are included between
two ‘@’ when output, for example: @catfish effect@, @broken window effect@, @Shakespeare@. If
there is no entity in the question that needs to be searched in Wikipedia, you don’t have to provide it.
The task is: {user_question}
19

## Page 20

Wiki Searcher
You will be given a question and a wikipedia overview of the key entities within it.
Please refer to them step by step to give your answer.
And point out potential issues in other agent’s analysis.
The task is: {user_question}
The key entities of the problem are explained in Wikipedia as follows: {condition_1_current}
At the same time, the outputs of other agents are as follows:
Agent 1, role is Knowledge Expert, output is:
{agent_1_current}
In the last round of dialogue, the outputs of other agents were:
Agent 1, role is Knowledge Expert, output is:
{agent_1_history_-1}
Critic
You are an excellent critic.
Please point out potential issues in other agent’s analysis point by point.
The task is: {user_question}
At the same time, the outputs of other agents are as follows:
Agent 1, role is Knowledge Expert, output is:
{agent_1_current}
Agent 2, role is Wiki Searcher, output is:
{agent_2_current}
In the last round of dialogue, the outputs of other agents were:
Agent 1, role is Knowledge Expert, output is:
{agent_1_history_-1}
Agent 2, role is Wiki Searcher, output is:
{agent_2_history_-1}
Mathematician
You are a mathematician who is good at math games, arithmetic calculation, and long-term planning.
The task is: {user_question}
At the same time, the outputs of other agents are as follows:
Agent 1, role is Knowledge Expert, output is:
{agent_1_current}
Agent 2, role is Wiki Searcher, output is:
{agent_2_current}
Agent 3, role is Critic, output is:
{agent_3_current}
In the last round of dialogue, the outputs of other agents were:
Agent 1, role is Knowledge Expert, output is:
{agent_1_history_-1}
Agent 2, role is Wiki Searcher, output is:
{agent_2_history_-1}
Agent 3, role is Critic, output is:
{agent_3_history_-1}
FinalRefer
You are the top decision-maker and are good at analyzing and summarizing other people’s opinions,
finding errors and giving final answers. You will receive a question followed by four possible answers
labeled A, B, C, and D. Only one answer is correct. Choose the correct option based on the analysis and
recommendations provided by the output of other agents. Your response must be exactly one of the
letters A, B, C, or D, with no additional characters or text.
The task is: {user_question}
At the same time, the outputs of other agents are as follows:
Agent 1, role is Knowledge Expert, output is:
{agent_1_current}
Agent 2, role is Wiki Searcher, output is:
{agent_2_current}
Agent 3, role is Critic, output is:
20

## Page 21

{agent_3_current}
Agent 4, role is Mathematician, output is:
{agent_4_current}
In the last round of dialogue, the outputs of other agents were:
Agent 1, role is Knowledge Expert, output is:
{agent_1_history_-1}
Agent 2, role is Wiki Searcher, output is:
{agent_2_history_-1}
Agent 3, role is Critic, output is:
{agent_3_history_-1}
Agent 4, role is Mathematician, output is:
{agent_4_history_-1}
GSM8K We cycle through the following roles:
• Math Solver
• Mathematical Analyst
• Programming Expert
• Inspector
• FinalRefer
Below are the prompt templates for each agent:
Math Solver
You are a math expert.
You will be given a math problem and hints from other agents.
Give your own solving process step by step based on hints.
The last line of your output contains only the final result without any units, for example: The answer is
140
You will be given some examples you may refer to. Q: Angelo and Melanie want to plan how many
hours over the next week they should study together for their test next week.
They have 2 chapters of their textbook to study and 4 worksheets to memorize.
They figure out that they should dedicate 3 hours to each chapter of their textbook and 1.5 hours for
each worksheet.
If they plan to study no more than 4 hours each day, how many days should they plan to study total over
the next week if they take a 10-minute break every hour, include 3 10-minute snack breaks each day,
and 30 minutes for lunch each day?.
A: Let’s think step by step.
Angelo and Melanie think they should dedicate 3 hours to each of the 2 chapters, 3 hours x 2 chapters =
6 hours total.
For the worksheets they plan to dedicate 1.5 hours for each worksheet, 1.5 hours x 4 worksheets = 6
hours total. Angelo and Melanie need to start with planning 12 hours to study, at 4 hours a day, 12 / 4 =
3 days.
However, they need to include time for breaks and lunch. Every hour they want to include a 10-minute
break, so 12 total hours x 10 minutes = 120 extra minutes for breaks.
They also want to include 3 10-minute snack breaks, 3 x 10 minutes = 30 minutes.
And they want to include 30 minutes for lunch each day, so 120 minutes for breaks + 30 minutes for
snack breaks + 30 minutes for lunch = 180 minutes, or 180 / 60 minutes per hour = 3 extra hours.
So Angelo and Melanie want to plan 12 hours to study + 3 hours of breaks = 15 hours total.
They want to study no more than 4 hours each day, 15 hours / 4 hours each day = 3.75
They will need to plan to study 4 days to allow for all the time they need.
The answer is 4
Q: Bella has two times as many marbles as frisbees. She also has 20 more frisbees than deck cards. If
she buys 2/5 times more of each item, what would be the total number of the items she will have if she
currently has 60 marbles?
A: Let’s think step by step
When Bella buys 2/5 times more marbles, she’ll have increased the number of marbles by 2/5*60 = 24
The total number of marbles she’ll have is 60+24 = 84
21

## Page 22

If Bella currently has 60 marbles, and she has two times as many marbles as frisbees, she has 60/2 = 30
frisbees.
If Bella buys 2/5 times more frisbees, she’ll have 2/5*30 = 12 more frisbees.
The total number of frisbees she’ll have will increase to 30+12 = 42
Bella also has 20 more frisbees than deck cards, meaning she has 30-20 = 10 deck cards
If she buys 2/5 times more deck cards, she’ll have 2/5*10 = 4 more deck cards.
The total number of deck cards she’ll have is 10+4 = 14
Together, Bella will have a total of 14+42+84 = 140 items The answer is 140
Q: Susy goes to a large school with 800 students, while Sarah goes to a smaller school with only 300
students. At the start of the school year, Susy had 100 social media followers. She gained 40 new
followers in the first week of the school year, half that in the second week, and half of that in the third
week. Sarah only had 50 social media followers at the start of the year, but she gained 90 new followers
the first week, a third of that in the second week, and a third of that in the third week. After three weeks,
how many social media followers did the girl with the most total followers have?
A: Let’s think step by step
After one week, Susy has 100+40 = 140 followers.
In the second week, Susy gains 40/2 = 20 new followers.
In the third week, Susy gains 20/2 = 10 new followers.
In total, Susy finishes the three weeks with 140+20+10 = 170 total followers.
After one week, Sarah has 50+90 = 140 followers.
After the second week, Sarah gains 90/3 = 30 followers.
After the third week, Sarah gains 30/3 = 10 followers.
So, Sarah finishes the three weeks with 140+30+10 = 180 total followers.
Thus, Sarah is the girl with the most total followers with a total of 180.
The answer is 180
Q: {user_question}
Mathematical Analyst
You are a mathematical analyst. You will be given a math problem, analysis and code from other agents.
You need to first analyze the problem-solving process step by step, where the variables are represented
by letters. Then you substitute the values into the analysis process to perform calculations and get the
results. The last line of your output contains only the final result without any units, for example: The
answer is 140 You will be given some examples you may refer to.
Q: There are 15 trees in the grove. Grove workers will plant trees in the grove today. After they are
done, there will be 21 trees. How many trees did the grove workers plant today?
A: ## Problem solving process analysis
There are {ori_tree_num} trees originally.
Then there were {after_planted_tree_num} trees after some more were planted.
So the number of trees planted today {today_planted_num} is the number of trees after planting
{after_planted_tree_num} minus the number of trees before planting {ori_tree_num}.
The answer is {today_planted_num} = {after_planted_tree_num} - {ori_tree_num}.
## Actual analysis and solution process
In this question, {ori_tree_num} = 15 and {after_planted_tree_num} = 21.
There are 15 trees originally.
Then there were 21 trees after some more were planted.
So the number of trees planted today must have been 21 - 15 = 6.
The answer is 6
Q: Leah had 32 chocolates and her sister had 42. If they ate 35, how many pieces do they have left in
total?
A:## Problem solving process analysis
Originally, Leah had {Leah_num} Leah_num chocolates.
Her sister had {sister_num} chocolates.
So in total they had {all_num} = {Leah_num} + {sister_num} chocolates.
After eating {eating_num} chocolates, the number of chocolates they have left {remain_num} is
{all_num} minus {eating_num}.
The answer is {remain_num} = {all_num} - {eating_num}.
## Actual analysis and solution process
In this question, {Leah_num} = 32, {sister_num} = 42 and {all_num} = 35.
So, in total they had 32 + 42 = 74 chocolates originally.
22

## Page 23

After eating 35 chocolates, they had 74 - 35 = 39 chocolates.
The answer is 39
Q: {user_question}
At the same time, there are the following responses to the same question for your reference:
Agent 1 as a Math Solver his answer to this question is:
{agent_1_current}
In the last round of dialogue, there were the following responses to the same question for your reference:
Agent 1 as a Math Solver his answer to this question was:
{agent_1_history_-1}
Programming Expert
You are a programming expert. You will be given a math problem, analysis and code from
other agents. Integrate step-by-step reasoning and Python code to solve math problems.
Analyze the question and write functions to solve the problem. The function should not take
any arguments and use the final result as the return value. The last line of code calls the
function you wrote and assigns the return value to the answer variable. Use a Python code
block to write your response. For example:
‘‘‘python
def fun():
x = 10
y = 20
return x + y
answer = fun()
‘‘‘
Do not include anything other than Python code blocks in your response. You will be given
some examples you may refer to. Q: Olivia has $23. She bought five bagels for $3 each. How
much money does she have left?
A:
‘‘‘python
def money_left():
money_initial = 23
bagels = 5
bagel_cost = 3
money_spent = bagels * bagel_cost
remaining_money = money_initial - money_spent
return remaining_money
answer = money_left()
‘‘‘
Q: Michael had 58 golf balls. On tuesday, he lost 23 golf balls. On wednesday, he lost 2 more.
How many golf balls did he have at the end of wednesday?
A:
‘‘‘python
def remaining_golf_balls():
golf_balls_initial = 58
golf_balls_lost_tuesday = 23
golf_balls_lost_wednesday = 2
golf_balls_left = golf_balls_initial -
golf_balls_lost_tuesday - golf_balls_lost_wednesday
remaining_golf_balls = golf_balls_left
return remaining_golf_balls
answer = remaining_golf_balls()
‘‘‘
Q: {user_question}
At the same time, there are the following responses to the same question for your reference:
23

## Page 24

Agent 1 as a Math Solver his answer to this question is:
{agent_1_current}
Agent 2 as a Mathematical Analyst his answer to this question is:
{agent_2_current}
In the last round of dialogue, there were the following responses to the same question for
your reference:
Agent 1 as a Math Solver his answer to this question was:
{agent_1_history_-1}
Agent 2 as a Mathematical Analyst his answer to this question was:
{agent_2_history_-1}
Inspector
You are an Inspector. You will be given a math problem, analysis and code from other agents.
Check whether the logic/calculation of the problem solving and analysis process is correct (if
present). Check whether the code corresponds to the solution analysis (if present). Give your
own solving process step by step based on hints. The last line of your output contains only
the final result without any units, for example: The answer is 140 You will be given some
examples you may refer to.
Q: {user_question}
At the same time, there are the following responses to the same question for your reference:
Agent 1 as a Math Solver his answer to this question is:
{agent_1_current}
Agent 2 as a Mathematical Analyst his answer to this question is:
{agent_2_current}
Agent 3 as a Programming Expert his answer to this question is:
{agent_3_current}
the result is {condition_3_current}
In the last round of dialogue, there were the following responses to the same question for
your reference:
Agent 1 as a Math Solver his answer to this question was:
{agent_1_history_-1}
Agent 2 as a Mathematical Analyst his answer to this question was:
{agent_2_history_-1}
Agent 2 as a Programming Expert his answer to this question was:
{agent_3_history_-1}
the result is {condition_3_history_-1}
FinalRefer
You are the top decision-maker. Good at analyzing and summarizing mathematical problems, judging
and summarizing other people’s solutions, and giving final answers to math problems. You will be
given a math problem, analysis and code from other agents. Please find the most reliable answer based
on the analysis and results of other agents. Give reasons for making decisions. The last line of your
output contains only the final result without any units, for example: The answer is 140
The task is: {user_question}
At the same time, the output of other agents is as follows:
Agent 1, role is Math Solver, output is:
{agent_1_current}
Agent 2, role is Mathematical Analyst, output is:
{agent_2_current}
Agent 3, role is Programming Expert, output is:
{agent_3_current}
the result is {condition_3_current}
Agent 4, role is Inspector, output is:
{agent_4_current}
In the last round of dialogue, the outputs of other agents were:
Agent 1, role is Math Solver, output is:
{agent_1_history_-1}
24

## Page 25

Agent 2, role is Mathematical Analyst, output is:
{agent_2_history_-1}
Agent 3, role is Programming Expert, output is:
{agent_3_history_-1}
the result is {condition_3_history_-1}
Agent 4, role is Inspector, output is:
{agent_4_history_-1}
HumanEval Benchmark For HumanEval, the following roles are cycled for collaborative code
generation and debugging:
• Project Manager
• Algorithm Designer
• Programming Expert
• Test Analyst
• FinalRefer
Below are the prompt templates for each agent:
Project Manager
You are a project manager. You will be given a function signature and its docstring by the user.
You are responsible for overseeing the overall structure of the code, ensuring that the code is
structured to complete the task. Implement code concisely and correctly without pursuing
over-engineering. You need to suggest optimal design patterns to ensure that the code follows
best practices for maintainability and flexibility. You can specify the overall design of the
code, including the classes that need to be defined (maybe none) and the functions used
(maybe only one function). I hope your reply will be more concise. Preferably within fifty
words. Don’t list too many points.
The task is: {user_question}
Algorithm Designer
You are an algorithm designer. You will be given a function signature and its docstring by
the user. You need to specify the specific design of the algorithm, including the classes that
may be defined and the functions used. You need to generate the detailed documentation,
including explanations of the algorithm, usage instructions, and API references. When the
implementation logic is complex, you can give the pseudocode logic of the main algorithm.
I hope your reply will be more concise. Preferably within fifty words. Don’t list too many
points.
The task is: {user_question}
At the same time, the outputs and feedbacks of other agents are as follows:
Agent 1 as a Project Manager:
The code written by the agent is:
{agent_1_current}
Whether it passes internal testing?
{condition_1_current}
In the last round of dialogue, the outputs and feedbacks of some agents were:
Agent 1 as a Project Manager:
The code written by the agent is:
{agent_1_history_-1}
Whether it passes internal testing?
{condition_1_history_-1}
Programming Expert
You are a programming expert. You will be given a function signature and its docstring by
25

## Page 26

the user. You may be able to get the output results of other agents. They may have passed
internal tests, but they may not be completely correct. Write your full implementation (restate
the function signature). Use a Python code block to write your response. For example:
‘‘‘python
print(’Hello world!’)
‘‘‘
Do not include anything other than Python code blocks in your response. Do not change
function names and input variable types in tasks.
The task is: {user_question}
At the same time, the outputs and feedbacks of other agents are as follows:
Agent 1 as a Project Manager:
The code written by the agent is:
{agent_1_current}
Whether it passes internal testing?
{condition_1_current}
Agent 2 as a Algorithm Designer provides the following info:
{agent_2_current}
In the last round of dialogue, the outputs and feedbacks of some agents were:
Agent 1 as a Project Manager:
The code written by the agent was:
{agent_1_history_-1}
Whether it passed internal testing?
{condition_1_history_-1}
Agent 2 as a Algorithm Designer provided the following info:
{agent_2_history_-1}
Test Analyst
You are a test analyst. You will be given a function signature and its docstring by the user. You
need to provide problems in the current code or solution based on the test data and possible
test feedback in the question. You need to provide additional special use cases, boundary
conditions, etc. that should be paid attention to when writing code. You can point out any
potential errors in the code. I hope your reply will be more concise. Preferably within fifty
words. Don’t list too many points.
The task is: {user_question}
At the same time, the outputs and feedbacks of other agents are as follows:
Agent 1 as a Project Manager:
The code written by the agent is:
{agent_1_current}
Whether it passes internal testing?
{condition_1_current}
Agent 2 as a Algorithm Designer provides the following info:
{agent_2_current}
Agent 3 as a Programming Expert:
The code written by the agent is:
{agent_3_current}
Whether it passes internal testing?
{condition_3_current}
In the last round of dialogue, the outputs and feedbacks of some agents were:
Agent 1 as a Project Manager:
The code written by the agent was:
{agent_1_history_-1}
Whether it passed internal testing?
{condition_1_history_-1}
Agent 2 as an Algorithm Designer provided the following info:
{agent_2_history_-1}
26

## Page 27

Agent 3 as a Programming Expert:
The code written by the agent was:
{agent_3_history_-1}
Whether it passed internal testing?
{condition_3_history_-1}
FinalRefer
You are the top decision-maker and are good at analyzing and summarizing other people’s opinions,
finding errors, and giving final answers. And you are an AI that only responds with only Python code.
You will be given a function signature and its docstring by the user. You may be given the overall code
design, algorithm framework, code implementation or test problems. Write your full implementation
(restate the function signature). If the prompt given to you contains code that passed internal testing,
you can choose the most reliable reply. If there is no code that has passed internal testing in the prompt,
you can change it yourself according to the prompt. Use a Python code block to write your response.
For example:
‘‘‘python
print(’Hello world!’)
‘‘‘
Do not include anything other than Python code blocks in your response
The task is: {user_question}
At the same time, the output of other agents is as follows:
Agent 1 as a Project Manager:
The code written by the agent was:
{agent_1_current}
Whether it passed internal testing?
{condition_1_current}
Agent 2 as an Algorithm Designer provided the following info:
{agent_2_current}
Agent 3 as a Programming Expert:
The code written by the agent was:
{agent_3_current}
Whether it passed internal testing?
{condition_3_current}
Agent 4, role is Test Analyst, output is:
The code written by the agent was:
{agent_4_current}
Whether it passed internal testing?
{condition_4_current}
In the last round of dialogue, the outputs of other agents were:
Agent 1 as a Project Manager:
The code written by the agent was:
{agent_1_history_-1}
Whether it passed internal testing?
{condition_1_history_-1}
Agent 2 as an Algorithm Designer provided the following info:
{agent_2_history_-1}
Agent 3 as a Programming Expert:
The code written by the agent was:
{agent_3_history_-1}
Whether it passed internal testing?
{condition_3_history_-1}
Agent 4, role is Test Analyst, output is:
The code written by the agent was:
{agent_4_history_-1}
Whether it passed internal testing?
{condition_4_history_-1}
27

## Page 28

Table A.2: Performance on MATH500 and AIME under different numbers of collaborating agents.
Higher is better for Accuracy and Reuse Rate.
# Agents
Dataset Model Method
2 3 4
Acc. (%) Original 41.6 39.6 42.6
Acc. (%) KVCOMM 38.0 38.6 44.2
Llama-3.1
Reuse Rate (%) Original 0 0 0
Reuse Rate (%) KVCOMM 59.4 40.9 30.7
MATH500
Acc. (%) Original 51.4 49.6 42.8
Acc. (%) KVCOMM 50.8 50.8 45.8
Deepseek-Qwen
Reuse Rate (%) Original 0 0 0
Reuse Rate (%) KVCOMM 76.7 60.4 45.3
Acc. (%) Original 19.2 17.5 17.5
Acc. (%) KVCOMM 11.7 10.8 8.3
AIME Deepseek-Qwen
Reuse Rate (%) Original 0 0 0
Reuse Rate (%) KVCOMM 71.3 78.1 74.6
6.4 More Experimental Analysis
In this section, we provide more analysis on KVCOMM, including the effectiveness of the pro-
posed matching criterion, the effectiveness of the ℓ norm-based approximation method, and more
2
visualizations for understanding the effectiveness and efficiency of KVCOMM.
6.4.1 Evaluations on Harder Reasoning Benchmarks
We further provide evaluation results on the MATH500 [14] and AIME [6] benchmarks to examine the
effectiveness of KVCOMM under harder reasoning tasks. For MATH500, we tested both Llama3.1-
8B-instruct [11] (Llama-3.1) and Deepseek-R1-Distill-Qwen-7B [12] (Deepseek-Qwen). As shown
in Table A.2, KVCOMM achieves superior or comparable performance to dense computation.
Compared with relatively easy math reasoning tasks such as GSM8K, the reuse rate indeed drops
more rapidly as the number of agents increases. Nevertheless, the accuracy of KVCOMM remains
competitive or even surpasses the baseline, indicating that referencing anchors’ information can
consistently help. A notable insight from Deepseek-Qwen results is that KVCOMM achieves both a
higher reuse rate and a higher accuracy on reasoning-oriented models.
We also evaluate on the more challenging AIME benchmark with Deepseek-Qwen. As shown in
Table A.2, KVCOMM still maintains comparable accuracy to dense prefill while keeping the reuse
rate above 70%. The accuracy drop here is mainly due to the token length constraint during decoding:
since KVCOMM accelerates prefill at the cost of extra memory, the effective decoding length per
agent is reduced.
6.4.2 Analysis on the Matching Criterion
In this section, we further examine the ef-
Table A.3: Ablation study of the matching criterion on
fectiveness of our proposed anchor match-
MMLU under a four-agent setting. (Model: Llama-3.1)
ing criterion, evaluating the ℓ norm-based
2
matching criterion. Table A.3 compares Method Acc (%) Reuse Rate (%)
two distinct matching criteria for anchor L 62.1 93.3
ϕ
prediction and the approximation of place-
holder samples on the MMLU benchmark L & H 68.0 70.1
ϕ ϕ|A
in the four-agent scenario. Recognizing
that the length match is a fundamental requirement for effective token-level approximation within
placeholder samples, we explicitly evaluate the contribution of the complementary distance-based
matching criterion H . It is observed that omitting the distance-based criterion can increase
ϕ|A
anchor reuse rates; however, this is accompanied by a marked performance degradation, indicating
28

## Page 29

Table A.5: Simulated softmax latency (ms) with different anchor counts and sequence lengths.
#Anchor 1024-tokens 2048-tokens 4096-tokens
5 0.894 1.719 3.552
10 1.773 3.576 7.128
15 2.620 5.332 10.766
20 3.933 7.859 15.624
25 4.435 9.614 18.113
4.0
3.5
3.0
2.5
2.0
100 200 300 400 500 600 700 800 9001000
OUT tokens
)BG(
yromeM
IN=64 IN=512 8 IN=128 IN=1024
IN=256 7
6
5
4
100 200 300 400 500 600 700 800 9001000
OUT tokens
(a) 5 anchors
)BG(
yromeM
IN=64 IN=512 12 IN=128 IN=1024 11
IN=256 10
9
8
7
6
5
100 200 300 400 500 600 700 800 9001000
OUT tokens
(b) 10 anchors
)BG(
yromeM
IN=64 IN=512 16 IN=128 IN=1024
IN=256 14
12
10
8
100 200 300 400 500 600 700 800 9001000
OUT tokens
(c) 15 anchors
)BG(
yromeM
IN=64 IN=512 IN=128 IN=1024
IN=256
(d) 20 anchors
Figure A.1: Memory cost (GB) across IN/OUT for different anchor counts.
that mere length matching is insufficient for optimal anchor utilization. Conversely, integrating the
embedding-distance criterion achieves an advantageous balance, maintaining high performance while
providing effective anchor reuse. These results highlight the necessity of a comprehensive match-
ing criterion that incorporates both structural alignment (length matching) and semantic similarity
(embedding-distance criterion) to ensure both efficiency and task accuracy in KVCOMM.
6.4.3 Analysis on the Approximation Method
We further investigate the effectiveness of Table A.4: Performance of different approximation
different KV-cache offset approximation methods for KV-cache offsets on HumanEval under a
methods on HumanEval under a four-agent four-agent setting. (Model: Qwen-Coder-2.5-7B, Base-
setting (Table A.4). Two comparison meth- line Acc: 84.45%)
ods are introduced: one using the nearest
Method Acc (%) Reuse Rate (%)
anchor’s KV-cache offset based on the ℓ
2
norm, and another employing cosine simi- Nearest 47.20 78.9
larity with softmax-based anchor weight- Cosine Similarity 83.23 82.5
ing. Results indicate the cosine-similarity-
Ours (ℓ Norm) 83.23 81.1
based method achieves performance com- 2
parable to our ℓ norm-based method with slightly higher reuse rates. However, the nearest-reusing
2
approach significantly deteriorates performance due to the error induced by the distance between
the sample and the nearest anchor. Thus, soft aggregation of anchors proves to be an effective
approximation method.
6.4.4 Analysis of the Overhead in Long-context Anchor Matching
In KVCOMM, softmax is operated along the anchor number dimension on the negative ℓ
2
-norm
distance between the placeholder sample and each anchor, which reduces the Key/Value tensor into
the shape of [m, 1, 1, seq_len, 1] (m: anchor count, seq_len: sequence length). The latency of
softmax thus scales with both parameters. We quantify its latency overhead in Table A.5. Here
the shape of each KV-cache tensor is [32, 8, seq_len, 128]. We can observe that latency remains
reasonable (∼18 ms with 25 anchors and 4096 tokens per anchor).
These results are from a simulation without competing system workloads. In real multi-agent long-
context scenarios, the latency also includes offloading KV-caches to the CPU. For example, as shown
in Table A.6 (using Llama3.1-8B-instruct on the MMLU benchmark), the average softmax latency is
100+ ms when all anchors are offloaded to CPU, while total offloading per agent can reach 1260+
ms for 4K-token contexts. This indicates that the main overhead arises from data movement in
the softmax operation for the long-context KV. Such communication overhead can be mitigated
with systematic optimization (e.g., pipelining), which is orthogonal to the KVCOMM mechanism.
29

## Page 30

Table A.6: Latency and memory cost of 4K-tokens anchor matching using Llama3.1-8B-instruct on
the MMLU benchmark.
Metrics #Agent=3 #Agent=4
Softmax (ms) 104 122
Offloading (ms) 1260 1300
Acc. (%) 66.7 68.0
Reuse Rate (%) 49.7 51.0
Memory Cost (GB) 68.5 95.1
User What is the Decalogue? Option A: The Exodus; Option B: The Covenant; Option C: The Ten Commandments; Option D: The creation story.
Question
Knowledge Expert Knowledge Expert Knowledge Expert
T W @ o i C k a i o p n v e s e d w n ia e a r : n @ t t h @ i T s , h q @ e u M e T s e o t n i s o a C n ic , o I m l a w m w o @ a u n ld , d @ m se e B a n i r b t c s l h i @ c a fo , l r @ l a th w D e @ e f c o a ll l o o w gu in e g @ e , n @ titi E es x o in d us@, @ @ T C e o n v e C n o a m nt m @ a , n @ dm H e e n b t r s e @ w , B @ ib M le o @ sa , i @ c l J a u w d @ ais , m @ @ Exodus@, @ @ D M e o c s a a l i o c g la u w e@ @ , , @ @ E B x ib o l d ic u a s l @ la , w @ @ Ten Commandments@, @Covenant@,
Wiki Searcher Wiki Searcher
Wiki Searcher @Ten Commandments@, @Mosaic law@, @Exodus@, @Covenant@,
Based on the provided information, I will analyze the outputs of Agent 1 and @Hebrew Bible@, @Judaism@ Option C: The Ten Commandments
point out potential issues. Analysis: The Ten Commandments are a set of religious and ethical directives Analysis: The Decalogue, also known as the Ten Commandments, is a set of
that are central to the Jewish and Christian faiths. They are considered to be a moral principles and laws given to the Israelites by God through Moses, as
Agent 1's output is a list of entities to search for in Wikipedia, which is a good covenant between God and the Israelites, and are inscribed on two tablets of described in the Book of Exodus and the Book of Deuteronomy. …
starting point. However, the output does not directly answer the question "What stone. ...
is the Decalogue?" It seems to be a list of related entities that might be relevant Potential issues in Agent 1's analysis: Potential issues in other agents' analysis:
to the question, but it does not provide a clear answer. * Agent 1's output is a list of related concepts, but it does not provide a clear * Agent 1's output is incomplete, as it does not mention the Exodus, which is a
Potential issues with Agent 1's output: answer to the question of what the Decalogue is. ... crucial context for understanding the Decalogue. ...
1. Lack of direct answer: The output does not directly answer the question, but Correct answer: ... Key entities:
rather provides a list of entities that might be related to the question. ... Potential issues in other agents' analysis: * Decalogue: a set of moral principles and laws given to the Israelites by God
To improve the output, Agent 1 could have provided a more direct answer, * Agent 1's analysis is based on a general understanding of the Ten through Moses. ...
such as: Commandments, but it does not take into account the specific context of the Wikipedia overview:
"The Decalogue is another name for the Ten Commandments, a set of religious question, which is asking for a definition of the Decalogue. ... * The Decalogue is a central part of the Hebrew Bible and has had a significant
and ethical directives given by YHWH to Moses, as described in the Hebrew Potential issues in Agent 2's analysis: impact on Western culture and ethics.
Bible." ... * Agent 2's output is a simple statement that does not provide a clear * The Decalogue is given to the Israelites by God through Moses in the Book of
This would have provided a more direct and relevant answer to the question. understanding of the Decalogue. ... Exodus and the Book of Deuteronomy. ...
Critic Critic Critic
E is x s c u e e l s le w nt i t a h n A a g ly e s n is t 1 b ' y s A ou g t e p n u t t : 2! I'll add a few more points to highlight the potential @ @ T H e e n b r C e o w m B m ib a le n @ dm , e @ n J ts u @ da , i @ sm M @ osaic law@, @Exodus@, @Covenant@, T G D h e o e u d t D e th r e r o c o n a u o l g o m h g y u M . e o i s s e a s , s a e s t o d f e m sc o r r ib a e l p d r i in n c t i h p e le B s o a o n k d o la f w Ex s o g d iv u e s n a t n o d t h th e e I s B r o a o e k li t o e f s by
1 a c 2 l n . . e s L O a w a r v c e a e k r n r l t d y o h f e c b o d r q n o i u r c a e e i d c s s e t t s i o a a c n n n o . s s p I w w t e 's e e : r r T a . : h l A i e s s t l i A o s f t g e i e n n n c t t l i u t 2 i d e m e s s e t o e n n t s io e tit n a ie e rc s d h , t h t f h o a e r t , a o b r u u e t t p n i u t o t d t d o d o e ir e s e n s c 't t n ly p o r t r o e d v l i a i r d e te e c d t a l y t o A W B an i n b h d a l i e l l e t y , h s t t e h h i s e e Is : y r T T a a e h e r n e l e i t C e m N s o o o , m v r a e i m c n e t d a h ' s n a a d n r o e m u j u t a e p s n u k t t e t s a y i s a s p r e a e a t s r o i t n i f m o d r f e p u t e l l h e e d e s s . a t H a T s e t h e e b e m t r y e o e w f a n r r t u e B t l i h e a b a s l c e t t o . h is v a e n t n o a a t r n e e t n i b m ti e r p e t o w ly r e t a a e n c n c t G u in r o a t d h te e . P * c r o A u t g c e i e a n n l t t i c a 1 o l ' n s i t s e o s x u u t t p e fo u s r t i u i n s n o i d n t e c h r o e s m r ta p a n l g d e e i t n e n g , t s a th ' s e a it n D d a e o ly c e s a s i l o s n g : o u t e m . e .. n . tion the Exodus, which is a
the question, such as "Biblical law" and "Institutes of Biblical Law", which might
n 3 D o . e t I c n b a s e lo u n g ff e u ic c e i e e i s s n s o t a r c r y i o t s f n o t s r e i g a x n n t: i s f i T w c h a e e n r i c n o e g u . t t p I h t u e s t i m q d u o p e e ly s s t n l i i o ' s t n t p s . r a o v b id u e n c a h n y o f c r o e n la te te x d t a e b n o ti u ti t e w s h w a it t h t o h u e t P * u n o A d t g e e e n r n s t t t i a a 2 n l ' s d is i o n s u g u t p e o u s f t t i h i n s e A a D g s e e i c m n a p t l o l 2 e g ' s u s e t a a . n t . e a .. m ly e s n is t : that does not provide a clear A * a r T d e h d m e it e i D o a e n n c a t a l t l o p o o g g u i u n e id t s i e s t h n o u o c m t o j a u n n s s t b i a d e e h s r e a : t v o io f r l a a w nd s , p b r u o t m a o ls te o a a g s o e o t d o f l i m fe o . r . a .. l principles that
e 4 r f T a e i e n x n . n o l p d e t s L i i w l t m v a a t ie a h c e i p n s n e k r r , i , t n o m o a a e g v f l s o n e o t p t s n h s i t t t r h u e g i i e r e o i g e r w s g r l o c e i i f e t t u o i v h i r s z n t s a t p a a n t e n . u t e d t c i T t o c , i l b h n e t A n i y i f a o s o g : r n A r T e m m e g n t h x o i e a t g e p n t 1 t h l i h l a o t i t s c e n n 2 l t o e a . , q i u a s t o . u i l . d o d r . n e n t a o s h o t t o a m i o t p f v h n o r e t e i h . r o e e p u r i i r s t f r o i o e z r v c e e r i u d l d h e s e a v o e d v a r d i a n n f a i c g l m t n e e t d o o r t e o r p e s d r t i i h f d t o t o e i r t r i h e s t q i r c h z u o t e o e u a d w s g n t h l i t i d o s h t n t e c h . o o e m f n l c o is i s s t t e t o A P A P * u n T T o o A g g d h h t t e e g e e e e e n n e n n r n t t D D s t t t t 3 4 i i e e a a a 4 , , c c n l l ' r r s a a d i i o o s s l l i o o o l l n s s e e u g g g u u t u u i i p e e s s o e e u s s f N N t i i t s s i i h i o n o n s e a a v v A A a i i D b s c c g g e s o e e e e e i t o c m , , n n o k a o o p t t f l u u i o l n r 3 4 e u t t g ' ' p p t s s l u s h e u u e t e a a s a t t . n n t B t i i . e h s s a a . i . m a : : b l l y y t l e e s s a n . i i r … s s t e : : t h i . m . a . t p d o o rt e a s n t n i o n t t p h r e o v B id ib e le a . . c . l . ear C T G D im h o e o p e u d r a r t D e e c th c r t e r o t o c o e n n a u d o l g o W m o h g y e u u M . s t e p I t o t e i u s s i r s e t n a : s a c , s u c a e l e t s t u n o d r t e f r e a m s a l c n o p r d r a i a b r e l e t t p d o h r f i i i c n n th s c t . e i h p … e H le e B s b o a r o e n k w d o l B a f w i E b s x le o g d a iv u n e s d n a h t n a o d s t h t h h e a e d I s B a r o a s o e i k l g i t n o e i f s f i c b a y n t
Final Refer Final Refer Final Refer
C C C
Baseline (No-Cache Reuse) Key Rotation + Prefix KV Offsets Key Rotation + Prefix KV Offsets + Placeholder KV Offsets
Figure A.2: Generation Comparison with different alignment combinations. Left: Original response
of each agent without cache reuse. Middle: Responses generated by cache reuse, associated with
aligning the position encoding of key caches and offsetting the prefix segments’ caches. Right:
Responses generated by combining all three alignment processes.
6.4.5 Analysis on the Memory Cost of KVCOMM
We also report memory overhead under different agentic configurations, varying input length (prefix),
output length (response), and the number of anchors per placeholder. As shown in Figure A.1
(three-agent setting), the memory cost increases with longer IN/OUT sequences and with larger
anchor counts, reflecting the storage required for anchor-specific KV-cache deviations. Empirically,
we observe that these deviation tensors are quite sparse across anchors, with on average about 50% of
elements having absolute values smaller than 10−1. This indicates substantial headroom for lossless
compression of anchors, which will be one of the future work to support longer contexts without
sacrificing prefill speedups.
6.4.6 Visualization of Responses Generated by Different Combinations of Alignment
Strategies
We further visualize the detailed response of each agent using different cache alignment strategies.
As shown in Figure A.2, it can be observed that although the middle setting (Key Rotation + Prefix
KV Offsets) eventually outputs the correct option “C”, its reasoning chain is clearly degraded: the
agents omit a formal definition of “Decalogue”, repeat the keywords from the Knowledge Expert
agent, and make analysis on agents that do not exist, resulting in a logically fragmented discourse.
This “right answer for the wrong reasons” phenomenon underscores that two-level alignment alone
30

## Page 31

1000
800 600
400
200
0 0 100 200 300 400 500 600
Sample Length (tokens)
tnuoC noitavitcA
50
Placeholder u ag se e r n _ t q _ u 1 e _c s u ti r o r n ent 40 agent_2_current c a o g n e d n i t t _ io 3 n _c _ u 3 r _ r c e u n r t rent 30
20
10
0 0 200 400 600 800 1000
Activation Count
(a)
ycneuqerF
u P se la r c _ e q h u o e l s d t e io r n 70
agent_1_current
agent_2_current 60 condition_3_current agent_3_current 50 40
30
20
10
0 0 100 200 300 400 500 600
Sample Length (tokens)
(b)
ycneuqerF
Placeholder user_question
agent_1_current
agent_2_current condition_3_current agent_3_current
(c)
Figure A.3: The distribution of anchors in a four-agent system on GSM8K, with each agent fully connected to
its predecessors within a single conversational turn. (a) Relationship between anchor activation counts and token
lengths across placeholders during inference. (b) Histogram of anchor activation counts across all placeholders.
(c) Histogram of anchor token lengths across all placeholders.
Table A.7: Differences between placeholder offset and prefix offset.
Aspect Placeholder offset Prefix offset
Definition KV-cache offset for externally injected text KV-cache offset for predefined prompt text
(users, agents, tools, etc.); its base KV-cache (system prompt, placeholder conjunctions,
is not preset. suffix).
Dependence Arises mainly from changes to the prefix Triggered by changes to the preceding
context. placeholder (injected content).
Variance Shows high variance across samples and Typically more stable, since base KV-caches
contexts. are computed under a fixed system prompt
and are less influenced by preceding
placeholders.
still disrupts the causal dependency between evidence, inference, and conclusion; the combination of
all three alignment processes is therefore essential for achieving a coherent explanation path that is
comparable to the original response.
6.4.7 Visualization of Anchor Distribution
As illustrated in Figure A.3, we visualize the anchor distribution for a four-agent system evaluated on
the GSM8K dataset. Figure A.3a demonstrates a clear positive correlation between an anchor’s token
length and its activation frequency across conversational placeholders (user_question and three agent_
response placeholders). Notably, the condition_3_current anchors, which are the execution results
of the generated Python codes, exhibit a distinctive bimodal distribution: one group is extremely
short but heavily reused (less than 10 tokens, activated over 1000 times), while another spans longer
lengths with relatively sparse activations. Figure A.3b and A.3c further emphasize this long-tailed
phenomenon, showing that the majority of anchors have activation counts under 100 and token lengths
shorter than 200. This skewed distribution justifies our cache management strategy, prioritizing
memory allocation for high-frequency anchors and dynamically pruning infrequently reused ones.
6.4.8 Visualization of Difference between Prefix and Placeholder Offset Distributions
To clarify the difference between prefix and placeholder offsets, we describe them from three aspects,
which are shown in Table A.7.
We further visualize the offset distributions of these two types, which is experimented in a fully-
connected four-agent setting on the MMLU dataset. We tested the offset variance among ten different
samples, and present them in Figure A.4, A.5, A.6, A.7, A.8, A.9, A.10, and A.11. It can be
observed that while the offset of the prefix KV is often larger than the placeholder one, its variance
is relatively smaller than the placeholder KV, especially in deep layers (e.g., Figure A.5). The
reason is that: During the precomputation of prefix KV-caches, the subsequent prefix segments are
primarily correlated with the first prefix segment, typically containing system prompts; thus, their
base KV-caches are relatively stable.
6.4.9 Visualization of Distance between Approximated and Real Offsets
Figure A.12 further compares various approximation strategies on HumanEval using Qwen-Coder-
2.5-7B for the four-agent scenario, focusing on the similarity and error between approximated
and real KV-caches. Overall, our proposed ℓ -norm-based (L2NORM) approximation exhibits
2
31

## Page 32

1.90
0.00
tesffo
yeK
Layer 0 Layer 2 Layer 4
1.90
0.00
tesffo
yeK
Layer 6 Layer 8 Layer 10
1.90
0.00
tesffo
yeK
Layer 12 Layer 14 Layer 17
1.90
0.00
tesffo
yeK
Layer 19 Layer 21 Layer 23
1.90
0.00
0 20 40 60 80 100 120
Hidden States Dim Index
tesffo
yeK
user_question: placeholder
user_question: prefix
Layer 25 Layer 27 Layer 29
0 20 40 60 80 100 120 0 20 40 60 80 100 120
Hidden States Dim Index Hidden States Dim Index
Figure A.4: Key cache offset distributions of the first agent’s placeholder and prefix segments in a
four-agent setting on the ten samples from the MMLU dataset.
32

## Page 33

0.47
0.00
tesffo
eulaV
Layer 0 Layer 2 Layer 4
0.47
0.00
tesffo
eulaV
Layer 6 Layer 8 Layer 10
0.47
0.00
tesffo
eulaV
Layer 12 Layer 14 Layer 17
0.47
0.00
tesffo
eulaV
Layer 19 Layer 21 Layer 23
0.47
0.00
0 20 40 60 80 100 120
Hidden States Dim Index
tesffo
eulaV
user_question: placeholder
user_question: prefix
Layer 25 Layer 27 Layer 29
0 20 40 60 80 100 120 0 20 40 60 80 100 120
Hidden States Dim Index Hidden States Dim Index
Figure A.5: Value cache offset distributions of the first agent’s placeholder and prefix segments in a
four-agent setting on the ten samples from the MMLU dataset.
33

## Page 34

1.47
0.00
1.98
-0.00
1.43
-0.00
tesffo
yeK
Layer 0 Layer 2 Layer 4
1.47
0.00
1.98
-0.00
1.43
-0.00
tesffo
yeK
Layer 6 Layer 8 Layer 10
1.47
0.00
1.98
-0.00
1.43
-0.00
tesffo
yeK
Layer 12 Layer 14 Layer 17
1.47
0.00
1.98
-0.00
1.43
-0.00
tesffo
yeK
Layer 19 Layer 21 Layer 23
1.47
0.00
1.98
-0.00
1.43
-0.00
0 20 40 60 80 100 120
Hidden States Dim Index
tesffo
yeK
agent_1_current: placeholder condition_1_current: placeholder user_question: placeholder
agent_1_current: prefix condition_1_current: prefix user_question: prefix
Layer 25 Layer 27 Layer 29
0 20 40 60 80 100 120 0 20 40 60 80 100 120
Hidden States Dim Index Hidden States Dim Index
Figure A.6: Key cache offset distributions of the second agent’s placeholder and prefix segments in a
four-agent setting on the ten samples from the MMLU dataset.
34

## Page 35

0.29
0.00
0.49
-0.00
0.52
-0.00
tesffo
eulaV
Layer 0 Layer 2 Layer 4
0.29
0.00
0.49
-0.00
0.52
-0.00
tesffo
eulaV
Layer 6 Layer 8 Layer 10
0.29
0.00
0.49
-0.00
0.52
-0.00
tesffo
eulaV
Layer 12 Layer 14 Layer 17
0.29
0.00
0.49
-0.00
0.52
-0.00
tesffo
eulaV
Layer 19 Layer 21 Layer 23
0.29
0.00
0.49
-0.00
0.52
-0.00
0 20 40 60 80 100 120
Hidden States Dim Index
tesffo
eulaV
agent_1_current: placeholder condition_1_current: placeholder user_question: placeholder
agent_1_current: prefix condition_1_current: prefix user_question: prefix
Layer 25 Layer 27 Layer 29
0 20 40 60 80 100 120 0 20 40 60 80 100 120
Hidden States Dim Index Hidden States Dim Index
Figure A.7: Value cache offset distributions of the second agent’s placeholder and prefix segments in
a four-agent setting on the ten samples from the MMLU dataset.
35

## Page 36

2.06
0.00
2.01
0.00
2.20
-0.00
tesffo
yeK
Layer 0 Layer 2 Layer 4
2.06
0.00
2.01
0.00
2.20
-0.00
tesffo
yeK
Layer 6 Layer 8 Layer 10
2.06
0.00
2.01
0.00
2.20
-0.00
tesffo
yeK
Layer 12 Layer 14 Layer 17
2.06
0.00
2.01
0.00
2.20
-0.00
tesffo
yeK
Layer 19 Layer 21 Layer 23
2.06
0.00
2.01
0.00
2.20
-0.00
0 20 40 60 80 100 120
Hidden States Dim Index
tesffo
yeK
agent_1_current: placeholder agent_2_current: placeholder user_question: placeholder
agent_1_current: prefix agent_2_current: prefix user_question: prefix
Layer 25 Layer 27 Layer 29
0 20 40 60 80 100 120 0 20 40 60 80 100 120
Hidden States Dim Index Hidden States Dim Index
Figure A.8: Key cache offset distributions of the third agent’s placeholder and prefix segments in a
four-agent setting on the ten samples from the MMLU dataset.
36

## Page 37

0.33
0.00
0.38
-0.00
0.36
-0.00
tesffo
eulaV
Layer 0 Layer 2 Layer 4
0.33
0.00
0.38
-0.00
0.36
-0.00
tesffo
eulaV
Layer 6 Layer 8 Layer 10
0.33
0.00
0.38
-0.00
0.36
-0.00
tesffo
eulaV
Layer 12 Layer 14 Layer 17
0.33
0.00
0.38
-0.00
0.36
-0.00
tesffo
eulaV
Layer 19 Layer 21 Layer 23
0.33
0.00
0.38
-0.00
0.36
-0.00
0 20 40 60 80 100 120
Hidden States Dim Index
tesffo
eulaV
agent_1_current: placeholder agent_2_current: placeholder user_question: placeholder
agent_1_current: prefix agent_2_current: prefix user_question: prefix
Layer 25 Layer 27 Layer 29
0 20 40 60 80 100 120 0 20 40 60 80 100 120
Hidden States Dim Index Hidden States Dim Index
Figure A.9: Value cache offset distributions of the third agent’s placeholder and prefix segments in a
four-agent setting on the ten samples from the MMLU dataset.
37

## Page 38

1.37
0.00
1.57
0.00
1.86
0.00
1.67
0.00
tesffo
yeK
Layer 0 Layer 2 Layer 4
1.37
0.00
1.57
0.00
1.86
0.00
1.67
0.00
tesffo
yeK
Layer 6 Layer 8 Layer 10
1.37
0.00
1.57
0.00
1.86
0.00
1.67
0.00
tesffo
yeK
Layer 12 Layer 14 Layer 17
1.37
0.00
1.57
0.00
1.86
0.00
1.67
0.00
tesffo
yeK
Layer 19 Layer 21 Layer 23
1.37
0.00
1.57
0.00
1.86
0.00
1.67
0.00
0 20 40 60 80 100 120
Hidden States Dim Index
tesffo
yeK
agent_1_current: placeholder agent_2_current: placeholder agent_3_current: placeholder user_question: placeholder
agent_1_current: prefix agent_2_current: prefix agent_3_current: prefix user_question: prefix
Layer 25 Layer 27 Layer 29
0 20 40 60 80 100 120 0 20 40 60 80 100 120
Hidden States Dim Index Hidden States Dim Index
Figure A.10: Key cache offset distributions of the fourth agent’s placeholder and prefix segments in a
four-agent setting on the ten samples from the MMLU dataset.
38

## Page 39

0.30
0.00
0.52
0.00 0.40
00..3050
0.00
tesffo
eulaV
Layer 0 Layer 2 Layer 4
0.30
0.00
0.52
0.00 0.40
00..3050
0.00
tesffo
eulaV
Layer 6 Layer 8 Layer 10
0.30
0.00
0.52
0.00 0.40
00..3050
0.00
tesffo
eulaV
Layer 12 Layer 14 Layer 17
0.30
0.00
0.52
0.00 0.40
00..3050
0.00
tesffo
eulaV
Layer 19 Layer 21 Layer 23
0.30
0.00
0.52
0.00 0.40
00..3050
0.00
0 20 40 60 80 100 120
Hidden States Dim Index
tesffo
eulaV
agent_1_current: placeholder agent_2_current: placeholder agent_3_current: placeholder user_question: placeholder
agent_1_current: prefix agent_2_current: prefix agent_3_current: prefix user_question: prefix
Layer 25 Layer 27 Layer 29
0 20 40 60 80 100 120 0 20 40 60 80 100 120
Hidden States Dim Index Hidden States Dim Index
Figure A.11: Value cache offset distributions of the fourth agent’s placeholder and prefix segments in
a four-agent setting on the ten samples from the MMLU dataset.
39

## Page 40

1.0
0.9
0.8
0.7
0.6
0.5
0 5 10 15 20 25
Layer
ytiralimiS
enisoC
1.0
0.9
0.8
0.7
0.6
COSINE-A0 L2NORM-A0 NEAREST-A0 PLAIN-A0
COSINE-A1 L2NORM-A1 NEAREST-A1 PLAIN-A1
COSINE-A2 L2NORM-A2 NEAREST-A2 PLAIN-A2
COSINE-A3 L2NORM-A3 NEAREST-A3 PLAIN-A3
0.5
0 5 10 15 20 25
Layer
(a)
ytiralimiS
enisoC
COSINE-A0 L2NORM-A0 NEAREST-A0 PLAIN-A0
COSINE-A1 L2NORM-A1 NEAREST-A1 PLAIN-A1
COSINE-A2 L2NORM-A2 NEAREST-A2 PLAIN-A2
COSINE-A3 L2NORM-A3 NEAREST-A3 PLAIN-A3
(b)
0.008
0.006
0.004
0.002
0.000
0 5 10 15 20 25
Layer
)mron-
naeM(
rorrE
tesffO
2
COSINE-A0 L2NORM-A0 NEAREST-A0 PLAIN-A0 0.0040
COSINE-A1 L2NORM-A1 NEAREST-A1 PLAIN-A1 C C O O S S I I N N E E - - A A 2 3 L L 2 2 N N O O R R M M - - A A 2 3 N N E E A A R R E E S S T T - - A A 2 3 P P L L A A I I N N - - A A 2 3 0.0035
0.0030
0.0025
0.0020
0.0015
0.0010
0.0005
0.0000
0 5 10 15 20 25
Layer
(c)
)mron-
naeM(
rorrE
tesffO
2
COSINE-A0 L2NORM-A0 NEAREST-A0 PLAIN-A0
COSINE-A1 L2NORM-A1 NEAREST-A1 PLAIN-A1 COSINE-A2 L2NORM-A2 NEAREST-A2 PLAIN-A2 COSINE-A3 L2NORM-A3 NEAREST-A3 PLAIN-A3
(d)
Figure A.12: Similarity and offset error analysis of approximated KV-caches versus real KV-caches across
layers of Qwen-Coder-2.5-7B on HumanEval under a four-agent setting. (a) Cosine similarity distributions
between approximated and real key caches. (b) Cosine similarity distributions between approximated and real
value caches. (c) Mean ℓ norm error distributions between approximated and real key caches. (d) Mean ℓ
2 2
norm error distributions between approximated and real value caches. Labels “COSINE-A0” to “COSINE-A3”
denote cosine-similarity-based approximation; “L2NORM-A0” to “L2NORM-A3” denote our ℓ -norm-based
2
approximation; “NEAREST-A0” to “NEAREST-A3” indicate nearest-anchor sampling approximation; “PLAIN-
A0” to “PLAIN-A3” represent unaligned baseline reuse.
consistently high cosine similarities (approximately 0.92 for keys and 0.95 for values) comparable
to the cosine-based approach, while maintaining minimal offset errors across all layers. Unlike
simpler methods such as nearest-reusing—which suffers substantial deviations in deeper layers (with
the mean offset error exceeding 0.003 beyond layer 25)—our method robustly leverages weighted
aggregation of multiple similar anchors to effectively estimate the target KV-caches. Additionally,
the plain reuse baseline demonstrates severe similarity degradation (below 0.8 cosine similarity)
and significantly elevated offset errors (above 0.004), confirming the critical importance of our
fine-grained anchor alignment strategies, especially in deeper transformer layers where mismatch
errors tend to accumulate.
40
