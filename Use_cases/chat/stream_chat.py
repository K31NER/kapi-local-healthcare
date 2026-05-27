from typing import Generator
from fastapi import BackgroundTasks
from Infrastructure.Agents.workflow import kapi
from Repositories.user_repository import UserRepository
from Infrastructure.Agents.schemas.agent import InputModel
from Repositories.consultation_repository import ConsultationRepository
from Domain.chat import ChatEvent, ContentEvent, DoneEvent, ErrorEvent, ThinkingEvent

__all__ = [
    "StreamChat",
    "ChatEvent",
    "ContentEvent",
    "DoneEvent",
    "ErrorEvent",
    "ThinkingEvent",
]

class StreamChat:
    def __init__(self, save_repo: ConsultationRepository, user_repo: UserRepository):
        self._save_repo = save_repo
        self._user_repo = user_repo

    def execute(
        self,
        question: str,
        session_id: str,
        user_id: str,
        background_tasks: BackgroundTasks,
    ) -> Generator[ChatEvent, None, None]:
        user_input = InputModel(
            question=question,
            context_user=self._user_repo.get_user_context()
        )
        return kapi.run_stream(user_input, session_id, user_id, self._save_repo, background_tasks)
