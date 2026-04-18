"""Basic unit tests for the pipeline components (no OpenAI calls needed)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.config import RAW_DIR
from app.models import AnswerResult, Citation, DocumentMeta
from app.utils import doc_id_from_filename
from src.citations import format_citations_markdown, format_citations_text


def test_doc_id_deterministic():
    a = doc_id_from_filename("test.pdf")
    b = doc_id_from_filename("test.pdf")
    assert a == b
    assert len(a) == 12


def test_doc_id_unique():
    a = doc_id_from_filename("a.pdf")
    b = doc_id_from_filename("b.pdf")
    assert a != b


def test_document_meta_model():
    meta = DocumentMeta(
        doc_id="abc123", title="Test", filename="test.pdf", total_pages=5
    )
    assert meta.doc_id == "abc123"
    assert meta.total_pages == 5


def test_answer_result_defaults():
    ans = AnswerResult(question="test?", answer_text="answer")
    assert ans.confidence == "high"
    assert ans.citations == []
    assert ans.retrieved_nodes == 0


def test_citation_formatting():
    ans = AnswerResult(
        question="What is fair use?",
        answer_text="Fair use allows [1] limited use.",
        citations=[
            Citation(
                doc_title="Copyright Act",
                doc_id="abc123",
                page_numbers=[3, 4],
                node_id="node_001",
                excerpt="the fair use of a copyrighted work",
            )
        ],
    )
    text = format_citations_text(ans)
    assert "Copyright Act" in text
    assert "3, 4" in text

    md = format_citations_markdown(ans)
    assert "**[1]**" in md
    assert "`abc123`" in md


def test_citation_empty():
    ans = AnswerResult(question="x", answer_text="y", citations=[])
    assert "No citations" in format_citations_text(ans)
    assert "No citations" in format_citations_markdown(ans)
