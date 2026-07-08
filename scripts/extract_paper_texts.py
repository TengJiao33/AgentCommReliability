from __future__ import annotations

import json
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "papers"
TEXT_DIR = PAPER_DIR / "text"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_record(path: Path) -> dict[str, object]:
    stat = path.stat()
    return {
        "bytes": stat.st_size,
        "source_mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        "source_sha256": _file_sha256(path),
    }


def _metadata(path: Path) -> dict[str, object]:
    reader = PdfReader(str(path))
    meta = reader.metadata or {}
    return {
        "pages": len(reader.pages),
        "title": str(meta.get("/Title") or "").strip(),
        "author": str(meta.get("/Author") or "").strip(),
        "subject": str(meta.get("/Subject") or "").strip(),
    }


def _extract_pages(path: Path) -> list[str]:
    pages: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
            pages.append(text.strip())
    return pages


def _cached_record(path: Path) -> dict[str, object] | None:
    out_path = TEXT_DIR / f"{path.stem}.txt"
    page_index_path = TEXT_DIR / f"{path.stem}.pages.json"
    if not out_path.exists() or not page_index_path.exists():
        return None

    meta = _metadata(path)
    page_rows = json.loads(page_index_path.read_text(encoding="utf-8"))
    return {
        "pdf": path.name,
        "text": out_path.name,
        "pages_json": page_index_path.name,
        **_source_record(path),
        **meta,
        "extracted_chars": sum(int(row.get("chars", 0)) for row in page_rows),
        "cached": True,
    }


def extract_one(path: Path, *, force: bool = False) -> dict[str, object]:
    if not force:
        cached = _cached_record(path)
        if cached is not None:
            return cached

    meta = _metadata(path)
    pages = _extract_pages(path)
    out_path = TEXT_DIR / f"{path.stem}.txt"
    page_index_path = TEXT_DIR / f"{path.stem}.pages.json"

    blocks = [
        f"# source_pdf: {path.name}",
        f"# extracted_at_utc: {_utc_now()}",
        f"# pages: {meta['pages']}",
        f"# title: {meta['title']}",
        "",
    ]
    page_rows = []
    for idx, text in enumerate(pages, start=1):
        blocks.append(f"\n\n===== PAGE {idx} =====\n")
        blocks.append(text)
        page_rows.append({"page": idx, "chars": len(text)})

    out_path.write_text("\n".join(blocks), encoding="utf-8")
    page_index_path.write_text(
        json.dumps(page_rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "pdf": path.name,
        "text": out_path.name,
        "pages_json": page_index_path.name,
        **_source_record(path),
        **meta,
        "extracted_chars": sum(len(page) for page in pages),
        "cached": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract text from papers/*.pdf into papers/text with a reusable manifest."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-extract PDFs even when matching text and page index files already exist.",
    )
    args = parser.parse_args()

    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(PAPER_DIR.glob("*.pdf"))
    manifest = [extract_one(path, force=args.force) for path in pdfs]
    manifest_path = TEXT_DIR / "manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "generated_at_utc": _utc_now(),
                "source_dir": str(PAPER_DIR),
                "text_dir": str(TEXT_DIR),
                "force": args.force,
                "papers": manifest,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
