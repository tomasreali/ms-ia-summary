from fastapi import APIRouter, HTTPException
import logging
from config.settings import settings
from service.summary_service import generar_resumen
from app.models.summary_models import SummarizeRequest, SummarizeResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}


@router.post("/summarize", response_model=SummarizeResponse)
def summarize_text(request: SummarizeRequest):
    logger.info("Recibiendo texto para resumir")

    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="El texto es demasiado corto para resumir.")

    resumen = generar_resumen(request.text)

    logger.info("Resumen generado exitosamente")
    return {"summary": resumen}