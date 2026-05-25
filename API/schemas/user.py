from datetime import date
from typing import Optional
from pydantic import BaseModel, field_validator


class UserCreate(BaseModel):
    full_name: str
    birth_date: date
    gender: str
    blood_type: str
    allergies: list[str]
    chronic_conditions: list[str]
    emergency_contact_name: str
    emergency_contact_phone: str

    @field_validator("birth_date")
    @classmethod
    def birth_date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[list[str]] = None
    chronic_conditions: Optional[list[str]] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None

    @field_validator("birth_date")
    @classmethod
    def birth_date_not_future(cls, v: Optional[date]) -> Optional[date]:
        if v and v > date.today():
            raise ValueError("La fecha de nacimiento no puede ser futura")
        return v


class UserRead(BaseModel):
    id: int
    full_name: str
    birth_date: date
    gender: str
    blood_type: str
    allergies: list[str]
    chronic_conditions: list[str]
    emergency_contact_name: str
    emergency_contact_phone: str
