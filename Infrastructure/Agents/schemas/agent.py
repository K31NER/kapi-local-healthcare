from pydantic import BaseModel, Field
from typing import List, Literal
from Domain.user import CacheUser

class InputModel(BaseModel):
    question: str
    context_user: CacheUser = Field(..., description="Contexto del usuario")

class ResponseModel(BaseModel):
    analysis: str = Field(..., description="Análisis clínico interno basado en los síntomas expuestos.")
    steps: List[str] = Field(..., description="Lista de recomendaciones y pasos claros, cortos y accionables para el paciente.")
    status: Literal["Normal", "Moderado", "Crítico"] = Field(..., description="Nivel de gravedad o estado de triaje médico del paciente.")
