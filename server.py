import logging
from fastapi import FastAPI
from Config.settings import settings
from contextlib import asynccontextmanager
from Infrastructure.initialization import initialize_models
from AI_server.llama_server import start_llm_server, wait_for_llm_ready
from Infrastructure.Databases.sql.conexion import init_db

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida del servidor FastAPI."""

    print("\n" + "=" * 60)
    print("Iniciando servidor...")
    print("=" * 60)

    init_db()

    if settings.MODE == "llama":
        try:
            # Descargar e inicializar modelos automáticamente
            models = initialize_models(force_download=False)
            print(f"\n✓ Servidor listo con modelos cargados:")
            for key, value in models.items():
                print(f"  - {key}: {value}")
            print("=" * 60)
        except Exception as e:
            print(f"\n✗ Error inicializando modelos: {e}")
            print("  La aplicación puede no funcionar correctamente.")
            raise

        # Arrancar el servidor LLM embebido en hilo daemon
        start_llm_server(
            model_path=settings.MODEL_PATH,
            mmproj_path=getattr(settings, "MMPROJ_PATH", None),  # Opcional: visión
            n_ctx=8192,
            n_gpu_layers=-1,       # 0 = solo CPU; -1 = todo en GPU si hay CUDA
            chat_format="gemma",  # Gemma 4 usa este chat format en llama-cpp
        )

        # Validamos que se cargue el modelo
        if not await wait_for_llm_ready(timeout_seconds=180):
            raise RuntimeError(
                "El servidor LLM no respondió en el tiempo esperado. "
                "Verifica que MODEL_PATH apunte a un .gguf válido."
            )

    yield

    print("\n" + "=" * 60)
    print("Apagando servidor...")
    print("=" * 60)
