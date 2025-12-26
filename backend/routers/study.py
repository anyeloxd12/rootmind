from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List

from backend.app.deps import generate_study_context, get_study_context, set_study_context

router = APIRouter(prefix="/study", tags=["study"])


class StudyPlan(BaseModel):
    section: str
    objective: str


class StudyMetadata(BaseModel):
    title: str
    study_plan: List[StudyPlan]


@router.post("/metadata", response_model=StudyMetadata)
async def generate_study_metadata():
    """Genera el título creativo y plan de estudios del documento cargado."""
    try:
        context = await generate_study_context()
        set_study_context(context)
        return StudyMetadata(**context)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando metadatos: {exc}",
        ) from exc


@router.get("/metadata", response_model=StudyMetadata)
async def get_study_metadata():
    """Obtiene el título y plan de estudios generados previamente."""
    context = get_study_context()
    if not context.get("study_plan"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aún no se ha generado el contexto de estudio. Sube un PDF primero.",
        )
    return StudyMetadata(**context)
