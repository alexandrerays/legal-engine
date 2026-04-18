from __future__ import annotations

from pathlib import Path

from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document as LlamaDocument

from app.models import DocumentMeta
from app.utils import doc_id_from_filename


def parse_pdf(pdf_path: Path) -> list[LlamaDocument]:
    """Parse a single PDF into LlamaIndex Documents (one per page)."""
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = SimpleDirectoryReader(input_files=[str(pdf_path)])
    docs = reader.load_data()

    filename = pdf_path.name
    d_id = doc_id_from_filename(filename)

    for i, doc in enumerate(docs):
        doc.metadata["doc_id"] = d_id
        doc.metadata["filename"] = filename
        doc.metadata["title"] = pdf_path.stem.replace("_", " ").title()
        doc.metadata["page_number"] = doc.metadata.get("page_label", i + 1)
        doc.metadata["source_type"] = "pdf"

    return docs


def parse_all_pdfs(pdf_dir: Path) -> tuple[list[LlamaDocument], list[DocumentMeta]]:
    """Parse all PDFs in a directory. Returns (documents, metadata_list)."""
    if not pdf_dir.exists():
        raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

    pdf_files = sorted(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(f"No PDF files found in {pdf_dir}")

    all_docs: list[LlamaDocument] = []
    all_meta: list[DocumentMeta] = []

    for pdf_path in pdf_files:
        try:
            docs = parse_pdf(pdf_path)
            all_docs.extend(docs)

            meta = DocumentMeta(
                doc_id=doc_id_from_filename(pdf_path.name),
                title=pdf_path.stem.replace("_", " ").title(),
                filename=pdf_path.name,
                total_pages=len(docs),
            )
            all_meta.append(meta)
        except Exception as e:
            print(f"Warning: failed to parse {pdf_path.name}: {e}")

    return all_docs, all_meta
