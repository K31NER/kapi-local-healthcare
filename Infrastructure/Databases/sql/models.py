from typing import Optional
from sqlmodel import SQLModel, Field


class UserTable(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    birth_date: str        # ISO date string "YYYY-MM-DD"
    gender: str
    blood_type: str
    allergies: str         # JSON: '["penicilina"]'
    chronic_conditions: str  # JSON: '["diabetes"]'
    emergency_contact_name: str
    emergency_contact_phone: str


class ConsultationTable(SQLModel, table=True):
    __tablename__ = "consultations"
    id: Optional[int] = Field(default=None, primary_key=True)
    question: str
    answer: str
    steps: str    # JSON: '["Descansa", "Hidratate"]'
    summary: str  # JSON: '{"urgency": "low"}'
    created_at: str  # ISO datetime string "YYYY-MM-DDTHH:MM:SS"
