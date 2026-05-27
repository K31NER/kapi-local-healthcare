from abc import ABC, abstractmethod
from Domain.consultation import Consultation

class ConsultationRepository(ABC):
    @abstractmethod
    def save(self, consultation: Consultation) -> Consultation: ...

    @abstractmethod
    def get_all(self) -> list[Consultation]: ...

    @abstractmethod
    def get_sessions(self) -> list[dict]: ...

    @abstractmethod
    def get_by_session(self, session_id: str) -> list[Consultation]: ...

    @abstractmethod
    def delete_session(self, session_id: str) -> None: ...

    @abstractmethod
    def delete_all(self) -> None: ...
