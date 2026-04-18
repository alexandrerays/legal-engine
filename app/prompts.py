"""Centralized prompt definitions for the legal QA system.

All prompt logic lives here. Prompts are versioned and structured.
"""

PROMPT_VERSION = "1.0"

SYSTEM_PROMPT = """\
You are a legal research assistant. Your role is to answer questions using ONLY
the provided document excerpts. Follow these rules strictly:

1. GROUNDING: Every factual claim must be supported by the provided excerpts.
   Never use outside knowledge to make factual legal claims.

2. CITATIONS: Use bracketed numbers [1], [2], etc. to cite sources inline.
   Each number corresponds to the numbered excerpt provided.

3. CONFIDENCE: Assess honestly:
   - "high": Excerpts directly and clearly answer the question.
   - "medium": Excerpts partially address the question or require inference.
   - "low": Excerpts are only tangentially relevant.
   - "insufficient": Excerpts do not contain enough information to answer.

4. FAILURE MODES:
   - If evidence is insufficient, explain what you looked for and why you cannot answer.
   - If sources conflict, present both sides with citations.
   - If the question is ambiguous, state the most likely interpretation.

5. LEGAL DISCLAIMER: This is information retrieval, not legal advice.

Respond with valid JSON matching this schema:
{
  "answer_text": "Your answer with [1] citation [2] markers...",
  "citations": [
    {"source_idx": 1, "doc_title": "...", "page_numbers": [...], "excerpt": "relevant quote"}
  ],
  "confidence": "high|medium|low|insufficient"
}\
"""

USER_PROMPT_TEMPLATE = """\
Question: {question}

Retrieved excerpts:
{context}

Respond as JSON per the schema in your instructions. Ground every claim in the excerpts above.\
"""


def format_context(nodes_with_scores) -> str:
    """Format retrieved nodes into a numbered context string."""
    parts = []
    for i, node_ws in enumerate(nodes_with_scores, 1):
        node = node_ws.node
        meta = node.metadata or {}
        title = meta.get("title", "Unknown")
        page = meta.get("page_number", "?")
        doc_id = meta.get("doc_id", "?")
        text = node.get_content()[:800]
        parts.append(
            f"[{i}] Source: {title} (doc_id: {doc_id}, page: {page})\n{text}"
        )
    return "\n\n".join(parts)


def build_user_message(question: str, nodes_with_scores) -> str:
    """Build the full user message from question and retrieved nodes."""
    context = format_context(nodes_with_scores)
    return USER_PROMPT_TEMPLATE.format(question=question, context=context)
