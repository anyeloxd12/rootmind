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


async def generate_study_context() -> dict:
    """Genera un título creativo y plan de estudios desde el contenido del PDF."""
    from langchain_core.prompts import ChatPromptTemplate
    
    try:
        # Obtener una muestra del contenido del vector store
        retriever = get_retriever()
        sample_docs = retriever.invoke("conceptos principales temas importantes")
        
        if not sample_docs:
            return {
                "title": "Documento de Estudio",
                "study_plan": [{"section": "Contenido", "objective": "Explorar el material proporcionado"}],
            }
        
        # Concatenar el contenido de muestra
        sample_content = "\n\n".join([doc.page_content[:500] for doc in sample_docs[:3]])
        
        # Prompt para generar título y plan
        llm = get_llm()
        prompt = ChatPromptTemplate.from_template(
            """Analiza el siguiente contenido educativo y genera:

1. Un título creativo y profesional para el documento (máximo 60 caracteres).
2. Un plan de estudios estructurado en 5-7 secciones principales, donde cada sección tenga:
   - Título descriptivo
   - Objetivo de aprendizaje breve (una línea)

Formato de respuesta (JSON válido):
{{
  "title": "Tu título aquí",
  "study_plan": [
    {{"section": "Sección 1", "objective": "Objetivo 1"}},
    {{"section": "Sección 2", "objective": "Objetivo 2"}}
  ]
}}

Contenido a analizar:
{content}"""
        )
        
        chain = prompt | llm
        result = chain.invoke({"content": sample_content})
        
        # Parsear la respuesta JSON
        import json
        import re
        
        # Extraer JSON de la respuesta
        json_match = re.search(r'\{.*\}', result.content, re.DOTALL)
        if json_match:
            study_context = json.loads(json_match.group())
            return study_context
        else:
            return {
                "title": "Documento de Estudio",
                "study_plan": [{"section": "Contenido", "objective": "Explorar el material proporcionado"}],
            }
    except Exception as e:
        print(f"Error generando contexto de estudio: {e}")
        return {
            "title": "Documento de Estudio",
            "study_plan": [{"section": "Contenido", "objective": "Explorar el material proporcionado"}],
        }


# Variable global para almacenar el contexto de estudio
_study_context = None


def get_study_context() -> dict:
    global _study_context
    return _study_context or {
        "title": "Documento de Estudio",
        "study_plan": [],
    }


def set_study_context(context: dict):
    global _study_context
    _study_context = context