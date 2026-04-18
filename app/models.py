from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentMeta(BaseModel):
    doc_id: str
    title: str
    source_url: str = ""
    filename: str = ""
    total_pages: int = 0


class Citation(BaseModel):
    doc_title: str
    doc_id: str
    page_numbers: list[int] = Field(default_factory=list)
    node_id: str = ""
    excerpt: str = ""


class AnswerResult(BaseModel):
    question: str
    answer_text: str
    citations: list[Citation] = Field(default_factory=list)
    confidence: str = "high"  # high | medium | low | insufficient
    retrieved_nodes: int = 0
