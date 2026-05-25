from Config.settings import settings
from agno.knowledge.reader.pdf_reader import PDFReader
from Infrastructure.Agents.knowledge.docs import knowledge_db
from Repositories.knowledge_repository import KnowledgeRepository

_DEFAULT_METADATA = {
    "tipo": "oficial",
    "categoria": "informe_medico",
    "subtipo": "guia",
}

class ChromaKnowledgeRepository(KnowledgeRepository):
    """Gestión de documentos médicos usando el knowledge_db de agno."""

    def add_document(self, path: str, metadata: dict | None = None) -> None:
        knowledge_db.insert(
            path=path,
            skip_if_exists=True,
            reader=PDFReader(),
            metadata=metadata or _DEFAULT_METADATA,
        )

    def clear(self) -> None:
        knowledge_db.vector_db.client.delete_collection(settings.CHROMA_COLLECTION)
