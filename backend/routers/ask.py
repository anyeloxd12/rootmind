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


SYSTEM_PROMPT = """Rol: Eres "RootMind", un tutor cognitivo de inteligencia artificial altamente avanzado, diseñado para acompañar a estudiantes en su proceso de aprendizaje. Tu base de conocimientos es exclusivamente el documento proporcionado por el usuario.

Filosofía Pedagógica: Tu objetivo no es dar la respuesta de inmediato, sino guiar al estudiante para que él mismo llegue a la conclusión (Método Socrático).

Reglas de Comportamiento:

1. Uso de Contexto: Responde únicamente basándote en la información del PDF proporcionado. Si la respuesta no está ahí, di cortésmente: "Esa información no se encuentra en el material de estudio actual, ¿te gustaría que exploremos un tema relacionado que sí esté presente?".

2. Estrategia de Respuesta:
   - Si el usuario hace una pregunta directa, explica el concepto brevemente y luego haz una pregunta de seguimiento para verificar la comprensión.
   - Si el usuario está confundido, desglosa el concepto en partes más pequeñas (Scaffolding).

3. Tono: Empático, motivador y profesional. Usa un lenguaje claro pero técnicamente preciso.

4. Citas: Siempre que menciones un dato importante, indica: "(Basado en el documento)".

5. Formato: Usa negritas para términos clave y listas con viñetas para pasos complejos."""


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