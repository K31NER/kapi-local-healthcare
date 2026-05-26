from pydantic import BaseModel, Field
from typing import Dict, List,Optional
from Domain.user import CacheUser
class InputModel(BaseModel):
    question: str
    context_user: CacheUser = Field(...,description="Contexto del usuario")

class ResponseModel(BaseModel):
    analysis: str = Field(...,description="Analisis de detallado del sintoma del usuario")
    answer: str   = Field(...,description="Tu solucion al problema del paciente en base al analysis que hiciste")
    steps: Optional[List[str]] = Field(...,description="Lista de recomendacion que debe seguir paso paso")
    summary: Dict[str,str] = Field(...,description="Resumen la interaccion")