from pydantic_settings import BaseSettings, SettingsConfigDict

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """Centralizovaná konfigurace aplikace."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_prefix="RAG_",
        extra="ignore",
    )

    app_name: str = "RAG API"
    environment: str = "development"

    data_dir: Path = BASE_DIR / "data"
    chroma_dir: Path = BASE_DIR / "chroma_db"

    collection_name: str = "ospf"

    embedding_model_name: str = "all-MiniLM-L6-v2"
    generation_model_name: str = "google/flan-t5-base"
    reranker_model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_candidate_lines: int = Field(default=30, ge=5, le=100)

    retrieval_results: int = Field(default=8, ge=1, le=20)
    max_context_lines: int = Field(default=5, ge=1, le=30)
    returned_sources: int = Field(default=3, ge=0, le=20)
    generation_max_new_tokens: int = Field(default=80, ge=1, le=512)
    source_preview_chars: int = Field(default=500, ge=100, le=3000)


@lru_cache
def  get_settings() -> Settings:
    """
    Vrátí jednu sdílenou instanci konfigurace aplikace.
    """

    return Settings()
