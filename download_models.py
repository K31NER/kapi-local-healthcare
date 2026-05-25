#!/usr/bin/env python3
"""Script independiente para descargar modelos de IA.

Ejecutar antes de empaquetar con PyInstaller para tener los modelos listos.

Uso:
    python download_models.py              # Descarga ambos modelos
    python download_models.py --force      # Fuerza descarga aunque existan
"""

import sys
import logging
from pathlib import Path

# Agregar raíz del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from Infrastructure.initialization import initialize_models, setup_logging


def main():
    """Descarga modelos de IA."""
    setup_logging()
    logger = logging.getLogger(__name__)

    force = "--force" in sys.argv

    logger.info("\n" + "=" * 70)
    logger.info("DESCARGADOR DE MODELOS - Telemedicina")
    logger.info("=" * 70)

    try:
        initialize_models(force_download=force)
        logger.info("\n" + "=" * 70)
        logger.info("✓ LISTO PARA EMPAQUETAR CON PYINSTALLER")
        logger.info("=" * 70)
        logger.info("\nPróximos pasos:")
        logger.info("1. Los modelos están guardados en: ./models/")
        logger.info("2. Ejecuta: pyinstaller --onefile --hidden-import=...")
        logger.info("3. Los usuarios recibirán la app sin descargar modelos")
        logger.info("=" * 70 + "\n")

    except Exception as e:
        logger.error(f"\n✗ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
