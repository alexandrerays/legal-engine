# Project Overview

This repository contains a local legal research prototype built in Python with a Streamlit UI.

Core goals:
- Ingest a small corpus of public legal PDFs
- Parse and preserve source metadata
- Build hierarchical chunks using LlamaIndex `HierarchicalNodeParser`
- Retrieve with FAISS-based vector search
- Expand context automatically using LlamaIndex `AutoMergingRetriever`
- Generate grounded answers with citations
- Run fully locally except for optional OpenAI API calls for embeddings and/or answer generation

This is a compact prototype for legal QA and legal research. Prioritize correctness, grounded citations, traceability, and simplicity over feature breadth.

# Architecture Rules

- Build everything locally.
- Use Python only.
- Use Streamlit for the UI.
- Use FAISS for vector similarity search.
- Use LlamaIndex `HierarchicalNodeParser` plus `AutoMergingRetriever` for parent-child hierarchical retrieval.
- Use OpenAI API only when necessary, mainly for embeddings and answer generation.
- Do not introduce unnecessary external services, databases, message queues, or cloud infrastructure.
- Keep the implementation compact and easy to run from a fresh local environment.

# Product Requirements

The system must support:
- loading a small legal corpus from public PDFs
- preserving document metadata and traceable document IDs
- hierarchical chunking
- retrieval over the corpus
- grounded answers with explicit citations
- at least one graceful failure mode such as insufficient evidence
- a lightweight evaluation harness
- a concise README and design note

# Preferred Project Structure

Use this structure unless there is a clear reason to improve it:

.
├── app/
│   ├── ui.py
│   ├── config.py
│   ├── models.py
│   ├── prompts.py
│   └── utils.py
├── src/
│   ├── ingest.py
│   ├── parse_pdf.py
│   ├── chunking.py
│   ├── indexing.py
│   ├── retrieval.py
│   ├── qa.py
│   ├── citations.py
│   └── evaluation.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── indexes/
├── tests/
├── examples/
├── README.md
├── requirements.txt
├── .env.example
└── CLAUDE.md

# Coding Principles

- Favor small, explicit modules over abstractions.
- Keep functions short and easy to test.
- Use type hints throughout.
- Use dataclasses or Pydantic models for structured records when helpful.
- Prefer simple synchronous code unless async clearly adds value.
- Avoid over-engineering.
- Minimize framework magic.
- Use clear names for chunk IDs, document IDs, page ranges, and citation records.
- Every important claim shown to the user must be traceable to retrieved source text.

# Retrieval and Chunking Rules

- Hierarchical retrieval is required.
- Use `HierarchicalNodeParser` to create multi-level chunks.
- Use `AutoMergingRetriever` so retrieval starts from smaller chunks and expands to larger parent context automatically.
- Persist enough metadata to trace every retrieved node back to source document and page numbers.
- Keep chunking configuration explicit and easy to adjust.
- Prefer a simple chunk hierarchy such as larger parent chunks and smaller child chunks.
- Record chunk sizes and overlap in config, not inline magic numbers.
- Keep citation fidelity more important than maximizing recall.

# FAISS Rules

- Use FAISS as the local vector index.
- Keep metadata in local Python or JSON structures alongside the FAISS index.
- Do not add a full vector database unless absolutely necessary.
- The indexing pipeline must be reproducible from raw documents.

# OpenAI Usage Rules

- OpenAI API is optional and should be isolated behind a small client wrapper.
- Never hardcode API keys.
- Read secrets from environment variables only.
- Keep prompts versioned and explicit.
- If OpenAI is unavailable, fail clearly and gracefully.
- Prefer deterministic settings for evaluation and reproducibility where possible.

# Prompting Rules

- Do not bury system behavior in ad hoc prompt strings spread across files.
- Centralize prompt definitions in one place.
- Prompt contract must enforce:
  - answer only from retrieved evidence
  - cite supporting sources
  - say when evidence is insufficient
  - avoid unsupported legal conclusions
- Make failure behavior explicit.
- Keep prompts short, structured, and versioned.

# Citation Rules

- Every answer must include clear citations.
- Citations must reference enough information for a human reviewer to verify the claim.
- At minimum preserve:
  - source title
  - document ID
  - page number or page range
  - chunk or node ID if available
- If support is weak or absent, the answer must abstain or narrow the claim.

# UI Rules

- Streamlit UI should be simple and functional.
- Include:
  - corpus status
  - question input
  - answer output
  - citation display
  - optional retrieved-context inspection
- Do not spend time polishing visual design unless requested.
- The UI must help verify retrieval and grounding, not just display the final answer.

# Evaluation Rules

- Include a lightweight evaluation harness.
- Minimum checks:
  - retrieval returns expected source for known questions
  - answers contain citations
  - system abstains when evidence is insufficient
- Keep the evaluation set small and explicit.
- Prefer a few high-quality test cases over many shallow ones.

# Error Handling Rules

- Handle these cases gracefully:
  - PDF parsing failure
  - empty corpus
  - index missing
  - weak retrieval
  - OpenAI API not configured
  - insufficient evidence
- Error messages should be clear and actionable.

# Documentation Rules

- README must explain:
  - architecture
  - setup
  - how to run locally
  - chunking strategy
  - retrieval strategy
  - citation strategy
  - evaluation approach
  - limitations
  - how this would evolve for production
- Keep documentation concise and technical.
- Focus on engineering judgment and tradeoffs.

# Local Development Commands

Use these commands by default if the repo contains the matching files:

- Create venv:
  - `python -m venv .venv`
- Activate venv:
  - macOS/Linux: `source .venv/bin/activate`
  - Windows: `.venv\Scripts\activate`
- Install deps:
  - `pip install -r requirements.txt`
- Run app:
  - `streamlit run app/ui.py`
- Run tests:
  - `pytest -q`
- Format:
  - `black .`
- Lint:
  - `ruff check .`
- Type check:
  - `mypy .`

# Workflow Rules

- Before coding, inspect the repo structure and existing files.
- Prefer editing existing files over creating redundant new ones.
- Keep changes incremental and runnable.
- After a meaningful set of changes:
  - run targeted tests if present
  - run lint if configured
  - run the app if the change affects Streamlit flow
- When adding a dependency, justify it by clear value.
- Do not rewrite large parts of the project unless necessary.

# Implementation Priorities

When building from scratch, follow this order:
1. project scaffolding
2. PDF ingestion and parsing
3. metadata model
4. hierarchical chunking
5. FAISS indexing
6. retrieval
7. prompt and QA logic
8. citation formatting
9. Streamlit UI
10. evaluation harness
11. README and design note

# Non-Goals

- full production auth
- multi-tenant infrastructure
- complex job orchestration
- distributed indexing
- polished enterprise frontend
- legal reasoning beyond retrieved evidence

# Common Gotchas

- Do not lose source-page traceability during parsing or chunking.
- Do not return answers without citations.
- Do not let the LLM answer beyond retrieved evidence.
- Do not hide important configuration inside code constants across multiple files.
- Do not overbuild infra for a local prototype.

# Definition of Done

A task is complete only when:
- code runs locally
- documents can be ingested and indexed
- questions can be answered with citations
- at least one graceful failure path works
- a small evaluation harness runs
- README explains tradeoffs and limitations