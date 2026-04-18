"""Run a sample query against the indexed corpus.

Usage:
    python examples/run_example.py "What are the four factors of fair use?"
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.citations import format_citations_text
from src.indexing import load_index
from src.qa import answer_question
from src.retrieval import get_retriever, retrieve


def main():
    if len(sys.argv) < 2:
        print("Usage: python examples/run_example.py 'your question here'")
        sys.exit(1)

    question = sys.argv[1]
    print(f"Question: {question}\n")

    try:
        index = load_index()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Run the Streamlit app first and build the index from the sidebar.")
        sys.exit(1)

    retriever = get_retriever(index)
    nodes = retrieve(retriever, question)
    print(f"Retrieved {len(nodes)} passages.\n")

    if not nodes:
        print("No relevant passages found.")
        sys.exit(0)

    answer = answer_question(question, nodes)

    print(f"{'='*60}")
    print(f"ANSWER (confidence: {answer.confidence})")
    print(f"{'='*60}")
    print(answer.answer_text)
    print(f"\n{'─'*60}")
    print("CITATIONS:")
    print(format_citations_text(answer))


if __name__ == "__main__":
    main()
