import hashlib
import logging
from ollama import Client
from config.settings import settings

logger = logging.getLogger(__name__)
cliente_ia = Client(host=settings.ollama_url)

# Cache en memoria (Patrón Cache): guarda resúmenes por hash MD5 del texto
# para evitar llamadas redundantes a la IA y acelerar respuestas repetidas.
_cache: dict[str, str] = {}


def generar_resumen(texto: str) -> str:
    """Genera un resumen del texto usando Ollama. Utiliza cache en memoria para textos repetidos."""
    if not texto or len(texto.strip()) < 10:
        return "El texto proporcionado es demasiado corto para resumir."

    # 1. Calcular clave hash del texto
    cache_key = hashlib.md5(texto.encode("utf-8")).hexdigest()

    # 2. Si ya está en cache, devolverlo de inmediato (Cache HIT)
    if cache_key in _cache:
        logger.info(f"Cache HIT — Clave: {cache_key[:8]}... Resumen recuperado de memoria.")
        return _cache[cache_key]

    logger.info(f"Cache MISS — Clave: {cache_key[:8]}... Solicitando resumen a Ollama.")

    # 3. Si no está en cache, llamar a Ollama
    prompt = f"Haz un resumen claro, conciso y en español del siguiente texto:\n\n{texto}"

    try:
        respuesta = cliente_ia.generate(model=settings.ollama_model, prompt=prompt)
        resultado = respuesta["response"]

        # 4. Guardar en cache para próximas peticiones
        _cache[cache_key] = resultado
        logger.info(f"Resumen almacenado en cache — Clave: {cache_key[:8]}...")
        return resultado
    except Exception as e:
        return f"Error al comunicarse con la IA: {str(e)}"