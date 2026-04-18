from __future__ import annotations

import json
import re

from llama_index.core.schema import NodeWithScore
from openai import OpenAI

from app.config import LLM_MODEL, LLM_TEMPERATURE
from app.models import AnswerResult, Citation
from app.prompts import SYSTEM_PROMPT, build_user_message
from app.utils import get_openai_key


def _parse_response(raw: str, nodes: list[NodeWithScore]) -> dict:
    """Extract JSON from LLM response text."""
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("No JSON found in LLM response")


def _build_citations(
    parsed: dict, nodes: list[NodeWithScore]
) -> list[Citation]:
    """Convert parsed citation dicts into Citation models with real metadata."""
    citations = []
    for c in parsed.get("citations", []):
        source_idx = c.get("source_idx", 0)
        node_meta = {}
        node_id = ""
        if 1 <= source_idx <= len(nodes):
            node_meta = nodes[source_idx - 1].node.metadata or {}
            node_id = nodes[source_idx - 1].node.node_id

        page_raw = c.get("page_numbers", node_meta.get("page_number", []))
        if isinstance(page_raw, int):
            page_numbers = [page_raw]
        elif isinstance(page_raw, list):
            page_numbers = [int(p) for p in page_raw]
        else:
            page_numbers = []

        citations.append(Citation(
            doc_title=c.get("doc_title", node_meta.get("title", "Unknown")),
            doc_id=node_meta.get("doc_id", ""),
            page_numbers=page_numbers,
            node_id=node_id,
            excerpt=c.get("excerpt", ""),
        ))
    return citations


def answer_question(
    question: str,
    nodes: list[NodeWithScore],
    model: str | None = None,
) -> AnswerResult:
    """Generate a grounded answer from retrieved nodes."""
    if not nodes:
        return AnswerResult(
            question=question,
            answer_text="No relevant documents were retrieved for this question. "
            "Please ensure the corpus has been ingested and indexed.",
            confidence="insufficient",
        )

    user_message = build_user_message(question, nodes)

    client = OpenAI(api_key=get_openai_key())
    response = client.chat.completions.create(
        model=model or LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    raw_text = response.choices[0].message.content or ""

    try:
        parsed = _parse_response(raw_text, nodes)
    except (json.JSONDecodeError, ValueError):
        return AnswerResult(
            question=question,
            answer_text=raw_text,
            confidence="low",
            retrieved_nodes=len(nodes),
        )

    citations = _build_citations(parsed, nodes)

    return AnswerResult(
        question=question,
        answer_text=parsed.get("answer_text", raw_text),
        citations=citations,
        confidence=parsed.get("confidence", "medium"),
        retrieved_nodes=len(nodes),
    )
