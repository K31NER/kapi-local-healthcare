from abc import ABC, abstractmethod

class KnowledgeRepository(ABC):
    """Contrato para gestionar documentos médicos en el índice vectorial."""

    @abstractmethod
    def add_document(self, path: str, metadata: dict | None = None) -> None:
        """Indexa un documento PDF en el knowledge base vía agno."""

    @abstractmethod
    def clear(self) -> None:
        """Elimina el contenido del repositorio vectorial."""
