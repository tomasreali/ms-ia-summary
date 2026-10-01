from ollama import Client
from config.settings import settings

cliente_ia = Client(host=settings.ollama_url)


def generar_resumen(texto: str) -> str:
    """Genera un resumen del texto usando Ollama."""
    if not texto or len(texto.strip()) < 10:
        return "El texto proporcionado es demasiado corto para resumir."

    prompt = f"Haz un resumen claro, conciso y en español del siguiente texto:\n\n{texto}"

    try:
        respuesta = cliente_ia.generate(model=settings.ollama_model, prompt=prompt)
        return respuesta["response"]
    except Exception as e:
        return f"Error al comunicarse con la IA: {str(e)}"