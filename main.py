from fastapi import FastAPI
from app.routers import router
from config.logging_config import setup_logging
import logging

# Configurar logging estructurado en JSON (Twelve-Factor: Factor 11)
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="ms-ia-summary", description="Microservicio de resumen de texto con IA")

app.include_router(router)

logger.info("ms-ia-summary iniciado correctamente.")