# CPAC-DCAC 原始样本调查

## 结论先说人话

这轮 CPAC+DCAC full run 的总体读数是正的，但正得很薄：same-run initial majority 是 320/500，CPAC+DCAC final 是 325/500，只多 5 题。继续往原始样本里钻以后，最关键的判断是：

1. **CPAC 这个外层分流是有价值的。** 它把 500 题切成了三种很不一样的状态：220 题 collapse、189 题 majority/minority、91 题 no-majority conflict。后面的成败确实跟这三类状态高度相关。
2. **当前 DCAC 版本还没有站住。** DCAC 分支 189 题里，追回 4 题，伤害 8 题，净值 -4。它不是“完全没抓到真错”，而是“抓真错的同时更容易被假证据骗”。
3. **真正贡献正净值的是 listwise 分支。** no-majority conflict 的 91 题里，listwise 追回 11 题、伤害 2 题，净值 +9。但很多追回不是纯粹从候选中选对，而是 reviewer 重新做了一遍题，甚至输出了初始三张卡里没有的答案。
4. **MCE 没有进入这轮代码和 run，不能把任何提升归因给 MCE。** 但原始样本显示 MCE 的位置比较清楚：它更像是 CPAC 在 collapse 和 no-majority conflict 下调用的“认知线索交换”，而不是替代 DCAC 的 minority 翻盘证书。

所以，如果问“CPAC 和 DCAC 能不能有机合体”，答案是：**能，但现在该相信的是 CPAC 的状态控制，不该相信当前 prompt 版 DCAC 的翻盘精度。** DCAC 可以留在 CPAC 的 `unique=2` 分支里，但它必须升级成更硬的、可核算的 discriminant test，而不是让模型用 XML 标签说谁 pass/fail。

## 证据来源

- Full run: `experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/`
- Summary: `experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/math500-qwen25-7b-instruct-cpac-dcac/summary.json`
- Records: `experiments/20260705-a8002-math500-cpac-dcac-qwen25-7b-full/math500-qwen25-7b-instruct-cpac-dcac/records.jsonl`
- 这里的样本编号使用 records 中的 `index` 字段。
- 表里的“三路原始答案”指 records 中 parser 抽到的 `parsed_answer` / `normalized_answer`，不是完整模型原文。完整 rationale 保留在 records 的 `initial_outputs.output`、`dcac_claims.claim_output`、`dcac_certificates.certificate_output`、`listwise_outputs.output` 中。

## 方法实际怎么起作用

这轮代码不是单纯“多数投票后再辩论”。它的路径是：

1. 先让 3 个 initial agents 独立答题，并 parse/normalize 成候选答案。
2. CPAC 诊断候选池：
   - `collapse`：只有一个候选答案，直接 keep initial。
   - `minority_bearing`：2:1 分歧，进入 DCAC。
   - `no_majority_conflict`：三路都不同，进入 listwise discriminant。
3. DCAC 对 2:1 分歧做两段检查：
   - 少数派候选必须先生成一个方向性 claim，说明多数答案哪里违反必要条件。
   - 3 个 certificate reviewers 检查这个 claim，至少 2 个给出 admissible flip 才翻盘。
4. listwise 分支让 reviewers 同时看所有候选卡，输出最终答案，再聚合。

这个设计的好处是分工清楚：CPAC 负责判断“现在是什么候选池状态”，DCAC 只处理 `unique=2` 的 minority 翻盘，listwise 只处理无多数冲突。坏处也很直接：如果 DCAC 的 claim/certificate 本身不可靠，CPAC 会很清楚地把这块负贡献暴露出来。

## 总体分支画像

| 分支 | n | 初始错 -> 最终对 | 初始对 -> 最终错 | 净值 |
| --- | ---: | ---: | ---: | ---: |
| collapse / keep initial | 220 | 0 | 0 | 0 |
| DCAC | 189 | 4 | 8 | -4 |
| listwise discriminant | 91 | 11 | 2 | +9 |

从 branch decision 看，DCAC 一共真正 flip 了 17 次：4 次 `MaW_to_C`，8 次 `MaC_to_W`，5 次 `MaW_to_W`。这说明当前 DCAC 不是太激进，而是**翻盘精度低**：它翻得不多，但翻错占比高。

DCAC 的 claim 触发也很说明问题：

| DCAC 转移 | n | 有 valid directional claim | 产生 certificate case | flip |
| --- | ---: | ---: | ---: | ---: |
| `MaW_to_C` | 4 | 4 | 4 | 4 |
| `MaC_to_W` | 8 | 8 | 8 | 8 |
| `MaW_to_W` | 73 | 18 | 18 | 5 |
| `MaC_to_C` | 104 | 35 | 35 | 0 |

好消息是：4 个成功追回样本全部走通了 claim -> certificate -> flip。坏消息是：8 个伤害样本也全部走通了同一条链。也就是说，当前 certificate 机制能把“正确的少数派证据”结构化，也能把“错误的少数派叙事”结构化。

## DCAC 成功样本：它在什么情况下真有用

### idx 29：少数派补上了遗漏的组合因子

题目是从 5 个 upper class 里选 4 个、10 个 lower class 里选 8 个，总方案数应为 `C(5,4) * C(10,8) = 225`。

| 字段 | 内容 |
| --- | --- |
| Gold | `225` |
| 三路 parsed answer | `225`, `5`, `5` |
| 初始多数 | `5` |
| DCAC final | `225` |
| 转移 | `MaW_to_C` |

这里 DCAC 的作用非常干净：多数派只算了 `C(5,4)=5`，少数派算了上下两类士兵的组合乘积。claim 明确指出 `5` 没有计入 lower class 的选择数；三个 certificate 都检查到 `C(5,4) * C(10,8) = 5 * 45 = 225`，于是翻盘。

这是 DCAC 原设想中最理想的形态：少数派不是“我觉得另一个答案更好”，而是指出多数答案少了一个必要因子。

### idx 59：少数派用 inclusion-exclusion 打掉多数

| 字段 | 内容 |
| --- | --- |
| Gold | `5` |
| 三路 parsed answer | `5`, `15`, `15` |
| 初始多数 | `15` |
| DCAC final | `5` |
| 转移 | `MaW_to_C` |

题目是 50 人班级中，28 人 MATHCOUNTS，21 人 science club，6 人都不参加，所以至少参加一个活动的是 44 人。多数答案 `15` 会让 `28 + 21 - 15 = 34`，对不上 44；少数答案 `5` 满足 `28 + 21 - 5 = 44`。DCAC 在这里正好把“答案差异”变成了一个可检查等式。

### idx 92：少数派保留了二项分布完整公式

| 字段 | 内容 |
| --- | --- |
| Gold | `448/15625` |
| 三路 parsed answer | `2240/78125`, `21/625`, `21/625` |
| 初始多数 | `21/625` |
| DCAC final | `448/15625` |
| 转移 | `MaW_to_C` |

少数派的 `2240/78125` normalize 后等价于 `448/15625`。certificate 检查的是 `C(7,4) * (1/5)^4 * (4/5)^3`。这个样本里 claim 本身写得很弱，只是说两个分数不相等；真正起作用的是 certificate reviewer 重建了二项分布公式。

这也提示一个边界：DCAC 成功不一定来自 claim 生成得漂亮，有时来自 reviewer 自己把题重解对了。

### idx 216：单位换算题里，证书抓到了正确换算链

| 字段 | 内容 |
| --- | --- |
| Gold | `6` |
| 三路 parsed answer | `6`, `8`, `8` |
| 初始多数 | `8` |
| DCAC final | `6` |
| 转移 | `MaW_to_C` |

题目是 Trinket/Blinket/Drinket 换算。多数派给 `8`，少数派给 `6`。certificate 里出现了 `56 Drinkets = 6 Trinkets` 这样的检查，虽然有些 certificate 条件文本很粗糙，但最终方向对了。

这类样本说明 DCAC 可以当“少数派必要条件检查器”：当错误多数少乘、少除、少套一个约束时，DCAC 有机会把那一步暴露出来。

## DCAC 失败样本：它为什么现在还不能作为主 claim

### idx 41：XML 标签和计算文字互相矛盾，聚合却信了标签

题目给平行四边形四个点，其中第四点 `(x,y)` 满足 `x > 7`，gold 是 `17`。

| 字段 | 内容 |
| --- | --- |
| Gold | `17` |
| 三路 parsed answer | `7`, `17`, `17` |
| 初始多数 | `17` |
| DCAC final | `7` |
| 转移 | `MaC_to_W` |

少数派 claim 说：多数答案里 `x=8` 不满足 `x>7`，而 challenger 的 `x=7` 满足。这个 claim 在数学上是反的：`8 > 7` 成立，`7 > 7` 不成立。

更严重的是，某个 certificate 的 calculation 明明写了“majority answer x=8 satisfies this condition, but challenger x=7 does not”，但 XML 标签仍然给了 `<majority>fail</majority>`、`<challenger>pass</challenger>`、`<decision>flip</decision>`。当前聚合逻辑信标签，于是把正确多数翻成错误少数。

这是当前 DCAC 最大的结构性风险：**证书文本里可能已经暴露矛盾，但 parser/aggregator 只看结构标签。**

### idx 214：错误的 inclusion-exclusion 也能被包装成证书

| 字段 | 内容 |
| --- | --- |
| Gold | `110` |
| 三路 parsed answer | `40`, `120`, `120` |
| 初始多数 | `120` |
| DCAC final | `40` |
| 转移 | `MaW_to_W` |

这里多数 `120` 是错的，少数 `40` 也是错的。DCAC claim 指出 `120` 不满足某个 inclusion-exclusion 方程，并把 `P=40` 当成正确结果。certificate reviewers 接受了这个错误方程，于是 wrong-to-wrong flip。

这说明 DCAC 并不只需要判断“多数错没错”，还必须判断“少数派是不是正确修复”。当前证书经常只完成前半截。

### idx 256：证书里承认多数计算，却仍然翻向少数

| 字段 | 内容 |
| --- | --- |
| Gold | `8/21` |
| 三路 parsed answer | `4/21`, `4/7`, `4/7` |
| 初始多数 | `4/7` |
| DCAC final | `4/21` |
| 转移 | `MaW_to_W` |

题目是 `1/5 * 8/7 ÷ 12/20`，正确是 `8/21`。多数 `4/7` 错，少数 `4/21` 也错。一个 certificate 的 calculation 写出 `160/420 = 4/7`，却仍然标 `<majority>fail</majority>`、`<challenger>pass</challenger>`。这和 idx 41 是同一种病：标签层和推理层脱节。

### idx 310：reviewer 算到了 49，却翻向了 3

| 字段 | 内容 |
| --- | --- |
| Gold | `49` |
| 三路 parsed answer | `3`, `7/3`, `7/3` |
| 初始多数 | `7/3` |
| DCAC final | `3` |
| 转移 | `MaW_to_W` |

这个样本更刺眼：certificate calculation 里出现了正确计算 `7 * 10 * 21/30 = 49`，但 challenger answer 是 `3`，最终却翻向 `3`。说明当前 DCAC 缺一个硬约束：certificate 的计算结论必须和 challenger 的 parsed answer 一致。

### idx 343：算式对，乘法结果错，reviewer 照样盖章

| 字段 | 内容 |
| --- | --- |
| Gold | `58,500` |
| 三路 parsed answer | `625200`, `62400`, `62400` |
| 初始多数 | `62400` |
| DCAC final | `625200` |
| 转移 | `MaW_to_W` |

题目是车牌：2 个不同字母、2 个不同数字。正确计算是 `26 * 25 * 10 * 9 = 58,500`。少数派写成 `625,200`，这是明显乘法错误。claim 和 certificates 都抓住了“第二个 digit 应该有 9 种”这个方向，但没有核对最后乘积，于是把一个错误答案翻成另一个更离谱的错误答案。

这类样本说明 DCAC 的 discriminant 条件不能只检查“结构方向”，必须检查“最终数值闭环”。

### idx 32 和 idx 50：正确少数派在 claim 阶段直接哑火

| idx | Gold | 三路 parsed answer | 初始多数 | final | 现象 |
| ---: | --- | --- | --- | --- | --- |
| 32 | `720` | `720`, `120`, `120` | `120` | `120` | 正确少数派存在，但 claim 是 `NO_ADMISSIBLE_CLAIM` |
| 50 | `203` | `203`, `216`, `216` | `216` | `216` | 正确少数派存在，但 claim 是 `NO_ADMISSIBLE_CLAIM` |

idx 32 是圆桌排列，3 人必须坐一起。少数派用 block 方法得到 `5! * 3! = 720`，多数给 `120`。这是很适合 DCAC 的题：多数少乘了 block 内部 3 人排列。但 claim generator 没能提出 admissible claim，所以 DCAC 没进入 certificate，直接 keep 了错误多数。

这类样本说明 DCAC 当前有两种失效方向：该翻时不敢翻，不该翻时又被错误 claim 骗着翻。

## listwise 分支：为什么它带来正净值

listwise 处理的是三路都不同的 `no_majority_conflict`。这 91 题没有严格多数，原始 majority 只是 tie-breaking 意义上的 initial answer。listwise 最终贡献 +9：追回 11，伤害 2。

### idx 109：典型的从三张卡里选出正确卡

| 字段 | 内容 |
| --- | --- |
| Gold | `120` |
| 三路 parsed answer | `30`, `45`, `120` |
| listwise outputs | `120`, `120`, `30` |
| final | `120` |
| 转移 | `MaW_to_C` |

这里 listwise reviewer 真的在做 discriminant selection：三张卡里本来就有正确答案 `120`，两个 reviewer 选了它，一个 reviewer 仍选 `30`，最终 2:1 选对。

### idx 198：reviewer 重新做题，输出了候选池里没有的正确答案

| 字段 | 内容 |
| --- | --- |
| Gold | `10080` |
| 三路 parsed answer | `720`, `120`, `480` |
| listwise outputs | `10080`, `10080`, `10080` |
| final | `10080` |
| 转移 | `MaW_to_C` |

这题是 6 个女孩、2 个男孩坐一排，两个男孩相邻。初始三张卡没有一个给 `10080`。listwise reviewers 直接重算：把两个男孩当 block，共 7 个单位排列，再乘男孩内部 `2!`，得到 `7! * 2 = 10080`。

这对结果有利，但对机制归因很重要：这不是“候选识别成功”，而是“候选冲突触发了重新求解”。如果论文要讲 CPAC 的 candidate-pool identification，这种样本不能简单算成 listwise 在候选里选对。

### idx 440：代数化简也主要靠重解

| 字段 | 内容 |
| --- | --- |
| Gold | `14` |
| 三路 parsed answer | `-11`, `9`, `u - 24` |
| listwise outputs | `14`, `14`, `-11` |
| final | `14` |
| 转移 | `MaW_to_C` |

题目是展开 `(u+4)(u-1) - (u-3)(u+6)`。初始三张卡都没有正确答案 `14`。两个 listwise reviewers 展开重算得到 `14`，一个 reviewer 错选 `-11`。这再次说明 listwise 分支的正信号很大一部分来自 re-solve。

### idx 428 / idx 453 / idx 302：有正确候选时，listwise 也能做选择

| idx | Gold | 三路 parsed answer | listwise outputs | 作用 |
| ---: | --- | --- | --- | --- |
| 428 | `64` | `36`, `84`, `64` | `64`, `64`, `36` | 两个 reviewer 用 Cauchy/Titu 选到正确卡 |
| 453 | `10` | `70`, `10`, `468/47` | `10`, `10`, `10` | 比例代表数题，三票选到正确卡 |
| 302 | `5` | `30`, `178`, `5` | `5`, `30`, `5` | 循环节长度题，2:1 选到正确卡 |

这些样本比较接近 CPAC 设想：no-majority conflict 里本来含有正确候选，listwise reviewer 做判别后选出来。

### idx 279 和 idx 396：listwise 也会被集体误读带偏

| idx | Gold | 三路 parsed answer | listwise outputs | final | 转移 |
| ---: | --- | --- | --- | --- | --- |
| 279 | `7π` | `7π`, `20π`, `4π` | `20π`, `20π`, `7π` | `20π` | `MaC_to_W` |
| 396 | `2` | `2`, `4`, `1.5` | `4`, `4`, `4` | `4` | `MaC_to_W` |

idx 279 是同心圆区域面积，初始三张卡里第一张就是 gold `7π`，但两个 listwise reviewers 误读区域，选了 `20π`。idx 396 是 tangram 面积，三个 reviewers 都选 `4`，把正确初始答案 `2` 翻掉。

这说明 listwise 的问题不是没有，而是它在当前 run 中比 DCAC 更稳定：91 题里只伤害 2 题。但它的成功机制混合了 candidate selection 和 full re-solve，必须分开归因。

## collapse 分支：CPAC 保守，但没有恢复能力

collapse 是 CPAC 的“别折腾”分支。220 题中，188 题初始多数正确并被保留，32 题初始多数错误也被保留。它的净值是 0，但这个 0 很有意义：它避免了无分歧时乱翻，同时暴露了 coverage collapse。

### idx 35：三路都同错，没有分歧抓手

| 字段 | 内容 |
| --- | --- |
| Gold | `3` |
| 三路 parsed answer | `0`, `0`, `0` |
| CPAC action | keep initial |
| final | `0` |

题目是模 7 乘积。三个 initial agents 都给 `0`，CPAC 没有 challenger，也就没有 DCAC 的入口。这不是 DCAC 失败，而是候选池覆盖失败。要处理这种题，必须引入新采样、新视角或 MCE 这种不直接暴露答案的认知 cue，而不是在现有候选上投票。

### idx 127：base notation 暴露 evaluator/candidate-card 风险

| 字段 | 内容 |
| --- | --- |
| Gold | `4210_5` |
| 三路 parsed answer | `4230_5`, `4210_5`, `4230_5` |
| normalized | 三路都落到 `expr:5` |
| CPAC state | `collapse` with `base_notation` representation risk |
| final | `expr:5` |

这个样本很关键：原始 parsed answer 里其实出现了正确的 `4210_5`，但 normalizer 把 base notation 压坏了，三路都变成 `expr:5`，于是 CPAC 认为候选池 collapse。这个不是机制本身的数学判断，而是 evaluator/normalizer 把候选差异吞掉了。

因此所有涉及 base notation 的结论都要带 caveat。idx 338 也类似：题目 gold 是 `4343_6`，DCAC 翻向 raw `4343`，数学方向接近正确，但由于 base suffix 丢失和 normalizer 行为，记录里变成 `MaC_to_W`。这类样本不能粗暴拿来证明 DCAC 好或坏，只能证明 representation-risk 必须被单独处理。

## 机制归因

### CPAC 的作用

CPAC 这轮最大的价值不是直接提高很多分，而是把错误空间拆开了。以前只看总准确率，会混在一起：有些题全员同错，有些题 2:1 分歧，有些题三路冲突。现在能看到：

- collapse：多数时候 keep 是对的，但全员同错时完全没恢复能力。
- minority-bearing：有可恢复空间，但当前 DCAC 选择器不稳。
- no-majority conflict：有很强的重新判别/重解空间，当前 listwise 给了正贡献。

这个分解本身是可靠的研究资产。它告诉我们“什么时候该用什么通信动作”，而不是让一个统一 debate 协议吃所有题。

### DCAC 的作用

DCAC 的原始想法是对的：少数派不能凭存在感推翻多数，必须提出能区分两个答案的必要条件。成功样本里，它确实抓到了遗漏组合因子、inclusion-exclusion 等式、二项分布公式、单位换算链。

但当前实现的核心缺陷也很明确：

- claim generator 对真正正确 minority 的召回不够，idx 32、idx 50 直接 `NO_ADMISSIBLE_CLAIM`。
- certificate reviewer 会相信错误 claim，idx 214、idx 343 是典型 wrong-to-wrong。
- XML 标签和 calculation 文本可能矛盾，idx 41、idx 256 特别明显。
- certificate 的计算结果不一定和 challenger parsed answer 一致，idx 310 是典型。

所以当前 DCAC 不是“没戏”，而是“不能靠自然语言证书标签收口”。它需要把 certificate 变成更硬的结构：条件、代入、计算结果、candidate answer 一致性都要可核验。

### listwise 的作用

listwise 在这轮里是真正带来净增益的分支。它既能在三张卡里选出正确卡，也能在候选全错时被冲突触发重新求解。后者对系统效果好，但对论文叙事要谨慎：它不是纯 candidate-pool selection，而是 re-solving after disagreement。

换句话说，listwise 是一个很强的 fallback action，但不能直接证明“候选池已有正确答案，只差识别”。

### MCE 的位置

MCE 没进这轮实验，所以没有直接证据。只从样本机制看，它最自然的位置有两个：

1. collapse 中全员同错时，直接再投票没有用，MCE 可以尝试交换 answer-free cue，让 agent 看到“可能漏掉的约束/计数维度/表示风险”。
2. no-majority conflict 中，listwise 现在常靠完整重解；MCE 可以把完整答案交换降级成局部认知线索交换，看能不能保留恢复、减少被错误完整 rationale 带偏。

但这只是由样本失败模式推出的位置判断，不是实验结果。

## 最终判断

这轮深入原始样本后，我对三件事的信心排序是：

1. **CPAC 有戏。** 它提供了清晰的状态空间，把不同失败模式拆开了。
2. **listwise 作为 CPAC 的 no-majority action 有实证正信号。** 但它混入了 re-solve，方法归因要诚实。
3. **DCAC 的方向有戏，当前实现没站住。** 自然语言 claim + XML certificate 标签不足以当可靠准入；它必须加入更硬的数值闭环、一致性检查和 representation-risk guard。

如果要把 CPAC 和 DCAC 有机合体，比较稳的说法不是“DCAC 提升了整体准确率”，而是：

> CPAC exposes when a minority-admissibility mechanism is needed; current DCAC is a first diagnostic implementation of that branch, and raw-sample evidence shows both the promise of answer-delta certificates and the failure modes that must be structurally constrained.

中文直说就是：**CPAC 负责把场子搭对，DCAC 负责在 2:1 分歧里审少数派；这套戏可以唱，但现在 DCAC 的唱腔还跑调，不能当主角。**
