import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def download_gemma_model_auto(force_download=False):
    from Config.settings import settings
    model_path = Path(settings.MODEL_PATH)
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # Si ya existe el modelo, devolver la ruta
    if model_path.exists() and not force_download:
        logger.info(f"✓ Modelo Gemma encontrado localmente: {model_path}")
        return str(model_path)

    try:
        from huggingface_hub import hf_hub_download, list_repo_files

        logger.info("   (Conectando a Hugging Face... buscando archivos .gguf en el repo)")

        # Listar archivos del repo y buscar un .gguf disponible
        files = list_repo_files("unsloth/gemma-4-E2B-it-GGUF")
        gguf_files = [f for f in files if f.lower().endswith('.gguf')]

        if not gguf_files:
            logger.warning("⚠ No se encontraron archivos .gguf en el repo de Hugging Face")
            # Mostrar instrucciones manual al final
        else:
            # Elegir el primer .gguf candidato (preferir Q4_K_M si está presente)
            preferred = None
            for candidate in gguf_files:
                if 'Q4_K_M' in candidate or 'q4_k_m' in candidate.lower():
                    preferred = candidate
                    break
            filename = preferred or gguf_files[0]

            logger.info(f"   Se descargará: {filename}")

            downloaded_path = hf_hub_download(
                repo_id="unsloth/gemma-4-E2B-it-GGUF",
                filename=filename,
                cache_dir=str(model_path.parent),
                local_dir=str(model_path.parent),
                local_dir_use_symlinks=False,
            )

            if Path(downloaded_path).exists():
                # Copiar a la ruta final si es diferente
                if downloaded_path != str(model_path):
                    import shutil

                    shutil.copy2(downloaded_path, model_path)
                logger.info(f"✓ Modelo descargado correctamente: {model_path}")
                return str(model_path)
            else:
                logger.warning("⚠ Descarga incompleta")
                # continuar a mostrar instrucciones manuales

    except Exception as e:
        logger.warning(f"⚠ Descarga automática falló: {str(e)}")

    # Instrucciones de descarga manual
    logger.warning(f"⚠ Modelo NO encontrado: {model_path}")
    logger.warning(f"\nDESCARGA MANUAL:")
    logger.warning(f"1. Visita: https://huggingface.co/unsloth/gemma-4-E2B-it-GGUF")
    logger.warning(f"2. Descarga un archivo .gguf")
    logger.warning(f"3. Coloca en: {model_path.parent}")
    logger.warning(f"4. Renombralo a: {model_path.name}\n")
    return None

def download_embeddings_model(force_download=False):
    from Config.settings import settings
    model_name = "intfloat/multilingual-e5-small"
    cache_dir = Path(settings.EMBEDDINGS_CACHE_PATH)
    cache_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Descargando embeddings...")
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(model_name, cache_folder=str(cache_dir))
        logger.info(f"✓ Embeddings OK")
        return model_name
    except Exception as e:
        logger.warning(f"⚠ Error embeddings: {e}")
        return None

def initialize_models(force_download=False):
    logger.info("="*80)
    logger.info("🚀 Inicializando modelos...")
    logger.info("="*80)
    models = {}
    models["gemma_model"] = download_gemma_model_auto(force_download)
    models["embeddings_model"] = download_embeddings_model(force_download)
    logger.info("="*80)
    return models

def setup_logging():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

if __name__ == "__main__":
    setup_logging()
    initialize_models()
