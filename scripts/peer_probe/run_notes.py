"""Run-note rendering helpers for peer-exposure probes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def write_readme(
    out_dir: Path,
    summary: Dict[str, Any],
    command: str,
    started_at: str,
    ended_at: str,
    *,
    dataset_name: str,
    model: str,
) -> None:
    lines = [
        "# Peer Exposure Probe",
        "",
        "## What We Tried",
        "",
        "A controlled peer-exposure probe over saved mixed-correctness disagreement cases.",
        "Each case first gets a no-peer answer, then the same target model revises after",
        "seeing controlled peer surfaces derived from saved peer responses.",
        "",
        "## Setup",
        "",
        f"- Dataset/task: `{dataset_name}`",
        f"- Model: `{model}`",
        f"- Peer warning: `{summary.get('peer_warning')}`",
        f"- Peer source mode: `{summary.get('peer_source_mode', 'named')}`",
        f"- Response mode: `{summary.get('response_mode')}`",
        f"- Selection mode: `{summary.get('selection_mode')}`",
        f"- Sample seed: `{summary.get('sample_seed')}`",
        "",
        "## Command",
        "",
        "```bash",
        command,
        "```",
        "",
        "## What Happened",
        "",
        f"- Run ID: `{summary['run_id']}`",
        f"- Cases: `{summary['num_cases']}`",
        f"- Records: `{summary['num_records']}`",
        f"- Started: `{started_at}`",
        f"- Ended: `{ended_at}`",
        "",
        "| Condition | Records | Accuracy | Right->Wrong | Wrong->Right | Stable Right | Stable Wrong | Unknown | Peer Adoption |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for condition, stats in summary["conditions"].items():
        lines.append(
            f"| `{condition}` | {stats.get('records', 0)} | "
            f"{stats.get('accuracy', 0):.3f} | {stats.get('right_to_wrong', 0)} | "
            f"{stats.get('wrong_to_right', 0)} | {stats.get('stable_right', 0)} | "
            f"{stats.get('stable_wrong', 0)} | {stats.get('unknown', 0)} | "
            f"{stats.get('peer_answer_adoption_rate', 0):.3f} |"
        )
    lines += [
        "",
        "## Caveats",
        "",
    ]
    for caveat in summary["caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")
    out_dir.joinpath("README.md").write_text("\n".join(lines), encoding="utf-8")
