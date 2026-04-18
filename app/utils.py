from __future__ import annotations

import hashlib
import os

from dotenv import load_dotenv


def load_env() -> None:
    load_dotenv()


def get_openai_key() -> str:
    load_env()
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key or key.startswith("sk-your"):
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return key


def init_llama_settings() -> None:
    """Load .env and configure LlamaIndex global Settings with OpenAI models."""
    load_env()
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key or key.startswith("sk-your"):
        raise EnvironmentError(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )

    from llama_index.core import Settings
    from llama_index.embeddings.openai import OpenAIEmbedding
    from llama_index.llms.openai import OpenAI

    from app.config import EMBEDDING_DIM, EMBEDDING_MODEL, LLM_MODEL, LLM_TEMPERATURE

    Settings.embed_model = OpenAIEmbedding(
        model=EMBEDDING_MODEL, api_key=key, dimensions=EMBEDDING_DIM
    )
    Settings.llm = OpenAI(
        model=LLM_MODEL, temperature=LLM_TEMPERATURE, api_key=key
    )


def doc_id_from_filename(filename: str) -> str:
    return hashlib.sha256(filename.encode()).hexdigest()[:12]
