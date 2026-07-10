# mad-divergent-thinking-2305.19118

- Source PDF: `mad-divergent-thinking-2305.19118.pdf`
- Extracted at UTC: `2026-07-09T05:57:18.224234+00:00`
- Pages: 16
- Title: 
- SHA256: `7696fb358c8a8ba982a314b95269485b49b5ab830eec3e2f217d89f71e541c17`

## Page 1

Encouraging Divergent Thinking in Large Language Models
through Multi-Agent Debate
Tian Liang1,3* Zhiwei He2* Wenxiang Jiao3* Xing Wang3† Yan Wang3
Rui Wang2 Yujiu Yang1† Shuming Shi3 Zhaopeng Tu3
1Tsinghua University 2Shanghai Jiao Tong University 3Tencent AI Lab
1{liangt21@mails,yang.yujiu@sz}.tsinghua.edu.cn
2zwhe.cs@sjtu.edu.cn 3{joelwxjiao,brightxwang,zptu}@tencent.com
Abstract 1.00
Multi-Agent Debate
Self-Reflection
Modern large language models (LLMs) like 0.75
ChatGPT have shown remarkable performance
on general language tasks but still struggle on
0.50
complex reasoning tasks, which drives the re-
search on cognitive behaviors of LLMs to ex-
plore human-like problem-solving strategies. 0.25
Along this direction, one representative strat-
egy is self-reflection, which asks an LLM to
0.00
refine the solution with the feedback gener- 1 2 3 4 5
Iteration
ated by itself iteratively. However, our study
shows that such reflection-style methods suf-
fer from the Degeneration-of-Thought (DoT)
problem: once the LLM has established confi-
dence in its solutions, it is unable to generate
novel thoughts later through reflection even if
its initial stance is incorrect. To address the
DoT problem, we propose a Multi-Agent De-
bate (MAD) framework, in which multiple
agents express their arguments in the state of
“tit for tat” and a judge manages the debate
process to obtain a final solution. Clearly, our
MAD framework encourages divergent think-
ing in LLMs which would be helpful for tasks
that require deep levels of contemplation. Ex-
periment results on two challenging datasets,
commonsense machine translation and counter-
intuitive arithmetic reasoning, demonstrate the
effectiveness of our MAD framework. Exten-
sive analyses suggest that the adaptive break of
debate and the modest level of “tit for tat” state
are required for MAD to obtain good perfor-
mance. Moreover, we find that LLMs might not
be a fair judge if different LLMs are used for
agents. Code is available at https://github.
com/Skytliang/Multi-Agents-Debate.
1 Introduction
Large language models (LLMs) have shown
remarkable performance on general language
tasks (Jiao et al., 2023; Wu et al., 2023; Bang
* Contributed equally. Work was done when Tian and
Zhiwei were interning at Tencent AI Lab.
† Xing and Yujiu are co-corresponding authors.
tnemeergasiD
.gvA
Figure 1: Disagreement between two adjacent iterations
with respect to the iteration of debate/self-reflection.
et al., 2023) but still struggle on complex reasoning
tasks (Zhu et al., 2023a; Gou et al., 2023), which
drives the research on cognitive behaviors of LLMs
to explore human-like problem-solving strategies.
In particular, self-reflection (Madaan et al., 2024;
Shinn et al., 2024), a concept that usually refers to
the process of introspection and examination of a
person’s own thoughts, has been explored to solve
intricate tasks that could be challenging for a zero-
shot generation or even chain-of-thought (CoT)
prompting (Wei et al., 2022). Specifically, self-
reflection involves an iterative refinement process
such that the LLM generates a new answer based on
the answers and feedback in previous iterations and
then provides feedback for the new answer. While
self-reflection can be effective in creating better an-
swers, it is highly dependent on the self-evaluation
capabilities of LLMs, which are not formally guar-
anteed (Shinn et al., 2024).
In this work, we focus on the Degeneration-of-
Thought (DoT) problem in self-reflection, which
is proposed and defined by us for the first time.
Formally, DoT describes the following scenario:
Once the LLM-based agent has estab-
lished confidence in its answers, it is
unable to generate novel thoughts later
through self-reflection even if the initial
stance is incorrect.
4202
tcO
9
]LC.sc[
4v81191.5032:viXra

## Page 2

To demonstrate this problem, we force the agents Translation (Common MT) and Counter-Intuitive
to engage in a debate or self-reflection for 5 rounds Arithmetic Reasoning (Counter-Intuitive AR). The
before reaching an answer. Next, we manually de- common characteristic of the two tasks is that our
termine the disagreement as 1 and agreement as instincts are mostly incorrect based on only the su-
0 between two adjacent iterations. We define the perficial expressions of the questions, and deeper
average disagreement in iteration i as the percent- levels of contemplation are required for better an-
age of opposition occurring between two debaters swers. Experimental results demonstrate that our
across multiple debates (or self-confliction in self- MAD framework outperforms the baseline meth-
reflection). We show the trends in Figure 1. The ods, especially, GPT-3.5-Turbo with MAD can
low disagreement of self-reflection suggests that surpass the performance of GPT-4 on Common MT.
the LLM sticks to the incorrect answers predicted The contributions of this work are summarized
by CoT and is unable to engage in meaningful self- as follows:
reflection.
• We propose and define the Degeneration-of-
There are various factors (Bortolotti, 2011;
Thought (DoT) problem in self-reflection, and
Keestra, 2017) that could result in DoT, and we out-
address it by proposing the Multi-Agent De-
line three here: (1) Bias and Distorted Perception.
bate (MAD) framework to explore divergent
Self-perception can be influenced by biases, pre-
chain-of-thoughts.
conceived notions, and distorted thinking patterns,
which can be learned from the massive amount of • We demonstrate the effectiveness of MAD
data during pretraining. If an LLM’s self-reflection on two challenging tasks, and find that
is clouded by such biases or distorted thinking, it GPT-3.5-Turbo with MAD can even surpass
can lead to inaccurate conclusions instinctively. (2) GPT-4 on the Common MT dataset.
Rigidity and Resistance to Change. Self-reflection
• Experimental results show that the adaptive
often involves challenging one’s beliefs, assump-
break strategy and the modest level of “tit for
tions, and behaviors. If an LLM is resistant to
tat” state are required for performance improve-
change or holds rigid beliefs, it may struggle to en-
ment. In addition, we find that the llm-based
gage in meaningful self-reflection that leads to bet-
judge shows a preference to the side with the
ter answers. (3) Limited External Feedback. Self-
same LLM as the backbone.
reflection is primarily an internal process, but exter-
nal feedback can provide valuable perspectives and 2 Multi-Agent Debate Framework
insights. Without considering external feedback, an
Figure 2 illustrates the general framework of MAD,
LLM may miss important blind spots or alternative
where two debaters and a judge are involved in a de-
viewpoints that can enrich its self-reflection.
bate to resolve a math problem while self-reflection
To address the DoT issue, we leverage an-
descends into the trap of DoT. Generally, our MAD
other fundamental characteristic of human problem-
framework is composed of three components which
solving, i.e., debate, to encourage divergent think-
are elaborated as follows:
ing in LLMs. Specifically, we propose the MAD
framework, short for Multi-Agent Debate, where Meta Prompts. We use meta prompts to intro-
two agents express their own arguments in the duce the topic to be solved, the number of debaters,
state of “tit for tat” and a judge monitors and man- the iteration limit, and other requirements. An ex-
ages the debate process to obtain a final solution. ampe of meta prompts for the arithmetic reasoning
The nature of MAD determines that (1) The dis- task in Figure 2 is:
torted thinking of one agent can be corrected by the
You are a debater. Hello and welcome to the
others; (2) The resistance to change of one agent
debate competition. It’s not necessary to
will be complemented by the others; and (3) each
fully agree with each other’s perspectives,
agent can obtain external feedback from the others.
as our objective is to find the correct an-
Therefore, MAD is less susceptible to the factors of
swer. The debate topic is stated as follows:
DoT, and can explore divergent chain-of-thoughts
<debate topic>.
to achieve accurate answers.
We conducted experiments on both natural lan- As seen, we require the agents to “tit for tat” (e.g.
guage generation and understanding through two contents underlined in meta prompts above) so as
challenging tasks, namely, Commonsense Machine to create an atmosphere of debate.

## Page 3

Counter-Intuitive Question
The two circles are externally tangent and there is no relative sliding. The radius of circle A is 1/3 the radius of circle
B. Circle A rolls around circle B one trip back to its starting point. How many times will circle A revolve in total?
Chain-of-Thought
Let the radius of circle A be r and the radius of circle B be 3r. The distance circle A travels along the circumference
of circle B is equal to the circumference of circle B, which is 6πr. The number of revolutions = (6πr) / (2πr) = 6πr /
2πr = 3. So, circle A will revolve 3 times in total as it rolls around circle B once.
Self-Reflection Multi-Agent Debate
Reflection:
I disagree with you. To find the total number of revolutions, we need
(1) I have a clear understanding
to consider both the rotation around circle B and the rotation of circle
of the problem.
A itself. Therefore, circle A will revolve 3 times around its own center
(2) I have used the correct
and 1 time around circle B, making a total of 4 revolutions.
formula for the circumference of a
circle and applied it to both circles
to find the number of revolutions. I see your point, but...
(3) I have correctly calculated the
number of revolutions of circle A.
That's a valid point, however...
Based on the results of my self-
reflection, I am confident that my The negative side correctly considers both the rotation of circle A
answer is correct. Therefore, around its own center and its rotation around circle B, while the
circle A will revolve 3 times in total affirmative side only considers the rotation around circle B.
as it rolls around circle B once. Therefore, the answer is 4.
Figure 2: Framework of Multi-Agent Debate. Here we designate the devil ( ) as the affirmative side while the
angel ( ) as the negative side. We want the angel to correct the devil’s mistakes.
Debaters. There are N debaters D = {D }N the judge J needs to extract the final solution based
i i=1
involved in the framework. In each debate iteration, on the whole debate history: J (H) = a, since
e
the debaters D speak one by one in a fixed order no correct solution is identified within the iteration
i
and express their arguments based on the previous limit of debate. An example of a judge prompt ( )
debate history H, i.e., D (H) = h. An example of appears below:
i
a debater prompt appears below:
You are a moderator. There will be two
• Prompt for Affirmative Debater ( ) debaters involved in a debate competition.
They will present their answers and discuss
You are affirmative side. Please express
their perspectives on the <debate topic>.
your viewpoints.
At the end of each round, you will evaluate
• Prompt for Negative Debater ( ) both sides’ answers and decide which one
is correct.
You are negative side. You disagree with
the affirmative side’s points. Provide
3 Experiment
your reasons and answer.
3.1 Challenging Testbeds
Judge. We also design a judge J to manage and
monitor the whole debate process. The judge con- We conduct experiments on two challenging tasks,
tains two different modes: (a) Discrinative Mode, namely, commonsense machine translation (i.e.,
in which the judge J decides whether the correct Common MT), and counter-intuitive arithmetic rea-
solution can be obtained after all the debaters finish soning (i.e., Counter-Intuitive AR), which require
their arguments in the current iteration: deep levels of contemplation for LLMs. Please
refer to Appendix A for more details.
(cid:40)
True, solution obtained
J d (H) = (1) Commonsense Machine Translation The Com-
False, otherwise
mon MT dataset is composed of Chinese⇒English
If it is True, the debate is over. Otherwise, the translation examples (He et al., 2020), which are
debate continues. (b) Extractive Mode, in which used to examine three types of ambiguity resolution

## Page 4

abilities of translation models, covering lexical and Backbone Models. In this work, we mainly
contextless/contextual syntactic ambiguity. Within use three agents in our MAD framework,
the challenging part of Common MT, the authen- including two debaters (i.e., affirmative
tic translation of each source sentence requires a and negative) and a judge. We assess two
proper understanding of common sense knowledge. open-source (i.e., vicuna-7b-v1.5-16k3
While these ambiguous sentences might appear to and vicuna-13b-v1.5-16k4) and two api-
have a straightforward translation, such a literal based LLMs (i.e., GPT-3.5-Turbo-0301 and
interpretation is erroneous. Failure to address such GPT-4-0314).
ambiguities may result in inaccurate translations.
Compared Methods. Generally, we compare
Counter-Intuitive Arithmetic Reasoning Pre-
our MAD framework with baseline models and
vious studies on thinking hierarchy (Daniel, 2017)
Self-Reflect on both tasks. We also include other
suggest that we humans have a fast and intu-
baseline methods individually, namely, Rerank
itive system and a slow and logical system, and
and MAPS for Common MT, CoT and Self-
tend to run the lower level system before the
Consistency for Counter-Intuitive AR. Below elab-
higher level one. Inspired by this, we created a
orates the details of them:
more challenging dataset named Counter-Intuitive
Arithmetic Reasoning (CIAR) to evaluate the rea- • Self-Reflect (Shinn et al., 2024): This approach
soning abilities of LLMs at deep levels. Our requires the LLM to refine its translation until it
Counter-Intuitive AR dataset contains 200 ques- deems the current output satisfactory.
tions collected from elicitation questions (Kong
et al., 2022)1, web data2 and additional manual • Rerank (He et al., 2024): We sample the transla-
derivatives of these questions. Compared to the tions from the LLM for four times, from which
commonly-used datasets, e.g., MultiArith (Roy and we select the best candidate based on a quality
Roth, 2015), GSM8K (Cobbe et al., 2021), our estimation (QE) HUMANr5. This approach can
dataset presents two distinct challenges: be seen as analogous to self-consistency (Wang
et al., 2022), where the majority voting is re-
• Resistance to Intuition. The questions are em-
placed by an external QE HUMANr.
bedded in hidden traps designed to elicit intuitive
and appealing answers that are often incorrect.
• MAPS (He et al., 2024): This method enables
This feature evaluates the abilities of LLMs to
LLMs to mimic the human translation process:
resist the traps of superficial expressions.
analyze before translate, which can be viewed as
• Multi-Step Reasoning. Each correct answer a chain-of-thought method applied to translation.
within the dataset requires a rigorous multi-step
reasoning process, thereby evaluating the ca- • CoT (Kojima et al., 2022): This approach con-
pacity of LLMs to engage in complex decision- catenates a trigger sentence “Let’s think step by
making and problem-solving. step” to the test question.
3.2 Setups
• Self-Consistency (Wang et al., 2022): This
Input Format. Our experiments are performed
method samples multiple responses and deter-
in zero-shot instructions (setting temperature to
mines the final answer through a majority vote.
0). For all used datasets, we use a unified prompt
to make LLMs give explanations and answers. All agents in our experimental setup, such
We present the inputs to agents through <debate as debaters and judge, are large language mod-
topic> as mentioned in Section 2. For example, els. Here, we implement the methods on top of
if we want to translate “吃掉敌人一个师” from GPT-3.5-Turbo and Vicuna models.
Chinese to English, we will set the <debate topic>
as “What is the correct English translation of the Evaluation Metrics. For Counter-Intuitive AR,
following Chinese text: 吃掉敌人一个师”. For we report the accuracy (ACC) of predictions.
QA task, we employ the same prompt except set For Common MT, we adopt automatic metrics
the <debate topic> to the arithmetic question.
3https://huggingface.co/lmsys/vicuna-7b-v1.5-16k
1https://elicitation.info/questionnaire/1/ 4https://huggingface.co/lmsys/vicuna-13b-v1.5-16k
2https://www.geeksforgeeks.org/puzzles/ 5We use wmt21-comet-qe-da as the QE HUMANr.

## Page 5

Lexical Contextless Contextual
Method
COMET BLEURT HUMAN COMET BLEURT HUMAN COMET BLEURT HUMAN
GPT-4 82.0 70.1 3.41 84.7 73.6 3.63 85.0 73.7 3.65
Turbo 80.3 68.2 3.14 84.0 72.9 3.43 84.9 73.4 3.57
+ Rerank 80.9 68.6 3.16 84.5 73.2 3.46 85.3 73.9 3.58
+ MAPS 81.9 70.1 3.43 84.2 73.5 3.45 85.2 74.0 3.56
+ Self-Reflect 81.0 69.1 3.43 83.6 72.2 3.46 84.9 73.5 3.63
+ MAD 82.0 70.9 3.78 84.8 73.7 3.67 85.3 74.0 3.67
Vicuna-7b 74.9 62.0 2.55 78.3 64.6 2.53 80.2 68.2 3.23
+ MAD 75.6 62.6 2.67 78.6 66.0 2.69 81.8 69.9 3.27
Vicuna-13b 76.6 63.7 2.81 77.6 66.8 3.04 82.2 70.0 3.37
+ MAD 77.2 65.1 2.96 80.1 67.3 3.11 82.6 70.9 3.45
Table 1: Translation performance on Common MT. Note that Rerank and MAPS use the external quality estimation
tool to select the best translation from multiple translation candidates. HUMAN: direct assessment of translation
quality from human evaluators on a scale ranging from 1 to 5.
like COMET6 and BLEURT7, which are widely Source 吃掉敌人一个师。
adopted evaluation metrics for LLM-based transla- Correct Ref. Destroy a division of the enemy.
tion literature (He et al., 2024; Hendy et al., 2023; Incorrect Ref. Eat up an enemy division.
Garcia et al., 2023; Pilault et al., 2023). In addition, GPT-4 Eat up an enemy division.
we also employ professional human translators to GPT-3.5-Turbo Eat up an enemy division.
directly assess the translation results, measuring + Self-Reflect Eat up an enemy division.
translation quality on a scale ranging from 1 to 5. + MAD Eliminate an enemy division.
Table 2: Example translations generated by different
3.3 Results on Common MT
methods. Best viewed in color.
Results. In Common MT test set, we focus more
on the translation accuracy of specific words and Method ACC (%)
whether they conform to common sense. However, GPT-4 51.0
such minor variations at token level are difficult
GPT-3.5-Turbo 26.0
to reflect on automatic metrics. We therefore pro-
+ CoT 28.0
vide human HUMAN to evaluate these methods
+ Self-Consistency 29.5
more accurately. Table 1 presents the experimental
+ Self-Reflect 27.5
results. MAPS and Self-Reflec achieve improve-
+ MAD 37.0
ments over baseline GPT-3.5-Turbo. Remarkably,
our proposed MAD, by utilizing GPT-3.5 as the Table 3: Accuracy on Counter-Intuitive AR.
backbone model, has demonstrated significant ad-
vancements over GPT-4 across both automatic and can generate the free translation of the underlined
human evaluation metrics. words within the source sentences.
Case Study. Table 2 shows example translations
3.4 Results on Counter-Intuitive AR
generated by baseline GPT-3.5-Turbo and the
proposed MAD. We can find that the baseline Results. Table 3 lists the results in terms of
GPT-3.5-Turbo (even the more powerful GPT-4) reasoning accuracy. We can observe that Self-
incorrectly translates the source words literally. Be- Reflect only marginally improves over the baseline
cause of the DoT issue, Self-Reflect cannot rectify GPT-3.5-Turbo, while CoT and Self-Consistency
the literal translation. The proposed MAD frame- bring more improvements. Our MAD framework,
work, which explores divergent chain-of-thoughts, though not as good as GPT-4, outperforms all the
other compared methods based on GPT-3.5-Turbo,
6https://github.com/Unbabel/COMET/,
which further demonstrates its effectiveness. We
Unbabel/wmt22-comet-da
also validate MAD on math and symbolic reason-
7https://github.com/google-research/bleurt,
BLEURT-20 ing tasks and report our results in Appendix C.

## Page 6

Method Bias↓ Diversity↑ Judge LLM COMET HUMAN
Self-Reflect 29.0 19.3 Vicuna-13b as Debaters
MAD 24.8 49.7 Vicuna-13b 79.9 3.20
GPT-3.5-Turbo 80.4 3.25
Table 4: Mitigation of Degeneration-of-Thought.
GPT-3.5-Turbo as Debaters
Vicuna-13b 83.2 3.47
Case Study. Figure 2 shows an example on
GPT-3.5-Turbo 84.4 3.69
Counter-Intuitive AR. We find both CoT and Self-
Reflect fail to reach the right answer by mistakenly Table 5: Translation performance with different judge.
outputing 3. With divergent thinking, our MAD
framework emerges “we need to consider both the
translation (possible modified answer after Self-
rotation around circle B and the rotation of circle
Reflection or negative side’s response in MAD).
A itself ” and find the correct answer 4.
As shown in Table 4, Bias and Rigidity are signif-
4 Analysis icant factors causing DoT. In addition, addressing
these biases and stereotypes through self-reflection
In this section, we present a qualitative analysis to can be challenging. MAD framework effectively
provide some insights how MAD works. Unless corrects inherent biases in translation, mitigates
otherwise stated, we report the overall results on DoT, and considerably improves performance.
the Common MT dataset.
4.2 Analysis of Judge
4.1 Mitigation of DoT
In this section, we analyze the behavior of the judge
As mentioned in the Section 1, the DoT problem
for different settings of the debaters.
originates from three factors: (1) Bias and Dis-
torted Perception, (2) Rigidity and Resistance to Strong debaters with a weak judge work bet-
Change, and (3) Limited External Feedback. In ter than the reverse. To understand the roles
our MAD framework, we introduce the views of of debaters and judge in MAD, we employ vari-
other agents in the form of debates, solving the phe- ous combinations of models to initialize the agents.
nomenon of limited external feedback (problem 3). Specifically, we utilize the smaller language model
Next, this section will delve into the mitigation of (vicuna-13b-v1.5-16k) as a judge to evaluate
problems 1 and 2 through experiments. the debate results of the more powerful LLMs
(GPT-3.5-Turbo), and vice versa.
• Bias: We observe that LLMs often rely on direct The detailed experimental findings are presented
intuition, which can lead to incorrect or inappro- in Table 5. The quality of the debaters’ responses
priate responses. To address this problem, we significantly impact the performance ceiling of
use human evaluation to determine the ambiguity MAD. Regardless of the model chosen for the
error rate of LLMs’ responses, examining if the judge, Turbo debaters consistently generate supe-
LLM’s output is biased. rior translations compared to Vicuna. In addition,
the selection of the judge agent plays a secondary
• Diversity: LLMs are resistant to changing their
role. When Turbo debaters are involved, Vicuna,
answers and lack diverse reflection. The diver-
serving as the judge, underperforms Turbo across
sity of the translations is evaluated using the
all test sets.
Self-BLEU score (Yin et al., 2020). In other
words, methods lacking diverse reflection pro- LLM may not act as an impartial judge when
duce more similar translation candidates. Con- different LLMs are used as debaters. We study
sequently, higher Self-BLEU scores mean lower the behavior of agents by calculating how many
diversity. We calculate text diversity via: times the judge chooses the answers of each de-
bater as the final solution in different scenarios.
Diversity = 100 − Self_BLEU (Cand , Cand ) (2)
1 2 The results are listed in Table 6 and we have the
following observations:
In formula (2), candidates 1 and 2 represent the
initial translation (base answer in Self-Reflection or • Same LLM for All Agents (Rows ⃝1 and ⃝2 ):
affirmative side’s response in MAD) and the current We find that the judge consistently favors the

## Page 7

)%001×(
noituloseR
ytiugibmA
0.9
0.8
0.7
0.6
0.5
tnemeergasiD
.gvA
1.00
Avg. Disagreement
Ambiguity Resolution
00..8800
0.75
00..7722
0.50
00..6666
00..6633
0.25
0.00
0 1 2 3
Level
Figure 3: Translation performance with respect to the
debate level on Lexical.
Debater Winner
ID Jud
Aff Neg Aff Neg Tie
⃝1 Turbo Turbo Turbo 87 104 9
⃝2 GPT-4 GPT-4 GPT-4 67 124 9
⃝3 Turbo GPT-4 52 136 12
GPT-4
⃝4 GPT-4 Turbo 120 77 3
Table 6: Number of times the judge chooses the answers
of each debater based on different LLM.
negative side, which is believed to contribute to
the performance improvement in MAD. When
encountering complex tasks, the affirmative side
tends to make mistakes that should be corrected
by the opposing side to achieve improvements.
• Debaters of Different LLMs (Rows ⃝3 and ⃝4 ):
We find that the judge shows a preference to
the side with the same LLM as the backbone.
This bias indicates that LLMs might not be a fair
judge (Wang et al., 2023) when different LLMs
are used for the agents.
4.3 Analysis of Debaters
In this section, we will discuss several factors of de-
baters that would affect the performance of MAD:
debater number, debate level, and debate iteration.
Increasing the number of debaters fails when
backbone LLMs are poor at long-text modeling.
It seems intuitive that increasing the number of
debaters would enhance diversity of thought and
subsequently improve performance. However, as
shown in Table 7, an increase in the number of
debaters has resulted in varying degrees of perfor-
mance reduction.
To address this issue, we manually analyze the
debate processes in approximately 10% of the test
erocS
namuH
4.5
4.0
3.5
3.0
2.5
selpmaS
fo
rebmuN
200
Number of Samples
Baseline
MAD
150
3.81
3.72
100
3.25
3.16
3.00
50 2.88
0
1 2 3
Iteration
Figure 4: Distribution of iteration rounds and a human
score of each iteration subset.
# of Debaters COMET HUMAN
2 (Default) 84.4 3.69
3 83.1 3.58
4 82.9 3.49
Table 7: Translation performance with more debaters.
subset. As the number of debaters increases, the
length and complexity of the text also increase.
Such LLM-based debaters tend to forget the views
of other debaters during the debate. Moreover, it
becomes more challenging for the judge to extract
information from the debates for summarization.
This suggests that the key challenge of MAD with
more debaters lies in the limitations of the LLMs
to handle long texts (Liu et al., 2024).
Appropriate "tit for tat" is beneficial for effec-
tive debate. We then study how the intensity of
“tit for tat” affects the performance of MAD. To
achieve so, we design different instructions (see Ta-
ble 11 in Appendix) to initialize the debaters’ meta
prompt. As shown in Figure 3, asking the debaters
to “tit for tat” (i.e., higher disagreement) is neces-
sary for MAD to achieve good performance. How-
ever, we find that “must disagree with each other on
every point ” (with a disagreement of 0.988) does
not lead to the best performance. We speculate that
continuous disagreement without finding common
ground can contribute to polarization, where the
debate becomes more about winning the argument
than seeking truth or understanding. This can re-
inforce pre-existing biases and make it difficult to
reach a meaningful consensus.
Complex questions require more iteration
rounds of debate. In our experimental setup, we
did not implement any additional stopping strate-

## Page 8

TEMOC
82.5 5 Related Work
Multi-Agent Debate
Self-Reflection
82.0 Chain-of-Thought Prompting. Recently, (Wei
Adaptive Break
et al., 2022) has proposed chain-of-thought (CoT)
81.5 prompting to improve the reasoning ability of
LLMs. Specifically, CoT prompts LLMs to gener-
81.0
ate a series of intermediate steps that lead to the
final answer of a multi-step problem. Most earlier
80.5
work primarily concentrates on two main aspects:
80.0 prompt design and decoding strategies. Zero-shot
0 1 2 3 4 5
CoT (Kojima et al., 2022) employs the trigger sen-
Iteration
tence “Let’s think step by step” to provide guid-
Figure 5: Performance with respect to the iteration of
ance for the decoding of LLMs. Advanced sam-
debate or self-reflection.
pling strategies have been explored to improve CoT
by generating diverse reasoning paths, e.g., Self-
gies besides setting the maximum debate iteration Consistency (Wang et al., 2022), Auto-CoT (Zhang
to 3. In other words, the judge can take an adaptive et al., 2022), Active-Prompting (Diao et al., 2023),
break if it believes the optimal answer has already Complexity-based Consistency (Fu et al., 2022),
been obtained, efficiently ending the debate early. Multi-Chain Reasoning (Yoran et al., 2023), and
To understand the distribution of iteration rounds Progressive-Hint Prompting (Zheng et al., 2023).
and factors contributing to a longer debate process, With the emergence of powerful LLMs, ap-
we analyze the experimental results and present proaches based on self-evaluation have attracted
them in Figure 4. In the majority of cases, the increasing attention. These approaches involve
optimal answer can be achieved through a single the generation of initial output, followed by eval-
round of debate, demonstrating the efficiency of uating the output to acquire feedback, which is
MAD. However, when translating more complex then utilized to refine the output. Evaluation
sentences (subsets with lower human scores), the feedback can come from the model itself, e.g.,
judge requires additional iterations to gather ade- Self-refine (Madaan et al., 2024) and Tree of
quate information from the debaters before mak- Thoughts (Yao et al., 2024)) or external environ-
ing a final decision. We also find that our MAD ments, e.g., QAaP (Zhu et al., 2023b) and Reflec-
framework consistently brings performance im- tion (Shinn et al., 2024). The intuition behind these
provements across all the three subsets, demon- approaches involves the utilization of robust LLMs
strating its effectiveness. to mimic the human cognition process.
Adaptive break plays an important role to con- Generative Agents. Recently, LLM-based multi-
clude the debate in the optimal moment. In- agent intelligent, e.g., Generative Agents (Park
tuitively, longer debates would encourage more et al., 2023), Ghost in the Minecraft (Zhu et al.,
diverse thinking. It raises the question of how 2023c), GPT-Bargaining (Fu et al., 2023), has
the model’s performance would be affected if con- drawn significant attention for enabling simulations
strained to conclude at a specific debate round. For of human behavior. Our work follows this research
each iteration, we force the judge J to extract the line to address the DoT problem of LLMs. Con-
final answer (a = J (H)) instead of adaptively current with our work, a few studies (Xiong et al.,
e
breaking the debate as in MAD. 2023; Du et al., 2023) also explore the multi-agent
As shown in figure 5, we can observe that MAD debate framework to enhance the reasoning abil-
performs better than self-reflection as the iteration ity of LLMs. The main differences between our
increases. However, the highest COMET score ap- MAD framework and these works are: (1) we in-
pears at the first iteration and is also lower than the troduce an additional judge with an adaptive break
result of the adaptive break. It indicates that, for mechanism to decide the optimal moment to con-
most examples, MAD can generate good transla- clude the debate; (2) our work aims to address the
tions at the first iteration such that the debate should DoT problem, which is an inherent deficiency of
be stopped. Forcing the debate to continue will LLMs; and (3) we empirically find that our MAD
harm the translation results, which demonstrates framework can yield enhanced performance by em-
the reasonableness of our adaptive break strategy. ploying agents with the identical backbone LLM.

## Page 9

6 Conclusion Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian,
Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias
We propose and define the Degeneration-of- Plappert, Jerry Tworek, Jacob Hilton, Reiichiro
Thought (DoT) problem in self-reflection, and Nakano, et al. 2021. Training verifiers to solve math
word problems. arXiv preprint arXiv:2110.14168.
address it by proposing the Multi-Agent De-
bate (MAD) framework to explore divergent chain- Kahneman Daniel. 2017. Thinking, fast and slow. Far-
of-thoughts. We demonstrate the effectiveness rar, Straus and Giroux.
of MAD on two challenging tasks and find that
Shizhe Diao, Pengcheng Wang, Yong Lin, and Tong
GPT-3.5-Turbo with MAD can even surpass Zhang. 2023. Active prompting with chain-of-
GPT-4 on the Common MT dataset. Extensive anal- thought for large language models. arXiv preprint
yses suggest that the adaptive break strategy of arXiv:2302.12246.
debate and the modest level of “tit for tat” state
Yilun Du, Shuang Li, Antonio Torralba, Joshua B Tenen-
are required for MAD to obtain good performance. baum, and Igor Mordatch. 2023. Improving factual-
Complex samples require more rounds of debate. ity and reasoning in language models through multia-
gent debate. arXiv preprint arXiv:2305.14325.
More interestingly, we find that LLMs might not be
a fair judge if different LLMs are used for agents. Yao Fu, Hao Peng, Tushar Khot, and Mirella Lapata.
Future work includes scheduling more agents in 2023. Improving language model negotiation with
the debate in an appropriate manner, multi-agent self-play and in-context learning from ai feedback.
arXiv preprint arXiv:2305.10142.
intelligence for board games, and AI feedback for
model alignment. Yao Fu, Hao Peng, Ashish Sabharwal, Peter Clark,
and Tushar Khot. 2022. Complexity-based prompt-
Limitations ing for multi-step reasoning. arXiv preprint
arXiv:2210.00720.
A limitation of this work is that our method re-
Xavier Garcia, Yamini Bansal, Colin Cherry, George
quires more time cost, as agents need to engage in
Foster, Maxim Krikun, Melvin Johnson, and Orhan
multiple rounds of interaction to present and refute Firat. 2023. The unreasonable effectiveness of few-
arguments. Moreover, current LLM-based agents shot learning for machine translation. In Inter-
national Conference on Machine Learning, pages
may struggle to maintain coherence and relevance
10867–10878. PMLR.
in long context scenarios, leading to potential mis-
understandings and loss of context. Enhancing Zhibin Gou, Zhihong Shao, Yeyun Gong, Yelong Shen,
Yujiu Yang, Nan Duan, and Weizhu Chen. 2023.
long-text modeling capability of large language
Critic: Large language models can self-correct with
models remains a future challenge. LLM-based
tool-interactive critiquing.
judge may have a preference for outputs generated
by itself. To mitigate this bias within the MAD Jie He, Tao Wang, Deyi Xiong, and Qun Liu. 2020.
The box is in the pen: Evaluating commonsense rea-
framework, we recommend that all roles, including
soning in neural machine translation. In Findings
both the judge and debaters, utilize the same LLM,
of the Association for Computational Linguistics:
or alternatively, that the judge and debaters employ EMNLP 2020, pages 3662–3672, Online. Association
distinct LLMs. for Computational Linguistics.
Zhiwei He, Tian Liang, Wenxiang Jiao, Zhuosheng
Zhang, Yujiu Yang, Rui Wang, Zhaopeng Tu, Shum-
References ing Shi, and Xing Wang. 2024. Exploring human-
like translation strategy with large language models.
Yejin Bang, Samuel Cahyawijaya, Nayeon Lee, Wen-
Transactions of the Association for Computational
liang Dai, Dan Su, Bryan Wilie, Holy Lovenia, Ziwei
Linguistics, 12:229–246.
Ji, Tiezheng Yu, Willy Chung, et al. 2023. A multi-
task, multilingual, multimodal evaluation of chatgpt Amr Hendy, Mohamed Abdelrehim, Amr Sharaf,
on reasoning, hallucination, and interactivity. In Pro- Vikas Raunak, Mohamed Gabr, Hitokazu Matsushita,
ceedings of the 13th International Joint Conference Young Jin Kim, Mohamed Afify, and Hany Hassan
on Natural Language Processing and the 3rd Confer- Awadalla. 2023. How good are gpt models at ma-
ence of the Asia-Pacific Chapter of the Association chine translation? a comprehensive evaluation. arXiv
for Computational Linguistics (Volume 1: Long Pa- preprint arXiv:2302.09210.
pers), pages 675–718.
Mohammad Javad Hosseini, Hannaneh Hajishirzi, Oren
Lisa Bortolotti. 2011. Does reflection lead to wise Etzioni, and Nate Kushman. 2014. Learning to solve
choices? Philosophical Explorations, 14(3):297– arithmetic word problems with verb categorization.
313. In Proceedings of the 2014 Conference on Empirical

## Page 10

Methods in Natural Language Processing (EMNLP), Aarohi Srivastava, Abhinav Rastogi, Abhishek Rao,
pages 523–533. Abu Awal Md Shoeb, Abubakar Abid, Adam Fisch,
Adam R Brown, Adam Santoro, Aditya Gupta, Adrià
Wenxiang Jiao, Wenxuan Wang, Jen-tse Huang, Xing Garriga-Alonso, et al. 2023. Beyond the imitation
Wang, Shuming Shi, and Zhaopeng Tu. 2023. Is chat- game: Quantifying and extrapolating the capabili-
gpt a good translator? yes with gpt-4 as the engine. ties of language models. Transactions on Machine
arXiv preprint arXiv:2301.08745. Learning Research.
Mirac Suzgun, Nathan Scales, Nathanael Schärli, Se-
Machiel Keestra. 2017. Metacognition and reflection
bastian Gehrmann, Yi Tay, Hyung Won Chung,
by interdisciplinary experts: Insights from cognitive
Aakanksha Chowdhery, Quoc Le, Ed Chi, Denny
science and philosophy. Issues in Interdisciplinary
Zhou, et al. 2023. Challenging big-bench tasks and
Studies, 35:121–169.
whether chain-of-thought can solve them. In Find-
ings of the Association for Computational Linguistics:
Takeshi Kojima, Shixiang Shane Gu, Machel Reid, Yu-
ACL 2023, pages 13003–13051.
taka Matsuo, and Yusuke Iwasawa. 2022. Large lan-
guage models are zero-shot reasoners. Advances in
Peiyi Wang, Lei Li, Liang Chen, Zefan Cai, Dawei Zhu,
neural information processing systems, 35:22199–
Binghuai Lin, Yunbo Cao, Qi Liu, Tianyu Liu, and
22213.
Zhifang Sui. 2023. Large language models are not
fair evaluators. arXiv preprint arXiv:2305.17926.
Yuqing Kong, Yunqi Li, Yubo Zhang, Zhihuan Huang,
and Jinzhao Wu. 2022. Eliciting thinking hierarchy Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc Le,
without a prior. Advances in Neural Information Ed Chi, Sharan Narang, Aakanksha Chowdhery, and
Processing Systems, 35:13329–13341. Denny Zhou. 2022. Self-consistency improves chain
of thought reasoning in language models. arXiv
Nelson F Liu, Kevin Lin, John Hewitt, Ashwin Paran- preprint arXiv:2203.11171.
jape, Michele Bevilacqua, Fabio Petroni, and Percy
Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten
Liang. 2024. Lost in the middle: How language mod-
Bosma, Fei Xia, Ed Chi, Quoc V Le, Denny Zhou,
els use long contexts. Transactions of the Association
et al. 2022. Chain-of-thought prompting elicits rea-
for Computational Linguistics, 12:157–173.
soning in large language models. Advances in neural
information processing systems, 35:24824–24837.
Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler
Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon,
Haoran Wu, Wenxuan Wang, Yuxuan Wan, Wenxiang
Nouha Dziri, Shrimai Prabhumoye, Yiming Yang,
Jiao, and Michael Lyu. 2023. Chatgpt or grammarly?
et al. 2024. Self-refine: Iterative refinement with
evaluating chatgpt on grammatical error correction
self-feedback. Advances in Neural Information Pro-
benchmark. arXiv preprint arXiv:2303.13648.
cessing Systems, 36.
Kai Xiong, Xiao Ding, Yixin Cao, Ting Liu, and Bing
Joon Sung Park, Joseph O’Brien, Carrie Jun Cai, Mered- Qin. 2023. Diving into the inter-consistency of large
ith Ringel Morris, Percy Liang, and Michael S Bern- language models: An insightful analysis through de-
stein. 2023. Generative agents: Interactive simulacra bate. arXiv preprint arXiv:2305.11595.
of human behavior. In Proceedings of the 36th An-
nual ACM Symposium on User Interface Software Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran,
and Technology, pages 1–22. Tom Griffiths, Yuan Cao, and Karthik Narasimhan.
2024. Tree of thoughts: Deliberate problem solving
Jonathan Pilault, Xavier Garcia, Arthur Bražinskas, and with large language models. Advances in Neural
Orhan Firat. 2023. Interactive-chain-prompting: Am- Information Processing Systems, 36.
biguity resolution for crosslingual conditional gen-
Haiyan Yin, Dingcheng Li, Xu Li, and Ping Li. 2020.
eration with interaction. In Proceedings of the 13th
Meta-cotgan: A meta cooperative training paradigm
International Joint Conference on Natural Language
for improving adversarial text generation. In Pro-
Processing and the 3rd Conference of the Asia-Pacific
ceedings of the AAAI Conference on Artificial Intelli-
Chapter of the Association for Computational Lin-
gence, volume 34, pages 9466–9473.
guistics (Volume 1: Long Papers), pages 455–483.
Ori Yoran, Tomer Wolfson, Ben Bogin, Uri Katz, Daniel
Subhro Roy and Dan Roth. 2015. Solving general arith-
Deutch, and Jonathan Berant. 2023. Answering
metic word problems. In Proceedings of the 2015
questions by meta-reasoning over multiple chains of
Conference on Empirical Methods in Natural Lan-
thought. In Proceedings of the 2023 Conference on
guage Processing, pages 1743–1752.
Empirical Methods in Natural Language Processing,
pages 5942–5966.
Noah Shinn, Federico Cassano, Ashwin Gopinath,
Karthik Narasimhan, and Shunyu Yao. 2024. Re- Zhuosheng Zhang, Aston Zhang, Mu Li, and Alex
flexion: Language agents with verbal reinforcement Smola. 2022. Automatic chain of thought prompt-
learning. Advances in Neural Information Process- ing in large language models. arXiv preprint
ing Systems, 36. arXiv:2210.03493.

## Page 11

Chuanyang Zheng, Zhengying Liu, Enze Xie, Zhenguo
Li, and Yu Li. 2023. Progressive-hint prompting
improves reasoning in large language models. arXiv
preprint arXiv:2304.09797.
Xinyu Zhu, Junjie Wang, Lin Zhang, Yuxiang Zhang,
Yongfeng Huang, Jiaxing Zhang, Yujiu Yang, et al.
2023a. Solving math word problems via cooperative
reasoning induced language models. In The 61st An-
nual Meeting Of The Association For Computational
Linguistics.
Xinyu Zhu, Cheng Yang, Bei Chen, Siheng Li, Jian-
Guang Lou, and Yujiu Yang. 2023b. Question an-
swering as programming for solving time-sensitive
questions. In Proceedings of the 2023 Conference on
Empirical Methods in Natural Language Processing,
pages 12775–12790.
Xizhou Zhu, Yuntao Chen, Hao Tian, Chenxin Tao, Wei-
jie Su, Chenyu Yang, Gao Huang, Bin Li, Lewei Lu,
Xiaogang Wang, et al. 2023c. Ghost in the minecraft:
Generally capable agents for open-world enviroments
via large language models with text-based knowledge
and memory. arXiv preprint arXiv:2305.17144.

## Page 12

A Challenging Testbeds
We conduct experiments on two challenging tasks, namely, commonsense machine translation (i.e.,
Common MT), and counter-intuitive arithmetic reasoning (i.e., Counter-Intuitive AR), which require deep
levels of contemplation for LLMs.
A.1 Commonsense Machine Translation
Ambiguity Type Source Sentence Correct Reference Incorrect Translation
吃掉敌人一个师。 Destroy a division of the enemy. Eat up an enemy division.
Lexical
他喜欢吃苹果。 He likes to eat apples. He likes to destory apples.
正在手术的 是 健 康 的 A healthy doctor is doing surgery. What is undergoing surgery is a
医生。 doctor who is healthy.
Contextless
正在手术的 是 生 命 垂 What is undergoing surgery is a pa- A patient whose life is dying is
危的病人。 tient whose life is dying. doing surgery.
当 地 震 袭 击 中 国 When the earthquake hit China, When the earthquake hit China,
时，援助的是中国。 China was aided. China has assisted.
Contextual
当 地 震 袭 击 日 本 When the earthquake hit Japan, When the earthquake hit Japan,
时，援助的是中国。 China has assisted. China was aided.
Table 8: Examples of lexical, contextual and contextless syntactic ambiguity from the Common MT dataset. The
underlined Chinese words are translated into the corresponding colored words in English. Best viewed in color.
The Common MT dataset is composed of Chinese⇒English translation examples (He et al., 2020),
which are used to examine three types of ambiguity resolution abilities of translation models. Specifically,
The Common MT test set we used covers 200 examples of lexical ambiguity, 450 examples of contextless
syntactic ambiguity, and 350 examples of contextual syntactic ambiguity. Within the challenging part
of Common MT, the authentic translation of each source sentence requires a proper understanding of
common sense knowledge. While these ambiguous sentences might appear to have a straightforward
translation, such a literal interpretation is erroneous. Failure to identify and address such ambiguities may
result in inaccurate translations.
Table 8 lists some examples of these three types of ambiguity. Lexical ambiguity refers to words with
multiple meanings in different contexts. Contextless and contextual syntactic ambiguity involve sentences
with multiple interpretations, which can be resolved by context or common sense. As the lexical ambiguity
of “吃掉敌人一个师” shows, the source word “吃掉” should be translated to “destroy” rather than the
straightforward translation “eat up” by considering the common sense in the real world.
A.2 Counter-Intuitive Arithmetic Reasoning
Previous studies on thinking hierarchy (Daniel, 2017) suggest that we humans have a fast and intuitive
system and a slow and logical system, and tend to run the lower level system before the higher level one.
Inspired by this, we created a more challenging dataset named Counter-Intuitive Arithmetic Reasoning
(CIAR) to evaluate the reasoning abilities of LLMs at deep levels.
Dataset Description. Our Counter-Intuitive AR dataset contains 200 questions collected from elicitation
questions (Kong et al., 2022)8, web data9 and additional manual derivatives of these questions. Compared
to the commonly-used datasets, e.g., MultiArith (Roy and Roth, 2015), GSM8K (Cobbe et al., 2021), our
dataset presents two distinct challenges:
• Resistance to Intuition. The questions in our dataset are embedded in hidden traps designed to elicit
intuitive and appealing answers that are often incorrect. This feature evaluates the abilities of LLMs to
resist the traps of superficial expressions.
8https://elicitation.info/questionnaire/1/
9https://www.geeksforgeeks.org/puzzles/

## Page 13

Components Content
Question When Alice walks up the hill, her speed is 1 m/s and when she goes down the
hill, her speed is 3 m/s. Then when Alice walks up and down the hill, what is
her average speed?
Correct Answer 1.5 m/s
Explanation If Alice covers a distance of d going up and down the hill, then her total distance
is 2d. Her time going up the hill is d/1 = d, and her time going down the hill is
d/3. So, her total time is d + d/3 = 4d/3. Therefore, her average speed is 2d /
(4d/3) = 3/2 m/s.
Incorrect Answer 2 m/s
Explanation Alice’s average speed can be calculated by adding her speed going up the hill
and her speed going down the hill, and then dividing by 2. So, (1 m/s + 3 m/s) /
2 = 2 m/s. Therefore, Alice’s average speed is 2 m/s.
Table 9: An example in Counter-Intuitive AR dataset.
• Multi-Step Reasoning. Each correct answer within the dataset requires a rigorous multi-step reasoning
process, thereby evaluating the capacity of LLMs to engage in complex decision-making and problem-
solving.
Dataset Format. In our Counter-Intuitive AR dataset, each example contains three key components
(see Table 9 for an example). We elaborate on the details below:
• Questions. The questions in our dataset are designed to stimulate counter-intuitive thinking, which
aims to challenge conventional decision-making by presenting situations where the immediate, intuitive
response is often incorrect.
• Answers. Each question is provided with a correct answer, which requires deep comprehension of the
question and commonsense knowledge. Additionally, we also provide a plausible yet incorrect answer
for comparison.
• Explanations. We offer comprehensive explanations for each correct answer, detailing the step-by-step
rationale that leads to the right solution. We also provide the seemingly logical reasoning process
behind incorrect answers. This reasoning process highlights the potential pitfalls and misconceptions
during decision-making, especially when intuition is prioritized over rigorous logical reasoning.
Experimental Settings. During our experiments, we did not utilize the explanations from the dataset.
We provided detailed explanations to facilitate subsequent researchers to understand how the correct
answer was derived.
B Human Evaluation Details
We implement human evaluation as follows:
• Human Score: We randomly shuffled the display order of the translated sentences from all methods in
an anonymous manner. Then, employed three professional human translators (Krippendorff’s Alpha =
0.76) to directly assess all methods together. Finally, we calculated the average scores for each methods.
• Bias: We also focus on whether the translation of specific words in CommonMT conforms to common-
sense. Table 8 lists an example of lexical ambiguity, where the source word “吃掉” should be translated
to “destroy” rather than the straightforward translation “eat up”. Here, we asked the annotators to label
each sentence as 1 (not conforming to commonsense) or 0 (conforming to commonsense), and report
the degree of bias for the whole test set.

## Page 14

C Results on math and symbolic reasoning tasks
Math Reasoning Symbolic Reasoning (BBH)
Method
GSM AddSub Penguin Date Colored Objects
CoT 70.2 87.3 58.9 56.4 57.2
Self-Reflect 70.8 87.6 61.0 58.0 58.0
MAD 73.8 92.1 63.7 65.2 58.8
Table 10: Comparison of accuracy on math (e.g. GSM (Cobbe et al., 2021) and AddSub (Hosseini et al., 2014)) and
symbolic reasoning (three datasets from Big-Bench (Srivastava et al., 2023; Suzgun et al., 2023)).
D Prompts for Different Debate Levels
Level Prompt
Both sides must reach a full consensus on every point of the debate. Every statement
0
must be agreed upon by both sides.
Most of the debate should be characterized by disagreements, but there may still be a
1
small amount of consensus on less significant points.
It’s not necessary to fully agree with each other’s perspectives, as our objective is to
2 (Default)
find the correct answer.
Both sides must disagree with each other on every point of the debate. There should
3
be no consensus whatsoever.
Table 11: Prompts for different levels of “tit for tat” state. We modulate the level of “tit for tat” state outlined in
Section 2 through appending natural language instructions to the debaters’ meta prompt.
E Extra Computational Cost
Method Cost (# Generated Tokens)
COT 1.0
Self-Reflect 1.83×
MAD 2.46×
Table 12: Extra generated tokens on the counter-intuitive AR task.
We measure the inference cost by the number of generated tokens. As listed in Table 12, the self-
reflection cost is 1.83 times that of the baseline COT method. Meanwhile, our MAD approach incurs an
additional 0.63 times the inference cost. This increase in cost is deemed acceptable given the significant
benefit our approach offers in enhancing LLMs’ divergent thinking capabilities without requiring external
signals (interaction with humans).

## Page 15

F Debate Process
F.1 Commonsense Machine Translation
Table 13 presents the debate process of example translation discussed in Section 3.3. In this debate, both
sides disputed the English translation of the Chinese sentence “吃掉敌人一个师”. The affirmative side
proposed “eat up an enemy division”, advocating for a more literal translation to depict the consumption
or devouring of the enemy. In contrast, the negative side suggested “eliminate an enemy division”, arguing
this expression better conveys the destruction of the enemy in a military context. After the debate, the
judge favored “eliminate”, as it accurately reflected the severity and intent of the original military language.
This debate highlights the complexities of translation, where context and nuance significantly impact
the selection of appropriate words. In response to this issue, our MAD method helps LLMs understand
semantics correctly and generate highly authentic translations.
<Debate Topic>: What is the correct English translation of the following text: 吃掉敌人一个师?
I believe the correct translation of the Chinese text “吃掉敌人一个师” is “Eat up an enemy
division.” The word “吃掉” literally means “eat up” or “consume.”
I disagree with your translation. I believe the correct translation of the Chinese text “吃掉
敌人一个师” is “Eliminate an enemy division.” While “吃掉” can be translated as “eat up” or
“consume”, it can also mean “eliminate” or “annihilate” in a military context. In this case, it is more
appropriate to use “eliminate” as it conveys the idea of completely destroying the enemy division.
Both sides presented valid arguments and translations that accurately convey the meaning of
the original Chinese text. The choice between “eat up” and “eliminate” may depend on the context
and tone of the text. Therefore, there is no clear preference for either side at this time.
While “eliminate” does convey the idea of completely destroying the enemy division, it doesn’t
capture the connotation of consuming or devouring the enemy that is implied by “吃掉”.
In a military context, “吃掉” is often used to describe the complete destruction of the enemy,
rather than the consumption of their resources or territory.
Both sides presented valid arguments, but the negative side’s argument that “eliminate” better
captures the intensity and seriousness of the military language used in the original Chinese text was
more convincing. Additionally, “eliminate” accurately conveys the idea of completely destroying
the enemy division. Therefore, the correct English translation of the Chinese text “吃掉敌人一个
师” is “Eliminate an enemy division.”
Table 13: The debate process of translation example on Chinese sentence “吃掉敌人一个师”.

## Page 16

F.2 Counter-Intuitive Arithmetic Reasoning
Table 14 shows the debate process of example answer in Table 9. This debate is about calculating Alice’s
average speed while walking up and down a hill, with speeds given as 1 m/s uphill and 3 m/s downhill.
Initially, it was incorrectly proposed by affirmative side to just average the uphill and downhill speeds. The
negative side, which is correct, states that average speed is total distance divided by total time. Given that
the distances up and down the hill are equal, we must calculate the total time taken for the two directions
before finding the average speed. Therefore, the average speed is calculated using the sum of the uphill
and downhill distances (twice the distance of the hill) and the sum of the time taken for each (d/1 for uphill
and d/3 for downhill). This leads to an average speed of 1.5 m/s, not 2 m/s as the affirmative side proposed.
And the judge also supports the response from the negative side. Here, LLMs made a common mistake
initially in understanding the concept of average speed. Our MAD method encourages divergent thinking
and effectively prevents intuitive but incorrect responses, leading to the correct method for calculating
average speed.
<Debate Topic>: When Alice walks up the hill, her speed is 1 m/s and when she goes down the
hill, her speed is 3 m/s. Then when Alice walks up and down the hill, what is her average speed?
Alice’s average speed can be calculated by adding her speed going up the hill and her speed
going down the hill, and then dividing by 2. So, (1 m/s + 3 m/s) / 2 = 2 m/s. Therefore, Alice’s
average speed is 2 m/s.
I disagree with your answer. The problem doesn’t give us any information about the distance
Alice covers while going up and down the hill. So, we cannot simply add her speeds and divide by
2 to get her average speed. We need to know the distance she covers to calculate her average speed.
The average speed is calculated by dividing the total distance by the total time taken. As Alice
walks up and down the hill, the distance covered in both directions is the same. Therefore, the total
distance covered is 2 times the distance of either direction.
That’s a good point. But we can assume that Alice covers the same distance going up and down
the hill. In that case, we can use the formula for average speed, which is total distance divided by
total time. If Alice covers a distance of d going up and down the hill, then her total distance is 2d.
Her time going up the hill is d/1 = d, and her time going down the hill is d/3. So, her total time is d
+ d/3 = 4d/3. Therefore, her average speed is 2d/(4d/3) = 3/2 m/s.
Thank you for providing your answer. This average speed of 1.5 m/s takes into account both
the uphill and downhill speeds, providing a balanced representation of Alice’s overall performance
while walking up and down the hill.
Yes. Let’s assume the distance is d. The time taken to walk up the hill is d/1 and the time taken
to walk down the hill is d/3. The total time taken is d/1 + d/3 = 4d/3. Therefore, the average speed
is (2d)/(4d/3) = 1.5 m/s. Hence, the negative side is correct.
Table 14: The debate process of arithmetic reasoning example.
