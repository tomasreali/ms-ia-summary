from fastapi import FastAPI
from app.routers import router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="ms-ia-summary", description="Microservicio de resumen de texto con IA")

app.include_router(router)

logger.info("ms-ia-summary iniciado correctamente.")