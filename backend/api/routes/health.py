from fastapi import APIRouter
from ..schemas.response import HealthResponse
from ...core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Quick liveness check — also verifies Groq API key is set."""
    groq_ok = bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_groq_api_key_here")
    return HealthResponse(
        status="ok" if groq_ok else "degraded",
        model=settings.GROQ_MODEL,
        groq_connected=groq_ok,
    )
