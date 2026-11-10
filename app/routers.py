from fastapi import APIRouter, HTTPException
import logging
import time
import asyncio
from datetime import datetime, timezone
from config.settings import settings
from service.summary_service import generar_resumen
from app.models.summary_models import SummarizeRequest, SummarizeResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Variables para health check mejorado (Tarea 8)
_start_time = time.time()
_version = "1.0.0"

# Rate Limit: máximo 3 resúmenes simultáneos (evita saturar a Ollama)
MAX_CONCURRENT_SUMMARIES = 3
_summary_semaphore = asyncio.Semaphore(MAX_CONCURRENT_SUMMARIES)


@router.get("/health")
async def health_check():
    """Health check mejorado con uptime y versión (Twelve-Factor App, Factor 11)."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": _version,
        "uptime_seconds": round(time.time() - _start_time, 2),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """Genera un resumen del texto recibido usando Ollama."""
    start = time.time()
    logger.info("Request recibido: POST /summarize")

    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="El texto es demasiado corto para resumir.")

    # Rate Limit: si ya hay 3 resúmenes en curso, rechazar inmediatamente con 429
    if _summary_semaphore.locked():
        logger.warning("Rate limit activado: demasiadas solicitudes simultáneas a /summarize")
        raise HTTPException(
            status_code=429,
            detail="Demasiadas solicitudes simultáneas. Intente nuevamente en unos segundos."
        )

    async with _summary_semaphore:
        loop = asyncio.get_event_loop()
        resumen = await loop.run_in_executor(None, generar_resumen, request.text)

    duration = round((time.time() - start) * 1000, 2)
    logger.info(f"Resumen generado exitosamente - {duration}ms")
    return {"summary": resumen}