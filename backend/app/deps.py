from pathlib import Path
from typing import Optional

from langchain_chroma import Chroma
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings

from backend.config.settings import Settings, get_settings


_settings = get_settings()

_persist_dir = Path(_settings.chroma_persist_dir)
_persist_dir.mkdir(parents=True, exist_ok=True)

_embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=_settings.azure_endpoint,
    azure_deployment=_settings.azure_embedding_deployment,
    model=_settings.azure_embedding_model,
    api_key=_settings.azure_api_key,
    api_version=_settings.azure_api_version,
)

_vectorstore = Chroma(
    collection_name="rootmind",
    embedding_function=_embeddings,
    persist_directory=str(_persist_dir),
)


def get_settings_instance() -> Settings:
    return _settings


def get_embeddings() -> AzureOpenAIEmbeddings:
    return _embeddings


def get_vectorstore() -> Chroma:
    return _vectorstore


def get_retriever():
    return _vectorstore.as_retriever(search_kwargs={"k": _settings.top_k})


def get_llm(settings: Optional[Settings] = None) -> AzureChatOpenAI:
    cfg = settings or _settings
    return AzureChatOpenAI(
        azure_endpoint=cfg.azure_endpoint,
        azure_deployment=cfg.azure_deployment,
        api_key=cfg.azure_api_key,
        api_version=cfg.azure_api_version,
        temperature=0.2,
    )