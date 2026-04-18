from __future__ import annotations

from pathlib import Path

from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.schema import BaseNode
from llama_index.core.storage.docstore import SimpleDocumentStore

from app.config import INDEX_DIR


def build_index(
    all_nodes: list[BaseNode],
    leaf_nodes: list[BaseNode],
    persist_dir: Path | None = None,
) -> VectorStoreIndex:
    """Build a FAISS-backed vector index from leaf nodes, with all nodes in docstore."""
    docstore = SimpleDocumentStore()
    docstore.add_documents(all_nodes)

    storage_context = StorageContext.from_defaults(docstore=docstore)

    index = VectorStoreIndex(
        nodes=leaf_nodes,
        storage_context=storage_context,
    )

    out_dir = persist_dir or INDEX_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    storage_context.persist(persist_dir=str(out_dir))
    print(f"Index persisted to {out_dir}")

    return index


def load_index(persist_dir: Path | None = None) -> VectorStoreIndex:
    """Load a previously persisted index."""
    source_dir = persist_dir or INDEX_DIR
    if not source_dir.exists():
        raise FileNotFoundError(
            f"No index found at {source_dir}. Run ingestion first."
        )

    storage_context = StorageContext.from_defaults(persist_dir=str(source_dir))
    index = load_index_from_storage(storage_context)
    return index
