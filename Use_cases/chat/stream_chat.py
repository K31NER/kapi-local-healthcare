from typing import Generator
from Repositories.consultation_repository import ConsultationRepository
from Infrastructure.Agents.workflow import kapi
from Domain.chat import ChatEvent, ContentEvent, DoneEvent, ErrorEvent, ThinkingEvent

# Re-exportamos los eventos para que API/routers/chat.py no cambie sus imports
__all__ = [
    "StreamChat",
    "ChatEvent",
    "ContentEvent",
    "DoneEvent",
    "ErrorEvent",
    "ThinkingEvent",
]


class StreamChat:
    def __init__(self, save_repo: ConsultationRepository):
        self._save_repo = save_repo

    def execute(
        self,
        question: str,
        session_id: str,
        user_id: str,
    ) -> Generator[ChatEvent, None, None]:
        return kapi.run_stream(question, session_id, user_id, self._save_repo)
