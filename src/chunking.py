from __future__ import annotations

from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.schema import Document as LlamaDocument, BaseNode

from app.config import CHILD_CHUNK_SIZE, CHUNK_OVERLAP, PARENT_CHUNK_SIZE


def build_hierarchy(
    documents: list[LlamaDocument],
    parent_chunk_size: int = PARENT_CHUNK_SIZE,
    child_chunk_size: int = CHILD_CHUNK_SIZE,
) -> list[BaseNode]:
    """Build a two-level node hierarchy from documents.

    Returns all nodes (parents + children). Use get_leaf_nodes() to get only
    the child nodes for indexing.
    """
    parser = HierarchicalNodeParser.from_defaults(
        chunk_sizes=[parent_chunk_size, child_chunk_size],
    )
    all_nodes = parser.get_nodes_from_documents(documents)
    return all_nodes


def get_leaves(all_nodes: list[BaseNode]) -> list[BaseNode]:
    """Extract leaf (child) nodes for vector indexing."""
    return get_leaf_nodes(all_nodes)
