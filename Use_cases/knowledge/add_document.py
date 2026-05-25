from pathlib import Path
from Repositories.knowledge_repository import KnowledgeRepository

DOCS_DIR = Path("Infrastructure/Agents/knowledge/docs")

class AddDocument:
    def __init__(self, knowledge_repo: KnowledgeRepository):
        self._repo = knowledge_repo

    def execute(
        self,
        file_bytes: bytes,
        filename: str,
        metadata: dict | None = None,
    ) -> str:
        """Guarda el PDF en disco e indexa en agno. Retorna el path guardado."""
        if not filename.lower().endswith(".pdf"):
            raise ValueError(f"Solo se aceptan archivos PDF. Recibido: {filename}")

        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        dest = DOCS_DIR / filename
        dest.write_bytes(file_bytes)

        self._repo.add_document(str(dest), metadata)
        return str(dest)
