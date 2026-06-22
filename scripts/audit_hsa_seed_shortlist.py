#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_CASE_CARDS = Path("experiments/20260618-local-hiddenbench-failure-seeds/case_cards.jsonl")
DEFAULT_FACT_DRAFT = Path("experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/p0p1p2_fact_units.draft.json")
DEFAULT_PERT_DRAFT = Path("experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/p0p1p2_perturbations.draft.json")
DEFAULT_PACKET = Path("experiments/20260619-local-hsa-v0-p0p1p2-seed-expansion36-draft/packet/hsa_v0_packet.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260619-local-hsa-v0-seed-shortlist-gate")

P0_NEXT = {12, 31}
P2_BULKY = {5}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, blob: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(blob, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def avg_private_chars(row: dict[str, Any]) -> float:
    facts = [str(item.get("private_fact", "")) for item in row.get("private_facts", []) if isinstance(item, dict)]
    return sum(len(item) for item in facts) / len(facts) if facts else 0.0


def priority_for(row: dict[str, Any], packet_rows: int, has_fact: bool) -> str:
    task_id = int(row.get("task_id", -1))
    if packet_rows and row.get("recommended_v0_seed"):
        return "DONE"
    if packet_rows:
        return "SANITY"
    if not row.get("recommended_v0_seed"):
        return "OUT"
    if not has_fact and task_id in P0_NEXT:
        return "P0"
    if not has_fact and task_id in P2_BULKY:
        return "P2"
    return "P1"


def readiness(row: dict[str, Any], packet_rows: int, has_fact: bool, has_pert: bool) -> str:
    if packet_rows and row.get("recommended_v0_seed"):
        return "packetized_shortlist_seed"
    if packet_rows:
        return "packetized_sanity_seed"
    if not row.get("recommended_v0_seed"):
        return "extracted_not_recommended"
    if not has_fact:
        return "needs_manual_fact_units"
    if not has_pert:
        return "needs_perturbation_draft"
    return "draft_ready_not_packetized"


def next_action(row: dict[str, Any], status: str, priority: str) -> str:
    if status == "packetized_shortlist_seed":
        return "keep as current HSA packet coverage"
    if status == "packetized_sanity_seed":
        return "keep as sanity row; do not count as recommended seed coverage"
    if priority == "P0":
        return "write source cards, oracle units, and two perturbations next"
    if priority == "P1":
        return "queue after P0 once annotation pattern is stable"
    if priority == "P2":
        return "defer until bulky hidden-profile rows are needed"
    return "archive as extracted background"


def short_private_surface(row: dict[str, Any]) -> str:
    facts = []
    for item in row.get("private_facts", []):
        if not isinstance(item, dict):
            continue
        text = " ".join(str(item.get("private_fact", "")).split())
        if text:
            facts.append(text[:90])
    return " || ".join(facts[:4])


def build_rows(
    case_cards: list[dict[str, Any]],
    fact_drafts: list[dict[str, Any]],
    perturbations: list[dict[str, Any]],
    packet_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fact_by_task = {int(row.get("source_ref", {}).get("task_id")): row for row in fact_drafts}
    pert_by_sketch = {row.get("sketch_id"): row for row in perturbations}
    packet_count_by_task: dict[int, int] = {}
    for row in packet_rows:
        task_id = row.get("hsa_meta", {}).get("source_ref", {}).get("task_id")
        if isinstance(task_id, int):
            packet_count_by_task[task_id] = packet_count_by_task.get(task_id, 0) + 1

    out: list[dict[str, Any]] = []
    seen_task_ids: set[int] = set()
    for row in sorted(case_cards, key=lambda item: (not bool(item.get("recommended_v0_seed")), int(item.get("task_id", 9999)))):
        task_id = int(row.get("task_id"))
        seen_task_ids.add(task_id)
        fact = fact_by_task.get(task_id)
        sketch_id = fact.get("sketch_id") if fact else ""
        has_fact = fact is not None
        has_pert = bool(sketch_id and sketch_id in pert_by_sketch)
        packet_rows_n = packet_count_by_task.get(task_id, 0)
        status = readiness(row, packet_rows_n, has_fact, has_pert)
        priority = priority_for(row, packet_rows_n, has_fact)
        out.append(
            {
                "priority": priority,
                "task_id": task_id,
                "task_name": row.get("task_name"),
                "recommended_v0_seed": bool(row.get("recommended_v0_seed")),
                "gold_answer": row.get("gold_answer"),
                "possible_answer_count": len(row.get("possible_answers", [])),
                "shared_fact_count": len(row.get("shared_information", [])),
                "private_fact_count": len(row.get("private_facts", [])),
                "avg_private_fact_chars": round(avg_private_chars(row), 1),
                "manual_fact_draft": has_fact,
                "perturbation_draft": has_pert,
                "packet_rows": packet_rows_n,
                "readiness": status,
                "next_action": next_action(row, status, priority),
                "private_surface": short_private_surface(row),
            }
        )
    for task_id, fact in sorted(fact_by_task.items()):
        if task_id in seen_task_ids:
            continue
        fake_row = {
            "task_id": task_id,
            "task_name": fact.get("source_ref", {}).get("name"),
            "recommended_v0_seed": False,
            "gold_answer": fact.get("evaluator_metadata", {}).get("correct_answer"),
        }
        sketch_id = fact.get("sketch_id", "")
        has_pert = bool(sketch_id and sketch_id in pert_by_sketch)
        packet_rows_n = packet_count_by_task.get(task_id, 0)
        status = readiness(fake_row, packet_rows_n, True, has_pert)
        priority = priority_for(fake_row, packet_rows_n, True)
        source_facts = [item for item in fact.get("source_facts", []) if isinstance(item, dict)]
        hidden_facts = [item for item in source_facts if item.get("channel") == "hidden"]
        shared_facts = [item for item in source_facts if item.get("channel") == "shared"]
        private_surface = " || ".join(" ".join(str(item.get("text", "")).split())[:90] for item in hidden_facts[:4])
        avg_chars = sum(len(str(item.get("text", ""))) for item in hidden_facts) / len(hidden_facts) if hidden_facts else 0.0
        out.append(
            {
                "priority": priority,
                "task_id": task_id,
                "task_name": fake_row["task_name"],
                "recommended_v0_seed": False,
                "gold_answer": fake_row["gold_answer"],
                "possible_answer_count": len(fact.get("evaluator_metadata", {}).get("possible_answers", [])),
                "shared_fact_count": len(shared_facts),
                "private_fact_count": len(hidden_facts),
                "avg_private_fact_chars": round(avg_chars, 1),
                "manual_fact_draft": True,
                "perturbation_draft": has_pert,
                "packet_rows": packet_rows_n,
                "readiness": status,
                "next_action": next_action(fake_row, status, priority),
                "private_surface": private_surface,
            }
        )
    return out


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "priority",
        "task_id",
        "task_name",
        "recommended_v0_seed",
        "gold_answer",
        "possible_answer_count",
        "shared_fact_count",
        "private_fact_count",
        "avg_private_fact_chars",
        "manual_fact_draft",
        "perturbation_draft",
        "packet_rows",
        "readiness",
        "next_action",
        "private_surface",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def format_md(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    recommended = [row for row in rows if row["recommended_v0_seed"]]
    p0 = [row for row in recommended if row["priority"] == "P0"]
    done = [row for row in recommended if row["priority"] == "DONE"]
    if p0:
        p0_names = "、".join(f"`HB{int(row['task_id']):02d}`" for row in p0)
        next_sentence = f"下一批最适合补的是 {p0_names}。这些 seed 需要补 source cards、oracle admission units、rejections、base variant 和两个 perturbation。"
    elif len(done) == len(recommended):
        next_sentence = "推荐 seed 已全量纳入当前 HSA 包。下一步若扩包，应先做 expansion selection gate，从非推荐候选或新增 case 中重新筛选。"
    else:
        next_sentence = "当前没有自动 P0 标注目标。下一步应人工复核未入包 seed 的事实面、候选数量和扰动可构造性。"
    lines = [
        "# HSA-v0 Seed Shortlist Gate",
        "",
        "日期：2026-06-19",
        "",
        "## 核心判断",
        "",
        f"HiddenBench failure seed 池里有 `{summary['recommended_v0_seed_count']}` 个推荐 seed。当前已有人工 HSA fact draft 的推荐 seed 有 `{summary['recommended_with_fact_draft']}` 个，已经进入 HSA packet 的推荐 seed 有 `{summary['recommended_packetized']}` 个。",
        "",
        next_sentence,
        "",
        "## 计数",
        "",
        "| 项 | 数量 |",
        "| --- | ---: |",
        f"| extracted candidates | `{summary['candidate_count']}` |",
        f"| recommended seeds | `{summary['recommended_v0_seed_count']}` |",
        f"| recommended with fact draft | `{summary['recommended_with_fact_draft']}` |",
        f"| recommended packetized | `{summary['recommended_packetized']}` |",
        f"| sanity packetized outside shortlist | `{summary['sanity_packetized']}` |",
        "",
        "## 推荐 Seed 状态",
        "",
        "| 优先级 | task | name | gold | shared | private | packet rows | 状态 | 下一步 |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for row in recommended:
        lines.append(
            "| {priority} | `{task_id}` | {task_name} | {gold_answer} | {shared_fact_count} | {private_fact_count} | {packet_rows} | `{readiness}` | {next_action} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## P0 标注目标",
            "",
        ]
    )
    if p0:
        for row in p0:
            lines.extend(
                [
                    f"### HB{int(row['task_id']):02d} {row['task_name']}",
                    "",
                    f"- gold: `{row['gold_answer']}`",
                    f"- shared facts: `{row['shared_fact_count']}`",
                    f"- private facts: `{row['private_fact_count']}`",
                    f"- private surface: {row['private_surface']}",
                    "- 需要补：source cards、oracle admission units、rejections、base variant、两个扰动。",
                    "",
                ]
            )
    else:
        lines.extend(
            [
                "当前没有 P0 推荐 seed 待标注。",
                "",
            ]
        )
    lines.extend(
        [
            "## 准入规则",
            "",
            "扩 seed 前必须先补人工事实单元和扰动定义。只要缺少 `oracle_admission_units` 或 `expected_downstream_delta`，就不能启动模型真跑。",
            "",
            "本 gate 的作用是防止 HSA 从机制表滑回普通 HiddenBench prompt 表。下一轮应先做扩展候选筛选门，再 materialize packet 并做 transparent controls。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit HiddenBench candidate seeds for HSA-v0 packet readiness.")
    parser.add_argument("--case-cards", type=Path, default=DEFAULT_CASE_CARDS)
    parser.add_argument("--fact-draft", type=Path, default=DEFAULT_FACT_DRAFT)
    parser.add_argument("--perturbation-draft", type=Path, default=DEFAULT_PERT_DRAFT)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    args = parser.parse_args()

    case_cards = read_jsonl(args.case_cards)
    fact_drafts = read_json(args.fact_draft)
    perturbations = read_json(args.perturbation_draft)
    packet_rows = read_jsonl(args.packet)
    rows = build_rows(case_cards, fact_drafts, perturbations, packet_rows)

    recommended = [row for row in rows if row["recommended_v0_seed"]]
    summary = {
        "candidate_count": len(rows),
        "recommended_v0_seed_count": len(recommended),
        "recommended_with_fact_draft": sum(1 for row in recommended if row["manual_fact_draft"]),
        "recommended_packetized": sum(1 for row in recommended if row["packet_rows"] > 0),
        "recommended_unpacketized": sum(1 for row in recommended if row["packet_rows"] == 0),
        "sanity_packetized": sum(1 for row in rows if row["packet_rows"] > 0 and not row["recommended_v0_seed"]),
        "p0_next_task_ids": [row["task_id"] for row in recommended if row["priority"] == "P0"],
        "out_dir": str(args.out_dir),
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.out_dir / "seed_gate_rows.csv", rows)
    write_json(args.out_dir / "seed_gate_summary.json", summary)
    (args.out_dir / "seed_gate.md").write_text(format_md(rows, summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
