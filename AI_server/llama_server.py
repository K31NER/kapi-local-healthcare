import time
import httpx
import uvicorn
import logging
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Constantes del servidor embebido
LLM_HOST = "127.0.0.1"
LLM_PORT = 11435
LLM_BASE_URL = f"http://{LLM_HOST}:{LLM_PORT}/v1"
LLM_API_KEY = "no-key-required"  # llama-cpp-python no valida la key


def start_llm_server(
    model_path: str,
    mmproj_path: Optional[str] = None,
    n_ctx: int = 8192,
    n_gpu_layers: int = 0,
    chat_format: str = "gemma",
) -> threading.Thread:
    """
    Crea y arranca el servidor llama-cpp-python en un hilo daemon.

    Args:
        model_path:    Ruta al archivo .gguf del modelo (Gemma4 E2B Q4_K_M).
        mmproj_path:   Ruta al mmproj.gguf para multimodalidad (visión).
                       Si es None, el servidor arranca sin soporte de imágenes.
        n_ctx:         Tamaño del contexto en tokens.
        n_gpu_layers:  Capas en GPU. 0 = solo CPU. -1 = todo en GPU.
        chat_format:   Plantilla de chat. "gemma" para Gemma 4.

    Returns:
        El hilo daemon activo (referencia para monitoreo, no es necesario
        hacer join; se cierra automáticamente al terminar el proceso).
    """
    # Validar existencia del modelo antes de intentar levantar el servidor
    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Modelo no encontrado en: {model_path}\n"
            "Coloca el archivo .gguf en la ruta configurada en settings.MODEL_PATH"
        )

    # Importar aquí para no fallar en import si llama-cpp-python[server]
    # no está instalado (da un error claro en lugar de uno críptico)
    try:
        from llama_cpp.server.app import create_app
        from llama_cpp.server.settings import ModelSettings, ServerSettings
    except ImportError as exc:
        raise ImportError(
            "Falta instalar el extra de servidor: "
            "pip install 'llama-cpp-python[server]'"
        ) from exc

    # ── Configuración del modelo ────────────────────────────────────────────
    model_kwargs = dict(
        model=model_path,
        n_ctx=n_ctx,
        n_gpu_layers=n_gpu_layers,
        chat_format=chat_format,
        verbose=False,
    )

    # Agregar soporte multimodal solo si se provee el mmproj
    if mmproj_path:
        if not Path(mmproj_path).exists():
            logger.warning(
                "mmproj_path especificado pero no encontrado: %s. "
                "El servidor arrancará SIN soporte de imágenes.",
                mmproj_path,
            )
        else:
            model_kwargs["clip_model_path"] = mmproj_path
            logger.info("Multimodalidad (visión) activada con mmproj: %s", mmproj_path)

    model_settings = ModelSettings(**model_kwargs)

    server_settings = ServerSettings(
        host=LLM_HOST,
        port=LLM_PORT,
        interrupt_requests=True,  # Permite cancelar requests en curso (streaming)
    )

    llm_app = create_app(
        server_settings=server_settings,
        model_settings=[model_settings],   # create_app espera List[ModelSettings]
    )

    # ── Configurar uvicorn para correr el servidor en el hilo ───────────────
    config = uvicorn.Config(
        llm_app,
        host=LLM_HOST,
        port=LLM_PORT,
        log_level="error",   # Silencioso; los logs del modelo van por `logger`
        loop="asyncio",
    )
    server = uvicorn.Server(config)

    thread = threading.Thread(
        target=server.run,
        daemon=True,          # Se cierra automáticamente con el proceso padre
        name="llm-cpp-server",
    )
    thread.start()
    logger.info("Hilo del servidor LLM arrancado (puerto %s).", LLM_PORT)

    return thread

async def wait_for_llm_ready(timeout_seconds: int = 180) -> bool:
    """
    Hace polling ASYNC al servidor hasta que responda OK o se agote el timeout.
    
    IMPORTANTE: debe ser `async` y usar `asyncio.sleep` para no bloquear el
    event loop principal de FastAPI mientras el hilo daemon levanta uvicorn.
    Usar `time.sleep` aquí causaba el timeout aunque el modelo cargara bien.
    
    Prueba dos endpoints en orden:
        1. /health  → disponible en versiones recientes de llama-cpp-python
        2. /v1/models → fallback compatible con todas las versiones
    """
    import asyncio
    # Endpoints a probar en orden; el primero que responda 200 confirma que
    # el servidor está listo
    candidates = [
        f"http://{LLM_HOST}:{LLM_PORT}/health",
        f"http://{LLM_HOST}:{LLM_PORT}/v1/models",
    ]
    
    deadline = time.time() + timeout_seconds
    logger.info(
        "Esperando que el servidor LLM esté listo (puerto %s)...", LLM_PORT
    )
    
    async with httpx.AsyncClient(timeout=3.0) as client:
        while time.time() < deadline:
            for url in candidates:
                try:
                    response = await client.get(url)
                    if response.status_code == 200:
                        logger.info("✅ Servidor LLM listo (%s).", url)
                        return True
                except (httpx.ConnectError, httpx.TimeoutException):
                    pass  # Puerto todavía no disponible; seguir esperando
    
            await asyncio.sleep(1)  # ← cede el control al event loop (no bloquea)
    
    logger.error(
        "❌ Timeout esperando el servidor LLM (%s s).", timeout_seconds
    )
    return False