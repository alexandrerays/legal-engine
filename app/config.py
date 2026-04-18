from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "indexes"

PARENT_CHUNK_SIZE = 2048
CHILD_CHUNK_SIZE = 512
CHUNK_OVERLAP = 64

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536
LLM_MODEL = "gpt-4o-mini"
LLM_TEMPERATURE = 0.1

TOP_K = 6
SIMILARITY_THRESHOLD = 0.3
