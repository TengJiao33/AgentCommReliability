#!/usr/bin/env python3
"""Run the PACT public-state field packet against an OpenAI-compatible endpoint."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


DEFAULT_PACKET = Path("experiments/20260615-local-pact-public-state-field-packet/field_packet.jsonl")
DEFAULT_OUT_ROOT = Path("experiments/20260615-local-pact-public-state-field-packet/model-runs")


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def append_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def chat_completion(
    *,
    base_url: str,
    model: str,
    api_key: str,
    prompt: str,
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> Tuple[str, Dict[str, Any]]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {detail}") from exc
    data = json.loads(raw)
    return data["choices"][0]["message"]["content"], data.get("usage") or {}


def selected_rows(args: argparse.Namespace) -> List[Dict[str, Any]]:
    rows = load_jsonl(args.packet)
    if args.conditions:
        allowed = set(args.conditions)
        rows = [row for row in rows if row.get("condition") in allowed]
    if args.source_runs:
        allowed = set(args.source_runs)
        rows = [row for row in rows if row.get("source_run") in allowed]
    if args.sample_indices:
        allowed = {int(value) for value in args.sample_indices}
        rows = [row for row in rows if int(row.get("sample_index")) in allowed]
    if args.limit is not None:
        rows = rows[: args.limit]
    return rows


def existing_packet_ids(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    return {
        str(row["packet_id"])
        for row in load_jsonl(path)
        if row.get("packet_id") is not None
    }


def resolve_api_key(args: argparse.Namespace) -> str:
    if args.api_key:
        return args.api_key
    if args.api_key_env:
        return os.environ.get(args.api_key_env, "")
    return os.environ.get("OPENAI_API_KEY", "")


def build_manifest(
    *,
    args: argparse.Namespace,
    run_id: str,
    selected_count: int,
    skipped_count: int,
    completed_count: int,
    failed_count: int,
) -> Dict[str, Any]:
    return {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "packet": str(args.packet),
        "base_url": args.base_url,
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "timeout": args.timeout,
        "selected_count": selected_count,
        "skipped_count": skipped_count,
        "completed_count": completed_count,
        "failed_count": failed_count,
        "conditions": args.conditions,
        "source_runs": args.source_runs,
        "sample_indices": args.sample_indices,
        "limit": args.limit,
        "outputs": str(args.out_dir / "outputs.jsonl"),
        "failures": str(args.out_dir / "failures.jsonl"),
        "note": "Run outputs can be scored with scripts/evaluate_pact_public_state_field_packet.py --prediction-source outputs.",
    }


def run(args: argparse.Namespace) -> Dict[str, Any]:
    if not args.base_url or not args.model:
        raise SystemExit("--base-url and --model are required")
    api_key = resolve_api_key(args)
    if not api_key:
        raise SystemExit("No API key supplied. Use --api-key, --api-key-env, or OPENAI_API_KEY.")

    if args.out_dir is None:
        safe_model = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in args.model)
        run_id = datetime.now().strftime(f"%Y%m%d-%H%M%S-{safe_model}")
        args.out_dir = DEFAULT_OUT_ROOT / run_id
    else:
        run_id = args.out_dir.name
    args.out_dir.mkdir(parents=True, exist_ok=True)
    outputs_path = args.out_dir / "outputs.jsonl"
    failures_path = args.out_dir / "failures.jsonl"

    rows = selected_rows(args)
    already_done = existing_packet_ids(outputs_path) if args.resume else set()
    completed = 0
    failed = 0
    skipped = 0
    for index, row in enumerate(rows, start=1):
        packet_id = str(row["packet_id"])
        if packet_id in already_done:
            skipped += 1
            continue
        started = time.time()
        try:
            output, usage = chat_completion(
                base_url=args.base_url,
                model=args.model,
                api_key=api_key,
                prompt=str(row["prompt"]),
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                timeout=args.timeout,
            )
            append_jsonl(outputs_path, [{
                "packet_id": packet_id,
                "sample_index": row.get("sample_index"),
                "source_run": row.get("source_run"),
                "condition": row.get("condition"),
                "output": output.strip(),
                "raw_output": output,
                "usage": usage,
                "latency_seconds": round(time.time() - started, 3),
                "model": args.model,
            }])
            completed += 1
        except Exception as exc:  # noqa: BLE001 - preserve endpoint failure detail.
            append_jsonl(failures_path, [{
                "packet_id": packet_id,
                "sample_index": row.get("sample_index"),
                "source_run": row.get("source_run"),
                "condition": row.get("condition"),
                "error": str(exc),
                "model": args.model,
            }])
            failed += 1
            if not args.keep_going:
                break
        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)
        if args.progress_every and (completed + failed + skipped) % args.progress_every == 0:
            print(
                json.dumps(
                    {
                        "seen": index,
                        "completed": completed,
                        "failed": failed,
                        "skipped": skipped,
                    },
                    ensure_ascii=False,
                )
            )

    manifest = build_manifest(
        args=args,
        run_id=run_id,
        selected_count=len(rows),
        skipped_count=skipped,
        completed_count=completed,
        failed_count=failed,
    )
    write_json(args.out_dir / "manifest.json", manifest)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--api-key")
    parser.add_argument("--api-key-env", default="OPENAI_API_KEY")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--conditions", nargs="*")
    parser.add_argument("--source-runs", nargs="*")
    parser.add_argument("--sample-indices", nargs="*", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--keep-going", action="store_true")
    parser.add_argument("--sleep-seconds", type=float, default=0.0)
    parser.add_argument("--progress-every", type=int, default=25)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    manifest = run(args)
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
