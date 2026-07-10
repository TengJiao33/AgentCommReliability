# cotie-communicate-while-thinking-cot-state-communication-2026-openreview

- Source PDF: `cotie-communicate-while-thinking-cot-state-communication-2026-openreview.pdf`
- Extracted at UTC: `2026-07-09T06:20:55.323042+00:00`
- Pages: 30
- Title: 
- SHA256: `ca33cf246f20363d7d87868003452ba92ce0bd8ef3bdb5243b9554542da0c03f`

## Page 1

Communicate While Thinking: CoT-state Communication for Better and
Token-Efficient Multi-Agent Reasoning
Anonymous ACL submission
Abstract
001
002 Multi-agent LLM systems often coordinate
003 only after agents complete their local Chain-of-
004 Thought (CoT), by exchanging final answers,
005 critiques, or rationales. This output-level com-
006 munication can arrive too late: intermediate
007 assumptions, evidence choices, or computation
008 errors may already have shaped the final answer
009 before peer information is used.
010 We introduce COTIE (CoT-State Inter-Agent
011 Exchange), a multi-agent reasoning approach
012 that shifts communication from final outputs
013 to intermediate CoT states. Instead of wait- Figure 1: Better performance with lower token usage
014 ing for completed answers, a caller agent can on cooperative MultiAgentBench. Compared with
015 request focused help from a peer during ongo- output-level message passing, COTIE improves sce-
016 ing reasoning and integrate the response before nario scores while reducing token usage across Coding,
017 producing the final answer. The key idea is Research, and Database tasks.
018 not to add a new workflow optimizer, but to
019 change where peer information is attached in
020 the reasoning process. 2024; Chen et al., 2024a; Liang et al., 2024). Once 043
an agent has committed to intermediate hypotheses, 044
021 Across MATH, HumanEval, HotpotQA, and
022 MultiAgentBench, COTIE improves task per- evidence choices, or computations during reason- 045
023 formance over output-level communication ing, these decisions may already have shaped the 046
024 baselines under matched evaluation settings. final answer. At that point, messages, critiques, 047
025 On cooperative MultiAgentBench, where to- votes, or answer-level reconciliation (Chen et al., 048
026 ken accounting is directly comparable, COTIE 2024a) may arrive too late to repair the reasoning 049
027 improves the three-scenario average score from error where it first occurred. 050
028 67.5 to 78.3 while reducing observed aver-
029 age token usage from 129,270 to 67,157 com- Figure 2 contrasts conventional output-level 051
030 pared with MAB, and raises aggregate score per communication with COTIE’s intermediate CoT- 052
031 100K tokens from 52.2 to 116.5. Code is avail- state communication. In output-level communica- 053
032 able for at https://anonymous.4open. tion, a possible local error in an early reasoning step 054
033 science/r/CoTIE-2837/. may propagate through the remaining local trace 055
1 Introduction before any peer input is introduced. This contrast 056
034
motivates the specific design question studied in 057
035 Chain-of-Thought (CoT) prompting enables step- this paper: under a fixed multi-agent setting, should 058
036 by-step reasoning in LLMs (Wei et al., 2022), peer input be introduced only after local CoT traces 059
037 and multi-agent LLM systems extend this idea by are completed, or while the caller is still reasoning 060
038 distributing complex tasks across role-specialized from an intermediate CoT state? We use communi- 061
039 agents (Hong et al., 2024; Qian et al., 2024; Wu cation attachment point to denote when peer input 062
040 et al., 2023). However, many multi-agent reasoning is introduced into the caller’s CoT process: after a 063
041 systems still postpone communication until each completed output or during an intermediate CoT 064
042 agent has completed its own CoT process (Du et al., state. COTIE adopts the latter attachment-point 065
1

## Page 2

Figure 2: CoTIE vs. output-level communication. Output-level communication exchanges peer information only
after local CoT completion, whereas COTIE attaches communication to an intermediate CoT state and integrates
the response before finalization.
066 principle rather than introducing a new workflow while reducing observed average token usage from 092
067 optimizer or fixed routing policy. At an interme- 129,270 to 67,157; it also improves aggregate score 093
068 diate reasoning step, the caller sends a bounded, per 100K tokens from 52.2 to 116.5 compared with 094
069 state-derived request containing the relevant task MAB. 095
070 slice, a short partial trace, the current help need, and
071 the requested help type. The peer returns a targeted Contributions. 096
072 response or sub-result, which the caller integrates • COTIE as a novel CoT-state communication 097
073 before producing the final answer. Algorithm 1 for- approach. We introduce COTIE, a new ap- 098
074 malizes this mechanism through configurable peer proach to multi-agent CoT reasoning in which 099
075 selection (line 7), request-option selection (line 8), agents exchange information through interme- 100
076 pre-final message sending (line 10), and response diate CoT states rather than only through com- 101
077 integration (line 12). pleted outputs. This makes the communication at- 102
078 Empirically, the main comparison is between tachment point an explicit design choice in multi- 103
079 final-output-level communication, Late CoT Mes- agent LLM reasoning. 104
080 sage Passing, and CoT-state communication. On • An efficient step-level COTIE algorithm. Be- 105
081 the general benchmarks, we use the same two-agent yond the general CoT-state communication prin- 106
082 setting, backbone model, task input, and final inte- ciple, we instantiate COTIE as an efficient step- 107
083 gration rule. On MultiAgentBench, we preserve the level algorithm, formalized in Algorithm 1. The 108
084 benchmark-provided agent topology and replace algorithm realizes CoT-state exchange through 109
085 the output-level coordination opportunity with in- a compact request–response–integration proce- 110
086 termediate CoT-state communication. We do not dure, enabling a caller to obtain focused peer 111
087 impose a fixed communication count or total-token input during reasoning and incorporate it before 112
088 budget; token usage is logged after execution as an finalization. 113
089 observed cost of each protocol. On the coopera- • Higher task performance. Across MATH, 114
090 tive MultiAgentBench scenarios, COTIE improves HumanEval, HotpotQA, and MultiAgentBench, 115
091 the three-scenario average score from 67.5 to 78.3 COTIE improves task performance over output- 116
2

## Page 3

117 level communication baselines. This suggests where trace (t) is the reasoning trace produced so 164
i
118 that introducing peer information during interme- far, h (t) is the agent’s current intermediate conclu- 165
i
119 diate reasoning can be more useful than exchang- (t)
sion or partial answer, u is the specific point the 166
120 ing information only after agents have completed i
agent wants help with at step t, such as a missing 167
121 their local CoT traces.
computation, an unclear condition, a verification 168
122 • Higher token utilization efficiency. The to-
need, or a task fragment that it cannot complete 169
123 ken reduction is consistent with COTIE’s de- (t)
confidently, and C records previous cross-agent 170
124 sign: peer information is made available earlier i
requests made during the same run. 171
125 in the reasoning process, which can reduce re-
126 dundant downstream reasoning and final-stage Definition 3 (CoTIE request). A COTIE request 172
127 coordination content. On the cooperative Multi- is a step-level cross-agent message sent from caller 173
128 AgentBench scenarios, where token accounting a i to target agent a j while a i is still reasoning. It 174
129 is directly comparable, COTIE reduces token us- has the form 175
130 age and obtains higher task performance per unit (t) (cid:0) (t) (t)
m = t, P , trace , h ,
131 of token cost than output-level communication i→j slice i,short i
176
132 baselines. Since no fixed token budget is im- u (t) , r (t) , µ (t) , ϕ (cid:1) .
i i i
133 posed, token usage is measured after execution
134 as an outcome of each protocol rather than as a where t is the caller’s current CoT step, P slice is the 177
135 pre-specified constraint. part of the task relevant to the request, trace (t) 178
i,short
136 Overall, these results show that COTIE improves is a summarized or compressed view of the rea- 179
137 reasoning quality and token efficiency by intro- soning produced so far, h (t) is the caller’s current 180
i
138 ducing peer input during intermediate reasoning intermediate conclusion or partial answer, u (t) is 181
i
139 rather than after completed outputs. (t)
the specific help needed at step t, r is the re- 182
i
(t)
140 2 Method quested help type, µ i ∈ {CONSULT, INJECT} is 183
the request option, and ϕ is the expected reply for- 184
141 2.1 Overview mat. 185
142 COTIE changes where cross-agent communication This distinguishes COTIE from final-output- 186
143 is attached in multi-agent Chain-of-Thought rea- level communication, where agents first complete 187
144 soning. Rather than exchanging information only their own CoT processes and only then exchange 188
145 after local reasoning is complete, a caller agent answers, rationales, critiques, or votes. We make 189
146 sends a compact request based on its current CoT this distinction operational through three criteria. 190
147 state during ongoing reasoning, receives a targeted Definition 4 (CoT-state communication). We treat 191
148 peer response, and integrates it before finalization. an exchange as CoT-state communication when it 192
149 We first define the multi-agent setting, CoT state, satisfies the following operational criteria, corre- 193
150 and CoT-state request, and then instantiate the prin- sponding to the state-message-integration sequence 194
151 ciple as a step-level algorithm. The same interface in Algorithm 1: 195
152 supports CONSULT and INJECT requests, while re- C1. Active caller state. The caller maintains an 196
153 maining independent of any particular triggering, intermediate CoT state σ (t) and has not yet 197
i
154 routing, or workflow-optimization policy. finalized its answer. The exchange is therefore 198
attached to a live reasoning step of the caller, 199
155 2.2 CoTIE Approach
rather than to a completed local output. 200
156 Definition 1 (Multi-agent reasoning system). A C2. State-conditioned message construction. 201
157 multi-agent reasoning instance is a tuple (N , τ, G), Given σ (t) , the caller selects a reachable peer 202
i
158 where N = {a 1 , . . . , a n } is a set of role- a j with (a i , a j ) ∈ G, chooses a request op- 203
159 specialized agents, τ is the input task, and G ⊆ tion µ (t) ∈ {CONSULT, INJECT}, and con- 204
i
160 N × N is the allowed communication graph. (t)
structs a compact message m containing 205
i→j
161 Definition 2 (CoT state). The CoT state of agent the relevant task slice, summarized partial 206
162 a i at reasoning step t is trace, current intermediate conclusion, help 207
need, requested help type, request option, and 208
(t) (cid:0) (t) (t) (t) (t)(cid:1)
163 σ = trace , h , u , C , expected reply format. 209
i i i i i
3

## Page 4

210 C3. Pre-final state update. The peer re- Algorithm 1 COTIE: CoT-State Inter-Agent Ex-
211 sponse resp (t) is used to update change Principle
j→i
212 the caller’s next CoT state through Require: Task τ ; agents N ; allowed communication graph
(t+1) G; configuration Ω
213 an integration decision, σ i ← Ensure: Final answer yˆ
214 INTEGRATERESPONSE(σ i (t) , resp ( j t → ) i ), 1: Each agent a i ∈ N maintains an intermediate CoT state
215 before the caller produces its final answer. σ i (t) while solving τ .
2: for each reasoning agent a ∈ N do
216 If the response is used only for final voting, 3: t ← 0 i
217 final debate, or final answer selection, the 4: while a i has not finalized its answer do
218 exchange is final-output-level communication 5: a i advances or updates its local reasoning state σ i (t).
6: if a communication opportunity is invoked under Ω
219 rather than CoT-state communication. then
7: Choose a reachable peer agent a with
220 These criteria define the communication attach- j
(a , a ) ∈ G.
i j
221 ment point tested in our experiments. They do not 8: Choose a request option µ(t) ∈
i
222 require a specific JSON schema, prompt template, {CONSULT, INJECT}.
223 or agent architecture; they specify what must be 9: Construct a compact, history-summarized CoT-
state message
224 true for communication to occur during the caller’s
225 CoT process. m(t) = (cid:0) t, P , trace(t) , h(t),
i→j slice i,short i
u(t), r(t), µ(t), ϕ (cid:1) .
226 2.3 CoTIE Algorithm i i i
227 COTIE operates at the level of reasoning steps. 10: Send m( i→ t) j while a i is still reasoning, before a i
228 At each step, an agent may continue reasoning produces its final answer.
11: The peer a returns a response resp(t) accord-
229 alone, or it may issue a cross-agent request. If a re- j j→i
ing to the requested help type r(t) and reply
230 quest is issued, the caller selects a target agent and i
format ϕ.
231 chooses one of two request options: consultation or 12: The caller produces the next CoT state through
232 injection. The response is then integrated into the an integration decision before finalization:
233 caller’s CoT before the final answer is produced. σ(t+1) ← INTEGRATERESPONSE (cid:0) σ(t), resp(t) (cid:1) .
234 Algorithm 1 presents COTIE as a communica- i i j→i
235 tion principle rather than as a fixed routing or trig- 13: Record the exchange, including caller, peer, step
236 gering algorithm. The trigger policy, peer selection index, request option, request, response, integra-
tion decision, and token usage when available.
237 policy, request-option selection, and integration
238 rule are implementation choices under configura- 14: end if
239 tion Ω. What defines COTIE is the line-level se- 15: t ← t + 1
16: end while
240 quence: a caller maintains an intermediate CoT 17: s ← final answer produced by agent a .
i i
241 state (line 1), selects a reachable peer and request 18: end for
242 option (lines 7–8), sends a bounded state message 19: return yˆ using the task-specific final-answer rule.
243 before finalization (lines 9– 10), and integrates the
244 peer response into the next CoT state before pro-
nism. The key distinction is whether peer infor- 260
245 ducing the final answer (lines 11– 12).
mation enters after a completed output has been 261
246 The configuration Ω specifies implementation
produced or while the caller is still reasoning from 262
247 choices such as the triggering policy, peer-selection
an intermediate CoT state. Thus, COTIE can be 263
248 rule, request-option selection rule, communication
instantiated with fixed rules, heuristic triggers, role- 264
249 timing, context-management strategy, and integra-
based matching, or learned routing policies, but the 265
250 tion rule. Different implementations may instanti-
defining property is pre-final CoT-state exchange 266
251 ate these choices differently. In the reported exper-
and integration. 267
252 iments, Ω does not impose an explicit maximum
253 number of cross-agent requests or a fixed total- 3 Experiments
268
254 token budget. Instead, each method runs under
255 its assigned communication protocol, and token We evaluate whether replacing final-output-level 269
256 usage is measured after execution as an empirical communication with intermediate CoT-state com- 270
257 outcome. munication improves both task performance and 271
258 COTIE defines the communication attachment observed token efficiency. Table 1 reports the main 272
259 point, not a specific routing or budgeting mecha- output-level communication comparison. Table 2 273
4

## Page 5

274 compares the communication attachment point un- HotpotQA, Output-level MP exchanges final an- 324
275 der the same backbone, task inputs, agent roles, and swers or short rationales after both agents complete 325
276 final aggregation rules. The compared protocols local CoT. Output-level MP+SC and Output-level 326
277 use broadly comparable cross-agent communica- MP+SR use the same output-level communication 327
278 tion opportunities, while differing in whether peer protocol but strengthen each agent’s local reason- 328
279 information is attached after local CoT completion ing with Self-Consistency or Self-Refine before 329
280 or during an ongoing CoT state. Token usage is the exchange. Late CoT Message Passing is used 330
281 logged after execution as an observed protocol cost only in the attachment-point comparison: it keeps 331
282 rather than imposed as a fixed budget. the same late communication timing but shares 332
a summarized completed-CoT trace. On MultiA- 333
283 3.1 Experimental Setup gentBench, MAB denotes the benchmark-provided 334
284 We use DeepSeek-V3.2 (DeepSeek-AI, 2025) as output-level coordination protocol, with MAB+SC 335
285 the fixed backbone model. We evaluate on and MAB+SR as strengthened variants. Full base- 336
286 MATH (Hendrycks et al., 2021), HumanEval (Chen line definitions and prompt templates are provided 337
287 et al., 2021), HotpotQA (Yang et al., 2018), and in Appendices F and G. 338
288 three cooperative MultiAgentBench (Zhu et al.,
289 2025) scenarios: Coding, Research, and Database. 3.3 Evaluation Metrics 339
290 We use the cooperative scenarios because they We report the official task metric for each bench- 340
291 match the setting studied here, where agents share mark: accuracy for MATH, Pass@1 for Hu- 341
292 information or complete subtasks toward a joint so- manEval, EM/F1 for HotpotQA, and the official 342
293 lution; adversarial scenarios are excluded from the scenario score for MultiAgentBench. We also re- 343
294 main evaluation because they confound assistance port total token cost, defined as prompt plus com- 344
295 with debate-style interaction. pletion tokens, and use score per 100K tokens for 345
296 Across communication methods, we align the aggregate MultiAgentBench efficiency. Since our 346
297 backbone model, task input, agent roles, commu- experiments do not impose a fixed token budget, 347
298 nication graph when applicable, decoding settings, token cost should be interpreted as an observed 348
299 history-summarization strategy, and final aggrega- outcome of each protocol rather than as a con- 349
300 tion rule. The main manipulated variable is the trolled input. For MATH, HumanEval, and Hot- 350
301 attachment point of peer information: output-level potQA, token counts are reported for transparency 351
302 baselines communicate after local CoT completion, and implementation-cost comparison. Our formal 352
303 Late CoT Message Passing shares completed CoT token-efficiency analysis focuses on cooperative 353
304 summaries after local reasoning is finished, and MultiAgentBench, where the compared methods 354
305 COTIE sends a compact state-conditioned request share the same benchmark-level multi-agent set- 355
306 during ongoing reasoning and integrates the peer ting, broadly comparable cross-agent communi- 356
307 response before finalization. cation opportunities, and directly comparable to- 357
308 We do not impose a fixed communication count ken accounting. We therefore use token usage, 358
309 or total-token budget. Each method runs under rather than model-call count, as the primary ob- 359
310 its assigned communication protocol until it pro- served cost metric. Property 1 is supported when 360
311 duces the task-level final answer, and token usage COTIE achieves higher or comparable task perfor- 361
312 is logged after execution as an observed protocol mance under lower observed token cost than the 362
313 cost. For MultiAgentBench, we write MAB for the reference baseline; Property 2 is supported when it 363
314 benchmark-provided protocol with its output-level also obtains a higher score per 100K tokens. The 364
315 coordination stage; MAB-COTIE uses the same formal cost-quality definitions and scope of these 365
316 benchmark setting but replaces that output-level co- properties are given in Appendix C.1, and the full 366
317 ordination opportunity with intermediate CoT-state MultiAgentBench cost calculations are reported in 367
318 communication. Additional implementation, de- Appendix D. 368
319 coding, context-management, and logging details
320 are provided in Appendix E. 3.4 Main Results Across Benchmarks 369
Table 1 reports the main output-level communica- 370
321 3.2 Compared Methods tion comparison, while Table 2 isolates communica- 371
322 We compare against output-level two-agent com- tion timing. Both tables place score and token cost 372
323 munication baselines. On MATH, HumanEval, and in adjacent columns for each benchmark, making 373
5

## Page 6

374 the cost-quality comparison visible without adding shows that the first peer response becomes part of 426
375 extra rows. Full cost calculations are provided in the caller’s intermediate reasoning context for the 427
376 Appendix D. next request, and that the final proposal develops 428
377 On the general reasoning benchmarks, COTIE a peer-generated research direction before finaliza- 429
378 achieves the best task performance across MATH, tion. This distinguishes COTIE from final-stage 430
379 HumanEval, and HotpotQA. Compared with critique or post-hoc answer aggregation. 431
380 Output-level MP, COTIE improves MATH accu- The broad comparison does not by itself clarify 432
381 racy from 86.8 to 96.0, HumanEval Pass@1 from whether the gain comes from sharing reasoning 433
382 90.7 to 95.6, and HotpotQA score from 59.3 to content or from making that content available be- 434
383 65.4, while also using fewer tokens on all three fore finalization. We therefore compare COTIE 435
384 benchmarks. COTIE also outperforms the strength- with a late reasoning-content control, Late CoT 436
385 ened output-level variants: compared with Output- Message Passing, which shares completed CoT 437
386 level MP+SR, the strongest output-level variant on summaries only after local reasoning is finished. 438
387 MATH and HumanEval, COTIE improves MATH
388 from 90.3 to 96.0 and HumanEval from 94.7 to
389 95.6 while using fewer tokens; on HotpotQA, it 3.5 Communication Timing Ablation 439
390 improves over all output-level variants by at least
Table 2 compares late reasoning-content exchange 440
391 6.1 points. Because token usage is measured af-
with CoT-state exchange. Output-level MP ex- 441
392 ter execution rather than fixed in advance, these
changes final answers or short rationales after local 442
393 results suggest that the observed gains are not ob-
CoT completion. Late CoT MP keeps the same late 443
394 tained simply by increasing token consumption.
timing but shares a summarized completed-CoT 444
395 Instead, COTIE achieves higher task performance
trace. COTIE instead sends a compact CoT-state 445
396 with lower observed token cost in these settings.
request during the caller’s ongoing reasoning pro- 446
397 On MultiAgentBench, MAB-COTIE improves
cess and integrates the peer response before final- 447
398 over MAB in all three cooperative scenarios: Cod-
ization. The attachment-point criteria are stated in 448
399 ing rises from 48.2 to 63.5, Research from 84.4
Definition 4; logging details are provided in Ap- 449
400 to 89.3, and Database from 69.8 to 82.0. It also
pendix H. 450
401 improves the three-scenario average score from
402 67.5 to 78.3 while reducing average token usage The critical comparison is Late CoT MP versus 451
403 from 129,270 to 67,157. These results support both COTIE: both expose reasoning content to another 452
404 cost-quality properties on cooperative MultiAgent- agent, but only COTIE attaches the exchange to 453
405 Bench: COTIE obtains higher task quality with an ongoing reasoning state. On the general reason- 454
406 fewer observed tokens and a higher score per 100K ing benchmarks, COTIE improves over Late CoT 455
407 tokens than MAB, MAB+SC, and MAB+SR. Ap- MP on MATH (91.8 to 96.0), HumanEval (94.3 456
408 pendix D reports the full aggregate and domain- to 95.6), and HotpotQA (60.3 to 65.4), while also 457
409 level cost breakdown: COTIE reaches 116.5 score using fewer tokens on all three tasks. The same 458
410 points per 100K tokens, compared with 52.2 for score pattern holds on MultiAgentBench: COTIE 459
411 MAB, 41.1 for MAB+SC, and 27.5 for MAB+SR, improves Coding from 56.7 to 63.5, Research from 460
412 while reducing average token usage by 48.0% rela- 87.1 to 89.3, and Database from 78.6 to 82.0. To- 461
413 tive to MAB. ken usage is lower in all three MultiAgentBench 462
414 A representative logged MAB-Research trace scenarios and lower on average across the three 463
415 illustrates this mechanism. At step 4, the caller scenarios. This comparison suggests that the ad- 464
416 requests a literature-review subtask from agent3 vantage is not explained only by exposing agents 465
417 and integrates the returned gaps into its interme- to more reasoning text. Making peer information 466
418 diate research state. At step 5, the caller explic- available before the caller finalizes its reasoning 467
419 itly conditions a new request to agent2 on that ac- appears to be an important part of the observed 468
420 cepted review, asks for research ideas, partially gain. 469
421 integrates two complete directions, rejects an in- Appendix H.6 describes the logged diagnostics 470
422 complete third idea, and later develops the robust used to inspect this mechanism, and Appendix B 471
423 explainable-planning direction in the final proposal. gives a concrete trace in which an intermediate peer 472
424 Appendix B gives the full request, response, inte- response is reused in a subsequent request and then 473
425 gration record, and final-use evidence. The trace developed into the final answer. 474
6

## Page 7

A. General reasoning benchmarks (containing 2 agents)
Method MATH HumanEval HotpotQA
Acc. Tok. Pass@1 Tok. Score Tok.
Output-level two-agent communication baselines
Output-level MP 86.8 ± 2.5 3,407 90.7 ± 0.7 1,254 59.3 ± 2.1 2,936
Output-level MP+SC 84.1 ± 4.0 5,244 92.5 ± 0.4 1,967 58.3 ± 3.1 4,512
Output-level MP+SR 90.3 ± 1.7 5,429 94.7 ± 0.9 2,021 58.0 ± 2.6 4,638
Proposed CoT-state communication
COTIE 96.0 ± 1.3 3,271 95.6 ± 1.2 1,189 65.4 ± 2.4 2,803
B. MultiAgentBench cooperative scenarios (containing 3 to 22 agents)
Method Coding Research Database
Score Tok. Score Tok. Score Tok.
Benchmark output-level protocol
MAB 48.2 ± 1.1 241,296 84.4 ± 1.7 101,574 69.8 ± 2.1 44,939
MAB+SC 53.9 ± 1.2 291,786 85.7 ± 1.2 148,621 71.3 ± 2.7 72,658
MAB+SR 51.6 ± 0.8 401,574 87.7 ± 0.9 179,541 69.5 ± 1.9 177,656
CoT-state communication
MAB-COTIE 63.5 ± 1.6 115,249 89.3 ± 1.5 70,407 82.0 ± 1.9 15,814
Table 1: Main benchmark comparison with DeepSeek-V3.2. Score and total-token columns are shown side by side
for each benchmark. Panel A compares two-agent output-level message-passing baselines with COTIE on general
reasoning benchmarks. Output-level MP+SC and Output-level MP+SR strengthen the local reasoning of each agent
before the same output-level exchange. Panel B uses MAB for the benchmark-provided MultiAgentBench protocol
with its output-level coordination stage; MAB+SC and MAB+SR add local Self-Consistency or Self-Refine before
that coordination stage. The communication attachment-point comparison is reported in Table 2.
A. General reasoning benchmarks
Method MATH HumanEval HotpotQA
Acc. Tok. Pass@1 Tok. Score Tok.
Output-level MP 86.8 ± 2.5 3,407 90.7 ± 0.7 1,254 59.3 ± 2.1 2,936
Late CoT Message Passing 91.8 ± 1.9 3,302 94.3 ± 0.6 1,297 60.3 ± 1.6 3,027
COTIE 96.0 ± 1.3 3,271 95.6 ± 1.2 1,189 65.4 ± 2.4 2,803
B. MultiAgentBench cooperative scenarios
Method MAB-Coding MAB-Research MAB-Database
Score Tok. Score Tok. Score Tok.
MAB 48.2 ± 1.1 241,296 84.4 ± 1.7 101,574 69.8 ± 2.1 44,939
MAB LATE COT MP 56.7 ± 2.7 137,857 87.1 ± 2.1 110,714 78.6 ± 0.8 68,054
MAB-COTIE 63.5 ± 1.6 115,249 89.3 ± 1.5 70,407 82.0 ± 1.9 15,814
Table 2: Score and total-token columns are shown side by side for each benchmark. Output-level Message Passing
and Late CoT Message Passing attach peer information after local CoT completion, whereas COTIE attaches peer
information to an ongoing CoT state and integrates the response before finalization. The protocols use broadly
comparable cross-agent communication opportunities; the key difference is the attachment point of peer information.
Token usage is logged after execution as an observed protocol cost. In Panel B, MAB is the benchmark-provided
coordination baseline, MAB Late CoT MP is the late-CoT control, and MAB-COTIE is the CoT-state instantiation
on MultiAgentBench.
475 3.6 Mechanism and Cost-Quality Analysis 67,157, a 48.0% reduction. This supports quality- 482
improving token reduction rather than merely qual- 483
476 The MultiAgentBench results support two distinct ity preservation. 484
477 cost-quality properties. First, MAB-COTIE im-
478 proves final task quality while reducing observed Second, MAB-COTIE improves token utiliza- 485
479 token usage. Compared with MAB, it raises the tion efficiency. It reaches 116.5 aggregate score 486
480 three-scenario average score from 67.5 to 78.3 points per 100K tokens, compared with 52.2 for 487
481 and reduces average token usage from 129,270 to MAB, 41.1 for MAB+SC, and 27.5 for MAB+SR. 488
7

## Page 8

Stage Logged evidence from a MAB-Research
run
Request 1 Agent1 sends an INJECT request to Agent3
for a literature review before finalization.
Integration 1 Agent1 records the response as integrated
and updates its intermediate state with ac-
cepted research gaps.
Request 2 Agent1 asks Agent2 for research ideas ex-
plicitly based on Agent3’s returned review.
Integration 2 Agent1 partially integrates two complete
ideas and rejects one incomplete idea.
Final use The final proposal develops the accepted
robust explainable-planning direction.
Figure 3: Agent-count scaling of observed token
cost on MultiAgentBench. We compare MAB and
Table 3: Minimal trace evidence for pre-final CoT-state
MAB-COTIE on MultiAgentBench tasks with different
integration. The table reports only the mechanism-
numbers of agents. The observed token gap generally
critical chain; the complete request, response, integra-
widens as the coordination scale increases: in the 22-
tion record, and final-use evidence are provided in Ap-
agent setting, MAB-COTIE uses 624,580 tokens, while
pendix B.
MAB uses 2,664,728 tokens. This trend is consistent
with the communication-replacement view of COTIE:
task-relevant information is exchanged and integrated
4 Conclusion
through intermediate CoT states rather than through 514
bulky late-stage exchanges of completed local ratio-
nales. Because task identity, topology, and agent count We introduced COTIE, a CoT-state communica- 515
are not fully disentangled, this figure should be inter-
tion approach for multi-agent Chain-of-Thought 516
preted as an observed scaling trend.
reasoning. Rather than exchanging information 517
only after agents have produced completed outputs, 518
COTIE attaches compact peer requests to inter- 519
489 Thus, the gain is not obtained by consuming more mediate CoT states and integrates peer responses 520
490 inference tokens; in the cooperative MultiAgent- before finalization. The contribution is a communi- 521
491 Bench setting, COTIE obtains more final task per- cation attachment-point principle and its step-level 522
492 formance from each unit of observed token cost. instantiation, rather than a new routing mechanism 523
493 We do not attribute this effect to fewer model or workflow optimizer. 524
494 invocations. In the evaluated settings, output-level Across MATH, HumanEval, HotpotQA, and co- 525
495 communication and COTIE use broadly compara- operative MultiAgentBench, replacing output-level 526
496 ble cross-agent communication opportunities. The communication with CoT-state communication im- 527
497 relevant cost difference is that the two protocols proves final task performance under matched back- 528
498 attach peer information at different points in the rea- bone, task inputs, agent roles, and final integra- 529
499 soning trajectory, which changes how much down- tion settings. The Late CoT Message Passing 530
500 stream reasoning and final-stage coordination con- control further indicates that the gains are not ex- 531
501 tent is generated before the final answer. plained only by sharing more reasoning text, but 532
by making peer information available before the 533
502 The timing ablation further suggests that the im-
caller finalizes its CoT. On cooperative MultiAgent- 534
503 provement is not explained only by exposing agents
Bench, COTIE raises the three-scenario average 535
504 to more reasoning text. Late CoT Message Passing
score from 67.5 to 78.3 while reducing observed 536
505 also shares completed reasoning summaries, but it
average token usage from 129,270 to 67,157, a 537
506 does so after local reasoning is finished. COTIE
48.0% reduction. It also improves aggregate token 538
507 improves over this late reasoning-content control
utilization to 116.5 score points per 100K tokens, 539
508 across all reported task-quality metrics, indicating
compared with 52.2 for MAB, 41.1 for MAB+SC, 540
509 that making peer information available before final-
and 27.5 for MAB+SR. These results show that 541
510 ization is an important part of the observed gain.
communication timing and attachment point are 542
511 Figure 3 further shows the observed token-cost substantive design choices for improving both rea- 543
512 trend across MultiAgentBench tasks with different soning quality and observed token efficiency in 544
513 numbers of agents. cooperative multi-agent LLM systems. 545
8

## Page 9

546 5 Limitations Harri Edwards, Yuri Burda, Nicholas Joseph, Greg 595
Brockman, Alex Ray, Raul Puri, Gretchen Krueger, 596
547 This work focuses on cooperative multi-agent rea- Michael Petrov, Heidy Khlaaf, Girish Sastry, Pamela 597
548 soning settings, where agents share information or Mishkin, Brooke Chan, Scott Gray, and 39 others. 598
549 complete subtasks toward a joint solution. This 2021. Evaluating large language models trained on 599
code. arXiv preprint arXiv:2107.03374. 600
550 setting matches the main motivation of COTIE:
551 making peer assistance available while a caller is Weize Chen, Yusheng Su, Jingwei Zuo, Cheng Yang, 601
552 still reasoning. Other interaction patterns, such as Chenfei Yuan, Chen Qian, Chi-Min Chan, Yujia Qin, 602
Yaxi Lu, Ruobing Xie, Zhiyuan Liu, Maosong Sun, 603
553 adversarial debate, competitive negotiation, or pref-
and Jie Zhou. 2024b. AgentVerse: Facilitating multi- 604
554 erence aggregation among conflicting agents, may agent collaboration and exploring emergent behav- 605
555 require different communication strategies. Extend- iors. In The Twelfth International Conference on 606
556 ing CoT-state communication to these settings is Learning Representations. 607
557 an interesting direction for future work. DeepSeek-AI. 2025. DeepSeek-V3.2: Pushing the 608
558 Finally, the current study evaluates COTIE pri- frontier of open large language models. Preprint, 609
559 marily at the protocol level: whether moving com- arXiv:2512.02556. 610
560 munication from completed outputs to intermediate Yilun Du, Shuang Li, Antonio Torralba, Joshua B. 611
561 CoT states improves task quality and observed to- Tenenbaum, and Igor Mordatch. 2024. Improving 612
562 ken utilization. The logged traces provide evidence factuality and reasoning in language models through 613
563 that peer responses can be integrated before final- multiagent debate. In Proceedings of the 41st Inter- 614
national Conference on Machine Learning, volume 615
564 ization, but future work can further analyze which 235 of Proceedings of Machine Learning Research, 616
565 request types, integration patterns, and task struc- pages 11733–11763. PMLR. 617
566 tures contribute most to the observed gains.
Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul 618
Ethical Considerations Arora, Steven Basart, Eric Tang, Dawn Song, and 619
567
Jacob Steinhardt. 2021. Measuring mathematical 620
568 COTIE aims to make multi-agent LLM reasoning problem solving with the MATH dataset. In Thirty- 621
fifth Conference on Neural Information Processing 622
569 more efficient and more coordinated. Like other Systems Datasets and Benchmarks Track. 623
570 methods that strengthen collaborative LLM reason-
571 ing, it may support socially beneficial applications, Sirui Hong, Mingchen Zhuge, Jonathan Chen, Xiawu 624
Zheng, Yuheng Cheng, Ceyao Zhang, Jinlin Wang, 625
572 such as scientific synthesis, software-engineering Zili Wang, Steven Ka Shing Yau, Zijuan Lin, Liyang 626
573 productivity, and accessible education, but it may Zhou, Chenyu Ran, Lingfeng Xiao, Chenglin Wu, 627
574 also increase the scalability of harmful uses, such and Jürgen Schmidhuber. 2024. MetaGPT: Meta pro- 628
575 as automated disinformation generation or phish- gramming for a multi-agent collaborative framework. 629
In The Twelfth International Conference on Learning 630
576 ing workflows. We therefore view transparency and Representations. 631
577 auditability as necessary requirements for respon-
578 sible deployment. The logging schema described Md. Ashraful Islam, Mohammed Eunus Ali, and 632
Md Rizwan Parvez. 2024. MapCoder: Multi-agent 633
579 in Appendix H.6 is intended to support auditability
code generation for competitive problem solving. In 634
580 by recording the caller, target agent, request con- Proceedings of the 62nd Annual Meeting of the As- 635
581 tent, response content, integration status, and token sociation for Computational Linguistics (Volume 1: 636
582 usage when available. Such logs can help down- Long Papers), pages 4912–4944, Bangkok, Thailand. 637
Association for Computational Linguistics. 638
583 stream inspection and debugging of cross-agent
584 interactions in production assistant settings. Guohao Li, Hasan Abed Al Kader Hammoud, Hani 639
Itani, Dmitrii Khizbullin, and Bernard Ghanem. 2023. 640
CAMEL: Communicative agents for “mind” explo- 641
References ration of large language model society. In Ad- 642
585
vances in Neural Information Processing Systems, 643
586 Justin Chen, Swarnadeep Saha, and Mohit Bansal. volume 36, pages 51991–52008. 644
587 2024a. ReConcile: Round-table conference im-
588 proves reasoning via consensus among diverse LLMs. Tian Liang, Zhiwei He, Wenxiang Jiao, Xing Wang, 645
589 In Proceedings of the 62nd Annual Meeting of the Yan Wang, Rui Wang, Yujiu Yang, Shuming Shi, and 646
590 Association for Computational Linguistics (Volume 1: Zhaopeng Tu. 2024. Encouraging divergent thinking 647
591 Long Papers), pages 7066–7085, Bangkok, Thailand. in large language models through multi-agent debate. 648
592 Association for Computational Linguistics. In Proceedings of the 2024 Conference on Empiri- 649
cal Methods in Natural Language Processing, pages 650
593 Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, 17889–17904, Miami, Florida, USA. Association for 651
594 Henrique Ponde de Oliveira Pinto, Jared Kaplan, Computational Linguistics. 652
9

## Page 10

653 Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler for diverse, explainable multi-hop question answer- 709
654 Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, ing. In Proceedings of the 2018 Conference on Em- 710
655 Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, pirical Methods in Natural Language Processing, 711
656 Shashank Gupta, Bodhisattwa Prasad Majumder, pages 2369–2380, Brussels, Belgium. Association 712
657 Katherine Hermann, Sean Welleck, Amir Yazdan- for Computational Linguistics. 713
658 bakhsh, and Peter Clark. 2023. Self-refine: Itera-
659 tive refinement with self-feedback. In Advances in Shunyu Yao, Dian Yu, Jeffrey Zhao, Izhak Shafran, 714
660 Neural Information Processing Systems, volume 36, Thomas L. Griffiths, Yuan Cao, and Karthik 715
661 pages 46534–46594. Narasimhan. 2023. Tree of thoughts: Deliberate 716
problem solving with large language models. In Ad- 717
662 Md Mahadi Hasan Nahid and Davood Rafiei. vances in Neural Information Processing Systems, 718
663 2025. PRISM: Agentic retrieval with LLMs for volume 36, pages 11809–11822. 719
664 multi-hop question answering. arXiv preprint
665 arXiv:2510.14278. Zhangyue Yin, Qiushi Sun, Cheng Chang, Qipeng 720
Guo, Junqi Dai, Xuanjing Huang, and Xipeng Qiu. 721
666 Archiki Prasad, Alexander Koller, Mareike Hartmann, 2023. Exchange-of-thought: Enhancing large lan- 722
667 Peter Clark, Ashish Sabharwal, Mohit Bansal, and guage model capabilities through cross-model com- 723
668 Tushar Khot. 2024. ADaPT: As-needed decompo- munication. In Proceedings of the 2023 Conference 724
669 sition and planning with language models. In Find- on Empirical Methods in Natural Language Process- 725
670 ings of the Association for Computational Linguis- ing, pages 15135–15153. Association for Computa- 726
671 tics: NAACL 2024, pages 4226–4252, Mexico City, tional Linguistics. 727
672 Mexico. Association for Computational Linguistics.
Guibin Zhang, Yanwei Yue, Xiangguo Sun, Guancheng 728
Wan, Miao Yu, Junfeng Fang, Kun Wang, Tianlong 729
673 Chen Qian, Wei Liu, Hongzhang Liu, Nuo Chen, Yufan
Chen, and Dawei Cheng. 2025a. G-designer: Ar- 730
674 Dang, Jiahao Li, Cheng Yang, Weize Chen, Yusheng
chitecting multi-agent communication topologies via 731
675 Su, Xin Cong, Juyuan Xu, Dahai Li, Zhiyuan Liu, graph neural networks. In Proceedings of the 42nd 732
676 and Maosong Sun. 2024. ChatDev: Communicative International Conference on Machine Learning, vol- 733
677 agents for software development. In Proceedings ume 267 of Proceedings of Machine Learning Re- 734
678 of the 62nd Annual Meeting of the Association for search, Vancouver, Canada. PMLR. 735
679 Computational Linguistics (Volume 1: Long Papers),
680 pages 15174–15186, Bangkok, Thailand. Association Jiayi Zhang, Jinyu Xiang, Zhaoyang Yu, Fengwei Teng, 736
681 for Computational Linguistics. Xiong-Hui Chen, Jiaqi Chen, Mingchen Zhuge, Xin 737
Cheng, Sirui Hong, Jinlin Wang, Bingnan Zheng, 738
682 Noah Shinn, Federico Cassano, Ashwin Gopinath, Bang Liu, Yuyu Luo, and Chenglin Wu. 2025b. 739
683 Karthik Narasimhan, and Shunyu Yao. 2023. Re- AFlow: Automating agentic workflow generation. In 740
684 flexion: Language agents with verbal reinforcement The Thirteenth International Conference on Learning 741
685 learning. In Advances in Neural Information Pro- Representations. 742
686 cessing Systems, volume 36, pages 8634–8652.
Kunlun Zhu, Hongyi Du, Zhaochen Hong, Xiaocheng 743
687 Xuezhi Wang, Jason Wei, Dale Schuurmans, Quoc V. Yang, Shuyi Guo, Zhe Wang, Zhenhailong Wang, 744
688 Le, Ed H. Chi, Sharan Narang, Aakanksha Chowd- Cheng Qian, Xiangru Tang, Heng Ji, and Jiaxuan You. 745
689 hery, and Denny Zhou. 2023. Self-consistency im- 2025. MultiAgentBench: Evaluating the collabora- 746
690 proves chain of thought reasoning in language mod- tion and competition of LLM agents. In Proceedings 747
691 els. In The Eleventh International Conference on of the 63rd Annual Meeting of the Association for 748
692 Learning Representations. Computational Linguistics (Volume 1: Long Papers), 749
pages 8580–8622, Vienna, Austria. Association for 750
693 Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Computational Linguistics. 751
694 Bosma, Brian Ichter, Fei Xia, Ed H. Chi, Quoc V. Le,
695 and Denny Zhou. 2022. Chain-of-thought prompt-
696 ing elicits reasoning in large language models. In
697 Advances in Neural Information Processing Systems,
698 volume 35, pages 24824–24837.
699 Qingyun Wu, Gagan Bansal, Jieyu Zhang, Yiran Wu,
700 Beibin Li, Erkang Zhu, Li Jiang, Xiaoyun Zhang,
701 Shaokun Zhang, Jiale Liu, Ahmed Hassan Awadallah,
702 Ryen W. White, Doug Burger, and Chi Wang. 2023.
703 AutoGen: Enabling next-gen LLM applications via
704 multi-agent conversation framework. arXiv preprint
705 arXiv:2308.08155.
706 Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Ben-
707 gio, William W. Cohen, Ruslan Salakhutdinov, and
708 Christopher D. Manning. 2018. HotpotQA: A dataset
10

## Page 11

752 A Related Work Debate and output-level communication. 803
Multi-Agent Debate and related debate-style meth- 804
753 CoT reasoning and local refinement. Chain-of-
ods let agents produce answers and then exchange 805
754 Thought (CoT) prompting improves LLM reason-
arguments, critiques, or votes before selecting a 806
755 ing by eliciting intermediate reasoning steps before
final answer (Du et al., 2024; Liang et al., 2024). 807
756 the final answer (Wei et al., 2022). A large body
Other reconciliation methods similarly focus 808
757 of work improves this paradigm by sampling, re-
on combining or correcting completed outputs 809
758 vising, or structuring a model’s own reasoning pro-
(Chen et al., 2024a). These methods are strong 810
759 cess. Self-Consistency samples multiple indepen-
multi-agent reasoning baselines because they allow 811
760 dent CoT traces and aggregates their final answers
agents to challenge each other’s conclusions and 812
761 (Wang et al., 2023). Self-Refine revises a com-
expose weaknesses in completed answers. 813
762 pleted output using feedback (Madaan et al., 2023),
However, debate and reconciliation differ from 814
763 while reflection-style methods ask a model to cri-
COTIE in both timing and communication objec- 815
764 tique and improve its previous behavior (Shinn
tive. Their main interaction usually occurs after 816
765 et al., 2023). Tree-structured reasoning methods
agents have produced candidate answers or substan- 817
766 explore multiple possible reasoning paths before
tial reasoning traces. COTIE is cooperative and 818
767 selecting an answer (Yao et al., 2023).
step-level: a caller asks for help on a current CoT 819
768 These methods are important reasoning-
state, and the returned peer response is integrated 820
769 enhancement baselines, but they mainly operate
before the final answer is produced. For this reason, 821
770 within a single agent or on completed outputs.
we compare against output-level message passing 822
771 In our experiments, CoT, Self-Consistency, and
and debate-style baselines, while using Late CoT 823
772 Self-Refine are therefore treated as local reasoning
Message Passing as a controlled comparison that 824
773 enhancers inside output-level multi-agent baselines.
exposes reasoning content only after local reason- 825
774 By themselves, they do not test the communication
ing is complete. 826
775 attachment point studied in this paper: whether
776 peer information should enter after local CoT During-reasoning communication and work- 827
777 completion or during intermediate CoT generation. flow orchestration. The closest prior direction is 828
Exchange-of-Thought, which studies cross-model 829
778 Multi-agent LLM collaboration. Multi-agent
communication during CoT-like problem solv- 830
779 LLM systems distribute tasks across role-
ing (Yin et al., 2023). This makes it an impor- 831
780 specialized agents and coordinate their outputs
tant conceptual predecessor. Our focus is narrower: 832
781 through communication, decomposition, voting,
we isolate the communication attachment point at 833
782 debate, or aggregation. Representative systems in-
which peer information enters the caller’s reasoning 834
783 clude AutoGen (Wu et al., 2023), MetaGPT (Hong
process. This lets us separate the effect of sharing 835
784 et al., 2024), ChatDev (Qian et al., 2024),
reasoning content from the effect of making that 836
785 CAMEL (Li et al., 2023), and AgentVerse (Chen
content available before finalization. 837
786 et al., 2024b). Task-specific multi-agent systems
A separate line of work studies how to construct, 838
787 further apply these ideas to domains such as code
select, or optimize agent workflows. Systems such 839
788 generation and retrieval-augmented multi-hop ques-
as ADaPT (Prasad et al., 2024), AFlow (Zhang 840
789 tion answering (Islam et al., 2024; Nahid and
et al., 2025b), and G-Designer (Zhang et al., 2025a) 841
790 Rafiei, 2025). These works show that multiple
search over workflow structures, agent organiza- 842
791 agents can improve task solving by assigning roles,
tions, or adaptive routing strategies. Our work is 843
792 exchanging messages, and combining intermediate
complementary: rather than searching for the best 844
793 products.
overall workflow, we hold the main multi-agent 845
794 Most such systems communicate through mes-
setting fixed and study a specific design variable in- 846
795 sages, drafts, critiques, or final answers after agents
side it—whether cross-agent information exchange 847
796 have produced substantial outputs. COTIE stud-
happens after completed outputs or during interme- 848
797 ies a more specific design choice inside multi-
diate CoT generation. 849
798 agent reasoning: where peer information enters
799 the caller’s CoT process. Instead of waiting for
800 completed outputs, COTIE introduces peer input
801 at an intermediate CoT state and allows the caller
802 to integrate it before finalization.
11

## Page 12

B Trace Evidence: MAB-Research content. At this recorded step, the caller does 888
850
HARMONIC Workflow not ask for a final answer. Instead, it injects a 889
851
literature-review subtask into a peer agent: 890
852 This section presents a trace-level case study from
Exchange 1: caller request
853 the Research scenario of MultiAgentBench. We se-
“Conduct a comprehensive literature review on cognitive
854 lect a run in which the agents are asked to develop architectures for robotics, hybrid control systems, and ex-
855 a research proposal related to the HARMONIC plainable AI in robotics. Focus on understanding the cur-
856 framework for embodied robots. The final COTIE rent state of research in cognitive architectures for human–
robot collaboration, hybrid control systems, explainability
857 output proposes a robust strategic-layer planning and trust in robotic systems, integration of LLMs/VLMs
858 module for the HARMONIC architecture that main- in robotic architectures, and the HARMONIC framework
859 tains causal explainability under adversarial condi- mentioned in the Introduction and similar approaches.” 891
860 tions and distribution shifts. The omitted part of the request specifies that 892
861 This appendix reports a logged HARMONIC HARMONIC extends hybrid control systems and 893
862 workflow from the MAB-Research scenario. DIARC-style architectures through independent 894
863 Rather than compressing the case into a schematic, strategic and tactical layers. The caller asks the 895
864 we provide the corresponding logged metadata, re- peer to identify research gaps and clarify what 896
865 quest content, peer responses, integration records, makes HARMONIC novel. Thus, the request 897
866 and how the returned information is used before the constructs a literature-grounded intermediate state 898
867 final proposal is produced. The reported fields cor- rather than asking the peer to produce the final 899
868 respond to the logging step in Algorithm 1, line 13. proposal. 900
Trace summary The peer response supplies the requested liter- 901
Main caller: agent1. Exchange 1: agent1 → ature context. It summarizes prior work on cog- 902
agent3, request_option=INJECT, literature nitive architectures, normative behavior, collabo- 903
review on cognitive architectures, hybrid control ration systems, hybrid control, explainability, and 904
systems, explainable robotics, and HARMONIC-
related gaps. Exchange 2: agent1 → agent2, HARMONIC-style dual-layer architectures: 905
request_option=INJECT, research-idea brain- Exchange 1: peer response
storming conditioned on the literature review returned by
agent3. Logged integration evidence: both exchanges “The literature reveals several approaches to cognitive
contain structured integration records, including accepted architectures for human–robot collaboration, including
points, rejected points, conflicts, an updated caller-state memory-centred cognitive architectures, normative archi-
summary, and an integration reason. Observed use: tectures, essential-skills frameworks, and integrated collab-
the final proposal develops the accepted direction of oration systems. HARMONIC extends traditional hybrid
robust, causally explainable strategic-layer planning control systems by making strategic and tactical layers
for HARMONIC under adversarial conditions and function independently and interactively, while current
distribution shifts. LLM/VLM-based systems still face limitations in explain-
869 ability, trust establishment, normative behavior, capability
870 The purpose of this case study is to show how calibration, and human–robot information exchange.”
906
871 COTIE operates inside a research trajectory, rather
The new log records not only that the response 907
872 than only reporting the final answer. The run log
was integrated, but also which peer points were ac- 908
873 records exchanges at discrete scheduler steps rather
cepted into the caller’s intermediate state. This 909
874 than at token-level CoT positions. We therefore re-
makes the case study stronger than a manual 910
875 port the recorded step_id values verbatim and
content-level comparison. 911
876 interpret each exchange by its request content, peer
Exchange 1: logged integration record
877 response, logged integration decision, and subse-
878 quent use in the final proposal. Integration status: integrated.
Accepted points include: memory-centred cognitive ar-
879 Exchange 1: injecting a literature- chitectures for social interaction; normative architectures
for collaborative decision-making; essential-skills frame-
880 review subtask. The first relevant works for joint action; integrated collaboration systems
881 COTIE exchange has run_id=718a6798, for multi-human–robot teamwork; HARMONIC’s inde-
882
caller_id=agent1, target_id=agent3, pendent strategic and tactical layers; HARMONIC’s ex-
tension of DIARC-style architectures; limitations of gen-
883
step_id=4, request_option=INJECT,
eralist LLM/VLM modules for human-level explainabil-
884 and help_type=verify. In this log, ity; capability-calibration problems; pacing mismatches
885 help_type is an auxiliary implementa- in human–robot collaboration; and the need for explicit
human–robot information exchange.
886 tion tag; the exchange type is identified by Rejected points: none.
887 request_option and the actual request Conflicts: none.
912
12

## Page 13

Updated state summary: the caller updates its research Exchange 2: peer response
state with a literature-grounded view of cognitive archi-
“Idea 1: Adversarially Robust Explainable Planning for
tectures, hybrid control systems, explainability challenges,
HARMONIC Framework. How can we develop robust
and HARMONIC’s novel dual-layer contribution. The
strategic-layer planning modules that maintain explainabil-
updated state identifies robot explainability, trust establish-
ity under adversarial conditions and distribution shifts?
ment, normative behavior, LLM/VLM integration limita-
The approach combines LLM-based reasoning with adver-
tions, and strategic–tactical coordination as the main gaps
sarial training, a robustness-aware explanation generator,
for later idea generation.
and domain adaptation for novel situations while maintain-
913
ing causal explainability.”
914 This integration record shows that the first peer 950
915 response becomes part of the caller-side research The same peer response also proposes a second 951
916 state before the final proposal is written. In particu- complete idea on causal representation learning 952
917 lar, the caller does not merely receive a final-stage for cross-domain skill transfer. A third idea on 953
918 comment; it records a set of accepted literature adversarial-aware human–robot communication is 954
919 gaps that are available for subsequent reasoning. started but is incomplete in the returned response. 955
Unlike a final-stage aggregation protocol, 956
920 Exchange 2: using the peer review
COTIE records how the caller selectively integrates 957
921 to generate research ideas. The sec-
the peer response before finalization: 958
922 ond relevant COTIE exchange occurs
923 in the same run: run_id=718a6798, Exchange 2: logged integration record
924 caller_id=agent1, target_id=agent2, Integration status: partially_integrated.
Accepted points: the caller accepts Idea 1: Adversarially
925
step_id=5, request_option=INJECT,
Robust Explainable Planning for HARMONIC Framework,
926 and help_type=verify. This exchange is because it directly addresses explainability limitations un-
927 especially informative because the caller explicitly der adversarial conditions and distribution shifts. The
caller also accepts Idea 2: Causal Representation Learn-
928 conditions the new request on the literature review ing for Cross-Domain Skill Transfer, because it addresses
929 returned by agent3: skill acquisition and contextual understanding gaps.
Rejected points: the caller rejects Idea 3: Adversarial-
Exchange 2: caller request
Aware Human–Robot Communication Protocol because
“Based on the provided Introduction about the HAR- the peer response is cut off and incomplete.
MONIC framework and the comprehensive literature re- Conflicts: none.
view conducted by agent3, brainstorm potential research Updated state summary: the caller now has two com-
ideas that build upon or address gaps in the Introduction. plete research directions: robust explainable planning and
The Introduction discusses limitations of current robots causal representation learning for skill transfer. The third
including lack of cognitive abilities to assess semantics idea is marked as incomplete and would require a follow-
of situations, inability to engage in meaning-oriented dia- up completion step if it were to be used.
959
log, struggles with disturbances and novel situations, and
inability to generate causal explanations.” This integration record is important because it 960
930 shows selective pre-final use of peer information. 961
931 The omitted part of the request lists seven gaps The caller does not blindly copy the peer response. 962
932 identified in the literature review: limited explain- Instead, it accepts two complete research directions, 963
933 ability of LLMs/VLMs in robotics, normative be- rejects the incomplete third direction, records no 964
934 havior challenges, pacing mismatch in human– conflicts, and updates its state before producing the 965
935 robot collaboration, capability calibration prob- final answer. 966
936 lems, contextual-understanding limitations, infor-
937 mation exchange complexity, and skill-acquisition Integration into the final proposal. The final 967
938 difficulties in shared workspaces. output develops the accepted robust-planning di- 968
939 This request shows a concrete information flow rection from Exchange 2 into the central research 969
940 across agents. The caller does not issue an inde- proposal: 970
941 pendent second request from scratch; it conditions Final proposal
942 the second request on the literature review returned
“How can we develop a robust strategic layer planning mod-
943 by agent3. In other words, the output of the first ule for the HARMONIC framework that maintains causal
944 COTIE exchange becomes part of the caller’s inter- explainability under adversarial conditions and distribution
shifts while ensuring safe human–robot collaboration?”
945 mediate reasoning context for the next exchange. 971
946 The second peer then proposes research ideas The final proposal further specifies four technical 972
947 using its robust-AI and safe-machine-learning ex- components: a hybrid planning architecture com- 973
948 pertise. The most important accepted direction is bining LLM-based reasoning with formal symbolic 974
949 the first idea: planning, adversarial training with explanation- 975
13

## Page 14

976 preserving regularization, a robustness-aware ex- intermediate peer assistance can make the caller’s 1027
977 planation generator, and a domain-adaptation mod- research trajectory more focused before the final 1028
978 ule that maps novel situations to known causal pat- answer is written. In this trace, the caller first com- 1029
979 terns. This final research plan directly extends the presses a literature review into an accepted gap 1030
980 accepted robust-planning idea from the second peer summary, then uses that summary to request tar- 1031
981 response, while using the literature-grounded gaps geted idea generation, and finally develops one 1032
982 introduced by the first peer response. accepted direction into the final proposal. This 1033
shows how CoT-state exchange can reduce unfo- 1034
983 Effect on the reasoning trajectory. This trace
cused downstream reasoning and final-stage recon- 1035
984 provides stronger evidence of pre-final integration
ciliation in research-type multi-agent tasks. 1036
985 than a content-only case study because the inte-
986 gration decisions are explicitly logged. The first C Cost-Quality Analysis and Scope
1037
987 exchange, agent1 → agent3 at step_id=4,
988 injects a literature-review subtask and returns a The main method section defines the operational 1038
989 structured account of cognitive architectures, hy- attachment-point criteria for CoT-state communi- 1039
990 brid strategic–tactical control, explainability gaps, cation in Definition 4. We use this appendix only 1040
991 LLM/VLM limitations, and HARMONIC’s dual- to specify the cost-quality metrics and the scope of 1041
992 layer contribution. The integration record explicitly the empirical claim, avoiding a second definition 1042
993 lists accepted points and updates the caller’s state of the communication protocol. 1043
994 summary with these gaps. C.1 Token Cost and Reasoning Efficiency 1044
995 The second exchange, agent1 → agent2 at
996 step_id=5, is then explicitly conditioned on the Because COTIE introduces cross-agent communi- 1045
997 literature review from agent3. The caller asks cation during CoT, its benefit should not be eval- 1046
998 for research ideas that address the identified gaps uated only by final task performance. A useful 1047
999 using robust-AI and safe-machine-learning exper- method should also avoid unnecessary reasoning 1048
1000 tise. The integration record shows selective use: cost. We therefore evaluate COTIE using two em- 1049
1001 the caller partially integrates the response, accepts pirical cost-quality properties. In this paper, the 1050
1002 the robust explainable planning idea and the causal token-efficiency analysis focuses on the three co- 1051
1003 representation learning idea, rejects an incomplete operative MultiAgentBench scenarios, where all 1052
1004 communication-protocol idea, records no conflicts, compared methods use the same benchmark-level 1053
1005 and updates its state to focus on the two complete multi-agent setting and token accounting is directly 1054
1006 directions. comparable. 1055
1007 The key point is not that another agent comments Property 1: quality-improving token reduction. 1056
1008 on a completed answer. Rather, peer information COTIE should reduce observed token usage while 1057
1009 is introduced before the final proposal is formed reaching higher or comparable final task quality 1058
1010 and is recorded as part of the caller’s intermediate than the corresponding output-level communica- 1059
1011 state. The logged trajectory shows the following tion baseline. Token savings are meaningful only 1060
1012 pre-final chain: literature review → accepted gap when they do not come at the expense of task perfor- 1061
1013 summary → gap-conditioned idea generation → mance; in the strongest case, the method improves 1062
1014 selective integration → final proposal. This illus- task quality while reducing observed token cost. 1063
1015 trates the mechanism that COTIE is designed to Property 2: higher token utilization efficiency. 1064
1016 expose: cross-agent information is attached to an A stronger property is that COTIE obtains more 1065
1017 ongoing reasoning process and used before finaliza- task performance per unit of token cost. In this 1066
1018 tion, instead of being appended only as final-stage case, the method is not merely lower-cost; it uses 1067
1019 feedback. its inference cost more effectively. 1068
1020 Relation to the aggregate result. This example For each method m, we measure total token cost 1069
1021 is consistent with the aggregate Research result re- as 1070
1022 ported in the main experiments. In the cooperative T m = T m prompt + T m completion. 1071
1023 MultiAgentBench Research scenario, COTIE ob- When communication tokens can be separated from 1072
1024 tains a higher score than the MAB baseline while ordinary reasoning tokens, we also report them sep- 1073
1025 using fewer observed tokens. The case study gives arately. We focus on token usage as the primary 1074
1026 a qualitative illustration of how this can happen: cost measure because the compared protocols are 1075
14

## Page 15

1076 designed to replace, rather than stack on top of, redundant local trajectory. When the agent pool is 1125
1077 the corresponding output-level coordination oppor- small, this overhead is limited. When the number 1126
1078 tunity. Consequently, COTIE has approximately of agents increases, however, the system may accu- 1127
1079 comparable model-call overhead to the correspond- mulate many local histories and then spend addi- 1128
1080 ing output-level baseline in our implementation. tional tokens reconciling, summarizing, or revising 1129
1081 We therefore treat score per 100K tokens as a token- them only after local CoT traces have already been 1130
1082 utilization metric, while leaving a full latency and completed. 1131
1083 serving-cost analysis to future work. COTIE changes this cost structure. A useful 1132
1084 To measure whether COTIE improves efficiency, peer response can be integrated before the caller 1133
1085 we compare both performance and token cost continues, potentially avoiding downstream reason- 1134
1086 against final-output-level communication baselines. ing from a flawed, incomplete, or redundant state. 1135
1087 For a baseline b, we report token reduction as This does not imply that every individual exchange 1136
T m repairs an error. Rather, it suggests that earlier 1137
1088 TokenReduction(m, b) = 1 − .
T b CoT-state exchange can reduce the amount of un- 1138
1089 A positive value means that method m uses fewer necessary reasoning that accumulates before final 1139
1090 tokens than baseline b. coordination. 1140
1091 To measure token utilization efficiency, we also This hypothesis is supported by the agent-count 1141
1092 report score per 100K tokens: scaling analysis reported in Appendix E.3. Across 1142
S m MultiAgentBench tasks with agent counts rang- 1143
1093 ScorePer100K(m) = ,
T m /100K ing from 3 to 22, the observed token gap between 1144
1094 where S m is the task score of method m and T m is CoT and COTIE widens as the number of agents 1145
1095 its average token cost per task. Higher values indi- increases. In the 22-agent setting, COTIE uses 1146
1096 cate that the method obtains more task performance slightly over 600K tokens, while CoT exceeds 1147
1097 from the same token cost. 2.6M tokens. This trend helps explain why token 1148
1098 These metrics are central to our setting. If savings are modest in two-agent general bench- 1149
1099 COTIE improves task performance but uses sub- marks but substantial in larger cooperative multi- 1150
1100 stantially more tokens, the gain may come from a agent settings. 1151
1101 higher inference cost. If COTIE improves task per- The scaling analysis should be interpreted as a 1152
1102 formance while using fewer observed tokens, the trend rather than a strict causal ablation, because 1153
1103 result is consistent with the efficiency hypothesis: task identity, topology, and agent count are not 1154
1104 communicating earlier during CoT can reduce un- fully disentangled. A stricter future experiment 1155
1105 necessary downstream reasoning and may prevent could vary the number of agents while holding the 1156
1106 incomplete intermediate states from expanding into task fixed. Nevertheless, the observed trend is con- 1157
1107 longer traces. sistent with the proposed efficiency mechanism: 1158
1108 This effect is expected to become more visible CoT-state communication is most useful when co- 1159
1109 as the number of agents grows. In small two-agent ordination cost itself grows with the size of the 1160
1110 settings, the amount of cross-agent context and agent pool. 1161
1111 final-stage coordination is limited. In larger multi-
C.3 Scope of the Analysis 1162
1112 agent settings, however, final-stage coordination
1113 can accumulate many local histories, repeated ra- This analysis supports an empirical claim about the 1163
1114 tionales, and overlapping reasoning traces. Under evaluated protocols, not a universal theorem. We 1164
1115 such conditions, CoT-state exchange can reduce do not claim that communication during CoT is 1165
1116 cost by making useful peer information available always better than final-output-level communica- 1166
1117 before each caller continues expanding its local tion. Final-output-level interaction remains useful 1167
1118 trajectory. for answer selection, critique, debate, and aggre- 1168
gation after agents have completed their own CoT 1169
1119 C.2 Why Token Savings Can Grow with processes. 1170
1120 Agent Count The claim tested in this paper is narrower: under 1171
1121 The efficiency hypothesis follows from the com- the same task inputs, backbone model, agent roles, 1172
1122 munication attachment point. In final-output-level and final integration rule, COTIE tests whether 1173
1123 communication, each agent may continue reason- communication during the CoT process can out- 1174
1124 ing from an early mistake, incomplete state, or perform communication after CoT traces are com- 1175
15

## Page 16

1176 pleted. Our token-efficiency claim is strongest Method MATH HumanEval HotpotQA
1177 on cooperative MultiAgentBench, where the com- Acc. Pass@1 Score
1178 pared methods share the same benchmark-level MAD 86.0 ± 3.0 90.0 ± 1.5 60.3 ± 3.2
1179 multi-agent setting and token accounting is directly MAD+SC 92.0 ± 3.0 72.0 ± 4.3 57.7 ± 4.7
MAD+SR 85.0 ± 3.0 77.8 ± 2.0 61.0 ± 4.4
1180 comparable.
1181 A stricter question remains open: whether COTIE 96.0 ± 1.3 95.6 ± 1.2 65.4 ± 2.4
1182 COTIE still outperforms final-output-level commu- Table 6: Additional competitive multi-agent baselines
1183 nication under exactly matched total-token usage. on general reasoning benchmarks. SC denotes Self-
1184 Our current results show that COTIE can achieve Consistency and SR denotes Self-Refine. These re-
sults are reported as score-only comparisons because the
1185 better performance while reducing observed token
MAD-family baselines were not logged under the same
1186 cost in the evaluated cooperative MultiAgentBench
token-accounting format used in the main cost-quality
1187 settings. The agent-count scaling analysis further analysis.
1188 suggests that this observed cost reduction becomes
1189 stronger as the number of agents increases, but with MAB+SC, COTIE uses 60.7% fewer tokens 1215
1190 it should not be interpreted as a fully controlled and improves the average score by 8.0 points. Com- 1216
1191 causal ablation of agent count. pared with MAB+SR, COTIE uses 73.4% fewer to- 1217
kens and improves the average score by 8.7 points. 1218
1192 D Additional Results and Token-Cost These results support Property 1 on cooperative 1219
1193 Tables MultiAgentBench: COTIE reduces observed token 1220
usage without sacrificing final quality. They also 1221
1194 D.1 Token Cost
support Property 2 in the same setting. In terms 1222
1195 This appendix expands the token-cost metrics in- of score per 100K tokens, COTIE achieves 116.5, 1223
1196 troduced in Section 3.3 and reports the full Multi- compared with 52.2 for MAB, 41.1 for MAB+SC, 1224
1197 AgentBench cost calculations. We report observed and 27.5 for MAB+SR. Thus, COTIE obtains more 1225
1198 token cost to test whether COTIE improves per- task performance from each unit of token usage. 1226
1199 formance by simply consuming more tokens, or
1200 whether earlier communication can also reduce Scenario MAB COTIE Reduction
1201 unnecessary reasoning under the evaluated proto- Coding 241,296 115,249 52.2%
Research 101,574 70,407 30.7%
1202 cols. Table 4 reports aggregate token utilization
Database 44,939 15,814 64.8%
1203 efficiency on the cooperative MultiAgentBench Aggregate 129,270 67,157 48.0%
1204 scenarios, measured as aggregate score per 100K
Table 5: Domain-level token reduction on MultiAgent-
1205 tokens. Bench relative to MAB. COTIE reduces average token
Method Score Tokens Score/100K usage in all three cooperative scenarios, with the largest
reduction on Database.
MAB 67.5 129,270 52.2
MAB+SC 70.3 171,022 41.1
MAB+SR 69.6 252,924 27.5 D.3 Additional Competitive Multi-Agent 1227
COTIE 78.3 67,157 116.5
Baselines 1228
Table 4: Aggregate token utilization efficiency on the co-
Table 6 reports additional competitive multi-agent 1229
operative MultiAgentBench scenarios. Score and tokens
are averaged over the Coding, Research, and Database baselines on the three general reasoning bench- 1230
scenarios. Score/100K denotes average score per 100K marks. These baselines are included as score- 1231
tokens. only comparisons because their token usage was 1232
not logged under the same directly comparable 1233
1206 D.2 MultiAgentBench Token Efficiency accounting format used for the main cost-quality 1234
analysis. Therefore, they are not used for the token- 1235
1207 The token-efficiency gain is especially relevant on
efficiency claims in Section 3; those claims focus 1236
1208 MultiAgentBench, where the benchmark already
on cooperative MultiAgentBench, where the com- 1237
1209 includes communication among agents. We there-
pared protocols share directly comparable token 1238
1210 fore analyze cost-quality trade-offs on the three
accounting. 1239
1211 cooperative MultiAgentBench scenarios.
1212 Compared with MAB, COTIE reduces average
1213 tokens per task by 48.0% while improving the three-
1214 scenario average score by 10.8 points. Compared
16

## Page 17

1240 E Additional Experimental Details level coordination opportunity with intermediate 1290
CoT-state communication. We evaluate the Re- 1291
1241 E.1 Reproducibility and Sampling Protocol
search, Coding, and Database scenarios because 1292
1242 To support reproducibility, we fix the random seeds they are cooperative multi-agent tasks. We exclude 1293
1243 used for benchmark subsampling and repeated runs. adversarial scenarios from the main evaluation be- 1294
1244 All reported experiments are averaged over three cause they would mix CoT-state assistance with 1295
1245 random seeds: 21, 42, and 63. For each of MATH, debate-style interaction. 1296
1246 HumanEval, and HotpotQA, we use each seed to
1247 randomly select 150 evaluation examples from the E.2 Experimental Instantiation Details 1297
1248 corresponding benchmark split. For the three co- This appendix provides additional details on how 1298
1249 operative MultiAgentBench scenarios, Coding, Re- the abstract COTIE protocol is instantiated in 1299
1250 search, and Database, we use the same seeding the reported experiments. In all settings, COTIE 1300
1251 procedure and randomly select 70 examples from changes the timing and attachment point of cross- 1301
1252 each scenario for each seed. agent communication rather than the underlying 1302
1253 All methods compared within a benchmark use task, backbone model, or final evaluation rule. 1303
1254 the same sampled examples under the same seed. For the general reasoning benchmarks, including 1304
1255 Thus, for a given seed and benchmark, COTIE and MATH, HumanEval, and HotpotQA, we instantiate 1305
1256 the corresponding baselines are evaluated on iden- a two-agent setting. The baseline communication 1306
1257 tical task instances. This keeps the comparison methods exchange information only after an agent 1307
1258 focused on the communication protocol rather than has produced a complete local output, whereas 1308
1259 differences in the evaluated example set. The back- COTIE allows a caller agent to send a structured 1309
1260 bone model, decoding settings, agent roles, final CoT-state request during intermediate reasoning. 1310
1261 integration rule, and context-management strategy This keeps the comparison focused on whether in- 1311
1262 are kept fixed across methods as described in Ap- termediate CoT-state communication provides an 1312
1263 pendix E. advantage over final-output message passing. 1313
For MultiAgentBench, we preserve the 1314
1264 Backbone and decoding. All reported experi-
benchmark-provided task structure and agent topol- 1315
1265 ments use DeepSeek-V3.2 as the fixed backbone
ogy. COTIE does not introduce new task-specific 1316
1266 model. Unless otherwise stated, all compared meth-
agents or change the benchmark roles. Instead, it 1317
1267 ods use greedy decoding with temperature 0.0, a
changes how an agent can request and integrate 1318
1268 maximum generation length of 8192 tokens for lo-
peer information during the reasoning trajectory. 1319
1269 cal reasoning, and the same stopping criteria across
This design keeps the comparison aligned with the 1320
1270 methods. Each reported number is averaged over
original MultiAgentBench setting while allowing 1321
1271 three runs with seeds 21, 42, and 63. These values
us to test whether pre-final CoT-state exchange 1322
1272 are fixed across the two-agent output-level base-
improves the cost–quality trade-off. 1323
1273 lines and the CoT-state communication methods.
Token usage is not imposed as a hard constraint 1324
1274 Benchmarks. For MATH, HumanEval, and Hot- during execution. We log token usage after each 1325
1275 potQA, all reported baselines are two-agent com- run and report it as an observed protocol cost. This 1326
1276 munication methods with the same role pair and is why the main experiments compare both task per- 1327
1277 final integration prompt. Output-level MP ex- formance and token utilization rather than treating 1328
1278 changes completed local answers or short ra- cost as a fixed input constraint. 1329
1279 tionales; Output-level MP+SC and Output-level
Unrestricted communication execution. In the 1330
1280 MP+SR strengthen each agent’s local reasoning be-
reported experiments, communication-based meth- 1331
1281 fore the same output-level exchange. Late CoT
ods are not assigned a manually fixed number of 1332
1282 Message Passing is used as the late reasoning-
communication rounds or a fixed total-token bud- 1333
1283 content control in the timing ablation. For MultiA-
get. Each method is executed under its correspond- 1334
1284 gentBench, MAB denotes the benchmark-provided
ing communication protocol until it produces the 1335
1285 protocol with its task roles, interaction topology,
task-level final answer. Output-level methods ex- 1336
1286 and output-level coordination stage. MAB+SC
change information after local reasoning has pro- 1337
1287 and MAB+SR strengthen local agent reasoning
duced completed outputs or rationales, whereas 1338
1288 before that coordination stage. MAB-COTIE uses
COTIE allows peer requests to be issued during an 1339
1289 the same benchmark setting but replaces the output-
17

## Page 18

1340 ongoing CoT state. We log prompt tokens, comple- This analysis compares CoT and COTIE across 1389
1341 tion tokens, communication-related tokens when MultiAgentBench tasks whose agent counts range 1390
1342 available, and total tokens after execution. Thus, from 3 to 22. 1391
1343 the reported token cost is an empirical outcome of Figure 3 reports the observed total-token cost 1392
1344 the method rather than a pre-specified budget. as a function of the number of agents. The trend 1393
shows that the token gap between CoT and COTIE 1394
1345 History summarization. During development,
becomes larger as the number of agents increases. 1395
1346 we observed that passing the accumulated reason-
In the 22-agent setting, COTIE uses slightly over 1396
1347 ing history verbatim can cause the context to grow
600K tokens, while CoT exceeds 2.6M tokens. 1397
1348 quickly across reasoning steps and cross-agent ex-
This suggests that COTIE becomes increasingly 1398
1349 changes. To keep context handling comparable,
token-efficient when the coordination scale grows. 1399
1350 the reported CoT and COTIE runs use the same
This pattern helps explain the difference between 1400
1351 history-summarization strategy: accumulated rea-
the general reasoning benchmarks and MultiAgent- 1401
1352 soning history is summarized before being reused
Bench. The general benchmarks use two-agent 1402
1353 as context. This prevents the comparison from giv-
settings, where the amount of cross-agent context 1403
1354 ing COTIE a special compression advantage and
and final-stage coordination is limited. In contrast, 1404
1355 makes token usage an observed result under aligned
larger MultiAgentBench tasks create more local 1405
1356 context-management conditions.
histories, more repeated reasoning, and more final- 1406
1357 Cost logging. We report token usage as the pri- stage coordination cost. CoT-state communication 1407
1358 mary cost metric because prompt and completion can reduce this accumulated cost by allowing peer 1408
1359 tokens are consistently logged across all compared information to enter before each caller expands its 1409
1360 methods. For each run, we log prompt tokens, com- reasoning trajectory. 1410
1361 pletion tokens, communication tokens when appli- This analysis should be interpreted as a scaling 1411
1362 cable, and total tokens. We do not use model-call trend rather than a strict causal ablation. Agent 1412
1363 overhead as the primary cost metric because the count, task identity, and benchmark topology are 1413
1364 output-level communication baselines and CoTIE not fully disentangled in the available MultiAgent- 1414
1365 use broadly comparable cross-agent communica- Bench tasks. Nevertheless, the observed widening 1415
1366 tion opportunities in the evaluated settings. The of the token gap is consistent with the hypothesis 1416
1367 main cost difference therefore comes from the that the efficiency advantage of COTIE is most vis- 1417
1368 amount of reasoning and communication content ible when multi-agent coordination itself becomes 1418
1369 generated under each protocol, which is directly costly. 1419
1370 captured by prompt, completion, communication,
F Method Taxonomy and Baseline Details
1371 and total token counts. 1420
1372 Agent-count scaling analysis. For the agent- This appendix summarizes the method families 1421
1373 count scaling analysis in Appendix E.3, we com- used in the main experiments, the attachment-point 1422
1374 pare CoT and COTIE on MultiAgentBench tasks comparison, the MultiAgentBench evaluation, and 1423
1375 with agent counts ranging from 3 to 22. The num- the agent-count token-scaling analysis. The goal 1424
1376 ber of agents is determined by the benchmark task of this taxonomy is to make clear which compari- 1425
1377 configuration. We do not manually vary the number son each method supports. In particular, not every 1426
1378 of agents for the same task; therefore, this analysis method is used for the same purpose: some meth- 1427
1379 should be interpreted as an observed scaling trend ods are output-level baselines for the main results, 1428
1380 across available tasks rather than a strict causal ab- some are late-reasoning-content controls for the 1429
1381 lation. For each task, we record the observed total attachment-point comparison, and some are used 1430
1382 token usage of CoT and COTIE and plot token cost only for the agent-count scaling analysis. 1431
1383 against the number of agents. Table 7 separates four groups: 1432
1. general two-agent output-level communication 1433
1384 E.3 Agent-Count Scaling of Token Cost baselines; 1434
1385 The main MultiAgentBench cost tables aggregate 2. attachment-point comparison methods; 1435
1386 over the Coding, Research, and Database scenarios. 3. MultiAgentBench output-level and CoT-state 1436
1387 We further analyze whether the observed token- protocols; 1437
1388 saving effect changes with the number of agents. 4. the CoT baseline used for the agent-count token- 1438
18

## Page 19

1439 scaling analysis. pre-specified token budget. As reported in Ap- 1490
1440 Output-level Message Passing is the standard pendix E.3, the observed token gap widens as the 1491
1441 two-agent final-output communication baseline. number of agents increases; in the 22-agent setting, 1492
1442 Output-level MP+SC and Output-level MP+SR COTIE uses slightly over 600K tokens, while CoT 1493
1443 keep the same late communication stage but exceeds 2.6M tokens. 1494
1444 strengthen each agent’s local reasoning before
G Prompt Templates
1495
1445 that exchange. Late CoT Message Passing is
1446 not intended as a broad new baseline; it is a late This appendix reports the prompt templates used 1496
1447 reasoning-content control. It shares CoT-like rea- for COTIE and the compared output-level base- 1497
1448 soning information after local CoT completion, lines. The templates define the reasoning-agent 1498
1449 whereas COTIE shares a compact CoT-state re- interface, task-specific roles, peer-request actions, 1499
1450 quest during the caller’s ongoing reasoning pro- pre-final integration records, and result-level ex- 1500
1451 cess. This comparison tests whether the advantage change prompts used by the baselines. 1501
1452 comes from the attachment point of peer informa-
1453 tion rather than merely from exposing agents to G.1 CoTIE Peer-Request Interface 1502
1454 more reasoning text. CoTIE gives a reasoning agent two peer-request 1503
1455 For MultiAgentBench, MAB denotes the actions. The first action, CONSULT, asks a peer 1504
1456 benchmark-provided protocol with its output-level for targeted help on a specific uncertainty in the 1505
1457 coordination stage. MAB LATE COT MP de- caller’s current reasoning state. The second action, 1506
1458 notes the corresponding late-CoT control in the INJECT, asks a peer to solve a separable subtask 1507
1459 same benchmark setting. MAB-COTIE denotes and return a sub-result that the caller can use in its 1508
1460 the same benchmark setting with intermediate CoT- ongoing reasoning. In both cases, the request is 1509
1461 state communication. The agent-count scaling issued before the caller produces its final answer, 1510
1462 analysis additionally uses a MAB-COT baseline: and the returned response is evaluated before final- 1511
1463 agents solve the corresponding benchmark task ization. 1512
1464 with local CoT-like reasoning and the same history- In the implementation, CONSULT is exposed 1513
1465 summarization strategy, but without intermediate as request_consult. INJECT is exposed as 1514
1466 CoT-state exchange. This baseline is used only to request_delegate, because the returned sub- 1515
1467 study how observed token cost scales as the number result is injected into the caller’s ongoing reasoning 1516
1468 of agents grows from 3 to 22. state. 1517
1469 Interpretation of the taxonomy. The taxonomy CONSULT request. 1518
1470 distinguishes three different experimental ques-
Name: request_consult 1519
1471 tions. First, the main benchmark comparison asks
Description: Ask another agent for targeted help 1520
1472 whether replacing final-output-level communica-
during your reasoning. Use this when you are un- 1521
1473 tion with CoT-state communication improves task certain about a specific claim, calculation, knowl- 1522
1474 performance and observed token efficiency. Sec- edge point, evidence item, interpretation, or im- 1523
plementation detail before you produce your final 1524
1475 ond, the attachment-point comparison asks whether answer. Describe your question and the kind of 1525
1476 the gain persists when the late baseline is allowed to help needed. 1526
1477 share completed CoT-like reasoning content. Third, Arguments: 1527
1478 the agent-count scaling analysis asks whether the • question: Your specific question. Include 1528
1479 observed token-cost gap between CoT and COTIE enough context so the peer can answer without 1529
seeing your full reasoning trace. 1530
1480 becomes larger as the number of agents increases. • help_type: The type of help you need. 1531
1481 The MAB-COT row is included only for the One of: verify, compute, retrieve, 1532
1482 third question. It should not be confused with clarify, debug, or critique. 1533
• preferred_expertise: Optional. The 1534
1483 MAB, which is the benchmark-provided output- kind of expertise that would be most helpful, 1535
1484 level coordination protocol used in the main Mul- such as calculation_verification, 1536
1485 tiAgentBench comparison. In the scaling analy- code_review, database_analysis, 1537
literature_review, or 1538
1486 sis, MAB-COT and MAB-COTIE are compared evidence_checking. 1539
1487 under the same task-specific agent configuration • context: Optional. Additional context about 1540
1488 and history-summarization strategy. The key mea- your reasoning so far that will help the peer 1541
understand the question. 1542
1489 sured quantity is observed total-token cost, not a
19

## Page 20

Method Agents Communication timing Reasoning / message format Role in evaluation
General two-agent output-level baselines
Output-level MP 2 After both agents complete Each agent first produces a completed local Standard two-agent output-level
local CoT reasoning trace and final answer. The agents then communication baseline; also serves as
exchange final answers, short rationales, critiques, the final-output control in the
or concerns. attachment-point comparison.
Output-level MP+SC 2 After SC-enhanced local CoT Each agent applies local Self-Consistency before Stronger output-level baseline; tests
the same output-level exchange. The whether local sampling explains the gain.
communication stage remains final-output-level.
Output-level MP+SR 2 After SR-enhanced local CoT Each agent applies local Self-Refine before the Stronger output-level baseline; tests
same output-level exchange. The communication whether local self-revision explains the
stage remains final-output-level. gain.
Attachment-point comparison methods
Late CoT Message 2 After both agents complete The peer message contains a summarized Late reasoning-content control. It tests
Passing local CoT completed-CoT trace, the final answer, and whether sharing CoT reasoning content
optional uncertainty or concern. The message is after completion explains the gain, or
constructed only after local reasoning is complete. whether pre-final CoT-state attachment
matters.
COTIE 2 During the caller’s ongoing The caller sends a compact CoT-state request Proposed two-agent CoT-state
CoT process derived from its current reasoning state, receives a communication method; tests pre-final
targeted peer response or sub-result, and integrates attachment of peer information.
it before finalization.
MultiAgentBench output-level and CoT-state protocols
MAB Benchmark Benchmark output-level The benchmark-provided multi-agent protocol with Main MultiAgentBench output-level
agents coordination its task-specific roles, interaction topology, history baseline; also used as the output-level
summarization, and output-level coordination stage. reference in the agent-count
In the scaling logs, MAB-COT denotes this same token-scaling analysis.
output-level protocol rather than a separate
baseline.
MAB LATE COT MP Benchmark After local CoT completion Benchmark-specific late-CoT control: agents share MultiAgentBench late reasoning-content
agents summarized completed-CoT content after local control for the attachment-point
reasoning has finished. comparison.
MAB+SC Benchmark Benchmark output-level Local Self-Consistency is added before the Stronger MAB baseline; tests whether
agents coordination after local SC benchmark-provided output-level coordination local sampling improves the benchmark
stage. protocol.
MAB+SR Benchmark Benchmark output-level Local Self-Refine is added before the Stronger MAB baseline; tests whether
agents coordination after local SR benchmark-provided output-level coordination local self-revision improves the
stage. benchmark protocol.
MAB-COTIE Benchmark During CoT The benchmark setting is preserved, but the COTIE instantiated in the
agents output-level coordination opportunity is replaced MultiAgentBench cooperative setting;
by intermediate CoT-state communication. A caller compared against MAB in the main
sends a CoT-state request, receives a peer response cost-quality analysis and the agent-count
or sub-result, and integrates it before finalization. token-scaling analysis.
Table 7: Method taxonomy used in the experiments. The table separates output-level baselines, attachment-point
comparison methods, and MultiAgentBench-specific protocols. Output-level MP, Output-level MP+SC, Output-
level MP+SR, Late CoT Message Passing, and MAB communicate only after local reasoning is complete or
through the benchmark-provided output-level coordination stage. COTIE and MAB-COTIE attach communication
to an ongoing CoT state and integrate the peer response before finalization. MAB-COT, when it appears in
implementation logs for the agent-count scaling analysis, denotes the same output-level MAB protocol and is not
treated as a separate baseline.
20

## Page 21

1543 INJECT request. Before requesting peer improvements, check 1604
whether the main workspace file exists and has 1605
1544 Name: request_delegate
content. If the file is empty or missing, create 1606
1545 Description: Ask another agent to solve a separa- the initial content yourself first using the appro- 1607
1546 ble subtask during your reasoning. Use this when priate environment tool. Only after the file exists 1608
1547 you encounter a sub-problem that can be solved with real content should you request peer improve- 1609
1548 independently, has clear input/output boundaries, ments, reviews, or extensions. 1610
1549 and returns a sub-result that can be integrated into
1550 your ongoing reasoning before you produce the G.3 Pre-final Integration Record 1611
1551 final answer.
1552 Arguments: After receiving a peer response, the caller records 1612
1553 • subtask_description: Complete de- how the response affects its current reasoning state. 1613
1554 scription of the subtask. Include what needs This record is used for trace analysis and auditabil- 1614
1555 to be done and any constraints. ity. It documents whether and how the peer re- 1615
1556 • expected_output: What kind of output
1557 you expect back from the peer. Be specific sponse is integrated before finalization. 1616
1558 about format and content.
1559 • context: Relevant context the peer needs to You just received a response from another agent. 1617
1560 understand the subtask, such as background, Evaluate what you will integrate into your reason- 1618
1561 current progress, constraints, partial findings, ing. 1619
1562 or intermediate results. Peer response: 1620
1563 • preferred_expertise: Optional. The
1564 type of expertise that would be most helpful {peer_response} 1621
1565 for the subtask. Provide a structured assessment in JSON format: 1622
1566 G.2 CoTIE Agent Decision Rule
{ 1623
1567 Each CoTIE-enabled reasoning agent receives an "status": 1624
1568 instruction that makes the communication attach- "integrated|partially_integrated| 1625
rejected|deferred", 1626
1569 ment point explicit. At each step, the agent may "accepted_points": [ 1627
1570 continue reasoning locally, issue a CONSULT "point 1", 1628
1571 request, issue an INJECT request, use a task- "point 2" 1629
], 1630
1572 provided environment tool when available, or fi- "rejected_points": [ 1631
1573 nalize. "point 3" 1632
], 1633
1574 You are a collaborative reasoning agent. At each "conflicts": [ 1634
1575 step, choose the next action that best advances the "conflict 1" 1635
1576 task. ], 1636
1577 Decision rule: "updated_state_summary": 1637
"brief summary of your updated 1638
1578 1. If you are uncertain about a fact, claim, compu-
reasoning state", 1639
1579 tation, interpretation, evidence item, or imple-
"reason": 1640
1580 mentation detail, use request_consult.
"why you made these choices" 1641
1581 2. If you encounter a separable sub-problem
} 1642
1582 that can be solved independently and
1583 has clear input/output boundaries, use
1584 request_delegate. Return only the JSON object. 1643
1585 3. If the task requires environment data, file op-
1586 erations, code execution, database inspection, G.4 MultiAgentBench Instantiation 1644
1587 or other task-provided operations, use an avail-
1588 able environment tool. For MultiAgentBench experiments, we preserve 1645
1589 4. If you are fully confident and ready to answer, the benchmark-provided agents, roles, task setting, 1646
1590 produce the final answer in the required task
1591 format. tool environment, and default history summariza- 1647
1592 After receiving a peer result, evaluate it before tion mechanism. The history summarization mech- 1648
1593 continuing. If the response is incomplete, low anism is part of the benchmark execution setting 1649
1594 quality, only partially useful, or inconsistent with and is kept consistent across the corresponding 1650
1595 the task constraints, continue reasoning, request
1596 additional help if needed, or reject the unsup- MAB-based protocols. CoTIE changes the com- 1651
1597 ported part. Receiving a peer response does not munication attachment point: a caller may issue 1652
1598 mean the task is complete. a CONSULT or INJECT request from an ongo- 1653
1599 Do not guess when targeted peer assistance can ing reasoning state and integrate the peer response 1654
1600 resolve a specific uncertainty.
before producing the final answer. 1655
1601 For shared-workspace tasks, such as coding
1602 tasks in MultiAgentBench, the agent also receives
1603 a workspace-safety instruction:
21

## Page 22

1656 MultiAgentBench CoTIE agent instruction. Solver system prompt. 1716
1657 You are a collaborative reasoning agent working You are a MATH SOLVER specializing in step-by- 1717
1658 on a MultiAgentBench task. Use your assigned step reasoning. Your expertise covers algebra, ge- 1718
1659 role, available tools, and peer-request actions to ometry, calculus, number theory, combinatorics, 1719
1660 solve the task. and probability. 1720
1661 You may use request_consult when you Output format: Your final answer must be in- 1721
1662 need targeted help on a specific uncertainty, such side \boxed{...}. Example: \boxed{42} 1722
1663 as checking a claim, debugging code, retrieving a or \boxed{x = 5}. 1723
1664 missing fact, verifying an intermediate result, or
Workflow: 1724
1665 clarifying a task constraint.
1. Decompose the problem into sub-steps. 1725
1666 You may use request_delegate when you
2. Reason through each step carefully. 1726
1667 encounter a separable subtask that can be solved
3. If uncertain about a specific calculation or 1727
1668 independently and whose result can be integrated
claim, use request_consult to ask the 1728
1669 into your ongoing solution.
Verifier. 1729
1670 When you receive a peer response, evaluate it 4. If you identify a separable sub- 1730
1671 before using it. Accept useful points, reject in- problem outside your core strength, 1731
1672 complete or unsupported points, record conflicts use request_delegate. 1732
1673 when they exist, and update your reasoning state 5. When fully confident, produce the final answer 1733
1674 before producing the final answer. in \boxed{...} format. 1734
1675 When the task is complete, produce the final an- Decision rule: 1735
1676 swer required by the benchmark.
• Uncertain about a step? Use 1736
request_consult with help_type 1737
1677 Benchmark history summarization prompt. verify or compute. 1738
• Separable sub-problem? Use 1739
1678 You are an advanced summarizer agent designed request_delegate. 1740
1679 to condense and clarify the history of conversa- • Confident and done? Produce the final answer 1741
1680 tions between multiple agents. Your task is to with \boxed{...}. 1742
1681 analyze dialogues from various participants and
1682 generate a cohesive summary that captures the key Do not guess. Ask the Verifier when targeted 1743
1683 points, themes, and decisions made throughout verification is needed. 1744
1684 the interactions.
Verifier system prompt. 1745
1685 Your primary objectives are:
1686 1. Contextual Analysis: Carefully review the en- You are a MATH VERIFIER specializing in er- 1746
1687 tire conversation history to understand the con- ror detection. Your expertise covers calculation 1747
1688 text, including the roles of different agents and verification, logic checking, proof validation, and 1748
1689 the progression of discussions. edge case detection. 1749
1690 2. Identify Key Themes: Extract the main
Output format: When confirming or correcting, 1750
1691 themes, topics, and significant moments in the
state the correct result clearly. If producing a final 1751
1692 dialogue, noting any recurring issues or points
answer, use \boxed{...}. 1752
1693 of contention.
1694 3. Summarize Conversations: Create a clear and Workflow: 1753
1695 concise summary that outlines the conversa- 1. When consulted, check the specific step or 1754
1696 tion’s flow, important exchanges, decisions claim presented. 1755
1697 made, and any action items that emerged. En- 2. Verify calculations, logic, assumptions, and 1756
1698 sure that the summary reflects the contribu- boundary cases. 1757
1699 tions of each agent without losing the overall 3. If you find an error, explain what is wrong and 1758
1700 narrative. suggest the correction. 1759
1701 4. Highlight Outcomes: Emphasize any conclu- 4. If the reasoning is correct, confirm it clearly. 1760
1702 sions reached or actions agreed upon by the
1703 agents, providing a sense of closure to the sum- Be thorough. A missed error can propagate 1761
1704 marized conversation. through the entire solution. 1762
1705 When composing the summary, maintain clarity,
MATH agent profiles. 1763
1706 coherence, and logical organization. The goal is
1707 to provide a comprehensive yet succinct overview
Solver profile: Decomposes math problems, rea- 1764
1708 that enables the next reasoning step to understand
sons step by step, and proposes solutions. Ex- 1765
1709 the essential state of the multi-agent dialogue.
pertise tags include algebra, geometry, calculus, 1766
number theory, combinatorics, probability, step- 1767
1710 G.5 MATH Prompts wise reasoning, and problem decomposition. 1768
1711 For MATH, we use two role-specialized agents: a Verifier profile: Checks calculation accuracy, 1769
1712 Solver and a Verifier. The Solver is responsible finds logic errors, and suggests corrections. Ex- 1770
pertise tags include error detection, calculation 1771
1713 for step-by-step solution construction, while the verification, logic checking, algebra, geometry, 1772
1714 Verifier checks calculations, logical consistency, calculus, edge cases, and proof validation. 1773
1715 assumptions, and edge cases.
22

## Page 23

1774 G.6 HumanEval Prompts 2. Test mentally with sample inputs and edge 1831
cases. 1832
1775 For HumanEval, we use a Coder and a Reviewer. 3. Identify specific issues with clear explana- 1833
1776 The Coder writes the required Python solution, tions. 1834
1777 while the Reviewer checks correctness, edge cases, 4. Provide feedback that the Coder can use to fix 1835
the code. 1836
1778 and implementation quality.
Decision rule: 1837
1779 Coder system prompt. • Need more context? Use 1838
request_consult. 1839
1780 You are a PYTHON DEVELOPER. Write clean, • Code is correct? Confirm clearly. 1840
1781 correct, well-structured code. • Found a bug? Explain the exact issue and fix. 1841
1782 Output format: Return only the required Python Be specific. Point to the exact line or logic issue. 1842
1783 code content, indented by four spaces. Do not Avoid vague feedback. 1843
1784 include markdown fences, extra explanations, or
1785 text before or after the code. G.7 HotpotQA Prompts 1844
1786 Example for a task requiring the body
1787 of has_close_elements(numbers, For HotpotQA, we use a Retriever and a Synthe- 1845
1788 threshold): sizer. The Retriever identifies supporting facts from 1846
the provided context, while the Synthesizer checks 1847
1789 for i in range(len(numbers)): consistency and produces the final multi-hop an- 1848
1790 for j in range(i + 1,
1791 len(numbers)): swer. 1849
1792 if abs(numbers[i] -
1793 numbers[j]) < threshold: Retriever system prompt. 1850
1794 return True
1795 return False You are an INFORMATION RETRIEVER spe- 1851
cializing in multi-hop questions. 1852
1796 Workflow: Output format: Your final answer must be a 1853
JSON object: 1854
1797 1. Read the problem carefully. Understand in-
1798 puts, outputs, constraints, and edge cases.
1799 2. Design the algorithm and write the required {"answer": "<short answer string>", 1855
1800 code content. "sp": [["title", sent_id], ...]} 1856
1801 3. If uncertain about correctness or edge cases,
1802 use request_consult to ask the Re- Workflow: 1857
1803 viewer.
1. Decompose the question into sub-questions. 1858
1804 4. If you need a full code review, use
2. For each sub-question, identify the key facts 1859
1805 request_delegate.
needed. 1860
1806 5. When confident, output only the required code
3. Use the provided context to find supporting 1861
1807 content.
sentences. 1862
1808 Decision rule: 4. If uncertain about a fact, use 1863
1809 • Unsure about correctness? Use request_consult to ask the Syn- 1864
1810 request_consult with help_type thesizer. 1865
1811 verify or debug. 5. When all facts are gathered, produce the JSON 1866
1812 • Need a full review? Use with answer and supporting fact IDs. 1867
1813 request_delegate. Decision rule: 1868
1814 • Confident? Output the required code content
• Unsure about a fact? Use 1869
1815 directly.
request_consult with help_type 1870
1816 No markdown fences. No extra explanation. Re- verify or retrieve. 1871
1817 turn only the required code. • Need synthesis help? Use 1872
request_delegate. 1873
1818 Reviewer system prompt. • Facts gathered? Output JSON with answer and 1874
supporting facts. 1875
1819 You are a CODE REVIEWER specializing in cor- Do not fabricate facts. Only use evidence from 1876
1820 rectness and quality. the context. Label supporting sentences by index. 1877
1821 Output format: When reviewing code, be spe-
1822 cific. Point to the exact issue and suggest the Synthesizer system prompt. 1878
1823 fix. If producing the final code, output only the
1824 required code content. You are an ANSWER SYNTHESIZER specializ- 1879
1825 Workflow: ing in multi-hop QA. 1880
1826 1. First, cross-check the problem examples Output format: Your final answer must be a 1881
1827 against the code logic. If the problem JSON object: 1882
1828 says f(2, 8) => [2, 4, 6, 8], trace
1829 manually through the code and verify whether {"answer": "<short answer string>", 1883
1830 it actually produces that output. "sp": [["title", sent_id], ...]} 1884
23

## Page 24

1885 Workflow: Instructions: 1941
1886 1. Review the facts provided by the Retriever. 1. Check whether the completed outputs agree. 1942
1887 2. Check for consistency and contradictions 2. If they disagree, compare the supporting ratio- 1943
1888 across facts. nales. 1944
1889 3. Synthesize a clear, concise answer addressing 3. Prefer the answer that is better supported by 1945
1890 all parts of the question. the task evidence, computation, examples, or 1946
1891 4. If facts are missing or inconsistent, use constraints. 1947
1892 request_consult to ask the Retriever. 4. Produce only the final answer in the required 1948
1893 5. When the answer is complete, output the task format. 1949
1894 JSON.
1895 Decision rule: G.8.2 Output-Level Message Passing with 1950
1896 • Missing facts? Use request_consult with Self-Consistency 1951
1897 help_type retrieve or clarify. Local self-consistency prompt. 1952
1898 • Need more evidence? Use
1899 request_delegate. You are a role-specialized reasoning agent. Gen- 1953
1900 • Answer complete? Output JSON. erate multiple independent solutions to the same 1954
1901 Do not fabricate facts. If evidence is insufficient, task. Each solution should be produced indepen- 1955
1902 say so in the answer. Do not add markdown fences dently, without relying on the others. After gener- 1956
1903 or extra text around the JSON. ating the candidate solutions, compare their final 1957
answers and select the most consistent answer. 1958
1904 G.8 Output-Level Baseline Prompts Do not request peer help during candidate genera- 1959
tion. Complete the local self-consistency process 1960
1905 This section reports the prompts used for the output- first. Your selected answer will later be compared 1961
1906 level baselines. These baselines differ from CoTIE with another agent’s completed output. 1962
1907 in the communication attachment point: agents Return format: 1963
1908 first complete their local reasoning or local refine-
1909 ment, and only then exchange completed outputs, { 1964
"candidate_answers": ["...", "...", 1965
1910 rationales, critiques, or completed reasoning sum- "..."], 1966
1911 maries. "selected_answer": "...", 1967
"selection_reason": "...", 1968
1912 G.8.1 Output-Level Message Passing "confidence": "high|medium|low" 1969
} 1970
1913 Local answer prompt.
1914 You are a role-specialized reasoning agent. Solve Output-level exchange after self-consistency. 1971
1915 the task independently using your assigned role
1916 and expertise. Produce your local answer and a You are given completed self-consistency outputs 1972
1917 concise rationale supporting it. from multiple agents. Each agent has already 1973
generated candidate answers and selected its local 1974
1918 Do not request peer help during your reasoning.
final answer. 1975
1919 Complete your local reasoning first. Your out-
1920 put will later be compared with another agent’s Compare the selected answers and their selection 1976
1921 completed output. reasons. Identify agreements, disagreements, and 1977
possible errors. Produce the final task answer in 1978
1922 Return format:
the required benchmark format. 1979
1923 { Inputs: 1980
1924 "local_answer": "...", • Agent 1 self-consistency output: 1981
1925 "rationale": "...", {agent1_sc_output} 1982
1926 "confidence": "high|medium|low" • Agent 2 self-consistency output: 1983
1927 } {agent2_sc_output} 1984
Instructions: 1985
1928 Final output exchange prompt.
1. Compare the selected answers. 1986
1929 You are given completed outputs from multiple 2. Use candidate-answer consistency as support- 1987
1930 agents. Each output contains a local answer, a ing evidence, not as the only decision rule. 1988
1931 concise rationale, and a confidence estimate. 3. Resolve disagreements using task evidence, 1989
computations, examples, or constraints. 1990
1932 Compare the completed outputs. Identify agree- 4. Produce only the final answer in the required 1991
1933 ments, disagreements, and possible errors. Then task format. 1992
1934 produce the final task answer in the required
1935 benchmark format. G.8.3 Output-Level Message Passing with 1993
1936 Inputs: Self-Refine 1994
1937 • Agent 1 completed output:
Initial local answer prompt. 1995
1938 {agent1_output}
1939 • Agent 2 completed output:
1940 {agent2_output}
24

## Page 25

1996 You are a role-specialized reasoning agent. Pro- G.8.4 Late CoT Message Passing 2052
1997 duce an initial answer to the task using your as-
Late CoT Message Passing is the attachment-point 2053
1998 signed expertise. Include a concise rationale.
control used to distinguish CoTIE from the expla- 2054
1999 Return format:
nation that agents benefit only from seeing more 2055
2000 { reasoning text. In this baseline, agents share com- 2056
2001 "draft_answer": "...",
2002 "draft_rationale": "..." pleted reasoning summaries after local reasoning 2057
2003 } has finished. 2058
2004 Local feedback prompt. Completed reasoning summary prompt. 2059
You have completed your local reasoning for the 2060
2005 Review your own draft answer. Identify possi-
task. Summarize the reasoning that led to your 2061
2006 ble mistakes, missing evidence, incorrect calcula-
local answer. The summary should be concise 2062
2007 tions, edge cases, formatting problems, or unsup-
but include the main assumptions, intermediate 2063
2008 ported claims.
results, evidence, computations, and final local 2064
2009 Draft answer: {draft_answer} answer. 2065
2010 Draft rationale: {draft_rationale} Do not introduce new reasoning steps after the 2066
2011 Return format: local answer is completed. Summarize only the 2067
completed reasoning. 2068
2012 { Return format: 2069
2013 "feedback": ["issue 1", "issue 2"],
2014 "revision_plan": "..." { 2070
2015 } "completed_reasoning_summary": 2071
"...", 2072
2016 Local revision prompt. "local_answer": "...", 2073
"confidence": "high|medium|low" 2074
2017 Revise your draft answer using the feedback and } 2075
2018 revision plan.
2019 Draft answer: {draft_answer} Late reasoning-content exchange prompt. 2076
2020 Feedback: {feedback} You are given completed reasoning summaries 2077
from multiple agents. Each summary was pro- 2078
2021 Revision plan: {revision_plan}
duced after the agent completed its local reason- 2079
2022 Return your revised local answer and concise ra- ing. 2080
2023 tionale.
Compare the completed reasoning summaries. 2081
2024 Return format: Identify agreements, disagreements, missing as- 2082
sumptions, unsupported claims, or possible errors. 2083
2025 { Then produce the final task answer in the required 2084
2026 "revised_answer": "...", benchmark format. 2085
2027 "revised_rationale": "...", Inputs: 2086
2028 "confidence": "high|medium|low"
2029 } • Agent 1 completed reasoning summary: 2087
{agent1_completed_cot} 2088
• Agent 2 completed reasoning summary: 2089
2030 Output-level exchange after self-refine. {agent2_completed_cot} 2090
2031 You are given completed revised outputs from Instructions: 2091
2032 multiple agents. Each agent has already produced
1. Compare the final local answers. 2092
2033 an initial answer, reviewed it, and revised it lo-
2. Compare the reasoning summaries supporting 2093
2034 cally.
those answers. 2094
2035 Compare the revised answers and rationales. Iden- 3. Determine whether any completed reasoning 2095
2036 tify agreements, disagreements, and possible re- summary contains a likely error. 2096
2037 maining errors. Produce the final task answer in 4. Produce only the final answer in the required 2097
2038 the required benchmark format. task format. 2098
2039 Inputs: G.9 MultiAgentBench Output-Level Baseline 2099
2040 • Agent 1 revised output: Prompts 2100
2041 {agent1_sr_output}
2042 • Agent 2 revised output: For MultiAgentBench output-level baselines, 2101
2043 {agent2_sr_output}
agents complete their assigned local work under 2102
2044 Instructions:
the benchmark task setting and then exchange com- 2103
2045 1. Compare the revised answers.
pleted outputs or completed reasoning summaries. 2104
2046 2. Check whether either revision introduced a
2047 new inconsistency. The MAB-based baselines preserve the benchmark- 2105
2048 3. Resolve disagreements using task evidence, provided agents, roles, tool environment, task set- 2106
2049 computations, examples, or constraints.
2050 4. Produce only the final answer in the required ting, and default history summarization mecha- 2107
2051 task format. nism. 2108
25

## Page 26

2109 G.9.1 MAB Output-Level Protocol MAB output-level exchange after local self- 2161
2110 Local MAB agent prompt. consistency. 2162
You are given selected outputs from agents that 2163
2111 You are a role-specialized agent working on a
have each completed local self-consistency. Com- 2164
2112 MultiAgentBench task. Complete your assigned
pare the selected outputs, resolve disagreements, 2165
2113 part of the task using your role, available tools,
and produce the final task-level answer required 2166
2114 and task environment.
by the benchmark. 2167
2115 Produce your completed output, including the rel-
Inputs: 2168
2116 evant result, concise rationale, and any files, code,
2117 database results, research findings, or intermedi- • Selected outputs from participating agents: 2169
2118 ate artifacts required by the task. {selected_agent_outputs} 2170
2119 Return format: Instructions: 2171
1. Compare the selected outputs. 2172
2120 { 2. Use each agent’s selection reason as support- 2173
2121 "completed_output": "...", ing evidence. 2174
2122 "supporting_rationale": "...", 3. Resolve conflicts using task constraints, files, 2175
2123 "artifacts_or_results": "...", code behavior, database results, research evi- 2176
2124 "confidence": "high|medium|low" dence, or other benchmark-specific signals. 2177
2125 } 4. Produce the final answer in the required bench- 2178
mark format. 2179
2126 MAB output-level exchange prompt. G.9.3 MAB with Local Self-Refine 2180
2127 You are given completed outputs from the agents MAB local draft prompt. 2181
2128 participating in the task. Review the completed
2129 outputs, identify agreements and inconsistencies, You are a role-specialized agent working on a 2182
2130 and produce the final task-level answer required MultiAgentBench task. Produce an initial local 2183
2131 by the benchmark. output for your assigned part of the task. 2184
2132 Inputs: Return format: 2185
2133 • Completed outputs from participating agents:
{ 2186
2134 {completed_agent_outputs}
"draft_output": "...", 2187
2135 Instructions: "draft_rationale": "..." 2188
} 2189
2136 1. Check whether the completed outputs are mu-
2137 tually consistent.
2138 2. Identify missing pieces, unsupported claims, MAB local feedback prompt. 2190
2139 implementation errors, or conflicting conclu-
2140 sions. Review your own draft output. Identify possi- 2191
2141 3. Use the completed outputs to form the final ble errors, missing pieces, unsupported claims, 2192
2142 task-level answer. inefficient code, incorrect database assumptions, 2193
2143 4. Return the answer in the required benchmark weak research evidence, formatting problems, or 2194
2144 format. violations of task constraints. 2195
Draft output: {draft_output} 2196
2145 G.9.2 MAB with Local Self-Consistency Draft rationale: {draft_rationale} 2197
2146 MAB local self-consistency prompt. Return format: 2198
2147 You are a role-specialized agent working on a { 2199
2148 MultiAgentBench task. Generate multiple inde- "feedback": ["issue 1", "issue 2"], 2200
2149 pendent local attempts for your assigned part of "revision_plan": "..." 2201
2150 the task. Compare the attempts and select the } 2202
2151 most reliable local output before the output-level
2152 exchange.
MAB local revision prompt. 2203
2153 Return format:
Revise your draft output using the feedback and 2204
2154 { revision plan. 2205
2155 "candidate_outputs": ["...", "...", Draft output: {draft_output} 2206
2156 "..."],
2157 "selected_output": "...", Feedback: {feedback} 2207
2158 "selection_reason": "...", Revision plan: {revision_plan} 2208
2159 "confidence": "high|medium|low"
Return format: 2209
2160 }
{ 2210
"revised_output": "...", 2211
"revised_rationale": "...", 2212
"confidence": "high|medium|low" 2213
} 2214
26

## Page 27

2215 MAB output-level exchange after local self- H Protocol Details and Logging 2274
2216 refine.
This appendix provides additional details about the 2275
2217 You are given revised outputs from participating CoTIE exchange protocol, the distinction between 2276
2218 agents. Each agent has already drafted, reviewed,
2219 and revised its local output. Compare the revised CoTIE and output-level communication baselines, 2277
2220 outputs, resolve disagreements, and produce the and the logs used for trace analysis and repro- 2278
2221 final task-level answer required by the benchmark. ducibility. The purpose of this appendix is to make 2279
2222 Inputs: the evaluated communication attachment point ex- 2280
2223 • Revised outputs from participating agents: plicit. 2281
2224 {revised_agent_outputs}
2225 Instructions: H.1 CoTIE Exchange Structure 2282
2226 1. Compare the revised outputs. A CoTIE exchange is a peer-to-peer request issued 2283
2227 2. Check whether any revision introduced a new
2228 issue. by a caller agent while its reasoning is still ongoing. 2284
2229 3. Resolve conflicts using task constraints, files, The exchange is attached to an intermediate CoT 2285
2230 code behavior, database results, research evi- state rather than to a completed answer. The peer 2286
2231 dence, or other benchmark-specific signals.
2232 4. Produce the final answer in the required bench- response is then evaluated and integrated before 2287
2233 mark format. the caller produces its final answer. 2288
2234 G.9.4 MAB Late CoT Message Passing Each CoTIE exchange contains three conceptual 2289
components: 2290
2235 MAB completed reasoning summary prompt.
1. Caller state. The caller has an ongoing reason- 2291
2236 You have completed your local reasoning and ing state, including its current subgoal, partial 2292
2237 local task contribution. Summarize the reason-
reasoning, intermediate conclusion, uncertainty, 2293
2238 ing that led to your completed output. Include
2239 the main assumptions, intermediate findings, tool or separable subtask. 2294
2240 results, code changes, database conclusions, re- 2. Peer request. The caller sends a bounded re- 2295
2241 search evidence, and final local output.
quest to a peer. The request may ask for targeted 2296
2242 Do not introduce new reasoning steps after the
assistance or for a separable sub-result. 2297
2243 local output is completed. Summarize only the
2244 completed reasoning and completed work. 3. Pre-final integration. The caller evaluates the 2298
2245 Return format: peer response and updates its reasoning state 2299
before finalization. 2300
2246 { The defining property is the communication at- 2301
2247 "completed_reasoning_summary":
2248 "...", tachment point: the peer response can affect the 2302
2249 "completed_output": "...", caller’s subsequent reasoning, not only a final-stage 2303
2250 "artifacts_or_results": "...", vote, critique, or aggregation decision. 2304
2251 "confidence": "high|medium|low"
2252 }
H.2 Consultation Requests 2305
2253 MAB late reasoning-content exchange prompt. A CONSULT request is used when the caller wants 2306
targeted help on a specific uncertainty in its current 2307
2254 You are given completed reasoning summaries
2255 and completed outputs from the participating reasoning state. The peer is asked to verify, com- 2308
2256 agents. Compare the summaries and outputs. pute, retrieve, clarify, debug, or critique a localized 2309
2257 Identify agreements, disagreements, missing as-
part of the caller’s ongoing reasoning. 2310
2258 sumptions, implementation errors, unsupported
2259 claims, or conflicting conclusions. Then produce For example, in a math task, a caller may ask a 2311
2260 the final task-level answer required by the bench- peer to verify whether an algebraic transformation 2312
2261 mark.
is valid. In a coding task, a caller may ask whether 2313
2262 Inputs:
a specific implementation step, method behavior, 2314
2263 • Completed reasoning summaries and outputs:
edge case, or error message indicates a bug. In a 2315
2264 {completed_reasoning_summaries}
multi-hop QA task, a caller may ask a peer to check 2316
2265 Instructions:
whether a retrieved sentence supports a proposed 2317
2266 1. Compare the completed outputs.
2267 2. Compare the completed reasoning summaries answer. 2318
2268 supporting those outputs. A CONSULT response is not treated as a sepa- 2319
2269 3. Resolve disagreements using task constraints, rate final answer. It is used to repair, confirm, or 2320
2270 files, code behavior, database results, research
2271 evidence, or other benchmark-specific signals. strengthen the caller’s ongoing reasoning before 2321
2272 4. Produce the final answer in the required bench- later steps are generated. 2322
2273 mark format.
27

## Page 28

2323 H.3 Injection Requests "accepted_points": ["..."], 2373
"rejected_points": ["..."],
2324 An INJECT request is used when the caller identi- 2374
"conflicts": ["..."],
2325 fies a separable subtask whose result can be incor- 2375
"updated_state_summary": "...",
2326 porated into the caller’s ongoing reasoning. The 2376
"reason": "..."
2327 caller provides the relevant task fragment, context, 2377
},
2328 constraints, and expected output. The peer returns 2378
"token_usage": {
2329 a sub-result, such as a literature review fragment, 2379
"prompt_tokens": ...,
2330 debugging analysis, candidate implementation, evi- 2380
"completion_tokens": ...,
2331 dence synthesis, database reasoning result, or other 2381
"total_tokens": ...
2332 task-specific intermediate artifact. 2382
},
2333 The returned sub-result is not used as an inde- 2383
"answer_changed_after_response":
2334 pendent final answer. The caller evaluates it, ac- 2384
true
2335 cepts useful parts, rejects unsupported or incom- 2385
}
2336 plete parts, and integrates the accepted content into 2386
2337 its ongoing reasoning state before finalization. The field request_option specifies whether 2387
2338 Thus, CONSULT and INJECT differ in the size the exchange is a CONSULT or INJECT request. 2388
2339 and role of the requested help: CONSULT asks The field help_type specifies the requested 2389
2340 for localized assistance on a current uncertainty, kind of assistance. The integration field 2390
2341 whereas INJECT asks for a structured sub-result records whether the peer response was accepted, 2391
2342 that can be incorporated into later reasoning. Both partially accepted, rejected, or deferred. The 2392
2343 are instances of the same CoTIE principle because answer_changed_after_response field 2393
2344 both occur before the caller finalizes its answer. records whether the caller’s subsequent answer 2394
changed after receiving the peer response. 2395
2345 H.4 Request–Response–Integration Record This unified record makes different CoTIE ex- 2396
2346 For trace analysis, each CoTIE exchange is changes comparable. A verification request, a de- 2397
2347 recorded as a request–response–integration record. bugging request, a retrieval request, and a struc- 2398
2348 This record is used to verify that the exchange oc- tured subtask injection all share the same observ- 2399
2349 curred before finalization and to inspect whether able trace structure: caller, peer, step index, request 2400
2350 the peer response was actually used by the caller. option, request content, peer response, integration 2401
2351 A CoTIE record contains the following fields: status, updated caller state, and token usage. 2402
{
2352
H.5 Relation to Output-Level Communication 2403
"run_id": "...",
2353
"timestamp": "...", The key difference between CoTIE and output- 2404
2354
"caller_id": "...", level multi-agent communication is not whether 2405
2355
"peer_id": "...", agents exchange information. Both settings ex- 2406
2356
"step_id": ..., change information. The difference is when the 2407
2357
"request_option": exchange occurs and how the returned information 2408
2358
"CONSULT | INJECT", can affect the caller. 2409
2359
"help_type": "verify | compute | In output-level communication, each agent first 2410
2360
retrieve | clarify | debug completes its own local CoT process and produces 2411
2361
| critique", a completed answer, rationale, critique, vote, or 2412
2362
"request": { summary. The exchange happens only after local 2413
2363
"question_or_subtask": "...", reasoning has already been finalized. Such interac- 2414
2364
"context": "...", tion can help with final answer selection or final- 2415
2365
"expected_output": "..." stage critique, but it cannot affect the caller’s earlier 2416
2366
}, reasoning trajectory. 2417
2367
"peer_response": "...", In Late CoT Message Passing, agents also com- 2418
2368
"integration": { municate after local reasoning is complete, but the 2419
2369
"status": "integrated | exchanged content includes completed reasoning 2420
2370
partially_integrated | rejected s | ummaries. This is a stronger timing baseline be- 2421
2371
deferred", cause it exposes more reasoning content than final- 2422
2372
28

## Page 29

2423 answer-only exchange. However, it still attaches I Discussion: Semantic Compression for 2455
2424 peer information after local finalization. CoT-State Communication 2456
2425 In CoTIE, the caller sends a peer request from an
CoTIE changes the attachment point of cross-agent 2457
2426 ongoing reasoning state. The returned response is
communication. It does not introduce a new sum- 2458
2427 evaluated and integrated before the caller produces
marization algorithm or a new context-compression 2459
2428 the final answer. Therefore, the peer contribution
method. This distinction is important for interpret- 2460
2429 can influence subsequent reasoning steps, not only
ing the token-efficiency results. 2461
2430 final aggregation.
Method fam- When agents What is ex- Role I.1 Benchmark-Provided History 2462
ily communicate changed Summarization 2463
Final message After com- Answer, ratio- Output- In the MultiAgentBench experiments, history sum- 2464
passing pleted local nale, critique, or level
reasoning vote baseline marization follows the benchmark-provided default 2465
context-management mechanism. We do not claim 2466
Late CoT Mes- After com- Completed CoT Timing
sage Passing pleted local summary and an- baseline this summarization mechanism as part of CoTIE. 2467
reasoning swer It is part of the benchmark execution setting and 2468
CoTIE During on- CoT-state re- Proposed is kept consistent across the corresponding MAB- 2469
going CoT quest and peer attach- based protocols. 2470
reasoning response or ment
sub-result point Therefore, the token-efficiency result should 2471
not be interpreted as evidence that CoTIE intro- 2472
Table 8: Communication attachment points. Output-
duces a better summarizer. The relevant compar- 2473
level message passing and Late CoT Message Passing
communicate only after agents complete local reason- ison is instead: under the same benchmark-level 2474
ing. CoTIE communicates during an ongoing reasoning context-management setting, what happens when 2475
process and integrates the peer response before finaliza- the communication attachment point is moved from 2476
tion. completed-output exchange to intermediate CoT- 2477
state exchange? 2478
2431 H.6 Logging and Reproducibility In the reported cooperative MultiAgentBench ex- 2479
periments, CoTIE obtains higher task performance 2480
2432 For each CoTIE exchange, we log the caller agent,
while using fewer observed tokens than the corre- 2481
2433 peer agent, step index, request option, help type,
sponding output-level MAB protocols. This sup- 2482
2434 request content, peer response, integration record,
ports the claim that, under the benchmark execution 2483
2435 and token usage when available. These logs sup-
setting, pre-final CoT-state communication can im- 2484
2436 port both cost accounting and mechanism analysis.
prove observed token utilization. 2485
2437 The primary diagnostic fields are:
2438 • whether the request used CONSULT or INJECT; I.2 Why Context Management Matters 2486
2439 • whether the response was integrated, partially
Moving communication into intermediate reason- 2487
2440 integrated, rejected, or deferred;
ing states creates a practical context-management 2488
2441 • which points were accepted or rejected by the
challenge. A peer request should include enough 2489
2442 caller;
information for the peer to provide useful help, but 2490
2443 • whether conflicts were detected;
it should not repeatedly transmit irrelevant or re- 2491
2444 • how the caller’s intermediate state was updated;
dundant reasoning history. 2492
2445 • whether the caller’s later answer changed after
A useful CoT-state request should preserve: 2493
2446 receiving the peer response;
• the current subgoal or local uncertainty; 2494
2447 • the observed token usage of the exchange when
• the relevant task slice or constraints; 2495
2448 available.
• the caller’s current intermediate conclusion; 2496
2449 These logs are used to inspect whether CoTIE’s
• the specific help needed at the current step; 2497
2450 gains are consistent with the proposed attachment-
• any previously accepted peer information that 2498
2451 point mechanism: peer information is introduced
later reasoning depends on; 2499
2452 into an ongoing reasoning process and can affect
• the expected response format. 2500
2453 subsequent reasoning before the final answer is
At the same time, it should avoid transmitting un- 2501
2454 produced.
necessary repeated context, stale intermediate text, 2502
29

## Page 30

2503 unsupported speculative reasoning, or derivations
2504 that are no longer relevant to the current request.
2505 This context-managem, but it becomes more visi-
2506 ble when communication happens during reasoning
2507 rather than only at the final-output stage. The exper-
2508 iments in this paper keep the benchmark-provided
2509 context-management setting fixed when comparing
2510 MAB-based protocols, so that the primary manipu-
2511 lated variable remains the communication attach-
2512 ment point.
2513 I.3 Future Work: Reasoning-Aware State
2514 Compression
2515 Although CoTIE does not introduce a new summa-
2516 rization method, the results point to an important
2517 future direction: reasoning-aware state compres-
2518 sion for multi-agent CoT communication.
2519 A general-purpose dialogue summary may not
2520 preserve all information needed for downstream
2521 reasoning. In contrast, a reasoning-aware state rep-
2522 resentation should preserve entities, numerical val-
2523 ues, constraints, adopted peer information, open
2524 questions, intermediate conclusions, and dependen-
2525 cies that later reasoning steps may rely on.
2526 Future work can study adaptive CoT-state rep-
2527 resentations. For example, a caller may send a
2528 short state when asking for local verification, but
2529 a richer state when asking a peer to solve an in-
2530 jected subtask. Another direction is to represent
2531 the reasoning state as structured fields, such as cur-
2532 rent subgoal, known facts, unresolved uncertainties,
2533 accepted peer contributions, rejected claims, and
2534 required output format.
2535 Such compression methods would be com-
2536 plementary to CoTIE. CoTIE specifies when
2537 peer information enters the reasoning trajectory;
2538 reasoning-aware compression would specify how
2539 the intermediate state should be represented so that
2540 the exchange remains informative and efficient.
30
