from functools import lru_cache
from pathlib import Path
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
    )
    
    azure_endpoint: str = Field(..., alias="AZURE_OPENAI_ENDPOINT")
    azure_api_key: str = Field(..., alias="AZURE_OPENAI_KEY")
    azure_deployment: str = Field(..., alias="AZURE_OPENAI_DEPLOYMENT")
    azure_embedding_deployment: str = Field(..., alias="AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT")
    azure_embedding_model: str = Field(
        "text-embedding-3-small",
        alias="AZURE_OPENAI_EMBEDDINGS_MODEL",
    )
    azure_api_version: str = Field("2024-02-15-preview", alias="AZURE_OPENAI_API_VERSION")

    chunk_size: int = Field(1000, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(150, alias="CHUNK_OVERLAP")
    top_k: int = Field(4, alias="TOP_K")

    chroma_persist_dir: Path = Field(Path(__file__).resolve().parent.parent / ".chroma", alias="CHROMA_PERSIST_DIR")


@lru_cache
def get_settings() -> Settings:
    return Settings()