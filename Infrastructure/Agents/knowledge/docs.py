from Config.settings import settings
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.knowledge import Knowledge
from agno.knowledge.reader.pdf_reader import PDFReader
from agno.knowledge.embedder.sentence_transformer import SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder(
    id=settings.EMBEDDING_MODEL,        
)

# Apuntar a tu Chroma existente
vector_db = ChromaDb(
    collection=settings.CHROMA_COLLECTION,
    path=settings.CHROMA_PATH,
    persistent_client=True,
    embedder=embedder,
)

# Knowledge base 
knowledge_db= Knowledge(
    name="Documentos-Medicos",       
    vector_db=vector_db,
    max_results=15
)

# Carga inicial 
knowledge_db.insert(
    path="Infrastructure/Agents/knowledge/protocolos_clinicos_rurales.pdf",
    skip_if_exists=True,
    reader=PDFReader(),
    metadata={
        "tipo": "oficial",
        "categoria": "informe_medico",
        "subtipo": "guia",
    },
)