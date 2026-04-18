from __future__ import annotations

import json
import urllib.request
from pathlib import Path

from app.config import PROCESSED_DIR, RAW_DIR
from app.models import DocumentMeta

from .parse_pdf import parse_all_pdfs

SAMPLE_CORPUS = [
    {
        "url": "https://www.copyright.gov/title17/92chap1.pdf",
        "filename": "copyright_act_chapter1.pdf",
        "title": "Copyright Act - Chapter 1: Subject Matter and Scope",
    },
    {
        "url": "https://www.govinfo.gov/content/pkg/USCODE-2023-title42/pdf/USCODE-2023-title42-chap21-subchapI-sec1983.pdf",
        "title": "42 U.S.C. § 1983 - Civil Action for Deprivation of Rights",
        "filename": "usc_42_1983.pdf",
    },
]


def download_corpus(target_dir: Path | None = None) -> list[Path]:
    """Download sample legal PDFs. Returns list of downloaded file paths."""
    out_dir = target_dir or RAW_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []

    for source in SAMPLE_CORPUS:
        dest = out_dir / source["filename"]
        if dest.exists():
            paths.append(dest)
            continue
        try:
            req = urllib.request.Request(
                source["url"],
                headers={"User-Agent": "legal-engine/0.1 (educational-prototype)"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                dest.write_bytes(resp.read())
            paths.append(dest)
            print(f"Downloaded: {source['filename']}")
        except Exception as e:
            print(f"Warning: could not download {source['filename']}: {e}")

    return paths


def run_ingestion(pdf_dir: Path | None = None):
    """Full ingestion pipeline: parse PDFs, save metadata."""
    source_dir = pdf_dir or RAW_DIR

    if not list(source_dir.glob("*.pdf")):
        print("No PDFs found. Downloading sample corpus...")
        download_corpus(source_dir)

    docs, doc_metas = parse_all_pdfs(source_dir)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = PROCESSED_DIR / "document_metadata.json"
    meta_path.write_text(
        json.dumps([m.model_dump() for m in doc_metas], indent=2)
    )

    print(f"Ingested {len(doc_metas)} documents ({len(docs)} pages total)")
    return docs, doc_metas
