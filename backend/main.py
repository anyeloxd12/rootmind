from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.deps import get_settings_instance
from backend.routers import ask, upload

app = FastAPI(title="RootMind Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://humble-succotash-q7px9jgjgj69fgjq-5173.app.github.dev",
        "http://localhost:8000",  # Para CORS preflight desde localhost
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(ask.router)


@app.get("/health")
async def health_check():
    settings = get_settings_instance()
    return {
        "status": "ok",
        "model": settings.azure_deployment,
        "store": str(settings.chroma_persist_dir),
    }
