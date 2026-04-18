from __future__ import annotations

from llama_index.core import VectorStoreIndex
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.schema import NodeWithScore

from app.config import TOP_K


def get_retriever(
    index: VectorStoreIndex,
    top_k: int = TOP_K,
) -> AutoMergingRetriever:
    """Create an AutoMergingRetriever over the hierarchical index.

    Retrieval starts from leaf (child) chunks. When enough children from the
    same parent are retrieved, AutoMergingRetriever merges them into the
    parent node automatically, providing broader context to the LLM.
    """
    base_retriever = index.as_retriever(similarity_top_k=top_k)

    retriever = AutoMergingRetriever(
        vector_retriever=base_retriever,
        storage_context=index.storage_context,
        simple_ratio_thresh=0.4,
    )
    return retriever


def retrieve(
    retriever: AutoMergingRetriever,
    query: str,
) -> list[NodeWithScore]:
    """Run retrieval for a query. Returns scored nodes."""
    return retriever.retrieve(query)
