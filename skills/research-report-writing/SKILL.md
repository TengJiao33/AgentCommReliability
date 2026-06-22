---
name: research-report-writing
description: Project-level writing discipline for Chinese oral updates, mentor-facing research reports, experiment result explanations, and paper-story memos in AgentCommReliability. Use when Codex reports research progress to the user, writes or revises reports under reports/, summarizes experiment outcomes, explains whether a result supports a claim, prepares mentor/A-conference narrative updates, or turns messy evidence into clear Chinese prose without inflating claims.
---

# Research Report Writing

## Core Rule

Make the reader understand the judgment before the evidence pile.

For this project, a good report is not a polished-sounding essay. It is a clear
research artifact that lets the user see:

- what we now believe;
- what concrete evidence supports it;
- what failed, weakened, or bounded it;
- what claim is not yet earned;
- what the next pressure point should be.

This skill is distilled from `Master-cai/Research-Paper-Writing-Skills`
(`research-paper-writing`, MIT; itself adapted from Peng Sida's public research
writing notes). Keep only the parts useful for this project: paragraph flow,
claim-evidence discipline, introduction-style story logic, experiment writing,
and reviewer-style self-audit.

## Language Default

Write in Chinese when reporting to the user unless the user explicitly asks for
English or for paper-ready English text.

Use direct, concrete Chinese. Avoid slogan-like novelty language. Prefer:

```text
目前它更像一个可工作的机制切口，但还不是完整方法故事。
```

over:

```text
这证明了一个全新的多智能体通信范式。
```

## Report Spine

Use this spine for oral updates, written reports, and result explanations:

1. Bottom line: one or two sentences naming the current judgment.
2. Evidence: exact runs, reports, paths, numbers, or inspected cases.
3. Interpretation: what the evidence means and which mechanism it suggests.
4. Caveats: parser, benchmark, prompt, sample, or design issues near the claim.
5. Next pressure: the smallest or sharpest move that would change the judgment.

For longer reports, use this expanded order:

```text
一句话判断 -> 背景/问题 -> 我们做了什么 -> 发生了什么 ->
为什么重要 -> 为什么还不能这么说 -> 下一步怎么压
```

## Paragraph Discipline

Each paragraph should carry one message only.

Before writing a paragraph, silently choose its role:

- judgment;
- evidence;
- mechanism;
- caveat;
- comparison;
- next step;
- failure/postmortem.

The first sentence should reveal that role. If the paragraph cannot be
reverse-outlined into one sentence, split or rewrite it.

Sentence-to-sentence flow should use one clear relation:

- cause: because / 因为 / 这说明;
- contrast: but / 但 / 然而;
- consequence: therefore / 所以 / 因此;
- refinement: more precisely / 更准确地说;
- example: for example / 具体来说.

Do not stack unrelated observations in one long paragraph just because they
came from the same experiment.

## Claim-Evidence Discipline

Every strong claim must have an evidence handle.

Use this internal check before making a claim:

```text
Claim: what am I saying?
Evidence: which run/report/case/number shows it?
Status: supported, diagnostic, hypothesis, or unsupported?
Caveat: what could make this interpretation wrong?
```

If the status is not `supported`, weaken the wording:

- `证明` -> `提示`, `支持`, `暴露出`, `更像是`;
- `有效` -> `在这个设置下出现信号`;
- `失败` -> `这个实验未能回答原问题`;
- `没有效果` -> `当前设置没有分辨出效果`;
- `novel` -> `可能有新颖切口，但还需要外部压力和更干净实验`.

Never turn plumbing failure into behavioral evidence. If the result is wrong
because of parser/gold/data/control design, say it is a workflow failure.

## Story Logic

When explaining the paper idea, reason backward before writing forward.

Backward questions:

- What exact technical problem are we claiming exists?
- Why is it not just a known limitation or generic model weakness?
- What mechanism explains the failure?
- What evidence would falsify this mechanism?
- What intervention, protocol, or benchmark directly pressures it?

Forward report order:

1. Define the task or setting.
2. Name the unresolved failure or tension.
3. Explain the suspected technical reason.
4. State our handle or intervention.
5. Show the evidence and boundary.

Avoid the weak structure:

```text
别人方法不好 -> 我们加一个东西 -> 指标涨了
```

Prefer the stronger structure:

```text
现有通信设定默认 A，但在 P 条件下 A 会暴露 B；
我们的 C 不是泛泛补丁，而是直接让 B 可见、可控或可被压力测试。
```

## A-Conference Status Reporting

When reporting whether the project is "A-conference shaped", name the route
before judging strength: method improvement, diagnostic / compiler discipline,
benchmark / stress test, or mechanism microscope.

Do not say "no result" when the evidence has only failed to earn a method
claim. Instead name the downgrade:

```text
这还不是方法提升结果；它目前更像一个诊断/执行边界结果。
```

When a strong transparent baseline beats or matches the proposed method, report
that near the claim. Then state whether the remaining value is diagnostic,
benchmark-facing, or only historical background.

## Experiment Reporting

When explaining an experiment, separate purpose from result.

Minimum structure:

- Purpose: this run was supposed to answer which question.
- Design: what contrast or control made it answerable.
- Result: what happened, with numbers if available.
- Diagnosis: whether the result is claim-bearing, diagnostic, failed, or retired.
- Caveat: what could confound it.
- Consequence: what should change in the research plan.

If the experiment failed, classify the failure:

- design failure;
- data/gold failure;
- evaluator/parser failure;
- execution failure;
- true negative.

Only true negatives directly pressure the idea. Other failures pressure the
workflow and should become prevention rules or cleaner packets.

## Reviewer-Style Self-Audit

Before finalizing a substantial report, check five rejection risks:

- Contribution: does the report identify real new knowledge, not just a task
  where models fail?
- Clarity: can a reader reconstruct the setup, contrast, and evidence path?
- Empirical strength: are the numbers/cases meaningful rather than decorative?
- Evaluation completeness: are controls, baselines, gold, parser, and benchmark
  caveats visible?
- Design soundness: could the experiment be too artificial, too concentrated,
  or too dependent on one prompt/case?

If a risk is live, mention it near the relevant claim rather than hiding it at
the end.

## Output Shapes

For quick oral-style updates:

```text
我的判断是...
支撑它的是...
但现在最危险的 caveat 是...
所以我会把下一步压在...
```

For detailed Chinese reports:

```text
# 标题

## 核心判断
## 证据链
## 机制解释
## 失败和边界
## 对论文故事的影响
## 下一步压力测试
```

For failed experiments:

```text
## 原本想回答什么
## 实际发生了什么
## 为什么它没有回答原问题
## 哪些东西还能保留
## 下次必须怎么防
```

## Relationship To Other Skills

Use `research-experiment-gate` for run design, launch, triage, and run records.

Use `research-story-synthesis` for judging whether the evidence supports a
solid/novel/live/stale research story. When discussing external pressure or
possible novelty collision, use its full-paper collision-audit rule rather than
abstract-level keyword similarity.

Use this skill when shaping the final communication to the user, mentor, or
paper-facing report. It governs prose, structure, and claim hygiene.
