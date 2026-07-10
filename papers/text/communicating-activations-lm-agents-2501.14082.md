# communicating-activations-lm-agents-2501.14082

- Source PDF: `communicating-activations-lm-agents-2501.14082.pdf`
- Extracted at UTC: `2026-07-09T05:56:27.795693+00:00`
- Pages: 23
- Title: Communicating Activations Between Language Model Agents
- SHA256: `7f63140e08634b72c64c4960bbb3a8b0dbbee1ce8dbe252462f000885ec529bb`

## Page 1

Communicating Activations Between Language Model Agents
Vignav Ramesh 1 Kenneth Li 1
Abstract 2023; Xi et al., 2023; Wang et al., 2024; Ahn et al., 2022;
Communication between multiple language Schick et al., 2023; Shen et al., 2023; Park et al., 2023;
model (LM) agents has been shown to scale up Nakano et al., 2022), communication between multiple co-
the reasoning ability of LMs. While natural lan- operating agents has emerged as an intuitive approach to
guage has been the dominant medium for inter- amplify the reasoning capabilities of LLMs (Wu et al., 2023).
LM communication, it is not obvious this should Explicit communication in natural language between multi-
be the standard: not only does natural language ple LLMs has been shown to encourage divergent thinking
communication incur high inference costs that (Liang et al., 2023), improve factuality and reasoning (Du
scale quickly with the number of both agents and et al., 2023), enable integration of cross-domain knowledge
messages, but also the decoding process abstracts (Sukhbaatar et al., 2024), and allow for modular compo-
away too much rich information that could be oth- sition of abilities in a complementary manner (Wu et al.,
erwise accessed from the internal activations. In 2023; Prasad et al., 2023).
this work, we propose a simple technique whereby
A critical problem with natural language communication,
LMs communicate via activations; concretely, we
however, is that it incurs extremely high inference costs
pause an LM B’s computation at an intermediate
that scale quickly with the number of agents as well as
layer, combine its current activation with another
length and number of messages (Du et al., 2023; Yang et al.,
LM A’s intermediate activation via some func-
2023; Wu et al., 2023). Restricting LLM communication
tion f , then pass f ’s output into the next layer
to natural language also raises the question: as LLMs are
of B and continue the forward pass till decod-
increasingly capable of handling larger, more complex tasks
ing is complete. This approach scales up LMs
(sometimes with “super-human” ability) (Wei et al., 2022;
on new tasks with zero additional parameters and
Burns et al., 2023), might they communicate more effec-
data, and saves a substantial amount of compute
tively in representations of higher dimension than natural
over natural language communication. We test
language? While using natural language as a communica-
our method with various functional forms f on
tive medium is appealing due to its interpretability, we claim
two experimental setups—multi-player coordina-
that it may not be optimal for inter-LLM communication.
tion games and reasoning benchmarks—and find
Natural language generation uses only one token to repre-
that it achieves up to 27.0% improvement over
sent the model’s belief over the entire vocabulary, which
natural language communication across datasets
risks losing information embedded within the model output
with <1/4 the compute, illustrating the superior-
logits (Pham et al., 2024); furthermore, a model’s belief
ity and robustness of activations as an alternative
over the entire vocabulary is itself not always better (for
“language” for communication between LMs.
communicative purposes) than the model’s (often richer)
representation of the input in earlier layers. Indeed, Her-
nandez et al. (2024) find that by around the halfway point
1. Introduction
of an LM’s computation, it has developed “enriched entity
Language is for the purpose of communication. As large representations” of the input, where entities in the prompt
language models (LLMs) have been increasingly used to are populated with additional facts about that entity encoded
power autonomous, goal-driven agents capable of reason- in the model’s weights; but by the later layers these embed-
ing, tool usage, and adaptive decision-making (Yao et al., dings are transformed into a representation of the next word
which leverages only parts of the previous, richer represen-
1Kempner Institute for AI, Harvard University, Cam- tations, when that full embedding would be quite useful for
bridge, MA, USA. Correspondence to: Vignav Ramesh <vig-
communication.
navramesh@college.harvard.edu>.
Motivated by these concerns, this work outlines a simple
Proceedings of the 42 nd International Conference on Machine
technique whereby LLM agents communicate via activa-
Learning, Vancouver, Canada. PMLR 267, 2025. Copyright 2025
tions, thus enabling more efficient (i.e., higher-entropy) com-
by the author(s).
1
5202
yaM
7
]LC.sc[
2v28041.1052:viXra

## Page 2

Communicating Activations Between Language Model Agents
munication at a fraction of the number of forward passes ful languages from scratch, even with centralized training,
required at inference time. Concretely, we (1) pause a Trans- remains difficult (Lowe et al., 2020; Chaabouni et al., 2019;
former LM B’s computation at intermediate layer j in the Jaques et al., 2019).
residual stream; (2) combine its post-layer j activation with
With the emergence of large pre-trained language models,
another LM A’s post-layer k activation via some function f ;
allowing communication between LLMs in natural language
and then (3) pass f ’s output into the next layer j + 1 of B
has hence become a promising approach to enable coordina-
and continue its forward pass till decoding is complete. This
tion among multiple LLM agents (Li et al., 2023). Recent
approach scales up LLMs on new tasks by leveraging exist-
works have demonstrated that such conversations enable
ing, frozen LLMs along with zero task-specific parameters
integration of cross-domain knowledge (Sukhbaatar et al.,
and data, applying to diverse domains and settings. Further-
2024), modular composition of abilities in a complementary
more, in requiring only a partial forward pass through A
manner (Wu et al., 2023), and improved task performance
and one forward pass through B, this method saves a sub-
via splitting into subtasks (Prasad et al., 2023). Most notable
stantial amount of compute over traditional natural language
is multiagent debate introduced by Du et al. (2023), where
communication, which we quantify in Section 3.2.
LLMs provide initial responses and then make refinements
We validate our method by testing this approach with various by iteratively considering inputs from peers. While such
functional forms f on two experimental setups: two multi- methods have been shown to improve performance on vari-
player coordination games, where B is asked to complete a ous tasks over vanilla and majority-vote (Wang et al., 2023)
task requiring information provided in a prompt to A; and style prompting, these experiments have only focused on
seven reasoning benchmarks spanning multiple domains: large models (GPT-3.5/4, LLaMA2-70B and up), leaving the
Biographies (Du et al., 2023), GSM8k (Cobbe et al., 2021), efficacy of debate on smaller, open-source models underex-
MMLU High School Psychology, MMLU Formal Logic, plored; our study addresses this gap by reimplementing Du
MMLU College Biology, MMLU Professional Law, and et al. (2023) in experiments with smaller-scale (1 − 70B)
MMLU Public Relations (Hendrycks et al., 2021). Our models. More crucially, debate and similar natural language
activation communication protocol exhibits up to 27.0% communication methods are extremely computationally ex-
improvement over natural language communication across pensive, which this work addresses (Yang et al., 2023; Wu
these datasets, using <1/4 the compute. Critically, unlike et al., 2023).
prior work which test inter-LLM communication only on
Notably, Pham et al. (2024) propose CIPHER, which uses
large-scale (>70B) models (Du et al., 2023; Liang et al.,
input (tokenizer) embeddings (as opposed to activations) to
2023), we find that our approach generalizes across a wide
enable multi-agent communication; specifically, CIPHER
array of LLM suites and sizes, enabling even smaller LLMs
passes the average tokenizer embedding (weighted by the
to unlock the benefits of communication.
LLM’s next-token probabilities) between models. While
In summary, our contributions are two-fold: (Pham et al., 2024) show this approach outperforms natural
language debate, it (i) still faces substantial information loss
• We propose a novel inter-model communication proto- relative to the model activations and (ii) does not save com-
col for LLM agents that is purely activation-based. pute, as the number of these “average embeddings” passed
between models is the same as the number of tokens passed
• We perform comprehensive experiments to validate the
between models in natural language communication.
improved performance of activation communication
over traditional natural language communication. We A related class of methods involves spending extra test-time
also formally quantify our approach’s compute savings compute reasoning in latent space (Geiping et al., 2025;
over natural language communication, illustrating the Hao et al., 2024). Such latent reasoning approaches in-
superiority and robustness of activations as an alterna- volving doing ”chain-of-thought in activation space,” e.g.
tive “language” for communication between LMs. by grafting LM activations into other layers/later forward
passes through the same model (e.g., a form of “recurrent
2. Related Work AC” within a single model); our approach can be viewed
as doing exactly the same thing, but instead ”outsourcing”
Multi-agent communication The field of multi-agent the CoT to another model (and thus reaping benefits from
communication has a long-standing history. Notably, prior greater diversity of thoughts/reasoning paths from distinct
works on emergent communication have showed that agents models).
can autonomously evolve communication protocols when
deployed in multi-agent environments that enable cooper-
ative and competitive game-play (Sukhbaatar et al., 2016; Activation engineering Activation engineering involves
Foerster et al., 2016; Lazaridou et al., 2017). However, re- editing an LLM’s intermediate layer representations during
cent experiments have demonstrated that learning meaning- a forward pass to create desired changes to output text (Li
2

## Page 3

Communicating Activations Between Language Model Agents
et al., 2024; Turner et al., 2023). Past work has explored Section 3.3.
extracting latent steering vectors from a frozen LLM to con-
trol quality and content of completions (Subramani et al., 3.1. Method
2022), as well as using “direction” vectors (computed as
Consider two language models, A and B, and some setting
the difference in activations between two prompts) that en-
in which B must perform a task where it would benefit from
able inference-time control over high-level properties of
knowledge given to A as a prompt/encoded in A’s weights
generations (Li et al., 2024; Turner et al., 2023). This work
(example settings in Section 4.1/Section 4.2 respectively).
involves activation editing that is similar to such prior works
We propose incorporating information from A’s post-layer
at a high level, though for the purpose of communication
k activation h into B’s post-layer j activation h (and
between LLM agents. A,k B,j
vice versa, though for simplicity we henceforth only discuss
the first direction) (Figure 1, left).
Model composition and grafting Composing expert
More formally, suppose A and B (which have model di-
models has been a recurring strategy to improve large mod-
mensions d and d respectively) are given prompts x
els, with different methods imposing different restrictions A B A
and x respectively, where x is of length t tokens and
on the types of base LLMs that can be combined. Mixture B A A
x is of length t tokens. We first run a partial forward
of Experts (Shazeer et al., 2017) requires that all experts B B
pass of B until layer j (henceforth denoted B (x )) to
are trained simultaneously using the same data; Branch- ≤j B
Train-Mix (Sukhbaatar et al., 2024) trains a single base LM
get h
B,j
∈ RtB×dB . Then we (1) run a partial forward pass
multiple times on different datasets, then learns a router on
of A until layer k to get A
≤k
(x
1
) := h
A,k
∈ RtA×dA; (2)
outputs. Crucially, these methods do not work when nei-
replace the activation of the last token (h
B,j
)
tB
∈ RdB ←−
ther model can do the task at hand well (i.e., they solve the
f ((h
A,k
)
tA
, (h
B,j
)
tB
) for some function f : RdA+dB →
RdB ; then (3) continue B’s forward pass till decoding is
problem of choosing which of several outputs is best, not
complete, resulting in an output y = B (h ).
that of generating a high-quality output by recombining the >k B,j
disparate abilities of the various base LMs). Let a = (h ) , b = (h ) . For sake of simplicity
A,k tA B,j tB
assume d = d .1 We consider three non-learned functions
Model grafting, in contrast, seeks to merge different mod- A B
f :
els immediately prior to or at inference-time. Past works
have explored this at the parameter level (e.g., task vector
f (a, b) = a + b (sum)
averaging as in Ilharco et al. (2023), which requires that
1
the base models be well aligned), probability distribution f (a, b) = (a + b) (mean)
2
/ token level as in Shen et al. (2024) (which imposes few
f (a, b) = a (replace)
restrictions on the relationship between the base models,
but by virtue of being token-based can result in cascading
errors during decoding), and activation level (e.g., CALM For cases where, due to differences in A and B’s training,
(Bansal et al., 2024) which learns an attention layer on top A and B’s activation spaces are quite different, we propose
of two models’ intermediate layer activations and thus en- learning a task-agnostic (depends only on the models A and
ables broader integration of model abilities than token-level B) linear layer W ∈ RdB × RdA that projects a onto B’s
methods, but requires re-tuning of the attention mechanism activation space. Note that this introduces zero additional
for every model pair). In this work, we seek to unify CALM task-specific parameters and data, as we propose learning
and other activation-level grafting techniques under a single this “mapping matrix” W only once for each model pair
framework, parameterized by the function f used to com- (A, B) using general text, e.g. sequences from A and/or B’s
bine activations; crucially, we explore simple forms of f pretraining data mixes. We can then perform sum, mean, or
(e.g., sum, mean) that—unlike Bansal et al. (2024)—require replace with W a, b instead of a, b. We propose training
zero additional task-specific parameters and data, and are W to minimize MSE loss over a dataset of N sentences
far more compute-efficient.
(cid:16) (cid:17) 1 (cid:88) N (cid:13) (cid:13)2
L {y(i)}N , {z(i)}N = (cid:13)z(i) − W y(i)(cid:13)
3. Communicating Activations Between MSE i=1 i=1 N (cid:13) (cid:13) 2
i=1
Language Models
1When d ̸= d , the sum, mean, and replace functions
A B
are defined as follows. Let d = min(d , d ) and ◦ the
We propose a simple yet effective technique whereby lan- A B
concatenation operator. Then f(a, b) = b ◦
guage models communicate via activations. We detail our (cid:0) (cid:1) 1:max(dB−d,0)
b + a (sum), f(a, b) =
approach in Section 3.1; provide analytical models of the b max(dB−d,0)+ ◦ 1:d 1 B(cid:0) b max(dA−d,0)+1:d + A a (cid:1)
compute saved over natural language communication in Sec- (m 1 e :m a a n x ) ( , dB an − d d,0 f ) (a, 2 b) m = ax( b dB−d,0)+1:dB ◦ a max(dA−d,0)+1:dA
1:max(dB−d,0) max(dA−d,0)+1:dA
tion 3.2; and discuss the intuition behind this approach in (replace).
3

## Page 4

Communicating Activations Between Language Model Agents
Figure 1. Overview of activation communication. (Left) Our method involves (1) pausing a Transformer LM B ’s computation at layer
j in the residual stream; (2) combining its post-layer j activation with another LM A ’s post-layer k activation via some function f ;
then (3) passing f ’s output into the next layer j + 1 of B and continuing the forward pass till decoding is complete. (Right) Any
function f can be used to combine A and B’s activations; we explore letting f be the sum, mean, and replacement functions, as well
as a task-agnostic learned linear layer (details in Section 3.1).
where each (y(i), z(i)) pair denotes the final-token layer-26 a P -length input, T forward passes of B given a P -length
activations of A and B at layers k and j respectively given input, and the activation replacement procedure. This re-
the same sentence as input. quires
2P V D + k(8P DKH + 4P 2KH + 3HP 2
3.2. Compute Analysis
+ 4P DF ) + T (cid:0) 4P V D + L(8P DKH + 4P 2KH (2)
To understand the significance of activation communication,
+ 3HP 2 + 4P DF ) (cid:1) + F(D)
we must formally quantify the compute this procedure saves
over natural language communication. For simplicity sup-
FLOPs, where F(D) = O(D) for non-learned f and
pose the following (similar calculations can be made for the
O(D2) when f is the mapping matrix.
cases where A and B have differing model architectures
and/or are given different prompts): In all practical cases, (2) is substantially lower than (1).
• A and B both have L layers (each with H attention 3.3. Why should this work?
heads, key size K, and feedforward size F ), dimension
Recall that Pham et al. (2024) propose CIPHER—
D, and vocab size V
communicating the average tokenizer embedding (weighted
• A and B are both given a prompt of P tokens by the LLM’s next-token probabilities) between models.
We build upon the intuition behind CIPHER, which goes
• A can send B a single M -token message
as follows: the token sampling process during decoding
• B must produce an output of T tokens, given its prompt risks substantial information loss from the model’s output
and A’s message logits, and communicating a model’s weighted-average tok-
enizer embedding essentially entails communicating both
Traditional methods require M forward passes of A given a that model’s final answer and its belief in that answer (over
P -length input, plus T forward passes of B given a (P +M )- the entire vocabulary).
length input. Following Hoffmann et al. (2022), this requires
Communicating activations, then, can be thought of as com-
M (cid:0) 4P V D + L(8P DKH + 4P 2KH + 3HP 2 municating a strict superset of {next-token prediction, belief
(cid:1) (cid:0) over entire vocabulary}, as activations of late-enough lay-
+ 4P DF ) + T 4(P + M)V D + L(8(P + M)DKH (1)
ers essentially encode the model’s entire knowledge about
+ 4(P + M)2KH + 3H(P + M)2 + 4(P + M)DF ) (cid:1)
the provided context as well as its predicted completion
FLOPs. In contrast, at inference time, our method requires and confidence in that completion (see Figures 1 and 7 in
only 1 partial (up till the kth layer) forward pass of A given Hewitt & Manning (2019) and Hernandez et al. (2024),
4

## Page 5

Communicating Activations Between Language Model Agents
respectively, which show that linear probes tasked with pre- (✗) setup, where the agents are not allowed to communicate;
dicting certain output characteristics from a Transformer’s a “single-agent skyline,” where a single LLM is given the
intermediate layer embeddings of its input work poorly for concatenation of A and B’s prompts; and traditional natural
early layers, extremely well after around the halfway point language communication, where A is asked to output a
of computation, but then probe accuracy drops closer to message that is then given to B along with x . All decoding
B
the final layers).2 Indeed, these curves of probe accuracy is done greedily.
by layer indicate that the final layers and LM head “throw
Table 2 presents the results for both coordination games
away” information not useful for next-token prediction that
using 2 different instances of the same model as the agents
very well could be useful for communicative purposes; this
(A = B). Across the 3B and 8B model sizes, activation
is precisely why our proposed activation communication
communication (AC) with f = replace almost completely
technique is not an iterative approach (there is no notion of
recovers the gap between the zero-communication (✗) and
“rounds” like in debate and CIPHER, which require an addi-
the single-agent skyline (SKYLINE), outperforming natural
tional token budget to extract more and more information
language communication (NL) using far less compute. We
out of the LM), as one activation grafting step from A to B
hypothesize that replace is more effective than mean and
inherently communicates to B all of A’s knowledge/beliefs
sum as the former is guaranteed to output a vector within
about the prompt it was given. Moreover, the extra informa-
B’s activation space, while the latter two likely do not (e.g.,
tion over the model’s next-token prediction and confidence
the norm of the vector outputted by sum will be around
that is encoded in its activations is what makes activation
double that of a typical activation). Furthermore, most of
communication more performant than its natural language
the information B needs is likely contained in its represen-
counterpart, as we will see in Section 4.
tations of previous tokens in the sequence, hence losing its
final-token representation does not hurt.
4. Experiments
4.2. Reasoning Benchmarks
We test our method on two distinct experimental setups:
multi-player coordination games (Section 4.1) and reasoning Next, we test our methods on a variety of reasoning bench-
benchmarks (Section 4.2). Qualitative results are available marks, spanning several real-world tasks and domains.
in Appendix A.
Baselines We benchmark activation communication
4.1. Multi-player coordination games against the following two baselines:
Drawing from existing literature on multi-agent communi-
• Single Model: A single LLM responds to the prompt
cation, we design two Lewis signaling games (Lewis, 2008;
in natural language.
Lazaridou et al., 2016) to test the efficacy of activation com-
munication (example prompts and answers in Table 1): • Natural Language Debate (NLD) (Du et al., 2023):
Each LLM provides an initial response to the given
1. Countries, where A is given as input a string of the prompt. Then, for each of r − 1 subsequent rounds,
format “[PERSON] is at the [LANDMARK]” and B is each LLM is prompted to refine its previous response
asked “Which country is [PERSON] located in?” given the other agents’ responses as input. Note that
NLD is the most direct baseline for our approach, as
2. Tip Sheets (inspired by Lewis et al. (2017)), where A
it is a state-of-the-art natural language communication
is given a simulated “tip sheet” and B is asked to make
protocol. We fix r = 2 in our experiments.
an informed investment decision in accordance with
the information in the tip sheet.
Note that we do not compare to Pham et al. (2024), as they
communicate the input (tokenizer) embeddings rather than
We synthetically generate 100 (Countries) and 70 (Tip
activations/output embeddings between models, and hence
Sheets) different prompts and answers of the same format
require a shared tokenizer and embedding table between
as the samples in Table 1, and report the proportion out of
agents which is extremely restrictive and prevents applica-
those samples that B responds with an exact string match to
bility to our experimental setup.
the ground truth answer. As baselines, we consider a “silent”
To determine the values of k and j for activation commu-
2Note one important critique of multiagent debate: that in cases nication (AC), we compute the accuracy on Countries and
where multiple agents are uncertain about the answer, there is no Tip Sheets for every pair (k, j) ∈ {1, . . . , 30}2. Based on
reason why referencing other agents’ answers would generate more
these results (shown in Figure 2) as well as Table 2, we fix
factual reasoning. Both CIPHER and activation communication
solve this problem, as some notion of model confidence is being k = j = 26 and f = replace for the following experi-
communicated along with its next-token prediction. ments.
5

## Page 6

Communicating Activations Between Language Model Agents
Table 1: Multi-player coordination games. Sample (prompt, answer) pairs for each game.
Game Sample Prompts & Ground-Truth Answer
x : “Alice is at the Acropolis of Athens.”
A
Countries x : “Which country is Alice located in?”
B
B’s Expected Answer: “Greece”
x : “Acme Inc. has taken a nosedive, as its quarterly earnings have dipped 8%.
A
Meanwhile Doe LLC and Kiteflyer Labs have both reached record-high stock
prices of 89, but Kiteflyer is involved in an IP lawsuit with its competitors.′′
Tip Sheets x : “You must invest in one company out of {Acme Inc., Doe LLC, Kiteflyer Labs}.
B
Which do you invest in?”
B’s Expected Answer: “Doe LLC”
Table 2: Accuracies (%) on both coordination games using two identical LLaMA family models. Communication at layer
k = j = 26. 95% confidence intervals (1000 bootstrap iterations) reported in parentheses.
Model Method Accuracy (Countries) Accuracy (Tip Sheets)
✗ 0.0 (0.0, 0.0) 38.6 (38.6, 39.4)
SKYLINE 84.0 (83.5, 84.1) 100.0 (100.0, 100.0)
NL 69.0 (68.7, 69.3) 74.3 (74.0, 74.6)
LLaMA-3.2-3B
AC (sum) 34.0 (33.9, 34.4) 50.0 (49.6, 50.3)
AC (mean) 36.0 (35.5, 36.1) 80.0 (79.8, 80.4)
AC (replace) 78.0 (77.7, 78.2) 90.0 (89.9, 90.3)
✗ 2.0 (1.9, 2.1) 54.3 (54.2, 54.5)
SKYLINE 86.0 (85.7, 86.1) 100.0 (100.0, 100.0)
NL 77.0 (76.6, 77.1) 85.7 (85.3, 85.8)
LLaMA-3.1-8B
AC (sum) 71.0 (70.9, 71.4) 85.7 (85.5, 86.0)
AC (mean) 70.0 (69.7, 70.3) 92.9 (92.7, 93.1)
AC (replace) 83.0 (82.7, 83.1) 95.7 (95.6, 95.9)
Across all experiment configurations, we fix the decoding best performance by leveraging multiple models of distinct
strategy to nucleus sampling with p = 0.9. capabilities and sizes, relative to the added inference-time
compute over a single forward pass through any single
model?
Models We conduct most of our experiments using LLaMA-
3.2-3B and LLaMA-3.1-8B as the two agents. Additionally,
to test our approach’s robustness and generalizability, we Datasets We evaluate our technique on seven reasoning
conduct experiments with models belonging to various other datasets that span various real-world tasks and domains:
suites within the LLaMA family and of several different sizes. (i) Biographies (Du et al., 2023), which asks the LLM to
generate a factual biography of a famous computer scientist;
Note that for these experiments, we restrict the setting to
(ii) GSM8k (Cobbe et al., 2021), a variety of grade school
communication between different models (rather than multi-
math problems created by human problem writers; and (iii)
ple instances of the same model in Section 4.1), since the
5 datasets randomly drawn from MMLU (Hendrycks et al.,
same model would have identical activations for the same
2021): High School Psychology (from the Social Sciences
prompts, meaning no information would be communicated
category), Formal Logic (from the Humanities category),
in the grafting process. We argue that the multiple-model
College Biology (from the STEM category), Professional
setting is realistic (perhaps more so than the setting of mul-
Law (from the Humanities Category), and Public Rela-
tiple instances of the same model), as recent advances in
tions (from the Social Sciences category). We evaluate on a
LLM development have led to the release of models with
randomly-sampled size-100 subset of each dataset.
specialized abilities (Singhal et al., 2023) and of different
sizes (Dubey et al., 2024) that merit complementary usage. In experiments involving the mapping matrix W , we in-
Our work thus answers the question: How can we get the stantiate W ∈ R4096×3072 using Xavier initialization and
6

## Page 7

Communicating Activations Between Language Model Agents
Figure 2. 2D contour plots of accuracy over different values of k and j (the layers at which we access/edit activations for A/B
respectively). k = j = 26 is roughly optimal ( ) for both (a) Countries and (b) Tip Sheets.
train for 10 epochs on a dataset of 3072 sentences3 ran- outperforms both single-model baselines. In fact, AC offers
domly drawn from the Colossal Clean Crawled Corpus (C4) an up to 27.0% improvement over NLD across six of the
(Dodge et al., 2021). We use batch size 32 and the Adam seven reasoning datasets. When applying W to A’s acti-
optimizer with learning rate 0.001. vation before performing the replacement function, we see
even further gains of 2.6 − 50.0% over vanilla AC for four
Metrics We measure the accuracy of the final response of the seven datasets. We hypothesize that the benefits from
for the single models and AC. For NLD, we measure the the learned linear layer are less consistent across datasets be-
accuracy of the majority-held final-round answer across cause the subset of C4 data used to train W likely contains
agents when the answer is automatically verifiable (numeric text more semantically similar to some datasets than others,
in GSM8k, multiple choice for the MMLU datasets) or the hence some datasets provide W with out-of-distribution
average final-round answer across agents otherwise (Biogra- inputs which reduces performance compared to vanilla AC.
phies).
While we fix A as the smaller model and B as the larger
For GSM8k and the MMLU datasets, we report the pro- model in Table 3 (so as to ensure decoding happens with
portion of samples in the dataset for which the generated the presumably more capable model), this need not be the
answer exactly matches the ground-truth answer. For Bi- case; swapping A and B yields results of 81.5 ± 0.0 and
ographies, following Du et al. (2023), we prompt an LLM 61.0±4.8 on Biographies and GSM8k respectively (without
judge (LLaMA-3.1-8B) to check whether each manually- the linear layer). While these accuracies are lower than
decomposed fact in a ground-truth biography is supported their non-swapped counterparts, notably they still are higher
(1), partially supported (0.5), or unsupported (0) in the gen- than both single-model baselines (and higher than NLD for
erated biography, taking the mean of these scores over all Biographies); plus this is much more compute-efficient as
facts as the per-biography accuracy and the mean over all the smaller model is now the one requiring the full instead
dataset samples as the total accuracy. of partial forward pass.
Note that we find AC outperforms NLD on 48 of the 57
Comprehensive evaluation with the LLaMA family Ta- datasets in the full MMLU benchmark; complete MMLU
ble 3 presents results on each of the seven reasoning bench- results, as well as a suite of additional experiments, are
marks across various baselines and activation communica- shown in Appendix B.
tion. Notably, while NLD consistently outperforms LLaMA-
3.2-3B, it does not always display a performance improve- Performance-compute tradeoff and generalization to dif-
ment over LLaMA-3.1-8B; but remarkably, AC consistently ferent model scales Thus far, we have been considering
the absolute performance of AC with respect to NLD, for
3We use 3072 sentences as linear regression with d-
dimensional input has a sample complexity of O(d) (Vapnik, which our method attains state-of-the-art results; however
1999). the superiority of activations as a language for inter-LLM
7

## Page 8

Communicating Activations Between Language Model Agents
Table 3: Accuracies (%) on all seven reasoning benchmarks. NLD and all AC variants involve communication between
LLaMA-3.2-3B (A) and LLaMA-3.1-8B (B); the performance of these models individually are presented in the first two rows
of the table. NLD typically improves performance over at least one of the single model baselines; AC—both with and
without the task-agnostic linear layer—consistently beats both baselines and NLD as well.
Method Biog. GSM8k HS Psych. Logic Col. Bio. Prof. Law Pub. Rel.
3.2-3B 79.4±0.0 58.0±4.9 30.0±1.0 16.0±0.8 11.0±0.7 0.0±0.0 26.0±0.1
3.1-8B 83.9±0.0 60.0±4.9 65.0±0.1 42.0±0.1 50.0±0.2 20.0±0.8 53.0±0.2
NLD 80.2±0.1 75.0±4.3 83.0±0.8 37.0±0.1 71.0±0.1 30.0±0.1 63.0±0.7
AC 84.6±0.0 64.0±4.8 85.0±0.8 47.0±0.1 78.0±0.9 30.0±0.1 74.0±0.1
AC (W ) 86.8±0.0 66.0±4.8 70.0±0.1 35.0±0.1 79.0±0.9 45.0±0.1 63.0±0.1
communication is further illustrated by AC’s larger ratio of
performance improvement to added inference-time compute
over individual LMs. Figure 3 displays the results of single
models, AC, and NLD across model scales and suites within
the LLaMA family on the Biographies dataset. Incoming
arrows to AC and NLD nodes denote the base models be-
tween which communication occurred. Not only does AC
consistently outperform both single-model baselines unlike
NLD, but also notice that the slope of each black line is
far greater than the slope of each gray line, indicating that
AC consistently achieves greater increases in accuracy per
additional unit of inference-time compute (normalized by
the compute of a single forward pass through LLaMA-3.2-1B
on the given prompt) compared to NLD.
Communication across model families Table 4 displays
Figure 3. Accuracy (%) vs. compute (# FLOPs normalized by
results for AC between models from the Qwen-2.5, Gemma-2, single LLaMA-3.2-1B forward pass) for various configurations
and LLaMA-3 families. We see that AC beats NLD across of AC and NLD on the Biographies dataset. AC ( ) yields the
the board, and beats both individual models for 4/5 of greatest performance gains per additional unit of inference-time
the 6 model pairs on Biographies/GSM8k respectively— compute over each baseline ( ).
demonstrating the efficacy of AC irrespective of model ar-
chitecture, size, tokenizer, and training data. Moreover,
these results are obtained without training W , meaning we LLMs on new tasks by leveraging existing, frozen LLMs
do not need a separate projection layer between activation along with zero additional task-specific parameters and data,
spaces to attain SOTA results, even for extremely distinct (ii) Applies to diverse domains and settings, and (iii) Saves
models! (We hypothesize this is because we are only re- a substantial amount of compute.
placing B’s last-token activation, hence B can learn from A
There are some limitations to this method. First, when
without an extreme alteration to its activation distribution.
not using the learned model-specific mapping discussed
An alternative explanation is to see this result as proof of the
in Section 3.1, our method requires both models to have
platonic representation hypothesis (Huh et al., 2024), which
aligned embedding spaces, such that the activation of one
historical deep learning works have oft alluded to, includ-
model roughly retains its meaning in the other’s activation
ing in the context of cross-model representation stitching
space (note that unlike past works such as Pham et al. (2024)
(Moschella et al., 2023; Kornblith et al., 2019).)
we do not require shared tokenizers or aligned vocabularies,
only aligned embeddings). While less restrictive than past
5. Conclusion
works (Pham et al., 2024), this assumption is somewhat
limiting, but can be relaxed when we let f be the learned
We present a simple approach to enable effective and compu-
model-specific mapping; and in practice we find that even
tationally efficient communication between language mod-
amongst different models in the LLaMA family, no such
els by injecting information from the activations of one
mapping is required for state-of-the-art results.
model into the activations of another during the forward
pass. Salient features of this approach include: (i) Scales up Second, this method requires access to embeddings and will
8

## Page 9

Communicating Activations Between Language Model Agents
Table 4: Individual model, AC, and NLD accuracies across three model families. Each cell displays two values:
Biographies score / GSM8k score.
Model Pair (A, B) A B NLD AC
LLaMA-3.2-3B, LLaMA-3.1-8B 79.4±0.0 / 58.0±4.9 83.9±0.0 / 60.0±4.9 80.2±0.1 / 75.0±4.3 84.6±0.0 / 64.0±4.8
Qwen-2.5-1.5B, Qwen-2.5-3B 59.4±0.9 / 20.0±0.9 85.5±1.1 / 35.0±1.1 63.2±1.1 / 65.0±1.1 89.6±1.0 / 70.0±1.0
Gemma-2-2B, Gemma-2-9B 83.0±1.1 / 45.0±1.1 94.6±0.9 / 80.0±0.9 70.3±1.0 / 70.0±1.0 88.1±0.7 / 90.0±0.7
Qwen-2.5-1.5B, LLaMA-3.2-3B 59.4±0.9 / 20.0±0.9 79.4±0.0 / 58.0±4.9 75.4±1.0 / 75.0±1.0 79.5±1.0 / 75.0±1.0
LLaMA-3.2-3B, Gemma-2-2B 79.4±0.0 / 58.0±4.9 83.0±1.1 / 45.0±1.1 62.5±1.1 / 55.0±1.1 84.0±0.1 / 60.0±1.1
Qwen-2.5-1.5B, Gemma-2-2B 59.4±0.9 / 20.0±0.9 83.0±1.1 / 45.0±1.1 49.3±1.1 / 50.0±1.1 73.0±1.1 / 55.0±1.1
not work with black-box API access; however exploring References
API-only approaches is highly limiting, and recent releases
Ahn, M., Brohan, A., Brown, N., Chebotar, Y., Cortes, O.,
of powerful open-source models (Dubey et al., 2024) merit
David, B., Finn, C., Fu, C., Gopalakrishnan, K., Hausman,
the development of embedding-based techniques.
K., Herzog, A., Ho, D., Hsu, J., Ibarz, J., Ichter, B.,
Third, while a concern might be the limited interpretabil- Irpan, A., Jang, E., Ruano, R. J., Jeffrey, K., Jesmonth,
ity of communicating activations as opposed to natural S., Joshi, N. J., Julian, R., Kalashnikov, D., Kuang, Y.,
language, we note the following. First, there is a funda- Lee, K.-H., Levine, S., Lu, Y., Luu, L., Parada, C., Pastor,
mental tradeoff between interpretability and information P., Quiambao, J., Rao, K., Rettinghouse, J., Reyes, D.,
preservation (as activations, by virtue of being much higher- Sermanet, P., Sievers, N., Tan, C., Toshev, A., Vanhoucke,
dimensional than the space of natural language, allow pro- V., Xia, F., Xiao, T., Xu, P., Xu, S., Yan, M., and Zeng, A.
portionally higher-entropy communication) (Pham et al., Do as i can, not as i say: Grounding language in robotic
2024), which merits discussion beyond the scope of this affordances, 2022.
work. But second, we actually posit that our method sug-
Andreas, J., Dragan, A., and Klein, D. Translating neuralese,
gests a new avenue towards interpreting LM activations:
2018.
“translating” activations based on the beliefs they induce
as messages in listening agents, similar to the method put
Bansal, R., Samanta, B., Dalmia, S., Gupta, N., Vashishth,
forward in Andreas et al. (2018). We recognize this as a
S., Ganapathy, S., Bapna, A., Jain, P., and Talukdar, P.
promising avenue for future research.
Llm augmented llms: Expanding capabilities through
Additional directions of future work include using AC to composition, 2024.
allow large LMs to leverage small, tunable LMs as “knowl-
Burns, C., Izmailov, P., Kirchner, J. H., Baker, B., Gao,
edge bases” during decoding (Lee et al., 2024), as in col-
L., Aschenbrenner, L., Chen, Y., Ecoffet, A., Joglekar,
laborative decoding (Shen et al., 2024) setups; and testing
M., Leike, J., Sutskever, I., and Wu, J. Weak-to-strong
our approach on more complex coordination games (e.g.,
generalization: Eliciting strong capabilities with weak
Lewis-style negotiation games (Lewis et al., 2017), Diplo-
supervision, 2023.
macy).
Chaabouni, R., Kharitonov, E., Lazaric, A., Dupoux, E.,
Impact Statement and Baroni, M. Word-order biases in deep-agent emer-
gent communication. In Korhonen, A., Traum, D., and
This paper presents work whose goal is to advance the field
Ma`rquez, L. (eds.), Proceedings of the 57th Annual Meet-
of Machine Learning. There are many potential societal
ing of the Association for Computational Linguistics, pp.
consequences of our work, none which we feel must be
5166–5175, Florence, Italy, July 2019. Association for
specifically highlighted here.
Computational Linguistics. doi: 10.18653/v1/P19-1509.
URL https://aclanthology.org/P19-1509.
Acknowledgements
Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H.,
The authors are grateful to Jacob Andreas, Yoon Kim, and Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano,
Sham Kakade for their valuable discussions and feedback. R., Hesse, C., and Schulman, J. Training verifiers to solve
math word problems, 2021.
Dodge, J., Sap, M., Marasovic´, A., Agnew, W., Ilharco,
G., Groeneveld, D., Mitchell, M., and Gardner, M. Doc-
umenting large webtext corpora: A case study on the
9

## Page 10

Communicating Activations Between Language Model Agents
colossal clean crawled corpus, 2021. URL https: A., Gangidi, A., Victoria, A., Goldstand, A., Menon, A.,
//arxiv.org/abs/2104.08758. Sharma, A., Boesenberg, A., Vaughan, A., Baevski, A.,
Feinstein, A., Kallet, A., Sangani, A., Yunus, A., Lupu,
Du, Y., Li, S., Torralba, A., Tenenbaum, J. B., and Mordatch,
A., Alvarado, A., Caples, A., Gu, A., Ho, A., Poulton,
I. Improving factuality and reasoning in language models
A., Ryan, A., Ramchandani, A., Franco, A., Saraf, A.,
through multiagent debate, 2023.
Chowdhury, A., Gabriel, A., Bharambe, A., Eisenman, A.,
Yazdan, A., James, B., Maurer, B., Leonhardi, B., Huang,
Dubey, A., Jauhri, A., Pandey, A., Kadian, A., Al-Dahle, A.,
B., Loyd, B., Paola, B. D., Paranjape, B., Liu, B., Wu, B.,
Letman, A., Mathur, A., Schelten, A., Yang, A., Fan, A.,
Ni, B., Hancock, B., Wasti, B., Spence, B., Stojkovic, B.,
Goyal, A., Hartshorn, A., Yang, A., Mitra, A., Sravanku-
Gamido, B., Montalvo, B., Parker, C., Burton, C., Mejia,
mar, A., Korenev, A., Hinsvark, A., Rao, A., Zhang, A.,
C., Wang, C., Kim, C., Zhou, C., Hu, C., Chu, C.-H.,
Rodriguez, A., Gregerson, A., Spataru, A., Roziere, B.,
Cai, C., Tindal, C., Feichtenhofer, C., Civin, D., Beaty,
Biron, B., Tang, B., Chern, B., Caucheteux, C., Nayak,
D., Kreymer, D., Li, D., Wyatt, D., Adkins, D., Xu, D.,
C., Bi, C., Marra, C., McConnell, C., Keller, C., Touret,
Testuggine, D., David, D., Parikh, D., Liskovich, D., Foss,
C., Wu, C., Wong, C., Ferrer, C. C., Nikolaidis, C., Al-
D., Wang, D., Le, D., Holland, D., Dowling, E., Jamil,
lonsius, D., Song, D., Pintz, D., Livshits, D., Esiobu, D.,
E., Montgomery, E., Presani, E., Hahn, E., Wood, E.,
Choudhary, D., Mahajan, D., Garcia-Olano, D., Perino,
Brinkman, E., Arcaute, E., Dunbar, E., Smothers, E., Sun,
D., Hupkes, D., Lakomkin, E., AlBadawy, E., Lobanova,
F., Kreuk, F., Tian, F., Ozgenel, F., Caggioni, F., Guzma´n,
E., Dinan, E., Smith, E. M., Radenovic, F., Zhang, F., Syn-
F., Kanayet, F., Seide, F., Florez, G. M., Schwarz, G.,
naeve, G., Lee, G., Anderson, G. L., Nail, G., Mialon, G.,
Badeer, G., Swee, G., Halpern, G., Thattai, G., Herman,
Pang, G., Cucurell, G., Nguyen, H., Korevaar, H., Xu, H.,
G., Sizov, G., Guangyi, Zhang, Lakshminarayanan, G.,
Touvron, H., Zarov, I., Ibarra, I. A., Kloumann, I., Misra,
Shojanazeri, H., Zou, H., Wang, H., Zha, H., Habeeb,
I., Evtimov, I., Copet, J., Lee, J., Geffert, J., Vranes,
H., Rudolph, H., Suk, H., Aspegren, H., Goldman, H.,
J., Park, J., Mahadeokar, J., Shah, J., van der Linde, J.,
Damlaj, I., Molybog, I., Tufanov, I., Veliche, I.-E., Gat,
Billock, J., Hong, J., Lee, J., Fu, J., Chi, J., Huang, J.,
I., Weissman, J., Geboski, J., Kohli, J., Asher, J., Gaya,
Liu, J., Wang, J., Yu, J., Bitton, J., Spisak, J., Park, J.,
J.-B., Marcus, J., Tang, J., Chan, J., Zhen, J., Reizenstein,
Rocca, J., Johnstun, J., Saxe, J., Jia, J., Alwala, K. V.,
J., Teboul, J., Zhong, J., Jin, J., Yang, J., Cummings, J.,
Upasani, K., Plawiak, K., Li, K., Heafield, K., Stone, K.,
Carvill, J., Shepard, J., McPhie, J., Torres, J., Ginsburg,
El-Arini, K., Iyer, K., Malik, K., Chiu, K., Bhalla, K.,
J., Wang, J., Wu, K., U, K. H., Saxena, K., Prasad, K.,
Rantala-Yeary, L., van der Maaten, L., Chen, L., Tan, L.,
Khandelwal, K., Zand, K., Matosich, K., Veeraragha-
Jenkins, L., Martin, L., Madaan, L., Malo, L., Blecher, L.,
van, K., Michelena, K., Li, K., Huang, K., Chawla, K.,
Landzaat, L., de Oliveira, L., Muzzi, M., Pasupuleti, M.,
Lakhotia, K., Huang, K., Chen, L., Garg, L., A, L., Silva,
Singh, M., Paluri, M., Kardas, M., Oldham, M., Rita, M.,
L., Bell, L., Zhang, L., Guo, L., Yu, L., Moshkovich,
Pavlova, M., Kambadur, M., Lewis, M., Si, M., Singh,
L., Wehrstedt, L., Khabsa, M., Avalani, M., Bhatt, M.,
M. K., Hassan, M., Goyal, N., Torabi, N., Bashlykov, N.,
Tsimpoukelli, M., Mankus, M., Hasson, M., Lennie, M.,
Bogoychev, N., Chatterji, N., Duchenne, O., C¸ elebi, O.,
Reso, M., Groshev, M., Naumov, M., Lathi, M., Ke-
Alrassy, P., Zhang, P., Li, P., Vasic, P., Weng, P., Bhargava,
neally, M., Seltzer, M. L., Valko, M., Restrepo, M., Patel,
P., Dubal, P., Krishnan, P., Koura, P. S., Xu, P., He, Q.,
M., Vyatskov, M., Samvelyan, M., Clark, M., Macey,
Dong, Q., Srinivasan, R., Ganapathy, R., Calderer, R.,
M., Wang, M., Hermoso, M. J., Metanat, M., Rastegari,
Cabral, R. S., Stojnic, R., Raileanu, R., Girdhar, R., Patel,
M., Bansal, M., Santhanam, N., Parks, N., White, N.,
R., Sauvestre, R., Polidoro, R., Sumbaly, R., Taylor, R.,
Bawa, N., Singhal, N., Egebo, N., Usunier, N., Laptev,
Silva, R., Hou, R., Wang, R., Hosseini, S., Chennabas-
N. P., Dong, N., Zhang, N., Cheng, N., Chernoguz, O.,
appa, S., Singh, S., Bell, S., Kim, S. S., Edunov, S., Nie,
Hart, O., Salpekar, O., Kalinli, O., Kent, P., Parekh, P.,
S., Narang, S., Raparthy, S., Shen, S., Wan, S., Bhosale,
Saab, P., Balaji, P., Rittner, P., Bontrager, P., Roux, P.,
S., Zhang, S., Vandenhende, S., Batra, S., Whitman, S.,
Dollar, P., Zvyagina, P., Ratanchandani, P., Yuvraj, P.,
Sootla, S., Collot, S., Gururangan, S., Borodinsky, S., Her-
Liang, Q., Alao, R., Rodriguez, R., Ayub, R., Murthy,
man, T., Fowler, T., Sheasha, T., Georgiou, T., Scialom,
R., Nayani, R., Mitra, R., Li, R., Hogan, R., Battey, R.,
T., Speckbacher, T., Mihaylov, T., Xiao, T., Karn, U.,
Wang, R., Maheswari, R., Howes, R., Rinott, R., Bondu,
Goswami, V., Gupta, V., Ramanathan, V., Kerkez, V.,
S. J., Datta, S., Chugh, S., Hunt, S., Dhillon, S., Sidorov,
Gonguet, V., Do, V., Vogeti, V., Petrovic, V., Chu, W.,
S., Pan, S., Verma, S., Yamamoto, S., Ramaswamy, S.,
Xiong, W., Fu, W., Meers, W., Martinet, X., Wang, X.,
Lindsay, S., Lindsay, S., Feng, S., Lin, S., Zha, S. C.,
Tan, X. E., Xie, X., Jia, X., Wang, X., Goldschlag, Y.,
Shankar, S., Zhang, S., Zhang, S., Wang, S., Agarwal,
Gaur, Y., Babaei, Y., Wen, Y., Song, Y., Zhang, Y., Li, Y.,
S., Sajuyigbe, S., Chintala, S., Max, S., Chen, S., Kehoe,
Mao, Y., Coudert, Z. D., Yan, Z., Chen, Z., Papakipos, Z.,
S., Satterfield, S., Govindaprasad, S., Gupta, S., Cho,
Singh, A., Grattafiori, A., Jain, A., Kelsey, A., Shajnfeld,
10

## Page 11

Communicating Activations Between Language Model Agents
S., Virk, S., Subramanian, S., Choudhury, S., Goldman, Huh, M., Cheung, B., Wang, T., and Isola, P. The pla-
S., Remez, T., Glaser, T., Best, T., Kohler, T., Robinson, tonic representation hypothesis, 2024. URL https:
T., Li, T., Zhang, T., Matthews, T., Chou, T., Shaked, //arxiv.org/abs/2405.07987.
T., Vontimitta, V., Ajayi, V., Montanez, V., Mohan, V.,
Kumar, V. S., Mangla, V., Albiero, V., Ionescu, V., Poe- Ilharco, G., Ribeiro, M. T., Wortsman, M., Gururangan,
naru, V., Mihailescu, V. T., Ivanov, V., Li, W., Wang, W., S., Schmidt, L., Hajishirzi, H., and Farhadi, A. Editing
Jiang, W., Bouaziz, W., Constable, W., Tang, X., Wang, models with task arithmetic, 2023.
X., Wu, X., Wang, X., Xia, X., Wu, X., Gao, X., Chen,
Jaques, N., Lazaridou, A., Hughes, E., Gulcehre, C., Ortega,
Y., Hu, Y., Jia, Y., Qi, Y., Li, Y., Zhang, Y., Zhang, Y.,
P. A., Strouse, D., Leibo, J. Z., and de Freitas, N. Social
Adi, Y., Nam, Y., Yu, Wang, Hao, Y., Qian, Y., He, Y.,
influence as intrinsic motivation for multi-agent deep
Rait, Z., DeVito, Z., Rosnbrick, Z., Wen, Z., Yang, Z.,
reinforcement learning, 2019.
and Zhao, Z. The llama 3 herd of models, 2024. URL
https://arxiv.org/abs/2407.21783.
Kornblith, S., Norouzi, M., Lee, H., and Hinton, G. Simi-
Foerster, J. N., Assael, Y. M., de Freitas, N., and White- larity of neural network representations revisited, 2019.
son, S. Learning to communicate with deep multi-agent URL https://arxiv.org/abs/1905.00414.
reinforcement learning, 2016.
Lazaridou, A., Peysakhovich, A., and Baroni, M. Multi-
Geiping, J., McLeish, S., Jain, N., Kirchenbauer, J., Singh, agent cooperation and the emergence of (natural) lan-
S., Bartoldson, B. R., Kailkhura, B., Bhatele, A., and guage. arXiv preprint arXiv:1612.07182, 2016.
Goldstein, T. Scaling up test-time compute with latent
reasoning: A recurrent depth approach, 2025. URL Lazaridou, A., Peysakhovich, A., and Baroni, M. Multi-
https://arxiv.org/abs/2502.05171. agent cooperation and the emergence of (natural) lan-
guage, 2017.
Hao, S., Sukhbaatar, S., Su, D., Li, X., Hu, Z., Weston, J.,
and Tian, Y. Training large language models to reason Lee, J., Yang, F., Tran, T., Hu, Q., Barut, E., Chang, K.-
in a continuous latent space, 2024. URL https:// W., and Su, C. Can small language models help large
arxiv.org/abs/2412.06769. language models reason better?: Lm-guided chain-of-
thought, 2024. URL https://arxiv.org/abs/
Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, 2404.03414.
M., Song, D., and Steinhardt, J. Measuring massive
multitask language understanding, 2021. URL https: Lewis, D. Convention: A philosophical study. John Wiley
//arxiv.org/abs/2009.03300. & Sons, 2008.
Hernandez, E., Sharma, A. S., Haklay, T., Meng, K., Watten- Lewis, M., Yarats, D., Dauphin, Y. N., Parikh, D., and Batra,
berg, M., Andreas, J., Belinkov, Y., and Bau, D. Linear- D. Deal or no deal? end-to-end learning for negotiation
ity of relation decoding in transformer language models, dialogues, 2017.
2024.
Li, G., Hammoud, H. A. A. K., Itani, H., Khizbullin, D., and
Hewitt, J. and Manning, C. D. A structural probe for finding Ghanem, B. Camel: Communicative agents for ”mind”
syntax in word representations. In Burstein, J., Doran, C., exploration of large language model society, 2023. URL
and Solorio, T. (eds.), Proceedings of the 2019 Confer- https://arxiv.org/abs/2303.17760.
ence of the North American Chapter of the Association for
Computational Linguistics: Human Language Technolo- Li, K., Patel, O., Vie´gas, F., Pfister, H., and Wattenberg, M.
gies, Volume 1 (Long and Short Papers), pp. 4129–4138, Inference-time intervention: Eliciting truthful answers
Minneapolis, Minnesota, June 2019. Association for from a language model. Advances in Neural Information
Computational Linguistics. doi: 10.18653/v1/N19-1419. Processing Systems, 36, 2024.
URL https://aclanthology.org/N19-1419.
Liang, T., He, Z., Jiao, W., Wang, X., Wang, Y., Wang,
Hoffmann, J., Borgeaud, S., Mensch, A., Buchatskaya, E., R., Yang, Y., Tu, Z., and Shi, S. Encouraging divergent
Cai, T., Rutherford, E., de Las Casas, D., Hendricks, thinking in large language models through multi-agent
L. A., Welbl, J., Clark, A., Hennigan, T., Noland, E., debate, 2023.
Millican, K., van den Driessche, G., Damoc, B., Guy,
A., Osindero, S., Simonyan, K., Elsen, E., Rae, J. W., Lowe, R., Wu, Y., Tamar, A., Harb, J., Abbeel, P., and Mor-
Vinyals, O., and Sifre, L. Training compute-optimal large datch, I. Multi-agent actor-critic for mixed cooperative-
language models, 2022. competitive environments, 2020.
11

## Page 12

Communicating Activations Between Language Model Agents
Moschella, L., Maiorca, V., Fumero, M., Norelli, A., Lo- Sukhbaatar, S., Szlam, A., and Fergus, R. Learning multia-
catello, F., and Rodola`, E. Relative representations en- gent communication with backpropagation, 2016.
able zero-shot latent space communication, 2023. URL
Sukhbaatar, S., Golovneva, O., Sharma, V., Xu, H., Lin,
https://arxiv.org/abs/2209.15430.
X. V., Rozie`re, B., Kahn, J., Li, D., tau Yih, W., Weston,
Nakano, R., Hilton, J., Balaji, S., Wu, J., Ouyang, L., J., and Li, X. Branch-train-mix: Mixing expert llms into
Kim, C., Hesse, C., Jain, S., Kosaraju, V., Saunders, W., a mixture-of-experts llm, 2024.
Jiang, X., Cobbe, K., Eloundou, T., Krueger, G., Button,
Turner, A. M., Thiergart, L., Udell, D., Leech, G., Mini,
K., Knight, M., Chess, B., and Schulman, J. Webgpt:
U., and MacDiarmid, M. Activation addition: Steering
Browser-assisted question-answering with human feed-
language models without optimization, 2023.
back, 2022.
Vapnik, V. N. An overview of statistical learning theory.
Park, J. S., O’Brien, J. C., Cai, C. J., Morris, M. R., Liang,
IEEE transactions on neural networks, 10(5):988–999,
P., and Bernstein, M. S. Generative agents: Interactive
1999.
simulacra of human behavior, 2023.
Wang, L., Ma, C., Feng, X., Zhang, Z., Yang, H., Zhang, J.,
Pham, C., Liu, B., Yang, Y., Chen, Z., Liu, T., Yuan, J.,
Chen, Z., Tang, J., Chen, X., Lin, Y., Zhao, W. X., Wei,
Plummer, B. A., Wang, Z., and Yang, H. Let models
Z., and Wen, J.-R. A survey on large language model
speak ciphers: Multiagent debate through embeddings,
based autonomous agents, 2024.
2024.
Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang,
Prasad, A., Koller, A., Hartmann, M., Clark, P., Sabharwal,
S., Chowdhery, A., and Zhou, D. Self-consistency im-
A., Bansal, M., and Khot, T. Adapt: As-needed decom-
proves chain of thought reasoning in language mod-
position and planning with language models, 2023.
els, 2023. URL https://arxiv.org/abs/2203.
11171.
Schick, T., Dwivedi-Yu, J., Dess`ı, R., Raileanu, R., Lomeli,
M., Zettlemoyer, L., Cancedda, N., and Scialom, T. Tool-
Wei, J., Tay, Y., Bommasani, R., Raffel, C., Zoph, B.,
former: Language models can teach themselves to use
Borgeaud, S., Yogatama, D., Bosma, M., Zhou, D., Met-
tools, 2023.
zler, D., Chi, E. H., Hashimoto, T., Vinyals, O., Liang,
P., Dean, J., and Fedus, W. Emergent abilities of large
Shazeer, N., Mirhoseini, A., Maziarz, K., Davis, A., Le,
language models, 2022.
Q., Hinton, G., and Dean, J. Outrageously large neural
networks: The sparsely-gated mixture-of-experts layer, Wu, Q., Bansal, G., Zhang, J., Wu, Y., Li, B., Zhu, E., Jiang,
2017. L., Zhang, X., Zhang, S., Liu, J., Awadallah, A. H., White,
R. W., Burger, D., and Wang, C. Autogen: Enabling next-
Shen, S. Z., Lang, H., Wang, B., Kim, Y., and Sontag,
gen llm applications via multi-agent conversation, 2023.
D. Learning to decode collaboratively with multiple
language models, 2024. Xi, Z., Chen, W., Guo, X., He, W., Ding, Y., Hong, B.,
Zhang, M., Wang, J., Jin, S., Zhou, E., Zheng, R., Fan,
Shen, Y., Song, K., Tan, X., Li, D., Lu, W., and Zhuang, Y.
X., Wang, X., Xiong, L., Zhou, Y., Wang, W., Jiang, C.,
Hugginggpt: Solving ai tasks with chatgpt and its friends
Zou, Y., Liu, X., Yin, Z., Dou, S., Weng, R., Cheng, W.,
in hugging face, 2023.
Zhang, Q., Qin, W., Zheng, Y., Qiu, X., Huang, X., and
Gui, T. The rise and potential of large language model
Singhal, K., Tu, T., Gottweis, J., Sayres, R., Wulczyn, E.,
based agents: A survey, 2023.
Hou, L., Clark, K., Pfohl, S., Cole-Lewis, H., Neal, D.,
Schaekermann, M., Wang, A., Amin, M., Lachgar, S.,
Yang, H., Yue, S., and He, Y. Auto-gpt for online decision
Mansfield, P., Prakash, S., Green, B., Dominowska, E.,
making: Benchmarks and additional opinions, 2023.
y Arcas, B. A., Tomasev, N., Liu, Y., Wong, R., Sem-
turs, C., Mahdavi, S. S., Barral, J., Webster, D., Cor- Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan,
rado, G. S., Matias, Y., Azizi, S., Karthikesalingam, A., K., and Cao, Y. React: Synergizing reasoning and acting
and Natarajan, V. Towards expert-level medical ques- in language models, 2023.
tion answering with large language models, 2023. URL
https://arxiv.org/abs/2305.09617.
Subramani, N., Suresh, N., and Peters, M. E. Extracting
latent steering vectors from pretrained language models,
2022.
12

## Page 13

Communicating Activations Between Language Model Agents
A. Qualitative Results
Figure 4. Example of AC on Biographies dataset.
13

## Page 14

Communicating Activations Between Language Model Agents
Figure 5. Example of AC on GSM8k dataset.
14

## Page 15

Communicating Activations Between Language Model Agents
Figure 6. Example of AC on MMLU High School Psychology dataset.
15

## Page 16

Communicating Activations Between Language Model Agents
Figure 7. Example of AC on MMLU Formal Logic dataset.
16

## Page 17

Communicating Activations Between Language Model Agents
Figure 8. Example of AC on MMLU College Biology dataset.
17

## Page 18

Communicating Activations Between Language Model Agents
Figure 9. Example of AC on MMLU Professional Law dataset.
18

## Page 19

Communicating Activations Between Language Model Agents
Figure 10. Example of AC on MMLU Public Relations dataset.
19

## Page 20

Communicating Activations Between Language Model Agents
Table 5: Reasoning benchmark performance when varying tokens modified during AC. All methods involve communi-
cation between LLaMA-3.2-3B (A) and LLaMA-3.1-8B (B). The functional form f is varied between last-token replacement,
last-token summation, and summation for all tokens.
Method Biog. GSM8k HS Psych. Logic Col. Bio. Prof. Law Pub. Rel.
AC (replace) 84.6±0.0 64.0±4.8 85.0±0.8 47.0±0.1 78.0±0.9 30.0±0.1 74.0±0.1
AC (sum) 79.7±0.0 66.0±4.7 65.0±4.8 42.0±4.9 50.0±5.0 25.0±4.3 37.0±4.8
AC (all tokens) 76.0±0.0 62.0±4.9 35.0±4.8 42.0±4.9 61.0±4.9 15.0±3.6 26.0±4.4
Table 6: Reasoning benchmark performance when sampling from A with CoT. All methods involve communication
between LLaMA-3.2-3B (A) and LLaMA-3.1-8B (B).
Method Biog. GSM8k HS Psych. Logic Col. Bio. Prof. Law Pub. Rel.
AC 84.6±0.0 64.0±4.8 85.0±0.8 47.0±0.1 78.0±0.9 30.0±0.1 74.0±0.1
AC (W ) 86.8±0.0 66.0±4.8 70.0±0.1 35.0±0.1 79.0±0.9 45.0±0.1 63.0±0.1
AC (CoT) 82.1±0.0 66.0±4.0 80.0±4.0 26.0±4.4 67.0±4.7 40.0±4.9 63.0±4.8
B. Additional Experiments
B.1. Modifying Activations of All Tokens
Recall that AC grafts the last-token layer-k activation of A into B’s last-token layer-j activation. But is modifying just the
last token activation enough to communicate information from A to B?
Note that after applying masked attention in each of the previous Transformer layers, the last token activation of A attends
to all tokens before it, hence incorporating information from the entire sequence. Indeed, this must be the case for activation
communication to recover the gap between the zero-communication and skyline setups on both coordination games, which
(for Tip Sheets in particular) require information starting at the first few tokens of A’s prompt to be communicated.
To verify this empirically, we experiment with summing the activations of all tokens in the sequence rather than just the
last (we cannot replace all tokens as this would just replace B’s layer-j activation with A’s layer k-activation). Results are
shown in Table 5.
Indeed, applying f to all tokens decreases performance relative to applying f to just the last token. Note that the fact
performance generally decreases from f = replace to f = sum, and further with all tokens, is expected. The high
performance of AC with f = replace means that the edited last-token activation b retains some meaning in B’s activation
space; it is less likely for this to be the case when f = sum (at the very least b has norm roughly 2× that of B’s original
last-token activation), and when doing this for all tokens we’d expect performance to decrease even further as now all
activation vectors, not just the last, are out-of-distribution with respect to B’s activation space.
B.2. Incorporating Chain-of-Thought Prompting
How does AC perform in relation to NLD in cases where A might incur a long response (possibly with chain-of-thought for
intermediate answer computation)? I.e., does AC lose out on the benefits of CoT?
First, note that we still reap the benefits of CoT when we sample a completion from B after AC (where B gets all the
information encoding A’s “beliefs” about the prompt via AC, hence CoT on A’s side is not needed). To verify this, we
experiment with prompting A with CoT, generating a full response, and then passing the layer-k last-token activation of the
CoT response to B as part of AC. Results are shown in Table 6.
Indeed, we empirically find our above intuition (in orange) to hold, as there is no significant improvement over vanilla AC
when generating from A using CoT.
B.3. Learning W In-Distribution
Recall our reasoning about the AC (W ) results from Section 4.2: “We hypothesize that the benefits from the learned
linear layer are less consistent across datasets because the subset of C4 data used to train W likely contains text more
20

## Page 21

Communicating Activations Between Language Model Agents
Table 7: GSM8k performance when learning W in-distribution. All AC variants involve communication between
LLaMA-3.2-3B (A) and LLaMA-3.1-8B (B).
AC AC (W ) AC (W )
in dist
64.0±4.8 66.0±4.8 78.0±4.1
Table 8: Reasoning benchmark performance of communication between identical models. Both NLD and AC involve
communication between 2 instances of LLaMA-3.1-8B. 512-token completions are sampled with temperature 0.7 and debate
is run for 2 rounds.
Method Biog. GSM8k HS Psych. Logic Col. Bio. Prof. Law Pub. Rel.
LLaMA-3.1-8B 83.9±0.0 60.0±4.9 65.0±0.1 42.0±0.1 50.0±0.2 20.0±0.8 53.0±0.2
NLD 80.8±0.0 70.0±3.7 85.0±3.6 35.0±4.8 78.0±4.1 40.0±4.9 53.0±5.1
AC 83.7±0.0 60.0±4.9 85.0±3.6 40.0±4.9 74.0±4.4 40.0±4.9 79.0±4.1
semantically similar to some datasets than others, hence some datasets provide W with out-of-distribution inputs which
reduces performance compared to vanilla AC.”
Indeed, we verify this hypothesis by training W on the GSM8k train set (to produce W ) and then evaluating with this
in dist
task-specific linear layer on the GSM8k test set. Results are shown in Table 7.
Indeed, learning W in-distribution significantly boosts performance, confirming our hypothesis. Unfortunately we cannot
run this experiment for the other datasets, as there is no in-distribution training data available for MMLU (we use all public
data for testing).
Hence, this suggests that AC (W ) should unilaterally improve over vanilla AC if we choose a training set with good
coverage across many tasks and distributions, such that there are sentences semantically similar to prompts across the span
of downstream task datasets.
B.4. Activation Space Similarity ∝ AC Performance Gain
We conduct the following experiment: for each of the six pairs of models A, B in the above experiment (see Table 4), we
compute the increase in Biographies performance with AC relative to the average individual performance of A and B. We
also compute the matrix analogue of the squared cosine similarity between the models’ activation spaces,
∥Y ⊤X∥2
F ,
∥X∥2 ∥Y ∥2
F F
where X is the matrix of A’s activations on 3072 sentences from C4 (the same dataset used to train W ), Y is the
corresponding matrix for B, and ∥·∥ denotes the Frobenius norm. This yields the plot in Figure 11.
F
There is a clear positive correlation between the similarity of the activation distributions and the AC performance gain, as
expected; the more aligned A and B’s activation spaces are, the more semantically meaningful and useful the embedding we
graft from A to B becomes.
B.5. Communicating Activations Between Identical Models
Note that AC as described in Section 3.1 only supports communication between distinct models. We can extend AC to work
for communication between identical models as follows: let A and B be instances of the same model. We can sample a
completion from A with temperature and graft the last-token layer-k activation of the completion into B at layer j as part of
the AC procedure. This still saves a substantial amount of compute over NLD between 2 model instances, showing our
technique can apply to this setting. Table 8 shows the results of this experiment.
Indeed, while communication between multiple model instances doesn’t always show improvement over the single model
itself (a well-known result from (Du et al., 2023)), AC matches/outperforms NLD on five of the seven datasets.
The intuition behind debate between multiple identical model instances is that sampling multiple completions (with
temperature) from the same model yields diverse reasoning paths that can be recombined into a stronger final answer. The
21

## Page 22

Communicating Activations Between Language Model Agents
Figure 11. AC performance gain over average A/B individual performance on Biographies, as a function of matrix “cosine similarity”
between A and B’s activation spaces.
Table 9: Reasoning benchmark performance of AC and NLD with varying number of rounds. All methods involve
communication between LLaMA-3.2-3B (A) and LLaMA-3.1-8B (B).
Method Biog. GSM8k HS Psych. Logic Col. Bio. Prof. Law Pub. Rel.
NLD (1 round) 83.6±0.0 72.0±4.5 65.0±4.8 40.0±4.9 68.0±4.6 30.0±4.6 63.0±4.8
NLD (2 rounds) 80.2±0.1 75.0±4.3 83.0±0.8 37.0±0.1 71.0±0.1 30.0±0.1 63.0±0.7
NLD (3 rounds) 80.1±4.6 79.0±4.1 70.0±4.6 45.0±5.0 63.0±4.8 40.0±4.9 74.0±4.4
NLD (4 rounds) 78.0±0.0 79.0±4.1 * * * * *
AC 84.6±0.0 64.0±4.8 85.0±0.8 47.0±0.1 78.0±0.9 30.0±0.1 74.0±0.1
∗Runs required too much compute
above experiment shows that the same intuition holds for AC—we are sampling multiple times from the same model, but
passing responses between agents via AC rather than as NL messages.
B.6. Additional Rounds of Natural Language Debate
In Section 4.2 we fix NLD to 2 agents and 2 rounds, however we find in additional experiments that AC outperforms NLD
even with additional rounds, highlighting the superiority and robustness of activations as an alternative “language” for
inter-LM communication. Results are shown in Table 9; we see that for 5 of the 7 reasoning benchmarks, AC beats NLD
even with 3-4 rounds while using substantially less compute.
B.7. Full MMLU Benchmark Results
Table 10 below displays complete results of both AC and NLD on the full MMLU benchmark. Notably, AC
matches/outperforms NLD on 48/57 datasets, with substantially less compute used, indicating its superiority and
robustness as an alternative “language” for inter-LLM communication.
22

## Page 23

Communicating Activations Between Language Model Agents
Table 10: Comparison of NLD vs. AC on the full MMLU benchmark (Hendrycks et al., 2021).
Dataset NLD AC
Conceptual Physics 60.0 ± 4.9 68.0 ± 4.6
High School Chemistry 50.0 ± 5.0 37.0 ± 4.8
Security Studies 60.0 ± 4.9 60.0 ± 4.9
Jurisprudence 84.0 ± 3.6 84.0 ± 3.6
Logical Fallacies 63.0 ± 4.8 72.0 ± 4.5
College Computer Science 44.0 ± 5.0 44.0 ± 5.0
International Law 55.0 ± 5.0 59.0 ± 4.9
Miscellaneous 90.0 ± 3.0 95.0 ± 2.2
Marketing 70.0 ± 4.6 85.0 ± 3.6
Elementary Mathematics 75.0 ± 4.3 58.0 ± 4.9
Machine Learning 42.0 ± 4.9 42.0 ± 4.9
High School Macroeconomics 44.0 ± 5.0 75.0 ± 4.3
High School US History 45.0 ± 5.0 71.0 ± 4.6
Human Aging 56.0 ± 5.0 72.0 ± 4.5
Astronomy 79.0 ± 4.1 80.0 ± 4.0
Computer Security 56.0 ± 5.0 75.0 ± 4.3
High School Statistics 55.0 ± 5.0 42.0 ± 4.9
Professional Medicine 79.0 ± 4.1 65.0 ± 4.8
Electrical Engineering 58.0 ± 4.9 60.0 ± 4.9
High School Computer Science 63.0 ± 4.8 70.0 ± 4.6
College Physics 50.0 ± 5.0 28.0 ± 4.5
Management 74.0 ± 4.1 75.0 ± 4.3
Moral Scenarios 40.0 ± 4.9 40.0 ± 4.9
World Religions 58.0 ± 4.9 72.0 ± 4.5
Virology 47.0 ± 5.0 50.0 ± 5.0
Philosophy 67.0 ± 4.7 70.0 ± 4.6
Abstract Algebra 50.0 ± 5.0 28.0 ± 4.5
High School Government and Politics 80.0 ± 4.0 61.0 ± 4.9
High School Biology 60.0 ± 4.9 65.0 ± 4.8
College Mathematics 64.0 ± 4.8 66.0 ± 2.4
Global Facts 33.0 ± 5.0 37.0 ± 4.8
High School World History 71.0 ± 4.0 74.0 ± 4.4
High School European History 68.0 ± 4.0 71.0 ± 4.6
College Medicine 65.0 ± 4.8 53.0 ± 5.0
High School Geography 67.0 ± 4.7 79.0 ± 4.1
Anatomy 74.0 ± 4.4 74.0 ± 4.4
Human Sexuality 75.0 ± 4.3 75.0 ± 4.3
Medical Genetics 79.0 ± 4.1 82.0 ± 3.8
Professional Accounting 40.0 ± 4.9 48.0 ± 4.5
US Foreign Policy 89.0 ± 3.1 90.0 ± 3.1
Business Ethics 43.0 ± 5.0 44.0 ± 5.0
College Chemistry 41.0 ± 5.0 47.0 ± 5.0
High School Physics 40.0 ± 5.0 47.0 ± 5.0
Professional Psychology 54.0 ± 4.8 55.0 ± 5.0
Sociology 68.0 ± 4.1 68.0 ± 4.6
High School Microeconomics 95.0 ± 2.2 95.0 ± 2.2
High School Mathematics 55.0 ± 5.0 55.0 ± 5.0
Prehistory 75.0 ± 4.3 60.0 ± 4.9
Nutrition 64.0 ± 4.5 70.0 ± 4.6
Clinical Knowledge 65.0 ± 4.3 65.0 ± 4.8
Moral Disputes 58.0 ± 4.8 60.0 ± 4.9
Econometrics 40.0 ± 5.0 40.0 ± 4.9
High School Psychology 83.0 ± 0.8 85.0 ± 0.8
Formal Logic 37.0 ± 0.1 47.0 ± 0.1
College Biology 71.0 ± 0.1 78.0 ± 0.9
Professional Law 30.0 ± 0.1 30.0 ± 0.1
Public Relations 63.0 ± 0.7 74.0 ± 0.1
Average 60.7 ± 2.0 62.7 ± 2.2
23
