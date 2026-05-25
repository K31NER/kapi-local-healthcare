"""
Inicia FastAPI y Streamlit en ventanas de consola separadas (Windows).

Uso:
    uv run python start.py
"""

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Flag de Windows para abrir una nueva ventana de consola por proceso
CREATE_NEW_CONSOLE = 0x00000010


def _popen(args: list[str]) -> subprocess.Popen:
    return subprocess.Popen(
        args,
        cwd=str(BASE_DIR),
        creationflags=CREATE_NEW_CONSOLE,
    )


def main():
    print("=" * 50)
    print("  Iniciando Kapi")
    print("  FastAPI   → http://localhost:8000")
    print("  Streamlit → http://localhost:8501")
    print("=" * 50)

    api_proc = _popen(["uv", "run", "fastapi", "dev", "main.py"])
    ui_proc = _popen(["uv", "run", "streamlit", "run", "app/main.py"])

    print("\nAmbos servidores abiertos en ventanas separadas.")
    print("Cierra cada ventana para detener el servidor correspondiente.")
    print("Presiona Ctrl+C aquí para detener ambos desde esta ventana.\n")

    try:
        api_proc.wait()
        ui_proc.wait()
    except KeyboardInterrupt:
        print("\nDeteniendo servidores...")
        api_proc.terminate()
        ui_proc.terminate()
        sys.exit(0)


if __name__ == "__main__":
    main()
