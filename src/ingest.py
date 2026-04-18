from __future__ import annotations

import json
from pathlib import Path

from app.config import PROCESSED_DIR, RAW_DIR
from app.models import DocumentMeta

from .parse_pdf import parse_all_pdfs


def run_ingestion(pdf_dir: Path | None = None):
    """Full ingestion pipeline: parse PDFs, save metadata."""
    source_dir = pdf_dir or RAW_DIR
    docs, doc_metas = parse_all_pdfs(source_dir)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    meta_path = PROCESSED_DIR / "document_metadata.json"
    meta_path.write_text(
        json.dumps([m.model_dump() for m in doc_metas], indent=2)
    )

    print(f"Ingested {len(doc_metas)} documents ({len(docs)} pages total)")
    return docs, doc_metas
