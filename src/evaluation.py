from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from app.models import AnswerResult

TEST_CASES = [
    {
        "question": "What are the four factors considered in a fair use analysis?",
        "expected_doc_keywords": ["copyright", "fair use"],
        "expected_answer_keywords": ["purpose", "nature", "amount", "market"],
        "expected_confidence": "high",
        "should_decline": False,
    },
    {
        "question": "Under what circumstances can a person sue a state official for civil rights violations?",
        "expected_doc_keywords": ["1983", "civil rights"],
        "expected_answer_keywords": ["color of law", "deprivation"],
        "expected_confidence": "high",
        "should_decline": False,
    },
    {
        "question": "Does fair use apply to commercial uses of copyrighted material?",
        "expected_doc_keywords": ["copyright", "fair use"],
        "expected_answer_keywords": ["commercial", "purpose"],
        "expected_confidence": "high",
        "should_decline": False,
    },
    {
        "question": "What is the penalty for insider trading under SEC regulations?",
        "expected_doc_keywords": [],
        "expected_answer_keywords": [],
        "expected_confidence": "insufficient",
        "should_decline": True,
    },
    {
        "question": "What exclusive rights does a copyright owner have?",
        "expected_doc_keywords": ["copyright", "exclusive"],
        "expected_answer_keywords": ["reproduce", "derivative", "distribute"],
        "expected_confidence": "high",
        "should_decline": False,
    },
]


@dataclass
class EvalResult:
    question: str
    has_citations: bool = False
    keyword_recall: float = 0.0
    confidence_match: bool = False
    decline_correct: bool = False
    score: float = 0.0


def evaluate_single(tc: dict, answer: AnswerResult) -> EvalResult:
    result = EvalResult(question=tc["question"])

    result.has_citations = len(answer.citations) > 0

    expected_kw = tc.get("expected_answer_keywords", [])
    if expected_kw:
        text_lower = answer.answer_text.lower()
        hits = sum(1 for kw in expected_kw if kw.lower() in text_lower)
        result.keyword_recall = hits / len(expected_kw)

    expected_conf = tc.get("expected_confidence", "")
    if expected_conf:
        result.confidence_match = answer.confidence == expected_conf

    if tc.get("should_decline"):
        result.decline_correct = answer.confidence in ("insufficient", "low")

    components = []
    if not tc.get("should_decline"):
        components.append(1.0 if result.has_citations else 0.0)
    if expected_kw:
        components.append(result.keyword_recall)
    if expected_conf:
        components.append(1.0 if result.confidence_match else 0.0)
    if tc.get("should_decline"):
        components.append(1.0 if result.decline_correct else 0.0)

    result.score = sum(components) / len(components) if components else 0.0
    return result


def run_evaluation(
    query_fn,
    test_cases: list[dict] | None = None,
) -> dict:
    """Run the evaluation harness.

    query_fn: callable(question: str) -> AnswerResult
    """
    cases = test_cases or TEST_CASES
    results = []

    for tc in cases:
        answer = query_fn(tc["question"])
        result = evaluate_single(tc, answer)
        results.append(result)

    avg = sum(r.score for r in results) / len(results) if results else 0.0

    summary = {
        "total": len(results),
        "average_score": round(avg, 3),
        "results": [
            {
                "question": r.question,
                "score": round(r.score, 3),
                "has_citations": r.has_citations,
                "keyword_recall": round(r.keyword_recall, 3),
                "confidence_match": r.confidence_match,
                "decline_correct": r.decline_correct,
            }
            for r in results
        ],
    }
    return summary


def print_eval_report(summary: dict) -> None:
    print(f"\n{'='*60}")
    print("EVALUATION REPORT")
    print(f"{'='*60}")
    print(f"Total: {summary['total']} | Average score: {summary['average_score']:.1%}")
    print(f"{'-'*60}")

    for r in summary["results"]:
        status = "PASS" if r["score"] >= 0.5 else "FAIL"
        print(f"\n[{status}] {r['question'][:70]}")
        print(f"  Score: {r['score']:.1%} | Citations: {r['has_citations']} | KW recall: {r['keyword_recall']:.0%}")

    print(f"\n{'='*60}")
