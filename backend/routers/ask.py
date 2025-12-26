from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from langchain_core.prompts import ChatPromptTemplate

from backend.app.deps import (
    get_llm,
    get_retriever,
    get_settings_instance,
    get_study_context,
    add_to_chat_history,
    get_recent_history,
)

router = APIRouter(prefix="/ask", tags=["ask"])


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: List[dict]  # Cambiar a lista de dicts con página y fuente


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
"""
Regla de Persistencia:
- Si el usuario indica que no sabe la respuesta o se siente perdido, NO cambies de tema. En su lugar, proporciona una pista pequeña (hint) basada en el contexto actual o haz una pregunta de opción múltiple para facilitar la respuesta (2–4 opciones).

Transiciones:
- Para mantener coherencia, usa frases de transición como: "No te preocupes, volvamos a lo que estábamos hablando sobre..." antes de continuar la explicación.
"""
"""
Extensión de Estrategia (Modo Secuencial):

6. Orden Secuencial: Prioriza el contenido de las páginas/segmentos más tempranos del documento. Construye la explicación desde lo general a lo específico, y de fundamentos a aplicaciones. Evita introducir temas avanzados si antes no has cubierto las bases.

7. Gestión de Preguntas Avanzadas: Si la pregunta del usuario apunta a temas avanzados, responde brevemente y señala los prerrequisitos con referencias a páginas/segmentos anteriores. Propón un camino: "Primero revisa X (pág. A), luego Y (pág. B) y finalmente Z (pág. C)".

8. Citas con Página: Cuando cites, incluye la página: "(Ver pág. N)" además de "(Basado en el documento)".

9. Estructura de la Respuesta: Usa una microsecuencia:
    - Contextualización breve del tema
    - Fundamento(s) clave (en orden)
    - Concepto/respondido
    - Pregunta de verificación
    - Referencias (páginas)
"""


@router.post("", response_model=AskResponse)
async def ask_question(payload: AskRequest):
    retriever = get_retriever()
    llm = get_llm()
    settings = get_settings_instance()

    # Use recent conversation (last 3 messages) to condense the question
    recent = get_recent_history(3)
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in recent]) if recent else ""

    condense_prompt = ChatPromptTemplate.from_template(
        """
        Reescribe la pregunta del usuario como una pregunta autocontenida y específica, manteniendo el mismo tema.
        Si hay conversación reciente, úsala para NO cambiar de tema y preservar el foco.

        Conversación reciente (máx. 3 mensajes):
        {history}

        Pregunta actual:
        {question}

        Pregunta autocontenida:
        """
    )
    condense_chain = condense_prompt | llm
    try:
        condensed = condense_chain.invoke({"history": history_text, "question": payload.question})
        condensed_q = getattr(condensed, "content", None) or str(condensed)
    except Exception:
        condensed_q = payload.question

    # Retrieve using the condensed question
    docs = retriever.invoke(condensed_q)
    if not docs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay documentos indexados aún. Sube un PDF primero.",
        )

    # Ordenar documentos por número de página ascendente para respetar la secuencia del material
    def _page_of(d):
        p = d.metadata.get("page", 0)
        try:
            return int(p)
        except Exception:
            return 0

    sorted_docs = sorted(docs, key=_page_of)

    context_blocks = []
    sources: List[dict] = []
    for doc in sorted_docs:
        src = doc.metadata.get("source", "desconocida")
        page = doc.metadata.get("page", "sin página")
        sources.append({"file": src, "page": page})
        context_blocks.append(f"Fuente: {src} (Página {page})\n{doc.page_content}")

    # Include study title from backend context to keep consistency
    study_ctx = get_study_context()
    doc_title = study_ctx.get("title", "Documento de Estudio")
    context_text = f"Título del documento: {doc_title}\n\n" + "\n\n".join(context_blocks)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            (
                "human",
                "Pregunta: {question}\n\nContexto (ordenado de inicial a avanzado):\n{context}\n\n"
                "Instrucciones: Responde de forma secuencial (de fundamentos a aplicaciones), evita saltos de nivel sin cubrir bases, y cita páginas."
                " Cierra con una pregunta breve de verificación.",
            ),
        ]
    )

    chain = prompt | llm
    result = chain.invoke({"question": payload.question, "context": context_text})

    answer_text = result.content if hasattr(result, "content") else str(result)

    # Deduplicate sources by page
    unique_by_page = {}
    for s in sources:
        unique_by_page[str(s.get("page"))] = s  # keep first file for page
    dedup_sources = list(unique_by_page.values())

    # Update memory with this turn
    try:
        add_to_chat_history("user", payload.question)
        add_to_chat_history("assistant", answer_text)
    except Exception:
        pass

    return AskResponse(answer=answer_text, sources=dedup_sources)