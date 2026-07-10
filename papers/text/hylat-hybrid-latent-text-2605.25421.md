# hylat-hybrid-latent-text-2605.25421

- Source PDF: `hylat-hybrid-latent-text-2605.25421.pdf`
- Extracted at UTC: `2026-07-09T05:56:53.553157+00:00`
- Pages: 15
- Title: HyLaT: Efficient Multi-Agent Communication via Hybrid Latent-Text Protocol
- SHA256: `e38b551aa3bdda6b88bbe241b153824ee01c0b622592d36cd6f5bc925950b923`

## Page 1

HyLaT: Efficient Multi-Agent Communication via
Hybrid Latent-Text Protocol
Xinyi Mou1*, Siyuan Wang2*, Zejun Li1, Yulan He3,4†, Zhongyu Wei1,5†
1Fudan University, 2The Chinese University of Hong Kong,
3King’s College London, 4The Alan Turing Institute, 5Shanghai Innovation Institute
{xymou20, zejunli20, zywei}@fudan.edu.cn,
siyuanwang@cuhk.edu.hk, yulan.he@kcl.ac.uk
Abstract (A) Text-based Communication (B) Latent Communication
Let’s analyze it carefully. <|Latent|> <|Latent|>
First, we … Plan A is better. <|Latent|> <|Latent|>
Communication protocol design is a cen- <|Latent|> <|Latent|>
I agree that. However, we
tral challenge in large language model-based Agent 1 still need… I support plan A. Agent 2 Agent 1 <|Latent|> <|Latent|> Agent 2
multi-agent systems. Existing single-channel Low efficiency Visible to all Efficient Invisible to users
approaches face an inherent communication Agent Response (C) Hybrid Dual-Channel Communication (Ours)
trilemma: text-based methods are interpretable V Ex e p r l b a o n s a e ti o C n o , ntent: <|Latent|> <|Latent|> <|Latent|>
b ef u fi t c v ie e n rb t o b s u e t , o w p h a i q le ue la a t n en d t- l s im pa i c te e d m to eth u o n d id s ir a e r c e - T D D C A h e e n o o d m s n u w u c o g c e i n h s t r i s e , t o t s c r n C , o a , E o t n L x i n c o i a s l t n m u t e i … s n n p io g t le , n : s, L ( a D t e N e n n a se t t u E in r m a fo l b r T m e e d a x t d t io in n g ) Agent 1 < < < | | | L L L a a a t t t e e e n n n t t t | | | > > > … … <|L S I a o s t u , e p P n p l t a | o n > rt A < P | i l s a La b n t e e A t n t . e t| r. > Agent 2
tional workflows. Inspired by multi-channel Information Channe l (V S is p ib e le c i i n a fo l r i m za a t ti i o o n n ) Efficient Key Information Visible
communication theory, we propose HyLaT, a
Figure 1: Comparison among different multi-agent
hybrid latent-text communication protocol that
communication paradigms. (A) Text-based commu-
transmits elaborate cognitive signals through
nication: fully readable but with a heavy efficiency bot-
a latent channel for efficiency, while express-
tleneck. (B) Latent communication: highly efficient but
ing concise critical signals in natural language
opaque to users. (C) Hybrid latent-text communication
to preserve interpretability and precision. We
(ours): balances efficiency and explainability through a
introduce a two-stage training framework com-
dual-channel design.
bining single-agent hybrid generation learn-
ing and multi-agent interactive co-training, en-
abling agents to generate and interpret hy- shapes system capability and scalability (Marro
brid messages across multiple rounds of in- et al., 2024; Zhang et al., 2024; Chen et al., 2025).
teraction. Experiments demonstrate that Hy-
Existing communication paradigms can be
LaT reduces communication overhead signifi-
broadly characterized as single-channel, either
cantly while maintaining competitive task per-
text or latent space. As illustrated in Figure 1A,
formance, with strong generalization and ro-
bustness across diverse settings 1. text-based methods (Du et al., 2023; Park et al.,
2023; Zhang et al., 2025) rely entirely on natural
language, which, while interpretable, leads to ver-
1 Introduction
bose messages with high token overhead. Recent
latent-space communication methods (Zou et al.,
Large Language Models (LLM)-based multi-agent
2025; Du et al., 2025; Fu et al., 2025; Wu et al.,
systems have shown strong performance in collabo-
2025) instead exchange internal representations
rative problem solving and social simulations (Guo
(Figure 1B), achieving dense and efficient transfer
et al., 2024; Mou et al., 2024a; Qian et al., 2024a).
but at the cost of interpretability. Latent signals are
In these systems, communication serves as the
opaque to external observers, limiting applicabil-
backbone of coordination, enabling agents to ex-
ity to scenarios where intermediate transparency is
change information, align on shared goals, and
essential, such as social simulation. Moreover, ex-
collectively reason across extended interactions.
isting latent-space methods are primarily designed
As systems scale to more agents and longer hori-
for single-shot or one-directional exchanges within
zons, the design of inter-agent communication pro-
a fixed workflow. This leaves multi-round interac-
tocols becomes a central challenge that directly
tive communication among multiple agents in more
*Equal contribution. realistic settings largely unsupported.
†Corresponding author.
The tension between interpretability and effi-
1Code is available at https://github.com/xymou/
hylat. ciency reflects a deeper structural limitation known
6202
yaM
52
]LC.sc[
1v12452.5062:viXra

## Page 2

as the agent communication trilemma (Marro • We identify channel multiplicity as a structural
et al., 2024): no single-channel protocols can si- resolution to the agent communication trilemma
multaneously optimize for efficiency, portability, and introduce HyLaT, a hybrid latent-text com-
and versatility. This suggests that the communica- munication protocol that enables agents to ex-
tion channel itself must be reconsidered. Inspired change information through complementary la-
by multi-channel communication theory (Shannon, tent and textual channels.
1948; Monge and Contractor, 2003) that different
• We propose a two-stage training approach com-
types of information are best transmitted through
bining single-agent hybrid learning and multi-
varied channels suited to their functional roles, we
agent interactive co-learning, enabling agents to
argue that the heterogeneous nature of agent mes-
generate and interpret both latent and textual mes-
sages calls for an analogous hybrid communication
sages in multi-round interactions.
design. Specifically, agent messages often contain
• Experiments demonstrate that HyLaT effectively
two functionally distinct types of information: (1)
balances communication efficiency and informa-
elaborate cognitive signals, such as explanations,
tion transparency, enabling scalable and inter-
intermediate reasoning, and contextual elaboration,
pretable multi-agent collaboration.
that are well-suited to compact latent-space rep-
resentations; and (2) concise but critical signals, 2 Methodology
such as answers, commitments, or final decisions,
that must remain interpretable to both agents and 2.1 Overview
human observers. This section details the proposed HyLaT frame-
work, designed to facilitate efficient and transpar-
To this end, we propose HyLaT, a Hybrid
ent communication among agents. As illustrated in
Latent-Text communication protocol that routes
Figure 2, we first define the dual-channel agent
each type of information through a dedicated chan-
communication protocol in Section 2.2. Further-
nel (Figure 1C). Dense intermediate information
more, we design a two-stage training framework to
flows through a latent channel for efficient machine-
empower existing models with dual-channel com-
to-machine transfer, while concise critical signals
munication capabilities. Stage 1: Single-Agent
are expressed in natural language to preserve inter-
Hybrid Generation Learning (Section 2.3) trains
pretability. This dual-channel design addresses all
each agent to generate hybrid outputs consisting
axes of the trilemma: the latent channel provides
of both text and latent representations; and Stage
efficiency, the text channel enables interoperation
2: Multi-agent Interactive Co-Training (Sec-
with agents using other protocols, and the combina-
tion 2.4) enables the shared backbone of multiple
tion provides versatility by supporting multi-round,
agents to jointly learn to interpret and respond to
multi-agent interaction, a setting that prior latent-
dual-channel information generated by others dur-
space methods largely cannot handle.
ing multi-turn interactions.
Realizing this design poses key training chal-
2.2 Hybrid Communication Protocol
lenges that agents need to learn generating hybrid
outputs and also interpreting latent vectors from Interactive Setup As illustrated in the top part
peers during multi-turn interactions. We address of Figure 2, we consider a multi-agent system of
this with a two-stage training framework. The N agents powered by a shared backbone model
first stage, single-agent hybrid generation learn- M , communicating over T interaction rounds. At
ing, equips the model to generate hybrid responses round t = 1, every agent receives a text context. At
from text-only inputs, using a cross-channel align- each subsequent round t > 1, agent i receives its
ment loss to transfer the semantic content of textual accumulated context together with the responses
elaborations into the latent space. The second stage, from all other agents in the previous round:
multi-agent interactive co-learning, enables agents (cid:104) (cid:105)
(t) (t−1) (t−1)
x = x , ⊕ o , t > 1 (1)
to jointly learn to interpret and respond across both i i j̸=i j
channels. We evaluate HyLaT on various tasks,
(t−1)
where x is agent i’s accumulated context up
demonstrating that it significantly reduces commu- i
(t−1)
nication overhead while maintaining strong task to round t − 1, o denotes the response from
j
performance and preserving interpretability. Our agent j at round t−1, and ⊕ denotes concatenation.
(t) (t)
contributions are summarized as follows: Agent i then generates a response o = M (x ).
i i

## Page 3

Discussion Topic Hybrid Communication Protocol Latent Token Text Token
…
Motivation Idea Thought Reply Hesitation Commitment Rationale Conclusion
Trend Question
Stage 1: Single-Agent Hybrid Generation Learnining Stage 2: Multi-agent Interactive Co-Training
Forward with Hybrid Responses ℒhybrid
𝑧1 … 𝑧𝑘 My answer is A … <Text> ℒ𝑎1 … <Text> ℒ𝑎1
LLM ℎ𝑆 𝑙 LLM
<Context> 𝑥 bot 𝑧1 … 𝑧𝑘−1 eot My answer is <Context> … <Text> Others said: … <Text> … <Text> …
Latent Signals
ℒalign
Forward with Textual Responses ℒtext <Context> … <Text> Others said: … <Text> … <Text> …
<Text Elaboration> 𝑒 My answer is A
LLM
LLM ℎ𝑙 𝑇
<Context>𝑥 <Text Elaboration> 𝑒 My answer is … <Text> ℒ𝑎2 … <Text> ℒ𝑎2
Figure 2: Overview of the proposed HyLaT framework. Agents exchange elaborate intermediate signals through a
latent channel and concise commitments through a text channel. The model is trained to generate hybrid content in
Stage 1 and to support multi-round hybrid communication in Stage 2.
Dual-Channel Response Format In HyLaT, the as supervision. Each turn pairs a text input x with a
output of agent i at round t consists of two parts target response including both a textual elaboration
from distinct channels: a latent component Z (t) = e and a critical output y, corresponding to the two
i
(z , . . . , z ) carrying elaborate cognitive signals, information types defined earlier.
1 k
(t) As shown in Figure 2 (bottom-left), each training
and a text component Y = (y , . . . , y ) carry-
i 1 m
step involves two forward passes over the input:
ing concise, interpretable conclusions:
(t) Forward with Hybrid Responses Since no
o = [⟨bot⟩ z , . . . , z ⟨eot⟩] ∥ [y , . . . , y ],
i 1 k 1 m ground-truth latent supervision exists, teacher forc-
(cid:124) (cid:123)(cid:122) (cid:125) (cid:124) (cid:123)(cid:122) (cid:125)
latent component text component ing is inapplicable to the latent component. The
(2)
model instead autoregressively generates k contin-
where the latent component consists of k contin-
uous latent vectors (Z = {z }k ) starting from
uous vectors produced by autoregressively propa- i i=1
⟨bot⟩, after which ⟨eot⟩ and target y are appended.
gating the model’s last hidden state, delimited by
The language modeling loss is computed over y:
two learnable special tokens ⟨bot⟩ and ⟨eot⟩. The
text component is a standard natural-language se- 1 (cid:88)
L = − log P (y | y , x, Z), (3)
quence generated after ⟨eot⟩. hybrid |y| i 1:i−1
i
Channel Specialization To balance communi-
L guides the model to derive y based on its
hybrid
cation efficiency with transparency, we retain the
self-generated intermediate latent information Z.
summary part of agent responses–such as final an-
swers and commitments–in the textual channel. Forward with Textual Responses To provide
Conversely, verbose information, including expla- meaningful supervision for Z, we follow Shen et al.
nations, elaboration, and reasoning processes, is (2025) and introduce a pure-text branch. In parallel
compressed into the latent component. This chan- with the hybrid forward pass, the model is trained
nel specialization capability is induced through the to generate r = [e, y] conditioned on x:
structure of training data described in Section 2.3.
1 (cid:88)
L = − log P (r | r , x), (4)
text i 1:i−1
2.3 Stage 1: Single-Agent Hybrid Generation |r|
i
Learning
L is optimized under teacher forcing to preserve
text
The goal of Stage 1 is to train the model to produce
the model’s ability to produce explicit elaborations.
well-formed hybrid outputs from text-only input,
preparing it for multi-agent interaction in Stage 2. Cross-Channel Alignment Based on the paral-
To achieve this, we construct single- and multi-turn lel forward passes, we transfer the information en-
user-assistant dialogues in single-agent scenarios coded in e into the latent space by aligning the

## Page 4

hidden activations of both branches at a shared tar- agents are exposed to peers’ latent vectors as part
get position. This position is defined as the token of their input context and learn to interpret them
immediately preceding the final answer (e.g., the to- while generating a proper hybrid response.
ken “is” in “My answer is A”), where all preceding
3 Experimental Setup
context about the elaboration must be compressed
before predicting the answer. This alignment is
3.1 Training Data Construction
applied across all L transformer layers:
Stage 1 To construct data required in Section 2.3,
L we collect datasets with detailed explanations or
1 (cid:88) (cid:13) (cid:104) (cid:105) (cid:13)
L = (cid:13)sg hl − hl (cid:13) , (5) reasoning chains as supervision for the latent com-
align L (cid:13) T S(cid:13) 2
l=1 ponent: CommonsenseQA (Talmor et al., 2019),
SocialIQA (Sap et al., 2019), WorldTree (Jansen
where hl and hl denote the hidden activations at
T S et al., 2018), PubMedQA (Jin et al., 2019),
the target position in the l-th layer for the textual
and StrategyQA (Geva et al., 2021). All se-
and the hybrid forward pass, respectively. sg(·) is
lected datasets contain detailed reasoning processes
the stop-gradient operation.
paired with concise final answers. This data-driven
Overall, the training loss for Stage 1 is:
approach allows channel specialization to emerge
naturally from the structure of the training exam-
L = αL + βL + γL , (6)
stage1 hybrid text align
ples, without requiring explicit routing annotations.
where α, β and γ are hyperparameters. This train-
Stage 2 We construct two types of multi-agent
ing process can be directly extended to multi-turn interaction data. (1) Refinement: using Llama-
dialogues by generating latent-channel responses
3.2-1B-Instruct and GPT-5 (Singh et al., 2025) to
turn-by-turn during the hybrid forward pass.
conduct simulated multi-agent debate on Stage 1
datasets, producing multi-round hybrid-output tra-
2.4 Stage 2: Multi-Agent Interactive
jectories that converge to a final answer, where
Co-Training
the answers of the first round may be incorrect.
Stage 2 trains agents to communicate under the Hy-
(2) Decomposition: Multi-hop questions sampled
LaT protocol, exposing each agent to latent vectors
from HotpotQA (Yang et al., 2018), 2WikiMul-
produced by its peers. The training data consists
tiHopQA (Ho et al., 2020), and GSM8K-Aug-
of multi-turn, multi-agent dialogues, including the
NL (Shen et al., 2025) are decomposed into parallel
topic context for the initial round x(1) and the tex-
sub-questions assigned across agents, who collabo-
tual responses {y (t) }N from N agents at each rate to reach a final answer. Dataset statistics and
i i=1
(t)
turn t. Similar to Stage 1, each response y is construction details are provided in Appendix A.1.
i
(t)
augmented with its corresponding elaboration e .
i 3.2 Implementation Details
Following the protocol formulated in Section 2.2,
(t) We use Llama-3.2-1B-Instruct (Grattafiori et al.,
we construct the input x for each agent at turn
i 2024) as the backbone for main experiments, while
t by integrating prior context and responses from
experiments on other backbones are provided in
other agents (Equation 1). Regarding the outputs,
Appendix B. Parameter-efficient fine-tuning is ap-
consistent with Stage 1, the textual forward pass
plied via LoRA (Hu et al., 2022) with rank r = 128
(t) (t)
utilizes the labeled [e , y ] under teacher-forcing
i i and α = 32, applied to all attention projection ma-
training, while the hybrid forward pass generates
trices. The number of latent vectors per turn is set
(t)
latent representations Z turn-by-turn.
i to k = 6. Both stages are trained on 2-turn dia-
Based on the constructed inputs and outputs, we
logues, with Stage 2 involving N =2 agents. All
calculate the loss L for each agent, then aggre-
stage1 training experiments are conducted on 8 NVIDIA
gate losses across all N agents:
H200 GPUs. For evaluation, each task is run inde-
pendently on a single H200 GPU. More details can
N
L =
1 (cid:88)(cid:16)
α L (i) + β L (i) + γ L (i)
(cid:17)
, be found in Appendix A.3.
stage2 N hybrid text align
i=1
(7) 3.3 Evaluation
(i) (i) (i)
where L , L , and L are respectively de- Tasks Following Du et al. (2023), we adopt
hybrid text align
fined in Equations 3–5. Through this joint training, multi-agent debate (MAD) as the primary task for

## Page 5

In-Domain Out-of-Domain Inference
Method Efficiency
Commonsense StrategyQA SocialIQA WorldTree PubMedQA MedQA ARC-E ARC-C
Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. # token time
Training-Free Single-Agent Baseline
Single-Agent 43.67 43.67 52.00 52.00 56.00 56.00 59.33 59.33 55.67 55.67 38.33 38.33 30.67 30.67 34.00 34.00 113.59 1.25
Training-Free Text-Based Communication Methods
NL 49.56 53.33 54.44 54.67 58.22 61.00 69.33 73.00 54.56 59.00 42.67 42.67 35.33 37.67 31.78 32.00 1247.50 13.15
AutoForm 47.78 50.33 54.56 55.00 59.89 63.00 67.11 68.67 56.11 57.00 44.11 46.00 35.89 35.33 33.56 34.00 1717.60 18.18
EcoLang 48.00 50.67 49.44 50.33 55.78 61.33 68.11 71.33 54.67 57.33 41.89 42.67 37.33 36.67 34.89 36.00 960.26 10.04
SDE 47.22 49.00 52.67 52.67 58.11 60.67 64.56 68.00 49.67 53.00 40.78 41.67 34.78 36.67 32.89 32.33 1316.20 14.48
Training-Free Latent-Space Communication Methods
Cipher 50.22 52.00 52.78 54.67 57.89 60.33 69.22 71.33 55.44 57.67 42.56 43.33 35.67 36.00 34.56 35.33 1137.89 11.58
LatentMAS-V 26.11 26.00 49.67 50.00 42.78 43.00 45.00 46.33 54.22 55.00 32.67 33.00 27.67 27.89 27.00 28.33 324.43 3.61
Training-Based Communication Methods
TextFullT 64.44 66.33 64.11 65.00 76.66 77.63 70.56 73.33 69.67 71.00 44.55 44.67 42.33 42.67 34.89 34.67 505.03 5.47
LatentFullT 56.00 56.33 63.11 63.33 80.78 80.67 68.56 68.33 66.11 66.67 42.11 42.33 38.89 38.67 33.78 34.00 57.00 0.70
HyLaT 63.78 64.33 64.67 65.33 82.56 83.00 69.22 69.00 67.44 67.33 42.11 42.33 39.00 39.33 33.89 34.00 72.01 1.47
Table 1: Experimental results of different methods. We report average accuracy (Avg.) and majority-vote accuracy
(Maj.) across agents, along with communication efficiency measured by average token count (# token) and wall-
clock time (time, in seconds). Bold denotes the best result and underline denotes the second best.
evaluation. We report results on both in-domain • SDE (Tang et al., 2025), where agents trans-
datasets encountered during training, i.e., Com- mit textual tokens alongside the model’s internal
monsenseQA, StrategyQA, SocialIQA, WorldTree, state-difference trajectory recorded in generation;
and PubMedQA, as well as several out-of-domain and (2) latent-space methods, including:
datasets, specifically MedQA (Jin et al., 2021), • Cipher (Pham et al., 2023) replaces textual mes-
ARC-Easy and ARC-Challenge (Clark et al., 2018). sages with semantic embedding vectors, com-
We follow Tang et al. (2025) to use the first 300 puted as the belief-weighted average over the
questions of each dataset to build MAD tasks. We output vocabulary distribution.
conduct evaluations on these tasks with 3 agents
• LatentMAS-V2 (Zou et al., 2025) has each agent
communicating over 2 turns.
autoregressively generate hidden-state vectors
from the final layer and pass its full key–value
Metrics We assess both task performance and
cache as a latent memory to the next agent.
communication efficiency. For performance, we
report the average per-agent accuracy (Avg.) across Since the aforementioned methods do not involve
all agents and the majority-vote accuracy (Maj.) ag- additional training, we introduce additional base-
gregated over all agents. For efficiency, we report lines, TextFullT and LatentFullT, to ensure a fair
the average number of tokens generated per ques- comparison. TextFullT is trained on the same data
tion across all communication rounds (# token), as HyLaT but restricts all communication, includ-
and the average running time per question. ing elaborations and conclusions to a single textual
channel. LatentFullT is trained on the same data
3.4 Compared Methods as HyLaT, but intermediate rounds communicate
purely through latent vectors, while only the final
We compare HyLaT against various methods de-
round retains a latent vector and a text output for
signed to optimize communication between agents.
supervision and evaluation.
The “Single-Agent” baseline serves as a lower
bound with no inter-agent communication. Multi-
4 Experimental Results
agent baselines are further categorized into: (1)
text-based methods, including: 4.1 Main Results
• NL uses unoptimised Natural-Language mes- Table 1 reports the overall performance of various
sages as the communication channel; methods, with several key findings highlighted:
• AutoForm (Chen et al., 2024) directly prompts I. Training-free methods fail to balance effi-
agents to communicate in structured language, ciency and performance. Among training-free
such as JSON and code;
2Since the original LatentMAS does not distinguish be-
• EcoLang (Mou et al., 2025) evolves efficient tween dialogue roles and does not support multi-round multi-
agent communication, we adapt its implementation to the
communication rules via a selection procedure
multi-round setting. This modification may not reflect its
and prepends them to agent instructions; intended use and could underestimate its performance.

## Page 6

Method Avg. Maj. # token time format err.(%) communication efficiency, maintaining task capa-
TextFullT 58.40 59.41 505.03 5.47 0.00 bilities of other multi-agent frameworks while
LatentFullT 56.17 56.29 57.00 0.70 0.00 operating at or below single-agent costs.
Ours 57.83 58.08 72.01 1.47 0.00
Variants based on Single-Channel Communication 4.2 Ablation Study
w/ pure text 56.93 57.00 639.18 13.18 3.28
w/ pure latent 50.28 50.33 56.09 1.16 6.12 Furthermore, we compare several variants of Hy-
Variants with Single-Stage Training LaT in Table 2 to validate the effectiveness of the
w/o Stage 1 38.43 38.58 102.59 1.38 9.13 proposed dual-channel communication framework.
w/o Stage 2 43.64 43.96 136.10 2.87 22.27
Effect of the Hybrid Channel Design We first
Table 2: Ablation study of the HyLaT framework. Re-
ported results are averaged over all datasets. ablate the channel composition by comparing two
degenerate variants: (1) w/ pure text uses our
trained model, rather than TextFullT, to generate
approaches: (1) The single-agent baseline achieves
natural language throughout all rounds, resulting in
the highest efficiency but suffers from poor perfor-
significantly higher token usage and inference time,
mance. (2) Text-based multi-agent methods yield
while yielding only marginal accuracy gains. This
strong results, yet offer limited room for efficiency
confirms that the latent channel is the primary
optimization–even the most efficient one, EcoLang,
driver of HyLaT’s efficiency advantage. (2) w/
requires 9× the duration of the single-agent base-
pure latent restricts intermediate rounds to latent-
line. (3) Latent-space methods are generally more
only outputs, reserving hybrid generation for the fi-
efficient, particularly LatentMAS-V, but at the cost
nal round only. Despite achieving the lowest token
of a severe performance drop. These observations
count, this variant suffers a notable drop in accu-
suggest that in a zero-shot setting, the fixed back-
racy and a higher format error rate, suggesting that
bone model significantly constrains agent behavior,
textual signals are crucial for agents to maintain
highlighting the necessity of additional training
coherent comprehension across multiple turns.
to co-optimize efficiency and performance.
In summary, the advantages of the two channels
are clearly complementary. Thus, the dual-channel
II. HyLaT strikes a balance between efficiency
design of HyLaT represents the optimal choice for
and performance. (1) Unparalleled efficiency.
balancing efficiency and performance.
HyLaT operates at execution times close to the
single-agent baseline while using only half the to- Effect of Two-stage Training The variant w/o
kens. Specifically, HyLaT improves token and Stage 1 skips the single-agent warm-up and directly
time efficiency by 10.6×/6.8× and 3.6×/2.5× over trains multi-agent interaction from scratch. With-
the most efficient text-based and latent-space base- out first learning to generate stable hybrid outputs
lines, respectively. (2) Task performance. Un- at the individual level, the latent representations
like LatentMAS-V, HyLaT preserves strong task produced early in training are noisy and unsta-
performance, achieving top-2 or comparative per- ble, and these errors propagate across rounds and
formance on both in-domain and out-of-domain agents, making optimization substantially more dif-
datasets. Notably, on SocialIQA, HyLaT clearly ficult and leading to negative results. The variant
outperforms all baselines by utilizing the latent w/o Stage 2 applies the Stage 1 checkpoint directly
channel to supplement information that text alone to multi-agent communication without co-learning.
cannot fully convey. (3) Advantage over Text- Since the model has never been exposed to peers’
FullT and LatentFullT. Although HyLaT slightly hybrid outputs during training, it frequently fails to
trails TextFullT on tasks requiring exhaustive struc- process latent vectors from other agents at test time,
tured reasoning, such as WorldTree and ARC-E, its resulting in a high format error rate (22.27%) and a
overall performance is highly comparable, while substantial drop in task performance. This confirms
incurring substantially lower time and token costs. that Stage 2 co-learning is essential for enabling
Meanwhile, LatentFullT only slightly improves robust multi-round hybrid communication.
computational efficiency, but its performance is in-
4.3 Compatibility and Robustness of the
ferior to that of HyLaT, suggesting that the interme-
Hybrid Protocol
diate text channel serves as a semantic anchor that
maintains contextual coherence across rounds. In Communication Protocol Compatibility A
summary, HyLaT effectively enhances multi-agent practical advantage of HyLaT’s hybrid design is

## Page 7

62.5 60.0 57.5
55.0 52.5
50.0
47.5
3× HyLaT 2× HyLaT 1× HyLaT 3× NL
1× NL 2× NL
)%( ycaruccA
.jaM
Maj. Acc 2× HyLaT 1× NL 62 Avg. # Tokens 1× HyLaT 2× NL 3× HyLaT 3× NL 60 58
56 54
52
50
0 0.01 0.050.1 0.5 1.0
Noise (log scale)
)%( ycaruccA
.jaM
1400 H NL yLaT 1200 TextFullT 1000
800 600
400
200
0
snekoT
# .gvA
58 56
54
52
50
2 3 4 5 Number of Agents (N)
(a)
(a) (b)
Figure 3: (a) Task performance and communication cost
under heterogeneous agent settings; (b) Majority voting
accuracy of HyLaT under increasing Gaussian noise
applied to latent vectors at inference time.
that the preserved text channel allows it to interop-
erate with agents using other communication pro-
tocols. To verify this, we construct heterogeneous
multi-agent groups mixing HyLaT- and NL-based
agents in varying proportions and evaluate task
performance and token usage. As shown in Fig-
ure 3(a), increasing the proportion of HyLaT agents
consistently reduces token consumption while im-
proving task performance, indicating that HyLaT
agents can effectively communicate with NL agents
through the shared text channel and guide the group
toward more efficient and accurate outcomes. This
compatibility is unavailable to pure latent commu-
nication methods, whose opaque signals cannot be
interpreted by agents operating in natural language.
Robustness to Latent Perturbation To assess
the stability, we inject Gaussian noise of varying
magnitude into each latent vector at inference time.
As shown in Figure 3(b), HyLaT maintains stable
performance for σ ≤ 0.5. This robustness stems
from the hybrid channel design: while the latent
channel carries intermediate reasoning, critical in-
formation such as the final answer is expressed
through the text channel, where discrete tokens
are more resilient to noise than continuous vectors,
safeguarding the output from total degradation.
Heterogeneous Agent Communication HyLaT
can be naturally extended to heterogeneous multi-
agent settings with minimal architectural modifica-
tion. During Stage 2 training, a lightweight MLP
adapter is introduced for each agent to project re-
ceived latent representations into its own seman-
tic space prior to fusion, thereby bridging the rep-
resentational gap between agents from different
model families. To validate this, we construct a
heterogeneous variant of HyLaT pairing Llama-
3.2-1B-Instruct and Qwen2-1.5B-Instruct as com-
municating agents. We evaluate this variant on the
MAD task under a 2-agent, 2-round setting. As
ycaruccA 58 56
54 52
50
48
2 3 4 5 Number of Rounds (T)
(b)
ycaruccA 2000
1500 1000
500
0
nekoT
# gvA
2500 2000
1500 1000
500
0
nekoT
# gvA
NL TextFullT HyLaT Avg. Accuracy Avg. # Token
Figure 4: We vary the number of agents (N) while fixing
the number of communication rounds to T=2 (left), and
vary the number of rounds (T) while fixing N=2 (right).
shown in Figure 8(a), the results demonstrate that
HyLaT successfully enables effective communica-
tion between agents from different model families,
confirming the generality of our hybrid latent-text
communication framework.
4.4 Scalability and Generalization Analysis
This section demonstrates that HyLaT can scale to
more complex agent interactions and generalizes
to other task scenarios, such as social simulation.
Scalability of Agent Count and Interaction
Rounds As shown in Figure 4, HyLaT’s token
usage remains relatively stable as both N and T in-
crease, while NL incurs rapidly growing overhead
and TextFullT shows moderate growth. On accu-
racy, increasing N or T does not consistently lead
to performance gains across all three methods, sug-
gesting that effective coordination in more complex
interactions generally remains challenging for 1B-
scale models. For HyLaT, the degradation is also
partially attributed to the gap between training and
evaluation configuration: as the model is optimized
for a small-scale setup where N = 2, T = 2, yet
evaluated under larger-scale conditions. To verify
this hypothesis, we constructed 3,400 training sam-
ples with 4-agent interactions and retrained Stage
2 of HyLaT. Figure 8(b) shows that the retrained
model (HyLaT-scaled) notably alleviates the perfor-
mance degradation. All these results demonstrate
that the efficiency advantage of HyLaT becomes
increasingly pronounced as interactions scale,
and that HyLaT can generalize to larger multi-
agent settings, which can be further enhanced
with correspondingly scaled training data.
Generalization to Social Simulation To further
explore the applicability of HyLaT to multi-agent
social simulation, we conduct the repeated trust
game from Xie et al. (2024), in which a trustor and
a trustee interact over 7 rounds: the trustor decides
how much to send each round, and the trustee de-
cides how much to return. As shown in Table 3,

## Page 8

Trust through these continuous representations. When
Method
Avg. Sent Avg. Returned # token time generating the critical textual output, the agent at-
tends to a mixture of the other agent’s textual re-
NL 3.82 5.10 2134.13 22.36
Autoform 4.56 7.75 4963.44 55.34 sponse and its own latent tokens, indicating that
Ecolang 4.05 7.13 776.81 8.43 the final decision integrates both explicitly com-
SDE 3.66 6.60 1717.69 18.82
municated content and implicitly encoded details.
TextFullT 3.22 9.04 797.94 8.45
HyLaT 3.53 10.84 182.00 3.49 Nevertheless, attention patterns alone do not repre-
sent causal explanations, and we will explore more
Human* 7.48 12.24 - -
rigorous interpretability analysis in future work.
Table 3: Results on repeated trust game for human trust
behavior simulation. Avg. Sent and Avg. Returned Probing the Latent Tokens To examine whether
represents the average amount sent by the trustors and latent tokens encode meaningful information, we
that returned by the trustees. Human*: estimated from visualize the final-step latent embeddings across
figures in (Cochard et al., 2004; Xie et al., 2024)
five datasets using PCA. As shown in Figure 9, the
latent representations exhibit clear domain-level
Answer the question based on the given context.
Context: Jordan gave people hugs whether he knew them or not. clustering despite the model never receiving ex-
Question Question: How would Others feel as a result?
Options: A. like kissing him; B. uncomfortable; C. happy plicit domain labels, demonstrating that the latent
Briefly explain your answer, and write your final choice on ...
channel organizes information by semantic con-
Gen. Pos. Top Attened Tokens
Round 1 '<|begin_of_text|>', '<bot>', ' parentheses', ' answer’, tent rather than surface form. The first two prin-
First Latent ' context’, ' example’, ' uncomfortable', ' enclosed'
cipal components account for 70.5% of the total
Round 1 '<|begin_of_text|>', 'is', '<latent_0>', '<eot>', ' answer', '
Text Answer parentheses’, 'B', ' uncomfortable', '<bot>', '<latent_4>', '<latent_5>' variance, indicating that the latent space organizes
'<|begin_of_text|>', '<bot>', ' answer', '<latent_5>', '<latent_3>', around a small number of dominant semantic di-
Round 2
'<latent_2>', '<latent_4>', '<latent_5>' , '<latent_1>' ,' parentheses',
First Latent rections rather than distributing information uni-
'<latent_4>', '<latent_1>', '<latent_2>', '<latent_5>'
formly. These observations suggest that latent to-
Round 2 '<|begin_of_text|>', '<eot>', ' answer', ' parentheses', 'A', ' B', ' B',
Text Answer '<latent_4>', '<latent_5>', '<latent_3>', '<latent_2>', ' B', '<latent_1>' kens are not merely auxiliary padding: they actively
Figure 5: Top attended words at various generation steps
encode task-specific semantics in a geometrically
during multi-agent communication. Tokens are color-
organized space, providing the downstream text
coded by source: black (instructions and questions),
decoder with structured, domain-relevant context.
gray (templates), green/blue (agent’s own latent/text),
and orange/red (other agents’ latent/text).
5 Related Work
both HyLaT and TextFullT achieve substantially 5.1 LLM-based Multi-agent Systems
higher returned amounts than other methods. We LLM-based multi-agent systems (MAS) have
attribute this to training on social reasoning data, demonstrated strong performance across various
which likely improves agents’ ability to understand scenarios (Guo et al., 2024; Mou et al., 2024a).
and respond to others’ intentions. HyLaT addition- Representative applications include debate (Du
ally achieves this with far lower communication et al., 2023; Tang et al., 2025), software devel-
cost, suggesting that hybrid communication can opment (Qian et al., 2024a), and social simula-
preserve the social reasoning capability acquired tion (Mou et al., 2024b). In these settings, agents
while substantially reducing overhead. communicate via natural language, structured mes-
sages, or shared memory to exchange information
4.5 Interpretability Analysis
and coordinate actions. However, as the number of
Cross-Agent Attention Analysis To understand agents and interaction rounds increases, the rapidly
how agents utilize information from both channels growing communication overhead poses efficiency
during communication, we analyze the learned at- challenges (Qian et al., 2024b; Chen et al., 2025).
tention in Figure 5. In Round 1, latent generation
5.2 Multi-agent Communication
primarily attends to keywords from the question
and task instructions, while text generation shifts To optimize the communication efficiency, early
attention toward the agent’s own latent tokens. In work on emergent communication (Lazaridou and
Round 2, a more striking pattern emerges: latent Baroni, 2020) showed that agents can develop their
generation is dominated by the other agent’s latent own compact protocols to solve cooperative tasks.
tokens from the previous round, providing direct ev- With the rise of LLMs, recent studies have inves-
idence that cross-agent information change occurs tigated how to optimize communication for both

## Page 9

efficiency and performance. Some works (Chen • Deployment scale. HyLaT’s modified gener-
et al., 2024; Mou et al., 2025; Chen et al., 2025) ation procedure is currently incompatible with
explore ways to compress or simplify message con- inference frameworks such as vLLM, preclud-
tent while maintaining task effectiveness. Other ing evaluation in large-scale or long-horizon
works prune message-passing graph (Zhang et al., multi-agent scenarios, where communication
2024) or reorganize protocols (Marro et al., 2024) efficiency becomes more important.
to reduce redundancy. Despite these advances,
• Text channel diversity. The expressive di-
most approaches are limited to either structured text
versity of the text channel is constrained by
or learned symbolic languages, which constrains
the scarcity of high-quality multi-agent com-
the density of information that can be exchanged.
munication data and human communication
5.3 Latent Reasoning and Communication data. Currently, our training set mainly in-
cludes QA-style debating data, and follow-
Recent work has explored latent representations as
ing Shen et al. (2025), we append a fixed
an alternative medium for reasoning in LLMs (Hao
answer prompt to align generation, both of
et al., 2024; Shen et al., 2025; Wei et al., 2025),
which limit the range of communicative be-
improving efficiency compared to explicit chain-
haviors the text channel can express. Explor-
of-thought approaches. While this line of research
ing richer and more diverse communication
mainly focuses on single-turn reasoning, it has re-
scenarios is an important direction for future
cently been extended to multi-agent collaboration.
work.
These methods typically enable semantic transfer
across models by sharing hidden states or project- • Latent interpretability. While HyLaT im-
ing KV-cache representations (Pham et al., 2023; proves upon pure latent communication by
Fu et al., 2025; Zou et al., 2025; Du et al., 2025). preserving observable intermediate text out-
Despite these advances, existing approaches gen- puts, the latent channel itself remains opaque.
erally rely solely on latent communication, which Decoding the semantic content of latent vec-
reduces interpretability and controllability. More- tors is still highly challenging, and how to
over, their thought-transfer mechanisms are often balance latent decodability with communica-
designed for sequential workflows and do not sup- tion performance is a non-trivial open problem
port multi-turn interactions, which are more com- that we leave for future work.
mon in general communication scenarios.
6 Conclusion
References
In this paper, we present HyLaT, a hybrid latent-
Weize Chen, Chenfei Yuan, Jiarui Yuan, Yusheng Su,
text communication protocol that transfers elabo- Chen Qian, Cheng Yang, Ruobing Xie, Zhiyuan Liu,
rate cognitive signals through a latent channel and and Maosong Sun. 2024. Beyond natural language:
Llms leveraging alternative formats for enhanced rea-
concise critical signals through a text channel. A
soning and communication. In Findings of the Asso-
two-stage training framework is proposed to enable
ciation for Computational Linguistics: EMNLP 2024,
agents to participate in effective multi-round hybrid pages 10626–10641.
communication. Experiments show that HyLaT
Weize Chen, Jiarui Yuan, Chen Qian, Cheng Yang,
dramatically improves communication efficiency
Zhiyuan Liu, and Maosong Sun. 2025. Optima: Op-
while maintaining competitive task performance. timizing effectiveness and efficiency for llm-based
multi-agent system. In Findings of the Association
Limitations for Computational Linguistics: ACL 2025, pages
11534–11557.
While HyLaT demonstrates promising results, sev-
Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot,
eral limitations remain. We discuss them below
Ashish Sabharwal, Carissa Schoenick, and Oyvind
and outline directions for future work. Tafjord. 2018. Think you have solved question an-
swering? try arc, the ai2 reasoning challenge. arXiv
• Model scale. Due to computational con-
preprint arXiv:1803.05457.
straints, all experiments are conducted on rel-
Francois Cochard, Phu Nguyen Van, and Marc Willinger.
atively small models (1B and 3B parameters).
2004. Trusting behavior in a repeated investment
Whether HyLaT’s benefits extend to larger-
game. Journal of Economic Behavior & Organiza-
scale models remains to be verified. tion, 55(1):31–44.

## Page 10

Yilun Du, Shuang Li, Antonio Torralba, Joshua B Tenen- Qiao Jin, Bhuwan Dhingra, Zhengping Liu, William Co-
baum, and Igor Mordatch. 2023. Improving factual- hen, and Xinghua Lu. 2019. Pubmedqa: A dataset for
ity and reasoning in language models through multia- biomedical research question answering. In Proceed-
gent debate. arXiv preprint arXiv:2305.14325. ings of the 2019 conference on empirical methods
in natural language processing and the 9th interna-
Zhuoyun Du, Runze Wang, Huiyu Bai, Zouying Cao, tional joint conference on natural language process-
Xiaoyong Zhu, Yu Cheng, Bo Zheng, Wei Chen, ing (EMNLP-IJCNLP), pages 2567–2577.
and Haochao Ying. 2025. Enabling agents to com-
municate entirely in latent space. arXiv preprint Angeliki Lazaridou and Marco Baroni. 2020. Emergent
arXiv:2511.09149. multi-agent communication in the deep learning era.
arXiv preprint arXiv:2006.02419.
Tianyu Fu, Zihan Min, Hanling Zhang, Jichao Yan,
Guohao Dai, Wanli Ouyang, and Yu Wang. 2025. Samuele Marro, Emanuele La Malfa, Jesse Wright, Guo-
Cache-to-cache: Direct semantic communication hao Li, Nigel Shadbolt, Michael Wooldridge, and
between large language models. arXiv preprint Philip Torr. 2024. A scalable communication pro-
arXiv:2510.03215. tocol for networks of large language models. arXiv
preprint arXiv:2410.11905.
Mor Geva, Daniel Khashabi, Elad Segal, Tushar Khot,
Peter R Monge and Noshir S Contractor. 2003. Theo-
Dan Roth, and Jonathan Berant. 2021. Did aristotle
ries of communication networks. Oxford University
use a laptop? a question answering benchmark with
Press, USA.
implicit reasoning strategies. Transactions of the
Association for Computational Linguistics, 9:346–
Xinyi Mou, Xuanwen Ding, Qi He, Liang Wang, Jing-
361.
cong Liang, Xinnong Zhang, Libo Sun, Jiayu Lin, Jie
Zhou, Xuanjing Huang, and 1 others. 2024a. From
Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri,
individual to society: A survey on social simulation
Abhinav Pandey, Abhishek Kadian, Ahmad Al-
driven by large language model-based agents. arXiv
Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten,
preprint arXiv:2412.03563.
Alex Vaughan, and 1 others. 2024. The llama 3 herd
of models. arXiv preprint arXiv:2407.21783.
Xinyi Mou, Chen Qian, Wei Liu, Xuanjing Huang, and
Zhongyu Wei. 2025. Ecolang: Efficient and effective
Taicheng Guo, Xiuying Chen, Yaqi Wang, Ruidi Chang,
agent communication language induction for social
Shichao Pei, Nitesh V Chawla, Olaf Wiest, and Xi-
simulation. arXiv preprint arXiv:2505.06904.
angliang Zhang. 2024. Large language model based
multi-agents: A survey of progress and challenges.
Xinyi Mou, Zhongyu Wei, and Xuan-Jing Huang. 2024b.
arXiv preprint arXiv:2402.01680.
Unveiling the truth and facilitating change: Towards
agent-based large-scale social movement simulation.
Shibo Hao, Sainbayar Sukhbaatar, DiJia Su, Xian Li,
In Findings of the Association for Computational
Zhiting Hu, Jason Weston, and Yuandong Tian. 2024.
Linguistics: ACL 2024, pages 4789–4809.
Training large language models to reason in a contin-
uous latent space. arXiv preprint arXiv:2412.06769. Joon Sung Park, Joseph O’Brien, Carrie Jun Cai, Mered-
ith Ringel Morris, Percy Liang, and Michael S Bern-
Xanh Ho, Anh-Khoa Duong Nguyen, Saku Sugawara,
stein. 2023. Generative agents: Interactive simulacra
and Akiko Aizawa. 2020. Constructing a multi-hop
of human behavior. In Proceedings of the 36th an-
qa dataset for comprehensive evaluation of reasoning
nual acm symposium on user interface software and
steps. In Proceedings of the 28th International Con-
technology, pages 1–22.
ference on Computational Linguistics, pages 6609–
6625. Chau Pham, Boyi Liu, Yingxiang Yang, Zhengyu Chen,
Tianyi Liu, Jianbo Yuan, Bryan A Plummer, Zhaoran
Edward J Hu, Yelong Shen, Phillip Wallis, Zeyuan Wang, and Hongxia Yang. 2023. Let models speak ci-
Allen-Zhu, Yuanzhi Li, Shean Wang, Liang Wang, phers: Multiagent debate through embeddings. arXiv
Weizhu Chen, and 1 others. 2022. Lora: Low-rank preprint arXiv:2310.06272.
adaptation of large language models. Iclr, 1(2):3.
Chen Qian, Wei Liu, Hongzhang Liu, Nuo Chen, Yufan
Peter Jansen, Elizabeth Wainwright, Steven Mar- Dang, Jiahao Li, Cheng Yang, Weize Chen, Yusheng
morstein, and Clayton Morrison. 2018. Worldtree: A Su, Xin Cong, and 1 others. 2024a. Chatdev: Com-
corpus of explanation graphs for elementary science municative agents for software development. In Pro-
questions supporting multi-hop inference. In Pro- ceedings of the 62nd annual meeting of the associa-
ceedings of the Eleventh International Conference on tion for computational linguistics (volume 1: Long
Language Resources and Evaluation (LREC 2018). papers), pages 15174–15186.
Di Jin, Eileen Pan, Nassim Oufattole, Wei-Hung Weng, Chen Qian, Zihao Xie, Yifei Wang, Wei Liu, Kunlun
Hanyi Fang, and Peter Szolovits. 2021. What disease Zhu, Hanchen Xia, Yufan Dang, Zhuoyun Du, Weize
does this patient have? a large-scale open domain Chen, Cheng Yang, and 1 others. 2024b. Scaling
question answering dataset from medical exams. Ap- large language model-based multi-agent collabora-
plied Sciences, 11(14):6421. tion. arXiv preprint arXiv:2406.07155.

## Page 11

Maarten Sap, Hannah Rashkin, Derek Chen, Ronan Guibin Zhang, Yanwei Yue, Zhixun Li, Sukwon Yun,
Le Bras, and Yejin Choi. 2019. Social iqa: Com- Guancheng Wan, Kun Wang, Dawei Cheng, Jef-
monsense reasoning about social interactions. In frey Xu Yu, and Tianlong Chen. 2024. Cut the
Proceedings of the 2019 conference on empirical crap: An economical communication pipeline for
methods in natural language processing and the 9th llm-based multi-agent systems. arXiv preprint
international joint conference on natural language arXiv:2410.02506.
processing (EMNLP-IJCNLP), pages 4463–4473.
Xinnong Zhang, Jiayu Lin, Xinyi Mou, Shiyue Yang,
Xiawei Liu, Libo Sun, Hanjia Lyu, Yihang Yang,
Claude Elwood Shannon. 1948. A mathematical theory
Weihong Qi, Yue Chen, and 1 others. 2025. Socio-
of communication. The Bell system technical journal,
verse: A world model for social simulation powered
27(3):379–423.
by llm agents and a pool of 10 million real-world
users. arXiv preprint arXiv:2504.10157.
Zhenyi Shen, Hanqi Yan, Linhai Zhang, Zhanghao Hu,
Yali Du, and Yulan He. 2025. Codi: Compress-
Jiaru Zou, Xiyuan Yang, Ruizhong Qiu, Gaotang Li,
ing chain-of-thought into continuous space via self-
Katherine Tieu, Pan Lu, Ke Shen, Hanghang Tong,
distillation. In Proceedings of the 2025 Conference
Yejin Choi, Jingrui He, and 1 others. 2025. Latent
on Empirical Methods in Natural Language Process-
collaboration in multi-agent systems. arXiv preprint
ing, pages 677–693.
arXiv:2511.20639.
Aaditya Singh, Adam Fry, Adam Perelman, Adam Tart,
Adi Ganesh, Ahmed El-Kishky, Aidan McLaughlin,
Aiden Low, AJ Ostrow, Akhila Ananthram, and 1 oth-
ers. 2025. Openai gpt-5 system card. arXiv preprint
arXiv:2601.03267.
Alon Talmor, Jonathan Herzig, Nicholas Lourie, and
Jonathan Berant. 2019. Commonsenseqa: A question
answering challenge targeting commonsense knowl-
edge. In Proceedings of the 2019 Conference of
the North American Chapter of the Association for
Computational Linguistics: Human Language Tech-
nologies, Volume 1 (Long and Short Papers), pages
4149–4158.
Yichen Tang, Weihang Su, Yujia Zhou, Yiqun Liu, Min
Zhang, Shaoping Ma, and Qingyao Ai. 2025. Aug-
menting multi-agent communication with state delta
trajectory. In Proceedings of the 2025 Conference on
Empirical Methods in Natural Language Processing,
pages 10230–10251.
Xilin Wei, Xiaoran Liu, Yuhang Zang, Xiaoyi Dong,
Yuhang Cao, Jiaqi Wang, Xipeng Qiu, and Dahua
Lin. 2025. Sim-cot: Supervised implicit chain-of-
thought. arXiv preprint arXiv:2509.20317.
Shiguang Wu, Yaqing Wang, and Quanming Yao. 2025.
Dense communication between language models.
arXiv preprint arXiv:2505.12741.
Chengxing Xie, Canyu Chen, Feiran Jia, Ziyu Ye,
Shiyang Lai, Kai Shu, Jindong Gu, Adel Bibi, Ziniu
Hu, David Jurgens, and 1 others. 2024. Can large lan-
guage model agents simulate human trust behavior?
arXiv preprint arXiv:2402.04559.
Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio,
William Cohen, Ruslan Salakhutdinov, and Christo-
pher D Manning. 2018. Hotpotqa: A dataset for
diverse, explainable multi-hop question answering.
In Proceedings of the 2018 conference on empiri-
cal methods in natural language processing, pages
2369–2380.

## Page 12

A Supplemented Implementation Details Dataset Type # samples
CommonsenseQA (Talmor et al., 2019) commonsense reasoning 3,600
StrategyQA (Geva et al., 2021) commonsense reasoning 1,800
A.1 Training Data Details
SocialIQA (Sap et al., 2019) social reasoning 1,800
WorldTree (Jansen et al., 2018) scientific question answering 2,204
Datasets of Stage 1 To support hybrid communi- PubMedQA (Jin et al., 2019) medical question answering 500
cation, Stage 1 training requires data that naturally
Table 4: Statistics of training datasets in Stage 1.
exhibits the two-part structure of HyLaT’s output:
an elaborate cognitive signal encoding dense inter-
Round 1: Initial Prompt
mediate reasoning and a concise signal expressing
the final response. Rather than constructing such Please answer the following question: {question}
data from scratch, we sample from training sets
First explain your reasoning, and provide
of existing datasets that already contain detailed
your final answer in the form \boxed{answer}, at
reasoning processes alongside short final answers, the end of your response.
treating the reasoning or explanation as the target
for the latent channel and the concise answer as
Round t > 1: Multi-Agent Interaction Prompt
the supervision target for the text channel. Based
on this, multiple QA pairs can be concatenated to These are the solutions from other agents:
One agent’s response: ˋˋˋ{agent_response}ˋˋˋ
form multi-turn dialogues. Dataset statistics are
[repeated for each other agent]
summarized in Table 4.
Using the responses from other agents as additional
Datasets of Stage 2 To support multi-round information, can you provide your answer to the
question? The original question is {question}.
multi-agent communication, we construct train-
ing data through multi-agent debate simulation Your final answer should be in the form
\boxed{answer}, at the end of your response.
along two complementary axes. (1) Refinement:
In this setting, agents independently answer the
same question in parallel and iteratively refine their
Figure 6: Prompts used for multi-agent interaction data
responses through discussion. To ensure that inter-
construction. Round 1 elicits an initial response with
agent communication provides meaningful infor- explicit reasoning. In subsequent rounds, each agent
mation gain, we deliberately avoid using a strong receives the responses of all other agents and is asked
model for all rounds, as it tends to produce cor- to produce a revised answer.
rect answers in the first round, leaving little room
for correction through communication. Instead,
more than 300 test examples, we evaluate on the
we adopt a weak-strong pairing strategy: the first
first 300 samples. Evaluation tasks are constructed
round is generated by Llama-3.2-1B and the second
from the test splits of Stage 1 datasets as in-domain
round by GPT-5, and dialogues in which the sec-
tasks, together with three additional out-of-domain
ond round answer remains incorrect are discarded.
datasets: MedQA (Jin et al., 2021), ARC-Easy and
We randomly sample questions from the Stage 1
ARC-Challenge (Clark et al., 2018). Unless other-
datasets and retain 3,960 valid dialogues; (2) De-
wise specified, all main experiments are conducted
composition: In this setting, agents collaboratively
with N = 3 agents over T = 2 interaction rounds.
solve a complex question by first addressing com-
During inference, we use the following generation
plementary sub-problems in parallel, then synthe-
configuration: temperature = 0.2, top-k = 20, top-
sizing their findings to produce a final answer in the
p = 0.9, with sampling enabled. The prompt tem-
second round. We sample 2,000 structurally paral-
plates for multi-agent debate are adapted from Tang
lel questions from HotpotQA (Yang et al., 2018),
et al. (2025) (Figure 7).
2WikiMultihopQA (Ho et al., 2020), and GSM8K-
AUG-NL (Shen et al., 2025), respectively. The
A.3 Implementation Details
prompts for data generation are provided in Fig-
ure 6. We follow previous work (Hao et al., 2024; Shen
et al., 2025) to set the number of latent vectors k =
A.2 Evaluation Details
6, and we list the hyper-parameter settings used in
We implement all the multi-agent communication Table 7. For Stage 2 training, we only supervise on
experiments using the framework provided by Tang the last turn, considering that the intermediate con-
et al. (2025). Following them, for datasets with clusions can be incorrect in the refinement data.

## Page 13

In-Domain Out-of-Domain Inference
Method Efficiency
Commonsense StrategyQA SocialIQA WorldTree PubMedQA MedQA ARC-E ARC-C
Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. # token time
Training-Free Single-Agent Baseline
Single-Agent 73.67 73.67 66.00 66.00 74.00 74.00 89.00 89.00 71.00 71.00 62.00 62.00 42.67 42.67 45.67 45.67 130.65 2.46
Training-Free Text-Based Communication Methods
NL 72.33 76.00 66.56 67.67 74.89 76.33 89.78 90.33 69.00 69.00 60.44 62.00 44.00 44.67 44.89 46.00 1094.83 19.13
AutoForm 68.11 69.00 70.33 72.67 75.56 76.00 88.78 90.00 69.56 69.33 65.00 68.00 42.56 43.00 44.22 44.33 1668.19 29.09
EcoLang 72.33 74.33 68.44 68.00 74.44 73.33 87.89 88.33 69.22 69.33 61.11 61.33 43.00 43.67 42.78 42.00 603.64 10.43
SDE 72.56 74.00 64.89 65.33 72.89 74.67 86.56 88.67 69.00 69.00 58.67 62.67 42.56 43.67 43.67 44.67 913.33 16.35
Training-Free Latent-Space Communication Methods
Cipher 71.67 73.67 66.89 69.33 74.89 75.00 86.56 87.00 67.89 69.33 59.56 60.33 44.11 44.33 46.11 48.00 1080.19 18.40
LatentMAS-V 70.78 72.17 59.67 61.67 73.00 74.33 84.56 84.67 62.44 64.00 60.11 61.67 41.78 41.33 42.89 44.33 570.63 10.58
Training-Based Communication Methods
TextFullT 72.22 72.67 77.22 78.67 84.78 84.33 87.67 89.33 74.00 75.33 60.44 62.00 43.22 43.33 44.89 46.00 748.74 12.79
LatentFullT 78.67 78.33 81.22 81.00 89.22 89.67 84.67 84.67 73.56 73.33 59.44 59.00 43.67 43.67 43.33 43.33 57.00 1.21
HyLaT 78.67 78.33 85.00 85.00 90.11 90.00 86.89 86.33 73.89 74.00 59.44 59.33 44.00 44.00 43.44 43.67 72.00 2.46
Table 5: Experimental results of different methods on Llama-3.2-3B-Instruct. We report average accuracy (Avg.)
and majority-vote accuracy (Maj.) across agents, along with communication efficiency measured by average token
count (# token) and wall-clock time (time, in seconds). Bold denotes the best result and underline denotes the
second best.
In-Domain Out-of-Domain Inference
Method Efficiency
Commonsense StrategyQA SocialIQA WorldTree PubMedQA MedQA ARC-E ARC-C
Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. Avg. Maj. # token time
Training-Free Single-Agent Baseline
Single-Agent 58.00 58.00 50.67 50.67 68.67 68.67 72.00 72.00 61.33 61.33 39.00 39.00 38.00 38.00 35.00 35.00 87.11 1.65
Training-Free Text-Based Communication Methods
NL 59.33 60.67 50.33 50.00 67.22 69.00 74.33 77.00 58.11 58.00 37.78 38.33 37.67 38.33 38.00 39.67 552.40 10.38
AutoForm 50.78 55.33 50.22 50.67 66.56 68.00 77.89 79.67 56.78 57.33 35.33 36.33 37.67 38.33 35.33 36.67 344.69 6.51
EcoLang 61.11 62.00 51.00 51.00 69.22 69.33 78.56 78.67 59.00 58.67 36.22 36.67 36.67 37.33 39.67 39.67 235.55 4.49
SDE 58.67 61.33 49.67 49.33 67.56 70.33 75.44 78.33 59.44 59.67 38.78 40.67 38.00 39.33 37.22 38.33 1514.63 10.29
Training-Free Latent-Space Communication Methods
Cipher 60.11 60.00 51.67 51.67 69.78 70.00 78.33 78.67 61.11 61.00 36.00 36.33 39.33 39.33 36.11 36.33 691.38 7.84
LatentMAS-V 4.56 4.00 0.33 0.00 13.78 13.00 10.33 10.00 21.00 20.33 13.89 12.33 4.33 3.67 4.33 3.00 587.99 11.86
Training-Based Communication Methods
TextFullT 62.56 62.00 55.11 55.00 76.11 76.00 78.33 78.67 59.11 60.33 38.67 39.00 38.56 40.00 37.67 39.33 545.30 10.06
LatentFullT 59.83 60.00 55.17 56.67 76.17 76.33 76.00 75.33 53.67 53.33 36.50 38.33 41.00 41.00 37.67 38.67 46.00 0.81
HyLaT 62.78 63.00 55.89 56.67 76.44 76.33 78.56 78.67 59.67 61.00 38.67 38.67 41.89 41.67 39.44 39.67 66.00 2.43
Table 6: Experimental results of different methods on Qwen2-1.5B-Instruct. We report average accuracy (Avg.) and
majority-vote accuracy (Maj.) across agents, along with communication efficiency measured by average token count
(# token) and wall-clock time (time, in seconds). Bold denotes the best result and underline denotes the second best.
Configuration Stage 1 Stage 2 B Supplementary Experimental Results
Model initialization Llama-3.2-1B-Instruct Stage 1 and Analysis
LoRA rank=128, alpha=32 rank=128, alpha=32
Global batch size 128 128 B.1 Heterogeneous Agent Communication
Peaking learning rate 8.00e-04 3.00e-04
Optimizer AdamW AdamW We implemented a heterogeneous variant of HyLaT
LR scheduler Cosine Cosine pairing Llama-3.2-1B and Qwen2-1.5B as commu-
Training epochs 3 3
Warmup ratio 0.03 0.03 nicating agents, with a lightweight MLP adapter
Precision bfloat16 bfloat16 bridging their respective latent spaces. We evalu-
α 1 1
ated this variant on the MAD task under a 2-agent
β 1 1
γ 20 20 and 2-round setting. Figure 8(a) shows that al-
though the heterogeneous setting sometimes does
Table 7: The detailed training hyper-parameters of Hy-
not surpass the best homogeneous configuration (2
LaT.
× stronger model), HyLaT consistently performs
well across all agent configurations.
B.2 Further Improve the Scalability
In Figure 4(a), we can observe that performance be-
gins to degrade when number of agents exceeds 3.
This degradation with more agents is attributed to

## Page 14

Initial Prompt
Can you answer the following question as accurately
as possible?
{question}
Explain your reasoning, and write your final answer
on a new line.
{format_instruction}
Debate Prompt
These are the solutions to the problem from other
agents:
{all_other_response}
Using the reasoning from other agents as additional
advice, can you give an updated answer? Exam-
ine your solution and that of other agents step by step.
The original question is {question}.
{format_instruction}
Figure 7: Prompt templates used for multi-agent debate
evaluation.
60
55
50
45
40
2×LLaMA 2×Qwen 1×LLaMA+1×Qwen
Agent Configuration
(a)
ycaruccA
NL TextFullT HyLaT
Accuracy Avg # Token
60
59 58
57
56
55
54
2 3 4 5
Number of Agents (N)
(b)
ycaruccA
HyLaT Accuracy
HyLaT-scaled Avg # Token
800
600
400
200
0
nekoT
#
gvA
140
120
100
80
60
nekoT
#
gvA
0.010
0.008
0.006 0.004
0.002
0.000
0.002
0.004
0.006 0.010 0.005 0.000 0.005 0.010
PC1 (50.5%)
(a)
Figure 8: (a) Performance of different communication
methods under homogeneous and heterogeneous agent
configurations; (b) Performance of HyLaT trained on
original vs. scaled data as the number of agents in-
creases.
two factors: (1) this phenomenon is a general char-
acteristic of multi-agent systems at this model scale
or for these tasks, rather than a limitation intro-
duced by our method alone, as TextFullT exhibits
the same degradation pattern when the number of
agents exceeds 3. (2) the degradation in HyLaT
is partly due to a gap between training and evalua-
tion: Our current training setup uses 2-agent inter-
action, which does not fully cover the distribution
of larger-scale agent configurations at evaluation
time. To verify this hypothesis and mitigate the
issue, we constructed 3,400 training samples with
4-agent interactions using the refinement method
in Sec 3.1, and retrained stage 2 of HyLaT. Results
in Figure 8(b) show that such training data notably
alleviates the performance degradation, confirming
)%0.02(
2CP
CommonsenseQA
PubMed 0.8
SocialIQA
Strategy WorldTree 0.6
0.4
0.2
0.0 1 2 3 4 5 6 7 8 9 10
Principal Component
(b)
oitaR
ecnairaV
denialpxE
Cumulative
Individual
Figure 9: (a) PCA analysis of final-step latent embed-
dings across five datasets. (b) Explained variance ratio
of the top-10 principal components of the latent embed-
dings.
that the scalability limitation stems from insuffi-
cient training coverage rather than a fundamental
constraint of our method.
B.3 Probing the Latent Tokens
To probe the semantic content encoded in HyLaT’s
latent channel, we collect 180 latent embeddings
produced by agents at the final interaction round
for each for the five datasets and apply PCA to
project them into two dimensions. The results are
visualized in Figure 9. As shown in the figure,
embeddings from the same dataset form relatively
compact clusters that are well-separated from those
of other datasets, suggesting that the latent vectors
capture dataset-specific semantic structure rather
than collapsing into an undifferentiated representa-
tion. This provides indirect evidence that the latent
channel encodes meaningful content that reflects
the nature of the task and communicative context,
even though the vectors are never decoded into
discrete tokens during inference.
B.4 Different Model Scales
We extend the experiments on larger Llama back-
bones, i.e., Llama-3.2-3B-Instruct. Results in Ta-
ble 5 show that HyLaT scales effectively to this set-
ting: task performance remains competitive across
most benchmarks, and the efficiency advantage is
fully preserved. The exception is WorldTree, where
the 3B model already achieves strong performance
under text-based communication, leaving limited
room for further improvement.
B.5 Different Model Families
We also conducted additional experiments using
Qwen2-1.5B-Instruct as the backbone. Results
in Table 6 show that HyLaT also demonstrates
effectiveness on Qwen, matching or outperform-
ing TextFullT across most tasks, while achiev-
ing dramatically higher communication efficiency.

## Page 15

We also note that LatentMAS-V fails to produce
meaningful results on most MAD tasks on Qwen,
suggesting that adapting the original approach to
multi-round multi-agent communication for differ-
ent models requires non-trivial effort. Overall, the
aforementioned results demonstrate that HyLaT
possesses superior cross-family generalization.
