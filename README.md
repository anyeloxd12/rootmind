# RootMind

Tutor Cognitivo con RAG para la Imagine Cup.

## 🚀 Inicio Rápido

### Opción 1: Script automatizado (recomendado)

```bash
./run.sh
```

Este script inicializa:
- ✓ Backend FastAPI en `http://localhost:8000`
- ✓ Frontend React + Vite en `http://localhost:5173`

### Opción 2: Manual

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend (en otra terminal):**
```bash
cd frontend
npm install
npm run dev
```

## 📋 Configuración

### Backend (.env)

Copia `backend/.env.example` a `backend/.env` y completa:

```dotenv
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT=text-embedding-3-small
AZURE_OPENAI_EMBEDDINGS_MODEL=text-embedding-3-small
```

### Frontend

- API base: `http://localhost:8000` (configurable vía `VITE_API_BASE`)

## 📚 Stack

- **Backend:** FastAPI + LangChain + AzureChatOpenAI
- **RAG:** Chroma (persistencia local) + text-embedding-3-small
- **Frontend:** React + Vite + Tailwind CSS

## 🔗 Endpoints

- `POST /upload` - Sube PDF, lo procesa e ingesta al vector store
- `POST /ask` - Pregunta con contexto RAG
- `GET /health` - Estado del backend
- `GET /docs` - Swagger UI (en `http://localhost:8000/docs`)

## 📦 Estructura

```
/backend
  ├── main.py              # App FastAPI
  ├── config/settings.py   # Configuración
  ├── app/deps.py          # Dependencias (LLM, embeddings, store)
  ├── routers/
  │   ├── upload.py        # Ingesta de PDFs
  │   └── ask.py           # QA con RAG
  └── requirements.txt

/frontend
  ├── src/
  │   ├── App.tsx          # Composición principal
  │   ├── components/
  │   │   ├── Upload.tsx   # Carga de PDF
  │   │   └── Chat.tsx     # Chat de estudio
  │   ├── lib/api.ts       # Cliente HTTP
  │   └── index.css        # Tailwind
  ├── vite.config.ts
  └── package.json
```

## 🐛 Depuración

- **Backend logs:** Check terminal where `uvicorn` runs
- **Chroma store:** `backend/.chroma` (persistencia local)
- **Frontend dev:** Vite recompila automáticamente
- **API docs:** `http://localhost:8000/docs`

---

**Desarrollado para Imagine Cup** 🏆
