# latentmas-latent-collaboration-2511.20639

- Source PDF: `latentmas-latent-collaboration-2511.20639.pdf`
- Extracted at UTC: `2026-07-09T05:57:10.390086+00:00`
- Pages: 35
- Title: Latent Collaboration in Multi-Agent Systems
- SHA256: `10a9d1d141cfac51720abcd476d200f275db54d5ff3c74ec86a6f65341418ca2`

## Page 1

Latent Collaboration in Multi-Agent Systems
Jiaru Zou 1 2 * † Ruizhong Qiu 3 † Gaotang Li 3 † Xiyuan Yang 3 † Katherine Tieu 3 † Pan Lu 2 † Ke Shen
Hanghang Tong 3 Yejin Choi 2 Jingrui He 3 (cid:66) James Zou 2 (cid:66) Mengdi Wang 1 (cid:66) Ling Yang 1 (cid:66)
Project Page: https://github.com/Gen-Verse/LatentMAS
Avg. 83.7% Fewer Tokens
↓ 85.9%
snekoT
fo
#
97.9
50.0 93.7
Avg. +13.3%
58.4 89.8
Accuracy
↓ 83.4%
↓ 82.7%
↓ 84.7%
63.3
74.2
72.2
81.3
↓ 83.5% ↓ 81.7%
pu-deepS
dnE-ot-dnE
x7.0
x5.7
Avg. x4.3 Faster Inference
x4.7
x4.1 x3.2 x3.7 x3.1 x3.4 x3.4
Figure 1. Performance of LatentMAS across (i) task accuracy (%), (ii) inference speed (time(s) / run), and (iii) token usage (per token) over
9 benchmarks and 3 LLM model scales under the Hierarchical MAS setting. LatentMAS consistently improves system-level reasoning
accuracy while substantially reducing computational overhead compared with single model and text-based MAS.
Abstract each agent’s internal representations and latent
Multi-agent systems (MAS) extend large lan- thoughts, ensuring lossless information exchange
guage models (LLMs) from independent single- without re-encoding. We provide detailed theoret-
model reasoning to coordinative system-level in- ical analyses showing that LatentMAS achieves
telligence. While existing LLM agents depend on higher expressiveness and lossless information
text-based mediation for reasoning and communi- preservation with lower overall complexity than
cation, we take a step forward by enabling models standard text-based MAS. In addition, empiri-
to collaborate directly within the continuous la- cal evaluations across 9 comprehensive bench-
tent space. We introduce LatentMAS, an end-to- marks spanning math and science reasoning, com-
end training-free framework that enables pure la- monsense understanding, and code generation
tent collaboration among LLM agents. In Latent- show that LatentMAS outperforms advanced sin-
MAS, each agent first performs auto-regressive gle agents and text-based MAS baselines, achiev-
latent thoughts generation through last-layer hid- ing up to 14.6% higher accuracy, reducing output
den embeddings instead of text. Then, a shared token usage by 70.8%-83.7%, and providing 4×-
latent working memory preserves and transfers 4.3× faster end-to-end inference.
*Project Lead. †Core Contributors. 1Princeton Uni- 1. Introduction
versity 2Stanford University 3UIUC. Correspondence
to: <jingrui@illinois.edu>, <jamesz@stanford.edu>, Model collaboration emerges as the foundation of system-
<mengdiw@princeton.edu>, <ly1988@princeton.edu>.
level intelligence in the era of Agentic AI (Acharya et al.,
2025). Recent advances in multi-agent systems (MAS) (Wu
Proceedings of the 43 rd International Conference on Machine
Learning, Seoul, South Korea. PMLR 306, 2026. Copyright 2026 et al., 2024; Hu et al., 2025) have catalyzed a paradigm
by the author(s). shift from solitary, model-centric reasoning into a collabora-
1
6202
nuJ
1
]LC.sc[
3v93602.1152:viXra

## Page 2

Latent Collaboration in Multi-Agent Systems
tive endeavor among multiple interacting models. Among The first two principles jointly underscore the advantage of
these, large language model (LLM)-based MAS has been LatentMAS by enabling richer latent reasoning and lossless
adopted across various downstream applications, including latent communication. The last principle characterizes how
cooperative math and science reasoning (Pezeshkpour et al., latent collaboration reshapes the efficiency-expressiveness
2024; Zhou et al., 2025), automated code generation (Yang tradeoff, illustrating that LatentMAS enables scalable multi-
et al., 2024b; Ding et al., 2025), and open-domain question agent coordination with reduced computational overhead.
answering (Jin et al., 2025; Li et al., 2025c; 2026). Within
To empirically assess the efficacy of LatentMAS, we con-
LLM-based MAS, natural language or text generally serves
duct comprehensive evaluations on 9 benchmarks spanning
as the lingua franca – the common medium that carries each
math and science reasoning, commonsense understanding,
agent’s internal thoughts and enables communication across
and code generation (Figure 1). Across both sequential
different agents (Guo et al., 2024).
and hierarchical MAS settings, and over five different back-
Beyond explicit text, several studies have explored the use bone models spanning the Qwen3 (Yang et al., 2025) and
of LLMs’ continuous latent space as a new form of “model Llama3 (Grattafiori et al., 2024) families, LatentMAS con-
language,” (Chen et al., 2025b) by either (i) leveraging hid- sistently outperforms advanced single-model and text-based
den representations within transformers to enable single MAS baselines by (i) improving accuracy by up to 14.6%,
model’s internal latent chain-of-thought (CoT) reasoning (ii) reducing output token usage by 70.8%-83.7%, and (iii)
(Hao et al., 2024; Zheng et al., 2025; Zhang et al., 2025), delivering 4×-4.3× faster end-to-end inference. These re-
or (ii) employing KV caches or layer embeddings for in- sults demonstrate that latent collaboration not only enhances
formation exchange across two models (Liu et al., 2024; system-level reasoning quality but also provides consistent
Fu et al., 2025). However, a comprehensive model col- efficiency gains without any additional training. Further
laboration framework unifying both latent reasoning and detailed analyses of latent thought expressiveness, working-
latent communication remains unexplored. Moving one step memory transfer, and input-output alignment confirm that
forward, we aim to investigate: LatentMAS enables semantically meaningful, lossless, and
stable collaboration entirely in latent space.
Can MAS achieve pure latent collaboration?
2. Preliminary and Notations
To address this question, we introduce LatentMAS, an end-
to-end collaborative framework that operates entirely within
Auto-regressive Generation in Transformer. Let f (·)
the continuous latent space. Our core design integrates both θ
denotes the function computed by a standard Transformer
internal latent thoughts generation and cross-agent latent
model (Vaswani et al., 2017), parameterized by θ. Given
working memory transfer. Inside each agent, reasoning
an input sequence x = (x , x , . . . , x ), the transformer
unfolds through auto-regressive generation of last-layer hid- 1 2 T
f (·) first encodes each token via its input embedding
den representations, capturing the model’s ongoing internal θ
layer W to obtain token embeddings up to step t, i.e.,
thoughts without explicit decoding. Across agents, informa- in
tion is exchanged via shared latent working memory stored
E = [e
1
, e
2
, . . . , e
t
] ∈ Rt×dh, where d
h
is the model’s hid-
den dimension. The input token embeddings E then succes-
in layer-wise KV caches, capturing both the input context
sively process through L transformer layers in the forward
and newly generated latent thoughts. Overall, LatentMAS
pass through the model’s residual stream, yielding the final-
is completely training-free, enabling all agents to think and
interact purely through their internal latent representations.
layer hidden representations H = [h
1
, h
2
, . . . , h
t
] ∈ Rt×dh.
For next token generation, the model computes:
Building on this framework design, LatentMAS is grounded
f (x | x ) = softmax(h W ), (1)
on three foundational principles, which are substantiated θ t+1 ≤t t out
through comprehensive theoretical and empirical analyses: where W denotes the language model head that maps the
out
hidden representation to the vocabulary space. Each token
• Reasoning Expressiveness: Hidden representations
is generated in an auto-regressive manner and appended to
naturally encode model continuous thoughts, making
the input sequence. For latent generation, the model per-
each latent step more expressive than discrete tokens
forms auto-regression over hidden representations instead
and capable of conveying richer semantic information.
of tokens, bypassing explicit decoding (Hao et al., 2024).
• Communication Fidelity: Latent working memory
KV Cache as Working Memory. In decoder-only Trans-
preserves input representations and latent thoughts,
formers, the Key-Value (KV) cache functions as a dynamic
enabling lossless information transfer across agents.
working memory during auto-regressive generation, stor-
ing intermediate representations from previous decoding
• Collaboration Complexity: LatentMAS exhibits
steps to avoid redundant computation. Specifically, given
higher collaborative expressiveness than text-based
the input embeddings E, each transformer layer projects
MAS with substantially lower inference complexity.
them through projection matrices W , W , W to obtain
Q K V
2

## Page 3

Code
Aggregator
Math
Science
Latent Collaboration in Multi-Agent Systems
Q, K, V . When the next token at step t + 1 is generated, 3. LatentMAS
the model appends its embedding to the input sequence and
We introduce LatentMAS, an end-to-end latent collabora-
updates the cache (K , V ) as:
cache cache
tion framework that all agents reason and communicate
K ← [K ; K ], V ← [V ; V ], (2) entirely within the latent space. As illustrated in Figure 3,
cache ≤t t+1 cache ≤t t+1
our method enables LLM agents to (i) auto-regressively gen-
where K ≤t , V ≤t are accumulated key/value matrices from erate expressive latent thoughts (Section 3 S .1 o ), lv (i e i) r transfer
all previous steps and K t+1 , V t+1 are new key/value vec- latent working memory across agents with lossless com-
tors computed from the current token’s hidden state. This munication fidelity (Section 3.2), and (iii) achieve lower
accumulative property enables the KV cache to maintain a inference complexity than text-based MAS while support-
growing working memory of model internal representations. ing a higher degree of model coordination (Section 3.3).
Sequential MAS Method Roadmap. In the following sub-sections, we
present the complete pipeline of LatentMAS, detailing each
component and interleaving theoretical analyses to justify
the corresponding design principles.
Critic Planner Critic Refiner Solver 3.1. Auto-regressive Latent Thoughts Generation
Hierarchical MAS We first describe how each LLM agent performs latent rea-
aggregate
soning through its layer-wise hidden states. Instead of de-
coding explicit tokens, reasoning unfolds directly within the
Planner Refiner
agent by auto-regressively appending hidden representations
Math
from the final model layer.
Code Summarizer Given the input embeddings E = [e , e , . . . , e ] containing
1 2 t
Science
Solver the information from the question q and each agent’s instruc-
tion prompt, each LLM agent A ∈ A passes E through
Figure 2. Illustration of sequential and hierarchical MAS settings. i
L transformer layers to compute the last-layer hidden rep-
LLM-based MAS Setting. We consider a multi-agent
resentation h at current step t. Then, we insert h as the
t t
system S composed of N agents, denoted as A =
input embedding for the next step t + 1, replacing the origi-
{A , A , . . . , A }, where each agent A is an LLM corre-
1 2 N i nal decoding and next-token embedding processes used in
sponding to f above. At inference time, an input question
θi standard token generation. We auto-regressively repeat the
q is provided to the system S, which orchestrates interac-
process for m latent steps, yielding a sequence of newly gen-
tions among agents to collaboratively produce a final answer
erated last-layer hidden states H = [h , h , . . . , h ].
t+1 t+2 t+m
a corresponding to q. As MAS design paradigms are not
We define the continuous output representations H as the
definitive in general and often vary across downstream tasks
latent thoughts generated by A .
i
(Tran et al., 2025; Cemri et al., 2025), we do not restrict
our latent collaboration design to any particular architec- Input-Output Distribution Alignment. Since the newly
ture. Instead, we adopt two most commonly used MAS generated H form a sequence of dense, high-level repre-
settings (sequential and hierarchical) as the bases to ex- sentations, directly inserting them into shallow layers as
perimentally evaluate our method. Figure 2 illustrates the input embeddings may lead to out-of-distribution activa-
two MAS architecture settings. In the sequential MAS, tions (Meegahapola et al., 2019; Zhou et al., 2019) , as these
we adopt a chain-of-agents design (Zhang et al., 2024b; hidden states differ from the statistical patterns of learned to-
Zhao et al., 2026) comprising four LLM agents: planner, ken embeddings. To mitigate this in a training-free manner,
critic, refiner, and solver. These agents assume we propose a linear alignment operator that maps last-layer
complementary reasoning roles and are organized in a se- hidden states back to the valid input embeddings. Specifi-
quential pipeline, where the CoT output of each agent with cally, given W in , W out as the input and output embedding
the question q serves as the input to the next agent. In layers of A i , we seek a projection matrix W a ∈ Rdh×dh
the hierarchical MAS, we adopt a domain-specialized de- that maps each output vector h ∈ H to a new input vector e
sign (Zhuge et al., 2024; Zhao et al., 2025). Multiple LLM to align with valid input space defined by W in :
agents, including code, math, and science agents, op-
erate as different domain experts. Each agent independently e = hW , where W ≈ W † W . (3)
a a out in
reasons over the question q from its disciplinary perspective.
A summarizer agent then receives all intermediate re- Here, W † is the pseudo-inverse (Hoerl & Kennard, 1970)
out
sponses along with the question q and performs hierarchical of W (in Appendix A, we provide a detailed theoretical
out
aggregation to synthesize and refine the final answer. justification for the effectiveness of W in the input–output
a
3

## Page 4

Latent Collaboration in Multi-Agent Systems
Latent Collaboration (LatentMAS)
Latent Communication Latent Communication
𝑨𝑨𝟏𝟏 𝑨𝑨𝟐𝟐 𝑨𝑨𝟑𝟑 …
Latent Reasoning Latent Reasoning Latent Reasoning
Layer N
Latent Thoughts of
(Last-Layer Hidden States) …
Agent
𝑨𝑨… 𝟏𝟏
…
L
M
at
e
e
m
n
o
t
r
W
y o
o
f
r king
Layer 1
Key-Valu
𝑨𝑨
e
𝟏𝟏
(KV) Pairs
ℎt ℎ𝑡𝑡+1 ℎ𝑡𝑡+2 ℎ𝑡𝑡+𝑚𝑚
… 𝑨𝑨𝟏𝟏
Condition Generated on
… …
Both and
Agent
𝐴𝐴1 𝐴𝐴…2
Compute via
x
𝑄𝑄, 𝐾𝐾, 𝑉𝑉 𝑊𝑊𝑄𝑄, 𝑊𝑊𝐾𝐾, 𝑊𝑊𝑉𝑉 KV of 𝑨𝑨𝟐𝟐 KV of
… … 𝑁𝑁 … … …
𝐴𝐴1 𝐴𝐴2
T 𝑒𝑒 o 1 ken Emb 𝑒𝑒 e 2 dding Lay 𝑒𝑒 e 𝑡𝑡 r 𝑒𝑒 I 𝑡𝑡 n + p 1 ut-Ou 𝑒𝑒 t 𝑡𝑡 p + u 2 t Align𝑒𝑒m 𝑡𝑡 e + n 𝑚𝑚 t (input + latent) Concat
Compute
x
…
…𝑄𝑄, 𝐾𝐾,𝑉𝑉 …
𝑁𝑁
𝑥𝑥1 Input 𝑥𝑥 S 2 equence 𝑥𝑥𝑡𝑡 ℎ𝑡𝑡 laℎt𝑡𝑡e+n1t stepsℎ𝑡𝑡+𝑚𝑚−1
…
𝒎𝒎
Figure 3. Overview of the LatentMAS framework. To enable end-to-end system-wide latent collaboration, each LLM agent in
LatentMAS first performs reasoning in latent space by generating latent thoughts from last-layer hidden states (Section 3.1), and then
communicates its internal reasoning to subsequent agents via layer-wise transfer through shared latent working memory (Section 3.2).
alignment process, followed by a formal derivation of W a ). Remark 3.2. Theorem 3.1 suggests that latent thoughts
We then append the aligned vector e into the input sequence generation can be O (cid:0) d / log |V| (cid:1) times more efficient
h
for auto-regressive latent generation. Note that W a is a than text-based reasoning. In addition, the expressive-
small projection matrix of size d h × d h (e.g., d h =1024 ness scales linearly with d h , implying that larger models
for Qwen3-0.6B) and is computed once and reused in all inherently exhibits greater latent reasoning capacity.
subsequent latent steps. This design makes the alignment
computationally negligible while maintaining distributional As an illustration to Remark 3.2, for Qwen3-4B / 8B / 14B
consistency between latent and discrete representations. models (Yang et al., 2025), latent thoughts generation can
be 235.7 / 377.1 / 471.4 times more efficient than text-based
Expressiveness on Continuous Latent Thoughts. With the
reasoning. The full proof of Theorem 3.1 is provided in
mechanism of latent thought generation established within
Appendix B.1. Beyond reasoning within individual agents,
each agent, we next provide a theoretical analysis to quantify
collaboration in LatentMAS further relies on how these
its representational advantage over conventional discrete
agents exchange latent information, which we detail next.
token generation. The following theorem formalizes that
latent thoughts, which inherently preserve richer semantic 3.2. Thoughts Transfer via Latent Working Memory
structures, achieve substantially higher expressive capacity In text-based MAS, after one LLM agent completes its
than discrete text-based reasoning. generation, the natural language output is directly appended
to the input sequence of the next agent. However, since
Theorem 3.1 (Expressiveness of Latent Thoughts).
each agent in LatentMAS performs hidden-state generation
Under the Linear Representation Hypothesis on h (stated
without explicit text outputs, we design a new latent working
in Assumption B.1), if the sequence of all latent thoughts
memory transfer mechanism to ensure lossless information
with length m can be expressed losslessly through cor-
preservation and exchange.
responding text-based reasoning, then the length of text
(cid:0) (cid:1)
(in tokens) needs to be at least Ω d m/ log |V| , where For clarity, we describe the memory transfer mechanism
h
|V| > 1 denotes the vocabulary size. using the first two consecutive LLM agents A , A ∈ A.
1 2
As shown in Figure 3, agent A first performs m latent steps
1
4

## Page 5

Latent Collaboration in Multi-Agent Systems
of generation (Section 3.1). After completing these steps, Theorem 3.4 (LatentMAS Complexity). The time
we extract the KV-caches from all L transformer layers of complexity for each agent of LatentMAS is O (cid:0) (d2 m +
h
A 1 once and collect the latent working memory of A 1 as: d h m2 + d h tm)L (cid:1) , where t is the input length of this
M = (cid:110)(cid:16) K(l) , V (l) (cid:17) (cid:12) (cid:12) l = 1, 2, . . . , L (cid:111) , agent, and m is the length of latent thoughts. In con-
A1 A1,cache A1,cache (cid:12) trast, assuming Theorem 3.1, the time complexity for
with K(l) = [K(l) , . . . , K(l) ], (4) each agent of the vanilla text-based MAS needs to
A1,cache A1,1 A1,t+m be O (cid:0)(cid:0) d3 m 1 + d3 m2 1 + d2 tm 1 (cid:1) L +
and V A (l 1 ) ,cache = [V A (l 1 ) ,1 , . . . , V A (l 1 ) ,t+m ]. d2 |V|m h 1 lo (cid:1) g | t V o | achie h ve th l e og s 2 a | m V| e expr h essiv l e og ne |V ss | .
h log |V|
Here K(l) and V (l) are accumulated key and
A1,cache A1,cache The full proof of Theorem 3.4 is provided in B.3. It is
value matrices at the l-th layer. Unlike direct cache-sharing
worth noting that LatentMAS is agnostic to specific model
methods that exchange information mainly on prefilled input
collaboration strategies and can be seamlessly applied to
context across models, the collection of layer-wise caches
sequential, hierarchical, or other advanced MAS designs.
in M encapsulates both the initial input context and the
A1
newly generated latent thoughts of agent A .
1 4. Empirical Evaluations
Next, the successive agent A integrates the working mem-
2
Tasks and Datasets. We conduct comprehensive evalua-
ory M from agent A . Before A generates latent
A1 1 2
tions of LatentMAS across 9 benchmarks spanning both
thoughts (i.e., last-layer hidden states), we perform layer-
general-purpose and reasoning-intensive tasks: (i) Math &
wise concatenation to update its KV cache by prepending
each K(l) and V (l) to existing K(l) and Science Reasoning, including GSM8K (Cobbe et al., 2021),
A1,cache A1,cache A2,cache AIME24 (Maxwell-Jia, 2024), AIME25 (math ai, 2025),
V A (l 2 ) ,cache . By doing so, the new latent thoughts genera- GPQA-Diamond (Rein et al., 2023), and MedQA (Yang
tion in A 2 is conditioned on both the working memory of et al., 2024a); (ii) Commonsense Reasoning, including ARC-
A 1 and its own internal representations. Easy (Clark et al., 2018b) and ARC-Challenge (Clark et al.,
2018a); and (iii) Code Generation, including MBPP-Plus
Lossless Information Transfer. The latent working mem-
(Liu et al., 2023) and HumanEval-Plus (Liu et al., 2023).
ory transfer mechanism ensures that each succeeding agent
Additional benchmark details are provided in Appendix C.1.
in LatentMAS seamlessly receives its predecessor’s com-
plete output without re-encoding. In the following theorem, Models and Baselines. We adopt 5 off-the-shelf models
we further formalize this property to demonstrate that latent from both the Qwen3 family (Yang et al., 2025) (4B, 8B,
working memory transfer guarantees information fidelity and 14B) and the Llama 3 family (Grattafiori et al., 2024)
equivalent to explicit input exchange. (3B, 8B) to construct LatentMAS at different scales. For
baseline comparison, we evaluate LatentMAS against: (i)
Theorem 3.3 (Information Preservation via Latent
Single LLM agents (Single), where a single LLM directly
Working Memory). In both latent and text-based rea-
performs standard auto-regressive generation with token-
soning, the outputs of an agent when receiving latent
level decoding; (ii) Sequential text-based MAS (Sequen-
working memory from preceding agents are equivalent
tial TextMAS), following the chain-of-agents design (Zhang
to those obtained when directly inputting the preceding
et al., 2024b) with text-mediated reasoning and communi-
agents’ outputs.
cation; and (iii) Hierarchical text-based MAS (Hierarchi-
Full proof of Theorem 3.3 is provided in B.2. With lossless cal TextMAS), where domain-specialized agents collaborate
information preservation, we transfer latent working mem- through a summarizer (Zhuge et al., 2024) using text-based
ory in KV rather than directly transmitting hidden states to reasoning and communication. Detailed model and baseline
avoid redundant recomputation for the successive agent. implementations are provided in Appendix C.2.
3.3. End-to-End Pipeline with Complexity Analyses Implementation Details. For latent thoughts genera-
tion, we compute the realignment matrix W once per
For the remaining agents in LatentMAS, we follow the same a
run and reuse it across all inference steps. Each LLM
latent thoughts generation and working memory transfer
agent performs m ∈ {0, 10, 20, 40, 80} latent steps dur-
mechanism described above. Specifically, agent A inherits
3 ing reasoning. For working memory transfer, we directly
the working memory M from the preceding agent A ,
A2 2 concatenate the KV caches from the immediately pre-
performs auto-regressive last-layer hidden state generation,
ceding agent into the corresponding transformer layers
and subsequently transmits its updated latent working mem-
through the past key values interface in HuggingFace
ory M to the next agent. This process continues across
A3 Transformers (Face, 2025). Besides the HuggingFace
all agents in LatentMAS, with only the last agent decod-
implementation, we also integrate all baseline methods and
ing the final answer in texts. In the following theorem, we
LatentMAS with the vLLM backend (Kwon et al., 2023),
theoretically analyze the overall complexity of LatentMAS.
5

## Page 6

Latent Collaboration in Multi-Agent Systems
Table 1. Main results of LatentMAS on 6 general tasks under the Sequential MAS setting. We report 3 metrics in total, including
task accuracy (%, “Acc.”), total output token usage (“Token”), and end-to-end inference speed (time(s) / run, “Speed”). We compare
LatentMAS with both TextMAS and single-model (“Single”) baselines. For each metric, we bold the better performance and visualize
LatentMAS gains over TextMAS in the Improve columns. Additional results under the Hierarchical MAS setting are shown in Table 3.
Qwen3-4B Qwen3-8B Qwen3-14B
Tasks Metrics Improve Improve Improve
Single TextMAS LatentMAS Single TextMAS LatentMAS Single TextMAS LatentMAS
Sequential MAS Setting
Acc. 95.4 96.4 98.6 ↑ 2.2 95.6 99.1 98.8 ↓ 0.3 97.2 99.0 99.4 ↑ 0.4
ARC-E Token 724 2420 581 ↓ 76.0% 656 2085 490 ↓ 76.5% 608 1670 224 ↓ 86.6%
Speed 369 2874 512 ×5.6 404 3702 1759 ×2.1 551 9171 2124 ×4.3
Acc. 89.2 90.0 92.3 ↑ 2.3 91.0 94.6 94.4 ↓ 0.2 92.6 95.9 95.6 ↓ 0.3
ARC-C Token 913 2678 718 ↓ 73.2% 846 2252 529 ↓ 76.5% 773 2985 426 ↓ 85.7%
Speed 97 1579 260 ×6.1 266 2059 703 ×2.9 338 5125 1136 ×4.5
Acc. 82.4 89.8 88.2 ↓ 1.6 81.1 92.3 93.8 ↑ 1.5 83.7 93.8 95.2 ↑ 1.4
GSM8K Token 1136 3172 607 ↓ 80.9% 1280 2324 860 ↓ 63.0% 1118 3324 644 ↓ 80.6%
Speed 469 1970 375 ×5.3 449 1739 543 ×3.2 536 3729 1952 ×1.9
Acc. 47.7 65.3 66.3 ↑ 1.0 53.0 75.0 75.3 ↑ 0.3 64.7 80.3 80.7 ↑ 0.4
MedQA Token 2134 3962 1685 ↓ 57.5% 2098 4260 1555 ↓ 63.5% 1746 3444 1841 ↓ 46.5%
Speed 236 1267 438 ×2.9 476 1923 928 ×2.1 1360 4142 1420 ×2.9
Acc. 63.5 69.8 73.5 ↑ 3.7 64.8 69.5 74.6 ↑ 5.1 68.5 72.8 75.7 ↑ 2.9
MBPP+ Token 1634 4420 1339 ↓ 69.7% 2053 3695 1164 ↓ 68.5% 1858 4971 1621 ↓ 67.4%
Speed 523 2148 577 ×3.7 1064 3628 1275 ×2.8 2410 8728 2400 ×3.6
Acc. 75.0 79.7 79.9 ↑ 0.2 74.4 80.5 80.5 ↑ 0.0 76.8 81.1 86.5 ↑ 5.4
HumanEval+ Token 2380 5987 1775 ↓ 70.4% 2507 4593 1866 ↓ 59.4% 2366 5934 2042 ↓ 65.6%
Speed 274 1044 350 ×3.0 502 1619 497 ×3.3 1084 4062 1285 ×3.2
x6.7 ↓ 65.6%
Avg. x4.0 Faster Inference ↓ 68.5%
Avg. 70.8% Fewer Tokens ↓ 56.4%
x4.5
x4.0 x4.0
x3.5 x3.4 x3.2 x3.6 ↓ 78.9% ↓ 76.1%
x2.6 ↓ 79.0%
pu-deepS
dnE-ot-dnE
Figure 4. Efficiency gains of LatentMAS over single model and TextMAS under the Sequential MAS setting. Left: LatentMAS
achieves consistent faster end-to-end inference speed. Right: LatentMAS requires fewer system-wise token usage in total.
enabling prefix caching and tensor-parallel inference for built from 5 different scales of LLM backbones. To thor-
efficient deployment of larger LLM agents. We perform oughly examine collaboration behaviors during inference,
hyperparameter tuning and report the mean performance we evaluate each method from three complementary per-
over three independent runs. Across both baselines and spectives: (i) task accuracy, (ii) system throughput (total
our method, we set all LLM agents with a temperature of output tokens), and (iii) end-to-end inference speed. Across
0.6 and a top-p of 0.95. We adjust the maximum output all tasks, LatentMAS consistently improves over the single-
length for each task according to its relative difficulty. We model baseline by an average of 14.6% and 13.3% under
set the maximum length to 2,048 tokens for ARC-Eacy, the sequential and hierarchical settings, respectively, and
ARC-Challenge, and GSM8K, 4096 tokens for MedQA, further yields gains of 2.8% and 4.6% over text-based MAS.
MBPP+, and Humaneval+, 8,192 tokens for GPQA and Under identical MAS architectures, LatentMAS provides
20,000 tokens for AIME24 and AIME25. All experiments 4× and 4.3× faster inference speed on average compared
are conducted on 8×NVIDIA A100-80G GPUs. with sequential and hierarchical text-based MAS. Addition-
ally, as the agents’ collaboration occurs entirely in latent
4.1. Main Results
space, LatentMAS reduces token usage by 70.8% and 83.7%
Tables 1, 2, and 3 report the overall performance of Latent- relative to sequential and hierarchical TextMAS. We leave
MAS across 9 general and reasoning-intensive benchmarks additional results on Llama backbones in Appendix D.2.
6

## Page 7

Latent Collaboration in Multi-Agent Systems
Table 2. Main results of LatentMAS on 3 reasoning-intensive tasks under Sequential and Hierarchical MAS settings. We report
accuracy, token usage, and end-to-end speed, and highlight the performance gains following the same evaluation protocol as in Table 1.
Qwen3-8B Qwen3-14B
Tasks Metrics Improve Improve
Single TextMAS LatentMAS Single TextMAS LatentMAS
Sequential MAS Setting
Acc. 50.0 53.3 56.7 ↑ 3.4 63.3 63.3 66.7 ↑ 3.4
AIME24 Token 12891 38596 8953 ↓ 76.8% 11263 32092 10593 ↓ 67.0%
Speed 421 2808 688 ×4.1 1018 4554 1149 ×4.0
Acc. 46.7 53.3 53.3 ↑ 0.0 56.7 60.0 63.3 ↑ 3.3
AIME25 Token 14692 45088 8699 ↓ 80.7% 11298 44618 11402 ↓ 74.4%
Speed 450 3150 820 ×3.8 1040 5184 1473 ×3.5
Acc. 39.9 43.4 45.5 ↑ 2.1 48.5 51.5 52.0 ↑ 0.5
GPQA-Diamond Token 6435 17986 4571 ↓ 74.6% 5547 12676 5454 ↓ 57.0%
Speed 813 5771 854 ×6.8 1043 9714 1475 ×6.6
Hierarchical MAS Setting
Acc. 50.0 53.3 53.3 ↑ 0.0 63.3 70.0 73.3 ↑ 3.3
AIME24 Token 12891 42629 7526 ↓ 82.3% 11263 29025 10230 ↓ 64.8%
Speed 421 3132 776 ×4.0 1018 5718 1089 ×5.3
Acc. 46.7 50.0 50.0 ↑ 0.0 56.7 66.7 66.7 ↑ 0.0
AIME25 Token 14692 53929 13230 ↓ 75.5% 11298 50003 9527 ↓ 80.9%
Speed 450 3488 616 ×5.7 1040 6019 1056 ×5.7
Acc. 39.9 43.0 46.9 ↑ 3.9 48.5 52.0 53.0 ↑ 1.0
GPQA-Diamond Token 6435 22450 3395 ↓ 84.9% 5547 20931 3606 ↓ 82.8%
Speed 813 6108 798 ×7.7 1043 9119 1458 ×6.3
4.2. Efficiency Analyses on Latent Collaboration. lower token usage than single agents. Compared with single-
model reasoning, LatentMAS distributes the input question
End-to-end Inference Speed. As established earlier in
across collaborating agents, greatly reducing the burden on
Theorem 3.1, LatentMAS can achieve orders-of-magnitude
the final agent, which primarily aggregates preceding latent
higher expressiveness, thereby enabling more efficient infer-
thoughts and decodes the final answer using only a small
ence than text-based MAS. We further empirically validate
number of tokens. As a result, the entire system generates
this advantage through comparisons with TextMAS. As
fewer output tokens while still achieving higher accuracy.
shown in Figure 4 and 10 (left), even after accelerating the
TextMAS baselines using the vLLM service, LatentMAS 5. In-depth Analyses on LatentMAS
still achieves a 2.6×-7× speedup over the vLLM-optimized
TextMAS. This improvement stems from the substantially Do Latent Thoughts Reflect Text Reasoning? We first
reduced number of latent steps required for latent thoughts verify whether latent thoughts generation in LatentMAS pro-
generation compared with the much larger decoding steps duces meaningful and semantically expressive representa-
needed for per-token text generation. With fewer than 50 tions. To this end, we compare the distribution of newly gen-
latent steps, LatentMAS attains comparable or even higher erated last-layer embeddings in LatentMAS with the embed-
performance on reasoning-intensive tasks such as AIME dings of token-by-token responses produced by TextMAS.
24/25, whereas TextMAS typically requires more than 20K Experiments are conducted on 300 MedQA questions, using
output tokens to complete full text-based CoT trajectories. 40 latent steps for LatentMAS and a 4096 max-token budget
for the TextMAS baseline.
Token Throughput. In addition, as illustrated in Figure 4
and 10 (right), LatentMAS reduces token usage by 59.4%- As shown in Figure 5, we highlight two key observations:
87.9% compared with TextMAS, as agents in LatentMAS (i) The last-layer embeddings from LatentMAS share nearly
communicate by directly transferring latent working mem- the same region of the embedding space with the token
ory into another agent’s internal layers rather than relying embeddings from TextMAS, indicating that latent thoughts
on the text medium. LatentMAS also achieves 15.0%-60.3% encode similar semantic representations as the correct text
7

## Page 8

Latent Collaboration in Multi-Agent Systems
Qwen3-4B Qwen3-8B Qwen3-14B
Figure 5. Illustration of the semantic meaning encoded by LatentMAS. LatentMAS’s generated latent thoughts embeddings largely
cover the embedding space of text-based generated tokens, indicating the semantic consistency and expressive capacity of LatentMAS.
Input–Output Alignment Input–Output Alignment
(Qwen3-4B) (Qwen3-14B)
ℎ "
! "
ℎ "
! "
Density Embedding Space Density Embedding Space
Figure 6. Effectiveness of the input-output alignment W on MedQA. Unaligned output embeddings (h ) drift away from the original
a t
input embeddings (e ), while the aligned vectors (e ) realign with e , demonstrating that W preserves embedding-space structure and
t t+1 t a
prevents representation drift. Analyses on additional models are provided in Appendix E.1.
responses. (ii) The last-layer embeddings from LatentMAS
largely cover the distribution of token embeddings from
TextMAS, indicating that latent thoughts offer greater diver-
+ 2.3%
sity and expressive capacity than discrete tokens. Together,
these findings show that latent thoughts not only capture
+ 3.6% + 5.3%
the valid semantics of their corresponding text responses
but also encode richer and more expressive representations
inside. We further include a case study in Appendix J ana-
lyzing how LLM agents in LatentMAS interpret their own
latent thoughts to provide additional validation.
Effectiveness on Input-Output Alignment. We next em-
pirically evaluate the effectiveness of the input-output align-
ment in our method design. First, we compare the input
vector e obtained from the standard token embedding layer Figure 7. Downstream accuracy performance (%) on 3 benchmarks
t
before/after applying the input-output alignment W .
with both the newly generated output vector h before align- a
t
ment and the after-aligned vector e . As shown in Figure
t+1 e , indicating that W effectively restores the geometric
t a
6, we visualize the three embedding vectors by comparing
and statistical structure of the input embedding space and
both density distributions and geometric relationships in
mitigates representation drift across iterative latent steps.
the projected embedding space. We observe that the new
In Figure 7, across 3 different tasks, we further compare
h deviates largely from the original input embedding e .
t t downstream performance before and after applying W and
a
After applying W , the aligned vector e realigns with
a t+1 observe consistent accuracy gains of 2.3%-5.3% by W .
a
8

## Page 9

Latent Collaboration in Multi-Agent Systems
aims to construct a multi-agent collaboration system entirely
in latent space, treating agents as tightly integrated compo-
nents to achieve more expressive and efficient coordination.
Model Collaboration in Latent Space. Recent studies
on model collaboration (Tran et al., 2025) have gradually
shifted from text-level coordination toward interaction di-
rectly in latent representations. Instead of exchanging infor-
mation through texts, these works (Coda-Forno et al., 2025;
Ye et al., 2025a; Fu et al., 2025; Zheng et al., 2025) enable
models to communicate through model internal states such
as hidden representations (Coda-Forno et al., 2025) for ef-
Figure 8. Effectiveness of different latent step depths.
ficiency (Kong et al., 2026). Most existing methods rely
on auxiliary alignment mechanisms and typically require
Optimal Latent Step Depth. To understand how many
additional training to facilitate effective cross-model com-
latent steps are needed for optimal performance in Latent-
munication. On the other hand, LatentMAS is a training-free
MAS, we analyze the effect of increasing latent step depth
latent multi-agent system in which each agent reasons and
across three downstream tasks. As shown in Figure 8,
communicates via native latent representations.
increasing the number of latent steps generally improves
downstream performance, indicating that additional latent We leave additional related works on latent reasoning and
thoughts enhance collaborative expressiveness. Across the agent collaboration in Appendix H.
three tasks on Qwen3-14B, we find that accuracy steadily
rises and peaks around 40-80 steps. Beyond this range, per-
7. Conclusion
formance plateaus or declines, suggesting that excessive
latent thought generation may introduce redundant or less We introduce LatentMAS, a training-free framework that
useful information. Based on this observation, we adopt a enables multi-agent systems to collaborate entirely within
moderate latent step budget within this range in practice, as latent space. Our framework enables latent auto-regressive
it consistently provides the best accuracy-efficiency trade- reasoning with a lossless latent working-memory transfer
off without requiring any task-specific training procedures. mechanism. Theoretical analyses and empirical evaluations
across diverse reasoning and generation benchmarks demon-
Intermediate Error Tracking within LatentMAS. To bet-
strate that LatentMAS consistently improves accuracy per-
ter audit and interpret the latent collaboration process, we
formance, token usage, and decoding speed over strong
extend our original framework with an additional “debug
single-model and text-based MAS baselines. LatentMAS
mode” to enable a flexible conversion between inner la-
establishes a scalable and general paradigm for agentic col-
tent thoughts and outer human-readable texts within each
laboration beyond the constraints of natural language.
agent. We leave implementation details on how to converse
to the debug mode in LatentMAS, together with additional
Acknowledgment
detailed analyses and case studies, to Appendix E,F, and J.
The authors thank members of the iDEA-iSAIL Lab and
6. Related Work the Zou Group for helpful discussions and feedback on
this work. This work is supported by National Science
LLM-based Multi-agent Systems. Recent studies in Agen- Foundation under Award No. IIS-2433308 and Award No.
tic AI have extended classical multi-agent systems (Hong IIS-2117902. The views and conclusions are those of the
et al., 2023; Park et al., 2023a; Yang et al., 2024c) grounded authors and should not be interpreted as representing the
in traditional reinforcement learning and policy coordi- official policies of the funding agencies or the government.
nation, to modern LLM settings (Li et al., 2025b; Tan
et al., 2025), enabling models to operate as autonomous Impact Statement
agents that collaborate in reasoning, planning, and problem-
solving (Tao et al., 2024; Wang et al., 2025c; Zhao et al., This paper introduces LatentMAS, a framework for multi-
2025). Early methods (Yao et al., 2022; Wu et al., 2024; Li agent collaboration in the latent space, aiming to improve
et al., 2023) coordinate multiple LLMs through explicit dia- reasoning performance while reducing inference cost. The
logue and role assignment. Additional methods introduce methods and findings in this work are intended to advance
structured communication protocols to enhance cooperation research in efficient and scalable machine learning systems.
efficiency (Ye et al., 2025a) and emergent specialization We do not anticipate immediate negative societal impacts
(Mieczkowski et al., 2025; Huang et al., 2026) among agents. beyond those commonly associated with deploying more
Building upon these advanced text-MAS methods, our work capable and efficient language model systems.
9

## Page 10

Latent Collaboration in Multi-Agent Systems
References Fourney, A., Bansal, G., Mozannar, H., Tan, C., Salinas,
E., Niedtner, F., Proebsting, G., Bassman, G., Gerrits,
Acharya, D. B., Kuppan, K., and Divya, B. Agentic ai:
J., Alber, J., et al. Magentic-one: A generalist multi-
Autonomous intelligence for complex goals–a compre-
agent system for solving complex tasks. arXiv preprint
hensive survey. IEEe Access, 2025.
arXiv:2411.04468, 2024.
Ainsworth, S. K., Hayase, J., and Srinivasa, S. Git re-basin: Fu, T., Min, Z., Zhang, H., Yan, J., Dai, G., Ouyang, W.,
Merging models modulo permutation symmetries. arXiv and Wang, Y. Cache-to-cache: Direct semantic commu-
preprint arXiv:2209.04836, 2022. nication between large language models. arXiv preprint
arXiv:2510.03215, 2025.
Cemri, M., Pan, M. Z., Yang, S., Agrawal, L. A., Chopra,
B., Tiwari, R., Keutzer, K., Parameswaran, A., Klein, D., Fungwacharakorn, W., Thanh, N. H., Zin, M. M., and Satoh,
Ramchandran, K., et al. Why do multi-agent llm systems K. Layer-of-thoughts prompting (lot): Leveraging llm-
fail? arXiv preprint arXiv:2503.13657, 2025. based retrieval with constraint hierarchies. arXiv preprint
arXiv:2410.12153, 2024.
Chen, W., Yuan, J., Qian, C., Yang, C., Liu, Z., and Sun, M.
Optima: Optimizing effectiveness and efficiency for llm- Grattafiori, A., Dubey, A., Jauhri, A., Pandey, A., Kadian,
based multi-agent system. In Findings of the Association A., Al-Dahle, A., Letman, A., Mathur, A., Schelten, A.,
for Computational Linguistics: ACL 2025, pp. 11534– Vaughan, A., et al. The llama 3 herd of models. arXiv
11557, 2025a. preprint arXiv:2407.21783, 2024.
Chen, X., Zhao, A., Xia, H., Lu, X., Wang, H., Chen, Y., Guo, T., Chen, X., Wang, Y., Chang, R., Pei, S., Chawla,
Zhang, W., Wang, J., Li, W., and Shen, X. Reasoning be- N. V., Wiest, O., and Zhang, X. Large language model
yond language: A comprehensive survey on latent chain- based multi-agents: A survey of progress and challenges.
of-thought reasoning. arXiv preprint arXiv:2505.16782, arXiv preprint arXiv:2402.01680, 2024.
2025b.
Hao, S., Sukhbaatar, S., Su, D., Li, X., Hu, Z., Weston,
J., and Tian, Y. Training large language models to
Clark, P., Cowhey, I., Etzioni, O., Khot, T., Sabharwal, A.,
reason in a continuous latent space. arXiv preprint
Schoenick, C., and Tafjord, O. Think you have solved
arXiv:2412.06769, 2024.
question answering? try arc, the ai2 reasoning challenge.
arXiv preprint arXiv:1803.05457, 2018a.
Hoerl, A. E. and Kennard, R. W. Ridge regression: Biased
estimation for nonorthogonal problems. Technometrics,
Clark, P., Cowhey, I., Etzioni, O., Khot, T., Sabharwal, A.,
12(1):55–67, 1970.
Schoenick, C., and Tafjord, O. Think you have solved
question answering? try arc, the ai2 reasoning challenge.
Hong, S., Zhuge, M., Chen, J., Zheng, X., Cheng, Y., Wang,
arXiv preprint arXiv:1803.05457, 2018b.
J., Zhang, C., Wang, Z., Yau, S. K. S., Lin, Z., et al.
Metagpt: Meta programming for a multi-agent collabora-
Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H.,
tive framework. In The Twelfth International Conference
Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano,
on Learning Representations, 2023.
R., Hesse, C., and Schulman, J. Training verifiers to solve
math word problems, 2021. URL https://arxiv. Hu, M., Zhou, Y., Fan, W., Nie, Y., Xia, B., Sun, T., Ye, Z.,
org/abs/2110.14168. Jin, Z., Li, Y., Chen, Q., et al. Owl: Optimized workforce
learning for general multi-agent assistance in real-world
Coda-Forno, J., Zhao, Z., Zhang, Q., Tamboli, D., Li, W.,
task automation. arXiv preprint arXiv:2505.23885, 2025.
Fan, X., Zhang, L., Schulz, E., and Tseng, H.-P. Explor-
ing system 1 and 2 communication for latent reasoning Huang, Q., Zhou, Z., Li, Y., Yang, K., Wang, B., and
in llms. arXiv preprint arXiv:2510.00494, 2025. Wang, Y. Many minds, one goal: Time series forecast-
ing via sub-task specialization and inter-agent coopera-
Ding, H., Tao, S., Pang, L., Wei, Z., Gao, J., Ding, B., tion. In The Thirty-ninth Annual Conference on Neural
Shen, H., and Cheng, X. Toolcoder: A systematic code- Information Processing Systems, 2026. URL https:
empowered tool learning framework for large language //openreview.net/forum?id=Uon41HfqR3.
models. arXiv preprint arXiv:2502.11404, 2025.
Jin, B., Zeng, H., Yue, Z., Yoon, J., Arik, S., Wang, D.,
Face, H. Transformers documentation. https: Zamani, H., and Han, J. Search-r1: Training llms to
//huggingface.co/docs/transformers/ reason and leverage search engines with reinforcement
en/index, 2025. learning. arXiv preprint arXiv:2503.09516, 2025.
10

## Page 11

Latent Collaboration in Multi-Agent Systems
Kong, Z., Li, Y., Zeng, F., Xin, L., Messica, S., Lin, X., Meegahapola, L., Subramaniam, V., Kaplan, L., and Misra,
Zhao, P., Kellis, M., Tang, H., and Zitnik, M. Token re- A. Prior activation distribution (pad): A versatile rep-
duction should go beyond efficiency in generative models resentation to utilize dnn hidden units. arXiv preprint
– from vision, language to multimodality, 2026. URL arXiv:1907.02711, 2019.
https://arxiv.org/abs/2505.18227.
Mieczkowski, E., Mon-Williams, R., Bramley, N., Lu-
Kwon, W., Li, Z., Zhuang, S., Sheng, Y., Zheng, L., Yu, cas, C. G., Velez, N., and Griffiths, T. L. Predicting
C. H., Gonzalez, J., Zhang, H., and Stoica, I. Efficient multi-agent specialization via task parallelizability. arXiv
memory management for large language model serving preprint arXiv:2503.15703, 2025.
with pagedattention. In Proceedings of the 29th sym-
posium on operating systems principles, pp. 611–626, Park, J. S., O’Brien, J., Cai, C. J., Morris, M. R., Liang,
2023. P., and Bernstein, M. S. Generative agents: Interactive
simulacra of human behavior. In Proceedings of the 36th
Li, B., Sun, X., Liu, J., Wang, Z., Wu, J., Yu, X., Chen, annual acm symposium on user interface software and
H., Barsoum, E., Chen, M., and Liu, Z. Latent visual technology, pp. 1–22, 2023a.
reasoning. arXiv preprint arXiv:2509.24251, 2025a.
Park, K., Choe, Y. J., and Veitch, V. The linear represen-
Li, G., Al Kader Hammoud, H. A., Itani, H., Khizbullin, tation hypothesis and the geometry of large language
D., and Ghanem, B. Camel: communicative agents for models. arXiv preprint arXiv:2311.03658, 2023b.
”mind” exploration of large language model society. In
Proceedings of the 37th International Conference on Neu- Pezeshkpour, P., Kandogan, E., Bhutani, N., Rahman, S.,
ral Information Processing Systems, NIPS ’23, Red Hook, Mitchell, T., and Hruschka, E. Reasoning capacity in
NY, USA, 2023. Curran Associates Inc. multi-agent systems: Limitations, challenges and human-
centered solutions. arXiv preprint arXiv:2402.01108,
Li, Z., Ji, Q., Ling, X., and Liu, Q. A comprehensive review 2024.
of multi-agent reinforcement learning in video games.
IEEE Transactions on Games, 2025b. Rein, D., Hou, B. L., Stickland, A. C., Petty, J., Pang, R. Y.,
Dirani, J., Michael, J., and Bowman, S. R. Gpqa: A
Li, Z., Zhang, H., Han, S., Liu, S., Xie, J., Zhang, Y., graduate-level google-proof q&a benchmark, 2023. URL
Choi, Y., Zou, J., and Lu, P. In-the-flow agentic system https://arxiv.org/abs/2311.12022.
optimization for effective planning and tool use. arXiv
preprint arXiv:2510.05592, 2025c. Sagi, O. and Rokach, L. Ensemble learning: A survey. Wiley
interdisciplinary reviews: data mining and knowledge
Li, Z., Zou, J., Fang, F., Ning, X., Ai, M., Wei, T., Chen, S., discovery, 8(4):e1249, 2018.
Yang, X., and He, J. Heterogeneous scientific foundation
model collaboration. CoRR, abs/2604.27351, 2026. doi: Shi, X., Chiesa, M., Maguire Jr, G. Q., and Kostic, D. Kv-
10.48550/ARXIV.2604.27351. URL https://doi. comm: Enabling efficient llm communication through
org/10.48550/arXiv.2604.27351. selective kv sharing. arXiv preprint arXiv:2510.03346,
2025.
Liu, J., Xia, C. S., Wang, Y., and Zhang, L. Is your code
generated by chatgpt really correct? rigorous evaluation Tan, L., Wei, F., Ma, X., Peng, R., Xiao, H., and Yang,
of large language models for code generation. Advances L. Systemic condition-based maintenance optimization
in Neural Information Processing Systems, 36:21558– under inspection uncertainties: A customized multiagent
21572, 2023. reinforcement learning approach. IEEE Transactions on
Reliability, 2025.
Liu, L., Pfeiffer, J., Wu, J., Xie, J., and Szlam, A. Delibera-
tion in latent space via differentiable cache augmentation. Tao, W., Zhou, Y., Wang, Y., Zhang, W., Zhang, H., and
arXiv preprint arXiv:2412.17747, 2024. Cheng, Y. Magis: Llm-based multi-agent framework for
github issue resolution. Advances in Neural Information
math ai. AIME 2025 dataset. https://huggingface. Processing Systems, 37:51963–51993, 2024.
co/datasets/math-ai/aime25, 2025.
Tran, K.-T., Dao, D., Nguyen, M.-D., Pham, Q.-V.,
Maxwell-Jia. AIME 2024 dataset. https:// O’Sullivan, B., and Nguyen, H. D. Multi-agent collab-
huggingface.co/datasets/Maxwell-Jia/ oration mechanisms: A survey of llms. arXiv preprint
AIME_2024, 2024. arXiv:2501.06322, 2025.
11

## Page 12

Latent Collaboration in Multi-Agent Systems
Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, Yang, J., Jimenez, C. E., Wettig, A., Lieret, K., Yao, S.,
L., Gomez, A. N., Kaiser, L. u., and Polosukhin, I. At- Narasimhan, K. R., and Press, O. SWE-agent: Agent-
tention is all you need. In Guyon, I., Luxburg, U. V., computer interfaces enable automated software engineer-
Bengio, S., Wallach, H., Fergus, R., Vishwanathan, S., ing. In The Thirty-eighth Annual Conference on Neural
and Garnett, R. (eds.), Advances in Neural Information Information Processing Systems, 2024b. URL https:
Processing Systems, volume 30. Curran Associates, Inc., //openreview.net/forum?id=mXpq6ut8J3.
2017.
Yang, Y., Peng, Q., Wang, J., Wen, Y., and Zhang, W. Llm-
Wang, J., WANG, J., Athiwaratkun, B., Zhang, C., and based multi-agent systems: Techniques and business per-
Zou, J. Mixture-of-agents enhances large language model spectives. arXiv preprint arXiv:2411.14033, 2024c.
capabilities. In The Thirteenth International Conference
on Learning Representations, 2025a. URL https:// Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan,
openreview.net/forum?id=h0ZfDIrj7T. K. R., and Cao, Y. React: Synergizing reasoning and
acting in language models. In The eleventh international
Wang, Q., Shi, Y., Wang, Y., Zhang, Y., Wan, P., Gai, K., conference on learning representations, 2022.
Ying, X., and Wang, Y. Monet: Reasoning in latent
visual space beyond images and language. arXiv preprint Ye, H., Gao, Z., Ma, M., Wang, Q., Fu, Y., Chung, M.-Y.,
arXiv:2511.21395, 2025b. Lin, Y., Liu, Z., Zhang, J., Zhuo, D., et al. Kvcomm:
Online cross-context kv-cache communication for ef-
Wang, Z., Moriyama, S., Wang, W.-Y., Gangopadhyay, B., ficient llm-based multi-agent systems. arXiv preprint
and Takamatsu, S. Talk structurally, act hierarchically: arXiv:2510.12872, 2025a.
A collaborative framework for llm multi-agent systems.
arXiv preprint arXiv:2502.11098, 2025c. Ye, J., Zhang, X., Xu, H., Liu, H., Wang, J., Zhu, Z., Zheng,
Z., Gao, F., Cao, J., Lu, Z., et al. Mobile-agent-v3:
Wortsman, M., Ilharco, G., Gadre, S. Y., Roelofs, R., Fundamental agents for gui automation. arXiv preprint
Gontijo-Lopes, R., Morcos, A. S., Namkoong, H., arXiv:2508.15144, 2025b.
Farhadi, A., Carmon, Y., Kornblith, S., et al. Model
soups: averaging weights of multiple fine-tuned models Yue, L., Xing, S., Chen, J., and Fu, T. Clinicalagent: Clinical
improves accuracy without increasing inference time. In trial multi-agent system with large language model-based
International conference on machine learning, pp. 23965– reasoning. In Proceedings of the 15th ACM International
23998. PMLR, 2022. Conference on Bioinformatics, Computational Biology
and Health Informatics, pp. 1–10, 2024.
Wu, F., Li, Z., Wei, F., Li, Y., Ding, B., and Gao, J.
Talk to right specialists: Routing and planning in multi- Zhang, C., He, S., Qian, J., Li, B., Li, L., Qin, S., Kang,
agent system for question answering. arXiv preprint Y., Ma, M., Liu, G., Lin, Q., et al. Large language
arXiv:2501.07813, 2025. model-brained gui agents: A survey. arXiv preprint
arXiv:2411.18279, 2024a.
Wu, Q., Bansal, G., Zhang, J., Wu, Y., Li, B., Zhu, E., Jiang,
L., Zhang, X., Zhang, S., Liu, J., et al. Autogen: Enabling Zhang, Y., Sun, R., Chen, Y., Pfister, T., Zhang, R., and Arik,
next-gen llm applications via multi-agent conversations. S. Chain of agents: Large language models collaborating
In First Conference on Language Modeling, 2024. on long-context tasks. Advances in Neural Information
Processing Systems, 37:132208–132237, 2024b.
Yan, B., Zhou, Z., Zhang, L., Zhang, L., Zhou, Z., Miao,
D., Li, Z., Li, C., and Zhang, X. Beyond self-talk: A Zhang, Z., He, X., Yan, W., Shen, A., Zhao, C., Wang, S.,
communication-centric survey of llm-based multi-agent Shen, Y., and Wang, X. E. Soft thinking: Unlocking the
systems. arXiv preprint arXiv:2502.14321, 2025. reasoning potential of llms in continuous concept space.
arXiv preprint arXiv:2505.15778, 2025.
Yang, A., Li, A., Yang, B., Zhang, B., Hui, B., Zheng, B.,
Yu, B., Gao, C., Huang, C., Lv, C., et al. Qwen3 technical Zhao, J., Xie, H., Lei, Y., Song, X., Shi, Z., Li, L., Liu, S.,
report. arXiv preprint arXiv:2505.09388, 2025. Xie, L., and Zhang, H. Cochain: Balancing insufficient
and excessive collaboration in llm agent workflows, 2026.
Yang, H., Chen, H., Guo, H., Chen, Y., Lin, C.-S., Hu, URL https://arxiv.org/abs/2505.10936.
S., Hu, J., Wu, X., and Wang, X. Llm-medqa: Enhanc-
ing medical question answering through case studies in Zhao, W., Yuksekgonul, M., Wu, S., and Zou, J. Sirius:
large language models. arXiv preprint arXiv:2501.05464, Self-improving multi-agent systems via bootstrapped rea-
2024a. soning. arXiv preprint arXiv:2502.04780, 2025.
12

## Page 13

Latent Collaboration in Multi-Agent Systems
Zheng, Y., Zhao, Z., Li, Z., Xie, Y., Gao, M., Zhang, L.,
and Zhang, K. Thought communication in multiagent
collaboration. arXiv preprint arXiv:2510.20733, 2025.
Zhou, H., Geng, H., Xue, X., Kang, L., Qin, Y., Wang,
Z., Yin, Z., and Bai, L. Reso: A reward-driven self-
organizing llm-based multi-agent system for reasoning
tasks. arXiv preprint arXiv:2503.02390, 2025.
Zhou, W., Du, J., and Ren, X. Improving bert fine-
tuning with embedding normalization. arXiv preprint
arXiv:1911.03918, 2019.
Zhu, H., Hao, S., Hu, Z., Jiao, J., Russell, S., and Tian,
Y. Reasoning by superposition: A theoretical perspec-
tive on chain of continuous thought. arXiv preprint
arXiv:2505.12514, 2025.
Zhuge, M., Wang, W., Kirsch, L., Faccio, F., Khizbullin,
D., and Schmidhuber, J. Language agents as optimizable
graphs. arXiv preprint arXiv:2402.16823, 2024.
Zou, A., Phan, L., Chen, S., Campbell, J., Guo, P., Ren, R.,
Pan, A., Yin, X., Mazeika, M., Dombrowski, A.-K., et al.
Representation engineering: A top-down approach to ai
transparency. arXiv preprint arXiv:2310.01405, 2023.
13

## Page 14

Latent Collaboration in Multi-Agent Systems
Table of Contents
A Input-Output Alignment in LatentMAS 15
A.1 Theoretical Justification on W . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
a
A.2 Solving the Alignment Matrix W . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
a
B Theoretical Analysis 18
B.1 Proof of Theorem 3.1 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
B.2 Proof of Theorem 3.3 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
B.3 Proof of Theorem 3.4 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
C Experiment Setups 20
C.1 Evaluation Details . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
C.2 Implementation Details . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
D Additional Experiments 22
D.1 Performance of LatentMAS under Hierarchical MAS Setting . . . . . . . . . . . . . . . . . . . . . . . . 22
D.2 LatentMAS on Llama Backbones . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
D.3 Additional Efficiency Analyses on LatentMAS . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 23
E Detailed Analyses on LatentMAS 25
E.1 Additional Analyses on Input-Output Alignment . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
E.2 Quantifying Latent Thought Diversity. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 25
E.3 Ablations on Latent Reasoning and Communication in LatentMAS . . . . . . . . . . . . . . . . . . . . . 25
F How to Debug LatentMAS? 26
G Additional Discussions on LatentMAS 27
H Additional Related Works 27
I Case Study on Intermediate Error Tracking of LatentMAS 28
J Case Study on LatentMAS 30
K Prompt Template for LatentMAS 32
14

## Page 15

Latent Collaboration in Multi-Agent Systems
Appendix
A. Input-Output Alignment in LatentMAS
A.1. Theoretical Justification on W
a
In this section, we outline the theoretical justification for how W minimizes the distributional gap between the distribution
a
of token embeddings and the distribution of aligned embeddings.
Let P and P be the distribution of token embeddings e and the hidden embeddings h, respectively. We assume that P
e h e
and P can be generated by e = (cid:80) σ W and h = β (cid:80) σ W , respectively, where each semantic σ ∈ RV
h x∈V x in,x x∈V x out,x
is represented as a weight vector over tokens V with ∥σ∥ ≤ 1 and follows an underlying discrete semantic distribution
2
σ ∼ P , and β > 0 characterizes the scale of output embeddings h. In practice, we calculate the scale β by V∥h∥ .
σ (cid:80)
x∈V
∥Win,x∥
For an alignment matrix W , the aligned embedding distribution P is
a eˆ,Wa
P : eˆ = hW , h ∼ P . (5)
eˆ,Wa a h
Our goal is to minimize the distance between the aligned embedding distribution P and the token embedding distribution
eˆ,Wa
P , which we measure via the Wasserstein distance:
e
(cid:114)
d (P , P ) := inf E [∥eˆ − e∥2], (6)
Wasserstein eˆ,Wa e
γ∈Γ(Pe,Peˆ,Wa ) (eˆ,e)∼γ
2
where Γ(P , P ) is the set of all couplings of P and P .
eˆ,Wa e e eˆ,Wa
Theorem A.1 (Upper Bound on Distribution Alignment). For any alignment matrix W , the Wasserstein distance
a
between P and P is upper bounded by
e eˆ,Wa
d (P , P ) ≤ ∥βW W − W ∥ . (7)
Wasserstein eˆ,Wa e out a in F
As we show in Appendix A.2, our choice of W (Equation 3) minimizes this upper bound of W (P , P ).
a eˆ,Wa e
Proof. Consider the following joint distribution γ∗(eˆ, e):
(cid:88)
γ∗(eˆ, e) := P σ (σ)1 [β (cid:80)
x∈V
σxWout,xWa=eˆ] 1 [(cid:80)
x∈V
σxWin,x=e] . (8)
σ∈supp(Pσ)
Note that for every eˆ,
(cid:88) (cid:88) (cid:88)
γ∗(eˆ, e) = P σ (σ)1 [β (cid:80)
x∈V
σxWout,xWa=eˆ] 1 [(cid:80)
x∈V
σxWin,x=e] (9)
e∈supp(Pe) e∈supp(Pe) σ∈supp(Pσ)
(cid:88) (cid:88)
= P σ (σ)1 [β (cid:80)
x∈V
σxWout,xWa=eˆ] 1 [(cid:80)
x∈V
σxWin,x=e] (10)
σ∈supp(Pσ) e∈supp(Pe)
(cid:88)
= P σ (σ)1 [β (cid:80)
x∈V
σxWout,xWa=eˆ] 1 [(cid:80)
x∈V
σxWin,x∈supp(Pe)] (11)
σ∈supp(Pσ)
(cid:88)
= P σ (σ)1 [β (cid:80)
x∈V
σxWout,xWa=eˆ] (12)
σ∈supp(Pσ)
= P (eˆ); (13)
eˆ,Wa
15

## Page 16

Latent Collaboration in Multi-Agent Systems
and that for every e,
(cid:88) (cid:88) (cid:88)
γ∗(eˆ, e) = P σ (σ)1 [β (cid:80)
x∈V
σxWout,xWa=eˆ] 1 [(cid:80)
x∈V
σxWin,x=e] (14)
eˆ∈supp(Peˆ,Wa ) eˆ∈supp(Peˆ,Wa ) σ∈supp(Pσ)
(cid:88) (cid:88)
= P σ (σ)1 [(cid:80)
x∈V
σxWin,x=e] 1 [β (cid:80)
x∈V
σxWout,xWa=eˆ] (15)
σ∈supp(Pσ) eˆ∈supp(Peˆ,Wa )
(cid:88)
= P σ (σ)1 [(cid:80)
x∈V
σxWin,x=e] 1 [β (cid:80)
x∈V
σxWout,xWa∈supp(Peˆ,Wa )] (16)
σ∈supp(Pσ)
(cid:88)
= P σ (σ)1 [(cid:80)
x∈V
σxWin,x=e] (17)
σ∈supp(Pσ)
= P (e). (18)
e
This implies γ∗ ∈ Γ(P , P ). Since σ is a distribution over tokens, and ∥ · ∥2 is a convex function. Finally, since ∥σ∥ ≤
eˆ,Wa e 2 2
for all semantic σ ∈ supp(P ), we have
σ
(cid:114)
d (P , P ) = inf E [∥eˆ − e∥2] (19)
Wasserstein eˆ,Wa e
γ∈Γ(Pe,Peˆ,Wa ) (eˆ,e)∼γ
2
(cid:114)
≤ E [∥eˆ − e∥2] (20)
2
(eˆ,e)∼γ∗
(cid:115)
(cid:88) (cid:88)
= γ∗(eˆ, e)∥eˆ − e∥2 (21)
2
eˆ∈supp(Peˆ,Wa ) e∈supp(Pe)
(cid:115)
(cid:88) (cid:88) (cid:88)
= P σ (σ)1 [β (cid:80) x∈V σxWout,xWa=eˆ] 1 [(cid:80) x∈V σxWin,x=e] ∥eˆ − e∥2 2
eˆ∈supp(Peˆ,Wa ) e∈supp(Pe) σ∈supp(Pσ)
(22)
(cid:115)
(cid:88) (cid:88) (cid:88)
= P σ (σ) 1 [β (cid:80) x∈V σxWout,xWa=eˆ] 1 [(cid:80) x∈V σxWin,x=e] ∥eˆ − e∥2 2
σ∈supp(Pσ) eˆ∈supp(Peˆ,Wa ) e∈supp(Pe)
(23)
(cid:118)
(cid:117) (cid:13) (cid:13)2
(cid:117) (cid:88) (cid:13) (cid:88) (cid:88) (cid:13)
= (cid:116) P σ (σ)(cid:13)β σ x W out,x W a − σ x W in,x(cid:13) (24)
(cid:13) (cid:13)
σ∈supp(Pσ) x∈V x∈V 2
(cid:118)
(cid:117) (cid:13) (cid:13)2
(cid:117) (cid:88) (cid:13) (cid:88) (cid:13)
= (cid:116) P σ (σ)(cid:13) σ x (βW out,x W a − W in,x )(cid:13) (25)
(cid:13) (cid:13)
σ∈supp(Pσ) x∈V 2
(cid:115)
(cid:88)
= P (σ)∥σ(βW W − W )∥2 (26)
σ out a in 2
σ∈supp(Pσ)
(cid:115)
(cid:88)
≤ P (σ)∥σ∥2∥βW W − W ∥2 (27)
σ 2 out a in 2
σ∈supp(Pσ)
(cid:115)
(cid:88)
≤ P (σ)∥βW W − W ∥2 (28)
σ out a in 2
σ∈supp(Pσ)
(cid:115)
(cid:88)
≤ P (σ)∥βW W − W ∥2 (29)
σ out a in F
σ∈supp(Pσ)
(cid:113)
= ∥βW W − W ∥2 (30)
out a in F
= ∥βW W − W ∥ . (31)
out a in F
16

## Page 17

Latent Collaboration in Multi-Agent Systems
A.2. Solving the Alignment Matrix W
a
In Section 3.1, we put the last-layer hidden states h back to the input sequence to enable the model’s latent reasoning.
However, since the h is not perfectly aligned with the input embedding space, directly feeding h into shallow layers may
lead to out-of-distribution activation patterns inside LLMs. To mitigate this in a training-free way, we seek a matrix W
a
which maps h to a valid input space (i.e., e = hW ). A straightforward way to calculate W is to enforce that the aligned
a a
latent vector e behaves similarly to a real input embedding when it enters the model. Motivated by our Theorem A.1 below,
this corresponds to the following minimization problem:
min ∥βW W − W ∥2 . (32)
out a in F
Wa
This objective is quadratic in W , so we can derive a closed-form solution by setting its derivative to zero, which yields the
a
normal equation:
βW ⊤ W W − W ⊤ W = 0. (33)
out out a out in
Solving for W gives:
a
W = 1 (cid:0) W ⊤ W (cid:1)−1 W ⊤ W . (34)
a β out out out in
For numerical stability, we further add a small hyperparameter λ > 0 to obtain a ridge regression solution (Hoerl & Kennard,
1970):
W = 1 (cid:0) W ⊤ W + λI (cid:1)−1 W ⊤ W , (35)
a β out out out in
which we compute once and reuse for all latent reasoning steps. Here, λ > 0 is a small hyperparameter to approximate the
pseudo-inverse W † = lim (cid:0) W ⊤ W + λI (cid:1)−1 W ⊤ .
out λ↘0 out out out
17

## Page 18

Latent Collaboration in Multi-Agent Systems
B. Theoretical Analysis
B.1. Proof of Theorem 3.1
Assumption B.1 (Linear Representation Hypothesis; Park et al., 2023b). We assume that the hidden embeddings h are
linear combinations (cid:80)d
i=
h
1
c
i
s
i
of an underlying semantic basis {s
1
, . . . , s
dh
} ⊂ Rdh (linearly independent) with ternary
coefficients c , . . . , c ∈ {0, ±1}, where c = 0 represents that h does not have semantic i, and c = ±1 represents that h
1 dh i i
has semantic i in a positive/negative way.
Theorem B.1 (Restate of Theorem 3.1). Under the Linear Representation Hypothesis on h, if the sequence of all latent
thoughts with length m can be expressed losslessly through corresponding text-based reasoning, then the length of text
(cid:0) (cid:1)
(in tokens) needs to be at least Ω d m/ log |V| , where |V| > 1 denotes the vocabulary size.
h
Proof of Theorem 3.1. Under Assumption B.1, the set H of hidden embeddings is
(cid:26)
(cid:88)
dh (cid:27)
H = c s : c , . . . , c ∈ {0, ±1} , (36)
i i 1 dh
i=1
where {s
1
, . . . , s
dh
} ⊂ Rdh is the underlying semantic basis. Then, the set of length-t latent reasoning sequences is Hm.
Since the semantic basis is linearly independent, the size of the set H of hidden embeddings is
|H| = |{0, ±1}||{s1,...,sdh }| = 3dh. (37)
Thus, the size of the set of length-m latent reasoning sequences is
|Hm| = |H|m = (3dh)m = 3dhm. (38)
To represent the set Hm of length-m latent reasoning sequences via the set Vm′ of length-m′ text-based reasoning sequences
losslessly, there needs to exist an surjective map from Vm′ to Hm, which implies that |Vm′| ≥ |Hm|. Therefore,
m′ = log (|V|m′ ) = log |Vm′ | (39)
|V| |V|
≥ log |Hm| = log (3dhm) (40)
|V| |V|
d m log 3 (cid:16) d m (cid:17)
= h = Ω h .
log |V| log |V|
B.2. Proof of Theorem 3.3
Theorem B.2 (Restate of Theorem 3.3). In both latent and text-based reasoning, the outputs of an agent when receiving
latent working memory from preceding agents are equivalent to those obtained when directly inputting the preceding
agents’ outputs.
Proof. Let h(l), K(l), V (l) and h′(l), K′(l), V ′(l) denote the output, keys, and values of l-th transformer layer when receiving
latent working memory from preceding agents and when directly inputting the preceding agents’ outputs, respectively. In
the following, we will use induction to show that h(l) = h′(l) for every layer l = 1, . . . , L.
Induction step. Suppose that h(l−1) = h′(l−1), and we will show that h(l) = h′(l).
The KV cache contains K (l) and V (l). For each past token layers, at each attention layer, the transformer produces
≤t+m ≤t+m
one column of K (l) and a corresponding column of V (l). At the next step the model forms a query from the
≤t+m ≤t+m
current input and then uses that query together with the stored K (l) and V (l) to form the attention result. That
≤t+m ≤t+m
attention result is a deterministic function of the query and of the keys and values it attends to.
We are comparing two ways to make those same keys and values available to the current computation: (i) actually feeding
the earlier tokens into the model again, in which case the model will recompute the same keys and values and then use them
in attention; (ii) reading in K (l) and V (l) from the cache and use them directly. In both cases the keys and values
≤t+m ≤t+m
presented to the attention computation are identical, because the cache was produced by the same model on the same inputs.
18

## Page 19

Latent Collaboration in Multi-Agent Systems
Given identical keys and values and the same current input, the attention output is the same in both scenarios. The
remainder of the transformer computation that produces the last-layer hidden embedding is a deterministic function of that
attention output (and the current input). Therefore the last-layer hidden embedding h(l) produced for the current step is the
same whether the model recomputed keys/values from tokens or read K (l), V (l) from cache. Formally, since
≤t+m ≤t+m
h(l−1) = h′(l−1), K (l) = K′ (l), and V (l) = V ′ (l), then h(l) = h′(l).
≤t+m ≤t+m ≤t+m ≤t+m
Induction base case. For the first layer, similarly with the induction step, since the input is the same (for both latent-based
and text-based reasoning), K (1) = K′ (1), and V (1) = V ′ (1), then h(1) = h′(1).
≤t+m ≤t+m ≤t+m ≤t+m
Conclusion. By induction, we have that h(l) = h′(l) of every layer l = 1, . . . , L. In particular, since h = h(L) and
h′ = h′(L), then h = h(L) = h′(L) = h′.
B.3. Proof of Theorem 3.4
Theorem B.3 (Restate of Theorem 3.4). The time complexity for each agent of LatentMAS is O (cid:0) (d2 m + d m2 +
h h
(cid:1)
d tm)L , where t is the input length of this agent, and m is the length of latent thoughts. In contrast, assuming
h
Theorem 3.1, the time complexity for each agent of the vanilla text-based MAS needs to be O (cid:0)(cid:0) d3 m 1 +d3 m2 1 +
h log |V| h log2 |V|
d2 tm 1 (cid:1) L + d2 |V|m 1 (cid:1) to achieve the same expressiveness.
h log |V| h log |V|
Proof. We analyze the time complexity of our LatentMAS and the vanilla text-based MAS separately.
Time complexity of our method. Recall that a transformer layer consists of two main components: self-attention and
feed-forward networks. For a length-(t + m) sequence, the time complexity to compute self-attention for m latent reasoning
steps is O(d (t + m)m) = O(d (m2 + tm)) due to the attention computation between O(t2) pairs of tokens, and the time
h h
complexity to compute feed-forward networks for m latent reasoning steps is O(d2 m) due to matrix–vector multiplication.
h
Since there are L layers, the overall time complexity of our method is
O (cid:0) (d (m2 + tm) + d2 m)L (cid:1) . (41)
h h
Time complexity of the vanilla text-based MAS. Let m′ denote the number of text-based reasoning steps. Similarly with
the complexity analysis of our method, the time complexity to compute the hidden embeddings is
O (cid:0) (d (m′2 + tm′) + d2 m′)L (cid:1) . (42)
h h
Besides that, due to matrix–vector multiplication and softmax computation, the time complexity to decode hidden embed-
dings into tokens is
O
(cid:0)
d
|V|m′(cid:1)
. (43)
h
Hence, the overall time complexity of the vanilla MAS is
O (cid:0) (d (m′2 + tm′) + d2 m′)L + d |V|m′(cid:1) . (44)
h h h
Assuming Theorem 3.1, the number of text-based reasoning steps is
(cid:16) d m (cid:17)
m′ = O h . (45)
log |V|
It follows that the overall time complexity is
O (cid:0) (d (m′2 + tm) + d2 m′)L + d |V|m′(cid:1) (46)
h h h
(cid:16)(cid:16) (cid:16)(cid:16) d m (cid:17)2 (cid:16) d m (cid:17)(cid:17) (cid:16) d m (cid:17)(cid:17) (cid:16) d m (cid:17)(cid:17)
= d h + t h + d2 h L + d |V| h (47)
h log |V| log |V| h log |V| h log |V|
(cid:16)(cid:16) d3 m2 d3 m d2 tm (cid:17) d2 |V|m (cid:17)
= O h + h + h L + h . (48)
log2 |V| log |V| log |V| log |V|
19

## Page 20

Latent Collaboration in Multi-Agent Systems
C. Experiment Setups
C.1. Evaluation Details
We introduce all datasets used in our experiments as follows:
Math & Science Reasoning.
• GSM8K (Cobbe et al., 2021) is a widely used benchmark of 8.5K grade-school math word problems designed to evaluate
multi-step numerical reasoning. Each problem requires decomposing a natural-language description into structured
arithmetic steps, making it a standard testbed for assessing chain-of-thought reasoning ability.
• AIME24 (Maxwell-Jia, 2024) consists of 30 competition-level problems from the 2024 American Invitational Mathematics
Examination. These questions span algebra, geometry, number theory, and combinatorics, and require precise numeric
answers with typically 1–3 digits, making the benchmark a compact but challenging evaluation of high-school Olympiad-
style reasoning.
• AIME25 (math ai, 2025) provides 30 additional problems from the 2025 AIME exam, maintaining the same answer
format and difficulty profile. Compared with AIME24, this benchmark includes more multi-phase derivations and intricate
combinatorial constructions, offering a complementary stress test for mathematical robustness.
• GPQA-Diamond (Rein et al., 2023) is the most difficult split of the GPQA benchmark with 198 questions, featuring
graduate-level multiple-choice questions written by domain experts in physics, biology, and chemistry. The dataset
emphasizes conceptual depth, cross-disciplinary reasoning, and the ability to synthesize multi-step scientific arguments
under rigorous distractor settings.
• MedQA (Yang et al., 2024a) contains real medical licensing exam questions that assess biomedical knowledge, clinical
reasoning, and diagnostic decision-making. Problems require integrating textual context with domain-specific medical
understanding, making the benchmark a representative testbed for professional-level scientific reasoning.
Commonsense Reasoning.
• ARC-Easy (Clark et al., 2018b) consists of grade-school science questions from the AI2 Reasoning Challenge that test
foundational factual knowledge and straightforward commonsense reasoning. As a simplified subset of ARC, it serves as
a baseline measure of basic scientific understanding without requiring complex multi-step inference.
• ARC-Challenge (Clark et al., 2018a) includes the most difficult items from the AI2 Reasoning Challenge. These
questions are intentionally adversarial, requiring multi-hop reasoning, causal and counterfactual inference, and systematic
elimination of distractor choices. Performance on ARC-Challenge is widely regarded as a strong indicator of robust
commonsense reasoning capabilities.
Code Generation.
• MBPP-Plus (Liu et al., 2023) extends the original MBPP benchmark with broader input coverage, additional hidden
test cases, and stricter execution-based evaluation. Each problem requires generating a self-contained Python function
that satisfies a comprehensive unit-test suite, making the benchmark a robust measure of code synthesis reliability and
correctness.
• HumanEval-Plus (Liu et al., 2023) augments HumanEval with denser, more challenging test suites, significantly
increasing the rigor of functional correctness evaluation. The benchmark emphasizes generalization beyond prompt
examples and tests a model’s ability to produce semantically precise, executable Python code under more demanding
verification settings.
C.2. Implementation Details
In addition to the experimental setups described in the main paper, we provide additional implementation and evaluation
details below.
20

## Page 21

Latent Collaboration in Multi-Agent Systems
Software Backend All methods are implemented in Python using PyTorch and HuggingFace Transformers, with an
optional vLLM backend for fast decoding and tensor-parallel inference. We use the official chat templates and special tokens
such as <|im start|> and <|im end|>.
Evaluation protocol. For all non-coding benchmarks, we report accuracy based on answer matching of the final answer
after text normalization (lowercasing, trimming whitespace, and removing extraneous punctuation).
For multiple-choice datasets (GPQA-Diamond, MedQA, ARC-Easy, ARC-Challenge), we first extract the model’s final
answer string and then compare it via exact match to the answer letter.
For numeric problems (GSM8k, AIME24, AIME25), we evaluate correctness based on numeric equality: we extract the
final predicted answer, parse both prediction and answer into numbers, and mark as correct only if the two values match.
Predictions that fail numeric parsing are counted as incorrect.
For code generation tasks (MBPP-Plus and HumanEval-Plus), we evaluate the code by executing unit tests. Specifically, we
extract the predicted code from model’s output, append the ground-truth tests provided by the benchmark, and execute the
combined script in a sandboxed environment with a 10-second timeout. A sample is counted as correct if and only if all tests
pass without runtime errors.
21

## Page 22

Latent Collaboration in Multi-Agent Systems
D. Additional Experiments
Figure 9. Illustration of the accuracy gains via LatentMAS across the Sequential and Hierarchical MAS settings. LatentMAS consistently
improves system-level reasoning accuracy compared with single model and text-based MAS.
D.1. Performance of LatentMAS under Hierarchical MAS Setting
Table 3. Main results of LatentMAS on 6 general tasks under the Hierarchical MAS setting. We report accuracy, token usage, and
end-to-end speed, and highlight the performance gains following the same evaluation protocol as in Table 1.
Qwen3-4B Qwen3-8B Qwen3-14B
Tasks Metrics Improve Improve Improve
Single TextMAS LatentMAS Single TextMAS LatentMAS Single TextMAS LatentMAS
Hierarchical MAS Setting
Acc. 95.4 97.1 96.8 ↓ 0.3 95.6 98.2 98.3 ↑ 0.1 97.2 98.3 98.7 ↑ 0.4
ARC-E Token 724 2054 363 ↓ 82.3% 656 2237 308 ↓ 86.2% 608 2752 619 ↓ 77.5%
Speed 369 2239 591 ×3.8 404 3619 1779 ×2.0 551 7102 1884 ×3.8
Acc. 89.2 92.5 91.7 ↓ 0.8 91.0 93.3 93.9 ↑ 0.6 92.6 95.3 95.5 ↑ 0.2
ARC-C Token 913 2674 447 ↓ 83.3% 846 2854 344 ↓ 87.9% 773 2167 295 ↓ 86.4%
Speed 97 1275 299 ×4.3 266 2034 714 ×2.8 338 4283 1090 ×3.9
Acc. 82.4 89.4 88.4 ↓ 1.0 81.1 90.4 89.5 ↓ 0.9 83.7 90.8 91.6 ↑ 0.8
GSM8K Token 1136 3098 555 ↓ 82.1% 1280 2370 353 ↓ 85.1% 1118 3021 495 ↓ 83.6%
Speed 469 1878 360 ×5.2 449 1365 702 ×1.9 536 3675 1631 ×2.3
Acc. 47.7 65.0 67.3 ↑ 2.3 53.0 76.3 77.0 ↑ 0.7 64.7 78.0 78.3 ↑ 0.3
MedQA Token 2134 6702 1015 ↓ 84.9% 2098 6893 1007 ↓ 85.4% 1746 5473 899 ↓ 83.6%
Speed 236 1495 557 ×2.7 476 3387 964 ×3.5 1360 7591 1250 ×6.1
Acc. 63.5 69.3 70.6 ↑ 1.3 64.8 71.9 72.2 ↑ 0.3 68.5 73.0 73.8 ↑ 0.8
MBPP+ Token 1634 6782 1339 ↓ 80.3% 2053 7703 1264 ↓ 83.6% 1858 7458 1187 ↓ 84.1%
Speed 523 1766 489 ×3.6 1064 3898 1387 ×2.8 2410 9162 2507 ×3.7
Acc. 75.0 76.2 79.3 ↑ 3.1 74.4 76.8 78.0 ↑ 1.2 76.8 84.1 86.6 ↑ 2.5
HumanEval+ Token 2380 8127 1373 ↓ 83.1% 2507 8768 1274 ↓ 85.5% 2366 8114 1512 ↓ 81.4%
Speed 274 931 333 ×2.8 502 1809 439 ×4.1 1084 3988 1188 ×3.4
We report additional results on three Qwen3 backbones under the hierarchical MAS setting to complement the main
experiments. As shown in Table 3, LatentMAS consistently achieves higher or comparable system-level accuracy relative to
TextMAS while substantially reducing both end-to-end inference time and total system token usage. These results mirror the
trends observed in the sequential setting and confirm that latent working-memory transfer remains effective in hierarchical
collaboration, where multiple expert agents contribute to the final prediction.
22

## Page 23

Latent Collaboration in Multi-Agent Systems
D.2. LatentMAS on Llama Backbones
Table 4. Main results of LatentMAS on Llama3 families under Sequential and Hierarchical MAS settings. We report accuracy,
token usage, and end-to-end speed, and highlight the performance gains following the same evaluation protocol as in Table 1.
Llama-3.2-3B-Instruct Llama-3.1-8B-Instruct
Tasks Metrics Improve Improve
Single TextMAS LatentMAS Single TextMAS LatentMAS
Sequential MAS Setting
Acc. 79.2 80.1 80.4 ↑ 0.3 85.7 89.6 91.2 ↑ 1.6
ARC-E Token 236 1889 229 ↓ 87.9% 219 1981 228 ↓ 88.5%
Speed 155 1670 392 ×4.3 352 2708 516 ×5.2
Acc. 46.7 48.0 48.0 ↑ 0.0 59.0 65.0 65.3 ↑ 0.3
MedQA Token 405 1595 403 ↓ 74.7% 382 2354 316 ↓ 86.6%
Speed 51 236 85 ×2.8 112 589 182 ×3.2
Acc. 39.6 43.2 44.5 ↑ 1.3 51.2 55.4 56.7 ↑ 1.3
HumanEval+ Token 227 1042 338 ↓ 67.6% 161 740 218 ↓ 70.5%
Speed 64 199 77 ×2.6 80.6 333 101 ×3.3
Hierarchical MAS Setting
Acc. 79.2 81.6 82.3 ↑ 0.7 85.7 89.3 90.4 ↑ 1.1
ARC-E Token 236 956 177 ↓ 81.5% 219 1118 206 ↓ 81.6%
Speed 155 615 192 ×3.2 352 1832 669 ×2.7
Acc. 46.7 50.3 50.0 ↓ 0.3 59.0 64.3 67.7 ↑ 3.4
MedQA Token 405 1729 359 ↓ 79.2% 382 1847 191 ↓ 89.7%
Speed 51 282 73 ×3.9 112 464 204 ×2.3
Acc. 39.6 43.9 45.7 ↑ 1.8 51.2 54.2 55.4 ↑ 1.2
HumanEval+ Token 227 719 226 ↓ 68.6% 161 414 187 ↓ 54.8%
Speed 64 133 72 ×1.8 80.6 156 88 ×1.8
We report additional sequential and hierarchical MAS results on Llama-3 backbones to complement the main evaluations.
Consistent with Table 1 and 2 in the main paper, LatentMAS maintains higher or comparable accuracy relative to TextMAS
while consistently reducing system-wise token usage and inference time. Across tasks, LatentMAS preserves the same
qualitative trend observed for Qwen models, achieving faster end-to-end inference with markedly fewer decoded tokens,
indicating that LatentMAS exhibits strong generalizability across different model families.
D.3. Additional Efficiency Analyses on LatentMAS
x7.0
x5.7
Avg. x4.3 Faster Inference
x4.7
x4.1
x3.7
x3.2 x3.1 x3.4 x3.4
pu-deepS
dnE-ot-dnE
↓ 83.4%
↓ 82.7%
↓ 84.7%
Avg. 83.7% Fewer Tokens
↓ 81.7% ↓ 85.9% ↓ 83.5%
snekoT
fo
#
Figure 10. Efficiency gains of LatentMAS over single model and TextMAS under the Hierarchical MAS setting. Left: LatentMAS
achieves consistent faster end-to-end inference speed. Right: LatentMAS requires fewer system-wise token usage in total.
23

## Page 24

Latent Collaboration in Multi-Agent Systems
Table 5. Token usage of the final agent in MAS. LatentMAS consistently reduces the final decoding length compared with TextMAS.
Method Size ARC-C GSM8K MedQA HumanEval+ GPQA-D
TextMAS 4B 614 607 1539 2037 –
LatentMAS 4B 447 555 1015 1373 –
TextMAS 8B 685 412 1664 2167 4758
LatentMAS 8B 344 353 1007 1274 3395
TextMAS 14B 492 573 1303 2008 4517
LatentMAS 14B 295 495 899 1512 3606
Final-Agent Token Usage in LatentMAS. To further disentangle the source of token savings, we additionally measure the
output length of the final answering agent only. This analysis excludes intermediate agents and therefore directly compares
the final decoding stage of LatentMAS and TextMAS. As shown in Table 5, the final agent in LatentMAS consistently
generates fewer text tokens than the final agent in TextMAS across different model scales and tasks, with an average
reduction of 29.1%. This indicates that the token savings in LatentMAS come not only from eliminating intermediate
textual communication among agents, but also from shortening the final answer decoding process. This reduction occurs
since the final agent in TextMAS receives long textual reasoning traces from preceding agents and often continues the
text-based reasoning process before producing the answer. In contrast, the final agent in LatentMAS receives preceding
agents’ information through compact latent working memory and aggregates these latent thoughts before decoding the final
response. As a result, LatentMAS reduces both inter-agent communication tokens and the final-stage decoding length.
24

## Page 25

Latent Collaboration in Multi-Agent Systems
E. Detailed Analyses on LatentMAS
E.1. Additional Analyses on Input-Output Alignment
Input–Output Alignment
(Qwen3-8B)
ℎ "
! "
Density Embedding Space
Figure 11. Effectiveness of the input-output alignment W on 8B models. Unaligned output embeddings (h ) drift away from the
a t
original input embeddings (e ), while the aligned vectors (e ) realign with e , demonstrating that W preserves embedding-space
t t+1 t a
structure and prevents representation drift.
In Figure 11, we extend the input-output alignment analysis to additional 8B model scales beyond the Qwen3-4B and
Qwen3-14B examples shown in Figure 6. For Qwen3-8B models, the same pattern holds: unaligned latent outputs drift
away from the input embedding distribution, while applying the alignment matrix restores geometric and density-level
consistency with the original embedding space.
E.2. Quantifying Latent Thought Diversity.
While Figure 5 provides a qualitative visualization of the embedding distributions, we further quantify the representational
diversity of latent thoughts using a cosine-similarity-based metric. Specifically, for each method, we compute the average
pairwise cosine similarity among the generated embeddings. A lower value indicates that the representations are less
collapsed and more dispersed in the embedding space, corresponding to higher representational diversity.
Table 6. Diversity analysis of generated representations. We report the average pairwise cosine similarity among generated embeddings,
where lower values indicate less collapsed and more diverse representations.
Method Qwen3-4B Qwen3-8B Qwen3-14B
TextMAS 0.126 0.142 0.155
LatentMAS 0.104 0.093 0.108
As shown in Table 6, LatentMAS consistently achieves lower average cosine similarity than TextMAS across all three
Qwen3 backbones. This confirms that the latent thoughts are not merely aligned with the semantic region of text-based
reasoning but also span a broader and less concentrated representation space. Together with Figure 5, these results provide
both qualitative and quantitative evidence that latent thoughts preserve semantic consistency with text reasoning while
offering richer representational diversity.
E.3. Ablations on Latent Reasoning and Communication in LatentMAS
To isolate the contribution of each component in LatentMAS, we further conduct hybrid ablations by selectively replacing
either latent reasoning or latent communication with its text-based counterpart. Specifically, we compare LatentMAS with
the following two variants:
• Latent Reasoning + Text Communication, where each agent performs latent reasoning but communicates to the next
agent through decoded text, using only the last 128 decoded tokens;
• Text Reasoning + Latent Communication, where each agent performs standard text-based reasoning while transferring
intermediate information to the next agent through latent working memory.
25

## Page 26

Latent Collaboration in Multi-Agent Systems
As shown in Table 7, both hybrid variants underperform full LatentMAS across all evaluated tasks. This demonstrates that
the gains of LatentMAS cannot be attributed to only one component. Latent reasoning improves the expressiveness of each
agent’s internal computation, while latent communication preserves and transfers intermediate information without forcing
it through a compressed text interface. Combining both components enables end-to-end latent collaboration and yields the
strongest performance.
Table 7. Hybrid ablations on latent reasoning and latent communication using Qwen3-8B. Replacing either component with its text-based
counterpart leads to consistent performance drops, indicating that both components contribute to the overall gains of LatentMAS.
Method GSM8K MBPP+ MedQA
Latent Reasoning + Text Communication 85.5 66.4 65.9
Text Reasoning + Latent Communication 90.1 68.0 71.2
LatentMAS 93.8 74.6 75.3
F. How to Debug LatentMAS?
In LatentMAS “debug mode”, we introduce a switch that enables us to inspect the content of the latent thoughts of agents
without altering the overall LatentMAS pipeline. Specifically, when we switch on the “debug mode”, each agent should
simultaneously generate its latent thoughts and another text response within the same contextual information (e.g., agent
prompt and latent working memory). The latent thoughts are passed to the next agent, and the parallel text response serves
as a probe for the latent thoughts.
By checking the details of text response of intermediate agents, we can identify the root causes of errors in the final answer.
To illustrate this, we present two distinct case studies generated in “debug mode” using Qwen3-14B model on GSM8K
dataset, corresponding to a failure case and a success case below.
• Case 1: Incorrect Intermediate Text Leads to Error in LatentMAS Answer. In the first case of Section I, we
examine a problem where LatentMAS produces an incorrect final answer. According to the intermediate agent output,
we find the Refiner agent gives an incorrect numerical relationship (as highlighted in red), leading the final Solver agent
to utilize this erroneous dependency in its calculation.
• Case 2: Correct Intermediate Text Leads to Correct LatentMAS Answer. Conversely, in the second case of
Section I, all intermediate agents produce logically sound intermediate outputs, which successfully guides the final
agent to derive the correct answer.
Finally, to quantitatively validate that the text in “debug mode” serves as a faithful probe for LatentMAS, we conduct a
correlation study on 100 debug text - final answer pairs using Qwen3-14B model on GSM8K dataset, which consists of 80
instances with correct final answers and 20 instances with incorrect final answers. We manually annotated the correctness of
the each debug text and analyzed their correlation with the final correctness of LatentMAS.
Table 8. Correlation analysis between the correctness of intermediate text from “debug mode” and the final answers of LatentMAS. The
reported statistics demonstrate a high consistency between intermediate text correctness and final answer accuracy.
LatentMAS Final Answer
Correct (N = 80) Incorrect (N = 20)
Correct 96.2% (77/80) 10.0% (2/20)
Intermediate Debug Text
Incorrect 3.8% (3/80) 90.0% (18/20)
As shown in Table 8, we observe a high consistency between the correctness of the intermediate text and the final answer.
We find that 96.2% of the intermediate text are valid when the final answer is correct, while 90.0% contain errors when the
final answer contains error. The result shows that the correctness of intermediate text output aligns well with LatentMAS,
validating the “debug mode” as a reliable probe for our framework.
26

## Page 27

Latent Collaboration in Multi-Agent Systems
G. Additional Discussions on LatentMAS
Extension to Heterogeneous Agents. For simplicity and training-free purposes, we assume that all agents in LatentMAS
share the same shape of transformer layers. To relax this assumption and support heterogeneous agents in practice, one can
directly leverage prior studies on layer mapping and ensemble learning (Ainsworth et al., 2022; Wortsman et al., 2022) by
introducing a trainable adapter to align and share latent representations across different models.
In addition, a potential future direction is to adapt advanced post-training paradigms from text-based MAS to optimize
LatentMAS ’s latent collaboration protocols to unlock more effective multi-agent reasoning strategies.
H. Additional Related Works
Latent Reasoning in LLMs. Beyond explicit chain-of-thought (CoT) reasoning, recent work has explored the continuous
latent space of LLMs as an alternative reasoning medium (Hao et al., 2024; Chen et al., 2025b; Zhu et al., 2025), revealing
that hidden states encode richer semantic structures than what discrete token generation can express (Zhang et al., 2025;
Liu et al., 2024). Latent reasoning methods such as CoCoNut (Hao et al., 2024) and latent-space editing approaches (e.g.,
RepE (Zou et al., 2023), LoT (Fungwacharakorn et al., 2024)) demonstrate that manipulating internal representations can
guide models to reason more coherently and improve controllability without explicit token-level rationales. Other works (Li
et al., 2025a; Wang et al., 2025b; Shi et al., 2025) have also extended latent reasoning paradigms to vision-language models.
These methods leverage the structure of hidden states to perform interventions, such as steering, editing, or optimizing
latent trajectories, that shape downstream reasoning behavior while remaining agnostic to surface-level text. By operating
directly in the continuous space, they can induce reasoning steps that would be difficult or inefficient to express (Zhang
et al., 2025; Liu et al., 2024; Coda-Forno et al., 2025). Despite these benefits, existing techniques are confined to a single
model’s internal computations and do not consider interaction or coordination across multiple reasoning entities (Hao et al.,
2024). On the other hand, LatentMAS extends latent reasoning to a multi-agent setting, enabling each agent to generate
latent thoughts and propagate latent information to others. Our new framework shifts latent reasoning from an isolated
capability of individual models to a system-level collaborative mechanism.
Agentic Model Collaboration. With increasing algorithmic advances, LLM-based MAS have been applied across diverse
domains (Sagi & Rokach, 2018; Chen et al., 2025a; Yan et al., 2025), such as math and science reasoning (Pezeshkpour et al.,
2024; Yue et al., 2024; Wang et al., 2025a), open-domain question answering (Fourney et al., 2024; Wu et al., 2025), and
multi-modal GUI interaction (Zhang et al., 2024a; Ye et al., 2025b), demonstrating their versatility in complex real-world
settings. A large amount of prior works follow sequential planner-solver pipelines or hierarchical expert-summarizer
structures, which correspond to the two MAS settings we adopt for evaluating LatentMAS.
27

## Page 28

Latent Collaboration in Multi-Agent Systems
I. Case Study on Intermediate Error Tracking of LatentMAS
Incorrect Case with LatentMAS (Debug Mode)
Question:
In a room, there are various toys: 5 red cars, 3 action figures, and a doll. The doll costs as much as 3 action figures and one red car costs
4 dollars. How much are all toys worth, of an action figure costs 5 dollars?
Planner:
Okay, I need to make a detailed plan to solve the math problem.
1. Determine the cost of one action figure (given as $5).
2. Calculate the total cost of the doll; calculate the total cost of all red cars using the given cost of one red car ($4); calculate the total
cost of all action figures by multiplying the number of action figures by the cost of one action figure.
3. Add the costs of all toys (red cars, action figures, and the doll) to find the total value of all toys.
Critic:
The original plan from the Planner Agent was:
1. Identify the cost of action figure.
2. Calculate the total cost for each type by multiplying the quantity by the individual cost.
3. Sum up all the total costs to find the total value of all toys.
But the problem is that the Planner Agent’s plan didn’t account for the doll’s cost being dependent on the action figures and the red car.
So, the original plan might have missed that step. Let me check the original plan again.
But the doll’s cost isn’t given directly. It’s given in terms of other toys. So, the first step should be to calculate the doll’s cost based on
the given relationship. The original plan might have missed that step, assuming that the cost of each type is given directly, which is
not the case for the doll. Therefore, the plan needs to be adjusted to first calculate the doll’s cost using the given relationship before
proceeding to calculate the total cost for each type.
So, the feedback should point out that the plan didn’t account for the doll’s cost calculation based on the given relationship. The
user needs to first determine the doll’s cost by using the values of the action figures and the red car, then proceed with the rest of the steps.
Refiner:
The Original Plan is:
1. Identify the cost of each type of toy.
2. Calculate the total cost for each type by multiplying the quantity by the individual cost.
3. Sum up all the total costs to find the total value of all toys.
Feedback: The original plan fails to explicitly address the doll’s cost, which is not directly given but derived from the cost of 3 action
figures and 1 red car. To refine the plan:
• First, calculate the doll’s cost using the given relationship (3 × action figure cost + 1 × red car cost).
• Ensure all quantities (5 red cars, 3 action figures, 1 doll) are accounted for.
• Clarify that the total value includes all toys with their respective quantities and derived costs.
The Refined Plan is:
1. Determine individual costs.
2. Calculate total cost for each toy type.
3. Sum all totals.
Solver:
To determine the total value of all the toys, the doll costs as much as 3 action figures and 1 red car, so Doll = 3 · $5 + 1 · $4 = $19.
Then Red cars = 5 · $4 = $20, Action figures = 3 · $5 = $15, Doll = 1 · $19 = $19. Thus the total value is $20 + $15 + $19 =
$54. The final answer is 54 .
28

## Page 29

Latent Collaboration in Multi-Agent Systems
Correct Case with LatentMAS (Debug Mode)
Question:
Jean is two years older than Mark. Two years ago Mark was 5 years older than half Jan’s age. If Jan is 30 how old is Jean?
Planner:
1. Determine Mark’s current age by using the information about his age two years ago relative to Jan’s age.
2. Calculate half of Jan’s age two years ago and then determine Mark’s age at that time based on the given relationship.
3. Use the relationship between Jean and Mark’s ages to find Jean’s current age.
Critic:
The user wants to know Jean’s age based on the given information. The original plan provided by the Planner Agent was a bit
incomplete, so I need to figure out where it went wrong.
The original plan is a good start but lacks specific details on how to calculate Mark’s age two years ago and how to derive Jean’s age
from Mark’s current age. To improve, the plan should explicitly outline the mathematical operations needed, such as calculating half of
Jan’s current age, adding 5 years, adjusting for the two-year time difference, and then applying the age difference between Jean and
Mark. Additionally, the plan should emphasize verifying each step for consistency with the given information.
Refiner:
First, I need to break down the information step by step. Let’s start by noting down all the given information clearly. Jan’s current age is
30. That’s a concrete number, so that’s a good starting point.
Next, the problem mentions something about two years ago. So, I should probably calculate Jan’s age two years ago. Since Jan is 30
now, two years ago she was 30 − 2 = 28 years old. That seems straightforward.
Now, the problem says that two years ago, Mark was 5 years older than half of Jan’s age at that time. So, half of Jan’s age two years ago
is 28/2 = 14. Then adding 5 years to that gives 14 + 5 = 19. So, Mark was 19 years old two years ago. Therefore, Mark’s current age
would be 19 + 2 = 21 years old. Wait, that seems a bit young, but maybe that’s correct based on the given info.
Then, the problem states that Jean is two years older than Mark. If Mark is currently 21, then Jean would be 21 + 2 = 23 years old.
But wait, that seems like a possible answer, but I need to check if I did all the steps correctly.
Let me verify each step again. Jan is 30 now. Two years ago, she was 28. Half of 28 is 14. Adding 5 gives 19, which is Mark’s age
two years ago. Adding 2 years brings Mark’s current age to 21. Jean is two years older than Mark, so 21+2 = 23. That seems consistent.
Feedback: The original plan is a good start but lacks specific details on how to calculate Mark’s age two years ago and how to derive
Jean’s age from Mark’s current age. To improve, the plan should explicitly outline the mathematical operations needed, such as
calculating half of Jan’s current age, adding 5 years, adjusting for the two-year time difference, and then applying the age difference
between Jean and Mark. Additionally, the plan should emphasize verifying each step for consistency with the given information.
The Refined Plan is:
1. Identify known values.
2. Calculate Jan’s age two years ago.
3. Determine Mark’s age two years ago.
4. Calculate Mark’s current age.
5. Find Jean’s current age.
Solver:
According to the provided plan, to solve the problem step-by-step: Jan is currently 30, so two years ago Jan was 30 − 2 = 28. Half of
Jan’s age two years ago is 28/2 = 14, and Mark was 5 years older than that at the time, so Mark was 14 + 5 = 19 two years ago and is
therefore 19 + 2 = 21 now. Since Jean is 2 years older than Mark, Jean is 21 + 2 = 23 years old. Hence, the final answer is 23 .
29

## Page 30

Latent Collaboration in Multi-Agent Systems
J. Case Study on LatentMAS
Case Study (TextMAS on GSM8K)
Input Question: Debra is monitoring a beehive to see how many bees come and go in a day. She sees 30 bees leave the hive in the first
6 hours, and then she sees 1/2 that many bees return in the next 6 hours. She sees two times as many bees as she saw first leave the hive
fly from the hive and leave in the next 6 hours. Then every bee that left before that hadn’t already returned returns to the hive in the next
6 hours. How many bees did Debra see return to the hive in the last 6 hours of the day?
TextMAS Output
Planner Agent: Okay, let’s see. I need to figure out how many bees Debra saw return to the hive in the last 6 hours. Let me break down
the problem step by step. First, the problem mentions different time intervals: first 6 hours, next 6 hours, then the next 6 hours, and
finally the last 6 hours. So there are four 6-hour periods in a day, making up 24 hours total. Let me note each period and what happens
in each. Starting with the first 6 hours: Debra sees 30 bees leave the hive. Let me write that down as the first data point. So, Period 1
(0-6 hours): 30 bees leave. Then, the next 6 hours (Period 2: 6-12 hours), she sees half that number return. Half of 30 is 15. So, 15 bees
return in Period 2. Next, the third period (Period 3: 12-18 hours), she sees two times as many bees as she saw first leave the hive fly
from the hive and leave. The first time she saw 30 bees leave, so two times that is 60. So, 60 bees leave in Period 3. Then, the fourth
period (Period 4: 18-24 hours), every bee that left before that hadn’t already returned returns to the hive.
Critic Agent: The reasoning plan correctly identifies all four 6-hour periods and reaches the right final conclusion, but the
intermediate analysis contains several issues that reduce clarity and efficiency. First, the interpretation of the phrase “before that” is
revisited multiple times, even though it simply refers to the event in the previous sentence (the 60 bees leaving), meaning only bees that
left in Period 1 are relevant. Second, the plan temporarily entertains the possibility that bees may have left in Period 2, despite the
problem statement explicitly describing only returns during this interval. Third, the plan repeatedly questions whether the 15 returning
bees in Period 2 originate from the initial 30, even though the text directly states they are “half that many” and therefore unambiguously
tied to Period 1. These detours introduce redundancy and confusion. Overall, while the conclusion of 15 returning bees is correct, the
path to it is unnecessarily convoluted and would benefit from a more concise timeline-based analysis.
Refiner Agent: I will provide a refined plan based on previous agents’ information.
1. Identify the Time Periods and Events. We divide the day into four 6-hour intervals and record the events in each:
• Period 1 (0–6 hours): 30 bees leave the hive.
• Period 2 (6–12 hours): Half of those bees return, i.e., 15 bees.
• Period 3 (12–18 hours): Twice the number of bees that left in Period 1 leave the hive: 2 × 30 = 60 bees.
• Period 4 (18–24 hours): Every bee that left before Period 3 and has not yet returned comes back to the hive.
2. Track Bees Leaving and Returning.
• Period 1: 30 bees leave.
• Period 2: 15 of these 30 bees return, leaving 15 still outside the hive.
• Period 3: 60 new bees leave (these are not relevant for the final return count).
• Period 4: Only bees that left before Period 3 and have not returned will come back.
3. Determine Which Bees Return in Period 4. The only bees that left before Period 3 are the 30 from Period 1. Of these, 15 returned in
Period 2. Thus, the remaining 15 bees from Period 1 return in Period 4.
4. Return the Final Answer.
Solver Agent: Okay, let’s see. I need to figure out how many bees Debra saw return to the hive in the last 6 hours. Let
me break down the problem step by step.
First, the problem mentions different time intervals: first 6 hours, next 6 hours, then the next 6 hours, and finally the last 6 hours. So
there are four 6-hour periods in a day, making up 24 hours total. Let me note each period and what happens in each. Starting with the
first 6 hours: Debra sees 30 bees leave the hive. Let me write that down as the first data point. So, Period 1 (0-6 hours): 30 bees leave.
Then, the next 6 hours (Period 2: 6-12 hours), she sees half that number return. Half of 30 is 15. So, 15 bees return in Period 2. Next,
the third period (Period 3: 12-18 hours), she sees two times as many bees as she saw first leave the hive fly from the hive and leave. The
first time she saw 30 bees leave, so two times that is 60. So, 60 bees leave in Period 3. Then, the fourth period (Period 4: 18-24 hours),
every bee that left before that hadn’t already returned returns to the hive. So, bees that left in Period 1 and Period 2. But some of those
bees may have already returned in Period 2.
### Final Answer
Debra saw 15 bees return to the hive in the last 6 hours of the day. (✗ Wrong Final Answer)
30

## Page 31

Latent Collaboration in Multi-Agent Systems
Case Study (LatentMAS on GSM8K)
Input Question: Debra is monitoring a beehive to see how many bees come and go in a day. She sees 30 bees leave the hive in the first
6 hours, and then she sees 1/2 that many bees return in the next 6 hours. She sees two times as many bees as she saw first leave the hive
fly from the hive and leave in the next 6 hours. Then every bee that left before that hadn’t already returned returns to the hive in the next
6 hours. How many bees did Debra see return to the hive in the last 6 hours of the day?
LatentMAS Output
We are given a sequence of events involving bees leaving and returning to the hive over the course of a day, broken into 6-hour intervals.
According to the refiner’s plan, we need to track how many bees leave and return during each 6-hour interval, noting that 30 leave first,
15 return next, and 60 more leave afterward. In the final interval, all bees that had left and not yet returned came back, giving a total of
15 remaining from the first group, plus 60 from the third group, for a total of 75 returning bees.
Let’s break it down step by step based on the plan:
Step 1: Bees that leave in the first 6 hours. Debra sees 30 bees leave the hive during the first 6-hour period.
Step 2: Bees that return in the next 6 hours. In the second 6-hour period, she sees half as many bees return: 1 × 30 = 15 bees return.
2
Step 3: Bees that leave in the third 6-hour period. In the next 6 hours, twice the number from Step 1 leave: 2 × 30 = 60 bees leave.
Step 4: Bees that return in the final 6 hours. During the final 6 hours, every bee that had left earlier and had not yet returned comes
back to the hive.
We track the bees that left and determine which have already returned:
• From the first 6 hours: 30 bees left; 15 returned in Step 2, leaving 15 bees still out.
• From the third 6 hours: 60 bees left; none have returned yet.
Thus, the total number of bees returning in the final 6 hours is 15 + 60 = 75 bees.
###Final Answer: 75 (✓ Correct Final Answer)
To comprehensively learn how latent collaboration changes multi-agent reasoning dynamics, we conduct a detailed case study
on GSM8K using the Qwen3-14B backbone under the Sequential MAS setting. As shown in the example, TextMAS agents
rely on lengthy textual exchanges that often amplify early reasoning errors, misinterpretations by the planner propagate
through the critic and refiner, ultimately constraining the solver’s search space. In contrast, LatentMAS operates entirely
through latent working-memory transfer: each agent receives rich, continuous representations of prior reasoning rather
than brittle text, enabling later agents to reinterpret, refine, and correct upstream reasoning without inheriting surface-level
mistakes. This latent collaboration leads to more coherent intermediate steps, more stable numerical reasoning, and
ultimately yields the correct final answer, where TextMAS fails. The case study illustrates how LatentMAS mitigates error
compounding in multi-agent pipelines and demonstrates the qualitative advantage of latent over text-based communication.
31

## Page 32

Latent Collaboration in Multi-Agent Systems
K. Prompt Template for LatentMAS
Sequential LatentMAS Prompts on Numeric Tasks (GSM8K / AIME2024 / AIME2025)
System Prompt for All Agents:
You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
Prompt for Planner Agent:
You are a Planner Agent. Given an input question, design a clear, step-by-step plan for how to solve the question. Question: {question}
Your outlined plan should be concise with a few bulletpoints for each step. Do not produce the final answer. Now output your plan to
solve the question below:
Prompt for Critic Agent:
You are a Critic Agent to evaluate the correctness of the input plan for the given question and provide helpful feedback for improving
the plan. Question: {question}
The plan information is provided in latent KV representation format. Review the plan and question and output: (1) original plan contents
(2) constructive feedback on the original plan. Format your response as follows: Original Plan: [Copy the provided Planner Agent’s
plan here] Feedback: [Your detailed feedback to improve the plan here] Now, output your response below:
Prompt for Refiner Agent:
You are a Refiner Agent to provide a refined step-by-step plan for solving the given question. Question: {question}
You are provided with: (1) latent-format information: a previous plan with feedback (2) text-format information: the input question you
need to solve. Based on the input, write a refined and improved plan to solve the question. Make sure your output plan is correct and
concise. Now, output your refined plan below:
Prompt for Solver Agent:
You are a helpful assistant. You are provided with latent information for reference and a target question to solve. Target Question:
{question}
The latent information might contain irrelevant contents. Ignore it if it is not helpful for solving the target question. Now, reason step by
step and output the final answer inside \boxed{YOUR FINAL ANSWER}:
Sequential LatentMAS prompts for multiple-choice tasks (ARC-E, ARC-C, GPQA, MedQA)
System Prompt for All Agents:
You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
Prompt for Planner Agent:
You are a Planner Agent. Given an input question, design a clear, step-by-step plan for how to solve the question. Question: {question}
Your outlined plan should be concise with a few bulletpoints for each step. Do not produce the final answer. Now output your plan to
solve the question below:
Prompt for Critic Agent:
You are a Critic Agent to evaluate the correctness of the input plan for the given question and provide helpful feedback for improving
the plan. Question: {question}
The plan information is provided in latent KV representation format. Review the plan and question and output: (1) original plan contents
(2) constructive feedback on the original plan. Format your response as follows: Original Plan: [Copy the provided Planner Agent’s
plan here] Feedback: [Your detailed feedback to improve the plan here] Now, output your response below:
Prompt for Refiner Agent:
You are a Refiner Agent to provide a refined step-by-step plan for solving the given question. Question: {question}
You are provided with: (1) latent-format information: a previous plan with feedback (2) text-format information: the input question you
need to solve. Based on the input, write a refined and improved plan to solve the question. Make sure your output plan is correct and
concise. Now, output your refined plan below:
Prompt for Solver Agent:
You are a helpful assistant. You are provided with latent information for reference and a target question to solve. Target Question:
{question}
The latent information might contain irrelevant contents. Ignore it if it is not helpful for solving the target question. Your final answer
must be selected from A,B,C,D. For example \boxed{A}. Do not add any other contents inside the box. Now, reason step by step and
output the final answer inside \boxed{YOUR FINAL ANSWER}:
32

## Page 33

Latent Collaboration in Multi-Agent Systems
Sequential LatentMAS prompts for python coding tasks (MBPP-Plus, HumanEval-Plus)
System Prompt for All Agents:
You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
Prompt for Planner Agent:
You are a Planner Agent. Given an input question, design a clear, step-by-step plan for how to solve the question. Question: {question}
Your outlined plan should be concise with a few bulletpoints for each step. Do not produce the final answer. Now output your plan to
solve the question below:
Prompt for Critic Agent:
You are a Critic Agent to evaluate the correctness of the input plan for the given question and provide helpful feedback for improving
the plan. Question: {question}
The plan information is provided in latent KV representation format. Review the plan and question and output: (1) original plan contents
(2) constructive feedback on the original plan. Format your response as follows: Original Plan: [Copy the provided Planner Agent’s
plan here] Feedback: [Your detailed feedback to improve the plan here] Now, output your response below:
Prompt for Refiner Agent:
You are a Refiner Agent to provide a refined step-by-step plan for solving the given question. Question: {question}
You are provided with: (1) latent-format information: a previous plan with feedback (2) text-format information: the input question you
need to solve. Based on the input, write a refined and improved plan to solve the question. Make sure your output plan is correct and
concise. Now, output your refined plan below:
Prompt for Solver Agent:
You are a helpful assistant. You are provided with latent information for reference and a target question to solve. Target Question:
{question}
The latent information might contain irrelevant contents. Ignore it if it is not helpful for solving the target question. Your must reason
step-by-step to solve the **provided Target Question** witout outputing other irrelevant inforamtion. You must put all python code as
self-contained Python function in markdown code blocks. For example
‘‘‘python
import math
def add(a, b):
return a + b‘‘‘.
Do not add any other contents inside the markdown code block. Now, reason step by step and output the final answer inside ‘‘‘python
YOUR PYTHON CODE‘‘‘:
Hierarchical LatentMAS prompts for numeric-answer tasks (GSM8K, AIME2024, AIME2025)
System prompt for All Agents:
You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
Prompt for Math Agent:
You are a math agent. Given the input question, reason step-by-step and put the final answer inside \boxed{YOUR FINAL ANSWER}.
Question: {question}
Your response:
Prompt for Science Agent:
You are a science agent. Given the input question, reason step-by-step and put the final answer inside
\boxed{YOUR FINAL ANSWER}. Question: {question}
Your response:
Prompt for Code Agent:
You are a code agent. Given the input question, reason step-by-step and put the final answer inside \boxed{YOUR FINAL ANSWER}.
Question: {question}
Your response:
Prompt for Task Summarizer Agent:
You are a task summarizer. Given the input question and responses from previous agents as reference, reason step-by-step and put the
final answer inside \boxed{YOUR FINAL ANSWER}.
Question: {question}
Your response:
33

## Page 34

Latent Collaboration in Multi-Agent Systems
Hierarchical LatentMAS prompts for multiple-choice tasks (ARC-E, ARC-C, GPQA, MedQA)
System Prompt for All Agents:
You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
Prompt for Math Agent:
You are a math agent. Given the input question, reason step-by-step and put the final answer inside \boxed{YOUR FINAL ANSWER}.
Your final answer must be selected from A,B,C,D. For example \boxed{A}. Do not add any other contents inside the box. Question:
{question}
Your response:
Prompt for Science Agent:
You are a science agent. Given the input question, reason step-by-step and put the final answer inside
\boxed{YOUR FINAL ANSWER}. Your final answer must be selected from A,B,C,D. For example \boxed{A}. Do not
add any other contents inside the box. Question: {question}
Your response:
Prompt for Code Agent:
You are a code agent. Given the input question, reason step-by-step and put the final answer inside \boxed{YOUR FINAL ANSWER}.
Your final answer must be selected from A,B,C,D. For example \boxed{A}. Do not add any other contents inside the box. Question:
{question}
Your response:
Prompt for Task Summarizer Agent:
You are a task summarizer. Given the input question and responses from previous agents as reference, reason step-by-step and put the
final answer inside \boxed{YOUR FINAL ANSWER}. Your final answer must be selected from A,B,C,D. For example \boxed{A}.
Do not add any other contents inside the box. Question: {question}
Your response:
34

## Page 35

Latent Collaboration in Multi-Agent Systems
Hierarchical LatentMAS prompts for python coding tasks (MBPP-Plus, HumanEval-Plus)
System Prompt for All Agents:
You are Qwen, created by Alibaba Cloud. You are a helpful assistant.
Prompt for Math Agent:
You are a math agent. Given the input question, reason step by step and provide an efficient and self-contained Python function that
solves the following problem in a markdown code block. You must put all python code as self-contained Python function in markdown
code blocks. For example
‘‘‘python
import math
def add(a, b):
return a + b‘‘‘. Do not add any other contents inside the markdown code block.
Question: {question}
Your response:
Prompt for Science Agent:
You are a science agent. Given the input question, reason step by step and provide an efficient and self-contained Python function that
solves the following problem in a markdown code block.
You must put all python code as self-contained Python function in markdown code blocks. For example
‘‘‘python
import math
def add(a, b):
return a + b‘‘‘. Do not add any other contents inside the markdown code block.
Question: {question}
Your response:
Prompt for Code Agent:
You are a code agent. Given the input question, reason step by step and provide an efficient and self-contained Python function that
solves the following problem in a markdown code block.
You must put all python code as self-contained Python function in markdown code blocks. For example
‘‘‘python
import math
def add(a, b):
return a + b‘‘‘. Do not add any other contents inside the markdown code block.
Question: {question}
Your response:
Prompt for Task Summarizer Agent:
You are a task summarizer. Given the input question and responses from previous agents as reference, reason step by step and provide
an efficient and self-contained Python function that solves the following problem in a markdown code block.
You must put all python code as self-contained Python function in markdown code blocks. For example
‘‘‘python
import needed library
def FUNC NAME(a, b):
return a + b‘‘‘. Do not add any other contents inside the markdown code block.
Input Question: {question}
Your response:
35
