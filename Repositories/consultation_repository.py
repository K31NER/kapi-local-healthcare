from abc import ABC, abstractmethod
from Domain.consultation import Consultation


class ConsultationRepository(ABC):
    @abstractmethod
    def save(self, consultation: Consultation) -> Consultation: ...

    @abstractmethod
    def get_all(self) -> list[Consultation]: ...
