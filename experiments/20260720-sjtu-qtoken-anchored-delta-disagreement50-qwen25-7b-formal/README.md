# Question-token anchored delta：SJTU 50 题正式实验

状态：`COMPLETED`

## 结论

题目 token 绑定没有提高正确率。

baseline、`raw_delta` 和 `question_token_delta` 都答对 9/50。随机同范数对照答对 10/50，比 token 绑定多 1 题。绑定 token 会明显改变答案，但没有显示出方法特异性收益。

## 结果

| 条件 | 正确 | 相对 baseline | 答案改变 | 错转对 | 对转错 | 多数票平局 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 9/50 | — | — | — | — | 27/50 |
| `raw_delta` | 9/50 | 0 | 23/50 | 1 | 1 | 24/50 |
| `question_token_delta` | 9/50 | 0 | 29/50 | 1 | 1 | 22/50 |
| `question_token_random_same_norm` | 10/50 | +1 | 32/50 | 2 | 1 | 24/50 |

`question_token_delta` 把多数票平局从 27 题降到 22 题，但没有增加答对题数。它改变了 29 题的答案，说明干预确实进入了模型；随机同范数向量改变了更多答案，而且正确率略高。因此，本次结果不支持“题目 token 绑定比位置扰动本身更有效”。

## 配置

- 模型：Qwen2.5-7B-Instruct，BF16
- 数据：`math500/mca_disagreement_v1` 前 50 题
- agents：3
- 层：22
- 上下文上限：8192 tokens
- 输出上限：1536 tokens
- conditions：`raw_delta`、`question_token_delta`、`question_token_random_same_norm`
- GPU：RTX 3090 24 GB
- 分片：8 个互不重叠的单卡作业
- 最大峰值显存：14.42 GiB

## 完整性检查

- 8 个作业全部 `Completed`。
- 分片行数为 `7+7+6+6+6+6+6+6=50`。
- 50 个题目 ID 唯一。
- 合并后的顺序与输入文件前 50 题完全一致。
- 150 个 baseline agent 输出中，1 个没有解析出答案，22 个达到 1536-token 上限。

输出截断会影响一部分题目的答案质量。当前 runner 没有记录 condition 输出的 token 数，因此不能精确统计三个干预条件的截断率。这个限制不改变条件间的直接计数，但意味着本次准确率不能代表模型在无限输出预算下的能力。

## 作业记录

| 分片 | 行数 | Job ID | runner 用时 |
| ---: | ---: | --- | ---: |
| 0 | 7 | `job-178456064958854271966-feiyang-ying` | 2165.5 秒 |
| 1 | 7 | `job-178456065047985039180-feiyang-ying` | 1162.2 秒 |
| 2 | 6 | `job-178456065139232793151-feiyang-ying` | 1472.7 秒 |
| 3 | 6 | `job-178456065231074090434-feiyang-ying` | 1316.7 秒 |
| 4 | 6 | `job-178456065322530291098-feiyang-ying` | 1567.9 秒 |
| 5 | 6 | `job-178456065411945532192-feiyang-ying` | 1454.0 秒 |
| 6 | 6 | `job-178456065501460385259-feiyang-ying` | 1770.9 秒 |
| 7 | 6 | `job-178456065593686502482-feiyang-ying` | 1082.3 秒 |

集群先启动 6 个分片，另外 2 个在 GPU 释放后开始。从首次提交到全部结束约 49 分钟。8 个分片累计计算时间为 11992.2 秒；最慢分片为 2165.5 秒。

合并结果位于 `math500-qwen25-7b-instruct-mca-question-token-anchored-delta/`。各分片的原始结果保存在相邻的 `-shardXX-of-08` 目录中。
