import json
import requests

API_URL = "http://localhost:8000"


def api_get_user():
    try:
        r = requests.get(f"{API_URL}/user", timeout=5)
        return None if r.status_code == 404 else r.json()
    except requests.ConnectionError:
        return "offline"


def api_save_user(payload: dict, editing: bool):
    if editing:
        r = requests.put(f"{API_URL}/user", json=payload, timeout=5)
    else:
        r = requests.post(f"{API_URL}/user", json=payload, timeout=5)
    r.raise_for_status()
    return r.json()


def api_delete_user():
    requests.delete(f"{API_URL}/user", timeout=5).raise_for_status()


def api_export_pdf() -> bytes:
    r = requests.get(f"{API_URL}/report/export", timeout=60)
    r.raise_for_status()
    return r.content


def api_upload_document(file_bytes: bytes, filename: str, tipo: str, categoria: str, subtipo: str) -> dict:
    r = requests.post(
        f"{API_URL}/knowledge/upload",
        files={"file": (filename, file_bytes, "application/pdf")},
        data={"tipo": tipo, "categoria": categoria, "subtipo": subtipo},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()


def iter_chat_events(question: str, session_id: str):
    """Yields (event_type, data_dict) for each SSE event from /chat/stream."""
    with requests.post(
        f"{API_URL}/chat/stream",
        json={"question": question, "session_id": session_id, "user_id":"Local-User"},
        stream=True,
        timeout=180,
    ) as resp:
        resp.raise_for_status()
        buffer = ""
        for raw in resp.iter_content(chunk_size=None, decode_unicode=True):
            if not raw:
                continue
            buffer += raw
            while "\n\n" in buffer:
                block, buffer = buffer.split("\n\n", 1)
                event_type = "message"
                data_line = ""
                for line in block.strip().split("\n"):
                    if line.startswith("event:"):
                        event_type = line[6:].strip()
                    elif line.startswith("data:"):
                        data_line = line[5:].strip()
                if not data_line:
                    continue
                try:
                    parsed = json.loads(data_line)
                except json.JSONDecodeError:
                    continue
                yield event_type, parsed
