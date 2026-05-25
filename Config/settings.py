from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    
    MODEL: str = "gemma4:e2b"
    MODEL_PATH: str = "./models/gemma-4-E2B-it-GGUF-Q4_K_M.gguf"
    DB_URI: str = "sqlite:///./telemedicina.db"
    CHROMA_PATH: str = "./data/chroma"
    CHROMA_COLLECTION: str = "medical_knowledge"
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"
    EMBEDDINGS_CACHE_PATH: str = "./models/embeddings"
    MODE:str = "llama"
    class Config:
        env_file = ".env"
        
settings = Settings()
os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
os.makedirs(settings.EMBEDDINGS_CACHE_PATH, exist_ok=True)