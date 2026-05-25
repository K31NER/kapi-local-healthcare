from pathlib import Path

_PIN_FILE = Path(__file__).parent.parent.parent.parent / ".kapi_pin"


def is_registered() -> bool:
    return _PIN_FILE.exists()


def save_pin(pin: str) -> None:
    _PIN_FILE.write_text(pin.strip(), encoding="utf-8")


def check_pin(pin: str) -> bool:
    return _PIN_FILE.exists() and _PIN_FILE.read_text(encoding="utf-8").strip() == pin.strip()


def delete_credentials() -> None:
    if _PIN_FILE.exists():
        _PIN_FILE.unlink()
