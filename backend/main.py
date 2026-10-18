from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .api.routes.health import router as health_router
from .api.routes.query import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: pre-compile the LangGraph, warm up LLM, and initialize DB tables."""
    print(f"🚀 Starting DYNAMO — model: {settings.GROQ_MODEL}")
    from .orchestrator.graph import dynamo_graph  # triggers compile
    print("✅ LangGraph compiled and ready")

    # Auto-initialize database tables in Supabase / PostgreSQL
    try:
        from .core.database import engine, Base
        from .core.models import BenchmarkRun
        if engine is not None:
            Base.metadata.create_all(bind=engine)
            print("✅ Database tables verified and ready in PostgreSQL / Supabase")
    except Exception as e:
        print(f"⚠️ Warning: Database auto-initialization could not complete: {e}")

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
