import os
import tempfile
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader

from backend.app.deps import get_settings_instance, get_vectorstore, reset_vectorstore

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se aceptan archivos PDF.",
        )

    settings = get_settings_instance()
    # Clean previous collection to avoid mixing across uploads
    reset_vectorstore()
    vectorstore = get_vectorstore()

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        loader = PyPDFLoader(tmp_path)
        docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        split_docs = splitter.split_documents(docs)

        for doc in split_docs:
            doc.metadata["source"] = file.filename

        vectorstore.add_documents(split_docs)

        return {
            "chunks_added": len(split_docs),
            "persist_dir": str(settings.chroma_persist_dir),
        }
    except Exception as exc:  # pragma: no cover - guardrails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando el PDF: {exc}",
        ) from exc
    finally:
        try:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass