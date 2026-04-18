from __future__ import annotations

from app.models import AnswerResult, Citation


def format_citations_text(answer: AnswerResult) -> str:
    """Format citations into a human-readable text block."""
    if not answer.citations:
        return "No citations available."

    lines = []
    for i, c in enumerate(answer.citations, 1):
        pages = ", ".join(str(p) for p in c.page_numbers) if c.page_numbers else "N/A"
        lines.append(f"[{i}] {c.doc_title}")
        lines.append(f"    Document ID: {c.doc_id}")
        lines.append(f"    Page(s): {pages}")
        if c.node_id:
            lines.append(f"    Node ID: {c.node_id}")
        if c.excerpt:
            excerpt = c.excerpt[:200] + "..." if len(c.excerpt) > 200 else c.excerpt
            lines.append(f'    Excerpt: "{excerpt}"')
        lines.append("")
    return "\n".join(lines)


def format_citations_markdown(answer: AnswerResult) -> str:
    """Format citations as Markdown for Streamlit display."""
    if not answer.citations:
        return "*No citations available.*"

    parts = []
    for i, c in enumerate(answer.citations, 1):
        pages = ", ".join(str(p) for p in c.page_numbers) if c.page_numbers else "N/A"
        excerpt = ""
        if c.excerpt:
            short = c.excerpt[:200] + "…" if len(c.excerpt) > 200 else c.excerpt
            excerpt = f'\n> *"{short}"*'
        parts.append(
            f"**[{i}]** {c.doc_title}  \n"
            f"Doc ID: `{c.doc_id}` · Page(s): {pages}"
            f"{excerpt}"
        )
    return "\n\n".join(parts)
