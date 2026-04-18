from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import INDEX_DIR, RAW_DIR, TOP_K
from app.prompts import PROMPT_VERSION, format_context
from app.utils import init_llama_settings
from src.citations import format_citations_markdown
from src.chunking import build_hierarchy, get_leaves
from src.indexing import build_index, load_index
from src.ingest import run_ingestion
from src.qa import answer_question
from src.retrieval import get_retriever, retrieve

st.set_page_config(page_title="Legal Engine", layout="wide")
st.title("Legal Research Engine")
st.caption(f"Prompt charter v{PROMPT_VERSION} · Hierarchical RAG with auto-merging retrieval")

try:
    init_llama_settings()
except EnvironmentError as e:
    st.error(str(e))
    st.stop()


# --- Sidebar: corpus status and controls ---
with st.sidebar:
    st.header("Corpus")

    pdf_files = list(RAW_DIR.glob("*.pdf")) if RAW_DIR.exists() else []
    index_exists = INDEX_DIR.exists() and any(INDEX_DIR.iterdir())

    st.metric("PDFs loaded", len(pdf_files))
    st.metric("Index ready", "Yes" if index_exists else "No")

    if pdf_files and st.button("Build index"):
        with st.spinner("Parsing, chunking, and indexing..."):
            docs, metas = run_ingestion()
            all_nodes = build_hierarchy(docs)
            leaves = get_leaves(all_nodes)
            build_index(all_nodes, leaves)
        st.success(f"Indexed {len(metas)} docs ({len(leaves)} leaf chunks)")
        st.rerun()

    st.divider()
    st.header("Settings")
    top_k = st.slider("Retrieval top-k", 1, 20, TOP_K)

# --- Main panel ---
if not index_exists:
    st.info(
        "No index found. Add PDFs to data/raw/ and click 'Build index' in the sidebar."
    )
    st.stop()

question = st.text_input(
    "Ask a legal research question:",
    placeholder="e.g. What are the four factors of fair use?",
)

if question:
    try:
        index = load_index()
    except FileNotFoundError as e:
        st.error(str(e))
        st.stop()

    retriever = get_retriever(index, top_k=top_k)

    with st.spinner("Retrieving relevant passages..."):
        nodes = retrieve(retriever, question)

    if not nodes:
        st.warning("No relevant passages found. Try a different question or re-index.")
        st.stop()

    with st.spinner("Generating answer..."):
        try:
            answer = answer_question(question, nodes)
        except EnvironmentError as e:
            st.error(str(e))
            st.stop()

    # Answer display
    confidence_colors = {
        "high": "green", "medium": "orange", "low": "red", "insufficient": "red"
    }
    color = confidence_colors.get(answer.confidence, "gray")

    st.subheader("Answer")
    st.markdown(f"**Confidence:** :{color}[{answer.confidence}]")
    st.markdown(answer.answer_text)

    # Citations
    st.subheader("Citations")
    st.markdown(format_citations_markdown(answer))

    # Retrieved context (expandable)
    with st.expander("Retrieved context (raw passages)", expanded=False):
        context_str = format_context(nodes)
        st.text(context_str)

    # Retrieval scores
    with st.expander("Retrieval scores", expanded=False):
        for i, n in enumerate(nodes, 1):
            meta = n.node.metadata or {}
            st.text(
                f"[{i}] score={n.score:.4f} | "
                f"{meta.get('title', '?')} p.{meta.get('page_number', '?')} | "
                f"node={n.node.node_id[:12]}..."
            )
