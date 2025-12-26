from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from backend.app.deps import get_llm, get_retriever, get_settings_instance

router = APIRouter(prefix="/ask", tags=["ask"])


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: List[str]


SYSTEM_PROMPT = (
    "Eres RootMind, un tutor cognitivo. Guias al alumno paso a paso con preguntas "
    "socráticas, aclaras dudas y das ejemplos breves. Usa el contexto recuperado; "
    "si falta información, sé honesto y sugiere cómo avanzar."
)


@router.post("", response_model=AskResponse)
async def ask_question(payload: AskRequest):
    retriever = get_retriever()
    llm = get_llm()
    settings = get_settings_instance()

    docs = retriever.invoke(payload.question)
    if not docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay documentos indexados aún. Sube un PDF primero.",
        )

    context_blocks = []
    sources: List[str] = []
    for doc in docs:
        src = doc.metadata.get("source", "desconocida")
        sources.append(src)
        context_blocks.append(f"Fuente: {src}\n{doc.page_content}")

    context_text = "\n\n".join(context_blocks)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "Pregunta: {question}\n\nContexto:\n{context}\n\n"
                "Responde como tutor, guiando y explicando brevemente.",
            ),
        ]
    )

    chain = prompt | llm
    result = chain.invoke({"question": payload.question, "context": context_text})

    answer_text = result.content if hasattr(result, "content") else str(result)

    return AskResponse(answer=answer_text, sources=sources[: settings.top_k])