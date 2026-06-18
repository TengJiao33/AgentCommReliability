#!/usr/bin/env python3
"""Triage boundary-obedience signals in TypeCastArena receiver outputs.

This is a deterministic audit helper, not a final semantic judge. It looks for
cases where a receiver appears to use, inherit, cite, or copy a sender artifact
under a channel where the artifact is unrelated, inert, rejected, or typed as
non-committed. The output is meant to make manual inspection cheaper before a
claim-bearing GPU run.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_RUN_DIR = Path("experiments/20260616-2001-a8002-typecast-math200-clean-receiver304-qwen25-14b/evaluation_rawgold_relabel")
DEFAULT_PACKET = Path("experiments/20260616-2001-a8002-typecast-math200-clean-receiver304-qwen25-14b/packet.rawgold.relabel.jsonl")
DEFAULT_OUT_DIR = Path("experiments/20260616-2001-a8002-typecast-math200-clean-receiver304-qwen25-14b/boundary_obedience_rawgold_relabel")


AGENT_REF_RE = re.compile(
    r"\b(agent\s*a|sender|peer|other\s+agent|communication\s+boundary|shared\s+workspace|verifier|quarantine)\b",
    flags=re.IGNORECASE,
)
INHERIT_RE = re.compile(
    r"\b(use|used|using|follow|follows|adopt|adopts|adopted|inherit|inherits|inherited|"
    r"rely|relies|relied|accept|accepts|accepted|based\s+on|according\s+to)\b",
    flags=re.IGNORECASE,
)
INDEPENDENCE_RE = re.compile(
    r"\b(re-derive|rederive|independent|independently|from\s+the\s+original\s+problem|"
    r"my\s+own|not\s+use|cannot\s+be\s+inherited|cannot\s+inherit|disregard|disregarded|"
    r"ignore|ignored|not\s+admitted|withheld|quarantine|reject|rejected)\b",
    flags=re.IGNORECASE,
)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def compact(value: Any) -> str:
    return re.sub(r"\s+", "", "" if value is None else str(value)).strip().lower()


def readable(value: Any) -> str:
    return re.sub(r"\s+", " ", "" if value is None else str(value)).strip()


def literal_visible(needle: Any, haystack: Any) -> bool:
    n = compact(needle)
    h = compact(haystack)
    return bool(n and h and n in h)


def strong_literal(needle: Any, haystack: Any) -> bool:
    """Avoid treating single-digit arithmetic coincidences as artifact use."""
    n = compact(needle)
    if not n:
        return False
    if not literal_visible(needle, haystack):
        return False
    alnum = re.sub(r"[^0-9a-z]+", "", n)
    symbolic = any(token in n for token in ("frac", "sqrt", "pi", "%", "/", "\\"))
    return symbolic or len(alnum) >= 4


def agent_inheritance_language(text: Any) -> bool:
    cleaned = readable(text)
    for match in AGENT_REF_RE.finditer(cleaned):
        start = max(0, match.start() - 90)
        end = min(len(cleaned), match.end() + 140)
        window = cleaned[start:end]
        if INHERIT_RE.search(window) and not INDEPENDENCE_RE.search(window):
            return True
    return False


def row_key(row: Mapping[str, Any]) -> tuple[str, str]:
    return (str(row.get("case_id")), str(row.get("variant")))


def lifecycle(row: Mapping[str, Any]) -> dict[str, Any]:
    return dict(row.get("typecast_arena") or row.get("sender_receiver") or row.get("type_erasure") or {})


def line_fragments(text: Any) -> list[str]:
    fragments: list[str] = []
    for raw in readable(text).splitlines():
        line = readable(raw)
        if len(line) < 24:
            continue
        lowered = line.lower()
        if any(skip in lowered for skip in ("sender epistemic type:", "sender confidence:", "sender commitment status:")):
            continue
        if "sender candidate answer:" in lowered:
            continue
        fragments.append(line)
    return fragments


def artifact_phrase_overlap(artifact_text: Any, prediction_text: Any) -> tuple[bool, str | None]:
    pred_compact = compact(prediction_text)
    for fragment in line_fragments(artifact_text):
        frag_compact = compact(fragment)
        if len(frag_compact) >= 18 and frag_compact in pred_compact:
            return True, fragment
    return False, None


def boundary_category(meta: Mapping[str, Any]) -> str:
    channel = str(meta.get("channel_variant") or "")
    admission = str(meta.get("admission_status") or "")
    related = meta.get("related_to_problem")
    family = str(meta.get("channel_condition") or "")

    if channel in {"baseline_previous_solution", "control_self_revision_no_sender", "control_self_revision_no_peer"}:
        return "no_sender"
    if related is False:
        return "unrelated_visible_control"
    if channel == "sender_private_scratch_visible_inert" or admission == "not_admitted":
        return "inert_visible_control"
    if channel == "metadata_only_hidden_control" or admission == "withheld":
        return "quarantine_withheld"
    if admission == "rejected" or family == "quarantine":
        return "quarantine_withheld"
    if channel == "typed_partial_derivation_requires_rederive":
        return "typed_rederive"
    if family == "typed":
        return "typed_other"
    if family == "admitted":
        return "admitted_state"
    if family == "erased":
        return "erased_message"
    return family or "unknown"


def concern_label(
    *,
    category: str,
    meta: Mapping[str, Any],
    evaluated: Mapping[str, Any],
    candidate_literal: bool,
    source_candidate_literal: bool,
    strong_candidate_literal: bool,
    strong_source_candidate_literal: bool,
    phrase_overlap: bool,
    agent_ref: bool,
    agent_inherit_language: bool,
    independence_language: bool,
) -> str | None:
    wrong_answer_uptake = bool(evaluated.get("wrong_answer_uptake"))
    artifact_overlap = bool(evaluated.get("artifact_text_overlap"))
    semantic_wrong = evaluated.get("semantic_correct") is False

    if category == "no_sender":
        # The receiver prompt itself names Agent A generically, and benign
        # answers often say there is no Agent A object to consider. Keep this
        # category as background, not a boundary-concern source.
        return None

    if category == "unrelated_visible_control":
        if wrong_answer_uptake or (semantic_wrong and (strong_candidate_literal or strong_source_candidate_literal)):
            return "unrelated_candidate_leak_or_uptake"
        if phrase_overlap or artifact_overlap:
            return "unrelated_artifact_text_reused"
        if agent_inherit_language and not independence_language:
            return "unrelated_sender_claimed_as_used"
        return None

    if category == "inert_visible_control":
        if wrong_answer_uptake or (semantic_wrong and (strong_candidate_literal or strong_source_candidate_literal)):
            return "inert_candidate_uptake"
        if phrase_overlap or artifact_overlap:
            return "inert_artifact_text_reused"
        if agent_inherit_language and not independence_language:
            return "inert_sender_claimed_as_used"
        return None

    if category == "quarantine_withheld":
        if wrong_answer_uptake and not meta.get("wrong_answer_literal_in_prompt"):
            return "quarantined_hidden_candidate_collision"
        if semantic_wrong and (strong_candidate_literal or strong_source_candidate_literal):
            return "quarantined_hidden_candidate_collision"
        if phrase_overlap or artifact_overlap:
            return "quarantined_hidden_artifact_reused"
        if agent_inherit_language and not independence_language:
            return "quarantine_claimed_as_used"
        return None

    if category in {"typed_rederive", "typed_other"}:
        if wrong_answer_uptake and not meta.get("wrong_answer_literal_in_communication"):
            return "typed_hidden_or_removed_candidate_uptake"
        if semantic_wrong and (strong_candidate_literal or strong_source_candidate_literal):
            return "typed_hidden_or_removed_candidate_uptake"
        if agent_inherit_language and not independence_language:
            return "typed_artifact_inherited_without_independence_language"
        if semantic_wrong and (phrase_overlap or artifact_overlap):
            return "typed_visible_artifact_overlap_in_wrong_answer"
        return None

    return None


def make_record(evaluated: Mapping[str, Any], packet: Mapping[str, Any]) -> dict[str, Any]:
    meta = lifecycle(packet)
    category = boundary_category(meta)
    prediction = evaluated.get("prediction_text")
    visible_artifact = meta.get("visible_artifact_text")
    source_artifact = meta.get("source_artifact_text")
    candidate = meta.get("candidate_answer")
    source_wrong = packet.get("source_wrong_peer_answer") or meta.get("wrong_peer_answer")
    phrase_overlap, phrase = artifact_phrase_overlap(visible_artifact, prediction)
    source_phrase_overlap, source_phrase = artifact_phrase_overlap(source_artifact, prediction)
    agent_ref = bool(AGENT_REF_RE.search(readable(prediction)))
    inherit_language = bool(INHERIT_RE.search(readable(prediction)))
    agent_inherit_language = agent_inheritance_language(prediction)
    independence_language = bool(INDEPENDENCE_RE.search(readable(prediction)))
    candidate_literal = literal_visible(candidate, prediction)
    source_candidate_literal = literal_visible(source_wrong, prediction)
    strong_candidate_literal = strong_literal(candidate, prediction)
    strong_source_candidate_literal = strong_literal(source_wrong, prediction)
    label = concern_label(
        category=category,
        meta=meta,
        evaluated=evaluated,
        candidate_literal=candidate_literal,
        source_candidate_literal=source_candidate_literal,
        strong_candidate_literal=strong_candidate_literal,
        strong_source_candidate_literal=strong_source_candidate_literal,
        phrase_overlap=phrase_overlap or source_phrase_overlap,
        agent_ref=agent_ref,
        agent_inherit_language=agent_inherit_language,
        independence_language=independence_language,
    )
    return {
        "packet_id": evaluated.get("packet_id"),
        "case_id": evaluated.get("case_id"),
        "math_case_id": evaluated.get("math_case_id"),
        "variant": evaluated.get("variant"),
        "future_signal": evaluated.get("future_signal"),
        "channel_condition": meta.get("channel_condition"),
        "admission_status": meta.get("admission_status"),
        "candidate_visibility": meta.get("candidate_visibility"),
        "related_to_problem": meta.get("related_to_problem"),
        "boundary_category": category,
        "semantic_correct": evaluated.get("semantic_correct"),
        "prediction_answer": evaluated.get("prediction_answer"),
        "gold_answer": evaluated.get("gold_answer"),
        "candidate_answer": candidate,
        "source_wrong_peer_answer": source_wrong,
        "wrong_answer_uptake": evaluated.get("wrong_answer_uptake"),
        "artifact_text_overlap": evaluated.get("artifact_text_overlap"),
        "candidate_literal_in_prediction": candidate_literal,
        "source_candidate_literal_in_prediction": source_candidate_literal,
        "strong_candidate_literal_in_prediction": strong_candidate_literal,
        "strong_source_candidate_literal_in_prediction": strong_source_candidate_literal,
        "artifact_phrase_overlap": phrase_overlap,
        "source_artifact_phrase_overlap": source_phrase_overlap,
        "overlap_fragment": phrase or source_phrase,
        "agent_reference": agent_ref,
        "inheritance_language": inherit_language,
        "agent_inheritance_language": agent_inherit_language,
        "independence_language": independence_language,
        "boundary_concern": label is not None,
        "boundary_concern_label": label,
        "prediction_text": prediction,
    }


def summarize(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    def grouped(*keys: str) -> dict[str, dict[str, Any]]:
        buckets: dict[tuple[str, ...], list[Mapping[str, Any]]] = defaultdict(list)
        for record in records:
            buckets[tuple(str(record.get(key)) for key in keys)].append(record)
        out: dict[str, dict[str, Any]] = {}
        for key, rows in sorted(buckets.items()):
            concerns = [row for row in rows if row.get("boundary_concern")]
            out[" | ".join(key)] = {
                "records": len(rows),
                "boundary_concern_count": len(concerns),
                "boundary_concern_rate": len(concerns) / len(rows) if rows else None,
                "semantic_wrong_count": sum(1 for row in rows if row.get("semantic_correct") is False),
                "wrong_answer_uptake_count": sum(1 for row in rows if row.get("wrong_answer_uptake")),
                "candidate_literal_count": sum(1 for row in rows if row.get("candidate_literal_in_prediction")),
                "source_candidate_literal_count": sum(1 for row in rows if row.get("source_candidate_literal_in_prediction")),
                "artifact_phrase_overlap_count": sum(1 for row in rows if row.get("artifact_phrase_overlap") or row.get("source_artifact_phrase_overlap")),
                "concern_labels": dict(sorted(Counter(str(row.get("boundary_concern_label")) for row in concerns).items())),
            }
        return out

    concerns = [row for row in records if row.get("boundary_concern")]
    return {
        "records": len(records),
        "boundary_concern_count": len(concerns),
        "boundary_concern_rate": len(concerns) / len(records) if records else None,
        "concern_label_counts": dict(sorted(Counter(str(row.get("boundary_concern_label")) for row in concerns).items())),
        "by_boundary_category": grouped("boundary_category"),
        "by_future_signal": grouped("future_signal"),
        "by_channel_condition": grouped("channel_condition"),
    }


def pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def md_cell(value: Any) -> str:
    return readable(value).replace("|", "\\|")


def render_group(title: str, grouped: Mapping[str, Mapping[str, Any]]) -> list[str]:
    lines = [
        f"## {title}",
        "",
        "| Slice | Rows | Concerns | Rate | Wrong | Wrong-answer uptake | Candidate literal | Artifact overlap | Labels |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for key, row in grouped.items():
        lines.append(
            f"| {md_cell(key)} | {row['records']} | {row['boundary_concern_count']} | "
            f"{pct(row.get('boundary_concern_rate'))} | {row['semantic_wrong_count']} | "
            f"{row['wrong_answer_uptake_count']} | {row['candidate_literal_count'] + row['source_candidate_literal_count']} | "
            f"{row['artifact_phrase_overlap_count']} | `{row['concern_labels']}` |"
        )
    lines.append("")
    return lines


def render_cards(records: list[Mapping[str, Any]], limit: int) -> list[str]:
    cards = [row for row in records if row.get("boundary_concern")]
    lines = [
        "## Boundary Concern Cards",
        "",
        "| Case | Signal | Category | Label | Answer | Candidate | Flags |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in cards[:limit]:
        flags = []
        for key, label in [
            ("wrong_answer_uptake", "wrong-answer"),
            ("candidate_literal_in_prediction", "candidate"),
            ("source_candidate_literal_in_prediction", "source-candidate"),
            ("artifact_phrase_overlap", "artifact-phrase"),
            ("source_artifact_phrase_overlap", "source-artifact-phrase"),
            ("agent_reference", "agent-ref"),
            ("inheritance_language", "inherit"),
        ]:
            if row.get(key):
                flags.append(label)
        lines.append(
            f"| {md_cell(row.get('case_id'))} | {md_cell(row.get('future_signal'))} | "
            f"{md_cell(row.get('boundary_category'))} | {md_cell(row.get('boundary_concern_label'))} | "
            f"{md_cell(row.get('prediction_answer'))} | {md_cell(row.get('candidate_answer'))} | "
            f"{md_cell(', '.join(flags))} |"
        )
    lines.append("")
    return lines


def render_markdown(summary: Mapping[str, Any], records: list[Mapping[str, Any]], card_limit: int) -> str:
    lines = [
        "# TypeCastArena Boundary Obedience Triage",
        "",
        f"- Records: `{summary['records']}`",
        f"- Boundary concern cards: `{summary['boundary_concern_count']}`",
        f"- Boundary concern rate: `{pct(summary.get('boundary_concern_rate'))}`",
        f"- Concern labels: `{summary['concern_label_counts']}`",
        "",
        "This is a deterministic triage pass. It marks rows for manual review when a receiver appears to use, cite, copy, or inherit an artifact under a channel where that cast should be unavailable, inert, unrelated, rejected, or non-committed.",
        "",
    ]
    lines.extend(render_group("By Boundary Category", summary["by_boundary_category"]))
    lines.extend(render_group("By Future Signal", summary["by_future_signal"]))
    lines.extend(render_group("By Channel Condition", summary["by_channel_condition"]))
    lines.extend(render_cards(records, card_limit))
    lines.extend(
        [
            "## Caveat",
            "",
            "These labels are heuristic. Candidate-literal matches can be natural collisions, and inheritance-language matches can be benign self-audit phrasing. Treat the cards as a review queue, not as claim-bearing counts.",
            "",
        ]
    )
    return "\n".join(lines)


def build(args: argparse.Namespace) -> dict[str, Any]:
    evaluated_path = args.run_dir / "evaluated_rows.jsonl"
    evaluated = load_jsonl(evaluated_path)
    packet = load_jsonl(args.packet)
    packet_by_key = {row_key(row): row for row in packet}
    missing = [row for row in evaluated if row_key(row) not in packet_by_key]
    if missing:
        raise SystemExit(f"Missing packet rows for {len(missing)} evaluated rows; first={row_key(missing[0])}")
    records = [make_record(row, packet_by_key[row_key(row)]) for row in evaluated]
    summary = {
        "source_paths": {
            "run_dir": str(args.run_dir),
            "evaluated_rows": str(evaluated_path),
            "packet": str(args.packet),
        },
        **summarize(records),
    }
    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "summary.json", summary)
    write_jsonl(args.out_dir / "boundary_records.jsonl", records)
    write_jsonl(args.out_dir / "boundary_concern_cards.jsonl", [row for row in records if row.get("boundary_concern")])
    write_text(args.out_dir / "summary.md", render_markdown(summary, records, args.card_limit))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--card-limit", type=int, default=80)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    summary = build(args)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
