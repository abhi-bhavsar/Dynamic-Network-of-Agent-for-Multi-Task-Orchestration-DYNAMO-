from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .api.routes.health import router as health_router
from .api.routes.query import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: pre-compile the LangGraph and warm up the LLM client."""
    print(f"🚀 Starting DYNAMO — model: {settings.GROQ_MODEL}")
    from .orchestrator.graph import dynamo_graph  # triggers compile
    print("✅ LangGraph compiled and ready")
    yield
    print("🛑 DYNAMO shutting down")


app = FastAPI(
    title="DYNAMO API",
    description="Dynamic Network of Agents for Multi-Task Orchestration",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health_router, tags=["System"])
app.include_router(query_router, prefix="/api/v1", tags=["DYNAMO"])


@app.get("/")
async def root():
    return {
        "system": "DYNAMO",
        "version": "1.0.0",
        "model": settings.GROQ_MODEL,
        "docs": "/docs",
    }
